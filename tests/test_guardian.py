from datetime import datetime, timezone

from bk_capital_intelligence.guardian import GuardianPolicy, evaluate
from bk_capital_intelligence.models import Opportunity


def opportunity(confidence=0.9, sustainability=0.1):
    return Opportunity(
        opportunity_id="guardian-1", protocol="Example", strategy="lending", chain="Ethereum", asset="USDC",
        gross_apy=0.08, fees_apy=0.0, tvl_usd=10_000_000, liquidity_usd=10_000_000,
        lockup_days=0, leverage=1.0, contract_risk=0.1, protocol_risk=0.1, asset_risk=0.1,
        oracle_risk=0.1, governance_risk=0.1, counterparty_risk=0.1, chain_risk=0.1,
        sustainability_risk=sustainability, updated_at=datetime.now(timezone.utc),
        liquidity_risk=0.1, confidence=confidence,
    )


def test_guardian_approves_only_when_all_gates_pass():
    decision = evaluate(opportunity())
    assert decision.approved
    assert decision.reasons == ()


def test_guardian_rejects_low_confidence():
    decision = evaluate(opportunity(confidence=0.59))
    assert not decision.approved
    assert "evidence confidence below Guardian minimum" in decision.reasons


def test_guardian_rejects_overweight_proposal():
    decision = evaluate(opportunity(), proposed_weight=0.36)
    assert not decision.approved
    assert "proposed single-opportunity exposure exceeds policy" in decision.reasons


def test_guardian_respects_blocklists():
    policy = GuardianPolicy(blocked_protocols=("Example",))
    decision = evaluate(opportunity(), policy=policy)
    assert not decision.approved
    assert "protocol is explicitly blocked" in decision.reasons

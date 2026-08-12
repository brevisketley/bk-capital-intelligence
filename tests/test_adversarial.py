from datetime import datetime, timezone

from bk_capital_intelligence.adversarial import review
from bk_capital_intelligence.models import Opportunity, RiskAssessment


def opportunity(**overrides):
    data = dict(
        opportunity_id="x", protocol="p", strategy="lending", chain="ethereum", asset="USDC",
        gross_apy=0.10, fees_apy=0.01, tvl_usd=1_000_000, liquidity_usd=200_000,
        lockup_days=0, leverage=1.0, contract_risk=.2, protocol_risk=.2, asset_risk=.2,
        oracle_risk=.2, governance_risk=.2, counterparty_risk=.2, chain_risk=.2,
        sustainability_risk=.2, liquidity_risk=.2, confidence=.9,
        source="defillama", updated_at=datetime.now(timezone.utc), base_apy=.09, reward_apy=.01,
    )
    data.update(overrides)
    return Opportunity(**data)


def risk(o, blocked=False):
    return RiskAssessment(o.opportunity_id, .8 if not blocked else .2, blocked, (), {})


def test_adversarial_review_passes_clean_case():
    o = opportunity()
    result = review([o], [risk(o)], {o.opportunity_id: .25})
    assert result.passed
    assert result.required_actions == ()


def test_adversarial_review_rejects_reward_heavy_low_confidence_case():
    o = opportunity(confidence=.3, gross_apy=.50, base_apy=.05, reward_apy=.45)
    result = review([o], [risk(o)], {o.opportunity_id: .25})
    assert not result.passed
    assert any("incentives" in action or "confidence" in action for action in result.required_actions)


def test_adversarial_review_rejects_blocked_risk():
    o = opportunity()
    result = review([o], [risk(o, blocked=True)], {o.opportunity_id: .25})
    assert not result.passed

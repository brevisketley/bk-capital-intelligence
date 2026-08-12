from datetime import datetime, timezone

from bk_capital_intelligence.agent_feedback import progressive_review
from bk_capital_intelligence.models import Opportunity, RiskAssessment


def opportunity(**overrides):
    data = dict(
        opportunity_id="p1", protocol="test", strategy="lending", chain="Ethereum", asset="USDC",
        gross_apy=8.0, fees_apy=0.1, tvl_usd=2_000_000, liquidity_usd=1_000_000,
        lockup_days=0, leverage=1.0, contract_risk=0.1, protocol_risk=0.1, asset_risk=0.1,
        oracle_risk=0.1, governance_risk=0.1, counterparty_risk=0.1, chain_risk=0.1,
        sustainability_risk=0.1, updated_at=datetime.now(timezone.utc), liquidity_risk=0.1,
        base_apy=7.0, reward_apy=1.0, source="test", confidence=0.9,
    )
    data.update(overrides)
    return Opportunity(**data)


def risk(score=20.0):
    return RiskAssessment("p1", score, False, (), {})


def test_progressive_review_passes_clean_context():
    result = progressive_review([opportunity()], [risk()], {"p1": 0.2})
    assert result.final_decision == "PASS"
    assert len(result.iterations) == 1


def test_progressive_review_vetoes_critical_risk():
    result = progressive_review([opportunity()], [risk(90)], {"p1": 0.2})
    assert result.final_decision == "VETO"
    assert any(f.agent == "risk" and f.decision == "VETO" for f in result.iterations[0].findings)


def test_progressive_review_remediates_extreme_incentive_yield():
    result = progressive_review([opportunity(gross_apy=150.0, base_apy=10.0, reward_apy=140.0)], [risk()], {"p1": 0.2})
    assert result.final_decision == "PASS"
    assert len(result.iterations) == 2
    assert any(f.agent == "sustainability" and f.decision == "REVISE" for f in result.iterations[0].findings)
    assert dict(result.final_weights)["p1"] == 0.0

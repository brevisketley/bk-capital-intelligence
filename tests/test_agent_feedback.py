from bk_capital_intelligence.agent_feedback import progressive_review
from bk_capital_intelligence.models import Opportunity, RiskAssessment


def opportunity(**overrides):
    data = dict(opportunity_id="p1", protocol="test", chain="Ethereum", symbol="USDC", gross_apy=8.0, apy_base=7.0, apy_reward=1.0, tvl_usd=2_000_000, source="test", confidence=0.9)
    data.update(overrides)
    return Opportunity(**data)


def risk(risk_score=20.0):
    return RiskAssessment("p1", risk_score, 10, 10, 10, 10, 10, 10, 10, 10, "ok")


def test_progressive_review_passes_clean_context():
    result = progressive_review([opportunity()], [risk()], {"p1": 0.2})
    assert result.final_decision == "PASS"
    assert len(result.iterations) == 1


def test_progressive_review_vetoes_critical_risk():
    result = progressive_review([opportunity()], [risk(90)], {"p1": 0.2})
    assert result.final_decision == "VETO"
    assert any(f.agent == "risk" and f.decision == "VETO" for f in result.iterations[0].findings)


def test_progressive_review_flags_extreme_incentive_yield():
    result = progressive_review([opportunity(gross_apy=150.0, apy_base=10.0, apy_reward=140.0)], [risk()], {"p1": 0.2})
    assert result.final_decision == "REVISE"
    assert any(f.agent == "sustainability" and f.decision == "REVISE" for f in result.iterations[-1].findings)

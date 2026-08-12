from datetime import datetime, timezone

from bk_capital_intelligence.models import Opportunity
from bk_capital_intelligence.risk_engine import assess, risk_adjusted_rank


def make(**overrides):
    data = dict(
        opportunity_id="test-1",
        protocol="Test Protocol",
        strategy="stablecoin lending",
        chain="ethereum",
        asset="USDC",
        gross_apy=10.0,
        fees_apy=1.0,
        tvl_usd=10_000_000,
        liquidity_usd=5_000_000,
        lockup_days=0,
        leverage=1.0,
        contract_risk=0.1,
        protocol_risk=0.1,
        asset_risk=0.1,
        oracle_risk=0.1,
        governance_risk=0.1,
        counterparty_risk=0.1,
        chain_risk=0.1,
        sustainability_risk=0.1,
        updated_at=datetime.now(timezone.utc),
    )
    data.update(overrides)
    return Opportunity(**data)


def test_high_contract_risk_is_blocked():
    result = assess(make(contract_risk=0.95))
    assert result.blocked is True
    assert any("contract risk" in reason for reason in result.reasons)


def test_zero_liquidity_is_blocked():
    result = assess(make(liquidity_usd=0))
    assert result.blocked is True


def test_score_is_bounded():
    result = assess(make())
    assert 0 <= result.score <= 100


def test_ranking_does_not_return_blocked_opportunity_as_winner():
    safe = make(opportunity_id="safe", gross_apy=8.0)
    unsafe = make(opportunity_id="unsafe", gross_apy=80.0, contract_risk=0.95)
    ranked = risk_adjusted_rank([unsafe, safe])
    assert ranked[0][0].opportunity_id == "safe"
    assert ranked[1][1].blocked is True

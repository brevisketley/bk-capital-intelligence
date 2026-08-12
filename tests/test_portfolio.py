from datetime import datetime, timezone

import pytest

from bk_capital_intelligence.models import Opportunity
from bk_capital_intelligence.portfolio import construct_risk_adjusted_portfolio


def make_opportunity(i: int, apy: float) -> Opportunity:
    return Opportunity(
        opportunity_id=f"op-{i}", protocol="Protocol", strategy="lending", chain="Ethereum",
        asset="USDC", gross_apy=apy, fees_apy=0.0, tvl_usd=10_000_000, liquidity_usd=10_000_000,
        lockup_days=0, leverage=1.0, contract_risk=0.1, protocol_risk=0.1, asset_risk=0.1,
        oracle_risk=0.1, governance_risk=0.1, counterparty_risk=0.1, chain_risk=0.1,
        sustainability_risk=0.1, updated_at=datetime.now(timezone.utc),
    )


def test_portfolio_never_exceeds_single_weight_cap():
    ops = [make_opportunity(i, 0.08 - i * 0.005) for i in range(5)]
    allocations = construct_risk_adjusted_portfolio(ops, max_single_weight=0.35)
    assert sum(a.weight for a in allocations) == pytest.approx(1.0, abs=1e-7)
    assert all(a.weight <= 0.35 + 1e-8 for a in allocations)


def test_invalid_cap_is_rejected():
    with pytest.raises(ValueError):
        construct_risk_adjusted_portfolio([make_opportunity(1, 0.05)], max_single_weight=0)

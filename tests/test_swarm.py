from datetime import datetime, timezone

from bk_capital_intelligence.models import Opportunity
from bk_capital_intelligence.swarm import run


def test_swarm_never_approves_unknown_evidence_by_default():
    op = Opportunity(
        opportunity_id="swarm-1", protocol="Example", strategy="lending", chain="Ethereum", asset="USDC",
        gross_apy=0.08, fees_apy=0.0, tvl_usd=10_000_000, liquidity_usd=10_000_000,
        lockup_days=0, leverage=1.0, contract_risk=0.1, protocol_risk=0.1, asset_risk=0.1,
        oracle_risk=0.1, governance_risk=0.1, counterparty_risk=0.1, chain_risk=0.1,
        sustainability_risk=0.1, updated_at=datetime.now(timezone.utc), liquidity_risk=0.1,
        confidence=0.2, source="test",
    )
    result = run([op])
    assert result.findings[0].evidence_quality == 0.2
    assert not result.guardian[0].approved

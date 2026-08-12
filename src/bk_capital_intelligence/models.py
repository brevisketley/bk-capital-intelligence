from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Opportunity:
    opportunity_id: str
    protocol: str
    strategy: str
    chain: str
    asset: str
    gross_apy: float
    fees_apy: float
    tvl_usd: float
    liquidity_usd: float
    lockup_days: int
    leverage: float
    contract_risk: float
    protocol_risk: float
    asset_risk: float
    oracle_risk: float
    governance_risk: float
    counterparty_risk: float
    chain_risk: float
    sustainability_risk: float
    updated_at: datetime
    liquidity_risk: float = 0.50
    base_apy: Optional[float] = None
    reward_apy: Optional[float] = None
    source: str = "unknown"
    source_url: Optional[str] = None
    confidence: float = 0.0
    notes: Optional[str] = None

    @property
    def net_apy(self) -> float:
        return self.gross_apy - self.fees_apy

    @property
    def liquidity_ratio(self) -> float:
        if self.tvl_usd <= 0:
            return 0.0
        return min(1.0, self.liquidity_usd / self.tvl_usd)


@dataclass(frozen=True)
class RiskAssessment:
    opportunity_id: str
    score: float
    blocked: bool
    reasons: tuple[str, ...]
    components: dict[str, float]

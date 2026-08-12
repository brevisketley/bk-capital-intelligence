"""Public yield-opportunity ingestion with provenance and conservative defaults."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Iterable
from urllib.request import Request, urlopen

from .models import Opportunity

DEFILLAMA_POOLS_URL = "https://yields.llama.fi/pools"
USER_AGENT = "BK-Capital-Intelligence/0.1"

class IngestionError(RuntimeError):
    """Raised when a source cannot be safely normalized."""


def fetch_json(url: str = DEFILLAMA_POOLS_URL, timeout: int = 20) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise IngestionError(f"yield source unavailable: {exc}") from exc


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _risk_from_data(row: dict[str, Any]) -> dict[str, float]:
    """Create provisional source-derived risk inputs; unknowns remain cautious."""
    tvl = _number(row.get("tvl"))
    apy = _number(row.get("apy"))
    reward_apy = _number(row.get("apyReward"))
    base_apy = _number(row.get("apyBase"))
    reward_share = reward_apy / apy if apy > 0 else 0.0
    sustainability = min(1.0, 0.25 + reward_share * 0.65)
    if apy > 100.0:
        sustainability = max(sustainability, 0.85)
    if base_apy <= 0 and reward_apy > 0:
        sustainability = max(sustainability, 0.90)
    # These are not security audits. Missing evidence is deliberately not treated as safe.
    unknown = 0.60
    return {
        "contract": unknown, "protocol": unknown, "asset": 0.45,
        "oracle": unknown, "governance": unknown, "counterparty": 0.55,
        "chain": 0.45, "sustainability": sustainability,
        "liquidity": 0.75 if tvl < 100_000 else 0.45 if tvl < 1_000_000 else 0.20,
    }


def normalize_pool(row: dict[str, Any], observed_at: datetime | None = None) -> Opportunity:
    required = ("pool", "project", "chain", "symbol")
    missing = [key for key in required if not row.get(key)]
    if missing:
        raise IngestionError(f"pool missing required fields: {', '.join(missing)}")
    observed_at = observed_at or datetime.now(timezone.utc)
    risk = _risk_from_data(row)
    return Opportunity(
        opportunity_id=f"defillama:{row['pool']}",
        protocol=str(row["project"]),
        strategy=str(row.get("poolMeta") or "generic_yield"),
        chain=str(row["chain"]),
        asset=str(row["symbol"]),
        gross_apy=_number(row.get("apy")) / 100.0,
        fees_apy=0.0,
        tvl_usd=_number(row.get("tvl")),
        liquidity_usd=_number(row.get("tvl")),
        lockup_days=0,
        leverage=1.0,
        contract_risk=risk["contract"], protocol_risk=risk["protocol"],
        asset_risk=risk["asset"], oracle_risk=risk["oracle"],
        governance_risk=risk["governance"], counterparty_risk=risk["counterparty"],
        chain_risk=risk["chain"], sustainability_risk=risk["sustainability"],
        updated_at=observed_at,
        notes="DeFiLlama source; provisional risk inputs require enrichment before capital use.",
    )


def normalize_pools(payload: dict[str, Any], limit: int | None = None) -> list[Opportunity]:
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise IngestionError("yield source response does not contain a data list")
    result: list[Opportunity] = []
    for row in rows[:limit]:
        if isinstance(row, dict):
            try:
                result.append(normalize_pool(row))
            except IngestionError:
                continue
    return result


def opportunities_as_dicts(opportunities: Iterable[Opportunity]) -> list[dict[str, Any]]:
    return [asdict(item) for item in opportunities]

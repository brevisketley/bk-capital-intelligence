"""Research scanner: ingest public yield data, score it, and return explainable rankings."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .ingestion import fetch_json, normalize_pools
from .risk_engine import assess


def scan(limit: int = 100, minimum_tvl: float = 1_000_000) -> list[dict[str, Any]]:
    """Return ranked opportunities without executing or recommending transactions."""
    opportunities = normalize_pools(fetch_json())
    filtered = [item for item in opportunities if item.tvl_usd >= minimum_tvl]
    rows: list[dict[str, Any]] = []
    for opportunity in filtered:
        assessment = assess(opportunity)
        if assessment.blocked:
            continue
        score = max(0.0, opportunity.net_apy) * assessment.score / 100.0
        row = asdict(opportunity)
        row.update({
            "risk_score": assessment.score,
            "risk_adjusted_yield": round(score, 8),
            "blocked": assessment.blocked,
            "risk_reasons": list(assessment.reasons),
        })
        rows.append(row)
    return sorted(rows, key=lambda item: item["risk_adjusted_yield"], reverse=True)[:limit]


def main() -> None:
    for rank, row in enumerate(scan(), start=1):
        print(f"{rank:02d} {row['protocol']} | {row['chain']} | {row['asset']} | APY={row['gross_apy']:.2%} | risk={row['risk_score']:.1f} | adjusted={row['risk_adjusted_yield']:.4%}")


if __name__ == "__main__":
    main()

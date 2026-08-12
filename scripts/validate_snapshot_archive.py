"""Evaluate the accumulated point-in-time snapshot archive.

A PASS is impossible until there are enough independent out-of-sample periods. The
report also refuses to call the result realized P&L because APY-implied replay is a
research proxy.
"""
from __future__ import annotations

import json
from pathlib import Path

from bk_capital_intelligence.replay import period_return_series
from bk_capital_intelligence.validation import validate_period_returns

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "data" / "snapshots"
REPORTS = ROOT / "data" / "validation"


def load_series() -> tuple[dict[str, list[dict]], int]:
    files = sorted(SNAPSHOTS.glob("*/**.json"))
    series: dict[str, list[dict]] = {}
    for path in files:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for row in document.get("data", []):
            opportunity_id = row.get("opportunity_id")
            if not opportunity_id:
                continue
            # Snapshot timestamps are authoritative decision timestamps.
            ts = int(path.stat().st_mtime)
            series.setdefault(opportunity_id, []).append({
                "timestamp": ts,
                "apy": float(row.get("gross_apy") or 0.0) * 100.0,
                "apyReward": float(row.get("reward_apy") or 0.0) * 100.0,
                "tvlUsd": float(row.get("tvl_usd") or 0.0),
            })
    for points in series.values():
        points.sort(key=lambda p: p["timestamp"])
    return series, len(files)


def main() -> None:
    series, snapshot_count = load_series()
    if snapshot_count < 2:
        result = {"status": "INSUFFICIENT_DATA", "snapshot_count": snapshot_count, "message": "Need at least two snapshots to form a forward period."}
    else:
        bk, high, equal, observations = period_return_series(series)
        validation = validate_period_returns(bk, high, equal)
        result = {
            "status": validation.status,
            "eligible": validation.eligible,
            "snapshot_count": snapshot_count,
            "paired_periods": observations,
            "metrics": validation.metrics,
            "message": validation.message,
            "realized_pnl": False,
            "note": "APY-implied research proxy; token price, gas, slippage and depeg effects are not represented unless explicitly added to the dataset.",
        }
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / "snapshot-validation-latest.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()

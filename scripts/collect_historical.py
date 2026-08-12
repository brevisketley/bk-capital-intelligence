"""Build a point-in-time research dataset from DeFiLlama pool charts.

This is deliberately labelled conditional: the initial backfill starts from the
current pool universe, so it must NOT be presented as an unbiased historical
universe. The daily snapshot collector remains the source for future unbiased
walk-forward universe selection.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from bk_capital_intelligence.ingestion import DEFILLAMA_POOLS_URL, USER_AGENT

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "historical"
CHART_URL = "https://yields.llama.fi/chart/{}"


def get_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main(limit: int = 30) -> None:
    universe = get_json(DEFILLAMA_POOLS_URL).get("data", [])
    eligible = [
        row for row in universe
        if isinstance(row, dict) and row.get("pool") and float(row.get("tvlUsd") or 0) >= 1_000_000
    ]
    eligible.sort(key=lambda row: float(row.get("tvlUsd") or 0), reverse=True)
    selected = eligible[:limit]
    series: dict[str, list[dict]] = {}
    failed: list[str] = []
    for row in selected:
        pool = str(row["pool"])
        try:
            payload = get_json(CHART_URL.format(pool))
            points = payload.get("data", [])
            if isinstance(points, list) and len(points) >= 2:
                series[pool] = points
            else:
                failed.append(pool)
        except Exception:
            failed.append(pool)
        time.sleep(0.15)

    now = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"conditional-{now.strftime('%Y%m%dT%H%M%SZ')}.json"
    document = {
        "observed_at": now.isoformat(),
        "source": "DeFiLlama /chart",
        "dataset_type": "conditional_current_universe_backfill",
        "survivorship_bias_warning": True,
        "selection_rule": "current pools with TVL >= $1m, top by current TVL",
        "pool_count": len(series),
        "failed_pool_count": len(failed),
        "series": series,
    }
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()

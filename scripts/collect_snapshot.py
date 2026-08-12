from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from bk_capital_intelligence.ingestion import fetch_json, normalize_pools, opportunities_as_dicts


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "snapshots"


def main() -> None:
    now = datetime.now(timezone.utc)
    payload = fetch_json()
    opportunities = normalize_pools(payload)
    # Keep the research archive bounded: top 100 by TVL, with full source metadata.
    opportunities = sorted(opportunities, key=lambda item: item.tvl_usd, reverse=True)[:100]
    target = OUT / now.strftime("%Y-%m-%d")
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{now.strftime('%H%M%S')}Z.json"
    document = {
        "observed_at": now.isoformat(),
        "source": "DeFiLlama",
        "count": len(opportunities),
        "data": opportunities_as_dicts(opportunities),
    }
    path.write_text(json.dumps(document, indent=2, default=str) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()

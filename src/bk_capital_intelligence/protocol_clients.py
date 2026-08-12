"""Official protocol data clients used for enrichment.

These clients are read-only. They never construct or sign transactions.
"""
from __future__ import annotations

import json
from typing import Any
from urllib.request import Request, urlopen

MORPHO_GRAPHQL = "https://api.morpho.org/graphql"
PENDLE_MARKETS = "https://api-v2.pendle.finance/core/v2/markets/all"


def _get_json(url: str, timeout: int = 20) -> Any:
    request = Request(url, headers={"User-Agent": "BK-Capital-Intelligence/0.2", "Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def morpho_markets(first: int = 100) -> list[dict[str, Any]]:
    query = """
    query Markets($first: Int) {
      markets(first: $first) {
        items {
          uniqueKey
          lltv
          loanAsset { address symbol decimals }
          collateralAsset { address symbol decimals }
          state { supplyAssets borrowAssets utilization fee }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"first": min(max(first, 1), 100)}}).encode()
    request = Request(MORPHO_GRAPHQL, data=payload, headers={"User-Agent": "BK-Capital-Intelligence/0.2", "Content-Type": "application/json"})
    with urlopen(request, timeout=20) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("errors"):
        raise RuntimeError(f"Morpho API error: {result['errors']}")
    return result.get("data", {}).get("markets", {}).get("items", [])


def pendle_markets(limit: int = 100) -> list[dict[str, Any]]:
    payload = _get_json(f"{PENDLE_MARKETS}?limit={min(max(limit, 1), 100)}&skip=0")
    markets = payload.get("markets", []) if isinstance(payload, dict) else []
    return markets if isinstance(markets, list) else []

"""Walk-forward yield-implied benchmark simulator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .backtest import Performance, evaluate


@dataclass(frozen=True)
class ReplayResult:
    bk: Performance
    highest_apy: Performance
    equal_weight: Performance
    observations: int


def _risk_proxy(point: dict[str, Any]) -> float:
    tvl = float(point.get("tvlUsd") or 0.0)
    apy = float(point.get("apy") or 0.0)
    reward = float(point.get("apyReward") or 0.0)
    reward_share = reward / apy if apy > 0 else 0.0
    tvl_risk = 0.75 if tvl < 100_000 else 0.45 if tvl < 1_000_000 else 0.20
    sustainability = min(1.0, 0.25 + reward_share * 0.65)
    if apy > 100.0:
        sustainability = max(sustainability, 0.85)
    score = 100.0 * (1.0 - (0.55 * tvl_risk + 0.45 * sustainability))
    return max(0.0, min(100.0, score))


def _daily_growth(next_apy_percent: float) -> float:
    return 1.0 + max(-0.99, next_apy_percent / 100.0 / 365.0)


def period_return_series(pool_series: dict[str, list[dict[str, Any]]], top_k: int = 5) -> tuple[list[float], list[float], list[float], int]:
    """Return paired forward period returns for BK, highest-APY and equal-weight.

    Selection uses only the earlier observation. The later observation is used only
    for the simulated forward yield. Missing pool transitions are excluded and
    counted in coverage rather than silently treated as profitable exits.
    """
    if not pool_series:
        raise ValueError("pool_series cannot be empty")
    indexed: dict[str, dict[int, dict[str, Any]]] = {}
    timestamps: set[int] = set()
    for pool_id, points in pool_series.items():
        indexed[pool_id] = {}
        for point in points:
            ts = int(point.get("timestamp"))
            indexed[pool_id][ts] = point
            timestamps.add(ts)
    ordered = sorted(timestamps)
    if len(ordered) < 2:
        raise ValueError("at least two observations are required")

    bk_returns: list[float] = []
    high_returns: list[float] = []
    equal_returns: list[float] = []
    for ts, next_ts in zip(ordered, ordered[1:]):
        available = [(pool, indexed[pool][ts]) for pool in indexed if ts in indexed[pool] and next_ts in indexed[pool]]
        if not available:
            continue
        by_apy = sorted(available, key=lambda item: float(item[1].get("apy") or 0.0), reverse=True)
        by_adjusted = sorted(
            available,
            key=lambda item: (float(item[1].get("apy") or 0.0) / 100.0) * _risk_proxy(item[1]) / 100.0,
            reverse=True,
        )
        high = by_apy[:1]
        bk = by_adjusted[:max(1, top_k)]
        high_growth = _daily_growth(float(indexed[high[0][0]][next_ts].get("apy") or 0.0))
        bk_growth = sum(_daily_growth(float(indexed[pool][next_ts].get("apy") or 0.0)) for pool, _ in bk) / len(bk)
        equal_growth = sum(_daily_growth(float(indexed[pool][next_ts].get("apy") or 0.0)) for pool, _ in available) / len(available)
        high_returns.append(high_growth - 1.0)
        bk_returns.append(bk_growth - 1.0)
        equal_returns.append(equal_growth - 1.0)
    return bk_returns, high_returns, equal_returns, len(bk_returns)


def replay(pool_series: dict[str, list[dict[str, Any]]], top_k: int = 5) -> ReplayResult:
    bk_returns, high_returns, equal_returns, observations = period_return_series(pool_series, top_k)
    if observations == 0:
        raise ValueError("no overlapping consecutive observations")
    def compound(returns: list[float]) -> list[float]:
        values = [1.0]
        for r in returns:
            values.append(values[-1] * (1.0 + r))
        return values
    return ReplayResult(
        bk=evaluate(compound(bk_returns)),
        highest_apy=evaluate(compound(high_returns)),
        equal_weight=evaluate(compound(equal_returns)),
        observations=observations,
    )

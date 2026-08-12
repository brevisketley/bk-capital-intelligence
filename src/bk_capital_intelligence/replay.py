"""Walk-forward yield-implied benchmark simulator.

Selection at time t uses only information in the t observation. The next period's
APY is used only for the simulated outcome. This is a research proxy, not realized
PnL: it excludes token price moves, gas, slippage, depegs and other path-dependent
cash-flow effects unless those are represented in the source series.
"""
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
    """Convert annualized APY to a simple one-day yield-implied growth factor."""
    return 1.0 + max(-0.99, next_apy_percent / 100.0 / 365.0)


def replay(pool_series: dict[str, list[dict[str, Any]]], top_k: int = 5) -> ReplayResult:
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

    values_bk = [1.0]
    values_high = [1.0]
    values_equal = [1.0]
    observations = 0
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
        equal = available  # true equal-weight baseline across the full eligible universe
        high_growth = _daily_growth(float(indexed[high[0][0]][next_ts].get("apy") or 0.0))
        bk_growth = sum(_daily_growth(float(indexed[pool][next_ts].get("apy") or 0.0)) for pool, _ in bk) / len(bk)
        equal_growth = sum(_daily_growth(float(indexed[pool][next_ts].get("apy") or 0.0)) for pool, _ in equal) / len(equal)
        values_high.append(values_high[-1] * high_growth)
        values_bk.append(values_bk[-1] * bk_growth)
        values_equal.append(values_equal[-1] * equal_growth)
        observations += 1

    if observations == 0:
        raise ValueError("no overlapping consecutive observations")
    return ReplayResult(
        bk=evaluate(values_bk),
        highest_apy=evaluate(values_high),
        equal_weight=evaluate(values_equal),
        observations=observations,
    )

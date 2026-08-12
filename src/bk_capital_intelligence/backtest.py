"""Deterministic paper-performance and benchmark metrics.

This module consumes observations that were available at each decision timestamp.
It intentionally does not query future data, preventing accidental look-ahead bias.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class Performance:
    ending_value: float
    total_return: float
    annualized_return: float
    annualized_volatility: float
    max_drawdown: float


def _max_drawdown(values: list[float]) -> float:
    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        if peak > 0:
            worst = min(worst, value / peak - 1.0)
    return worst


def evaluate(values: list[float], periods_per_year: float = 365.0) -> Performance:
    if not values or any(value <= 0 for value in values):
        raise ValueError("portfolio values must be positive")
    if len(values) < 2:
        return Performance(values[-1], 0.0, 0.0, 0.0, 0.0)
    returns = [values[i] / values[i - 1] - 1.0 for i in range(1, len(values))]
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / len(returns)
    volatility = sqrt(variance) * sqrt(periods_per_year)
    years = (len(values) - 1) / periods_per_year
    annualized = (values[-1] / values[0]) ** (1 / years) - 1 if years > 0 else 0.0
    return Performance(
        ending_value=values[-1],
        total_return=values[-1] / values[0] - 1.0,
        annualized_return=annualized,
        annualized_volatility=volatility,
        max_drawdown=_max_drawdown(values),
    )


def compare(bk_values: list[float], highest_apy_values: list[float], equal_weight_values: list[float]) -> dict[str, Performance]:
    """Return apples-to-apples metrics for the three required research baselines."""
    return {
        "bk_risk_adjusted": evaluate(bk_values),
        "highest_apy": evaluate(highest_apy_values),
        "equal_weight": evaluate(equal_weight_values),
    }

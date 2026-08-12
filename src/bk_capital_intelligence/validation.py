"""Walk-forward validation gates.

This module prevents the product from declaring historical superiority until there
is enough point-in-time data and the comparison is genuinely out-of-sample.
"""
from __future__ import annotations
from dataclasses import dataclass
from statistics import mean


@dataclass(frozen=True)
class ValidationResult:
    status: str
    eligible: bool
    periods: int
    message: str
    metrics: dict[str, float]


def validate_period_returns(
    bk_returns: list[float],
    apy_returns: list[float],
    equal_returns: list[float],
    *,
    min_periods: int = 12,
) -> ValidationResult:
    """Validate paired walk-forward periods without hindsight leakage.

    Returns are expected to be realized/forward returns calculated from snapshots
    that existed before each decision. APY-implied replay alone cannot be labelled
    realized performance.
    """
    n = min(len(bk_returns), len(apy_returns), len(equal_returns))
    if n < min_periods:
        return ValidationResult(
            "INSUFFICIENT_DATA", False, n,
            f"Need at least {min_periods} paired out-of-sample periods; have {n}.", {},
        )
    bk, apy, eq = bk_returns[:n], apy_returns[:n], equal_returns[:n]
    metrics = {
        "bk_mean_period_return": mean(bk),
        "apy_mean_period_return": mean(apy),
        "equal_mean_period_return": mean(eq),
        "bk_excess_vs_apy": mean(bk) - mean(apy),
        "bk_excess_vs_equal": mean(bk) - mean(eq),
    }
    eligible = metrics["bk_excess_vs_apy"] > 0 and metrics["bk_excess_vs_equal"] > 0
    return ValidationResult(
        "PASS" if eligible else "FAIL",
        eligible,
        n,
        "BK beats both baselines on mean paired out-of-sample return." if eligible else "BK does not beat both baselines on the supplied out-of-sample periods.",
        metrics,
    )

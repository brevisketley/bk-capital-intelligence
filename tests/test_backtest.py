import pytest

from bk_capital_intelligence.backtest import compare, evaluate


def test_metrics_are_deterministic():
    result = evaluate([100.0, 110.0, 105.0, 120.0], periods_per_year=3)
    assert result.ending_value == 120.0
    assert result.total_return == pytest.approx(0.20)
    assert result.max_drawdown == pytest.approx(-5 / 110)
    assert result.annualized_volatility > 0


def test_compare_returns_all_required_baselines():
    result = compare([100, 102], [100, 101], [100, 101.5])
    assert set(result) == {"bk_risk_adjusted", "highest_apy", "equal_weight"}


def test_non_positive_values_are_rejected():
    with pytest.raises(ValueError):
        evaluate([100, 0])

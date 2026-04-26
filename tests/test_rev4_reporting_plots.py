from __future__ import annotations

import numpy as np
import pandas as pd

from nse_engine.reporting import (
    plot_rev4_direction_accuracy,
    plot_rev4_error_distribution,
    plot_rev4_forecast_overview,
    plot_rev4_market_context,
    plot_rev4_metrics_comparison,
    plot_rev4_residuals,
)


def _prediction_frame(rows: int = 40) -> pd.DataFrame:
    dates = pd.date_range("2010-01-01", periods=rows, freq="D")
    actual = np.linspace(1000, 1200, rows)
    lstm = actual - 20
    last_value = pd.Series(actual).shift(1).bfill().to_numpy()
    moving_average = pd.Series(actual).rolling(window=5).mean().shift(1).bfill().to_numpy()
    return pd.DataFrame(
        {
            "date": dates.astype(str),
            "actual": actual,
            "lstm_rev4_prediction": lstm,
            "lstm_rev4_residual": lstm - actual,
            "last_value_prediction": last_value,
            "last_value_residual": last_value - actual,
            "moving_average_21_prediction": moving_average,
            "moving_average_21_residual": moving_average - actual,
        }
    )


def _comparison() -> list[dict[str, float | str]]:
    return [
        {
            "model": "last_value",
            "mae": 10.0,
            "rmse": 12.0,
            "mape_percent": 1.0,
            "directional_accuracy_percent": 50.0,
        },
        {
            "model": "lstm_rev4",
            "mae": 20.0,
            "rmse": 25.0,
            "mape_percent": 2.0,
            "directional_accuracy_percent": 54.0,
        },
        {
            "model": "moving_average_21",
            "mae": 30.0,
            "rmse": 35.0,
            "mape_percent": 3.0,
            "directional_accuracy_percent": 56.0,
        },
    ]


def test_rev4_prediction_plots_are_created(tmp_path) -> None:
    frame = _prediction_frame()
    outputs = [
        tmp_path / "forecast.png",
        tmp_path / "residuals.png",
        tmp_path / "errors.png",
    ]

    plot_rev4_forecast_overview(frame, output_path=outputs[0])
    plot_rev4_residuals(frame, output_path=outputs[1])
    plot_rev4_error_distribution(frame, output_path=outputs[2])

    assert all(path.exists() and path.stat().st_size > 0 for path in outputs)


def test_rev4_metric_plots_are_created(tmp_path) -> None:
    comparison = _comparison()
    outputs = [
        tmp_path / "metrics.png",
        tmp_path / "direction.png",
    ]

    plot_rev4_metrics_comparison(comparison, output_path=outputs[0])
    plot_rev4_direction_accuracy(comparison, output_path=outputs[1])

    assert all(path.exists() and path.stat().st_size > 0 for path in outputs)


def test_rev4_market_context_handles_panic_mode_and_missing_panic_mode(tmp_path) -> None:
    frame = pd.DataFrame(
        {
            "Date": pd.date_range("2003-01-01", periods=40, freq="D"),
            "Market_Close": np.linspace(8000, 8500, 40),
            "Volatility_1M": np.linspace(0.01, 0.05, 40),
            "Panic_Mode": [0] * 30 + [1] * 10,
        }
    )
    with_panic = tmp_path / "context_with_panic.png"
    without_panic = tmp_path / "context_without_panic.png"

    plot_rev4_market_context(frame, output_path=with_panic)
    plot_rev4_market_context(frame.drop(columns=["Panic_Mode"]), output_path=without_panic)

    assert with_panic.exists() and with_panic.stat().st_size > 0
    assert without_panic.exists() and without_panic.stat().st_size > 0

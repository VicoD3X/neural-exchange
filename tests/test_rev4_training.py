from __future__ import annotations

import numpy as np
import pandas as pd

from nse_engine.config import DOW_MACRO_REV4_FEATURE_COLUMNS
from nse_engine.evaluation import (
    build_naive_baselines,
    build_prediction_frame,
    compare_prediction_sets,
    compute_regression_metrics,
)
from nse_engine.features import add_rev4_market_features
from nse_engine.lstm import Rev4LSTMModel, predict_scaled
from nse_engine.sequences import build_rev4_sequences, inverse_transform_target


def _synthetic_rev4_frame(rows: int = 80) -> pd.DataFrame:
    dates = pd.date_range("2003-01-01", periods=rows, freq="D")
    base = np.linspace(1000, 1200, rows)
    data = {
        "Date": dates,
        "Market_Close": base,
        "FEDFUNDS": np.linspace(1.0, 2.0, rows),
        "CPIAUCSL": np.linspace(180, 190, rows),
        "MORTGAGE30US": np.linspace(5.0, 6.0, rows),
        "UMCSENT": np.linspace(70, 90, rows),
        "T10Y2Y": np.linspace(1.0, 2.0, rows),
        "UNRATE": np.linspace(5.0, 6.0, rows),
        "HOUST": np.linspace(1000, 1200, rows),
        "TOTALSA": np.linspace(10.0, 12.0, rows),
        "Volatility_1W": np.linspace(0.01, 0.03, rows),
        "Volatility_1M": np.linspace(0.02, 0.04, rows),
        "Panic_Mode": [0] * (rows - 5) + [1] * 5,
    }
    return pd.DataFrame(data)


def test_build_rev4_sequences_has_temporal_split_without_future_target_leakage() -> None:
    frame = _synthetic_rev4_frame()
    dataset = build_rev4_sequences(frame, sequence_length=10, train_ratio=0.75)

    assert dataset.x_train.shape[1:] == (10, len(DOW_MACRO_REV4_FEATURE_COLUMNS))
    assert dataset.x_test.shape[1:] == (10, len(DOW_MACRO_REV4_FEATURE_COLUMNS))
    assert dataset.train_rows == 60
    assert dataset.test_dates[0] == "2003-03-02"
    assert dataset.test_dates[0] == frame.loc[dataset.train_rows, "Date"].date().isoformat()
    assert dataset.test_dates[0] > frame.loc[dataset.train_rows - 1, "Date"].date().isoformat()


def test_rev4_scaler_is_fitted_on_train_only() -> None:
    frame = _synthetic_rev4_frame()
    frame.loc[70:, "Market_Close"] = 5000.0

    dataset = build_rev4_sequences(frame, sequence_length=10, train_ratio=0.75)
    target_index = dataset.target_index

    assert dataset.scaler.data_max_[target_index] < frame["Market_Close"].max()
    assert np.isclose(dataset.scaler.data_max_[target_index], frame.loc[:59, "Market_Close"].max())


def test_panic_mode_feature_is_binary_and_detects_volatility_spike() -> None:
    rows = 80
    prices = np.array([100.0] * 40 + [150.0, 80.0, 155.0, 75.0, 160.0] + [120.0] * 35)
    frame = pd.DataFrame(
        {
            "Date": pd.date_range("2003-01-01", periods=rows, freq="D"),
            "Market_Close": prices,
        }
    )

    features = add_rev4_market_features(frame)

    assert set(features["Panic_Mode"].unique()).issubset({0, 1})
    assert features["Panic_Mode"].sum() >= 1
    assert features[["Volatility_1W", "Volatility_1M", "Panic_Mode"]].isna().sum().sum() == 0


def test_rev4_lstm_forward_shape() -> None:
    model = Rev4LSTMModel(input_size=len(DOW_MACRO_REV4_FEATURE_COLUMNS), hidden_size=8)
    x_values = np.zeros((4, 10, len(DOW_MACRO_REV4_FEATURE_COLUMNS)), dtype=np.float32)

    predictions = predict_scaled(model, x_values)

    assert predictions.shape == (4,)
    assert np.isfinite(predictions).all()


def test_inverse_transform_target_and_metrics_are_finite() -> None:
    dataset = build_rev4_sequences(_synthetic_rev4_frame(), sequence_length=10, train_ratio=0.75)
    restored = inverse_transform_target(
        dataset.y_test.reshape(-1),
        scaler=dataset.scaler,
        n_features=len(dataset.feature_columns),
        target_index=dataset.target_index,
    )
    metrics = compute_regression_metrics(restored, restored)

    assert np.isfinite(restored).all()
    assert metrics["mae"] == 0.0
    assert metrics["rmse"] == 0.0


def test_naive_baselines_are_causal_and_exportable() -> None:
    frame = _synthetic_rev4_frame()
    dataset = build_rev4_sequences(frame, sequence_length=10, train_ratio=0.75)
    actuals = frame["Market_Close"].iloc[dataset.train_rows :].to_numpy(dtype=np.float32)
    baselines = build_naive_baselines(
        frame,
        target_column="Market_Close",
        train_rows=dataset.train_rows,
        moving_average_window=5,
    )
    prediction_frame = build_prediction_frame(
        dates=dataset.test_dates,
        actuals=actuals,
        predictions={"lstm_rev4": actuals, **baselines},
    )
    comparison = compare_prediction_sets(actuals=actuals, predictions={"lstm_rev4": actuals, **baselines})

    assert np.isclose(baselines["last_value"][0], frame.loc[dataset.train_rows - 1, "Market_Close"])
    assert np.isfinite(baselines["moving_average_5"]).all()
    assert {"date", "actual", "lstm_rev4_prediction", "last_value_prediction"}.issubset(
        prediction_frame.columns
    )
    assert comparison[0]["model"] == "lstm_rev4"

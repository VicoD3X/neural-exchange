"""Evaluation critique du modele Rev4 avec baselines simples."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def compute_regression_metrics(actuals: np.ndarray, predictions: np.ndarray) -> dict[str, float]:
    """Calcule les metriques communes pour comparer modele et baselines."""

    errors = predictions - actuals
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors**2)))
    mape = float(np.mean(np.abs(errors / actuals)) * 100)
    directional_accuracy = float(
        np.mean(np.sign(np.diff(actuals)) == np.sign(np.diff(predictions))) * 100
    )
    return {
        "mae": mae,
        "rmse": rmse,
        "mape_percent": mape,
        "directional_accuracy_percent": directional_accuracy,
    }


def build_naive_baselines(
    df: pd.DataFrame,
    *,
    target_column: str,
    train_rows: int,
    moving_average_window: int = 21,
) -> dict[str, np.ndarray]:
    """Construit des baselines causales pour la periode de test."""

    target = df[target_column].astype(float)
    last_value = target.shift(1)
    moving_average = target.rolling(window=moving_average_window).mean().shift(1)
    moving_average = moving_average.fillna(last_value)

    return {
        "last_value": last_value.iloc[train_rows:].to_numpy(dtype=np.float32),
        f"moving_average_{moving_average_window}": moving_average.iloc[train_rows:].to_numpy(
            dtype=np.float32
        ),
    }


def build_prediction_frame(
    *,
    dates: list[str],
    actuals: np.ndarray,
    predictions: dict[str, np.ndarray],
) -> pd.DataFrame:
    """Assemble predictions et residus dans un DataFrame exportable."""

    frame = pd.DataFrame({"date": dates, "actual": actuals.astype(float)})
    for name, values in predictions.items():
        frame[f"{name}_prediction"] = values.astype(float)
        frame[f"{name}_residual"] = values.astype(float) - frame["actual"]
    return frame


def compare_prediction_sets(
    *,
    actuals: np.ndarray,
    predictions: dict[str, np.ndarray],
) -> list[dict[str, Any]]:
    """Compare plusieurs jeux de predictions avec les memes metriques."""

    rows = []
    for name, values in predictions.items():
        metrics = compute_regression_metrics(actuals, values)
        rows.append({"model": name, **metrics})
    return sorted(rows, key=lambda row: row["mae"])

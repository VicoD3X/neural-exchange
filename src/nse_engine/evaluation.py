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


def summarize_lstm_vs_baselines(
    comparison: list[dict[str, Any]],
    *,
    lstm_model_name: str = "lstm_rev4",
) -> dict[str, Any]:
    """Produit un verdict lisible entre LSTM et meilleures baselines naives."""

    if not comparison:
        return {
            "status": "not_evaluated",
            "message": "Aucune comparaison disponible.",
        }

    by_model = {row["model"]: row for row in comparison}
    lstm_row = by_model.get(lstm_model_name)
    baseline_rows = [row for row in comparison if row["model"] != lstm_model_name]
    if lstm_row is None or not baseline_rows:
        return {
            "status": "not_evaluated",
            "message": "Comparaison LSTM/baselines incomplete.",
        }

    best_baseline = min(baseline_rows, key=lambda row: row["mae"])
    best_overall = min(comparison, key=lambda row: row["mae"])
    lstm_rank = sorted(comparison, key=lambda row: row["mae"]).index(lstm_row) + 1
    mae_delta = float(lstm_row["mae"] - best_baseline["mae"])
    mae_ratio = float(lstm_row["mae"] / best_baseline["mae"]) if best_baseline["mae"] else float("inf")
    direction_delta = float(
        lstm_row["directional_accuracy_percent"]
        - best_baseline["directional_accuracy_percent"]
    )
    beats_best_baseline = mae_delta < 0

    if beats_best_baseline:
        status = "lstm_beats_best_naive_baseline"
        message = (
            "Le LSTM Rev4 bat la meilleure baseline naive sur le MAE. "
            "Ce signal reste retrospectif et doit etre confirme par une validation plus robuste."
        )
    else:
        status = "lstm_does_not_beat_best_naive_baseline"
        message = (
            "Le LSTM Rev4 ne bat pas la meilleure baseline naive sur le MAE. "
            "Ce resultat n'est pas un echec : il montre que le modele est evalue contre une reference simple."
        )

    return {
        "status": status,
        "message": message,
        "primary_metric": "mae",
        "best_overall_model": best_overall["model"],
        "best_baseline_model": best_baseline["model"],
        "lstm_rank_by_mae": lstm_rank,
        "lstm_beats_best_baseline": beats_best_baseline,
        "mae_delta_vs_best_baseline": mae_delta,
        "mae_ratio_vs_best_baseline": mae_ratio,
        "direction_delta_vs_best_baseline": direction_delta,
    }

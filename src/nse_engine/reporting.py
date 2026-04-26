"""Reporting reproductible pour Rev4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


def build_rev4_report(
    *,
    metadata: dict[str, Any],
    test_dates: list[str],
    actuals: np.ndarray,
    predictions: np.ndarray,
    losses: list[float],
) -> dict[str, Any]:
    """Construit un rapport compact pour le modele Rev4."""

    preview_count = min(10, len(actuals))
    prediction_preview = [
        {
            "date": test_dates[index],
            "actual": float(actuals[index]),
            "prediction": float(predictions[index]),
            "error": float(predictions[index] - actuals[index]),
        }
        for index in range(preview_count)
    ]
    tail_preview = [
        {
            "date": test_dates[index],
            "actual": float(actuals[index]),
            "prediction": float(predictions[index]),
            "error": float(predictions[index] - actuals[index]),
        }
        for index in range(max(0, len(actuals) - preview_count), len(actuals))
    ]

    return {
        "summary": {
            "model_name": metadata["model_name"],
            "dataset_name": metadata["dataset_name"],
            "target_column": metadata["target_column"],
            "train_rows": metadata["train_rows"],
            "test_rows": metadata["test_rows"],
            "final_train_loss": metadata["final_train_loss"],
        },
        "metrics": metadata["metrics"],
        "features": metadata["feature_columns"],
        "training": {
            "sequence_length": metadata["sequence_length"],
            "hidden_size": metadata["hidden_size"],
            "epochs": metadata["epochs"],
            "batch_size": metadata["batch_size"],
            "learning_rate": metadata["learning_rate"],
            "random_seed": metadata["random_seed"],
            "loss_first": float(losses[0]),
            "loss_last": float(losses[-1]),
        },
        "prediction_preview": prediction_preview,
        "prediction_tail": tail_preview,
        "limitations": [
            "Modele experimental local, non destine au trading.",
            "Evaluation retrospective uniquement sur la periode disponible.",
            "Aucune promesse de prediction fiable des marches ou des crises.",
        ],
        "financial_disclaimer": metadata["financial_disclaimer"],
    }


def write_rev4_report(
    report: dict[str, Any],
    *,
    report_json_path: Path,
    report_md_path: Path,
) -> None:
    """Sauvegarde le rapport Rev4 en JSON et Markdown."""

    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    report_md_path.parent.mkdir(parents=True, exist_ok=True)
    report_json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report_md_path.write_text(render_rev4_markdown(report), encoding="utf-8")


def render_rev4_markdown(report: dict[str, Any]) -> str:
    """Rend un rapport Markdown lisible."""

    summary = report["summary"]
    metrics = report["metrics"]
    training = report["training"]
    lines = [
        "# Rapport Rev4 - Neural Stock Exchange",
        "",
        "## Synthese",
        "",
        f"- Modele : `{summary['model_name']}`",
        f"- Dataset : `{summary['dataset_name']}`",
        f"- Cible : `{summary['target_column']}`",
        f"- Train rows : {summary['train_rows']}",
        f"- Test rows : {summary['test_rows']}",
        "",
        "## Metriques",
        "",
        f"- MAE : {metrics['mae']:.2f}",
        f"- RMSE : {metrics['rmse']:.2f}",
        f"- MAPE : {metrics['mape_percent']:.2f}%",
        f"- Directional accuracy : {metrics['directional_accuracy_percent']:.2f}%",
        "",
        "## Entrainement",
        "",
        f"- Sequence length : {training['sequence_length']}",
        f"- Hidden size : {training['hidden_size']}",
        f"- Epochs : {training['epochs']}",
        f"- Batch size : {training['batch_size']}",
        f"- Learning rate : {training['learning_rate']}",
        f"- Loss initiale : {training['loss_first']:.6f}",
        f"- Loss finale : {training['loss_last']:.6f}",
        "",
        "## Apercu predictions",
        "",
        "| Date | Reel | Prediction | Ecart |",
        "|---|---:|---:|---:|",
    ]
    for row in report["prediction_tail"]:
        lines.append(
            f"| {row['date']} | {row['actual']:.2f} | {row['prediction']:.2f} | {row['error']:+.2f} |"
        )

    lines.extend(
        [
            "",
            "## Limites",
            "",
            *[f"- {item}" for item in report["limitations"]],
            "",
            f"> {report['financial_disclaimer']}",
            "",
        ]
    )
    return "\n".join(lines)


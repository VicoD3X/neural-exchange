"""Reporting reproductible pour Rev4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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
        "baseline_comparison": metadata.get("baseline_comparison", []),
        "critical_evaluation": metadata.get("critical_evaluation", {}),
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
    ]

    baseline_comparison = report.get("baseline_comparison", [])
    if baseline_comparison:
        critical_evaluation = report.get("critical_evaluation", {})
        lines.extend(
            [
                "## Comparaison critique",
                "",
                f"- Verdict : {critical_evaluation.get('message', 'Evaluation critique disponible dans le rapport baseline.')}",
                "",
                "| Modele | MAE | RMSE | MAPE % | Direction % |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for row in baseline_comparison:
            lines.append(
                "| {model} | {mae:.2f} | {rmse:.2f} | {mape:.2f} | {direction:.2f} |".format(
                    model=row["model"],
                    mae=row["mae"],
                    rmse=row["rmse"],
                    mape=row["mape_percent"],
                    direction=row["directional_accuracy_percent"],
                )
            )
        lines.extend(
            [
                "",
                "Cette section compare le LSTM Rev4 a des baselines causales simples. "
                "Elle sert a verifier si le modele apporte un signal utile par rapport a des references naives.",
                "",
            ]
        )

    lines.extend(
        [
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
    )
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


def build_rev4_baseline_report(
    *,
    metadata: dict[str, Any],
    comparison: list[dict[str, Any]],
    critical_evaluation: dict[str, Any],
    prediction_frame: pd.DataFrame,
) -> dict[str, Any]:
    """Construit le rapport de comparaison critique Rev4."""

    return {
        "summary": {
            "model_name": metadata["model_name"],
            "dataset_name": metadata["dataset_name"],
            "target_column": metadata["target_column"],
            "test_rows": metadata["test_rows"],
            "best_by_mae": comparison[0]["model"] if comparison else None,
        },
        "critical_evaluation": critical_evaluation,
        "comparison": comparison,
        "prediction_preview": prediction_frame.head(10).to_dict(orient="records"),
        "prediction_tail": prediction_frame.tail(10).to_dict(orient="records"),
        "interpretation": [
            "La comparaison utilise uniquement des baselines causales simples.",
            "Une baseline naive forte peut battre un LSTM sur une serie financiere de prix.",
            "Ces resultats sont retrospectifs et ne constituent pas une preuve de prediction future.",
        ],
        "financial_disclaimer": metadata["financial_disclaimer"],
    }


def write_rev4_baseline_report(
    report: dict[str, Any],
    prediction_frame: pd.DataFrame,
    *,
    report_json_path: Path,
    report_md_path: Path,
    predictions_csv_path: Path,
) -> None:
    """Sauvegarde le rapport baseline Rev4 et les predictions completes."""

    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    report_md_path.parent.mkdir(parents=True, exist_ok=True)
    predictions_csv_path.parent.mkdir(parents=True, exist_ok=True)
    report_json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report_md_path.write_text(render_rev4_baseline_markdown(report), encoding="utf-8")
    prediction_frame.to_csv(predictions_csv_path, index=False)


def render_rev4_baseline_markdown(report: dict[str, Any]) -> str:
    """Rend le rapport de comparaison baseline en Markdown."""

    summary = report["summary"]
    critical_evaluation = report.get("critical_evaluation", {})
    lines = [
        "# Comparaison critique Rev4 - LSTM vs baselines",
        "",
        "## Synthese",
        "",
        f"- Modele : `{summary['model_name']}`",
        f"- Dataset : `{summary['dataset_name']}`",
        f"- Cible : `{summary['target_column']}`",
        f"- Test rows : {summary['test_rows']}",
        f"- Meilleur MAE : `{summary['best_by_mae']}`",
        "",
        "## Verdict",
        "",
        f"- Statut : `{critical_evaluation.get('status', 'not_evaluated')}`",
        f"- Lecture : {critical_evaluation.get('message', 'Evaluation critique non disponible.')}",
        f"- Meilleure baseline : `{critical_evaluation.get('best_baseline_model', 'n/a')}`",
        f"- Rang du LSTM par MAE : {critical_evaluation.get('lstm_rank_by_mae', 'n/a')}",
        f"- Delta MAE vs meilleure baseline : {critical_evaluation.get('mae_delta_vs_best_baseline', 0):.2f}",
        f"- Ratio MAE vs meilleure baseline : {critical_evaluation.get('mae_ratio_vs_best_baseline', 0):.2f}",
        f"- Delta direction vs meilleure baseline : {critical_evaluation.get('direction_delta_vs_best_baseline', 0):+.2f} points",
        "",
        "## Metriques",
        "",
        "| Modele | MAE | RMSE | MAPE % | Direction % |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report["comparison"]:
        lines.append(
            "| {model} | {mae:.2f} | {rmse:.2f} | {mape:.2f} | {direction:.2f} |".format(
                model=row["model"],
                mae=row["mae"],
                rmse=row["rmse"],
                mape=row["mape_percent"],
                direction=row["directional_accuracy_percent"],
            )
        )

    lines.extend(
        [
            "",
            "## Lecture",
            "",
            *[f"- {item}" for item in report["interpretation"]],
            "",
            "## Dernieres predictions",
            "",
            "| Date | Reel | LSTM | Last value | Moving average 21 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in report["prediction_tail"]:
        lines.append(
            "| {date} | {actual:.2f} | {lstm:.2f} | {last:.2f} | {ma:.2f} |".format(
                date=row["date"],
                actual=row["actual"],
                lstm=row["lstm_rev4_prediction"],
                last=row["last_value_prediction"],
                ma=row["moving_average_21_prediction"],
            )
        )

    lines.extend(["", f"> {report['financial_disclaimer']}", ""])
    return "\n".join(lines)


def plot_rev4_predictions(prediction_frame: pd.DataFrame, *, output_path: Path) -> None:
    """Genere le graphique reel vs LSTM vs baselines."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    x_values = pd.to_datetime(prediction_frame["date"])

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x_values, prediction_frame["actual"], label="Reel", linewidth=2.0)
    ax.plot(x_values, prediction_frame["lstm_rev4_prediction"], label="LSTM Rev4", linewidth=1.5)
    ax.plot(x_values, prediction_frame["last_value_prediction"], label="Last value", linewidth=1.2)
    ax.plot(
        x_values,
        prediction_frame["moving_average_21_prediction"],
        label="Moving average 21",
        linewidth=1.2,
    )
    ax.set_title("Rev4 - Reel vs LSTM vs baselines")
    ax.set_xlabel("Date")
    ax.set_ylabel("Market_Close")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=140)
    plt.close(fig)


def plot_rev4_residuals(prediction_frame: pd.DataFrame, *, output_path: Path) -> None:
    """Genere le graphique des residus."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    x_values = pd.to_datetime(prediction_frame["date"])

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axhline(0, color="#111827", linewidth=1.0)
    ax.plot(x_values, prediction_frame["lstm_rev4_residual"], label="LSTM Rev4", linewidth=1.5)
    ax.plot(x_values, prediction_frame["last_value_residual"], label="Last value", linewidth=1.2)
    ax.plot(
        x_values,
        prediction_frame["moving_average_21_residual"],
        label="Moving average 21",
        linewidth=1.2,
    )
    ax.set_title("Rev4 - Residus")
    ax.set_xlabel("Date")
    ax.set_ylabel("Prediction - reel")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=140)
    plt.close(fig)

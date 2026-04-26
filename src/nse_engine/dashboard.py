"""Export public des donnees de dashboard Rev4."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from nse_engine.config import (
    DOW_MACRO_REV4_FEATURES_PATH,
    FINANCIAL_DISCLAIMER,
    PROJECT_ROOT,
    REV4_BASELINE_REPORT_JSON_PATH,
    REV4_DIRECTION_ACCURACY_PNG_PATH,
    REV4_ERROR_DISTRIBUTION_PNG_PATH,
    REV4_FORECAST_OVERVIEW_PNG_PATH,
    REV4_MARKET_CONTEXT_PANIC_MODE_PNG_PATH,
    REV4_METADATA_PATH,
    REV4_METRICS_COMPARISON_PNG_PATH,
    REV4_PREDICTIONS_CSV_PATH,
    REV4_REPORT_JSON_PATH,
    REV4_REPORTS_DIR,
    REV4_RESIDUALS_PNG_PATH,
)

DASHBOARD_DATA_PATH = REV4_REPORTS_DIR / "dashboard_data.json"

REQUIRED_DASHBOARD_KEYS = {
    "metadata",
    "summary",
    "metrics",
    "critical_evaluation",
    "baseline_comparison",
    "regime_analysis",
    "charts",
    "artifacts",
    "limitations",
    "financial_disclaimer",
}


def build_dashboard_data(
    *,
    training_report_path: Path = REV4_REPORT_JSON_PATH,
    baseline_report_path: Path = REV4_BASELINE_REPORT_JSON_PATH,
    predictions_csv_path: Path = REV4_PREDICTIONS_CSV_PATH,
    feature_dataset_path: Path = DOW_MACRO_REV4_FEATURES_PATH,
    metadata_path: Path = REV4_METADATA_PATH,
) -> dict[str, Any]:
    """Construit un export JSON public sans relancer l'entrainement."""

    training_report = _read_json(training_report_path)
    baseline_report = _read_json(baseline_report_path)
    model_metadata = _read_json(metadata_path) if metadata_path.exists() else {}

    predictions = _read_predictions(predictions_csv_path)
    features = _read_features(feature_dataset_path)
    regime_analysis = build_regime_analysis(predictions, features)

    dashboard_data = {
        "metadata": {
            "generated_at": datetime.now(UTC).isoformat(),
            "project": "Neural Stock Exchange",
            "engine": "nse-engine Rev4",
            "source_files": {
                "training_report": _relative_path(training_report_path),
                "baseline_report": _relative_path(baseline_report_path),
                "predictions": _relative_path(predictions_csv_path),
                "feature_dataset": _relative_path(feature_dataset_path)
                if feature_dataset_path.exists()
                else None,
                "model_metadata": _relative_path(metadata_path) if metadata_path.exists() else None,
            },
            "data_scope": "Export public derive des rapports Rev4. Aucun appel reseau.",
        },
        "summary": {
            **training_report.get("summary", {}),
            "best_by_mae": baseline_report.get("summary", {}).get("best_by_mae"),
            "features_count": len(training_report.get("features", [])),
        },
        "metrics": training_report.get("metrics", {}),
        "critical_evaluation": baseline_report.get(
            "critical_evaluation", training_report.get("critical_evaluation", {})
        ),
        "baseline_comparison": baseline_report.get(
            "comparison", training_report.get("baseline_comparison", [])
        ),
        "regime_analysis": regime_analysis,
        "charts": _build_chart_manifest(),
        "artifacts": {
            "model": "models/rev4/nse_lstm_rev4_dow_macro.pt",
            "scaler": "models/rev4/nse_lstm_rev4_dow_macro_scaler.joblib",
            "metadata": "models/rev4/nse_lstm_rev4_dow_macro.metadata.json",
            "reports": [
                "reports/rev4/rev4_training_report.md",
                "reports/rev4/rev4_baseline_comparison.md",
            ],
        },
        "legacy": {
            "rev2": "Archive historique non reproductible completement.",
            "rev25": "Archive historique avec apparition du signal Panic_Mode.",
            "rev3": "Legacy-advanced conserve comme inspiration technique.",
            "gold": "Ancien LSTM Gold recupere pour demonstration primitive.",
        },
        "features": training_report.get("features", model_metadata.get("feature_columns", [])),
        "prediction_preview": baseline_report.get("prediction_preview", []),
        "prediction_tail": baseline_report.get("prediction_tail", []),
        "limitations": [
            "Projet experimental local, sans conseil financier.",
            "Evaluation retrospective, non suffisante pour valider une prediction future.",
            "Le LSTM Rev4 ne bat pas la baseline last_value sur le MAE actuel.",
            "Panic_Mode est un indicateur de stress base volatilite, pas un detecteur fiable de crise.",
        ],
        "financial_disclaimer": training_report.get("financial_disclaimer", FINANCIAL_DISCLAIMER),
    }
    validate_dashboard_data(dashboard_data)
    return dashboard_data


def write_dashboard_data(data: dict[str, Any], output_path: Path = DASHBOARD_DATA_PATH) -> None:
    """Ecrit le JSON dashboard public."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_dashboard_data(path: Path = DASHBOARD_DATA_PATH) -> dict[str, Any]:
    """Charge et valide un export dashboard."""

    data = _read_json(path)
    validate_dashboard_data(data)
    return data


def validate_dashboard_data(data: dict[str, Any]) -> None:
    """Valide les cles principales attendues par Streamlit et React."""

    missing = sorted(REQUIRED_DASHBOARD_KEYS - set(data))
    if missing:
        raise ValueError(f"dashboard_data.json incomplet. Cles absentes: {', '.join(missing)}")


def build_regime_analysis(predictions: pd.DataFrame, features: pd.DataFrame) -> dict[str, Any]:
    """Analyse les erreurs par regime temporel et Panic_Mode si possible."""

    if predictions.empty:
        return {
            "status": "unavailable",
            "message": "Aucune prediction disponible pour l'analyse par regime.",
            "segments": [],
        }

    frame = predictions.copy()
    frame["date"] = pd.to_datetime(frame["date"])

    if not features.empty and {"Date", "Panic_Mode"}.issubset(features.columns):
        feature_frame = features[["Date", "Panic_Mode", "Volatility_1M"]].copy()
        feature_frame["Date"] = pd.to_datetime(feature_frame["Date"])
        frame = frame.merge(feature_frame, left_on="date", right_on="Date", how="left")
        frame.drop(columns=["Date"], inplace=True)
    else:
        frame["Panic_Mode"] = np.nan
        frame["Volatility_1M"] = np.nan

    segments = [
        _segment_metrics("test_complet", "Periode de test complete", frame),
        _segment_metrics("hors_panic_mode", "Hors Panic_Mode", frame[frame["Panic_Mode"] == 0]),
        _segment_metrics("panic_mode", "Panic_Mode", frame[frame["Panic_Mode"] == 1]),
        _segment_metrics("annee_2009", "Annee 2009", frame[frame["date"].dt.year == 2009]),
        _segment_metrics("annee_2010", "Annee 2010", frame[frame["date"].dt.year == 2010]),
    ]

    panic_rows = int((frame["Panic_Mode"] == 1).sum()) if "Panic_Mode" in frame else 0
    return {
        "status": "available",
        "message": (
            "Analyse retrospective par regime. Les groupes courts doivent etre lus avec prudence."
        ),
        "test_start": frame["date"].min().date().isoformat(),
        "test_end": frame["date"].max().date().isoformat(),
        "panic_mode_rows_in_test": panic_rows,
        "segments": segments,
    }


def _segment_metrics(segment_id: str, label: str, frame: pd.DataFrame) -> dict[str, Any]:
    if len(frame) < 3:
        return {
            "id": segment_id,
            "label": label,
            "rows": int(len(frame)),
            "status": "insufficient_data",
            "metrics": {},
        }

    metrics: dict[str, Any] = {}
    for model in ("lstm_rev4", "last_value", "moving_average_21"):
        residual_column = f"{model}_residual"
        if residual_column not in frame.columns:
            continue
        residuals = frame[residual_column].astype(float)
        actuals = frame["actual"].astype(float)
        metrics[model] = {
            "mae": float(residuals.abs().mean()),
            "rmse": float(np.sqrt(np.mean(residuals**2))),
            "mape_percent": float((residuals.abs() / actuals).mean() * 100),
        }

    best_by_mae = min(metrics.items(), key=lambda item: item[1]["mae"])[0] if metrics else None
    return {
        "id": segment_id,
        "label": label,
        "rows": int(len(frame)),
        "status": "available",
        "best_by_mae": best_by_mae,
        "metrics": metrics,
    }


def _build_chart_manifest() -> list[dict[str, str]]:
    charts = [
        ("market_context", "Contexte marche et Panic_Mode", REV4_MARKET_CONTEXT_PANIC_MODE_PNG_PATH),
        ("forecast_overview", "Reel vs LSTM vs baselines", REV4_FORECAST_OVERVIEW_PNG_PATH),
        ("metrics_comparison", "Comparaison des metriques", REV4_METRICS_COMPARISON_PNG_PATH),
        ("residuals", "Residus", REV4_RESIDUALS_PNG_PATH),
        ("error_distribution", "Distribution des erreurs", REV4_ERROR_DISTRIBUTION_PNG_PATH),
        ("direction_accuracy", "Direction accuracy", REV4_DIRECTION_ACCURACY_PNG_PATH),
    ]
    return [
        {
            "id": chart_id,
            "title": title,
            "path": _relative_path(path),
        }
        for chart_id, title, path in charts
    ]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {_relative_path(path)}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_predictions(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _read_features(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()

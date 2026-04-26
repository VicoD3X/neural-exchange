"""Pipeline d'entrainement Rev4 reproductible."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import torch

from nse_engine.config import (
    FINANCIAL_DISCLAIMER,
    REV4_ACTUAL_VS_PREDICTIONS_PNG_PATH,
    REV4_BASELINE_REPORT_JSON_PATH,
    REV4_BASELINE_REPORT_MD_PATH,
    REV4_BATCH_SIZE,
    REV4_EPOCHS,
    REV4_HIDDEN_SIZE,
    REV4_LEARNING_RATE,
    REV4_METADATA_PATH,
    REV4_MODEL_PATH,
    REV4_PRIMARY_DATASET_NAME,
    REV4_PRIMARY_DATASET_PATH,
    REV4_RANDOM_SEED,
    REV4_REPORT_JSON_PATH,
    REV4_REPORT_MD_PATH,
    REV4_RESIDUALS_PNG_PATH,
    REV4_SCALER_PATH,
    REV4_SEQUENCE_LENGTH,
    REV4_TRAIN_RATIO,
    REV4_PREDICTIONS_CSV_PATH,
)
from nse_engine.evaluation import (
    build_naive_baselines,
    build_prediction_frame,
    compare_prediction_sets,
    compute_regression_metrics,
)
from nse_engine.lstm import Rev4LSTMModel, predict_scaled, set_reproducible_seed, train_lstm_model
from nse_engine.reporting import (
    build_rev4_baseline_report,
    build_rev4_report,
    plot_rev4_predictions,
    plot_rev4_residuals,
    write_rev4_baseline_report,
    write_rev4_report,
)
from nse_engine.sequences import build_rev4_sequences, inverse_transform_target, load_rev4_dataset


def train_rev4_pipeline(
    *,
    dataset_path: Path = REV4_PRIMARY_DATASET_PATH,
    model_path: Path = REV4_MODEL_PATH,
    scaler_path: Path = REV4_SCALER_PATH,
    metadata_path: Path = REV4_METADATA_PATH,
    report_json_path: Path = REV4_REPORT_JSON_PATH,
    report_md_path: Path = REV4_REPORT_MD_PATH,
    baseline_report_json_path: Path = REV4_BASELINE_REPORT_JSON_PATH,
    baseline_report_md_path: Path = REV4_BASELINE_REPORT_MD_PATH,
    predictions_csv_path: Path = REV4_PREDICTIONS_CSV_PATH,
    prediction_plot_path: Path = REV4_ACTUAL_VS_PREDICTIONS_PNG_PATH,
    residual_plot_path: Path = REV4_RESIDUALS_PNG_PATH,
) -> dict[str, Any]:
    """Entraine le modele Rev4 principal et sauvegarde artefacts + rapport."""

    set_reproducible_seed(REV4_RANDOM_SEED)
    df = load_rev4_dataset(dataset_path)
    sequences = build_rev4_sequences(df)

    model = Rev4LSTMModel(
        input_size=sequences.x_train.shape[2],
        hidden_size=REV4_HIDDEN_SIZE,
    )
    history = train_lstm_model(
        model,
        sequences.x_train,
        sequences.y_train,
        epochs=REV4_EPOCHS,
        batch_size=REV4_BATCH_SIZE,
        learning_rate=REV4_LEARNING_RATE,
    )
    predictions_scaled = predict_scaled(model, sequences.x_test)

    predictions = inverse_transform_target(
        predictions_scaled,
        scaler=sequences.scaler,
        n_features=len(sequences.feature_columns),
        target_index=sequences.target_index,
    )
    actuals = inverse_transform_target(
        sequences.y_test.reshape(-1),
        scaler=sequences.scaler,
        n_features=len(sequences.feature_columns),
        target_index=sequences.target_index,
    )
    metrics = compute_regression_metrics(actuals, predictions)
    baselines = build_naive_baselines(
        df,
        target_column=sequences.target_column,
        train_rows=sequences.train_rows,
    )
    prediction_sets = {"lstm_rev4": predictions, **baselines}
    comparison = compare_prediction_sets(actuals=actuals, predictions=prediction_sets)
    prediction_frame = build_prediction_frame(
        dates=sequences.test_dates,
        actuals=actuals,
        predictions=prediction_sets,
    )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    scaler_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_path)
    joblib.dump(sequences.scaler, scaler_path)

    metadata = {
        "model_name": "nse-lstm-rev4-dow-macro",
        "dataset_name": REV4_PRIMARY_DATASET_NAME,
        "dataset_path": _relative_path(dataset_path),
        "generated_at": datetime.now(UTC).isoformat(),
        "feature_columns": sequences.feature_columns,
        "target_column": sequences.target_column,
        "sequence_length": REV4_SEQUENCE_LENGTH,
        "train_ratio": REV4_TRAIN_RATIO,
        "train_rows": sequences.train_rows,
        "test_rows": sequences.test_rows,
        "input_size": sequences.x_train.shape[2],
        "hidden_size": REV4_HIDDEN_SIZE,
        "epochs": REV4_EPOCHS,
        "batch_size": REV4_BATCH_SIZE,
        "learning_rate": REV4_LEARNING_RATE,
        "random_seed": REV4_RANDOM_SEED,
        "metrics": metrics,
        "baseline_comparison": comparison,
        "artifacts": {
            "model_path": _relative_path(model_path),
            "scaler_path": _relative_path(scaler_path),
            "metadata_path": _relative_path(metadata_path),
            "baseline_report_json_path": _relative_path(baseline_report_json_path),
            "baseline_report_md_path": _relative_path(baseline_report_md_path),
            "predictions_csv_path": _relative_path(predictions_csv_path),
            "prediction_plot_path": _relative_path(prediction_plot_path),
            "residual_plot_path": _relative_path(residual_plot_path),
        },
        "final_train_loss": history.losses[-1],
        "financial_disclaimer": FINANCIAL_DISCLAIMER,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    report = build_rev4_report(
        metadata=metadata,
        test_dates=sequences.test_dates,
        actuals=actuals,
        predictions=predictions,
        losses=history.losses,
    )
    write_rev4_report(report, report_json_path=report_json_path, report_md_path=report_md_path)
    baseline_report = build_rev4_baseline_report(
        metadata=metadata,
        comparison=comparison,
        prediction_frame=prediction_frame,
    )
    write_rev4_baseline_report(
        baseline_report,
        prediction_frame,
        report_json_path=baseline_report_json_path,
        report_md_path=baseline_report_md_path,
        predictions_csv_path=predictions_csv_path,
    )
    plot_rev4_predictions(prediction_frame, output_path=prediction_plot_path)
    plot_rev4_residuals(prediction_frame, output_path=residual_plot_path)
    return metadata


def _relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()

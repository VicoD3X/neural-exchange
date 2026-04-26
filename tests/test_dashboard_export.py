from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from nse_engine.dashboard import (
    build_dashboard_data,
    build_regime_analysis,
    validate_dashboard_data,
    write_dashboard_data,
)


def test_dashboard_data_contains_required_keys() -> None:
    data = build_dashboard_data()

    validate_dashboard_data(data)
    assert data["summary"]["dataset_name"] == "dow_macro_rev4_features"
    assert data["critical_evaluation"]["best_baseline_model"] == "last_value"
    assert data["financial_disclaimer"]


def test_dashboard_chart_paths_exist() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data = build_dashboard_data()

    missing = [chart["path"] for chart in data["charts"] if not (project_root / chart["path"]).exists()]

    assert missing == []


def test_write_dashboard_data_outputs_json(tmp_path: Path) -> None:
    data = build_dashboard_data()
    output_path = tmp_path / "dashboard_data.json"

    write_dashboard_data(data, output_path)
    loaded = json.loads(output_path.read_text(encoding="utf-8"))

    assert loaded["metadata"]["project"] == "Neural Stock Exchange"
    assert "baseline_comparison" in loaded


def test_dashboard_validation_reports_missing_key() -> None:
    with pytest.raises(ValueError, match="Cles absentes"):
        validate_dashboard_data({"summary": {}})


def test_regime_analysis_handles_missing_panic_mode() -> None:
    predictions = pd.DataFrame(
        {
            "date": ["2010-01-01", "2010-01-02", "2010-01-03"],
            "actual": [100.0, 101.0, 102.0],
            "lstm_rev4_residual": [1.0, -1.0, 2.0],
            "last_value_residual": [0.5, -0.5, 1.0],
            "moving_average_21_residual": [1.5, -1.5, 2.5],
        }
    )

    analysis = build_regime_analysis(predictions, pd.DataFrame())

    assert analysis["status"] == "available"
    assert analysis["segments"][0]["status"] == "available"

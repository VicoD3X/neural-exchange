from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from nse_engine.config import (
    DOW_MACRO_REV4_FEATURES_PATH,
    GOLD_FEATURE_COLUMNS,
    MARKET_MACRO_REV4_FEATURES_PATH,
)
from nse_engine.legacy_models import (
    DOW_MACRO_LEGACY_SPEC,
    GOLD_LEGACY_SPEC,
    build_gold_sequences,
    dow_macro_legacy_dry_run,
    infer_lstm_spec_from_state_dict,
    load_legacy_model,
    load_state_dict,
    predict_gold_legacy,
)


def test_legacy_state_dict_shapes_are_known() -> None:
    gold_state = load_state_dict(GOLD_LEGACY_SPEC.path)
    dow_state = load_state_dict(DOW_MACRO_LEGACY_SPEC.path)

    assert infer_lstm_spec_from_state_dict(gold_state) == (5, 64)
    assert infer_lstm_spec_from_state_dict(dow_state) == (13, 50)


def test_gold_legacy_model_loads_and_predicts_primitive_value(tmp_path: Path) -> None:
    df = _synthetic_gold_frame()
    data_path = tmp_path / "gold_features.csv"
    df.to_csv(data_path, index=False)
    model = load_legacy_model(GOLD_LEGACY_SPEC)
    prediction = predict_gold_legacy(data_path=data_path)

    assert model.training is False
    assert prediction.sequence_shape == (1, 6, 5)
    assert prediction.target_date == "2003-01-20"
    assert math.isfinite(prediction.predicted_gold_close)
    assert prediction.actual_gold_close > 0


def test_gold_legacy_sequences_are_rebuilt_from_synthetic_dataset() -> None:
    df = _synthetic_gold_frame()
    sequences, targets, _ = build_gold_sequences(df)

    assert sequences.shape[1:] == (6, 5)
    assert len(sequences) == len(targets)
    assert len(sequences) == 14


def test_dow_macro_legacy_is_only_architecture_dry_run() -> None:
    input_size, hidden_size, output_shape = dow_macro_legacy_dry_run()

    assert input_size == 13
    assert hidden_size == 50
    assert output_shape == (1, 1)


def test_dow_macro_legacy_is_not_bound_to_rev4_datasets() -> None:
    rev4_paths = {DOW_MACRO_REV4_FEATURES_PATH.name, MARKET_MACRO_REV4_FEATURES_PATH.name}

    assert DOW_MACRO_LEGACY_SPEC.status == "archive_rev2_non_connectee"
    assert DOW_MACRO_LEGACY_SPEC.path.name == "nse_lstm_combined.pt"
    assert DOW_MACRO_LEGACY_SPEC.path.name not in rev4_paths


def _synthetic_gold_frame() -> pd.DataFrame:
    dates = pd.date_range("2003-01-01", periods=20, freq="D")
    close = [1000 + index * 2 for index in range(20)]
    df = pd.DataFrame(
        {
            "Date": dates,
            "Gold_Close": close,
            "Gold_Close_Log": [math.log(value) for value in close],
            "Gold_Close_WMA": close,
            "Gold_Close_EMA": close,
            "Momentum": [0.0, *[0.002] * 19],
        }
    )
    assert list(GOLD_FEATURE_COLUMNS) == [
        "Gold_Close",
        "Gold_Close_Log",
        "Gold_Close_WMA",
        "Gold_Close_EMA",
        "Momentum",
    ]
    return df

from __future__ import annotations

import math

from nse_engine.config import (
    DOW_MACRO_REV4_FEATURES_PATH,
    MARKET_MACRO_REV4_FEATURES_PATH,
)
from nse_engine.legacy_models import (
    DOW_MACRO_LEGACY_SPEC,
    GOLD_LEGACY_SPEC,
    build_gold_sequences,
    dow_macro_legacy_dry_run,
    infer_lstm_spec_from_state_dict,
    load_gold_features,
    load_legacy_model,
    load_state_dict,
    predict_gold_legacy,
)


def test_legacy_state_dict_shapes_are_known() -> None:
    gold_state = load_state_dict(GOLD_LEGACY_SPEC.path)
    dow_state = load_state_dict(DOW_MACRO_LEGACY_SPEC.path)

    assert infer_lstm_spec_from_state_dict(gold_state) == (5, 64)
    assert infer_lstm_spec_from_state_dict(dow_state) == (13, 50)


def test_gold_legacy_model_loads_and_predicts_primitive_value() -> None:
    model = load_legacy_model(GOLD_LEGACY_SPEC)
    prediction = predict_gold_legacy()

    assert model.training is False
    assert prediction.sequence_shape == (1, 6, 5)
    assert prediction.target_date == "2010-12-30"
    assert math.isfinite(prediction.predicted_gold_close)
    assert prediction.actual_gold_close > 0


def test_gold_legacy_sequences_are_rebuilt_from_generated_dataset() -> None:
    df = load_gold_features()
    sequences, targets, _ = build_gold_sequences(df)

    assert sequences.shape[1:] == (6, 5)
    assert len(sequences) == len(targets)
    assert len(sequences) > 1000


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


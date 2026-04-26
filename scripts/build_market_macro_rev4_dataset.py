"""Genere le dataset Market/Macro Rev4 depuis FRED public."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> None:
    from nse_engine.config import (
        MACRO_SOURCE,
        MARKET_MACRO_REV4_FEATURES_PATH,
        REV4_END_DATE,
        REV4_MARKET_CLOSE_COLUMN,
        REV4_MARKET_NAME,
        REV4_MARKET_SERIES,
        REV4_START_DATE,
    )
    from nse_engine.data_cleaning import clean_market_dataframe, reject_uncontrolled_missing_values
    from nse_engine.data_sources import fetch_fred_macro, fetch_fred_market_series
    from nse_engine.features import add_rev4_market_features, dow_macro_rev4_feature_columns
    from nse_engine.metadata import build_dataset_metadata

    market_raw = fetch_fred_market_series(
        REV4_MARKET_SERIES,
        REV4_START_DATE,
        REV4_END_DATE,
        value_column=REV4_MARKET_CLOSE_COLUMN,
    )
    market = clean_market_dataframe(market_raw, ["Date", REV4_MARKET_CLOSE_COLUMN])
    macro = fetch_fred_macro(REV4_START_DATE, REV4_END_DATE)
    merged = market.merge(macro, on="Date", how="inner")
    features = add_rev4_market_features(merged)
    reject_uncontrolled_missing_values(features, ["Date", *dow_macro_rev4_feature_columns()])

    MARKET_MACRO_REV4_FEATURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(MARKET_MACRO_REV4_FEATURES_PATH, index=False)
    metadata = build_dataset_metadata(
        dataset_name="market_macro_rev4_features",
        source=f"{MACRO_SOURCE}:{REV4_MARKET_SERIES}+macro",
        output_path=MARKET_MACRO_REV4_FEATURES_PATH,
        requested_start=REV4_START_DATE,
        requested_end=REV4_END_DATE,
        df=features,
        raw_rows=len(market_raw),
        notes=[
            f"Indice marche Rev4: {REV4_MARKET_NAME}.",
            "Source unique FRED public pour eviter le rate limit Yahoo sur ^DJI.",
        ],
    )
    MARKET_MACRO_REV4_FEATURES_PATH.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Dataset Market/Macro Rev4 genere: {MARKET_MACRO_REV4_FEATURES_PATH}")


if __name__ == "__main__":
    main()

"""Genere le dataset Dow/Macro Rev4 depuis yfinance et FRED public."""

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
        DOW_JONES_MARKET_NAME,
        DOW_JONES_TICKER,
        DOW_MACRO_REV4_FEATURES_PATH,
        MACRO_SOURCE,
        MARKET_SOURCE,
        REV4_END_DATE,
        REV4_MARKET_CLOSE_COLUMN,
        REV4_START_DATE,
    )
    from nse_engine.data_cleaning import clean_market_dataframe, reject_uncontrolled_missing_values
    from nse_engine.data_sources import fetch_fred_macro, fetch_yfinance_history
    from nse_engine.features import add_rev4_market_features, dow_macro_rev4_feature_columns
    from nse_engine.metadata import build_dataset_metadata

    market_raw = fetch_yfinance_history(DOW_JONES_TICKER, REV4_START_DATE, REV4_END_DATE)
    price_column = "Adj Close" if "Adj Close" in market_raw.columns else "Close"
    market_raw[REV4_MARKET_CLOSE_COLUMN] = market_raw[price_column]
    market = clean_market_dataframe(market_raw, ["Date", REV4_MARKET_CLOSE_COLUMN])
    macro = fetch_fred_macro(REV4_START_DATE, REV4_END_DATE)
    merged = market.merge(macro, on="Date", how="inner")
    features = add_rev4_market_features(merged)
    reject_uncontrolled_missing_values(features, ["Date", *dow_macro_rev4_feature_columns()])

    DOW_MACRO_REV4_FEATURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(DOW_MACRO_REV4_FEATURES_PATH, index=False)
    metadata = build_dataset_metadata(
        dataset_name="dow_macro_rev4_features",
        source=f"{MARKET_SOURCE}:{DOW_JONES_TICKER}+{MACRO_SOURCE}:macro",
        output_path=DOW_MACRO_REV4_FEATURES_PATH,
        requested_start=REV4_START_DATE,
        requested_end=REV4_END_DATE,
        df=features,
        raw_rows=len(market_raw),
        notes=[
            f"Indice marche Rev4: {DOW_JONES_MARKET_NAME}.",
            "Generation permise apres upgrade yfinance vers 1.3.0.",
        ],
    )
    DOW_MACRO_REV4_FEATURES_PATH.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Dataset Dow/Macro Rev4 genere: {DOW_MACRO_REV4_FEATURES_PATH}")


if __name__ == "__main__":
    main()

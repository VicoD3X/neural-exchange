"""Prepare la generation future du dataset Gold propre."""

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
        GOLD_FEATURES_PATH,
        GOLD_TICKER,
        MARKET_SOURCE,
        REV4_END_DATE,
        REV4_START_DATE,
    )
    from nse_engine.data_cleaning import clean_market_dataframe, reject_uncontrolled_missing_values
    from nse_engine.data_sources import fetch_yfinance_history
    from nse_engine.features import add_gold_features, gold_feature_columns
    from nse_engine.metadata import build_dataset_metadata

    raw = fetch_yfinance_history(GOLD_TICKER, REV4_START_DATE, REV4_END_DATE)
    price_column = "Adj Close" if "Adj Close" in raw.columns else "Close"
    raw["Gold_Close"] = raw[price_column]
    clean = clean_market_dataframe(raw, ["Date", "Gold_Close"])
    features = add_gold_features(clean)
    reject_uncontrolled_missing_values(features, ["Date", *gold_feature_columns()])

    GOLD_FEATURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(GOLD_FEATURES_PATH, index=False)
    metadata = build_dataset_metadata(
        dataset_name="gold_features",
        source=MARKET_SOURCE,
        output_path=GOLD_FEATURES_PATH,
        requested_start=REV4_START_DATE,
        requested_end=REV4_END_DATE,
        df=features,
        raw_rows=len(raw),
        notes=["Dataset genere via script preparatoire Bloc 3."],
    )
    GOLD_FEATURES_PATH.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Dataset Gold genere: {GOLD_FEATURES_PATH}")


if __name__ == "__main__":
    main()

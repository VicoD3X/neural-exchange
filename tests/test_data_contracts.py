from __future__ import annotations

from nse_engine.config import (
    GOLD_FEATURE_COLUMNS,
    MARKET_MACRO_REV4_FEATURE_COLUMNS,
    REV4_END_DATE,
    REV4_MARKET_CLOSE_COLUMN,
    REV4_MARKET_SERIES,
    REV4_START_DATE,
)
from nse_engine.features import dow_macro_rev4_feature_columns, gold_feature_columns


def test_gold_feature_contract_is_explicit() -> None:
    assert gold_feature_columns() == list(GOLD_FEATURE_COLUMNS)
    assert "Gold_Close" in gold_feature_columns()
    assert "Momentum" in gold_feature_columns()


def test_rev4_contract_is_explicit_and_dated() -> None:
    assert REV4_START_DATE == "2003-01-01"
    assert REV4_END_DATE == "2010-12-31"
    assert REV4_MARKET_SERIES == "NASDAQCOM"
    assert dow_macro_rev4_feature_columns() == list(MARKET_MACRO_REV4_FEATURE_COLUMNS)
    assert REV4_MARKET_CLOSE_COLUMN in dow_macro_rev4_feature_columns()
    assert "Panic_Mode" in dow_macro_rev4_feature_columns()
    assert "FEDFUNDS" in dow_macro_rev4_feature_columns()

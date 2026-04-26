from __future__ import annotations

import pandas as pd
import pytest

from nse_engine.data_cleaning import (
    clean_market_dataframe,
    reject_uncontrolled_missing_values,
    validate_schema,
)


def test_clean_market_dataframe_removes_invalid_dates_and_converts_numeric_values() -> None:
    raw = pd.DataFrame(
        {
            "Date": ["Ticker", "2003-01-02", "2003-01-03"],
            "DJI_Close": ["^DJI", "8500.5", "bad"],
            "DJI_Volume": ["^DJI", "1000", "2000"],
        }
    )

    clean = clean_market_dataframe(raw, ["Date", "DJI_Close", "DJI_Volume"])

    assert len(clean) == 1
    assert clean.loc[0, "Date"].strftime("%Y-%m-%d") == "2003-01-02"
    assert clean.loc[0, "DJI_Close"] == 8500.5


def test_validate_schema_reports_missing_columns() -> None:
    validation = validate_schema(pd.DataFrame({"Date": []}), ["Date", "Gold_Close"])

    assert not validation.is_valid
    assert validation.missing_columns == ["Gold_Close"]


def test_reject_uncontrolled_missing_values_raises_with_details() -> None:
    df = pd.DataFrame({"Date": ["2003-01-01"], "Value": [None]})

    with pytest.raises(ValueError, match="Value=1"):
        reject_uncontrolled_missing_values(df, ["Value"])


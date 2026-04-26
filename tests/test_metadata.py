from __future__ import annotations

from pathlib import Path

import pandas as pd

from nse_engine.metadata import build_dataset_metadata


def test_build_dataset_metadata_contains_required_fields() -> None:
    df = pd.DataFrame(
        {
            "Date": ["2003-01-01", "2003-01-02"],
            "Value": [1.0, 2.0],
        }
    )

    metadata = build_dataset_metadata(
        dataset_name="test_dataset",
        source="unit-test",
        output_path=Path("data/processed/test.csv"),
        requested_start="2003-01-01",
        requested_end="2010-12-31",
        df=df,
        raw_rows=3,
    )

    assert metadata["dataset_name"] == "test_dataset"
    assert metadata["raw_rows"] == 3
    assert metadata["clean_rows"] == 2
    assert metadata["observed_start"] == "2003-01-01"
    assert metadata["observed_end"] == "2003-01-02"
    assert metadata["output_path"] == "data/processed/test.csv"
    assert set(["dataset_name", "source", "columns", "missing_values", "financial_disclaimer"]).issubset(metadata)
    assert "conseil financier" in metadata["financial_disclaimer"]

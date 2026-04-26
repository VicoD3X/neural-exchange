"""Generation de metadata pour datasets regeneres."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from nse_engine.config import FINANCIAL_DISCLAIMER


def build_dataset_metadata(
    *,
    dataset_name: str,
    source: str,
    output_path: Path,
    requested_start: str,
    requested_end: str,
    df: pd.DataFrame,
    raw_rows: int | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    """Construit une metadata lisible et versionnable."""

    try:
        normalized_output_path = output_path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        normalized_output_path = output_path.as_posix()

    date_min = None
    date_max = None
    if "Date" in df.columns and not df.empty:
        dates = pd.to_datetime(df["Date"], errors="coerce").dropna()
        if not dates.empty:
            date_min = dates.min().date().isoformat()
            date_max = dates.max().date().isoformat()

    return {
        "dataset_name": dataset_name,
        "source": source,
        "output_path": normalized_output_path,
        "generated_at": datetime.now(UTC).isoformat(),
        "requested_start": requested_start,
        "requested_end": requested_end,
        "observed_start": date_min,
        "observed_end": date_max,
        "raw_rows": raw_rows if raw_rows is not None else len(df),
        "clean_rows": len(df),
        "columns": list(df.columns),
        "missing_values": {column: int(count) for column, count in df.isna().sum().items()},
        "notes": notes or [],
        "financial_disclaimer": FINANCIAL_DISCLAIMER,
    }

"""Nettoyage strict des futurs exports de marche et macro."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SchemaValidation:
    """Resultat simple de validation de schema."""

    is_valid: bool
    missing_columns: list[str]
    extra_columns: list[str]


def validate_schema(df: pd.DataFrame, required_columns: list[str]) -> SchemaValidation:
    """Verifie que les colonnes attendues sont presentes."""

    missing = [column for column in required_columns if column not in df.columns]
    extra = [column for column in df.columns if column not in required_columns]
    return SchemaValidation(is_valid=not missing, missing_columns=missing, extra_columns=extra)


def clean_market_dataframe(
    df: pd.DataFrame,
    required_columns: list[str],
    *,
    date_column: str = "Date",
    drop_missing: bool = True,
) -> pd.DataFrame:
    """Nettoie un DataFrame financier sans supposer sa provenance exacte."""

    if date_column not in df.columns:
        raise ValueError(f"Colonne de date absente: {date_column}")

    working = df.copy()
    working[date_column] = pd.to_datetime(working[date_column], errors="coerce", format="mixed")
    working = working.dropna(subset=[date_column])

    missing_columns = [column for column in required_columns if column not in working.columns]
    if missing_columns:
        raise ValueError(f"Colonnes manquantes: {', '.join(missing_columns)}")

    numeric_columns = [column for column in required_columns if column != date_column]
    for column in numeric_columns:
        working[column] = pd.to_numeric(working[column], errors="coerce")

    if drop_missing:
        working = working.dropna(subset=required_columns)

    working = working.sort_values(date_column).reset_index(drop=True)
    return working[required_columns]


def reject_uncontrolled_missing_values(df: pd.DataFrame, columns: list[str]) -> None:
    """Leve une erreur si des NaN restent dans les colonnes critiques."""

    missing_counts = df[columns].isna().sum()
    uncontrolled = missing_counts[missing_counts > 0]
    if not uncontrolled.empty:
        details = ", ".join(f"{column}={count}" for column, count in uncontrolled.items())
        raise ValueError(f"Valeurs manquantes non maitrisees: {details}")

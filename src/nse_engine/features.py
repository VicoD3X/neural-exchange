"""Definitions de features pour Gold legacy et Dow/Macro Rev4."""

from __future__ import annotations

import numpy as np
import pandas as pd

from nse_engine.config import (
    DOW_MACRO_REV4_FEATURE_COLUMNS,
    GOLD_FEATURE_COLUMNS,
    REV4_MARKET_CLOSE_COLUMN,
    REV4_ENGINEERED_COLUMNS,
)


def add_gold_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les features Gold historiques a partir de Gold_Close."""

    if "Gold_Close" not in df.columns:
        raise ValueError("Colonne Gold_Close absente.")

    working = df.copy()
    working["Gold_Close_Log"] = np.log(working["Gold_Close"])
    working["Gold_Close_WMA"] = (
        working["Gold_Close"]
        .rolling(window=3)
        .apply(lambda values: 0.5 * values[-1] + 0.3 * values[-2] + 0.2 * values[-3], raw=True)
    )
    working["Gold_Close_EMA"] = working["Gold_Close"].ewm(span=3, adjust=False).mean()
    working["Momentum"] = working["Gold_Close"].pct_change()
    return working.dropna(subset=GOLD_FEATURE_COLUMNS).reset_index(drop=True)


def add_rev4_market_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les features de volatilite et Panic_Mode candidates pour Rev4."""

    if REV4_MARKET_CLOSE_COLUMN not in df.columns:
        raise ValueError(f"Colonne {REV4_MARKET_CLOSE_COLUMN} absente.")

    working = df.copy()
    returns = working[REV4_MARKET_CLOSE_COLUMN].pct_change()
    working["Volatility_1W"] = returns.rolling(window=5).std()
    working["Volatility_1M"] = returns.rolling(window=21).std()
    threshold = working["Volatility_1M"].quantile(0.95)
    working["Panic_Mode"] = (working["Volatility_1M"] >= threshold).astype(int)
    return working.dropna(subset=REV4_ENGINEERED_COLUMNS).reset_index(drop=True)


def gold_feature_columns() -> list[str]:
    """Retourne les features Gold attendues."""

    return list(GOLD_FEATURE_COLUMNS)


def dow_macro_rev4_feature_columns() -> list[str]:
    """Retourne le schema candidat Rev4 Dow/Macro."""

    return list(DOW_MACRO_REV4_FEATURE_COLUMNS)

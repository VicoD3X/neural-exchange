"""Fonctions de collecte preparatoires, non appelees automatiquement."""

from __future__ import annotations

import os
import time

import pandas as pd

from nse_engine.config import FRED_API_KEY_ENV, MACRO_SERIES


def fetch_yfinance_history(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Telecharge un historique yfinance lorsque le script de generation est appele."""

    import yfinance as yf

    last_error: Exception | None = None
    data = pd.DataFrame()
    for attempt in range(3):
        try:
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                interval="1d",
                auto_adjust=False,
                progress=False,
            )
            if not data.empty:
                break
        except Exception as exc:  # pragma: no cover - depend du reseau externe
            last_error = exc

        if attempt < 2:
            time.sleep(5 * (attempt + 1))

    if data.empty:
        if last_error:
            raise RuntimeError(f"Aucune donnee yfinance recuperee pour {ticker}: {last_error}") from last_error
        raise RuntimeError(f"Aucune donnee yfinance recuperee pour {ticker}.")

    data = data.reset_index()
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [column[0] if isinstance(column, tuple) else column for column in data.columns]
    return data


def fetch_fred_macro(start_date: str, end_date: str) -> pd.DataFrame:
    """Telecharge les series macro FRED avec cle API ou CSV public officiel."""

    api_key = os.getenv(FRED_API_KEY_ENV)
    if api_key:
        from fredapi import Fred

        fred = Fred(api_key=api_key)
        macro_data = {
            series: fred.get_series(series, start_date, end_date)
            for series in MACRO_SERIES
        }
    else:
        macro_data = {
            series: _fetch_fred_public_csv(series, start_date, end_date)
            for series in MACRO_SERIES
        }

    df = pd.DataFrame(macro_data)
    df.index = pd.to_datetime(df.index)
    all_days = pd.date_range(start=start_date, end=end_date, freq="D")
    df = df.reindex(all_days).ffill().interpolate()
    return df.reset_index(names="Date")


def fetch_fred_market_series(
    series: str,
    start_date: str,
    end_date: str,
    *,
    value_column: str,
) -> pd.DataFrame:
    """Recupere un indice de marche depuis FRED et le normalise en Date + value_column."""

    raw = _fetch_fred_public_csv(series, start_date, end_date)
    df = raw.reset_index()
    df.columns = ["Date", value_column]
    return df


def _fetch_fred_public_csv(series: str, start_date: str, end_date: str) -> pd.Series:
    """Recupere une serie FRED depuis l'endpoint CSV public officiel."""

    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    df = pd.read_csv(url)
    if "observation_date" not in df.columns or series not in df.columns:
        raise RuntimeError(f"Schema FRED inattendu pour {series}.")

    df["observation_date"] = pd.to_datetime(df["observation_date"], errors="coerce")
    df[series] = pd.to_numeric(df[series], errors="coerce")
    df = df.dropna(subset=["observation_date"])
    mask = (df["observation_date"] >= pd.Timestamp(start_date)) & (
        df["observation_date"] <= pd.Timestamp(end_date)
    )
    df = df.loc[mask, ["observation_date", series]].dropna(subset=[series])
    if df.empty:
        raise RuntimeError(f"Aucune donnee FRED publique exploitable pour {series}.")

    return pd.Series(df[series].to_numpy(), index=df["observation_date"], name=series)

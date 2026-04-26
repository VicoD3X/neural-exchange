"""Preparation des sequences temporelles Rev4."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from nse_engine.config import (
    DOW_MACRO_REV4_FEATURE_COLUMNS,
    REV4_SEQUENCE_LENGTH,
    REV4_TARGET_COLUMN,
    REV4_TRAIN_RATIO,
)


@dataclass(frozen=True)
class Rev4SequenceDataset:
    x_train: np.ndarray
    y_train: np.ndarray
    x_test: np.ndarray
    y_test: np.ndarray
    test_dates: list[str]
    scaler: MinMaxScaler
    feature_columns: list[str]
    target_column: str
    target_index: int
    train_rows: int
    test_rows: int
    sequence_length: int


def load_rev4_dataset(path: Path) -> pd.DataFrame:
    """Charge un dataset Rev4 deja genere."""

    if not path.exists():
        raise FileNotFoundError(f"Dataset Rev4 introuvable: {path}")

    df = pd.read_csv(path, parse_dates=["Date"])
    required = ["Date", *DOW_MACRO_REV4_FEATURE_COLUMNS]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Colonnes Rev4 manquantes: {', '.join(missing)}")

    df = df.dropna(subset=required).sort_values("Date").reset_index(drop=True)
    return df[required]


def build_rev4_sequences(
    df: pd.DataFrame,
    *,
    feature_columns: list[str] | None = None,
    target_column: str = REV4_TARGET_COLUMN,
    sequence_length: int = REV4_SEQUENCE_LENGTH,
    train_ratio: float = REV4_TRAIN_RATIO,
) -> Rev4SequenceDataset:
    """Construit des sequences LSTM avec scaler ajuste uniquement sur le train."""

    feature_columns = feature_columns or list(DOW_MACRO_REV4_FEATURE_COLUMNS)
    if target_column not in feature_columns:
        raise ValueError(f"Target absente des features: {target_column}")
    if len(df) <= sequence_length + 10:
        raise ValueError("Dataset trop court pour construire des sequences Rev4.")

    train_rows = int(len(df) * train_ratio)
    if train_rows <= sequence_length:
        raise ValueError("Split train trop court pour la sequence_length demandee.")

    values = df[feature_columns].to_numpy(dtype=np.float32)
    scaler = MinMaxScaler()
    scaler.fit(values[:train_rows])
    scaled = scaler.transform(values)
    target_index = feature_columns.index(target_column)

    x_train, y_train = _build_sequences_range(
        scaled,
        start=0,
        stop=train_rows - sequence_length,
        sequence_length=sequence_length,
        target_index=target_index,
    )
    x_test, y_test = _build_sequences_range(
        scaled,
        start=train_rows - sequence_length,
        stop=len(scaled) - sequence_length,
        sequence_length=sequence_length,
        target_index=target_index,
    )
    test_dates = [
        pd.Timestamp(date).date().isoformat()
        for date in df["Date"].iloc[train_rows : len(scaled)].tolist()
    ]

    return Rev4SequenceDataset(
        x_train=x_train,
        y_train=y_train,
        x_test=x_test,
        y_test=y_test,
        test_dates=test_dates,
        scaler=scaler,
        feature_columns=list(feature_columns),
        target_column=target_column,
        target_index=target_index,
        train_rows=train_rows,
        test_rows=len(df) - train_rows,
        sequence_length=sequence_length,
    )


def inverse_transform_target(
    values: np.ndarray,
    *,
    scaler: MinMaxScaler,
    n_features: int,
    target_index: int,
) -> np.ndarray:
    """Inverse uniquement la colonne cible d'un scaler multivarie."""

    shaped = np.zeros((len(values), n_features), dtype=np.float32)
    shaped[:, target_index] = values.reshape(-1)
    return scaler.inverse_transform(shaped)[:, target_index]


def _build_sequences_range(
    scaled: np.ndarray,
    *,
    start: int,
    stop: int,
    sequence_length: int,
    target_index: int,
) -> tuple[np.ndarray, np.ndarray]:
    x_values: list[np.ndarray] = []
    y_values: list[float] = []

    for index in range(start, stop):
        x_values.append(scaled[index : index + sequence_length])
        y_values.append(float(scaled[index + sequence_length, target_index]))

    return np.array(x_values, dtype=np.float32), np.array(y_values, dtype=np.float32).reshape(-1, 1)


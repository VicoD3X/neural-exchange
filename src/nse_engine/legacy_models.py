"""Chargement controle des modeles LSTM legacy."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import MinMaxScaler
from torch import nn

from nse_engine.config import (
    GOLD_FEATURE_COLUMNS,
    GOLD_FEATURES_PATH,
    LEGACY_DOW_MACRO_HIDDEN_SIZE,
    LEGACY_DOW_MACRO_INPUT_SIZE,
    LEGACY_DOW_MACRO_MODEL_PATH,
    LEGACY_DOW_MACRO_SEQUENCE_LENGTH,
    LEGACY_GOLD_HIDDEN_SIZE,
    LEGACY_GOLD_MODEL_PATH,
    LEGACY_GOLD_SEQUENCE_LENGTH,
)


class LegacyLSTMModel(nn.Module):
    """Architecture LSTM simple utilisee par les prototypes historiques."""

    def __init__(self, input_size: int, hidden_size: int, output_size: int = 1) -> None:
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=1, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, (hidden, _) = self.lstm(x)
        return self.fc(hidden[-1])


@dataclass(frozen=True)
class LegacyModelSpec:
    name: str
    path: Path
    input_size: int
    hidden_size: int
    sequence_length: int
    status: str


@dataclass(frozen=True)
class GoldLegacyPrediction:
    predicted_gold_close: float
    actual_gold_close: float
    target_date: str
    sequence_shape: tuple[int, int, int]
    used_features: list[str]


GOLD_LEGACY_SPEC = LegacyModelSpec(
    name="nse-engine-gold-legacy",
    path=LEGACY_GOLD_MODEL_PATH,
    input_size=len(GOLD_FEATURE_COLUMNS),
    hidden_size=LEGACY_GOLD_HIDDEN_SIZE,
    sequence_length=LEGACY_GOLD_SEQUENCE_LENGTH,
    status="rechargeable",
)

DOW_MACRO_LEGACY_SPEC = LegacyModelSpec(
    name="nse-engine-legacy-dow-macro",
    path=LEGACY_DOW_MACRO_MODEL_PATH,
    input_size=LEGACY_DOW_MACRO_INPUT_SIZE,
    hidden_size=LEGACY_DOW_MACRO_HIDDEN_SIZE,
    sequence_length=LEGACY_DOW_MACRO_SEQUENCE_LENGTH,
    status="archive_rev2_non_connectee",
)


def load_state_dict(path: Path) -> dict[str, torch.Tensor]:
    """Charge un state_dict PyTorch legacy en CPU."""

    if not path.exists():
        raise FileNotFoundError(f"Modele legacy introuvable: {path}")
    return torch.load(path, map_location="cpu", weights_only=True)


def infer_lstm_spec_from_state_dict(state_dict: dict[str, torch.Tensor]) -> tuple[int, int]:
    """Infere input_size et hidden_size depuis les poids LSTM."""

    weight_ih = state_dict["lstm.weight_ih_l0"]
    weight_hh = state_dict["lstm.weight_hh_l0"]
    input_size = int(weight_ih.shape[1])
    hidden_size = int(weight_hh.shape[1])
    return input_size, hidden_size


def load_legacy_model(spec: LegacyModelSpec) -> LegacyLSTMModel:
    """Instancie et charge un modele legacy selon son contrat connu."""

    state_dict = load_state_dict(spec.path)
    inferred_input_size, inferred_hidden_size = infer_lstm_spec_from_state_dict(state_dict)
    if (inferred_input_size, inferred_hidden_size) != (spec.input_size, spec.hidden_size):
        raise ValueError(
            f"Contrat modele inattendu pour {spec.name}: "
            f"{inferred_input_size=} {inferred_hidden_size=}"
        )

    model = LegacyLSTMModel(input_size=spec.input_size, hidden_size=spec.hidden_size)
    model.load_state_dict(state_dict)
    model.eval()
    return model


def load_gold_features(path: Path = GOLD_FEATURES_PATH) -> pd.DataFrame:
    """Charge le dataset Gold propre genere au Bloc 3."""

    if not path.exists():
        raise FileNotFoundError(f"Dataset Gold introuvable: {path}")

    df = pd.read_csv(path, parse_dates=["Date"])
    missing = [column for column in GOLD_FEATURE_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Colonnes Gold manquantes: {', '.join(missing)}")
    return df.dropna(subset=["Date", *GOLD_FEATURE_COLUMNS]).reset_index(drop=True)


def build_gold_sequences(
    df: pd.DataFrame,
    sequence_length: int = LEGACY_GOLD_SEQUENCE_LENGTH,
) -> tuple[np.ndarray, np.ndarray, MinMaxScaler]:
    """Reconstruit les sequences Gold et le scaler absent du modele legacy."""

    values = df[GOLD_FEATURE_COLUMNS].to_numpy(dtype=np.float32)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    sequences: list[np.ndarray] = []
    targets: list[float] = []
    for index in range(len(scaled) - sequence_length):
        sequences.append(scaled[index : index + sequence_length])
        targets.append(float(scaled[index + sequence_length, 0]))

    return np.array(sequences, dtype=np.float32), np.array(targets, dtype=np.float32), scaler


def predict_gold_legacy(
    *,
    data_path: Path = GOLD_FEATURES_PATH,
    model_path: Path = LEGACY_GOLD_MODEL_PATH,
) -> GoldLegacyPrediction:
    """Produit une prediction primitive sur la derniere sequence Gold disponible."""

    spec = LegacyModelSpec(
        name=GOLD_LEGACY_SPEC.name,
        path=model_path,
        input_size=GOLD_LEGACY_SPEC.input_size,
        hidden_size=GOLD_LEGACY_SPEC.hidden_size,
        sequence_length=GOLD_LEGACY_SPEC.sequence_length,
        status=GOLD_LEGACY_SPEC.status,
    )
    model = load_legacy_model(spec)
    df = load_gold_features(data_path)
    sequences, _, scaler = build_gold_sequences(df, spec.sequence_length)
    if len(sequences) == 0:
        raise ValueError("Pas assez de donnees Gold pour produire une sequence.")

    sequence = sequences[-1:]
    with torch.no_grad():
        predicted_scaled = float(model(torch.tensor(sequence, dtype=torch.float32)).item())

    fake_scaled = np.zeros((1, len(GOLD_FEATURE_COLUMNS)), dtype=np.float32)
    fake_scaled[0, 0] = predicted_scaled
    predicted_gold_close = float(scaler.inverse_transform(fake_scaled)[0, 0])
    actual_gold_close = float(df["Gold_Close"].iloc[-1])
    target_date = pd.Timestamp(df["Date"].iloc[-1]).date().isoformat()

    return GoldLegacyPrediction(
        predicted_gold_close=predicted_gold_close,
        actual_gold_close=actual_gold_close,
        target_date=target_date,
        sequence_shape=tuple(sequence.shape),
        used_features=list(GOLD_FEATURE_COLUMNS),
    )


def dow_macro_legacy_dry_run() -> tuple[int, int, tuple[int, int, int]]:
    """Charge le modele Dow/Macro legacy et valide seulement son architecture."""

    model = load_legacy_model(DOW_MACRO_LEGACY_SPEC)
    dummy = torch.zeros(
        1,
        DOW_MACRO_LEGACY_SPEC.sequence_length,
        DOW_MACRO_LEGACY_SPEC.input_size,
        dtype=torch.float32,
    )
    with torch.no_grad():
        output = model(dummy)
    return DOW_MACRO_LEGACY_SPEC.input_size, DOW_MACRO_LEGACY_SPEC.hidden_size, tuple(output.shape)


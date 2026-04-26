"""Modele LSTM Rev4 et boucle d'entrainement."""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


@dataclass(frozen=True)
class TrainingHistory:
    losses: list[float]


class Rev4LSTMModel(nn.Module):
    """LSTM simple pour baseline Rev4 reproductible."""

    def __init__(self, input_size: int, hidden_size: int, output_size: int = 1) -> None:
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=1, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, (hidden, _) = self.lstm(x)
        return self.fc(hidden[-1])


def set_reproducible_seed(seed: int) -> None:
    """Fixe les graines principales pour une execution locale reproductible."""

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def train_lstm_model(
    model: Rev4LSTMModel,
    x_train: np.ndarray,
    y_train: np.ndarray,
    *,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> TrainingHistory:
    """Entraine un LSTM Rev4 sur sequences preconstruites."""

    x_tensor = torch.tensor(x_train, dtype=torch.float32)
    y_tensor = torch.tensor(y_train, dtype=torch.float32)
    dataset = TensorDataset(x_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    losses: list[float] = []

    model.train()
    for _ in range(epochs):
        epoch_loss = 0.0
        for x_batch, y_batch in loader:
            optimizer.zero_grad()
            output = model(x_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += float(loss.item())
        losses.append(epoch_loss / max(len(loader), 1))

    model.eval()
    return TrainingHistory(losses=losses)


def predict_scaled(model: Rev4LSTMModel, x_values: np.ndarray) -> np.ndarray:
    """Produit les predictions scalees du modele."""

    model.eval()
    with torch.no_grad():
        output = model(torch.tensor(x_values, dtype=torch.float32))
    return output.detach().cpu().numpy().reshape(-1)


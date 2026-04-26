"""Entraine le modele Rev4 principal et genere les artefacts reproductibles."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> None:
    from nse_engine.training import train_rev4_pipeline

    metadata = train_rev4_pipeline()
    metrics = metadata["metrics"]
    print("Modele Rev4 entraine.")
    print(f"Dataset: {metadata['dataset_name']}")
    print(f"MAE: {metrics['mae']:.2f}")
    print(f"RMSE: {metrics['rmse']:.2f}")
    print(f"MAPE: {metrics['mape_percent']:.2f}%")
    print(f"Directional accuracy: {metrics['directional_accuracy_percent']:.2f}%")


if __name__ == "__main__":
    main()


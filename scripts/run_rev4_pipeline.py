"""Orchestration complete du flux Rev4 reproductible."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Enchaine dataset Dow/Macro Rev4, entrainement, rapports et graphiques."""

    steps = [
        ("Generation du dataset Dow/Macro Rev4", PROJECT_ROOT / "scripts" / "build_dow_macro_rev4_dataset.py"),
        ("Entrainement Rev4 et generation des rapports", PROJECT_ROOT / "scripts" / "train_rev4_model.py"),
    ]
    for label, script_path in steps:
        print(f"[Rev4] {label}...")
        subprocess.run([sys.executable, str(script_path)], cwd=PROJECT_ROOT, check=True)

    print("[Rev4] Pipeline termine.")
    print("[Rev4] Rapports et graphiques disponibles dans reports/rev4/.")


if __name__ == "__main__":
    main()

"""Exporte les donnees publiques du dashboard Rev4."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from nse_engine.dashboard import DASHBOARD_DATA_PATH, build_dashboard_data, write_dashboard_data  # noqa: E402


def main() -> None:
    print("Generation de reports/rev4/dashboard_data.json...")
    data = build_dashboard_data()
    write_dashboard_data(data, DASHBOARD_DATA_PATH)
    print(f"Export dashboard termine: {DASHBOARD_DATA_PATH}")


if __name__ == "__main__":
    main()

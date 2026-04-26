"""Synchronise les donnees et graphiques Rev4 vers le dashboard statique."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = SCRIPT_PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from nse_engine.config import PROJECT_ROOT  # noqa: E402
from nse_engine.dashboard import DASHBOARD_DATA_PATH, load_dashboard_data  # noqa: E402

DASHBOARD_PUBLIC_DIR = PROJECT_ROOT / "dashboard" / "public"
DASHBOARD_ASSETS_DIR = DASHBOARD_PUBLIC_DIR / "assets" / "rev4"
DASHBOARD_DATA_DESTINATION = DASHBOARD_PUBLIC_DIR / "dashboard_data.json"


def main() -> None:
    print("Verification du dashboard_data.json...")
    data = load_dashboard_data(DASHBOARD_DATA_PATH)

    DASHBOARD_PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARD_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    shutil.copy2(DASHBOARD_DATA_PATH, DASHBOARD_DATA_DESTINATION)
    print(f"JSON synchronise: {DASHBOARD_DATA_DESTINATION}")

    copied = 0
    for chart in data.get("charts", []):
        source = PROJECT_ROOT / chart["path"]
        if not source.exists():
            raise FileNotFoundError(f"Graphique introuvable: {source}")
        destination = DASHBOARD_ASSETS_DIR / source.name
        shutil.copy2(source, destination)
        copied += 1

    print(f"Graphiques synchronises: {copied}")
    print("Synchronisation dashboard terminee.")


if __name__ == "__main__":
    main()

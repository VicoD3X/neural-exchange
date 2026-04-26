"""Convertit les rapports Excel historiques en CSV, JSON et Markdown."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> None:
    from nse_engine.legacy_reporting import convert_legacy_reports

    report = convert_legacy_reports()
    summary = report["summary"]
    print("Rapports legacy convertis.")
    print(f"Lignes converties: {summary['rows']}")
    print(f"Periode: {summary['date_min']} a {summary['date_max']}")
    print(f"Panic Mode: {summary['panic_mode_rows']} ligne(s)")


if __name__ == "__main__":
    main()

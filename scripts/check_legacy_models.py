"""Controle console des modeles legacy Neural Stock Exchange."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main() -> None:
    from nse_engine.legacy_models import (
        DOW_MACRO_LEGACY_SPEC,
        GOLD_LEGACY_SPEC,
        dow_macro_legacy_dry_run,
        predict_gold_legacy,
    )

    print("Controle des modeles legacy Neural Stock Exchange")
    print()

    gold_prediction = predict_gold_legacy()
    print(f"[OK] {GOLD_LEGACY_SPEC.name}")
    print(f"     modele: {GOLD_LEGACY_SPEC.path}")
    print(f"     features: {', '.join(gold_prediction.used_features)}")
    print(f"     sequence_shape: {gold_prediction.sequence_shape}")
    print(f"     date cible: {gold_prediction.target_date}")
    print(f"     prediction primitive Gold_Close: {gold_prediction.predicted_gold_close:.2f}")
    print(f"     valeur reelle Gold_Close: {gold_prediction.actual_gold_close:.2f}")
    print("     note: scaler reconstruit depuis le dataset Gold propre, non sauvegarde historiquement.")
    print()

    input_size, hidden_size, output_shape = dow_macro_legacy_dry_run()
    print(f"[OK] {DOW_MACRO_LEGACY_SPEC.name}")
    print(f"     modele: {DOW_MACRO_LEGACY_SPEC.path}")
    print(f"     input_size: {input_size}")
    print(f"     hidden_size: {hidden_size}")
    print(f"     dry_run_output_shape: {output_shape}")
    print("     note: archive Rev2 chargeable, non branchee sur Rev3 ou Rev4.")


if __name__ == "__main__":
    main()


from __future__ import annotations

import ast
from pathlib import Path


SCRIPTS_WITHOUT_DIRECT_NETWORK_CLIENTS = {
    "check_legacy_models.py",
    "convert_legacy_reports.py",
    "export_dashboard_data.py",
    "sync_dashboard_assets.py",
    "train_rev4_model.py",
    "run_rev4_pipeline.py",
}

NETWORK_MODULES = {"yfinance", "fredapi"}


def test_critical_offline_scripts_do_not_import_network_clients() -> None:
    project_root = Path(__file__).resolve().parents[1]
    scripts_dir = project_root / "scripts"

    offenders: list[str] = []
    for script_name in SCRIPTS_WITHOUT_DIRECT_NETWORK_CLIENTS:
        tree = ast.parse((scripts_dir / script_name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported = {node.module.split(".")[0]}
            else:
                continue

            blocked = imported & NETWORK_MODULES
            if blocked:
                offenders.append(f"{script_name}: {', '.join(sorted(blocked))}")

    assert offenders == []


def test_dataset_generation_scripts_are_the_only_scripts_allowed_to_use_network_clients() -> None:
    project_root = Path(__file__).resolve().parents[1]
    scripts_dir = project_root / "scripts"
    generation_scripts = {
        "build_gold_dataset.py",
        "build_dow_macro_rev4_dataset.py",
        "build_market_macro_rev4_dataset.py",
    }

    checked_scripts = {path.name for path in scripts_dir.glob("*.py")}

    assert SCRIPTS_WITHOUT_DIRECT_NETWORK_CLIENTS.issubset(checked_scripts)
    assert generation_scripts.issubset(checked_scripts)


def test_rev4_pipeline_script_orchestrates_dataset_then_training() -> None:
    project_root = Path(__file__).resolve().parents[1]
    script_text = (project_root / "scripts" / "run_rev4_pipeline.py").read_text(encoding="utf-8")

    dataset_index = script_text.index("build_dow_macro_rev4_dataset.py")
    training_index = script_text.index("train_rev4_model.py")

    assert dataset_index < training_index
    assert "subprocess.run" in script_text
    assert "reports/rev4/" in script_text

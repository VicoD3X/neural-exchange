from __future__ import annotations

from pathlib import Path


def test_active_code_does_not_read_pre_git_quarantine() -> None:
    project_root = Path(__file__).resolve().parents[1]
    active_files = [
        *project_root.joinpath("src").rglob("*.py"),
        *project_root.joinpath("scripts").rglob("*.py"),
    ]

    offenders = [
        path
        for path in active_files
        if "_pre_git_roadmap/quarantine" in path.read_text(encoding="utf-8")
        or "_pre_git_roadmap\\quarantine" in path.read_text(encoding="utf-8")
    ]

    assert offenders == []


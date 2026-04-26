"""Conversion des rapports historiques Neural Stock Exchange."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from nse_engine.config import (
    FINANCIAL_DISCLAIMER,
    LEGACY_REPORT_JSON_PATH,
    LEGACY_REPORT_MD_PATH,
    LEGACY_REV2_REPORT_PATH,
    LEGACY_REV25_REPORT_PATH,
)


@dataclass(frozen=True)
class LegacyReportSource:
    """Definition d'un rapport Excel historique a convertir."""

    revision: str
    path: Path


LEGACY_REPORT_SOURCES = [
    LegacyReportSource(revision="Rev2", path=LEGACY_REV2_REPORT_PATH),
    LegacyReportSource(revision="Rev2.5", path=LEGACY_REV25_REPORT_PATH),
]


def convert_legacy_reports(
    *,
    sources: list[LegacyReportSource] | None = None,
    output_dir: Path | None = None,
    summary_json_path: Path = LEGACY_REPORT_JSON_PATH,
    summary_md_path: Path = LEGACY_REPORT_MD_PATH,
) -> dict[str, Any]:
    """Convertit les rapports Excel historiques en CSV, JSON et Markdown."""

    selected_sources = sources or LEGACY_REPORT_SOURCES
    target_dir = output_dir or summary_json_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    converted_reports = []
    all_observations = []
    for source in selected_sources:
        observations = load_legacy_report(source.path, revision=source.revision)
        csv_path = target_dir / f"legacy_{source.revision.lower().replace('.', '')}_predictions.csv"
        pd.DataFrame(observations).to_csv(csv_path, index=False, encoding="utf-8")
        converted_reports.append(
            {
                "revision": source.revision,
                "source_path": _relative_path(source.path),
                "csv_path": _relative_path(csv_path),
                "rows": len(observations),
                "has_panic_mode": any(row["panic_mode"] is not None for row in observations),
            }
        )
        all_observations.extend(observations)

    summary = build_legacy_report_summary(converted_reports, all_observations)
    summary_json_path.parent.mkdir(parents=True, exist_ok=True)
    summary_json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_md_path.write_text(render_legacy_report_markdown(summary), encoding="utf-8")
    return summary


def load_legacy_report(path: Path, *, revision: str) -> list[dict[str, Any]]:
    """Charge un rapport Excel historique et renvoie des observations normalisees."""

    df = pd.read_excel(path)
    return normalize_legacy_report_frame(df, revision=revision)


def normalize_legacy_report_frame(df: pd.DataFrame, *, revision: str) -> list[dict[str, Any]]:
    """Normalise les colonnes historiques sans modifier les valeurs observees."""

    observations = []
    for _, row in df.iterrows():
        prediction = _parse_number(row.get("Prédiction NSE (€)"))
        actual = _parse_number(row.get("Valeur réelle (€)"))
        error_percent = _parse_percent(row.get("Écart (%)"))
        date_value = pd.to_datetime(row.get("Date"), errors="coerce")
        if pd.isna(date_value):
            continue
        panic_raw = row.get("Panic Mode ?")
        observations.append(
            {
                "revision": revision,
                "date": date_value.strftime("%Y-%m-%d"),
                "prediction": prediction,
                "actual": actual,
                "error_percent": error_percent,
                "panic_mode": _parse_panic_mode(panic_raw),
                "trend_note": _clean_text(row.get("Tendance captée ?")),
            }
        )
    return observations


def build_legacy_report_summary(
    converted_reports: list[dict[str, Any]],
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Construit un resume auditable des rapports historiques convertis."""

    dates = [row["date"] for row in observations]
    panic_events = [row for row in observations if row["panic_mode"] is True]
    return {
        "summary": {
            "project": "Neural Stock Exchange",
            "report_type": "legacy_predictions",
            "source": "Excel historiques convertis sans modification des resultats",
            "rows": len(observations),
            "date_min": min(dates) if dates else None,
            "date_max": max(dates) if dates else None,
            "panic_mode_rows": len(panic_events),
        },
        "converted_reports": converted_reports,
        "observations": observations,
        "panic_mode_observations": panic_events,
        "limitations": [
            "Rapports historiques issus des prototypes Rev2 et Rev2.5.",
            "Les valeurs sont converties pour lecture, sans recalcul de performance.",
            "Les fichiers Rev2 d'origine et scalers associes ne sont pas disponibles.",
            "Ces resultats ne constituent pas une preuve de robustesse predictive.",
        ],
        "financial_disclaimer": FINANCIAL_DISCLAIMER,
    }


def render_legacy_report_markdown(report: dict[str, Any]) -> str:
    """Rend le resume legacy en Markdown."""

    summary = report["summary"]
    lines = [
        "# Reporting legacy - Neural Stock Exchange",
        "",
        "## Synthese",
        "",
        f"- Type : `{summary['report_type']}`",
        f"- Lignes converties : {summary['rows']}",
        f"- Periode observee : {summary['date_min']} a {summary['date_max']}",
        f"- Lignes avec Panic Mode : {summary['panic_mode_rows']}",
        "",
        "## Sources converties",
        "",
        "| Revision | Source | CSV | Lignes | Panic Mode |",
        "|---|---|---|---:|---|",
    ]
    for item in report["converted_reports"]:
        lines.append(
            "| {revision} | `{source}` | `{csv}` | {rows} | {panic} |".format(
                revision=item["revision"],
                source=item["source_path"],
                csv=item["csv_path"],
                rows=item["rows"],
                panic="oui" if item["has_panic_mode"] else "non",
            )
        )

    lines.extend(
        [
            "",
            "## Observations",
            "",
            "| Revision | Date | Prediction | Reel | Ecart % | Panic Mode | Note |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in report["observations"]:
        panic = "oui" if row["panic_mode"] is True else "non" if row["panic_mode"] is False else "n/a"
        lines.append(
            "| {revision} | {date} | {prediction:.2f} | {actual:.2f} | {error:.2f} | {panic} | {note} |".format(
                revision=row["revision"],
                date=row["date"],
                prediction=row["prediction"],
                actual=row["actual"],
                error=row["error_percent"],
                panic=panic,
                note=row["trend_note"],
            )
        )

    lines.extend(
        [
            "",
            "## Panic Mode",
            "",
            "| Revision | Date | Prediction | Reel | Ecart % | Note |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for row in report["panic_mode_observations"]:
        lines.append(
            "| {revision} | {date} | {prediction:.2f} | {actual:.2f} | {error:.2f} | {note} |".format(
                revision=row["revision"],
                date=row["date"],
                prediction=row["prediction"],
                actual=row["actual"],
                error=row["error_percent"],
                note=row["trend_note"],
            )
        )

    lines.extend(
        [
            "",
            "## Limites",
            "",
            *[f"- {item}" for item in report["limitations"]],
            "",
            f"> {report['financial_disclaimer']}",
            "",
        ]
    )
    return "\n".join(lines)


def _parse_number(value: Any) -> float:
    if value is None or pd.isna(value):
        return float("nan")
    text = str(value).replace("\u00a0", " ").replace(" ", "").replace(",", ".")
    return float(re.sub(r"[^0-9.+-]", "", text))


def _parse_percent(value: Any) -> float:
    if value is None or pd.isna(value):
        return float("nan")
    text = str(value).replace("%", "").replace(",", ".").strip()
    return float(re.sub(r"[^0-9.+-]", "", text))


def _parse_panic_mode(value: Any) -> bool | None:
    if value is None or pd.isna(value):
        return None
    text = _clean_text(value).lower()
    if "oui" in text:
        return True
    if "non" in text:
        return False
    return None


def _clean_text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    return " ".join(text.split())


def _relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()

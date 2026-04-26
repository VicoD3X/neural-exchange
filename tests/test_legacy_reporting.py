from __future__ import annotations

import json

import pandas as pd

from nse_engine.legacy_reporting import (
    LegacyReportSource,
    convert_legacy_reports,
    normalize_legacy_report_frame,
    render_legacy_report_markdown,
)


def test_normalize_legacy_report_frame_parses_values() -> None:
    df = pd.DataFrame(
        [
            {
                "Date": "2008-10-12",
                "Prédiction NSE (€)": "10 443.32",
                "Valeur réelle (€)": "8 451.19",
                "Écart (%)": "+23.54%",
                "Panic Mode ?": "Oui",
                "Tendance captée ?": "NSE detecte la crise",
            }
        ]
    )

    rows = normalize_legacy_report_frame(df, revision="Rev2.5")

    assert rows == [
        {
            "revision": "Rev2.5",
            "date": "2008-10-12",
            "prediction": 10443.32,
            "actual": 8451.19,
            "error_percent": 23.54,
            "panic_mode": True,
            "trend_note": "NSE detecte la crise",
        }
    ]


def test_render_legacy_report_markdown_contains_panic_mode() -> None:
    report = {
        "summary": {
            "report_type": "legacy_predictions",
            "rows": 1,
            "date_min": "2008-10-12",
            "date_max": "2008-10-12",
            "panic_mode_rows": 1,
        },
        "converted_reports": [
            {
                "revision": "Rev2.5",
                "source_path": "reports/legacy/source.xlsx",
                "csv_path": "reports/converted/source.csv",
                "rows": 1,
                "has_panic_mode": True,
            }
        ],
        "observations": [
            {
                "revision": "Rev2.5",
                "date": "2008-10-12",
                "prediction": 10443.32,
                "actual": 8451.19,
                "error_percent": 23.54,
                "panic_mode": True,
                "trend_note": "NSE detecte la crise",
            }
        ],
        "panic_mode_observations": [
            {
                "revision": "Rev2.5",
                "date": "2008-10-12",
                "prediction": 10443.32,
                "actual": 8451.19,
                "error_percent": 23.54,
                "trend_note": "NSE detecte la crise",
            }
        ],
        "limitations": ["Test"],
        "financial_disclaimer": "Aucun conseil financier.",
    }

    markdown = render_legacy_report_markdown(report)

    assert "Panic Mode" in markdown
    assert "2008-10-12" in markdown
    assert "23.54" in markdown


def test_convert_legacy_reports_writes_outputs(tmp_path) -> None:
    source_path = tmp_path / "legacy.xlsx"
    df = pd.DataFrame(
        [
            {
                "Date": "2009-03-01",
                "Prédiction NSE (€)": "7 868.21",
                "Valeur réelle (€)": "6 626.93",
                "Écart (%)": "+18.74%",
                "Panic Mode ?": "Oui",
                "Tendance captée ?": "NSE voit la panique",
            }
        ]
    )
    df.to_excel(source_path, index=False)

    json_path = tmp_path / "summary.json"
    md_path = tmp_path / "summary.md"
    report = convert_legacy_reports(
        sources=[LegacyReportSource(revision="Test", path=source_path)],
        output_dir=tmp_path,
        summary_json_path=json_path,
        summary_md_path=md_path,
    )

    assert report["summary"]["rows"] == 1
    assert json.loads(json_path.read_text(encoding="utf-8"))["summary"]["rows"] == 1
    assert md_path.exists()
    assert (tmp_path / "legacy_test_predictions.csv").exists()

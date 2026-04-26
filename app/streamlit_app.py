"""Dashboard local Neural Stock Exchange."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from nse_engine.dashboard import DASHBOARD_DATA_PATH, load_dashboard_data  # noqa: E402


st.set_page_config(
    page_title="Neural Stock Exchange - Rev4",
    page_icon="NSE",
    layout="wide",
)


def main() -> None:
    data = _load_data()
    if data is None:
        return

    _render_header(data)
    _render_kpis(data)
    _render_verdict(data)
    _render_tabs(data)


def _load_data() -> dict[str, Any] | None:
    try:
        return load_dashboard_data(DASHBOARD_DATA_PATH)
    except (FileNotFoundError, ValueError) as exc:
        st.title("Neural Stock Exchange - Dashboard Rev4")
        st.error("Donnée non disponible dans l'export actuel.")
        st.code("python scripts/export_dashboard_data.py", language="bash")
        st.caption(str(exc))
        return None


def _render_header(data: dict[str, Any]) -> None:
    st.title("Neural Stock Exchange - Rev4 Analysis Cockpit")
    st.caption("Laboratoire experimental LSTM, series financieres, baselines causales et Panic_Mode.")
    st.warning(data.get("financial_disclaimer", "Aucun resultat ne constitue un conseil financier."))


def _render_kpis(data: dict[str, Any]) -> None:
    summary = data.get("summary", {})
    metrics = data.get("metrics", {})
    critical = data.get("critical_evaluation", {})
    regime = data.get("regime_analysis", {})

    cols = st.columns(5)
    cols[0].metric("MAE LSTM", _format_number(metrics.get("mae")))
    cols[1].metric("RMSE LSTM", _format_number(metrics.get("rmse")))
    cols[2].metric("Direction", f"{metrics.get('directional_accuracy_percent', 0):.2f}%")
    cols[3].metric("Best MAE", str(summary.get("best_by_mae", "n/a")))
    cols[4].metric("Panic rows test", regime.get("panic_mode_rows_in_test", "n/a"))

    st.caption(
        "Le dashboard lit uniquement `reports/rev4/dashboard_data.json` et les graphiques deja generes."
    )
    st.caption(
        f"Dataset: `{summary.get('dataset_name', 'n/a')}` - Test rows: {summary.get('test_rows', 'n/a')} - "
        f"Features: {summary.get('features_count', 'n/a')}"
    )
    if critical.get("mae_ratio_vs_best_baseline") is not None:
        st.caption(
            "Ratio MAE LSTM / meilleure baseline: "
            f"{critical.get('mae_ratio_vs_best_baseline'):.2f}"
        )


def _render_verdict(data: dict[str, Any]) -> None:
    critical = data.get("critical_evaluation", {})
    message = critical.get("message", "Verdict critique non disponible.")
    st.subheader("Verdict critique")
    st.info(message)
    st.write(
        "La baseline `last_value` reste tres forte sur une serie de prix. "
        "Le LSTM Rev4 sert ici a documenter une experimentation reproductible, pas a produire un signal de trading."
    )


def _render_tabs(data: dict[str, Any]) -> None:
    tabs = st.tabs(["Graphiques", "Baselines", "Regimes", "Legacy & limites"])
    with tabs[0]:
        _render_charts(data)
    with tabs[1]:
        _render_baselines(data)
    with tabs[2]:
        _render_regimes(data)
    with tabs[3]:
        _render_legacy_and_limits(data)


def _render_charts(data: dict[str, Any]) -> None:
    charts = data.get("charts", [])
    if not charts:
        st.info("Donnée non disponible dans le rapport actuel.")
        return

    for chart in charts:
        st.markdown(f"### {chart.get('title', 'Graphique Rev4')}")
        image_path = PROJECT_ROOT / chart.get("path", "")
        if image_path.exists():
            st.image(str(image_path), use_container_width=True)
        else:
            st.warning(f"Graphique introuvable: `{chart.get('path')}`")


def _render_baselines(data: dict[str, Any]) -> None:
    comparison = data.get("baseline_comparison", [])
    if not comparison:
        st.info("Donnée non disponible dans le rapport actuel.")
        return

    frame = pd.DataFrame(comparison)
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.bar_chart(frame.set_index("model")[["mae", "rmse"]])
    st.caption("Les baselines sont causales : elles n'utilisent pas d'information future.")


def _render_regimes(data: dict[str, Any]) -> None:
    regime = data.get("regime_analysis", {})
    st.write(regime.get("message", "Analyse par regime non disponible."))
    st.caption(
        f"Fenetre test: {regime.get('test_start', 'n/a')} -> {regime.get('test_end', 'n/a')}"
    )

    segments = regime.get("segments", [])
    if not segments:
        st.info("Donnée non disponible dans le rapport actuel.")
        return

    rows = []
    for segment in segments:
        base = {
            "segment": segment.get("label"),
            "rows": segment.get("rows"),
            "status": segment.get("status"),
            "best_by_mae": segment.get("best_by_mae"),
        }
        for model, metrics in segment.get("metrics", {}).items():
            rows.append({**base, "model": model, **metrics})

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Donnée non disponible dans le rapport actuel.")


def _render_legacy_and_limits(data: dict[str, Any]) -> None:
    st.subheader("Legacy")
    legacy = data.get("legacy", {})
    for name, description in legacy.items():
        st.markdown(f"- **{name}** : {description}")

    st.subheader("Limites")
    for item in data.get("limitations", []):
        st.markdown(f"- {item}")

    st.subheader("Artefacts")
    artifacts = data.get("artifacts", {})
    for key, value in artifacts.items():
        st.markdown(f"- **{key}** : `{value}`")


def _format_number(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.2f}"
    return "n/a"


if __name__ == "__main__":
    main()

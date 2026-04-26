"""Interface locale minimale pour visualiser le modele Gold legacy."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _line_points(values: list[float], *, width: int = 920, height: int = 220) -> str:
    if len(values) < 2:
        return ""

    min_value = min(values)
    max_value = max(values)
    value_range = max(max_value - min_value, 1e-9)

    points = []
    for index, value in enumerate(values):
        x = index * (width / (len(values) - 1))
        y = height - ((value - min_value) / value_range) * height
        points.append(f"{x:.2f},{y:.2f}")
    return " ".join(points)


def create_app():
    from flask import Flask, render_template_string

    from nse_engine.legacy_models import GOLD_LEGACY_SPEC, load_gold_features, predict_gold_legacy

    app = Flask(__name__)

    @app.route("/")
    def index() -> str:
        prediction = predict_gold_legacy()
        df = load_gold_features()
        chart_df = df.tail(260)
        values = chart_df["Gold_Close"].astype(float).tolist()
        delta = prediction.predicted_gold_close - prediction.actual_gold_close
        delta_pct = delta / prediction.actual_gold_close * 100

        return render_template_string(
            TEMPLATE,
            model_name=GOLD_LEGACY_SPEC.name,
            model_path=GOLD_LEGACY_SPEC.path.as_posix(),
            features=prediction.used_features,
            sequence_shape=prediction.sequence_shape,
            target_date=prediction.target_date,
            predicted=prediction.predicted_gold_close,
            actual=prediction.actual_gold_close,
            delta=delta,
            delta_pct=delta_pct,
            chart_points=_line_points(values),
            chart_min=min(values),
            chart_max=max(values),
            first_date=str(chart_df["Date"].iloc[0].date()),
            last_date=str(chart_df["Date"].iloc[-1].date()),
            rows=chart_df.tail(8).to_dict("records"),
        )

    return app


TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Neural Stock Exchange - Gold Legacy</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #06111f;
      --panel: #0d1d31;
      --panel-soft: #132941;
      --text: #f5f8ff;
      --muted: #9fb0c8;
      --line: #74d7a7;
      --accent: #8cc8ff;
      --danger: #ff9a8d;
      --border: rgba(255, 255, 255, 0.1);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(140, 200, 255, 0.18), transparent 34rem),
        linear-gradient(135deg, #06111f 0%, #09172a 55%, #0c2136 100%);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
    }
    main {
      width: min(1180px, calc(100vw - 40px));
      margin: 0 auto;
      padding: 34px 0;
    }
    header {
      display: flex;
      justify-content: space-between;
      gap: 20px;
      align-items: flex-start;
      margin-bottom: 24px;
    }
    .eyebrow {
      color: var(--accent);
      font-size: 12px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      font-weight: 800;
    }
    h1 {
      margin: 8px 0 10px;
      font-size: clamp(34px, 5vw, 64px);
      line-height: 0.95;
      letter-spacing: -0.06em;
    }
    .lead {
      max-width: 720px;
      color: var(--muted);
      font-size: 18px;
      line-height: 1.55;
    }
    .badge {
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.06);
      padding: 10px 14px;
      border-radius: 999px;
      color: var(--text);
      font-weight: 800;
      white-space: nowrap;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin: 22px 0;
    }
    .card {
      background: linear-gradient(180deg, rgba(255,255,255,0.075), rgba(255,255,255,0.035));
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 20px;
      box-shadow: 0 20px 80px rgba(0, 0, 0, 0.28);
    }
    .label {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-weight: 900;
    }
    .value {
      margin-top: 10px;
      font-size: 32px;
      font-weight: 900;
      letter-spacing: -0.04em;
    }
    .value.good { color: var(--line); }
    .value.warn { color: var(--danger); }
    .wide { grid-column: span 3; }
    .side { grid-column: span 1; }
    svg {
      width: 100%;
      height: auto;
      overflow: visible;
      margin-top: 12px;
    }
    polyline {
      fill: none;
      stroke: var(--line);
      stroke-width: 3.5;
      stroke-linecap: round;
      stroke-linejoin: round;
      filter: drop-shadow(0 0 10px rgba(116, 215, 167, 0.45));
    }
    .meta {
      display: flex;
      justify-content: space-between;
      color: var(--muted);
      font-size: 13px;
      margin-top: 10px;
    }
    .pill-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 16px;
    }
    .pill {
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.06);
      border-radius: 999px;
      padding: 8px 10px;
      font-size: 13px;
      color: var(--muted);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
      font-size: 14px;
    }
    th, td {
      padding: 10px 8px;
      border-bottom: 1px solid var(--border);
      text-align: right;
    }
    th:first-child, td:first-child { text-align: left; }
    th { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
    .note {
      color: var(--muted);
      line-height: 1.55;
      margin-top: 14px;
      font-size: 14px;
    }
    @media (max-width: 900px) {
      header { flex-direction: column; }
      .grid { grid-template-columns: 1fr; }
      .wide, .side { grid-column: auto; }
    }
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <div class="eyebrow">Neural Stock Exchange - Legacy Lab</div>
      <h1>Gold LSTM Legacy</h1>
      <p class="lead">
        Petite interface locale pour visualiser la recharge du modèle historique Gold.
        Le scaler est reconstruit depuis le dataset propre, donc cette sortie est une preuve technique,
        pas une promesse de performance financière.
      </p>
    </div>
    <div class="badge">local only</div>
  </header>

  <section class="grid">
    <article class="card">
      <div class="label">Prediction primitive</div>
      <div class="value good">{{ "%.2f"|format(predicted) }}</div>
    </article>
    <article class="card">
      <div class="label">Valeur réelle</div>
      <div class="value">{{ "%.2f"|format(actual) }}</div>
    </article>
    <article class="card">
      <div class="label">Écart</div>
      <div class="value warn">{{ "%+.2f"|format(delta) }}</div>
    </article>
    <article class="card">
      <div class="label">Écart relatif</div>
      <div class="value warn">{{ "%+.2f"|format(delta_pct) }}%</div>
    </article>
  </section>

  <section class="grid">
    <article class="card wide">
      <div class="label">Gold_Close - derniers points du dataset</div>
      <svg viewBox="0 0 920 220" role="img" aria-label="Courbe Gold Close">
        <polyline points="{{ chart_points }}"></polyline>
      </svg>
      <div class="meta">
        <span>{{ first_date }} → {{ last_date }}</span>
        <span>min {{ "%.2f"|format(chart_min) }} - max {{ "%.2f"|format(chart_max) }}</span>
      </div>
    </article>
    <article class="card side">
      <div class="label">Modèle</div>
      <div class="value" style="font-size: 22px;">{{ model_name }}</div>
      <p class="note">Date cible : {{ target_date }}</p>
      <p class="note">Shape séquence : {{ sequence_shape }}</p>
      <p class="note">Artefact : {{ model_path }}</p>
      <div class="pill-list">
        {% for feature in features %}
          <span class="pill">{{ feature }}</span>
        {% endfor %}
      </div>
    </article>
  </section>

  <section class="card">
    <div class="label">Dernières lignes Gold</div>
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Close</th>
          <th>EMA</th>
          <th>Momentum</th>
        </tr>
      </thead>
      <tbody>
        {% for row in rows %}
        <tr>
          <td>{{ row["Date"].date() }}</td>
          <td>{{ "%.2f"|format(row["Gold_Close"]) }}</td>
          <td>{{ "%.2f"|format(row["Gold_Close_EMA"]) }}</td>
          <td>{{ "%+.4f"|format(row["Momentum"]) }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <p class="note">Aucun conseil financier. Prototype expérimental local, reconstruit depuis les artefacts legacy.</p>
  </section>
</main>
</body>
</html>
"""


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=7864, debug=False, use_reloader=False)

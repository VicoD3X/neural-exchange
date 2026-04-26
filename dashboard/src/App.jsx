import React, { useEffect, useState } from "react";
import {
  chartUrl,
  formatNumber,
  formatPercent,
  loadDashboardData,
  modelLabel,
} from "./data.js";

const tabs = ["Graphiques", "Baselines", "Regimes", "Legacy"];

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("Graphiques");

  useEffect(() => {
    loadDashboardData().then(setData).catch((err) => setError(err.message));
  }, []);

  if (error) {
    return (
      <main className="shell">
        <section className="empty-state">
          <p className="eyebrow">Export manquant</p>
          <h1>Donnée non disponible dans l'export actuel.</h1>
          <code>python scripts/export_dashboard_data.py</code>
          <code>python scripts/sync_dashboard_assets.py</code>
          <p>{error}</p>
        </section>
      </main>
    );
  }

  if (!data) {
    return <main className="shell loading">Chargement du dashboard Rev4...</main>;
  }

  return (
    <main className="shell">
      <Hero data={data} />
      <KpiGrid data={data} />
      <section className="workspace">
        <aside className="side-panel">
          <p className="eyebrow">Verdict critique</p>
          <h2>LSTM utile pour apprendre, pas encore pour battre la baseline.</h2>
          <p>{data.critical_evaluation.message}</p>
          <div className="verdict-card">
            <span>Meilleur MAE</span>
            <strong>{data.summary.best_by_mae}</strong>
          </div>
          <div className="verdict-card muted">
            <span>Panic_Mode test</span>
            <strong>{data.regime_analysis.panic_mode_rows_in_test} lignes</strong>
          </div>
        </aside>
        <section className="main-panel">
          <nav className="tabs" aria-label="Sections dashboard">
            {tabs.map((tab) => (
              <button
                className={tab === activeTab ? "active" : ""}
                key={tab}
                onClick={() => setActiveTab(tab)}
                type="button"
              >
                {tab}
              </button>
            ))}
          </nav>
          {activeTab === "Graphiques" && <Charts data={data} />}
          {activeTab === "Baselines" && <Baselines data={data} />}
          {activeTab === "Regimes" && <Regimes data={data} />}
          {activeTab === "Legacy" && <Legacy data={data} />}
        </section>
      </section>
      <footer>
        <strong>Aucun conseil financier.</strong> Dashboard statique, sans backend, sans inference en
        ligne, construit depuis les rapports Rev4.
      </footer>
    </main>
  );
}

function Hero({ data }) {
  return (
    <section className="hero">
      <div>
        <p className="eyebrow">Experimental LSTM Market Lab</p>
        <h1>Neural Stock Exchange</h1>
        <p>
          Visualisation statique du flux Rev4 : donnees marche et macro, LSTM PyTorch,
          baselines causales et indicateur de stress Panic_Mode.
        </p>
      </div>
      <div className="hero-card">
        <span>Scope</span>
        <strong>{data.summary.dataset_name}</strong>
        <small>{data.metadata.data_scope}</small>
      </div>
    </section>
  );
}

function KpiGrid({ data }) {
  const metrics = data.metrics;
  const critical = data.critical_evaluation;
  const items = [
    ["MAE LSTM", formatNumber(metrics.mae)],
    ["RMSE LSTM", formatNumber(metrics.rmse)],
    ["Direction", formatPercent(metrics.directional_accuracy_percent)],
    ["Ratio MAE", formatNumber(critical.mae_ratio_vs_best_baseline)],
  ];

  return (
    <section className="kpi-grid">
      {items.map(([label, value]) => (
        <article className="kpi" key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </article>
      ))}
    </section>
  );
}

function Charts({ data }) {
  return (
    <div className="chart-grid">
      {data.charts.map((chart) => (
        <article className="chart-card" key={chart.id}>
          <div className="chart-title">
            <span>{chart.title}</span>
          </div>
          <img alt={chart.title} src={chartUrl(chart)} />
        </article>
      ))}
    </div>
  );
}

function Baselines({ data }) {
  return (
    <div className="table-card">
      <h2>Comparaison causale</h2>
      <p>Les baselines utilisent uniquement les informations disponibles avant la date predite.</p>
      <table>
        <thead>
          <tr>
            <th>Modele</th>
            <th>MAE</th>
            <th>RMSE</th>
            <th>MAPE</th>
            <th>Direction</th>
          </tr>
        </thead>
        <tbody>
          {data.baseline_comparison.map((row) => (
            <tr key={row.model}>
              <td>{modelLabel(row.model)}</td>
              <td>{formatNumber(row.mae)}</td>
              <td>{formatNumber(row.rmse)}</td>
              <td>{formatPercent(row.mape_percent)}</td>
              <td>{formatPercent(row.directional_accuracy_percent)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Regimes({ data }) {
  return (
    <div className="regime-grid">
      {data.regime_analysis.segments.map((segment) => (
        <article className="regime-card" key={segment.id}>
          <span>{segment.label}</span>
          <strong>{segment.rows} lignes</strong>
          <p>{segment.status === "available" ? `Best MAE: ${segment.best_by_mae}` : "Données insuffisantes"}</p>
        </article>
      ))}
    </div>
  );
}

function Legacy({ data }) {
  return (
    <div className="legacy-grid">
      {Object.entries(data.legacy).map(([key, value]) => (
        <article className="legacy-card" key={key}>
          <span>{key}</span>
          <p>{value}</p>
        </article>
      ))}
      <article className="legacy-card wide">
        <span>Limites</span>
        <ul>
          {data.limitations.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </article>
    </div>
  );
}

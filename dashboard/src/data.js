const DATA_URL = `${import.meta.env.BASE_URL}dashboard_data.json`;
const ASSET_BASE = `${import.meta.env.BASE_URL}assets/rev4/`;

export async function loadDashboardData() {
  const response = await fetch(DATA_URL);
  if (!response.ok) {
    throw new Error("Donnée non disponible dans l'export actuel.");
  }
  const data = await response.json();
  validateDashboardData(data);
  return data;
}

export function validateDashboardData(data) {
  const requiredKeys = [
    "metadata",
    "summary",
    "metrics",
    "critical_evaluation",
    "baseline_comparison",
    "regime_analysis",
    "charts",
    "limitations",
    "financial_disclaimer",
  ];
  const missing = requiredKeys.filter((key) => !(key in data));
  if (missing.length > 0) {
    throw new Error(`Export dashboard incomplet: ${missing.join(", ")}`);
  }
}

export function chartUrl(chart) {
  const fileName = String(chart.path || "").split("/").pop();
  return `${ASSET_BASE}${fileName}`;
}

export function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "n/a";
  }
  return Number(value).toLocaleString("fr-FR", {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });
}

export function formatPercent(value) {
  return `${formatNumber(value)} %`;
}

export function modelLabel(model) {
  return {
    last_value: "Last value",
    lstm_rev4: "LSTM Rev4",
    moving_average_21: "Moyenne mobile 21",
  }[model] || model;
}

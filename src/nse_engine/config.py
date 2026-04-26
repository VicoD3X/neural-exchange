"""Configuration centrale des futurs datasets Neural Stock Exchange."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOCAL_DATA_DIR = DATA_DIR / "local"
MODELS_DIR = PROJECT_ROOT / "models"
LEGACY_MODELS_DIR = MODELS_DIR / "legacy"
REV4_MODELS_DIR = MODELS_DIR / "rev4"
REPORTS_DIR = PROJECT_ROOT / "reports"
LEGACY_REPORTS_DIR = REPORTS_DIR / "legacy"
CONVERTED_REPORTS_DIR = REPORTS_DIR / "converted"
REV4_REPORTS_DIR = REPORTS_DIR / "rev4"

GOLD_FEATURES_PATH = PROCESSED_DATA_DIR / "gold_features.csv"
MARKET_MACRO_REV4_FEATURES_PATH = PROCESSED_DATA_DIR / "market_macro_rev4_features.csv"
DOW_MACRO_REV4_FEATURES_PATH = PROCESSED_DATA_DIR / "dow_macro_rev4_features.csv"
LEGACY_GOLD_MODEL_PATH = LEGACY_MODELS_DIR / "nse_lstm_light.pt"
LEGACY_DOW_MACRO_MODEL_PATH = LEGACY_MODELS_DIR / "nse_lstm_combined.pt"
REV4_MODEL_PATH = REV4_MODELS_DIR / "nse_lstm_rev4_dow_macro.pt"
REV4_SCALER_PATH = REV4_MODELS_DIR / "nse_lstm_rev4_dow_macro_scaler.joblib"
REV4_METADATA_PATH = REV4_MODELS_DIR / "nse_lstm_rev4_dow_macro.metadata.json"
REV4_REPORT_JSON_PATH = REV4_REPORTS_DIR / "rev4_training_report.json"
REV4_REPORT_MD_PATH = REV4_REPORTS_DIR / "rev4_training_report.md"
REV4_BASELINE_REPORT_JSON_PATH = REV4_REPORTS_DIR / "rev4_baseline_comparison.json"
REV4_BASELINE_REPORT_MD_PATH = REV4_REPORTS_DIR / "rev4_baseline_comparison.md"
REV4_PREDICTIONS_CSV_PATH = REV4_REPORTS_DIR / "rev4_predictions.csv"
REV4_FORECAST_OVERVIEW_PNG_PATH = REV4_REPORTS_DIR / "rev4_forecast_overview.png"
REV4_RESIDUALS_PNG_PATH = REV4_REPORTS_DIR / "rev4_residuals.png"
REV4_METRICS_COMPARISON_PNG_PATH = REV4_REPORTS_DIR / "rev4_metrics_comparison.png"
REV4_ERROR_DISTRIBUTION_PNG_PATH = REV4_REPORTS_DIR / "rev4_error_distribution.png"
REV4_DIRECTION_ACCURACY_PNG_PATH = REV4_REPORTS_DIR / "rev4_direction_accuracy.png"
REV4_MARKET_CONTEXT_PANIC_MODE_PNG_PATH = REV4_REPORTS_DIR / "rev4_market_context_panic_mode.png"
LEGACY_REV2_REPORT_PATH = LEGACY_REPORTS_DIR / "Stats NSE Rev2.xlsx"
LEGACY_REV25_REPORT_PATH = LEGACY_REPORTS_DIR / "Stats NSE Rev2.5.xlsx"
LEGACY_REPORT_JSON_PATH = CONVERTED_REPORTS_DIR / "legacy_predictions_summary.json"
LEGACY_REPORT_MD_PATH = CONVERTED_REPORTS_DIR / "legacy_predictions_summary.md"

FRED_API_KEY_ENV = "FRED_API_KEY"

GOLD_TICKER = "GC=F"
LEGACY_DOW_JONES_TICKER = "^DJI"
DOW_JONES_TICKER = "^DJI"
DOW_JONES_MARKET_NAME = "Dow Jones Industrial Average"
REV4_MARKET_SERIES = "NASDAQCOM"
REV4_MARKET_NAME = "NASDAQ Composite"
REV4_MARKET_CLOSE_COLUMN = "Market_Close"

REV4_START_DATE = "2003-01-01"
REV4_END_DATE = "2010-12-31"

MARKET_SOURCE = "yfinance"
MACRO_SOURCE = "FRED"

FINANCIAL_DISCLAIMER = (
    "Donnees et modeles experimentaux. Aucun resultat ne constitue un conseil financier."
)

GOLD_FEATURE_COLUMNS = [
    "Gold_Close",
    "Gold_Close_Log",
    "Gold_Close_WMA",
    "Gold_Close_EMA",
    "Momentum",
]

LEGACY_GOLD_SEQUENCE_LENGTH = 6
LEGACY_GOLD_HIDDEN_SIZE = 64
LEGACY_DOW_MACRO_SEQUENCE_LENGTH = 4
LEGACY_DOW_MACRO_INPUT_SIZE = 13
LEGACY_DOW_MACRO_HIDDEN_SIZE = 50

REV4_MARKET_COLUMNS = [REV4_MARKET_CLOSE_COLUMN]

MACRO_SERIES = {
    "FEDFUNDS": "Fed Funds Rate",
    "CPIAUCSL": "CPI Inflation",
    "MORTGAGE30US": "30Y Mortgage Rate",
    "UMCSENT": "Consumer Sentiment",
    "T10Y2Y": "10Y-2Y Treasury Spread",
    "UNRATE": "Unemployment Rate",
    "HOUST": "Housing Starts",
    "TOTALSA": "Total Consumer Credit",
}

REV4_ENGINEERED_COLUMNS = [
    "Volatility_1W",
    "Volatility_1M",
    "Panic_Mode",
]

DOW_MACRO_REV4_FEATURE_COLUMNS = [
    *REV4_MARKET_COLUMNS,
    *MACRO_SERIES.keys(),
    *REV4_ENGINEERED_COLUMNS,
]

MARKET_MACRO_REV4_FEATURE_COLUMNS = DOW_MACRO_REV4_FEATURE_COLUMNS

REV4_TARGET_COLUMN = REV4_MARKET_CLOSE_COLUMN
REV4_PRIMARY_DATASET_NAME = "dow_macro_rev4_features"
REV4_PRIMARY_DATASET_PATH = DOW_MACRO_REV4_FEATURES_PATH
REV4_SEQUENCE_LENGTH = 21
REV4_TRAIN_RATIO = 0.8
REV4_HIDDEN_SIZE = 64
REV4_BATCH_SIZE = 32
REV4_LEARNING_RATE = 0.001
REV4_EPOCHS = 60
REV4_RANDOM_SEED = 42

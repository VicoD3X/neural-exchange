import yfinance as yf
import pandas as pd
import fredapi
import os

FRED_API_KEY = os.getenv("FRED_API_KEY")

### 🚀 Récupération des données du Dow Jones (^DJI) en daily ###
def fetch_dowjones_data(start_date, end_date):
    print(f"📊 [Rev3] Fetching Dow Jones (^DJI) daily data from {start_date} to {end_date}...")
    data = yf.download("^DJI", start=start_date, end=end_date, interval="1d")

    if data.empty:
        print("❌ No Dow Jones data retrieved.")
        return None
    
    print("✅ Dow Jones daily data retrieved successfully.")
    
    # Renommer les colonnes pour éviter les conflits
    data = data.rename(columns={
        "Adj Close": "DJI_Adj_Close",
        "Close": "DJI_Close",
        "Open": "DJI_Open",
        "High": "DJI_High",
        "Low": "DJI_Low",
        "Volume": "DJI_Volume"
    })

    # Réinitialiser l'index pour avoir la colonne 'Date'
    data.reset_index(inplace=True)
    
    return data

### 🚀 Récupération des données macroéconomiques (FRED), enrichies ###
def fetch_macro_data(start_date, end_date):
    print(f"📈 [Rev3] Fetching macroeconomic data (daily resample) between {start_date} and {end_date}...")
    
    if not FRED_API_KEY:
        print("❌ Missing FRED_API_KEY environment variable.")
        return None

    try:
        fred = fredapi.Fred(api_key=FRED_API_KEY)
    except Exception as e:
        print(f"❌ Failed to initialize FRED API: {e}")
        return None

    # Liste élargie de séries
    macro_series = {
        "FEDFUNDS": "Fed Funds Rate",
        "CPIAUCSL": "CPI Inflation",
        "MORTGAGE30US": "30Y Mortgage Rate",
        "UMCSENT": "Consumer Sentiment",
        "T10Y2Y": "10Y-2Y Treasury Spread",
        "UNRATE": "Unemployment Rate",
        "HOUST": "Housing Starts",
        "TOTALSA": "Total Consumer Credit"
    }

    macro_data = {}
    for series, description in macro_series.items():
        try:
            data = fred.get_series(series, start_date, end_date)
            if data is None or data.empty:
                print(f"⚠️ No data for {description} ({series})!")
            else:
                print(f"✅ {description} ({series}) data retrieved.")
            macro_data[series] = data
        except Exception as e:
            print(f"⚠️ Error fetching {description} ({series}): {e}")
            macro_data[series] = None

    df_macro = pd.DataFrame(macro_data)
    df_macro.index = pd.to_datetime(df_macro.index)

    # Avant resampling (certaines séries sont mensuelles, d'autres hebdo)
    print("\n🧐 Macro DataFrame before daily resampling:")
    print(df_macro.head(10))

    # Resampling en daily pour aligner sur ^DJI (1 jour)
    all_days = pd.date_range(start=start_date, end=end_date, freq='D')
    df_macro = df_macro.reindex(all_days).ffill().interpolate()

    print("\n✅ Macro DataFrame after daily resampling & ffill/interpolate:")
    print(df_macro.head(10))
    print(df_macro.tail(3))

    # On veut garder une colonne 'Date'
    df_macro.reset_index(inplace=True)
    df_macro.rename(columns={"index": "Date"}, inplace=True)

    return df_macro

### 🚀 Sauvegarde des datasets ###
def save_separate_datasets(dowjones_df, macro_df):
    print("\n💾 Saving separate datasets for Rev3...")

    # Assure-toi que le dossier /data existe, sinon on le crée
    os.makedirs("data", exist_ok=True)

    dowjones_file = "data/Rev3_dji.csv"
    macro_file = "data/Rev3_macro.csv"

    dowjones_df.to_csv(dowjones_file, index=False)
    print(f"✅ Dow Jones dataset saved as {dowjones_file}")

    macro_df.to_csv(macro_file, index=False)
    print(f"✅ Macro dataset saved as {macro_file}")

### 🚀 Pipeline principal ###
def fetch_and_save_all_data():
    start_date = "2003-01-01"
    end_date   = "2010-12-31"
    print(f"🏁 [Rev3] Collecting ^DJI + macro from {start_date} to {end_date}")

    # 1) Dow Jones data
    dowjones_data = fetch_dowjones_data(start_date, end_date)
    # 2) Macro data
    macro_data = fetch_macro_data(start_date, end_date)

    if dowjones_data is not None and not dowjones_data.empty \
       and macro_data is not None and not macro_data.empty:
        save_separate_datasets(dowjones_data, macro_data)
        print("\n✅ [Rev3] All data successfully saved.")
    else:
        print("\n❌ [Rev3] Failed to fetch all required data.")

### 🚀 Lancer la collecte ###
if __name__ == "__main__":
    fetch_and_save_all_data()

import os
import numpy as np
import pandas as pd
import yfinance as yf

def fetch_and_prepare_gold_data(
    start_date="1970-01-01",   # Début maximal (approx.) pour GC=F
    end_date=None,            # None => Jusqu'à la date actuelle (aujourd'hui)
    interval="1d",            # Fréquence quotidienne
    output_file="NSE_Light/data/Train_light.csv"
):
    """
    Télécharge les données Gold Futures (GC=F) via yfinance (du 01/01/1970 à aujourd'hui).

    """

    # Assure l'existence du dossier
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    date_fin_affichee = end_date if end_date else "aujourd'hui"
    print(f"📂 Récupération des données XAU/USD ({interval}) de {start_date} à {date_fin_affichee}...")

    try:
        # 1) Téléchargement des données brutes
        df = yf.download("GC=F", start=start_date, end=end_date, interval=interval)
        if df.empty:
            print("❌ Aucune donnée récupérée de Yahoo Finance.")
            return

        # 2) Nettoyage initial : Date + Gold_Close
        df.reset_index(inplace=True)
        df.rename(columns={"Date": "Date", "Adj Close": "Gold_Close"}, inplace=True)

        # Conserver uniquement Date et Gold_Close (pas besoin du Open, High, Low, Volume)
        df = df[["Date", "Gold_Close"]].dropna()

        # Tri par date si nécessaire
        df.sort_values("Date", inplace=True)

        # 3) Calcul des indicateurs
        # 3.1) Log du prix
        df["Gold_Close_Log"] = np.log(df["Gold_Close"])

        # 3.2) WMA (Weighted Moving Average) sur 3 points
        def wma_3(series):
            if len(series) < 3:
                return np.nan
            return 0.5*series.iloc[-1] + 0.3*series.iloc[-2] + 0.2*series.iloc[-3]
        df["Gold_Close_WMA"] = df["Gold_Close"].rolling(window=3).apply(wma_3, raw=False)

        # 3.3) EMA (Exponential Moving Average) sur 3 points
        df["Gold_Close_EMA"] = df["Gold_Close"].ewm(span=3, adjust=False).mean()

        # 3.4) Momentum (variation sur 1 pas)
        df["Momentum"] = df["Gold_Close"].pct_change()

        # On enlève d'éventuelles lignes NaN
        df.dropna(inplace=True)

        # 4) Sauvegarde en CSV unique
        df.to_csv(output_file, index=False)
        print(f"✅ Données enrichies sauvegardées dans {output_file}")

    except Exception as e:
        print(f"❌ Erreur lors de la récupération ou du traitement : {e}")


# ------------------------------------------------------------------------
# Point d'entrée principal
# ------------------------------------------------------------------------
if __name__ == "__main__":
    fetch_and_prepare_gold_data()

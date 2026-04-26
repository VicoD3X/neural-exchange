import tkinter as tk
from tkinter import scrolledtext
import pandas as pd
import numpy as np
import torch
import datetime
import sys
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

print("🚀 Lancement de NSE Light Display...")

# -----------------------------------------------------------------------------
# Import du modèle et de la fonction prepare_sequences (version multi-features)
# -----------------------------------------------------------------------------
try:
    from starter_light import LSTMModel, prepare_sequences
except ImportError:
    print("❌ Impossible d'importer starter_light.py. Vérifiez qu'il se trouve dans le même dossier ou le PYTHONPATH.")
    sys.exit(1)

# -----------------------------------------------------------------------------
# Chemins d'accès aux fichiers
# -----------------------------------------------------------------------------
DATA_PATH = "NSE_Light/data/Train_light.csv"
MODEL_PATH = "NSE_Light/models/nse_lstm_light.pt"

# -----------------------------------------------------------------------------
# Chargement du modèle et des données
# -----------------------------------------------------------------------------
def load_model_and_data(file_path, model_path, sequence_length, hidden_size):
    """
    1) Lit le CSV enrichi (plusieurs colonnes, ex: [Gold_Close, Gold_Close_Log, etc.]).
    2) Appelle prepare_sequences(df, sequence_length) => X, y, scaler, used_cols.
    3) Initialise le LSTM (input_size = nb_features).
    4) Charge les poids du modèle LSTM.
    5) Retourne (df, model, scaler, used_cols).
    """
    try:
        # Lecture du CSV, index = Date
        df = pd.read_csv(file_path, parse_dates=["Date"])
        df.set_index("Date", inplace=True)
        df.dropna(how="any", inplace=True)  # On enlève les lignes NaN

        print(f"✅ Données chargées : {df.shape[0]} lignes, {df.shape[1]} colonnes.")

        # On n'utilise pas 'y' dans l'inférence, donc on met `_` ou None
        X, _, scaler, used_cols = prepare_sequences(df, sequence_length)

        # On crée le LSTM en fonction du nombre de features
        nb_features = X.shape[2]
        model = LSTMModel(
            input_size=nb_features,
            hidden_size=hidden_size,
            output_size=1
        )

        # Charger les poids (weights_only=True => PyTorch >=2.1)
        model.load_state_dict(
            torch.load(model_path, map_location=torch.device("cpu"), weights_only=True)
        )
        model.eval()

        print("✅ Modèle chargé et prêt pour la prédiction.")
        return df, model, scaler, used_cols

    except Exception as e:
        print(f"❌ Erreur lors du chargement des données ou du modèle : {e}")
        return None, None, None, None

# -----------------------------------------------------------------------------
# Validation de la date entrée par l'utilisateur
# -----------------------------------------------------------------------------
def validate_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

# -----------------------------------------------------------------------------
# Génération dynamique des valeurs futures (jour par jour), multivarié
# -----------------------------------------------------------------------------
def generate_future_sequence_daily(df, model, scaler, used_cols, sequence_length, num_days=1):
    """
    Extrapole jour par jour en prenant *toutes* les colonnes (used_cols).
    On considère que la 1ère colonne (Gold_Close) est la cible principale.
    Retourne la dernière valeur prédite (float) pour Gold_Close.
    """
    temp_df = df[used_cols].copy()  # On ne prend que les colonnes utiles
    future_values = []

    # Trouver l'indice de la colonne Gold_Close
    if "Gold_Close" in used_cols:
        gold_idx = used_cols.index("Gold_Close")
    else:
        # Si pas de Gold_Close => on arrête
        print("❌ 'Gold_Close' introuvable dans used_cols.")
        return None

    for _ in range(num_days):
        last_sequence = temp_df.iloc[-sequence_length:].values  # shape [seq_length, nb_features]
        seq_scaled = scaler.transform(last_sequence)
        seq_tensor = torch.tensor(seq_scaled[np.newaxis, :, :], dtype=torch.float32)

        with torch.no_grad():
            pred_scaled = model(seq_tensor).item()

        # Reconstruire un vecteur scaled complet (0 partout sauf la valeur d'intérêt)
        fake_scaled = np.zeros((1, len(used_cols)), dtype=np.float32)
        fake_scaled[0, gold_idx] = pred_scaled

        real_values = scaler.inverse_transform(fake_scaled)
        predicted_gold_close = real_values[0, gold_idx]

        # Ajout de la nouvelle ligne (Date = dernier + 1 jour)
        new_date = temp_df.index[-1] + pd.DateOffset(days=1)

        # On initialise la nouvelle ligne : on duplique la dernière pour "remplir" 
        # (ou on met tout à NA, à vous de voir)
        new_row = temp_df.iloc[-1].copy()
        # Seule la colonne Gold_Close est mise à jour
        new_row["Gold_Close"] = predicted_gold_close

        # Ajout au DataFrame
        temp_df.loc[new_date] = new_row
        future_values.append(predicted_gold_close)

    return future_values[-1]

# -----------------------------------------------------------------------------
# Comparaison avec ARIMA et Prophet (facultatif)
# -----------------------------------------------------------------------------
def compare_models(df):
    """
    Compare ARIMA et Prophet sur ~6 pas de temps futurs de la colonne Gold_Close.
    Retourne (arima_pred, prophet_pred) ou (None, None).
    """
    try:
        # ARIMA
        arima_model = ARIMA(df["Gold_Close"], order=(5,1,0))
        arima_fit = arima_model.fit()
        arima_pred = arima_fit.forecast(steps=6).iloc[-1]

        # Prophet
        df_prophet = df.reset_index().rename(columns={"Date": "ds", "Gold_Close": "y"})
        prophet_model = Prophet()
        prophet_model.fit(df_prophet)
        future = prophet_model.make_future_dataframe(periods=6, freq="W")
        prophet_pred = prophet_model.predict(future)["yhat"].iloc[-1]

        return arima_pred, prophet_pred

    except Exception as e:
        print(f"❌ Erreur dans Prophet/ARIMA : {e}")
        return None, None

# -----------------------------------------------------------------------------
# Prédiction du prix de l'or pour une date donnée (multivarié)
# -----------------------------------------------------------------------------
def predict_for_date(df, model, scaler, used_cols, date_str, sequence_length):
    date_obj = validate_date(date_str)
    if not date_obj:
        return "❌ Date invalide. Format attendu : YYYY-MM-DD."

    last_date = df.index[-1]

    # Si la date est future => extrapolation jour par jour
    if date_obj > last_date:
        num_days = (date_obj - last_date).days
        if num_days < 1:
            num_days = 1
        print(f"🕵️‍♂️ Génération dynamique des valeurs jusqu'à {date_obj} ({num_days} jours)...")

        predicted_value = generate_future_sequence_daily(df, model, scaler, used_cols, sequence_length, num_days)
        if predicted_value is None:
            return "❌ Erreur lors de la génération future (Gold_Close introuvable)."

        arima_pred, prophet_pred = compare_models(df)
        return (
            f"📊 NSE Light : {predicted_value:.2f}€ (Projection dynamique)\n"
            f"📊 ARIMA : {arima_pred:.2f}€\n"
            f"📊 Prophet : {prophet_pred:.2f}€"
        )

    # Sinon, c'est une date historique => on prend la séquence [date_idx - seq_len : date_idx]
    if date_obj not in df.index:
        return "❌ La date fournie n'existe pas dans l'historique de données."

    date_idx = df.index.get_loc(date_obj)
    if date_idx < sequence_length:
        return "⚠️ Pas assez de données pour une prédiction à cette date."

    sub_df = df.iloc[date_idx - sequence_length : date_idx][used_cols]
    arr = sub_df.values
    scaled = scaler.transform(arr)
    tensor = torch.tensor(scaled[np.newaxis, :, :], dtype=torch.float32)

    with torch.no_grad():
        pred_scaled = model(tensor).item()

    # Identifie l'indice de Gold_Close
    if "Gold_Close" not in used_cols:
        return "❌ Impossible de retrouver Gold_Close dans used_cols, échec inverse_transform."

    gold_idx = used_cols.index("Gold_Close")
    fake_scaled = np.zeros((1, len(used_cols)), dtype=np.float32)
    fake_scaled[0, gold_idx] = pred_scaled
    real_values = scaler.inverse_transform(fake_scaled)
    predicted_gold_close = real_values[0, gold_idx]

    return f"📊 Prédiction du prix de l'or après {date_str} : {predicted_gold_close:.2f}€"

# -----------------------------------------------------------------------------
# Interface utilisateur Tkinter
# -----------------------------------------------------------------------------
class GoldChatUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NSE Light - Prédictions multivariées")

        # Zone de texte
        self.chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=15, font=("Arial", 10))
        self.chat_box.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Message de bienvenue
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(
            tk.END,
            "🏆 Bienvenue dans NSE Light - Analyse de l'Or (multi-features) !\n"
            "🔎 Entrez une date (format YYYY-MM-DD) pour une prédiction.\n"
            "🛑 Tapez 'exit' pour quitter.\n\n"
        )
        self.chat_box.config(state=tk.DISABLED)

        # Champ de saisie
        self.entry = tk.Entry(root, width=20, font=("Arial", 12))
        self.entry.grid(row=1, column=0, padx=10, pady=10)

        # Bouton prédiction
        self.predict_button = tk.Button(root, text="📈 Prédire", command=self.get_prediction, font=("Arial", 12))
        self.predict_button.grid(row=1, column=1, padx=10, pady=10)

        # Bouton sortie
        self.quit_button = tk.Button(root, text="❌ Quitter", command=root.quit, font=("Arial", 12))
        self.quit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Paramètres
        self.sequence_length = 6
        self.hidden_size = 64

        # Chargement DataFrame + modèle
        self.df, self.model, self.scaler, self.used_cols = load_model_and_data(
            DATA_PATH, MODEL_PATH, self.sequence_length, self.hidden_size
        )

        if self.df is None or self.model is None or self.scaler is None:
            self.chat_box.config(state=tk.NORMAL)
            self.chat_box.insert(tk.END, "\n❌ Erreur : Impossible de charger le modèle ou les données.\n")
            self.chat_box.config(state=tk.DISABLED)

    def get_prediction(self):
        user_input = self.entry.get().strip()
        if user_input.lower() == "exit":
            self.root.quit()
            return

        if self.df is None or self.model is None or self.scaler is None:
            response = "❌ Modèle ou données indisponibles."
        else:
            response = predict_for_date(
                self.df, self.model, self.scaler, self.used_cols,
                user_input, self.sequence_length
            )

        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"\n🧑‍💻 Vous : {user_input}\n🏆 {response}\n")
        self.chat_box.config(state=tk.DISABLED)
        self.entry.delete(0, tk.END)

# -----------------------------------------------------------------------------
# Lancement de l'application
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GoldChatUI(root)
    root.mainloop()

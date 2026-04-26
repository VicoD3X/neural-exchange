import tkinter as tk
from tkinter import scrolledtext
import pandas as pd
import numpy as np
import torch
import datetime

# Importer le modèle LSTM depuis starter.py
from starter import LSTMModel, load_combined_data, prepare_sequences

# Charger le modèle et les données
def load_model_and_data(file_path_dji, file_path_macro, model_path, sequence_length, hidden_size):
    """
    Charger les datasets fusionnés et le modèle entraîné.
    """
    # Charger les données DJI et Macro
    df = load_combined_data(file_path_dji, file_path_macro)

    # Convertir Date en datetime et l'utiliser comme index
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    # Vérifier que l'index est bien au format datetime
    print(f"📆 Index après correction : {df.index}")

    # Préparer les séquences et le scaler
    x, _, scaler = prepare_sequences(df, sequence_length)

    # Initialisation du modèle
    model = LSTMModel(input_size=x.shape[2], hidden_size=hidden_size, output_size=1)

    # Charger uniquement les poids du modèle fusionné
    model.load_state_dict(torch.load(model_path))
    model.eval()

    return df, model, scaler, x

# Vérifier la validité de la date
def validate_date(date_str, date_format="%Y-%m-%d"):
    try:
        date = datetime.datetime.strptime(date_str, date_format)
        return date
    except ValueError:
        return None

# Faire une prédiction pour une date donnée
def predict_for_date(df, model, scaler, x, date_str, sequence_length):
    date = validate_date(date_str)
    if not date:
        return "❌ Date invalide. Format attendu : AAAA-MM-JJ."

    # Vérifier si la date est bien dans l'index
    if date not in df.index:
        print(f"⚠️ Date {date} non trouvée dans l'index. Voici les premières et dernières dates de l'index :")
        print(f"📆 Première date : {df.index.min()}, Dernière date : {df.index.max()}")
        return f"⚠️ Date hors de la plage des données ({df.index.min().strftime('%Y-%m-%d')} à {df.index.max().strftime('%Y-%m-%d')})."

    date_idx = df.index.get_loc(date)
    if date_idx < sequence_length:
        return "⚠️ Pas assez de données avant cette date pour une prédiction."

    sequence = df.iloc[date_idx-sequence_length:date_idx].values  # Prendre toutes les features
    sequence_scaled = scaler.transform(sequence)
    sequence_tensor = torch.tensor(sequence_scaled[np.newaxis, :, :], dtype=torch.float32)

    with torch.no_grad():
        prediction_scaled = model(sequence_tensor).item()
        predicted_value = scaler.inverse_transform([[prediction_scaled] + [0] * (sequence.shape[1] - 1)])[0, 0]

    # Vérifier si le Panic Mode est activé
    panic_mode = df.iloc[date_idx]["Panic_Mode"]
    panic_message = "⚠️ ALERTE CRISE : PANIC MODE ACTIVÉ ⚠️" if panic_mode == 1 else "✅ Marché stable"

    return f"📊 Prédiction pour la semaine après {date_str} : {predicted_value:.2f}€\n{panic_message}"

# Interface utilisateur avec Tkinter
class NSEChatUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NSE Rev-2.5 - Prédictions Fusionnées")

        # Zone d'affichage du chat
        self.chat_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15, font=("Arial", 10))
        self.chat_box.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.chat_box.insert(tk.END, "💬 Bienvenue dans le système NSE Rev-2.5 !\n")
        self.chat_box.insert(tk.END, "📅 Entrez une date entre 2005-01-01 et 2009-12-28 pour une prédiction.\n")
        self.chat_box.insert(tk.END, "🛑 Tapez 'exit' pour quitter.\n\n")
        self.chat_box.config(state=tk.DISABLED)

        # Zone d'entrée utilisateur
        self.entry = tk.Entry(root, width=30, font=("Arial", 12))
        self.entry.grid(row=1, column=0, padx=10, pady=10)

        # Bouton de prédiction
        self.predict_button = tk.Button(root, text="📈 Prédire", command=self.get_prediction, font=("Arial", 12))
        self.predict_button.grid(row=1, column=1, padx=10, pady=10)

        # Bouton Quitter
        self.quit_button = tk.Button(root, text="❌ Quitter", command=root.quit, font=("Arial", 12))
        self.quit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Charger modèle et données
        self.file_path_dji = "data/Rev2_dji.csv"
        self.file_path_macro = "data/Rev2_macro.csv"
        self.model_path = "models/nse_lstm_combined.pt"
        self.sequence_length = 4
        self.hidden_size = 50

        self.df, self.model, self.scaler, self.x = load_model_and_data(
            self.file_path_dji, self.file_path_macro, self.model_path, self.sequence_length, self.hidden_size
        )

    def get_prediction(self):
        user_input = self.entry.get().strip()

        if user_input.lower() == "exit":
            self.root.quit()

        response = predict_for_date(self.df, self.model, self.scaler, self.x, user_input, self.sequence_length)

        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"\n🧑‍💻 Vous : {user_input}\n")
        self.chat_box.insert(tk.END, f"🤖 NSE : {response}\n")
        self.chat_box.config(state=tk.DISABLED)

        self.entry.delete(0, tk.END)

# Lancer l'interface Tkinter
if __name__ == "__main__":
    root = tk.Tk()
    app = NSEChatUI(root)
    root.mainloop()

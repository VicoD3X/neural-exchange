import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import os
import random

# -----------------------------------------------------------------------------
# Configuration des hyperparamètres
# -----------------------------------------------------------------------------
CONFIG = {
    "sequence_length": 6,
    "hidden_size": 64,
    "batch_size": 16,
    "learning_rate": 0.0005,
    "epochs": 30,
}

# -----------------------------------------------------------------------------
# Colonnes/features qu'on souhaite utiliser (si elles existent dans le CSV)
# -----------------------------------------------------------------------------
FEATURE_COLUMNS = [
    "Gold_Close",
    "Gold_Close_Log",
    "Gold_Close_WMA",
    "Gold_Close_EMA",
    "Momentum"
]

# -----------------------------------------------------------------------------
# Chargement des données de l'or
# -----------------------------------------------------------------------------
def load_gold_data(file_path):
    print(f"📂 Chargement du fichier : {file_path}")

    try:
        df = pd.read_csv(file_path, parse_dates=["Date"], index_col="Date")
        # On s'assure que 'Gold_Close' est bien numérique
        df["Gold_Close"] = pd.to_numeric(df["Gold_Close"], errors="coerce")
        df.dropna(subset=["Gold_Close"], inplace=True)

        print(f"✅ Données chargées : {df.shape[0]} lignes, {df.shape[1]} colonnes.")
        return df
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données : {e}")
        return None

# -----------------------------------------------------------------------------
# Préparer les séquences pour l'entraînement (multivarié)
# -----------------------------------------------------------------------------
def prepare_sequences(data, sequence_length):
    """
    1) Sélectionne les colonnes FEATURE_COLUMNS disponibles dans le DataFrame.
    2) Applique un MinMaxScaler globalement sur ces colonnes.
    3) Construit les séquences (X) et les cibles (Y).
       - X : [batch, sequence_length, nb_features]
       - Y : [batch, 1]  (ici la cible = 'Gold_Close' du pas suivant)
    """
    # On filtre les colonnes existantes
    used_cols = [col for col in FEATURE_COLUMNS if col in data.columns]
    if not used_cols:
        raise ValueError("❌ Aucune des FEATURE_COLUMNS n'est présente dans le DataFrame.")

    # On prépare le MinMaxScaler
    scaler = MinMaxScaler()

    # On récupère toutes les valeurs (ex: 5 colonnes => shape [N, 5])
    raw_values = data[used_cols].values
    scaled_data = scaler.fit_transform(raw_values)  # shape : [N, nb_features]

    sequences, targets = [], []
    # Indice de la colonne 'Gold_Close' dans used_cols (pour la cible)
    # On suppose que used_cols contient "Gold_Close" ! 
    # (Sinon, adapt. ex: la cible est la 1re col.)
    target_idx = used_cols.index("Gold_Close")

    for i in range(len(scaled_data) - sequence_length):
        # X => séquence multivariée de length = sequence_length
        seq_x = scaled_data[i : i + sequence_length]
        sequences.append(seq_x)

        # Y => la valeur "Gold_Close" du pas suivant (i + sequence_length)
        seq_y = scaled_data[i + sequence_length, target_idx]  # scalaire
        targets.append(seq_y)

    # Convertir en np.array
    sequences = np.array(sequences)  # shape [N - seq_len, seq_len, nb_features]
    targets = np.array(targets).reshape(-1, 1)  # shape [N - seq_len, 1]

    return sequences, targets, scaler, used_cols

# -----------------------------------------------------------------------------
# Modèle LSTM (pas de changement majeur, sauf input_size variable)
# -----------------------------------------------------------------------------
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=1, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # x shape : [batch_size, sequence_length, input_size]
        _, (hidden, _) = self.lstm(x)  # hidden shape : [1, batch_size, hidden_size]
        out = self.fc(hidden[-1])      # out shape : [batch_size, output_size]
        return out

# -----------------------------------------------------------------------------
# Ajouter du bruit économique (optionnel)
# -----------------------------------------------------------------------------
def add_noise(predicted_value, df, strength=0.05):
    """
    Ajoute un bruit économique basé sur la volatilité des 3 derniers mois.
    """
    volatility = df["Gold_Close"].pct_change().rolling(12).std().iloc[-1]
    noise = random.uniform(-strength, strength) * volatility
    return predicted_value * (1 + noise)

# -----------------------------------------------------------------------------
# Fonction d'entraînement
# -----------------------------------------------------------------------------
def train_model(model, train_loader, epochs, criterion, optimizer):
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for x_batch, y_batch in train_loader:
            optimizer.zero_grad()
            output = model(x_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"📈 Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(train_loader):.4f}")

# -----------------------------------------------------------------------------
# Entraîner et évaluer le modèle sur l'or
# -----------------------------------------------------------------------------
def train_and_evaluate_gold(file_path):
    print(f"🚀 Entraînement du modèle sur {file_path}")

    df = load_gold_data(file_path)
    if df is None:
        return None, None

    # Préparation des séquences multi-features
    sequences, targets, scaler, used_cols = prepare_sequences(df, CONFIG["sequence_length"])
    print(f"✅ Features utilisées : {used_cols}")

    # Convertir en tenseurs PyTorch
    x_tensor = torch.tensor(sequences, dtype=torch.float32)   # shape [samples, seq_len, nb_features]
    y_tensor = torch.tensor(targets, dtype=torch.float32)     # shape [samples, 1]

    # LSTM input_size = nb_features (par exemple 5 si vous avez 5 colonnes)
    nb_features = sequences.shape[2]

    model = LSTMModel(
        input_size=nb_features,
        hidden_size=CONFIG["hidden_size"],
        output_size=1
    )

    dataset = TensorDataset(x_tensor, y_tensor)
    train_loader = DataLoader(dataset, batch_size=CONFIG["batch_size"], shuffle=True)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=CONFIG["learning_rate"])

    print("🔄 Entraînement du modèle stable...")
    train_model(model, train_loader, CONFIG["epochs"], criterion, optimizer)

    # Sauvegarde du modèle
    os.makedirs("NSE_Light/models", exist_ok=True)
    model_path = "NSE_Light/models/nse_lstm_light.pt"
    try:
        torch.save(model.state_dict(), model_path)
        print(f"✅ Modèle stable entraîné et sauvegardé sous {model_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du modèle : {e}")

    return model

# -----------------------------------------------------------------------------
# Pipeline principal
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    file_path = "NSE_Light/data/Train_light.csv"
    train_and_evaluate_gold(file_path)

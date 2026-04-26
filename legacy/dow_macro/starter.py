# Importations générales
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import os

# Configuration des hyperparamètres
CONFIG = {
    "sequence_length": 4,
    "hidden_size": 50,
    "batch_size": 16,
    "learning_rate": 0.001,
    "epochs": 20,
}

# Ajouter un indicateur de "Taux de Violence" basé sur la volatilité
def add_volatility_features(df):
    """
    Ajoute un indicateur de volatilité basé sur la variation des prix sur 1 semaine et 1 mois.
    """
    # Convertir DJI_Close en float (gestion des erreurs pour éviter le crash)
    df["DJI_Close"] = pd.to_numeric(df["DJI_Close"], errors="coerce")

    # Vérifier si la colonne est bien en float
    if df["DJI_Close"].isna().sum() > 0:
        print("⚠️ Attention : Certaines valeurs de DJI_Close sont NaN après conversion !")

    df["Volatility_1W"] = df["DJI_Close"].pct_change(periods=1).fillna(0)  # Variation hebdomadaire
    df["Volatility_1M"] = df["DJI_Close"].pct_change(periods=4).fillna(0)  # Variation mensuelle

    # Indicateur de "panic mode" si la volatilité dépasse un certain seuil
    df["Panic_Mode"] = ((df["Volatility_1W"].abs() > 0.05) | (df["Volatility_1M"].abs() > 0.1)).astype(int)

    return df


# Charger les données combinées
def load_combined_data(dji_path, macro_path):
    print(f"📂 Chargement des fichiers : {dji_path} et {macro_path}")

    try:
        df_dji = pd.read_csv(dji_path)
        df_macro = pd.read_csv(macro_path)

        # Convertir la colonne Date en datetime
        df_dji["Date"] = pd.to_datetime(df_dji["Date"])
        df_macro["Date"] = pd.to_datetime(df_macro["Date"])

        # Fusionner sur la colonne Date
        df = pd.merge(df_dji, df_macro, on="Date", how="left")

        # Ajouter la volatilité et Panic Mode
        df = add_volatility_features(df)

        # Supprimer les valeurs manquantes
        df.dropna(inplace=True)

        print(f"✅ Données fusionnées : {df.shape[0]} lignes, {df.shape[1]} colonnes.")
        return df
    except Exception as e:
        print(f"❌ Erreur lors du chargement des données : {e}")
        return None

# Préparer les séquences pour l'entraînement avec plusieurs features
def prepare_sequences(data, sequence_length):
    scaler = MinMaxScaler()

    # Supprimer la colonne Date avant de scaler
    if "Date" in data.columns:
        data = data.drop(columns=["Date"])

    scaled_data = scaler.fit_transform(data.values)  # Transformer uniquement les valeurs numériques

    sequences, targets = [], []
    for i in range(len(scaled_data) - sequence_length):
        sequences.append(scaled_data[i:i+sequence_length])
        targets.append(scaled_data[i+sequence_length, 0])  # Prédire uniquement DJI_Close

    return np.array(sequences), np.array(targets), scaler

# Définir un modèle LSTM capable de gérer plusieurs entrées
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        _, (hidden, _) = self.lstm(x)
        out = self.fc(hidden[-1])
        return out

# Fonction d'entraînement
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

# Entraîner et évaluer le modèle combiné
def train_and_evaluate_combined(dji_path, macro_path):
    print(f"🚀 Entraînement du modèle fusionné sur {dji_path} et {macro_path}")

    df = load_combined_data(dji_path, macro_path)
    if df is None:
        return None, None

    x, y, scaler = prepare_sequences(df, CONFIG["sequence_length"])
    x_tensor = torch.tensor(x, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1)  # Ajout d'une dimension pour compatibilité

    model = LSTMModel(input_size=x.shape[2], hidden_size=CONFIG["hidden_size"], output_size=1)
    dataset = TensorDataset(x_tensor, y_tensor)
    train_loader = DataLoader(dataset, batch_size=CONFIG["batch_size"], shuffle=True)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=CONFIG["learning_rate"])

    print("🔄 Entraînement du modèle fusionné...")
    train_model(model, train_loader, CONFIG["epochs"], criterion, optimizer)

    # Sauvegarde du modèle fusionné
    os.makedirs("models", exist_ok=True)
    try:
        model_path = "models/nse_lstm_combined.pt"
        torch.save(model.state_dict(), model_path)
        print(f"✅ Modèle fusionné entraîné et sauvegardé sous {model_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde du modèle : {e}")

    model.eval()
    with torch.no_grad():
        last_sequence = torch.tensor(x[-1:], dtype=torch.float32)
        prediction = model(last_sequence).item()
        predicted_value = scaler.inverse_transform([[prediction] + [0] * (x.shape[2] - 1)])[0, 0]
        print(f"📊 Prédiction pour la prochaine semaine (Modèle Fusionné): {predicted_value:.2f}")

    return model, predicted_value

# Pipeline principal
if __name__ == "__main__":
    dji_path = "data/Rev2_dji.csv"
    macro_path = "data/Rev2_macro.csv"

    model, prediction = train_and_evaluate_combined(dji_path, macro_path)

    print("\n🔍 **Résultat du modèle fusionné**:")
    print(f"📊 Prédiction finale (Modèle Fusionné): {prediction:.2f}")

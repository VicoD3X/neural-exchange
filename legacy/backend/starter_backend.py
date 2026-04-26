from flask import Flask, jsonify, request
from flask_cors import CORS
from starter import load_data, moving_average, predict_next_week

app = Flask(__name__)
CORS(app)  # Pour autoriser les requêtes venant du frontend React

# Endpoint pour charger les données
@app.route('/data', methods=['GET'])
def get_data():
    df = load_data()
    return jsonify(df.tail(10).to_dict(orient='records'))

# Endpoint pour la prédiction
@app.route('/predict', methods=['POST'])
def predict():
    df = load_data()
    window_size = request.json.get('window_size', 4)
    prediction, _ = predict_next_week(df, window_size)
    return jsonify({"prediction": prediction})

if __name__ == '__main__':
    app.run(debug=True)

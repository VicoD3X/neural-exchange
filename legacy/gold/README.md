# Legacy Gold

Ancien prototype Gold de Neural Stock Exchange.

Statut :
- flux le plus recuperable ;
- modele legacy compatible en dimensions avec les features Gold historiques ;
- ancien CSV place en quarantaine, donc le dataset devra etre regenere.

Fichiers :
- `gold_data.py` : ancienne collecte et enrichissement Gold ;
- `starter_light.py` : ancien entrainement LSTM Gold ;
- `display_light.py` : ancienne inference Tkinter avec comparaison ARIMA / Prophet.

Decision :
utiliser ce dossier comme reference pour reconstruire `nse-engine-gold` proprement.


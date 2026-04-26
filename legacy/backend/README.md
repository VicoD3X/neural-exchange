# Legacy Backend

Ancien backend Flask.

Statut :
casse et conserve uniquement comme trace.

Probleme principal :
`starter_backend.py` importe des fonctions qui n'existent plus dans l'ancien `starter.py` :
- `load_data` ;
- `moving_average` ;
- `predict_next_week`.

Decision :
ne pas reparer maintenant. Aucune API ne doit etre construite avant stabilisation d'un flux local reproductible.


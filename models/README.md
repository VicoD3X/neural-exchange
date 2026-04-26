# Models

Ce dossier regroupe les artefacts modele du projet.

Deux familles coexistent :

- `models/legacy/` : poids historiques conserves pour leur valeur d'apprentissage et de recuperation technique.
- `models/rev4/` : premier modele LSTM Rev4 reproductible, avec scaler et metadata.

Les modeles ne doivent pas etre presentes comme des systemes fiables de prevision financiere.
Ils servent a documenter un laboratoire experimental de series temporelles.

## Rev4

Le flux Rev4 sauvegarde trois artefacts ensemble :

- `nse_lstm_rev4_dow_macro.pt` : poids PyTorch ;
- `nse_lstm_rev4_dow_macro_scaler.joblib` : scaler ajuste sur la partie entrainement ;
- `nse_lstm_rev4_dow_macro.metadata.json` : schema, features, hyperparametres et metriques.

Cette structure corrige une limite des modeles legacy : le scaler est maintenant conserve.

## Legacy

Voir `models/legacy/README.md`.

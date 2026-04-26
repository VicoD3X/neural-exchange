# Legacy Models

Modeles historiques de Neural Stock Exchange.

Ces artefacts sont conserves pour documenter l'evolution du projet et l'apprentissage terrain autour des LSTM.
Ils ne doivent pas etre presentes comme des modeles robustes de prevision financiere.

## nse_lstm_light.pt

Nom logique :
`nse-engine-gold-legacy`.

Statut :
recuperable et teste primitivement.

Contrat :
- input_size = 5 ;
- hidden_size = 64 ;
- sequence_length = 6 ;
- features : Gold_Close, Gold_Close_Log, Gold_Close_WMA, Gold_Close_EMA, Momentum.

Validation :
le modele charge dans l'environnement actuel et produit une prediction primitive depuis `data/processed/gold_features.csv`.

Limite :
le scaler n'a pas ete sauvegarde. Il est reconstruit depuis le dataset Gold propre, ce qui rend la prediction utile comme test technique, pas comme preuve de performance.

## nse_lstm_combined.pt

Nom logique :
`nse-engine-legacy-dow-macro`.

Statut :
archive Rev2 chargeable en dry-run architecture uniquement.

Contrat :
- input_size = 13 ;
- hidden_size = 50 ;
- sequence_length historique = 4.

Limite :
les fichiers Rev2 d'origine sont absents et le scaler n'a pas ete sauvegarde.
Rev3 reste `legacy-advanced`, mais non actif.
Rev4 dispose de datasets propres, mais ce modele ne doit pas y etre branche par simple changement de chemin.

Regle :
ne pas brancher ce modele sur Rev3 ou Rev4.
Toute utilisation future devra passer par un nouveau modele Rev4 avec scaler, metadata et schema de features sauvegardes.

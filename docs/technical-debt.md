# Dette technique

Cette note liste les zones connues qui ne doivent pas etre confondues avec le flux actif.

## Legacy

- Scripts historiques conserves dans `legacy/`.
- Backend Flask archive, non repare.
- Dashboard React archive, non maintenu.
- Notebooks anciens conserves comme traces.

## Modeles

- Les modeles legacy n'ont pas de scaler historique sauvegarde.
- Le modele Dow/Macro legacy ne doit pas etre branche a Rev3 ou Rev4.
- Le modele Gold legacy fonctionne seulement comme recuperation primitive.

## Donnees

- Les datasets complets sont regenerables et ignores par Git.
- Rev3 reste `legacy-advanced`, non actif.
- Rev4 doit rester la base reproductible.

## Prochaines ameliorations possibles

- Ajouter une validation walk-forward.
- Ajouter d'autres baselines au-dela de `last_value` et moyenne mobile.
- Evaluer specifiquement les periodes de stress.
- Ameliorer l'analyse de `Panic_Mode` avec faux positifs et faux negatifs.
- Ajouter un dashboard uniquement apres consolidation de l'evaluation.
- Repenser un dashboard uniquement quand le flux inference est stabilise.

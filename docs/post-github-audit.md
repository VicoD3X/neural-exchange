# Audit post-GitHub - Neural Stock Exchange

## Lecture generale

Neural Stock Exchange est maintenant lisible comme un laboratoire experimental autour des series temporelles financieres, des LSTM PyTorch, des donnees macro et de la detection de regimes de stress.

Le depot ne cherche pas a vendre une prediction de marche. Sa valeur principale est la demarche : recuperation d'un prototype personnel, separation du legacy, reconstruction Rev4, evaluation contre baselines, rapports reproductibles et transparence sur les limites.

## Forces actuelles

- README fort et visuel, avec graphes Rev4 directement visibles.
- Flux Rev4 reproductible : dataset local, modele, scaler, metadata, rapports et graphiques.
- Evaluation critique contre baselines causales.
- Documentation explicite sur `Panic_Mode`, les limites et les revisions legacy.
- Tests offline couvrant nettoyage, sequences, fuite temporelle, metadata, reporting et scripts critiques.
- CI GitHub Actions presente pour pytest, ruff et pip check.

## Faiblesses restantes

- Pas encore de validation walk-forward avancee.
- Analyse des regimes de stress encore limitee par la fenetre de test actuelle.
- Le LSTM Rev4 ne bat pas `last_value` sur le MAE.
- Les modeles legacy restent utiles historiquement, mais incomplets conceptuellement sans scaler d'origine.
- Les dashboards visualisent les rapports existants, ils ne remplacent pas une evaluation scientifique plus robuste.

## Risques a surveiller

- Surpromesse financiere : le projet doit rester un laboratoire, pas un outil de decision.
- Confusion entre prediction de prix et detection de regime.
- Lecture trop optimiste du signal directionnel.
- Regression de reproductibilite si les exports dashboard ne sont pas synchronises apres regeneration Rev4.

## Priorites scientifiques

1. Ajouter une validation walk-forward simple.
2. Evaluer les erreurs par regime de marche sur une fenetre plus adaptee.
3. Tester differents seuils `Panic_Mode`.
4. Comparer Dow seul, NASDAQ seul et Dow + NASDAQ.
5. Separer clairement forecasting de prix et detection de stress.

## Priorites portfolio

1. Garder le README centre sur le verdict critique.
2. Maintenir les graphes Rev4 a jour.
3. Proposer un dashboard Streamlit local pour l'analyse.
4. Proposer un dashboard React statique pour GitHub Pages.
5. Garder Flask en archive legacy tant qu'aucune API publique n'est justifiee.

## Decision dashboard

- Streamlit : retenu pour l'analyse locale rapide.
- React/Vite : retenu pour la vitrine GitHub Pages.
- Flask : hors scope, conserve uniquement comme historique legacy.

## Verdict

Le projet est suffisamment propre pour etre presente comme laboratoire experimental. Le prochain vrai saut de niveau ne viendra pas d'une interface plus spectaculaire, mais d'une evaluation temporelle plus robuste et d'une meilleure analyse des regimes de stress.

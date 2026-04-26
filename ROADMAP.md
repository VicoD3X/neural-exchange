# Roadmap - Neural Stock Exchange

Cette roadmap decrit les prochaines evolutions apres publication GitHub.

Le projet reste un laboratoire experimental. Les evolutions ci-dessous doivent renforcer la reproductibilite, l'evaluation et la lisibilite, sans transformer le depot en produit financier.

## Priorite 1 - Evaluation Rev4

Objectif : mesurer plus serieusement le premier modele Rev4.

- Ajouter une baseline naive : derniere valeur connue.
- Ajouter une baseline moyenne mobile.
- Comparer Rev4 contre les baselines sur MAE, RMSE, MAPE et direction.
- Ajouter une validation walk-forward simple.
- Evaluer separement les periodes de stress, notamment 2008-2009.
- Documenter clairement les limites des resultats.

## Priorite 2 - Flux multi-marches

Objectif : tester si la combinaison Dow Jones + NASDAQ apporte un signal plus riche.

- Construire un dataset Rev4 multi-marches.
- Ajouter `Dow_Close`, `Nasdaq_Close`, volatilites separees et features macro communes.
- Comparer trois approches : Dow seul, NASDAQ seul, Dow + NASDAQ.
- Garder une cible explicite : prix de marche ou signal de stress, pas les deux sans separation.
- Ne pas presenter le resultat comme une prediction de crise.

## Priorite 3 - Signal de stress

Objectif : recentrer une partie du projet sur la detection de regime plutot que la prediction exacte du prix.

- Formaliser `Panic_Mode`.
- Tester des seuils de volatilite alternatifs.
- Ajouter une lecture precision / recall sur les periodes de stress historiques.
- Documenter les faux positifs et faux negatifs.
- Comparer un signal simple base volatilite contre le LSTM.

## Priorite 4 - Reporting et visualisation locale

Objectif : rendre les resultats plus lisibles sans ajouter une architecture lourde.

- Ajouter un rapport Markdown enrichi pour Rev4.
- Ajouter un export JSON unifie pour les resultats modele.
- Ajouter quelques graphiques statiques dans `reports/`.
- Eventuellement ajouter une interface Streamlit locale minimale.
- Ne pas relancer le dashboard React tant que l'inference n'est pas stabilisee.

## Priorite 5 - Nettoyage legacy progressif

Objectif : conserver l'histoire du projet sans laisser le legacy brouiller le flux actif.

- Documenter les scripts legacy restants.
- Identifier ce qui peut etre archive plus proprement.
- Garder les modeles `.pt` legacy avec leur documentation.
- Ne pas brancher le modele Dow/Macro legacy sur Rev4.
- Conserver Rev3 comme inspiration technique uniquement.

## Priorite 6 - Qualite projet

Objectif : rendre le depot plus robuste pour une lecture externe.

- Ajouter une CI GitHub Actions minimale.
- Lancer `pytest`, `ruff` et `pip check` en CI.
- Ajouter un badge CI au README.
- Ajouter un scan secrets manuel avant chaque push important.
- Ajouter un guide de contribution minimal si le projet grossit.

## Hors scope

Ces elements ne sont pas prevus a court terme :

- bot de trading ;
- API publique ;
- backend production ;
- dashboard complexe ;
- promesse de prediction de marche ;
- conseil financier ;
- deploiement cloud.

## Positionnement cible

Neural Stock Exchange doit rester un laboratoire local clair, honnete et reproductible autour des signaux financiers, des features macroeconomiques et des LSTM PyTorch.

Le succes du projet ne se mesure pas a une promesse de profit, mais a la qualite de la demarche : donnees propres, evaluation serieuse, limites explicites et experimentation lisible.

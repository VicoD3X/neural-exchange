# Resume du projet

Neural Stock Exchange est un projet experimental de series temporelles financieres.

Il doit etre lu comme un laboratoire etudiant avance : un ancien prototype personnel, conserve avec ses revisions legacy, puis reconstruit autour d'un flux Rev4 plus propre et mesurable.

L'objectif est d'explorer comment combiner :

- donnees de marche ;
- variables macroeconomiques ;
- volatilite court et moyen terme ;
- signaux de stress de type `Panic_Mode` ;
- modeles LSTM PyTorch.

Le projet a ete reconstruit autour d'un moteur propre, `nse-engine`, pour separer les scripts historiques du flux reproductible.

## Positionnement

Le depot est un laboratoire local, pas un produit financier.

Il montre une demarche technique :

- recuperation de prototypes legacy ;
- documentation des limites ;
- regeneration de donnees propres ;
- entrainement d'un baseline Rev4 ;
- comparaison du LSTM avec des baselines simples ;
- conversion de rapports historiques ;
- tests offline.

La comparaison critique est centrale : le projet documente explicitement quand le LSTM ne bat pas une baseline naive, afin de montrer une demarche d'evaluation mature.

## Revisions

| Revision | Statut | Description |
|---|---|---|
| Rev2 | Legacy | Ancien prototype Dow/Macro avec modele conserve mais donnees/scaler incomplets |
| Rev2.5 | Legacy | Variante de reporting historique avec `Panic_Mode` |
| Rev3 | Legacy-advanced | Prototype avance, non retenu comme base active |
| Rev4 | Reproductible | Flux propre avec dataset, scaler, modele, metadata et rapport |

## Non-objectifs

Le projet ne vise pas a fournir :

- un bot de trading ;
- un conseil financier ;
- une prediction fiable des marches ;
- une application de production ;
- un systeme de gestion de risque reel.

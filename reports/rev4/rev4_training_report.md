# Rapport Rev4 - Neural Stock Exchange

## Synthese

- Modele : `nse-lstm-rev4-dow-macro`
- Dataset : `dow_macro_rev4_features`
- Cible : `Market_Close`
- Train rows : 1594
- Test rows : 399

## Metriques

- MAE : 209.86
- RMSE : 238.41
- MAPE : 2.04%
- Directional accuracy : 53.52%

## Comparaison critique

- Verdict : Le LSTM Rev4 ne bat pas la meilleure baseline naive sur le MAE. Ce resultat n'est pas un echec : il montre que le modele est evalue contre une reference simple.

| Modele | MAE | RMSE | MAPE % | Direction % |
|---|---:|---:|---:|---:|
| last_value | 72.34 | 101.00 | 0.72 | 50.25 |
| lstm_rev4 | 209.86 | 238.41 | 2.04 | 53.52 |
| moving_average_21 | 225.67 | 265.50 | 2.23 | 55.78 |

Cette section compare le LSTM Rev4 a des baselines causales simples. Elle sert a verifier si le modele apporte un signal utile par rapport a des references naives.

## Entrainement

- Sequence length : 21
- Hidden size : 64
- Epochs : 60
- Batch size : 32
- Learning rate : 0.001
- Loss initiale : 0.064024
- Loss finale : 0.000369

## Apercu predictions

| Date | Reel | Prediction | Ecart |
|---|---:|---:|---:|
| 2010-12-16 | 11499.25 | 11314.74 | -184.51 |
| 2010-12-17 | 11491.91 | 11354.02 | -137.89 |
| 2010-12-20 | 11478.13 | 11374.63 | -103.50 |
| 2010-12-21 | 11533.16 | 11376.16 | -157.00 |
| 2010-12-22 | 11559.49 | 11382.62 | -176.87 |
| 2010-12-23 | 11573.49 | 11392.88 | -180.61 |
| 2010-12-27 | 11555.03 | 11401.00 | -154.03 |
| 2010-12-28 | 11575.54 | 11403.82 | -171.72 |
| 2010-12-29 | 11585.38 | 11409.90 | -175.48 |
| 2010-12-30 | 11569.71 | 11417.52 | -152.19 |

## Limites

- Modele experimental local, non destine au trading.
- Evaluation retrospective uniquement sur la periode disponible.
- Aucune promesse de prediction fiable des marches ou des crises.

> Donnees et modeles experimentaux. Aucun resultat ne constitue un conseil financier.

# Comparaison critique Rev4 - LSTM vs baselines

## Synthese

- Modele : `nse-lstm-rev4-dow-macro`
- Dataset : `dow_macro_rev4_features`
- Cible : `Market_Close`
- Test rows : 399
- Meilleur MAE : `last_value`

## Verdict

- Statut : `lstm_does_not_beat_best_naive_baseline`
- Lecture : Le LSTM Rev4 ne bat pas la meilleure baseline naive sur le MAE. Ce resultat n'est pas un echec : il montre que le modele est evalue contre une reference simple.
- Meilleure baseline : `last_value`
- Rang du LSTM par MAE : 2
- Delta MAE vs meilleure baseline : 137.52
- Ratio MAE vs meilleure baseline : 2.90
- Delta direction vs meilleure baseline : +3.27 points

## Metriques

| Modele | MAE | RMSE | MAPE % | Direction % |
|---|---:|---:|---:|---:|
| last_value | 72.34 | 101.00 | 0.72 | 50.25 |
| lstm_rev4 | 209.86 | 238.41 | 2.04 | 53.52 |
| moving_average_21 | 225.67 | 265.50 | 2.23 | 55.78 |

## Lecture

- La comparaison utilise uniquement des baselines causales simples.
- Une baseline naive forte peut battre un LSTM sur une serie financiere de prix.
- Ces resultats sont retrospectifs et ne constituent pas une preuve de prediction future.

## Dernieres predictions

| Date | Reel | LSTM | Last value | Moving average 21 |
|---|---:|---:|---:|---:|
| 2010-12-16 | 11499.25 | 11314.74 | 11457.47 | 11247.90 |
| 2010-12-17 | 11491.91 | 11354.02 | 11499.25 | 11270.55 |
| 2010-12-20 | 11478.13 | 11374.63 | 11491.91 | 11293.60 |
| 2010-12-21 | 11533.16 | 11376.16 | 11478.13 | 11307.74 |
| 2010-12-22 | 11559.49 | 11382.62 | 11533.16 | 11323.43 |
| 2010-12-23 | 11573.49 | 11392.88 | 11559.49 | 11341.57 |
| 2010-12-27 | 11555.03 | 11401.00 | 11573.49 | 11367.15 |
| 2010-12-28 | 11575.54 | 11403.82 | 11555.03 | 11384.66 |
| 2010-12-29 | 11585.38 | 11409.90 | 11575.54 | 11407.69 |
| 2010-12-30 | 11569.71 | 11417.52 | 11585.38 | 11433.07 |

> Donnees et modeles experimentaux. Aucun resultat ne constitue un conseil financier.

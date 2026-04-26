# Inventaire des modeles

Le projet contient deux familles de modeles : legacy et Rev4.

## Modeles legacy

Les modeles legacy sont conserves pour leur valeur historique et technique.
Ils ne constituent pas une preuve de performance robuste.

| Modele | Statut | Notes |
|---|---|---|
| `nse_lstm_light.pt` | Gold legacy recuperable | Prediction primitive possible avec scaler reconstruit |
| `nse_lstm_combined.pt` | Dow/Macro legacy archive | Chargeable en dry-run, non branche a Rev3 ou Rev4 |

Limite majeure :
les scalers historiques n'ont pas ete sauvegardes.

## Modele Rev4

Le modele Rev4 principal est :

`models/rev4/nse_lstm_rev4_dow_macro.pt`

Il est accompagne de :

- `nse_lstm_rev4_dow_macro_scaler.joblib` ;
- `nse_lstm_rev4_dow_macro.metadata.json`.

Cette structure rend le flux plus propre que les modeles legacy.

## Lecture des performances

Les metriques Rev4 sont retrospectives et exploratoires.
Elles valident surtout que la chaine technique fonctionne.

Le rapport Rev4 compare aussi le LSTM a deux baselines simples :

- derniere valeur connue ;
- moyenne mobile 21 jours.

La comparaison actuelle montre que `last_value` est plus solide sur l'erreur de prix.
Ce resultat est conserve volontairement, car il rend l'evaluation plus credible.

Elles ne doivent pas etre interpretees comme une promesse de prediction future.

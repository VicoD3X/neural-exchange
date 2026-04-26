# Inventaire des donnees

Les donnees completes sont locales et regenerables.
Elles ne sont pas versionnees par defaut.

## Sources

| Flux | Source | Role |
|---|---|---|
| Gold | yfinance `GC=F` | Variante legacy Gold et dataset de reference |
| Dow Jones | yfinance `^DJI` | Flux principal Rev4 Dow/Macro |
| NASDAQ | FRED `NASDAQCOM` | Vue marche alternative Rev4 |
| Macro | FRED | Variables macroeconomiques |

## Datasets generes localement

Les scripts generent des CSV dans `data/processed/` :

- `gold_features.csv` ;
- `dow_macro_rev4_features.csv` ;
- `market_macro_rev4_features.csv`.

Ces fichiers sont ignores par Git car ils peuvent etre reconstruits.

Commande Rev4 complete :

```bash
python scripts/run_rev4_pipeline.py
```

Cette commande regenere `dow_macro_rev4_features.csv`, puis relance l'entrainement Rev4,
les rapports et les graphiques.
Elle necessite un acces reseau et peut utiliser `FRED_API_KEY` si la recuperation FRED par API est active.

## Schema Rev4 Dow/Macro

Colonnes principales :

- `Date` ;
- `Market_Close` ;
- `FEDFUNDS` ;
- `CPIAUCSL` ;
- `MORTGAGE30US` ;
- `UMCSENT` ;
- `T10Y2Y` ;
- `UNRATE` ;
- `HOUST` ;
- `TOTALSA` ;
- `Volatility_1W` ;
- `Volatility_1M` ;
- `Panic_Mode`.

## Nettoyage

Les regles appliquees sont volontairement strictes :

- parser `Date` en datetime ;
- supprimer les dates invalides ;
- convertir les colonnes numeriques ;
- rejeter les valeurs manquantes non maitrisees ;
- trier les observations dans l'ordre temporel ;
- produire des metadata de generation.

## Donnees legacy

Les anciens CSV Rev2 / Rev3 / Gold historique ne sont pas utilises comme sources actives.
Rev3 peut servir d'inspiration pour comprendre certaines features, mais le flux reproductible repart de Rev4.

# nse-engine

Ce dossier contiendra le moteur propre de **Neural Stock Exchange**.

Objectif futur :
- collecte de donnees marche et macro ;
- nettoyage strict des exports ;
- feature engineering temporel ;
- preparation de sequences LSTM ;
- entrainement et inference PyTorch ;
- generation de rapports reproductibles.

Les anciens scripts ont ete deplaces dans `legacy/` et ne doivent pas etre modifies directement sans decision explicite.

## Bloc 3 - donnees

Les premiers modules actifs posent les contrats data :

- `config.py` : tickers, periode Rev4, chemins et schemas de features ;
- `data_cleaning.py` : nettoyage Date / numerique / NaN / schema ;
- `features.py` : features Gold et candidates Rev4 ;
- `metadata.py` : metadata standardisee ;
- `data_sources.py` : appels yfinance / FRED, uniquement utilises par scripts explicites.

Rev3 reste `legacy-advanced`.
Le futur flux actif est Rev4.

## Bloc 4 - modeles legacy

`legacy_models.py` permet de relire les poids historiques sans les melanger avec le flux actif :

- Gold legacy : prediction primitive recuperable ;
- Dow/Macro legacy : chargement/dry-run seulement, sans branchement Rev3 ou Rev4.

## Bloc 5 - Rev4 reproductible

Les modules actifs du nouveau flux Rev4 sont :

- `sequences.py` : preparation des sequences temporelles et split train/test ;
- `lstm.py` : modele LSTM PyTorch et boucle d'entrainement ;
- `training.py` : orchestration modele + scaler + metadata ;
- `reporting.py` : generation des rapports JSON et Markdown.

Commande principale :

```bash
python scripts/train_rev4_model.py
```

Le flux Rev4 sauvegarde le modele, le scaler et les metadata dans `models/rev4/`,
puis le rapport dans `reports/rev4/`.

## Bloc 6 - reporting legacy

`legacy_reporting.py` convertit les rapports Excel historiques en exports propres :

- CSV par revision ;
- JSON de synthese ;
- Markdown lisible.

Commande principale :

```bash
python scripts/convert_legacy_reports.py
```

Cette conversion ne recalcule pas la performance.
Elle rend seulement les observations historiques auditables.

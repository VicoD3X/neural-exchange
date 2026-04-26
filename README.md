# Neural Stock Exchange - Experimental LSTM Market Lab

![Python](https://img.shields.io/badge/Python-3.11-blue)
![CI](https://github.com/VicoD3X/neural-exchange/actions/workflows/ci.yml/badge.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-LSTM-orange)
![Status](https://img.shields.io/badge/Status-Experimental_MVP-lightgrey)
![Data](https://img.shields.io/badge/Data-FRED_+_yfinance-0f766e)
![No Advice](https://img.shields.io/badge/No_financial_advice-required-red)

## Presentation

Neural Stock Exchange est un laboratoire experimental autour des series temporelles financieres.

Le projet explore la combinaison de donnees de marche, de variables macroeconomiques, de features de volatilite et de modeles LSTM PyTorch pour analyser des signaux de stress sur la periode 2003-2010.

Ce depot ne presente pas un produit financier, un bot de trading ou une promesse de prediction fiable. Il documente une remise en etat progressive d'un prototype personnel vers un moteur local plus propre, testable et reproductible.

## Avertissement

Ce projet est strictement experimental.

Les resultats, rapports, predictions et signaux `Panic_Mode` ne constituent pas un conseil financier. Ils ne doivent pas etre utilises pour prendre des decisions d'investissement, de trading ou de gestion de risque reel.

## Objectif

Le projet vise a montrer :

- la collecte de donnees marche et macro ;
- le nettoyage strict de series temporelles ;
- la creation de features de volatilite ;
- la preparation de sequences LSTM ;
- l'entrainement d'un baseline Rev4 reproductible ;
- la conservation documentee de modeles legacy ;
- la conversion de rapports historiques en Markdown, CSV et JSON.

## Architecture

```text
.
|-- data/                 # Donnees locales regenerables, non versionnees par defaut
|-- docs/                 # Documentation publique du projet
|-- legacy/               # Scripts historiques conserves comme archive technique
|-- models/
|   |-- legacy/           # Poids historiques Rev2 / Gold legacy
|   `-- rev4/             # Modele Rev4, scaler et metadata
|-- reports/
|   |-- legacy/           # Rapports historiques Excel
|   |-- converted/        # Exports legacy propres
|   `-- rev4/             # Rapport du modele Rev4
|-- scripts/              # Commandes locales
|-- src/nse_engine/       # Moteur Python propre
|-- tests/                # Tests offline
|-- requirements.txt
|-- requirements-legacy.txt
|-- requirements-dev.txt
`-- README.md
```

## Revisions

Le projet distingue clairement plusieurs etapes.

| Revision | Statut | Role |
|---|---|---|
| Rev2 | Legacy | Prototype Dow/Macro historique, modele conserve mais donnees/scaler incomplets |
| Rev2.5 | Legacy | Ajout historique du signal `Panic_Mode` dans les rapports |
| Rev3 | Legacy-advanced | Prototype avance, utile comme inspiration, non utilise comme pipeline actif |
| Rev4 | Reproductible | Flux reconstruit avec dataset propre, LSTM, scaler, metadata et rapport |

## nse-engine et nse-engine-gold

`nse-engine` est le moteur Python propre du projet. Il contient le nettoyage, les features, la preparation de sequences, les modeles LSTM, le reporting et les conversions legacy.

`nse-engine-gold` designe la variante historique Gold. Elle sert de preuve de recuperation technique du vieux LSTM Gold, avec une prediction primitive documentee. Ce flux reste legacy et ne doit pas etre presente comme un modele financier fiable.

## Donnees

Les donnees completes ne sont pas versionnees par defaut.

Sources utilisees ou preparees :

- Gold : yfinance, ticker `GC=F` ;
- Dow Jones : yfinance, ticker `^DJI` ;
- NASDAQ : FRED public, serie `NASDAQCOM` ;
- macro : FRED, avec fallback CSV public quand possible.

Les exports locaux sont generes dans `data/processed/` et restent ignores par Git car ils sont reconstruisibles.

## Commandes locales

Installation :

```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
```

Dépendances legacy optionnelles :

```bash
.\.venv\Scripts\python.exe -m pip install -r requirements-legacy.txt
```

Generer les datasets :

```bash
python scripts/build_gold_dataset.py
python scripts/build_dow_macro_rev4_dataset.py
python scripts/build_market_macro_rev4_dataset.py
```

Verifier les modeles legacy :

```bash
python scripts/check_legacy_models.py
```

Entrainer le modele Rev4 :

```bash
python scripts/train_rev4_model.py
```

Convertir les rapports historiques :

```bash
python scripts/convert_legacy_reports.py
```

Lancer les tests :

```bash
pytest tests -q
ruff check src scripts tests
pip check
```

## Resultats disponibles

Le depot contient deux familles de resultats lisibles :

- `reports/converted/legacy_predictions_summary.md` : conversion des rapports Rev2 et Rev2.5.
- `reports/rev4/rev4_training_report.md` : premier rapport du baseline LSTM Rev4.
- `reports/rev4/rev4_baseline_comparison.md` : comparaison critique LSTM vs baselines.

Les performances Rev4 sont retrospectives et exploratoires. Elles servent a valider que le flux fonctionne, pas a prouver une capacite de prediction exploitable.

## Evaluation critique

Le modele Rev4 est compare a deux baselines simples :

- derniere valeur connue ;
- moyenne mobile 21 jours.

Cette comparaison est volontairement centrale : un LSTM n'a d'interet que s'il apporte quelque chose face a des references simples.

Resultat actuel :

| Modele | MAE | RMSE | MAPE % | Direction % |
|---|---:|---:|---:|---:|
| Last value | 72.34 | 101.00 | 0.72 | 50.25 |
| LSTM Rev4 | 209.86 | 238.41 | 2.04 | 53.52 |
| Moving average 21 | 225.67 | 265.50 | 2.23 | 55.78 |

Lecture : la baseline `last_value` est meilleure sur l'erreur de prix, ce qui rappelle qu'un LSTM ne doit jamais etre juge sans baseline naive. Le LSTM Rev4 reste utile comme base experimentale reproductible, mais il ne constitue pas encore un modele de forecasting robuste.

Les graphiques disponibles dans `reports/rev4/` montrent :

- reel vs LSTM vs baselines ;
- residus du LSTM et des baselines.

## Tests

Les tests sont concus pour rester offline.

Ils couvrent notamment :

- nettoyage de ligne parasite type yfinance ;
- validation de schema ;
- calcul de features `Panic_Mode` ;
- preparation de sequences LSTM ;
- absence de fuite temporelle simple ;
- shapes LSTM ;
- metadata ;
- conversion de rapports legacy ;
- absence d'appel reseau dans les scripts critiques offline.

## Limites

- Aucune garantie de performance predictive.
- Pas de validation walk-forward avancee.
- Pas de conseil financier.
- Pas de dashboard actif.
- Backend Flask historique archive, non maintenu.
- Rev2 et Rev2.5 sont documentes mais non reproductibles completement.
- Rev3 reste une archive avancee, non utilisee comme source active.

## Documentation

Voir aussi :

- `docs/project-summary.md`
- `docs/data-inventory.md`
- `docs/model-inventory.md`
- `docs/reporting.md`
- `docs/limitations.md`
- `docs/technical-debt.md`
- `ROADMAP.md`

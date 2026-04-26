# Reporting

Le projet contient deux types de rapports.

## Rapports legacy convertis

Les fichiers Excel historiques sont conserves dans `reports/legacy/`.
Ils sont convertis en exports propres dans `reports/converted/`.

Commande :

```bash
python scripts/convert_legacy_reports.py
```

Exports :

- `legacy_rev2_predictions.csv` ;
- `legacy_rev25_predictions.csv` ;
- `legacy_predictions_summary.json` ;
- `legacy_predictions_summary.md`.

Ces exports documentent :

- dates testees ;
- predictions ;
- valeurs reelles ;
- ecarts ;
- `Panic_Mode` quand disponible ;
- notes historiques.

Aucun resultat n'est invente ou recalcule pendant cette conversion.

## Rapport Rev4

Le rapport Rev4 est genere pendant l'entrainement :

```bash
python scripts/train_rev4_model.py
```

Le flux complet peut aussi etre relance avec :

```bash
python scripts/run_rev4_pipeline.py
```

Exports :

- `reports/rev4/rev4_training_report.json` ;
- `reports/rev4/rev4_training_report.md`.
- `reports/rev4/rev4_baseline_comparison.json` ;
- `reports/rev4/rev4_baseline_comparison.md` ;
- `reports/rev4/rev4_predictions.csv` ;
- `reports/rev4/rev4_forecast_overview.png` ;
- `reports/rev4/rev4_residuals.png` ;
- `reports/rev4/rev4_metrics_comparison.png` ;
- `reports/rev4/rev4_error_distribution.png` ;
- `reports/rev4/rev4_direction_accuracy.png` ;
- `reports/rev4/rev4_market_context_panic_mode.png`.

Le rapport contient les metriques retrospectives, les features, les hyperparametres,
un apercu de predictions, une comparaison contre deux baselines simples et des graphiques
scientifiques clairs pour lire le contexte, les erreurs, les residus et la direction.

## Interpretation

Les rapports servent a comprendre le comportement historique et experimental du projet.
Ils ne doivent pas etre utilises comme preuve de robustesse financiere.

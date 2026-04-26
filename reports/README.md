# Reports

Ce dossier regroupe les rapports historiques et reproductibles du projet.

## Rev4

`reports/rev4/` contient le rapport du premier entrainement Rev4 :

- `rev4_training_report.json` : format structure pour exploitation future ;
- `rev4_training_report.md` : lecture humaine rapide.

Le rapport est genere par :

```bash
python scripts/train_rev4_model.py
```

## Converted

`reports/converted/` contient la conversion des rapports Excel historiques :

- `legacy_rev2_predictions.csv` ;
- `legacy_rev25_predictions.csv` ;
- `legacy_predictions_summary.json` ;
- `legacy_predictions_summary.md`.

Ces fichiers sont generes par :

```bash
python scripts/convert_legacy_reports.py
```

Ils documentent les dates testees, les predictions, les valeurs reelles, les ecarts
et les lignes `Panic Mode` quand elles existent dans la source.
Aucun resultat n'est invente ou recalcule.

## Legacy

Les rapports historiques sont conserves dans `reports/legacy/`.
Ils ne doivent pas etre interpretes comme des resultats reproductibles modernes sans conversion et documentation.

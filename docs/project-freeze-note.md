# Note de gel temporaire

## Etat du projet

Neural Stock Exchange est mis en pause dans un etat sain.

Le depot contient :

- un flux Rev4 reproductible ;
- un modele LSTM PyTorch avec scaler et metadata ;
- une comparaison critique contre baselines causales ;
- des graphiques Rev4 versionnes ;
- un dashboard Streamlit local ;
- un dashboard React/Vite deploye sur GitHub Pages ;
- une documentation publique alignee ;
- une CI GitHub Actions active.

## Validation de gel

Derniere validation locale :

```bash
pytest tests -q
ruff check src scripts tests
pip check
pip-audit -r requirements.txt -r requirements-dev.txt -r requirements-app.txt
cd dashboard
npm run build
```

GitHub Pages :

[https://vicod3x.github.io/neural-exchange/](https://vicod3x.github.io/neural-exchange/)

## Regles pour la reprise

- Ne pas relancer une refonte globale.
- Ne pas reactiver Flask sans besoin d'API clair.
- Ne pas transformer le projet en outil financier.
- Conserver le verdict critique LSTM vs baseline au centre du projet.
- Prioriser ensuite la validation walk-forward et l'analyse des regimes de stress.

## Prochaine reprise recommandee

Le prochain vrai saut de niveau doit porter sur :

1. validation walk-forward ;
2. analyse Panic_Mode par seuils ;
3. comparaison Dow seul / NASDAQ seul / multi-marche ;
4. meilleure separation forecasting de prix vs detection de regime.

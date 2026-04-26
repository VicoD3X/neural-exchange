# Dashboards

Neural Stock Exchange propose deux visualisations complementaires.

## Streamlit local

Le dashboard Streamlit sert de cockpit d'analyse local.

Commande :

```bash
pip install -r requirements-app.txt
python scripts/export_dashboard_data.py
streamlit run app/streamlit_app.py
```

Il affiche :

- KPI Rev4 ;
- comparaison LSTM vs baselines ;
- graphiques Rev4 ;
- analyse par regime quand les donnees sont disponibles ;
- limites et avertissement financier.

## React / GitHub Pages

Le dashboard React/Vite sert de vitrine publique statique.

URL :

[https://vicod3x.github.io/neural-exchange/](https://vicod3x.github.io/neural-exchange/)

Commandes locales :

```bash
python scripts/export_dashboard_data.py
python scripts/sync_dashboard_assets.py
cd dashboard
npm install
npm run dev
```

Build :

```bash
npm run build
```

## Contrat de donnees

Les deux dashboards lisent le meme export :

```text
reports/rev4/dashboard_data.json
```

Le dashboard statique utilise une copie synchronisee :

```text
dashboard/public/dashboard_data.json
dashboard/public/assets/rev4/*.png
```

## Limites

- Aucun backend.
- Aucune inference en ligne.
- Aucun appel reseau.
- Aucun recalcul du modele au lancement.
- Aucun conseil financier.

Les dashboards sont des lecteurs de rapports. Ils ne remplacent pas l'evaluation scientifique du modele.

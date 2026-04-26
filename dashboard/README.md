# Neural Exchange Dashboard

Dashboard statique React/Vite pour visualiser les resultats Rev4 de Neural Stock Exchange.

Il lit uniquement :

- `dashboard/public/dashboard_data.json`
- `dashboard/public/assets/rev4/*.png`

Il ne lance aucun entrainement, aucune inference et aucun appel reseau.

## Synchroniser les donnees

Depuis la racine du depot :

```bash
python scripts/export_dashboard_data.py
python scripts/sync_dashboard_assets.py
```

## Lancer localement

```bash
cd dashboard
npm install
npm run dev
```

## Build statique

```bash
npm run build
```

Le build est concu pour GitHub Pages via Vite avec `base: "./"`.

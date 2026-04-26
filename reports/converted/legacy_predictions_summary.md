# Reporting legacy - Neural Stock Exchange

## Synthese

- Type : `legacy_predictions`
- Lignes converties : 22
- Periode observee : 2005-03-27 a 2010-01-03
- Lignes avec Panic Mode : 4

## Sources converties

| Revision | Source | CSV | Lignes | Panic Mode |
|---|---|---|---:|---|
| Rev2 | `reports/legacy/Stats NSE Rev2.xlsx` | `reports/converted/legacy_rev2_predictions.csv` | 8 | non |
| Rev2.5 | `reports/legacy/Stats NSE Rev2.5.xlsx` | `reports/converted/legacy_rev25_predictions.csv` | 14 | oui |

## Observations

| Revision | Date | Prediction | Reel | Ecart % | Panic Mode | Note |
|---|---|---:|---:|---:|---|---|
| Rev2 | 2005-03-27 | 10556.33 | 10498.59 | 0.55 | n/a | Tres precis |
| Rev2 | 2006-07-02 | 11003.11 | 11090.67 | -0.79 | n/a | Tres precis |
| Rev2 | 2007-07-01 | 13455.70 | 13611.68 | -1.14 | n/a | NSE capte bien le pic du marche |
| Rev2 | 2007-10-07 | 13513.15 | 14164.53 | -4.60 | n/a | NSE sous-estime le pic mais capte la tendance |
| Rev2 | 2008-09-14 | 11230.41 | 10917.51 | 2.87 | n/a | NSE capte la chute juste avant Lehman Brothers |
| Rev2 | 2009-03-01 | 8040.91 | 6469.95 | 24.30 | n/a | NSE voit la chute mais la sous-estime |
| Rev2 | 2009-09-06 | 9429.57 | 9504.72 | -0.79 | n/a | NSE capte bien le rebond |
| Rev2 | 2010-01-03 | 10296.09 | 10583.96 | -2.72 | n/a | NSE suit bien la reprise |
| Rev2.5 | 2005-03-27 | 10729.29 | 10442.87 | 2.74 | non | Precision correcte |
| Rev2.5 | 2006-06-25 | 11264.53 | 11009.09 | 2.32 | non | NSE capte la stabilite du marche |
| Rev2.5 | 2006-07-02 | 11247.42 | 11150.22 | 0.87 | non | Tres precis |
| Rev2.5 | 2007-02-25 | 12867.48 | 12610.41 | 2.04 | non | NSE suit la tendance mais surestime legerement |
| Rev2.5 | 2007-07-01 | 13652.26 | 13408.62 | 1.82 | non | NSE suit la tendance |
| Rev2.5 | 2007-10-07 | 13722.97 | 14066.01 | -2.44 | non | Sous-estime legerement le sommet |
| Rev2.5 | 2008-01-20 | 13056.94 | 12099.30 | 7.92 | oui | NSE declenche Panic Mode des janvier 2008 |
| Rev2.5 | 2008-03-16 | 12211.99 | 11951.09 | 2.18 | non | NSE suit le marche mais ne detecte pas encore l'instabilite |
| Rev2.5 | 2008-09-14 | 11493.11 | 11388.44 | 0.92 | non | NSE voit la baisse mais ne declenche pas Panic Mode |
| Rev2.5 | 2008-10-12 | 10443.32 | 8451.19 | 23.54 | oui | NSE detecte la crise mais sous-estime sa violence |
| Rev2.5 | 2009-03-01 | 7868.21 | 6626.93 | 18.74 | oui | NSE voit la panique mais manque d'agressivite |
| Rev2.5 | 2009-04-05 | 7623.10 | 7012.93 | 8.70 | oui | NSE suit la tendance baissiere et anticipe le stress economique |
| Rev2.5 | 2009-09-06 | 9619.72 | 9441.27 | 1.89 | non | NSE capte bien la reprise post-crise |
| Rev2.5 | 2009-12-27 | 10402.35 | 10428.05 | -0.25 | non | NSE suit bien la tendance |

## Panic Mode

| Revision | Date | Prediction | Reel | Ecart % | Note |
|---|---|---:|---:|---:|---|
| Rev2.5 | 2008-01-20 | 13056.94 | 12099.30 | 7.92 | NSE declenche Panic Mode des janvier 2008 |
| Rev2.5 | 2008-10-12 | 10443.32 | 8451.19 | 23.54 | NSE detecte la crise mais sous-estime sa violence |
| Rev2.5 | 2009-03-01 | 7868.21 | 6626.93 | 18.74 | NSE voit la panique mais manque d'agressivite |
| Rev2.5 | 2009-04-05 | 7623.10 | 7012.93 | 8.70 | NSE suit la tendance baissiere et anticipe le stress economique |

## Limites

- Rapports historiques issus des prototypes Rev2 et Rev2.5.
- Les valeurs sont converties pour lecture, sans recalcul de performance.
- Les fichiers Rev2 d'origine et scalers associes ne sont pas disponibles.
- Ces resultats ne constituent pas une preuve de robustesse predictive.

> Donnees et modeles experimentaux. Aucun resultat ne constitue un conseil financier.

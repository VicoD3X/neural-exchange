# Donnees - Neural Stock Exchange

Ce dossier regroupe les emplacements de donnees locales du projet.

## Strategie

Aucun CSV complet n'est versionne par defaut.
Les exports locaux sont regenerables et ignores par Git.

## Sources attendues

- Gold : yfinance, ticker `GC=F`.
- Dow/Macro Rev4 : yfinance, ticker `^DJI`.
- Market/Macro Rev4 : FRED public, serie `NASDAQCOM` (NASDAQ Composite).
- Macro : FRED, via `FRED_API_KEY` si disponible ou via les CSV publics officiels FRED.

## Rev3 legacy-advanced

Rev3 est conservee comme prototype avance, mais abandonnee comme pipeline actif.
Elle peut servir a comprendre certaines idees :

- fusion marche + macro ;
- features de volatilite ;
- `Panic_Mode` ;
- selection candidate de series macro.

Elle ne doit pas etre relancee ni presentee comme base reproductible finale.

## Rev4

La Rev4 est regeneree proprement sur la periode cible `2003-01-01` a `2010-12-31`.

Le Dow Jones historique via Yahoo a ete debloque apres mise a jour de `yfinance` en version `1.3.0`.
Rev4 conserve donc deux vues marche :

- `NASDAQCOM` via FRED public ;
- `^DJI` via yfinance.

Chaque dataset genere a pour objectif d'avoir :

- un schema explicite ;
- un nettoyage strict des dates ;
- une conversion numerique controlee ;
- une gestion explicite des valeurs manquantes ;
- une metadata de generation ;
- un avertissement clair : aucun usage de conseil financier.

## Note FRED

La cle `FRED_API_KEY` reste recommandee pour un usage robuste.
En son absence, le pipeline peut utiliser les exports CSV publics FRED pour les series documentees.

## Dossiers

- `data/raw/` : donnees brutes locales, ignorees.
- `data/local/` : donnees locales temporaires, ignorees.
- `data/processed/` : exports propres regenerables, ignores tant qu'une decision de versioning n'est pas prise.
- `data/sample/` : aucun echantillon versionne pour l'instant.

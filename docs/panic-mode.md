# Panic_Mode

`Panic_Mode` est un indicateur experimental de stress de marche base sur la volatilite.

Il ne doit pas etre interprete comme un detecteur fiable de crise financiere.
Il sert a enrichir l'analyse Rev4 avec un signal simple, lisible et reproductible.

## Principe

Le signal est construit a partir de la volatilite glissante du marche.

Dans Rev4 :

- les rendements journaliers sont calcules depuis `Market_Close` ;
- `Volatility_1W` mesure une volatilite courte sur 5 observations ;
- `Volatility_1M` mesure une volatilite plus large sur 21 observations ;
- `Panic_Mode` vaut 1 lorsque `Volatility_1M` atteint les 5% les plus eleves de la periode disponible.

Cette logique est volontairement simple.
Elle donne un point de depart pour raisonner sur des regimes de stress sans inventer un modele de crise.

## Role dans le projet

`Panic_Mode` permet de montrer :

- comment transformer une serie de prix en signal de regime ;
- comment separer forecasting de prix et detection de stress ;
- comment documenter une intuition experimentale sans la survendre ;
- comment relier le projet a son intention initiale autour des periodes de tension de marche.

## Limites

- Le seuil est calcule sur la periode disponible, pas sur une validation walk-forward.
- Le signal depend fortement de la definition de volatilite retenue.
- Un pic de volatilite n'est pas automatiquement une crise.
- Le signal ne predit pas un evenement futur par lui-meme.

## Prochaine evolution utile

Une evolution plus solide serait de comparer plusieurs seuils de volatilite et d'evaluer
les faux positifs et faux negatifs sur des periodes de stress connues.

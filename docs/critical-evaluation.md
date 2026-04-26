# Evaluation critique Rev4

L'objectif de l'evaluation Rev4 n'est pas de faire gagner le LSTM a tout prix.
L'objectif est de mesurer s'il apporte quelque chose face a des references simples.

## Baselines causales

Les baselines utilisees sont causales :

- `last_value` utilise uniquement la derniere valeur connue avant la date predite ;
- `moving_average_21` utilise une moyenne mobile passee, decalee d'une observation ;
- aucune baseline ne lit la valeur future au moment de produire sa prediction.

Cette contrainte est essentielle sur une serie temporelle.
Sans elle, une evaluation peut sembler bonne tout en etant invalide.

## Pourquoi `last_value` est forte

Sur une serie de prix financiers, la derniere valeur connue est souvent une baseline tres difficile a battre.

Les prix sont fortement autocorreles a court terme : le niveau de demain est souvent proche du niveau d'aujourd'hui.
Une baseline naive peut donc obtenir un MAE faible sans comprendre le marche.

Dans Rev4, `last_value` bat le LSTM sur le MAE.
Ce resultat est conserve volontairement, car il rend l'evaluation plus credible.

## Ce que le LSTM peut capter

Le LSTM peut apprendre :

- une dynamique sequentielle locale ;
- des effets de lissage ;
- des interactions faibles entre marche, volatilite et variables macro ;
- un signal directionnel legerement different de l'erreur de prix.

Dans les resultats actuels, le LSTM ne gagne pas sur le MAE mais montre une direction accuracy superieure a `last_value`.
Cette observation reste experimentale et ne suffit pas a conclure que le modele est robuste.

## Ce que le LSTM ne capte pas encore

Le modele Rev4 ne capte pas encore :

- les retournements rapides avec assez de precision ;
- les ruptures de regime de facon fiable ;
- une superiorite nette contre une baseline naive forte ;
- une robustesse hors periode testee.

Il peut aussi lisser ou retarder sa reaction, ce qui est visible dans les courbes de prediction et les residus.

## Lecture correcte

Le bon verdict n'est pas "le modele echoue".

Le bon verdict est :

- le pipeline Rev4 est reproductible ;
- les baselines sont explicites et causales ;
- le LSTM ne bat pas `last_value` sur l'erreur de prix ;
- la direction peut raconter une information differente du MAE ;
- la suite doit renforcer l'evaluation avant toute interface ambitieuse.

# Legacy Dow Macro

Ancien prototype Dow Jones + macro FRED.

Statut :
- conserve comme archive technique ;
- non executable proprement en l'etat ;
- depend de fichiers Rev2 absents ;
- modele historique incompatible avec Rev3 et avec le futur schema Rev4.

Fichiers :
- `catch_data.py` : ancienne collecte yfinance/FRED ;
- `starter.py` : ancien entrainement LSTM Dow Jones/macro ;
- `display.py` : ancienne interface Tkinter.

Decision :
ne pas reparer par changement de chemins. Rev3 est classe en legacy-advanced : utile comme reference partielle, mais abandonne comme pipeline actif. Le futur flux Dow Jones sera reconstruit dans `src/nse_engine/` sur Rev4 propre.

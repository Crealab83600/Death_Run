# RAGE.EXE (Death_Run)

Jeu de plateforme punitif pour calculatrice **NumWorks** (320 x 222, kandinsky + ion).
Traversez 20 niveaux de plus en plus difficiles jusqu'a la porte verte : pics, trous,
plateformes fragiles / qui tombent / mobiles / invisibles, ressorts et pieges surprises.

## Installation
- Ouvrez [my.numworks.com/python](https://my.numworks.com/python), creez un script nomme `RAGE.EXE`
- Collez le contenu de `RAGE.py`, envoyez vers la calculatrice

## Commandes
- Fleches gauche / droite : se deplacer
- OK : sauter / valider
- BACK (BACKSPACE) : retour menu / quitter

## Fonctions
- Menu : JOUER (reprend le niveau courant), CHOISIR UN NIVEAU, RECOMMENCER, QUITTER
- Grille des 20 niveaux (deverrouillage progressif) avec record par niveau ("--" si aucun)
- Compteurs : morts totales de la session et essais (morts) du niveau courant
- Types de plateformes : normale, fragile (tremble puis cede), qui tombe, mobile
  horizontale, invisible a distance, mobile verticale, ressort
- Pieges surprises : declenchement horizontal, proximite verticale, compteur de trames
- Game feel : coyote time, jump buffer, collisions laterales, flash + message a la mort

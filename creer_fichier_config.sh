#!/bin/bash

# créé le fichier de config $HOME/.artebox.cfg par défaut

CONFIG_FILE=$HOME/.artebox.cfg
DOSSIER=$HOME/artebox

if [ -f $CONFIG_FILE ]; then
    echo "$CONFIG_FILE existe déjà, bye"
    exit 0
fi

echo -e "[paramètres]\n\
dossier     = $DOSSIER\n\
catalogue   = $DOSSIER/catalogue.txt\n\
abonnements = $DOSSIER/abonnements.txt" | tee $CONFIG_FILE

echo
mkdir -pv  $DOSSIER
touch "$DOSSIER/abonnements.txt"

exit 0


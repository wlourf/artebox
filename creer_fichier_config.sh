#!/bin/bash

CONFIG_FILE=$HOME/.artebox.cfg

if [ -f $CONFIG_FILE ]; then
    echo "$CONFIG_FILE existe déjà, bye"
    exit 0
fi

echo -e "[paramètres]\ndossier=$HOME/artebox\ncatalogue=$HOME/artebox/catalogue.txt\nabonnements=$HOME/artebox/abonnements.txt"  | tee  $CONFIG_FILE

exit 0


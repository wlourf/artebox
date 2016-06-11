# artebox
arte+7 downloader 

Téléchargement des émissions de arte+7 en ligne de commande ou avec interface GTK

  
Exemple de fichier de configuration, par défaut ~/.artebox.cfg <b>a créer manuellement</b> ou avec le script creer_fichier_config.sh :

    [paramètres]
    # où sont enregistrés les vidéos
    dossier = /home/wlourf/artebox
    
    # catalogue contenant les fichiers déjà téléchargés
    catalogue = /home/wlourf/artebox/catalogue.txt
    
    # fichier contenant les noms des abonnements (optionnel)
    abonnements = /home/wlourf/artebox/abonnements.txt

Exemple de fichier "abonnements" (le symbole * permet de rechercher sur une partie du nom) :

    Le dessous des cartes
    Mystères*

Lancer le programme avec l'interface graphique :
  
    artebox
  
En CLI, télécharger les émissions définies dans le fichier "abonnements" :

    artebox -a 

En CLI, télécharger des émissions ponctuellement (recherche dans les noms d'émissions):    

    artebox -e xenius*

En CLI, télécharger des émissions ponctuellement (recherche dans les sujets d'émissions):    

    artebox -e futur* -t 

En CLI, télécharger des émissions interactivement :

    artebox -i 
  
Autres paramètres :

    artebox -h 
 
    usage: ArteBox [-h] [-a] [-e EMISSION] [-t] [-L] [-D] [-i] [-v] [--no-dl]
                   [-S SIZE]
                   [CONFIG_FILE]
    
    Arte+7 downloader
    
    positional arguments:
      CONFIG_FILE        fichier de configuration, défaut = ~/.artebox.cfg
    
    optional arguments:
      -h, --help         show this help message and exit
      -a                 télécharger les abonnements
      -e EMISSION        émission à télécharger, peut être utilisé plusieurs fois
      -t                 recherche dans les titres
      -L                 liste les émissions disponibles et quitte
      -D                 liste les émissions disponibles et les détails et quitte
      -i, --interactive  choix interactifs
      -v, --version      affiche la version
    
    pour debug:
      --no-dl            pas de download (pour debug)
      -S SIZE            taille en Mo (pour debug)
    

Dépendances : 

    python3
    python3-bs4
    python3-gi
    gir1.2-gtk-3.0

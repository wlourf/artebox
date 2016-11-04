#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__name__ = "ArteBox"
__version__ = "0.1"
__description__ = "Arte+7 downloader"

__license__ = """
Artebox, Arte+7 downloader

This file is part of ArteBox.

ArteBox is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

ArteBox is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import argparse
import os
import sys 
import configparser
import importlib

import subfunctions as sf
import download as dl
import interface as ui

try :
    from bs4 import BeautifulSoup
except:
    print("Installer BeautifulSoup (python3-bs4)")
    sys.exit(1)
                    

class Base:
    """
    Main application
    """
    def __init__(self):
        
        # constantes
        self.default_config_name = '.artebox.cfg'
        self.pages_arte = ['actu-societe' , 'series-fiction', 'cinema',
                          'arts-spectacles-classiques',
                          'culture-pop', 'decouverte', 'histoire',
                          'junior']
        # pour test une page
        # self.pages_arte = [ 'actu-société' ]
        self.url_arte7 = 'http://www.arte.tv/guide/fr/plus7/'

        # Initialize vars
        self.args = None
        self.has_gui = False
        self.GUI = None
        self.TITLE = __name__ + ' ' + __version__
        self.params = {}
        self.abos = []  # abonnements + emissions passées avec -e
        self.cat  = []  # catalogue
        self.arte7 = [] # emissions disponibles sur le site
        self.downloads = []
        self.dl_running = False
        self.force_cancel = False
 

        self.args, self.has_gui =  self.parse_command_line()
        
        # Listing des émissions, en console uniquement
        if self.args.LISTING or self.args.LISTING_PLUS :
            sf.listing_emissions_arte(self, True)
            sys.exit(0)

        self.params, self.abos = self.parse_config_file(self.args.CONFIG_FILE)
        self.check_params()
        self.cat = self.get_catalogue()

        if self.has_gui :
            self.GUI = ui.GUI_Main(self)

        if self.args.INTERACTIVE :
            self.arte7 = sf.listing_emissions_arte(self, True)
            self.interactive_download()
            sys.exit(0)              

        # Infos dans terminal
        # print("== Options ==")
        # print("affichage interface     : %s" % self.has_gui)
        print("\n== Paramètres ==")
        print("fichier configuration   : %s" % self.args.CONFIG_FILE)
        print("dossier enregistrements : %s" % self.params['save_dir'])
        print("fichier catalogue       : %s" % self.params['catalogue'])
        print("                          %d lignes" % len(self.cat))
        if self.args.ABOS:
            print("fichier abonnements     : %s" % self.params['abonnements'])
        
        # Affichage emissions dans terminal
        if len(self.abos)>0 :
            for nom in self.abos:
                if nom == self.abos[0]:
                    print("\némission(s)             : - %s " % nom)
                else:
                    print("                          - %s" % nom)
                    

        # GO GUI
        if self.has_gui : 
             self.GUI.run()

        # GO CLI
        if not self.has_gui:
            if len(self.abos) == 0 :
                print('\nRien à faire ...\nBye')
                sys.exit(0)

            #pour formatage affichage
            lg = 0
            for abo in self.abos :
                lg = max(len(abo), lg)

            #récupère les urls des abonnements
            sf.display_info(self.GUI,
                            "\nRécupère les liens des émissions ...")
            self.arte7 = sf.listing_emissions_arte(self,False)

            #création du tableau de téléchargements
            for abo in self.abos:
                nbLiens = 0 #nb de liens pour une émission donnée

                #pour les séries, on utilise *
                abo_serial = ''
                if abo.find("*") > -1:
                    abo_serial = abo.split("*")[0]
                
                for page_info in self.arte7 :
                    #recherche dans nom émission
                    if page_info[2].lower() == abo.lower():
                        self.downloads.append( page_info )
                        nbLiens +=1

                    if abo_serial != '' and  page_info[2].lower().find(abo_serial.lower())> -1 :
                        self.downloads.append( page_info  )
                        nbLiens +=1

                    if self.args.SEARCH_IN_TITLE :    
                        #recherche dans sujet émission
                        if page_info[5].lower() == abo.lower():
                            self.downloads.append( page_info )
                            nbLiens +=1

                        if abo_serial != '' and  page_info[5].lower().find(abo_serial.lower())> -1 :
                            self.downloads.append( page_info  )
                            nbLiens +=1

                #mise en forme affichage
                print('%s %d émission(s)' % (abo.ljust(lg + 4, "."), nbLiens))

            print("\n %d émission(s) disponible(s)\n" %len (self.downloads))
        
            for download in self.downloads:
                print (download[3], download[2], download[5])

            if len(self.downloads)>0:
                print ("\n== Téléchargements ==")
                
            for download in self.downloads:
                dl.download_video( self, download ) #args, params, arrCatalogue, dl )
            
        return



    def interactive_download(self):
        """
        choix interactif en CLI des émissions à télécharger
        """
        idx_downloads = []
        idx = 0

        #récupère le plus long titre
        zMax = 0
        for z in self.arte7:
            zMax = max(len(z[2]) +2, zMax)

        iMin, iMax = 0, 0
        flagTitre = True

        for line in self.arte7:
            if idx < len(self.arte7) :
                if self.arte7[idx][1] != self.arte7[idx-1][1]:
                    print ("\n    Page " + line[1])
                    iMin = idx

                print (str(idx+1).rjust(3), line[2].ljust(zMax, '.'), line[3], line[4], line[5])
                    
                if idx+1 == len(self.arte7) or  self.arte7[idx][1] != self.arte7[idx+1][1]:
                    flagOK = False
                    iMax= idx
                    while not flagOK :
                        response = input('\nChoix (séparés par des espaces ou ENTER): ')                    
                        flagOK = self.interactive_check(iMin, iMax, response)
                    for r in response.split():
                        idx_downloads.append(r)
                        
            idx += 1

        if len(idx_downloads) == 0:
            print ("\nRien à faire ...")
            sys.exit(0)

        for d in idx_downloads:
            download =  self.arte7[int(d)-1]
            print (download[3], download[2], download[5])

        print ("\n== Téléchargements ==")
                            
        for d in idx_downloads:
             idx = int(d)-1
             dl.download_video(self, self.arte7[idx])
             

    def interactive_check(self, iMin, iMax, response):
        """
        controle choix interactif
        """
        
        flag = True
        for r in response.split():
            flag = r.isnumeric()

            if flag and int(r) not in range(iMin+1, iMax+2):
                flag = False

            if not flag:
                break

        if not flag :
            print ("Choisir entre", iMin+1,"et",  iMax+1)
            
        return flag
            
    def check_params(self):
        """
        vérifie paramètres (présence dossiers enreg et fichier catalogue)
        """
        params = self.params

        if not os.path.isdir(params['save_dir']):
            try :
                os.makedirs(params['save_dir'])
                sf.display_info(self.GUI,
                        "Création du dossier",  params['save_dir'])
            except :
                ui.stop_app (self,
                            'Erreur dossier d\'enregistrement : ',
                            params['save_dir'])

    
        if not os.path.isfile( params['catalogue'] ):
            try :
                f = open(params['catalogue'], 'w')
                f.close()
                sf.display_info(self.GUI,
                                "Création du catalogue : " + params['catalogue'])
            except:
                ui.stop_app (self,
                            'Erreur lors de la création du catalogue : ',
                            params['catalogue'] )
            
        return
    

    def get_catalogue(self):
        """
        lit et retourne le catalogue
        """
        params = self.params

        arrCatalogue = []
        try:
            fcat = open(params['catalogue'], 'r')
            arrCatalogue = fcat.readlines()
            fcat.close()
        except:
            ui.stop_app(self,
                        'Erreur lors de la lecture du catalogue ',
                        params['catalogue'])

        return arrCatalogue


    
    def parse_command_line(self):
        """
        command line parser
        """
        parser = argparse.ArgumentParser(
                prog=__name__,
                description = __description__,
                formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument('CONFIG_FILE', type = str ,
                help='fichier de configuration, défaut = ~/' +
                self.default_config_name,
                nargs='?',
                default =  os.path.join(os.getenv("HOME"), self.default_config_name) )
        parser.add_argument('-a', action='store_true',
                dest ='ABOS',
                help='télécharger les abonnements')
        parser.add_argument('-e', action='append',     
                dest ='EMISSION', 
                help='émission à télécharger, peut être utilisé plusieurs fois')
        parser.add_argument('-t', action='store_true',     
                dest ='SEARCH_IN_TITLE', 
                help='recherche dans les titres')
        

        parser.add_argument('-L', action='store_true', 
                dest ='LISTING', 
                help='liste les émissions disponibles et quitte')
        parser.add_argument('-D', action='store_true', 
                dest ='LISTING_PLUS', 
                help='liste les émissions disponibles et les détails et quitte')

        parser.add_argument('-i','--interactive', action='store_true', 
                dest ='INTERACTIVE', 
                help='choix interactifs')

                
        parser.add_argument('-v', '--version', action='version', 
                version=__name__ + ' version ' + __version__,
                help='affiche la version')


        debug_group = parser.add_argument_group('pour debug')
        #debug_subparsers = parser.add_subparsers(title='pour debug')
        #parser_foo = debug_subparsers.add_parser('foo')
        debug_group.add_argument('--no-dl',  action='store_true',
                dest ='NODL', 
                help='pas de download (pour debug)')                
                                    #help='additional help')
#help = "utilisé pour tests")
        
        debug_group.add_argument('-S',  type =int , 
                dest ='SIZE', 
                help='taille en Mo (pour debug)')

        #parser_a = debug_group.add_parser('-C', help='a help')
        #parser_a.add_argument('--bar', type=int, help='bar help')
                                                                
        args = parser.parse_args()
        

        has_gui = (not args.ABOS) and (args.EMISSION is None) and \
                (not args.INTERACTIVE)


        #Mutual exclusion works only for 1 arg against two args
        if args.INTERACTIVE and (args.ABOS or (args.EMISSION is not None)):
            print ("-i non compatible avec -a ou -e")
            sys.exit(1)
        
        return args, has_gui




    def parse_config_file(self, config_file):
        """
        vérifie présence et validité du fichier de config
        necessité d'une section ['paramètres']
        """

        if not os.path.isfile(config_file):
            ui.stop_app (self, 'Erreur fichier de configuration manquant : ', config_file)
                
        dict = {}
        config = configparser.RawConfigParser(dict)
        try:
            config.read(config_file)
        except:
            ui.stop_app (self, 'Erreur dans fichier de configuration : ', config_file )
           
        arrSections = config.sections()
        if not 'paramètres' in arrSections:
            ui.stop_app (self, 'Section \'paramètres\' manquante dans ', config_file)

        params = {}
        if config.has_option('paramètres', 'dossier'):
            params['save_dir']  = config.get('paramètres', 'dossier')
        else:
            ui.stop_app (self, 'Paramètres \'dossier\' non défini dans ', config_file)
                                            
        if config.has_option('paramètres', 'catalogue'):
            params['catalogue'] = config.get('paramètres', 'catalogue')
        else:
            ui.stop_app (self, 'Paramètres \'catalogue\' non défini dans ', config_file)

        #arrAbo = abonnements définis dans le params['abonnements']
        #         ou tableau args.EMISSION
        arrAbo = []
        if self.args.EMISSION is not None:
            arrAbo = self.args.EMISSION[:]

        # le paramètre 'abonnements' n'est utilisé qu'en CLI, avec le param -a                
        if self.args.ABOS : 
            if config.has_option('paramètres', 'abonnements'):
                params['abonnements'] = config.get('paramètres', 'abonnements')
            else:
                ui.stop_app (self, 'Paramètres \'abonnements\' non défini dans ', config_file)
            try:
                f = open(params['abonnements'])
                listeAbo = f.readlines()
                f.close()
            except:
                ui.stop_app (self, 'Erreur lecture paramètre \'abonnements\' : ', params['abonnements'] )

            for nom in listeAbo :
                if nom.find("#") > -1: #remove comment
                    nom = nom[:nom.find("#")]
                nom = nom.replace('\n', '').strip()
                if nom !="":
                    arrAbo.append(nom)

        #supprime les doublons avec list
        return params, list(set(arrAbo))


    def main(self):
        return




if __name__ == "__main__":
    
    app = Base()

    try:
        app.main()
    except KeyboardInterrupt:
        pass

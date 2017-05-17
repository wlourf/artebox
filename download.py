#!/usr/bin/env python3
# -*- coding:utf-8 -*-

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

import urllib.request, urllib.error, urllib.parse
import os
import json
import time
import sys
import shutil

import subfunctions as sf


def download_video( base, pg_info, tree_model_row = None ) :
    """
    pg_info = [ nomAbo, [infos sur la vidéo] ]
    nomAbo  = None si par GTK, on prend le nom de la page_arte
    pour créer le sous-dossier d'enregistrement
    downloade en VOST par défaut, sinon VF
    """

    if base.has_gui:
        iter_model_row = tree_model_row.iter
        from gi.repository import Gtk

    racine  = "http://arte.tv/papi/tvguide/videos/stream/player/F/"
    suffixe = "_PLUS7-F/ALL/ALL.json"

    racine = "https://api.arte.tv/api/player/v1/config/fr/"
    suffixe = ""

    args         = base.args
    params       = base.params
    arrCatalogue = base.cat
    #emi_id = pg_info[0]

    #f = urllib.request.urlopen(url)
    #html_doc = f.read()
    #f.close()

    #soup = BeautifulSoup(html_doc, 'html.parser')
    #menuCollection = soup.find("iframe")
    #JSONlink = menuCollection['src']

    #print (JSONlink)


    emi_id = pg_info[0]
    id_url = emi_id.split("_")[0]

    titre  = pg_info[2].strip().replace(' ', '_')
    sujet  = pg_info[5]#).decode('utf-8')
    sujet  = sujet.strip().replace(' ', '_')

    # on enregistre dans le dossier de la page, et non dans le dossier
    # de l'abonnement pour l'instant
    nomAbo =  pg_info[1].replace(' ', '_')
    pc_dir  = os.path.join(params['save_dir'], nomAbo)

    if not os.path.isdir(pc_dir):
        sf.display_info(base.GUI, 'Création du dossier' , pc_dir )
        os.makedirs(pc_dir)

    print (emi_id)
    print (id_url)
    # lien Json contient le lien vers la vidéo
    # et les infos supplémentaires sur la vidéo
    lienJSon = racine + id_url + suffixe
    print ("JSON", lienJSon)

    # emisison id, parfois
    # liens : parfois 049281-000-F_PLUS7-F
    try:
        f = urllib.request.urlopen(lienJSon)
    except urllib.error.HTTPError as err:
        strErr = 'Erreur ' + str(err.code) + ' : ' + err.msg
        if base.has_gui:
            tree_model_row[5] = strErr
            iter_row = sf.display_info(base.GUI, titre + '-' + sujet, strErr )
            base.GUI.mdl_dl.remove(iter_model_row)

        else:
            print (strErr)

        return

    json_doc = f.read()
    f.close()
    dataVideo = json.loads(json_doc.decode('utf-8'))

    #formats de la vidéo

    #jsonplayer = open('/tmp/jsonplayer.txt', 'w')
    #for f in dataVideo['videoJsonPlayer']:
    #    print (f , dataVideo['videoJsonPlayer'][f])
    #    jsonplayer.write( str(f) + '\t' + str(dataVideo['videoJsonPlayer'][f]) + '\n')
    #jsonplayer.close()
#    for k in  dataVideo['videoJsonPlayer'].keys():
#        print (k, dataVideo['videoJsonPlayer'][k])
#    print ()

    if 'V7T' in  dataVideo['videoJsonPlayer'] :
        teaser = dataVideo['videoJsonPlayer']['V7T']
    else:
        teaser = ""
    formats  =  dataVideo['videoJsonPlayer']['VSR']
    tdate = dataVideo['videoJsonPlayer']['VRA'] #VDA VRA?
    tdate = tdate[:-6] #remove offset UTC, %z fonctionne pas avec strptime ?

    ttitle = dataVideo['videoJsonPlayer']['VTI']
    if 'subtitle' in  dataVideo['videoJsonPlayer'] :
        tsubtitle = dataVideo['videoJsonPlayer']['subtitle']
    else:
        tsubtitle = ""

    tID = dataVideo['videoJsonPlayer']['VID']
    outDate = time.strptime(tdate, "%d/%m/%Y %H:%M:%S")
    if sujet == '':
        sujet = time.strftime( "%Y%m%d_%H%M%S", outDate)
    else:
        sujet = time.strftime( "%Y%m%d", outDate) + '-' + sujet

    fichier = titre + '-' + sujet + '.mp4'
    fichier = sf.clean_file_name(fichier)

    file_name = os.path.join(pc_dir, fichier)
    file_name_txt = file_name.replace('.mp4', '.txt' )
    file_name_tmp = file_name + '.tmp'

    # print "*"*50
    # formatsvideo = open('/tmp/tmp.txt', 'w')
    #for f in formats:
    #    print (f , formats[f])
    #    formatsvideo.write( str(f) + '\t' + str(formats[f]) + '\n')
    # formatsvideo.close()


    #_2 : Allemand original (VA)
    #_3 : Français (Sous-titres)  : VOST
    #_1 : Français doublé VF
    #_8 : VF ST sourds/mal
    #_11 : VOST anglais
    #_12 : VOST espagnol

    # SQ : bitrate 2200
    # EQ : bitrate 1500
    # HQ : bitrate 800
    # MQ : bitrate 300
    # VOST par défaut, VF sinon

    if 'HTTPS_MP4_SQ_3' in formats:
        url = formats['HTTPS_MP4_SQ_3']['url']
        info_version = ' (VOST)'
    elif 'HTTPS_MP4_SQ_1' in formats:
        url = formats['HTTPS_MP4_SQ_1']['url']
        info_version = ' (VF)'
    elif 'HTTPS_SQ_1' in formats:
        url = formats['HTTPS_SQ_1']['url']
        info_version = ' (VF)'
    elif 'HTTPS_MP4_EQ_3' in formats:
        url = formats['HTTPS_MP4_EQ_3']['url']
        info_version = ' (VOST)'
    elif 'HTTPS_MP4_EQ_1' in formats:
        url = formats['HTTPS_MP4_EQ_1']['url']
        info_version = ' (VF)'
    elif 'HTTPS_EQ_1' in formats:
        url = formats['HTTPS_EQ_1']['url']
        info_version = ' (VF)'
    elif 'HTTPS_HQ_1' in formats:
        url = formats['HTTPS_HQ_1']['url']
        info_version = ' (VF)'
    elif 'HTTPS_MP4_MQ_3' in formats:
        url = formats['HTTPS_MP4_MQ_3']['url']
        info_version = ' (VOST)'
    elif 'HTTPS_MQ_1' in formats:
        url = formats['HTTPS_MQ_1']['url']
        info_version = ' (VF)'
    else:
        url = formats['HTTPS_MP4_MQ_1']['url']
        info_version = ' (VF)'




    print (url)
    print (info_version)
    # fichier dans cataloguue
    flagDL = True
    if len(arrCatalogue) > 0:
        for ligne in reversed(arrCatalogue):
            if len(ligne) > 0 and emi_id == ligne.split(";")[0]:
                sf.display_info(base.GUI, fichier , 'Déjà présent dans le catalogue' )
                if base.has_gui :
                    tree_model_row[5] = "Présent dans le catalogue"
                    tree_model_row[7] = file_name + " présent dans le catalogue"

                flagDL = False
                break


    if flagDL:
        base.dl_running = True

        if base.has_gui :
            pass


        if base.args.NODL: #pour debug
            txt_no_dl = ' --> option no-dl : skip download'
            if base.has_gui:
                tree_model_row[5] = txt_no_dl
                tree_model_row[7] = fichier + " non téléchargé"
            else:
                print(fichier, '--> ' + txt_no_dl)
        else:
            try:
                response = urllib.request.urlopen(url)
            except urllib.error.HTTPError as err:
                strErr =  'Erreur ' + str(err.code) + ' : ' + err.msg
                if gui is not None:
                    info_row[4] = strErr
                else:
                    print(">", strErr)
                return

            file_size = int(response.headers['content-length'])

            CHUNK = 16 * 1024
            bytes_so_far = 0.0

            if not base.has_gui:
                print(fichier + info_version)
            else:
                tree_model_row[7] = file_name + info_version
            with open(file_name_tmp, 'wb') as fp:
                while True:
                    if base.force_cancel :
                        print('Cancel')
                        tree_model_row[5] = "Annulé"
                        tree_model_row[7] = file_name_tmp + " : annulé"
                        sf.display_info(base.GUI, fichier, "annulé")
                        break

                    chunk = response.read(CHUNK)
                    if base.args.SIZE is not None and base.args.SIZE > 0 and bytes_so_far > base.args.SIZE*1024*1024:
                        break
                    if not chunk :
                        break
                    bytes_so_far += len(chunk)
                    fp.write(chunk)
                    percent = 100.*bytes_so_far/file_size
                    if base.has_gui:
                        tree_model_row[6] = percent
                        # le texte n'est pas automatique car il s'agit de
                        # la meme progressbar que pour le chargement des émissions
                        tree_model_row[5] = str("%d/%d Mo : %0.1f %%" %  (bytes_so_far/1024/1024, file_size/1024/1024,percent))
                        while Gtk.events_pending():
                            Gtk.main_iteration()
                    else:
                        sys.stdout.write("\rTéléchargé : %d/%d Mo (%0.1f%%)" % (bytes_so_far/1024/1024, file_size/1024/1024,percent))
                        sys.stdout.flush()

            if base.has_gui :
                if not base.force_cancel :
                    sf.display_info(base.GUI, fichier, "terminé")
                base.GUI.view_emi.set_sensitive(True)
            print('\n')


        if not base.force_cancel and not base.args.NODL:
            os.rename(file_name_tmp, file_name)

            # fichier txt résumé
            finfo = open(file_name_txt, 'w')
            finfo.write("Émission   : " + pg_info[2] +"\n")
            finfo.write("Date       : " + tdate + "\n")
            finfo.write("Durée      : " + str(pg_info[4]) + "\n")
            finfo.write("Titre      : " + ttitle + "\n")
            finfo.write("Sous-titre : " + tsubtitle + "\n")
            finfo.write("\nRésumé     : \n" + teaser + "\n")
            finfo.write("\nId         : " + tID + "\n")
            finfo.close()

            # inscrit le fichier téléchargé dans le catalogue
            fcat = open(params['catalogue'],"a")
            fcat.write(emi_id + ';' + fichier + ';\n')
            fcat.close()


        if not base.has_gui:
            print()

    if not base.force_cancel and base.has_gui :
        base.GUI.mdl_dl.remove(iter_model_row)


    base.dl_running = False

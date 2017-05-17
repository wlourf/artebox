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
import json
import time
import sys

try :
    from bs4 import BeautifulSoup
except:
    print("Installer BeautifulSoup (python3-bs4)")
    sys.exit(1)


def listing_emissions_arte(base, bDisplay = False, treeRow = None):
    """Liste les titres d'émissions disponibles."""

    tabXML = []
    racine = base.url_arte7
    idx = 1
    tabEmissions2 = []

    for p in base.pages_arte:
        if base.args.LISTING :
            print('\n# Page ' + p)

        if base.args.LISTING_PLUS or base.args.INTERACTIVE :
            sys.stdout.write('\rLecture page ' + p + 50*" " + "\r")

        url = urllib.parse.quote(racine + p,
                                safe=':/', encoding='utf-8')
#        url = url + "?country=FR"


        print ("subfonction : ", url)
        try:
            f = urllib.request.urlopen(url)
        except urllib.error.HTTPError as err:
            treeRow[4] = 'Erreur ' + str(err.code) + ' : ' + err.msg
            return tabXML

        if treeRow is not None :
            from gi.repository import Gtk
            #mise à jour progress bar
            tpercent = 100*idx/len(base.pages_arte)
            treeRow[2] = 'page : ' + str(idx) + '/' + str(len(base.pages_arte)) +\
                        ' (' + p +')'
            idx+=1
            while Gtk.events_pending():
                Gtk.main_iteration()
        html_doc = f.read()
        f.close()

        soup = BeautifulSoup(html_doc, 'html.parser')
        #divCollection = soup.find("div", {"id": "container-collection"})
        menuCollection = soup.find("ul", {"class": "next-menu-nav__sub-menu is-open"})
        subLinks=[]
        for subMenu in menuCollection:
            for sm in subMenu:
                if sm["href"][:4] != 'http' :
                    subLinks.append( sm["href"])
                #exit()
                #print ("href", x["href"])
                #for y in x:
                #    print ("y", y)
#        liCollection = soup.fing

        tabEmissions = []
        for subPage in subLinks :
            print ( '\t' + subPage)
            htmlPage = 'http://www.arte.tv' +  subPage + '/'
#            print ()
#            print ("MAIN : ", htmlPage)
            url = urllib.parse.quote(htmlPage,
                                safe=':/', encoding='utf-8')

#            try:
            f = urllib.request.urlopen(url)
#            except urllib.error.HTTPError as err:
#                treeRow[4] = 'Erreur ' + str(err.code) + ' : ' + err.msg
#                return tabXML

            html_doc = f.readlines()
            f.close()
#            print (len(html_doc))
            for line in html_doc:
                uline = str(line, 'utf-8')
                if (uline.find('window.__INITIAL_STATE__'))> -1:
                    texte = uline
                    break
                    #print (len(uline))
                    #print (uline.split("{\"id"))
            startCar = texte.find("=") +1

            # put data in JSON
            texte = texte[startCar:-2]
#            textedumps = json.dumps(texte)
            data = json.loads(texte)

            #print (html_doc[0])
            #print (html_doc[1])
            #print (html_doc[2])

            #html_doc = 'http://www.arte.tv' +  subPage + '/'
            # print (html_doc)
            #soup = BeautifulSoup(html_doc, 'html.parser')
           # divCollection = soup.find("article", {"class": "next-teaser"})
            #divCollection = soup.find_all("a", {"class": "next-teaser__link"})
           # divCollection = soup.find_all("href", {"class": "next-teaser__link"})
#            divCollection = soup.find("a", {"class": "next-teaser-full__link"})
#            divCollection = soup.find("section", {"class": "next-section"})
#            divCollection = soup.find("div", {"class" :"column column-block"})  #section", {"class": "next-section"})
            #divCollection = soup.find_all("script")
            #print (len(divCollection))
#            print()
            #for X in divCollection:
            #    print (len(X), X[0])
                    #print ("X", X)

           # for link in soup.find_all('a', {"class": "next-teaser__link"}):
           #     print(link.get('href'))
           # data = json.loads(divCollection["a"])
#            print ("divC", divCollection)
            #print ("href", "http://www.arte.tv" + divCollection["href"])
            #print ()

#            for T in divCollection:
#                print ("T",T)
#            print ()
#            data = json.loads(divCollection["a"])
            #print (len(data))
            #print (data['subcategory']['videos'])
#            print (data['subcategory']['videos'])#['subcategory']['url'])
            for v in data['subcategory']['videos']:
 #               print ()
#                print (v)
#                exit()
 #               print ()
 #               print (v['url'])
                scheduled = v['images'][0]['lastModified']
                #scheduled = scheduled.replace('T', ' ')
                #scheduled = scheduled.replace('Z', ' ')
                scheduled = scheduled[8:10] + "/" +scheduled[5:7]+ "/"+ scheduled[:4]
                #scheduled = '' #creationDate']
                subtitle = v['subtitle'] or ''
                id = v['id'] #[:10]
                duration = v['duration'] or ''
#                print (v['title'], scheduled)
#                print (duration)
                prefixe = 'http://arte.tv/papi/tvguide/videos/stream/player/F/'
                suffixe = '_PLUS7-F/ALL/ALL.json'
                #url = prefixe + id + suffixe
                if bDisplay:
                    tabEmissions.append(v['title'].strip())
                    tabEmissions2.append( [p, v['title'].strip(), subtitle, scheduled] )
                #print (data['page']['title'])
                tabXML.append([ id,
                                p,
                                v['title'],
#                                str(v['title']).encode('utf-8'),
                                scheduled,
                                str(duration),
                                subtitle,
                                '', # v['rights_end'],
                                '', # v['teaser'],
                                '', # v['thumbnail_url'],
                                ''  # v['views']
                               ])
#            print (data)
#            print (data['page']['id'])
                """
        exit()
        data = json.loads(divCollection["a"])
        print
        print (data)
        tabEmissions = []
        for v in data['videos']:
            scheduled = v['scheduled_on']
            if scheduled is  None: # ça arrive
                scheduled = ""
            else:
                scheduled = scheduled[8:] + "/" +scheduled[5:7]+ "/"+ scheduled[:4]

            subtitle = v['subtitle'] or ''

            id = v['id'] #[:10]

            duration =  time.strftime("%H:%M", time.gmtime(v['duration']))

            prefixe = 'http://arte.tv/papi/tvguide/videos/stream/player/F/'
            suffixe = '_PLUS7-F/ALL/ALL.json'
            url = prefixe + id + suffixe

            if bDisplay:
                tabEmissions.append(v['title'].strip())
                tabEmissions2.append( [p, v['title'].strip(), subtitle, scheduled] )
                #s, subtitle])
                #print (v['title'], subtitle)
            #else:
            tabXML.append([ id,
                                p,
                                v['title'],
#                                str(v['title']).encode('utf-8'),
                                scheduled,
                                duration,
                                subtitle,
                                v['rights_end'],
                                v['teaser'],
                                v['thumbnail_url'],
                                v['views']
                               ])
            """
    if base.args.LISTING:
        tabSingle = list(set(tabEmissions))
        tabSingle.sort()
        for emi in tabSingle :
            print('\t' + emi)


    if base.args.LISTING_PLUS or base.args.INTERACTIVE :
        sys.stdout.write('\r' + 100*" " + "\r")

    if base.args.LISTING_PLUS:
        zMax = 0
        for z in tabEmissions2:
            zMax = max(len(z[1]) +2, zMax)

        idx = 0
        for z in tabEmissions2:
            #if idx ==0 :
            #    print ("\n\t\tPage " + tabEmissions2[idx][0])
            if idx < len(tabEmissions2)-1:
                if tabEmissions2[idx][0] != tabEmissions2[idx-1][0] :
                    print ("\n    Page " + tabEmissions2[idx+1][0])
            #print ("\n\t\tPage " + tabEmissions2[idx][0], tabEmissions2[idx+1][0] )
            idx += 1
            print (str(idx).rjust(3), z[1].ljust(zMax, '.'), z[3], z[2])



    if treeRow is not None :
        treeRow[1] = "Mise à jour des émissions"
        treeRow[2] = str(len(tabXML)) + " émissions disponibles"


    return tabXML



def display_emi_iter(store, treeiter,  dl_id):
    """Réaffiche le row masqué dans la zone emissions."""

    while treeiter is not None:
        if store[treeiter][0] == dl_id:
            store[treeiter][5] = True
            break
        if store.iter_has_child(treeiter):
            childiter = store.iter_children(treeiter)
            display_emi_iter(store, childiter,  dl_id)
        treeiter = store.iter_next(treeiter)





def display_info(GUI, text1, text2='' ):
    """Affiche message d'info dans le terminal ou en dans l'interface."""

    if GUI is not None :
        treeiter = GUI.mdl_info.append([time.strftime('%H:%M:%S'),text1, text2 ])
        return treeiter
    else:
        print(text1, text2)



def get_pluriel(val):
    """Retourne le pluriel s !"""

    if val > 1:
        return 's'
    else:
        return ''





def clean_file_name(nom):
    """Supprime les caractères superflus du nom de l'émission."""

    #nom = unicode(nom).decode('utf-8')
    nom = nom.replace('\\"', '"')
    nom = nom.replace('\n', '')
    nom = nom.replace('?', '_')
    nom = nom.replace('’', '\'')
    nom = nom.replace('/', '_')
    nom = nom.replace('...', '')
    nom = nom.replace('..', '.')
    return nom




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

import sys
from gi.repository import Gtk
from gi.repository import GLib

import subfunctions as sf
import download as dl


def stop_app(self,txt,stxt):
    """
    Quitte l'application avec message d'erreur.
    """

    if self.has_gui:
        message = Gtk.MessageDialog(
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=txt)
        message.format_secondary_text(stxt)
        message.set_title(__name__)
        message.set_position(Gtk.WindowPosition.CENTER)
        message.run()
    else:
        print(txt, stxt)
    sys.exit(1)


        
def alert_gui_message(gui, txt):
    """
    Message d'avertissement en GUI.
    """

    message = Gtk.MessageDialog(
        parent = gui.root,
        type=Gtk.MessageType.WARNING,
        buttons=Gtk.ButtonsType.OK,
        flags=Gtk.DialogFlags.MODAL,
        text=txt)
    message.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)    
    message.set_title(__name__)
    message.run()
    return message


                
class GUI_Main:
    """
    GUI application
    """

    def __init__(self, base):
        self.base = base
        self.has_gui = self.base.has_gui # pour appeler display_info
        self.base.GUI = self

        self.root = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.root.set_title(self.base.TITLE)
        self.root.set_size_request(800, 600)
        self.root.set_border_width(5)
        #self.root.set_has_frame(True) ## fuck the resize
        self.root.connect("destroy", self.destroy_cb)
        self.root.connect("show", self.show_window_cb)

        self.header_bar = Gtk.HeaderBar()
        self.header_bar.set_title(self.base.TITLE)
        self.header_bar.set_show_close_button (True)
        
        # Quitter par Escape
        self.accelgroup = Gtk.AccelGroup()
        key, modifier = Gtk.accelerator_parse('Escape')
        self.accelgroup.connect(key, modifier,
                                            Gtk.AccelFlags.VISIBLE,
                                            self.destroy_cb)
        self.root.add_accel_group(self.accelgroup)

        # Création des modèles et des treeview 
        self.StoreEmissions   = EmissionsModel()
        self.DisplayEmissions = DisplayEmissionsModel(self)
        self.StoreDownloads   = DownloadsModel()
        self.DisplayDownloads = DisplayDownloadsModel(self)
        self.StoreInfos       = InfosModel()
        self.DisplayInfos     = DisplayInfosModel()

        self.main_paned = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
        self.main_paned.set_position( int(0.75* self.root.get_size()[1]) )
        
        # Top Pane
        self.vpaned = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
        self.vpaned.set_position( int(0.5* self.root.get_size()[1]) )
        
        # top box = view_emi + command bar
        self.top_box = Gtk.VBox(homogeneous = False, spacing = 0)

        # cmd_box = controls
        self.cmd_box = Gtk.HBox(homogeneous = False, spacing = 0)

        # pour avoir les deux boutons DL Cancel avec la même taille
        self.btn_box = Gtk.HBox(homogeneous = True, spacing = 5)
        
        #self.btn_download.set_use_stock(False)
        ##Gtk.stock_add([(Gtk.STOCK_GO_DOWN, "_Télécharger", 0, 0, "")])
        #Gtk.stock_add([Gtk.STOCK_GO_DOWN, "_Télécharger"])
        #self.btn_download.new_from_stock( Gtk.STOCK_GO_DOWN) # = Gtk.Button("_Open")
         #self.btn_download.set_label('Gtk.STOCK_GO_DOWN')
        #self.btn_download    = Gtk.Button( stock = Gtk.STOCK_GO_DOWN, use_underline=True)
        #self.btn_download = Gtk.Button("_Open", stock=Gtk.STOCK_SAVE, use_stock=False, use_underline = True)
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # image and label are defined elsewhere
        box.add(Gtk.Image.new_from_icon_name(Gtk.STOCK_SAVE, Gtk.IconSize.BUTTON))
        box.add(Gtk.Label("_Télécharger", use_underline=True))
        self.btn_download = Gtk.Button(use_underline=True, always_show_image=True)
        self.btn_download.add(box)

        
        #button.show_all()
        #self.btn_download = Gtk.Button("_Save", use_stock=True, use_underline = True)
        self.btn_download.set_sensitive(False)
        self.btn_download.connect("clicked", self.download_cb)

        self.btn_cancel = Gtk.Button(stock = Gtk.STOCK_CANCEL, use_underline = True)
        self.btn_cancel.set_sensitive(False)
        self.btn_cancel.connect("clicked", self.cancel_download_cb)

        self.btn_quit       = Gtk.Button( stock=Gtk.STOCK_QUIT, use_underline=True)
        self.btn_quit.connect("clicked", self.destroy_cb, self.root )
        
        # scrolled window pour émissions
        self.scrol_win_emi = Gtk.ScrolledWindow()
        self.scrol_win_emi.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        self.scrol_win_emi.set_shadow_type(Gtk.ShadowType.IN)

        # scrolled window pour downloads
        self.scrol_win_dl = Gtk.ScrolledWindow()
        self.scrol_win_dl.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        self.scrol_win_dl.set_shadow_type(Gtk.ShadowType.IN)
        
        # scrolled window pour informations
        self.scrol_win_info = Gtk.ScrolledWindow()
        self.scrol_win_info.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrol_win_info.set_shadow_type(Gtk.ShadowType.IN)
        self.scrol_win_info.set_min_content_height(125)

        # Get the model and attach it to the view
        self.mdl_emi   = self.StoreEmissions.get_model()
        self.view_emi  = self.DisplayEmissions.make_view( self.mdl_emi )

        self.mdl_dl    = self.StoreDownloads.get_model()
        self.view_dl   = self.DisplayDownloads.make_view(self.mdl_dl)
        self.view_dl.connect('size-allocate', self.view_info_changed)

        self.mdl_dl.connect('row-inserted', self.model_dl_inserted)
        self.mdl_dl.connect('row-deleted', self.model_dl_deleted)
        
        self.mdl_info  = self.StoreInfos.get_model()
        self.view_info = self.DisplayInfos.make_view( self.mdl_info )
        self.view_info.connect('size-allocate', self.view_info_changed)
        
        # packing
        self.scrol_win_emi.add(self.view_emi)
        self.scrol_win_dl.add(self.view_dl)
        self.scrol_win_info.add(self.view_info)
        self.btn_box.pack_start(self.btn_download, True, True, 0)
        self.header_bar.pack_start(self.btn_download)
        self.btn_box.pack_start(self.btn_cancel, True, True, 0)
        self.cmd_box.pack_start(self.btn_box, False, False, 0)
        self.cmd_box.pack_end(self.btn_quit, False, False, 0)

        self.top_box.pack_start(self.scrol_win_emi, True, True, 0)
        self.top_box.pack_start(self.cmd_box, False, False, 5)
        self.vpaned.pack1(self.top_box, shrink = False)
        self.top_box.set_size_request(-1, 150)
        self.vpaned.pack2(self.scrol_win_dl, shrink = False)
        self.scrol_win_dl.set_size_request(-1, 100)
        self.vpaned.set_wide_handle = 30

        self.main_paned.pack1(self.vpaned, shrink = False) #_start(self.vpaned, True, True, 0)
        self.main_paned.pack2(self.scrol_win_info) #_end(self.scrol_win_info, False, True, 0)

        self.root.add(self.main_paned)
        self.root.show_all()
        
        return

    def model_dl_inserted(self,tree, model, path):
        self.update_dl()
        
    def model_dl_deleted(self, tree, model):
        self.update_dl()
        
    def update_dl(self):
        self.btn_download.set_sensitive( len(self.mdl_dl) != 0 ) 
        
    def view_info_changed(self, widget, event, data=None):
        """
        pour auto scroll:
        http://stackoverflow.com/questions/5218948/how-to-auto-scroll-a-Gtk-scrolledwindow
        """
        adj = self.scrol_win_info.get_vadjustment()
        adj.set_value( adj.get_upper() - adj.get_page_size() )
    

    def cancel_download_cb(self, widget):
        """Annule un téléchargement en cours."""
        self.base.force_cancel = True

        
        
        
    def download_cb(self, widget):
        """Lance les téléchargements."""
        self.base.force_cancel = False
        nbDL = len(self.mdl_dl)
        pluriel = sf.get_pluriel(nbDL)

        widget.set_sensitive(False)
        self.btn_cancel.set_sensitive(True)

        while len(self.mdl_dl)> 0 and not self.base.force_cancel:
            #id de la première ligne
            emi_id     = self.mdl_dl[0][0]
            #pgbar_text = self.mdl_dl[0][5]
            
            for page_info in self.base.arte7 :
                if page_info[0] == emi_id : #id match
                    dl.download_video(self.base, page_info, self.mdl_dl[0])
                    #supprime ligne mdl_dl et réaffiche dans mdl_emi
                    rootiter = self.mdl_emi.get_iter_first()
                    sf.display_emi_iter(self.mdl_emi, rootiter, page_info[0])                    
                        #print (page_info)

        widget.set_sensitive(True)
        if self.base.force_cancel:
            sf.display_info(self, "Téléchargement(s) annulé(s)")

        # efface sélection
        self.base.downloads = []

        
        self.btn_download.set_sensitive(len(self.mdl_dl)>0)
        self.btn_cancel.set_sensitive(False)
        self.base.cat = self.base.get_catalogue()


 

    def destroy_cb(self, *kw):
        """ Destroy callback to shutdown the app """
        if self.base.dl_running:
            message = Gtk.MessageDialog(
                parent = self.root,
                type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Interrompre le(s) téléchargement(s) ?")
            message.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
            
            
            reponse = message.run()
            if reponse == Gtk.ResponseType.YES:
                self.base.force_cancel = True
                Gtk.main_quit()
            else:
                message.destroy()
        else:        
            Gtk.main_quit()
        return

    def run(self):
        """ run is called to set off the Gtk mainloop """
        Gtk.main()
         

    def update_emissions(self, info_row):
        # print (self.mdl_emi)
        self.mdl_emi.clear()
        self.base.arte7 = sf.listing_emissions_arte(self.base, treeRow = info_row)
        self.StoreEmissions.put_data(self.base)
        self.view_emi.expand_all()
        
    
    def show_window_cb(self, widget):
        """ affichage application """
                
        sf.display_info(self.base.GUI, 
                "Démarrage, fichier de conf. : " + self.base.args.CONFIG_FILE)
        nbCat = len(self.base.cat)
        pluriel = sf.get_pluriel(nbCat)
        sf.display_info(self, 
            "Lecture du catalogue " + self.base.params['catalogue'] + \
            " : " + str(nbCat) + " ligne" + pluriel)
        iterRow = sf.display_info(self, "Mise à jour émissions ...")
        info_row =  self.mdl_info[iterRow]
        
        # affichage progressbar
        # info_row[3] = True #visible
        # time pour afficher les infos dans le bon ordre dans la fenetre (démarrage, catalogue ...)
        GLib.timeout_add(100, self.update_emissions, info_row )
        
        return




class InfosModel:
    """ 
    Modèle pour listview infos.
    """
    def __init__(self):
        self.list_store = Gtk.ListStore(
                str,  #0 Time
                str,  #1 Information / fichier
                str)  #2 Message
        return

    def get_model(self):
        """ Returns the model """
        if self.list_store:
            return self.list_store 
        else:
            return None





class DisplayInfosModel:
    """
    treeView Informations
    """
    def make_view(self, model):
        self.view = Gtk.TreeView (model)
       # self.view.set_level_indentation(0)
        self.cell0 = Gtk.CellRendererText()
        self.cell1 = Gtk.CellRendererText()
        self.cell2 = Gtk.CellRendererText()
        
        self.column0 = Gtk.TreeViewColumn("Heure",         self.cell0, text=0)
        self.column1 = Gtk.TreeViewColumn("Info./fichier", self.cell1, text=1)
        self.column2 = Gtk.TreeViewColumn("Message",       self.cell2, text=2 )
        
        self.column0.set_resizable(True)
        self.column1.set_resizable(True)
        self.column2.set_resizable(True)
                
        #self.column2.add_attribute(self.progress, 'visible', 3)

        self.view.set_enable_search(False)
        self.view.append_column( self.column0 )
        self.view.append_column( self.column1 )
        self.view.append_column( self.column2 )
        #self.view.set_tooltip_column(1)
        self.view.connect("button-release-event",  self.click_tree_view, model)


        self.menu_info = Gtk.Menu()
        self.menu_info_remove_all   = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_REMOVE, None)
        self.menu_info_remove_all.set_label("Tout e_ffacer")
        self.menu_info_remove_all.connect('activate', lambda q: model.clear() ) #]self.view.expand_all())
        self.menu_info.append( self.menu_info_remove_all )
        self.menu_info.show_all()

                
        return self.view

    def click_tree_view(self, treeview, event, model):
        if event.button == 3 :
            self.menu_info_remove_all.set_sensitive(len(model) != 0)
            self.menu_info.popup(None, None, None,  None, event.button, event.time)


class EmissionsModel:
    """ 
    model class pour les émissions disponibles
    """
    def __init__(self):
        self.tree_store = Gtk.TreeStore(
                str,    #0 id
                str,    #1 page /emission
                str,    #2 date
                str,    #3 durée
                str,    #4 titre
                bool,   #5 show
                str)    #6 teaser
        return

    def put_data(self, base):
        """
        création de la liste d'émissions disponibles"
        """

        for pg in base.pages_arte:
            parent = self.tree_store.append (None,  #parent
                                    (None,
                                    pg.capitalize(),
                                     None, None, None, True, None))
            idx = 0
            for emi in base.arte7:
                #0 id          #5 subtitle
                #1 page        #6 right_ends
                #2 titre       #7 teaser    
                #3 scheduled   #8 thumbnail_url
                #4 duration    #9 views
                if emi[1] == pg:
                    self.tree_store.append(parent,
                        (emi[0],
                        emi[2],
                        emi[3],
                        emi[4], 
                        emi[5],
                        True ,
                        emi[7]
                        ))
                        #idx   )) #index dans arrEmission
                    idx +=1
                    
                                   
    def get_model(self):
        """ Returns the model """
        if self.tree_store:
            return self.tree_store 
        else:
            return None





class DownloadsModel:
    """ 
    model class pour les dowloads disponibles
    """
    def __init__(self):
        self.tree_store = Gtk.ListStore( 
                str,    #0 id
                str,    #1 emission
                str,    #2 date
                str,    #3 durée
                str,    #4 titre
                str,    #5 progress bar text
                float,  #6 progress bar value
                str)    #8 tooltip

#                bool,   #7 display pg bar
        return

      
                                   
    def get_model(self):
        """ Returns the model """
        if self.tree_store:
            return self.tree_store 
        else:
            return None



class DisplayDownloadsModel:
    """
    TreeView Emissions
    """
    def __init__(self, GUI):
        self.parent = GUI
        return

    """ Displays the Info_Model model in a view """
    def make_view( self, model ):
    
        """ Form a view for the Tree Model """
        self.view = Gtk.TreeView( model )
        #self.view.set_reorderable(True)
        #self.toggle_dl    = Gtk.CellRendererToggle()
        #self.toggle_dl.set_property('activatable', True)

        #self.cell01    = Gtk.CellRendererText()
        self.renderer0 = Gtk.CellRendererText()
        self.renderer1 = Gtk.CellRendererText()
        self.renderer2 = Gtk.CellRendererText()
        self.renderer3 = Gtk.CellRendererText()
        self.renderer4 = Gtk.CellRendererProgress()
        #self.renderer5 = Gtk.CellRendererText()

        #self.toggle_dl.connect( 'toggled', self.toggle_dl_cb, model )
        
        #self.column0.pack_start(self.toggle_dl, False)
        #self.column0.pack_start(self.renderer1, True)        

        #self.column0.add_attribute(self.toggle_dl, 'active', False)
        #self.column0.add_attribute(self.toggle_dl, 'visible', 1)
        #self.column0.add_attribute(self.cell01, 'text', 2)
        self.column0 = Gtk.TreeViewColumn("Nom", self.renderer1, text=1 )
        self.column1 = Gtk.TreeViewColumn("Date", self.renderer1, text=2 )
        self.column2 = Gtk.TreeViewColumn("Durée", self.renderer1, text=3 )
        self.column3 = Gtk.TreeViewColumn("Titre", self.renderer2, text=4 )
        self.column4 = Gtk.TreeViewColumn("Progression", self.renderer4, text=5 , value=6)
        #self.column5 = Gtk.TreeViewColumn("tooltip", self.renderer2, text=7 )
        
        self.view.append_column( self.column0 )
        self.view.append_column( self.column1 )
        self.view.append_column( self.column2 )
        self.view.append_column( self.column3 )
        self.view.append_column( self.column4 )
        #self.view.append_column( self.column5 )

        self.column0.set_resizable(True)
        self.column1.set_resizable(True)
        self.column2.set_resizable(True)
        self.column3.set_resizable(True)
        self.column4.set_resizable(True)
        #self.column5.set_resizable(True)
        #self.view.connect("row-activated", self.row_click, model)

        #self.view.expand_all()
        self.view.connect("row-activated", self.row_download_click)
        self.view.set_tooltip_column(7)
        
        self.view.set_enable_search(False)
        return self.view

    def row_download_click(self, iter, path, view_column):
        """
        double click active check box
        """

        """
        model_dl  = self.parent.mdl_dl
        selection = self.view.get_selection()
        model_emi, treeiter = selection.get_selected()

        #cas click sur mod
        if model_emi[path][0] is None :
            return

        treeiter0 = model_dl.append(None, [model_emi[treeiter][0],
                                        model_emi[treeiter][1],
                                        model_emi[treeiter][2],
                                        model_emi[treeiter][3],
                                        model_emi[treeiter][4],
                                        "En attente", 0, True])

        self.filter[path][5] = False

        """
        if self.parent.base.dl_running:
            message = alert_gui_message(self.parent, "Téléchargement en cours, interrompre par bouton annuler")
            message.destroy()
            return
        model_emi = self.parent.mdl_emi
        #model_dl  = self.parent.mdl_dl

        selection = self.view.get_selection()
        model_dl, treeiter = selection.get_selected()
        dl_id = model_dl[treeiter][0]
        
        model_dl.remove( treeiter )

        """
        def display_emi_iter(store, treeiter,  dl_id):

        """
           # réaffiche le row masqué dans la zone emissions
        """
            while treeiter is not None:
                if store[treeiter][0] == dl_id:
                    store[treeiter][5] = True
                    break
                if store.iter_has_child(treeiter):
                    childiter = store.iter_children(treeiter)
                    display_emi_iter(store, childiter,  dl_id)
                treeiter = store.iter_next(treeiter)
        """
        
        rootiter = model_emi.get_iter_first()
        sf.display_emi_iter(model_emi, rootiter, dl_id)


        
        #self.filter[path][5] = False            

#    def row_click(self,iter,  path, view_column, model):
#        """
#        double click active check box
#        """
#        self.toggle_dl_cb(None, path, model)



 #   def toggle_dl_cb( self, cell, path, model ):
 #       """
 #       Sets the toggled state on the toggle button to true or false.
 #       """
 #       if self.base.dl_running:
 #           message = alert_gui_message(self.base.GUI,
 #                               "Action impossible lorsqu'un téléchargement est actif")
 #           message.destroy()
 #           return
            
 #       model[path][0] = not model[path][0]
 #       id = model[path][3]

 #       for ligne in self.base.arte7:
 #           if id == ligne[2]:
 #               newEmi = ligne
 #               break
 #               
 #       if model[path][0]:
 #           self.base.downloads.append([ None, newEmi, path  ] ) #Abo = None, [page_info], path dans treemodel
 #       else:
#            self.base.downloads.remove([ None, newEmi, path ] )  #Abo = None, [page_info], path dans treemodel
#
 #       nbDL = len(self.base.downloads)
 #       pluriel = sf.get_pluriel ( nbDL )
 #       self.base.GUI.btn_download.set_sensitive( nbDL !=0)
 #       self.base.GUI.label_selection.set_text("Sélection : %d émission%s " % ( nbDL , pluriel) )



class DisplayEmissionsModel:
    """
    TreeView Emissions
    """
    def __init__(self, GUI):
        self.parent = GUI
        return

    """ Displays the Info_Model model in a view """
    def make_view( self , model_emi):
    
        """ Form a view for the Tree Model """

        self.filter = model_emi.filter_new()
        self.filter.set_visible_column(5)
        
        self.view = Gtk.TreeView(self.filter)
        

        self.toggle_dl    = Gtk.CellRendererToggle()
        self.toggle_dl.set_property('activatable', True)

        #self.cell01    = Gtk.CellRendererText()
        #self.renderer00 = Gtk.CellRendererText()
        self.renderer0 = Gtk.CellRendererText()
        self.renderer1 = Gtk.CellRendererText()
        self.renderer2 = Gtk.CellRendererText()
        self.renderer3 = Gtk.CellRendererText()
        #self.renderer4 = Gtk.CellRendererToggle()


        #self.toggle_dl.connect( 'toggled', self.toggle_dl_cb, self.GUI.mdl_emi )
        

        #self.column0.pack_start(self.toggle_dl, False)
        #self.column0.pack_start(self.renderer1, True)        

        #self.column0.add_attribute(self.toggle_dl, 'active', False)
        #self.column0.add_attribute(self.toggle_dl, 'visible', 1)
        #self.column0.add_attribute(self.cell01, 'text', 2)
        #self.column00 = Gtk.TreeViewColumn("ID",   self.renderer00, text=0)            
        self.column0 = Gtk.TreeViewColumn("Nom",   self.renderer0, text=1)            
        self.column1 = Gtk.TreeViewColumn("Date",  self.renderer1, text=2 )
        self.column2 = Gtk.TreeViewColumn("Durée", self.renderer2, text=3 )
        self.column3 = Gtk.TreeViewColumn("Titre", self.renderer3, text=4 )
        #self.column4 = Gtk.TreeViewColumn("visible", self.renderer4, active=5 )


        #self.column00.set_resizable(True)
        self.column0.set_resizable(True)
        self.column1.set_resizable(True)
        self.column2.set_resizable(True)
        self.column3.set_resizable(True)
        #self.column4.set_resizable(True)
                
        #self.view.append_column( self.column00 )
        self.view.append_column( self.column0 )
        self.view.append_column( self.column1 )
        self.view.append_column( self.column2 )
        self.view.append_column( self.column3 )
        #self.view.append_column( self.column4 )


        self.view.connect("row-activated", self.row_emission_click)
        self.view.connect("button-release-event",  self.click_tree_view)
        self.view.expand_all()
        
        self.view.set_tooltip_column(6)
        self.view.set_enable_search(False)


        self.menu_emi = Gtk.Menu()
        self.menu_emi_expand   = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_ADD, None)
        self.menu_emi_collapse = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_REMOVE, None)
        self.menu_emi_expand.set_label("Tout dépli_er")
        self.menu_emi_collapse.set_label("Tout _replier")
        self.menu_emi_expand.connect('activate', lambda q: self.view.expand_all())
        self.menu_emi_collapse.connect('activate', lambda q: self.view.collapse_all())
        self.menu_emi.append( self.menu_emi_expand )
        self.menu_emi.append( self.menu_emi_collapse )
        self.menu_emi.show_all()
        return self.view

    def click_tree_view(self, treeview, event):
        if event.button == 3 :
            self.menu_emi.popup(None, None, None,  None, event.button, event.time)


            

    def row_emission_click(self,iter,  path, view_column):
        """
        double click active check box
        """
        model_dl  = self.parent.mdl_dl
        selection = self.view.get_selection()
        model_emi, treeiter = selection.get_selected()

        #cas click sur mod
        if model_emi[path][0] is None :
            return

        treeiter0 = model_dl.append( [model_emi[treeiter][0],
                                        model_emi[treeiter][1],
                                        model_emi[treeiter][2],
                                        model_emi[treeiter][3],
                                        model_emi[treeiter][4],
                                        "En attente", 0,
                                        model_emi[treeiter][1] + " (" + model_emi[treeiter][2] + ") : en attente"
                                        ])
        self.filter[path][5] = False


    def toggle_dl_cb( self, cell, path, model ):
        """
        Sets the toggled state on the toggle button to true or false.
        """
        if self.base.dl_running:
            message = alert_gui_message(self.base.GUI,
                                "Action impossible lorsqu'un téléchargement est actif")
            message.destroy()
            return
            
        model[path][0] = not model[path][0]
        id = model[path][3]

        for ligne in self.base.arte7:
            if id == ligne[2]:
                newEmi = ligne
                break
                
        if model[path][0]:
            self.base.downloads.append([ None, newEmi, path  ] ) #Abo = None, [page_info], path dans treemodel
        else:
            self.base.downloads.remove([ None, newEmi, path ] )  #Abo = None, [page_info], path dans treemodel

        nbDL = len(self.base.downloads)
        pluriel = sf.get_pluriel ( nbDL )
        self.base.GUI.btn_download.set_sensitive( nbDL !=0)
        self.base.GUI.label_selection.set_text("Sélection : %d émission%s " % ( nbDL , pluriel) )
        

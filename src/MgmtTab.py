from gtk import TRUE, FALSE
import string
import gobject
import sys
import MessageLibrary
from CommandError import CommandError
from clui_constants import *
from CommandHandler import CommandHandler

import gettext
_ = gettext.gettext
### gettext first, then import gtk (exception prints gettext "_") ###
try:
    import gtk
    import gtk.glade
except RuntimeError, e:
    print _("""
  Unable to initialize graphical environment. Most likely cause of failure
  is that the tool was not run using a graphical environment. Please either
  start your graphical user interface or set your DISPLAY variable.
                                                                                
  Caught exception: %s
""") % e
    sys.exit(-1)
                                                                                
import gnome
import gnome.ui
                                                                                
#from MgmtTabController import MgmtTabController

ON_MEMBER=_("On Member: %s")

STATUS=_("Status: %s")

S_NAME=_("Service Name")
S_STATE=_("State")
S_OWNER=_("Owner")
S_LASTOWNER=_("Previous Owner")
S_RESTARTS=_("Restarts")

NAME_COL = 0
VOTES_COL = 1
STATUS_COL = 2

S_NAME_COL = 0
S_STATE_COL = 1
S_OWNER_COL = 2
S_LASTOWNER_COL = 3
S_RESTARTS_COL = 4

############################################
class MgmtTab:
  def __init__(self, glade_xml, model_builder):

    self.model_builder = model_builder
    self.glade_xml = glade_xml
    self.command_handler = CommandHandler()
                                                                                
    #set up node tree structure
    self.nodetree = self.glade_xml.get_widget('nodetree')
    self.treemodel = gtk.TreeStore (gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gobject.TYPE_STRING)
    self.nodetree.set_model(self.treemodel)

    renderer = gtk.CellRendererText()
    column1 = gtk.TreeViewColumn(T_NAME,renderer,text=0)
    self.nodetree.append_column(column1)

    renderer2 = gtk.CellRendererText()
    column2 = gtk.TreeViewColumn(T_VOTES,renderer2,text=1)
    self.nodetree.append_column(column2)

    renderer3 = gtk.CellRendererText()
    column3 = gtk.TreeViewColumn(T_STATUS,renderer3,text=2)
    self.nodetree.append_column(column3)


    self.prep_tree()

    #set up services tree structure
    self.servicetree = self.glade_xml.get_widget('servicetree')
    self.streemodel = gtk.TreeStore (gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gobject.TYPE_STRING)
    self.servicetree.set_model(self.streemodel)

    srenderer = gtk.CellRendererText()
    scolumn1 = gtk.TreeViewColumn(S_NAME,srenderer,text=0)
    self.servicetree.append_column(scolumn1)

    srenderer2 = gtk.CellRendererText()
    scolumn2 = gtk.TreeViewColumn(S_STATE,srenderer2,text=1)
    self.servicetree.append_column(scolumn2)

    srenderer3 = gtk.CellRendererText()
    scolumn3 = gtk.TreeViewColumn(S_OWNER,srenderer3,text=2)
    self.servicetree.append_column(scolumn3)

    srenderer4 = gtk.CellRendererText()
    scolumn4 = gtk.TreeViewColumn(S_LASTOWNER,srenderer4,text=3)
    self.servicetree.append_column(scolumn4)

    srenderer5 = gtk.CellRendererText()
    scolumn5 = gtk.TreeViewColumn(S_RESTARTS,srenderer5,text=4)
    self.servicetree.append_column(scolumn5)

    self.prep_service_tree()


    self.clustername = self.glade_xml.get_widget('entry25')
    self.clustername.set_text(self.command_handler.getClusterName())
    self.qbox = self.glade_xml.get_widget('checkbutton3')
    if self.command_handler.isClusterQuorate() == TRUE:
      self.qbox.set_active(TRUE)
    else:
      self.qbox.set_active(FALSE)

    #Now set info labels
    self.glade_xml.get_widget('label90').set_text(STATUS % self.command_handler.getClusterStatus())
    self.glade_xml.get_widget('label93').set_text(ON_MEMBER % self.command_handler.getNodeName())
                                                                                
#    self.controller = MgmtTabController(self.model_builder,
#                                          self.nodetree,
#                                          self.glade_xml,
#                                          self.reset_tree_model)
                                                                                

  def prep_tree(self):
    treemodel = self.nodetree.get_model()
    treemodel.clear()

    try:
      nodes = self.command_handler.getNodesInfo()
    except CommandError, e:
      retval = MessageLibrary.errorMessage(e.getMessage())
      return

    for node in nodes:
      iter = treemodel.append(None)
      name, votes, status = node.getNodeProps()
      treemodel.set(iter, NAME_COL, name,
                          VOTES_COL, votes,
                          STATUS_COL, status) 

  def prep_service_tree(self):
    treemodel = self.servicetree.get_model()
    treemodel.clear()

    try:
      services = self.command_handler.getServicesInfo()
    except CommandError, e:
      retval = MessageLibrary.errorMessage(e.getMessage())
      return

    for service in services:
      iter = treemodel.append(None)
      name, state, owner, lastowner, restarts = service.getServiceProps()
      treemodel.set(iter, S_NAME_COL, name,
                          S_STATE_COL, state,
                          S_OWNER_COL, owner,
                          S_LASTOWNER_COL, lastowner,
                          S_RESTARTS_COL, restarts) 

from gtk import TRUE, FALSE
import string
import gobject
import sys
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

T_NAME=_("Name")
T_VOTES=_("Votes")
T_STATUS=_("Status")

NAME_COL = 0
VOTES_COL = 1
STATUS_COL = 2

############################################
class MgmtTab:
  def __init__(self, glade_xml, model_builder):

    self.model_builder = model_builder
    self.glade_xml = glade_xml
    self.command_handler = CommandHandler()
                                                                                
    #set up tree structure
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

    nodes = self.command_handler.getNodesInfo()
    for node in nodes:
      iter = treemodel.append(None)
      name, votes, status = node.getNodeProps()
      treemodel.set(iter, NAME_COL, name,
                          VOTES_COL, votes,
                          STATUS_COL, status) 

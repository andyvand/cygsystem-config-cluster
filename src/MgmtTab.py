from gtk import TRUE, FALSE
import string
import gobject
import sys
from clui_constants import *

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
                                                                                
from MgmtTabController import MgmtTabController

############################################
class MgmtTab:
  def __init__(self, glade_xml, model_builder):

    self.model_builder = model_builder
    self.glade_xml = glade_xml
                                                                                
    #set up tree structure
    self.nodetree = self.glade_xml.get_widget('nodetree')
    self.treemodel = gtk.TreeStore (gobject.TYPE_STRING,
                                    gobject.TYPE_INT,
                                    gobject.TYPE_PYOBJECT)
    self.nodetree.set_model(self.treemodel)
    #self.treeview.set_headers_visible(FALSE)
                                                                                
    self.controller = MgmtTabController(self.model_builder,
                                          self.nodetree,
                                          self.glade_xml,
                                          self.reset_tree_model)
                                                                                



from Service import Service
from ResourceHandler import *
import gobject
from gtk import TRUE, FALSE
from clui_constants import *

import gettext
_ = gettext.gettext
### gettext first, then import gtk (exception prints gettext "_") ###
import gtk
import gtk.glade 

R_NAME_COL = 0
R_TYPE_COL = 1
R_SCOPE_COL = 2
R_OBJ_COL = 3

###YUK! XXX make access to this static in ResourceHandler
###This is an awful copy
RC_OPTS = {"ip":_("IP Address"),
           "script":_("Script"),
           "nfsclient":_("NFS Client"),
           "nfsexport":_("NFS Export"),
           "fs":_("File System"),
           "service":_("Service"),
           "group":_("Resource Group") }


SHARED_RESOURCE=_("Shared")
PRIVATE_RESOURCE=_("Private")

class ServiceController:
  def __init__(self, glade_xml,model_builder,reset_tree_model):
    self.glade_xml = glade_xml
    self.model_builder = model_builder
    self.reset_tree_model = reset_tree_model
    self.process_widgets()
    self.rm_ptr = self.model_builder.getResourceManagerPtr()
    self.current_service = None
    self.foreach_found_sentinel = FALSE
    self.rc_prettyname_hash = RC_OPTS
    

  def process_widgets(self):
    self.svc_treeview = self.glade_xml.get_widget('svc_treeview')
    self.treemodel = gtk.ListStore(gobject.TYPE_STRING, #Name
                                   gobject.TYPE_STRING, #Priority
                                   gobject.TYPE_STRING, #Priority
                                   gobject.TYPE_PYOBJECT) #OBJ_COL
    self.svc_treeview.set_model(self.treemodel)
    selection = self.svc_treeview.get_selection()
    selection.connect('changed',self.on_list_selection_changed)

    renderer = gtk.CellRendererText()
    self.column1 = gtk.TreeViewColumn("Name",renderer,markup=0)
    self.svc_treeview.append_column(self.column1)

    renderer2 = gtk.CellRendererText()
    self.column2 = gtk.TreeViewColumn("Type",renderer2,markup=1)
    self.svc_treeview.append_column(self.column2)

    renderer3 = gtk.CellRendererText()
    self.column3 = gtk.TreeViewColumn("Scope",renderer3,markup=2)
    self.svc_treeview.append_column(self.column3)

    self.treeview_window = self.glade_xml.get_widget('scrolledwindow3')
    self.glade_xml.get_widget('button22').connect("clicked",self.on_add_shared)
    self.glade_xml.get_widget('button23').connect("clicked",self.on_add_private)
    self.glade_xml.get_widget('button24').connect("clicked",self.on_del_resource)
    self.service_name_label = self.glade_xml.get_widget('label103')


  def on_add_shared(self, button):

    pass


  def on_add_private(self, button):
    pass

  def on_del_resource(self, button):
    selection = self.svc_treeview.get_selection()
    model, iter = selection.get_selected()
    robj = model.get_value(iter, R_OBJ_COL)
    self.current_service.removeChild(robj)
    self.prep_service_tree()

  def on_list_selection_changed(self, *args):
    selection = self.svc_treeview.get_selection()
    model,iter = selection.get_selected()


  def prep_service_panel(self, svc):
    self.current_service = svc
    if self.current_service != None:  
      self.service_name_label.set_markup("<span><b>" + svc.getName() + "</b></span>")


      #self.prep_optionmenu()
      self.prep_service_tree()

#  def prep_optionmenu(self):
#    pass
#    found = FALSE
#    optionmenu_candidates = list()
#    nodes = self.model_builder.getNodes()
#    for node in nodes:
#      found = FALSE
#      children = self.current_faildom.getChildren()
#      for child in children:
#        if child.getName().strip() == node.getName().strip():
#          found = TRUE
#          break
#      if found:
#        continue
#      else:
#        optionmenu_candidates.append(node.getName()) 
#
#    #Now we have the set of node names NOT in the current failover domain
#    menu = gtk.Menu()
#    if len(optionmenu_candidates) > 0:
#      m = gtk.MenuItem(NODES_AVAILABLE)
#      m.show()
#      menu.append(m)
#      for opt in optionmenu_candidates:
#        m = gtk.MenuItem(opt)
#        m.show()
#        menu.append(m)
#    else:
#      m = gtk.MenuItem(NO_NODES_AVAILABLE)
#      m.show()
#      menu.append(m)
#
#    self.node_options.set_menu(menu)
#
  def prep_service_tree(self):
    resources = self.current_service.getChildren()
    treemodel = self.svc_treeview.get_model()
    treemodel.clear()
    for child in resources:
      if child.isRefObject() == TRUE:
        str_buf = SHARED_RESOURCE
      else:
        str_buf = PRIVATE_RESOURCE
      prettyname = self.rc_prettyname_hash[child.getTagName()]
      iter = treemodel.append()
      treemodel.set(iter, R_NAME_COL, child.getName(),
                            R_TYPE_COL, prettyname,
                            R_SCOPE_COL, str_buf,
                            R_OBJ_COL, child)

      self.svc_treeview.get_selection().unselect_all()  
      

  def set_model(self, model_builder):
    self.model_builder = model_builder


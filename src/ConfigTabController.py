"""This class represents the primary controller interface
   for the cluster management tab.
"""
__author__ = 'Jim Parsons (jparsons@redhat.com)'
                                                                                
                                                                                
from gtk import TRUE, FALSE
import string
import os
import gobject

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

from clui_constants import *
from FenceHandler import FenceHandler
from FenceDevice import FenceDevice
from FaildomController import FaildomController
from FailoverDomain import FailoverDomain
from Device import Device
from Method import Method
from Fence import Fence
from ResourceHandler import ResourceHandler
from PropertiesRenderer import PropertiesRenderer

PIXMAP_DIR = "./pixmaps/"
INSTALLDIR = "/usr/share/system-config-cluster/"

 
FENCE_PIX_COL=0
FENCE_NAME_COL=1
FENCE_TYPE_COL=2
FENCE_OBJ_COL=3

NODE_NEW = 0
NODE_EXISTING = 1

NAME_ATTR = "name"
VOTES_ATTR = "votes"

FI_TYPE=_("Fence Device Type: \n %s")

AFF_NODES=_("Affected Cluster Nodes")

WARNING1=_("The following Cluster Node depends on Fence Device %s.")

WARNINGS1=_("The following Cluster Nodes depend on Fence Device %s.")

WARNING2=_("Removing this Fence Device will alter Fencing on this Cluster Node.\n Are you certain that you wish to continue?")

WARNINGS2=_("Removing this Fence Device will alter Fencing on these Cluster Nodes.\n Are you certain that you wish to continue?")

ADD_FENCE_DEVICE=_("Add a New Fence Device")

EDIT_FENCE_DEVICE=_("Edit Properties for this Fence Device")

CONFIRM_FD_DELETE=_("Are you certain that you wish to delete Fence Device %s?")

ADD_FENCE=_("Add a New Fence")

EDIT_FENCE=_("Edit Properties for Fence: %s")

FENCE_PANEL_LABEL=_("<span size=\"11000\">Fence Configuration for Cluster Node: <b> %s</b></span>")

NEED_CLUSTER_NAME=_("Please provide a name for the cluster")

NODE_UNIQUE_NAME=_("Names for Cluster Nodes must be Unique. Please choose another name for this Node.")

NODE_NAME_REQUIRED=_("Please provide a name for this Cluster Node.")

FAILDOM_NAME_REQUIRED=_("Please provide a name for the new Failover Domain")

UNIQUE_FAILDOM_NAME=_("Failover Domains must have unique names. The name %s is already in use. Please provide a unique name.")

VOTES_ONLY_DIGITS=_("Valid values for the votes field are integer values between zero and 255, or nothing, which defaults to 1.")

CONFIRM_NODE_REMOVE=_("Are you sure you wish to remove node %s? This node, along with its fence instances and membership in failover domains will be removed.")

CONFIRM_FAILDOM_REMOVE=_("Are you certain that you wish to remove Failover Domain %s ?")

CONFIRM_RC_REMOVE=_("Are you certain that you wish to remove resource %s ?")

CONFIRM_LEVEL_REMOVE=_("Are you certain that you wish to remove this fence level and all fences contained within it??")

CONFIRM_LEVEL_REMOVE_EMPTY=_("Are you certain that you wish to remove this fence level?")

CONFIRM_FI_REMOVE=_("Are you certain that you wish to remove this fence?")

SELECT_RC_TYPE=_("<span><b>Select a Resource Type:</b></span>")

RC_PROPS=_("Properties for %s Resource: %s")

###TRANSLATOR: The string below is used as an attr value in an XML file, as well
###as a GUI string. Please do not use whitespace in this string. 
FENCE_LEVEL=_("Fence-Level-%d")

from ClusterNode import ClusterNode

class ConfigTabController:
  def __init__(self,model_builder, treeview, glade_xml,reset_tree_model):
    self.model_builder = model_builder
    self.treeview = treeview
    self.glade_xml = glade_xml
    self.reset_tree_model = reset_tree_model

    self.faildom_controller = FaildomController(self.glade_xml,self.model_builder,reset_tree_model)

    if not os.path.exists(PIXMAP_DIR):
      PIXMAPS = INSTALLDIR + PIXMAP_DIR
    else:
      PIXMAPS = PIXMAP_DIR
    self.node_pixbuf = gtk.gdk.pixbuf_new_from_file(PIXMAPS + "node.png")
    self.fence_pixbuf = gtk.gdk.pixbuf_new_from_file(PIXMAPS + "fence.png")

    self.fence_props_area = self.glade_xml.get_widget('drawingarea2')
    #self.fence_props_area.connect('expose-event',self.on_f_props_expose_event)
    #self.fence_prop_renderer = PropertiesRenderer(self.fence_props_area,self.fence_props_area.window)
    #self.fence_prop_renderer.clear_layout_area()


    #Flags for interpreting dialogs
    self.node_props_flag = NODE_NEW
   
    self.fi_proxy = self.glade_xml.get_widget('fence_instance_proxy') 
    self.fd_proxy = self.glade_xml.get_widget('fence_device_proxy') 
    self.fence_handler = FenceHandler(self.fi_proxy,self.fd_proxy, self.model_builder)
    self.fenceinstance_form_hash = self.fence_handler.get_fence_instance_hash()
    self.fencedevice_form_hash = self.fence_handler.get_fence_device_hash()

    self.fi_optionmenu_hash = {}
    self.fi_agent_hash = {}
    self.fi_prettyname_hash = {}
    self.fd_optionmenu_hash = {}

    self.rc_proxy = self.glade_xml.get_widget('rc_proxy')
    self.rc_handler = ResourceHandler(self.rc_proxy,self.model_builder)
    self.rc_form_hash = self.rc_handler.get_rc_hash()
    self.rc_prettyname_hash = self.rc_handler.get_pretty_rcname_hash()
    self.rc_optionmenu_hash = {}
    self.rc_dlg_label = self.glade_xml.get_widget('rc_dlg_label')
    self.rc_panel = self.glade_xml.get_widget('rc_panel')
    self.rc_panel.connect("delete_event",self.rc_panel_delete)

    self.setupFencePanel()
    self.setupDialogsandButtons()

  def setupDialogsandButtons(self):

    self.props_area = self.glade_xml.get_widget('props_area')
    self.fence_panel_label = self.glade_xml.get_widget('fence_panel_label')
    self.fi_task_label = self.glade_xml.get_widget('fence_panel_task_label')
    #dialogs
    self.node_props = self.glade_xml.get_widget('node_properties')
    self.node_props.connect("delete_event",self.node_props_delete)
    self.node_props_ok = self.glade_xml.get_widget('okbutton11')
    self.node_props_ok.connect("clicked",self.on_node_props_ok)
    self.node_props_cancel = self.glade_xml.get_widget('cancelbutton11')
    self.node_props_cancel.connect("clicked",self.on_node_props_cancel)

    self.fence_panel = self.glade_xml.get_widget('fence_panel')
    self.fence_panel.connect("delete_event", self.fence_panel_delete)
    self.faildom_panel = self.glade_xml.get_widget('faildom_panel')
    self.faildom_panel.connect("delete_event", self.faildom_panel_delete)

    ##buttons from button panels
    #Nodes
    self.clusternode_add_b = self.glade_xml.get_widget('clusternode_add_b')
    self.clusternode_add_b.connect("clicked",self.on_clusternode_add_b)
    self.clusternode_edit_b = self.glade_xml.get_widget('node_edit_b')
    self.clusternode_edit_b.connect("clicked",self.on_clusternode_edit_b)
    self.clusternode_delete_b = self.glade_xml.get_widget('node_delete_b')
    self.clusternode_delete_b.connect("clicked",self.on_clusternode_delete_b)
    self.clusternode_fence_b = self.glade_xml.get_widget('node_fence_b')
    self.clusternode_fence_b.connect("clicked",self.on_clusternode_fence_b)
    self.fence_edit_b = self.glade_xml.get_widget('fence_edit_b')
    self.fence_edit_b.connect("clicked",self.on_clusternode_fence_b)

    ##Cluster Props
    self.glade_xml.get_widget('cluster_edit_b').connect('clicked',self.on_cluster_props_edit)
    self.glade_xml.get_widget('cancelbutton16').connect('clicked',self.on_cluster_props_edit_cancel)
    self.glade_xml.get_widget('okbutton16').connect('clicked',self.on_cluster_props_edit_ok)
    self.cluster_props_dlg = self.glade_xml.get_widget('cluster_props')
    self.clustername = self.glade_xml.get_widget('clustername')

    ##Node Fields
    #Node Props
    self.node_props_name = self.glade_xml.get_widget('entry23')
    self.node_props_votes = self.glade_xml.get_widget('entry24')

    ##Fence Panel
    self.fi_options = self.glade_xml.get_widget('fi_menu')
    self.fi_options.connect('changed',self.fi_optionmenu_change)

    self.glade_xml.get_widget('faildoms_add_b').connect('clicked',self.on_faildom_add)
    self.glade_xml.get_widget('faildom_edit_b').connect('clicked',self.on_faildom_edit)
    self.glade_xml.get_widget('faildom_delete_b').connect('clicked',self.on_faildom_delete)

    self.faildom_name = self.glade_xml.get_widget('faildom_name')
    self.add_faildom_dlg = self.glade_xml.get_widget('add_faildom_dlg')
    self.add_faildom_dlg.connect("delete_event", self.add_faildom_dlg_delete)
    self.glade_xml.get_widget('on_faildom_add_cancel').connect('clicked',self.on_faildom_add_cancel)
    self.glade_xml.get_widget('on_faildom_add_ok').connect('clicked',self.on_faildom_add_ok)



    #Fence Devices
    self.glade_xml.get_widget('fencedevices_add_b').connect('clicked',self.on_fd)
    self.glade_xml.get_widget('fencedevice_edit_b').connect('clicked',self.on_fd)
    self.glade_xml.get_widget('fencedevice_delete_b').connect('clicked',self.on_fd_delete)
    self.fd_panel = self.glade_xml.get_widget('fd_panel')
    self.fd_panel.connect("delete_event", self.fd_panel_delete)
    self.fd_options = self.glade_xml.get_widget('fd_options')
    self.fd_options.connect('changed',self.fd_optionmenu_change)
    self.prep_fd_options()
    self.fd_panel_label = self.glade_xml.get_widget('fd_panel_label')
    self.glade_xml.get_widget('cancelbutton12').connect('clicked',self.on_fd_panel_cancel)
    self.glade_xml.get_widget('okbutton12').connect('clicked',self.on_fd_panel_ok)

    self.fd_delete = self.glade_xml.get_widget('fd_delete')
    self.fd_delete.connect("delete_event",self.fd_delete_delete)
    self.fd_delete_warning1 = self.glade_xml.get_widget('fd_delete_warning1')
    self.fd_delete_warning2 = self.glade_xml.get_widget('fd_delete_warning2')
    self.fd_delete_treeview = self.glade_xml.get_widget('fd_delete_treeview')
    self.fd_delete_treemodel = gtk.ListStore (gobject.TYPE_STRING,
                                              gobject.TYPE_PYOBJECT,
                                              gobject.TYPE_STRING)

    self.fd_delete_treeview.set_model(self.fd_delete_treemodel)
    self.fd_delete_treeview.set_headers_visible(TRUE)
    self.fd_delete_treeview.get_selection().set_mode(gtk.SELECTION_NONE)
    self.fd_delete_treeview.get_selection().unselect_all()

    renderer0 = gtk.CellRendererText()
    column0 = gtk.TreeViewColumn(AFF_NODES,renderer0, text=0)
    self.fd_delete_treeview.append_column(column0)

    self.glade_xml.get_widget('okbutton15').connect('clicked',self.on_fd_delete_ok)
    self.glade_xml.get_widget('cancelbutton15').connect('clicked',self.on_fd_delete_cancel)

    self.rc_options = self.glade_xml.get_widget('rc_options')
    self.rc_options.connect('changed',self.rc_optionmenu_change)
    self.prep_rc_options()
    self.glade_xml.get_widget('resource_add_b').connect('clicked',self.on_rc)
    self.glade_xml.get_widget('resource_edit_b').connect('clicked',self.on_rc)
    self.glade_xml.get_widget('resource_delete_b').connect('clicked',self.on_rc_delete)


  def setupFencePanel(self):
    self.fence_treeview = self.glade_xml.get_widget('fencepanel_tree_view')
    self.fence_treemodel = gtk.TreeStore (gtk.gdk.Pixbuf,
                                          gobject.TYPE_STRING,
                                          gobject.TYPE_INT,
                                          gobject.TYPE_PYOBJECT)
    self.fence_treeview.set_model(self.fence_treemodel)
    self.fence_treeview.set_headers_visible(FALSE)

    selection = self.fence_treeview.get_selection()
    selection.connect('changed',self.on_fence_tree_changed)

    renderer0 = gtk.CellRendererPixbuf()
    column0 = gtk.TreeViewColumn("Node",renderer0, pixbuf=0)
    self.fence_treeview.append_column(column0)

    renderer = gtk.CellRendererText()
    column1 = gtk.TreeViewColumn("Fence Management",renderer,markup=1)
    self.fence_treeview.append_column(column1)

    self.fence_panel_close = self.glade_xml.get_widget('fence_panel_close')
    self.fence_panel_close.connect('clicked',self.on_fence_panel_close)

    self.fence_node_buttons = self.glade_xml.get_widget('fp_node_b_panel')
    self.fence_level_buttons = self.glade_xml.get_widget('fp_level_b_panel')
    self.fence_buttons = self.glade_xml.get_widget('fp_fence_b_panel')

    self.level_properties_panel = self.glade_xml.get_widget('level_props_panel')
    self.no_selection_panel = self.glade_xml.get_widget('none_selected_panel')
    self.level_props_label = self.glade_xml.get_widget('level_props_label')

    self.glade_xml.get_widget('button12').connect('clicked',self.on_create_level)
    self.glade_xml.get_widget('button13').connect('clicked',self.on_create_fi)
    self.glade_xml.get_widget('button14').connect('clicked', self.on_del_level)
    self.glade_xml.get_widget('button15').connect('clicked', self.on_edit_fi)
    self.glade_xml.get_widget('button16').connect('clicked', self.on_del_fi)
    
    self.fi_panel = self.glade_xml.get_widget('fi_panel')
    self.fi_panel.connect("delete_event",self.fi_panel_delete)
    self.fi_type_label = self.glade_xml.get_widget('fi_type_label')
    self.fi_panel_label = self.glade_xml.get_widget('fi_panel_label')
    self.glade_xml.get_widget('okbutton13').connect('clicked',self.on_fi_ok)
    self.glade_xml.get_widget('cancelbutton13').connect('clicked',self.on_fi_cancel)

   
  def on_cluster_props_edit(self, button):
    cptr = self.model_builder.getClusterPtr()
    name = cptr.getName()
    self.clustername.set_text(name)
    self.cluster_props_dlg.show()

  def on_cluster_props_edit_ok(self, button):
    cptr = self.model_builder.getClusterPtr()
    name = self.clustername.get_text()
    if name == "":
      self.errorMessage(NEED_CLUSTER_NAME)
      return
    cptr.addAttribute("name",name)
    apply(self.reset_tree_model)
    self.cluster_props_dlg.hide()


  def on_cluster_props_edit_cancel(self, button):
    self.clustername.set_text("")
    self.cluster_props_dlg.hide()
 
  def on_clusternode_fence_b(self, button):
    #This method works for either 'Fence this Node' button or 'Fence Panel'
    #First we need to get selection and find out which button is pushed
    #Then we need to build the tree for the fence panel.
    #Tree change listener will build fence props buttons
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    treetype = model.get_value(iter, TYPE_COL)
    if treetype == CLUSTER_NODE_TYPE:
      nd = model.get_value(iter, OBJ_COL)
    else:  #Must be a fence type
      parent_iter = model.iter_parent(iter)
      nd = model.get_value(parent_iter, OBJ_COL)
    
    self.prep_fence_panel(nd)
    self.fence_panel.show()
    self.fence_props_area.connect('expose-event',self.on_f_props_expose_event)
    self.fence_prop_renderer = PropertiesRenderer(self.fence_props_area,self.fence_props_area.window)
    self.fence_prop_renderer.clear_layout_area()
    #self.fence_panel.show()

  def prep_fence_panel(self, nd):
    level_index = 1
    treemodel = self.fence_treeview.get_model()
    treemodel.clear()

    node_iter = treemodel.append(None)
    node_str = "<span size=\"11000\"><b>" + nd.getName() + "</b></span>"
    treemodel.set(node_iter, FENCE_PIX_COL, self.node_pixbuf,
                             FENCE_NAME_COL, node_str,
                             FENCE_TYPE_COL, F_NODE_TYPE,
                             FENCE_OBJ_COL, nd)

    self.fence_panel_label.set_use_markup(TRUE)
    self.fence_panel_label.set_markup(FENCE_PANEL_LABEL % nd.getName())
    fence_placeholder = nd.getChildren()
    if len(fence_placeholder) == 0:
      fens = Fence()
      nd.addChild(fens)
    chilluns = fence_placeholder[0].getChildren()
    #chilluns holds a list of fence levels
    for chillun in chilluns:
      flevel_iter = treemodel.append(node_iter)
      flevel_substr = FENCE_LEVEL % level_index
      ##The next line mutates the incoming obj tree to issue sensible 
      ##level names
      chillun.addAttribute("name",str(level_index))
      level_index = level_index + 1
      flevel_str = "<span size=\"11000\"><b>" + flevel_substr + "</b></span>"
      treemodel.set(flevel_iter, FENCE_NAME_COL, flevel_str,
                                 FENCE_TYPE_COL, F_LEVEL_TYPE,
                                 FENCE_OBJ_COL, chillun )

      fences = chillun.getChildren()
      for fence in fences:
        fence_iter = treemodel.append(flevel_iter)
        fence_str = "<span size=\"11000\"><b>" + fence.getName() + "</b></span>"
        treemodel.set(fence_iter, FENCE_PIX_COL, self.fence_pixbuf,
                                  FENCE_NAME_COL, fence_str,
                                  FENCE_TYPE_COL, F_FENCE_TYPE,
                                  FENCE_OBJ_COL, fence)

    self.fence_treeview.expand_all()


  def on_fence_panel_close(self, button):
    self.fence_panel.hide()

  def on_fence_tree_changed(self, *args):
    selection = self.fence_treeview.get_selection()
    model,iter = selection.get_selected()
    if iter == None:
      return
    selected_type = model.get_value(iter, FENCE_TYPE_COL)
    obj = model.get_value(iter, FENCE_OBJ_COL)
    if selected_type == F_NODE_TYPE:
      self.clear_fence_buttonpanels()
      self.clear_fencepanel_widgets()
      self.fence_node_buttons.show()
    elif selected_type == F_LEVEL_TYPE:
      self.clear_fence_buttonpanels()
      self.clear_fencepanel_widgets()
      self.fence_prop_renderer.render_to_layout_area(obj.getProperties(), obj.getName(), selected_type)
      self.fence_level_buttons.show()
    else:
      self.clear_fence_buttonpanels()
      self.clear_fencepanel_widgets()
      self.fence_prop_renderer.render_to_layout_area(obj.getProperties(), obj.getName(), selected_type)
      #self.refresh_fi_panel()
      self.fence_buttons.show()

  def clear_fence_buttonpanels(self):
    self.fence_node_buttons.hide()
    self.fence_level_buttons.hide()
    self.fence_buttons.hide()

  def clear_fencepanel_widgets(self):
    self.fi_panel.hide()

  def on_create_fi(self, button):
    self.prep_fi_options()
    self.fi_options.set_history(0)
    ########Call change listener here
    self.fi_optionmenu_change(None)
    self.fi_panel_label.set_text(ADD_FENCE)
    self.fence_handler.clear_fi_forms()
    self.fi_options.show()
    self.fi_panel.show()

  def on_edit_fi(self, button):
    #1-find fence instance to edit 2-populate form 3-display 
    selection = self.fence_treeview.get_selection()
    model,iter = selection.get_selected()
    fi_obj = model.get_value(iter, FENCE_OBJ_COL)
    attrs = fi_obj.getAttributes()
    agent_type = fi_obj.getAgentType()
    self.fence_handler.clear_fi_forms()
    self.fi_options.hide()
    namehasher = self.fence_handler.getFENCE_OPTS()
    self.fi_type_label.set_text(FI_TYPE % namehasher[agent_type])
    self.fi_panel_label.set_text(EDIT_FENCE % fi_obj.getName())
    fences = self.fenceinstance_form_hash.keys()
    for fence in fences: #hide all forms
      self.fenceinstance_form_hash[fence].hide()
    self.fence_handler.populate_fi_form(agent_type, attrs)
    self.fenceinstance_form_hash[agent_type].show()
    self.fi_panel.show()

  def on_fi_ok(self, button):
    selection = self.fence_treeview.get_selection()
    model,iter = selection.get_selected()
    root_iter = model.get_iter_root()
    nd = model.get_value(root_iter, FENCE_OBJ_COL)
    type = model.get_value(iter,FENCE_TYPE_COL)
    if type == F_LEVEL_TYPE:  #this is a new fi...
      level_obj = model.get_value(iter,FENCE_OBJ_COL)
      #get agent type from options menu
      idx = self.fi_options.get_history()
      name = self.fi_optionmenu_hash[idx]
      agent_type = self.fi_agent_hash[name]
      attrlist = self.fence_handler.validate_fenceinstance(agent_type)
      if attrlist != None:
        f_obj = Device()
        f_obj.addAttribute("name",name)
        f_obj.setAgentType(agent_type)
        kees = attrlist.keys()
        for k in kees:
          f_obj.addAttribute(k,attrlist[k])
        level_obj.addChild(f_obj)
        self.prep_fence_panel(nd)
        self.fi_panel.hide()

    else:  #We were just editing props
      f_obj = model.get_value(iter, FENCE_OBJ_COL)
      agent_type = f_obj.getAgentType()
      attrlist = self.fence_handler.validate_fenceinstance(agent_type)
      if attrlist != None:
        kees = attrlist.keys()
        for k in kees:
          f_obj.addAttribute(k,attrlist[k])
        self.prep_fence_panel(nd)
        self.fi_panel.hide()
 

    #self.fi_panel.hide()

  def on_create_level(self, button):
    selection = self.fence_treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, FENCE_OBJ_COL) #node
    fence_ptr = obj.getChildren()[0]
    #find out how many levels
    kin = fence_ptr.getChildren()
    num_kin = len(kin)
    if num_kin > 0:
      attr_val = num_kin + 1
    else:
      attr_val = 1
    method = Method()
    method.addAttribute("name",str(attr_val))
    fence_ptr.addChild(method)
    self.prep_fence_panel(obj)

  def on_del_level(self, button):
    selection = self.fence_treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, FENCE_OBJ_COL)
    if len(obj.getChildren()) == 0:
      msg = CONFIRM_LEVEL_REMOVE_EMPTY
    else:
      msg = CONFIRM_LEVEL_REMOVE

    retval = self.warningMessage(msg)
    if (retval == gtk.RESPONSE_NO):
      return

    root_iter = model.get_iter_root()
    nd = model.get_value(root_iter, FENCE_OBJ_COL)
    fence_ptr = nd.getChildren()[0]
    fence_ptr.removeChild(obj)
    self.prep_fence_panel(nd)

  def on_del_fi(self, button):
    retval = self.warningMessage(CONFIRM_FI_REMOVE)
    if (retval == gtk.RESPONSE_NO):
      return
    selection = self.fence_treeview.get_selection()
    model,iter = selection.get_selected()
    root_iter = model.get_iter_root()
    nd = model.get_value(root_iter, FENCE_OBJ_COL)
    obj = model.get_value(iter, FENCE_OBJ_COL)
    parent_iter = model.iter_parent(iter)
    parent_obj = model.get_value(parent_iter,FENCE_OBJ_COL)
    parent_obj.removeChild(obj)
    self.prep_fence_panel(nd)
    


  def prep_fi_options(self):
    fds = self.model_builder.getFenceDevices()
    self.fi_optionmenu_hash.clear()
    self.fi_agent_hash.clear()
    self.fi_prettyname_hash.clear()
   
    menu = gtk.Menu() 
    #make two hashes here - one for idx -> agent and one for 
    pretty_name_hash = self.fence_handler.getFENCE_OPTS()
    ks = pretty_name_hash.keys()
    ks.sort()
    counter = 0
    for fd in fds:
      self.fi_optionmenu_hash[counter] = fd.getName()
      self.fi_agent_hash[fd.getName()] = fd.getAgentType()
      self.fi_prettyname_hash[counter] = pretty_name_hash[fd.getAgentType()]
      m = gtk.MenuItem(fd.getName())
      counter = counter + 1
      m.show()
      menu.append(m)

    self.fi_options.set_menu(menu) 

  def refresh_fi_panel(self, editmode=TRUE):
    #1) Load option menu by getting list of current fence devices and
    #   building menu's by setting menu labels to 
    #   <Generic Fence Name> + (name used in fence device table)
    #   and store menu indexes in hash table
    self.load_fence_agent_optionmenu()

    #2) identify fence to edit from tree selection
    selection = self.fence_treeview.get_selection()
    model,iter = selection.get_selected()
    fence_obj = model.get_value(iter, FENCE_OBJ_COL)
    attrs = fence_obj.getAttributes()
    #3) get its agent name 
    agent_type = fence_obj.getAgentType()
    #3A) Set optionmenu to agent name
    self.fi_optionmenu.set_history(self.fi_optionmenu_hash_rev[agent_type])
    #3B) Set fence instance panel label with proper name params
    #4) get fence object, its attr list, and pass into fence handler
    #   with agent name, and it will set field values
    self.fence_handler.populate_fi_form(agent_type, attrs)
    #5) use fence instance hash to turn on proper form
    #6) turn on 'edit/cancel' buttonrow and turn off other
    if editmode:
      self.fi_edit_row.show()
      self.fi_create_row.hide()
    else:
      self.fi_edit_row.hide()
      self.fi_create_row.show()
    
    #

  def load_fence_agent_optionmenu(self):
    fds = self.model_builder.getFenceDevices()
    self.fi_optionmenu_hash.clear()
    self.fi_optionmenu_hash_rev.clear()
    counter = 0
    menu = gtk.Menu()
    for fd in fds:
      agent_type = fd.getAgentType()
      menu_str = self.fence_handler.pretty_agentname_hash[agent_type] + " \"" + fd.getName() + "\""
      m = gtk.MenuItem(menu_str)
      self.fi_optionmenu_hash[counter] = agent_type
      self.fi_optionmenu_hash_rev[agent_type] = counter
      counter = counter + 1
      m.show()
      menu.append(m)

    self.fi_optionmenu.set_menu(menu)

  def fi_optionmenu_change(self, widget):
    fi_idx = self.fi_options.get_history()
    agent_type = self.fi_agent_hash[self.fi_optionmenu_hash[fi_idx]]
    fences = self.fenceinstance_form_hash.keys()
    self.fi_type_label.set_text(FI_TYPE % self.fi_prettyname_hash[fi_idx])
    for fence in fences: #hide all forms
      self.fenceinstance_form_hash[fence].hide()
    self.fenceinstance_form_hash[agent_type].show()

  def on_fi_cancel(self, button):
    self.fi_panel.hide()
      
      
  def fd_optionmenu_change(self, widget):
    fd_idx = self.fd_options.get_history()
    agent_type = self.fd_optionmenu_hash[fd_idx]
    fences = self.fencedevice_form_hash.keys()
    for fence in fences: #hide all forms
      self.fencedevice_form_hash[fence].hide()
    self.fencedevice_form_hash[agent_type].show()
      

  def on_clusternode_add_b(self, button):
    self.node_props_flag = NODE_NEW
    self.node_props_name.set_text("")
    self.node_props_votes.set_text("")
    self.node_props.show()
   
  def on_node_props_ok(self, button):
    #Get attrs
    #check votes between 0 <-> 255
    votesattr = self.node_props_votes.get_text()
    if votesattr == "":
      votesattr = "1"

    if votesattr.isdigit() == FALSE:
      self.errorMessage(VOTES_ONLY_DIGITS)
      self.node_props_votes.set_text("")
      return

    #New Node: get selection...get list nodes...check for unique name
    #existing node: check for diff between current name - if so, get list 
    #and check for unique
    nameattr = self.node_props_name.get_text()
    if nameattr == "":
      self.errorMessage(NODE_NAME_REQUIRED)
      self.node_props_name.set_text("")
      return

    if self.node_props_flag == NODE_NEW:
      nds = self.model_builder.getNodes()
      for n in nds:
        if n.getName() == nameattr:
          self.errorMessage(NODE_UNIQUE_NAME)
          self.node_props_name.set_text("")
          return 

      cn = ClusterNode()
      cn.addAttribute(NAME_ATTR,nameattr)
      cn.addAttribute(VOTES_ATTR,votesattr)
      self.model_builder.addNode(cn)
    else:
      selection = self.treeview.get_selection()
      model,iter = selection.get_selected()
      nd = model.get_value(iter, OBJ_COL)
      ndname = nd.getName()
      if (ndname != nameattr): #indicates user changed name string
        nds = self.model_builder.getNodes()
        for n in nds:
          if n.getName() == nameattr:
            self.errorMessage(NODE_UNIQUE_NAME)
            self.node_props_name.set_text("ndname")
            return 
        nd.addAttribute(NAME_ATTR,nameattr)
      nd.addAttribute(VOTES_ATTR,votesattr) 
    apply(self.reset_tree_model)

      
    self.node_props_flag = NODE_NEW
    self.node_props.hide() 

  def on_node_props_cancel(self, button):
    self.node_props_flag = NODE_NEW
    self.node_props.hide() 

  def on_clusternode_edit_b(self, button):
    self.node_props_flag = NODE_EXISTING
    self.prep_clusternode_edit_dialog(NODE_EXISTING)
    self.node_props.show()

  def on_clusternode_delete_b(self, button):
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    nd = model.get_value(iter,OBJ_COL)

    retval = self.warningMessage(CONFIRM_NODE_REMOVE % nd.getName())
    if (retval == gtk.RESPONSE_NO):
      return

    self.model_builder.deleteNode(nd)
    self.node_props_flag = NODE_NEW
    apply(self.reset_tree_model)

  def prep_clusternode_edit_dialog(self, status):
    if status == NODE_NEW:
      self.node_props_name.set_text("")
      self.node_props_votes.set_text("")
    else:
      selection = self.treeview.get_selection()
      model,iter = selection.get_selected()
      nd = model.get_value(iter, OBJ_COL)
      attrs = nd.getAttributes()
      try:
        self.node_props_name.set_text(attrs[NAME_ATTR]) 
        self.node_props_votes.set_text(attrs[VOTES_ATTR]) 
      except KeyError, e:
        print " Error looking up key in Nodes attr hash"

    self.node_props.show()

  def on_fd(self, button):
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    #first, see if this will be a new device, or an edit
    type = model.get_value(iter, TYPE_COL)
    if type == FENCE_DEVICES_TYPE:
      self.fence_handler.clear_fd_forms()
      self.fd_panel_label.set_text(ADD_FENCE_DEVICE)
      #set optionmenu to zero index
      self.fd_options.set_history(0)
      self.fd_optionmenu_change(None)
      self.fd_options.show()
      fences = self.fencedevice_form_hash.keys()
      #for fence in fences: #hide all forms
      #  self.fencedevice_form_hash[fence].hide()
      self.fd_panel.show()
    else:
      fd_obj = model.get_value(iter,OBJ_COL)
      attrs = fd_obj.getAttributes()
      agent_type = fd_obj.getAgentType()
      self.fence_handler.clear_fd_forms()
      #hide optionmenu for fence devices
      self.fd_options.hide()
      self.fd_panel_label.set_text(EDIT_FENCE_DEVICE)
      fences = self.fencedevice_form_hash.keys()
      for fence in fences: #hide all forms
        self.fencedevice_form_hash[fence].hide()
      self.fencedevice_form_hash[agent_type].show()
      self.fence_handler.populate_fd_form(agent_type, attrs)
      self.fencedevice_form_hash[agent_type].show()
      self.fd_panel.show()

  def on_fd_delete(self, button):
    ref_hash = {}
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, OBJ_COL)
    fd_name = obj.getName().strip()
    nodes = self.model_builder.getNodes()
    for node in nodes:
      flevels = node.getFenceLevels()
      for flevel in flevels:
        kids = flevel.getChildren() # list of fences per level
        for kid in kids:
          if kid.getName().strip() == fd_name:
            ref_hash[node] = 0  #Just making a keys list w/o dupes

    #ref_hash.keys() now holds list of node objs that have fence
    #instances (one or more) that refer to the fd to be deleted
    kees = ref_hash.keys()
    num_kees = len(kees)
    if num_kees == 0:  #simple warning...
      retval = self.warningMessage(CONFIRM_FD_DELETE % fd_name)
      if (retval == gtk.RESPONSE_NO):
        return
      fd_ptr = self.model_builder.getFenceDevicePtr()
      fd_ptr.removeChild(obj)
      apply(self.reset_tree_model)
      return
    else:
      treemodel = self.fd_delete_treeview.get_model()
      treemodel.clear()

      for kee in kees:
        new_iter = treemodel.append()
        treemodel.set(new_iter, 0, kee.getName(),
                                1, kee,
                                2, fd_name)

      self.fd_delete_treeview.get_selection().unselect_all()

      if num_kees == 1:
        self.fd_delete_warning1.set_text(WARNING1 % fd_name)
        self.fd_delete_warning2.set_text(WARNING2)
      else:
        self.fd_delete_warning1.set_text(WARNINGS1 % fd_name)
        self.fd_delete_warning2.set_text(WARNINGS2)

      self.fd_delete.show()

  def on_fd_delete_ok(self, button):
    selection = self.treeview.get_selection()
    outer_model,outer_iter = selection.get_selected()
    obj = outer_model.get_value(outer_iter, OBJ_COL)
    fd_ptr = self.model_builder.getFenceDevicePtr()
    fd_ptr.removeChild(obj)
    model = self.fd_delete_treeview.get_model()
    model.foreach(self.remove_fence_from_node, None)
    self.fd_delete.hide()
    apply(self.reset_tree_model)

  def remove_fence_from_node(self, model,path,iter, *args):
    node = model.get_value(iter, 1)
    fd_name = model.get_value(iter, 2)
    got_one = 1
    while got_one > 0:
      got_one = 0
      flevels = node.getFenceLevels()
      for flevel in flevels:
        kids = flevel.getChildren()
        for kid in kids:
          if kid.getName().strip() == fd_name.strip():
            flevel.removeChild(kid)
            got_one = 1
      
  def on_fd_delete_cancel(self, button):
    self.fd_delete.hide()
      

  def on_fd_panel_cancel(self, button):
    self.fd_panel.hide()
    self.fence_handler.clear_fd_forms()
    fences = self.fencedevice_form_hash.keys()
    for fence in fences: #hide all forms
      self.fencedevice_form_hash[fence].hide()

  def on_fd_panel_ok(self, button):
    #first, find out if this is for edited props, or a new device 
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    type = model.get_value(iter, TYPE_COL)
    if type == FENCE_DEVICE_TYPE:  #edit
      f_obj = model.get_value(iter, OBJ_COL)
      agent_type = f_obj.getAgentType()
      returnlist = self.fence_handler.validate_fencedevice(agent_type, f_obj.getName())
      if returnlist != None:
        self.fd_panel.hide()
        for k in returnlist.keys():
          f_obj.addAttribute(k, returnlist[k])
          ##Reset TRee
        apply(self.reset_tree_model)

    else: #new device
      fd_obj = FenceDevice()
      fd_idx = self.fd_options.get_history()
      agent_type = self.fd_optionmenu_hash[fd_idx]
      return_list = self.fence_handler.validate_fencedevice(agent_type, None)
      if return_list != None:
        self.fd_panel.hide()
        for x in return_list.keys():
          fd_obj.addAttribute(x, return_list[x])
        fd_obj.addAttribute("agent", agent_type)
        ptr = self.model_builder.getFenceDevicePtr()
        ptr.addChild(fd_obj)
        apply(self.reset_tree_model)

  def prep_fd_options(self):
   
    menu = gtk.Menu() 
    #make two hashes here - one for idx -> agent and one for 
    pretty_name_hash = self.fence_handler.getFENCE_OPTS()
    self.fd_optionmenu_hash.clear()
    ks = pretty_name_hash.keys()
    ks.sort()
    counter = 0
    for k in ks:
      self.fd_optionmenu_hash[counter] = k
      m = gtk.MenuItem(pretty_name_hash[k])
      counter = counter + 1
      m.show()
      menu.append(m)

    self.fd_options.set_menu(menu) 

  def on_faildom_add(self, button):
    #launch dialog for faildom name field
    self.faildom_name.set_text("")
    self.add_faildom_dlg.show()

  def on_faildom_add_ok(self, button):
    fdoms = self.model_builder.getFailoverDomains()
    faildom_name = self.faildom_name.get_text().strip()
    if faildom_name == "":
      self.errorMessage(FAILDOM_NAME_REQUIRED)
      return
    for fdom in fdoms:
      if fdom.getName().strip() == faildom_name:
        self.faildom_name.select_region(0, (-1))
        self.errorMessage(UNIQUE_FAILDOM_NAME % faildom_name)
        return

    #Made it past unique name check -- ready to add faildom
    failover_domain = FailoverDomain()
    failover_domain.addAttribute("name",faildom_name)
    fdom_ptr = self.model_builder.getFailoverDomainPtr()
    fdom_ptr.addChild(failover_domain)
    self.add_faildom_dlg.hide()
    self.faildom_name.set_text("")
    self.faildom_controller.prep_faildom_panel(failover_domain)
    self.faildom_panel.show()

  def on_faildom_add_cancel(self, button):
    self.add_faildom_dlg.hide()

  def on_faildom_edit(self, button):
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, OBJ_COL)
    self.faildom_controller.prep_faildom_panel(obj)
    self.faildom_panel.show()

  def on_faildom_delete(self, button):
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, OBJ_COL)
    retval = self.warningMessage(CONFIRM_FAILDOM_REMOVE % obj.getName())
    if (retval == gtk.RESPONSE_NO):
      return
    ###XXX-FIX should be wrapped in exception handler
    faildoms_ptr = self.model_builder.getFailoverDomainPtr()
    faildoms_ptr.removeChild(obj)
    apply(self.reset_tree_model)

  def rc_optionmenu_change(self, widget):
    rc_idx = self.rc_options.get_history()
    tagname = self.rc_optionmenu_hash[rc_idx]
    ###
    rcs = self.rc_form_hash.keys()
    for rc in rcs: #hide all forms
      self.rc_form_hash[rc].hide()
    self.rc_form_hash[tagname].show()
    ### 

  def prep_rc_options(self):
    menu = gtk.Menu()
    self.rc_optionmenu_hash.clear()
    ks = self.rc_prettyname_hash.keys()
    ks.sort()
    counter = 0
    for k in ks:
      self.rc_optionmenu_hash[counter] = k
      m = gtk.MenuItem(self.rc_prettyname_hash[k])
      counter = counter + 1
      m.show()
      menu.append(m)

    self.rc_options.set_menu(menu)

  def on_rc(self, button):
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    #see if this will be a new resource, or an edit
    type = model.get_value(iter, TYPE_COL)
    if type == RESOURCES_TYPE: #new resource
      self.rc_handler.clear_rc_forms()
      self.rc_options.set_history(0)
      self.rc_options.show()
      self.rc_dlg_label.set_markup(SELECT_RC_TYPE)
      self.rc_panel.show()
    else:
      self.rc_options.hide()
      rc_obj = model.get_value(iter, OBJ_COL)
      attrs = rc_obj.getAttributes()
      tagname = rc_obj.getTagName()
      self.rc_dlg_label.set_markup(RC_PROPS % (self.rc_prettyname_hash[tagname],rc_obj.getName()))
      self.rc_handler.clear_rc_forms()
      rcs = self.rc_form_hash.keys()
      for rc in rcs:
        self.rc_form_hash[rc].hide()
      self.rc_handler.populate_rc_form(tagname, attrs)
      self.rc_form_hash[tagname].show()
      self.rc_panel.show()

  def on_rc_delete(self, button):
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, OBJ_COL)
    retval = self.warningMessage(CONFIRM_RC_REMOVE % obj.getName())
    if (retval == gtk.RESPONSE_NO):
      return
    rc_ptr = self.model_builder.getResourcesPtr()
    rc_ptr.removeChild(obj)
    apply(self.reset_tree_model)

  def on_f_props_expose_event(self, widget, event):
     self.fence_prop_renderer.do_render()

  def set_model(self, model_builder,treeview):
    self.model_builder = model_builder
    self.treeview = treeview
    self.faildom_controller.set_model(self.model_builder)
    self.fence_handler.set_model(self.model_builder)
    self.rc_handler.set_model(self.model_builder)

  def warningMessage(self, message):
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO,
                            message)
    dlg.show_all()
    rc = dlg.run()
    dlg.destroy()
    if (rc == gtk.RESPONSE_NO):
      return gtk.RESPONSE_NO
    if (rc == gtk.RESPONSE_DELETE_EVENT):
      return gtk.RESPONSE_NO
    if (rc == gtk.RESPONSE_CLOSE):
      return gtk.RESPONSE_NO
    if (rc == gtk.RESPONSE_CANCEL):
      return gtk.RESPONSE_NO
                                                                                
    return rc
                                                                                
  def errorMessage(self, message):
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                            message)
    dlg.show_all()
    rc = dlg.run()
    dlg.destroy()
    return rc
                                                                                
  def infoMessage(self, message):
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO,
                            message)
    dlg.show_all()
    rc = dlg.run()
    dlg.destroy()
    return rc
                                                                                
  def node_props_delete(self, *args):
    self.node_props.hide()
    return gtk.TRUE

  def fence_panel_delete(self, *args):
    self.fence_panel.hide()
    return gtk.TRUE

  def fd_panel_delete(self, *args):
    self.fd_panel.hide()
    return gtk.TRUE

  def fi_panel_delete(self, *args):
    self.fi_panel.hide()
    return gtk.TRUE

  def faildom_panel_delete(self, *args):
    self.faildom_panel.hide()
    return gtk.TRUE

  def add_faildom_dlg_delete(self, *args):
    self.add_faildom_dlg.hide()
    return gtk.TRUE

  def rc_panel_delete(self, *args):
    self.rc_panel.hide()
    return gtk.TRUE

  def fd_delete_delete(self, *args):
    self.fd_delete.hide()
    return gtk.TRUE


"""This class represents the primary controller interface
   for the cluster management tab.
"""
__author__ = 'Jim Parsons (jparsons@redhat.com)'
                                                                                
                                                                                
import string
import os
import gobject
import cgi

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
from FenceXVMd import FenceXVMd
from FaildomController import FaildomController
from ServiceController import ServiceController
from Service import Service
from FailoverDomain import FailoverDomain
from Device import Device
from Method import Method
from Vm import Vm
from Fence import Fence
from Lockserver import Lockserver
from ResourceHandler import ResourceHandler
from PropertiesRenderer import PropertiesRenderer
from Multicast import Multicast
import MessageLibrary

PIXMAP_DIR = "/usr/share/system-config-cluster/pixmaps/"
INSTALLDIR = "/usr/share/system-config-cluster/"

 
FENCE_PIX_COL=0
FENCE_NAME_COL=1
FENCE_TYPE_COL=2
FENCE_OBJ_COL=3

NODE_NEW = 0
NODE_EXISTING = 1
NFSCLIENT_TAG="nfsclient"

FI_TYPE=_("Fence Device Type: \n %s")

AFF_NODES=_("Affected Cluster Nodes")

FD_DELETION_WARNING=_("Fence Device Deletion Warning")
AFFECTED_CLUSTER_NODES=_("Affected Cluster Nodes")
WARNING1=_("The following Cluster Node depends on Fence Device %s.")
WARNINGS1=_("The following Cluster Nodes depend on Fence Device %s.")
WARNING2=_("Removing this Fence Device will alter Fencing on this Cluster Node.\n Are you certain that you wish to continue?")
WARNINGS2=_("Removing this Fence Device will alter Fencing on these Cluster Nodes.\n Are you certain that you wish to continue?")

FAILDOM_DELETION_WARNING=_("Failover Domain Deletion Warning")
AFFECTED_SERVICES=_("Affected Services")
WARNING3=_("The following Service depends on Failover Domain %s.")
WARNINGS3=_("The following Services depend on Failover Domain %s.")
WARNING4=_("Removing this Failover Domain will alter this Service.\n Are you certain that you wish to continue?")
WARNINGS4=_("Removing this Failover Domain will alter these Services.\n Are you certain that you wish to continue?")

RESOURCE_DELETION_WARNING=_("Resource Deletion Warning")
#AFFECTED_SERVICES=_("Affected Services")
WARNING5=_("The following Service depends on Resource %s.")
WARNINGS5=_("The following Services depend on Resource %s.")
WARNING6=_("Removing this Resource will alter this Service.\n Are you certain that you wish to continue?")
WARNINGS6=_("Removing this Resource will alter these Services.\n Are you certain that you wish to continue?")

ADD_FENCE_DEVICE=_("Add a New Fence Device")

EDIT_FENCE_DEVICE=_("Edit Properties for this Fence Device")

CONFIRM_FD_DELETE=_("Are you certain that you wish to delete Fence Device %s?")

ADD_FENCE=_("Add a New Fence")

UNABLE_LOCATE_VM=_("The Virtual Server to be edited, %s, can not be located")

EDIT_FENCE=_("Edit Properties for Fence: %s")

SELECT_LEVEL_FOR_FENCE=_("Please select a fence level for the new fence first.")

FENCE_PANEL_LABEL=_("<span size=\"11000\">Fence Configuration for Cluster Node: <b> %s</b></span>")

NEED_CLUSTER_NAME=_("Please provide a name for the cluster")

NODE_UNIQUE_NAME=_("Names for Cluster Nodes must be Unique. Please choose another name for this Node.")

NODE_NAME_EQUAL_TO_FD_NAME = _("There is a Fence Device named \"%s\". Cluster Nodes cannot have the same names as Fence Devices. Please choose another name for this Node.")

NODE_NAME_REQUIRED=_("Please provide a name for this Cluster Node.")

NODE_NAME_LENGTH_EXCEEDED=_("Node names may not exceed 64 characters. Please reduce the length of this node name")

NODE_NAME_WHITESPACE=_("Node names may not contain whitespace. Please remove whitespace from chosen name")

FAILDOM_NAME_REQUIRED=_("Please provide a name for the new Failover Domain")

UNIQUE_FAILDOM_NAME=_("Failover Domains must have unique names. The name %s is already in use. Please provide a unique name.")

VOTES_ONLY_DIGITS=_("Valid values for the votes field are integer values between zero and 255, or nothing, which defaults to 1.")

CONFIRM_NODE_REMOVE=_("Are you sure you wish to remove node %s? This node, along with its fence instances and membership in failover domains will be removed.")

CONFIRM_FAILDOM_REMOVE=_("Are you certain that you wish to remove Failover Domain %s ?")

CONFIRM_RC_REMOVE=_("Are you certain that you wish to remove resource %s ?")

CONFIRM_SVC_REMOVE=_("Are you certain that you wish to remove service %s ?")

CONFIRM_VM_REMOVE=_("Are you certain that you wish to remove virtual service %s ?")

VM_NAME_REQUIRED=_("Please provide a name for this virtual service.")

VM_PATH_REQUIRED=_("Please provide a path to the config file for this virtual service.")

SERVICE_NAME_REQUIRED=_("Please provide a name for this service.")

UNIQUE_SERVICE_NAME=_("Services must have unique names. The name %s is already in use. Please provide a unique name.")

CONFIRM_LEVEL_REMOVE=_("Are you certain that you wish to remove this fence level and all fences contained within it?")

CONFIRM_LEVEL_REMOVE_EMPTY=_("Are you certain that you wish to remove this fence level?")

CONFIRM_FI_REMOVE=_("Are you certain that you wish to remove this fence?")

NEED_CONFIG_VERSION=_("Please provide a Config Version")

CONFIG_VERSION_DIGITS=_("Config Version field must contain numeric digits only.")

CONFIG_VERSION_DIGITS_MAX=_("Config Version field is limited to values from 1 to 9999")

###TRANSLATOR: The string below is used as an attr value in an XML file, as well
###as a GUI string. Please do not use whitespace in this string. 
FENCE_LEVEL=_("Fence-Level-%d")

NEED_VALID_POSTJOIN=_("Post-Join Delay should be an integer value representing seconds. Leave this field blank to use the default value of three seconds.")

NEED_VALID_POSTFAIL=_("Post-Fail Delay should be an integer value representing seconds. Leave this field blank to use the default value of zero seconds.")

from ClusterNode import ClusterNode

class ConfigTabController:
  def __init__(self,model_builder, treeview, glade_xml,reset_tree_model):
    self.model_builder = model_builder
    self.treeview = treeview
    self.glade_xml = glade_xml
    self.reset_tree_model = reset_tree_model

    self.faildom_controller = FaildomController(self.glade_xml,self.model_builder,reset_tree_model)
    self.service_controller = ServiceController(self.glade_xml,self.model_builder,reset_tree_model)

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
    self.glade_xml.get_widget('okbutton14').connect('clicked', self.rc_panel_ok)
    self.glade_xml.get_widget('cancelbutton14').connect('clicked', self.rc_panel_cancel)


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
    self.gulm_lockserver = self.glade_xml.get_widget('gulm_lockserver')

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
    self.cluster_props_dlg.connect("delete_event", self.cluster_props_dlg_delete)
    self.clustername = self.glade_xml.get_widget('clustername')
    self.actualclustername = self.glade_xml.get_widget('actualclustername')
    self.config_version = self.glade_xml.get_widget('config_version')
    self.post_join = self.glade_xml.get_widget('post_join')
    self.post_fail = self.glade_xml.get_widget('post_fail')
    self.mcast_interface = self.glade_xml.get_widget('mcast_interface')
    self.mcast_interface_entry = self.glade_xml.get_widget('mcast_interface_entry')
    self.xvmd_cbox = self.glade_xml.get_widget('xvmd_cbox')

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

    #Services and Service button panels
    self.svc_add_dlg = self.glade_xml.get_widget('svc_add_dlg')
    self.svc_add_dlg.connect('delete_event',self.on_svc_add_delete)
    self.glade_xml.get_widget('okbutton18').connect("clicked",self.on_svc_add_ok)
    self.glade_xml.get_widget('cancelbutton18').connect("clicked",self.on_svc_add_cancel)
    self.svc_name = self.glade_xml.get_widget('svc_name')
    self.svc_mgmt = self.glade_xml.get_widget('service_manager')
    self.svc_mgmt.connect('delete_event',self.on_svc_mgmt_delete)
    self.glade_xml.get_widget('button21').connect('clicked',self.on_svc_edit_close)
    self.svc_treeview = self.glade_xml.get_widget('svc_treeview')
    self.glade_xml.get_widget('service_add_b').connect('clicked',self.on_svc_add)
    self.glade_xml.get_widget('service_edit_b').connect('clicked',self.on_svc_edit)
    self.glade_xml.get_widget('service_delete_b').connect('clicked',self.on_svc_del)


    #VMs and Virtual Services button panels
    self.vm_props_dlg = self.glade_xml.get_widget('vm_props_dlg')
    self.vm_props_dlg.connect('delete_event',self.on_vm_props_delete)
    self.glade_xml.get_widget('okbutton21').connect("clicked",self.on_vm_props_ok)
    self.glade_xml.get_widget('cancelbutton21').connect("clicked",self.on_vm_props_cancel)
    self.vm_name = self.glade_xml.get_widget('vm_name')
    self.vm_name_label = self.glade_xml.get_widget('vm_name_l')
    self.vm_path = self.glade_xml.get_widget('vm_path')
    self.glade_xml.get_widget('vm_add_b').connect('clicked',self.on_vm_add)
    self.glade_xml.get_widget('vm_edit_b').connect('clicked',self.on_vm_edit)
    self.glade_xml.get_widget('vm_delete_b').connect('clicked',self.on_vm_del)


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
    self.fd_delete_warning1 = self.glade_xml.get_widget('fd_delete_warning1')
    self.fd_delete_warning2 = self.glade_xml.get_widget('fd_delete_warning2')
    self.fd_delete_treeview = self.glade_xml.get_widget('fd_delete_treeview')
    self.fd_delete_treemodel = gtk.ListStore (gobject.TYPE_STRING,
                                              gobject.TYPE_PYOBJECT,
                                              gobject.TYPE_STRING)

    self.fd_delete_treeview.set_model(self.fd_delete_treemodel)
    self.fd_delete_treeview.set_headers_visible(True)
    self.fd_delete_treeview.get_selection().set_mode(gtk.SELECTION_NONE)
    self.fd_delete_treeview.get_selection().unselect_all()

    renderer0 = gtk.CellRendererText()
    column0 = gtk.TreeViewColumn(AFF_NODES,renderer0, text=0)
    self.fd_delete_treeview.append_column(column0)
    
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
    self.fence_treeview.set_headers_visible(False)

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
    fptr = self.model_builder.getFenceDaemonPtr()
    xptr = self.model_builder.getFenceXVMdPtr()

    #set fields for edit
    name = cptr.getNameAlias()
    actualname = cptr.getName()
    self.clustername.set_text(name)
    self.actualclustername.set_text(actualname)
    self.config_version.set_text(cptr.getConfigVersion())

    #set fence daemon fields
    self.post_join.set_text(fptr.getPostJoinDelay())
    self.post_fail.set_text(fptr.getPostFailDelay())
    if xptr == None:
      self.xvmd_cbox.set_active(False)
    else:
      self.xvmd_cbox.set_active(True)
    self.cluster_props_dlg.show()

  def on_cluster_props_edit_ok(self, button):
    cptr = self.model_builder.getClusterPtr()
    fdptr = self.model_builder.getFenceDaemonPtr()
    name = self.clustername.get_text()
    version = self.config_version.get_text()
    postjoin = self.post_join.get_text()
    postfail = self.post_fail.get_text()

    if name == "":
      self.errorMessage(NEED_CLUSTER_NAME)
      return

    if version == "":
      self.errorMessage(NEED_CONFIG_VERSION)
      self.config_version.set_text(cptr.getConfigVersion())
      self.config_version.select_region(0, -1)
      return

    if version.isdigit() == False: 
      self.errorMessage(CONFIG_VERSION_DIGITS)
      self.config_version.set_text(cptr.getConfigVersion())
      self.config_version.select_region(0, -1)
      return

    x = int(version)
    if (x >= 10000) or (x < 0):
      self.errorMessage(CONFIG_VERSION_DIGITS_MAX)
      self.config_version.set_text(cptr.getConfigVersion())
      self.config_version.select_region(0, -1)
      return


    if postjoin.startswith("-") == True:
      postjoinstr = postjoin[1:]
    else:
      postjoinstr = postjoin
    if postjoinstr.isdigit() == False:
      if postjoin.strip() != "":
        self.errorMessage(NEED_VALID_POSTJOIN)
        self.post_join.select_region(0, -1)
        return

    if postfail.startswith("-") == True:
      postfailstr = postfail[1:]
    else:
      postfailstr = postfail
    if postfailstr.isdigit() == False:
      if postfail.strip() != "":
        self.errorMessage(NEED_VALID_POSTFAIL)
        self.post_fail.select_region(0, -1)
        return

    cptr.addAttribute("alias",name)
    cptr.setConfigVersion(version)

    if postjoin.strip() != "":
      if int(postjoin) < 0:
        postjoin = "-1"  #If negative, make unlimitted delay
      fdptr.addAttribute("post_join_delay",postjoin)
    else:
      fdptr.addAttribute("post_join_delay",POST_JOIN_DEFAULT)

    if postfail.strip() != "":
      if int(postfail) < 0:
        postfail = "-1"  #If negative, make unlimitted delay
      fdptr.addAttribute("post_fail_delay",postfail)
    else:
      fdptr.addAttribute("post_fail_delay",POST_FAIL_DEFAULT)

    xptr = self.model_builder.getFenceXVMdPtr()
    if self.xvmd_cbox.get_active() == True:
      if xptr == None:
        xvmd = FenceXVMd()
        xptr = xvmd
        cptr.addChild(xvmd)
    else:
      if xptr != None:
        cptr.removeChild(xptr)
        xptr = None


    self.model_builder.setModified()
    args = list()
    args.append(CLUSTER_TYPE)
    apply(self.reset_tree_model, args)
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
    #self.fence_panel.run()
    self.fence_props_area.connect('expose-event',self.on_f_props_expose_event)
    self.fence_prop_renderer = PropertiesRenderer(self.fence_props_area,self.fence_props_area.window)
    self.fence_prop_renderer.clear_layout_area()
    #self.fence_panel.show()
    #self.fence_panel.run()

  def prep_fence_panel(self, nd):
    level_index = 1
    treemodel = self.fence_treeview.get_model()
    treemodel.clear()

    node_iter = treemodel.append(None)
    node_str = "<span size=\"11000\"><b>" + cgi.escape(nd.getName()) + "</b></span>"
    treemodel.set(node_iter, FENCE_PIX_COL, self.node_pixbuf,
                             FENCE_NAME_COL, node_str,
                             FENCE_TYPE_COL, F_NODE_TYPE,
                             FENCE_OBJ_COL, nd)

    self.fence_panel_label.set_use_markup(True)
    self.fence_panel_label.set_markup(FENCE_PANEL_LABEL % (cgi.escape(nd.getName())))
    for fence_level in nd.getFenceLevels():
      flevel_iter = treemodel.append(node_iter)
      flevel_substr = FENCE_LEVEL % level_index
      ##The next line mutates the incoming obj tree to issue sensible 
      ##level names
      fence_level.addAttribute("name",str(level_index))
      level_index = level_index + 1
      flevel_str = "<span size=\"11000\"><b>" + cgi.escape(flevel_substr) + "</b></span>"
      treemodel.set(flevel_iter, FENCE_NAME_COL, flevel_str,
                                 FENCE_TYPE_COL, F_LEVEL_TYPE,
                                 FENCE_OBJ_COL, fence_level )

      fences = fence_level.getChildren()
      for fence in fences:
        fence_iter = treemodel.append(flevel_iter)
        fence_str = "<span size=\"11000\"><b>" + cgi.escape(fence.getName()) + "</b></span>"
        treemodel.set(fence_iter, FENCE_PIX_COL, self.fence_pixbuf,
                                  FENCE_NAME_COL, fence_str,
                                  FENCE_TYPE_COL, F_FENCE_TYPE,
                                  FENCE_OBJ_COL, fence)

    self.fence_treeview.expand_all()
    root_iter = treemodel.get_iter_root()
    selection = self.fence_treeview.get_selection()
    selection.select_iter(root_iter)
    #self.fence_prop_renderer.clear_layout_area()
    self.on_fence_tree_changed(None)


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
    if len(self.model_builder.getFenceDevices()) == 0:
      MessageLibrary.errorMessage(_("No configured Fence Devices available.\nConfigure Fence Device first."))
      return
    selection = self.fence_treeview.get_selection()
    model,iter = selection.get_selected()
    if iter == None:
      root_iter = model.get_iter_root()
      nd = model.get_value(root_iter, FENCE_OBJ_COL)
      levels = nd.getFenceLevels()
      if  len(levels) != 1:
        retval = MessageLibrary.errorMessage(SELECT_LEVEL_FOR_FENCE)
        return 
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
    levels = nd.getFenceLevels()
    if iter == None:  #No selection - see if only one level exists
      type = None
    else:
      type = model.get_value(iter,FENCE_TYPE_COL)

    if (type == F_LEVEL_TYPE) or (type == None):  #this is a new fi...
      if type == F_LEVEL_TYPE:
        level_obj = model.get_value(iter,FENCE_OBJ_COL)
      else:  #level_obj needs to be the first fence level
        level_obj = levels[0]

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
        if agent_type == "fence_scsi":
          f_obj.addAttribute("node",nd.getName())
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

        #special case for drac/mc...if modulename is removed, attr must be as well
        if agent_type == "fence_drac":
          try:
            check_var = attrlist["modulename"]
            if check_var == "":
              f_obj.removeAttribute("modulename") #This rm's any old modulename
          except KeyError, e:
            pass    #no attr, no worries
 
        #special case for ipmi lanplus...if lanplus cbox is unchecked, attr must be as well
        if agent_type == "fence_ipmilan":
          try:
            check_var = attrlist["lanplus"]
            if check_var == "":
              f_obj.removeAttribute("lanplus") #This rm's any old lanplus
          except KeyError, e:
            pass    #no attr, no worries
 

    self.model_builder.setModified()
    #self.fi_panel.hide()

  def on_create_level(self, button):
    selection = self.fence_treeview.get_selection()
    model,iter = selection.get_selected()
    root_iter = model.get_iter_root()
    nd = model.get_value(root_iter, FENCE_OBJ_COL) #node
    #find out how many levels
    num_levels = len(nd.getFenceLevels())
    if num_levels > 0:
      attr_val = num_levels + 1
    else:
      attr_val = 1
    method = Method()
    method.addAttribute("name",str(attr_val))
    nd.getFence().addChild(method)
    self.model_builder.setModified()
    self.prep_fence_panel(nd)

  def on_del_level(self, button):
    selection = self.fence_treeview.get_selection()
    model,iter = selection.get_selected()
    if iter == None:
      return
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
    fence_ptr = nd.getFence()
    fence_ptr.removeChild(obj)
    self.model_builder.setModified()
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
    self.model_builder.setModified()
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
      normalized_name = fd.getName()
      normalized_name = normalized_name.replace('_','__')
      m = gtk.MenuItem(normalized_name)
      # m = gtk.MenuItem(fd.getName())
      counter = counter + 1
      m.show()
      menu.append(m)

    self.fi_options.set_menu(menu) 

  def refresh_fi_panel(self, editmode=True):
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
    self.node_props_name.grab_focus()
    self.node_props_name.set_activates_default(True)
    self.node_props_votes.set_text("")
    if self.model_builder.getLockType() == GULM_TYPE:
      self.gulm_lockserver.show()
      self.gulm_lockserver.set_active(False)
      self.mcast_interface.hide()
    else:
      self.gulm_lockserver.hide()
      if self.model_builder.isMulticast() == True:
        self.mcast_interface.show()
      else:
        self.mcast_interface.hide()

    self.node_props.set_default_response(gtk.RESPONSE_OK)
    self.node_props.run()
   
  def on_node_props_ok(self, button):
    #Get attrs
    #check votes between 0 <-> 255
    votesattr = self.node_props_votes.get_text()
    if votesattr == "":
      votesattr = "1"

    if votesattr.isdigit() == False:
      self.errorMessage(VOTES_ONLY_DIGITS)
      self.node_props_votes.set_text("")
      return

    intvote = int(votesattr)
    if (intvote < 0) or (intvote > 255):
      self.errorMessage(VOTES_ONLY_DIGITS)
      self.node_props_votes.set_text("")
      return

    #New Node: get selection...get list nodes...check for unique name
    #existing node: check for diff between current name - if so, get list 
    #and check for unique
    nameattr = self.node_props_name.get_text().strip()
    if nameattr == "":
      self.errorMessage(NODE_NAME_REQUIRED)
      self.node_props_name.set_text("")
      return

    if len(nameattr) > 64:
      self.errorMessage(NODE_NAME_LENGTH_EXCEEDED)
      return

    if nameattr.find(" ") != (-1):
      self.errorMessage(NODE_NAME_WHITESPACE)
      return


    if self.node_props_flag == NODE_NEW:
      nds = self.model_builder.getNodes()
      for n in nds:
        if n.getName() == nameattr:
          self.node_props_name.select_region(0, (-1))
          self.node_props_name.grab_focus()
          self.errorMessage(NODE_UNIQUE_NAME)
          return 
      # node's name may not be equal to fencedevice's name
      fds = self.model_builder.getFenceDevices()
      for fd in fds:
        if fd.getName() == nameattr:
          self.node_props_name.select_region(0, (-1))
          self.node_props_name.grab_focus()
          self.errorMessage(NODE_NAME_EQUAL_TO_FD_NAME % nameattr)
          return
      
      cn = ClusterNode()
      cn.addAttribute(NAME_ATTR,nameattr)
      cn.addAttribute(VOTES_ATTR,votesattr)
      nodeid = self.model_builder.getUniqueNodeID()
      cn.addAttribute(NODEID_ATTR,nodeid)
      self.model_builder.addNode(cn)

      if self.model_builder.getLockType() == GULM_TYPE:
        if self.gulm_lockserver.get_active() == True:
          ls = Lockserver()
          ls.addAttribute(NAME_ATTR,nameattr)
          self.model_builder.getGULMPtr().addChild(ls)
      else:  #DLM Type locking...
        if self.model_builder.isMulticast() == True:
          mcast = cn.getMulticastNode()
          if mcast != None:
            mcast.addAttribute("addr",self.model_builder.getMcastAddr())
            ifc = self.mcast_interface_entry.get_text().strip()
            if ifc == "":
              mcast.addAttribute("interface","eth0")
            else: 
              mcast.addAttribute("interface",ifc)

    else:  #this case is for editing existing nodes
      selection = self.treeview.get_selection()
      model,iter = selection.get_selected()
      nd = model.get_value(iter, OBJ_COL)
      ndname = nd.getName()
      islockserver = self.model_builder.isNodeLockserver(ndname)
      if (ndname != nameattr): #indicates user changed name string
        nds = self.model_builder.getNodes()
        for n in nds:
          if n.getName() == nameattr:
            #self.node_props_name.set_text("ndname")
            self.node_props_name.select_region(0, (-1))
            self.node_props_name.grab_focus()
            self.errorMessage(NODE_UNIQUE_NAME)
            return
        # node's name may not be equal to fencedevice's name
        for fd in self.model_builder.getFenceDevices():
          if fd.getName() == nameattr:
            self.node_props_name.select_region(0, (-1))
            self.node_props_name.grab_focus()
            self.errorMessage(NODE_NAME_EQUAL_TO_FD_NAME % nameattr)
            return
        if self.model_builder.getLockType() == GULM_TYPE:
          if islockserver and (self.gulm_lockserver.get_active() == True):
            lsn = self.model_builder.getLockServer(ndname)
            lsn.addAttribute(NAME_ATTR,nameattr)
        nd.addAttribute(NAME_ATTR,nameattr)
        #Before we are finished here, we need to iterate through all of the
        #current faildoms and replace ndname with nameattr...
        self.model_builder.rectifyNewNodenameWithFaildoms(ndname,nameattr)
      nd.addAttribute(VOTES_ATTR,votesattr) 

      if self.model_builder.getLockType() == GULM_TYPE:
        if islockserver and (self.gulm_lockserver.get_active() == False):
          gptr = self.model_builder.getGULMPtr()
          gptr.removeChild(self.model_builder.getLockServer(nd.getName()))
        elif (islockserver == False) and (self.gulm_lockserver.get_active() == True):
          ls = Lockserver()
          ls.addAttribute(NAME_ATTR,nameattr)
          gptr = self.model_builder.getGULMPtr()
          gptr.addChild(ls)

      else:
        if self.model_builder.isMulticast() == True:
          ifc = self.mcast_interface_entry.get_text().strip()
          if ifc == "":
            nd.setInterface("eth0") #set the default
          else: 
            nd.setInterface(ifc) 

    self.model_builder.setModified()
    args = list()
    args.append(CLUSTER_NODES_TYPE)
    apply(self.reset_tree_model, args)

      
    self.node_props_flag = NODE_NEW
    self.node_props.hide() 

  def on_node_props_cancel(self, button):
    self.node_props_flag = NODE_NEW
    self.node_props.hide() 

  def on_clusternode_edit_b(self, button):
    self.node_props_flag = NODE_EXISTING
    self.node_props_votes.set_activates_default(True)
    self.prep_clusternode_edit_dialog(NODE_EXISTING)
    self.node_props.set_default_response(gtk.RESPONSE_OK)
    self.node_props.run()

  def on_clusternode_delete_b(self, button):
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    nd = model.get_value(iter,OBJ_COL)

    retval = self.warningMessage(CONFIRM_NODE_REMOVE % nd.getName())
    if (retval == gtk.RESPONSE_NO):
      return

    self.model_builder.deleteNode(nd)
    self.node_props_flag = NODE_NEW
    args = list()
    args.append(CLUSTER_NODES_TYPE)
    apply(self.reset_tree_model, args)

  def prep_clusternode_edit_dialog(self, status):
    if status == NODE_NEW:
      self.node_props_name.set_text("")
      self.node_props_name.grab_focus("")
      self.node_props_votes.set_text("1")
      if self.model_builder.getLockType() == GULM_TYPE:
        self.gulm_lockserver.show()
        self.gulm_lockserver.set_active(False)
        self.mcast_interface.hide()  #Insurance...
      else:  #Uses DLM Type locking then...
        self.gulm_lockserver.hide()
        if self.model_builder.isMulticast() == True:
          self.mcast_interface.show()
        else: 
          self.mcast_interface.hide()
    else:
      selection = self.treeview.get_selection()
      model,iter = selection.get_selected()
      nd = model.get_value(iter, OBJ_COL)
      attrs = nd.getAttributes()
      try:
        self.node_props_name.set_text(attrs[NAME_ATTR]) 
        self.node_props_votes.select_region(0, (-1)) 
        self.node_props_votes.grab_focus() 
      except KeyError, e:
        print " Error looking up key in Nodes attr hash"

      try:
        self.node_props_votes.set_text(attrs[VOTES_ATTR]) 
      except KeyError, e:
        self.node_props_votes.set_text(ONE_VOTE)

      if self.model_builder.getLockType() == GULM_TYPE:
        self.gulm_lockserver.show()
        self.mcast_interface.hide()
        if self.model_builder.isNodeLockserver(attrs[NAME_ATTR]):
          self.gulm_lockserver.set_active(True)
        else:
          self.gulm_lockserver.set_active(False)
      else:  #DLM type then...
        self.gulm_lockserver.hide()
        if self.model_builder.isMulticast() == True:
          self.mcast_interface.show()
          ifc = nd.getInterface()
          if ifc != None:
            self.mcast_interface_entry.set_text(ifc)
          else:
            self.mcast_interface_entry.set_text("eth0")
        else: 
          self.mcast_interface.hide()

    #self.node_props.show()
    #self.node_props.run()

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
      #self.fd_panel.show()
      self.fd_panel.run()
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
      #self.fd_panel.show()
      self.fd_panel.run()

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
      args = list()
      args.append(FENCE_DEVICES_TYPE)
      apply(self.reset_tree_model, args)
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
      
      self.fd_delete.set_title(FD_DELETION_WARNING)
      self.fd_delete_treeview.get_column(0).set_title(AFFECTED_CLUSTER_NODES)
      if num_kees == 1:
        self.fd_delete_warning1.set_text(WARNING1 % fd_name)
        self.fd_delete_warning2.set_text(WARNING2)
      else:
        self.fd_delete_warning1.set_text(WARNINGS1 % fd_name)
        self.fd_delete_warning2.set_text(WARNINGS2)

      response = self.fd_delete.run()
      self.fd_delete.hide()
      if response == gtk.RESPONSE_YES:
        fd_ptr = self.model_builder.getFenceDevicePtr()
        fd_ptr.removeChild(obj)
        
        # update nodes' fences
        for node in kees:
          for fence_level in node.getFenceLevels():
            for fence in fence_level.getChildren()[:]:
              if fence.getName().strip() == obj.getName().strip():
                fence_level.removeChild(fence)
        
        self.model_builder.setModified()
        args = list()
        args.append(FENCE_DEVICES_TYPE)
        apply(self.reset_tree_model, args)
  
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
        self.model_builder.setModified()
        args = list()
        args.append( FENCE_DEVICES_TYPE) 
        apply(self.reset_tree_model, args)

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
        self.model_builder.setModified()
        args = list()
        args.append(FENCE_DEVICES_TYPE)
        apply(self.reset_tree_model, args)

    self.model_builder.setModified()

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
    self.add_faildom_dlg.run()

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
    self.model_builder.setModified()
    #self.faildom_panel.show()
    self.faildom_panel.run()

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
    faildom = model.get_value(iter, OBJ_COL)
    
    # find affected services
    services = []
    for service in self.model_builder.getServices():
      domain = service.getAttribute('domain')
      if domain == faildom.getName():
        services.append(service)
    
    # prompt
    if len(services) == 0:  #simple warning...
      retval = self.warningMessage(CONFIRM_FAILDOM_REMOVE % faildom.getName())
      if retval != gtk.RESPONSE_YES:
        return
    else:
      treemodel = self.fd_delete_treeview.get_model()
      treemodel.clear()
      for service in services:
        new_iter = treemodel.append()
        treemodel.set(new_iter, 0, service.getName())
      self.fd_delete_treeview.get_selection().unselect_all()
      self.fd_delete.set_title(FAILDOM_DELETION_WARNING)
      self.fd_delete_treeview.get_column(0).set_title(AFFECTED_SERVICES)
      if len(services) == 1:
        self.fd_delete_warning1.set_text(WARNING3 % faildom.getName())
        self.fd_delete_warning2.set_text(WARNING4)
      else:
        self.fd_delete_warning1.set_text(WARNINGS3 % faildom.getName())
        self.fd_delete_warning2.set_text(WARNINGS4)
      response = self.fd_delete.run()
      self.fd_delete.hide()
      if response != gtk.RESPONSE_YES:
        return
    
    # remove failover domain
    ###XXX-FIX should be wrapped in exception handler
    faildoms_ptr = self.model_builder.getFailoverDomainPtr()
    faildoms_ptr.removeChild(faildom)
    # update services
    for service in services:
      service.removeAttribute('domain')
    
    self.model_builder.setModified()
    args = list()
    args.append(FAILOVER_DOMAINS_TYPE)
    apply(self.reset_tree_model, args)

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
      self.rc_optionmenu_change(None)
      self.rc_options.show()
      self.rc_dlg_label.set_markup(SELECT_RC_TYPE)
      #self.rc_panel.show()
      self.rc_panel.run()
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
      #self.rc_panel.show()
      self.rc_panel.run()

  def on_rc_delete(self, button):
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    rc = model.get_value(iter, OBJ_COL)
    
    # find affected services
    services = []
    for service in self.model_builder.getServices():
      if self.__on_rc_delete_recurse(rc, service):
        services.append(service)
    
    # prompt
    if len(services) == 0:  #simple warning...
      retval = self.warningMessage(CONFIRM_RC_REMOVE % rc.getName())
      if retval != gtk.RESPONSE_YES:
        return
    else:
      treemodel = self.fd_delete_treeview.get_model()
      treemodel.clear()
      for service in services:
        new_iter = treemodel.append()
        treemodel.set(new_iter, 0, service.getName())
      self.fd_delete_treeview.get_selection().unselect_all()
      self.fd_delete.set_title(RESOURCE_DELETION_WARNING)
      self.fd_delete_treeview.get_column(0).set_title(AFFECTED_SERVICES)
      if len(services) == 1:
        self.fd_delete_warning1.set_text(WARNING5 % rc.getName())
        self.fd_delete_warning2.set_text(WARNING6)
      else:
        self.fd_delete_warning1.set_text(WARNINGS5 % rc.getName())
        self.fd_delete_warning2.set_text(WARNINGS6)
      response = self.fd_delete.run()
      self.fd_delete.hide()
      if response != gtk.RESPONSE_YES:
        return
    
    # remove
    self.model_builder.removeReferences(rc)
    rcs_ptr = self.model_builder.getResourcesPtr()
    rcs_ptr.removeChild(rc)
    self.model_builder.setModified()
    
    args = list()
    args.append(RESOURCES_TYPE)
    apply(self.reset_tree_model, args)
  def __on_rc_delete_recurse(self, tagobj, level):
    for t in level.getChildren():
      if t.isRefObject():
        if t.getObj() == tagobj:
          return True
      if self.__on_rc_delete_recurse(tagobj, t):
        return True
    return False
  
  def rc_panel_ok(self, button):
    #first, find out if this is for edited props, or a new device
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    type = model.get_value(iter, TYPE_COL)
    if type == RESOURCE_TYPE:  #edit
      r_obj = model.get_value(iter, OBJ_COL)
      tagname = r_obj.getTagName()
      if tagname == "ip":
        returnlist = self.rc_handler.validate_resource(tagname, r_obj.getAttribute("address"))
      elif tagname == "SAPDatabase":
        returnlist = self.rc_handler.validate_resource(tagname, r_obj.getAttribute("SID"))
      elif tagname == "SAPInstance":
        returnlist = self.rc_handler.validate_resource(tagname, r_obj.getAttribute("InstanceName"))
      else:
        returnlist = self.rc_handler.validate_resource(tagname, r_obj.getName())
      if returnlist != None:
        self.rc_panel.hide()
        for k in returnlist.keys():
          r_obj.addAttribute(k, returnlist[k])
        if r_obj.getTagName() == NFSCLIENT_TAG:
          #If path attr has been removed, we need to remove from obj as well
          try:
            pth = returnlist["path"]
            if pth == "":
              r_obj.removeAttribute("path")
          except KeyError, e:
            r_obj.removeAttribute("path")
        if r_obj.getTagName() == "SAPDatabase":
          #If dbj2ee_only attr has been removed, we need to remove from obj as well
          try:
            jonly = returnlist["DBJ2EE_ONLY"]
            if jonly == "FALSE":
              r_obj.removeAttribute("DBJ2EE_ONLY")
          except KeyError, e:
            r_obj.removeAttribute("DBJ2EE_ONLY")
        self.model_builder.updateReferences()
        self.model_builder.setModified()
        args = list()
        args.append( RESOURCES_TYPE)
        apply(self.reset_tree_model, args)

    else: #New...
      dex = self.rc_options.get_history()
      tagname = self.rc_optionmenu_hash[dex]
      newobj = self.model_builder.createObjectFromTagname(tagname)
      returnlist = self.rc_handler.validate_resource(tagname, None)
      if returnlist != None:
        self.rc_panel.hide()
        for x in returnlist.keys():
          newobj.addAttribute(x,returnlist[x])
        ptr = self.model_builder.getResourcesPtr()
        ptr.addChild(newobj)
        self.model_builder.setModified()
        args = list()
        args.append(RESOURCES_TYPE) 
        apply(self.reset_tree_model, args)

  def rc_panel_cancel(self, button):
    self.rc_panel.hide()
    self.rc_handler.clear_rc_forms()

  def on_vm_add(self, button):
    #launch dialog for virtual service creation
    self.vm_name.set_sensitive(True)
    self.vm_name.set_text("")
    self.vm_path.set_text("")
    self.vm_props_dlg.run()

  def on_vm_edit(self, button):
    #launch dialog for virtual service editing
    # find out which virtual service to edit
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, OBJ_COL)
    self.vm_name.set_text(obj.getName())
    self.vm_name.set_sensitive(False)
    path = obj.getAttribute("path")
    if path != None:
      self.vm_path.set_text(path)
    else:
      self.vm_path.set_text("")
    self.vm_props_dlg.run()

  def on_vm_del(self, button):
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, OBJ_COL)
    retval = self.warningMessage(CONFIRM_VM_REMOVE % obj.getName())
    if (retval == gtk.RESPONSE_NO):
      return
    rm_ptr = self.model_builder.getResourceManagerPtr()
    rm_ptr.removeChild(obj)
    self.model_builder.setModified()
    args = list()
    args.append(VMS_TYPE)
    apply(self.reset_tree_model, args)
    

  def on_svc_add(self, button):
    #launch dialog for service name field
    self.svc_name.set_text("")
    #self.svc_add_dlg.show()
    self.svc_add_dlg.run()

  def on_vm_props_ok(self, button):
    vm_name = self.vm_name.get_text().strip()
    if vm_name == "":
      self.errorMessage(VM_NAME_REQUIRED)
      return
    vm_path = self.vm_path.get_text().strip()
    if vm_path == "":
      self.errorMessage(VM_PATH_REQUIRED)
      return


    try:
      v = self.model_builder.retrieveVMsByName(vm_name)
    except:
      v = None  # Does not exist - good

    if self.vm_name.get_property('sensitive') != 0:  #A new VM
      if v == None: #This is a new VM
        v = Vm()
        v.addAttribute("name",vm_name)
        v.addAttribute("path",vm_path)
        rm_ptr = self.model_builder.getResourceManagerPtr()
        rm_ptr.addChild(v)
      else:  #Name collision
        self.vm_name.select_region(0, (-1))
        self.errorMessage(UNIQUE_VM_NAME % vm_name)
        return

    else:
      if v != None:
        v.addAttribute("path",vm_path)
      else:
        self.errorMessage(UNABLE_LOCATE_VM % vm_name)
        return

    self.vm_props_dlg.hide()
    self.model_builder.setModified()
    args = list()
    args.append(VMS_TYPE) 
    apply(self.reset_tree_model, args)

  def on_vm_props_cancel(self, button):
    self.vm_props_dlg.hide()

  def on_svc_add_ok(self, button):
    svcs = self.model_builder.getServices()
    svc_name = self.svc_name.get_text().strip()
    if svc_name == "":
      self.errorMessage(SERVICE_NAME_REQUIRED)
      return
    for svc in svcs:
      if svc.getName().strip() == svc_name:
        self.svc_name.select_region(0, (-1))
        self.errorMessage(UNIQUE_SERVICE_NAME % svc_name)
        return

    #Made it past unique name check -- ready to add service
    service = Service()
    service.addAttribute("name", svc_name)
    service.addAttribute("autostart", "1") #Have autostart set by default
    rm_ptr = self.model_builder.getResourceManagerPtr()
    rm_ptr.addChild(service)
    self.svc_add_dlg.hide()
    self.svc_name.set_text("")
    self.service_controller.prep_service_panel(service)
    self.model_builder.setModified()
    self.svc_mgmt.show()

  def on_svc_add_cancel(self, button):
    self.svc_add_dlg.hide()

  def on_svc_edit(self, button):
    #1) find out which service to edit
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, OBJ_COL)
    #2) populate interface
    self.service_controller.prep_service_panel(obj)
    #3) show dialog
    self.svc_mgmt.run()
    #self.svc_mgmt.show()

  def on_svc_edit_close(self, button):
      self.service_controller_close()
      
  def service_controller_close(self):
    self.service_controller.cleanup_panels()
    self.svc_mgmt.hide()
    args = list()
    args.append( RESOURCE_GROUPS_TYPE)
    apply(self.reset_tree_model, args)

  #This method identifies the service to be removed, and then
  #searches beneath the <rm> tag for it, and deletes it...simple.
  def on_svc_del(self, button):
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, OBJ_COL)
    retval = self.warningMessage(CONFIRM_SVC_REMOVE % obj.getName())
    if (retval == gtk.RESPONSE_NO):
      return
    rm_ptr = self.model_builder.getResourceManagerPtr()
    rm_ptr.removeChild(obj)
    self.model_builder.setModified()
    args = list()
    args.append(RESOURCE_GROUPS_TYPE)
    apply(self.reset_tree_model, args)





  def on_f_props_expose_event(self, widget, event):
     self.fence_prop_renderer.do_render()

  def set_model(self, model_builder,treeview):
    self.model_builder = model_builder
    self.treeview = treeview
    self.faildom_controller.set_model(self.model_builder)
    self.service_controller.set_model(self.model_builder)
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
    return True

  def cluster_props_dlg_delete(self, *args):
    self.cluster_props_dlg.hide()
    return True

  def fence_panel_delete(self, *args):
    self.fence_panel.hide()
    return True

  def fd_panel_delete(self, *args):
    self.fd_panel.hide()
    return True

  def fi_panel_delete(self, *args):
    self.fi_panel.hide()
    return True

  def faildom_panel_delete(self, *args):
    self.faildom_panel.hide()
    return True

  def add_faildom_dlg_delete(self, *args):
    self.add_faildom_dlg.hide()
    return True

  def rc_panel_delete(self, *args):
    self.rc_panel.hide()
    return True

  def on_svc_mgmt_delete(self, *args):
    self.service_controller_close()
    return True

  def on_svc_add_delete(self, *args):
    self.svc_add_dlg.hide()
    return True

  def on_vm_props_delete(self, *args):
    self.vm_props_dlg.hide()
    return True

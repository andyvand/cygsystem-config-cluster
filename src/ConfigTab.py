from gtk import TRUE, FALSE
import string
import gobject
import sys
from clui_constants import *
from PropertiesRenderer import PropertiesRenderer

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
                                                                                
from ConfigTabController import ConfigTabController

CLUSTER=_("Cluster")
CLUSTERNODES=_("Cluster Nodes")
CLUSTERNODE=_("Cluster Node")
FENCE=_("Fencing Configuration")
FENCEDEVICES=_("Fence Devices")
FENCEDEVICE=_("Fence Device")
MANAGED_RESOURCES=_("Managed Resources")
FAILOVER_DOMAINS=_("Failover Domains")
FAILOVER_DOMAIN=_("Failover Domain")
RESOURCE_GROUPS=_("Resource Groups")
RESOURCE_GROUP=_("Resource Group")
RESOURCES=_("Resources")
RESOURCE=_("Resource")
IPADDRESS=_("IP Address")

FENCE_CONFIGURATION=_("Fence Configuration for this Cluster Node")


############################################
class ConfigTab:
  def __init__(self, glade_xml, model_builder):

    self.model_builder = model_builder
    self.glade_xml = glade_xml

    #set up tree structure
    self.treeview = self.glade_xml.get_widget('maintree')
    self.treemodel = gtk.TreeStore (gobject.TYPE_STRING,
                                    gobject.TYPE_INT,
                                    gobject.TYPE_PYOBJECT)
    self.treeview.set_model(self.treemodel)
    self.treeview.set_headers_visible(FALSE)

    self.controller = ConfigTabController(self.model_builder, 
                                          self.treeview,
                                          self.glade_xml,
                                          self.reset_tree_model)

    #Tree Change Listener
    selection = self.treeview.get_selection()
    selection.connect('changed',self.on_tree_selection_changed)

    renderer = gtk.CellRendererText()
    column1 = gtk.TreeViewColumn("Cluster Management",renderer,markup=0)
    self.treeview.append_column(column1)

    self.area = self.glade_xml.get_widget('drawingarea1')
    self.area.connect('expose-event',self.on_props_expose_event)
    self.prop_renderer = PropertiesRenderer(self.area, self.area.window)
    self.prop_renderer.clear_layout_area()

    self.init_buttonpanels()

    self.prepare_tree()

  def clearall(self):
    treemodel = self.treeview.get_model()
    treemodel.clear()
    self.clear_all_buttonpanels()
    self.treeview.hide()

  def set_model(self, model_builder):
    self.model_builder = model_builder
    self.prepare_tree()
    self.controller.set_model(self.model_builder, self.treeview)

  def on_tree_selection_changed(self, *args):
    selection = self.treeview.get_selection()
    model,iter = selection.get_selected()
    if iter == None:
      return

    type = model.get_value(iter, TYPE_COL)
    obj = model.get_value(iter, OBJ_COL)

    if type == CLUSTER_TYPE:
      self.prop_renderer.render_to_layout_area(obj.getProperties(), obj.getName(),type) 
      self.clear_all_buttonpanels()
      self.cluster_p.show()
    elif type == CLUSTER_NODES_TYPE:
      self.prop_renderer.render_to_layout_area(obj.getProperties(), obj.getName(),type) 
      self.clear_all_buttonpanels()
      self.clusternode_p.show()
    elif type == CLUSTER_NODE_TYPE:
      self.prop_renderer.render_to_layout_area(None, obj.getName(),type) 
      self.clear_all_buttonpanels()
      self.node_p.show()
    elif type == FENCE_TYPE:
      self.prop_renderer.render_to_layout_area(None, obj.getName(),type) 
      self.clear_all_buttonpanels()
      self.fence_p.show()
    elif type == FENCE_DEVICES_TYPE:
      self.prop_renderer.render_to_layout_area(None, obj.getTagName(),type) 
      self.clear_all_buttonpanels()
      self.fencedevices_p.show()
    elif type == FENCE_DEVICE_TYPE:
      self.prop_renderer.render_to_layout_area(None, obj.getName(),type) 
      self.clear_all_buttonpanels()
      self.fencedevice_p.show()
    elif type == MANAGED_RESOURCES_TYPE:
      self.prop_renderer.render_to_layout_area(None, obj.getName(),type) 
      self.clear_all_buttonpanels()
    elif type == FAILOVER_DOMAINS_TYPE:
      self.prop_renderer.render_to_layout_area(obj.getProperties(), obj.getName(),type) 
      self.clear_all_buttonpanels()
      self.faildoms_p.show()
    elif type == FAILOVER_DOMAIN_TYPE:
      self.prop_renderer.render_to_layout_area(obj.getProperties(), obj.getName(),type) 
      self.clear_all_buttonpanels()
      self.faildom_p.show()
    elif type == RESOURCE_GROUPS_TYPE:
      self.prop_renderer.render_to_layout_area(None, obj.getName(),type) 
      self.clear_all_buttonpanels()
      self.resourcegroups_p.show()
    elif type == RESOURCE_GROUP_TYPE:
      self.prop_renderer.render_to_layout_area(None, obj.getName(),type) 
      self.clear_all_buttonpanels()
      self.resourcegroup_p.show()
    elif type == RESOURCES_TYPE:
      self.prop_renderer.render_to_layout_area(None, obj.getName(),type) 
      self.clear_all_buttonpanels()
      self.resources_p.show()
    elif type == RESOURCE_TYPE:
      if obj.getTagName() == "ip":
        nm = IPADDRESS
      else:
        nm = obj.getName()
      self.prop_renderer.render_to_layout_area(None, nm,type) 
      self.clear_all_buttonpanels()
      self.resource_p.show()
    else:
      self.clear_all_buttonpanels()

  def clear_all_buttonpanels(self):
    self.cluster_p.hide()
    self.clusternode_p.hide()
    self.node_p.hide()
    self.fence_p.hide()
    self.fencedevices_p.hide()
    self.fencedevice_p.hide()
    self.faildoms_p.hide()
    self.faildom_p.hide()
    self.resourcegroups_p.hide()
    self.resourcegroup_p.hide()
    self.resources_p.hide()
    self.resource_p.hide()

  def init_buttonpanels(self):
    self.cluster_p = self.glade_xml.get_widget('cluster_p')
    self.clusternode_p = self.glade_xml.get_widget('clusternode_p')
    self.node_p = self.glade_xml.get_widget('node_p')
    self.fence_p = self.glade_xml.get_widget('fence_p')
    self.fencedevices_p = self.glade_xml.get_widget('fencedevices_p')
    self.fencedevice_p = self.glade_xml.get_widget('fencedevice_p')
    self.faildoms_p = self.glade_xml.get_widget('faildoms_p')
    self.faildom_p = self.glade_xml.get_widget('faildom_p')
    self.resourcegroups_p = self.glade_xml.get_widget('resourcegroups_p')
    self.resourcegroup_p = self.glade_xml.get_widget('resourcegroup_p')
    self.resources_p = self.glade_xml.get_widget('resources_p')
    self.resource_p = self.glade_xml.get_widget('resource_p')

  def reset_tree_model(self, *in_args):
    args = list()
    for a in in_args:
      args.append(a)

    self.prepare_tree()


  def prepare_tree(self):
    treemodel = self.treeview.get_model()
    treemodel.clear()

    #Set all major divisions
    #For each minor element, call model_builder for items

    ###CLUSTER
    cluster_iter = treemodel.append(None)
    cluster_str = "<span size=\"11000\"><b>" + CLUSTER + "</b></span>"
    cluster_ptr = self.model_builder.getClusterPtr()
    treemodel.set(cluster_iter, NAME_COL, cluster_str,
                                TYPE_COL, CLUSTER_TYPE,
                                OBJ_COL, cluster_ptr)

    ###CLUSTER_NODES
    cn_iter = treemodel.append(cluster_iter)
    cn_str = "<span size=\"10000\" foreground=\"" + CLUSTERNODES_COLOR + "\"><b>" + CLUSTERNODES + "</b></span>"
    cn_ptr = self.model_builder.getClusterNodesPtr()
    treemodel.set(cn_iter, NAME_COL, cn_str,
                           TYPE_COL, CLUSTER_NODES_TYPE,
                           OBJ_COL, cn_ptr)

    ###NODES
    nodelist = self.model_builder.getNodes()
    for node in nodelist:
      n_iter = treemodel.append(cn_iter)
      n_str = "<span>" + node.getName() + "</span>"
      treemodel.set(n_iter, NAME_COL, n_str,
                            TYPE_COL, CLUSTER_NODE_TYPE,
                            OBJ_COL, node)
#      fences = node.getChildren()
#      if len(fences) > 0:
#        for fence in fences:
#          f_iter = treemodel.append(n_iter)
#          f_str = "<span>" + FENCE + "</span>"
#          treemodel.set(f_iter, NAME_COL, f_str,
#                                TYPE_COL, FENCE_TYPE)

    fencedevs = self.model_builder.getFenceDevices()
    fencedev_ptr = self.model_builder.getFenceDevicePtr()
    fds_iter = treemodel.append(cluster_iter)
    fds_str = "<span size=\"10000\" foreground=\"" + FENCEDEVICES_COLOR + "\"><b>" + FENCEDEVICES + "</b></span>"
    treemodel.set(fds_iter, NAME_COL, fds_str,
                            TYPE_COL, FENCE_DEVICES_TYPE,
                            OBJ_COL, fencedev_ptr) 
    for fd in fencedevs:
      fd_iter = treemodel.append(fds_iter) 
      fd_str = "<span>" + fd.getName() + "</span>"
      treemodel.set(fd_iter, NAME_COL, fd_str,
                             TYPE_COL, FENCE_DEVICE_TYPE,
                             OBJ_COL,  fd)

    ###MANAGED RESOURCES
    faildoms = self.model_builder.getFailoverDomains()

    rgroups = self.model_builder.getResourceGroups()

    resources = self.model_builder.getResources()

    mr_iter = treemodel.append(cluster_iter)
    mr_str = "<span size=\"10000\"><b>" + MANAGED_RESOURCES + "</b></span>"
    treemodel.set(mr_iter, NAME_COL, mr_str,
                           TYPE_COL, MANAGED_RESOURCES_TYPE)

    ###FAILOVER DOMAINS
    fdoms_iter = treemodel.append(mr_iter)
    fdoms_str = "<span size=\"10000\" foreground=\"" + FAILOVERDOMAINS_COLOR + "\"><b>" + FAILOVER_DOMAINS + "</b></span>"
    fdoms_ptr = self.model_builder.getFailoverDomainPtr()
    treemodel.set(fdoms_iter, NAME_COL, fdoms_str,
                              TYPE_COL, FAILOVER_DOMAINS_TYPE,
                              OBJ_COL, fdoms_ptr)

    for faildom in faildoms:
      fdom_iter = treemodel.append(fdoms_iter)
      fdom_str = "<span>" + faildom.getName() + "</span>"
      treemodel.set(fdom_iter, NAME_COL, fdom_str,
                               TYPE_COL,FAILOVER_DOMAIN_TYPE,
                               OBJ_COL, faildom)

    ###RESOURCES
    resources_iter = treemodel.append(mr_iter)
    rc_ptr = self.model_builder.getResourcesPtr()
    resources_str = "<span size=\"10000\" foreground=\"" + RESOURCES_COLOR + "\"><b>" + RESOURCES + "</b></span>"
    treemodel.set(resources_iter, NAME_COL, resources_str,
                              TYPE_COL, RESOURCES_TYPE,
                              OBJ_COL, rc_ptr)

    for resource in resources:
      resource_iter = treemodel.append(resources_iter)
      if resource.getTagName() == "ip":
        resource_str = "<span>" + RESOURCE + " " + IPADDRESS + "</span>"
      else:
        resource_str = "<span>" + RESOURCE + " " + resource.getName() + "</span>"
      treemodel.set(resource_iter, NAME_COL, resource_str,
                               TYPE_COL,RESOURCE_TYPE,
                               OBJ_COL, resource)

    ###RESOURCE GROUPS
    rgrps_iter = treemodel.append(mr_iter)
    rgrps_str = "<span size=\"10000\" foreground=\"" + RESOURCEGROUPS_COLOR + "\"><b>" + RESOURCE_GROUPS + "</b></span>"
    treemodel.set(rgrps_iter, NAME_COL, rgrps_str,
                              TYPE_COL, RESOURCE_GROUPS_TYPE)

    for rgroup in rgroups:
      try:
        rgroup_str = "<span>" + RESOURCE_GROUP + " " + rgroup.getName() + "</span>"
      except KeyError, e:
        continue
      rgroup_iter = treemodel.append(rgrps_iter)
      treemodel.set(rgroup_iter, NAME_COL, rgroup_str,
                               TYPE_COL, RESOURCE_GROUP_TYPE,
                               OBJ_COL, rgroup)

    self.treeview.expand_all()


  def on_props_expose_event(self, widget,event):
    self.prop_renderer.do_render()

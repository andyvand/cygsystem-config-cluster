from FailoverDomainNode import FailoverDomainNode
from FailoverDomain import FailoverDomain
import gobject
from gtk import TRUE, FALSE

import gettext
_ = gettext.gettext
### gettext first, then import gtk (exception prints gettext "_") ###
import gtk
import gtk.glade 

NODES_AVAILABLE = _("Available Cluster Nodes")
NO_NODES_AVAILABLE = _("No Cluster Nodes Available")

NAME_COL = 0
PRIORITY_COL = 1
OBJ_COL = 2
PRIORITY_INT_COL = 3

class FaildomController:
  def __init__(self, glade_xml,model_builder,reset_tree_model):
    self.glade_xml = glade_xml
    self.model_builder = model_builder
    self.reset_tree_model = reset_tree_model
    self.process_widgets()
    self.faildoms = self.model_builder.getFailoverDomainPtr()
    self.current_faildom = None
    self.foreach_found_sentinel = FALSE
    

  def process_widgets(self):
    self.faildom_treeview = self.glade_xml.get_widget('faildom_treeview')
    self.listmodel = gtk.ListStore(gobject.TYPE_STRING, #Name
                                   gobject.TYPE_STRING, #Priority
                                   gobject.TYPE_PYOBJECT, #OBJ_COL
                                   gobject.TYPE_INT) #Priority integer val
    self.listmodel.set_sort_column_id(3,gtk.SORT_ASCENDING)
    self.faildom_treeview.set_model(self.listmodel)
    selection = self.faildom_treeview.get_selection()
    selection.connect('changed',self.on_list_selection_changed)

    renderer = gtk.CellRendererText()
    column1 = gtk.TreeViewColumn("Member Node",renderer,markup=0)
    self.faildom_treeview.append_column(column1)

    renderer2 = gtk.CellRendererText()
    column2 = gtk.TreeViewColumn("Priority",renderer2,markup=1)
    self.faildom_treeview.append_column(column2)

    self.node_options = self.glade_xml.get_widget('node_options')
    self.faildom_name_label = self.glade_xml.get_widget('domain_name_label')
    self.add_member_b = self.glade_xml.get_widget('add_domain_member')
    self.add_member_b.connect('clicked',self.on_add_domain_member)

    self.priority_up = self.glade_xml.get_widget('priority_up')
    self.priority_up.connect('clicked',self.on_priority_up)
    self.priority_down = self.glade_xml.get_widget('priority_down')
    self.priority_down.connect('clicked',self.on_priority_down)

    self.del_from_faildom = self.glade_xml.get_widget('delete_from_faildom')
    self.del_from_faildom.connect('clicked',self.on_del_from_faildom)

    self.priority_label = self.glade_xml.get_widget('priority_label')

    self.member_options = self.glade_xml.get_widget('member_options')

    self.no_nodes_notice = self.glade_xml.get_widget('no_nodes_notice')
    self.treeview_window = self.glade_xml.get_widget('scrolledwindow3')

    self.faildom_panel = self.glade_xml.get_widget('faildom_panel')
    self.glade_xml.get_widget('faildom_panel_close').connect('clicked',self.on_faildom_panel_close)


  def on_add_domain_member(self, button):
    #get selection from optionmenu
    #add node to faildom
    #remove nodefrom optionmenu
    #redo tree view

    if self.node_options.get_history() == 0:
      return
    lbl = self.node_options.get_children()[0]
    fdn = FailoverDomainNode()
    fdn.addAttribute("name",lbl.get_text())
    self.current_faildom.addChild(fdn)
    #self.add_member(lbl)
    self.prep_faildom_panel(self.current_faildom)


  def on_list_selection_changed(self, *args):
    selection = self.faildom_treeview.get_selection()
    model,iter = selection.get_selected()
    if iter == None:
      self.priority_up.set_sensitive(FALSE)
      self.priority_down.set_sensitive(FALSE)
      self.del_from_faildom.set_sensitive(FALSE)
      self.priority_label.set_sensitive(FALSE)
    else:
      #set delete button annd spinner sensitive
      self.del_from_faildom.set_sensitive(TRUE)
      self.priority_label.set_sensitive(TRUE)
      obj = model.get_value(iter, OBJ_COL)
      priority_val = obj.getPriorityLevel()
      if priority_val > 1:
        self.priority_up.set_sensitive(TRUE)
        self.priority_down.set_sensitive(TRUE)
      else:
        self.priority_up.set_sensitive(FALSE)
        self.priority_down.set_sensitive(TRUE)
        
      
      #get selection value for priority and set 

  def on_priority_up(self, button):
    selection = self.faildom_treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, OBJ_COL)
    obj.raisePriorityLevel()
    self.prep_faildom_panel(self.current_faildom)
    self.select_faildomnode(obj.getName())
    pass

  def on_priority_down(self, button):
    selection = self.faildom_treeview.get_selection()
    model,iter = selection.get_selected()
    obj = model.get_value(iter, OBJ_COL)
    obj.lowerPriorityLevel()
    self.prep_faildom_panel(self.current_faildom)
    self.select_faildomnode(obj.getName())

  def on_del_from_faildom(self, button):
    selection = self.faildom_treeview.get_selection()
    model,iter = selection.get_selected()
    #get faildomnode object from tree
    obj = model.get_value(iter, OBJ_COL)
    #call into faildom and del faildomnode object
    if self.current_faildom != None:
      self.current_faildom.removeChild(obj)
      self.prep_faildom_panel(self.current_faildom)

  def select_faildomnode(self, name):
    self.foreach_found_sentinel = FALSE
    selection = self.faildom_treeview.get_selection()
    model, iter = selection.get_selected()
    model.foreach(self.select_node,name)

  def select_node(self,model, path, iter, *args):
    if self.foreach_found_sentinel == TRUE:
      return
    selection = self.faildom_treeview.get_selection()
    selection_args = list()
    for a in args:
      selection_args.append(a)
    obj = model.get_value(iter, OBJ_COL)
    name = obj.getName()
    in_name = args[0]
    if in_name == name.strip():
      self.foreach_found_sentinel = TRUE
      selection.select_range(path,path)
      


  def prep_faildom_panel(self, faildom):
    self.current_faildom = faildom
    if self.current_faildom != None:  
      self.faildom_name_label.set_markup("<span><b>" + faildom.getName() + "</b></span>")
      self.prep_optionmenu()
      self.prep_faildom_tree()

  def prep_optionmenu(self):
    found = FALSE
    optionmenu_candidates = list()
    nodes = self.model_builder.getNodes()
    for node in nodes:
      found = FALSE
      children = self.current_faildom.getChildren()
      for child in children:
        if child.getName().strip() == node.getName().strip():
          found = TRUE
          break
      if found:
        continue
      else:
        optionmenu_candidates.append(node.getName()) 

    #Now we have the set of node names NOT in the current failover domain
    menu = gtk.Menu()
    if len(optionmenu_candidates) > 0:
      m = gtk.MenuItem(NODES_AVAILABLE)
      m.show()
      menu.append(m)
      for opt in optionmenu_candidates:
        m = gtk.MenuItem(opt)
        m.show()
        menu.append(m)
    else:
      m = gtk.MenuItem(NO_NODES_AVAILABLE)
      m.show()
      menu.append(m)

    self.node_options.set_menu(menu)

  def prep_faildom_tree(self):
    children = self.current_faildom.getChildren()
    if len(children) == 0:
      self.treeview_window.hide()
      self.no_nodes_notice.show()
      self.priority_up.set_sensitive(FALSE)
      self.priority_down.set_sensitive(FALSE)
      self.del_from_faildom.set_sensitive(FALSE)
      self.priority_label.set_sensitive(FALSE)
    else:
      self.treeview_window.show()
      self.no_nodes_notice.hide()
      listmodel = self.faildom_treeview.get_model()
      listmodel.clear()
      for child in children:
        iter = listmodel.append()
        listmodel.set(iter, NAME_COL, child.getName(),
                            PRIORITY_COL, str(child.getPriorityLevel()),
                            OBJ_COL, child,
                            PRIORITY_INT_COL, child.getPriorityLevel())

      self.faildom_treeview.get_selection().unselect_all()  
      

  def on_faildom_panel_close(self, button):
    self.faildom_panel.hide() 
    apply(self.reset_tree_model)

  def set_model(self, model_builder):
    self.model_builder = model_builder

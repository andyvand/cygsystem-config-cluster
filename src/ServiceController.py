from Service import Service
from ResourceHandler import *
import gobject
from gtk import TRUE, FALSE
from clui_constants import *
from RefObject import RefObject

import gettext
_ = gettext.gettext
### gettext first, then import gtk (exception prints gettext "_") ###
import gtk
import gtk.glade 

R_NAME_COL = 0
R_TYPE_COL = 1
R_SCOPE_COL = 2
R_OBJ_COL = 3

S_NAME_COL = 0
S_TYPE_COL = 1
S_OBJ_COL = 2

NONE_PLACEHOLDER=_("None")

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
    self.rc_handler = None
    self.rc_optionmenu_hash = {}
    self.process_widgets()
    self.rm_ptr = self.model_builder.getResourceManagerPtr()
    self.current_service = None
    self.prepset = FALSE
    self.foreach_found_sentinel = FALSE
    self.isNewResource = FALSE
    self.isAttachedResource = FALSE
    

  def process_widgets(self):
    self.svc_treeview = self.glade_xml.get_widget('svc_treeview')
    self.treemodel = gtk.TreeStore(gobject.TYPE_STRING, #Name
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

    self.shared_treeview = self.glade_xml.get_widget('shared_treeview')
    self.streemodel = gtk.ListStore(gobject.TYPE_STRING, #Name
                                   gobject.TYPE_STRING, #Type
                                   gobject.TYPE_PYOBJECT) #OBJ_COL
    self.shared_treeview.set_model(self.streemodel)

    srenderer = gtk.CellRendererText()
    self.scolumn1 = gtk.TreeViewColumn("Name",srenderer,markup=0)
    self.shared_treeview.append_column(self.scolumn1)

    srenderer2 = gtk.CellRendererText()
    self.scolumn2 = gtk.TreeViewColumn("Type",srenderer2,markup=1)
    self.shared_treeview.append_column(self.scolumn2)

    self.glade_xml.get_widget('add_shared_rc').connect("clicked",self.on_add_shared)
    self.glade_xml.get_widget('create_new_rc').connect("clicked",self.on_add_private)
    self.attach_new_rc = self.glade_xml.get_widget('attach_new_rc')
    self.attach_new_rc.connect("clicked",self.on_attach_private)
    self.attach_shared_rc = self.glade_xml.get_widget('attach_shared_rc')
    self.attach_shared_rc.connect("clicked",self.on_attach_shared)
    self.edit_rc_button =  self.glade_xml.get_widget('edit_rc')
    self.edit_rc_button.connect("clicked",self.on_edit_rc)
    self.del_rc_button = self.glade_xml.get_widget('button24')
    self.del_rc_button.connect("clicked",self.on_del_resource)
    self.service_name_label = self.glade_xml.get_widget('label103')
    self.svc_fdom_optionmenu = self.glade_xml.get_widget('optionmenu1')
    self.svc_fdom_optionmenu.connect("changed",self.on_fdom_option_changed)

    self.shared_rc_panel = self.glade_xml.get_widget('shared_rc_panel')
    self.shared_rc_panel.connect("delete_event",self.shared_rc_panel_delete)
    self.glade_xml.get_widget('on_shared_rc_ok').connect('clicked',self.on_shared_rc_ok)
    self.glade_xml.get_widget('on_shared_rc_cancel').connect('clicked',self.on_shared_rc_cancel)

    self.rc_proxy = self.glade_xml.get_widget('svc_rc_proxy')
    self.rc_handler = ResourceHandler(self.rc_proxy,self.model_builder)
    self.rc_dlg_label = self.glade_xml.get_widget('svc_rc_dlg_label')
    self.svc_rc_panel = self.glade_xml.get_widget('svc_rc_panel')
    self.svc_rc_panel.connect("delete_event",self.svc_rc_panel_delete)
    self.rc_form_hash = self.rc_handler.get_rc_hash()
    self.rc_prettyname_hash = self.rc_handler.get_pretty_rcname_hash()
    self.rc_options = self.glade_xml.get_widget('optionmenu2')
    self.rc_options.connect('changed',self.rc_optionmenu_change)
    self.prep_rc_options()
    self.glade_xml.get_widget('on_svc_rc_ok').connect('clicked', self.rc_panel_ok)
    self.glade_xml.get_widget('on_svc_rc_cancel').connect('clicked', self.rc_panel_cancel)
    
 

  def populate_fdom_optionmenu(self):
    menu = gtk.Menu()
    faildoms = self.model_builder.getFailoverDomains()
    if len(faildoms) == 0:
      m = gtk.MenuItem(NONE_PLACEHOLDER)
      m.show()
      menu.append(m)
    else:
      m = gtk.MenuItem(NONE_PLACEHOLDER)
      m.show()
      menu.append(m)
      for fdom in faildoms:
        m = gtk.MenuItem(fdom.getName())
        m.show()
        menu.append(m)
    self.prepset = TRUE
    self.svc_fdom_optionmenu.set_menu(menu)

  def populate_shared_tree(self):
    listmodel = self.shared_treeview.get_model()
    listmodel.clear()
    resources_ptr = self.model_builder.getResourcesPtr()
    resources = resources_ptr.getChildren()
    for resource in resources:
      prettyname = self.rc_prettyname_hash[resource.getTagName()]
      iter = listmodel.append()
      listmodel.set(iter, S_NAME_COL, resource.getName(),
                          S_TYPE_COL, prettyname,
                          S_OBJ_COL, resource)

  def on_add_shared(self, button):
    self.populate_shared_tree()
    self.isAttachedResource = FALSE
    self.shared_rc_panel.show()

  def on_add_private(self, button):
    self.isNewResource = TRUE
    self.isAttachedResource = FALSE
    self.rc_handler.clear_rc_forms()
    self.rc_options.set_history(0)
    self.rc_options.show()
    self.rc_dlg_label.set_markup(SELECT_RC_TYPE)
    rcs = self.rc_form_hash.keys()
    for rc in rcs:
      self.rc_form_hash[rc].hide()
    tagname = self.rc_optionmenu_hash[0]
    self.rc_form_hash[tagname].show()
    self.svc_rc_panel.show()
 
  def on_attach_private(self, button):
    self.isNewResource = TRUE
    self.isAttachedResource = TRUE
    self.rc_handler.clear_rc_forms()
    self.rc_options.set_history(0)
    self.rc_options.show()
    self.rc_dlg_label.set_markup(SELECT_RC_TYPE)
    rcs = self.rc_form_hash.keys()
    for rc in rcs:
      self.rc_form_hash[rc].hide()
    tagname = self.rc_optionmenu_hash[0]
    self.rc_form_hash[tagname].show()
    self.svc_rc_panel.show()

  def on_attach_shared(self, button):
    self.populate_shared_tree()
    self.isAttachedResource = TRUE
    self.shared_rc_panel.show()

  def on_edit_rc(self, button):
    selection = self.svc_treeview.get_selection()
    model,iter = selection.get_selected()
    self.rc_options.hide()
    rc_obj = model.get_value(iter, R_OBJ_COL)
    attrs = rc_obj.getAttributes()
    tagname = rc_obj.getTagName()
    self.rc_dlg_label.set_markup(RC_PROPS % (self.rc_prettyname_hash[tagname],rc_obj.getName()))
    self.rc_handler.clear_rc_forms()
    rcs = self.rc_form_hash.keys()
    for rc in rcs:
      self.rc_form_hash[rc].hide()
    self.rc_handler.populate_rc_form(tagname, attrs)
    self.rc_form_hash[tagname].show()
    self.svc_rc_panel.show()


  def on_del_resource(self, button):
    selection = self.svc_treeview.get_selection()
    model, iter = selection.get_selected()
    robj = model.get_value(iter, R_OBJ_COL)
    self.current_service.removeChild(robj)
    self.model_builder.setModified()
    self.prep_service_tree()

  def on_list_selection_changed(self, *args):
    self.all_buttons_on()
    selection = self.svc_treeview.get_selection()
    model,iter = selection.get_selected()
    if iter == None:
      self.attach_new_rc.set_sensitive(FALSE)
      self.attach_shared_rc.set_sensitive(FALSE)
      self.del_rc_button.set_sensitive(FALSE)
      self.edit_rc_button.set_sensitive(FALSE)
      return
    else:
      #if appropriate, edit selection
      obj = model.get_value(iter, R_OBJ_COL)
      if obj.isRefObject() == TRUE:
        self.del_rc_button.set_sensitive(FALSE)
        self.edit_rc_button.set_sensitive(FALSE)
      else:
        self.del_rc_button.set_sensitive(TRUE)
        self.edit_rc_button.set_sensitive(TRUE)

  def on_fdom_option_changed(self, *args):
    if self.prepset == TRUE:
      self.prepset = FALSE
      return
    else:
      if self.svc_fdom_optionmenu.get_history() == 0:
        retval = self.current_service.removeAttribute("domain")
        return
      lbl = self.svc_fdom_optionmenu.get_children()[0]
      self.current_service.addAttribute("domain",lbl.get_text())

    

  def prep_service_panel(self, svc):
    self.current_service = svc
    if self.current_service != None:  
      self.service_name_label.set_markup("<span><b>" + svc.getName() + "</b></span>")

      self.populate_fdom_optionmenu()
      self.prep_service_tree()

  def prep_service_tree(self):
    resources = self.current_service.getChildren()
    treemodel = self.svc_treeview.get_model()
    treemodel.clear()
    for child in resources:
      iter = treemodel.append(None)
      self.add_tree_children(child, iter)

    self.svc_treeview.get_selection().unselect_all()
    self.attach_new_rc.set_sensitive(FALSE)
    self.attach_shared_rc.set_sensitive(FALSE)
    self.del_rc_button.set_sensitive(FALSE)
    self.edit_rc_button.set_sensitive(FALSE)

    self.prepset = TRUE
    domain = self.current_service.getAttribute("domain")
    if domain == None:
      self.svc_fdom_optionmenu.set_history(0)
    else:
      y = (-1)
      menu = self.svc_fdom_optionmenu.get_menu()
      for item in menu.get_children():
        y = y + 1
        children = item.get_children()
        if children:
          if item.get_children()[0].get_text() == domain:
            break
      self.svc_fdom_optionmenu.set_history(y)

  def add_tree_children(self, obj, iter):
    treemodel = self.svc_treeview.get_model()
    if obj.isRefObject() == TRUE:
      str_buf = SHARED_RESOURCE
    else:
      str_buf = PRIVATE_RESOURCE
    prettyname = self.rc_prettyname_hash[obj.getTagName()]
    treemodel.set(iter, R_NAME_COL, obj.getName(),
                        R_TYPE_COL, prettyname,
                        R_SCOPE_COL, str_buf,
                        R_OBJ_COL, obj)

    objs = obj.getChildren() 
    if len(objs) > 0:
      for ob in objs:
        child_iter = treemodel.append(iter, None)
        self.add_tree_children(ob, child_iter)

  def set_model(self, model_builder):
    self.model_builder = model_builder

  def prep_rc_options(self):
    menu = gtk.Menu()
    #self.rc_optionmenu_hash = {}
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

  def rc_optionmenu_change(self, widget):
    rc_idx = self.rc_options.get_history()
    tagname = self.rc_optionmenu_hash[rc_idx]
    ###
    rcs = self.rc_form_hash.keys()
    for rc in rcs: #hide all forms
      self.rc_form_hash[rc].hide()
    self.rc_form_hash[tagname].show()


  def rc_panel_ok(self, button):
    #first, find out if this is for edited props, or a new device
    selection = self.svc_treeview.get_selection()
    model,iter = selection.get_selected()
    r_obj = None
    type = None
    if iter != None:
      type = model.get_value(iter, R_TYPE_COL)
      r_obj = model.get_value(iter, R_OBJ_COL)
    if self.isNewResource == FALSE:  #edit
      tagname = r_obj.getTagName()
      if tagname == "ip":
        returnlist = self.rc_handler.validate_resource(tagname, r_obj.getAttribute("address"))
      else:
        returnlist = self.rc_handler.validate_resource(tagname, r_obj.getName())
      if returnlist != None:
        self.svc_rc_panel.hide()
        for k in returnlist.keys():
          r_obj.addAttribute(k, returnlist[k])
          self.model_builder.setModified()
        self.prep_service_tree()
                                                                                
    else: #New...
      dex = self.rc_options.get_history()
      tagname = self.rc_optionmenu_hash[dex]
      newobj = self.model_builder.createObjectFromTagname(tagname)
      returnlist = self.rc_handler.validate_resource(tagname, None)
      if returnlist != None:
        self.svc_rc_panel.hide()
        for x in returnlist.keys():
          newobj.addAttribute(x,returnlist[x])
        if self.isAttachedResource == FALSE:
          self.current_service.addChild(newobj)
        else:
          r_obj.addChild(newobj)
        self.model_builder.setModified()
        self.prep_service_tree()
                                                                                
  def rc_panel_cancel(self, button):
    self.svc_rc_panel.hide()
    self.isNewResource = FALSE
    self.isAttachedResource = FALSE
    self.rc_handler.clear_rc_forms()

  def on_shared_rc_ok(self, button):
    selection = self.shared_treeview.get_selection()
    model,iter = selection.get_selected()
    if iter == None:
      self.shared_rc_panel.hide()
      self.isNewResource = FALSE
      self.isAttachedResource = FALSE
      return
    r_obj = model.get_value(iter, S_OBJ_COL)
    rf = RefObject(r_obj)
    if self.isAttachedResource == TRUE:
      selection = self.svc_treeview.get_selection()
      smodel,iter = selection.get_selected()
      rc_obj = smodel.get_value(iter, R_OBJ_COL)
      rc_obj.addChild(rf)
    else:
      self.current_service.addChild(rf)
    self.model_builder.setModified()
                                                                                
  def on_shared_rc_cancel(self, button):
    self.shared_rc_panel.hide()
    self.isNewResource = FALSE
    self.isAttachedResource = FALSE
                                                                                
  def svc_rc_panel_delete(self, *args):
    self.svc_rc_panel.hide()
    self.isNewResource = FALSE
    self.isAttachedResource = FALSE
    return gtk.TRUE
 
  def shared_rc_panel_delete(self, *args):
    self.shared_rc_panel.hide()
    self.isNewResource = FALSE
    self.isAttachedResource = FALSE
    return gtk.TRUE

  def all_buttons_on(self): 
    self.attach_new_rc.set_sensitive(TRUE)
    self.attach_shared_rc.set_sensitive(TRUE)
    self.del_rc_button.set_sensitive(TRUE)
    self.edit_rc_button.set_sensitive(TRUE)

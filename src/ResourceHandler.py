import os

import gettext
_ = gettext.gettext

import gtk
import gtk.glade
from gtk import TRUE, FALSE
import MessageLibrary
import ModelBuilder
from ValidationError import ValidationError

NONE_PLACEHOLDER=_("None")

#ADDING A NEW RESOURCE: RC form should be named the same as its tagname in
#the glade file. Then add tagname to this list.

RC_OPTS = {"ip":_("IP Address"),
           "script":_("Script"),
           "nfsclient":_("NFS Client"),
           "nfsexport":_("NFS Export"),
           "fs":_("File System"),
           "group":_("Resource Group") }

class ResourceHandler:
  def __init__(self, rc_proxy_widget, model_builder):
    self.rc_proxy_widget = rc_proxy_widget
    self.model_builder = model_builder
    gladepath = "resources.glade"
    self.rc_xml = gtk.glade.XML(gladepath, domain="NULL")
    
    #generate hash table for rc_type -->  rc form
    self.rc_hash = { }
    rc_opt_keys = RC_OPTS.keys()
    for rc in rc_opt_keys:
      self.rc_hash[rc] = self.rc_xml.get_widget("rc_" + rc)

    self.pretty_rcname_hash = RC_OPTS

    self.rc_container = self.rc_xml.get_widget('rc_container')
    children = self.rc_container.get_children()
    for child in children:
      child.reparent(self.rc_proxy_widget)

    self.rc_populate_hash = {"ip":self.pop_ip,
                             "script":self.pop_script,
                             "nfsclient":self.pop_nfsclient,
                             "nfsexport":self.pop_nfsexport,
                             "fs":self.pop_fs,
                             "group":self.pop_group }

    self.rc_validate_hash = {"ip":self.val_ip,
                             "script":self.val_script,
                             "nfsclient":self.val_nfsclient,
                             "nfsexport":self.val_nfsexport,
                             "fs":self.val_fs,
                             "group":self.val_group }

    self.process_widgets()

  def get_pretty_rcname_hash(self):
    return self.pretty_rcname_hash

  def get_rc_hash(self):
    return self.rc_hash

  def populate_rc_form(self, tagname, *attrs):
    apply(self.rc_populate_hash[tagname], attrs)

  def pop_ip(self, attrs):
    pass

  def pop_script(self, attrs):
    pass

  def pop_nfsclient(self, attrs):
    pass

  def pop_nfsexport(self, attrs):
    pass

  def pop_fs(self, attrs):
    pass

  def pop_group(self, attrs):
    pass

 
  def clear_rc_forms(self):
    self.populate_group_optionmenu()

    self.ip0.set_text("")
    self.ip1.set_text("")
    self.ip2.set_text("")
    self.ip3.set_text("")
    self.monitor_link.set_active(TRUE)

    self.script_name.set_text("")
    self.script_filepath.set_text("")

    self.nfse_name.set_text("")

    self.nfsc_name.set_text("")
    self.nfsc_target.set_text("")
    self.nfsc_rw.set_active(TRUE)

    self.fs_name.set_text("")
    self.fs_mnt.set_text("")
    self.fs_device.set_text("")

    self.group_name.set_text("")

  #### Validation Methods
  def validate_resource(self, tagname, name=None):
    try:
      args = list()
      args.append(name)
      returnlist = apply(self.rc_validate_hash[tagname], args)
    except ValidationError, e:
      MessageLibrary.errorMessage(e.getMessage())
      return None

    return returnlist 

  def val_ip(self, name):
    pass

  def val_script(self, name):
    pass

  def val_nfsclient(self, name):
    pass

  def val_nfsexport(self, name):
    pass

  def val_fs(self, name):
    pass

  def val_group(self, name):
    pass

  def process_widgets(self):
    #self.fileselector = self.rc_xml.get_widget('fileselection1')

    self.ip0 = self.rc_xml.get_widget('entry1')
    self.ip1 = self.rc_xml.get_widget('entry2')
    self.ip2 = self.rc_xml.get_widget('entry3')
    self.ip3 = self.rc_xml.get_widget('entry4')
    self.monitor_link = self.rc_xml.get_widget('checkbutton1')

    self.script_name = self.rc_xml.get_widget('entry5')
    self.script_filepath = self.rc_xml.get_widget('entry6')
    #self.script_browse_button = self.rc_xml.get_widget('button1')

    self.nfse_name = self.rc_xml.get_widget('entry7')

    self.nfsc_name = self.rc_xml.get_widget('entry8')
    self.nfsc_target = self.rc_xml.get_widget('entry9')
    self.nfsc_rw = self.rc_xml.get_widget('radiobutton1')

    self.fs_name = self.rc_xml.get_widget('entry11')
    self.fs_optionmenu = self.rc_xml.get_widget('optionmenu2')
    self.fs_mnt = self.rc_xml.get_widget('entry12')
    self.fs_device = self.rc_xml.get_widget('fs_dev')

    self.group_name = self.rc_xml.get_widget('entry10')
    self.group_optionmenu = self.rc_xml.get_widget('optionmenu1')

  def populate_group_optionmenu(self):
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

    self.group_optionmenu.set_menu(menu)

import os

import gettext
_ = gettext.gettext

import gtk
import gtk.glade
from gtk import TRUE, FALSE
import MessageLibrary
import ModelBuilder
from ValidationError import ValidationError
from IPAddrEntry import IP

INSTALLDIR="/usr/share/system-config-cluster"

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
    if not os.path.exists(gladepath):
      gladepath = "%s/%s" % (INSTALLDIR,gladepath)

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
    addr = attrs["address"]
    self.ip.setAddrFromString(addr)
    monitor = attrs["monitor_link"]
    if (monitor == None) or (monitor == FALSE) or (monitor == "no"):
      self.monitor_link.set_active(FALSE)
    else:
      self.monitor_link.set_active(TRUE)

  def pop_script(self, attrs):
    self.script_name.set_text(attrs["name"])
    self.script_filepath.set_text(attrs["file"])

  def pop_nfsclient(self, attrs):
    self.nfsc_name.set_text(attrs["name"])
    self.nfsc_target.set_text(attrs["target"])
    if attrs["options"] == "rw":
      self.nfsc_rw.set_active(TRUE)
      self.nfsc_ro.set_active(FALSE)
    else:
      self.nfsc_ro.set_active(TRUE)
      self.nfsc_rw.set_active(FALSE)

  def pop_nfsexport(self, attrs):
    self.nfse_name.set_text(attrs["name"])

  def pop_fs(self, attrs):
    self.fs_name.set_text(attrs["name"])
    self.fs_mnt.set_text(attrs["mountpoint"])
    self.fs_device.set_text(attrs["device"])
   
    type = attrs["fstype"] 
    y = (-1)
    menu = self.fs_optionmenu.get_menu()
    for item in menu.get_children():
      y = y + 1
      children = item.get_children()
      if children:
        if item.get_children()[0].get_text() == type:
          break
    self.fs_optionmenu.set_history(y) 

  def pop_group(self, attrs):
    self.group_name.set_text(attrs["name"])
    domain = attrs["domain"]
    y = (-1)
    menu = self.group_optionmenu.get_menu()
    for item in menu.get_children():
      y = y + 1
      children = item.get_children()
      if children:
        if item.get_children()[0].get_text() == domain:
          break
    self.group_optionmenu.set_history(y) 

 
  def clear_rc_forms(self):
    self.populate_group_optionmenu()

    self.ip.clear()
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
    addr = self.ip.getAddrAsString()
    monitor = self.monitor_link.get_active()
    fields = {}
    fields["address"]= addr
    if monitor:
      fields["monitor_link"] = "1"
    else:
      fields["monitor_link"] = "0"

    return fields

  def val_script(self, name):

    script_name = self.script_name.get_text()
    if script_name == "":
      raise ValidationError('FATAL', RESOURCE_PROVIDE_NAME)

    if name != None:
      if name != script_name:
        res = self.check_unique_script_name(script_name)
        if res == FALSE:  #name already used for a script
          raise ValidationError('FATAL',RESOURCE_PROVIDE_NAME)

    filepath = self.script_filepath.get_text()
    
    fields = {}
    
    fields["name"] = script_name
    fields["file"] = filepath

    return fields

  def val_nfsclient(self, name):

    nfs_name = self.nfsc_name.get_text()
    if nfs_name == "":
      raise ValidationError('FATAL', RESOURCE_PROVIDE_NAME)

    if name != None:
      if name != nfs_name:
        res = self.check_unique_nfsc_name(nfs_name)
        if res == FALSE:  #name already used for an nfsc
          raise ValidationError('FATAL',RESOURCE_PROVIDE_NAME)

    fields = {}
    target = self.nfsc_target.get_text()
    opt = self.nfsc_rw.get_active()
    if opt == TRUE:
      option = "rw"
    else:
      option = "ro"

    fields["name"] = nfs_name
    fields["target"] = target
    fields["options"] = option

    return fields

  def val_nfsexport(self, name):

    nfs_name = self.nfse_name.get_text()
    if nfs_name == "":
      raise ValidationError('FATAL', RESOURCE_PROVIDE_NAME)

    if name != None:
      if name != nfs_name:
        res = self.check_unique_nfse_name(nfs_name)
        if res == FALSE:  #name already used for an nfsc
          raise ValidationError('FATAL',RESOURCE_PROVIDE_NAME)

    fields = {}
    fields["name"] = nfs_name

    return fields

  def val_fs(self, name):

    fs_name = self.fs_name.get_text()
    if fs_name == "":
      raise ValidationError('FATAL', RESOURCE_PROVIDE_NAME)

    if name != None:
      if name != fs_name:
        res = self.check_unique_fs_name(fs_name)
        if res == FALSE:  #name already used for an fs
          raise ValidationError('FATAL',RESOURCE_PROVIDE_NAME)

    fields = {}
    fields["name"] = fs_name
    mntp = self.fs_mnt.get_text()
    fields["mountpoint"] = mntp
    device = self.fs_device.get_text()
    fields["device"] = device
    fstypelabel = self.fs_optionmenu.get_children()[0]
    fstype = fstypelabel.get_text()
    fields["fstype"] = fstype

    return fields

  def val_group(self, name):
    pass

  def process_widgets(self):
    #self.fileselector = self.rc_xml.get_widget('fileselection1')

    self.ip = IP()
    self.ip.show_all()
    self.rc_xml.get_widget('ip_proxy').add(self.ip)
    self.monitor_link = self.rc_xml.get_widget('checkbutton1')

    self.script_name = self.rc_xml.get_widget('entry5')
    self.script_filepath = self.rc_xml.get_widget('entry6')
    #self.script_browse_button = self.rc_xml.get_widget('button1')

    self.nfse_name = self.rc_xml.get_widget('entry7')

    self.nfsc_name = self.rc_xml.get_widget('entry8')
    self.nfsc_target = self.rc_xml.get_widget('entry9')
    self.nfsc_rw = self.rc_xml.get_widget('radiobutton1')
    self.nfsc_ro = self.rc_xml.get_widget('radiobutton2')

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

  def set_model(self, model_builder):
    self.model_builder = model_builder

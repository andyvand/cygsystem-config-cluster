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

RESOURCE_PROVIDE_NAME=_("Please provide a name for this resource.")

RESOURCE_PROVIDE_UNIQUE_NAME=_("Please provide a unique name for this resource.")

PROVIDE_UNIQUE_IP=_("This IP Address is already declared as a resource. Please choose another.")

#ADDING A NEW RESOURCE: RC form should be named the same as its tagname in
#the glade file. Then add tagname to this list.

RC_OPTS = {"ip":_("IP Address"),
           "script":_("Script"),
           "nfsclient":_("NFS Client"),
           "nfsexport":_("NFS Export"),
           "netfs":_("NFS Mount"),
           "clusterfs":_("GFS"),
           "fs":_("File System") }

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
                             "netfs":self.pop_netfs,
                             "clusterfs":self.pop_clusterfs,
                             "fs":self.pop_fs }

    self.rc_validate_hash = {"ip":self.val_ip,
                             "script":self.val_script,
                             "nfsclient":self.val_nfsclient,
                             "nfsexport":self.val_nfsexport,
                             "netfs":self.val_netfs,
                             "clusterfs":self.val_clusterfs,
                             "fs":self.val_fs }

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

  def pop_netfs(self, attrs):
    try:
      self.netfs_name.set_text(attrs["name"])
    except KeyError, e:
      self.netfs_name.set_text("")

    try:
      self.netfs_mnt.set_text(attrs["mountpoint"])
    except KeyError, e:
      self.netfs_mnt.set_text("")

    try:
      self.netfs_host.set_text(attrs["host"])
    except KeyError, e:
      self.netfs_host.set_text("")

    try:
      self.netfs_export.set_text(attrs["export"])
    except KeyError, e:
      self.netfs_export.set_text("")

    try:
      fstype = attrs["fstype"]
      if fstype == "nfs":
        self.netfs_fstype.set_active(TRUE)
      else:
        self.netfs_fstype.set_active(FALSE)
    except KeyError, e:
      self.netfs_fstype.set_active(TRUE)

    try:
      force = attrs["force_unmount"]
      if force == "1" or force == "yes":
        self.netfs_force_unmount.set_active(TRUE)
      else:
        self.netfs_force_unmount.set_active(FALSE)
    except KeyError, e:
        self.netfs_force_unmount.set_active(FALSE)
 
    try:
      self.netfs_options.set_text(attrs["options"])
    except KeyError, e:
      self.netfs_options.set_text("")


  def pop_clusterfs(self, attrs):
    try:
      self.gfs_name.set_text(attrs["name"])
    except KeyError, e:
      self.gfs_name.set_text("")

    try:
      self.gfs_mnt.set_text(attrs["mountpoint"])
    except KeyError, e:
      self.gfs_mnt.set_text("")

    try:
      self.gfs_device.set_text(attrs["device"])
    except KeyError, e:
      self.gfs_host.set_text("")


    try:
      self.gfs_options.set_text(attrs["options"])
    except KeyError, e:
      self.gfs_options.set_text("")

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

  def clear_rc_forms(self):

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

    self.netfs_name.set_text("")
    self.netfs_mnt.set_text("")
    self.netfs_host.set_text("")
    self.netfs_export.set_text("")
    self.netfs_options.set_text("")
    self.netfs_force_unmount.set_active(FALSE)
    self.netfs_fstype.set_active(TRUE)

    self.gfs_name.set_text("")
    self.gfs_mnt.set_text("")
    self.gfs_device.set_text("")
    self.gfs_options.set_text("")


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

  def val_ip(self, *argname):
    inaddr = argname[0]
    addr = self.ip.getAddrAsString()
    if inaddr == None: #New resource...
      res = self.check_unique_ip(addr)
      if res == FALSE:  #adress already used
        raise ValidationError('FATAL',PROVIDE_UNIQUE_IP)
      
    else:
      if inaddr != addr:
        res = self.check_unique_ip(addr)
        if res == FALSE:  #address already used
          raise ValidationError('FATAL',PROVIDE_UNIQUE_IP)

    monitor = self.monitor_link.get_active()
    fields = {}
    fields["address"]= addr
    if monitor:
      fields["monitor_link"] = "1"
    else:
      fields["monitor_link"] = "0"

    return fields

  def val_script(self, *argname):
    name = argname[0]
    script_name = self.script_name.get_text()
    if script_name == "":
      raise ValidationError('FATAL', RESOURCE_PROVIDE_NAME)

    #This same method is used for validating names for all resources.
    #This could be a brand new resource, or an edited one.
    #If new, its name must be checked for duplicates, and if
    #a duplicate is found, an exception must be raised
    #If the resource is a new one, then the argname arg will be None
    #
    #If this is an edited resource, it's orig name must be
    #checked against the new name (argname[0])

    if name == None: #New resource...
      res = self.check_unique_script_name(script_name)
      if res == FALSE:  #name already used for a script
        raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)
      
    else:
      if name != script_name:
        res = self.check_unique_script_name(script_name)
        if res == FALSE:  #name already used for a script
          raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)

    filepath = self.script_filepath.get_text()
    
    fields = {}
    
    fields["name"] = script_name
    fields["file"] = filepath

    return fields

  def val_nfsclient(self, *argname):
    name = argname[0]

    nfs_name = self.nfsc_name.get_text()
    if nfs_name == "":
      raise ValidationError('FATAL', RESOURCE_PROVIDE_NAME)

    if name == None: #New resource...
      res = self.check_unique_nfsclient_name(nfs_name)
      if res == FALSE:  #name already used for a script
        raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)
      
    else:
      if name != nfs_name:
        res = self.check_unique_nfsclient_name(nfs_name)
        if res == FALSE:  #name already used for a script
          raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)

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

  def val_nfsexport(self, *argname):
    name = argname[0]

    nfs_name = self.nfse_name.get_text()
    if nfs_name == "":
      raise ValidationError('FATAL', RESOURCE_PROVIDE_NAME)

    if name == None: #New resource...
      res = self.check_unique_nfsexport_name(nfse_name)
      if res == FALSE:  #name already used for a script
        raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)
      
    else:
      if name != nfse_name:
        res = self.check_unique_nfsexport_name(nfse_name)
        if res == FALSE:  #name already used for a script
          raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)

    fields = {}
    fields["name"] = nfs_name

    return fields

  def val_netfs(self, *argname):
    name = argname[0]
    netfs_name = self.netfs_name.get_text()
    if netfs_name == "":
      raise ValidationError('FATAL', RESOURCE_PROVIDE_NAME)

    if name == None: #New resource...
      res = self.check_unique_netfs_name(netfs_name)
      if res == FALSE:  #name already used for a script
        raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)
      
    else:
      if name != netfs_name:
        res = self.check_unique_netfs_name(netfs_name)
        if res == FALSE:  #name already used for a script
          raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)

    fields = {}
    fields["name"] = netfs_name
    mntp = self.netfs_mnt.get_text()
    fields["mountpoint"] = mntp
    host = self.netfs_host.get_text()
    fields["host"] = host
    export = self.netfs_export.get_text()
    fields["export"] = export 
    if self.netfs_fstype.get_active() == TRUE:
      fstype = "nfs"
    else:
      fstype = "nfs4"
    fields["fstype"] = fstype
    options = self.netfs_options.get_text()
    fields["options"] = options
    unmount = self.netfs_force_unmount.get_active()
    if unmount == FALSE:
      umount = "0"
    else:
      umount = "1"
    fields["force_unmount"] = umount

    return fields

  def val_clusterfs(self, *argname):
    name = argname[0]
    gfs_name = self.gfs_name.get_text()
    if gfs_name == "":
      raise ValidationError('FATAL', RESOURCE_PROVIDE_NAME)

    if name == None: #New resource...
      res = self.check_unique_gfs_name(gfs_name)
      if res == FALSE:  #name already used for a script
        raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)
      
    else:
      if name != gfs_name:
        res = self.check_unique_gfs_name(gfs_name)
        if res == FALSE:  #name already used for a script
          raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)

    fields = {}
    fields["name"] = gfs_name
    mntp = self.gfs_mnt.get_text()
    fields["mountpoint"] = mntp
    device = self.gfs_device.get_text()
    fields["device"] = device
    options = self.gfs_options.get_text()
    fields["options"] = options

    return fields


  def val_fs(self, *argname):
    name = argname[0]
    fs_name = self.fs_name.get_text()
    if fs_name == "":
      raise ValidationError('FATAL', RESOURCE_PROVIDE_NAME)

    if name == None: #New resource...
      res = self.check_unique_fs_name(fs_name)
      if res == FALSE:  #name already used for a script
        raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)
      
    else:
      if name != gfs_name:
        res = self.check_unique_fs_name(fs_name)
        if res == FALSE:  #name already used for a script
          raise ValidationError('FATAL',RESOURCE_PROVIDE_UNIQUE_NAME)

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

    self.netfs_name = self.rc_xml.get_widget('entry16')
    self.netfs_mnt = self.rc_xml.get_widget('entry17')
    self.netfs_host = self.rc_xml.get_widget('entry18')
    self.netfs_export = self.rc_xml.get_widget('entry19')
    self.netfs_fstype = self.rc_xml.get_widget('nfs_button')
    self.netfs_force_unmount = self.rc_xml.get_widget('checkbutton2')
    self.netfs_options = self.rc_xml.get_widget('entry20')

    self.gfs_name = self.rc_xml.get_widget('gfs_name')
    self.gfs_mnt = self.rc_xml.get_widget('entry14')
    self.gfs_device = self.rc_xml.get_widget('entry15')
    self.gfs_options = self.rc_xml.get_widget('entry21')

    self.fs_name = self.rc_xml.get_widget('entry11')
    self.fs_optionmenu = self.rc_xml.get_widget('optionmenu2')
    self.fs_mnt = self.rc_xml.get_widget('entry12')
    self.fs_device = self.rc_xml.get_widget('fs_dev')

  def set_model(self, model_builder):
    self.model_builder = model_builder

  def check_unique_fs_name(self,fs_name):
    rcs = self.model_builder.getResources()
    for rc in rcs:
      if rc.getName() == fs_name:
        return FALSE

    return TRUE

  def check_unique_netfs_name(self,netfs_name):
    rcs = self.model_builder.getResources()
    for rc in rcs:
      if rc.getName() == netfs_name:
        return FALSE

    return TRUE

  def check_unique_gfs_name(self,gfs_name):
    rcs = self.model_builder.getResources()
    for rc in rcs:
      if rc.getName() == gfs_name:
        return FALSE

    return TRUE

  def check_unique_script_name(self,name):
    rcs = self.model_builder.getResources()
    for rc in rcs:
      if rc.getName() == name:
        return FALSE

    return TRUE

  def check_unique_ip(self,addr):
    rcs = self.model_builder.getResources()
    for rc in rcs:
      if rc.getName() == addr:
        return FALSE

    return TRUE

  def check_unique_nfsexport_name(self,name):
    rcs = self.model_builder.getResources()
    for rc in rcs:
      if rc.getName() == name:
        return FALSE

    return TRUE

  def check_unique_nfsclient_name(self,name):
    rcs = self.model_builder.getResources()
    for rc in rcs:
      if rc.getName() == name:
        return FALSE

    return TRUE


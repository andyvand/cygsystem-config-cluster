import os
import gtk
import gtk.glade
from gtk import TRUE, FALSE
from ValidationError import ValidationError
import MessageLibrary
import ModelBuilder

INSTALLDIR="/usr/share/system-config-cluster"

FD_PROVIDE_NAME = _("A unique name must be provided for each Fence Device")

FD_PROVIDE_PATH = _("An xCAT path must be provided for each xCAT Fence Device")
FD_PROVIDE_SERVER = _("A server address must be provided for this Fence Device")
FD_PROVIDE_CSERVER = _("A cserver address must be provided for this Egenera Fence Device")
FD_PROVIDE_IP = _("An IP address must be provided for this Fence Device")
FD_PROVIDE_LOGIN = _("A login name must be provided for this Fence Device")
FD_PROVIDE_PASSWD = _("A password must be provided for this Fence Device")
FI_PROVIDE_XCATNODENAME = _("An xCAT Nodename must be provided for this Fence")
FI_PROVIDE_SWITCH = _("A switch address must be provided for this Fence")
FI_PROVIDE_PORT = _("A port value must be provided for this Fence")
FI_PROVIDE_PORT = _("A Blade must be specified for this Fence")
FI_PROVIDE_IPADDRESS = _("An IP address must be provided for this Fence")
FI_PROVIDE_ELPAN = _("A LPAN value must be provided for this Egenera Fence")
FI_PROVIDE_EPSERVER = _("A PServer value must be provided for this Egenera Fence")


#ADDING A NEW FENCE: fence instance form should be named the same as its agent
#in gladefile. Then add agent name to this list.
#
#In Glade File, fence device form should be added to 'fence_device_container'
#and fence instance form to fence_instance_container
#
#For every new fence added, there will be a fence instance and fence device
#form needed. There will also be a populate and a validate method for each
#form. The methods will need to be added to this file, and the four hash
#tables (self.fi_populate, self.fi_validate, self.fd_populate, 
#self.fd_validate) must be updated. The methods will use fields in the
#forms to set_text and to check.

FENCE_OPTS = {"fence_apc":_("APC Power Device"),
              "fence_wti":_("WTI Power Device"),
              "fence_brocade":_("Brocade Switch"),
              "fence_vixel":_("Vixel SAN Switch"),
              "fence_gnbd":_("Global Network Block Device"),
              "fence_ilo":_("HP ILO Device"),
              "fence_sanbox2":_("QLogic SANBox2"),
              "fence_bladecenter":_("IBM Blade Center"),
              "fence_mcdata":_("McDATA SAN Switch"),
              "fence_egenera":_("Egenera SAN Controller"),
              "fence_manual":_("Manual Fencing") }

FENCE_FD_ATTRS = {"fence_apc":["name","ipaddr","login","passwd"],
              "fence_wti":["name","ipaddr","passwd"],
              "fence_brocade":["name","ipaddr","login","passwd"],
              "fence_vixel":["name","ipaddr","passwd"],
              "fence_gnbd":["name","server"],
              "fence_ilo":["name","hostname","login","passwd"],
              "fence_sanbox2":["name","ipaddr","login","passwd"],
              "fence_bladecenter":["name","ipaddr","login","passwd"],
              "fence_mcdata":["name","ipaddr","login","passwd"],
              "fence_egenera":["name","cserver"],
              "fence_manual":["name"] }

FENCE_FI_ATTRS = {"fence_apc":["port","switch"],
              "fence_wti":["port"],
              "fence_brocade":["port"],
              "fence_vixel":["port"],
              "fence_gnbd":["ipaddress"],
              "fence_ilo":[],
              "fence_sanbox2":["port"],
              "fence_bladecenter":["blade"],
              "fence_mcdata":["port"],
              "fence_egenera":["lpan","pserver"],
              "fence_manual":[] }

PRETTY_NAME_ATTRS = {"port":_("Port"),
                     "blade":_("Blade"), 
                     "switch":_("Switch"),
                     "ipaddr":_("IP Address"),
                     "nodename":_("Nodename"),
                     "lpan":_("LPAN"),
                     "pserver":_("PServer"),
                     "login":_("Login"),
                     "passwd":_("Password"),
                     "name":_("Name"),
                     "server":_("Server"),
                     "hostname":_("Hostname"),
                     "path":_("Path"),
                     "cserver":_("CServer") }  

class FenceHandler:
  def __init__(self, fi_proxy_widget, fd_proxy_widget, model_builder):
    self.fi_proxy_widget = fi_proxy_widget
    self.fd_proxy_widget = fd_proxy_widget
    self.model_builder = model_builder
    gladepath = "fence.glade"
    if not os.path.exists(gladepath):
      gladepath = "%s/%s" % (INSTALLDIR,gladepath)
                                                                                
    #gtk.glade.bindtextdomain(PROGNAME)
    self.fence_xml = gtk.glade.XML (gladepath, domain="NULL")

    #Generate hash table for agent --> fence instance form
    self.fi_hash = { }
    fence_opt_keys = FENCE_OPTS.keys()
    for fence in fence_opt_keys:
      self.fi_hash[fence] = self.fence_xml.get_widget(fence)

    #Generate hash table for agent --> fence device form
    self.fd_hash = { }
    fence_opt_keys = FENCE_OPTS.keys()
    for fence in fence_opt_keys:
      self.fd_hash[fence] = self.fence_xml.get_widget(fence + "_d")

    self.pretty_agentname_hash = FENCE_OPTS

    self.fi_container = self.fence_xml.get_widget('fence_instance_container')
    children = self.fi_container.get_children()
    for child in children:
      child.reparent(self.fi_proxy_widget)
    
    self.fd_container = self.fence_xml.get_widget('fence_device_container')
    children = self.fd_container.get_children()
    for child in children:
      child.reparent(self.fd_proxy_widget)
    
    #For testing...
    #self.fence_xml.get_widget('fi_wti').show()

    self.fi_populate = {"fence_apc":self.pop_apc,
              "fence_wti":self.pop_wti,
              "fence_brocade":self.pop_brocade,
              "fence_vixel":self.pop_vixel,
              "fence_gnbd":self.pop_gnbd,
              "fence_ilo":self.pop_ilo,
              "fence_sanbox2":self.pop_sanbox2,
              "fence_bladecenter":self.pop_bladecenter,
              "fence_mcdata":self.pop_mcdata,
              "fence_egenera":self.pop_egenera,
              "fence_manual":self.pop_manual }

    self.fd_populate = {"fence_apc":self.pop_apc_fd,
              "fence_wti":self.pop_wti_fd,
              "fence_brocade":self.pop_brocade_fd,
              "fence_vixel":self.pop_vixel_fd,
              "fence_gnbd":self.pop_gnbd_fd,
              "fence_ilo":self.pop_ilo_fd,
              "fence_sanbox2":self.pop_sanbox2_fd,
              "fence_bladecenter":self.pop_bladecenter_fd,
              "fence_mcdata":self.pop_mcdata_fd,
              "fence_egenera":self.pop_egenera_fd,
              "fence_manual":self.pop_manual_fd }

    self.fi_validate = {"fence_apc":self.val_apc,
              "fence_wti":self.val_wti,
              "fence_brocade":self.val_brocade,
              "fence_vixel":self.val_vixel,
              "fence_gnbd":self.val_gnbd,
              "fence_ilo":self.val_ilo,
              "fence_sanbox2":self.val_sanbox2,
              "fence_bladecenter":self.val_bladecenter,
              "fence_mcdata":self.val_mcdata,
              "fence_egenera":self.val_egenera,
              "fence_manual":self.val_manual }

    self.fd_validate = {"fence_apc":self.val_apc_fd,
              "fence_wti":self.val_wti_fd,
              "fence_brocade":self.val_brocade_fd,
              "fence_vixel":self.val_vixel_fd,
              "fence_gnbd":self.val_gnbd_fd,
              "fence_ilo":self.val_ilo_fd,
              "fence_sanbox2":self.val_sanbox2_fd,
              "fence_bladecenter":self.val_bladecenter_fd,
              "fence_mcdata":self.val_mcdata_fd,
              "fence_egenera":self.val_egenera_fd,
              "fence_manual":self.val_manual_fd }

    self.process_widgets()

  def get_fence_instance_hash(self):
    return self.fi_hash

  def get_fence_device_hash(self):
    return self.fd_hash

  def populate_fi_form(self, agent_type, *attrs):
    apply(self.fi_populate[agent_type], attrs)

  def populate_fd_form(self, agent_type, *attrs):
    apply(self.fd_populate[agent_type], attrs)

  def pop_apc(self, attrs):
    self.apc_port.set_text(attrs["port"]) 
    self.apc_switch.set_text(attrs["switch"]) 
 
  def pop_wti(self, attrs):
    self.wti_port.set_text(attrs["port"])
 
  def pop_brocade(self, attrs):
    self.brocade_port.set_text(attrs["port"])
 
  def pop_ilo(self, attrs):
    pass
 
  def pop_vixel(self, attrs):
    self.vixel_port_text(attrs["port"])
 
  def pop_mcdata(self, attrs):
    self.mcdata_port.set_text(attrs["port"])
 
  def pop_manual(self, attrs):
    pass
 
  def pop_gnbd(self, attrs):
    self.gnbd_ip.set_text(attrs["ipaddress"])
 
  def pop_egenera(self, attrs):
    self.egenera_lpan.set_text(attrs["lpan"])
    self.egenera_pserver.set_text(attrs["pserver"])
 
  def pop_sanbox2(self, attrs):
    self.sanbox2_port.set_text(attrs["port"])

  def pop_bladecenter(self, attrs):
    self.bladecenter_blade.set_text(attrs["blade"])

  def clear_fi_forms(self):
    self.apc_port.set_text("") 
    self.apc_switch.set_text("") 
    self.wti_port.set_text("") 
    self.brocade_port.set_text("")
    self.vixel_port.set_text("")
    self.gnbd_ip.set_text("") 
    self.sanbox2_port.set_text("")
    self.bladecenter_blade.set_text("")
    self.mcdata_port.set_text("")
    self.egenera_lpan.set_text("")
    self.egenera_pserver.set_text("")


  def clear_fd_forms(self):
    self.apc_fd_name.set_text("") 
    self.apc_fd_ip.set_text("")
    self.apc_fd_login.set_text("")
    self.apc_fd_passwd.set_text("")
    self.wti_fd_ip.set_text("")
    self.wti_fd_name.set_text("")
    self.wti_fd_passwd.set_text("")
    self.brocade_fd_name.set_text("")
    self.brocade_fd_ip.set_text("")
    self.brocade_fd_login.set_text("")
    self.brocade_fd_passwd.set_text("")
    self.ilo_fd_name.set_text("")
    self.ilo_fd_login.set_text("")
    self.ilo_fd_passwd.set_text("")
    self.ilo_fd_hostname.set_text("")
    self.vixel_fd_name.set_text("")
    self.vixel_fd_ip.set_text("")
    self.vixel_fd_passwd.set_text("")
    self.manual_fd_name.set_text("")
    self.mcdata_fd_name.set_text("")
    self.mcdata_fd_ip.set_text("")
    self.mcdata_fd_login.set_text("")
    self.mcdata_fd_passwd.set_text("")
    self.gnbd_fd_name.set_text("")
    self.gnbd_fd_server.set_text("")
    self.egenera_fd_name.set_text("")
    self.egenera_fd_cserver.set_text("")
    self.sanbox2_fd_name.set_text("")
    self.sanbox2_fd_ip.set_text("")
    self.sanbox2_fd_login.set_text("")
    self.sanbox2_fd_passwd.set_text("")
    self.bladecenter_fd_name.set_text("")
    self.bladecenter_fd_ip.set_text("")
    self.bladecenter_fd_login.set_text("")
    self.bladecenter_fd_passwd.set_text("")

  #Populate form methods for Fence Devices
  def pop_apc_fd(self, attrs):
    self.apc_fd_name.set_text(attrs["name"]) 
    self.apc_fd_ip.set_text(attrs["ipaddr"])
    self.apc_fd_login.set_text(attrs["login"])
    self.apc_fd_passwd.set_text(attrs["passwd"])

 
  def pop_wti_fd(self, attrs):
    self.wti_fd_ip.set_text(attrs["ipaddr"])
    self.wti_fd_name.set_text(attrs["name"])
    self.wti_fd_passwd.set_text(attrs["passwd"])
 
  def pop_brocade_fd(self, attrs):
    self.brocade_fd_name.set_text(attrs["name"])
    self.brocade_fd_ip.set_text(attrs["ipaddr"])
    self.brocade_fd_login.set_text(attrs["login"])
    self.brocade_fd_passwd.set_text(attrs["passwd"])

 
  def pop_ilo_fd(self, attrs):
    self.ilo_fd_name.set_text(attrs["name"])
    self.ilo_fd_login.set_text(attrs["login"])
    self.ilo_fd_passwd.set_text(attrs["passwd"])
    self.ilo_fd_hostname.set_text(attrs["hostname"])

 
  def pop_vixel_fd(self, attrs):
    self.vixel_fd_name.set_text(attrs["name"])
    self.vixel_fd_ip.set_text(attrs["ipaddr"])
    self.vixel_fd_passwd.set_text(attrs["passwd"])

 
  def pop_mcdata_fd(self, attrs):
    self.mcdata_fd_name.set_text(attrs["name"])
    self.mcdata_fd_ip.set_text(attrs["ipaddr"])
    self.mcdata_fd_login.set_text(attrs["login"])
    self.mcdata_fd_passwd.set_text(attrs["passwd"])

 
  def pop_manual_fd(self, attrs):
    self.manual_fd_name.set_text(attrs["name"])
 
  def pop_gnbd_fd(self, attrs):
    self.gnbd_fd_name.set_text(attrs["name"])
    self.gnbd_fd_server.set_text(attrs["server"])

 
  def pop_egenera_fd(self, attrs):
    self.egenera_fd_name.set_text(attrs["name"])
    self.egenera_fd_cserver.set_text(attrs["cserver"])

 
  def pop_sanbox2_fd(self, attrs):
    self.sanbox2_fd_name.set_text(attrs["name"])
    self.sanbox2_fd_ip.set_text(attrs["ipaddr"])
    self.sanbox2_fd_login.set_text(attrs["login"])
    self.sanbox2_fd_passwd.set_text(attrs["passwd"])

  def pop_bladecenter_fd(self, attrs):
    self.bladecenter_fd_name.set_text(attrs["name"])
    self.bladecenter_fd_ip.set_text(attrs["ipaddr"])
    self.bladecenter_fd_login.set_text(attrs["login"])
    self.bladecenter_fd_passwd.set_text(attrs["passwd"])


  def process_widgets(self):
    ##Fence Instance Form Fields
    self.apc_port = self.fence_xml.get_widget('entry1') 
    self.apc_switch = self.fence_xml.get_widget('entry2') 
    self.wti_port = self.fence_xml.get_widget('entry3') 
    self.brocade_port = self.fence_xml.get_widget('entry4') 
    self.vixel_port = self.fence_xml.get_widget('entry5') 
    self.gnbd_ip = self.fence_xml.get_widget('entry6') 
    self.ilo_port = self.fence_xml.get_widget('entry7') 
    self.sanbox2_port = self.fence_xml.get_widget('entry8') 
    self.bladecenter_blade = self.fence_xml.get_widget('entry41') 
    self.mcdata_port = self.fence_xml.get_widget('entry9') 
    self.egenera_lpan = self.fence_xml.get_widget('entry10') 
    self.egenera_pserver = self.fence_xml.get_widget('entry11') 

    ##Fence Device Forms
    self.apc_fd_name = self.fence_xml.get_widget('entry12')
    self.apc_fd_ip = self.fence_xml.get_widget('entry13')
    self.apc_fd_login = self.fence_xml.get_widget('entry14')
    self.apc_fd_passwd = self.fence_xml.get_widget('entry15')

    self.wti_fd_ip = self.fence_xml.get_widget('entry17')
    self.wti_fd_name = self.fence_xml.get_widget('entry16')
    self.wti_fd_passwd = self.fence_xml.get_widget('entry18')

    self.brocade_fd_name = self.fence_xml.get_widget('entry19')
    self.brocade_fd_ip = self.fence_xml.get_widget('entry20')
    self.brocade_fd_login = self.fence_xml.get_widget('entry21')
    self.brocade_fd_passwd = self.fence_xml.get_widget('entry22')

    self.vixel_fd_name = self.fence_xml.get_widget('entry23')
    self.vixel_fd_ip = self.fence_xml.get_widget('entry24')
    self.vixel_fd_passwd = self.fence_xml.get_widget('entry25')

    self.gnbd_fd_name = self.fence_xml.get_widget('entry26')
    self.gnbd_fd_server = self.fence_xml.get_widget('entry27')

    self.ilo_fd_name = self.fence_xml.get_widget('entry28')
    self.ilo_fd_login = self.fence_xml.get_widget('entry29')
    self.ilo_fd_passwd = self.fence_xml.get_widget('entry30')
    self.ilo_fd_hostname = self.fence_xml.get_widget('entry31')

    self.sanbox2_fd_name = self.fence_xml.get_widget('entry32')
    self.sanbox2_fd_ip = self.fence_xml.get_widget('entry33')
    self.sanbox2_fd_login = self.fence_xml.get_widget('entry46')
    self.sanbox2_fd_passwd = self.fence_xml.get_widget('entry47')

    self.bladecenter_fd_name = self.fence_xml.get_widget('entry42')
    self.bladecenter_fd_ip = self.fence_xml.get_widget('entry43')
    self.bladecenter_fd_login = self.fence_xml.get_widget('entry44')
    self.bladecenter_fd_passwd = self.fence_xml.get_widget('entry45')

    self.mcdata_fd_name = self.fence_xml.get_widget('entry34')
    self.mcdata_fd_ip = self.fence_xml.get_widget('entry35')
    self.mcdata_fd_login = self.fence_xml.get_widget('entry36')
    self.mcdata_fd_passwd = self.fence_xml.get_widget('entry37')

    self.egenera_fd_name = self.fence_xml.get_widget('entry38')
    self.egenera_fd_cserver = self.fence_xml.get_widget('entry39')

    self.manual_fd_name = self.fence_xml.get_widget('entry40')

  #####  Validation Methods
  def validate_fencedevice(self, agent_type, name=None):
    try:
      args = list()
      args.append(name)
      returnlist = apply(self.fd_validate[agent_type], args)
    except ValidationError, e:
      MessageLibrary.errorMessage(e.getMessage())
      return None

    return returnlist

  def val_apc_fd(self, name):
    if self.apc_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    if name != self.apc_fd_name.get_text():
      res = self.check_unique_fd_name(self.apc_fd_name.get_text())
      if res == FALSE:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if self.apc_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)
    if self.apc_fd_login.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_LOGIN)
    if self.apc_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    fields = {}
    fields["name"] = self.apc_fd_name.get_text()
    fields["ipaddress"] = self.apc_fd_ip.get_text()
    fields["login"] = self.apc_fd_login.get_text()
    fields["password"] = self.apc_fd_passwd.get_text()

    return fields
 
 
  def val_wti_fd(self, name):
    if self.wti_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    if name != self.wti_fd_name.get_text():
      res = self.check_unique_fd_name(self.wti_fd_name.get_text())
      if res == FALSE:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if self.wti_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)
    if self.wti_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    fields = {}
    fields["name"] = self.wti_fd_name.get_text()
    fields["ipaddress"] = self.wti_fd_ip.get_text()
    fields["password"] = self.wti_fd_passwd.get_text()

    return fields
 
 
  def val_brocade_fd(self, name):
    if self.brocade_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    if name != self.brocade_fd_name.get_text():
      res = self.check_unique_fd_name(self.brocade_fd_name.get_text())
      if res == FALSE:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if self.brocade_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)
    if self.brocade_fd_login.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_LOGIN)
    if self.brocade_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    fields = {}
    fields["name"] = self.brocade_fd_name.get_text()
    fields["ipaddress"] = self.brocade_fd_ip.get_text()
    fields["login"] = self.brocade_fd_login.get_text()
    fields["password"] = self.brocade_fd_passwd.get_text()

    return fields
 
 
  def val_ilo_fd(self, name):
    if self.ilo_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    if name != self.ilo_fd_name.get_text():
      res = self.check_unique_fd_name(self.ilo_fd_name.get_text())
      if res == FALSE:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if self.ilo_fd_login.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_LOGIN)
    if self.ilo_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)
    if self.ilo_fd_hostname.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_HOSTNAME)

    fields = {}
    fields["name"] = self.ilo_fd_name.get_text()
    fields["hostname"] = self.ilo_fd_hostname.get_text()
    fields["login"] = self.ilo_fd_login.get_text()
    fields["password"] = self.ilo_fd_passwd.get_text()

    return fields
 
 
  def val_vixel_fd(self, name):
    if self.vixel_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    if name != self.vixel_fd_name.get_text():
      res = self.check_unique_fd_name(self.vixel_fd_name.get_text())
      if res == FALSE:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if self.vixel_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)
    if self.vixel_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    fields = {}
    fields["name"] = self.vixel_fd_name.get_text()
    fields["ipaddress"] = self.vixel_fd_ip.get_text()
    fields["password"] = self.vixel_fd_passwd.get_text()

    return fields
 
 
  def val_mcdata_fd(self, name):
    if self.mcdata_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    if name != self.mcdata_fd_name.get_text():
      res = self.check_unique_fd_name(self.mcdata_fd_name.get_text())
      if res == FALSE:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if self.mcdata_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)
    if self.mcdata_fd_login.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_LOGIN)
    if self.mcdata_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    fields = {}
    fields["name"] = self.mcdata_fd_name.get_text()
    fields["ipaddress"] = self.mcdata_fd_ip.get_text()
    fields["login"] = self.mcdata_fd_login.get_text()
    fields["password"] = self.mcdata_fd_passwd.get_text()

    return fields
 
  def val_manual_fd(self, name):
    if self.manual_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    if name != self.manual_fd_name.get_text():
      res = self.check_unique_fd_name(self.manual_fd_name.get_text())
      if res == FALSE:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)

    fields = {}
    fields["name"] = self.manual_fd_name.get_text()

    return fields
 
  def val_gnbd_fd(self, name):
    if self.gnbd_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    if name != self.gnbd_fd_name.get_text():
      res = self.check_unique_fd_name(self.gnbd_fd_name.get_text())
      if res == FALSE:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if self.gnbd_fd_server.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_SERVER)

    fields = {}
    fields["name"] = self.gnbd_fd_name.get_text()
    fields["server"] = self.gnbd_fd_server.get_text()

    return fields
 
  def val_egenera_fd(self, name):
    if self.egenera_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    if name != self.egenera_fd_name.get_text():
      res = self.check_unique_fd_name(self.egenera_fd_name.get_text())
      if res == FALSE:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if self.egenera_fd_cserver.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_CSERVER)

    fields = {}
    fields["name"] = self.egenera_fd_name.get_text()
    fields["cserver"] = self.egenera_fd_cserver.get_text()

    return fields

 
  def val_sanbox2_fd(self, name):
    if self.sanbox2_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if name != self.sanbox2_fd_name.get_text():
      res = self.check_unique_fd_name(self.sanbox2_fd_name.get_text())
      if res == FALSE:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if self.sanbox2_fd_ip.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_IP)

    if self.sanbox2_fd_login.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_LOGIN)

    if self.sanbox2_fd_passwd.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    fields = {}
    fields["name"] = self.sanbox2_fd_name.get_text()
    fields["ipaddr"] = self.sanbox2_fd_ip.get_text()
    fields["login"] = self.sanbox2_fd_login.get_text()
    fields["passwd"] = self.sanbox2_fd_passwd.get_text()

    return fields

  def val_bladecenter_fd(self, name):
    if self.bladecenter_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if name != self.bladecenter_fd_name.get_text():
      res = self.check_unique_fd_name(self.bladecenter_fd_name.get_text())
      if res == FALSE:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)

    if self.bladecenter_fd_ip.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_IP)

    if self.bladecenter_fd_login.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_LOGIN)

    if self.bladecenter_fd_passwd.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    fields = {}
    fields["name"] = self.bladecenter_fd_name.get_text()
    fields["ipaddr"] = self.bladecenter_fd_ip.get_text()
    fields["login"] = self.bladecenter_fd_login.get_text()
    fields["passwd"] = self.bladecenter_fd_passwd.get_text()

    return fields

  #Validation Methods for Fence Instances 
  def validate_fenceinstance(self, agent_type):
    try:
      returnlist = apply(self.fi_validate[agent_type])
    except ValidationError, e:
      MessageLibrary.errorMessage(e.getMessage())
      return None

    return returnlist

  def val_apc(self):
    if self.apc_port.get_text() == "": 
      raise ValidationError('FATAL', FI_PROVIDE_PORT)
    if self.apc_switch.get_text() == "": 
      raise ValidationError('FATAL', FI_PROVIDE_SWITCH)

    fields = {}
    fields["port"] = self.apc_port.get_text()
    fields["switch"] = self.apc_switch.get_text()

    return fields

  def val_wti(self):
    if self.wti_port.get_text() == "":
      raise ValidationError('FATAL', FI_PROVIDE_PORT)

    fields = {}
    fields["port"] = self.wti_port.get_text()

    return fields

  def val_brocade(self):
    if self.brocade_port.get_text() == "":
      raise ValidationError('FATAL', FI_PROVIDE_PORT)

    fields = {}
    fields["port"] = self.brocade_port.get_text()

    return fields

  def val_vixel(self):
    if self.vixel_port.get_text() == "": 
      raise ValidationError('FATAL', FI_PROVIDE_PORT)

    fields = {}
    fields["port"] = self.vixel_port.get_text()

    return fields

  def val_gnbd(self):
    if self.gnbd_ip.get_text() == "": 
      raise ValidationError('FATAL', FI_PROVIDE_IPADDRESS)

    fields = {}
    fields["ipaddress"] = self.gnbd_ip.get_text()

    return fields

  def val_ilo(self):

    fields = {}

    return fields

  def val_sanbox2(self):
    if self.sanbox2_port.get_text() == "": 
      raise ValidationError('FATAL', FI_PROVIDE_PORT)

    fields = {}
    fields["port"] = self.sanbox2_port.get_text()

    return fields

  def val_bladecenter(self):
    if self.bladecenter_blade.get_text() == "": 
      raise ValidationError('FATAL', FI_PROVIDE_BLADE)

    fields = {}
    fields["blade"] = self.bladecenter_blade.get_text()

    return fields

  def val_mcdata(self):
    if self.mcdata_port.get_text() == "":
      raise ValidationError('FATAL', FI_PROVIDE_PORT)

    fields = {}
    fields["port"] = self.mcdata_port.get_text()

    return fields

  def val_egenera(self):
    if self.egenera_lpan.get_text() == "":
      raise ValidationError('FATAL', FI_PROVIDE_ELPAN)
    if self.egenera_pserver.get_text() == "":
      raise ValidationError('FATAL', FI_PROVIDE_EPSERVER)

    fields = {}
    fields["lpan"] = self.egenera_lpan.get_text()
    fields["pserver"] = self.egenera_pserver.get_text()

    return fields

  def val_manual(self): 

    fields = {}
    return fields

  def check_unique_fd_name(self, name):
    fds = self.model_builder.getFenceDevices()
    for fd in fds:
      if fd.getName() == name:
        return FALSE

    return TRUE

  def getFENCE_OPTS(self):
    return FENCE_OPTS

  def set_model(self, model_builder):
    self.model_builder = model_builder

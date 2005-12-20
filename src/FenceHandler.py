import os
import gtk
import gtk.glade
from ValidationError import ValidationError
import MessageLibrary
import ModelBuilder

INSTALLDIR="/usr/share/system-config-cluster"

FD_PROVIDE_NAME = _("A unique name must be provided for each Fence Device")
FD_NAME_EQUAL_TO_NODE_NAME = _("There is a Cluster Node named \"%s\". Fence Devices cannot have the same names as Cluster Nodes. Please choose another name for this Fence Device.")

FD_PROVIDE_PATH = _("An xCAT path must be provided for each xCAT Fence Device")
FD_PROVIDE_SERVERS = _("Servers' names or addresses, separated by whitespaces, must be provided for this Fence Device")
FD_PROVIDE_CSERVER = _("A cserver address must be provided for this Egenera Fence Device")
FD_PROVIDE_IP = _("An IP address must be provided for this Fence Device")
FD_PROVIDE_LOGIN = _("A login name must be provided for this Fence Device")
FD_PROVIDE_PASSWD = _("A password must be provided for this Fence Device")
FD_PROVIDE_DEVICE = _("A device path must be provided for this Fence Device")
FI_PROVIDE_XCATNODENAME = _("An xCAT Nodename must be provided for this Fence")
FI_PROVIDE_SWITCH = _("A switch address must be provided for this Fence")
FI_PROVIDE_PORT = _("A port value must be provided for this Fence")
FI_PROVIDE_BLADE = _("A Blade must be specified for this Fence")
FI_PROVIDE_DOMAIN = _("A Domain must be specified for this Fence")
FI_PROVIDE_IPADDRESS = _("An IP address must be provided for this Fence")
FI_PROVIDE_ELPAN = _("A LPAN value must be provided for this Egenera Fence")
FI_PROVIDE_EPSERVER = _("A PServer value must be provided for this Egenera Fence")

ILLEGAL_CHARS_REPLACED = _("Illegal characters were replaced by underscores. Feel free to set a new value.")
ILLEGAL_CHARS = [':', ' ']

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
              "fence_rps10":("RPS10 Serial Switch"),
              "fence_brocade":_("Brocade Switch"),
              "fence_vixel":_("Vixel SAN Switch"),
              "fence_gnbd":_("Global Network Block Device"),
              "fence_ilo":_("HP ILO Device"),
              "fence_sanbox2":_("QLogic SANBox2"),
              "fence_bladecenter":_("IBM Blade Center"),
              "fence_mcdata":_("McDATA SAN Switch"),
              "fence_egenera":_("Egenera SAN Controller"),
              "fence_bullpap":_("Bull PAP"),
              "fence_drac":_("DRAC"),
              "fence_ipmilan":_("IPMI Lan"),
              "fence_manual":_("Manual Fencing") }

FENCE_FD_ATTRS = {"fence_apc":["name","ipaddr","login","passwd"],
              "fence_wti":["name","ipaddr","passwd"],
              "fence_rps10":["name","device","port"],
              "fence_brocade":["name","ipaddr","login","passwd"],
              "fence_vixel":["name","ipaddr","passwd"],
              "fence_gnbd":["name","servers"],
              "fence_ilo":["name","hostname","login","passwd"],
              "fence_sanbox2":["name","ipaddr","login","passwd"],
              "fence_bladecenter":["name","ipaddr","login","passwd"],
              "fence_mcdata":["name","ipaddr","login","passwd"],
              "fence_egenera":["name","cserver"],
              "fence_ipmilan":["name","ipaddr","login","passwd"],
              "fence_bullpap":["name","ipaddr","login","passwd"],
              "fence_drac":["name","ipaddr","login","passwd"],
              "fence_manual":["name"] }

FENCE_FI_ATTRS = {"fence_apc":["port","switch"],
              "fence_wti":["port"],
              "fence_rps10":[],
              "fence_brocade":["port"],
              "fence_vixel":["port"],
              "fence_gnbd":[],
              "fence_ilo":[],
              "fence_sanbox2":["port"],
              "fence_bladecenter":["blade"],
              "fence_mcdata":["port"],
              "fence_egenera":["lpan","pserver"],
              "fence_ipmilan":[],
              "fence_bullpap":["domain"],
              "fence_drac":[],
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
                     "device":_("Device"),
                     "server":_("Server"),
                     "servers":_("Servers"),
                     "domain":_("Domain"),
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
    
    self.fi_container2 = self.fence_xml.get_widget('fence_instance_container2')
    children2 = self.fi_container2.get_children()
    for child in children2:
      child.reparent(self.fi_proxy_widget)
    
    self.fd_container = self.fence_xml.get_widget('fence_device_container')
    children = self.fd_container.get_children()
    for child in children:
      child.reparent(self.fd_proxy_widget)
    
    self.fd_container2 = self.fence_xml.get_widget('fence_device_container2')
    children2 = self.fd_container2.get_children()
    for child in children2:
      child.reparent(self.fd_proxy_widget)
    
    #For testing...
    #self.fence_xml.get_widget('fi_wti').show()

    self.fi_populate = {"fence_apc":self.pop_apc,
              "fence_wti":self.pop_wti,
              "fence_rps10":self.pop_rps10,
              "fence_brocade":self.pop_brocade,
              "fence_vixel":self.pop_vixel,
              "fence_gnbd":self.pop_gnbd,
              "fence_ilo":self.pop_ilo,
              "fence_drac":self.pop_drac,
              "fence_sanbox2":self.pop_sanbox2,
              "fence_bladecenter":self.pop_bladecenter,
              "fence_mcdata":self.pop_mcdata,
              "fence_egenera":self.pop_egenera,
              "fence_ipmilan":self.pop_ipmilan,
              "fence_bullpap":self.pop_bullpap,
              "fence_manual":self.pop_manual }

    self.fd_populate = {"fence_apc":self.pop_apc_fd,
              "fence_wti":self.pop_wti_fd,
              "fence_rps10":self.pop_rps10_fd,
              "fence_brocade":self.pop_brocade_fd,
              "fence_vixel":self.pop_vixel_fd,
              "fence_gnbd":self.pop_gnbd_fd,
              "fence_ilo":self.pop_ilo_fd,
              "fence_drac":self.pop_drac_fd,
              "fence_sanbox2":self.pop_sanbox2_fd,
              "fence_bladecenter":self.pop_bladecenter_fd,
              "fence_mcdata":self.pop_mcdata_fd,
              "fence_egenera":self.pop_egenera_fd,
              "fence_ipmilan":self.pop_ipmilan_fd,
              "fence_bullpap":self.pop_bullpap_fd,
              "fence_manual":self.pop_manual_fd }

    self.fi_validate = {"fence_apc":self.val_apc,
              "fence_wti":self.val_wti,
              "fence_rps10":self.val_rps10,
              "fence_brocade":self.val_brocade,
              "fence_vixel":self.val_vixel,
              "fence_gnbd":self.val_gnbd,
              "fence_ilo":self.val_ilo,
              "fence_drac":self.val_drac,
              "fence_sanbox2":self.val_sanbox2,
              "fence_bladecenter":self.val_bladecenter,
              "fence_mcdata":self.val_mcdata,
              "fence_egenera":self.val_egenera,
              "fence_ipmilan":self.val_ipmilan,
              "fence_bullpap":self.val_bullpap,
              "fence_manual":self.val_manual }

    self.fd_validate = {"fence_apc":self.val_apc_fd,
              "fence_wti":self.val_wti_fd,
              "fence_rps10":self.val_rps10_fd,
              "fence_brocade":self.val_brocade_fd,
              "fence_vixel":self.val_vixel_fd,
              "fence_gnbd":self.val_gnbd_fd,
              "fence_ilo":self.val_ilo_fd,
              "fence_drac":self.val_drac_fd,
              "fence_sanbox2":self.val_sanbox2_fd,
              "fence_bladecenter":self.val_bladecenter_fd,
              "fence_mcdata":self.val_mcdata_fd,
              "fence_egenera":self.val_egenera_fd,
              "fence_ipmilan":self.val_ipmilan_fd,
              "fence_bullpap":self.val_bullpap_fd,
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
 
  def pop_rps10(self, attrs):
    pass

  def pop_brocade(self, attrs):
    self.brocade_port.set_text(attrs["port"])
 
  def pop_ilo(self, attrs):
    pass
 
  def pop_drac(self, attrs):
    pass
 
  def pop_vixel(self, attrs):
    self.vixel_port_text(attrs["port"])
 
  def pop_mcdata(self, attrs):
    self.mcdata_port.set_text(attrs["port"])
 
  def pop_manual(self, attrs):
    pass
 
  def pop_gnbd(self, attrs):
    pass
 
  def pop_egenera(self, attrs):
    self.egenera_lpan.set_text(attrs["lpan"])
    self.egenera_pserver.set_text(attrs["pserver"])
 
  def pop_sanbox2(self, attrs):
    self.sanbox2_port.set_text(attrs["port"])

  def pop_bladecenter(self, attrs):
    self.bladecenter_blade.set_text(attrs["blade"])

  def pop_bullpap(self, attrs):
    self.bullpap_domain.set_text(attrs["domain"])

  def pop_ipmilan(self, attrs):
    pass
 
  def clear_fi_forms(self):
    self.apc_port.set_text("") 
    self.apc_switch.set_text("") 
    self.wti_port.set_text("") 
    self.brocade_port.set_text("")
    self.vixel_port.set_text("")
    self.sanbox2_port.set_text("")
    self.bladecenter_blade.set_text("")
    self.mcdata_port.set_text("")
    self.egenera_lpan.set_text("")
    self.egenera_pserver.set_text("")
    self.bullpap_domain.set_text("")


  def clear_fd_forms(self):
    self.apc_fd_name.set_text("") 
    self.apc_fd_ip.set_text("")
    self.apc_fd_login.set_text("")
    self.apc_fd_passwd.set_text("")
    self.wti_fd_ip.set_text("")
    self.wti_fd_name.set_text("")
    self.wti_fd_passwd.set_text("")
    self.rps10_fd_name.set_text("")
    self.rps10_fd_device.set_text("")
    self.rps10_fd_port.set_text("")
    self.brocade_fd_name.set_text("")
    self.brocade_fd_ip.set_text("")
    self.brocade_fd_login.set_text("")
    self.brocade_fd_passwd.set_text("")
    self.ilo_fd_name.set_text("")
    self.ilo_fd_login.set_text("")
    self.ilo_fd_passwd.set_text("")
    self.ilo_fd_hostname.set_text("")
    self.drac_fd_name.set_text("")
    self.drac_fd_login.set_text("")
    self.drac_fd_passwd.set_text("")
    self.drac_fd_ip.set_text("")
    self.vixel_fd_name.set_text("")
    self.vixel_fd_ip.set_text("")
    self.vixel_fd_passwd.set_text("")
    self.manual_fd_name.set_text("")
    self.mcdata_fd_name.set_text("")
    self.mcdata_fd_ip.set_text("")
    self.mcdata_fd_login.set_text("")
    self.mcdata_fd_passwd.set_text("")
    self.gnbd_fd_name.set_text("")
    self.gnbd_fd_servers.set_text("")
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
    self.ipmilan_fd_name.set_text("")
    self.ipmilan_fd_login.set_text("")
    self.ipmilan_fd_passwd.set_text("")
    self.ipmilan_fd_ip.set_text("")
    self.bullpap_fd_name.set_text("")
    self.bullpap_fd_login.set_text("")
    self.bullpap_fd_passwd.set_text("")
    self.bullpap_fd_ip.set_text("")

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
 
  def pop_rps10_fd(self, attrs):
    self.rps10_fd_name.set_text(attrs["name"])
    self.rps10_fd_device.set_text(attrs["device"])
    self.rps10_fd_port.set_text(attrs["port"])


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

  def pop_drac_fd(self, attrs):
    self.drac_fd_name.set_text(attrs["name"])
    self.drac_fd_login.set_text(attrs["login"])
    self.drac_fd_passwd.set_text(attrs["passwd"])
    self.drac_fd_ip.set_text(attrs["ipaddr"])

 
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
    self.gnbd_fd_servers.set_text(attrs["servers"])

 
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

  def pop_ipmilan_fd(self, attrs):
    self.ipmilan_fd_name.set_text(attrs["name"])
    self.ipmilan_fd_login.set_text(attrs["login"])
    self.ipmilan_fd_passwd.set_text(attrs["passwd"])
    self.ipmilan_fd_ip.set_text(attrs["ipaddr"])

  def pop_bullpap_fd(self, attrs):
    self.bullpap_fd_name.set_text(attrs["name"])
    self.bullpap_fd_login.set_text(attrs["login"])
    self.bullpap_fd_passwd.set_text(attrs["passwd"])
    self.bullpap_fd_ip.set_text(attrs["ipaddr"])


  def process_widgets(self):
    ##Fence Instance Form Fields
    self.apc_port = self.fence_xml.get_widget('entry1') 
    self.apc_switch = self.fence_xml.get_widget('entry2') 
    self.wti_port = self.fence_xml.get_widget('entry3') 
    self.brocade_port = self.fence_xml.get_widget('entry4') 
    self.vixel_port = self.fence_xml.get_widget('entry5') 
    self.ilo_port = self.fence_xml.get_widget('entry7') 
    self.sanbox2_port = self.fence_xml.get_widget('entry8') 
    self.bladecenter_blade = self.fence_xml.get_widget('entry41') 
    self.mcdata_port = self.fence_xml.get_widget('entry9') 
    self.egenera_lpan = self.fence_xml.get_widget('entry10') 
    self.egenera_pserver = self.fence_xml.get_widget('entry11')
    self.bullpap_domain = self.fence_xml.get_widget('entry51') 

    ##Fence Device Forms
    self.apc_fd_name = self.fence_xml.get_widget('entry12')
    self.apc_fd_ip = self.fence_xml.get_widget('entry13')
    self.apc_fd_login = self.fence_xml.get_widget('entry14')
    self.apc_fd_passwd = self.fence_xml.get_widget('entry15')

    self.wti_fd_ip = self.fence_xml.get_widget('entry17')
    self.wti_fd_name = self.fence_xml.get_widget('entry16')
    self.wti_fd_passwd = self.fence_xml.get_widget('entry18')

    self.rps10_fd_name = self.fence_xml.get_widget('entry61')
    self.rps10_fd_device = self.fence_xml.get_widget('entry62')
    self.rps10_fd_port = self.fence_xml.get_widget('entry63')

    self.brocade_fd_name = self.fence_xml.get_widget('entry19')
    self.brocade_fd_ip = self.fence_xml.get_widget('entry20')
    self.brocade_fd_login = self.fence_xml.get_widget('entry21')
    self.brocade_fd_passwd = self.fence_xml.get_widget('entry22')

    self.vixel_fd_name = self.fence_xml.get_widget('entry23')
    self.vixel_fd_ip = self.fence_xml.get_widget('entry24')
    self.vixel_fd_passwd = self.fence_xml.get_widget('entry25')

    self.gnbd_fd_name = self.fence_xml.get_widget('entry26')
    self.gnbd_fd_servers = self.fence_xml.get_widget('entry27')

    self.ilo_fd_name = self.fence_xml.get_widget('entry28')
    self.ilo_fd_login = self.fence_xml.get_widget('entry29')
    self.ilo_fd_passwd = self.fence_xml.get_widget('entry30')
    self.ilo_fd_hostname = self.fence_xml.get_widget('entry31')

    self.drac_fd_name = self.fence_xml.get_widget('entry57')
    self.drac_fd_login = self.fence_xml.get_widget('entry59')
    self.drac_fd_passwd = self.fence_xml.get_widget('entry60')
    self.drac_fd_ip = self.fence_xml.get_widget('entry58')

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

    self.ipmilan_fd_name = self.fence_xml.get_widget('entry55')
    self.ipmilan_fd_ip = self.fence_xml.get_widget('entry48')
    self.ipmilan_fd_login = self.fence_xml.get_widget('entry49')
    self.ipmilan_fd_passwd = self.fence_xml.get_widget('entry50')

    self.bullpap_fd_name = self.fence_xml.get_widget('entry56')
    self.bullpap_fd_ip = self.fence_xml.get_widget('entry52')
    self.bullpap_fd_login = self.fence_xml.get_widget('entry53')
    self.bullpap_fd_passwd = self.fence_xml.get_widget('entry54')

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
    rectify_fence_name = False
    if self.apc_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.apc_fd_name)
    if name != self.apc_fd_name.get_text():
      res = self.check_unique_fd_name(self.apc_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True
    
    if self.apc_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)
    if self.apc_fd_login.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_LOGIN)
    if self.apc_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.apc_fd_name.get_text())

    fields = {}
    fields["name"] = self.apc_fd_name.get_text()
    fields["ipaddr"] = self.apc_fd_ip.get_text()
    fields["login"] = self.apc_fd_login.get_text()
    fields["passwd"] = self.apc_fd_passwd.get_text()

    return fields
 
 
  def val_wti_fd(self, name):
    rectify_fence_name = False
    if self.wti_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.wti_fd_name)
    if name != self.wti_fd_name.get_text():
      res = self.check_unique_fd_name(self.wti_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.wti_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)
    if self.wti_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.wti_fd_name.get_text())

    fields = {}
    fields["name"] = self.wti_fd_name.get_text()
    fields["ipaddr"] = self.wti_fd_ip.get_text()
    fields["passwd"] = self.wti_fd_passwd.get_text()

    return fields
 
  def val_rps10_fd(self, name):
    rectify_fence_name = False
    if self.rps10_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.rps10_fd_name)
    if name != self.rps10_fd_name.get_text():
      res = self.check_unique_fd_name(self.rps10_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.rps10_fd_device.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_DEVICE)
    if self.rps10_fd_port.get_text() == "":
        raise ValidationError('FATAL', FI_PROVIDE_PORT)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.rps10_fd_name.get_text())

    fields = {}
    fields["name"] = self.rps10_fd_name.get_text()
    fields["device"] = self.rps10_fd_device.get_text()
    fields["port"] = self.rps10_fd_port.get_text()

    return fields
 
 
  def val_brocade_fd(self, name):
    rectify_fence_name = False
    if self.brocade_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.brocade_fd_name)
    if name != self.brocade_fd_name.get_text():
      res = self.check_unique_fd_name(self.brocade_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.brocade_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)
    if self.brocade_fd_login.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_LOGIN)
    if self.brocade_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.brocade_fd_name.get_text())

    fields = {}
    fields["name"] = self.brocade_fd_name.get_text()
    fields["ipaddr"] = self.brocade_fd_ip.get_text()
    fields["login"] = self.brocade_fd_login.get_text()
    fields["passwd"] = self.brocade_fd_passwd.get_text()

    return fields
 
 
  def val_ilo_fd(self, name):
    rectify_fence_name = False
    if self.ilo_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.ilo_fd_name)
    if name != self.ilo_fd_name.get_text():
      res = self.check_unique_fd_name(self.ilo_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.ilo_fd_login.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_LOGIN)
    if self.ilo_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)
    if self.ilo_fd_hostname.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_HOSTNAME)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.ilo_fd_name.get_text())

    fields = {}
    fields["name"] = self.ilo_fd_name.get_text()
    fields["hostname"] = self.ilo_fd_hostname.get_text()
    fields["login"] = self.ilo_fd_login.get_text()
    fields["passwd"] = self.ilo_fd_passwd.get_text()

    return fields
 
 
  def val_drac_fd(self, name):
    rectify_fence_name = False
    if self.drac_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.drac_fd_name)
    if name != self.drac_fd_name.get_text():
      res = self.check_unique_fd_name(self.drac_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.drac_fd_login.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_LOGIN)
    if self.drac_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)
    if self.drac_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.drac_fd_name.get_text())

    fields = {}
    fields["name"] = self.drac_fd_name.get_text()
    fields["ipaddr"] = self.drac_fd_ip.get_text()
    fields["login"] = self.drac_fd_login.get_text()
    fields["passwd"] = self.drac_fd_passwd.get_text()

    return fields
 
 
  def val_vixel_fd(self, name):
    rectify_fence_name = False
    if self.vixel_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.vixel_fd_name)
    if name != self.vixel_fd_name.get_text():
      res = self.check_unique_fd_name(self.vixel_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.vixel_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)
    if self.vixel_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.vixel_fd_name.get_text())

    fields = {}
    fields["name"] = self.vixel_fd_name.get_text()
    fields["ipaddr"] = self.vixel_fd_ip.get_text()
    fields["passwd"] = self.vixel_fd_passwd.get_text()

    return fields
 
 
  def val_mcdata_fd(self, name):
    rectify_fence_name = False
    if self.mcdata_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.mcdata_fd_name)
    if name != self.mcdata_fd_name.get_text():
      res = self.check_unique_fd_name(self.mcdata_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.mcdata_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)
    if self.mcdata_fd_login.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_LOGIN)
    if self.mcdata_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.mcdata_fd_name.get_text())

    fields = {}
    fields["name"] = self.mcdata_fd_name.get_text()
    fields["ipaddr"] = self.mcdata_fd_ip.get_text()
    fields["login"] = self.mcdata_fd_login.get_text()
    fields["passwd"] = self.mcdata_fd_passwd.get_text()

    return fields
 
  def val_manual_fd(self, name):
    self.validateNCName(self.manual_fd_name)
    if self.manual_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    
    rectify_fence_name = False
    if name != self.manual_fd_name.get_text():
      res = self.check_unique_fd_name(self.manual_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.manual_fd_name.get_text())

    fields = {}
    fields["name"] = self.manual_fd_name.get_text()

    return fields
 
  def val_gnbd_fd(self, name):
    self.validateNCName(self.gnbd_fd_name)
    if self.gnbd_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    
    rectify_fence_name = False
    if name != self.gnbd_fd_name.get_text():
      res = self.check_unique_fd_name(self.gnbd_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True
    
    servers_new = self.gnbd_fd_servers.get_text().strip()
    if servers_new == "":
      raise ValidationError('FATAL', FD_PROVIDE_SERVERS)
    for ch in ':;,':
      if ch in servers_new:
        raise ValidationError('FATAL', FD_PROVIDE_SERVERS)
    
    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.gnbd_fd_name.get_text())

    fields = {}
    fields["name"] = self.gnbd_fd_name.get_text()
    fields["servers"] = servers_new
    return fields
 
  def val_egenera_fd(self, name):
    rectify_fence_name = False
    if self.egenera_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.egenera_fd_name)
    if name != self.egenera_fd_name.get_text():
      res = self.check_unique_fd_name(self.egenera_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.egenera_fd_cserver.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_CSERVER)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.egenera_fd_name.get_text())

    fields = {}
    fields["name"] = self.egenera_fd_name.get_text()
    fields["cserver"] = self.egenera_fd_cserver.get_text()

    return fields

 
  def val_sanbox2_fd(self, name):
    rectify_fence_name = False
    if self.sanbox2_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.sanbox2_fd_name)
    if name != self.sanbox2_fd_name.get_text():
      res = self.check_unique_fd_name(self.sanbox2_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.sanbox2_fd_ip.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_IP)

    if self.sanbox2_fd_login.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_LOGIN)

    if self.sanbox2_fd_passwd.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.sanbox2_fd_name.get_text())

    fields = {}
    fields["name"] = self.sanbox2_fd_name.get_text()
    fields["ipaddr"] = self.sanbox2_fd_ip.get_text()
    fields["login"] = self.sanbox2_fd_login.get_text()
    fields["passwd"] = self.sanbox2_fd_passwd.get_text()

    return fields

  def val_bladecenter_fd(self, name):
    rectify_fence_name = False
    if self.bladecenter_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.bladecenter_fd_name)
    if name != self.bladecenter_fd_name.get_text():
      res = self.check_unique_fd_name(self.bladecenter_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.bladecenter_fd_ip.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_IP)

    if self.bladecenter_fd_login.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_LOGIN)

    if self.bladecenter_fd_passwd.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_PASSWD)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.bladecenter_fd_name.get_text())

    fields = {}
    fields["name"] = self.bladecenter_fd_name.get_text()
    fields["ipaddr"] = self.bladecenter_fd_ip.get_text()
    fields["login"] = self.bladecenter_fd_login.get_text()
    fields["passwd"] = self.bladecenter_fd_passwd.get_text()

    return fields

  def val_ipmilan_fd(self, name):
    rectify_fence_name = False
    if self.ipmilan_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.ipmilan_fd_name)
    if name != self.ipmilan_fd_name.get_text():
      res = self.check_unique_fd_name(self.ipmilan_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.ipmilan_fd_login.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_LOGIN)
    if self.ipmilan_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)
    if self.ipmilan_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.ipmilan_fd_name.get_text())

    fields = {}
    fields["name"] = self.ipmilan_fd_name.get_text()
    fields["ipaddr"] = self.ipmilan_fd_ip.get_text()
    fields["login"] = self.ipmilan_fd_login.get_text()
    fields["passwd"] = self.ipmilan_fd_passwd.get_text()

    return fields
 
 
  def val_bullpap_fd(self, name):
    rectify_fence_name = False
    if self.bullpap_fd_name.get_text() == "":
      raise ValidationError('FATAL', FD_PROVIDE_NAME)
    self.validateNCName(self.bullpap_fd_name)
    if name != self.bullpap_fd_name.get_text():
      res = self.check_unique_fd_name(self.bullpap_fd_name.get_text())
      if res == False:  #name is already used
        raise ValidationError('FATAL', FD_PROVIDE_NAME)
      rectify_fence_name = True

    if self.bullpap_fd_login.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_LOGIN)
    if self.bullpap_fd_passwd.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_PASSWD)
    if self.bullpap_fd_ip.get_text() == "":
        raise ValidationError('FATAL', FD_PROVIDE_IP)

    if rectify_fence_name == True:
      self.model_builder.rectifyNewFencedevicenameWithFences(name,self.bullpap_fd_name.get_text())

    fields = {}
    fields["name"] = self.bullpap_fd_name.get_text()
    fields["ipaddr"] = self.bullpap_fd_ip.get_text()
    fields["login"] = self.bullpap_fd_login.get_text()
    fields["passwd"] = self.bullpap_fd_passwd.get_text()

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

  def val_rps10(self):

    fields = {}

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
    fields = {}
    fields["nodename"] = "real value will be set at ModelBuilder.perform_final_check()"
    return fields

  def val_ilo(self):

    fields = {}

    return fields

  def val_drac(self):

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
    fields["nodename"] = "real value will be set at ModelBuilder.perform_final_check()"
    return fields

  def val_ipmilan(self):

    fields = {}

    return fields

  def val_bullpap(self):
    if self.bullpap_domain.get_text() == "":
      raise ValidationError('FATAL', FI_PROVIDE_DOMAIN)

    fields = {}
    fields["domain"] = self.bullpap_domain.get_text()

    return fields

  def check_unique_fd_name(self, name):
    # check fencedevice name uniqueness
    fds = self.model_builder.getFenceDevices()
    for fd in fds:
      if fd.getName() == name:
        return False
    # fencedevice name may not be equal to cluster node name
    nodes = self.model_builder.getNodes()
    for node in nodes:
      if node.getName() == name:
        #return False
        raise ValidationError('FATAL', FD_NAME_EQUAL_TO_NODE_NAME % name)
    # everything OK
    return True

  def getFENCE_OPTS(self):
    return FENCE_OPTS

  def set_model(self, model_builder):
    self.model_builder = model_builder



  ### name must conform to relaxNG ID type ##
  def isNCName(self, name):
    for ch in ILLEGAL_CHARS:
      if ch in name:
        return False
    return True
  
  def makeNCName(self, name):
    new_name = ''
    for ch in name:
      if ch in ILLEGAL_CHARS:
        new_name = new_name + '_'
      else:
        new_name = new_name + ch
    return new_name

  def validateNCName(self, gtkentry):
    name = gtkentry.get_text().strip()
    gtkentry.set_text(name)
    if not self.isNCName(name):
      name = self.makeNCName(name)
      gtkentry.set_text(name)
      # select text
      raise ValidationError('FATAL', ILLEGAL_CHARS_REPLACED)
 

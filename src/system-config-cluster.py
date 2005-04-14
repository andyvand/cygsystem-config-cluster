#!/usr/bin/python2

"""Entry point for system-config-cluster.

   This application creates and edits the cluster.conf file,
   and provides an interface to resource management.

"""
__author__ = 'Jim Parsons (jparsons@redhat.com)'
 
import sys
import types
import select
import signal
import string
import os
from gtk import TRUE, FALSE
import MessageLibrary
from CommandHandler import CommandHandler
from CommandError import CommandError

PROGNAME = "system-config-cluster"
VERSION = "@VERSION@"
INSTALLDIR="/usr/share/system-config-cluster"
CLUSTER_CONF_PATH="/etc/cluster/cluster.conf"
CLUSTER_CONF_DIR_PATH="/etc/cluster/"

### gettext ("_") must come before import gtk ###
import gettext
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)
try:
    gettext.install(PROGNAME, "/usr/share/locale", 1)
except IOError:
    import __builtin__
    __builtin__.__dict__['_'] = unicode
                                                                                

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
                                                                                
from ConfigTab import ConfigTab
from ModelBuilder import ModelBuilder
from clui_constants import *
from MgmtTab import MgmtTab
from IPAddrEntry import IP

import gnome
import gnome.ui

gnome.program_init (PROGNAME, VERSION)
gnome.app_version = VERSION
FORMALNAME=_("system-config-cluster")
ABOUT_VERSION=_("%s %s") % ('system-config-cluster',VERSION)
 
NO_CONF_PRESENT=_("The cluster configuration file, '/etc/cluster/cluster.conf' does not exist on this system. This application will help you build an initial configuration file, or you can open an existing configuration file in another location by selecting 'Open' in the file drop down menu.") 

NOT_CLUSTER_MEMBER=_("Because this node is not currently part of a cluster, the management tab for this application is not available.")

SAVED_FILE=_("The current configuration has been saved in \n %s")
CONFIRM_PROPAGATE=_("This action will save the current configuration in /etc/cluster/cluster.conf, and will propagate this configuration to all active cluster members. Do you wish to proceed?")

UNSAVED=_("Do you want to save your changes? \n\nThe current configuration has not been saved. Click 'No' to discard changes and quit. Click 'Yes' to return to the application where the configuration can be saved by choosing 'Save' or 'Save As' from the File menu.")

NO_MCAST_IP=_("Please Provide a Valid Multicast IP Address")

FILE_DOES_NOT_EXIST=_("The file %s does not exist on the filesystem.")
###############################################
class basecluster:
  def __init__(self, glade_xml, app):

    self.model_builder = None
    self.mcast_address = None
    self.configtab = None
    self.glade_xml = glade_xml
    self.command_handler = CommandHandler()
    self.init_widgets()

    ##First check for existence of cluster.conf
    ##then, make model builder and check for cluster
    ##this determines what to put in message dlg

    conf_exists = os.path.exists(CLUSTER_CONF_PATH)

    mb = ModelBuilder(1)
    is_cluster_member = mb.isClusterMember()

    if (conf_exists == FALSE):
      #hide mgmt tab
      self.mgmt_tab.hide()
      self.no_conf_label.set_text(NO_CONF_PRESENT + "\n\n" + NOT_CLUSTER_MEMBER)
      self.propagate_button.hide()
      #self.no_conf_dlg.show()
      self.no_conf_dlg.run()
    elif ((conf_exists == TRUE) and (is_cluster_member == FALSE)):
      self.mgmt_tab.hide()
      MessageLibrary.simpleInfoMessage(NOT_CLUSTER_MEMBER)
      self.propagate_button.hide()
      #try:
      #  self.command_handler.check_xml(CLUSTER_CONF_PATH)
      #except CommandError, e:
      #  self.bad_xml_label.set_text(XML_CONFIG_ERROR % CLUSTER_CONF_PATH)
      #  self.bad_xml_text.get_buffer().set_text(e.getMessage())
      #  retval = self.bad_xml_dlg.run()
      #  if retval == gtk.RESPONSE_CANCEL:
      #    gtk.main_quit()
      #  elif retval == gtk.RESPONSE_APPLY:
      #    #make new cfg file
      #    self.no_conf_dlg.run()
      #  else:  #Proceed anyway...
      #    self.model_builder = ModelBuilder(1, CLUSTER_CONF_PATH)
      self.model_builder = ModelBuilder(1, CLUSTER_CONF_PATH)
    else:
      self.model_builder = ModelBuilder(1, CLUSTER_CONF_PATH)
      self.propagate_button.show()
      self.mgmttab = MgmtTab(glade_xml, self.model_builder)

    self.configtab = ConfigTab(glade_xml, self.model_builder)


    self.glade_xml.signal_autoconnect(
      {
        "on_quit1_activate" : self.quit,
        "on_quit2_activate" : self.quit,
        "on_open1_activate" : self.open,
        "on_new1_activate" : self.new,
        "on_save1_activate" : self.save,
        "on_save_as1_activate" : self.save_as,
        "on_change_lockserver1_activate" : self.change_lockserver,
        "on_use_multicast_mode1_activate" : self.swap_multicast_state,
        "on_about1_activate" : self.on_about
      }
    )
                                                                                
  def on_about(self, *args):
        dialog = gnome.ui.About(
            ABOUT_VERSION,
            '', ### Don't specify version - already in ABOUT_VERSION
            _("Copyright (c) 2004 Red Hat, Inc. All rights reserved."),
            _("This software is licensed under the terms of the GPL."),
            [ 'Jim Parsons (system-config-cluster) <jparsons at redhat.com>',
              '',
              'Kevin Anderson (Project Leader) <kanderso at redhat.com>'],
            [ 'Paul Kennedy <pkennedy at redhat.com>',
              'John Ha <jha at redhat.com>'], # doc people
        ) ### end dialog
        dialog.set_title (FORMALNAME)
        dialog.show()
                                                                                
 
  def quit(self, *args):
    path = self.model_builder.getFilepath()
    mod = self.model_builder.isFileModified()
    if (path == "") or (path == None) or (mod == TRUE):
      retval = MessageLibrary.warningMessage(UNSAVED)
      if retval == gtk.RESPONSE_YES:
        return gtk.TRUE
      else:
        gtk.main_quit()

    gtk.main_quit()

  def open(self, *args):
    #offer fileselection
    popup = gtk.FileSelection()
    popup.set_filename(CLUSTER_CONF_DIR_PATH)
    popup.hide_fileop_buttons()
    popup.set_select_multiple(FALSE)
    popup.show_all()
    rc = popup.run()
    filepath = popup.get_filename()

    #Check to see if file actually exists
    path_exists = os.path.exists(filepath)
    if path_exists == FALSE:
      MessageLibrary.errorMessage(FILE_DOES_NOT_EXIST % filepath)
      popup.destroy()
      return
  
    if os.path.isdir(filepath):
      popup.destroy()
      return
    if not rc == gtk.RESPONSE_OK:
      popup.destroy()
      return
    else:
      self.model_builder = ModelBuilder(DLM_TYPE, filepath)
      self.configtab.set_model(self.model_builder)
      popup.destroy()

  def open_limited(self, *args):
    #offer fileselection
    popup = gtk.FileSelection()
    popup.set_filename(CLUSTER_CONF_DIR_PATH)
    popup.hide_fileop_buttons()
    popup.set_select_multiple(FALSE)
    popup.show_all()
    rc = popup.run()
    filepath = popup.get_filename()

    #Check to see if file actually exists
    path_exists = os.path.exists(filepath)
    if path_exists == FALSE:
      MessageLibrary.errorMessage(FILE_DOES_NOT_EXIST % filepath)
      popup.destroy()
      self.model_builder = ModelBuilder(DLM_TYPE, None)
      return
  
    if os.path.isdir(filepath):
      popup.destroy()
      self.model_builder = ModelBuilder(DLM_TYPE, None)
      return
    if not rc == gtk.RESPONSE_OK:
      popup.destroy()
      self.model_builder = ModelBuilder(DLM_TYPE, None)
      return
    else:
      self.model_builder = ModelBuilder(DLM_TYPE, filepath)
      popup.destroy()

  def save(self, *args):
    if self.model_builder.has_filepath():
      fp = self.model_builder.getFilepath()
      self.model_builder.exportModel()
      retval = MessageLibrary.simpleInfoMessage(SAVED_FILE % fp)
    else:  #Must have been a 'New' instance...
      self.save_as(None)


  def save_as(self, *args):
    popup = gtk.FileSelection()
    popup.set_filename(CLUSTER_CONF_PATH)
    popup.show_fileop_buttons()
    popup.set_select_multiple(FALSE)
    popup.show_all()
    rc = popup.run()
    filepath = popup.get_filename()
    if not rc == gtk.RESPONSE_OK:
      popup.destroy()
      return
    else:
      try:
        self.model_builder.exportModel(filepath)
        self.glade_xml.get_widget("filename_entry").set_text(filepath)
      except IOError, e:
        MessageLibrary.errorMessage("Something ugly happened when attempting to write output file")
    popup.destroy()

  def new(self, *args):
    #Ask what type of lockserver to employ
    self.mcast_cbox.set_sensitive(TRUE)
    self.mcast_cbox.set_active(FALSE)
    self.ip.set_sensitive(FALSE)
    self.mcast_address = None
    self.mcast_addr_label.set_sensitive(FALSE)
    self.radio_dlm.set_active(TRUE)
    self.lock_method_dlg.show()
    #print "So now the mcast_addr == %s" % self.mcast_address
    #self.model_builder = ModelBuilder(self.lock_type, None, self.mcast_address)
    ##set file name field at top of tab to 'New Configuration'
    #self.glade_xml.get_widget("filename_entry").set_text(NEW_CONFIG)
    #self.configtab.set_model(self.model_builder)

  def lock_ok(self, button):

    if self.radio_dlm.get_active() == TRUE:
      if self.mcast_cbox.get_active() == TRUE: #User wishes to use multicast
        if self.ip.isValid() == FALSE:
          retval = MessageLibrary.errorMessage(NO_MCAST_IP)
          self.mcast_address = None
          return
        else:
          self.mcast_address = self.ip.getAddrAsString() 
      self.lock_type = DLM_TYPE
    else:
      self.lock_type = GULM_TYPE
      self.mcast_address = None

    self.lock_method_dlg.hide()
    self.model_builder = ModelBuilder(self.lock_type, None, self.mcast_address)
    #set file name field at top of tab to 'New Configuration'
    self.glade_xml.get_widget("filename_entry").set_text(NEW_CONFIG)
    if self.configtab != None:
      self.configtab.set_model(self.model_builder)

  def lock_method_delete(self, *args):
    self.lock_type = DLM_TYPE
    self.lock_method_dlg.hide()
    return gtk.TRUE

  def on_no_conf_create(self, button):
    self.no_conf_dlg.hide()
    self.radio_dlm.set_active(TRUE)
    self.mcast_cbox.set_sensitive(TRUE)
    self.mcast_cbox.set_active(FALSE)
    self.ip.set_sensitive(FALSE)
    self.mcast_addr_label.set_sensitive(FALSE)
    self.lock_method_dlg.show_all()
    retval = self.lock_method_dlg.run()
    self.lock_method_dlg.destroy()
    self.model_builder = ModelBuilder(self.lock_type)
    
  def on_no_conf_open(self, button):
    self.no_conf_dlg.hide()
    self.open_limited(None)

  def on_mcast_cbox_changed(self, *args):
    if self.mcast_cbox.get_active() == FALSE:
      self.ip.set_sensitive(FALSE)
      self.mcast_addr_label.set_sensitive(FALSE)
    else:
      self.ip.set_sensitive(TRUE)
      self.mcast_addr_label.set_sensitive(TRUE)

  def on_radio_change(self, *args):
    if self.radio_dlm.get_active() == FALSE:
      self.mcast_cbox.set_sensitive(FALSE)
      self.ip.set_sensitive(FALSE)
      self.mcast_addr_label.set_sensitive(FALSE)
    else:
      self.mcast_cbox.set_sensitive(TRUE)
      self.ip.set_sensitive(TRUE)
      self.mcast_addr_label.set_sensitive(TRUE)
    

  def init_widgets(self):
    self.notebook = self.glade_xml.get_widget('notebook1')
    self.nodetree = self.glade_xml.get_widget('nodetree')
    mgmtpageidx = self.notebook.page_num(self.nodetree)
    self.mgmt_tab = self.notebook.get_nth_page(mgmtpageidx)
    self.lock_type = DLM_TYPE  #Default Value
    self.radio_dlm = self.glade_xml.get_widget('radio_dlm')
    self.radio_dlm.connect('toggled',self.on_radio_change)
    self.lock_method_dlg = self.glade_xml.get_widget('lock_method')
    self.glade_xml.get_widget('okbutton17').connect('clicked', self.lock_ok)
    self.no_conf_dlg = self.glade_xml.get_widget('no_conf')
    self.no_conf_label = self.glade_xml.get_widget('no_conf_label')
    self.glade_xml.get_widget('no_conf_create').connect('clicked',self.on_no_conf_create)
    self.glade_xml.get_widget('no_conf_open').connect('clicked',self.on_no_conf_open)
    self.propagate_button = self.glade_xml.get_widget('propagate')
    self.propagate_button.connect('clicked', self.propagate)
    self.bad_xml_dlg = self.glade_xml.get_widget('bad_xml_dlg')
    self.bad_xml_label = self.glade_xml.get_widget('bad_xml_label')
    self.bad_xml_text = self.glade_xml.get_widget('bad_xml_text')
    self.mcast_cbox = self.glade_xml.get_widget('mcast_cbox')
    self.mcast_cbox.connect('toggled',self.on_mcast_cbox_changed)
    self.mcast_addr_label = self.glade_xml.get_widget('label121')
    self.ip = IP()
    self.ip.show_all()
    self.glade_xml.get_widget('mcast_ip_proxy').add(self.ip)

  def propagate(self):
    retval = self.warningMessage(CONFIRM_PROPAGATE)
    if retval == gtk.RESPONSE_NO:
      return
    #1 save file to /etc/cluster/cluster.conf
    self.model_builder.exportModel(CLUSTER_CONF_PATH)
    #2 call ccs_tool
    try:
      self.command_handler.propagateConfig(CLUSTER_CONF_PATH)
    except CommandError, e:
      self.MessageLibrary.errorMessage(e.getMessage())
    #3 call cman_tool -r with config version
    ltype = self.model_builder.getLockType()
    if ltype == DLM_TYPE:
      cptr = self.model_builder.getClusterPtr()
      version = cptr.getConfigVersion()
      try:
        self.command_handler.propagateCManConfig(version)
      except CommandError, e:
        self.MessageLibrary.errorMessage(e.getMessage())

  def change_lockserver(self, *args):
    #warning message
    retval = MessageLibrary.warningMessage(DANGER_REBOOT_CLUSTER)
    if retval != gtk.RESPONSE_YES:
      print "NOT OK -- Sorry"
      return
    #call model builder call
    self.model_builder.switch_lockservers()
    #call configtab.prepare_tree()
    self.configtab.prepare_tree()

  def swap_multicast_state(self, *args):
    pass

#############################################################
def initGlade():
    gladepath = "clui.glade"
    if not os.path.exists(gladepath):
      gladepath = "%s/%s" % (INSTALLDIR,gladepath)

    gtk.glade.bindtextdomain(PROGNAME)
    glade_xml = gtk.glade.XML (gladepath, domain=PROGNAME)
    return glade_xml
                                                                                
def runFullGUI():
    glade_xml = initGlade()
    app = glade_xml.get_widget('system-config-cluster')
    baseapp = basecluster(glade_xml, app)
    app.show()
    #app.connect("destroy", lambda w: gtk.main_quit())
    app.connect("delete_event", baseapp.quit)
    #app.connect("destroy", baseapp.quit)
    gtk.main()
                                                                                
                                                                                
if __name__ == "__main__":
    cmdline = sys.argv[1:]
    sys.argv = sys.argv[:1]
                                                                                

    if os.getuid() != 0:
        print _("Please restart %s with root permissions!") % (sys.argv[0])
        sys.exit(10)

    runFullGUI()


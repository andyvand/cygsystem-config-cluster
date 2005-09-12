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
import MessageLibrary
from CommandHandler import CommandHandler
from CommandError import CommandError

PROGNAME = "system-config-cluster"
VERSION = "@VERSION@"
INSTALLDIR="/usr/share/system-config-cluster"

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
 
NO_CONF_PRESENT=_("The cluster configuration file, '/etc/cluster/cluster.conf' does not exist on this system. This application will help you build an initial configuration file, or you can open an existing configuration file in another location.")
NO_CONF_PRESENT_INVALID=_("The cluster configuration file, '/etc/cluster/cluster.conf' is not valid. This application will help you build an initial configuration file, or you can open an existing configuration file in another location.")

NOT_CLUSTER_MEMBER=_("Because this node is not currently part of a cluster, the management tab for this application is not available.")

SAVED_FILE=_("The current configuration has been saved in \n %s")
CONFIRM_PROPAGATE=_("This action will save the current configuration in /etc/cluster/cluster.conf, and will propagate this configuration to all active cluster members. Do you wish to proceed?")

UNSAVED=_("Do you want to save your changes? \n\nThe current configuration has not been saved. Click 'No' to discard changes and quit. Click 'Yes' to return to the application where the configuration can be saved by choosing 'Save' or 'Save As' from the File menu.")

NO_MCAST_IP=_("Please Provide a Valid Multicast IP Address")

PROPOGATION_CONFIRMATION=_("Success. The current configuration has been propagated to the cluster.")

FILE_DOES_NOT_EXIST=_("The file %s does not exist on the filesystem.")

CONFFILE_NOT_SAVED_MESSAGE=_("Configuration file not saved.")

###############################################
class basecluster:
  def __init__(self, glade_xml, app):

    self.winMain = app
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
    
    if conf_exists:
        use_default_clusterconf_path = True
        try:
            self.command_handler.check_xml(CLUSTER_CONF_PATH)
        except CommandError, e:
            self.bad_xml_label.set_text(XML_CONFIG_ERROR % CLUSTER_CONF_PATH)
            self.bad_xml_text.get_buffer().set_text(e.getMessage())
            retval = self.bad_xml_dlg.run()
            self.bad_xml_dlg.hide()
            if retval == gtk.RESPONSE_APPLY:
                # make new cfg file
                use_default_clusterconf_path = False
                self.on_no_conf_create(None)
            elif retval == gtk.RESPONSE_OK:
                # Proceed anyway...
                pass
            else:
                use_default_clusterconf_path = False
                self.no_conf_label.set_text(NO_CONF_PRESENT_INVALID)
                self.no_conf_dlg.run()
        if use_default_clusterconf_path:
            self.model_builder = ModelBuilder(1, CLUSTER_CONF_PATH)
        if is_cluster_member:
            self.propagate_button.show()
            self.mgmttab = MgmtTab(glade_xml, self.model_builder,self.winMain)
        else:
            self.mgmt_tab.hide()
            MessageLibrary.simpleInfoMessage(NOT_CLUSTER_MEMBER)
            self.propagate_button.hide()
    else:
        #hide mgmt tab
        self.mgmt_tab.hide()
        self.no_conf_label.set_text(NO_CONF_PRESENT + "\n\n" + NOT_CLUSTER_MEMBER)
        self.propagate_button.hide()
        # self.no_conf_dlg.show()
        self.no_conf_dlg.run()
    
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
    if (path == "") or (path == None) or (mod == True):
      retval = MessageLibrary.warningMessage(UNSAVED)
      if retval == gtk.RESPONSE_YES:
        return True
      else:
        gtk.main_quit()

    gtk.main_quit()

  def open(self, *args):
    #offer fileselection
    popup = gtk.FileSelection()
    popup.set_filename(CLUSTER_CONF_DIR_PATH)
    popup.hide_fileop_buttons()
    popup.set_select_multiple(False)
    popup.show_all()
    
    while popup.run() == gtk.RESPONSE_OK:
        filepath = popup.get_filename()
        #Check to see if file actually exists
        if not os.path.exists(filepath):
            MessageLibrary.errorMessage(FILE_DOES_NOT_EXIST % filepath)
            continue
        elif os.path.isdir(filepath):
            continue
        # process file
        try:
            self.command_handler.check_xml(filepath)
        except CommandError, e:
            self.bad_xml_label.set_text(XML_CONFIG_ERROR % filepath)
            self.bad_xml_text.get_buffer().set_text(e.getMessage())
            retval = self.bad_xml_dlg.run()
            self.bad_xml_dlg.hide()
            if retval == gtk.RESPONSE_OK:
                #Proceed anyway...
                pass
            elif retval == gtk.RESPONSE_APPLY:
                # make new cfg file
                popup.destroy()
                self.on_no_conf_create(None)
                return
            else:
                continue
        self.model_builder = ModelBuilder(DLM_TYPE, filepath)
        self.configtab.set_model(self.model_builder)
        break
    popup.destroy()
  
  def open_limited(self, *args):
    #offer fileselection
    popup = gtk.FileSelection()
    popup.set_filename(CLUSTER_CONF_DIR_PATH)
    popup.hide_fileop_buttons()
    popup.set_select_multiple(False)
    popup.show_all()
    
    while True:
        rc = popup.run()
        
        if rc != gtk.RESPONSE_OK:
            popup.destroy()
            self.no_conf_dlg.run()
            return
        
        filepath = popup.get_filename()
        #Check to see if file actually exists
        if not os.path.exists(filepath):
            MessageLibrary.errorMessage(FILE_DOES_NOT_EXIST % filepath)
            continue
        elif os.path.isdir(filepath):
            continue
        # process file
        try:
            self.command_handler.check_xml(filepath)
        except CommandError, e:
            self.bad_xml_label.set_text(XML_CONFIG_ERROR % filepath)
            self.bad_xml_text.get_buffer().set_text(e.getMessage())
            retval = self.bad_xml_dlg.run()
            self.bad_xml_dlg.hide()
            if retval == gtk.RESPONSE_OK:
                #Proceed anyway...
                popup.destroy()
                self.model_builder = ModelBuilder(DLM_TYPE, filepath)
                return
            elif retval == gtk.RESPONSE_APPLY:
                # make new cfg file
                popup.destroy()
                self.on_no_conf_create(None)
                return
            else:  
                continue
        popup.destroy()
        self.model_builder = ModelBuilder(DLM_TYPE, filepath)
        return
  
  def save(self, *args):
    if self.model_builder.has_filepath():
      fp = self.model_builder.getFilepath()
      if self.model_builder.exportModel() == True:
          retval = MessageLibrary.simpleInfoMessage(SAVED_FILE % fp)
          self.configtab.prepare_tree(True)
      else:
          MessageLibrary.errorMessage(CONFFILE_NOT_SAVED_MESSAGE)
    else:  #Must have been a 'New' instance...
      self.save_as(None)


  def save_as(self, *args):
    fname = ""
    flname = self.model_builder.getFilepath()
    if (flname == None) or (flname == ""):
      fname = CLUSTER_CONF_PATH
    else:
      fname = flname
    popup = gtk.FileSelection()
    popup.set_filename(fname)
    popup.show_fileop_buttons()
    popup.set_select_multiple(False)
    popup.show_all()
    rc = popup.run()
    filepath = popup.get_filename()
    if not rc == gtk.RESPONSE_OK:
      popup.destroy()
      return
    else:
      try:
        if self.model_builder.exportModel(filepath) == True:
            retval = MessageLibrary.simpleInfoMessage(SAVED_FILE % filepath)
            self.glade_xml.get_widget("filename_entry").set_text(filepath)
        else:
            MessageLibrary.errorMessage(CONFFILE_NOT_SAVED_MESSAGE)
      except IOError, e:
        MessageLibrary.errorMessage("Something ugly happened when attempting to write output file")
    popup.destroy()

  def new(self, *args):
    #Ask what type of lockserver to employ
    self.mcast_cbox.set_sensitive(True)
    self.mcast_cbox.set_active(False)
    self.ip.clear()
    self.ip.set_sensitive(False)
    self.mcast_address = None
    self.mcast_addr_label.set_sensitive(False)
    self.radio_dlm.set_active(True)
    self.lock_method_dlg.show()
    #print "So now the mcast_addr == %s" % self.mcast_address
    #self.model_builder = ModelBuilder(self.lock_type, None, self.mcast_address)
    ##set file name field at top of tab to 'New Configuration'
    #self.glade_xml.get_widget("filename_entry").set_text(NEW_CONFIG)
    #self.configtab.set_model(self.model_builder)

  def lock_ok(self, button):
    if self.radio_dlm.get_active() == True:
      if self.mcast_cbox.get_active() == True: #User wishes to use multicast
        if self.ip.isValid() == False:
          retval = MessageLibrary.errorMessage(NO_MCAST_IP)
          self.mcast_address = None
          self.lock_method_dlg.response(gtk.RESPONSE_NO)
          return True
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

  def on_no_conf_create(self, button):
    self.no_conf_dlg.hide()
    self.radio_dlm.set_active(True)
    self.mcast_cbox.set_sensitive(True)
    self.mcast_cbox.set_active(False)
    self.ip.clear()
    self.ip.set_sensitive(False)
    self.mcast_addr_label.set_sensitive(False)
    while self.lock_method_dlg.run() != gtk.RESPONSE_OK:
        # continue ONLY after self.model_builder has been set up
        pass
  
  def on_no_conf_open(self, button):
    self.no_conf_dlg.hide()
    self.open_limited(None)
  
  def on_no_conf_quit(self, button):
      sys.exit(0)
  
  def on_mcast_cbox_changed(self, *args):
    if self.mcast_cbox.get_active() == False:
      self.ip.set_sensitive(False)
      self.mcast_addr_label.set_sensitive(False)
    else:
      self.ip.set_sensitive(True)
      self.mcast_addr_label.set_sensitive(True)

  def on_radio_change(self, *args):
    if self.radio_dlm.get_active() == False:
      self.mcast_cbox.set_sensitive(False)
      self.ip.set_sensitive(False)
      self.mcast_addr_label.set_sensitive(False)
    else:
      self.mcast_cbox.set_sensitive(True)
      self.ip.set_sensitive(True)
      self.mcast_addr_label.set_sensitive(True)
    

  def init_widgets(self):
    self.notebook = self.glade_xml.get_widget('notebook1')
    self.notebook.connect("switch-page",self.on_notebook_change)

    self.tools1 = self.glade_xml.get_widget('tools1')
    self.new1 = self.glade_xml.get_widget('new1')
    self.open1 = self.glade_xml.get_widget('open1')
    self.save1 = self.glade_xml.get_widget('save1')
    self.save_as1 = self.glade_xml.get_widget('save_as1')

    self.nodetree = self.glade_xml.get_widget('nodetree')
    mgmtpageidx = self.notebook.page_num(self.nodetree)
    self.mgmt_tab = self.notebook.get_nth_page(mgmtpageidx)
    self.lock_type = DLM_TYPE  #Default Value
    self.radio_dlm = self.glade_xml.get_widget('radio_dlm')
    self.radio_dlm.connect('toggled',self.on_radio_change)
    self.lock_method_dlg = self.glade_xml.get_widget('lock_method')
    self.lock_method_dlg.connect("delete_event", self.lock_method_dlg_delete)
    self.glade_xml.get_widget('okbutton17').connect('clicked', self.lock_ok)
    self.no_conf_dlg = self.glade_xml.get_widget('no_conf')
    self.no_conf_dlg.connect("delete_event",self.on_no_conf_dlg_delete)
    self.no_conf_label = self.glade_xml.get_widget('no_conf_label')
    self.glade_xml.get_widget('no_conf_create').connect('clicked',self.on_no_conf_create)
    self.glade_xml.get_widget('no_conf_open').connect('clicked',self.on_no_conf_open)
    self.glade_xml.get_widget('no_conf_quit').connect('clicked',self.on_no_conf_quit)
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
    self.mcast_addr_entry = IP()
    self.mcast_addr_entry.show_all()
    self.glade_xml.get_widget('mcast_ip_proxy').add(self.ip)
    self.glade_xml.get_widget('mcast_addr_entry_proxy').add(self.mcast_addr_entry)
    self.mcast_ip_dlg = self.glade_xml.get_widget('mcast_ip_dlg')
    self.mcast_ip_dlg.connect("delete_event", self.mcast_ip_dlg_delete)

  def propagate(self, button):
    retval = MessageLibrary.warningMessage(CONFIRM_PROPAGATE)
    if retval == gtk.RESPONSE_NO:
      return

    #1 save file to /etc/cluster/cluster.conf
    if self.model_builder.exportModel(CLUSTER_CONF_PATH) == True:
        self.configtab.prepare_tree(True)
    else:
        MessageLibrary.errorMessage(_("Propagation aborted."))
        return
    #2 call ccs_tool
    try:
      self.command_handler.propagateConfig(CLUSTER_CONF_PATH)
    except CommandError, e:
      MessageLibrary.errorMessage(e.getMessage())
      return

    #3 call cman_tool -r with config version
    ltype = self.model_builder.getLockType()
    if ltype == DLM_TYPE:
      cptr = self.model_builder.getClusterPtr()
      version = cptr.getConfigVersion()
      try:
        self.command_handler.propagateCmanConfig(version)
      except CommandError, e:
        MessageLibrary.errorMessage(e.getMessage())
        return

    #4 Put up nice success message
    MessageLibrary.simpleInfoMessage(PROPOGATION_CONFIRMATION)

  def change_lockserver(self, *args):
    #warning message
    retval = MessageLibrary.warningMessage(DANGER_REBOOT_CLUSTER)
    if retval != gtk.RESPONSE_YES:
      return
    #call model builder call
    self.model_builder.switch_lockservers()
    #call configtab.prepare_tree()
    #self.configtab.prepare_tree(True)
    self.configtab.reset_tree_model(None)

  def swap_multicast_state(self, *args):
    address = None
    if self.model_builder.isMulticast() == False:
        self.mcast_addr_entry.clear()
        while address == None:
            retval = self.mcast_ip_dlg.run()
            if retval == gtk.RESPONSE_OK:
                if self.mcast_addr_entry.isValid():
                    address = self.mcast_addr_entry.getAddrAsString()
                    self.mcast_ip_dlg.hide()
                else:
                    MessageLibrary.errorMessage(NO_MCAST_IP)
                    continue
            else:
                self.mcast_ip_dlg.hide()
                return
    
    self.model_builder.swap_multicast_state(address)
    self.configtab.prepare_tree(True)
    self.configtab.reset_tree_model(None)
  
  def on_notebook_change(self, notebook, page, pagenum, *data):
    if pagenum == 0:  #Config page
      #turn on all menus
      self.tools1.set_sensitive(True)
      self.new1.set_sensitive(True)
      self.open1.set_sensitive(True)
      self.save1.set_sensitive(True)
      self.save_as1.set_sensitive(True)
    else:
      #turn off all but quit and help
      self.tools1.set_sensitive(False)
      self.new1.set_sensitive(False)
      self.open1.set_sensitive(False)
      self.save1.set_sensitive(False)
      self.save_as1.set_sensitive(False)

  def lock_method_dlg_delete(self, *args):
    return True

  def mcast_ip_dlg_delete(self, *args):
    self.mcast_ip_dlg.hide()
    return True

  def on_no_conf_dlg_delete(self, *args):
    sys.exit(0)

#############################################################
def initGlade():
    gladepath = "clui.glade"
    if not os.path.exists(gladepath):
      gladepath = "%s/%s" % (INSTALLDIR,gladepath)

    gtk.glade.bindtextdomain(PROGNAME)
    glade_xml = gtk.glade.XML (gladepath, domain=PROGNAME)
    return glade_xml
                                                                                
def runFullGUI():

    signal.signal (signal.SIGINT, signal.SIG_DFL)

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

    try:
      runFullGUI()
    except KeyboardInterrupt, e:
      pass


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

import gnome
import gnome.ui

gnome.program_init (PROGNAME, VERSION)
gnome.app_version = VERSION
FORMALNAME=_("system-config-cluster")
ABOUT_VERSION=_("%s %s") % ('system-config-cluster',VERSION)
 
NO_CONF_PRESENT=_("The cluster configuration file, '/etc/cluster/cluster.conf' does not exist on this system. This application will help you build an initial configuration file, or you can open an existing configuration file in another location by selecting 'Open' in the file drop down menu.") 

NOT_CLUSTER_MEMBER=_("Because this node is not currently part of a cluster, the management tab for this application is not available.")

SAVED_FILE=_("The current configuration has been saved in \n %s")
###############################################
class basecluster:
  def __init__(self, glade_xml, app):

    self.model_builder = None
    self.glade_xml = glade_xml
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
      #self.no_conf_dlg.show()
      self.no_conf_dlg.run()
    elif ((conf_exists == TRUE) and (is_cluster_member == FALSE)):
      self.mgmt_tab.hide()
      MessageLibrary.simpleInfoMessage(NOT_CLUSTER_MEMBER)
      self.model_builder = ModelBuilder(1, CLUSTER_CONF_PATH)
    else:
      self.model_builder = ModelBuilder(1, CLUSTER_CONF_PATH)
      #self.mgmttab = MgmtTab(glade_xml, self.model_builder)

    self.configtab = ConfigTab(glade_xml, self.model_builder)


    self.glade_xml.signal_autoconnect(
      {
        "on_quit1_activate" : self.quit,
        "on_open1_activate" : self.open,
        "on_new1_activate" : self.new,
        "on_save1_activate" : self.save,
        "on_save_as1_activate" : self.save_as,
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
      except IOError, e:
        MessageLibrary.errorMessage("Something ugly happened when attempting to write output file")
    popup.destroy()

  def new(self, *args):
    #Ask what type of lockserver to employ
    self.lock_method_dlg.show()
    self.model_builder = ModelBuilder(self.lock_type)
    self.configtab.set_model(self.model_builder)

  def lock_ok(self, button):
    if self.radio_dlm.get_active() == TRUE:
      self.lock_type = DLM_TYPE
    else:
      self.lock_type = GULM_TYPE

    self.lock_method_dlg.hide()

  def lock_method_delete(self, *args):
    self.lock_type = DLM_TYPE
    self.lock_method_dlg.hide()
    return gtk.TRUE

  def on_no_conf_create(self, button):
    self.no_conf_dlg.hide()
    self.lock_method_dlg.show_all()
    retval = self.lock_method_dlg.run()
    self.lock_method_dlg.destroy()
    self.model_builder = ModelBuilder(self.lock_type)
    
  def on_no_conf_open(self, button):
    self.no_conf_dlg.hide()
    self.open_limited(None)
    

  def init_widgets(self):
    self.notebook = self.glade_xml.get_widget('notebook1')
    self.nodetree = self.glade_xml.get_widget('nodetree')
    mgmtpageidx = self.notebook.page_num(self.nodetree)
    self.mgmt_tab = self.notebook.get_nth_page(mgmtpageidx)
    self.lock_type = DLM_TYPE  #Default Value
    self.radio_dlm = self.glade_xml.get_widget('radio_dlm')
    self.lock_method_dlg = self.glade_xml.get_widget('lock_method')
    self.glade_xml.get_widget('okbutton17').connect('clicked', self.lock_ok)
    self.no_conf_dlg = self.glade_xml.get_widget('no_conf')
    self.no_conf_label = self.glade_xml.get_widget('no_conf_label')
    self.glade_xml.get_widget('no_conf_create').connect('clicked',self.on_no_conf_create)
    self.glade_xml.get_widget('no_conf_open').connect('clicked',self.on_no_conf_open)


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
    app.connect("destroy", lambda w: gtk.main_quit())
    gtk.main()
                                                                                
                                                                                
if __name__ == "__main__":
    cmdline = sys.argv[1:]
    sys.argv = sys.argv[:1]
                                                                                

    if os.getuid() != 0:
        print _("Please restart %s with root permissions!") % (sys.argv[0])
        sys.exit(10)

    runFullGUI()


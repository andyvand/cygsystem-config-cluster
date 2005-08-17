import string
import gobject
import sys
import MessageLibrary
from CommandError import CommandError
from clui_constants import *
from CommandHandler import CommandHandler
from ForkedCommand import ForkedCommand


import gettext
_ = gettext.gettext
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
                                                                                
import gnome
import gnome.ui
                                                                                
#from MgmtTabController import MgmtTabController

ON_MEMBER=_("On Member: %s")

STATUS=_("Status: %s")

UNKNOWN=_("Status: Unknown")
                                                                                
MEMBER=_("Status: Cluster Member")

NO_SERVICES=_("No Services Currently Defined")

NODEINFO_ERROR=_("Node information is temporarily unavailable. Here is the error message: \n%s")

PATIENCE_MESSAGE=_("Please be patient.\n Starting and Stopping Services\n can sometimes take a minute or two.")

T_NAME=_("Name")
T_VOTES=_("Votes")
T_STATUS=_("Status")

S_NAME=_("Service Name")
S_STATE=_("State")
S_OWNER=_("Owner")
S_LASTOWNER=_("Previous Owner")
S_RESTARTS=_("Restarts")

TITLE_COL = 0
VOTES_COL = 1
STATUS_COL = 2
NAME_COL = 3

S_TITLE_COL = 0
S_STATE_COL = 1
S_OWNER_COL = 2
S_LASTOWNER_COL = 3
S_RESTARTS_COL = 4
S_NAME_COL = 5

python_code_targets = [('execable_python', 0, 0),
                       ('pickled_python', 0, 1)];

############################################
class MgmtTab:
  def __init__(self, glade_xml, model_builder,winmain):

    self.winMain = winmain
    # make sure threading is disabled
    try:
      from gtk import _disable_gdk_threading
      _disable_gdk_threading()
    except ImportError:
      pass


    self.model_builder = model_builder
    self.glade_xml = glade_xml
    self.command_handler = CommandHandler()
                                                                                
    #set up node tree structure
    self.nodetree = self.glade_xml.get_widget('nodetree')
    self.treemodel = gtk.TreeStore (gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gobject.TYPE_STRING)
    self.nodetree.set_model(self.treemodel)

    self.nodetree.drag_dest_set(gtk.DEST_DEFAULT_ALL, python_code_targets, gtk.gdk.ACTION_COPY)
    self.nodetree.connect('drag_data_received',self.dest_drag_data_received)

    renderer = gtk.CellRendererText()
    column1 = gtk.TreeViewColumn(T_NAME,renderer,markup=0)
    self.nodetree.append_column(column1)

    renderer2 = gtk.CellRendererText()
    column2 = gtk.TreeViewColumn(T_VOTES,renderer2,text=1)
    self.nodetree.append_column(column2)

    renderer3 = gtk.CellRendererText()
    column3 = gtk.TreeViewColumn(T_STATUS,renderer3,text=2)
    self.nodetree.append_column(column3)

    #set up nodetree error message in case node info call fails
    self.scrolled_window = self.glade_xml.get_widget('scrolledwindow5')
    self.nodetree_error_label = self.glade_xml.get_widget('nodetree_error_label')

    self.prep_tree()

    #set up services tree structure
    self.servicetree = self.glade_xml.get_widget('servicetree')
    self.streemodel = gtk.TreeStore (gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gobject.TYPE_STRING,
                                    gobject.TYPE_STRING)
    self.servicetree.set_model(self.streemodel)

    self.servicetree.drag_source_set(gtk.gdk.BUTTON1_MASK, python_code_targets, gtk.gdk.ACTION_COPY)
    self.servicetree.connect('drag_data_get',self.source_drag_data_get)

    srenderer = gtk.CellRendererText()
    scolumn1 = gtk.TreeViewColumn(S_NAME,srenderer,markup=0)
    self.servicetree.append_column(scolumn1)

    srenderer2 = gtk.CellRendererText()
    scolumn2 = gtk.TreeViewColumn(S_STATE,srenderer2,markup=1)
    self.servicetree.append_column(scolumn2)

    srenderer3 = gtk.CellRendererText()
    scolumn3 = gtk.TreeViewColumn(S_OWNER,srenderer3,text=2)
    self.servicetree.append_column(scolumn3)

    srenderer4 = gtk.CellRendererText()
    scolumn4 = gtk.TreeViewColumn(S_LASTOWNER,srenderer4,text=3)
    self.servicetree.append_column(scolumn4)

    srenderer5 = gtk.CellRendererText()
    scolumn5 = gtk.TreeViewColumn(S_RESTARTS,srenderer5,text=4)
    self.servicetree.append_column(scolumn5)

    self.prep_service_tree()


    self.clustername = self.glade_xml.get_widget('entry25')
    self.clustername.set_text(self.command_handler.getClusterName())
    self.qbox = self.glade_xml.get_widget('checkbutton3')
    if self.command_handler.isClusterQuorate() == True:
      self.qbox.set_active(True)
    else:
      self.qbox.set_active(False)

    #Now set info labels
    self.glade_xml.get_widget('label90').set_text(STATUS % self.command_handler.getClusterStatus())
    if self.model_builder.getLockType() == DLM_TYPE:
      self.glade_xml.get_widget('label93').set_text(ON_MEMBER % self.command_handler.getNodeName())
    else:
      self.glade_xml.get_widget('label93').hide()

    self.glade_xml.get_widget('button17').connect("clicked",self.on_svc_enable)
    self.glade_xml.get_widget('button18').connect("clicked",self.on_svc_disable)
    self.glade_xml.get_widget('button19').connect("clicked",self.on_svc_restart)
    
    self.timer_id = 0
    self.onTimer() 

  def prep_tree(self):
    self.scrolled_window.show()
    self.nodetree_error_label.hide()
    treemodel = self.nodetree.get_model()
    treemodel.clear()

    try:
      nodes = self.command_handler.getNodesInfo(self.model_builder.getLockType())
    except CommandError, e:
      self.nodetree_error_label.set_text(NODEINFO_ERROR % e.getMessage())
      self.scrolled_window.hide()
      self.nodetree_error_label.show()
      #retval = MessageLibrary.errorMessage(e.getMessage())
      return

    for node in nodes:
      iter = treemodel.append(None)
      name, votes, status = node.getNodeProps()
      name_str = "<span size=\"10000\"><b>" + name + "</b></span>"
      treemodel.set(iter, TITLE_COL, name_str,
                          VOTES_COL, votes,
                          STATUS_COL, status,
                          NAME_COL, name) 

  def prep_service_tree(self):
    treemodel = self.servicetree.get_model()
    treemodel.clear()

    try:
      services = self.command_handler.getServicesInfo()
    except CommandError, e:
      retval = MessageLibrary.errorMessage(e.getMessage())
      return

    if len(services) == 0:
      iter = treemodel.append(None)
      treemodel.set(iter, S_NAME_COL, "<span foreground=\"red\"><b>" + NO_SERVICES + "</b></span>")
    else:
      for service in services:
        iter = treemodel.append(None)
        name, state, owner, lastowner, restarts = service.getServiceProps()
        name_str = "<span size=\"10000\"><b>" + name + "</b></span>"
        if state == "started":
          color = "green"
        else:
          color = "red"
        state_str = "<span foreground=\"" + color + "\">" + state + "</span>"
        treemodel.set(iter, S_TITLE_COL, name_str,
                            S_STATE_COL, state_str,
                            S_OWNER_COL, owner,
                            S_LASTOWNER_COL, lastowner,
                            S_RESTARTS_COL, restarts,
                            S_NAME_COL, name) 

  def onTimer(self):
    if self.model_builder.isClusterMember():
      self.glade_xml.get_widget('label90').set_text(MEMBER)
      self.prep_tree()
      self.prep_service_tree()
    else:
      self.glade_xml.get_widget('label90').set_text(UNKNOWN)
      self.nodetree.get_model().clear()
      self.servicetree.get_model().clear()

    if self.timer_id == 0:
        self.timer_id = gobject.timeout_add(10000, self.onTimer)
    
    return True
    
  def on_svc_enable(self, button):
    selection = self.servicetree.get_selection()
    model,iter = selection.get_selected()
    if iter == None:
      return
    svc_name = model.get_value(iter, S_NAME_COL)
    svc_title = model.get_value(iter,S_TITLE_COL)
    if svc_title == "" or svc_title == None:
      return
    self.grayOutMainWindow()
    commandstring = "clusvcadm -q -e \"" + svc_name + "\""
    errorstring = (_("Error: Service Enable failed - please check the logs for error messages.\n\nOnce the problem has been corrected, the 'Failed' service must first be Disabled before it can be Enabled."))
    fm = ForkedCommand(commandstring, PATIENCE_MESSAGE, errorstring, self.ungrayOutAndResetMainWindow)

  def on_svc_disable(self, button):
    selection = self.servicetree.get_selection()
    model,iter = selection.get_selected()
    if iter == None:
      return
    svc_name = model.get_value(iter, S_NAME_COL)
    svc_title = model.get_value(iter,S_TITLE_COL)
    if svc_title == "" or svc_title == None:
      return
    commandstring = "clusvcadm -q -d \"" + svc_name + "\""
    errorstring = _(" An error has occurred while disabling this service. Please check logs for details.")
    self.grayOutMainWindow()
    fm = ForkedCommand(commandstring, PATIENCE_MESSAGE, errorstring, self.ungrayOutAndResetMainWindow)

  def on_svc_restart(self, button):
    selection = self.servicetree.get_selection()
    model,iter = selection.get_selected()
    if iter == None:
      return
    svc_name = model.get_value(iter, S_NAME_COL)
    svc_title = model.get_value(iter,S_TITLE_COL)
    if svc_title == "" or svc_title == None:
      return
    commandstring = "clusvcadm -q -R \"" + svc_name + "\""
    errorstring = ""
    self.grayOutMainWindow()
    fm = ForkedCommand(commandstring, PATIENCE_MESSAGE, errorstring,self.ungrayOutAndResetMainWindow)

  def grayOutMainWindow(self):
    #Temporarily mothball main window
    watch = gtk.gdk.Cursor (gtk.gdk.WATCH)
    self.winMain.window.set_cursor(watch)
    self.winMain.set_sensitive(False)
                                                                              
  def ungrayOutMainWindow(self):
    self.winMain.window.set_cursor(None)
    self.winMain.set_sensitive(True)
                                                                              
  def ungrayOutAndResetMainWindow(self):
    self.winMain.window.set_cursor(None)
    self.winMain.set_sensitive(True)
    self.prep_service_tree()

  def dest_drag_data_received(self,w, context, x, y, selection_data, info, time):
    errorstring1 = ""
    errorstring2 = ""
    #row = w.get_path_at_pos(x,y-25)[0][0]
    drop_info = w.get_dest_row_at_pos(x,y)
    if drop_info == None:
      return
    row = w.get_path_at_pos(x,y-25)[0][0]
    model=w.get_model()
    iter=model.get_iter_first()
    for i in range(row):
        iter=model.iter_next(iter)
    m_name = model.get_value (iter, NAME_COL)
    
    #if s.getStateString() == 'Disabled':
    ###XXX Fix - find out how to get state info on service here
    s_name, s_state = selection_data.data.split(' -- ')
    if s_name.strip() == '' or s_state.strip() == '':
        return
    if s_state.strip().lower() == 'disabled':
      ### Service is 'Disabled' - just 'enable' on new member
      commandstring = "clusvcadm -q -e \"" + s_name + "\" -m " + m_name
      self.grayOutMainWindow()
      fm = ForkedCommand(commandstring, PATIENCE_MESSAGE, errorstring1, self.ungrayOutAndResetMainWindow)
    else:
      ### Service is not 'Disabled' - restart it on new member
      commandstring = "clusvcadm -q -r \"" + s_name + "\" -m " + m_name
      self.grayOutMainWindow()
      fm = ForkedCommand(commandstring, PATIENCE_MESSAGE, errorstring2, self.ungrayOutAndResetMainWindow)
                                                                            
    return 

  def source_drag_data_get(self,w, context, selection_data, info, time):
    s_name = ""
    s_state = ""
    selection=w.get_selection()
    result = selection.get_selected ()
    if result != None:
      (model, iter) = result
      try:
        s_name = model.get_value(iter, S_NAME_COL)
        s_state = model.get_value(iter, S_STATE_COL)
        
        if '<span' in s_state:
            s_state = s_state.replace('</span>', '')
            s_state = s_state.replace(s_state[s_state.find('<span'):s_state.find('>')+1], '').strip()
      except:
        pass
    selection_data.set(selection_data.target, 0, s_name + ' -- ' + s_state)
    return

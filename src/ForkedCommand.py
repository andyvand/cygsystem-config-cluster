#############################################################
### This class is a utility class that displays a busy/wait
### progress bar and a message in a Dialog box.
###
### Constructor Arguments:
### commandstring:  The command and args you wish the system to run.
### message:  The message you wish displayed in the dialog box.
### errorstring: If the system call return value is non-zero, 
###     the busy/wait dialog will be replaced by a message dialog
###     that informs the user with this error string. If an errorstring
###     is not provided, a default generic one is used.
### post_fork_command: This is an optional param. If the calling party
###     wishes to have a method called when the child process 
###     has completed, it can be passed in here. 

import time
import gobject
import gtk
import os
import signal
import sys

EXT_PID = 0
SIGCHLD_RECIEVED = 0
ERROR_MESSAGE =_("An error has occurred while running a system command. Please check logs for details.") 


class ForkedCommand:
  def __init__(self,commandstring,message,errorstring, post_fork_command=None):
    global ERROR_MESSAGE
    global SIGCHLD_RECIEVED
    global EXT_PID
    
    self.timeout_id = 0
    self.pbar_timer = 0
    self.be_patient_dialog = 0
    self.system_command_retval = 0
    EXT_PID = 0
    SIGCHLD_RECIEVED = 0

    self.commandstring = commandstring
    self.message = message
    if(errorstring == ""):
      self.errorstring = ERROR_MESSAGE
    else:
      self.errorstring = errorstring

    self.post_fork_command = post_fork_command
    
    try:
      EXT_PID = os.fork()
    except OSError:
      sys.exit("Unable to create child to call clusvcadm.")
                                                                          
    if (EXT_PID != 0):
      #parent process

      #spawn dialog
      signal.signal(signal.SIGCHLD, self.serviceSignalHandler)
      self.timeout_id = gobject.timeout_add(100, self.showDialog, self.message)
                                                                          
    else:
      #child process
      ret = os.system(self.commandstring)
      if os.WIFEXITED(ret):
        # child exited normaly
        status = os.WEXITSTATUS(ret)
      else:
        status = -1
      os._exit(status)

  def showDialog(self,message):
    global SIGCHLD_RECIEVED
    
    if(SIGCHLD_RECIEVED == 1):
        return self.cleanup()
 
    self.be_patient_dialog = gtk.Dialog()
    self.be_patient_dialog.set_modal(True)
    self.be_patient_dialog.connect("response", self.__on_delete_event)
    self.be_patient_dialog.connect("close", self.__on_delete_event)
    self.be_patient_dialog.connect("delete_event", self.__on_delete_event)
    
    self.be_patient_dialog.set_has_separator(False)
    
    label = gtk.Label(message)
    self.be_patient_dialog.vbox.pack_start(label, True, True, 0)
    
    #Create an alignment object that will center the pbar
    align = gtk.Alignment(0.5, 0.5, 0, 0)
    self.be_patient_dialog.vbox.pack_start(align, False, False, 5)
    align.show()
                                                                            
    self.pbar = gtk.ProgressBar()
    align.add(self.pbar)
    self.pbar.show()

    #Start bouncing progress bar
    self.pbar_timer = gobject.timeout_add(100, self.progress_bar_timeout)

    self.be_patient_dialog.show_all()
    self.timeout_id = 0
    return False
                                                                            
  def progress_bar_timeout(self):
    global SIGCHLD_RECIEVED
    
    if (SIGCHLD_RECIEVED == 0):
      self.pbar.pulse()
      return True
    else:
      return self.cleanup()

  def serviceSignalHandler(self, signal_number, frame):
    global SIGCHLD_RECIEVED
    global EXT_PID

    my_pid = os.getpid()
    
    reaped, status = -1, -1
    try:
      (reaped, status) = os.waitpid(EXT_PID, os.WNOHANG)
    except IOError:
        print "Spurious IO signal error in waitpid attempt"
    except OSError:
        print "Spurious OS signal error in waitpid attempt"

    if(reaped == EXT_PID):
      if os.WIFEXITED(status):
        # child exited normaly
        SIGCHLD_RECIEVED = 1
        self.system_command_retval = os.WEXITSTATUS(status)
        
      elif WIFSIGNALED(status):
        # child terminated due to being signaled
        SIGCHLD_RECIEVED = 1
        self.system_command_retval = -1
        
      else:
        # child stopped, continue waiting for its death
        print "Child stopped, waiting for it; it might take long time"
    
  
  def post_fork(self):
    if(self.post_fork_command):
      apply(self.post_fork_command)

  def cleanup(self):
    global SIGCHLD_RECIEVED
    
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    SIGCHLD_RECIEVED = 0
    
    if(self.timeout_id != 0):
      gobject.source_remove(self.timeout_id)
    if(self.pbar_timer != 0):
      gobject.source_remove(self.pbar_timer)
    if(self.be_patient_dialog):
      self.be_patient_dialog.destroy()
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    
    if(self.system_command_retval):
      self.errorMessage(self.errorstring)
    self.post_fork()
    return 0
  
  def __on_delete_event(self, *args):
    return True
  
  def errorMessage(self, message):
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                            message)
    dlg.show_all()
    rc = dlg.run()
    dlg.destroy()
    return rc
 

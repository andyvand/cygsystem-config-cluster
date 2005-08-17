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
    self.fd_read = 0
    self.fd_write = 0
    EXT_PID = 0
    SIGCHLD_RECIEVED = 0

    self.commandstring = commandstring
    self.message = message
    if(errorstring == ""):
      self.errorstring = ERROR_MESSAGE
    else:
      self.errorstring = errorstring

    self.post_fork_command = post_fork_command

    #This pipe is for the parent process to receive
    #the result of the system call in the child process,
    #and take appropriate action if an error has occurred.
    self.fd_read, self.fd_write = os.pipe()

    try:
      EXT_PID = os.fork()
    except OSError:
      sys.exit("Unable to create child to call clusvcadm.")
                                                                          
    if (EXT_PID != 0):
      #parent process

      #spawn dialog
      signal.signal(signal.SIGCHLD, self.serviceSignalHandler)
      self.timeout_id = gtk.timeout_add(100, self.showDialog, self.message)
                                                                          
    else:
      #child process
      self.system_command_retval = os.system(self.commandstring)

      #let parent process know result of system call through IPC
      if(self.system_command_retval):
        os.write(self.fd_write, "failure")
      else:
        os.write(self.fd_write, "success")

      os._exit(self.system_command_retval)

  def showDialog(self,message):
    global SIGCHLD_RECIEVED

    if(SIGCHLD_RECIEVED == 1):
        return self.cleanup()
 
    self.be_patient_dialog = gtk.Dialog()
    label = gtk.Label(message)
    self.be_patient_dialog.vbox.pack_start(label, True, True, 0)
    self.be_patient_dialog.set_modal(True)
                                                                            
    #Create an alignment object that will center the pbar
    align = gtk.Alignment(0.5, 0.5, 0, 0)
    self.be_patient_dialog.vbox.pack_start(align, False, False, 5)
    align.show()
                                                                            
    self.pbar = gtk.ProgressBar()
    align.add(self.pbar)
    self.pbar.show()

    #Start bouncing progress bar
    self.pbar_timer = gtk.timeout_add(100, self.progress_bar_timeout)

    self.be_patient_dialog.show_all()
    self.timeout_id = 0
    return False
                                                                            
  def progress_bar_timeout(self):
    global SIGCHLD_RECIEVED

    self.pbar.pulse()
    if (SIGCHLD_RECIEVED == 0):
      return True
    else:
      return self.cleanup()

  def serviceSignalHandler(self, signal_number, frame):
    global SIGCHLD_RECIEVED
    global EXT_PID

    my_pid = os.getpid()

    #Stop caring about SIGCHLD...
    #signal.signal(signal.SIGCHLD, signal.SIG_DFL)

    try:
      (reaped, status) = os.waitpid((-1),0)
    except IOError:
        print "Spurious IO signal error in waitpid attempt"
    except OSError:
        print "Spurious OS signal error in waitpid attempt"

    if(reaped == EXT_PID):
      SIGCHLD_RECIEVED = 1

      #Check how things went with the system call
      first_char = os.read(self.fd_read, 1)
      if(first_char == 's'):
        self.system_command_retval = 0
      else:
        self.system_command_retval = 1
   
  def post_fork(self):
    if(self.post_fork_command):
      apply(self.post_fork_command)

  def cleanup(self):
    global SIGCHLD_RECIEVED
    SIGCHLD_RECIEVED = 0

    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    if(self.timeout_id != 0):
      gtk.timeout_remove(self.timeout_id)
    if(self.pbar_timer != 0):
      gtk.timeout_remove(self.pbar_timer)
    if(self.be_patient_dialog):
      self.be_patient_dialog.destroy()
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
    
    if(self.system_command_retval):
      self.errorMessage(self.errorstring)
    self.post_fork()
    return 0

  def errorMessage(self, message):
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                            message)
    dlg.show_all()
    rc = dlg.run()
    dlg.destroy()
    return rc
 

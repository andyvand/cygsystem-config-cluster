import gtk 

def warningMessage(message):
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_YES_NO,
                            message)
    dlg.show_all()
    rc = dlg.run()
    dlg.destroy()
    if (rc == gtk.RESPONSE_NO):
      return gtk.RESPONSE_NO
    if (rc == gtk.RESPONSE_DELETE_EVENT):
      return gtk.RESPONSE_NO
    if (rc == gtk.RESPONSE_CLOSE):
      return gtk.RESPONSE_NO
    if (rc == gtk.RESPONSE_CANCEL):
      return gtk.RESPONSE_NO
                                                                                
    return rc
                                                                                
def errorMessage( message):
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                            message)
    dlg.show_all()
    rc = dlg.run()
    dlg.destroy()
    return rc
                                                                                
def infoMessage( message):
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO,
                            message)
    dlg.show_all()
    rc = dlg.run()
    dlg.destroy()
    return rc
                                                                                
def simpleInfoMessage( message):
    dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                            message)
    dlg.show_all()
    rc = dlg.run()
    dlg.destroy()
    return rc
                                                                                
 

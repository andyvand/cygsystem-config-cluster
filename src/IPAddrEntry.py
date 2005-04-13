import gtk

from gtk import TRUE, FALSE

class IP (gtk.HBox):
  def __init__ (self):
    gtk.HBox.__init__ (self)
    self.set_spacing (3)

    self.e1 = gtk.Entry ()
    self.e1.set_property ("xalign", 1.0)
    self.e1.set_property ("width-chars", 3)
    self.e1.set_property ("max_length", 3)
    self.pack_start (self.e1, False, False, 0)
    self.pack_start (gtk.Label ('-'), False, False, 0)

    self.e2 = gtk.Entry ()
    self.e2.set_property ("xalign", 1.0)
    self.e2.set_property ("width-chars", 3)
    self.e2.set_property ("max_length", 3)
    self.pack_start (self.e2, False, False, 0)
    self.pack_start (gtk.Label ('-'), False, False, 0)

    self.e3 = gtk.Entry ()
    self.e3.set_property ("xalign", 1.0)
    self.e3.set_property ("width-chars", 3)
    self.e3.set_property ("max_length", 3)
    self.pack_start (self.e3, False, False, 0)
    self.pack_start (gtk.Label ('-'), False, False, 0)

    self.e4 = gtk.Entry ()
    self.e4.set_property ("xalign", 1.0)
    self.e4.set_property ("width-chars", 3)
    self.e4.set_property ("max_length", 3)
    self.pack_start (self.e4, False, False, 0)

  def clear(self):
    self.e1.set_text("")
    self.e2.set_text("")
    self.e3.set_text("")
    self.e4.set_text("")

  def getAddrAsString(self):
    rtval = self.e1.get_text() + "." + \
            self.e2.get_text() + "." + \
            self.e3.get_text() + "." + \
            self.e4.get_text()

    return rtval

  def getAddrAsList(self):
    rtlist = list()
    rtlist.append(self.e1.get_text())
    rtlist.append(self.e2.get_text())
    rtlist.append(self.e3.get_text())
    rtlist.append(self.e4.get_text())

    return rtlist

  def setAddrFromString(self, addr):
    octets = addr.split(".")
    self.e1.set_text(octets[0])
    self.e2.set_text(octets[1])
    self.e3.set_text(octets[2])
    self.e4.set_text(octets[3])

  def setAddrFromList(self, addr):
    pass

  #This method just checks that all fields are filled in
  def isValid(self):
    if self.e1.get_text().strip() == "":
      return FALSE
    elif self.e2.get_text().strip() == "":
      return FALSE
    elif self.e3.get_text().strip() == "":
      return FALSE
    elif self.e4.get_text().strip() == "":
      return FALSE

    return TRUE

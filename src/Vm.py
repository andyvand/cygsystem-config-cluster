import string
from TagObject import TagObject
import gettext
_ = gettext.gettext

VM_NAME=_("Virtual Service Name: %s")
VM_PATH=_("Path to Specification File: %s")

TAG_NAME = "vm"

class Vm(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    #Have autostart set by default
    self.addAttribute("autostart","1")

  def getProperties(self):
    stringbuf = ""
    stringbuf = VM_NAME % self.getName() + "\n"
    try:
      stringbuf = stringbuf + VM_PATH % self.getAttribute('path') + "\n"
    except KeyError, e:
      pass  #just don't print out path

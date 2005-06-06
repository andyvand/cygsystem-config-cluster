import string
from TagObject import TagObject

TAG_NAME = "service"

class Service(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    #Have autostart set by default
    self.addAttribute("autostart","1")

  def getProperties(self):
    stringbuf = ""
    return stringbuf

import string
from TagObject import TagObject

TAG_NAME = "ip"

class Ip(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.addAttribute("name"," ")

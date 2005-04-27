import string
from TagObject import TagObject

TAG_NAME = "lockserver"

class Lockserver(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME 

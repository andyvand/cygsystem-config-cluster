import string
from TagObject import TagObject

TAG_NAME = "method"

class Method(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getProperties(self):
    return "Fence Level"

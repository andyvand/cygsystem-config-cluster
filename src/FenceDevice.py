import string
from TagObject import TagObject

TAG_NAME = "fencedevice"

class FenceDevice(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getAgentType(self):
    return self.attr_hash["agent"]

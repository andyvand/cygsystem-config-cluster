import string
from TagObject import TagObject

TAG_NAME = "fencedevices"

class FenceDevices(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

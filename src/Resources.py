import string
from TagObject import TagObject

TAG_NAME = "resources"

class Resources(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

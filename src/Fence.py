import string
from TagObject import TagObject

TAG_NAME = "fence"
CONFIG_VERSION = "6"

class Fence(TagObject):
  def __init__(self, name="default", config_version=CONFIG_VERSION):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME 


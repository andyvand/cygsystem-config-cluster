import string
from TagObject import TagObject

TAG_NAME = "cluster"
CONFIG_VERSION = "6"

class Cluster(TagObject):
  def __init__(self, name="default", config_version=CONFIG_VERSION):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.addAttribute("name",name)
    self.addAttribute("config_version",config_version)

import string
from TagObject import TagObject

TAG_NAME = "base_resource"  #This tag name should never be seen

class BaseResource(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.resource_type = ""
    self.deny_all_children = False

  def getResourceType(self):
    return self.resource_type

  def isDenyAll(self):
    return self.deny_all_children
    

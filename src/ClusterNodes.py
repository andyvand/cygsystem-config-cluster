import string
from TagObject import TagObject

TAG_NAME = "clusternodes"

class ClusterNodes(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

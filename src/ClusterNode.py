import string
from TagObject import TagObject

TAG_NAME = "clusternode"

class ClusterNode(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getFenceLevels(self):
    #under this node will be a 'fence' block, then 0 or more 'method'  blocks.
    #This method returns the set of 'method' objs. 'method' blocks represent
    #fence levels
    child = self.getChildren()
    if len(child) > 0:
      return child[0].getChildren()
    else:
      return List()

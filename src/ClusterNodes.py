import string
from TagObject import TagObject

import gettext
_ = gettext.gettext
CLUSTER_POPULATION=_("There are currently %d member \n nodes in this cluster")
CLUSTER_POPULATION_ONE=_("There is currently one member \n node in this cluster")


TAG_NAME = "clusternodes"
CLUSTERNODES=_("Cluster Nodes")

class ClusterNodes(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getProperties(self):
    kids = self.getChildren()
    numkids = len(kids) 
    if numkids == 1:
      stringbuf = CLUSTER_POPULATION_ONE
    else:
      stringbuf = CLUSTER_POPULATION % numkids

    return stringbuf

  def getName(self):
    return CLUSTERNODES

import string
from TagObject import TagObject

import gettext
_ = gettext.gettext
CLUSTER_POPULATION=_("There are currently %d member \n nodes in this cluster")


TAG_NAME = "clusternodes"
CLUSTERNODES=_("Cluster Nodes")

class ClusterNodes(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getProperties(self):
    chilluns = self.getChildren()
    numkids = len(chilluns) 
    stringbuf = CLUSTER_POPULATION % numkids

    return stringbuf

  def getName(self):
    return CLUSTERNODES

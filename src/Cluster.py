import string
from TagObject import TagObject

TAG_NAME = "cluster"
import gettext
_ = gettext.gettext

CLUSTER_NAME=_("Cluster Name: %s")
CLUSTER_POPULATION=_("Number of Members: %d")
                                                                                
class Cluster(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getProperties(self):
    stringbuf = ""
    special_kid = None
    kidname = ""
    numkids = 0

    stringbuf = CLUSTER_NAME % self.getAttribute("name") + "\n"
    kids = self.getChildren()
    for kid in kids:
      try:
        kidname = kid.getName()
        if kidname.strip() == "clusternodes":
          special_kid = kid
          break
      except KeyError, e:
        kidname = ""
        continue
   
    if special_kid != None:
      chilluns = special_kid.getChildren() #Should be clusternodes...
      numkids = len(chilluns) #numkids == number of nodes in cluster

    stringbuf = stringbuf + CLUSTER_POPULATION % numkids

    return stringbuf

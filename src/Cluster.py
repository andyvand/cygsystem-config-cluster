import string
from TagObject import TagObject
from gtk import TRUE, FALSE

TAG_NAME = "cluster"
import gettext
_ = gettext.gettext

CLUSTER_NAME=_("Cluster Name: %s")
CLUSTER_POPULATION=_("Number of Members: %d")
DLM_TYPE=_("Locking Type: Distributed")
GULM_TYPE=_("Locking Type: GuLM")
LOCKSERVER=_("Lock Server:")
CONFIG_VERSION=_("Config Version")
                                                                                
class Cluster(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getProperties(self):
    stringbuf = ""
    special_kid = None
    kidname = ""
    numkids = 0
    dlm_locking = TRUE
    gulm_ptr = None

    stringbuf = CLUSTER_NAME % self.getAttribute("name") + "\n"

    stringbuf = stringbuf + CONFIG_VERSION + ": " + self.getConfigVersion() + "\n"

    kids = self.getChildren()
    for kid in kids:
      try:
        kidname = kid.getTagName()
        if kidname.strip() == "clusternodes":
          special_kid = kid
          break
      except KeyError, e:
        kidname = ""
        continue
   
    if special_kid != None:
      cnodes = special_kid.getChildren() #Should be clusternodes...
      numkids = len(cnodes) #numkids == number of nodes in cluster

    ###Here we walk through list of children an inefficient second time,
    ###But there will only be a few children here, and searching for
    ###both tag types in one loop will just make the loop code messy, imho
    kids = self.getChildren()
    for kid in kids:
      try:
        kidname = kid.getTagName()
        if kidname.strip() == "cman":
          dlm_locking = TRUE
          gulm_ptr = None          
          break
        if kidname.strip() == "gulm":
          dlm_locking = FALSE
          gulm_ptr = kid          
          break
      except KeyError, e:
        kidname = ""
        continue

    stringbuf = stringbuf + CLUSTER_POPULATION % numkids + "\n\n"

    if dlm_locking == TRUE:
      stringbuf = stringbuf + DLM_TYPE
    else:
      stringbuf = stringbuf + GULM_TYPE + "\n"
      lockservers = gulm_ptr.getChildren()
      for server in lockservers:
        stringbuf = stringbuf + "  " + LOCKSERVER + "  " + server.getName() + "\n"

    return stringbuf

  def getConfigVersion(self):
    version = self.getAttribute("config_version")
    return version

  def setConfigVersion(self, version):
    self.addAttribute(version)

  def incrementConfigVersion(self):
    version = self.getAttribute("config_version")
    intversion = int(version)
    intversion = intversion + 1
    self.addAttribute("config_version", str(intversion))

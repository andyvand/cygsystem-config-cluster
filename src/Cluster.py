import string
from TagObject import TagObject

TAG_NAME = "cluster"
import gettext
_ = gettext.gettext

CLUSTER_NAME=_("Cluster Name: %s")
CLUSTER_POPULATION=_("Number of Members: %d")
DLM_TYPE=_("Locking Type: Distributed")
GULM_TYPE=_("Locking Type: GULM")
LOCKSERVER=_("Lock Server:")
CONFIG_VERSION=_("Config Version")
MCAST_MODE=_("Cluster Manager using Multicast Mode. \n   Multicast Address: %s")
                                                                                
class Cluster(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.is_cfg_version_dirty = False

  def getProperties(self):
    stringbuf = ""
    special_kid = None
    kidname = ""
    numkids = 0
    dlm_locking = True
    gulm_ptr = None
    isMulticast = False
    mcast_address = ""

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
          dlm_locking = True
          gulm_ptr = None 
          cman_kids = kid.getChildren()
          for cman_kid in cman_kids:
            if cman_kid.getTagName() == "multicast":
              isMulticast = True
              mcast_address = cman_kid.getAttribute("addr")
              break
          break
        if kidname.strip() == "gulm":
          dlm_locking = False
          gulm_ptr = kid          
          break
      except KeyError, e:
        kidname = ""
        continue

    stringbuf = stringbuf + CLUSTER_POPULATION % numkids + "\n\n"

    if dlm_locking == True:
      stringbuf = stringbuf + DLM_TYPE + "\n"
      if isMulticast == True:
        stringbuf = stringbuf + (MCAST_MODE % mcast_address)
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
    current_version = self.getConfigVersion()
    if current_version == version:
      return

    self.addAttribute("config_version", version)
    self.is_cfg_version_dirty = True

  def incrementConfigVersion(self):
    version = self.getAttribute("config_version")
    intversion = int(version)
    intversion = intversion + 1
    self.addAttribute("config_version", str(intversion))
    #self.is_cfg_version_dirty = True

  #def addAttribute(self, name, value):
  #  if name == "config_version":
  #    cfg = self.getAttribute("config_version")
  #    if cfg != None:
  #      if int(value) != int(cfg):
  #        self.is_cfg_version_dirty = True
  # 
  #  self.attr_hash[name] = value


  def generateXML(self, doc, parent=None):
    if self.is_cfg_version_dirty == False:
      self.incrementConfigVersion()
    else:
      self.is_cfg_version_dirty = False
    tag = doc.createElement(self.TAG_NAME)
    if parent != None:
      parent.appendChild(tag)
    else:
      doc.appendChild(tag)
    #tag = parent.createChildElement(TAG_NAME)
    self.exportAttributes(tag)
    #parent.appendChild(tag)
    if len(self.children) > 0:
      for child in self.children:
        if child == None:
          continue
        child.generateXML(doc, tag)
                                                                                


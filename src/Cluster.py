import string
from TagObject import TagObject

TAG_NAME = "cluster"
import gettext
_ = gettext.gettext

CLUSTER_NAME_ALIAS=_("Cluster Name Alias: %s")
ACTUAL_CLUSTER_NAME=_("Actual Cluster Name: %s")
ACTUAL_CLUSTER_NAME_DESC=_("The Actual Cluster Name should \n be used for storage configuration,\n such as making a clustered file system")
CLUSTER_POPULATION=_("Number of Members: %d")
DLM_TYPE=_("Locking Type: Distributed")
GULM_TYPE=_("Locking Type: GULM")
LOCKSERVER=_("Lock Server:")
CONFIG_VERSION=_("Config Version")
MCAST_MODE=_("Cluster Manager using Custom Multicast Mode. \n   Multicast Address: %s")

#Quorum disk attributes
QD_USAGE=_("Quorum Disk In Use")
QD_INTERVAL=_("Interval: %s")
QD_TKO=_("TKO Value: %s")
QD_VOTES=_("Votes: %s")
QD_MIN_SCORE=_("Minimum Score: %s")
QD_DEVICE=_("Device: %s")
QD_LABEL=_("Label: %s")
HEURISTICS=_("    Heuristics")
H_PROGRAM=_("      Program: %s")
H_SCORE=_("      Score: %s")
H_INTERVAL=_("      Interval: %s")
                                                                                
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
    isQuorumD = False

    stringbuf = CLUSTER_NAME_ALIAS % self.getNameAlias() + "\n"

    stringbuf = stringbuf + ACTUAL_CLUSTER_NAME % self.getName() + "\n"

    stringbuf = stringbuf + ACTUAL_CLUSTER_NAME_DESC + "\n"

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
      stringbuf = stringbuf + DLM_TYPE + "\n\n"
      if isMulticast == True:
        stringbuf = stringbuf + (MCAST_MODE % mcast_address) + "\n\n"
    else:
      stringbuf = stringbuf + GULM_TYPE + "\n"
      lockservers = gulm_ptr.getChildren()
      for server in lockservers:
        stringbuf = stringbuf + "  " + LOCKSERVER + "  " + server.getName() + "\n"

    quorumd_ptr = self.doesClusterUseQuorumDisk()
    if quorumd_ptr != None:
      interval = quorumd_ptr.getAttribute('interval')
      if interval == None:
        interval = ""
      min_score = quorumd_ptr.getAttribute('min_score')
      if min_score == None:
        min_score = ""
      votes = quorumd_ptr.getAttribute('votes')
      if votes == None:
        votes = ""
      tko = quorumd_ptr.getAttribute('tko')
      if tko == None:
        tko = ""

      device = quorumd_ptr.getAttribute('device')
        
      label = quorumd_ptr.getAttribute('label')

      stringbuf = stringbuf + QD_USAGE + "\n\n" 
      stringbuf = stringbuf + QD_INTERVAL % interval + "\n" 
      stringbuf = stringbuf + QD_VOTES % votes + "\n" 
      stringbuf = stringbuf + QD_TKO % tko + "\n" 
      stringbuf = stringbuf + QD_MIN_SCORE % min_score + "\n" 
      if device != None:
        stringbuf = stringbuf + QD_DEVICE % device + "\n\n" 
      elif label != None:
        stringbuf = stringbuf + QD_LABEL % device + "\n\n" 

      heurs = quorumd_ptr.getChildren()
      if len(heurs) > 0:
        stringbuf = stringbuf + HEURISTICS + "\n"
        for heur in heurs:
          h_interval = heur.getAttribute('interval')
          if h_interval == None:
            h_interval = ""
          h_program = heur.getAttribute('program')
          if h_program == None:
            h_program = ""
          h_score = heur.getAttribute('score')
          if h_score == None:
            h_score = ""
          stringbuf = stringbuf + H_PROGRAM % h_program + "\n"
          stringbuf = stringbuf + H_INTERVAL % h_interval + "\n"
          stringbuf = stringbuf + H_SCORE % h_score + "\n"
      

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

  def getNameAlias(self):
    alias = self.getAttribute("alias")
    if alias == None:
      name = self.getAttribute("name")
      self.addAttribute("alias", name)
      return self.getAttribute("alias")
    else:
      return alias

  def doesClusterUseQuorumDisk(self):
    kids = self.getChildren()
    for kid in kids:
      if kid.getTagName().strip() == "quorumd":
        return kid

    return None


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
                                                                                


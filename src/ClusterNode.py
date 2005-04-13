import string
from TagObject import TagObject
from gtk import TRUE, FALSE

TAG_NAME = "clusternode"
import gettext
_ = gettext.gettext

FENCE_STATUS=_("Fence Status: ")
NOT_CURRENTLY_FENCED=_("Not currently fenced")
CURRENT_FENCING=_("One fence in one fence level.")
CURRENTS_FENCING=_("%d fences in one fence level.")
CURRENT_FENCINGS=_("One fence.")
CURRENTS_FENCINGS=_("%d fences in %d fence levels.")
CURRENT_VOTES=_("Quorom Votes: %s")

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
      retval = list()
      return retval

  def getMulticastNode(self):
    children = self.getChildren()
    for child in children:
      if child.getTagName() == "multicast":
        return child

    return None

  def getInterface(self):
    nd = self.getMulticastNode()
    if nd == None:
      return None
    else:
      return nd.getAttribute("interface")

  def setInterface(self, ifc):
    nd = self.getMulticastNode()
    if nd == None:
      return 
    else:
      nd.addAttribute("interface",ifc)


  def getProperties(self):
    stringbuf = ""
    try:
      vts = self.getAttribute("votes")
    except KeyError, e:
      vts = "1"
    fence_sum = 0
    flevels = self.getFenceLevels()
    num_levels = len(flevels)
    if num_levels == 0:
      return CURRENT_VOTES % vts + "\n\n" + FENCE_STATUS + "\n    " + NOT_CURRENTLY_FENCED

    for flevel in flevels:
      fence_sum = fence_sum + len(flevel.getChildren())

    if fence_sum == 1 and num_levels == 1:
      fence_str = CURRENT_FENCING
    elif fence_sum > 1 and num_levels == 1:
      fence_str = CURRENTS_FENCING % fence_sum
    elif fence_sum == 1 and num_levels > 1:
      fence_str = CURRENT_FENCINGS 
    else:
      fence_str = CURRENTS_FENCINGS % (fence_sum, num_levels)

    return CURRENT_VOTES % vts + "\n\n" + FENCE_STATUS + "\n    " + fence_str

  def isFenced(self):
    fence_sum = 0
    flevels = self.getFenceLevels()
    if len(flevels) == 0:
      return FALSE

    for flevel in flevels:
      fence_sum = fence_sum + len(flevel.getChildren())

    if fence_sum > 0:
      return TRUE
    else:
      return FALSE

import string
from TagObject import TagObject
import FenceHandler 

TAG_NAME = "fencedevices"

import gettext
_ = gettext.gettext
NO_FDS=_("No Fence Devices Configured")
TYPE=_("Type")
TYPES=_("Types")
CURRENTLY_CONFIGURED=_("Currently Configured:")

class FenceDevices(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getProperties(self):
    fence_opts = FenceHandler.FENCE_OPTS
    counter_hash = {}
    fdevs = self.getChildren()
    if len(fdevs) == 0:
      return NO_FDS

    stringbuf = CURRENTLY_CONFIGURED + "\n\n"

    for fd in fdevs:
      agent = fd.getAgentType()
      x = 0
      try:
        x = counter_hash[agent]
        counter_hash[agent] = x + 1
      except KeyError, e:
        counter_hash[agent] = 1

    kees = counter_hash.keys()
    for kee in kees:
      num = counter_hash[kee]
      if num > 1:
        stringbuf = stringbuf + "%d - " % num + fence_opts[kee] + " " + TYPES
        stringbuf = stringbuf + "\n"
      else: 
        stringbuf = stringbuf + "%d - " % num + fence_opts[kee] + " " + TYPE
        stringbuf = stringbuf + "\n"
   
    return stringbuf 

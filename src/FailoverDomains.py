import string
from TagObject import TagObject

TAG_NAME = "failoverdomains"
import gettext
_ = gettext.gettext
                                                                                

CURRENT_FAILDOMS=_("%d Failover Domains configured.")

NO_FDOMS=_("No Domains Currently Configured.")

class FailoverDomains(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getProperties(self):
    stringbuf = ""
    numkin = 0
    name_hash = {}
    kids = self.getChildren()
    numkin = len(kids)
    if numkin == 0:
      return NO_FDOMS

    #This double loop adds all failoverdomainnode names to a hash table as keys.
    #Used for counting how many nodes are employed in failover domains
    #for kid in kids:
    #  kiddies = kid.getChildren()
    #  for kiddie in kiddies:
    #    name_hash[kiddie.getName().strip()] = 0
    ##
    #numnodes = len(name_hash.keys())

    stringbuf = CURRENT_FAILDOMS % numkin

    return stringbuf

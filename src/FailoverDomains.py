import string
from TagObject import TagObject

TAG_NAME = "failoverdomains"
import gettext
_ = gettext.gettext
                                                                                

OF_CURRENT_FAILDOMS=_("Of the %d Failover Domains \n configured for this cluster, \n %d current clusternodes are included \n as Failover Domain members.")

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

    #This double loop adds all failoverdomainnode names to a hash table as keys.
    for kid in kids:
      kiddies = kid.getChildren()
      for kiddie in kiddies:
        name_hash[kiddie.getName().strip()] = 0

    numnodes = len(name_hash.keys())

    stringbuf = OF_CURRENT_FAILDOMS % (numkin,numnodes)

    return stringbuf

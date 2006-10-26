import string
from TagObject import TagObject

TAG_NAME = "rm"

import gettext
_ = gettext.gettext

NUM_FDOMS=_("Number of defined Failover Domains: %d")
NUM_RESOURCES=_("Number of Shareable Resources: %d")
NUM_SERVICES=_("Number of declared Services: %d")

class Rm(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME 

  def getProperties(self):
    stringbuf = ""

    num_fdoms = 0
    num_resources = 0
    num_services = 0

    children = self.getChildren()
    for child in children:
      tagname = child.getTagName()
      if tagname == "failoverdomains":
        num_fdoms = len(child.getChildren()) 
      elif tagname == "resources":
        num_resources = len(child.getChildren()) 
      elif tagname == "service":
        num_services = num_services + 1 

    stringbuf = NUM_FDOMS % num_fdoms + "\n"
    stringbuf = stringbuf + NUM_RESOURCES % num_resources + "\n"
    stringbuf = stringbuf + NUM_SERVICES % num_services

    return stringbuf

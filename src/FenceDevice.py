import string
import FenceHandler
from TagObject import TagObject

TAG_NAME = "fencedevice"

import gettext
_ = gettext.gettext

TYPE=_("Type")

class FenceDevice(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.fd_attrs = FenceHandler.FENCE_FD_ATTRS
    self.pretty_fence_names = FenceHandler.FENCE_OPTS
    self.pretty_name_attrs = FenceHandler.PRETTY_NAME_ATTRS

  def getAgentType(self):
    return self.attr_hash["agent"]

  def getProperties(self):
    stringbuf = ""
    agent_type = self.getAgentType()
    pretty_fence_type = self.pretty_fence_names[agent_type]
    attrlist = self.fd_attrs[agent_type]
                                                                                
    stringbuf = stringbuf + "<span><b>" + TYPE + ": " + "</b>" + pretty_fence_type + "\n</span>"
    i = 0 
    print "len attrl.ist is %d" % len(attrlist)
    for attr in attrlist:
      print "I = %d" % i
      i = i + 1
      print "Ding Dang It! it is -->%s<--" % self.pretty_name_attrs[attr] 
      try:
        NAME = self.pretty_name_attrs[attr]
        VALUE = self.getAttribute(attr)
      except KeyError, e:
        NAME = None
        VALUE = None

      if (NAME != None) and (VALUE != None):
        stringbuf = stringbuf + "<span><b>" + NAME + ": " + "</b>" + VALUE + "\n</span>"
                                                                                
    return stringbuf


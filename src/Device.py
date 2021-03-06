import string
import FenceHandler
import cgi
from TagObject import TagObject

TAG_NAME = "device"
OPTION = "option"

import gettext
_ = gettext.gettext

TYPE=_("Type")

#New Power Controller Fence Agent names should be added to
#the list below
power_controller_list=["fence_wti","fence_apc","fence_apc_snmp"]

class Device(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.agent_type = ""
    self.has_native_option_set = False
    self.fi_attrs = FenceHandler.FENCE_FI_ATTRS
    self.pretty_fence_names = FenceHandler.FENCE_OPTS
    self.pretty_name_attrs = FenceHandler.PRETTY_NAME_ATTRS

  def getAgentType(self):
    return self.agent_type

  def setAgentType(self, agent_type):
    self.agent_type = agent_type

  def hasNativeOptionSet(self):
    return self.has_native_option_set

  def isPowerController(self):
    for item in power_controller_list:
      if self.agent_type == item:
        return True

    return False

  def addAttribute(self, name, value):
    if name == OPTION:
      self.has_native_option_set = True
    self.attr_hash[name] = value

  def getProperties(self):
    stringbuf = ""
    pretty_fence_type = self.pretty_fence_names[self.agent_type]
    attrlist = self.fi_attrs[self.agent_type]

    stringbuf = stringbuf + "<span><b>" + TYPE + ": " + "</b>" + pretty_fence_type + "\n</span>"

    for attr in attrlist:
      NAME = self.pretty_name_attrs[attr]
      if self.getAttribute(attr) == None:
        continue
      VALUE = cgi.escape(self.getAttribute(attr))
      stringbuf = stringbuf + "<span><b>" + NAME + ": " + "</b>" + VALUE + "\n</span>"

    return stringbuf



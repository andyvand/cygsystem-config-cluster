import string
from TagObject import TagObject

TAG_NAME = "device"

class Device(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.agent_type = ""

  def getAgentType(self):
    return self.agent_type

  def setAgentType(self, agent_type):
    self.agent_type = agent_type

  def getProperties(self):
    return "A Fence"

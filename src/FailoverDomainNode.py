import string
from TagObject import TagObject

TAG_NAME = "failoverdomainnode"

class FailoverDomainNode(TagObject):
  def __init__(self):
    self.priority_level = 1
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.addAttribute("priority",str(self.priority_level))

  def raisePriorityLevel(self):
    if self.priority_level  > 1:
      self.priority_level = self.priority_level - 1
      self.addAttribute("priority",str(self.priority_level))
    
  def lowerPriorityLevel(self):
    self.priority_level = self.priority_level + 1
    self.addAttribute("priority",str(self.priority_level))

  def getPriorityLevel(self):
    return self.priority_level
   
  def setPriorityLevel(self, level):
    self.priority_level = level 
    self.addAttribute("priority",str(self.priority_level))

  def addAttribute(self, name, value):
    if name == "priority":
      self.priority_level = int(value)
    self.attr_hash[name] = value

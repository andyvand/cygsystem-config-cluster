import string
import gettext
_ = gettext.gettext


MEMBER=_("Member")
JOINING=_("Joining")
Dead=_("Dead")
UNKNOWN=_("Unknown")


class NodeData:
  def __init__(self, votes, status, name):
    self.votes = votes
    self.name = name
    stat = status.strip()
    if stat == "M":
      self.status = MEMBER
    elif stat == "J":
      self.status = JOINING
    elif stat == "X":
      self.status = DEAD
    else: 
      self.status = UNKNOWN

  def getNodeProps(self):
    return (self.name, self.votes, self.status)

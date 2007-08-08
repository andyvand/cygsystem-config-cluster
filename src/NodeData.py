import string
import gettext
_ = gettext.gettext


MEMBER=_("Member")
NOT_MEMBER=_("Not a member")
DISALLOWED=_("Disallowed")
JOINING=_("Joining")
DEAD=_("Dead")
UNKNOWN=_("Unknown")
NOT_APPLICABLE=_("N/A")


class NodeData:
  def __init__(self, is_member, node_id, status, incarnation,jdate,jtime, name):
    self.is_member = is_member
    self.node_id = node_id
    self.incarnation = incarnation
    self.join_date = jdate
    self.join_time = jtime
    self.name = name
    stat = status.strip()
    if is_member == True:
      self.status = MEMBER
    else:
      if stat == "X":
        self.status = NOT_MEMBER
      elif stat == "d":
        self.status = DISALLOWED
      else: 
        self.status = status

  def getNodeProps(self):
    return (self.name, self.node_id, self.status)

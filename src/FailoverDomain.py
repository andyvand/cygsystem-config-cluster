import string
from TagObject import TagObject

TAG_NAME = "failoverdomain"
import gettext
_ = gettext.gettext

UNRESTRICTED=_("This is an unrestricted domain\n")
RESTRICTED=_("This domain is restricted to members\n")
UNORDERED=_("All members share equal priority\n")
ORDERED=_("Members are ordered by priority\n")
NUM_KIN=_("There are currently %d members")
NO_KIN=_("There are no current members")

class FailoverDomain(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getProperties(self):
    stringbuf = ""
    restricted_status = ""
    ordereded_status = ""
    string_restricted = ""
    string_ordered = ""
    string_num_kin = ""
    num_kin = 0

    try:
      restricted_status = self.getAttribute("restricted")
    except KeyError, k:
      restricted_status = None
    if restricted_status == None:
      string_restricted = UNRESTRICTED
    else:
      if restricted_status == "0":
        string_restricted = UNRESTRICTED
      else:
        string_restricted = RESTRICTED

    try:
      ordered_status = self.getAttribute("ordered")
    except KeyError, k:
      ordered_status = None
    if ordered_status == None:
      string_ordered = UNORDERED
    else:
      if ordered_status == "0":
        string_ordered = UNORDERED
      else:
        string_ordered = ORDERED


    num_kin = len(self.getChildren())
    if num_kin > 0:
      string_num_kin = NUM_KIN % num_kin
    else:
      string_num_kin = NO_KIN

    return string_restricted + "\n" + string_ordered + "\n" + string_num_kin + "\n"


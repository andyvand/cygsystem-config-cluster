import string
from TagObject import TagObject

TAG_NAME = "multicast"

import gettext
_ = gettext.gettext


class Multicast(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME 


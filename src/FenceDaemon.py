import string
from TagObject import TagObject

TAG_NAME = "fence_daemon"

import gettext
_ = gettext.gettext

class FenceDaemon(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME 


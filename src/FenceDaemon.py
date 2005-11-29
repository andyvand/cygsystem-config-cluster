import string
from TagObject import TagObject
from clui_constants import *

TAG_NAME = "fence_daemon"

import gettext
_ = gettext.gettext

class FenceDaemon(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME 
    self.addAttribute("post_join_delay",POST_JOIN_DEFAULT)
    self.addAttribute("post_fail_delay",POST_FAIL_DEFAULT)

  def getPostJoinDelay(self):
    val = self.getAttribute("post_join_delay")
    return val

  def getPostFailDelay(self):
    val = self.getAttribute("post_fail_delay")
    return val



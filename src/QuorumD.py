import string
from TagObject import TagObject

TAG_NAME = "quorumd"

class QuorumD(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

import string
from TagObject import TagObject
from BaseResource import BaseResource

import gettext
_ = gettext.gettext

TAG_NAME = "fs"
RESOURCE_TYPE = _("File System: ")

class Fs(BaseResource):
  def __init__(self):
    BaseResource.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.resource_type = RESOURCE_TYPE

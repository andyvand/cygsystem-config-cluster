import string
from TagObject import TagObject
from BaseResource import BaseResource

import gettext
_ = gettext.gettext

TAG_NAME = "netfs"
RESOURCE_TYPE = _("NFS Mount: ")

class Netfs(BaseResource):
  def __init__(self):
    BaseResource.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.resource_type = RESOURCE_TYPE

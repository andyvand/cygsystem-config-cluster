import string
from TagObject import TagObject
from BaseResource import BaseResource

import gettext
_ = gettext.gettext

RESOURCE_TYPE = _("NFS Export: ")
TAG_NAME = "nfsexport"

class NFSExport(BaseResource):
  def __init__(self):
    BaseResource.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.resource_type = RESOURCE_TYPE

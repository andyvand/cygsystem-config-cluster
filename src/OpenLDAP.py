import string
from TagObject import TagObject
from BaseResource import BaseResource

import gettext
_ = gettext.gettext

TAG_NAME = "openldap"
RESOURCE_TYPE = _("Open LDAP Server")

class OpenLDAP(BaseResource):
  def __init__(self):
    BaseResource.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.resource_type = RESOURCE_TYPE

# Copyright (C) 2006-2007 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from BaseResource import BaseResource
from gettext import gettext as _

TAG_NAME = 'SAPInstance'
RESOURCE_TYPE = _('SAP Instance')

class SAPInstance(BaseResource):
  def __init__(self):
    BaseResource.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.resource_type = RESOURCE_TYPE

  def getName(self):
    try:
      return self.attr_hash['InstanceName']
    except KeyError, e:
      return ''


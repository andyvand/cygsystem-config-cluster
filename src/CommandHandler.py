import os
import string
from gtk import TRUE, FALSE
from CommandError import CommandError
import rhpl.executil

import gettext
_ = gettext.gettext

class CommandHandler:

  def __init__(self):
    pass

  def isClusterMember(self):
    args = list()
    args.append("/sbin/magma_tool")
    args.append("quorum")
    cmdstr = ' '.join(args)
    try:
      out, err, res = rhpl.executil.execWithCaptureErrorStatus("/sbin/magma_tool",args)
    except RuntimeError, e:
      return FALSE

    if res != 0:
      return FALSE

    #look for 'Connect Failure' substring
    lines = out.splitlines()
    for line in lines:
      val = line.find("Connect Failure")
      if val != (-1):
        return FALSE

    return TRUE


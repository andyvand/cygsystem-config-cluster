import os
import string
from gtk import TRUE, FALSE
from CommandError import CommandError
from NodeData import NodeData
import rhpl.executil

import gettext
_ = gettext.gettext

PROPAGATE_ERROR=_("Propagation of configuration file version #%s failed with the following error:\n %s")

NODES_INFO_ERROR=_("A problem was encountered when atempting to get information about the nodes in the cluster. The following error message was received from the cman_tool: %s")

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

  def getClusterName(self):
    args = list()
    args.append("/sbin/cman_tool")
    args.append("status")
    cmdstr = ' '.join(args)
    try:
      out,err,res =  rhpl.executil.execWithCaptureErrorStatus("/sbin/cman_tool",args)
    except RuntimeError, e:
      return FALSE

    if res != 0:
      return FALSE

    #look for Cluster Name string
    lines = out.splitlines()
    for line in lines:
      val = line.find("Cluster name:")
      if val != (-1):  #Found it
        v = line.find(":")
        return line[(v+1):].strip()

    return ""

  def getNodeName(self):
    args = list()
    args.append("/sbin/cman_tool")
    args.append("status")
    cmdstr = ' '.join(args)
    try:
      out,err,res =  rhpl.executil.execWithCaptureErrorStatus("/sbin/cman_tool",args)
    except RuntimeError, e:
      return FALSE

    if res != 0:
      return FALSE

    #look for Node Name string
    lines = out.splitlines()
    for line in lines:
      val = line.find("Node name:")
      if val != (-1):  #Found it
        v = line.find(":")
        return line[(v+1):].strip()

    return ""

  def getClusterStatus(self):
    args = list()
    args.append("/sbin/cman_tool")
    args.append("status")
    cmdstr = ' '.join(args)
    try:
      out,err,res =  rhpl.executil.execWithCaptureErrorStatus("/sbin/cman_tool",args)
    except RuntimeError, e:
      return FALSE

    if res != 0:
      return FALSE

    #look for Node Name string
    lines = out.splitlines()
    for line in lines:
      val = line.find("Membership state:")
      if val != (-1):  #Found it
        v = line.find(":")
        return line[(v+1):].strip()

    return ""

  def isClusterQuorate(self):
    args = list()
    args.append("/sbin/magma_tool")
    args.append("quorum")
    cmdstr = ' '.join(args)
    try:
      out,err,res =  rhpl.executil.execWithCaptureErrorStatus("/sbin/magma_tool",args)
    except RuntimeError, e:
      return FALSE

    if res != 0:
      return FALSE

    #look for Quorate string
    lines = out.splitlines()
    for line in lines:
      val = line.find("Quorate")
      if val != (-1):  #Found it
        return TRUE

    return FALSE

  def getNodesInfo(self):
    dataobjs = list()
    args = list()
    args.append("/sbin/cman_tool")
    args.append("nodes")
    cmdstr = ' '.join(args)
    try:
      out,err,res =  rhpl.executil.execWithCaptureErrorStatus("/sbin/cman_tool",args)
    except RuntimeError, e:
      return FALSE

    if res != 0:
      raise CommandError("FATAL", NODES_INFO_ERROR % err)

    lines = out.splitlines()
    y = (-1)
    for line in lines:
      y = y + 1
      if y == 0:
        continue
      words = line.split()
      nd = NodeData(words[1],words[3],words[4])
      dataobjs.append(nd)

    return dataobjs

  def propagateConfig(self, version):
    args = list()
    args.append("/sbin/cman_tool")
    args.append("version")
    args.append("-r")
    args.append(version)
    cmdstr = ' '.join(args)
    try:
      out,err,res = rhpl.executil.execWithCaptureErrorStatus("/sbin/cman_tool",args)
    except RuntimeError, e:
      raise CommandError("FATAL",PROPAGATE_ERROR % (version, err))

    return res







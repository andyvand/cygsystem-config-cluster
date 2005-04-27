import os
import string
from gtk import TRUE, FALSE
from CommandError import CommandError
from NodeData import NodeData
from ServiceData import ServiceData
from clui_constants import *
import rhpl.executil

import gettext
_ = gettext.gettext

PATH_TO_RELAXNG_FILE = "./misc/cluster.ng"
ALT_PATH_TO_RELAXNG_FILE = "/usr/share/system-config-cluster/misc/cluster.ng"

PROPAGATE_ERROR=_("Propagation of configuration file version #%s failed with the following error:\n %s")

PROPAGATE_ERROR=_("Propagation of configuration file failed with the following error:\n %s")

NODES_INFO_ERROR=_("A problem was encountered when attempting to get information about the nodes in the cluster. The following error message was received from the cman_tool: %s")

MODE_OFFSET = 4

NAME_STR = "Name"

class CommandHandler:

  def __init__(self):
    path_exists = os.path.exists(PATH_TO_RELAXNG_FILE)
    if path_exists == TRUE:
      self.relaxng_file = PATH_TO_RELAXNG_FILE
    else:
      self.relaxng_file = ALT_PATH_TO_RELAXNG_FILE
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
      return ""

    if res != 0:
      return ""

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

  def getNodesInfo(self, locking_type ):
    dataobjs = list()
    if locking_type == DLM_TYPE:
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

    else:
      args = list()
      args.append("/sbin/gulm_tool")
      args.append("nodelist")
      args.append("localhost:core")
      cmdstr = ' '.join(args)
      try:
        out,err,res =  rhpl.executil.execWithCaptureErrorStatus("/sbin/gulm_tool",args)
      except RuntimeError, e:
        return FALSE

      if res != 0:
        raise CommandError("FATAL", NODES_INFO_ERROR % err)

      lines = out.splitlines()
      line_counter = (-1)
      for line in lines:
        line_counter = line_counter + 1
        dex = line.find(NAME_STR)
        if dex == (-1):
          continue
        #We now have a name line
        words = line.split() #second word is name...
        name = words[1]
        modeline = lines[line_counter + MODE_OFFSET] #The mode is 4 lines down..
        mwords = modeline.split()
        mode = mwords[2]
        nd = NodeData(None,mode,name)
        dataobjs.append(nd)

      return dataobjs

  def getServicesInfo(self):
    dataobjs = list()
    args = list()
    args.append("/sbin/clustat")
    args.append("-x")
    cmdstr = ' '.join(args)
    try:
      out,err,res =  rhpl.executil.execWithCaptureErrorStatus("/sbin/clustat",args)
    except RuntimeError, e:
      return dataobjs  #empty list with no services

    if res != 0:
      raise CommandError("FATAL", NODES_INFO_ERROR % err)

    servicelist = list()
    lines = out.splitlines()
   
    y = 0 
    found_groups_tag = FALSE
    #First, run through lines and look for "<groups>" tag
    for line in lines:
      if line.find("<groups>") != (-1):
        found_groups_tag = TRUE
        break
      y = y + 1

    if found_groups_tag == FALSE:
      return dataobjs  #no services visible


    #y now holds index into line list for <groups> tag
    #We need to add one more to y before beginning to start with serices
    y = y + 1

    while lines[y].find("</groups>") == (-1):
      servicelist.append(lines[y])
      y = y + 1

    #servicelist now holds all services

    for service in servicelist:
      words = service.split()

      namestr = words[1]
      start = namestr.find("\"")
      end = namestr.rfind("\"")
      name = namestr[start+1:end]
      
      statestr = words[3]
      start = statestr.find("\"")
      end = statestr.rfind("\"")
      state = statestr[start+1:end]
      
      ownstr = words[4]
      start = ownstr.find("\"")
      end = ownstr.rfind("\"")
      owner = ownstr[start+1:end]
      
      lownstr = words[5]
      start = lownstr.find("\"")
      end = lownstr.rfind("\"")
      lastowner = lownstr[start+1:end]
      
      resstr = words[6]
      start = resstr.find("\"")
      end = resstr.rfind("\"")
      restarts = resstr[start+1:end]
      
      dataobjs.append(ServiceData(name,state,owner,lastowner,restarts))

    return dataobjs

  def propagateConfig(self, file):
    args = list()
    args.append("/sbin/ccs_tool")
    args.append("update")
    args.append(file)
    cmdstr = ' '.join(args)
    try:
      out,err,res = rhpl.executil.execWithCaptureErrorStatus("/sbin/ccs_tool",args)
    except RuntimeError, e:
      raise CommandError("FATAL",PROPAGATE_ERROR % (err))

    return res


  def propagateCmanConfig(self, version):
    args = list()
    args.append("/sbin/cman_tool")
    args.append("version")
    args.append("-r")
    args.append(version)
    cmdstr = ' '.join(args)
    try:
      out,err,res = rhpl.executil.execWithCaptureErrorStatus("/sbin/cman_tool",args)
    except RuntimeError, e:
      raise CommandError("FATAL",PROPAGATE_ERROR2 % (version, err))

    return res


  def check_xml(self, file):
    err = ""
    args = list()
    args.append("/usr/bin/xmllint")
    args.append("--relaxng")
    args.append(self.relaxng_file)
    args.append(file)
    try:
      out,err,res = rhpl.executil.execWithCaptureErrorStatus("/usr/bin/xmllint",args)
    except RuntimeError, e:
      raise CommandError("FATAL", str(e))

    if res != 0:
      raise CommandError("FATAL", err)


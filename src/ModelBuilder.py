#!/usr/bin/python2.3

#import xml.dom.minidom
from xml.dom import minidom, Node
import string
import os
### gettext ("_") must come before gtk ###
import gettext
from TagObject import TagObject
from Cluster import Cluster
from ClusterNode import ClusterNode
from ClusterNodes import ClusterNodes
from Fence import Fence
from FenceDevice import FenceDevice
from FenceDevices import FenceDevices
from Method import Method
from Device import Device
from Cman import Cman
from Gulm import Gulm
from Lockserver import Lockserver
from Ip import Ip
from Script import Script
from NFSClient import NFSClient
from NFSExport import NFSExport
from Fs import Fs
from Samba import Samba
from Multicast import Multicast
from FenceDaemon import FenceDaemon
from Netfs import Netfs
from Clusterfs import Clusterfs
from Resources import Resources
from Service import Service
from QuorumD import QuorumD
from Heuristic import Heuristic
from Vm import Vm
from RefObject import RefObject
from FailoverDomain import FailoverDomain
from FailoverDomains import FailoverDomains
from FailoverDomainNode import FailoverDomainNode
from Rm import Rm
from CommandHandler import CommandHandler
from CommandError import CommandError
from clui_constants import *
import MessageLibrary

TAGNAMES={ 'cluster':Cluster,
           'clusternodes':ClusterNodes,
           'clusternode':ClusterNode,
           'fence':Fence,
           'fencedevice':FenceDevice,
           'fencedevices':FenceDevices,
           'method':Method,
           'cman':Cman,
           'gulm':Gulm,
           'lockserver':Lockserver,
           'rm':Rm,
           'service':Service,
           'resources':Resources,
           'failoverdomain':FailoverDomain,
           'failoverdomains':FailoverDomains,
           'failoverdomainnode':FailoverDomainNode,
           'ip':Ip,
           'fs':Fs,
           'smb':Samba,
           'fence_daemon':FenceDaemon,
           'multicast':Multicast,
           'clusterfs':Clusterfs,
           'netfs':Netfs,
           'quorumd':QuorumD,
           'heuristic':Heuristic,
           'vm':Vm,
           'script':Script,
           'nfsexport':NFSExport, 
           'nfsclient':NFSClient,
           'device':Device }


###---Don't translate strings below---
CLUSTER_PTR_STR="cluster"
CLUSTERNODES_PTR_STR="clusternodes"
FAILDOMS_PTR_STR="failoverdomains"
FENCEDEVICES_PTR_STR="fencedevices"
RESOURCEMANAGER_PTR_STR="rm"
RESOURCES_PTR_STR="resources"
FENCEDAEMON_PTR_STR="fence_daemon"
SERVICE="service"
GULM_TAG_STR="gulm"
MCAST_STR="multicast"
CMAN_PTR_STR="cman"
QUORUMD_PTR_STR="quorumd"
VM="vm"
###-----------------------------------


INVALID_GULM_COUNT=_("GULM locking mechanism may consist of 1, 3, 4 or 5 locking servers. You have configured %d. Fix the error and try saving again.")


class ModelBuilder:
  def __init__(self, lock_type, filename=None, mcast_addr=None,new_clu_name=None,new_quorumdisk=None):

    if os.path.exists("/etc/cluster/") == False:
      try:
        os.makedirs("/etc/cluster")
      except OSError, e:
        pass

    self.filename = filename
    self.lock_type = DLM_TYPE
    self.mcast_address = mcast_addr
    self.cluster_ptr = None
    self.GULM_ptr = None
    self.CMAN_ptr = None
    self.clusternodes_ptr = None
    self.failoverdomains_ptr = None
    self.fencedevices_ptr = None
    self.resourcemanager_ptr = None
    self.resources_ptr = None
    self.fence_daemon_ptr = None
    self.quorumd_ptr = new_quorumdisk
    self.unusual_items = list()
    self.command_handler = CommandHandler()
    self.isModified = False
    if mcast_addr == None:
      self.usesMulticast = False
    else:
      self.usesMulticast = True

    if filename == None:
      if lock_type == DLM_TYPE:
        self.lock_type = DLM_TYPE
        self.object_tree = self.buildDLMModelTemplate(new_clu_name,new_quorumdisk)
      else:
        self.lock_type = GULM_TYPE
        self.object_tree = self.buildGULMModelTemplate(new_clu_name)
    else:
      try:
        self.parent = minidom.parse(self.filename)
      except IOError, e:
        pass

      self.object_tree = self.buildModel(None)
      self.check_empty_ptrs()
      self.check_fence_daemon()
      self.resolve_fence_instance_types()
      self.purgePCDuplicates()
      self.resolve_references()
      self.check_for_multicast()
      self.check_for_nodeids()


  def buildModel(self, parent_node, parent_object=None):

    if parent_node == None:
      parent_node = self.parent

    new_object = None
    if parent_node.nodeType == Node.DOCUMENT_NODE:
      parent_node = parent_node.firstChild

    if parent_node.nodeType == Node.ELEMENT_NODE:
      #Create proper type
      try:
        new_object = apply(TAGNAMES[parent_node.nodeName])
        attrs = parent_node.attributes
        for attrName in attrs.keys():
          attrNode = attrs.get(attrName)
          attrValue = attrNode.nodeValue
          new_object.addAttribute(attrName,attrValue)
      except KeyError, k: ##This allows for custom tags
        new_object = TagObject(parent_node.nodeName)
        attrs = parent_node.attributes
        for attrName in attrs.keys():
          attrNode = attrs.get(attrName)
          attrValue = attrNode.nodeValue
          new_object.addAttribute(attrName, attrValue)
        self.unusual_items.append((parent_object, new_object))
        for item in parent_node.childNodes:
          result_object = self.buildModel(item, new_object)
          if result_object != None:
            new_object.addChild(result_object)
        return None
          
      ######End of unusual item exception

      if parent_node.nodeName == CLUSTER_PTR_STR:
        self.cluster_ptr = new_object
      if parent_node.nodeName == CLUSTERNODES_PTR_STR:
        self.clusternodes_ptr = new_object
      elif parent_node.nodeName == FENCEDEVICES_PTR_STR:
        self.fencedevices_ptr = new_object
      elif parent_node.nodeName == FAILDOMS_PTR_STR:
        self.failoverdomains_ptr = new_object
      elif parent_node.nodeName == RESOURCEMANAGER_PTR_STR:
        self.resourcemanager_ptr = new_object
      elif parent_node.nodeName == QUORUMD_PTR_STR:
        self.quorumd_ptr = new_object
      elif parent_node.nodeName == RESOURCES_PTR_STR:
        self.resources_ptr = new_object
      elif parent_node.nodeName == FENCEDAEMON_PTR_STR:
        self.fence_daemon_ptr = new_object
      elif parent_node.nodeName == GULM_TAG_STR:
        self.GULM_ptr = new_object
        self.lock_type = GULM_TYPE
      elif parent_node.nodeName == CMAN_PTR_STR:
        self.CMAN_ptr = new_object
      elif parent_node.nodeName == MCAST_STR:
        self.usesMulticast = True

    else:
      return None


    for item in parent_node.childNodes:
      result_object = self.buildModel(item,new_object)
      if result_object != None:
        new_object.addChild(result_object)

    return (new_object)

  def buildDLMModelTemplate(self, new_clu_name, new_qd):
    obj_tree = Cluster()
    self.cluster_ptr = obj_tree
    if new_clu_name == None:
      new_clu_name = "new_cluster"
    else:
      new_clu_name = new_clu_name.strip()

    if new_qd != None:
      obj_tree.addChild(new_qd)

    obj_tree.addAttribute("name",new_clu_name)
    obj_tree.addAttribute("config_version","1")
    fdp = FenceDaemon()
    obj_tree.addChild(fdp)
    self.fence_daemon_ptr = fdp
    cns = ClusterNodes()
    obj_tree.addChild(cns)
    self.clusternodes_ptr = cns

    cman = Cman()
    self.CMAN_ptr = cman
    obj_tree.addChild(cman)

    if self.usesMulticast == True:
      mcast = Multicast()
      mcast.addAttribute("addr",self.mcast_address)
      cman.addChild(mcast)

    fds = FenceDevices()
    obj_tree.addChild(fds)
    self.fencedevices_ptr = fds

    rm = Rm()
    obj_tree.addChild(rm)
    self.resourcemanager_ptr = rm

    fdoms = FailoverDomains()
    self.failoverdomains_ptr = fdoms
    rm.addChild(fdoms)

    rcs = Resources()
    rm.addChild(rcs)
    self.resources_ptr = rcs

    self.isModified = False

    return obj_tree
    
  def buildGULMModelTemplate(self, new_clu_name):
    obj_tree = Cluster()
    self.cluster_ptr = obj_tree

    if new_clu_name == None:
      new_clu_name = "new_cluster"
    else:
      new_clu_name = new_clu_name.strip()

    obj_tree.addAttribute("name",new_clu_name)
    obj_tree.addAttribute("config_version","1")
    fdp = FenceDaemon()
    obj_tree.addChild(fdp)
    self.fence_daemon_ptr = fdp
    cns = ClusterNodes()
    obj_tree.addChild(cns)
    self.clusternodes_ptr = cns

    gulm = Gulm()
    self.GULM_ptr = gulm
    obj_tree.addChild(gulm)

    fds = FenceDevices()
    obj_tree.addChild(fds)
    self.fencedevices_ptr = fds

    rm = Rm()
    obj_tree.addChild(rm)
    self.resourcemanager_ptr = rm

    fdoms = FailoverDomains()
    self.failoverdomains_ptr = fdoms
    rm.addChild(fdoms)

    rcs = Resources()
    rm.addChild(rcs)
    self.resources_ptr = rcs

    self.isModified = False

    return obj_tree
    

  ##Because fence devices are declared in a separate XML section
  ##in conf file, agent types for fence instances must be done in
  ##a separate pass, after the DOM is completely built. This method
  ##sets the agent type for each fence instance.
  def resolve_fence_instance_types(self):
    fds = self.getFenceDevices()
    agent_hash = {}
    for fd in fds:
      agent = fd.getAttribute("agent")
      if agent != None:
        agent_hash[fd.getName()] = agent

    nodes = self.getNodes()
    for node in nodes:
      levels = node.getFenceLevels()
      for level in levels:
        children = level.getChildren()
        for child in children:
          child.setAgentType(agent_hash[child.getName()])

  ##This method builds RefObject containers for appropriate
  ##entities after the object tree is built. 
  def resolve_references(self):
    reset_list_sentinel = True
    while(reset_list_sentinel == True):
      reset_list_sentinel = False
      resource_children = self.resourcemanager_ptr.getChildren()
      for r_child in resource_children:
        if r_child.getTagName() == SERVICE:
         reset_list_sentinel = self.find_references(r_child)
         if reset_list_sentinel == True:
           break
                                                                                
  def find_references(self, entity, parent=None):
    result = False
    if (entity.getAttribute("ref") != None) and (entity.isRefObject() == False):
      result = self.transform_reference(entity, parent)
      return result
                                                                                
    children = entity.getChildren()
    if len(children) > 0:
      for child in children:
        result = self.find_references(child, entity)
        if result == True:
          return result
                                                                                
    return result
                                                                                
  def transform_reference(self, entity, parent):
    result = False
    #This entity has a "ref" attr...need to walk through resources list
    #and look for a match
    recs = self.resources_ptr.getChildren()
    for rec in recs:
      if rec.getTagName() == entity.getTagName():
        if entity.getTagName() == "ip":
          if entity.getAttribute("ref") == rec.getAttribute("address"):
            rf = RefObject(rec)
            kids = entity.getChildren()
            for kid in kids:
              rf.addChild(kid)
            result = True
            break
        else:
          if entity.getAttribute("ref") == rec.getName():
            rf = RefObject(rec)
            kids = entity.getChildren()
            for kid in kids:
              rf.addChild(kid)
            result = True
            break
                                                                                
    if result == False:
      return result
                                                                                
    if parent == None:  #Must be a service
      self.resourcemanager_ptr.addChild(rf)
      self.resourcemanager_ptr.removeChild(entity)
      return True
    else:
      parent.addChild(rf)
      parent.removeChild(entity)
      return True

  def testexportModel(self, *args):
    self.exportModel("/tmp/cluster.conf")

  def exportModel(self, filename=None):
    if self.perform_final_check() == False: # failed
      return False
    
    #check for dual power fences
    self.dual_power_fence_check()

    self.restore_unusual_items()

    try:
      if filename == None:
        filename = self.filename
      
      if filename == CLUSTER_CONF_PATH:
        if os.access(CLUSTER_CONF_DIR_PATH, os.F_OK) == 0:
          message = _("Directory %s does not exist. Should it be created?") % CLUSTER_CONF_DIR_PATH
          if MessageLibrary.infoMessage(message) == MessageLibrary.gtk.RESPONSE_YES:
            os.mkdir(CLUSTER_CONF_DIR_PATH)
          else:
            return False
        self.backup_configfile()
      
      fd = open(filename, "w+")
      
      doc = minidom.Document()
      self.object_tree.generateXML(doc)
      #print doc.toprettyxml()
      fd.write(doc.toprettyxml())
      self.filename = filename

      self.isModified = False
      #try:
      #  self.parent = minidom.parse(self.filename)
      #except IOError, e:
      #  print "Terrible error at exportModel in ModelBuilder"
      #  pass
      self.parent = doc

      self.object_tree = self.buildModel(None)
      self.check_empty_ptrs()
      self.check_fence_daemon()
      self.resolve_fence_instance_types()
      self.purgePCDuplicates()
      self.resolve_references()
      self.check_for_multicast()

    finally:
      pass
      #dual_power_fence_check() adds extra
      #fence instance entries for dual power controllers
      #These must be removed from the tree before the UI
      #can be used
      #self.purgePCDuplicates()

    return True

  ##This method attempts to restore custom tag objects
  def restore_unusual_items(self):
    for item in self.unusual_items:
      duplicate = False
      kids = item[0].getChildren()
      for kid in kids:
        if kid == item[1]:
          duplicate = True
          break
      if duplicate == True:
        continue
      else:
        item[0].addChild(item[1])
          
    
  
  def has_filepath(self):
    if self.filename == None:
      return False
    else:
      return True

  def getFilepath(self):
    return self.filename

  def isClusterMember(self):
    return self.command_handler.isClusterMember()
    
  def getNodes(self):
    #Find the clusternodes obj and return get_children 
    return self.clusternodes_ptr.getChildren()

  def addNode(self, clusternode):
    self.clusternodes_ptr.addChild(clusternode)
    if self.usesMulticast == True:
      mcast = Multicast()
      mcast.addAttribute("addr",self.mcast_address)
      mcast.addAttribute("interface","eth0")  #eth0 is the default
      clusternode.addChild(mcast)
    self.isModified = True

  def deleteNode(self, clusternode):
    #1) delete node
    #2) delete failoverdomainnodes with same name
    #3) delete lockserver nodes if GULM

    name = clusternode.getName()

    self.clusternodes_ptr.removeChild(clusternode)

    found_one = True

    while found_one == True:
      found_one = False
      fdoms = self.getFailoverDomains()
      for fdom in fdoms:
        children = fdom.getChildren()
        for child in children:
          if child.getName() == name:
            fdom.removeChild(child)
            found_one = True
            break

      lock_type = self.getLockType()
      if lock_type == GULM_TYPE:
        if self.isNodeLockserver(clusternode.getName()) == True:
          self.removeLockserver(clusternode)

    self.isModified = True

  def retrieveVMsByName(self, name):
    vms = self.getVMs()
    for v in vms:
      if v.getName() == name:
        return v
                                                                                
    raise GeneralError('FATAL',"Couldn't find vm name %s in current node list" % name)

  def getFenceDevices(self):
    if self.fencedevices_ptr == None:
      return list()
    else:
      return self.fencedevices_ptr.getChildren()

  def getFenceDevicePtr(self):
    return self.fencedevices_ptr

  def getFailoverDomains(self):
    if self.failoverdomains_ptr == None:
      return list()
    else:
      return self.failoverdomains_ptr.getChildren()
        
  def getFailoverDomainPtr(self):
    return self.failoverdomains_ptr

  def isMulticast(self):
    return self.usesMulticast

  def check_for_multicast(self):
    if self.usesMulticast == True:
      #set mcast address
      children = self.CMAN_ptr.getChildren()
      for child in children:
        if child.getTagName() == MCAST_STR:
          addr = child.getAttribute("addr")
          if addr != None:
            self.mcast_address = addr
            return
          else:  #What a mess! a multicast tag, but no addr attribute
            self.mcast_address = ""
            return

  def getMcastAddr(self):
    return self.mcast_address

  def check_for_nodeids(self):
    nodes = self.getNodes()
    for node in nodes:
      if node.getAttribute('nodeid') == None:
        new_id = self.getUniqueNodeID()
        node.addAttribute('nodeid',new_id)

  def getUniqueNodeID(self):
    nodes = self.getNodes()
    total_nodes = len(nodes)
    dex_list = list()
    for nd_idx in range (1, (total_nodes + 3)):
      dex_list.append(str(nd_idx))

    for dex in dex_list:
      found = False
      for node in nodes:
        ndid = node.getAttribute('nodeid')
        if ndid != None:
          if ndid == dex:
            found = True
            break
        else:
          continue

      if found == True:
        continue
      else:
        return dex

  def check_empty_ptrs(self):
    if self.resourcemanager_ptr == None:
      rm = Rm()
      self.cluster_ptr.addChild(rm)
      self.resourcemanager_ptr = rm

    if self.failoverdomains_ptr == None:
      fdoms = FailoverDomains()
      self.resourcemanager_ptr.addChild(fdoms)
      self.failoverdomains_ptr = fdoms

    if self.fencedevices_ptr == None:
      fds = FenceDevices()
      self.cluster_ptr.addChild(fds)
      self.fencedevices_ptr = fds
        
    if self.resources_ptr == None:
      rcs = Resources()
      self.resourcemanager_ptr.addChild(rcs)
      self.resources_ptr = rcs
        
    if self.fence_daemon_ptr == None:
      fdp = FenceDaemon()
      self.cluster_ptr.addChild(fdp)
      self.fence_daemon_ptr = fdp
        
  def getServices(self):
    rg_list = list()
    if self.resourcemanager_ptr != None:
      kids = self.resourcemanager_ptr.getChildren()
      for kid in kids:
        if kid.getTagName() == SERVICE:
          rg_list.append(kid)

    return rg_list

  def getVMs(self):
    rg_list = list()
    if self.resourcemanager_ptr != None:
      kids = self.resourcemanager_ptr.getChildren()
      for kid in kids:
        if kid.getTagName() == VM:
          rg_list.append(kid)
                                                                                
    return rg_list
        
  def getResources(self):
    if self.resources_ptr != None:
      return self.resources_ptr.getChildren()
    else:
      return list()

  def getResourcesPtr(self):
    return self.resources_ptr
  
  def getResourceManagerPtr(self):
    return self.resourcemanager_ptr
      
  def getClusterNodesPtr(self):
    return self.clusternodes_ptr
        
  def getClusterPtr(self):
    return self.cluster_ptr

  def getGULMPtr(self):
    return self.GULM_ptr

  def getLockServer(self, name):
    children = self.GULM_ptr.getChildren()
    for child in children:
      if child.getName() == name:
        return child

    return None

  def createObjectFromTagname(self,tagname):
    newobj = apply(TAGNAMES[tagname])
    return newobj

  def getLockType(self):
    return self.lock_type

  def isNodeLockserver(self,name):
    gptr = self.getGULMPtr()
    if gptr == None:  #Obviously not GULM
      return False
    children = gptr.getChildren()
    for child in children:
      if child.getName() == name:
        return True

    return False

  def removeLockserver(self, clusternode):
    gptr = self.getGULMPtr()
    if gptr == None:  #Obviously not GULM
      return
    children = gptr.getChildren()
    for child in children:
      if child.getName() == clusternode.getName():
        gptr.removeChild(child)
        break  #Only one will be found

    self.isModified = True

  def switch_lockservers(self):
    #first get what type of locking is currently in place
    if self.lock_type == DLM_TYPE:
      #remove <cman>
      self.cluster_ptr.removeChild(self.CMAN_ptr)
      self.CMAN_ptr = None

      #add gulm tag
      gulm = Gulm()
      self.GULM_ptr = gulm
      self.cluster_ptr.addChild(gulm)

      #check for multicast
      #if multicast, remove <multicast> from each node
      #remove votes attr from each node
      nodes = self.getNodes()
      for node in nodes:
        if self.usesMulticast == True:
          mnode = node.getMulticastNode()
          if mnode != None:
            node.removeChild(mnode)
        node.removeAttribute(VOTES_ATTR)

      self.usesMulticast = False
      self.mcast_address = None

      #reset self.lock_type
      self.lock_type = GULM_TYPE

      #make the first node a lockserver
      nodes = self.getNodes()
      for node in nodes:
        ls = Lockserver()
        ls.addAttribute(NAME_ATTR, node.getName())
        self.GULM_ptr.addChild(ls)
        break
 

      #set modified
      self.isModified = True

    else:
      #remove <gulm> tag
      children = self.cluster_ptr.getChildren()
      for child in children:
        if child.getTagName() == "gulm":
          self.cluster_ptr.removeChild(child)
          break

      #set gulm pointer to None
      self.GULM_ptr = None

      #add <cman> tag
      cman = Cman()
      self.CMAN_ptr = cman
      self.cluster_ptr.addChild(cman)

      #reset self.lock_type
      self.lock_type = DLM_TYPE

      #give each node a vote of 1
      nds = self.getNodes()
      for nd in nds:
        nd.addAttribute(VOTES_ATTR, ONE_VOTE)

      #set modified
      self.isModified = True

  def swap_multicast_state(self, address=None):
    if self.usesMulticast == True:
      #First, eliminate <multicast> tag
      if self.CMAN_ptr != None:
        children = self.CMAN_ptr.getChildren()
        if len(children) > 0:
          for child in children:
            if child.getTagName() == MCAST_STR:
              self.CMAN_ptr.removeChild(child)
              break
      found_one = True
      while found_one == True:
        found_one = False
        nodes = self.clusternodes_ptr.getChildren()
        for node in nodes:
          node_children = node.getChildren()
          for node_child in node_children:
            if node_child.getTagName() == MCAST_STR:
              node.removeChild(node_child)
              found_one = True
              break
          if found_one == True:
            break

      self.usesMulticast = False 
      self.mcast_address = None
      self.isModified = True
          

    else:
      if self.CMAN_ptr != None:
        mcast = Multicast()
        mcast.addAttribute("addr",address)
        self.CMAN_ptr.addChild(mcast)

      has_one = False
      nodes = self.getNodes()
      for node in nodes:
        has_one = False
        node_children = node.getChildren()
        for node_child in node_children:
          if node_child.getTagName() == MCAST_STR:
            has_one = True
            break;
        if has_one == False:
          mcast = Multicast()
          mcast.addAttribute("addr",address)
          mcast.addAttribute("interface","eth0")
          node.addChild(mcast)

      self.mcast_address = address
      self.usesMulticast = True
      self.isModified = True
        
    

  def check_fence_daemon(self):
    if self.fence_daemon_ptr == None:
      self.fence_daemon_ptr = FenceDaemon()
      self.cluster_ptr.addChild(self.fence_daemon_ptr)

  def getFenceDaemonPtr(self):
    return self.fence_daemon_ptr

  def isFileModified(self):
    return self.isModified

  def setModified(self, modified=None):
    if modified == None:
      self.isModified = True
    else:
      self.isModified = modified

  def rectifyNewNodenameWithFaildoms(self, oldname, newname):
    fdoms = self.getFailoverDomains()
    for fdom in fdoms:
      children = fdom.getChildren() #These are failoverdomainnodes...
      for child in children:
        if child.getName().strip() == oldname:
          child.addAttribute("name",newname)

  ###This method runs through ALL fences (Device objs) and changes name attr
  ###to new name
  def rectifyNewFencedevicenameWithFences(self, oldname, newname):
    nodes = self.getNodes()
    for node in nodes:
      levels = node.getFenceLevels()
      for level in levels:
        fences = level.getChildren()
        for fence in fences:
          if fence.getName() == oldname:
            fence.addAttribute("name",newname)

  def removeReferences(self, tagobj):
    self.__removeReferences(tagobj, self.cluster_ptr)
  def __removeReferences(self, tagobj, level):
    for t in level.getChildren()[:]:
      if t.isRefObject():
        if t.getObj() == tagobj:
          level.removeChild(t)
          continue
      self.__removeReferences(tagobj, t)
  
  def updateReferences(self):
    self.__updateReferences(self.cluster_ptr)
  def __updateReferences(self, level):
    for t in level.getChildren():
      if t.isRefObject():
        t.setRef(t.getObj().getName())
      self.__updateReferences(t)
  
  def backup_configfile(self, depth = 3):
    if depth == 0:
      return
    dir = os.listdir(CLUSTER_CONF_DIR_PATH)
    if CLUSTER_CONF_FILE in dir:
      basename = CLUSTER_CONF_FILE + ROTATE_BACKUP_EXT
      basepath = CLUSTER_CONF_DIR_PATH + basename
      for ext in range(depth - 1, 0, -1):
        if (basename + str(ext)) in dir:
          os.rename(basepath + str(ext), basepath + str(ext+1))
      os.rename(CLUSTER_CONF_PATH, basepath + '1')
      
  def perform_final_check(self):
    if self.check_gulm_count() == False:
      return False
    self.check_two_node()
    self.check_fi_nodenames()
    
    #add more checks
    
    return True
  
  def check_fi_nodenames(self):
    for node in self.clusternodes_ptr.getChildren():
      for fence_level in node.getFenceLevels():
        for fence in fence_level.getChildren():
          if fence.getAttribute("nodename") != None:
            fence.addAttribute("nodename", node.getName())
  
  def check_gulm_count(self):
    if self.getLockType() == GULM_TYPE:
      gulm_count = len(self.getGULMPtr().getChildren())
      if not (gulm_count in (1, 3, 4, 5)):
        MessageLibrary.errorMessage(INVALID_GULM_COUNT % gulm_count)
        return False
    return True

  def check_two_node(self):
    if self.getLockType() == DLM_TYPE and self.quorumd_ptr == None:
      clusternodes_count = len(self.clusternodes_ptr.getChildren())
      #Make certain that there is a cman tag in the file
      #If missing, it will not hurt to add it here
      if self.CMAN_ptr == None:
        cman = Cman()
        self.cluster_ptr.addChild(cman)
        self.CMAN_ptr = cman 
      if clusternodes_count == 2:
        self.CMAN_ptr.addAttribute('two_node', '1')
        self.CMAN_ptr.addAttribute('expected_votes', '1')
      else:
        if self.CMAN_ptr.getAttribute('expected_votes') in ('0', '1'):
          self.CMAN_ptr.removeAttribute('expected_votes')
        self.CMAN_ptr.removeAttribute('two_node')          

  def dual_power_fence_check(self):
    #if 2 or more power controllers reside in the same fence level,
    #duplicate entries must be made for every controller with an
    #attribute for option set first for off, then for on.

    #for every node:
      #for every fence level:
        #examine every fence
        #If fence is of power type, add to 'found' list for that level
        #If 'found' list is longer than 1, write out extra objs
    nodes = self.getNodes()
    for node in nodes:
      levels = node.getFenceLevels()
      for level in levels:
        kids = level.getChildren()
        l = list()
        for kid in kids:
          if kid.isPowerController() == True:
            l.append(kid)
        if len(l) > 1:  #Means we found multiple PCs in the same level
          for fence in l:
            fence.addAttribute("option","off")
          for fence in l:
            if fence.getAttribute("option") == "off":
              d = Device()
              d.setAgentType(fence.getAgentType())
              attrs = fence.getAttributes()
              kees = attrs.keys()
              for k in kees:
                d.addAttribute(k,attrs[k])
              d.addAttribute("option","on")
              level.addChild(d)
          
  def purgePCDuplicates(self):
    found_one = True
    while found_one == True:
      found_one = False
      nodes = self.getNodes()
      for node in nodes:
        levels = node.getFenceLevels()
        for level in levels:
          kids = level.getChildren()
          for kid in kids: #kids are actual fence instance objects
            res = kid.getAttribute("option")
            if res != None:
              if res == "off":
                kid.removeAttribute("option")
              else:
                level.removeChild(kid)
                found_one = True
                break
        if found_one == True:
          break
          
    
  def searchObjectTree(self, tagtype):
    objlist = list()
    self.object_tree.searchTree(objlist, tagtype)

    return objlist 
   
if __name__ == "__main__":
  print "Starting main program"
  mdl = ModelBuilder()
  objs = mdl.buildModel(None)

  mdl.exportModel("/tmp/tags.xml",objs)
 

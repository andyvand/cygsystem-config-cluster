#!/usr/bin/python2.3

#import xml.dom.minidom
from xml.dom import minidom, Node
import string
import os
from gtk import TRUE, FALSE
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
from Resources import Resources
from ResourceGroup import ResourceGroup
from Group import Group
from FailoverDomain import FailoverDomain
from FailoverDomains import FailoverDomains
from FailoverDomainNode import FailoverDomainNode
from Rm import Rm
from CommandHandler import CommandHandler
from CommandError import CommandError
from clui_constants import *

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
           'group':Group,
           'resourcegroup':ResourceGroup,
           'resources':Resources,
           'failoverdomain':FailoverDomain,
           'failoverdomains':FailoverDomains,
           'failoverdomainnode':FailoverDomainNode,
           'ip':Ip,
           'fs':Fs,
           'script':Script,
           'nfsexport':NFSExport, 
           'nfsclient':NFSClient,
           'device':Device }

#CLUSTER_CONF="../cluster.conf"
CLUSTER_CONF="/etc/cluster/cluster.conf"

###---Don't translate strings below---
CLUSTER_PTR_STR="cluster"
CLUSTERNODES_PTR_STR="clusternodes"
FAILDOMS_PTR_STR="failoverdomains"
FENCEDEVICES_PTR_STR="fencedevices"
RESOURCEMANAGER_PTR_STR="rm"
RESOURCES_PTR_STR="resources"
RESOURCEGROUP="resourcegroup"
GULM_TAG_STR="gulm"
###-----------------------------------

class ModelBuilder:
  def __init__(self, lock_type, filename=None):
    self.filename = filename
    self.lock_type = DLM_TYPE
    self.cluster_ptr = None
    self.GULM_ptr = None
    self.clusternodes_ptr = None
    self.failoverdomains_ptr = None
    self.fencedevices_ptr = None
    self.resourcemanager_ptr = None
    self.resources_ptr = None
    self.command_handler = CommandHandler()

    if filename == None:
      if lock_type == DLM_TYPE:
        self.lock_type = DLM_TYPE
        self.object_tree = self.buildDLMModelTemplate()
      else:
        self.lock_type = GULM_TYPE
        self.object_tree = self.buildGULMModelTemplate()
    else:
      try:
        self.parent = minidom.parse(self.filename)
      except IOError, e:
        pass

      self.object_tree = self.buildModel(None)
      self.resolve_fence_instance_types()


  def buildModel(self, parent_node):

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
      except KeyError, k:
        print "Can't locate %s in tag names dict" % parent_node.nodeName
        return None
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
      elif parent_node.nodeName == RESOURCES_PTR_STR:
        self.resources_ptr = new_object
      elif parent_node.nodeName == GULM_TAG_STR:
        self.GULM_ptr = new_object
        self.lock_type = GULM_TYPE

    else:
      return None


    for item in parent_node.childNodes:
      result_object = self.buildModel(item)
      if result_object != None:
        new_object.addChild(result_object)

    return (new_object)

  def buildDLMModelTemplate(self):
    obj_tree = Cluster()
    self.cluster_ptr = obj_tree

    obj_tree.addAttribute("name","alpha_cluster")
    obj_tree.addAttribute("config_version","1")
    cns = ClusterNodes()
    obj_tree.addChild(cns)
    self.clusternodes_ptr = cns

    obj_tree.addChild(Cman())

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

    return obj_tree
    
  def buildGULMModelTemplate(self):
    obj_tree = Cluster()
    self.cluster_ptr = obj_tree

    obj_tree.addAttribute("name","alpha_cluster")
    obj_tree.addAttribute("config_version","1")
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


  def testexportModel(self, *args):
    self.exportModel("/tmp/cluster.conf")

  def exportModel(self, filename=None):
    if filename == None:
      filename = self.filename

    fd = open(filename, "w+")

    doc = minidom.Document()
    self.object_tree.generateXML(doc)
    #print doc.toprettyxml()
    fd.write(doc.toprettyxml())
    self.filename = filename
     
  def has_filepath(self):
    if self.filename == None:
      return FALSE
    else:
      return TRUE

  def getFilepath(self):
    return self.filename

  def isClusterMember(self):
    return self.command_handler.isClusterMember()
    
  def getNodes(self):
    #Find the clusternodes obj and return get_children 
    return self.clusternodes_ptr.getChildren()

  def addNode(self, clusternode):
    self.clusternodes_ptr.addChild(clusternode)

  def deleteNode(self, clusternode):
    self.clusternodes_ptr.removeChild(clusternode)

  def getFenceDevices(self):
    return self.fencedevices_ptr.getChildren()

  def getFenceDevicePtr(self):
    return self.fencedevices_ptr

  def getFailoverDomains(self):
    return self.failoverdomains_ptr.getChildren()
        
  def getFailoverDomainPtr(self):
    return self.failoverdomains_ptr
        
  def getResourceGroups(self):
    rg_list = list()
    kids = self.resourcemanager_ptr.getChildren()
    for kid in kids:
      if kid.getTagName() == RESOURCEGROUP:
        rg_list.append(kid)

    return rg_list
        
  def getResources(self):
    return self.resources_ptr.getChildren()

  def getResourcesPtr(self):
    return self.resources_ptr
        
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
    if gptr == None:  #Obviously not GuLM
      return FALSE
    children = gptr.getChildren()
    for child in children:
      if child.getName() == name:
        return TRUE

    return FALSE
        
   
if __name__ == "__main__":
  print "Starting main program"
  mdl = ModelBuilder()
  objs = mdl.buildModel(None)

  mdl.exportModel("/tmp/tags.xml",objs)
 

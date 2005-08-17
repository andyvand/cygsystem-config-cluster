import string

TAG_NAME = "document"

class TagObject:
  def __init__(self):
    self.attr_hash = {}
    self.children = list()
    self.TAG_NAME = TAG_NAME

  def addChild(self, child):
    #print "in AddChild, adding child %s" % child.getName()
    self.children.append(child)

  def removeChild(self, child):
    self.children.remove(child)

  def addAttribute(self, name, value):
    self.attr_hash[name] = value

  def removeAttribute(self, key):
    try:
      del(self.attr_hash[key])
    except KeyError, e:
      return False

    return True

  def generateXML(self, doc, parent=None):
    #tag = parent.createNode(TAG_NAME)
    #print "TAGNAME is %s" % TAG_NAME
    #print "self.TAGNAME is %s" % self.TAG_NAME
    tag = doc.createElement(self.TAG_NAME)
    if parent != None:
      parent.appendChild(tag)
    else:
      doc.appendChild(tag)
    #tag = parent.createChildElement(TAG_NAME)
    self.exportAttributes(tag)
    #parent.appendChild(tag)
    if len(self.children) > 0:
      for child in self.children:
        if child == None:
          continue
        child.generateXML(doc, tag)

  def exportAttributes(self, tag):
    attrs = self.attr_hash.keys()
    for attr in attrs:
      tag.setAttribute(attr, self.attr_hash[attr])

  def getAttributes(self):
    return self.attr_hash

  def getAttribute(self, kee):
    try:
      return self.attr_hash[kee]
    except KeyError, e:
      return None

  def getChildren(self):
    return self.children

  def getName(self):
    try:
      return self.attr_hash["name"]
    except KeyError, e:
      return ""

  def getTagName(self):
    return self.TAG_NAME

  def getProperties(self):
    return ""

  def isRefObject(self):
    return False

import string
from gtk import TRUE, FALSE
from TagObject import TagObject

TAG_NAME = "ref"

class RefObject(TagObject):
  def __init__(self, obj):
    TagObject.__init__(self)
    self.is_ref_object = TRUE
    self.obj_ptr = obj
    self.TAG_NAME = self.obj_ptr.getTagName()
    if self.TAG_NAME == "ip":
      self.addAttribute("ref", self.obj_ptr.getAttribute("address"))
    else:
      self.addAttribute("ref", self.obj_ptr.getName())

  def getObj(self):
    return self.obj_ptr

  def setRef(self, attr):
    self.addAttribute("ref", attr)


  
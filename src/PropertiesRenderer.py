"""This renderer class renders volume properties into a separate
   drawing area next to the main volume rendering drawing area.
"""
 
import sys
import math
import operator
import types
import select
import signal
import gobject
import pango
import string
import os
from gtk import TRUE, FALSE
from clui_constants import *
import stat
import gettext
_ = gettext.gettext
### gettext first, then import gtk (exception prints gettext "_") ###
try:
    import gtk
    import gtk.glade
except RuntimeError, e:
    print _("""
  Unable to initialize graphical environment. Most likely cause of failure
  is that the tool was not run using a graphical environment. Please either
  start your graphical user interface or set your DISPLAY variable.
                                                                                
  Caught exception: %s
""") % e
    sys.exit(-1)
                                                                                
import gnome
import gnome.ui

LABEL_X = 275
LABEL_Y = 450
X_OFF = 2
Y_OFF = 2
BIG_HEADER_SIZE = 12000
#PROPERTY_SIZE = 10000
PROPERTY_SIZE = 8000
PROPERTIES_FOR_STR=_("Properties for ")
PROPERTIES_STR=_(" Properties")
CLUSTER_STR=_("Cluster")
CLUSTER_PROPS_STR=_("Cluster Properties")
CLUSTER_NODES_STR=_("Cluster Membership")
CLUSTER_NODE_STR=_("Cluster Node:")
FENCE_STR=_("Fence: ")
FENCE_DEVICES_STR=_("Fence Devices")
FENCE_DEVICE_STR=_("Fence Device:")
FENCE_LEVEL_STR=_("Fence Level")
FAILOVER_DOMAINS_STR=_("Failover Domains")
FAILOVER_DOMAIN_STR=_("Failover Domain:")
MANAGED_RESOURCES_STR=_("Managed Resources")
RESOURCES_STR=_("Resources")
RESOURCE_STR=_("Resource:")
SERVICES_STR=_("Services")
SERVICE_STR=_("Service: ")
                                                                                
##############################################################

class PropertiesRenderer:
  def __init__(self, area, widget):
    self.main_window = widget
    self.area = area  #actual widget, used for getting style, hence bgcolor

    #self.area.set_size_request(700, 500)

    self.current_selection_layout = None

    self.layout_list = list()

    self.color_type = "black"

    self.layout_pixmap = gtk.gdk.Pixmap(self.main_window, LABEL_X, LABEL_Y)

    self.gc = self.main_window.new_gc()
    self.pango_context = self.area.get_pango_context()

    self.clear_layout_pixmap()

  def render_to_layout_area(self, prop_list, name, type):
    self.clear_layout_pixmap()
    self.set_color_type(type)
    self.layout_list = list() #Clears list of what to render
    self.prepare_header_layout(name, type)
    self.prepare_prop_layout(prop_list, type)
    self.do_render()


  def prepare_header_layout(self, inname, type):
    pc = self.pango_context
    desc = pc.get_font_description()
    desc.set_size(BIG_HEADER_SIZE)
    pc.set_font_description(desc)
    header_layout = pango.Layout(pc)
    layout_string = ""
    name = inname.replace('_','__')


    if type == CLUSTER_TYPE:
      layout_string = "<span size=\"12000\">" + CLUSTER_PROPS_STR + "</span>"

    elif type == CLUSTER_NODES_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + CLUSTERNODES_COLOR + "\">" + CLUSTER_NODES_STR + "</span>"

    elif type == CLUSTER_NODE_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + CLUSTERNODES_COLOR + "\">" + CLUSTER_NODE_STR + "</span>" + "<span size=\"12000\">  " + name + "</span>" 

    elif type == FENCE_TYPE:
      layout_string = "<span size=\"12000\">" + PROPERTIES_FOR_STR + FENCE_STR % name + "</span>"

    elif type == F_FENCE_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + FENCEDEVICES_COLOR + "\">" + FENCE_STR + "</span>"+ "<span size=\"12000\">" + name + "</span>"

    elif type == FENCE_DEVICES_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + FENCEDEVICES_COLOR + "\">" + FENCE_DEVICES_STR + "</span>"

    elif type == FENCE_DEVICE_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + FENCEDEVICES_COLOR + "\">" + FENCE_DEVICE_STR + "</span>" + "<span size=\"12000\">  " + name + "</span>"

    elif type == MANAGED_RESOURCES_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + CLUSTER_COLOR + "\">" + MANAGED_RESOURCES_STR + "</span>"

    elif type == RESOURCES_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + RESOURCES_COLOR + "\">" + RESOURCES_STR + "</span>"

    elif type == RESOURCE_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + RESOURCE_COLOR + "\">" + RESOURCE_STR + "</span>" + "<span size=\"12000\">  " + name + "</span>"

    elif type == FAILOVER_DOMAINS_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + FAILOVERDOMAINS_COLOR + "\">" + FAILOVER_DOMAINS_STR + "</span>"

    elif type == FAILOVER_DOMAIN_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + FAILOVERDOMAIN_COLOR + "\">" + FAILOVER_DOMAIN_STR + "</span>" + "<span size=\"12000\">  " + name + "</span>"

    elif type == RESOURCE_GROUPS_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + RESOURCEGROUPS_COLOR + "\">" + SERVICES_STR + "</span>" + "<span size=\"12000\">  " + name + "</span>"

    elif type == RESOURCE_GROUP_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + RESOURCEGROUP_COLOR + "\">" + SERVICE_STR + "</span>" + "<span size=\"12000\">  " + name + "</span>"

    elif type == F_LEVEL_TYPE:
      layout_string = "<span size=\"12000\" foreground=\"" + FENCEDEVICES_COLOR + "\">" + FENCE_LEVEL_STR + "</span>" + "<span size=\"12000\">  " + name + "</span>"

    else:
      layout_string = "<span size=\"12000\">" + FAILOVER_DOMAINS_STR + "</span>"

    attr,text,a = pango.parse_markup(layout_string, u'_')
    header_layout.set_attributes(attr)
    header_layout.set_text(text)
    self.layout_list.append(header_layout)
    
    

  def prepare_prop_layout(self, prop_list,type):
    amended_prop_list = ""
    if prop_list == None:
      return
    pc = self.pango_context
    desc = pc.get_font_description()
    desc.set_stretch(pango.STRETCH_NORMAL)
    desc.set_size(PROPERTY_SIZE)
    #pc.set_font_description(desc)

    prop_layout = pango.Layout(pc)
    prop_layout.set_font_description(desc)

    for item in prop_list:
      amended_prop_list = amended_prop_list + item
      if item == "_":
        amended_prop_list = amended_prop_list + "_"

    text_str = "<span size=\"10000\">" + amended_prop_list + "</span>"

    #text_str = prop_list  ##FIX this madness
    #text_str = self.prepare_props_list(prop_list, type)
    #props_layout = pango.Layout(self.pango_context)
    attr,text,a = pango.parse_markup(text_str, u'_')
    prop_layout.set_attributes(attr)
    prop_layout.set_text(text)
    self.layout_list.append(prop_layout)

  def clear_layout_pixmap(self):
    self.set_color("white")
    self.layout_pixmap.draw_rectangle(self.gc, 1, 0, 0, -1, -1)

  def clear_layout_area(self):
    self.clear_layout_pixmap()
    self.layout_list = list()
    self.main_window.draw_drawable(self.gc, self.layout_pixmap, 0, 0, X_OFF, Y_OFF, -1, -1)
    

  def set_color(self, color):
    self.gc.set_foreground(gtk.gdk.colormap_get_system().alloc_color(color, 1,1))

#"""
#  def prepare_props_list(self, props_list, type):
#    stringbuf = list()
#    for i in range(0, len(props_list), 2):
#      if i == 0:
#        stringbuf.append("<b>" + props_list[i] + "</b>")
#        if (type == PHYS_TYPE) or (type == VG_PHYS_TYPE) or (type == UNALLOCATED_TYPE):
#          stringbuf.append("<span foreground=\"#ED1C2A\">")  
#        elif (type == LOG_TYPE) or (type == VG_LOG_TYPE):
#          stringbuf.append("<span foreground=\"#43ACE2\">")  
#        elif type == VG_TYPE:
#          stringbuf.append("<span foreground=\"#43A2FF\">")  
#        else:
#          stringbuf.append("<span foreground=\"#404040\">")  
#
#        stringbuf.append(props_list[i+1])
#        stringbuf.append("</span>")
#      else: 
#        stringbuf.append("\n")
#        stringbuf.append("<b>" + props_list[i] + "</b>")
#        if (type == PHYS_TYPE) or (type == VG_PHYS_TYPE) or (type == UNALLOCATED_TYPE):
#          stringbuf.append("<span foreground=\"#ED1C2A\">")  
#        elif (type == LOG_TYPE) or (type == VG_LOG_TYPE):
#          stringbuf.append("<span foreground=\"#43ACE2\">")  
#        elif type == VG_TYPE:
#          stringbuf.append("<span foreground=\"#43A2FF\">")  
#        else:
#          stringbuf.append("<span foreground=\"#404040\">")  
#
#        stringbuf.append(props_list[i+1])
#        stringbuf.append("</span>")
#
#    text_str = "".join(stringbuf)
#    return text_str
#
  ##This method does the actual rendering. It renders a header
  ##first, then draws a line beneath the  header, and then 
  ##renders the rest of the items in the layout list, with a line to the side
  def do_render(self):
    self.clear_layout_pixmap()
    self.set_color("black")
    y_offset = 0
    y_sum = 0
    start_of_vertical_line = 0
    for layout in self.layout_list:
      x,y = layout.get_pixel_size()
      ###XXX-FIX Check X size to see if it exceedswidth, or do it in proplayout
      if y_offset == 0: #First layout...
        self.layout_pixmap.draw_layout(self.gc, 4, 0, layout)
        y_offset = y_offset + y + 4  #4 is for line width
        self.set_color(self.color_type)
        self.layout_pixmap.draw_line(self.gc, 4,y_offset, LABEL_X - 20, y_offset) 
        self.set_color("black")
        start_of_vertical_line = y_offset
      else:
        self.layout_pixmap.draw_layout(self.gc, 6, y_offset + 5, layout)
        y_offset = y_offset + y
        y_sum = y_sum + y

      if self.current_selection_layout != None:
        self.layout_pixmap.draw_layout(self.gc, 0, y_offset + 5, self.current_selection_layout)

    if y_sum > 0:  #check that there is something to draw a line next to...
      self.set_color(self.color_type)
      self.layout_pixmap.draw_line(self.gc, 4, start_of_vertical_line,4, start_of_vertical_line + y_sum + 20)
      self.set_color("black")
        

    self.main_window.draw_drawable(self.gc, self.layout_pixmap, 0, 0, X_OFF, Y_OFF, -1, -1)

#  def render_selection(self, layout):
#    ###FIXME - This has the potential of eliminating all entries on the list.
#    if layout == None:
#      self.current_selection_layout = None
#      self.do_render()
#    elif layout is self.current_selection_layout:
#      return
#    else:
#      self.current_selection_layout = layout
#      self.do_render() 
##"""

  def set_color_type(self, type):
    if type == CLUSTER_TYPE:
      self.color_type = "black"
    elif type == CLUSTER_NODES_TYPE:
      self.color_type = CLUSTERNODES_COLOR
    elif type == CLUSTER_NODE_TYPE:
      self.color_type = CLUSTERNODES_COLOR
    elif type == FENCE_DEVICES_TYPE:
      self.color_type = FENCEDEVICES_COLOR
    elif type == F_FENCE_TYPE:
      self.color_type = FENCEDEVICES_COLOR
    elif type == FENCE_DEVICE_TYPE:
      self.color_type = FENCEDEVICES_COLOR
    elif type == FAILOVER_DOMAINS_TYPE:
      self.color_type = FAILOVERDOMAINS_COLOR
    elif type == FAILOVER_DOMAIN_TYPE:
      self.color_type = FAILOVERDOMAINS_COLOR
    elif type == RESOURCES_TYPE:
      self.color_type = RESOURCES_COLOR
    elif type == RESOURCE_TYPE:
      self.color_type = RESOURCES_COLOR
    elif type == RESOURCE_GROUPS_TYPE:
      self.color_type = RESOURCEGROUPS_COLOR
    elif type == RESOURCE_GROUP_TYPE:
      self.color_type = RESOURCEGROUPS_COLOR

import gettext
_ = gettext.gettext

DLM_TYPE = 0
GULM_TYPE = 1

CLUSTER_TYPE=1
CLUSTER_NODES_TYPE=2
CLUSTER_NODE_TYPE=3
FENCE_TYPE=4
FENCE_DEVICES_TYPE=5
FENCE_DEVICE_TYPE=6
MANAGED_RESOURCES_TYPE=7
FAILOVER_DOMAINS_TYPE=8
FAILOVER_DOMAIN_TYPE=9
RESOURCE_GROUPS_TYPE=10
RESOURCE_GROUP_TYPE=11
RESOURCES_TYPE=12
RESOURCE_TYPE=14
F_NODE_TYPE=15
F_LEVEL_TYPE=16
F_FENCE_TYPE=17
                                                                                
NAME_COL = 0
TYPE_COL = 1
OBJ_COL = 2

#DISPLAY COLORS
CLUSTER_COLOR="black"
CLUSTERNODES_COLOR="#0033FF"
CLUSTERNODE_COLOR="#0099FF"
FENCEDEVICES_COLOR="#990000"
FENCEDEVICE_COLOR="#CC0000"
FAILOVERDOMAINS_COLOR="#6600CC"
FAILOVERDOMAIN_COLOR="#9933CC"
RESOURCES_COLOR="#006600"
RESOURCE_COLOR="#00CC00"
RESOURCEGROUPS_COLOR="#FF6600"
RESOURCEGROUP_COLOR="#FF8800"

SELECT_RC_TYPE=_("<span><b>Select a Resource Type:</b></span>")

RC_PROPS=_("Properties for %s Resource: %s")

MODIFIED_FILE=_("<modified>")
NEW_CONFIG=_("<New Configuration>")

XML_CONFIG_ERROR=_("<span>A problem was encountered while reading configuration file <b>%s</b> . Details or the error appear below. Click the \'Cancel\' button to quit the application. Click the \'New\' button to create a new configuration file. To continue anyway (Not Recommended!), click the \'Ok\' button.</span>") 

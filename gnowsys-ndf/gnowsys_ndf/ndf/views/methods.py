
''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *

######################################################################################################################################

db = get_database()

#######################################################################################################################################
#                                                                       C O M M O N   M E T H O D S   D E F I N E D   F O R   V I E W S
#######################################################################################################################################

def check_existing_group(groupname):
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.one({"name": groupname})
  if colg:
    return True
  else:
    return False

def get_drawers(nid=None, nlist=[]):
    """Get both drawers-list.
    """

    dict_drawer={}
    dict1={}
    dict2={}

    gst_collection = db[GSystemType.collection_name]
    gst_page = gst_collection.GSystemType.one({'name': GAPPS[0]})
    gs_collection = db[GSystem.collection_name]
    drawer = gs_collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(gst_page._id)]}})

    if (nid is None) and (not nlist):
      for each in drawer:
        dict_drawer[each._id] = str(each.name)

    else:
      for each in drawer:
        if each._id != nid:
          if each._id not in nlist:
            dict1[each._id]=str(each.name)
          
          else:
            dict2[each._id]=str(each.name)
      
      dict_drawer['1'] = dict1
      dict_drawer['2'] = dict2

    return dict_drawer

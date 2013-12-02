''' -- imports from installed packages -- '''
from django.template import Library


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *

##################################################################################################

register=Library()
db=get_database()

##################################################################################################

"""
/**
 * Get GApps toolbar
 */
"""
@register.inclusion_tag('ndf/gapps_toolbar.html')
def get_gapps_toolbar(request):
  gst_collection = db[GSystemType.collection_name]
  gst_cur = gst_collection.GSystemType.find()

  gapps = {}
  for app in gst_cur:
    gapps[app._id] = app.name.lower()

  return {'template': 'ndf/gapps_toolbar.html', 'gapps': gapps,'request':request}

"""
/**
 * Get common template for editing and displaying collection
 */
"""
@register.inclusion_tag('ndf/edit_collection.html', takes_context=True)
def edit_collection(context):
  request = context['request']
  user = request.user
  node = context['node']
  
  collection_obj_dict = context['collection_obj_dict']

  drawers = get_drawers(node)
  drawer1 = drawers['1']
  drawer2 = drawers['2']
  
  return {'template': 'ndf/edit_collection.html', 'user': user, 'node': node, 'drawer1':drawer1,'drawer2':drawer2, 'collection_obj_dict': collection_obj_dict}

"""
/**
 * Get both the collection drawers-list
 */
"""
def get_drawers(node):
    dict_drawer={}
    dict1={}
    dict2={}

    gst_collection = db[GSystemType.collection_name]
    gst_page = gst_collection.GSystemType.one({'name': GAPPS[0]})

    col_GSystem = db[GSystem.collection_name]
    drawer = col_GSystem.GSystem.find({'gsystem_type': {'$all': [ObjectId(gst_page._id)]}})

    if node is None:
      for each in drawer:
        dict_drawer[each._id] = str(each.name)

    else:
      for each in drawer:
        if each._id != node._id:
          if each._id not in node.collection_set:
            dict1[each._id]=str(each.name)
          
          else:
            dict2[each._id]=str(each.name)
      
      dict_drawer['1'] = dict1
      dict_drawer['2'] = dict2

    return dict_drawer

"""
/**
 * Get common template for editing and displaying content
 */
"""
@register.inclusion_tag('ndf/edit_content.html', takes_context=True)
def edit_content(context):
  request = context['request']
  user = request.user
  
  doc_obj = context['node']
  return {'template': 'ndf/edit_content.html', 'user': user, 'node': doc_obj}

"""
/**
 * Get Existing Groups
 */
"""
@register.assignment_tag
def check_group(groupname):
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.one({"name":groupname})
  if colg:
    return True
  else:
    return False

@register.assignment_tag
def get_group_name(groupurl):
  print "SADF",groupurl
  sp=groupurl.split("/",2)
  print "sp=",sp,len(sp)
  if len(sp)<=1:
    return "home"
  if sp[1]:
    chsp=check_group(sp[1])
    if chsp:
      return sp[1]
    else:
      return "home"
  else:
      return "home"

@register.assignment_tag
def get_existing_groups():
  group = []
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.find()
  colg.sort('name')
  gr=list(colg)
  for items in gr:
    group.append(items.name)
  return group

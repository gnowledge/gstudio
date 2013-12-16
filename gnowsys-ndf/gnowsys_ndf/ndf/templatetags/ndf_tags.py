''' -- imports from installed packages -- '''
from django.template import Library


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import check_existing_group
from django.contrib.auth.models import User


##################################################################################################

register=Library()
db=get_database()

##################################################################################################

"""
/**
 * Get GApps toolbar
 */
"""
@register.inclusion_tag('ndf/gapps_menubar.html')
def get_gapps_menubar(request):
  """Get Gapps menu-bar
  """
  gst_collection = db[GSystemType.collection_name]
  gst_cur = gst_collection.GSystemType.find()

  gapps = {}
  for app in gst_cur:
    gapps[app._id] = app.name.lower()

  return {'template': 'ndf/gapps_menubar.html', 'gapps': gapps,'request':request}



#######################################################################################################################################


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

@register.inclusion_tag('ndf/edit_content.html', takes_context=True)
def edit_content(context):
  request = context['request']
  user = request.user
  
  doc_obj = context['node']
  return {'template': 'ndf/edit_content.html', 'user': user, 'node': doc_obj}
"""

@register.assignment_tag
def check_user_join(request,groupname):
  if not request.user:
    return "null"
  user=request.user
  print "grna=",groupname
  usern=User.objects.filter(username=user)
  if usern:
    usern=User.objects.get(username=user)
    user_id=usern.id
  else:
    return "null"
  print "userid",user_id
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.one({"name":groupname})
  print colg
  if colg:
    if colg.created_by == user_id:
      print "auth"
      return "author"
    if colg.author_set:
      if user_id in colg.author_set:
        print "join" 
        return "joined"
      else:
        return "not"
    else:
      return "not"
  else:
    return "nullobj"
  
@register.assignment_tag
def check_group(groupname):
  fl=check_existing_group(groupname)
  return fl

@register.assignment_tag
def get_group_name(groupurl):
  sp=groupurl.split("/",2)
  if len(sp)<=1:
    return "home"
  if sp[1]:
    chsp=check_existing_group(sp[1])
    if chsp:
      print "gname=",sp[1]
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

@register.assignment_tag
def get_existing_groups_excluded(grname):
  group = []
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.find()
  colg.sort('name')
  gr=list(colg)
  for items in gr:
    if items.name != grname:
      group.append(items.name)
  return group



@register.assignment_tag
def get_group_policy(group_name,user):
  policy =""
  col_Group = db[Group.collection_name]
  colg=col_Group.Group.one({"name":group_name})
  if colg:
    policy=str(colg.sub_policy)
  return policy
  

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

@register.inclusion_tag('ndf/gapps_menubar.html')
def get_gapps_menubar(group_name):
  """Get Gapps menu-bar
  """
  gst_collection = db[GSystemType.collection_name]
  gst_cur = gst_collection.GSystemType.find({'_type': u'GSystemType'})
  gapps = {}
  for app in gst_cur:
    gapps[app._id] = app.name.lower()

  return {'template': 'ndf/gapps_menubar.html', 'gapps': gapps, 'group_name': group_name}


@register.assignment_tag
def check_user_join(request,groupname):
  if not request.user:
    return "null"
  user=request.user
  usern=User.objects.filter(username=user)
  if usern:
    usern=User.objects.get(username=user)
    user_id=usern.id
  else:
    return "null"
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.one({"name":groupname})
  if colg:
    if colg.created_by == user_id:
      return "author"
    if colg.author_set:
      if user_id in colg.author_set:
        return "joined"
      else:
        return "not"
    else:
      return "not"
  else:
    return "nullobj"
  
@register.assignment_tag
def check_group(groupname):
  fl = check_existing_group(groupname)
  return fl


@register.assignment_tag
def get_group_name(groupurl):
  sp=groupurl.split("/",2)
  if len(sp)<=1:
    return "home"
  if sp[1]:
    chsp = check_existing_group(sp[1])
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
  colg = col_Group.Group.find({'_type': u'Group'})
  colg.sort('name')
  gr = list(colg)
  for items in gr:
    group.append(items.name)
  return group


@register.assignment_tag
def get_existing_groups_excluded(grname):
  group = []
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.find({'_type':u'Group'})
  colg.sort('name')
  gr=list(colg)
  for items in gr:
    if items.name != grname:
      group.append(items.name)
  if not group:
    group.append("None")
  return group



@register.assignment_tag
def get_group_policy(group_name,user):
  policy = ""
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.one({"name":group_name})
  if colg:
    policy = str(colg.sub_policy)
  return policy

'''this template function is used to get the user object from template''' 
@register.assignment_tag 
def get_user_object(user_id):
  user_obj=""
  try:
    user_obj=User.objects.get(id=user_id)
  except Exception as e:
    print "User Not found in User Table",e
  return user_obj
  

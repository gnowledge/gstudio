''' -- imports from installed packages -- '''
from django.template import Library


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import check_existing_group
from gnowsys_ndf.ndf.views.methods import get_drawers

#######################################################################################################################################

register = Library()
db = get_database()

#######################################################################################################################################

@register.inclusion_tag('ndf/drawer_widget.html')
def edit_drawer_widget(field, node):

  drawers = None
  drawer1 = None
  drawer2 = None

  if node :
    if field == "collection":
      drawers = get_drawers(node._id, node.collection_set)

    elif field == "prior_node":
      drawers = get_drawers(node._id, node.prior_node)
    
    drawer1 = drawers['1']
    drawer2 = drawers['2']

  else:
    drawer1 = get_drawers()

  return {'template': 'ndf/drawer_widget.html', 'widget_for': field, 'drawer1': drawer1, 'drawer2': drawer2}

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
def check_group(groupname):
  fl = check_existing_group(groupname)
  return fl


@register.assignment_tag
def get_group_name(groupurl):
  sp=groupurl.split("/",2)

  if len(sp) <= 1:
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
  

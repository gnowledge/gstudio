''' -- imports from installed packages -- '''
from django.template import Library


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import check_existing_group

from django.contrib.auth.models import User

from gnowsys_ndf.ndf.views.methods import get_drawers

register = Library()
db = get_database()

@register.simple_tag
def get_all_users_to_invite():
  try:
    inv_users={}
    users=User.objects.all()
    for each in users:
      inv_users[each.username.__str__()+"<"+each.email.__str__()+">"]=each.id
    return inv_users
  except Exception as e:
    print str(e)
 

@register.inclusion_tag('ndf/twist_replies.html')
def get_reply(thread,parent,ind,token,user):
  return {'thread':thread,'reply': parent,'user':user,'indent':ind+10,'csrf_token':token,'eachrep':parent}

@register.assignment_tag
def get_all_replies(parent):
   gs_collection = db[Node.collection_name]
   ex_reply=""
   if parent:
     ex_reply=gs_collection.GSystem.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(parent._id)}]})
     ex_reply.sort('created_at',-1)
   return ex_reply


@register.inclusion_tag('ndf/drawer_widget.html')
def edit_drawer_widget(field, group_name, node, checked=None):

  drawers = None
  drawer1 = None
  drawer2 = None

  if node :
    if field == "collection":
      if checked == "Quiz":
        checked = "QuizItem"
      else:
        checked = None

      drawers = get_drawers(group_name, node._id, node.collection_set, checked)

    elif field == "prior_node":
      checked = None
      drawers = get_drawers(group_name, node._id, node.prior_node, checked)
    
    drawer1 = drawers['1']
    drawer2 = drawers['2']

  else:
    if field == "collection" and checked == "Quiz":
      checked = "QuizItem"
    else:
      # To make the collection work as Heterogenous one, by default
      checked = None

    drawer1 = get_drawers(group_name, None, [], checked)

  return {'template': 'ndf/drawer_widget.html', 'widget_for': field, 'drawer1': drawer1, 'drawer2': drawer2, 'group_name': group_name}


@register.inclusion_tag('ndf/gapps_menubar.html')
def get_gapps_menubar(group_name, selectedGapp):
  """Get Gapps menu-bar
  """

  gst_collection = db[GSystemType.collection_name]
  gst_cur = gst_collection.GSystemType.find({'$and':[{'_type':'GSystemType'},{'member_of':'GAPP'}]})

  gapps = {}
  i = 0;
  for app in gst_cur:
    i = i+1;
    gapps[i] = {'id': app._id, 'name': app.name.lower()}

  selectedGapp = selectedGapp.split("/")[2]
  
  return {'template': 'ndf/gapps_menubar.html', 'gapps': gapps, 'selectedGapp':selectedGapp, 'group_name': group_name}


@register.assignment_tag
def get_forum_twists(forum):
  gs_collection = db[Node.collection_name]
  ret_replies=[]
  exstng_reply=gs_collection.GSystem.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(forum._id)}]})
  exstng_reply.sort('created_at')
  for each in exstng_reply:
    ret_replies.append(each)
  return ret_replies

lp=[]
def get_rec_objs(ob_id):
  lp.append(ob_id)
  exstng_reply=gs_collection.GSystem.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(ob_id)}]})
  for each in exstng_reply:
    get_rec_objs(each)
  return lp

@register.assignment_tag
def get_twist_replies(twist):
  gs_collection = db[Node.collection_name]
  ret_replies={}
  entries=[]
  exstng_reply=gs_collection.GSystem.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(twist._id)}]})
  for each in exstng_reply:
    lst=get_rec_objs(each)
        
      
  return ret_replies



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
  colg = col_Group.Group.one({'$and':[{'_type':'Group'},{'name':groupname}]})
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
    if items.name:
      group.append(items)
  return group


@register.assignment_tag
def get_existing_groups_excluded(grname):
  group = []
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.find({'_type':u'Group','group_type':"PUBLIC"})
  colg.sort('name')
  gr=list(colg)
  for items in gr:
    if items.name != grname:
      group.append(items)
  if not group:
    group.append("None")
  return group

@register.assignment_tag
def get_group_policy(group_name,user):
  try:
    policy = ""
    col_Group = db[Group.collection_name]
    colg = col_Group.Group.one({'$and':[{'_type':'Group'},{'name':group_name}]})
    if colg:
      policy = str(colg.subscription_policy)
  except:
    pass
  return policy

@register.assignment_tag
def get_user_group(user):

  group = []
  col_Group = db[Group.collection_name]

  colg = col_Group.Group.find({ '_type': u'Group', 
                                'name': {'$nin': ['home']},
                                '$or':[{'created_by':user.id}, {'group_type':'PUBLIC'},{'author_set':user.id}] 
                              })

  for g in colg:
    group.append(g)
    
  return group



'''this template function is used to get the user object from template''' 
@register.assignment_tag 
def get_user_object(user_id):
  user_obj=""
  try:
    user_obj=User.objects.get(id=user_id)
  except Exception as e:
    print "User Not found in User Table",e
  return user_obj
  

'''this template function is used to get the user object from template''' 
@register.assignment_tag 
def get_grid_fs_object(f):
  '''get the gridfs object by object id'''
  grid_fs_obj = ""
  try:
    file_collection = db[File.collection_name]
    file_obj = file_collection.File.one({'_id':ObjectId(f['_id'])})
    grid_fs_obj =  file_obj.fs.files.get(file_obj.fs_file_ids[0])
  except Exception as e:
    print "Object does not exist", e
  return grid_fs_obj
  

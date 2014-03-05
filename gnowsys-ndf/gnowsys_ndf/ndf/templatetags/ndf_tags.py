''' -- imports from python libraries -- '''
import re

''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.template import Library
from django.template import RequestContext,loader
from django.shortcuts import render_to_response, render

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, META_TYPE
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import check_existing_group
from gnowsys_ndf.ndf.views.methods import get_drawers


register = Library()
db = get_database()
collection = db[Node.collection_name]

@register.simple_tag
def get_all_users_to_invite():
  try:
    inv_users={}
    users=User.objects.all()
    for each in users:
      inv_users[each.username.__str__()]=each.id.__str__()
    return str(inv_users)
  except Exception as e:
    print str(e)
 

@register.inclusion_tag('ndf/twist_replies.html')
def get_reply(thread,parent,forum,token,user):
  return {'thread':thread,'reply': parent,'user':user,'forum':forum,'csrf_token':token,'eachrep':parent}

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
      
    elif field == "module":
      checked = "Module"
      drawers = get_drawers(group_name, node._id, node.collection_set, checked)
    
    drawer1 = drawers['1']
    drawer2 = drawers['2']

  else:
    if field == "collection" and checked == "Quiz":
      checked = "QuizItem"
      
    elif field == "module":
      checked = "Module"
      
    else:
      # To make the collection work as Heterogenous one, by default
      checked = None

    drawer1 = get_drawers(group_name, None, [], checked)

  return {'template': 'ndf/drawer_widget.html', 'widget_for': field, 'drawer1': drawer1, 'drawer2': drawer2, 'group_name': group_name}

@register.inclusion_tag('tags/dummy.html')
def list_widget(type_value, fields_value,template1='ndf/option_widget.html',template2='ndf/drawer_widget.html'):
  drawer1 = {}
  drawer2 = None
  group_name = ""
  alltypes = ["GSystemType","MetaType","AttributeType","RelationType"]
  fields_selection1 = ["subject_type","object_type","applicable_node_type","subject_applicable_nodetype","object_applicable_nodetype","data_type"]
  fields_selection2 = ["meta_type_set","attribute_type_set","relation_type_set","prior_node","member_of"]
  fields = {"subject_type":"GSystemType","object_type":"GSystemType","meta_type_set":"MetaType","attribute_type_set":"AttributeType","relation_type_set":"RelationType","member_of":"all_types","prior_node":"all_types","applicable_node_type":"NODE_TYPE_CHOICES","subject_applicable_nodetype":"NODE_TYPE_CHOICES","object_applicable_nodetype":"NODE_TYPE_CHOICES","data_type": "DATA_TYPE_CHOICES"}
  types = fields[type_value]

  if type_value in fields_selection1:
    print type_value,"tagss"
    if type_value in ("applicable_node_type","subject_applicable_nodetype","object_applicable_nodetype"):
      for each in NODE_TYPE_CHOICES:
        drawer1[each] = each
    elif type_value in ("data_type"):
      for each in DATA_TYPE_CHOICES:
        drawer1[each] = each
    else:
      drawer = collection.Node.find({"_type":types})
      for each in drawer:
        drawer1[str(each._id)]=each.name
    return {'template': template1, 'widget_for': type_value, 'drawer1': drawer1}
  
  if type_value in fields_selection2:
    if types in alltypes:
      for each in collection.Node.find({"_type":types}):
        drawer1[each._id] = each
    if types in ["all_types"]:
      for each in alltypes:
        for eachnode in collection.Node.find({"_type":each}):
          drawer1[eachnode._id] = eachnode
    return {'template': template2, 'widget_for': type_value, 'drawer1': drawer1, 'drawer2': drawer2, 'group_name': "home"}


@register.inclusion_tag('ndf/gapps_menubar.html')
def get_gapps_menubar(group_name, selectedGapp):
  """Get Gapps menu-bar
  """

  collection = db[Node.collection_name]
  
  gapps = {}
  i = 0;

  meta_type = collection.Node.one({'$and':[{'_type':'MetaType'},{'name': META_TYPE[0]}]})
  GAPPS = collection.Node.find({'$and':[{'_type':'GSystemType'},{'member_of':{'$all':[meta_type._id]}}]}).sort("created_at")

  for node in GAPPS:
    if node:
      if node.name not in ["Image", "Video"]:
        i = i+1;
        gapps[i] = {'id': node._id, 'name': node.name.lower()}

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
  colg = col_Group.Group.find({'_type':u'Group', 'group_type': "PUBLIC"})  
  colg.sort('name')
  gr=list(colg)
  for items in gr:
    if items.name != grname:
      group.append(items)
  if not group:
    return "None"
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
  author = None
  auth_type = ""

  col_Group = db[Group.collection_name]
  collection = db[Node.collection_name]

  group_gst = collection.Node.one({'_type': 'GSystemType', 'name': 'Group'})
  auth_obj = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Author'})

  if auth_obj:
    auth_type = auth_obj._id

  colg = col_Group.Group.find({ '_type': u'Group', 
                                'name': {'$nin': ['home']},
                                '$or':[{'created_by':user.id}, {'group_type':'PUBLIC'},{'author_set':user.id}, {'member_of': {'$all':[auth_type]}} ] 
                              })
  
  auth = col_Group.Group.one({'_type': u"Group", 'name': unicode(user.username)})
  
  for items in colg:  
    if items.created_by == user.pk:
      if items.name == auth.name:
        author = items
      else:
        group.append(items)
    
    else:
      if items.author_set or (items.group_type == "PUBLIC" and group_gst._id in items.member_of):
        group.append(items)

  if author: 
    group.append(author)

  if not group:
    return "None"

  return group


@register.assignment_tag
def get_profile_pic(user):

  ID = User.objects.get(username=user).pk
  GST_IMAGE = collection.GSystemType.one({'name': GAPPS[3]})

  prof_pic = collection.GSystem.one({'_type': 'File', 'type_of': 'profile_pic', 'member_of': {'$all': [ObjectId(GST_IMAGE._id)]}, 'created_by': int(ID) })  

  return prof_pic


@register.assignment_tag
def get_group_type(grname,user):
  col_Group = db[Group.collection_name]
  
  #get all the strings after and before the /
  split_result = re.split(r'[/=]', grname)
  
  # check wheather Group exist in the database
  colg=col_Group.Group.one({'_type': 'Group','name':split_result[1]})
  #Query for implemting the same senario with ObjectId instead of Group name
  #  colg=col_Group.Group.one({'_type': 'Group','_id':split_result[1]})

  #check if Group exist in the database
  if colg is not None:
	# Check is user is logged in
	if  user.id:
		# condition for group accesseble to logged user
	  	if colg.group_type=="PUBLIC" or colg.created_by==user.id or user.id in colg.author_set:
			return "allowed"
		else:
			raise Http404	
	else:
		#condition for groups,accesseble to not logged users
		if colg.group_type=="PUBLIC":
			
			return "allowed"
                else:
			print "redirection"
			raise Http404
  else:
	
	return "pass"		
	
  


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

@register.inclusion_tag('ndf/admin_class.html')
def get_class_list(class_name):
  """Get list of class 
  """
  class_list = ["GSystem", "File", "Group", "GSystemType", "RelationType", "AttributeType"]
  return {'template': 'ndf/admin_class.html', "class_list": class_list, "class_name":class_name,"url":"data"}

@register.inclusion_tag('ndf/admin_class.html')
def get_class_type_list(class_name):
  """Get list of class 
  """
  class_list = ["GSystemType", "RelationType", "AttributeType"]
  return {'template': 'ndf/admin_class.html', "class_list": class_list, "class_name":class_name,"url":"designer"}

@register.assignment_tag
def get_Object_count(key):
    try:
        return collection.Node.find({'_type':key}).count()
    except:
        return 'null'
  
@register.filter
def get_dict_item(dictionary, key):
    return dictionary.get(key)

@register.inclusion_tag('ndf/admin_fields.html')
def get_input_fields(fields_value,type_value):
  """Get html tags 
  """
  field_type_list = ["meta_type_set","attribute_type_set","relation_type_set","prior_node","member_of"]
  return {'template': 'ndf/admin_fields.html', "fields_value": fields_value, "type_value":type_value,"field_type_list":field_type_list}

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
from gnowsys_ndf.settings import GAPPS as setting_gapps, META_TYPE,CREATE_GROUP_VISIBILITY
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import check_existing_group,get_all_gapps,get_all_resources_for_group
from gnowsys_ndf.ndf.views.methods import get_drawers
from gnowsys_ndf.mobwrite.models import TextObj
from pymongo.errors import InvalidId as invalid_id
from django.contrib.sites.models import Site

register = Library()
db = get_database()
collection = db[Node.collection_name]
at_apps_list=collection.Node.one({'$and':[{'_type':'AttributeType'}, {'name':'apps_list'}]})
translation_set=[]
check=[]

@register.inclusion_tag('ndf/userpreferences.html')
def get_user_preferences(group,user):
	return {'groupid':group,'author':user}


@register.assignment_tag
def get_group_resources(group):
	try:
		res=get_all_resources_for_group(group['_id'])
		return res.count
	except Exception as e:
		print "Error in get_group_resources "+str(e)
	
@register.assignment_tag
def all_gapps():
	try:
		return get_all_gapps()
	except Exception as expt:
		print "Error in get_all_gapps "+str(expt)

@register.assignment_tag
def get_create_group_visibility():
	if CREATE_GROUP_VISIBILITY:
		return True
	else:
		return False

@register.assignment_tag
def get_site_info():
	sitename=Site.objects.all()[0].name.__str__()
	return sitename

@register.assignment_tag
def check_gapp_menus(groupid):
	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(groupid) is False :
		group_ins = collection.Node.find_one({'_type': "Group", "name": groupid}) 
		if group_ins:
			groupid = str(group_ins._id)
	else :
		pass
	grp=collection.Node.one({'_id':ObjectId(groupid)})
	if not at_apps_list:
		return False
	poss_atts=grp.get_possible_attributes(grp.member_of)
	if not poss_atts:
		return False
	return True
	
 
@register.assignment_tag
def get_apps_for_groups(groupid):
	try:
		ret_dict={}
		grp=collection.Node.one({'_id':ObjectId(groupid)})
		poss_atts=grp.get_possible_attributes(at_apps_list._id)
		if poss_atts:
			list_apps=poss_atts['apps_list']['object_value']
			counter=1
			for each in list_apps:
				obdict={}
				obdict['id']=each['_id']
				obdict['name']=each['name'].lower()
				ret_dict[counter]=obdict
				counter+=1 
			return ret_dict 
		else:
			gpid=collection.Group.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
			gapps = {}
			i = 0;
			meta_type = collection.Node.one({'$and':[{'_type':'MetaType'},{'name': META_TYPE[0]}]})
			GAPPS = collection.Node.find({'$and':[{'_type':'GSystemType'},{'member_of':{'$all':[meta_type._id]}}]}).sort("created_at")
			group_obj=collection.Group.one({'_id':ObjectId(groupid)})
			if group_obj.name == "home":
				not_in_menu_bar = ["Image", "Video"]
			else :
				not_in_menu_bar = ["Image", "Video", "Group"]
			for node in GAPPS:
				if node:
					if node.name not in not_in_menu_bar:
						i = i+1;
						if node.name in setting_gapps:
							gapps[i] = {'id': node._id, 'name': node.name.lower()}
						else:
							gapps[i] = {'id': node._id, 'name': node.name}
			return gapps
	except Exception as exptn:
		print "Exception in get_apps_for_groups "+str(exptn)


@register.assignment_tag
def check_is_user_group(group_id):
	try:
		lst_grps=[]
		all_user_grps=get_all_user_groups()
		grp=collection.Node.one({'_id':ObjectId(group_id)})
		for each in all_user_grps:
			lst_grps.append(each.name)
		if grp.name in lst_grps:
			return True
		else:
			return False
	except Exception as exptn:
		print "Exception in check_user_group "+str(exptn)

@register.assignment_tag
def switch_group_conditions(user,group_id):
	try:
		ret_policy=False
		req_user_id=User.objects.get(username=user).id
		group=collection.Node.one({'_id':ObjectId(group_id)})
		if req_user_id in group.author_set and group.group_type == 'PUBLIC':
			ret_policy=True
		return ret_policy
	except Exception as ex:
		print "Exception in switch_group_conditions"+str(ex)
 
@register.assignment_tag
def get_all_user_groups():
	try:
		all_groups=collection.Node.find({'_type':'Author'})
		return list(all_groups)
	except:
		print "Exception in get_all_user_groups"

@register.assignment_tag
def get_group_object(group_id = None):
	try:
		colln=db[Node.collection_name]
		if group_id == None :
			group_object=colln.Group.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
		else:
			group_object=colln.Group.one({'_id':ObjectId(group_id)})
		return group_object
	except invalid_id:
		group_object=colln.Group.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
		return group_object

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
def get_reply(thread,parent,forum,token,user,group_id):
	return {'thread':thread,'reply': parent,'user':user,'forum':forum,'csrf_token':token,'eachrep':parent,'groupid':group_id}

@register.assignment_tag
def get_all_replies(parent):
	 gs_collection = db[Node.collection_name]
	 ex_reply=""
	 if parent:
		 ex_reply=gs_collection.GSystem.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(parent._id)}]})
		 ex_reply.sort('created_at',-1)
	 return ex_reply


# @register.inclusion_tag('ndf/drawer_widget.html')
# def edit_drawer_widget(field, group_id, node, checked=None):

# 	drawers = None
# 	drawer1 = None
# 	drawer2 = None

# 	if node :
# 		if field == "collection":
# 			if checked == "Quiz":
# 				checked = "QuizItem"
# 			elif checked == "Theme":
# 				checked = "Theme"
# 			else:
# 				checked = None
# 			drawers = get_drawers(group_id, node._id, node.collection_set, checked)
# 		elif field == "prior_node":
# 			checked = None
# 			drawers = get_drawers(group_id, node._id, node.prior_node, checked)
# 		elif field == "module":
# 			checked = "Module"
# 			drawers = get_drawers(group_id, node._id, node.collection_set, checked)
		
# 		drawer1 = drawers['1']
# 		drawer2 = drawers['2']

# 	else:
# 		if field == "collection" and checked == "Quiz":
# 			checked = "QuizItem"

# 		elif field == "collection" and checked == "Theme":
# 			checked = "Theme"
			
# 		elif field == "module":
# 			checked = "Module"
			
# 		else:
# 			# To make the collection work as Heterogenous one, by default
# 			checked = None

# 		drawer1 = get_drawers(group_id, None, [], checked)

# 	return {'template': 'ndf/drawer_widget.html', 'widget_for': field, 'drawer1': drawer1, 'drawer2': drawer2, 'group_id': group_id,'groupid': group_id}

@register.inclusion_tag('tags/dummy.html')
def list_widget(fields_name, fields_type, fields_value, template1='ndf/option_widget.html',template2='ndf/drawer_widget.html'):
	drawer1 = {}
	drawer2 = None
	groupid = ""
	group_obj= collection.Node.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})

	if group_obj:
		groupid = str(group_obj[0]._id)

	alltypes = ["GSystemType","MetaType","AttributeType","RelationType"]

	fields_selection1 = ["subject_type","language","object_type","applicable_node_type","subject_applicable_nodetype","object_applicable_nodetype","data_type"]

	fields_selection2 = ["meta_type_set","attribute_type_set","relation_type_set","prior_node","member_of","type_of"]

	fields = {"subject_type":"GSystemType", "object_type":"GSystemType", "meta_type_set":"MetaType", "attribute_type_set":"AttributeType", "relation_type_set":"RelationType", "member_of":"MetaType", "prior_node":"all_types", "applicable_node_type":"NODE_TYPE_CHOICES", "subject_applicable_nodetype":"NODE_TYPE_CHOICES", "object_applicable_nodetype":"NODE_TYPE_CHOICES", "data_type": "DATA_TYPE_CHOICES", "type_of": "GSystemType","language":"GSystemType"}
	types = fields[fields_name]

	if fields_name in fields_selection1:
		if fields_value:
			dummy_fields_value = fields_value
			fields_value = []
			for v in dummy_fields_value:
				fields_value.append(v.__str__())

		if fields_name in ("applicable_node_type","subject_applicable_nodetype","object_applicable_nodetype"):
			for each in NODE_TYPE_CHOICES:
				drawer1[each] = each
		elif fields_name in ("data_type"):
			for each in DATA_TYPE_CHOICES:
				drawer1[each] = each
		elif fields_name in ("language"):
				drawer1['hi']='hi'
				drawer1['en']='en'
				drawer1['mar']='mar'
		else:
			drawer = collection.Node.find({"_type":types})
			for each in drawer:
				drawer1[str(each._id)]=each.name
		return {'template': template1, 'widget_for': fields_name, 'drawer1': drawer1, 'selected_value': fields_value}

	
	if fields_name in fields_selection2:
		fields_value_id_list = []

		if fields_value:
			for each in fields_value:
				if type(each) == ObjectId:
					fields_value_id_list.append(each)
				else:
					fields_value_id_list.append(each._id)

		if types in alltypes:
			for each in collection.Node.find({"_type": types}):
				if fields_value_id_list:
					if each._id not in fields_value_id_list:
						drawer1[each._id] = each
				else:
					drawer1[each._id] = each

		if types in ["all_types"]:
			for each in alltypes:
				for eachnode in collection.Node.find({"_type": each}):
					if fields_value_id_list:
						if eachnode._id not in fields_value_id_list:
							drawer1[eachnode._id] = eachnode
					else:
						drawer1[eachnode._id] = eachnode

		if fields_value_id_list:
			drawer2 = []
			for each_id in fields_value_id_list:
				each_node = collection.Node.one({'_id': each_id})
				if each_node:
					drawer2.append(each_node)

		return {'template': template2, 'widget_for': fields_name, 'drawer1': drawer1, 'drawer2': drawer2, 'group_id': groupid, 'groupid': groupid}


@register.inclusion_tag('ndf/gapps_menubar.html')
def get_gapps_menubar(group_id, selectedGapp):
	"""Get Gapps menu-bar
	"""
	try:
		group_name = ""
		collection = db[Node.collection_name]
		gpid=collection.Group.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
#    gst_cur = collection.Node.find({'_type': 'GSystemType', 'name': {'$in': GAPPS}})
		gapps = {}
		i = 0;
		meta_type = collection.Node.one({'$and':[{'_type':'MetaType'},{'name': META_TYPE[0]}]})
		
		GAPPS = collection.Node.find({'$and':[{'_type':'GSystemType'},{'member_of':{'$all':[meta_type._id]}}]}).sort("created_at")
		group_obj=collection.Group.one({'_id':ObjectId(group_id)})
		not_in_menu_bar = []
		if group_obj.name == "home":
			not_in_menu_bar = ["Image", "Video"]
		else :
			not_in_menu_bar = ["Image", "Video", "Group"]						
		for node in GAPPS:
			#node = collection.Node.one({'_type': 'GSystemType', 'name': app, 'member_of': {'$all': [meta_type._id]}})
			if node:
				if node.name not in not_in_menu_bar:
					i = i+1;
					gapps[i] = {'id': node._id, 'name': node.name.lower()}

		if len(selectedGapp.split("/")) > 2 :
			selectedGapp = selectedGapp.split("/")[2]
		else :
			selectedGapp = selectedGapp.split("/")[1]
		if group_id == None:
			group_id=gpid._id
		group_obj=collection.Group.one({'_id':ObjectId(group_id)})
		if not group_obj:
			group_id=gpid._id
		else :
			group_name = group_obj.name

		return {'template': 'ndf/gapps_menubar.html', 'gapps': gapps, 'selectedGapp':selectedGapp,'groupid':group_id, 'group_name':group_name}
	except invalid_id:
		gpid=collection.Group.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
		group_id=gpid._id
		return {'template': 'ndf/gapps_menubar.html', 'gapps': gapps, 'selectedGapp':selectedGapp,'groupid':group_id}


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
def check_user_join(request,group_id):
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
	if group_id == '/home/'or group_id == "":
		colg=col_Group.Group.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
	else:
		colg = col_Group.Group.one({'_id':ObjectId(group_id)})
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
def check_group(group_id):
	fl = check_existing_group(group_id)
	return fl


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
def get_existing_groups_excluding_username():
	group = []
	col_Group = db[Group.collection_name]
	user_list=[]
	users=User.objects.all()
	for each in users:
		user_list.append(each.username)
	colg = col_Group.Group.find({'$and':[{'_type': u'Group'},{'name':{'$nin':user_list}}]})
	colg.sort('name')
	gr = list(colg)
	for items in gr:
		if items.name:
			group.append(items)
	return group

@register.assignment_tag
def get_existing_groups_excluded(grname):
  """
  Returns only first 10 public group(s) (sorted by last_update field in descending order) 
  excluding the currently selected group if it comes under the searching criteria

  Keyword arguments:
  grname -- name of the group which is currently selected

  Returns:
  list of group node(s) resulted after given searching criteria
  """
  group_cur = collection.Node.find({'_type':u"Group", 'name': {'$nin': [u"home", grname]}, 'group_type': "PUBLIC"}).sort('last_update', -1).limit(10)

  if group_cur.count() <= 0:
    return "None"

  return group_cur

@register.assignment_tag
def get_group_policy(group_id,user):
	try:
		policy = ""
		col_Group = db[Group.collection_name]
		colg = col_Group.Group.one({'_id':ObjectId(group_id)})
		if colg:
			policy = str(colg.subscription_policy)
	except:
		pass
	return policy

@register.assignment_tag
def get_user_group(user, selected_group_name):
  """
  Returns first 10 group(s) to which logged-in user is subscribed to (sorted by last_update field in descending order) 
  excluding the currently selected group if it comes under the searching criteria

  Keyword arguments:
  user -- django's user object

  selected_group_name -- name of the group which is currently selected

  Returns:
  list of group and/or author (logged-in) node(s) resulted after given searching criteria
  """
  group_list = []
  auth_group = None

  group_cur = collection.Node.find({'_type': "Group", 'name': {'$nin': ["home", selected_group_name]}, 'author_set': user.id}).sort('last_update', -1).limit(10)

  auth_group = collection.Node.one({'_type': "Author", '$and': [{'name': unicode(user.username)}, {'name': {'$ne': selected_group_name}}]})

  if group_cur.count():
    for g in group_cur:
      group_list.append(g)

  if auth_group:
    # Appends author node at the bottom of the list, if it exists
    group_list.append(auth_group)

  if not group_list:
    return "None"

  return group_list


@register.assignment_tag
def get_profile_pic(user):
	ID = User.objects.get(username=user).pk
	auth = collection.Node.one({'_type': u'Author', 'name': unicode(user)})
	collection_tr = db[Triple.collection_name]

	if auth:
		profile_pic_RT = collection.Node.one({'_type': 'RelationType', 'name': u'has_profile_pic' })
		dbref_profile_pic = profile_pic_RT.get_dbref()
		prof_pic_rel = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_profile_pic })        

		if prof_pic_rel.count() :
			index = prof_pic_rel.count() - 1
			Index = prof_pic_rel[index].right_subject
			# prof_pic = collection.Node.one({'_type': 'File', '_id': ObjectId(prof_pic_rel['right_subject'])})      
			prof_pic = collection.Node.one({'_type': 'File', '_id': ObjectId(Index) })      
		else:
			prof_pic = "" 
	else:
		prof_pic = ""
		
	return prof_pic


@register.assignment_tag
def get_theme_node(groupid, node):

	topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
	theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})

	# code for finding nodes collection has only topic instances or not
	# It checks if first element in collection is theme instance or topic instance accordingly provide checks
	if node.collection_set:
		collection_nodes = collection.Node.one({'_id': ObjectId(node.collection_set[0]) })
		if theme_GST._id in collection_nodes.member_of:
			return "Theme_Enabled"
		if topic_GST._id in collection_nodes.member_of:
			return "Topic_Enabled"
		
	else:
		return True


@register.assignment_tag
def get_group_name(val):

	GroupName = []

	for each in val.group_set: 

		grpName = collection.Node.one({'_id': ObjectId(each) }).name.__str__()
		GroupName.append(grpName)
	
	return GroupName

@register.assignment_tag
def get_edit_url(groupid):

	node = collection.Node.one({'_id': ObjectId(groupid) }) 
	if node._type == 'GSystem':

		type_name = collection.Node.one({'_id': node.member_of[0]}).name

		if type_name == 'Quiz':
			return 'quiz_edit'    
		elif type_name == 'Page':
			return 'page_create_edit' 
		elif type_name == 'QuizItem':
			return 'quiz_item_edit'

	elif node._type == 'Group' or node._type == 'Author' :
		return 'edit_group'

	elif node._type == 'File':
		if node.mime_type == 'video':      
			return 'video_edit'       
		elif 'image' in node.mime_type:
			return 'image_edit'
		else:
			return 'file_edit'

@register.assignment_tag
def get_create_url(groupid):

  node = collection.Node.one({'_id': ObjectId(groupid) }) 
  if node._type == 'GSystem':

    type_name = collection.Node.one({'_id': node.member_of[0]}).name

    if type_name == 'Quiz':
      return 'quiz_create'    
    elif type_name == 'Page':
      return 'page_create_edit' 
    elif type_name == 'QuizItem':
      return 'quiz_item_create'

  elif node._type == 'Group' or node._type == 'Author' :
    return 'create_group'

  elif node._type == 'File':
    return 'uploadDoc'
	


@register.assignment_tag
def get_group_type(group_id, user):

	try:
		col_Group = db[Group.collection_name]

		if group_id == '/home/':
			colg=col_Group.Group.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
		else:  
			gid = group_id.replace("/", "")
			if ObjectId.is_valid(gid):
				colg = col_Group.Group.one({'_type': 'Group', '_id': ObjectId(gid)})
			else:
				colg = None
		
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
				#condition for groups, accessible to not logged users
				if colg.group_type == "PUBLIC":
					return "allowed"
				else:
					raise Http404
		else:
			return "pass"

	except Http404:
		raise Http404
		
	except Exception as e:
		print "Error in group_type_tag "+str(e)
		colg=col_Group.Group.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
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
                if file_obj.mime_type == 'video':
                        if len(file_obj.fs_file_ids) > 2:
                                if (file_obj.fs.files.exists(file_obj.fs_file_ids[2])):
                                        grid_fs_obj = file_obj.fs.files.get(ObjectId(file_obj.fs_file_ids[2]))
                else:
                        grid_fs_obj =  file_obj.fs.files.get(file_obj.fs_file_ids[0])
	except Exception as e:
		print "Object does not exist", e
	return grid_fs_obj

@register.inclusion_tag('ndf/admin_class.html')
def get_class_list(class_name):
	"""Get list of class 
	"""
	class_list = ["GSystem", "File", "Group", "GSystemType", "RelationType", "AttributeType", "GRelation", "GAttribute"]
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

@register.assignment_tag
def get_memberof_objects_count(key,group_id):
	try:
		return collection.Node.find({'member_of': {'$all': [ObjectId(key)]},'group_set': {'$all': [ObjectId(group_id)]}}).count()
	except:
		return 'null'
	
@register.filter
def get_dict_item(dictionary, key):
		return dictionary.get(key)


@register.assignment_tag
def get_policy(group, user):
  if group.group_type =='PUBLIC':
    return False
  elif user.is_superuser:
    return True
  elif user.id in group.author_set:
    return True
  elif user.id == group.created_by:
    return True
  else:
    return False


@register.inclusion_tag('ndf/admin_fields.html')
def get_input_fields(fields_type,fields_name,translate=None):
	"""Get html tags 
	"""
	field_type_list = ["meta_type_set","attribute_type_set","relation_type_set","prior_node","member_of","type_of"]
	return {'template': 'ndf/admin_fields.html', 
					"fields_name":fields_name, "fields_type": fields_type[0], "fields_value": fields_type[1], 
					"field_type_list":field_type_list,"translate":translate}
	

@register.assignment_tag
def group_type_info(groupid,user=0):
	col_Group =db[Group.collection_name]
	group_gst = col_Group.Group.one({'_id':ObjectId(groupid)})
	
	if group_gst.post_node:
		return "BaseModerated"
	elif group_gst.prior_node:
		return "Moderated"   
	else:
		return  group_gst.group_type                        

			
@register.assignment_tag
def user_access_policy(node, user):
  """
  Returns status whether logged-in user is able to access any resource.

  Check is performed in given sequence as follows (sequence has importance):
  - If user is superuser, then he/she is allowed
  - Else if group's edit-policy is "NON_EDITABLE" (currently "home" is such group), then user is NOT allowed
  - Else if user is creator of the group, then he/she is allowed
  - Else if user is member of the group, then he/she is allowed
  - Else user is NOT allowed!

  Arguments:
  node -- group's node that is currently selected by the user_access
  user -- user's node that is currently logged-in

  Returns:
  string value (allow/disallow), i.e. whether user is allowed or not!
  """
	# try:
	# 	col_Group=db[Group.collection_name]
	# 	group_gst = col_Group.Group.one({'_id':ObjectId(node)})
	# 	# if user.id in group_gst.group_set or group_gst.created_by == user.id:
	# 	if user.id in group_gst.author_set or group_gst.created_by == user.id :
	# 		return 'allow'
	# except Exception as e:
	# 	print "Exception in user_access_policy- "+str(e)

  user_access = False

  try:
    if user.is_superuser:
      user_access = True

    else:
      group_node = collection.Node.one({'_type': {'$in': ["Group", "Author"]}, '_id': ObjectId(node)})

      if user.id == group_node.created_by:
        user_access = True

      elif group_node.edit_policy == "NON_EDITABLE":
        user_access = False

      elif user.id in group_node.author_set:
        user_access = True

      else:
        user_access = False

    if user_access:
      return "allow"

    else:
      return "disallow"

  except Exception as e:
    error_message = "\n UserAccessPolicyError: " + str(e) + " !!!\n"
    raise Exception(error_message)
			
		
@register.assignment_tag
def resource_info(node):
		col_Group=db[Group.collection_name]
		try:
			group_gst=col_Group.Group.one({'_id':ObjectId(node._id)})
		except:
			grname=re.split(r'[/=]',node)
			group_gst=col_Group.Group.one({'_id':ObjectId(grname[1])})
		return group_gst
																
		
@register.assignment_tag
def edit_policy(groupid,node,user):
	group_access= group_type_info(groupid,user)
	resource_infor=resource_info(node)
	#code for public Groups and its Resources
	
	if group_access == "PUBLIC":
			#user_access=user_access_policy(groupid,user)
			#if user_access == "allow":
			return "allow"
	elif group_access == "PRIVATE":
			return "allow"
	elif group_access == "BaseModerated":
			 user_access=user_access_policy(groupid,user)
			 if user_access == "allow":
					resource_infor=resource_info(node)
					#code for exception 
					if resource_infor._type == "Group":
							return "allow"
					elif resource_infor.created_by == user.id:
							return "allow"    
					elif resource_infor.status == "PUBLISHED":    
							return "allow"
	elif group_access == "Moderated": 
			 return "allow"
	elif resource_infor.created_by == user.id:
							return "allow"    
						
		
	 

@register.assignment_tag
def get_prior_post_node(group_id):
	
	col_Group = db[Group.collection_name]
	prior_post_node=col_Group.Group.one({'_type': 'Group',"_id":ObjectId(group_id)})
	#check wheather we got the Group name       
	if prior_post_node is not  None:
			 #first check the prior node id  and take the id
			 Prior_nodeid=prior_post_node.prior_node
			 #once you have the id check search for the base node
			 base_colg=col_Group.Group.one({'_type':u'Group','_id':{'$in':Prior_nodeid}})
			 
			 if base_colg is None:
					#check for the Post Node id
					 Post_nodeid=prior_post_node.post_node
					 Mod_colg=col_Group.Group.one({'_type':u'Group','_id':{'$in':Post_nodeid}})
					 if Mod_colg is not None:
						#return node of the Moderated group            
						return Mod_colg
			 else:
					#return node of the base group
					return base_colg
	
@register.assignment_tag
def Group_Editing_policy(groupid,node,user):
	col_Group = db[Group.collection_name]
	node=col_Group.Group.one({"_id":ObjectId(groupid)})

	if node.edit_policy == "EDITABLE_MODERATED":
		 status=edit_policy(groupid,node,user)
		 if status is not None:
				return "allow"
	elif node.edit_policy == "NON_EDITABLE":
		status=non_editable_policy(groupid,user.id)
		if status is not None:
				return "allow"
	elif node.edit_policy == "EDITABLE_NON_MODERATED":  
		 status=edit_policy(groupid,node,user)
		 if status is not None:
				return "allow"
	elif node.edit_policy is None:
		return "allow"      
	


@register.assignment_tag
def get_publish_policy(request, groupid, res_node):
  resnode = collection.Node.one({"_id": ObjectId(res_node._id)})

  if resnode.status == "DRAFT":
    node = collection.Node.one({"_id": ObjectId(groupid)})

    group_type = group_type_info(groupid)
    group = user_access_policy(groupid,request.user)
    ver = node.current_version
    
    if request.user.id:
      if group_type == "Moderated":
      	base_group=get_prior_post_node(groupid)
      	if base_group is not None:
      		if base_group.status == "DRAFT" or node.status == "DRAFT":
    				return "allow"

      elif node.edit_policy == "NON_EDITABLE":
        if resnode._type == "Group":
        	if ver == "1.1" or (resnode.created_by != request.user.id and not request.user.is_superuser):
        		return "stop"
        if group == "allow":          
        	if resnode.status == "DRAFT": 
        			return "allow"    

      elif node.edit_policy == "EDITABLE_NON_MODERATED":
        #condition for groups
        if resnode._type == "Group":
          if ver == "1.1" or (resnode.created_by != request.user.id and not request.user.is_superuser):
            # print "\n version = 1.1\n"
            return "stop"

        if group == "allow":
          # print "\n group = allow\n"
          if resnode.status == "DRAFT": 
            return "allow"


@register.assignment_tag
def get_resource_collection(groupid, resource_type):
  """
  Returns collections of given resource-type belonging to currently selected group

  Arguments:
  groupid -- ObjectId (in string format) of currently selected group
  resource_type -- Type of resource (Page/File) whose collections need to find

  Returns:
  Mongodb's cursor object holding nodes having collections
  """
  try:
    gst = collection.Node.one({'_type': "GSystemType", 'name': unicode(resource_type)})

    res_cur = collection.Node.find({'_type': {'$in': [u"GSystem", u"File"]},
                                    'member_of': gst._id,
                                    'group_set': ObjectId(groupid),
                                    'collection_set': {'$exists': True, '$not': {'$size': 0}}
                                  })
    return res_cur

  except Exception as e:
    error_message = "\n CollectionsFindError: " + str(e) + " !!!\n"
    raise Exception(error_message)


@register.assignment_tag
def get_source_id(obj_id):
  try:
    source_id_at=collection.Node.one({'$and':[{'name':'source_id'},{'_type':'AttributeType'}]})
    att_set=collection.Node.one({'$and':[{'subject':ObjectId(obj_id)},{'_type':'GAttribute'},{'attribute_type.$id':source_id_at._id}]})
    return att_set.object_value
  except Exception as e:
    print str(e)
    return 'null'

 
def get_translation_relation(obj_id, translation_list = [], r_list = []):
	r_list.append(obj_id._id)
	relation_set=obj_id.get_possible_relations(obj_id.member_of)
	if relation_set.has_key('translation_of'):  
		for k,v in relation_set['translation_of'].items():                      
			if k == 'subject_or_right_subject_list':
				for each in v:
					dic={}
					if (each['_id'] not in r_list):
						r_list.append(each['_id'])
						dic[each['_id']]=each['language']
						translation_list.append(dic)
						get_translation_relation(each,translation_list, r_list)
	return translation_list

@register.assignment_tag
def get_possible_translations(obj_id):
	translation_list = []
	r_list1 = []
	return get_translation_relation(obj_id,r_list1,translation_list)



	#code commented in case required for groups not assigned edit_policy        
	#elif group_type is  None:
	#  group=user_access_policy(groupid,request.user)
	#  if group == "allow":
	#   if resnode.status == "DRAFT":
	#      return "allow"
			
	

#textb
@register.filter("mongo_id")
def mongo_id(value):
		 # Retrieve _id value
		if type(value) == type({}):
				if value.has_key('_id'):
						value = value['_id']
	 
		# Return value
		return unicode(str(value))

@register.simple_tag
def check_existence_textObj_mobwrite(node_id):
		'''
	to check object already created or not, if not then create 
	input nodeid 
		'''		
		check = ""
		system = collection.Node.find_one({"_id":ObjectId(node_id)})
		filename = TextObj.safe_name(str(system._id))
		textobj = TextObj.objects.filter(filename=filename)
		if textobj:
			textobj = TextObj.objects.get(filename=filename)
			pass
		else:
			if system.content_org == None:
				content_org = "None"
			else :
		 		content_org = system.content_org
			textobj = TextObj(filename=filename,text=content_org)
			textobj.save()
		check = textobj.filename
		return check
#textb 

@register.assignment_tag
def get_version_of_module(module_id):
	''''
	This method will return version number of module
	'''
	ver_at = collection.Node.one({'_type':'AttributeType','name':'version'})
	if ver_at:
		attr = collection.Triple.one({'_type':'GAttribute','attribute_type.$id':ver_at._id,'subject':ObjectId(module_id)})
		if attr:
			return attr.object_value
		else:
			return ""
	else:
		return ""

@register.assignment_tag
def get_group_name(groupid):
	group_name = ""
	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(groupid) is True :
		group_ins = collection.Node.find_one({'_type': "Group","_id": ObjectId(groupid)})
		if group_ins:
			group_name = group_ins.name
		else :
			auth = collection.Node.one({'_type': 'Author', "_id": ObjectId(groupid) })
			if auth :
				group_name = auth.name

	else :
		pass
	return group_name 

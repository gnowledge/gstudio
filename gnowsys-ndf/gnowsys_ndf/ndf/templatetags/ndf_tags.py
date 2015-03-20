''' -- imports from python libraries -- '''
import re
# import magic
import collections
from time import time
import json
import ox

''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.template import Library
from django.template import RequestContext,loader
from django.shortcuts import render_to_response, render
from mongokit import paginator
from mongokit import IS

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS as setting_gapps, DEFAULT_GAPPS_LIST, META_TYPE, CREATE_GROUP_VISIBILITY, GSTUDIO_SITE_DEFAULT_LANGUAGE
# from gnowsys_ndf.settings import GSTUDIO_SITE_LOGO,GSTUDIO_COPYRIGHT,GSTUDIO_GIT_REPO,GSTUDIO_SITE_PRIVACY_POLICY, GSTUDIO_SITE_TERMS_OF_SERVICE,GSTUDIO_ORG_NAME,GSTUDIO_SITE_ABOUT,GSTUDIO_SITE_POWEREDBY,GSTUDIO_SITE_PARTNERS,GSTUDIO_SITE_GROUPS,GSTUDIO_SITE_CONTACT,GSTUDIO_ORG_LOGO,GSTUDIO_SITE_CONTRIBUTE,GSTUDIO_SITE_VIDEO,GSTUDIO_SITE_LANDING_PAGE
from gnowsys_ndf.settings import *
try:
	from gnowsys_ndf.local_settings import GSTUDIO_SITE_NAME
except ImportError:
	pass

from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import check_existing_group,get_all_gapps,get_all_resources_for_group
from gnowsys_ndf.ndf.views.methods import get_drawers, get_group_name_id, cast_to_data_type
from gnowsys_ndf.mobwrite.models import TextObj
from pymongo.errors import InvalidId as invalid_id
from django.contrib.sites.models import Site

# from gnowsys_ndf.settings import LANGUAGES
# from gnowsys_ndf.settings import GROUP_AGENCY_TYPES,AUTHOR_AGENCY_TYPES

from gnowsys_ndf.ndf.node_metadata_details import schema_dict

register = Library()
at_apps_list = node_collection.one({'_type': 'AttributeType', 'name': 'apps_list'})
translation_set=[]
check=[]



@register.assignment_tag
def get_site_variables():
   site_var={}
   site_var['ORG_NAME']=GSTUDIO_ORG_NAME
   site_var['LOGO']=GSTUDIO_SITE_LOGO
   site_var['COPYRIGHT']=GSTUDIO_COPYRIGHT
   site_var['GIT_REPO']=GSTUDIO_GIT_REPO
   site_var['PRIVACY_POLICY']=GSTUDIO_SITE_PRIVACY_POLICY
   site_var['TERMS_OF_SERVICE']=GSTUDIO_SITE_TERMS_OF_SERVICE
   site_var['ORG_LOGO']=GSTUDIO_ORG_LOGO
   site_var['ABOUT']=GSTUDIO_SITE_ABOUT
   site_var['SITE_POWEREDBY']=GSTUDIO_SITE_POWEREDBY
   site_var['PARTNERS']=GSTUDIO_SITE_PARTNERS
   site_var['GROUPS']=GSTUDIO_SITE_GROUPS
   site_var['CONTACT']=GSTUDIO_SITE_CONTACT
   site_var['CONTRIBUTE']=GSTUDIO_SITE_CONTRIBUTE
   site_var['SITE_VIDEO']=GSTUDIO_SITE_VIDEO
   site_var['LANDING_PAGE']=GSTUDIO_SITE_LANDING_PAGE
   site_var['HOME_PAGE']=GSTUDIO_SITE_HOME_PAGE

   return  site_var


@register.assignment_tag
def get_author_agency_types():
   return AUTHOR_AGENCY_TYPES


@register.assignment_tag
def get_group_agency_types():
   return GROUP_AGENCY_TYPES


@register.assignment_tag
def get_node_type(node):
   if node:
      obj = node_collection.find_one({"_id": ObjectId(node._id)})
      nodetype=node.member_of_names_list[0]
      return nodetype
   else:
      return ""


@register.assignment_tag
def get_node(node):
    if node:
        obj = node_collection.one({"_id": ObjectId(node)})
        if obj:
            return obj
        else:
            return ""


@register.assignment_tag
def get_schema(node):
   obj = node_collection.find_one({"_id": ObjectId(node.member_of[0])}, {"name": 1})
   nam=node.member_of_names_list[0]
   if(nam == 'Page'):
        return [1,schema_dict[nam]]
   elif(nam=='File'):
	if( 'image' in node.mime_type):
		return [1,schema_dict['Image']]
        elif('video' in node.mime_type or 'Pandora_video' in node.mime_type):
        	return [1,schema_dict['Video']]
	else:
		return [1,schema_dict['Document']]	
   else:
	return [0,""]


@register.filter
def is_Page(node):
	Page = node_collection.one({"_type": "GSystemType", "name": "Page"})
	if(Page._id in node.member_of):
		return 1
	else:
		return 0


@register.filter
def is_Quiz(node):
	Quiz = node_collection.one({"_type": "GSystemType", "name": "Quiz"})
	if(Quiz._id in node.member_of):
		return 1
	else:
		return 0


@register.filter
def is_File(node):
	File = node_collection.one({"_type": "GSystemType", "name": "File"})
	if(File._id in node.member_of):
		return 1
	else:
		return 0


@register.inclusion_tag('ndf/userpreferences.html')
def get_user_preferences(group,user):
	return {'groupid':group,'author':user}


@register.assignment_tag
def get_languages():
        return LANGUAGES


@register.assignment_tag
def get_node_ratings(request,node):
        try:
                user=request.user
                node = node_collection.one({'_id': ObjectId(node._id)})
                sum=0
                dic={}
                cnt=0
                userratng=0
                tot_ratng=0
                for each in node.rating:
                     if each['user_id'] == user.id:
                             userratng=each['score']
                     if each['user_id']==0:
                             cnt=cnt+1
                     sum=sum+each['score']
                if len(node.rating)==1 and cnt==1:
                        tot_ratng=0
                        avg_ratng=0.0
                else:
                        if node.rating:
                           tot_ratng=len(node.rating)-cnt
                        if tot_ratng:
                           avg_ratng=float(sum)/tot_ratng
                        else:
                           avg_ratng=0.0
                dic['avg']=avg_ratng
                dic['tot']=tot_ratng
                dic['user_rating']=userratng
                return dic
        except Exception as e:
                print "Error in get_node_ratings "+str(e)


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
	sitename = Site.objects.all()[0].name.__str__()
	return sitename


@register.assignment_tag
def check_gapp_menus(groupid):
	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(groupid) is False :
		group_ins = node_collection.find_one({'_type': "Group", "name": groupid}) 
		if group_ins:
			groupid = str(group_ins._id)
	else :
		pass
	grp = node_collection.one({'_id': ObjectId(groupid)})
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
		grp = node_collection.one({'_id': ObjectId(groupid)})
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
			gpid = node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
			gapps = {}
			i = 0;
			meta_type = node_collection.one({'$and':[{'_type':'MetaType'},{'name': META_TYPE[0]}]})
			GAPPS = node_collection.find({'$and':[{'_type':'GSystemType'},{'member_of':{'$all':[meta_type._id]}}]}).sort("created_at")
			group_obj = node_collection.one({'_id':ObjectId(groupid)})

			# Forcefully setting GAPPS (Image, Video & Group) to be hidden from group(s)
			not_in_menu_bar = []
			if group_obj.name == "home":
				# From "home" group hide following GAPPS: Image, Video
				not_in_menu_bar = ["Image", "Video"]
			else :
				# From other remaining groups hide following GAPPS: Group, Image, Video
				not_in_menu_bar = ["Image", "Video", "Group"]

			# Defalut GAPPS to be listed on gapps-meubar/gapps-iconbar
			global DEFAULT_GAPPS_LIST
			if not DEFAULT_GAPPS_LIST:
				# If DEFAULT_GAPPS_LIST is empty, set bulit-in GAPPS (setting_gapps) list from settings file
				DEFAULT_GAPPS_LIST = setting_gapps

			for node in GAPPS:
				if node:
					if node.name not in not_in_menu_bar and node.name in DEFAULT_GAPPS_LIST:
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
		grp = node_collection.one({'_id':ObjectId(group_id)})
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
		group = node_collection.one({'_id':ObjectId(group_id)})
		if req_user_id in group.author_set and group.group_type == 'PUBLIC':
			ret_policy=True
		return ret_policy
	except Exception as ex:
		print "Exception in switch_group_conditions"+str(ex)


@register.assignment_tag
def get_all_user_groups():
	try:
		all_groups = node_collection.find({'_type':'Author'}).sort('name', 1)
		return list(all_groups)
	except:
		print "Exception in get_all_user_groups"


@register.assignment_tag
def get_group_object(group_id = None):
	try:
		if group_id == None :
			group_object = node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
		else:
			group_object = node_collection.one({'_id':ObjectId(group_id)})
		return group_object
	except invalid_id:
		group_object = node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
		return group_object


@register.assignment_tag
def get_states_object(request):
   group_object = node_collection.one({'$and':[{'_type':u'Group'},{'name':u'State Partners'}]})
   return group_object


@register.simple_tag
def get_all_users_to_invite():
	try:
		inv_users = {}
		users = User.objects.all()
		for each in users:
			inv_users[each.username.__str__()] = each.id.__str__()
		return str(inv_users)
	except Exception as e:
		print str(e)


@register.assignment_tag
def get_all_users_int_count():
	'''
	get integer count of all the users
	'''
	all_users = len(User.objects.all())
	return all_users

@register.inclusion_tag('ndf/twist_replies.html')
def get_reply(thread,parent,forum,token,user,group_id):
	return {'thread':thread,'reply': parent,'user':user,'forum':forum,'csrf_token':token,'eachrep':parent,'groupid':group_id}


@register.assignment_tag
def get_all_replies(parent):
	 ex_reply=""
	 if parent:
		 ex_reply = node_collection.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(parent._id)}],'status':{'$nin':['HIDDEN']}})
		 ex_reply.sort('created_at',-1)
	 return ex_reply


@register.assignment_tag
def get_metadata_values():

	metadata = {"educationaluse": GSTUDIO_RESOURCES_EDUCATIONAL_USE, "interactivitytype": GSTUDIO_RESOURCES_INTERACTIVITY_TYPE, "curricular": GSTUDIO_RESOURCES_CURRICULAR,
				"educationallevel": GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL, "educationalsubject": GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT, "language": GSTUDIO_RESOURCES_LANGUAGES,
				"timerequired": GSTUDIO_RESOURCES_TIME_REQUIRED, "audience": GSTUDIO_RESOURCES_AUDIENCE , "textcomplexity": GSTUDIO_RESOURCES_TEXT_COMPLEXITY,
				"age_range": GSTUDIO_RESOURCES_AGE_RANGE ,"readinglevel": GSTUDIO_RESOURCES_READING_LEVEL, "educationalalignment": GSTUDIO_RESOURCES_EDUCATIONAL_ALIGNMENT}
	return metadata


@register.assignment_tag
def get_attribute_value(node_id, attr):

	node_attr = None
	if node_id:
		node = node_collection.one({'_id': ObjectId(node_id) })
		gattr = node_collection.one({'_type': 'AttributeType', 'name': unicode(attr) })
        # print "node: ",node.name,"\n"
        # print "attr: ",attr,"\n"

		if node and gattr:
			node_attr = triple_collection.one({'_type': "GAttribute", "subject": node._id, 'attribute_type.$id': gattr._id})	

	if node_attr:
		attr_val = node_attr.object_value
	else:
		attr_val = ""

	# print "attr_val: ",attr_val,"\n"
	return attr_val


@register.inclusion_tag('ndf/drawer_widget.html')
def edit_drawer_widget(field, group_id, node=None, page_no=1, checked=None, **kwargs):
	drawers = None
	drawer1 = None
	drawer2 = None

	# Special case used while dealing with RelationType widget
	left_drawer_content = None
	paged_resources = ""
	if node:
		if field == "collection":
			if checked == "Quiz":
				checked = "QuizItem"
			elif checked == "Theme":
				checked = "Theme"
			else:
				checked = None
			drawers, paged_resources = get_drawers(group_id, node._id, node.collection_set, checked)

		elif field == "prior_node":
			checked = None
			drawers, paged_resources = get_drawers(group_id, node._id, node.prior_node, checked)

		elif field == "module":
			checked = "Module"
			drawers, paged_resources = get_drawers(group_id, node._id, node.collection_set, checked)

		elif field == "RelationType" or field == "CourseUnits":
			# Special case used while dealing with RelationType widget
			if kwargs.has_key("left_drawer_content"):
				widget_for = checked
				checked = field
				field = widget_for
				left_drawer_content = kwargs["left_drawer_content"]

				drawers = get_drawers(group_id, nid=node["_id"], nlist=node[field], checked=checked, left_drawer_content=left_drawer_content)
		
		drawer1 = drawers['1']
		drawer2 = drawers['2']

	else:
		if field == "collection" and checked == "Quiz":
			checked = "QuizItem"

		elif field == "collection" and checked == "Theme":
			checked = "Theme"
			
		elif field == "module":
			checked = "Module"

		elif field == "RelationType" or field == "CourseUnits":
			# Special case used while dealing with RelationType widget
			if kwargs.has_key("left_drawer_content"):
				widget_for = checked
				checked = field
				field = widget_for
				left_drawer_content = kwargs["left_drawer_content"]
		else:
			# To make the collection work as Heterogenous one, by default
			checked = None

		if checked == "RelationType" or checked == "CourseUnits" :
			drawer1 = get_drawers(group_id, checked=checked, left_drawer_content=left_drawer_content)
		else:
			drawer1, paged_resources = get_drawers(group_id, page_no=page_no, checked=checked)

	return {'template': 'ndf/drawer_widget.html', 
					'widget_for': field, 'drawer1': drawer1, 'drawer2': drawer2, 'page_info': paged_resources, 
					'is_RT': checked, 'group_id': group_id, 'groupid': group_id
				}


@register.inclusion_tag('tags/dummy.html')
def list_widget(fields_name, fields_type, fields_value, template1='ndf/option_widget.html',template2='ndf/drawer_widget.html'):
	drawer1 = {}
	drawer2 = None
	groupid = ""
	group_obj = node_collection.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})

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
			drawer = node_collection.find({"_type":types})
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
			for each in node_collection.find({"_type": types}):
				if fields_value_id_list:
					if each._id not in fields_value_id_list:
						drawer1[each._id] = each.name
				else:
					drawer1[each._id] = each.name

		if types in ["all_types"]:
			for each in alltypes:
				for eachnode in node_collection.find({"_type": each}):
					if fields_value_id_list:
						if eachnode._id not in fields_value_id_list:
							drawer1[eachnode._id] = eachnode.name
					else:
						drawer1[eachnode._id] = eachnode.name

		if fields_value_id_list:
			drawer2 = []
			for each_id in fields_value_id_list:
				each_node = node_collection.one({'_id': each_id})
				if each_node:
					drawer2.append(each_node)

		return {'template': template2, 'widget_for': fields_name, 'drawer1': drawer1, 'drawer2': drawer2, 'group_id': groupid, 'groupid': groupid}


@register.assignment_tag
def shelf_allowed(node):
	page_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Page'})
	file_GST = node_collection.one({'_type': 'GSystemType', 'name': 'File'})
	course_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Course'})
	quiz_GST= node_collection.one({'_type': 'GSystemType', 'name': 'Quiz'})
	topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})

	allowed_list = [page_GST._id,file_GST._id,course_GST._id,quiz_GST._id,topic_GST._id]
	if node:
		for each in node.member_of:
			if each in allowed_list :
				allowed = "True"
				return allowed


# This function is a duplicate of get_gapps_menubar and modified for the gapps_iconbar.html template to shows apps in the sidebar instead
@register.inclusion_tag('ndf/gapps_iconbar.html')
def get_gapps_iconbar(request, group_id):
	"""Get Gapps menu-bar
	"""
	try:
		selectedGapp = request.META["PATH_INFO"]
		group_name = ""
		gpid = node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
		gapps = {}
		i = 0;
		meta_type = node_collection.one({'$and':[{'_type':'MetaType'},{'name': META_TYPE[0]}]})
		
		GAPPS = node_collection.find({'$and':[{'_type':'GSystemType'},{'member_of':{'$all':[meta_type._id]}}]}).sort("created_at")
		group_obj = node_collection.one({'_id':ObjectId(group_id)})

		# Forcefully setting GAPPS (Image, Video & Group) to be hidden from group(s)
		not_in_menu_bar = []
		if group_obj.name == "home":
			# From "home" group hide following GAPPS: Image, Video
			not_in_menu_bar = ["Image", "Video"]
		else :
			# From other remaining groups hide following GAPPS: Group, Image, Video
			not_in_menu_bar = ["Image", "Video", "Group"]

		# Defalut GAPPS to be listed on gapps-meubar/gapps-iconbar
		global DEFAULT_GAPPS_LIST
		if not DEFAULT_GAPPS_LIST:
			# If DEFAULT_GAPPS_LIST is empty, set bulit-in GAPPS (setting_gapps) list from settings file
			DEFAULT_GAPPS_LIST = setting_gapps

		for node in GAPPS:
			#node = node_collection.one({'_type': 'GSystemType', 'name': app, 'member_of': {'$all': [meta_type._id]}})
			if node:
				if node.name not in not_in_menu_bar and node.name in DEFAULT_GAPPS_LIST:
					i = i+1;
					gapps[i] = {'id': node._id, 'name': node.name.lower()}

		if len(selectedGapp.split("/")) > 2 :
			selectedGapp = selectedGapp.split("/")[2]
		else :
			selectedGapp = selectedGapp.split("/")[1]
		if group_id == None:
			group_id=gpid._id
		group_obj=node_collection.one({'_id':ObjectId(group_id)})
		if not group_obj:
			group_id=gpid._id
		else :
			group_name = group_obj.name

		return {'template': 'ndf/gapps_iconbar.html', 'request': request, 'gapps': gapps, 'selectedGapp':selectedGapp,'groupid':group_id, 'group_name':group_name}
	except invalid_id:
		gpid=node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
		group_id=gpid._id
		return {'template': 'ndf/gapps_iconbar.html', 'request': request, 'gapps': gapps, 'selectedGapp':selectedGapp,'groupid':group_id}


@register.assignment_tag
def get_nroer_menu(request, group_name):

	gapps = GSTUDIO_NROER_GAPPS

	url_str = request.META["PATH_INFO"]
	url_split = url_str.split("/")

	# removing "" in the url_split
	url_split = filter(lambda x: x != "", url_split)
	# print "url_split : ", url_split

	nroer_menu_dict = {}
	top_menu_selected = ""

	if (len(url_split) > 1) and (url_split[1] != "dashboard"):
		selected_gapp = url_split[1]  # expecting e-library etc. type of extract

		# handling conditions of "e-library" = "file" and vice-versa.
		selected_gapp = "e-library" if (selected_gapp == "file") else selected_gapp

		# for deciding/confirming selected gapp
		for each_gapp in gapps:
			temp_val = each_gapp.values()[0]
			if temp_val == selected_gapp:
				nroer_menu_dict["selected_gapp"] = temp_val
				break

		# print "selected_gapp : ", selected_gapp

	mapping = GSTUDIO_NROER_MENU_MAPPINGS

	# deciding "top level menu selection"
	if (group_name == "home") and nroer_menu_dict.has_key("selected_gapp"):
		top_menu_selected = "Repository"
		
	elif group_name in mapping.values():
		sub_menu_selected = mapping.keys()[mapping.values().index(group_name)]  # get key of/from mapping
		nroer_menu_dict["sub_menu_selected"] = sub_menu_selected

		# with help of sub_menu_selected get it's parent from GSTUDIO_NROER_MENU
		top_menu_selected = [i.keys()[0] for i in GSTUDIO_NROER_MENU[1:] if sub_menu_selected in i.values()[0]][0]
		
		# for Partners, "Curated Zone" should not appear
		gapps = gapps[1:] if (top_menu_selected in ["Partners", "Groups"]) else gapps
		
	elif (len(url_split) >= 3) and ("nroer_groups" in url_split) and (url_split[2] in [i.keys()[0] for i in GSTUDIO_NROER_MENU[1:]]):
		top_menu_selected = url_split[2]
		gapps = ""
	# elif - put this for sub groups. Needs to fire queries etc. for future perspective.

	nroer_menu_dict["gapps"] = gapps
	nroer_menu_dict["top_menu_selected"] = top_menu_selected
	nroer_menu_dict["mapping"] = mapping
	nroer_menu_dict["top_menus"] = GSTUDIO_NROER_MENU[1:]

	# print "nroer_menu_dict : ", nroer_menu_dict
	return nroer_menu_dict
# ---------- END of get_nroer_menu -----------


@register.assignment_tag
def get_site_name_from_settings():
	# print "GSTUDIO_SITE_NAME : ", GSTUDIO_SITE_NAME
	print "site name",GSTUDIO_SITE_NAME
	return GSTUDIO_SITE_NAME


global_thread_rep_counter = 0	# global variable to count thread's total reply
global_thread_latest_reply = {"content_org":"", "last_update":"", "user":""}
def thread_reply_count( oid ):
	'''
	Method to count total replies for the thread.
	'''
	thr_rep = node_collection.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(oid)}],'status':{'$nin':['HIDDEN']}})
	global global_thread_rep_counter		# to acces global_thread_rep_counter as global and not as local, 
	global global_thread_latest_reply

	if thr_rep and (thr_rep.count() > 0):
		for each in thr_rep:

			global_thread_rep_counter += 1

			if not global_thread_latest_reply["content_org"]:
				global_thread_latest_reply["content_org"] = each.content_org
				global_thread_latest_reply["last_update"] = each.last_update
				global_thread_latest_reply["user"] = User.objects.get(pk=each.created_by).username
			else:
				if global_thread_latest_reply["last_update"] < each.last_update:
					global_thread_latest_reply["content_org"] = each.content_org
					global_thread_latest_reply["last_update"] = each.last_update
					global_thread_latest_reply["user"] = User.objects.get(pk=each.created_by).username
					
			thread_reply_count(each._id)
	
	return global_thread_rep_counter


# To get all the discussion replies
# global variable to count thread's total reply
# global_disc_rep_counter = 0	
# global_disc_all_replies = []
reply_st = node_collection.one({ '_type':'GSystemType', 'name':'Reply'})
@register.assignment_tag
def get_disc_replies( oid, group_id, global_disc_all_replies, level=1 ):
	'''
	Method to count total replies for the disc.
	'''

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False:
		group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        # auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
		if group_ins:
			group_id = str(group_ins._id)
		else:
			auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
			if auth :
				group_id = str(auth._id)
	else:
		pass

	# thr_rep = node_collection.find({'$and':[ {'_type':'GSystem'}, {'prior_node':ObjectId(oid)}, {'member_of':ObjectId(reply_st._id)} ]})#.sort({'created_at': -1})
	thr_rep = node_collection.find({'_type':'GSystem', 'group_set':ObjectId(group_id), 'prior_node':ObjectId(oid), 'member_of':ObjectId(reply_st._id)}).sort('created_at', -1)

	# to acces global_disc_rep_counter as global and not as local
	# global global_disc_rep_counter 
	# global global_disc_all_replies

	if thr_rep and (thr_rep.count() > 0):

		for each in thr_rep:

			# print "\n\n",each.created_at
			# if level == 1:
			# 	global_disc_all_replies = temp_list + global_disc_all_replies
			# 	temp_list = []

			# global_disc_rep_counter += 1
			temp_disc_reply = {"content":"", "last_update":"", "user":"", "oid":"", "prior_node":""}

			temp_disc_reply["HTMLcontent"] = each.content
			temp_disc_reply["ORGcontent"] = each.content_org
			temp_disc_reply["last_update"] = each.last_update
			temp_disc_reply["username"] = User.objects.get(pk=each.created_by).username
			temp_disc_reply["userid"] = int(each.created_by)
			temp_disc_reply["oid"] = str(each._id)
			temp_disc_reply["prior_node"] = str(each.prior_node[0])
			temp_disc_reply["level"] = level

			# to avoid redundancy of dicts, it checks if any 'oid' is not equals to each._id. Then only append to list
			if not any( d['oid'] == str(each._id) for d in global_disc_all_replies ):
				if type(global_disc_all_replies) == str:
					global_disc_all_replies = list(global_disc_all_replies)
				global_disc_all_replies.append(temp_disc_reply)
				# global_disc_all_replies.insert(0, temp_disc_reply)
				# temp_list.append(temp_disc_reply)
				# print "\n\n", temp_list
								
			# print "\n\n---- : ", level, " : ", each.content_org, temp_disc_reply
			# get_disc_replies(each._id, (level+1), temp_list)
			get_disc_replies(each._id, group_id, global_disc_all_replies, (level+1) )
	
	# print global_disc_all_replies
	return global_disc_all_replies
# global_disc_all_replies = []
	

@register.assignment_tag
def get_forum_twists(forum):
	ret_replies = []
	exstng_reply = node_collection.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(forum._id)}],'status':{'$nin':['HIDDEN']}})
	exstng_reply.sort('created_at')
	global global_thread_rep_counter 		# to acces global global_thread_rep_counter and reset it to zero
	global global_thread_latest_reply
	# for loop to get count of each thread's total reply
	for each in exstng_reply:
		global_thread_rep_counter = 0		# reset global_thread_rep_counter to zero
		global_thread_latest_reply = {"content_org":"", "last_update":"", "user":""}

		# as each thread is dict, adding one more field of thread_reply_count
		each['thread_reply_count'] = thread_reply_count(each._id)
		each['latest_reply'] = global_thread_latest_reply
		ret_replies.append(each)
	return ret_replies
lp=[]


def get_rec_objs(ob_id):
	lp.append(ob_id)
	exstng_reply = node_collection.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(ob_id)}]})
	for each in exstng_reply:
		get_rec_objs(each)
	return lp


@register.assignment_tag
def get_twist_replies(twist):
	ret_replies={}
	entries=[]
	exstng_reply = node_collection.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(twist._id)}]})
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
	if group_id == '/home/'or group_id == "":
		colg = node_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
	else:
		colg = node_collection.one({'_id':ObjectId(group_id)})
	if colg:
		if colg.created_by == user_id:
			return "author"
		if colg.author_set:
			if user_id in colg.group_admin or user_id in colg.author_set:
				return "joined"
			else:
				return "not"
		else:
			return "not"
	else:
		return "nullobj"
	

@register.assignment_tag
def check_group(group_id):
	if group_id:
		fl = check_existing_group(group_id)
		return fl
	else:
		return ""


@register.assignment_tag
def get_existing_groups():
	group = []
	colg = node_collection.find({'_type': u'Group'})
	colg.sort('name')
	gr = list(colg)
	for items in gr:
		if items.name:
			group.append(items)
	return group


@register.assignment_tag
def get_existing_groups_excluding_username():
	group = []
	user_list=[]
	users=User.objects.all()
	for each in users:
		user_list.append(each.username)
	colg = node_collection.find({'$and':[{'_type': u'Group'},{'name':{'$nin':user_list}}]})
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
  group_cur = node_collection.find({'_type':u"Group", 'name': {'$nin': [u"home", grname]}, 'group_type': "PUBLIC"}).sort('last_update', -1).limit(10)

  if group_cur.count() <= 0:
    return "None"

  return group_cur


@register.assignment_tag
def get_group_policy(group_id,user):
	try:
		policy = ""
		colg = node_collection.one({'_id':ObjectId(group_id)})
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
  
  group_cur = node_collection.find({'_type': "Group", 'name': {'$nin': ["home", selected_group_name]}, 
  									'$or': [{'group_admin': user.id}, {'author_set': user.id}],
  								}).sort('last_update', -1).limit(9)

  auth_group = node_collection.one({'_type': "Author", '$and': [{'name': unicode(user.username)}, {'name': {'$ne': selected_group_name}}]})

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
def get_profile_pic(user_pk):
    """
    This returns file document if exists, otherwise None value.
    """
    profile_pic_image = None
    ID = int(user_pk)
    auth = node_collection.one({'_type': "Author", 'created_by': ID}, {'_id': 1, 'relation_set': 1})

    if auth:
        for each in auth.relation_set:
            if "has_profile_pic" in each:
                profile_pic_image = node_collection.one(
                    {'_type': "File", '_id': each["has_profile_pic"][0]}
                )

                break

    return profile_pic_image


@register.assignment_tag
def get_theme_node(groupid, node):

	topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
	theme_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Theme'})
	theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item'})

	# code for finding nodes collection has only topic instances or not
	# It checks if first element in collection is theme instance or topic instance accordingly provide checks
	if node.collection_set:
		collection_nodes = node_collection.one({'_id': ObjectId(node.collection_set[0]) })
		if theme_GST._id in collection_nodes.member_of:
			return "Theme_Enabled"
		if theme_item_GST._id in collection_nodes.member_of:
			return "Theme_Item_Enabled"
		if topic_GST._id in collection_nodes.member_of:
			return "Topic_Enabled"
		
	else:
		return True


# @register.assignment_tag
# def get_group_name(val):
#          GroupName = []

# 	 for each in val.group_set: 

# 		grpName = node_collection.one({'_id': ObjectId(each) }).name.__str__()
# 		GroupName.append(grpName)
# 	 return GroupName


@register.assignment_tag
def get_edit_url(groupid):

	node = node_collection.one({'_id': ObjectId(groupid) }) 
	if node._type == 'GSystem':

		type_name = node_collection.one({'_id': node.member_of[0]}).name
                
		if type_name == 'Quiz':
			return 'quiz_edit'    
		elif type_name == 'Page':
			return 'page_create_edit' 
		elif type_name == 'Term':
			return 'term_create_edit' 
		elif type_name == 'Theme' or type_name == 'Topic':
			return 'theme_topic_create'
		elif type_name == 'QuizItem':
			return 'quiz_item_edit'
                elif type_name == 'Forum':
                        return 'edit_forum'
                elif type_name == 'Twist' or type_name == 'Thread':
                        return 'edit_thread'


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
def get_event_type(node):
    event = node_collection.one({'_id':{'$in':node.member_of}})
    return event._id


@register.assignment_tag
def get_url(groupid):
     
    node = node_collection.one({'_id': ObjectId(groupid) }) 
    
    if node._type == 'GSystem':

		type_name = node_collection.one({'_id': node.member_of[0]})
                if type_name.name == 'Exam' or type_name.name == "Classroom Session":
                   return ('event_app_instance_detail')
                if type_name.name == 'Quiz':
                   return 'quiz_details'
                elif type_name.name == 'Page':
                   return 'page_details' 
                elif type_name.name == 'Theme' or type_name == 'theme_item':
                   return 'theme_page'
                elif type_name.name == 'Forum':
	                 return 'show'
                elif type_name.name == 'Task' or type_name.name == 'task_update_history':
	                 return 'task_details'
                else:
	                  return 'None'    
    elif node._type == 'Group' :
                    return 'group'
    elif node._type == 'File':
		if (node.mime_type) == ("application/octet-stream"): 
			return 'video_detail'       
		elif 'image' in node.mime_type:
			return 'file_detail'
		else:
			return 'file_detail'
    else:
			return 'group'


@register.assignment_tag
def get_create_url(groupid):

  node = node_collection.one({'_id': ObjectId(groupid) }) 
  if node._type == 'GSystem':

    type_name = node_collection.one({'_id': node.member_of[0]}).name

    if type_name == 'Quiz':
      return 'quiz_create'    
    elif type_name == 'Page':
      return 'page_create_edit' 
    elif type_name == 'Term':
      return 'term_create_edit' 
    elif type_name == 'Theme' or type_name == 'Topic':
		return 'theme_topic_create'
    elif type_name == 'QuizItem':
      return 'quiz_item_create'

  elif node._type == 'Group' or node._type == 'Author' :
    return 'create_group'

  elif node._type == 'File':
    return 'uploadDoc'
	

@register.assignment_tag
def get_prior_node(node_id):

	obj = node_collection.one({'_id':ObjectId(node_id) })
	prior = []
	topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
	if topic_GST._id in obj.member_of:

		if obj.prior_node:
			for each in obj.prior_node:
				node = node_collection.one({'_id': ObjectId(each) })
				prior.append(( node._id , node.name ))

		return prior

	return prior


@register.assignment_tag
def get_contents(node_id, selected, choice):

	contents = {}
	image_contents = []
	video_contents = []
	document_contents = []
	page_contents = []
	audio_contents = []
	interactive_contents = []
	name = ""
	ob_id = ""

	obj = node_collection.one({'_id': ObjectId(node_id) })

	RT_teaches = node_collection.one({'_type':'RelationType', 'name': 'teaches'})
	RT_translation_of = node_collection.one({'_type':'RelationType','name': 'translation_of'})

	# "right_subject" is the translated node hence to find those relations which has translated nodes with RT 'translation_of'
	# These are populated when translated topic clicked.
	trans_grelations = triple_collection.find({'_type':'GRelation','right_subject':obj._id,'relation_type.$id':RT_translation_of._id })               
	# If translated topic then, choose its subject value since subject value is the original topic node for which resources are attached with RT teaches. 
	if trans_grelations.count() > 0:
		obj = node_collection.one({'_id': ObjectId(trans_grelations[0].subject)})

	# If no translated topic then, take the "obj" value mentioned above which is original topic node for which resources are attached with RT teaches
	list_grelations = triple_collection.find({'_type': 'GRelation', 'right_subject': obj._id, 'relation_type.$id': RT_teaches._id })

	for rel in list_grelations:
		rel_obj = node_collection.one({'_id': ObjectId(rel.subject)})

		if rel_obj._type == "File":
			gattr = node_collection.one({'_type': 'AttributeType', 'name': u'educationaluse'})
			# list_gattr = triple_collection.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id, "subject":rel_obj._id, 'object_value': selected })
			list_gattr = triple_collection.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id, "subject":rel_obj._id })

			for attr in list_gattr:
				left_obj = node_collection.one({'_id': ObjectId(attr.subject) })
				
				if selected and left_obj and selected != "language":
					AT = node_collection.one({'_type':'AttributeType', 'name': unicode(selected) })
					att = cast_to_data_type(choice, AT.data_type)
					attr_dict = {unicode(selected): att}

					for m in left_obj.attribute_set:
						if attr_dict == m:

							name = str(left_obj.name)
							ob_id = str(left_obj._id)

							if attr.object_value == "Images":
								image_contents.append((name, ob_id))
							elif attr.object_value == "Videos":
								video_contents.append((name, ob_id))
							elif attr.object_value == "Audios":
								audio_contents.append((name, ob_id))
							elif attr.object_value == "Interactives":
								interactive_contents.append((name, ob_id))
							elif attr.object_value == "Documents":
								document_contents.append((name, ob_id))

				else:
					if not selected or choice == left_obj.language:
						name = str(left_obj.name)
						ob_id = str(left_obj._id)

						if attr.object_value == "Images":
							image_contents.append((name, ob_id))
						elif attr.object_value == "Videos":
							video_contents.append((name, ob_id))
						elif attr.object_value == "Audios":
							audio_contents.append((name, ob_id))
						elif attr.object_value == "Interactives":
							interactive_contents.append((name, ob_id))
						elif attr.object_value == "Documents":
							document_contents.append((name, ob_id))

							
	if image_contents:
		contents['Images'] = image_contents
	
	if video_contents:
		contents['Videos'] = video_contents

	if audio_contents:
		contents['Audios'] = audio_contents		
	
	if document_contents:
		contents['Documents'] = document_contents
	
	if interactive_contents:
		contents['Interactives'] = interactive_contents
	
	# print "\n",contents,"\n"
	return contents
	

@register.assignment_tag
def get_teaches_list(node):
	
	teaches_list = []
	if node:
		relationtype = node_collection.one({"_type":"RelationType","name":"teaches"})
        list_grelations = triple_collection.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
        for relation in list_grelations:
        	obj = node_collection.one({'_id': ObjectId(relation.right_subject) })
          	teaches_list.append(obj)

	return teaches_list


@register.assignment_tag
def get_assesses_list(node):
	
	assesses_list = []
	if node:
		relationtype = node_collection.one({"_type":"RelationType","name":"assesses"})
        list_grelations = triple_collection.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
        for relation in list_grelations:
        	obj = node_collection.one({'_id': ObjectId(relation.right_subject) })
          	assesses_list.append(obj)

	return assesses_list


@register.assignment_tag
def get_group_type(group_id, user):
    """This function checks for url's authenticity

    """
    try:
        # Splitting url-content based on backward-slashes
        split_content = group_id.strip().split("/")
        
        # Holds primary key, group's ObjectId or group's name
        g_id = ""
        if split_content[0] != "":
            g_id = split_content[0]
        else:
            g_id = split_content[1]

        group_node = None

        if g_id.isdigit() and 'dashboard' in group_id:
            # User Dashboard url found
            u_id = int(g_id)
            user_obj = User.objects.get(pk=u_id)

            if not user_obj.is_active:
                error_message = "\n Something went wrong: Either url is invalid or such group/user doesn't exists !!!\n"
                raise Http404(error_message)

        else:
            # Group's url found
            if ObjectId.is_valid(g_id):
                # Group's ObjectId found
                group_node = node_collection.one({'_type': {'$in': ["Group", "Author"]}, '_id': ObjectId(g_id)})

            else:
                # Group's name found
                group_node = node_collection.one({'_type': {'$in': ["Group", "Author"]}, 'name': g_id})

            if group_node:
                # Check whether Group is PUBLIC or not
                if not group_node.group_type == u"PUBLIC":
                    # If Group other than Public one is found

                    if user.is_authenticated():
                        # Check for user's authenticity & accessibility of the group
                        if user.is_superuser or group_node.created_by == user.id or user.id in group_node.group_admin or user.id in group_node.author_set:
                            pass

                        else:
                            error_message = "\n Something went wrong: Either url is invalid or such group/user doesn't exists !!!\n"
                            raise Http404(error_message)

                    else:
                        # Anonymous user found which cannot access groups other than Public
                        error_message = "\n Something went wrong: Either url is invalid or such group/user doesn't exists !!!\n"
                        raise Http404(error_message)

            else:
                # If Group is not found with either given ObjectId or name in the database
                # Then compare with a given list of names as these were used in one of the urls
                # And still no match found, throw error
                if g_id not in ["online", "i18n", "raw", "r", "m", "t", "new", "mobwrite", "admin", "benchmarker", "accounts", "Beta", "welcome"]:
                    error_message = "\n Something went wrong: Either url is invalid or such group/user doesn't exists !!!\n"
                    raise Http404(error_message)

        return True

    except Exception as e:
        raise Http404(e)


@register.assignment_tag
def check_accounts_url(url_path):
	'''
	Checks whether the given path is of accounts related or not
	Accounts means regarding account's registrtion/activation, 
	login/logout or password-reset and all!

	Arguments:
	path -- Visited url by the user taken from request object

	Returns:
	A boolean value indicating the same
	'''
	if "accounts" in url_path and "/group" not in url_path:
		return True

	else:
		return False


'''this template function is used to get the user object from template''' 
@register.assignment_tag 
def get_user_object(user_id):
	user_obj=""
	try:
		user_obj=User.objects.get(id=user_id)
	except Exception as e:
		print "User Not found in User Table",e
	return user_obj


@register.assignment_tag
def get_grid_fs_object(f):
    """
    Get the gridfs object by object id
    """
    grid_fs_obj = ""
    try:
        file_obj = node_collection.one({
            '_id': ObjectId(f['_id'])
        })
        if file_obj.mime_type == 'video':
            if len(file_obj.fs_file_ids) > 2:
                if (file_obj.fs.files.exists(file_obj.fs_file_ids[2])):
                    grid_fs_obj = file_obj.fs.files.get(ObjectId(file_obj.fs_file_ids[2]))
        else:
            grid_fs_obj = file_obj.fs.files.get(file_obj.fs_file_ids[0])
    except Exception as e:
        print "Object does not exist", e

    return grid_fs_obj


@register.inclusion_tag('ndf/admin_class.html')
def get_class_list(group_id,class_name):
	"""Get list of class 
	"""
	class_list = ["GSystem", "File", "Group", "GSystemType", "RelationType", "AttributeType", "MetaType", "GRelation", "GAttribute"]
	return {'template': 'ndf/admin_class.html', "class_list": class_list, "class_name":class_name,"url":"data","groupid":group_id}


@register.inclusion_tag('ndf/admin_class.html')
def get_class_type_list(group_id,class_name):
	"""Get list of class 
	"""
	class_list = ["GSystemType", "RelationType", "AttributeType"]
	return {'template': 'ndf/admin_class.html', "class_list": class_list, "class_name":class_name,"url":"designer","groupid":group_id}


@register.assignment_tag
def get_Object_count(key):
		try:
				return node_collection.find({'_type':key}).count()
		except:
				return 'null'

@register.assignment_tag
def get_memberof_objects_count(key,group_id):
	try:
		return node_collection.find({'member_of': {'$all': [ObjectId(key)]},'group_set': {'$all': [ObjectId(group_id)]}}).count()
	except:
		return 'null'


'''Pass the ObjectId and get the name of it's first member_of element'''
@register.assignment_tag
def get_memberof_name(node_id):
	try:
		node_obj = node_collection.one({'_id': ObjectId(node_id)})
		member_of_name = ""
		if node_obj.member_of:
			member_of_name = node_collection.one({'_id': ObjectId(node_obj.member_of[0]) }).name
		return member_of_name
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
	group_gst = node_collection.one({'_id':ObjectId(groupid)})
	
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
  - Else if user is creator or admin of the group, then he/she is allowed
  - Else if group's edit-policy is "NON_EDITABLE" (currently "home" is such group), then user is NOT allowed
  - Else if user is member of the group, then he/she is allowed
  - Else user is NOT allowed!

  Arguments:
  node -- group's node that is currently selected by the user_access
  user -- user's node that is currently logged-in

  Returns:
  string value (allow/disallow), i.e. whether user is allowed or not!
  """
  user_access = False

  try:
  	# Please make a note, here the order in which check is performed is IMPORTANT!

    if user.is_superuser:
      user_access = True

    else:
      # group_node = node_collection.one({'_type': {'$in': ["Group", "Author"]}, '_id': ObjectId(node)})
      group_name, group_id = get_group_name_id(node)
      group_node = node_collection.one({"_id": ObjectId(group_id)})

      if user.id == group_node.created_by:
        user_access = True

      elif user.id in group_node.group_admin:
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
					 Mod_colg=col_Group.Group.find({'_type':u'Group','_id':{'$in':Post_nodeid}})
                                         Mod_colg=list(Mod_colg)
					 if list(Mod_colg) is not None:
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
def check_is_gstaff(groupid, user):
  """
  Checks whether given user belongs to GStaff.
  GStaff includes only those members which belongs to following criteria:
    1) User should be a super-user (Django's superuser)
    2) User should be a creator of the group (created_by field)
    3) User should be an admin-user of the group (group_admin field)
  
  Other memebrs (author_set field) doesn't belongs to GStaff.

  Arguments:
  groupid -- ObjectId of the currently selected group
  user -- User object taken from request object

  Returns:
  True -- If user is one of them, from the above specified list of categories.
  False -- If above criteria is not met (doesn't belongs to any of the category, mentioned above)!
  """

  try:
    group_node = node_collection.one({'_id': ObjectId(groupid)})

    if group_node:
      return group_node.is_gstaff(user)

    else:
      error_message = "No group exists with this id ("+str(groupid)+") !!!"
      raise Exception(error_message)

  except Exception as e:
    error_message = "\n IsGStaffCheckError: " + str(e) + " \n"
    raise Http404(error_message)


@register.assignment_tag
def check_is_gapp_for_gstaff(groupid, app_dict, user):
    """
    This restricts view of MIS & MIS-PO GApp to only GStaff members
    (super-user, creator, admin-user) of the group.
    That is, other subscribed-members of the group can't even see these GApps.

    Arguments:
    groupid -- ObjectId of the currently selected group
    app_dict -- A dictionary consisting of following key-value pair
                - 'id': ObjectId of the GApp
                - 'name': name of the GApp
    user - User object taken from request object

    Returns:
    A bool value indicating:-
    True --  if user is superuser, creator or admin of the group
    False -- if user is just a subscribed-member of the group
    """

    try:
        if app_dict["name"].lower() in ["mis", "mis-po", "batch"]:
            return check_is_gstaff(groupid, user)

        else:
            return True

    except Exception as e:
        error_message = "\n GroupAdminCheckError (For MIS): " + str(e) + " \n"
        raise Http404(error_message)


@register.assignment_tag
def get_publish_policy(request, groupid, res_node):
	resnode = node_collection.one({"_id": ObjectId(res_node._id)})

	if resnode.status == "DRAFT":
	    
	    # node = node_collection.one({"_id": ObjectId(groupid)})
		
		group_name, group_id = get_group_name_id(groupid)
		node = node_collection.one({"_id": ObjectId(group_id)})

		group_type = group_type_info(groupid)
		group = user_access_policy(groupid,request.user)
		ver = node.current_version

		if request.user.id:
			if group_type == "Moderated":
				base_group=get_prior_post_node(groupid)
				if base_group and (base_group[len(base_group) - 1] is not None):
					if base_group[len(base_group) - 1].status == "DRAFT" or node.status == "DRAFT":
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
    gst = node_collection.one({'_type': "GSystemType", 'name': unicode(resource_type)})

    res_cur = node_collection.find({'_type': {'$in': [u"GSystem", u"File"]},
                                    'member_of': gst._id,
                                    'group_set': ObjectId(groupid),
                                    'collection_set': {'$exists': True, '$not': {'$size': 0}}
                                  })
    return res_cur

  except Exception as e:
    error_message = "\n CollectionsFindError: " + str(e) + " !!!\n"
    raise Exception(error_message)


@register.assignment_tag
def get_all_file_int_count():
	'''
	getting all the file/e-library type resource
	'''
	all_files = node_collection.find({ "_type": "File", "access_policy": "PUBLIC" })
	return all_files.count()


@register.assignment_tag
def app_translations(request, app_dict):
   app_id=app_dict['id']
   get_translation_rt = node_collection.one({'$and':[{'_type':'RelationType'},{'name':u"translation_of"}]})
   if request.LANGUAGE_CODE != GSTUDIO_SITE_DEFAULT_LANGUAGE:
      get_rel = triple_collection.one({'$and':[{'_type':"GRelation"},{'relation_type.$id':get_translation_rt._id},{'subject':ObjectId(app_id)}]})
      if get_rel:
         get_trans=node_collection.one({'_id':get_rel.right_subject})
         if get_trans.language == request.LANGUAGE_CODE:
            return get_trans.name
         else:
            app_name=node_collection.one({'_id':ObjectId(app_id)})
            return app_name.name
      else:
         app_name=node_collection.one({'_id':ObjectId(app_id)})
         return app_name.name
   else:
      app_name=node_collection.one({'_id':ObjectId(app_id)})
      return app_name.name


@register.assignment_tag
def get_preferred_lang(request, group_id, nodes, node_type):
   group = node_collection({'_id':(ObjectId(group_id))})
   get_translation_rt = node_collection.one({'$and':[{'_type':'RelationType'},{'name':u"translation_of"}]})
   uname=node_collection.one({'name':str(request.user.username), '_type': {'$in': ["Group", "Author"]}})
   preferred_list=[]
   primary_list=[]
   default_list=[]
   node=node_collection.one({'_type':'GSystemType','name':node_type,})
   if uname:
      if uname.has_key("preferred_languages"):
		pref_lan=uname.preferred_languages
		if not pref_lan.keys():
			pref_lan={}
			pref_lan['primary']=request.LANGUAGE_CODE
			pref_lan['default']=u"en"
			uname.preferred_languages=pref_lan
			uname.save()   
      else:
         pref_lan={}
         pref_lan['primary']=request.LANGUAGE_CODE
         pref_lan['default']=u"en"
         uname.preferred_languages=pref_lan
         uname.save()
   else:
      pref_lan={}
      pref_lan[u'primary']=request.LANGUAGE_CODE
      pref_lan[u'default']=u"en"
   try:
      for each in nodes:
         get_rel = triple_collection.find({'$and':[{'_type':"GRelation"},{'relation_type.$id':get_translation_rt._id},{'subject':each._id}]})
         if get_rel.count() > 0:
            for rel in list(get_rel):
               rel_node = node_collection.one({'_id':rel.right_subject})
               if rel_node.language == pref_lan['primary']:
                  primary_nodes = node_collection.one({'$and':[{'member_of':node._id},{'group_set':group._id},{'language':pref_lan['primary']},{'_id':rel_node._id}]})
                  if primary_nodes:
                     preferred_list.append(primary_nodes)
                    
               else:
                  default_nodes=node_collection.one({'$and':[{'member_of':node._id},{'group_set':group._id},{'language':pref_lan['default']},{'_id':each._id}]})
                  if default_nodes:
                     preferred_list.append(default_nodes)
              
         elif get_rel.count() == 0:
            default_nodes = node_collection.one({'$and':[{'member_of':node._id},{'group_set':group._id},{'language':pref_lan['default']},{'_id':each._id}]})
            if default_nodes:
               preferred_list.append(default_nodes)
                  
      if preferred_list:
         return preferred_list
      
   except Exception as e:
      return 'error'


# getting video metadata from wetube.gnowledge.org
@register.assignment_tag
def get_pandoravideo_metadata(src_id):
  try:
    api=ox.api.API("http://wetube.gnowledge.org/api")
    data=api.get({"id":src_id,"keys":""})
    mdata=data.get('data')
    return mdata
  except Exception as e:
    return 'null'


@register.assignment_tag
def get_source_id(obj_id):
  try:
    source_id_at = node_collection.one({'$and':[{'name':'source_id'},{'_type':'AttributeType'}]})
    att_set = triple_collection.one({'_type': 'GAttribute', 'subject': ObjectId(obj_id), 'attribute_type.$id': source_id_at._id})
    return att_set.object_value
  except Exception as e:
    return 'null'


def get_translation_relation(obj_id, translation_list = [], r_list = []):
   get_translation_rt = node_collection.one({'$and':[{'_type':'RelationType'},{'name':u"translation_of"}]})
   if obj_id not in r_list:
      r_list.append(obj_id)
      node_sub_rt = triple_collection.find({'$and':[{'_type':"GRelation"},{'relation_type.$id':get_translation_rt._id},{'subject':obj_id}]})
      node_rightsub_rt = triple_collection.find({'$and':[{'_type':"GRelation"},{'relation_type.$id':get_translation_rt._id},{'right_subject':obj_id}]})
      
      if list(node_sub_rt):
         node_sub_rt.rewind()
         for each in list(node_sub_rt):
            right_subject = node_collection.one({'_id':each.right_subject})
            if right_subject._id not in r_list:
               r_list.append(right_subject._id)
      if list(node_rightsub_rt):
         node_rightsub_rt.rewind()
         for each in list(node_rightsub_rt):
            right_subject = node_collection.one({'_id':each.subject})
            if right_subject._id not in r_list:
               r_list.append(right_subject._id)
      if r_list:
         r_list.remove(obj_id)
         for each in r_list:
            dic={}
            node = node_collection.one({'_id':each})
            dic[node._id]=node.language
            translation_list.append(dic)
            get_translation_relation(each,translation_list, r_list)
   return translation_list


# returns object value of attribute 
@register.assignment_tag
def get_object_value(node):
   at_set = ['contact_point','house_street','town_city','state','pin_code','email_id','telephone','website']
   att_name_value= collections.OrderedDict()
           
   for each in at_set:
      attribute_type = node_collection.one({'_type':"AttributeType" , 'name':each}) 
      if attribute_type:
      	get_att = triple_collection.one({'_type':"GAttribute", 'subject':node._id, 'attribute_type.$id': attribute_type._id})
      	if get_att:
        	att_name_value[attribute_type.altnames] = get_att.object_value
         
   return att_name_value


@register.assignment_tag
# return json data of object
def get_json(node):
   node_obj = node_collection.one({'_id':ObjectId(str(node))})
   return json.dumps(node_obj, cls=NodeJSONEncoder, sort_keys = True)  
   

@register.filter("is_in")
# filter added to test if vaiable is inside of list or dict
def is_in(var, args):
    if args is None:
        return False
    arg_list = [arg.strip() for arg in args.split(',')]
    return var in arg_list


@register.filter("del_underscore")
# filter added to remove underscore from string
def del_underscore(var):
   var = var.replace("_"," ")   
   return var 


@register.assignment_tag
# this function used for info-box implementation 
# which convert str to dict type & returns dict which used for rendering in template 
def str_to_dict(str1):
    dict_format = json.loads(str1, object_pairs_hook = collections.OrderedDict)
    keys_to_remove = ('_id','access_policy','rating', 'fs_file_ids', 'content_org', 'content', 'comment_enabled', 'annotations', 'login_required','status','featured','module_set','property_order','url') # keys needs to hide
    keys_by_ids = ('member_of', 'group_set', 'collection_set','prior_node') # keys holds list of ids
    keys_by_userid = ('modified_by', 'contributors', 'created_by', 'author_set') # keys holds dada from User table
    keys_by_dict = ('attribute_set', 'relation_set')
    keys_by_filesize = ('file_size')
    for k in keys_to_remove:
      dict_format.pop(k, None)
    for k, v in dict_format.items():
      if type(dict_format[k]) == list :
          if len(dict_format[k]) == 0:
                  dict_format[k] = "None"
      if k in keys_by_ids:
        name_list = []
        if "None" not in dict_format[k]:
                for ids in dict_format[k]:
                        node = node_collection.one({'_id':ObjectId(ids)})
                        if node:
                                name_list.append(node)
                                dict_format[k] = name_list
              
      if k in keys_by_userid:
       
              if type(dict_format[k]) == list :
                      for userid in dict_format[k]:
                      		  if User.objects.filter(id = userid).exists():
	                              user = User.objects.get(id = userid)
	                              if user:
	                                dict_format[k] = user.get_username()
              else: 
                      if v != [] and v != "None":
                      		  if User.objects.filter(id = userid).exists():
	                              user = User.objects.get(id = v)
	                              if user:
	                                dict_format[k] = user.get_username()

      if k in keys_by_dict:
              att_dic = {}
              if "None" not in dict_format[k]:

                      if type(dict_format[k]) != str and k == "attribute_set":
                      
                              for att in dict_format[k]:
                                      for k1, v1 in att.items():
                                        if type(v1) == list :
                                                str1=",".join(v1)
                                                att_dic[k1] = str1
                                        else:
                                                att_dic[k1] = v1
                                                dict_format[k] = att_dic    
                      if k == "relation_set":
                              for each in dict_format[k]:
                                      for k1, v1 in each.items():
                                              for rel in v1:
                                                      rel = node_collection.one({'_id':ObjectId(rel)})
                                                      att_dic[k1] = rel.name
                                      dict_format[k] = att_dic                          
                                
      if k in keys_by_filesize:
              filesize_dic = {}
              for k1, v1 in dict_format[k].items():
                      filesize_dic[k1] = v1
              dict_format[k] = filesize_dic
    order_dict_format = collections.OrderedDict()
    order_val=['altnames','language','plural','_type','member_of','created_by','created_at','tags','modified_by','author_set','group_set','collection_set','contributors','last_update','start_publication','location','license','attribute_set','relation_set']
    for each in order_val:
            order_dict_format[each]=dict_format[each]
    return order_dict_format
    

@register.assignment_tag
def get_possible_translations(obj_id):
        translation_list = []
	r_list1 = []
        return get_translation_relation(obj_id._id,r_list1,translation_list)


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
		system = node_collection.find_one({"_id":ObjectId(node_id)})
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
	ver_at = node_collection.one({'_type':'AttributeType','name':'version'})
	if ver_at:
		attr = triple_collection.one({'_type':'GAttribute','attribute_type.$id':ver_at._id,'subject':ObjectId(module_id)})
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
		group_ins = node_collection.find_one({'_type': "Group","_id": ObjectId(groupid)})
		if group_ins:
			group_name = group_ins.name
		else :
			auth = node_collection.one({'_type': 'Author', "_id": ObjectId(groupid) })
			if auth :
				group_name = auth.name

	else :
		pass
	return group_name 


@register.filter
def get_field_type(node_structure, field_name):
  """Returns data-type value associated with given field_name.
  """
  return node_structure.get(field_name)


@register.inclusion_tag('ndf/html_field_widget.html')
# def html_widget(node_id, field, field_type, field_value):
# def html_widget(node_id, node_member_of, field, field_value):
def html_widget(groupid, node_id, field):
  """
  Returns html-widget for given attribute-field; that is, passed in form of
  field_name (as attribute's name) and field_type (as attribute's data-type)
  """
  # gs = None
  field_value_choices = []

  # This field is especially required for drawer-widets to work used in cases of RelationTypes
  # Represents a dummy document that holds node's _id and node's right_subject value(s) from it's GRelation instance
  node_dict = {}

  is_list_of = False
  LIST_OF = [ "[<class 'bson.objectid.ObjectId'>]",
              "[<type 'unicode'>]", "[<type 'basestring'>]",
              "[<type 'int'>]", "[<type 'float'>]", "[<type 'long'>]",
              "[<type 'datetime.datetime'>]"
            ]

  is_special_field = False
  included_template_name = ""
  SPECIAL_FIELDS = {"location": "ndf/location_widget.html",
                    "content_org": "ndf/add_editor.html"
                    # "attendees": "ndf/attendees_widget.html"  # Uncomment this to make attendance-widget working
                    }

  is_required_field = False

  is_mongokit_is_radio = False # False for drop-down True for radio buttons

  try:
    if node_id:
      node_id = ObjectId(node_id)
      node_dict['_id'] = node_id

    # if node_member_of:
    #   gs = node_collection.collection.GSystem()
    #   gs.get_neighbourhood(node_member_of)

    # field_type = gs.structure[field['name']]
    field_type = field['data_type']
    field_altnames = field['altnames']
    field_value = field['value']

    if type(field_type) == IS:
      field_value_choices = field_type._operands

      if len(field_value_choices) == 2:
        is_mongokit_is_radio = True

    elif field_type == bool:
      field_value_choices = [True, False]

    if field.has_key('_id'):
      field = node_collection.one({'_id': field['_id']})

    field['altnames'] = field_altnames

    if not field_value:
      if type(field_type) == IS:
      	field_value = [] 
      else:
      	field_value = ""

    if type(field_type) == type:
      field_type = field_type.__name__
    else:
      field_type = field_type.__str__()

    is_list_of = (field_type in LIST_OF)

    is_special_field = (field['name'] in SPECIAL_FIELDS.keys())
    if is_special_field:
      included_template_name = SPECIAL_FIELDS[field['name']]

    is_AT_RT_base = field["_type"]

    is_attribute_field = False
    is_relation_field = False
    is_base_field = False
    if is_AT_RT_base == "BaseField":
      is_base_field = True
      is_required_field = field["required"]

    elif is_AT_RT_base == "AttributeType":
      is_attribute_field = True
      is_required_field = field["required"]

    elif is_AT_RT_base == "RelationType":
      is_relation_field = True
      is_required_field = True
      #patch
      group = node_collection.find({"_id":ObjectId(groupid)})
      person = node_collection.find({"_id":{'$in': field["object_type"]}},{"name":1})
      
      if person[0].name == "Author":
          if field.name == "has_attendees":
              field_value_choices.extend(list(node_collection.find({'member_of': {'$in':field["object_type"]},
                                                                  'created_by':{'$in':group[0]["group_admin"]+group[0]["author_set"]},
                                                                  
                                                                 })
                                                                 ))
          else:       
              field_value_choices.extend(list(node_collection.find({'member_of': {'$in':field["object_type"]},
                                                            'created_by':{'$in':group[0]["group_admin"]},                                																														}).sort('name', 1)
                                      )
                                )
      #End path
      else:
        field_value_choices.extend(list(node_collection.find({'member_of': {'$in': field["object_type"]},
                                                              'status': u"PUBLISHED",
                                                              'group_set': ObjectId(groupid)
                                                               }).sort('name', 1)
                                      )
                                )
      
      if field_value:
	      if type(field_value[0]) == ObjectId or ObjectId.is_valid(field_value[0]):
	      	field_value = [str(each) for each in field_value]

	      else:
	      	field_value = [str(each._id) for each in field_value]

      if node_id:
      	node_dict[field['name']] = [ObjectId(each) for each in field_value]

    return {'template': 'ndf/html_field_widget.html',
            'field': field, 'field_type': field_type, 'field_value': field_value,
            'node_id': node_id, 'group_id': groupid, 'groupid': groupid, 'node_dict': node_dict,
            'field_value_choices': field_value_choices,
            'is_base_field': is_base_field,
            'is_attribute_field': is_attribute_field,
            'is_relation_field': is_relation_field,
            'is_list_of': is_list_of,
            'is_mongokit_is_radio': is_mongokit_is_radio,
            'is_special_field': is_special_field, 'included_template_name': included_template_name,
            'is_required_field': is_required_field
            # 'is_special_tab_field': is_special_tab_field
    }

  except Exception as e:
    error_message = " HtmlWidgetTagError: " + str(e) + " !!!"
    raise Exception(error_message)

  
@register.assignment_tag
def check_node_linked(node_id):
  """
  Checks whether the passed node is linked with it's corresponding author node (i.e via "has_login" relationship)

  Arguments:
  node_id -- ObjectId of the node

  Returns:
  A bool value, i.e.
  True: if linked (i.e. relationship is created for the given node)
  False: if not linked (i.e. relationship is not created)
  """

  try:
    node = node_collection.one({'_id': ObjectId(node_id)}, {'_id': 1})
    relation_type_node = node_collection.one({'_type': "RelationType", 'name': "has_login"})
    is_linked = triple_collection.one({'_type': "GRelation", 'subject': node._id, 'relation_type': relation_type_node.get_dbref()})

    if is_linked:
      return True

    else:
      return False

  except Exception as e:
    error_message = " NodeUserLinkFindError - " + str(e)
    raise Exception(error_message)


@register.assignment_tag
def get_file_node(request, file_name=""):
	file_list = []
	new_file_list = []

	a = str(file_name).split(',')

	for i in a:
		k = str(i.strip('   [](\'u\'   '))
		file_list.append(k)

	for each in file_list:
		if ObjectId.is_valid(each) is False:
			filedoc = node_collection.find({'_type':'File','name':unicode(each)})

		else:
			filedoc = node_collection.find({'_type':'File','_id':ObjectId(each)})			

		if filedoc:
			for i in filedoc:
				new_file_list.append(i)	

	return new_file_list	


@register.filter(name='jsonify')
def jsonify(value):
    """Parses python value into json-type (useful in converting
    python list/dict into javascript/json object).
    """

    return json.dumps(value, cls=NodeJSONEncoder)


@register.assignment_tag
def get_university(college_name):
    """
    Returns university name to which given college is affiliated to.
    """
    try:
        college = node_collection.one({
            '_type': "GSystemType", 'name': u"College"
        })

        sel_college = node_collection.one({
            'member_of': college._id, 'name': unicode(college_name)
        })

        university_name = None
        if sel_college:
            university = node_collection.one({
                '_type': "GSystemType", 'name': u"University"
            })
            sel_university = node_collection.one({
                'member_of': university._id,
                'relation_set.affiliated_college': sel_college._id
            })
            university_name = sel_university.name

        return university_name
    except Exception as e:
        error_message = "UniversityFindError: " + str(e) + " !!!"
        raise Exception(error_message)


@register.assignment_tag
def get_features_with_special_rights(group_id_or_name, user):
    """Returns list of features with special rights.

    If group is MIS_admin and user belongs to gstaff, then only give
    creation rights to list of feature(s) within MIS GApp shown as following:
      1. StudentCourseEnrollment

    For feature(s) included in list, don't provide creation rights.

    Arguments:
    group_id_or_name -- Name/ObjectId of the group
    user -- Logged-in user object (django-specific)

    Returns:
    List having names of feature(s) included in MIS GApp
    """
    # List of feature(s) for which creation rights should not be given
    features_with_special_rights = ["StudentCourseEnrollment"]

    mis_admin = node_collection.one({
        "_type": "Group", "name": "MIS_admin"
    })

    if (group_id_or_name == mis_admin.name or
            group_id_or_name == str(mis_admin._id)):
        if mis_admin.is_gstaff(user):
            features_with_special_rights = []

    return features_with_special_rights


@register.assignment_tag
def get_filters_data(gst_name):
	'''
	Returns the static data needed by filters. The data to be return will in following format:
	{ 
		"key_name": { "data_type": "<int>/<string>/<...>", "type": "attribute/field", "value": ["val1", "val2"]},
		... ,
		... ,
		"key_name": { "data_type": "<int>/<string>/<...>", "type": "attribute/field", "value": ["val1", "val2"]} 
	}
	'''

	static_mapping = {
                    "educationalsubject": GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT,
                    "language": GSTUDIO_RESOURCES_LANGUAGES,
                    # "educationaluse": GSTUDIO_RESOURCES_EDUCATIONAL_USE,
                    "interactivitytype": GSTUDIO_RESOURCES_INTERACTIVITY_TYPE,
                    "educationalalignment": GSTUDIO_RESOURCES_EDUCATIONAL_ALIGNMENT,
                    "educationallevel": GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL,
                    "curricular": GSTUDIO_RESOURCES_CURRICULAR,
                    "audience": GSTUDIO_RESOURCES_AUDIENCE,
                    "textcomplexity": GSTUDIO_RESOURCES_TEXT_COMPLEXITY
				}

	# following attr's values need to be get/not in settings:
	# timerequired, other_contributors, creator, age_range, readinglevel, adaptation_of, source, basedonurl

	filter_dict = {}

	gst = node_collection.one({'_type':"GSystemType", "name": unicode(gst_name)})
	poss_attr = gst.get_possible_attributes(gst._id)

	exception_list = ["educationaluse"]

	for k, v in poss_attr.iteritems():

		if (k in exception_list) or not static_mapping.has_key(k):
			continue

		filter_dict[k] = {
	    					"data_type": v["data_type"].__name__,
	    					"type" : "attribute",
	    					"value": json.dumps(static_mapping.get(k, []))
	    				}

	# additional filters:

	filter_dict["language"] = { 
								"data_type": "basestring", "type": "field",
								"value": json.dumps(static_mapping["language"]) 
							}

	return filter_dict

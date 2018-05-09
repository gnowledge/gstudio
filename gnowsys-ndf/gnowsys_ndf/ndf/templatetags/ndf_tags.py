''' -- imports from python libraries -- '''
import re
import json
import ox
import mailbox
import email.utils
import datetime
import os
import socket
import multiprocessing as mp
# import shutil
# import magic

from collections import OrderedDict
from time import time
from bson import json_util

#for creating deault mailbox : Metabox
from django_mailbox.models import Mailbox
from imaplib import IMAP4

''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.core.exceptions import PermissionDenied

from django.template import Library
from django.template import RequestContext,loader
from django.shortcuts import render_to_response, render
from django_mailbox.models import Mailbox

# cache imports
from django.core.cache import cache

from mongokit import IS

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS as setting_gapps, GSTUDIO_DEFAULT_GAPPS_LIST, META_TYPE, CREATE_GROUP_VISIBILITY, GSTUDIO_SITE_DEFAULT_LANGUAGE,GSTUDIO_DEFAULT_EXPLORE_URL,GSTUDIO_EDIT_LMS_COURSE_STRUCTURE,GSTUDIO_WORKSPACE_INSTANCE
# from gnowsys_ndf.settings import GSTUDIO_SITE_LOGO,GSTUDIO_COPYRIGHT,GSTUDIO_GIT_REPO,GSTUDIO_SITE_PRIVACY_POLICY, GSTUDIO_SITE_TERMS_OF_SERVICE,GSTUDIO_ORG_NAME,GSTUDIO_SITE_ABOUT,GSTUDIO_SITE_POWEREDBY,GSTUDIO_SITE_PARTNERS,GSTUDIO_SITE_GROUPS,GSTUDIO_SITE_CONTACT,GSTUDIO_ORG_LOGO,GSTUDIO_SITE_CONTRIBUTE,GSTUDIO_SITE_VIDEO,GSTUDIO_SITE_LANDING_PAGE
from gnowsys_ndf.settings import *
try:
	from gnowsys_ndf.local_settings import GSTUDIO_SITE_NAME
except ImportError:
	pass

from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import check_existing_group, get_gapps, get_all_resources_for_group, get_execution_time, get_language_tuple
from gnowsys_ndf.ndf.views.methods import get_drawers, get_group_name_id, cast_to_data_type, get_prior_node_hierarchy, get_course_completetion_status
# from gnowsys_ndf.mobwrite.models import TextObj

from pymongo.errors import InvalidId as invalid_id
from django.contrib.sites.models import Site

# from gnowsys_ndf.settings import LANGUAGES
# from gnowsys_ndf.settings import GSTUDIO_GROUP_AGENCY_TYPES,GSTUDIO_AUTHOR_AGENCY_TYPES

from gnowsys_ndf.ndf.node_metadata_details import schema_dict
from django_mailbox.models import Mailbox
import itertools

register = Library()
at_apps_list = node_collection.one({
    "_type": "AttributeType", "name": "apps_list"
})
translation_set=[]
check=[]

@get_execution_time
@register.assignment_tag
def get_site_registration_variable_visibility(registration_variable=None):
    """Returns dictionary variable holding variables defined in settings file
    for Author's class regarding their visibility in registration template

    If looking for value of single variable, then pass that variable name as
    string which will return it's corresponding value. For example,
        bool_val = get_site_registration_variable_visibility(
            registration_variable="GSTUDIO_REGISTRATION_AUTHOR_AGENCY_TYPE"
        )

    Otherwise, if no parameter is passed, then returns a dictionary variable.
    For example,
        site_dict = get_site_registration_variable_visibility()
    In order to fetch given variable's value from above dictionay use following:
        site_registration_dict["AUTHOR_AGENCY_TYPE"]
        site_registration_dict["AFFILIATION"]
    """
    if registration_variable:
        return eval(registration_variable)

    else:
        site_registration_variable_visibility = {}
        site_registration_variable_visibility["AUTHOR_AGENCY_TYPE"] = GSTUDIO_REGISTRATION_AUTHOR_AGENCY_TYPE
        site_registration_variable_visibility["AFFILIATION"] = GSTUDIO_REGISTRATION_AFFILIATION
    return site_registration_variable_visibility


@get_execution_time
@register.assignment_tag
def get_site_variables():

	result = cache.get('site_var')
	if result:
		return result

	site_var = {}
	site_var['ORG_NAME'] = GSTUDIO_ORG_NAME
	site_var['LOGO'] = GSTUDIO_SITE_LOGO
	site_var['SECONDARY_LOGO'] = GSTUDIO_SITE_SECONDARY_LOGO
	site_var['FAVICON'] = GSTUDIO_SITE_FAVICON
	site_var['COPYRIGHT'] = GSTUDIO_DEFAULT_COPYRIGHT
	site_var['GIT_REPO'] = GSTUDIO_GIT_REPO
	site_var['PRIVACY_POLICY'] = GSTUDIO_SITE_PRIVACY_POLICY
	site_var['TERMS_OF_SERVICE'] = GSTUDIO_SITE_TERMS_OF_SERVICE
	site_var['ORG_LOGO'] = GSTUDIO_ORG_LOGO
	site_var['ABOUT'] = GSTUDIO_SITE_ABOUT
	site_var['SITE_POWEREDBY'] = GSTUDIO_SITE_POWEREDBY
	site_var['PARTNERS'] = GSTUDIO_SITE_PARTNERS
	site_var['GROUPS'] = GSTUDIO_SITE_GROUPS
	site_var['CONTACT'] = GSTUDIO_SITE_CONTACT
	site_var['CONTRIBUTE'] = GSTUDIO_SITE_CONTRIBUTE
	site_var['SITE_VIDEO'] = GSTUDIO_SITE_VIDEO
	site_var['LANDING_PAGE'] = GSTUDIO_SITE_LANDING_PAGE
	site_var['LANDING_TEMPLATE'] = GSTUDIO_SITE_LANDING_TEMPLATE
	site_var['HOME_PAGE'] = GSTUDIO_SITE_HOME_PAGE
	site_var['SITE_NAME'] = GSTUDIO_SITE_NAME
	site_var['SECOND_LEVEL_HEADER'] = GSTUDIO_SECOND_LEVEL_HEADER
	site_var['MY_GROUPS_IN_HEADER'] = GSTUDIO_MY_GROUPS_IN_HEADER
	site_var['MY_COURSES_IN_HEADER'] = GSTUDIO_MY_COURSES_IN_HEADER
	site_var['MY_DASHBOARD_IN_HEADER'] = GSTUDIO_MY_DASHBOARD_IN_HEADER
	site_var['ISSUES_PAGE'] = GSTUDIO_SITE_ISSUES_PAGE
	site_var['ENABLE_USER_DASHBOARD'] = GSTUDIO_ENABLE_USER_DASHBOARD
	site_var['BUDDY_LOGIN'] = GSTUDIO_BUDDY_LOGIN
	site_var['INSTITUTE_ID'] = GSTUDIO_INSTITUTE_ID
	site_var['HEADER_LANGUAGES'] = HEADER_LANGUAGES
	site_var['GSTUDIO_DOC_FOOTER_TEXT'] = GSTUDIO_DOC_FOOTER_TEXT

	cache.set('site_var', site_var, 60 * 30)

	return  site_var


@get_execution_time
@register.assignment_tag
def get_oid_variables():

	result = cache.get('oid_var')
	if result:
		return result

	oid_var = {}

	try:
		# oid_var['ABOUT'] 				= GSTUDIO_OID_ABOUT
		# oid_var['COPYRIGHT'] 			= GSTUDIO_OID_COPYRIGHT
		# oid_var['PRIVACY_POLICY'] 	= GSTUDIO_OID_SITE_PRIVACY_POLICY
		# oid_var['TERMS_OF_SERVICE'] 	= GSTUDIO_OID_SITE_TERMS_OF_SERVICE
		# oid_var['PARTNERS'] 			= GSTUDIO_OID_SITE_PARTNERS
		# oid_var['GROUPS'] 			= GSTUDIO_OID_SITE_GROUPS
		# oid_var['CONTACT'] 			= GSTUDIO_OID_SITE_CONTACT
		# oid_var['CONTRIBUTE'] 		= GSTUDIO_OID_SITE_CONTRIBUTE
		# oid_var['LANDING_PAGE'] 		= GSTUDIO_OID_SITE_LANDING_PAGE
		# oid_var['HOME_PAGE'] 			= GSTUDIO_OID_SITE_HOME_PAGE

		oid_var['tc']			 	= GSTUDIO_OID_TC
		oid_var['oer']				= GSTUDIO_OID_OER

	except Exception, e:
		pass

	cache.set('oid_var', oid_var, 60 * 30)

	return  oid_var


@get_execution_time
@register.assignment_tag
def get_author_agency_types():
   return GSTUDIO_AUTHOR_AGENCY_TYPES


@get_execution_time
@register.assignment_tag
def get_group_agency_types():
   return GSTUDIO_GROUP_AGENCY_TYPES


@get_execution_time
@register.assignment_tag
def get_copyright():
   return GSTUDIO_COPYRIGHT


@get_execution_time
@register.assignment_tag
def get_agency_type_of_group(group_id):
	'''
	Getting agency_type value of the group.
	'''
	group_obj = node_collection.one({"_id": ObjectId(group_id)})
	group_agency_type = group_obj.agency_type
	# print "group_agency_type : ", group_agency_type
	return group_agency_type


@get_execution_time
@register.assignment_tag
def get_node_type(node):
   if node:
      obj = node_collection.find_one({"_id": ObjectId(node._id)})
      nodetype=node.member_of_names_list[0]
      if "Group" == nodetype:
        pe = get_sg_member_of(node._id)
        if "ProgramEventGroup" in pe:
          return "ProgramEventGroup"
      return nodetype
   else:
      return ""


@get_execution_time
@register.assignment_tag
def get_node(node_id):
    if node_id:
        obj = node_collection.one({"_id": ObjectId(node_id)})
        if obj:
            return obj
        else:
            return ""


@get_execution_time
@register.assignment_tag
def get_schema(node):
	if node:
		# obj = node_collection.find_one({"_id": ObjectId(node.member_of[0])}, {"name": 1})
		nam = node.member_of_names_list[0]
		if(nam == 'Page'):
			return [1,schema_dict[nam]]

		elif hasattr(node, 'mime_type') and (nam=='File'):
			mimetype_val = node.get_gsystem_mime_type()
			if( 'image' in node.mime_type):
				return [1,schema_dict['Image']]
			elif('video' in mimetype_val or 'Pandora_video' in mimetype_val):
				return [1,schema_dict['Video']]
			else:
				return [1,schema_dict['Document']]
		else:
			return [0,""]
	else:
		return [0,""]
'''
   if node:
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
   else:
       return [0,""]
'''

@get_execution_time
@register.filter
def is_Page(node):
	Page = node_collection.one({"_type": "GSystemType", "name": "Page"})
	if(Page._id in node.member_of):
		return 1
	else:
		return 0


@get_execution_time
@register.filter
def is_Quiz(node):
	Quiz = node_collection.one({"_type": "GSystemType", "name": "Quiz"})
	if(Quiz._id in node.member_of):
		return 1
	else:
		return 0


@get_execution_time
@register.filter
def is_File(node):
	File = node_collection.one({"_type": "GSystemType", "name": "File"})
	if(File._id in node.member_of):
		return 1
	else:
		return 0


@get_execution_time
@register.inclusion_tag('ndf/userpreferences.html')
def get_user_preferences(group,user):
	return {'groupid':group,'author':user}


@get_execution_time
@register.assignment_tag
def get_languages():
        return LANGUAGES


@get_execution_time
@register.assignment_tag
def get_node_ratings(request,node_id):
	try:
		user = request.user
		node_obj = node_collection.one({'_id': ObjectId(node_id)})
		total_score = 0
		total_rating = 0
		rating_by_user = 0
		counter_var = 0
		avg_rating = 0.0
		rating_data = {}
		for each in node_obj.rating:
			if each['user_id'] == user.id:
				rating_by_user = each['score']
			if each['user_id'] == 0:
				counter_var += 1
			total_score = total_score + each['score']
		if len(node_obj.rating) == 1 and counter_var == 1:
			total_rating = 0
		else:
			if node_obj.rating:
				total_rating = len(node_obj.rating) - counter_var
			if total_rating:
				if type(total_rating) is float:
					total_rating = round(total_rating,1)
				avg_rating = float(total_score)/total_rating
				avg_rating = round(avg_rating,1)

		rating_data['avg'] = avg_rating
		rating_data['tot'] = total_rating
		rating_data['user_rating'] = rating_by_user
		return rating_data

	except Exception as e:
		print "Error in get_node_ratings " + str(e)

@get_execution_time
@register.assignment_tag
def get_group_resources(group):
	try:
		res=get_all_resources_for_group(group['_id'])
		return res.count
	except Exception as e:
		print "Error in get_group_resources "+str(e)


@get_execution_time
@register.assignment_tag
def all_gapps():
	try:
		return get_gapps()
	except Exception as expt:
		print "Error in get_gapps "+str(expt)


@get_execution_time
@register.assignment_tag
def get_group_gapps(group_id=None):

	# group_obj = node_collection.one({"_id": ObjectId(group_id) }, { "name": 1, "attribute_set.apps_list": 1, '_type': 1 })

	if ObjectId.is_valid(group_id):

		# group_attrs = group_obj.get_possible_attributes(group_obj._id)
		# print group_attrs

		# gapps_list = group_attrs.get('apps_list', [])
		at_apps_list = node_collection.one({'_type': 'AttributeType', 'name': 'apps_list'})
		# attr_list = triple_collection.find({'_type': 'GAttribute', 'attribute_type': at_apps_list._id, 'subject':group_obj._id})
		# attr_list = triple_collection.one({
		# 									'_type': 'GAttribute',
		# 									'attribute_type': at_apps_list._id,
		# 									'subject': ObjectId(group_id),
		# 									'status': u'PUBLISHED'
		# 								},
		# 								{'_id': 0, 'object_value': 1}
		# 							)

		attr_list = triple_collection.find_one({
											'_type': 'GAttribute',
											'attribute_type': at_apps_list._id,
											'subject': ObjectId(group_id),
											'status': u'PUBLISHED',
											'object_value': {'$exists': 1}
										},
										{'_id': 0, 'object_value': 1}
									)
		# print attr_list.count()," ---------- count "

		if attr_list:
			all_gapp_ids_list = [node_collection.one({'_id': g['_id']}) for g in attr_list['object_value']]
			# all_gapp_ids_list = attr_list
			# print "\n legnt==== ", all_gapp_ids_list
			return all_gapp_ids_list
		# group_name = group_obj.name
		# for attr in group_obj.attribute_set:
		# 	if attr and "apps_list" in attr:
		# 		gapps_list = attr["apps_list"]
		# 		# print "\n", gapps_list,"\n"

		# 		all_gapp_ids_list = [node_collection.one({'_id':ObjectId(g['_id'])}) for g in gapps_list]
		# 		# print all_gapp_ids_list,">>>>>>>>>>\n\n works like prior_node"
		# 		return all_gapp_ids_list


	return []


@get_execution_time
@register.assignment_tag
def get_create_group_visibility():
	if CREATE_GROUP_VISIBILITY:
		return True
	else:
		return False


@get_execution_time
@register.assignment_tag
def get_site_info():
	sitename = Site.objects.all()[0].name.__str__()
	return sitename


@get_execution_time
@register.assignment_tag
def check_is_user_group(group_id):
	try:
		res_group_obj = get_group_name_id(group_id, True)
		# print "\n\n res_group_obj",res_group_obj._type
		if res_group_obj._type == "Author":
			return True
		else:
			return False
		# lst_grps=[]
		# all_user_grps=get_all_user_groups()
		# grp = node_collection.one({'_id':ObjectId(group_id)})
		# for each in all_user_grps:
		# 	lst_grps.append(each.name)
		# if grp.name in lst_grps:
		# 	return True
		# else:
		# 	return False
	except Exception as exptn:
		print "Exception in check_user_group "+str(exptn)


@get_execution_time
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


@get_execution_time
@register.assignment_tag
def get_all_user_groups():
	try:
		return node_collection.find({'_type':'Author'}).sort('name', 1)
		# return list(all_groups)
	except:
		print "Exception in get_all_user_groups"


@get_execution_time
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


@get_execution_time
@register.assignment_tag
def get_states_object(request):
   group_object = node_collection.one({'$and':[{'_type':u'Group'},{'name':u'State Partners'}]})
   return group_object


@get_execution_time
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


@get_execution_time
@register.assignment_tag
def get_all_users_int_count():
	'''
	get integer count of all the users
	'''
	all_users = len(User.objects.all())
	return all_users


@get_execution_time
@register.inclusion_tag('ndf/twist_replies.html')
def get_reply(request, thread,parent,forum,token,user,group_id):
	return {'request':request, 'thread':thread,'reply': parent,'user':user,'forum':forum,'csrf_token':token,'eachrep':parent,'groupid':group_id}


@get_execution_time
@register.inclusion_tag('ndf/uploaded_files_for_replies.html')
def get_files_for_reply(rep_id,groupid):
        lst_files_uploaded = []
        grp_id=groupid._id
        for each in rep_id.collection_set:
                file_item=node_collection.one({"_id": each})
                lst_files_uploaded.append(file_item)
	return {'group_id':groupid._id,'node_list':lst_files_uploaded}



@get_execution_time
@register.assignment_tag
def get_all_replies(parent):
	 ex_reply=""
	 if parent:
		 ex_reply = node_collection.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(parent._id)}],'status':{'$nin':['HIDDEN']}})
		 ex_reply.sort('created_at',-1)
	 return ex_reply


@get_execution_time
@register.assignment_tag
def get_all_possible_languages():
	language = list(LANGUAGES)
	all_languages = language + OTHER_COMMON_LANGUAGES
	return all_languages

@get_execution_time
@register.assignment_tag
def get_metadata_values(metadata_type=None):

	metadata = {"educationaluse": GSTUDIO_RESOURCES_EDUCATIONAL_USE, "interactivitytype": GSTUDIO_RESOURCES_INTERACTIVITY_TYPE, "curricular": GSTUDIO_RESOURCES_CURRICULAR,
				"educationallevel": GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL, "educationalsubject": GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT,
				# "language": GSTUDIO_RESOURCES_LANGUAGES,
				"timerequired": GSTUDIO_RESOURCES_TIME_REQUIRED, "audience": GSTUDIO_RESOURCES_AUDIENCE , "textcomplexity": GSTUDIO_RESOURCES_TEXT_COMPLEXITY,
				"age_range": GSTUDIO_RESOURCES_AGE_RANGE ,"readinglevel": GSTUDIO_RESOURCES_READING_LEVEL, "educationalalignment": GSTUDIO_RESOURCES_EDUCATIONAL_ALIGNMENT}
	if metadata_type and metadata_type in metadata:
		return metadata[metadata_type]
	return metadata


@get_execution_time
@register.assignment_tag
def get_attribute_value(node_id, attr_name, get_data_type=False, use_cache=True):
    cache_key = str(node_id) + 'attribute_value' + str(attr_name)
    cache_result = cache.get(cache_key)

    if (cache_key in cache) and not get_data_type and use_cache:
        return cache_result

    attr_val = ""
    node_attr = data_type = None
    if node_id:
        # print "\n attr_name: ", attr_name
        gattr = node_collection.one({'_type': 'AttributeType', 'name': unicode(attr_name) })
        if get_data_type:
            data_type = gattr.data_type
        if gattr: # and node  :
            node_attr = triple_collection.find_one({'_type': "GAttribute", "subject": ObjectId(node_id), 'attribute_type': gattr._id, 'status': u"PUBLISHED"})
    if node_attr:
        attr_val = node_attr.object_value
        # print "\n here: ", attr_name, " : ", type(attr_val), " : ", node_id
    if get_data_type:
        return {'value': attr_val, 'data_type': data_type}
    cache.set(cache_key, attr_val, 60 * 60)
    return attr_val


@get_execution_time
@register.assignment_tag
def get_relation_value(node_id, grel, return_single_right_subject=False):

    # import ipdb; ipdb.set_trace()
    try:
        result_dict = {}
        if node_id:
            node = node_collection.one({'_id': ObjectId(node_id) })
            relation_type_node = node_collection.one({'_type': 'RelationType', 'name': unicode(grel) })
            if node and relation_type_node:
                if relation_type_node.object_cardinality > 1:
                    node_grel = triple_collection.find({'_type': "GRelation", "subject": node._id, 'relation_type': relation_type_node._id,'status':"PUBLISHED"})
                    if node_grel:
                        grel_val = []
                        grel_id = []
                        for each_node in node_grel:
                            grel_val.append(each_node.right_subject)
                            grel_id.append(each_node._id)
                        grel_val_node_cur = node_collection.find({'_id':{'$in' : grel_val}})
                        result_dict.update({"cursor": True})
                        if return_single_right_subject:
                            grel_val_node_cur = node_collection.find_one({'_id':{'$in' : grel_val}})
                            result_dict.update({"cursor": False})
                        # nodes = [grel_node_val for grel_node_val in grel_val_node_cur]
                        # print "\n\n grel_val_node, grel_id == ",grel_val_node, grel_id
                        result_dict.update({"grel_id": grel_id, "grel_node": grel_val_node_cur})
                else:
                    node_grel = triple_collection.one({'_type': "GRelation", "subject": node._id, 'relation_type': relation_type_node._id,'status':"PUBLISHED"})
                    if node_grel:
                        grel_val = list()
                        grel_val = node_grel.right_subject
                        grel_val = grel_val if isinstance(grel_val, list) else [ObjectId(grel_val)]
                        grel_id = node_grel._id
                        # grel_val_node = node_collection.one({'_id':ObjectId(grel_val)})
                        grel_val_node = node_collection.find_one({'_id':{'$in': grel_val}})
                        # returns right_subject of grelation and GRelation _id
                        result_dict.update({"grel_id": grel_id, "grel_node": grel_val_node, "cursor": False})
        # print "\n\nresult_dict === ",result_dict
        return result_dict
    except Exception as e:
        print e
        return {}


@get_execution_time
@register.inclusion_tag('ndf/drawer_widget.html')
def edit_drawer_widget(field, group_id, node=None, page_no=1, checked=None, **kwargs):
	drawers = None
	drawer1 = None
	drawer2 = None
	user_type = None

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
			drawers, paged_resources = get_drawers(group_id, node._id, node.collection_set, page_no, checked)

		elif field == "prior_node":
			checked = None
			drawers, paged_resources = get_drawers(group_id, node._id, node.prior_node, checked)

		elif field == "Group":
			checked = checked
			if kwargs.has_key("user_type"):
				user_type = kwargs["user_type"]

			drawers, paged_resources = get_drawers(group_id, node._id, node.group_admin, page_no, checked)

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
					'is_RT': checked, 'group_id': group_id, 'groupid': group_id, 'user_type': user_type
				}


@get_execution_time
@register.inclusion_tag('tags/dummy.html')
# def list_widget( fields_name, fields_type, fields_value, template1='ndf/option_widget.html',template2='ndf/drawer_widget.html'):
def list_widget( fields_name, fields_type, fields_value, template1='ndf/option_widget.html'):
	drawer1 = {}
	drawer2 = None
	admin_related_drawer = True

	group_obj = node_collection.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})
	if group_obj:
		groupid = str(group_obj[0]._id)

	alltypes = ["GSystemType","MetaType","AttributeType","RelationType"]

	fields_selection1 = ["subject_type","language","object_type","applicable_node_type","subject_applicable_nodetype","object_applicable_nodetype","data_type"]
	# fields_selection2 = ["meta_type_set","attribute_type_set","relation_type_set","prior_node","member_of","type_of"]

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
			#drawer = node_collection.find({"_type":types,'name':{'$nin':[u'Voluntary Teacher']}})
			drawer = node_collection.find({"_type":types})
			for each in drawer:
				drawer1[str(each._id)]=each
		return {'template': template1, 'widget_for': fields_name, 'drawer1': drawer1, 'selected_value': fields_value}

	# if fields_name in fields_selection2:
	# 	fields_value_id_list = []

	# 	if fields_value:
	# 		for each in fields_value:
	# 			if type(each) == ObjectId:
	# 				fields_value_id_list.append(each)
	# 			else:
	# 				fields_value_id_list.append(each._id)

	# 	if types in alltypes:
	# 		for each in node_collection.find({"_type": types}):
	# 			if fields_value_id_list:
	# 				if each._id not in fields_value_id_list:
	# 					drawer1[each._id] = each
	# 			else:
	# 				drawer1[each._id] = each

	# 	if types in ["all_types"]:
	# 		for each in alltypes:
	# 			for eachnode in node_collection.find({"_type": each}):
	# 				if fields_value_id_list:
	# 					if eachnode._id not in fields_value_id_list:
	# 						drawer1[eachnode._id] = eachnode
	# 				else:
	# 					drawer1[eachnode._id] = eachnode

	# 	if fields_value_id_list:
	# 		drawer2 = []
	# 		for each_id in fields_value_id_list:
	# 			each_node = node_collection.one({'_id': each_id})
	# 			if each_node:
	# 				drawer2.append(each_node)


	# 	return {'template': template2, 'widget_for': fields_name, 'drawer1': drawer1, 'drawer2': drawer2, 'group_id': groupid,'groupid': groupid, 'admin_related_drawer': admin_related_drawer }


@get_execution_time
@register.assignment_tag
@register.inclusion_tag('ndf/admin_fields.html')
def get_selected_drawer_items_single_dropdown(fields_name,fields_value):
	fields_selection1 = ["subject_type","language","object_type","applicable_node_type","subject_applicable_nodetype","object_applicable_nodetype","data_type"]
	drawer2 ={}
	if fields_name in fields_selection1:
		fields_value_id_list = []

		if fields_value:
			for each in fields_value:
				if type(each) == ObjectId:
					fields_value_id_list.append(each)
				else:
					fields_value_id_list.append(each._id)

		if fields_value_id_list:
			drawer2 = []
			for each_id in fields_value_id_list:
				each_node = node_collection.one({'_id': each_id})
				if each_node:
					drawer2.append(each_node)

		return drawer2

	return []

@get_execution_time
@register.assignment_tag
@register.inclusion_tag('ndf/admin_fields.html')
def get_all_drawer_items_single_dropdown(fields_name,fields_value):
	fields_selection1 = ["subject_type","language","object_type","applicable_node_type","subject_applicable_nodetype","object_applicable_nodetype","data_type"]
	fields = {"subject_type":"GSystemType", "object_type":"GSystemType", "meta_type_set":"MetaType", "attribute_type_set":"AttributeType", "relation_type_set":"RelationType", "member_of":"MetaType", "prior_node":"all_types", "applicable_node_type":"NODE_TYPE_CHOICES", "subject_applicable_nodetype":"NODE_TYPE_CHOICES", "object_applicable_nodetype":"NODE_TYPE_CHOICES", "data_type": "DATA_TYPE_CHOICES", "type_of": "GSystemType","language":"GSystemType"}
	types = fields[fields_name]
	drawer1 = {}
	if fields_name in fields_selection1:
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
				drawer1[each]=each
	return drawer1

@get_execution_time
@register.assignment_tag
@register.inclusion_tag('ndf/admin_fields.html')
def get_all_drawer_items(fields_name,fields_value):
	drawer1 = {}
	alltypes = ["GSystemType","MetaType","AttributeType","RelationType"]
	fields_selection2 = ["meta_type_set","attribute_type_set","relation_type_set","member_of","type_of"]
	fields = {"subject_type":"GSystemType", "object_type":"GSystemType", "meta_type_set":"MetaType", "attribute_type_set":"AttributeType", "relation_type_set":"RelationType", "member_of":"MetaType", "prior_node":"all_types", "applicable_node_type":"NODE_TYPE_CHOICES", "subject_applicable_nodetype":"NODE_TYPE_CHOICES", "object_applicable_nodetype":"NODE_TYPE_CHOICES", "data_type": "DATA_TYPE_CHOICES", "type_of": "GSystemType","language":"GSystemType"}
	types = fields[fields_name]

	if fields_name in fields_selection2:
		if types in alltypes:
			for each in node_collection.find({"_type": types}):
				drawer1[each] = each
		return drawer1
	return []

@get_execution_time
@register.assignment_tag
@register.inclusion_tag('ndf/admin_fields.html')
def get_selected_drawer_items(fields_name,fields_value):
	drawer2 = None
	alltypes = ["GSystemType","MetaType","AttributeType","RelationType"]
	fields_selection2 = ["meta_type_set","attribute_type_set","relation_type_set","prior_node","member_of","type_of","subject_type"]
	fields = {"subject_type":"GSystemType", "object_type":"GSystemType", "meta_type_set":"MetaType", "attribute_type_set":"AttributeType",
	 "relation_type_set":"RelationType", "member_of":"MetaType", "prior_node":"all_types", "applicable_node_type":"NODE_TYPE_CHOICES",
	  "subject_applicable_nodetype":"NODE_TYPE_CHOICES", "object_applicable_nodetype":"NODE_TYPE_CHOICES", "data_type": "DATA_TYPE_CHOICES",
	   "type_of": "GSystemType","language":"GSystemType" , "subject_type":"GSystemType" }
	types = fields[fields_name]

	if fields_name in fields_selection2:
		fields_value_id_list = []

		if fields_value:
			for each in fields_value:
				if type(each) == ObjectId:
					fields_value_id_list.append(each)
				else:
					fields_value_id_list.append(each._id)

		if fields_value_id_list:
			drawer2 = []
			for each_id in fields_value_id_list:
				each_node = node_collection.one({'_id': each_id})
				if each_node:
					drawer2.append(each_node)

		return drawer2

	return []


@get_execution_time
@register.assignment_tag
@register.inclusion_tag('ndf/admin_fields.html')
def get_all_priornode_items(fields_name,fields_value):
	drawer1 = {}
	drawer = {}
	alltypes = ["GSystemType","MetaType","AttributeType","RelationType"]
	fields = {"meta_type_set":"MetaType", "relation_type_set":"RelationType", "member_of":"MetaType", "prior_node":"all_types","type_of": "GSystemType"}
	types = fields[fields_name]

	for each in alltypes:
		for eachnode in node_collection.find({"_type":each}):
			drawer[eachnode] = eachnode._id
	return drawer

	return []


@get_execution_time
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
@get_execution_time
@register.inclusion_tag('ndf/gapps_iconbar.html')
def get_gapps_iconbar(request, group_id, user_access=None):
    """Get GApps menu-bar
    """
    try:
    	group_name, group_id = get_group_name_id(group_id)
        selected_gapp = request.META["PATH_INFO"]
        if len(selected_gapp.split("/")) > 2:
            selected_gapp = selected_gapp.split("/")[2]
        else:
            selected_gapp = selected_gapp.split("/")[1]

        # If apps_list are set for given group
        # then list them
        # Otherwise fetch default apps list
        gapps_list = []

        group_name = ""
        group_id = ObjectId(group_id)
        # Fetch group

        group_obj = node_collection.one({
            "_id": group_id
        }, {
            "name": 1, "attribute_set.apps_list": 1, '_type': 1
        })

        if group_obj:
            group_name = group_obj.name

            # Look for list of gapps already set for group
            for attr in group_obj.attribute_set:
                if attr and "apps_list" in attr:
                    gapps_list = attr["apps_list"]

                    break
        if not gapps_list:
            # If gapps not found for group, then make use of default apps list
            gapps_list = get_gapps(default_gapp_listing=True)

        i = 0
        gapps = {}
        for node in gapps_list:
            if node:
                i += 1
                gapps[i] = {"id": node["_id"], "name": node["name"].lower()}
        if group_obj and group_obj._type == "Author":
			# user_gapps = ["page", "file"]
			user_gapps = [gapp_name.lower() for gapp_name in GSTUDIO_USER_GAPPS_LIST]
			for k, v in gapps.items():
				for k1, v1 in v.items():
					if k1 == "name":
						if v1.lower() not in user_gapps:
							del gapps[k]

	if group_obj.name == 'Trash':
		gapps={}
        return {
            "template": "ndf/gapps_iconbar.html",
            "request": request, 'user_access': user_access,
            "groupid": group_id, "group_name_tag": group_name,
            "gapps": gapps, "selectedGapp": selected_gapp
        }

    except invalid_id:
        gpid = node_collection.one({
            "_type": u"Group"
        }, {
            "name": u"home"
        })
        group_id = gpid._id
        return {
            'template': 'ndf/gapps_iconbar.html',
            'request': request, 'gapps': gapps, 'selectedGapp': selected_gapp,
            'groupid': group_id, 'user_access': user_access,
        }


@get_execution_time
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
	selected_gapp = ""

	if (len(url_split) > 1) and (url_split[1] != "dashboard"):
		selected_gapp = url_split[1]  # expecting e-library etc. type of extract

		# handling conditions of "e-library" = "file" and vice-versa.
		selected_gapp = "e-library" if (selected_gapp == "file") else selected_gapp
		selected_gapp = "topics" if (selected_gapp == "topic_details") else selected_gapp

		# for deciding/confirming selected gapp
		for each_gapp in gapps:
			temp_val = each_gapp.values()[0]
			if temp_val == selected_gapp:
				nroer_menu_dict["selected_gapp"] = temp_val
				break

		# print "selected_gapp : ", selected_gapp
	if (selected_gapp == "partner") and (len(url_split) > 2) and (url_split[2] in ["Partners", "Groups"]):
		top_menu_selected = url_split[2]

	mapping = GSTUDIO_NROER_MENU_MAPPINGS

	# deciding "top level menu selection"
	if ((group_name == "home") and nroer_menu_dict.has_key("selected_gapp")) or (selected_gapp == "repository"):
		top_menu_selected = "Repository"
		# print top_menu_selected

	elif (group_name in mapping.values()):
		sub_menu_selected = mapping.keys()[mapping.values().index(group_name)]  # get key of/from mapping
		nroer_menu_dict["sub_menu_selected"] = sub_menu_selected

		# with help of sub_menu_selected get it's parent from GSTUDIO_NROER_MENU
		top_menu_selected = [i.keys()[0] for i in GSTUDIO_NROER_MENU[1:] if sub_menu_selected in i.values()[0]][0]
		# for Partners, "Curated Zone" should not appear
		gapps = gapps[1:] if (top_menu_selected in ["Partners", "Groups"]) else gapps

	elif (len(url_split) >= 3) and ("nroer_groups" in url_split) and (url_split[2] in [i.keys()[0] for i in GSTUDIO_NROER_MENU[1:]]):
		# print "top_menu_selected ", top_menu_selected
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


@get_execution_time
@register.assignment_tag
def get_site_name_from_settings():
	# print "GSTUDIO_SITE_NAME : ", GSTUDIO_SITE_NAME
	# print "site name",GSTUDIO_SITE_NAME
	return GSTUDIO_SITE_NAME


global_thread_rep_counter = 0	# global variable to count thread's total reply
global_thread_latest_reply = {"content_org":"", "last_update":"", "user":""}
@get_execution_time
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
			elif global_thread_latest_reply["last_update"] < each.last_update:
				global_thread_latest_reply["content_org"] = each.content_org
				global_thread_latest_reply["last_update"] = each.last_update
				global_thread_latest_reply["user"] = User.objects.get(pk=each.created_by).username

			thread_reply_count(each._id)

	return global_thread_rep_counter


# To get all the discussion replies
# global variable to count thread's total reply
# global_disc_rep_counter = 0
# global_disc_all_replies = []
@get_execution_time
@register.assignment_tag
def get_disc_replies( oid, group_id, global_disc_all_replies, level=1 ):
	'''
	Method to count total replies for the disc.
	'''

	try:
		group_id = ObjectId(group_id)
	except:
		group_name, group_id = get_group_name_id(group_id)
	# ins_objectid  = ObjectId()
	# if ins_objectid.is_valid(group_id) is False:
	# 	group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	# 	if group_ins:
	# 		group_id = str(group_ins._id)
	# 	else:
	# 		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	# 		if auth :
	# 			group_id = str(auth._id)
	# else:
	# 	pass

	reply_st = node_collection.one({ '_type':'GSystemType', 'name':'Reply'})
	oid_obj = node_collection.one({'_id':ObjectId(oid)})
	# print "\n\n oid_obj----",oid_obj.name
	# thr_rep = node_collection.find({'$and':[ {'_type':'GSystem'}, {'prior_node':ObjectId(oid)}, {'member_of':ObjectId(reply_st._id)} ]})#.sort({'created_at': -1})
	thr_rep = node_collection.find({'_type':'GSystem', 'group_set':ObjectId(group_id), 'prior_node':ObjectId(oid), 'member_of':ObjectId(reply_st._id)}).sort('created_at', -1)

	# to acces global_disc_rep_counter as global and not as local
	# global global_disc_rep_counter
	# global global_disc_all_replies
	# print "\n\n thr_rep",thr_rep.count()

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
			temp_disc_reply["collection_set"] = [node_collection.one({'_id': ObjectId(i)}) for i in each.collection_set]
			temp_disc_reply["level"] = level
			temp_disc_reply["contributors"] = each.user_details_dict["contributors"]
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


@get_execution_time
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
@get_execution_time
def get_rec_objs(ob_id):
	lp.append(ob_id)
	exstng_reply = node_collection.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(ob_id)}]})
	for each in exstng_reply:
		get_rec_objs(each)
	return lp


@get_execution_time
@register.assignment_tag
def get_twist_replies(twist):
	ret_replies={}
	entries=[]
	exstng_reply = node_collection.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(twist._id)}]})
	for each in exstng_reply:
		lst=get_rec_objs(each)
	return ret_replies


@get_execution_time
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


@get_execution_time
@register.assignment_tag
def check_group(group_id):
	try:
		result = False
		if group_id:
			group_obj = node_collection.one({'_id': ObjectId(group_id)})
			if "Group" in group_obj.member_of_names_list or "Author" in group_obj.member_of_names_list:
				result = True
			if group_obj._type == "Author" or group_obj._type == "Group":
				result = True
		else:
			result = False
		return result
	except:
		return result

	# if group_id:
	# 	fl = check_existing_group(group_id)
	# 	return fl
	# else:
	# 	return ""


@get_execution_time
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


@get_execution_time
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


@get_execution_time
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


@get_execution_time
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


@get_execution_time
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


@get_execution_time
@register.assignment_tag
def get_profile_pic(user_pk):
	"""
	This returns file document if exists, otherwise None value.
	"""
	try:
		grel_val_node = ""
		profile_pic_image = None
		ID = int(user_pk)
		auth = node_collection.one({'_type': "Author", 'created_by': ID}, {'_id': 1, 'relation_set': 1})

		# if auth:
		#     for each in auth.relation_set:
		#         if "has_profile_pic" in each:
		#             profile_pic_image = node_collection.one(
		#                 {'_type': "File", '_id': each["has_profile_pic"][0]}
		#             )

		#             break
		if auth:
			grel = node_collection.one({'_type': 'RelationType', 'name': unicode("has_profile_pic") })
			if auth and grel:
				node_grel = triple_collection.one({'_type': "GRelation", "subject": auth._id, 'relation_type': grel._id,'status':"PUBLISHED"})
		if node_grel:
			grel_val = node_grel.right_subject
			grel_val_node = node_collection.one({'_id':ObjectId(grel_val)})
		return grel_val_node
	except Exception as e:
		return grel_val_node


@get_execution_time
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


@get_execution_time
@register.assignment_tag
def get_edit_url(groupid):

	node = node_collection.one({'_id': ObjectId(groupid) })
	if node._type == 'GSystem':

		type_name = node_collection.one({'_id': ObjectId(node.member_of[0])}).name
		if type_name == 'Quiz':
			return 'quiz_edit'
		elif type_name == 'Term':
			return 'term_create_edit'
		elif type_name == 'Theme' or type_name == 'Topic':
			return 'theme_topic_create'
		elif type_name == 'QuizItem' or type_name == 'QuizItemEvent':
			return 'quiz_item_edit'
		elif type_name == 'Forum':
			return 'edit_forum'
		elif type_name == 'Twist' or type_name == 'Thread':
			return 'edit_thread'
		elif type_name == 'File':
			return 'file_edit'
		else:
			return 'page_create_edit'


	elif node._type == 'Group' or node._type == 'Author' :
		return 'edit_group'

	elif node._type == 'File':

		mime_type = node.get_gsystem_mime_type()

		if 'video' in mime_type:
			return 'video_edit'
		elif 'image' in mime_type:
			return 'image_edit'
		else:
			return 'file_edit'

@get_execution_time
@register.assignment_tag
def get_event_type(node):
    event = node_collection.one({'_id':{'$in':node.member_of}})
    return event._id

@get_execution_time
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
		elif type_name.name == 'File':
			if (node.if_file.mime_type) == ("application/octet-stream"):
				return 'video_detail'
			elif 'image' in node.if_file.mime_type:
				return 'file_detail'
			else:
				return 'file_detail'
		else:
			return 'None'
	elif node._type == 'Group':
		return 'group'
	elif node._type == 'File':
		if "mime_type" in node:
			if (node.mime_type) == ("application/octet-stream"):
				return 'video_detail'
			elif 'image' in node.mime_type:
				return 'file_detail'
			else:
				return 'file_detail'
		else:
			if (node.if_file.mime_type) == ("application/octet-stream"):
				return 'video_detail'
			elif 'image' in node.if_file.mime_type:
				return 'file_detail'
			else:
				return 'file_detail'
	else:
		return 'group'

@get_execution_time
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

@get_execution_time
@register.assignment_tag
def get_prior_node(node_id):

	obj = node_collection.one({'_id':ObjectId(node_id) })
	prior = []
	topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
	if topic_GST._id in obj.member_of:

		if obj.prior_node:
	#	for each in obj.prior_node:
#			node = node_collection.one({'_id': ObjectId(each) })
	#		prior.append(( node._id , node.name ))
			prior=[(node_collection.one({'_id': ObjectId(each) })._id,node_collection.one({'_id': ObjectId(each) }).name) for each in obj.prior_node]
		return prior

	return prior


# method fist get all possible translations associated with current node &
# return the set of resources by using get_resources method
@get_execution_time
@register.assignment_tag
def get_all_resources(request,node_id):
        obj_set=[]
        keys=[] # set of keys used for creating the fieldset in template
        result_set=[]
        node=node_collection.one({'_id':ObjectId(node_id)})
        result_set=get_possible_translations(node)
        if node._id not in obj_set:
                obj_set.append(node._id)
                for item in result_set:
                        # print "\n=====",item.keys()
                        obj_set.extend(item.keys())
        resources={'Images':[],'Documents':[],'Audios':[],'Videos':[],'Interactives':[], 'eBooks':[]}
        for each in obj_set:
                n=node_collection.one({'_id':ObjectId(each)})
                resources_dict=get_resources(each,resources)
        res_dict={'Images':[],'Documents':[],'Audios':[],'Videos':[],'Interactives':[], 'eBooks':[]}

        for k,v in res_dict.items():
                res_dict[k]={'fallback_lang':[],'other_languages':[]}
        for key,val in resources_dict.items():
                if val:
                        keys.append(key)
                        for res in val:

                        	# following if condition is temp patch.
                        	# actually for this condition to get work, we need to have \
                        	# uniform data-type/format for storing in language field.
                        	# currently, we are also using any of: code or name or tuple.
                        	# e.g: "en" or "English" or ("en", "English")
                            # if (len(res.language) == len(request.LANGUAGE_CODE)) and (res.language != request.LANGUAGE_CODE):
                            if isinstance(res.language, (list, tuple)) and len(res.language) > 1 and (res.language[0] != request.LANGUAGE_CODE):
                                    res_dict[key]['other_languages'].append(res)
                            else:
                                    res_dict[key]['fallback_lang'].append(res)

        for k1,v1 in res_dict.items():
                if k1 not in keys :
                        del res_dict[k1]
        return res_dict
# method returns resources associated with node
@get_execution_time
@register.assignment_tag
def get_resources(node_id,resources):
    	node = node_collection.one({'_id': ObjectId(node_id)})
        RT_teaches = node_collection.one({'_type':'RelationType', 'name': 'teaches'})
        RT_translation_of = node_collection.one({'_type':'RelationType','name': 'translation_of'})
        teaches_grelations = triple_collection.find({'_type': 'GRelation', 'right_subject': node._id, 'relation_type': RT_teaches._id })
        AT_educationaluse = node_collection.one({'_type': 'AttributeType', 'name': u'educationaluse'})
        for each in teaches_grelations:
                obj=node_collection.one({'_id':ObjectId(each.subject)})
                mime_type=triple_collection.one({'_type': "GAttribute", 'attribute_type': AT_educationaluse._id, "subject":each.subject})
                for k,v in resources.items():
                        if mime_type and mime_type.object_value == k:
                                if obj.name not in resources[k]:
                                        resources.setdefault(k,[]).append(obj)

        return resources


@get_execution_time
@register.assignment_tag
def get_contents(node_id, selected=None, choice=None):

	contents = {}
	image_contents = []
	video_contents = []
	document_contents = []
	page_contents = []
	audio_contents = []
	interactive_contents = []
	ebook_contents = []
	name = ""
	ob_id = ""
	gst_file = node_collection.one({'_type':"GSystemType", 'name': 'File'})

	# print "node_id:",node_id,"\n"
	obj = node_collection.one({'_id': ObjectId(node_id) })

	RT_teaches = node_collection.one({'_type':'RelationType', 'name': 'teaches'})
	RT_translation_of = node_collection.one({'_type':'RelationType','name': 'translation_of'})

	# "right_subject" is the translated node hence to find those relations which has translated nodes with RT 'translation_of'
	# These are populated when translated topic clicked.
	trans_grelations = triple_collection.find({'_type':'GRelation','right_subject':obj._id,'relation_type':RT_translation_of._id })
	# If translated topic then, choose its subject value since subject value is the original topic node for which resources are attached with RT teaches.
	if trans_grelations.count() > 0:
		obj = node_collection.one({'_id': ObjectId(trans_grelations[0].subject)})

	# If no translated topic then, take the "obj" value mentioned above which is original topic node for which resources are attached with RT teaches
	list_grelations = triple_collection.find({'_type': 'GRelation', 'right_subject': obj._id, 'relation_type': RT_teaches._id })

	for rel in list_grelations:
		rel_obj = node_collection.one({'_id': ObjectId(rel.subject)})

		if (rel_obj._type == "File") or (gst_file._id in rel_obj.member_of):
			gattr = node_collection.one({'_type': 'AttributeType', 'name': u'educationaluse'})
			# list_gattr = triple_collection.find({'_type': "GAttribute", 'attribute_type': gattr._id, "subject":rel_obj._id, 'object_value': selected })
			list_gattr = triple_collection.find({'_type': "GAttribute", 'attribute_type': gattr._id, "subject":rel_obj._id })

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
							elif attr.object_value == "eBooks":
								ebook_contents.append((name, ob_id))

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
						elif attr.object_value == "eBooks":
								ebook_contents.append((name, ob_id))


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

	if ebook_contents:
		contents['eBooks'] = ebook_contents

	# print "\n",contents,"\n"
	return contents


@get_execution_time
@register.assignment_tag
def get_topic_res_count(node_id):
	'''
	This function returns the count of resources holding by topic
	'''
	contents = {}
	image_contents = []
	video_contents = []
	document_contents = []
	page_contents = []
	audio_contents = []
	interactive_contents = []
	name = ""
	ob_id = ""

	# print "node_id: ",node_id,"\n"
	obj = node_collection.one({'_id': ObjectId(node_id) })

	RT_teaches = node_collection.one({'_type':'RelationType', 'name': 'teaches'})

	if obj.language == u"hi":
		# "right_subject" is the translated node hence to find those relations which has translated nodes with RT 'translation_of'
		# These are populated when translated topic clicked.
		trans_grelations = triple_collection.find({'_type':'GRelation','right_subject':obj._id,'relation_type':RT_translation_of._id })
		# If translated topic then, choose its subject value since subject value is the original topic node for which resources are attached with RT teaches.
		if trans_grelations.count() > 0:
			obj = node_collection.one({'_id': ObjectId(trans_grelations[0].subject)})

	# If no translated topic then, take the "obj" value mentioned above which is original topic node for which resources are attached with RT teaches
	list_grelations = triple_collection.find({'_type': 'GRelation', 'right_subject': obj._id, 'relation_type': RT_teaches._id })

	count = list_grelations.count()


	# print "count: ",count,"\n"
	return count


@get_execution_time
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

@get_execution_time
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

@get_execution_time
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
                            raise PermissionDenied(error_message)

                    else:
                        # Anonymous user found which cannot access groups other than Public
                        error_message = "\n Something went wrong: Either url is invalid or such group/user doesn't exists !!!\n"
                        raise PermissionDenied(error_message)

            else:
                # If Group is not found with either given ObjectId or name in the database
                # Then compare with a given list of names as these were used in one of the urls
                # And still no match found, throw error
                if g_id not in ["online", "i18n", "raw", "r", "m", "t", "new", "mobwrite", "admin", "benchmarker", "accounts", "Beta", "welcome", "explore"]:
                    error_message = "\n Something went wrong: Either url is invalid or such group/user doesn't exists !!!\n"
                    raise Http404(error_message)

        return True

    except PermissionDenied as e:
		raise PermissionDenied(e)

    except Http404 as e:
		raise Http404(e)


@get_execution_time
@register.assignment_tag
def get_possible_group_type_values():
	'''
	Returns TYPES_OF_GROUP defined in models.py
	'''
	return TYPES_OF_GROUP


@get_execution_time
@register.assignment_tag
def get_possible_edit_policy_values():
	'''
	Returns EDIT_POLICY defined in models.py
	'''
	return EDIT_POLICY


@get_execution_time
@register.assignment_tag
def get_allowed_moderation_levels():
	'''
	Returns GSTUDIO_ALLOWED_GROUP_MODERATION_LEVELS from settings.
	'''
	return GSTUDIO_ALLOWED_GROUP_MODERATION_LEVELS


@get_execution_time
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
@get_execution_time
@register.assignment_tag
def get_user_object(user_id):
	user_obj=""
	try:
		user_obj=User.objects.get(id=user_id)
	except Exception as e:
		print "User Not found in User Table",e
	return user_obj


@get_execution_time
@register.filter
def get_username(user_id):
	try:
		return User.objects.get(id=user_id).username
	except:
		return user_id


@get_execution_time
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

@get_execution_time
@register.inclusion_tag('ndf/admin_class.html')
def get_class_list(group_id,class_name):
	"""Get list of class
	"""
	class_list = ["GSystem", "File", "Group", "GSystemType", "RelationType", "AttributeType", "MetaType", "GRelation", "GAttribute"]
	return {'template': 'ndf/admin_class.html', "class_list": class_list, "class_name":class_name,"url":"data","groupid":group_id}


@get_execution_time
@register.inclusion_tag('ndf/admin_class.html')
def get_class_type_list(group_id,class_name):
	"""Get list of class
	"""
	class_list = ["GSystemType", "RelationType", "AttributeType","GSystem"]
	return {'template': 'ndf/admin_class.html', "class_list": class_list, "class_name":class_name,"url":"designer","groupid":group_id}

@get_execution_time
@register.assignment_tag
def get_Object_count(key):
		try:
				return node_collection.find({'_type':key}).count()
		except:
				return 'null'

@get_execution_time
@register.assignment_tag
def get_memberof_objects_count(request, key, group_id):
	try:
		lang = list(get_language_tuple(request.LANGUAGE_CODE))
		return node_collection.find({'member_of': {'$all': [ObjectId(key)]},'group_set': {'$all': [ObjectId(group_id)]}, 'language': lang}).count()
	except:
		return 'null'


'''Pass the ObjectId and get the name of it's first member_of element'''
@get_execution_time
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

@get_execution_time
@register.filter
def get_dict_item(dictionary, key):
	return dictionary.get(key)


@get_execution_time
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


@get_execution_time
@register.inclusion_tag('ndf/admin_fields.html')
def get_input_fields(fields_type, fields_name, translate=None ):
	"""Get html tags
	"""
	# field_type_list = ["meta_type_set","attribute_type_set","relation_type_set","prior_node","member_of","type_of"]
	return {"fields_name":fields_name, "fields_type": fields_type[0], "fields_value": fields_type[1],"translate":translate }
	# return {"fields_name":fields_name, "fields_type": fields_type[0], "fields_value": fields_type[1],
					# "field_type_list":field_type_list,"translate":translate }
	# return {'template': 'ndf/admin_fields.html',
	# 				"fields_name":fields_name, "fields_type": fields_type[0], "fields_value": fields_type[1],
	# 				"field_type_list":field_type_list,"translate":translate}


@get_execution_time
@register.inclusion_tag('ndf/fetch_fields.html')
def fetch_req_fields(fields_type, fields_name ):
	'''
	this ndf tag returns the fields_name and fields_type of the GSystem object
	for name and altname of the GS
	'''
	return {"fields_name":fields_name, "fields_type": fields_type[0] , "fields_value": fields_type[1] }

@get_execution_time
@register.inclusion_tag('ndf/fetch_fields.html')
def ats_fields(fields_type, fields_name,groupid,complex_dt,help_text,validators,filled_up=None):
	'''
	this ndf tag returns the fields_name and fields_type of the GSystem object -- ats
	'''
	fields_value = None
	if filled_up[1]:
		for each in filled_up[1]:
			for value in each:
				if value == fields_name:
					fields_value = each[value]
	regularexp = None
	for each in validators:
		regularexp = each

	return {"fields_name":fields_name, "fields_type": fields_type, "fields_value":fields_value ,'groupid':groupid,
	'complex_dt':complex_dt ,'gs_type':'attribute_set', 'help_text':help_text , 'validators':validators , 'regularexp':regularexp }

@get_execution_time
@register.inclusion_tag('ndf/fetch_fields.html')
def rts_fields(fields_name,fields_object_type,groupid,filled_up=None):
	'''
	this ndf tag returns the fields_name and fields_type of the GSystem object -- rts
	'''
	fields_value = None
	if filled_up[1]:
		for each in filled_up[1]:
			for value in each:
				if value == fields_name:
					fields_value = each[value]
	drawer1 = {}
	for each in fields_object_type:
		drawer1[each] = each
	return {"fields_name":fields_name, "groupid":groupid, "fields_object_type":fields_object_type
	,'gs_type':'relation_set' , "fields_value":fields_value , "drawer1":drawer1 }


@get_execution_time
@register.assignment_tag
def group_type_info(groupid,user=0):

	cache_key = "group_type_" + str(groupid)
	cache_result = cache.get(cache_key)

	if cache_result:
		return cache_result

	# group_gst = node_collection.one({'_id': ObjectId(groupid)},
	# 	{'post_node': 1, 'prior_node': 1, 'group_type': 1})
	group_gst = get_group_name_id(groupid, get_obj=True)

	if group_gst.post_node:
		group_type = "BaseModerated"
	elif group_gst.prior_node:
		group_type = "Moderated"
	else:
		group_type = group_gst.group_type

	if cache_result != group_type:
		cache.set(cache_key, group_type)

	return group_type


@get_execution_time
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

    if not user.is_authenticated:
        return "disallow"

    if user.is_superuser:
        user_access = True

    else:
      # group_node = node_collection.one({'_type': {'$in': ["Group", "Author"]}, '_id': ObjectId(node)})
      group_node = get_group_name_id(node, get_obj=True)
      # group_node = node_collection.one({"_id": ObjectId(group_id)})

      if user.id == group_node.created_by:
        user_access = True

      elif user.id in group_node.group_admin:
        user_access = True

      elif "PartnerGroup" in group_node.member_of_names_list:
        user_access = True

      elif group_node.edit_policy == "NON_EDITABLE":
        user_access = False

      elif user.id in group_node.author_set:
        user_access = True

      else:
        auth_obj = Author.get_author_by_userid(user.id)
        if auth_obj:
          if auth_obj.agency_type == 'Teacher':
            user_access = True
          elif auth_obj.agency_type == 'Student' and GSTUDIO_IMPLICIT_ENROLL:
            user_access = True

    if user_access:
      return "allow"

    else:
      return "disallow"

  except Exception as e:
    error_message = "\n UserAccessPolicyError: " + str(e) + " !!!\n"
    # raise Exception(error_message)
    return 'disallow'

@get_execution_time
@register.assignment_tag
def resource_info(node):
		col_Group=db[Group.collection_name]
		try:
			group_gst=col_Group.Group.one({'_id':ObjectId(node._id)})
		except:
			grname=re.split(r'[/=]',node)
			group_gst=col_Group.Group.one({'_id':ObjectId(grname[1])})
		return group_gst


@get_execution_time
@register.assignment_tag
def edit_policy(groupid,node,user):
	groupnode = node_collection.find_one({"_id":ObjectId(groupid)})
	# node=resource_info(node)
	#code for public Groups and its Resources
	resource_type = node_collection.find_one({"_id": {"$in":node.member_of}})
	if resource_type.name == 'Page':
		if node.type_of:
			resource_type_name = get_objectid_name(node.type_of[0])
			if resource_type_name == 'Info page':
				if user.id in groupnode.group_admin:
					return "allow"
			elif resource_type_name == 'Wiki page':
				return "allow"
			elif resource_type_name == 'Blog page':
				if user.id ==  node.created_by:
					return "allow"
		else:
			return "allow"
	else:
		return "allow"
	'''
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
	elif resource_infor.created_by:
							return "allow"
	'''
@get_execution_time
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

@get_execution_time
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

@get_execution_time
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

  group_name, group_id = Group.get_group_name_id(groupid)
  cache_key = 'is_gstaff' + str(group_id) + str(user.id)

  if cache_key in cache:
    return cache.get(cache_key)

  groupid = groupid if groupid else 'home'

  try:

    if group_id:
        group_node = Group.get_group_name_id(groupid, get_obj=True)
        result = group_node.is_gstaff(user)
        cache.set(cache_key, result, 60 * 60)
        return result

    else:
    	error_message = "No group exists with this id ("+str(groupid)+") !!!"
    	raise Exception(error_message)

  except Exception as e:
    error_message = "\n IsGStaffCheckError: " + str(e) + " \n"
    raise Http404(error_message)

@get_execution_time
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


@get_execution_time
@register.assignment_tag
def get_publish_policy(request, groupid, res_node):
	resnode = node_collection.one({"_id": ObjectId(res_node._id)})
	if resnode.status == "DRAFT":
		# node = node_collection.one({"_id": ObjectId(groupid)})
		group_name, group_id = get_group_name_id(groupid)
		node = node_collection.one({"_id": ObjectId(group_id)})
		group_type = group_type_info(groupid)
		group = user_access_policy(groupid,request.user)
		ver = ''
		try:
			ver = resnode.current_version
		except:
			pass

		if request.user.id:
			if group_type == "Moderated":
				base_group=get_prior_post_node(groupid)
                                #if base_group and (base_group[len(base_group) - 1] is not None):
                                # comment as it throws key error 45
                                if base_group :
					#if base_group[len(base_group) - 1].status == "DRAFT" or node.status == "DRAFT":
                                        if base_group.status == "DRAFT" or node.status == "DRAFT":
						return "allow"

			elif node.edit_policy == "NON_EDITABLE":
				if resnode._type == "Group":
					if (ver and (ver == "1.1")) or (resnode.created_by != request.user.id and not request.user.is_superuser):
						return "stop"
		        if group == "allow":
		        	if resnode.status == "DRAFT":
		        			return "allow"

			elif node.edit_policy == "EDITABLE_NON_MODERATED":
		        #condition for groups
				if resnode._type == "Group":
					if (ver and (ver == "1.1")) or (resnode.created_by != request.user.id and not request.user.is_superuser):
		            	# print "\n version = 1.1\n"
						return "stop"

		        if group == "allow":
		          # print "\n group = allow\n"
		          if resnode.status == "DRAFT":
		            return "allow"
	elif resnode.status == "MODERATION":
		return "MODERATION"

@get_execution_time
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
    file_gst = node_collection.one({'_type': "GSystemType", 'name': unicode(resource_type)})
    page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
    res_cur = node_collection.find({'_type': {'$in': [u"GSystem", u"File"]},
                                    'member_of': {'$in': [file_gst._id, page_gst._id]},
                                    'group_set': ObjectId(groupid),
                                    'collection_set': {'$exists': True, '$not': {'$size': 0}}
                                  })
    return res_cur

  except Exception as e:
    error_message = "\n CollectionsFindError: " + str(e) + " !!!\n"
    raise Exception(error_message)

@get_execution_time
@register.assignment_tag
def get_all_file_int_count():
	'''
	getting all the file/e-library type resource
	'''
	all_files = node_collection.find({ "_type": "File", "access_policy": "PUBLIC" })
	return all_files.count()

@get_execution_time
@register.assignment_tag
def app_translations(request, app_dict):
   app_id=app_dict['id']
   get_translation_rt = node_collection.one({'$and':[{'_type':'RelationType'},{'name':u"translation_of"}]})
   if request.LANGUAGE_CODE != GSTUDIO_SITE_DEFAULT_LANGUAGE:
      get_rel = triple_collection.one({'$and':[{'_type':"GRelation"},{'relation_type':get_translation_rt._id},{'subject':ObjectId(app_id)}]})
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

@get_execution_time
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

		if pref_lan.keys():
			if pref_lan['primary'] != request.LANGUAGE_CODE:
				uname.preferred_languages['primary'] = get_language_tuple(request.LANGUAGE_CODE)
				uname.save()

		else:
			pref_lan={}
			pref_lan['primary'] = get_language_tuple(request.LANGUAGE_CODE)
			pref_lan['default'] = ('en', 'English')
			uname.preferred_languages = pref_lan
			uname.save()
      else:
         pref_lan={}
         pref_lan['primary'] = get_language_tuple(request.LANGUAGE_CODE)
         pref_lan['default'] = ('en', 'English')
         uname.preferred_languages=pref_lan
         uname.save()
   else:
      pref_lan={}
      pref_lan[u'primary'] = get_language_tuple(request.LANGUAGE_CODE)

      pref_lan[u'default']= ('en', 'English')
   try:
      for each in nodes:
         get_rel = triple_collection.find({'$and':[{'_type':"GRelation"},{'relation_type':get_translation_rt._id},{'subject':each._id}]})
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
@get_execution_time
@register.assignment_tag
def get_pandoravideo_metadata(src_id):
  try:
    api=ox.api.API("http://wetube.gnowledge.org/api")
    data=api.get({"id":src_id,"keys":""})
    mdata=data.get('data')
    return mdata
  except Exception as e:
    return 'null'

@get_execution_time
@register.assignment_tag
def get_source_id(obj_id):
  try:
    source_id_at = node_collection.one({'$and':[{'name':'source_id'},{'_type':'AttributeType'}]})
    att_set = triple_collection.one({'_type': 'GAttribute', 'subject': ObjectId(obj_id), 'attribute_type': source_id_at._id})
    return att_set.object_value
  except Exception as e:
    return 'null'

@get_execution_time
def get_translation_relation(obj_id, translation_list = [], r_list = []):
   get_translation_rt = node_collection.one({'$and':[{'_type':'RelationType'},{'name':u"translation_of"}]})
   r_list_append_temp=r_list.append #a temp. variable which stores the lookup for append method
   translation_list_append_temp=translation_list.append#a temp. variable which stores the lookup
   if obj_id not in r_list:
      r_list_append_temp(obj_id)
      node_sub_rt = triple_collection.find({'$and':[{'_type':"GRelation"},{'relation_type':get_translation_rt._id},{'subject':obj_id}]})
      node_rightsub_rt = triple_collection.find({'$and':[{'_type':"GRelation"},{'relation_type':get_translation_rt._id},{'right_subject':obj_id}]})

      if list(node_sub_rt):
         node_sub_rt.rewind()
         for each in list(node_sub_rt):
            right_subject = node_collection.one({'_id':each.right_subject})
            if right_subject._id not in r_list:
               r_list_append_temp(right_subject._id)
      if list(node_rightsub_rt):
         node_rightsub_rt.rewind()
         for each in list(node_rightsub_rt):
            right_subject = node_collection.one({'_id':each.subject})
            if right_subject._id not in r_list:
               r_list_append_temp(right_subject._id)
      if r_list:
         r_list.remove(obj_id)
         for each in r_list:
            dic={}
            node = node_collection.one({'_id':each})
            dic[node._id]=node.language
            translation_list_append_temp(dic)
            get_translation_relation(each,translation_list, r_list)
   return translation_list


# returns object value of attribute
@get_execution_time
@register.assignment_tag
def get_object_value(node):
   at_set = ['contact_point','house_street','town_city','state','pin_code','email_id','telephone','website']
   att_name_value= OrderedDict()

   for each in at_set:
      attribute_type = node_collection.one({'_type':"AttributeType" , 'name':each})
      if attribute_type:
      	get_att = triple_collection.one({'_type':"GAttribute", 'subject':node._id, 'attribute_type': attribute_type._id})
      	if get_att:
        	att_name_value[attribute_type.altnames] = get_att.object_value

   return att_name_value


@get_execution_time
@register.assignment_tag
# return json data of object
def get_json(node):
   node_obj = node_collection.one({'_id':ObjectId(str(node))})
   return json.dumps(node_obj, cls=NodeJSONEncoder, sort_keys = True)


@get_execution_time
@register.filter("is_in")
# filter added to test if vaiable is inside of list or dict
def is_in(var, args):
    if args is None:
        return False
    arg_list = [arg.strip() for arg in args.split(',')]
    return var in arg_list


@get_execution_time
@register.filter("del_underscore")
# filter added to remove underscore from string
def del_underscore(var):
   var = var.replace("_"," ")
   return var

@get_execution_time
@register.assignment_tag
# this function used for info-box implementation
# which convert str to dict type & returns dict which used for rendering in template
def str_to_dict(str1):
    dict_format = json.loads(str1, object_pairs_hook = OrderedDict)
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
                      # if v != [] and v != "None":
                      if v:
                      		  if User.objects.filter(id = v).exists():
	                              user = User.objects.get(id = v)
	                              if user:
	                                dict_format[k] = user.get_username()

      if k in keys_by_dict:
              att_dic = {}
              if "None" not in dict_format[k]:
                      if type(dict_format[k]) != str and k == "attribute_set":
                              for att in dict_format[k]:
                                      for k1, v1 in att.items():
                                        if type(v1) == list:
                                                str1 = ""
                                                if type(v1[0]) in [OrderedDict, dict]:
                                                    for each in v1:
                                                        str1 += each["name"] + ", "
                                                else:
                                                    str1 = ",".join(v1)
                                                att_dic[k1] = str1
                                                dict_format[k] = att_dic
                                        else:
                                                att_dic[k1] = v1
                                                dict_format[k] = att_dic
                      if k == "relation_set":
                              for each in dict_format[k]:
                                      for k1, v1 in each.items():
                                              for rel in v1:
                                                      rel = node_collection.one({'_id':ObjectId(rel)})
                                                      if rel:
                                                      	att_dic[k1] = rel.name
                                      dict_format[k] = att_dic

      if k in keys_by_filesize:
              filesize_dic = {}
              for k1, v1 in dict_format[k].items():
                      filesize_dic[k1] = v1
              dict_format[k] = filesize_dic
    order_dict_format = OrderedDict()
    order_val=['altnames','language','plural','_type','member_of','created_by','created_at','tags','modified_by','author_set','group_set','collection_set','contributors','last_update','start_publication','location','legal','attribute_set','relation_set']
    for each in order_val:
            order_dict_format[each]=dict_format[each]
    return order_dict_format

@get_execution_time
@register.assignment_tag
def get_possible_translations(obj_id):
        translation_list = []
	r_list1 = []
        return get_translation_relation(obj_id._id,r_list1,translation_list)


#textb
@get_execution_time
@register.filter("mongo_id")
def mongo_id(value):
		 # Retrieve _id value
		if type(value) == type({}):
				if value.has_key('_id'):
						value = value['_id']

		# Return value
		return unicode(str(value))

'''
@get_execution_time
@register.simple_tag
def check_existence_textObj_mobwrite(node_id):
	# to check object already created or not, if not then create
	# input nodeid
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
'''

@get_execution_time
@register.assignment_tag
def get_version_of_module(module_id):
	''''
	This method will return version number of module
	'''
	ver_at = node_collection.one({'_type':'AttributeType','name':'version'})
	if ver_at:
		attr = triple_collection.one({'_type':'GAttribute','attribute_type':ver_at._id,'subject':ObjectId(module_id)})
		if attr:
			return attr.object_value
		else:
			return ""
	else:
		return ""

@get_execution_time
@register.assignment_tag
def get_group_name(groupid):
	# group_name, group_id = get_group_name_id(groupid)
	return get_group_name_id(groupid)[0]


@register.filter
def concat(value1, value2):
    """concatenate multiple received args
    """
    return_str = value1.__str__()
    value2 = value2.__str__()
    return return_str + value2


@get_execution_time
@register.filter
def get_field_type(node_structure, field_name):
  """Returns data-type value associated with given field_name.
  """
  return node_structure.get(field_name)

@get_execution_time
@register.inclusion_tag('ndf/html_field_widget.html')
# def html_widget(node_id, field, field_type, field_value):
# def html_widget(node_id, node_member_of, field, field_value):
def html_widget(groupid, node_id, field,node_content=None):
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
    # field_value = field['value']
    field_value = None

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
      is_required_field = None
      # is_required_field = field["required"]

    elif is_AT_RT_base == "RelationType":
      is_relation_field = True
      is_required_field = True
      #patch
      group = node_collection.one({"_id":ObjectId(groupid)})
      group_users = []
      group_users.extend(group.group_admin)
      group_users.extend(group.author_set)
      group_users.append(group.created_by)
      # print "*************************",group.created_by
      person = node_collection.find({"_id":{'$in': field["object_type"]}},{"name":1})

      if person[0].name == "Author":
          if field.name == "has_attendees":
              field_value_choices.extend(list(node_collection.find({'_type': 'Author',
                                                                  'created_by':{'$in':group_users},

                                                                 })
                                                                 ))
          else:
              field_value_choices.extend(list(node_collection.find({'_type': 'Author',
                                                                  'created_by':{'$in':group_users},

                                                                 })
                                                                 ))      #End path
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
            'is_required_field': is_required_field,
            'node_content':node_content
            # 'is_special_tab_field': is_special_tab_field
    }

  except Exception as e:
    error_message = " HtmlWidgetTagError: " + str(e) + " !!!"
    raise Exception(error_message)

@get_execution_time
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

@get_execution_time
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

@get_execution_time
@register.filter(name='jsonify')
def jsonify(value):
    """Parses python value into json-type (useful in converting
    python list/dict into javascript/json object).
    """

    return json.dumps(value, cls=NodeJSONEncoder)

@get_execution_time
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

@get_execution_time
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

@get_execution_time
@register.assignment_tag
def get_filters_data(gst_name, group_name_or_id='home'):
	'''
	Returns the static data needed by filters. The data to be return will in following format:
	{
		"key_name": { "data_type": "<int>/<string>/<...>", "type": "attribute/field", "value": ["val1", "val2"]},
		... ,
		... ,
		"key_name": { "data_type": "<int>/<string>/<...>", "type": "attribute/field", "value": ["val1", "val2"]}
	}
	'''

	group_id, group_name = get_group_name_id(group_name_or_id)

	static_mapping = {
                    "educationalsubject": GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT,
                    "language": GSTUDIO_RESOURCES_LANGUAGES,
                    "educationaluse": GSTUDIO_RESOURCES_EDUCATIONAL_USE,
                    "interactivitytype": GSTUDIO_RESOURCES_INTERACTIVITY_TYPE,
                    # "educationalalignment": GSTUDIO_RESOURCES_EDUCATIONAL_ALIGNMENT,
                    "educationallevel": GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL,
                    # "curricular": GSTUDIO_RESOURCES_CURRICULAR,
                    "audience": GSTUDIO_RESOURCES_AUDIENCE,
                    # "textcomplexity": GSTUDIO_RESOURCES_TEXT_COMPLEXITY
				}

	# following attr's values need to be get/not in settings:
	# timerequired, other_contributors, creator, age_range, readinglevel, adaptation_of, source, basedonurl

	filter_dict = {}

	# gst = node_collection.one({'_type':"GSystemType", "name": unicode(gst_name)})
	gst = node_collection.one({'_type':"GSystemType", "name": unicode('File')})
	poss_attr = gst.get_possible_attributes(gst._id)
	# print gst_name, "============", gst.name

	filter_parameters = []
	# filter_parameters = GSTUDIO_FILTERS.get('File', [])
	filter_parameters = GSTUDIO_FILTERS.get(gst_name, [])[:]
	# print GSTUDIO_FILTERS
	# print filter_parameters

	exception_list = ["interactivitytype"]

	for k, v in poss_attr.iteritems():

		# if (k in exception_list) or not static_mapping.has_key(k):
		if (k in exception_list) or (k not in filter_parameters):
			continue

		# print k
		if static_mapping.has_key(k):
			fvalue = static_mapping.get(k, [])
		else:
			# print "================----"
			at_set_key = 'attribute_set.' + k
			group_obj = node_collection.one({"name":group_id,"_type":"Group"})
			all_at_list = node_collection.find({at_set_key: {'$exists': True, '$nin': ['', 'None', []], },"group_set":ObjectId(group_obj._id) }).distinct(at_set_key)

			fvalue = all_at_list

		filter_dict[k] = {
	    					"data_type": v["data_type"].__name__,
	    					"altnames": v['altnames'],
	    					"type" : "attribute",
	    					"value": json.dumps(fvalue)
	    				}

		try:
			filter_parameters.pop(filter_parameters.index(k))
		except Exception, e:
			pass

		# print filter_parameters

	# additional filters:

	filter_dict["Language"] = {
								"data_type": "basestring", "type": "field",
								"value": json.dumps(static_mapping["language"])
							}


	try:
		filter_parameters.pop(filter_parameters.index('language'))
	except Exception, e:
		pass

	if filter_parameters:
		gst_structure = gst.structure
		gst_structure_keys = gst.structure.keys()

		for each_fpara in filter_parameters:
			if each_fpara in gst_structure_keys:
				fvalue = node_collection.find({'group_set': {'$in': [ObjectId(group_id)]}, 'member_of': {'$in': [gst._id]} }).distinct(each_fpara)

				if fvalue:
					filter_dict[each_fpara] = {
											'data_type': gst_structure[each_fpara],
											'type': 'field',
											'value': json.dumps(value)
										}

	# print "@@@ ", filter_dict
	return filter_dict


def sorted_ls(path):
    '''
    takes {
        path : Path to the folder location
    }
    returns {
        list of file-names sorted based on time
    }
    '''
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))


@get_execution_time
@register.assignment_tag
def get_sg_member_of(group_id):
	'''
	Returns list of names of "member_of" of sub-groups.
	- Takes group_id as compulsory and only argument.
	'''

	sg_member_of_list = []
	# get all underlying groups
	try:
		group_id = ObjectId(group_id)
	except:
		group_id, group_name = get_group_name_id(group_id)

	group_obj = node_collection.one({'_id': ObjectId(group_id)})
	# print group_obj.name
	# Fetch post_node of group
	if group_obj:
		if "post_node" in group_obj:
			post_node_id_list = group_obj.post_node

			if post_node_id_list:
				# getting parent's sub group's member_of in a list
				for each_sg in post_node_id_list:
					each_sg_node = node_collection.one({'_id': ObjectId(each_sg)})
					if each_sg_node:
						sg_member_of_list.extend(each_sg_node.member_of_names_list)
		# print "\n\n sg_member_of_list---",sg_member_of_list
	return sg_member_of_list


def get_objectid_name(nodeid):
	return (node_collection.find_one({'_id':ObjectId(nodeid)}).name)


@register.filter
def is_dict(val):
    return isinstance(val, dict)

@register.filter
def is_empty(val):
    if val == None :
    	return 1
    else :
    	return 0


@get_execution_time
@register.inclusion_tag('ndf/breadcrumb.html')
def get_breadcrumb(url):

	url = url.strip()

	exception_list= [
						'welcome', 'accounts', 'admin', '/dashboard',
						'/partner/partners', '/partner/groups', '/group/'
					]
	path = []
	apps = GAPPS + ['repository']

	# print "===========", map(lambda x: x in url.lower(), exception_list)
	if not any(map(lambda x: x in url.lower(), exception_list)):
		# print url

		url_list = filter(lambda x: x != "", url.split('/'))

		try:

			# --- first element: group name ---
			first_el = url_list[0]
			group_obj = get_group_name_id(first_el, get_obj=True)
			# print "00000000000000000", first_el
			first_group_name = group_obj.altnames if group_obj.altnames else group_obj.name
			first_group_url = '/' + group_obj.name
			# if group_obj.name == 'home':
			# 	first_group_url += '/repository'

			path.append({'name': first_group_name, 'link': first_group_url})
			# print path

			# --- second element: app name ---
			second_el = url_list[1]
			if any(map(lambda x: x == second_el, [i.lower() for i in apps])):
				try:
					temp_obj = node_collection.one({'_type': 'GSystemType',
						'name': {'$regex': second_el, '$options': 'i'} })
					second_app_name = temp_obj.altnames if temp_obj.altnames else temp_obj.name
				except:
					second_app_name = second_el
				# print second_el,"second_app_name: ", second_app_name
				second_app_url = first_group_url + '/' + second_el
				path.append({'name': second_app_name, 'link': second_app_url})

				# --- third element: object/instance id ---
				third_el = url_list[2]
				if ObjectId.is_valid(third_el):
					node_obj = node_collection.one({'_id': ObjectId(third_el)})
					third_node_name = node_obj.name
					third_node_url = second_app_name + '/' + third_el
					path.append({'name': third_node_name, 'link': third_node_url})
				# else:
				# 	third_node_name =

				# --- fourth element: object/instance id ---
				fourth_el = url_list[3]
				if ObjectId.is_valid(fourth_el):
					node_obj = node_collection.one({'_id': ObjectId(fourth_el)})
					fourth_node_name = node_obj.name
					fourth_node_url = second_app_name + '/' + fourth_el
					path.append({'name': fourth_node_name, 'link': fourth_node_url})

		except:
			pass

	# print 'path : ', path
	return {'path': path if (len(path) > 1) else []}



@get_execution_time
@register.assignment_tag
def get_thread_node(node_id):
	if node_id:
		node_obj = node_collection.one({'_id': ObjectId(node_id)})
		thread_obj = None
		has_thread_rt = node_collection.one({'_type': 'RelationType', 'name': 'has_thread'})
		thread_rt = triple_collection.find_one({'subject': ObjectId(node_id),
			'relation_type': has_thread_rt._id, 'status': u'PUBLISHED'})
		if thread_rt:
			thread_id = thread_rt['right_subject']
			if thread_id:
				thread_obj = node_collection.one({'_id': ObjectId(thread_id)})

		# if node_obj.relation_set:
		# 	for rel in node_obj.relation_set:
		# 		if rel and 'has_thread' in rel:
		# 			thread_obj = rel['has_thread'][0]
		# print "\n\nthread_obj--",thread_obj
		return thread_obj
	return None


@get_execution_time
@register.filter
def is_media_collection(node_id):
    """To check whether all the items of collection_set are
    of Image or of Video.

    Args:
        node_id (ObjectId): _id of node whose collection_set to be checked for.

    Returns:
        bool: Returns True if all the items are of type Image or Video.
        Else returns False.
    """

    node_obj = node_collection.one({'_id': ObjectId(node_id)})

    if node_obj.collection_set:
	    cur = node_collection.find({'_id': {'$in': node_obj.collection_set} })

	    mimetype_list = [f.mime_type for f in cur if (f.mime_type and (f.mime_type.split('/')[0].lower() in ['image', 'video']) )]
	    # print "==", mimetype_list

	    # print len(node_obj.collection_set), len(mimetype_list)
	    if len(node_obj.collection_set) == len(mimetype_list):
		    return True
    return False

@get_execution_time
@register.assignment_tag
def get_all_subsections_of_course(group_id, node_id):
	node_obj = node_collection.one({'_id': ObjectId(node_id)})
	css = []
	if node_obj.collection_set:
		for each_node in node_obj.collection_set:
			each_node_obj = node_collection.one({'_id': ObjectId(each_node)})
			if each_node_obj and "CourseSectionEvent" in each_node_obj.member_of_names_list:
				if each_node_obj.collection_set:
					for each_node in each_node_obj.collection_set:
						each_css = node_collection.one({'_id': ObjectId(each_node)})
						if "CourseSubSectionEvent" in each_css.member_of_names_list:
							d = {'name':str(each_css.name),'id':str(each_css._id)}
							date_val = get_attribute_value(each_css._id,"start_time")
							if date_val:
								d['start_time'] = date_val.strftime("%d/%m/%Y")
							css.append(d)
	return css


@get_execution_time
@register.assignment_tag
def get_list_of_fields(oid_list, field_name='name'):
	if oid_list:
		cur = node_collection.find({'_id': {'$in': oid_list} }, {field_name: 1, '_id': 0})
		return [doc[field_name] for doc in cur]
	else:
		return []


@get_execution_time
@register.assignment_tag
def convert_list(value):
	#convert list of list to list
	return list(itertools.chain(*value))


@get_execution_time
@register.assignment_tag
def get_topic_breadcrumb_hierarchy(oid):

	nodes_cur = get_prior_node_hierarchy(oid)
	# removing top theme id
	nodes_cur.pop()
	nodes_cur_list = [n._id for n in nodes_cur]
	nodes_cur_list.reverse()

	comma_sep_str = ""
	for each_t in nodes_cur_list:
		comma_sep_str += each_t.__str__() + ","

	# print "comma_sep_str : ", comma_sep_str
	comma_sep_str = comma_sep_str[:-1]
	return comma_sep_str

@get_execution_time
@register.assignment_tag
def get_gstudio_help_sidebar():
	return GSTUDIO_HELP_SIDEBAR

@get_execution_time
@register.assignment_tag
def get_is_captcha_visible():
	return GSTUDIO_CAPTCHA_VISIBLE

@get_execution_time
@register.assignment_tag
def get_gstudio_twitter_via():
	return GSTUDIO_TWITTER_VIA

@get_execution_time
@register.assignment_tag
def get_gstudio_facebook_app_id():
	return GSTUDIO_FACEBOOK_APP_ID

@get_execution_time
@register.assignment_tag
def get_gstudio_social_share_resource():
	return GSTUDIO_SOCIAL_SHARE_RESOURCE


@get_execution_time
@register.assignment_tag
def get_ebook_help_text():
	return GSTUDIO_EBOOKS_HELP_TEXT

@get_execution_time
@register.assignment_tag
def get_gstudio_interaction_types():
	return GSTUDIO_INTERACTION_TYPES

@get_execution_time
@register.assignment_tag
def get_explore_url():
	return GSTUDIO_DEFAULT_EXPLORE_URL

@get_execution_time
@register.assignment_tag
def is_partner(group_obj):
	try:
		result = False
		partner_spaces = ["State Partners", "Individual Partners", "Institutional Partners"]
		if group_obj.name in partner_spaces:
			result = True
		return result
	except:
		return result

@get_execution_time
@register.assignment_tag
def get_event_status(node):
	status_msg = None
	"""
	Returns FORTHCOMING/OPEN/CLOSED
	"""
	if node:
		start_time_val = get_attribute_value(node._id,"start_time")
		end_time_val = get_attribute_value(node._id,"end_time")
		start_enroll_val = get_attribute_value(node._id,"start_enroll")
		end_enroll_val = get_attribute_value(node._id,"end_enroll")
		from datetime import datetime
		curr_date_time = datetime.now()
		if start_time_val and end_time_val and start_enroll_val and end_enroll_val:
			if curr_date_time.date() >= start_time_val.date() and curr_date_time.date() <= end_time_val.date() \
			or curr_date_time.date() >= start_enroll_val.date() and curr_date_time.date() <= end_enroll_val.date():
				status_msg = "in-progress"
			elif curr_date_time.date() < start_time_val.date() or curr_date_time.date() < start_enroll_val.date():
				status_msg = "upcoming"
			elif curr_date_time.date() > end_time_val.date() or curr_date_time.date() > end_enroll_val.date():
				status_msg = "completed"
	return status_msg


# @get_execution_time
# @register.assignment_tag
# def get_all_user_groups(user_id):

# 	user_id = int(user_id)

# 	gst_modg = node_collection.one({'_type': 'GSystemType', 'name': u'ModeratingGroup'})

# 	all_user_groups = node_collection.find({
# 				'_type': 'Group',
# 				'$or':[
# 						{'author_set': {'$in': [user_id]}},
# 						{'group_admin': {'$in': [user_id]}},
# 						{'created_by': user_id} #,
# 						# {'group_type': u'PUBLIC'}
# 					],
# 				'member_of': {'$nin': [gst_modg._id]}
# 				})

# 	return all_user_groups


@get_execution_time
@register.assignment_tag
def get_user_course_groups(user_id):

	user_id = int(user_id) if user_id else user_id

	gst_course = node_collection.one({'_type': 'GSystemType', 'name': u'CourseEventGroup'})

	all_user_groups = node_collection.find({
				'_type': 'Group',
				'$or':[
						{'author_set': {'$in': [user_id]}},
						{'group_admin': {'$in': [user_id]}},
						{'created_by': user_id} #,
						# {'group_type': u'PUBLIC'}
					],
				'member_of': {'$in': [gst_course._id]}
				})

	# all_courses = []

	all_courses_obj_grouped = {
							# 'all': [],
							'in-progress': [],
							'upcoming': [],
							'completed': []
						}

	courses_status_count_dict = {
							'all': all_user_groups.count(),
							'in-progress': 0,
							'upcoming': 0,
							'completed': 0
						}

	for each_course in all_user_groups:
		status_val = get_event_status(each_course)
		if status_val:
			each_course.course_status_field = status_val
			all_courses_obj_grouped[each_course.course_status_field].append(each_course)
			# all_courses_obj_grouped['all'].append(each_course)

			courses_status_count_dict[each_course.course_status_field] += 1

			# all_courses.append(each_course)

	# print "::: ", courses_status_count_dict
	# print "::: ", all_courses_obj_grouped
	return all_courses_obj_grouped

@get_execution_time
@register.assignment_tag
def get_course_session_status(node, get_current=False):

	"""
	Returns Session Start_time in Courses
	"""
	status = ""
	upcoming_course = False
	session_name = None
	if node:
		from datetime import datetime
		curr_date_time = datetime.now()
		start_time_val = get_attribute_value(node._id,"start_time")
		end_time_val = get_attribute_value(node._id,"end_time")

		if start_time_val and end_time_val:
			# print "\n start_time_val -- ", start_time_val
			# print "\n start_time_val type -- ", type(start_time_val)
			# convert to str
			start_time_val_str = start_time_val.strftime("%d/%m/%Y")
			end_time_val_str = end_time_val.strftime("%d/%m/%Y")
			# convert to datetime obj
			start_time_val = datetime.strptime(start_time_val_str,"%d/%m/%Y")
			end_time_val = datetime.strptime(end_time_val_str,"%d/%m/%Y")
			if curr_date_time.date() < start_time_val.date():
				upcoming_course = True
		if get_current:
			session_name = "Data Not Available"
		if node:
			for each_course_section in node.collection_set:
				each_course_section_node = node_collection.one({"_id":ObjectId(each_course_section)})
				if each_course_section_node:
					for each_course_subsection in each_course_section_node.collection_set:
						each_course_subsection_node = node_collection.one({"_id":ObjectId(each_course_subsection)})
						each_sub_section_start_time = get_attribute_value(each_course_subsection_node._id,"start_time")
						# print "each_sub_section_start_time",each_sub_section_start_time
						if each_sub_section_start_time:
							if curr_date_time.date() <= each_sub_section_start_time.date():
								status =  each_sub_section_start_time
								session_name = each_course_subsection_node.name
								if get_current:
									return session_name, status
								return status, upcoming_course
		if get_current:
			return session_name, status

		# print upcoming_course,node.name
		return status, upcoming_course

@get_execution_time
@register.assignment_tag
def get_user_quiz_resp(node_obj, user_obj):
	'''
	Accepts:
		* node_obj
			QuizItemEvent Object
		* user_obj
			django user object

	Actions:
		* Fetches QuizItemPost of user, i.e user's
		 quizitem response(answer)

	Returns:
		* Recently answered value.
		* Total count of answers for this particular
		 node_obj/QuizItemEvent

	'''
	result = {'count': 0, 'recent_ans': None}
	thread_obj = None
	if node_obj and user_obj:
		try:
			from gnowsys_ndf.ndf.templatetags.ndf_tags import get_thread_node
			thread_obj = get_thread_node(node_obj._id)

			# grel_dict = get_relation_value(node_obj._id,"has_thread", True)
			# is_cursor = grel_dict.get("cursor",False)
			# if not is_cursor:
			# 	thread_obj = grel_dict.get("grel_node")

			# for each_rel in node_obj.relation_set:
			# 	if each_rel and "has_thread" in each_rel:
			# 		thread_id = each_rel['has_thread'][0]
			# 		thread_obj = node_collection.one({'_id': ObjectId(thread_id)})
		except:
			pass
		if thread_obj:
			# print "\n thread_obj.post_node: ",thread_obj._id
			qip = node_collection.one({'_id':{'$in': thread_obj.post_node}, 'created_by': user_obj.id})
			# print "\nqip= ",qip.count()
			if qip:
				qip_sub = get_attribute_value(qip._id,'quizitempost_user_submitted_ans')
				if qip_sub:
					result['count'] = len(qip_sub)
					recent_ans = qip_sub[-1]
					result['recent_ans'] = recent_ans
					user_ans = recent_ans.values()[0]
					# result['recent_ans'] = (map(unicode,[re.sub(r'[\t\n\r]', '', u_ans) for u_ans in user_ans]))
					# result['recent_ans'] = [u_ans.decode('utf-8').decode('utf-8') for u_ans in user_ans]
					result['recent_ans'] = user_ans
		# return json.dumps(result,ensure_ascii=False)
		return result

@get_execution_time
@register.assignment_tag
def get_course_filters(group_id, filter_context):
	'''
	Returns the static data needed by filters. The data to be return will in following format:
	{
		"key_name": { "data_type": "<int>/<string>/<...>", "type": "attribute/field", "value": ["val1", "val2"]},
		... ,
		... ,
		"key_name": { "data_type": "<int>/<string>/<...>", "type": "attribute/field", "value": ["val1", "val2"]}
	}
	'''
	group_obj   = get_group_name_id(group_id, get_obj=True)
	filters_dict = {}
	gstaff_users = []
	all_user_objs = None
	all_users = False
	only_gstaff = False
	all_user_objs_uname = all_user_objs_id = None
	file_gst = node_collection.one({'_type': 'GSystemType', 'name': u'File'})
	if filter_context.lower() == "raw material":
		only_gstaff = True
	elif filter_context.lower() == "notebook":
		all_users = True

	for each_course_filter_key in GSTUDIO_COURSE_FILTERS_KEYS:
		if each_course_filter_key == "created_by":
			author_set_list = group_obj.author_set
			all_user_objs = User.objects.filter(id__in=author_set_list)
			filters_dict[each_course_filter_key] = {'type': 'field', 'data_type': 'basestring', 'altnames': 'User'}
			if not all_users:
				if only_gstaff:
					all_user_objs_uname = [eachuser.username for eachuser in all_user_objs if check_is_gstaff(group_obj._id,eachuser)]
				else:
					all_user_objs_uname = [eachuser.username for eachuser in all_user_objs if not check_is_gstaff(group_obj._id,eachuser)]
			else:
				all_user_objs_uname = list(all_user_objs.values_list('username', flat=True).order_by('username'))

			# Type-Cast from 'QuerySet' to 'list' to make it JSON serializable
			# all_user_names = list(all_user_objs.values_list('username', flat=True).order_by('username'))
			filters_dict[each_course_filter_key].update({'value': json.dumps(all_user_objs_uname)})

		# if each_course_filter_key == "tags" and filter_context.lower() == "notebook":
		if each_course_filter_key == "tags":
			# gstaff_users.extend(group_obj.group_admin)
			# gstaff_users.append(group_obj.created_by)
			all_superusers = User.objects.filter(is_superuser=True)
			all_superusers_ids = all_superusers.values_list('id',flat=True)
			gstaff_users.extend(group_obj.group_admin)
			gstaff_users.append(group_obj.created_by)
			gstaff_users.extend(all_superusers_ids)



			all_tags_list = [] # To prevent if no tags are found in any blog pages
			filters_dict[each_course_filter_key] = {'type': 'field', 'data_type': 'basestring', 'altnames': 'Tags'}

			if filter_context.lower() == "notebook":
				page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
				blogpage_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"})
				result_cur = node_collection.find({'member_of':page_gst._id, 'type_of': blogpage_gst._id,
							'group_set': group_obj._id, 'tags':{'$exists': True, '$not': {'$size': 0}} #'tags':{'$exists': True, '$ne': []}}
							},{'tags': 1, '_id': False})
			elif filter_context.lower() == "notebook_lms":
				page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
				blogpage_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"})
				result_cur = node_collection.find({'member_of':page_gst._id, 'type_of': blogpage_gst._id,
							'group_set': group_obj._id, 'tags':{'$exists': True, '$not': {'$size': 0}} #'tags':{'$exists': True, '$ne': []}}
							},{'tags': 1, '_id': False})

			elif filter_context.lower() == "gallery":
				# all_user_objs_id = [eachuser.id for eachuser in all_user_objs]
				result_cur = node_collection.find({'member_of': file_gst._id,'group_set': group_obj._id,
							'tags':{'$exists': True, '$not': {'$size': 0}},#'tags':{'$exists': True, '$ne': []}},
							'created_by': {'$nin': gstaff_users}
							},{'tags': 1, '_id': False})

			elif filter_context.lower() == "raw material":
				# all_user_objs_id = [eachuser.id for eachuser in all_user_objs if check_is_gstaff(group_obj._id,eachuser)]
				result_cur = node_collection.find({'member_of': file_gst._id,'group_set': group_obj._id,
							'tags':{'$exists': True, '$not': {'$size': 0}},#'tags':{'$exists': True, '$ne': []}},
							'created_by': {'$in': gstaff_users}
							},{'tags': 1, '_id': False})

			elif filter_context.lower() == "raw_material_lms":
				# all_user_objs_id = [eachuser.id for eachuser in all_user_objs if check_is_gstaff(group_obj._id,eachuser)]
				asset_gst_name, asset_gst_id = GSystemType.get_gst_name_id("Asset")
				result_cur = node_collection.find({'member_of': {'$in': [asset_gst_id]},
            'group_set': {'$all': [ObjectId(group_id)]},'tags':'raw@material'}).sort('last_update', -1)

			elif filter_context.lower() == "gallery_lms":
				# all_user_objs_id = [eachuser.id for eachuser in all_user_objs if check_is_gstaff(group_obj._id,eachuser)]
				asset_gst_name, asset_gst_id = GSystemType.get_gst_name_id("Asset")
				result_cur = node_collection.find({'member_of': {'$in': [asset_gst_id]},
				'group_set': {'$all': [ObjectId(group_id)]},'tags':'asset@gallery'}).sort('last_update', -1)

			elif filter_context.lower() == "assets_lms":
				# all_user_objs_id = [eachuser.id for eachuser in all_user_objs if check_is_gstaff(group_obj._id,eachuser)]
				asset_gst_name, asset_gst_id = GSystemType.get_gst_name_id("Asset")
				result_cur = node_collection.find({'member_of': {'$in': [asset_gst_id]},
				'group_set': {'$all': [ObjectId(group_id)]},'tags':'asset@asset'}).sort('last_update', -1)

			# print "\n\n result_cur.count()--",result_cur.count()
			# all_tags_from_cursor = map(lambda x: x['tags'], result_cur)
			# # # all_tags_from_cursor is a list having nested list
			# all_tags_list = list(itertools.chain(*all_tags_from_cursor))
			# if all_tags_list:
			# 	all_tags_list = json.dumps(all_tags_list)
			distinct_res_cur = result_cur.distinct('tags')
			if 'raw@material' in distinct_res_cur:
				distinct_res_cur.remove('raw@material')
			if 'asset@gallery' in distinct_res_cur:
				distinct_res_cur.remove('asset@gallery')
			if 'asset@asset' in distinct_res_cur:
				distinct_res_cur.remove('asset@asset')
			filters_dict[each_course_filter_key].update({'value': json.dumps(distinct_res_cur)})
	return filters_dict


@get_execution_time
@register.assignment_tag
def get_info_pages(group_id):
	list_of_nodes = []
	page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
	info_page_gst = node_collection.one({'_type': "GSystemType", 'name': "Info page"})
	info_page_nodes = node_collection.find({'member_of': page_gst._id, 'type_of': info_page_gst._id, 'group_set': ObjectId(group_id)})
	# print "\n\n info_page_nodes===",info_page_nodes.count()
	# if info_page_nodes.count():
	# 	for eachnode in info_page_nodes:
	# 		list_of_nodes.append({'name': eachnode.name,'id': eachnode._id})
	return info_page_nodes


@get_execution_time
@register.assignment_tag
def get_download_filename(node, file_size_name='original'):

	extension = None
	if hasattr(node, 'if_file') and node.if_file[file_size_name].relurl:
		from django.template.defaultfilters import slugify
		relurl = node.if_file[file_size_name].relurl
		relurl_split_list = relurl.split('.')

		if len(relurl_split_list) > 1:
			extension = "." + relurl_split_list[-1]
		elif 'epub' in node.if_file.mime_type:
			extension = '.epub'
		elif not extension:
			file_hive_obj = filehive_collection.one({'_id':ObjectId(node.if_file.original.id)})
			file_blob = node.get_file(node.if_file.original.relurl)
			file_mime_type = file_hive_obj.get_file_mimetype(file_blob)
			extension = mimetypes.guess_extension(file_mime_type)
		else:
			extension = mimetypes.guess_extension(node.if_file.mime_type)

		name = node.altnames if node.altnames else node.name
		name = name.split('.')[0]
		file_name = slugify(name)

		if extension:
			file_name += extension

		return file_name

	else:
		name = node.altnames if node.altnames else node.name

		return name


@get_execution_time
@register.assignment_tag
def get_file_obj(node):
	obj = node_collection.find_one({"_id": ObjectId(node._id)})
	# print "\n\nobj",obj
	if obj.if_file.original.id:
		original_file_id = obj.if_file.original.id
		original_file_obj = filehive_collection.find_one({"_id": ObjectId(obj.if_file.original.id)})
		return original_file_obj

@get_execution_time
@register.assignment_tag
def get_help_pages_of_node(node_obj,rel_name="has_help",language="en"):
	all_help_page_node_list = []
	from gnowsys_ndf.ndf.views.translation import get_lang_node
	try:
		has_help_rt = node_collection.one({'_type': 'RelationType', 'name': rel_name})
		help_rt = triple_collection.find({'subject':node_obj._id,'relation_type': has_help_rt._id, 'status': u'PUBLISHED'})
		if help_rt:
			for each_help_rt in help_rt:
				# print each_help_rt.right_subject
				help_pg_node = node_collection.one({'_id':ObjectId(each_help_rt.right_subject)})
				trans_node =   get_lang_node(help_pg_node._id,language)
				help_pg_node =  trans_node or help_pg_node 
				if help_pg_node:
					all_help_page_node_list.append(help_pg_node)


			# print "\n\n help_rt",help_rt.count()
			# help_pages_id_list = help_rt['right_subject']
			# print help_pages_id_list
			# if isinstance(help_pages_id_list,list):
			# 	all_help_page_node_list = [node_collection.one({'_id':ObjectId(each_help_id)}) for each_help_id in help_pages_id_list]
			# elif isinstance(help_pages_id_list,ObjectId):
			# print "\n\nall_help_page_node_list",all_help_page_node_list
			return all_help_page_node_list
	except:
		return all_help_page_node_list


@get_execution_time
@register.assignment_tag
def get_course_completetion_data(group_obj, user, ids_list=False):
    leaf_ids = completed_ids = incompleted_ids = total_count = completed_count = None
    result_status = course_complete_percentage = None
    return_dict = {}


    if user.is_authenticated:
        result_status = get_course_completetion_status(group_obj, user.id, True)
        # print "\n\n result_status --- ",result_status
        if result_status:
            if "completed_ids_list" in result_status:
                completed_ids_list = result_status['completed_ids_list']
            if "incompleted_ids_list" in result_status:
                incompleted_ids_list = result_status['incompleted_ids_list']
            if "list_of_leaf_node_ids" in result_status:
                list_of_leaf_node_ids = result_status['list_of_leaf_node_ids']

            return_dict = {"leaf_ids":list_of_leaf_node_ids,"completed_ids":completed_ids_list,"incompleted_ids":incompleted_ids_list}
	return return_dict

@register.assignment_tag
def get_pages(page_type):
	'''
	returns the array of 'page_type' pages in the group 'help'
	ex. page_type='Info page' returns all Info pages in help group
	'''
	page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
	help_page = node_collection.one({'_type': "Group", 'name': "help"})
	page_type_gst = node_collection.one({'_type': "GSystemType", 'name': page_type})
	page_nodes = node_collection.find({'member_of': page_gst._id, 'type_of': page_type_gst._id, 'group_set': help_page._id})
	return page_nodes

@register.assignment_tag
def get_relation_node(node_id,rel_name):
	node = node_collection.one({'_id':ObjectId(node_id)})
	rt_subtitle = node_collection.one({'_type':'RelationType', 'name':unicode(rel_name)})
	grel_nodes = triple_collection.find({'relation_type': rt_subtitle._id, 'subject': node._id},
              {'right_subject':1, 'relation_type_scope': 1, '_id': 0})
	
	data_list = []
	for each_grel in grel_nodes:
		data_dict = {}
		file_node = node_collection.one({'_id': ObjectId(each_grel['right_subject'])})
		data_dict.update({'file_path': file_node['if_file']['original']['relurl']})
		data_dict.update({'relation_type_scope': each_grel['relation_type_scope']})
		data_dict.update({'file_name': file_node.name})
		data_dict.update({'file_id': ObjectId(file_node.pk)})
	 	data_list.append(data_dict)
	# print data_list
	return data_list

@register.assignment_tag
def get_lessons(unit_node):
	# return list of ObjectIds of all lessons
	# lesson_gst_name, lesson_gst_id = GSystemType.get_gst_name_id('lesson')
	# all_lessons_for_unit = node_collection.find({'member_of': lesson_gst_id,
	# 						'group_set': unit_node})
	lesson_nodes = node_collection.find({'_id': {'$in': unit_node.collection_set}})
	return lesson_nodes


@register.assignment_tag
def get_gstudio_alt_file_formats(mime_type):
 	return GSTUDIO_ALTERNATE_FORMATS[mime_type]

@register.assignment_tag
def get_gstudio_alt_size(mime_type):
 	return GSTUDIO_ALTERNATE_SIZE[mime_type]

@register.assignment_tag
def get_gstudio_alt_opts():
 	return GSTUDIO_ALTERNATE_OPTS

@register.assignment_tag
def get_test_page_oid():
 	return GSTUDIO_OID_HELP

@register.assignment_tag
def get_gstudio_registration():
 	return GSTUDIO_REGISTRATION

@register.assignment_tag
def get_unit_total_points(user_id,group_id):
	counter_obj = Counter.get_counter_obj(user_id, ObjectId(group_id))
	return counter_obj['group_points']

"""  commented for section subsection template """
# @register.assignment_tag
# def get_node_hierarchy(node_obj):
#     node_structure = []
#     for each in node_obj.collection_set:
#         lesson_dict ={}
#         lesson = Node.get_node_by_id(each)
#         if lesson:
#             lesson_dict['name'] = lesson.name
#             lesson_dict['type'] = 'lesson'
#             lesson_dict['id'] = str(lesson._id)
#             lesson_dict['language'] = lesson.language[0]
#             lesson_dict['activities'] = []
#             if lesson.collection_set:
#                 for each_act in lesson.collection_set:
#                     activity_dict ={}
#                     activity = Node.get_node_by_id(each_act)
#                     if activity:
#                         activity_dict['name'] = activity.name
#                         activity_dict['type'] = 'activity'
#                         activity_dict['id'] = str(activity._id)
#                         lesson_dict['activities'].append(activity_dict)
#             node_structure.append(lesson_dict)

#     return json.dumps(node_structure)


@register.assignment_tag
def get_node_hierarchy(node_obj):
    node_structure = []
    for each in node_obj.collection_set:
        lesson_dict ={}
        lesson = Node.get_node_by_id(each)
        if lesson:
            lesson_dict['name'] = lesson.name
            lesson_dict['type'] = 'lesson'
            lesson_dict['id'] = str(lesson._id)
            lesson_dict['language'] = lesson.language[0]
            lesson_dict['activities'] = []
            if lesson.collection_set:
                for each_act in lesson.collection_set:
                    activity_dict ={}
                    activity = Node.get_node_by_id(each_act)
                    if activity:
                        activity_dict['name'] = activity.name
                        activity_dict['type'] = 'activity'
                        activity_dict['id'] = str(activity._id)
                        lesson_dict['activities'].append(activity_dict)
            node_structure.append(lesson_dict)

    return json.dumps(node_structure)

@register.assignment_tag
def user_groups(is_super_user,user_id):
	user_grps_count = {}
	gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')
	gst_group = node_collection.one({'_type': "GSystemType", 'name': "Group"})
	gst_course = node_collection.one({'_type': "GSystemType", 'name': "Course"})
	gst_basecoursegroup = node_collection.one({'_type': "GSystemType", 'name': "BaseCourseGroup"})
	ce_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseEventGroup"})
	
	query = {'_type': 'Group', 'status': u'PUBLISHED',
             'member_of': {'$in': [gst_group._id],
             '$nin': [gst_course._id, gst_basecoursegroup._id, ce_gst._id, gst_course._id, gst_base_unit_id]},
            }

	if is_super_user:
		query.update({'group_type': {'$in': [u'PUBLIC', u'PRIVATE']}})
	else:
		query.update({'name': {'$nin': GSTUDIO_DEFAULT_GROUPS_LIST},
                    'group_type': u'PUBLIC'})
	group_cur = node_collection.find(query).sort('last_update', -1)
	
	user_draft_nodes = node_collection.find({'_type': "Group",'member_of':ObjectId(gst_base_unit_id),'$or': [{'group_admin': user_id}, {'author_set': user_id},{'created_by':user_id}]})
	# user_projects_nodes = node_collection.find({'_type': "Group",'$or': [{'group_admin': user_id}, {'author_set': user_id},{'created_by':user_id}]})
	user_grps_count['drafts'] = user_draft_nodes.count()
	user_grps_count['projects'] = group_cur.count()
	return user_grps_count
	return counter_obj['group_points']

@register.assignment_tag
def if_edit_course_structure():
	return GSTUDIO_EDIT_LMS_COURSE_STRUCTURE

@register.assignment_tag
def get_default_discussion_lbl():
	return DEFAULT_DISCUSSION_LABEL

@register.assignment_tag
def get_gstudio_workspace_instance():
	return GSTUDIO_WORKSPACE_INSTANCE

@register.assignment_tag
def get_topic_nodes(node_id):
	RT_teaches = node_collection.one({'_type':'RelationType', 'name': 'teaches'})
	teaches_grelations = triple_collection.find({'_type': 'GRelation', 'right_subject': ObjectId(node_id), 'relation_type': RT_teaches._id })
	teaches_grelations_id_list = []
	for each in teaches_grelations:
		teaches_grelations_id_list.append(each.subject)
	teaches_nodes = node_collection.find({"_id":{'$in' : teaches_grelations_id_list } })
	return teaches_nodes

@register.assignment_tag
def get_selected_topics(node_id):
	rel_val = get_relation_value(ObjectId(node_id),'teaches')
	teaches_grelations_id_list = []
	for each in rel_val['grel_node']:
		teaches_grelations_id_list.append(str(each._id))
		# teaches_grelations_id_list = map(ObjectId,teaches_grelations_id_list)
	return teaches_grelations_id_list

@register.assignment_tag
def rewind_cursor(cursor_obj):
	cursor_obj.rewind()
	return cursor_obj

@register.assignment_tag
def get_node_by_member_of_name(group_id, member_of_name):
	member_of_gst_name, member_of_gst_id = GSystemType.get_gst_name_id(member_of_name)
	return list(node_collection.find({'group_set': group_id, 'member_of': member_of_gst_id}))

@get_execution_time
@register.assignment_tag
def cast_to_node(node_or_node_list):
	# print "\nInput type: ", type(node_or_node_list)
	if isinstance(node_or_node_list, list):
		return map(Node,node_or_node_list)
	else:
		return Node(node_or_node_list)

@register.assignment_tag
def get_trans_node(node_id,lang):
    rel_value = get_relation_value(ObjectId(node_id),"translation_of")
    for each in rel_value['grel_node']:
        if each.language[0] ==  get_language_tuple(lang)[0]:
            trans_node = each
            print "\n\ntrans_node", trans_node
            return trans_node

# @register.assignment_tag
@register.inclusion_tag('ndf/quiz_player.html')
def load_quiz_player(request, group_id, node, hide_edit_opt=False):
    from gnowsys_ndf.ndf.views.quiz import render_quiz_player
    node_member_of_names_list = node.member_of_names_list
    if "QuizItem" in node_member_of_names_list or "QuizItemEvent" in node_member_of_names_list:
        con_var = render_quiz_player(request, group_id, node, get_context=True)
        con_var.update({'template': 'ndf/quiz_player.html', 'request': request,
			'hide_edit_opt': hide_edit_opt})
    # rel_value = get_relation_value(ObjectId(node._id),"translation_of")
    # for each in rel_value['grel_node']:
    #     if each.language[0] ==  get_language_tuple(lang)[0]:
    #         node = each
    #         print "\n\nnode", node
    return con_var


@register.assignment_tag
def get_module_enrollment_status(request, module_obj):
    def _user_enrolled(userid,unit_ids_list):
        user_data_dict = {userid: None}
        enrolled_flag = True
        for unit_id in unit_ids_list:
            unit_obj = node_collection.one({'_id': ObjectId(unit_id), '_type': 'Group'})
            if unit_obj:
	            if userid not in unit_obj.author_set:
	                enrolled_flag = False
        user_data_dict[userid] = enrolled_flag
        return user_data_dict

    data_dict = {}
    buddies_ids = request.session.get('buddies_userid_list', [])
    # print "\nbuddies_ids: ", buddies_ids

    buddies_ids.append(request.user.pk)
    if buddies_ids:
        for  userid in buddies_ids:
            data_dict.update(_user_enrolled(userid, module_obj.collection_set))
            # data_dict.update({userid : all(userid in groupobj.author_set for ind, groupobj in module_obj.collection_dict.items())})
            data_dict.update({'full_enrolled': all(data_dict.values())})
        # print "\n data: ", data_dict
        return data_dict
    return _user_enrolled(request.user.pk, module_obj.collection_set)
    # return {request.user.pk : user_enrolled, 'full_enrolled': user_enrolled}

@get_execution_time
@register.filter
def get_unicode_lang(lang_code):
    try:
        return get_language_tuple(lang_code)[1]
    except Exception as e:
        return lang_code
        pass

@get_execution_time
@register.filter
def get_header_lang(lang):
    for each_lang in HEADER_LANGUAGES:
        if lang in each_lang:
            return each_lang[1]
    return lang


@get_execution_time
@register.assignment_tag
def get_profile_full_name(user_obj):
	if isinstance(user_obj, basestring):
		if user_obj.isdigit():
			user_obj = int(user_obj)
		else:
			user_obj = User.objects.get(username=user_obj)
	if isinstance(user_obj, int):
		user_obj = User.objects.get(pk=user_obj)
	auth_obj = Author.get_author_by_userid(user_obj.pk)
	list_of_attr = ['first_name', 'last_name']
	auth_attr = auth_obj.get_attributes_from_names_list(list_of_attr)
	if auth_attr.values():
		full_name = ' '.join("%s" % val for (key,val) in auth_attr.iteritems())
		full_name += " (Username: " + user_obj.username + ", ID: " + str(user_obj.pk) + ")"
	else:
		full_name = "Username: " + user_obj.username  + ", ID: " + str(user_obj.pk)
	return full_name

@get_execution_time
@register.assignment_tag
def get_implicit_enrollment_flag():
	return GSTUDIO_IMPLICIT_ENROLL

@get_execution_time
@register.assignment_tag
def get_name_by_node_id(node_id):
    if isinstance(node_id, list) and len(node_id):
        node_id = node_id[-1]
    node = Node.get_node_by_id(node_id)
    if node:
        return node.name
    else:
        return None

@get_execution_time
@register.assignment_tag
def get_institute_name():
	return GSTUDIO_INSTITUTE_NAME
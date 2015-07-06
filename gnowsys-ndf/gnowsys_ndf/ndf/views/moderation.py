''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
# from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import View

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, GSTUDIO_GROUP_AGENCY_TYPES, GSTUDIO_NROER_MENU, GSTUDIO_NROER_MENU_MAPPINGS

# from gnowsys_ndf.ndf.models import GSystemType, GSystem, Group, Triple
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_all_user_groups  # get_existing_groups
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.views.data_review import data_review
from gnowsys_ndf.ndf.views.group import CreateModeratedGroup


@login_required
def moderation_status(request, group_id, node_id):

    node = node_collection.one({'_id': ObjectId(node_id)})

    if not node:  # invalid ObjectId
    	return render_to_response('ndf/under_moderation.html', {
		'group_id': group_id, 'groupid': group_id, 'title': 'Under Moderation Status',
      }, RequestContext(request))

    node_status = node.status
    node_group_set = node.group_set
    current_mod_group_obj = None
    is_under_moderation = True
    top_group_name = ""

    mod_group_instance = CreateModeratedGroup(request)

    selected_group = None
    for each_group_id in node_group_set:
    	each_group_obj = node_collection.one({'_id': ObjectId(each_group_id), '_type': 'Group'})
    	if each_group_obj:
    		selected_group = each_group_obj._id

    selected_group = selected_group if selected_group else group_id

    group_hierarchy_result = mod_group_instance.get_all_group_hierarchy(selected_group)
    # returns result in <True, all_sub_group_list> format

    if group_hierarchy_result[0]:
    	group_hierarchy_obj_list = group_hierarchy_result[1]
    	group_hierarchy_id_list = [g._id for g in group_hierarchy_obj_list]
    	top_group_id = group_hierarchy_id_list[0]
    	top_group_name = group_hierarchy_obj_list[0].name
    	# print group_hierarchy_obj_list

    	cntr = 0
    	for each_group_id in node_group_set:
    		cntr += 1
	    	if each_group_id in group_hierarchy_id_list:
	    		if ObjectId(each_group_id) == ObjectId(top_group_id):
	    			is_under_moderation = False
	    		else:
	    			is_under_moderation = True
	    			current_mod_group_obj = group_hierarchy_obj_list[cntr]

    elif node_status == u'MODERATION':
    	is_under_moderation = True

    else:
    	is_under_moderation = False

    # print "is_under_moderation : ", is_under_moderation
    # print "=== ", current_mod_group_obj._id

    return render_to_response('ndf/under_moderation.html', {
		'group_id': group_id, 'groupid': group_id, 'node': node, 'title': 'Under Moderation Status',
		'is_under_moderation': is_under_moderation, 'current_mod_group_obj': current_mod_group_obj,
		'group_hierarchy_obj_list': group_hierarchy_obj_list, 'top_group_name': top_group_name
      }, RequestContext(request))


def all_under_moderation(request, group_id):

	group_obj = get_group_name_id(group_id, get_obj=True)

	if not group_obj.edit_policy == 'EDITABLE_MODERATED':
		raise Http404('Group is not EDITABLE_MODERATED') 

	mod_group_instance = CreateModeratedGroup(request)
	group_hierarchy_result = mod_group_instance.get_all_group_hierarchy(group_obj._id)
	group_hierarchy_obj_list = []

	if group_hierarchy_result[0]:
		group_hierarchy_obj_list = group_hierarchy_result[1]
		group_hierarchy_id_list = [g._id for g in group_hierarchy_obj_list]
		file_gst = node_collection.one({'_type': 'GSystemType', 'name': 'File'})
		page_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Page'})

		all_resources = node_collection.find({'member_of': {'$in': [file_gst._id, page_gst._id]}, 'group_set': {'$in': group_hierarchy_id_list[1:]} })

		# print "=== ", res_cur.count()
		# print [x.name for x in all_resources]

		return render_to_response('ndf/all_under_moderation_status.html', {
			"group_id": group_id, "groupid": group_id, "title": "All Under Moderation Resources",
			"files": all_resources, "group_hierarchy_obj_list": group_hierarchy_obj_list,
			"detail_urlname": "moderation_status", "filetype": "all", "dont_show_error": True
			}, RequestContext(request))

	else:
		raise Http404(error_message) 

@login_required
def moderation(request, group_id, page_no=1):
	# try:
	# 	group_id = ObjectId(group_id)
	# except:
	# 	group_name, group_id = get_group_name_id(group_id)

	context_variables = data_review(request, group_id, page_no, get_paged_resources=True)
	# adding title in context_variables
	context_variables['title'] = 'moderation'
	
	template_name = "ndf/moderation_data_review.html"

	return render_to_response(template_name, context_variables, context_instance=RequestContext(request))


@login_required
def approve_resource(request, group_id):
	'''
	Method to approve resorce.
	Means resource will get published by moderator to next moderated or parent group.
	'''
	node_id = request.POST.get('node_oid', '')
	node_obj = node_collection.one({'_id': ObjectId(node_id)})
	flag = 0  # good to check at JS/front-end level

	if node_obj:
		node_group_set = node_obj.group_set
		# make deep copy of object and not to copy it's reference with [:].
		group_set_details_dict = get_moderator_group_set(node_group_set[:], group_id, get_details=True)
		updated_group_set = group_set_details_dict['updated_group_set']
		# print "==== updated_group_set : ", updated_group_set
		# print "==== node_group_set : ", node_group_set
		# print "==== group_set_details_dict : ", group_set_details_dict

		# if set(node_group_set) != set(updated_group_set):
		if group_set_details_dict['is_group_set_updated']:
			
			node_obj.group_set = updated_group_set

			# ---| checking for top group. \
			# If not top group and it's fond to be sub group create task |---
			# one way:
			# group_obj = get_group_name_id(updated_group_set[len(updated_group_set) - 1], get_obj=True)
			# print "===== group_obj.member_of_names_list : ", group_obj.member_of_names_list
			# if group_obj.member_of_names_list[0] in ['ProgramEventGroup', 'CourseEventGroup', 'PartnerGroup', 'ModeratingGroup']:
			# second way:
			if group_set_details_dict['is_new_group_top_group']:
				# means, resource is passed through curation flow and \
				# therefore change the status from 'MODERATION' to 'PUBLISHED'
				node_obj.status = u'PUBLISHED'

				# intimate creator of object/resource and creator of parent group
				node_creator_username = User.objects.get(id=node_obj.created_by).username

				task_content_org = u"Congratulations " + unicode(node_creator_username) + \
								u",\n\n Your contribution is moderated and it's published to " + \
								group_set_details_dict['newly_appended_group_name'] + \
								u". \n\nWe appreciate your efforts and thank you for your contribution!"
				create_moderator_task(request, \
					group_set_details_dict['newly_appended_group_id'],\
					 node_obj._id, task_type_creation='multiple', \
					 task_type='Other', task_content_org=task_content_org,\
					 created_by_name=node_creator_username)
				

			else:
				# resource is in curation flow hence, create a task
				create_moderator_task(request, \
					group_set_details_dict['newly_appended_group_id'],\
					 node_obj._id)
			# node_obj.modified_by = int(request.user.id)
			node_obj.save(groupid=group_id)

			flag = 1
		else:
			flag = 0
		
	else:
		flag = 0

	return HttpResponse(flag)


@login_required
def create_moderator_task(request, group_id, node_id, \
	task_type_creation='group', task_type='Moderation', task_content_org="", \
	created_by_name=""):
	'''
	Method to create task to group admins or moderators of the moderated groups.
	'''
	# def create_task(task_dict, task_type_creation="single"):
    # task_dict
    # - Required keys: _id[optional], name, group_set, created_by, modified_by, contributors, content_org,
        # created_by_name, Status, Priority, start_time, end_time, Assignee, has_type

	node_obj = node_collection.one({'_id': ObjectId(node_id)})

	# last group is next appended group
	group_obj = get_group_name_id(group_id, get_obj=True)


	if task_type == "Moderation":
		task_title = u"Moderate Resource: " + node_obj.name
	else:
		task_title = u"\n\nResource " + node_obj.name + \
					u" is successfully moderated and published to " + group_obj.name

	glist_gst = node_collection.one({'_type': "GSystemType", 'name': "GList"})
	task_type_list = []
	task_type_list.append(node_collection.one({'member_of': glist_gst._id, 'name':unicode(task_type)})._id)

	site = Site.objects.get(pk=1)
	site = unicode(site.name.__str__())

	if task_content_org:
		pass

	else:
		url = u"http://" + site + "/"+ unicode(group_obj._id) \
				+ u"/moderation#" + unicode(node_obj._id.__str__())

		task_content_org = u'\n\nModerate resource: "' + unicode(node_obj.name) \
						+ u'" having id: "' + unicode(node_obj._id.__str__()) + '"' \
						+ u'\n\nPlease moderate resource accesible at following link: \n'\
						+ unicode(url)

	task_dict = {
	    "name": task_title,
	    "group_set": [group_obj._id],
	    "created_by": node_obj.created_by,
	    "modified_by": request.user.id,
	    "contributors": [request.user.id],
	    "content_org": unicode(task_content_org),
	    # "created_by_name": unicode(created_by_name),
	    "created_by_name": unicode(request.user.username),
	    "Status": u"New",
	    "Priority": u"Normal",
	    # "start_time": "",
	    # "end_time": "",
	    "Assignee": list(group_obj.group_admin[:] + [node_obj.created_by]),
	    "has_type": task_type_list
	}

	task_obj = create_task(task_dict, task_type_creation)

	if task_obj:
		return True


def get_moderator_group_set(node_group_set, curr_group_id, get_details=False):
	'''
	Returns the "group_set".
	Takes two arguments:
	- node_group_set: existing/current group_set of node object.
	- curr_group_id: current group in which this node resides.
	Pass the deep copy of group_set and not the reference.
	e.g: 
	updated_group_set = get_moderator_group_set(node_group_set[:], group_id)
	------------
	if there is need of extra information along with group_set, pass <get_details=True> as last arg.
	e.g:
	updated_group_set = get_moderator_group_set(node_group_set[:], group_id, get_details=True)
	Along with group_set following details will be returned in DICT format:
	{
		"updated_group_set": updated_group_set,
		"is_group_set_updated": is_group_set_updated,
		"removed_group_id": removed_group_id,
		"newly_appended_group_id": newly_appended_group_id,
		"newly_appended_group_name": newly_appended_group_name,
		"is_new_group_top_group": is_new_group_top_group
	}
	'''

	curr_group_obj = node_collection.one({'_id': ObjectId(curr_group_id)})
	group_set = node_group_set[:]
	is_group_set_updated = False
	is_new_group_top_group = False

	# initializing dict with defaults:
	details_dict = {
		"updated_group_set": group_set,
		"is_group_set_updated": is_group_set_updated,
		"removed_group_id": None,
		"newly_appended_group_id": None,
		"newly_appended_group_name": None,
		"is_new_group_top_group": is_new_group_top_group
	}

	# check if current group having edit policy of EDITABLE_MODERATED.
	# if no return group_set as it was
	if not curr_group_obj.edit_policy == 'EDITABLE_MODERATED':
		if get_details:
			return details_dict
		else:
			return node_group_set

	# ---| getting appropriate member_of group |---
	# for top level of moderated group
	if len(curr_group_obj.member_of) == 1 and 'Group' in curr_group_obj.member_of_names_list:
		member_of = node_collection.one({'_type': 'GSystemType', 'name': u'ModeratingGroup'})

    # for sub-group falling under one of following categories:
	elif curr_group_obj.member_of_names_list[0] in ['ProgramEventGroup', 'CourseEventGroup', 'PartnerGroup', 'ModeratingGroup']:
		member_of = node_collection.one({'_id': curr_group_obj.member_of[0]})

    # final fallback option
	else:
    	# GST of "ModeratingGroup"
		member_of = node_collection.one({'_type': 'GSystemType', 'name': u'ModeratingGroup'})

    # getting sub-group having:
    # curr_group in prior_node 
    # and member_of as fetched above
    # and moderation_level > -1
	sub_mod_group_obj = node_collection.one({
                        '_type': 'Group',
                        'prior_node': {'$in': [ObjectId(curr_group_obj._id)]},
                        'member_of': {'$in': [ObjectId(member_of._id)]},
                        'moderation_level': {'$gt': -1}
                        })
	# print "curr_group_obj._id : ", curr_group_obj._id
	# print "member_of._id : ", member_of._id
	# print "sub_mod_group_obj.name : ", sub_mod_group_obj.name

	# proper sub-group found
	if sub_mod_group_obj:

		if ObjectId(curr_group_id) in group_set:
    		# remove current group's _id
			removed_group_id = group_set.pop(group_set.index(ObjectId(curr_group_id)))

		if not ObjectId(sub_mod_group_obj._id) in group_set:
			# add next/sub-group's _id
			group_set.append(sub_mod_group_obj._id)
			newly_appended_group_id = sub_mod_group_obj._id.__str__()
			newly_appended_group_name = sub_mod_group_obj.name
			is_group_set_updated = True

	# if no sub-group found or it's last sub-group of hierarchy
	else:
		is_top_group, top_group_obj = get_top_group_of_hierarchy(curr_group_id)
		
		if ObjectId(curr_group_id) in group_set:
			# remove current group's _id
			removed_group_id = group_set.pop(group_set.index(ObjectId(curr_group_id)))
        
		if is_top_group and (not ObjectId(top_group_obj._id) in group_set):
			# add parent/top group's _id
			group_set.append(top_group_obj._id)
			newly_appended_group_id = top_group_obj._id.__str__()
			newly_appended_group_name = top_group_obj.name
			is_group_set_updated = True
			is_new_group_top_group = True
        
	if get_details:
		details_dict = {
			"updated_group_set": group_set,
			"is_group_set_updated": is_group_set_updated,
			"removed_group_id": removed_group_id,
			"newly_appended_group_id": newly_appended_group_id,
			"newly_appended_group_name": newly_appended_group_name,
			"is_new_group_top_group": is_new_group_top_group
		}
		return details_dict

	# print group_set
	return group_set


def get_top_group_of_hierarchy(group_id):
    '''
    getting top group object of hierarchy.
    Returns mongokit object of top group.
    '''
    curr_group_obj = node_collection.one({'_id': ObjectId(group_id)})

    # loop till there is no end of prior_node or till reaching at top group.
    while curr_group_obj and curr_group_obj.prior_node:
        curr_group_obj = node_collection.one({'_id': curr_group_obj.prior_node[0]})

        if curr_group_obj.edit_policy != 'EDITABLE_MODERATED':
            return False, "One of the group: " + str(curr_group_obj._id) \
             + " is not with edit_policy: EDITABLE_MODERATED."
        
    # send overwritten/first curr_group_obj's "_id"
    return True, curr_group_obj

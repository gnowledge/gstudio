''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import request
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
from gnowsys_ndf.ndf.models import NodeJSONEncoder
# from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_relation_value  # get_existing_groups
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.views.data_review import data_review
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_sg_member_of
from gnowsys_ndf.ndf.views.notify import *


@login_required
def moderation_status(request, group_id, node_id, get_only_response_dict=False):

	try:
		group_id = ObjectId(group_id)
	except:
		group_name, group_id = get_group_name_id(group_id)

	node = node_collection.one({'_id': ObjectId(node_id)})
	from gnowsys_ndf.ndf.views.group import CreateModeratedGroup, CreateEventGroup, CreateGroup

	if not node:  # invalid ObjectId
		return render_to_response('ndf/under_moderation.html', {
		'group_id': group_id, 'groupid': group_id, 'title': 'Under Moderation Status',
		}, RequestContext(request))

	node_status = node.status
	node_group_set = node.group_set
	current_mod_group_obj = None
	group_hierarchy_obj_list = []
	is_under_moderation = True
	top_group_obj = None
	cleared_group_objs = []
	next_mod_group_objs = []
	group_obj = node_collection.one({'_id': ObjectId(group_id)})
	mod_group_instance = CreateModeratedGroup(request)
	# list_of_sg_mn = mod_group_instance.get_all_subgroups_member_of_list(group_obj._id)
	# list_of_sg_member_of = get_sg_member_of(group_obj._id)
	# print "\n\nlist_of_sg_mn-----",list_of_sg_member_of

	# selected_group = None

	for each_group_id in node_group_set:
		each_group_obj = node_collection.one({'_id': ObjectId(each_group_id), '_type': 'Group'})
		if each_group_obj:
			# selected_group = each_group_obj._id
			selected_group_obj = each_group_obj

	# selected_group = selected_group if selected_group else group_id
	selected_group_obj = selected_group_obj if selected_group_obj else group_obj
	# selected_group_obj = node_collection.one({'_id': ObjectId(selected_group)})
	list_of_sg_member_of = []
	# To prevent error if resource is pulished in top_level_group
	if "Group" in selected_group_obj.member_of_names_list:
		list_of_sg_member_of = get_sg_member_of(selected_group_obj._id)

	# Based on the resource's current group's member_of
	# or if resource is in top_level_group, based on its sg_member_of
	if "ModeratingGroup" in selected_group_obj.member_of_names_list or "ModeratingGroup" in list_of_sg_member_of or selected_group_obj.name == "home":
		sg_member_of = "ModeratingGroup"
		mod_group_instance = CreateModeratedGroup(request)
	elif "ProgramEventGroup" in selected_group_obj.member_of_names_list or "ProgramEventGroup" in list_of_sg_member_of:
		sg_member_of = "ProgramEventGroup"
		mod_group_instance = CreateEventGroup(request)
	elif "CourseEventGroup" in selected_group_obj.member_of_names_list or "CourseEventGroup" in list_of_sg_member_of:
		sg_member_of = "CourseEventGroup"
		mod_group_instance = CreateEventGroup(request)

	# group_hierarchy_result = mod_group_instance.get_all_group_hierarchy(selected_group,sg_member_of)
	# print "\n sg_member_of",sg_member_of
	group_hierarchy_result = mod_group_instance.get_all_group_hierarchy(selected_group_obj._id,sg_member_of)
	# returns result in <True, all_sub_group_list> format
	# print "\n\n group_hierarchy_result",group_hierarchy_result
	if group_hierarchy_result[0]:
		group_hierarchy_obj_list = group_hierarchy_result[1]
		group_hierarchy_id_list = [g._id for g in group_hierarchy_obj_list]
		group_hierarchy_names_list = [str(g.altnames) if g.altnames else g.name for g in group_hierarchy_obj_list]
		top_group_id = group_hierarchy_id_list[0]
		top_group_obj = group_hierarchy_obj_list[0]
		# cntr = 0
		# for each_group_id in node_group_set:
		# 	cntr += 1
		# 	if each_group_id in group_hierarchy_id_list:
		# 		if ObjectId(each_group_id) == ObjectId(top_group_id):
		# 			is_under_moderation = False
		# 		else:
		# 			current_mod_group_obj = group_hierarchy_obj_list[cntr+1]
		# 			is_under_moderation = True
		if selected_group_obj != top_group_obj:
			current_mod_group_obj = selected_group_obj
			is_under_moderation = True
		else:
			is_under_moderation = False

		if current_mod_group_obj:
			current_group_index = None
			try:
				current_group_index = group_hierarchy_names_list.index(current_mod_group_obj.name)
			except ValueError as e:
				current_group_index = group_hierarchy_names_list.index(current_mod_group_obj.altnames)

			if current_group_index:
				cleared_group_objs = group_hierarchy_names_list[1:current_group_index]
				next_mod_group_objs = group_hierarchy_names_list[current_group_index+1:]
	elif node_status == u'MODERATION':
		is_under_moderation = True
	else:
		is_under_moderation = False

	# print "is_under_moderation : ", is_under_moderation
	# print "=== ", current_mod_group_obj.name
	# print "\n\n cleared_group_objs",cleared_group_objs
	# print "\n\n next_mod_group_objs",next_mod_group_objs

	response_dict = {
		'group_id': group_id, 'groupid': group_id, 'node': node, 'title': 'Under Moderation Status',
		'is_under_moderation': is_under_moderation, 'current_mod_group_obj': current_mod_group_obj,
		'group_hierarchy_obj_list': json.dumps(group_hierarchy_obj_list,cls=NodeJSONEncoder), 'top_group_obj': top_group_obj,
		'group_obj': group_obj, 'next_mod_group_objs':next_mod_group_objs,
		'cleared_group_objs':cleared_group_objs
	}

	if get_only_response_dict:
		return response_dict

	return render_to_response('ndf/under_moderation.html', response_dict, RequestContext(request))

def all_under_moderation(request, group_id):
	from gnowsys_ndf.ndf.views.group import CreateModeratedGroup, CreateEventGroup, CreateGroup

	group_obj = get_group_name_id(group_id, get_obj=True)
	if not group_obj.edit_policy == 'EDITABLE_MODERATED':
		raise Http404('Group is not EDITABLE_MODERATED')
	list_of_sg_mn = get_sg_member_of(group_id)
	# mod_group_instance = CreateGroup(request)
	# print "\n\n list_of_sg_mn",list_of_sg_mn
	# list_of_sg_mn = mod_group_instance.get_all_subgroups_member_of_list(group_obj._id)
	if "ProgramEventGroup" in list_of_sg_mn:
		sg_member_of = "ProgramEventGroup"
		mod_group_instance = CreateEventGroup(request)
	elif "CourseEventGroup" in list_of_sg_mn:
		sg_member_of = "CourseEventGroup"
		mod_group_instance = CreateEventGroup(request)
	elif "ModeratingGroup" in list_of_sg_mn:
		sg_member_of = "ModeratingGroup"
		mod_group_instance = CreateModeratedGroup(request)

	group_hierarchy_result = mod_group_instance.get_all_group_hierarchy(group_obj._id,sg_member_of)
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
		raise Http404('Group is not EDITABLE_MODERATED')

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
	from gnowsys_ndf.ndf.views.group import CreateModeratedGroup

	group_obj = get_group_name_id(group_id, get_obj=True)
	node_id = request.POST.get('node_oid', '')
	node_obj = node_collection.one({'_id': ObjectId(node_id)})
	approve_or_reject = request.POST.get('app_rej_state', '')
	flag = 0  # good to check at JS/front-end level
	if approve_or_reject == "Approve":
		if node_obj:
			node_group_set = node_obj.group_set
			# task_id = get_relation_value(node_obj._id,"has_current_approval_task")
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

	elif approve_or_reject == "Reject":
		reject_reason_msg = request.POST.get('reject_reason', '')
		# print "reject_reason_msg----", reject_reason_msg
		# raise Exception("bb")
		# task_node,task_rt = get_relation_value(node_obj._id,"has_current_approval_task")
		grel_dict = get_relation_value(node_obj._id,"has_current_approval_task")
		is_cursor = grel_dict.get("cursor",False)
		if not is_cursor:
			task_node = grel_dict.get("grel_node")
			task_rt = grel_dict.get("grel_id")

		auth_grp = node_collection.one({'_type': "Author", 'created_by': int(node_obj.created_by)})
		node_obj.group_set = [auth_grp._id]
		node_obj.status = u"DRAFT"
		node_obj.save()

		# is_top_group, top_group_obj = get_top_group_of_hierarchy(group_obj._id)
		mod_group_instance = CreateModeratedGroup(request)
		# is_top_group, top_group_obj = mod_group_instance.get_top_group_of_hierarchy(curr_group_id)
		is_top_group, top_group_obj = mod_group_instance.get_top_group_of_hierarchy(group_obj._id)

		list_of_recipients_ids = []
		list_of_recipients_ids.extend(group_obj.group_admin)
		list_of_recipients_ids.extend(top_group_obj.group_admin)
		list_of_recipients_ids.append(node_obj.created_by)
		# print list_of_recipients_ids

		if task_node:
			task_content_org = u"\n\nThis task is CLOSED.\n " \
						"The resource associated with Moderation Task has been REJECTED. \n"
			task_dict = {
				"name": task_node.name,
				"_id" : ObjectId(task_node._id),
				"created_by": node_obj.created_by,
				"modified_by": request.user.id,
				"contributors": [request.user.id],
				"content_org": unicode(task_content_org),
				"created_by_name": unicode(request.user.username),
				"Status": u"CLOSED",
				"Priority": u"Normal",
				"Assignee": list(group_obj.group_admin[:]),
				# "has_type": task_type_list
			}
			task_obj = create_task(task_dict, 'group')

		# Sending notification to all watchers about the updates of the task
		try:
			for each_user_id in list_of_recipients_ids:
				activ = "Contribution to " + group_obj.name +"."
				mail_content = u"\n The resource "+ node_obj.name +" is REJECTED by " \
							 + request.user.username + ". \n" \
							 + "Reason specified: "+ unicode(reject_reason_msg)
				user_obj = User.objects.get(id=int(each_user_id))
				set_notif_val(request, group_obj._id, mail_content, activ, user_obj)
		except Exception as e:
			print "\n Unable to send notifications ",e
		flag = 1
	return HttpResponse(flag)


@login_required
def create_moderator_task(request, group_id, node_id, \
	task_type_creation='group', task_type='Moderation', task_content_org="", \
	created_by_name="",on_upload=False):
	'''
	Method to create task to group admins or moderators of the moderated groups.
	'''
	from gnowsys_ndf.ndf.templatetags.ndf_tags import get_relation_value
	# def create_task(task_dict, task_type_creation="single"):
	# task_dict
	# - Required keys: _id[optional], name, group_set, created_by, modified_by, contributors, content_org,
		# created_by_name, Status, Priority, start_time, end_time, Assignee, has_type
	try:
		task_dict = {}
		node_obj = node_collection.one({'_id': ObjectId(node_id)})

		# task_id_val = get_relation_value(node_obj._id,"has_current_approval_task")
		grel_dict = get_relation_value(node_obj._id,"has_current_approval_task")
		is_cursor = grel_dict.get("cursor",False)
		if not is_cursor:
			task_node = grel_dict.get("grel_node",None)
			if task_node:
				task_dict['_id'] = task_node._id
			# grel_id = grel_dict.get("grel_id")
		# if task_id_val != None:
		# 	task_dict['_id'] = get_relation_value(node_obj._id,"has_current_approval_task")


		# if node_obj.relation_set:
		# 	for rel in node_obj.relation_set:
		# 		if rel and 'has_current_approval_task' in rel:
		# 			task_id = rel['has_current_approval_task'][0]
		# 			task_dict["_id"] = ObjectId(task_id)

		# last group is next appended group
		group_obj = get_group_name_id(group_id, get_obj=True)
		at_curr_app_task = node_collection.one({'_type': "RelationType", 'name': "has_current_approval_task"})
		glist_gst = node_collection.one({'_type': "GSystemType", 'name': "GList"})
		task_type_list = []
		task_type_list.append(node_collection.one({'member_of': glist_gst._id, 'name':unicode(task_type)})._id)

		site = Site.objects.get(pk=1)
		site_domain = site.domain
		# print "=== site_domain: ", site_domain
		site = unicode(site.name.__str__())

		auth_grp = node_collection.one({'_type': "Author", 'created_by': int(node_obj.created_by)})
		if task_type == "Moderation":
			task_title = u"Resource under moderation: " + node_obj.name
			if task_content_org:
				pass

			else:
				url = u"http://" + site_domain + "/"+ unicode(group_obj._id) \
						+ u"/moderation#" + unicode(node_obj._id.__str__())

				task_content_org = u'\n\nResource under moderation: "' + unicode(node_obj.name) \
								+ u'" having id: "' + unicode(node_obj._id.__str__()) + '"' \

			task_dict = {
				"name": task_title,
				"group_set": [group_obj._id],
				"created_by": node_obj.created_by,
				"modified_by": request.user.id,
				"contributors": [request.user.id],
				"content_org": unicode(task_content_org),
				"created_by_name": unicode(request.user.username),
				# "Status": u"New",
				"Priority": u"Normal",
				# "start_time": "",
				# "end_time": "",
				"Assignee": list(group_obj.group_admin[:]),
				"has_type": task_type_list
			}
			if on_upload:
				task_dict['Status'] = u"New"
			else:
				task_dict['Status'] = u"In Progress"

			task_obj = create_task(task_dict, task_type_creation)

			if task_obj:
				create_grelation(node_obj._id, at_curr_app_task, task_obj._id)
				try:
					url = u"http://" + site_domain + "/" + unicode(auth_grp._id) \
						+ u"/moderation/status/" + unicode(node_obj._id.__str__())
					activ = "Contribution to " + group_obj.name + "."

					if not on_upload:
						mail_content = "Moderation status of your contributed file has been updated.\n" \
							+ "You may visit this link to check the status of Moderation :\t" \
							+ url
					elif on_upload:
						mail_content = "Your contributed file has been sent for Moderation.\n" \
							+ "You may visit this link to check the status of Moderation :\t" \
							+ url
					user_obj = User.objects.get(id=node_obj.created_by)
					set_notif_val(request, auth_grp._id, mail_content, activ, user_obj)
				except Exception as notif_err:
					# print notif_err
					msg = "Unable to send Notification"
		else:
			# on final publish to top group

			# 	task_title = u"\n\nResource " + node_obj.name + \
			# 				 u" in " + group_obj.name + u" is Approved. "
			# 	task_dict = {
			# 	    "name": task_title,
			# 	    "modified_by": request.user.id,
			# 	    "created_by_name": unicode(request.user.username),
			# 	    "Status": u"Feedback",
			# 	    "group_set": [group_obj._id],
			# 	    "created_by": node_obj.created_by,
			# 	    "content_org": unicode(task_content_org),
			# 	    "modified_by": request.user.id,
			# 	    "contributors": [request.user.id],
			# 	    "Priority": u"Normal",
			# 	    "Assignee": list(group_obj.group_admin[:] + [node_obj.created_by]),
			# 	    "has_type": task_type_list
			# 	}

			try:
				# delete the task associated with the resource
				list_of_recipients_ids = []
				list_of_recipients_ids.extend(group_obj.group_admin)
				list_of_recipients_ids.append(node_obj.created_by)

				# Sending notification to all watchers about the updates of the task
				for each_user_id in list_of_recipients_ids:
					url = u"http://" + site_domain + "/"+ unicode(group_obj._id) \
						+ u"/file/" + unicode(node_obj._id.__str__())

					activ = "Contribution to " + group_obj.name +"."
					mail_content = u"\n\n Contribution file "+ node_obj.name +" is moderated " \
								 + "and successfully published to " + \
								group_obj.name + \
								u". \n\nVisit this link to view the resource : " \
								+ url
					user_obj = User.objects.get(id=int(each_user_id))
					set_notif_val(request, auth_grp._id, mail_content, activ, user_obj)
				if task_id:
					task_node = node_collection.one({'_id': ObjectId(task_id)})
					# del_status, del_status_msg = delete_node(
					# node_id=task_node._id, deletion_type=0)
					url = u"http://" + site_domain + "/"+ unicode(group_obj._id) \
						+ u"/file/" + unicode(node_obj._id.__str__())

					task_content_org = u"\n\nThis task is CLOSED.\n " \
								"However, you may find the moderated resource at following link: \n" \
								+ unicode(url)
					task_dict = {
						"name": task_node.name,
						"group_set": [group_obj._id],
						"created_by": node_obj.created_by,
						"modified_by": request.user.id,
						"contributors": [request.user.id],
						"content_org": unicode(task_content_org),
						"created_by_name": unicode(request.user.username),
						"Status": u"CLOSED",
						"Priority": u"Normal",
						"Assignee": list(group_obj.group_admin[:]),
						"has_type": task_type_list
					}
					task_obj = create_task(task_dict, task_type_creation)


			except Exception as e:
				msg = "Unable to send Notification", str(e)
	except Exception as e:
		print "Error in task create moderation --- " + str(e)

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
	from gnowsys_ndf.ndf.views.group import CreateModeratedGroup

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
	list_of_sg_member_of = get_sg_member_of(curr_group_obj._id)

	if "ModeratingGroup" in list_of_sg_member_of:
		member_of = node_collection.one({'_type': 'GSystemType', 'name': u'ModeratingGroup'})

	elif 'ProgramEventGroup' in list_of_sg_member_of:
		member_of = node_collection.one({'_type': 'GSystemType', 'name': u'ProgramEventGroup'})

	elif 'CourseEventGroup' in list_of_sg_member_of:
		member_of = node_collection.one({'_type': 'GSystemType', 'name': u'CourseEventGroup'})

    # for sub-group falling under one of following categories:
	# elif curr_group_obj.member_of_names_list[0] in ['PartnerGroup', 'ModeratingGroup']:
	# 	member_of = node_collection.one({'_id': curr_group_obj.member_of[0]})

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
		mod_group_instance = CreateModeratedGroup(request.HttpRequest())
		is_top_group, top_group_obj = mod_group_instance.get_top_group_of_hierarchy(curr_group_id)
		# print "==== ", is_top_group
		# print "==== ", top_group_obj

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


# def get_top_group_of_hierarchy(group_id):
# 	'''
# 	getting top group object of hierarchy.
# 	Returns mongokit object of top group.
# 	'''
# 	curr_group_obj = node_collection.one({'_id': ObjectId(group_id)})

# 	# loop till there is no end of prior_node or till reaching at top group.
# 	while curr_group_obj and curr_group_obj.prior_node:
# 		curr_group_obj = node_collection.one({'_id': curr_group_obj.prior_node[0]})
# 		if curr_group_obj.edit_policy != 'EDITABLE_MODERATED':
# 			return False, "One of the group: " + str(curr_group_obj._id) \
# 			 + " is not with edit_policy: EDITABLE_MODERATED."
# 	# send overwritten/first curr_group_obj's "_id"
# 	return True, curr_group_obj

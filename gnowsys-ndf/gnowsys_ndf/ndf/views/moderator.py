''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
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


def under_moderation(request, group_id, node_id):

    node = node_collection.one({'_id': ObjectId(node_id)})

    return render_to_response('ndf/under_moderation.html', {
      'group_id': group_id, 'groupid': group_id, 'node': node, 'title': 'Under Moderation'
      }, RequestContext(request))


def create_moderator_task(group_id, resource_id):
	'''
	Method to create task to group admins or moderators of the moderated groups.
	'''
	pass


def get_moderator_group_set(node_group_set, curr_group_id):
	'''
	Returns the "group_set".
	Takes two arguments:
	- node_group_set: existing/current group_set of node object.
	- curr_group_id: current group in which this node resides.
	'''
	curr_group_obj = node_collection.one({'_id': ObjectId(curr_group_id)})
	group_set = node_group_set
	is_undergone_moderation = False

	# check if current group having edit policy of EDITABLE_MODERATED.
	# if no return group_set as it was
	if not curr_group_obj.edit_policy == 'EDITABLE_MODERATED':
		return node_group_set

	# getting appropriate member_of object
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
			group_set.pop(group_set.index(ObjectId(curr_group_id)))

		if not ObjectId(sub_mod_group_obj._id) in group_set:
			# add next/sub-group's _id
			group_set.append(sub_mod_group_obj._id)
			is_undergone_moderation = True

	# if no sub-group found or it's last sub-group of hierarchy
	else:
		is_top_group, top_group_obj = get_top_group_of_hierarchy(curr_group_id)
		
		if ObjectId(curr_group_id) in group_set:
			# remove current group's _id
			group_set.pop(group_set.index(ObjectId(curr_group_id)))
        
		if is_top_group and (not ObjectId(top_group_obj._id) in group_set):
			# add parent/top group's _id
			group_set.append(top_group_obj._id)
			is_undergone_moderation = True
        
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

''' -- imports from python libraries -- '''
# import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect  # , HttpResponse uncomment when to use
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response  # , render  uncomment when to use
from django.template import RequestContext
from django.template import TemplateDoesNotExist
# from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# from django.contrib.sites.models import Site
# from mongokit import IS
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT, GSTUDIO_TASK_TYPES,GSTUDIO_DEFAULT_GROUPS
# from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import get_execution_time
# from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.templatetags.ndf_tags import check_is_gstaff
# from gnowsys_ndf.ndf.templatetags.ndf_tags import edit_drawer_widget, get_disc_replies, get_all_replies,user_access_policy, get_relation_value, check_is_gstaff
# from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data, get_execution_time, delete_node, replicate_resource
# from gnowsys_ndf.ndf.views.notify import set_notif_val
# from gnowsys_ndf.ndf.views.methods import get_property_order_with_value, get_group_name_id
# from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, create_task, delete_grelation
# from gnowsys_ndf.notification import models as notification


gst_course = node_collection.one({'_type': "GSystemType", 'name': "Course"})
ce_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseEventGroup"})
gst_acourse = node_collection.one({'_type': "GSystemType", 'name': "Announced Course"})
gst_group = node_collection.one({'_type': "GSystemType", 'name': "Group"})
group_id = node_collection.one({'_type': "Group", 'name': "home"})._id

def explore(request):

    title = 'explore'

    context_variable = {'title': title, 'group_id': group_id, 'groupid': group_id}

    return render_to_response(
        "ndf/explore.html",
        context_variable,
        context_instance=RequestContext(request))

@get_execution_time
def explore_courses(request):

    title = 'courses'
    print ce_gst._id
    ce_cur = node_collection.find({'member_of': ce_gst._id,
                                        '$or': [
                                          {'created_by': request.user.id}, 
                                          {'group_admin': request.user.id},
                                          {'author_set': request.user.id},
                                          {'group_type': 'PUBLIC'} 
                                          ]}).sort('last_update', -1)

    context_variable = {'title': title, 'doc_cur': ce_cur, 'card': 'ndf/event_card.html',
                        'group_id': group_id, 'groupid': group_id}

    return render_to_response(
        "ndf/explore.html",
        context_variable,
        context_instance=RequestContext(request))


@get_execution_time
def explore_groups(request):
    title = 'groups'
    gstaff_access = check_is_gstaff(group_id,request.user)
    if gstaff_access:
        group_cur = node_collection.find({'_type': 'Group', 'member_of': gst_group._id}).sort('last_update', -1)
    else:
        group_cur = node_collection.find({'_type': 'Group', 'member_of': gst_group._id,'name':{'$nin':GSTUDIO_DEFAULT_GROUPS }}).sort('last_update', -1)

    context_variable = {'title': title, 'doc_cur': group_cur, 'card': 'ndf/simple_card.html',
                        'group_id': group_id, 'groupid': group_id}

    return render_to_response(
        "ndf/explore.html",
        context_variable,
        context_instance=RequestContext(request))


@login_required
@get_execution_time
def explore_basecourses(request):

    gstaff_access = check_is_gstaff(group_id,request.user)
    if not gstaff_access:
        return HttpResponseRedirect(reverse('explore_courses'))

    title = 'base courses'

    course_cur = node_collection.find({'member_of': gst_course._id}).sort('last_update', -1)
    context_variable = {'title': title, 'doc_cur': course_cur, 'card': 'ndf/event_card.html',
                        'group_id': group_id, 'groupid': group_id}
    return render_to_response(
        "ndf/explore.html",
        context_variable,
        context_instance=RequestContext(request))


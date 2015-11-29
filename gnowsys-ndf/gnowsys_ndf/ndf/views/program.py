''' -- imports from python libraries -- '''
# from datetime import datetime
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect  # , HttpResponse uncomment when to use
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response  # , render  uncomment when to use
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_group_name_id, get_prior_node_hierarchy
from gnowsys_ndf.ndf.templatetags.ndf_tags import check_is_gstaff

def program_event_list(request, group_id):
    """
    * Renders a list of all 'programs'
    """
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    group_obj = node_collection.one({'_id': ObjectId(group_id)})

    course_coll = None
    enr_ce_coll = []
    list_of_pe = []
    all_pe = []
    pe_gst = node_collection.one({'_type': "GSystemType", 'name': "ProgramEventGroup"})

    # program events
    title = "Events"

    pe_coll = node_collection.find({'member_of': pe_gst._id}).sort('last_update', -1)
    for each_pe in pe_coll:
        list_of_hierarchy = get_prior_node_hierarchy(each_pe._id)
        if list_of_hierarchy:
            pe_obj = list_of_hierarchy[len(list_of_hierarchy)-1]
        if pe_obj not in list_of_pe and pe_obj._id in group_obj.post_node:
            list_of_pe.append(pe_obj)
    # print "\n\n list_of_pe",list_of_pe
    gstaff_access = False
    if request.user.id:
        gstaff_access = check_is_gstaff(group_id,request.user)
        userid = int(request.user.id)
        for each in list_of_pe:
            if userid in each.author_set:
                if each not in enr_ce_coll:
                    enr_ce_coll.append(each)     
            else:
                all_pe.append(each)   
    else:
        all_pe = list_of_pe
    if gstaff_access:
        all_pe = enr_ce_coll
    # If request.user is admin, enr_ce_coll is all_pe. 
    # As admin is added in author set of all pe
        # enr_ce_coll = node_collection.find({'$in': list_of_pe,'author_set': int(request.user.id)}).sort('last_update', -1)

    # ce_coll = node_collection.find({'member_of': pe_gst._id, 'author_set': {'$ne': int(request.user.id)}})

    return render_to_response("ndf/course.html",
                            {'title': title,
                             'course_gst': pe_gst,
                             'course_coll': list_of_pe,
                             'groupid': group_id, 'group_id': group_id,
                             'ce_coll':all_pe,
                             'enr_ce_coll':enr_ce_coll,
                            },
                            context_instance=RequestContext(request)
                            )     
''' -- Imports from python libraries -- '''
# import os, re
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponse
from django.shortcuts import render_to_response  # , render  #uncomment when to use
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from mongokit import paginator

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

# from django.http import Http404

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import Node  # , GRelation, Triple
from gnowsys_ndf.ndf.models import node_collection, triple_collection
# from gnowsys_ndf.ndf.models import GSystemType#, GSystem uncomment when to use
# from gnowsys_ndf.ndf.models import File
from gnowsys_ndf.ndf.models import STATUS_CHOICES
from gnowsys_ndf.ndf.views.methods import get_node_common_fields,get_execution_time  # , create_grelation_list ,set_all_urls
from gnowsys_ndf.ndf.views.methods import create_grelation
# from gnowsys_ndf.ndf.views.methods import create_gattribute
from gnowsys_ndf.ndf.views.methods import get_node_metadata, get_page, get_group_name_id
from gnowsys_ndf.ndf.views.search_views import results_search

# from gnowsys_ndf.settings import GSTUDIO_SITE_VIDEO
# from gnowsys_ndf.settings import EXTRA_LANG_INFO
from gnowsys_ndf.settings import GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT
from gnowsys_ndf.settings import GSTUDIO_RESOURCES_EDUCATIONAL_USE
from gnowsys_ndf.settings import GSTUDIO_RESOURCES_INTERACTIVITY_TYPE
from gnowsys_ndf.settings import GSTUDIO_RESOURCES_EDUCATIONAL_ALIGNMENT
from gnowsys_ndf.settings import GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL
from gnowsys_ndf.settings import GSTUDIO_RESOURCES_CURRICULAR
from gnowsys_ndf.settings import GSTUDIO_RESOURCES_AUDIENCE
from gnowsys_ndf.settings import GSTUDIO_RESOURCES_TEXT_COMPLEXITY
from gnowsys_ndf.settings import GSTUDIO_RESOURCES_LANGUAGES

GST_FILE = node_collection.one({'_type': 'GSystemType', 'name': u'File'})
pandora_video_st = node_collection.one({'$and': [{'_type': 'GSystemType'}, {'name': 'Pandora_video'}]})

file_id = node_collection.find_one({'_type': "GSystemType", "name": "File"}, {"_id": 1})
page_id = node_collection.find_one({'_type': "GSystemType", "name": "Page"}, {"_id": 1})
theme_gst_id = node_collection.find_one({'_type': "GSystemType", "name": "Theme"}, {"_id": 1})
group_gst_id = node_collection.find_one({'_type': "GSystemType", "name": "Group"}, {"_id": 1})


# data review in File app
@login_required
@get_execution_time
def data_review(request, group_id, page_no=1, **kwargs):
    '''
    To get all the information related to every resource object in the group.

    To get processed context_variables into another variable,
    pass <get_paged_resources=True> as last arg.

    e.g:
    context_variables = data_review(request, group_id, page_no, get_paged_resources=True)
    '''

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    files_obj = node_collection.find({
                                    'member_of': {'$in': [
                                        ObjectId(file_id._id),
                                        ObjectId(page_id._id),
                                        ObjectId(theme_gst_id._id),
                                        ObjectId(group_gst_id._id)
                                        ]},
                                    # '_type': 'File', 'fs_file_ids': {'$ne': []},
                                    'group_set': {'$in': [ObjectId(group_id)]},
                                    '$or': [
                                        {'access_policy': u"PUBLIC"},
                                        {'$and': [
                                            {'access_policy': u"PRIVATE"},
                                            {'created_by': request.user.id}
                                            ]
                                        }
                                    ]
                                        # {'member_of': {'$all': [pandora_video_st._id]}}
                                        }).sort("created_at", -1)

    # implementing pagination: paginator.Paginator(cursor_obj, <int: page no>, <int: no of obj in each page>)
    # (ref: https://github.com/namlook/mongokit/blob/master/mongokit/paginator.py)
    paged_resources = paginator.Paginator(files_obj, page_no, 10)

    # list to hold resources instances with it's attributes and relations
    files_list = []

    for each_resource in paged_resources.items:
        # each_resource, ver = get_page(request, each_resource)
        each_resource.get_neighbourhood(each_resource.member_of)
        files_list.append(node_collection.collection.GSystem(each_resource))
        # print "==============", each_resource.name, " : ", each_resource.group_set
        # print "\n\n\n========", each_resource.keys()
        # for each, val in each_resource.iteritems():
          # print each, "--", val,"\n"

    # print "files_obj.count: ", files_obj.count()
    files_obj.close()

    context_variables = {
            "group_id": group_id, "groupid": group_id,
            "files": files_list, "page_info": paged_resources,
            "urlname": "data_review_page", "second_arg": "",
            "static_educationalsubject": GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT,
            # "static_language": EXTRA_LANG_INFO,
            "static_language": GSTUDIO_RESOURCES_LANGUAGES,
            "static_educationaluse": GSTUDIO_RESOURCES_EDUCATIONAL_USE,
            "static_interactivitytype": GSTUDIO_RESOURCES_INTERACTIVITY_TYPE,
            "static_educationalalignment": GSTUDIO_RESOURCES_EDUCATIONAL_ALIGNMENT,
            "static_educationallevel": GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL,
            "static_curricular": GSTUDIO_RESOURCES_CURRICULAR,
            "static_audience": GSTUDIO_RESOURCES_AUDIENCE,
            "static_status": list(STATUS_CHOICES),
            "static_textcomplexity": GSTUDIO_RESOURCES_TEXT_COMPLEXITY
        }

    if kwargs.get('get_paged_resources', False):
        return  context_variables

    template_name = "ndf/data_review.html"

    return render_to_response(
        template_name,
        context_variables,
        context_instance=RequestContext(request)
    )
# ---END of data review in File app

@get_execution_time
def get_dr_search_result_dict(request, group_id, search_text=None, page_no=1):

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    # check if request is from form or from next page
    if request.GET.has_key("search_text"):
        search_text = request.GET.get("search_text", "")

    else:
        search_text = search_text.replace("+", " ")
        get_req = request.GET.copy()
        # adding values to GET req
        get_req.update({"search_text": search_text})
        # overwriting request.GET with newly created QueryDict instance get_req
        request.GET = get_req

    search_reply = json.loads(results_search(request, group_id, return_only_dict = True))
    exact_search_res = search_reply["exact"]["name"]
    result_ids_list = [ ObjectId(each_dict["_id"]) for each_dict in exact_search_res ]
    result_cur = node_collection.find({
                                    "_id": {"$in": result_ids_list},
                                    'member_of': {'$in': [ObjectId(file_id._id), ObjectId(page_id._id)]}
                                    })

    paged_resources = paginator.Paginator(result_cur, page_no, 10)

    # list to hold resources instances with it's attributes and relations
    files_list = []

    for each_resource in paged_resources.items:
        each_resource, ver = get_page(request, each_resource)
        each_resource.get_neighbourhood(each_resource.member_of)
        files_list.append(node_collection.collection.GSystem(each_resource))

    return render_to_response("ndf/data_review.html",
                {
                    "group_id": group_id, "groupid": group_id,
                    "files": files_list, "page_info": paged_resources,
                    "urlname": "data_review_search_page",
                    "second_arg": search_text, "search_text": search_text,
                    "static_educationalsubject": GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT,
                    # "static_language": EXTRA_LANG_INFO,
                    "static_language": GSTUDIO_RESOURCES_LANGUAGES,
                    "static_educationaluse": GSTUDIO_RESOURCES_EDUCATIONAL_USE,
                    "static_interactivitytype": GSTUDIO_RESOURCES_INTERACTIVITY_TYPE,
                    "static_educationalalignment": GSTUDIO_RESOURCES_EDUCATIONAL_ALIGNMENT,
                    "static_educationallevel": GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL,
                    "static_curricular": GSTUDIO_RESOURCES_CURRICULAR,
                    "static_audience": GSTUDIO_RESOURCES_AUDIENCE,
                    "static_status": list(STATUS_CHOICES),
                    "static_textcomplexity": GSTUDIO_RESOURCES_TEXT_COMPLEXITY
                }, context_instance=RequestContext(request))


# saving resource object of data review
@login_required
@get_execution_time
def data_review_save(request, group_id):
    '''
    Method to save each and every data-row edit of data review app
    '''

    userid = request.user.pk

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    group_obj = node_collection.one({"_id": ObjectId(group_id)})

    node_oid = request.POST.get("node_oid", "")
    node_details = request.POST.get("node_details", "")
    node_details = json.loads(node_details)

    # print "node_details : ", node_details

    # updating some key names of dictionary as per get_node_common_fields.
    node_details["lan"] = node_details.pop("language")
    node_details["prior_node_list"] = node_details.pop("prior_node")
    node_details["login-mode"] = node_details.pop("access_policy")
    status = node_details.pop("status")
    # node_details["collection_list"] = node_details.pop("collection") for future use

    # Making copy of POST QueryDict instance.
    # To make it mutable and fill in node_details value/s.
    post_req = request.POST.copy()

    # removing node_details dict from req
    post_req.pop('node_details')

    # adding values to post req
    post_req.update(node_details)

    # overwriting request.POST with newly created QueryDict instance post_req
    request.POST = post_req
    # print "\n---\n", request.POST, "\n---\n"

    copyright = request.POST.get('copyright', '')

    file_node = node_collection.one({"_id": ObjectId(node_oid)})

    if request.method == "POST":

        edit_summary = []

        file_node_before = file_node.copy()  # copying before it is getting modified
        is_changed = get_node_common_fields(request, file_node, group_id, GST_FILE)

        for key, val in file_node_before.iteritems():
            if file_node_before[key] != file_node[key]:
                temp_edit_summ = {}
                temp_edit_summ["name"] = "Field: " + key
                temp_edit_summ["before"] = file_node_before[key]
                temp_edit_summ["after"] = file_node[key]

                edit_summary.append(temp_edit_summ)

        # to fill/update attributes of the node and get updated attrs as return
        ga_nodes = get_node_metadata(request, file_node, is_changed=True)

        if len(ga_nodes):
            is_changed = True

            # adding the edit attribute name in summary
            for each_ga in ga_nodes:
                temp_edit_summ = {}
                temp_edit_summ["name"] = "Attribute: " + each_ga["node"]["attribute_type"]["name"]
                temp_edit_summ["before"] = each_ga["before_obj_value"]
                temp_edit_summ["after"] = each_ga["node"]["object_value"]

                edit_summary.append(temp_edit_summ)

        teaches_list = request.POST.get('teaches', '')  # get the teaches list
        prev_teaches_list = request.POST.get("teaches_prev", "")  # get the before-edit teaches list

        # check if teaches list exist means nodes added/removed for teaches relation_type
        # also check for if previous teaches list made empty with prev_teaches_list
        if (teaches_list != '') or prev_teaches_list:

            teaches_list = teaches_list.split(",") if teaches_list else []
            teaches_list = [ObjectId(each_oid) for each_oid in teaches_list]

            relation_type_node = node_collection.one({'_type': "RelationType", 'name':'teaches'})

            gr_nodes = create_grelation(file_node._id, relation_type_node, teaches_list)
            gr_nodes_oid_list = [ObjectId(each_oid["right_subject"]) for each_oid in gr_nodes] if gr_nodes else []

            prev_teaches_list = prev_teaches_list.split(",") if prev_teaches_list else []
            prev_teaches_list = [ObjectId(each_oid) for each_oid in prev_teaches_list]

            if len(gr_nodes_oid_list) == len(prev_teaches_list) and set(gr_nodes_oid_list) == set(prev_teaches_list):
                pass
            else:
                rel_nodes = triple_collection.find({'_type': "GRelation",
                                      'subject': file_node._id,
                                      'relation_type': relation_type_node._id
                                    })

                rel_oid_name = {}

                for each in rel_nodes:
                    temp = {}
                    temp[each.right_subject] = each.name
                    rel_oid_name.update(temp)

                is_changed = True
                temp_edit_summ = {}
                temp_edit_summ["name"] = "Relation: Teaches"
                temp_edit_summ["before"] = [rel_oid_name[each_oid].split(" -- ")[2] for each_oid in prev_teaches_list]
                temp_edit_summ["after"] = [rel_oid_name[each_oid].split(" -- ")[2] for each_oid in  gr_nodes_oid_list]
                edit_summary.append(temp_edit_summ)

        assesses_list = request.POST.get('assesses_list','')
        if assesses_list != '':
            assesses_list = assesses_list.split(",")
            assesses_list = [ObjectId(each_oid) for each_oid in assesses_list]

            relation_type_node = node_collection.one({'_type': "RelationType", 'name':'assesses'})

            gr_nodes = create_grelation(file_node._id, relation_type_node, teaches_list)
            gr_nodes_oid_list = [ObjectId(each_oid["right_subject"]) for each_oid in gr_nodes]

            if len(gr_nodes_oid_list) == len(teaches_list) and set(gr_nodes_oid_list) == set(teaches_list):
                pass
            else:
                is_changed = True

        # changing status to draft even if attributes/relations are changed
        if is_changed:

            file_node.status = unicode("DRAFT")
            file_node.modified_by = userid

            if userid not in file_node.contributors:
                file_node.contributors.append(userid)

        # checking if user is authenticated to change the status of node
        if status and ((group_obj.is_gstaff(request.user)) or (userid in group_obj.author_set)):
            if file_node.status != status:
                file_node.status = unicode(status)
                file_node.modified_by = userid

                if userid not in file_node.contributors:
                    file_node.contributors.append(userid)

                is_changed = True

        if is_changed:
            file_node.save(groupid=group_id)

        # print edit_summary

    return HttpResponse(file_node.status)

# ---END of data review saving.

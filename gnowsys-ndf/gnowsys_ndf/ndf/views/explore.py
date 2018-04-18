''' -- imports from python libraries -- '''
import json

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
from mongokit import paginator

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT, GSTUDIO_TASK_TYPES,GSTUDIO_DEFAULT_GROUPS_LIST
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME, GSTUDIO_NO_OF_OBJS_PP, GSTUDIO_PRIMARY_COURSE_LANGUAGE
from gnowsys_ndf.ndf.models import Node, Group, GSystemType,  AttributeType, RelationType
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import get_execution_time, get_language_tuple, create_gattribute, delete_gattribute
from gnowsys_ndf.ndf.templatetags.ndf_tags import check_is_gstaff, get_attribute_value, cast_to_node
# from gnowsys_ndf.ndf.views.methods import get_group_name_id
# from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data, get_execution_time, delete_node, replicate_resource


gst_course = node_collection.one({'_type': "GSystemType", 'name': "Course"})
gst_basecoursegroup = node_collection.one({'_type': "GSystemType", 'name': "BaseCourseGroup"})
ce_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseEventGroup"})
announced_unit_gst = node_collection.one({'_type': "GSystemType", 'name': "announced_unit"})
gst_acourse = node_collection.one({'_type': "GSystemType", 'name': "Announced Course"})
gst_group = node_collection.one({'_type': "GSystemType", 'name': "Group"})
group_id = node_collection.one({'_type': "Group", 'name': "home"})._id
gst_module_name, gst_module_id = GSystemType.get_gst_name_id('Module')
gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')
at_items_sort_list = node_collection.one({'_type': "AttributeType", 'name': "items_sort_list"})

@get_execution_time
def explore(request):
    return HttpResponseRedirect(reverse('explore_courses', kwargs={}))

    title = 'explore'

    context_variable = {'title': title, 'group_id': group_id, 'groupid': group_id}

    return render_to_response(
        "ndf/explore.html",
        context_variable,
        context_instance=RequestContext(request))

'''
Depricated as on 15 Apr 2017 - katkamrachana
For new explore UI to list Modules and announced-units
@get_execution_time
def explore_courses(request,page_no=1):
    # this will be announced tab
    title = 'courses'
    ce_cur = node_collection.find({'member_of': {'$in': [ce_gst._id, announced_unit_gst._id]},
                                        '$or': [
                                          {'created_by': request.user.id},
                                          {'group_admin': request.user.id},
                                          {'author_set': request.user.id},
                                          {'group_type': 'PUBLIC'}
                                          ]}).sort('last_update', -1)
    ce_page_cur = paginator.Paginator(ce_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)

    gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')
    # # parent_group_name, parent_group_id = Group.get_group_name_id(group_id)
    # ce_cur = node_collection.find({
    #                                 '_type': 'Group',
    #                                 # 'group_set': {'$in': [parent_group_id]},
    #                                 'member_of': {'$in': [gst_base_unit_id]}#,
    #                                 # '$or':[
    #                                 #     {'status': u'PUBLIC'},
    #                                 #     {
    #                                 #         '$and': [
    #                                 #             {'access_policy': u"PRIVATE"},
    #                                 #             {'created_by': request.user.id}
    #                                 #         ]
    #                                 #     }
    #                                 # ]
    #                             }).sort('last_update', -1)
    # ce_page_cur = paginator.Paginator(ce_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)
    # print ce_cur.count()
    context_variable = {
                        'title': title, 'doc_cur': ce_cur,
                        'group_id': group_id, 'groupid': group_id,
                        'card': 'ndf/event_card.html', 'ce_page_cur':ce_page_cur
                    }

    return render_to_response(
        # "ndf/explore.html", changed as per new Clix UI
        "ndf/explore_2017.html",
        context_variable,
        context_instance=RequestContext(request))
'''

@get_execution_time
def explore_groups(request,page_no=1):
    title = 'workspaces'
    gstaff_access = check_is_gstaff(group_id,request.user)

    query = {'_type': 'Group', 'status': u'PUBLISHED',
            'agency_type':u"School",
            '$or': [
                        {'access_policy': u"PUBLIC"},
                        {'$and': [
                                {'access_policy': u"PRIVATE"},
                                {'created_by': request.user.id}
                            ]
                        }
                    ],
             'member_of': {'$in': [gst_group._id],
             '$nin': [gst_course._id, gst_basecoursegroup._id, ce_gst._id, gst_course._id, gst_base_unit_id]},
            }

    if gstaff_access:
        query.update({'group_type': {'$in': [u'PUBLIC', u'PRIVATE']}})
    else:
        query.update({'name': {'$nin': GSTUDIO_DEFAULT_GROUPS_LIST},
                    'group_type': u'PUBLIC'})
    group_cur = node_collection.find(query).sort('last_update', -1)

    grp_page_cur = paginator.Paginator(group_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)
    context_variable = {'title': title, 'groups_cur': group_cur, 'card': 'ndf/card_group.html',
                        'group_id': group_id, 'groupid': group_id,'grp_page_cur': grp_page_cur}

    return render_to_response(
        "ndf/explore_2017.html",
        context_variable,
        context_instance=RequestContext(request))

@login_required
@get_execution_time
def explore_basecourses(request,page_no=1):

    title = 'courses'
    # ce_cur = node_collection.find({'member_of': ce_gst._id,
    #                                     '$or': [
    #                                       {'created_by': request.user.id},
    #                                       {'group_admin': request.user.id},
    #                                       {'author_set': request.user.id},
    #                                       {'group_type': 'PUBLIC'}
    #                                       ]}).sort('last_update', -1)
    # ce_page_cur = paginator.Paginator(ce_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)

    # parent_group_name, parent_group_id = Group.get_group_name_id(group_id)
    '''
    ce_cur = node_collection.find({
                                    '_type': 'Group',
                                    # 'group_set': {'$in': [parent_group_id]},
                                    'member_of': {'$in': [gst_base_unit_id]},
                                    '$or':[
                                        {'group_type': u'PUBLIC'},
                                        {
                                            '$and': [
                                                {'access_policy': u"PRIVATE"},
                                                {'created_by': request.user.id}
                                            ]
                                        }
                                    ],
                                    'status': u'PUBLISHED'
                                }).sort('last_update', -1)
    '''
    gstaff_access = check_is_gstaff(group_id,request.user)

    query = {'_type': 'Group', 'status': u'PUBLISHED',
             'member_of': {'$in': [gst_base_unit_id]},
            }

    if gstaff_access:
        query.update({'group_type': u'PRIVATE'})
    else:
        query.update({'group_type': u'PUBLIC'})
        if request.user.is_authenticated():
            query.update({'$and': [{'group_type': u'PRIVATE'},
                                        {'created_by': request.user.id}]})
    ce_cur = node_collection.find(query).sort('last_update', -1)



    ce_page_cur = paginator.Paginator(ce_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)
    # print ce_cur.count()
    title = 'base courses'
    context_variable = {
                        'title': title, 'doc_cur': ce_cur,
                        'group_id': group_id, 'groupid': group_id,
                        'card': 'ndf/card_group.html', 'ce_page_cur':ce_page_cur
                    }


    return render_to_response(
        # "ndf/explore.html", changed as per new Clix UI
        "ndf/explore_2017.html",
        context_variable,
        context_instance=RequestContext(request))

    # gstaff_access = check_is_gstaff(group_id,request.user)
    # if not gstaff_access:
    #     return HttpResponseRedirect(reverse('explore_courses'))


    # course_cur = node_collection.find({'member_of': {'$in': [gst_course._id, gst_basecoursegroup._id]}}).sort('last_update', -1)

    # ce_page_cur = paginator.Paginator(course_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)

    # context_variable = {
    #                     'title': title, 'doc_cur': course_cur, 'card': 'ndf/event_card.html',
    #                     'group_id': group_id, 'groupid': group_id, 'ce_page_cur':ce_page_cur
    #                     }

    # return render_to_response(
    #     "ndf/explore.html",
    #     context_variable,
    #     context_instance=RequestContext(request))

@get_execution_time
def explore_courses(request):

    # this will be announced tab
    title = 'courses'
    context_variable = {
                        'title': title, 
                        'group_id': group_id, 'groupid': group_id,
                        'modules_is_cur': True,
                    }
    modules_sort_list = get_attribute_value(group_id, 'items_sort_list')
    all_modules = node_collection.find({'member_of': gst_module_id ,'status':'PUBLISHED'}).sort('last_update', -1)
    if modules_sort_list:
        context_variable.update({'modules_sort_list': modules_sort_list})
    else:
        context_variable.update({'modules_sort_list': list(all_modules)})
        # modules_cur = map(Node,modules_sort_list)
        # context_variable.update({'modules_is_cur': False})
        # modules_node_sort_list = cast_to_node(modules_sort_list)

    all_modules.rewind()
    module_unit_ids = [val for each_module in all_modules for val in each_module.collection_set ]

    primary_lang_tuple = get_language_tuple(GSTUDIO_PRIMARY_COURSE_LANGUAGE)

    '''
    katkamrachana - 14June2017
    About following query:

        [A]. Finding CourseEventGroup instances(First $and in $or):
                    Find CourseEventGroup instances, that are published.
                    Get courses that are linked to the request.user
                    Also find courses, that are "PUBLIC AND LANGUAGE falls under
                    GSTUDIO_PRIMARY_COURSE_LANGUAGE"
                    Hence, Apply language constraint. Introduced to display concerned
                    course for i2c(in 3 languages)
        [B]. Finding announced_unit instances(Second $and in $or):
                    Find announced_unit instances, that are published.
                    Get courses that are linked to the request.user
                    Also find courses, that are "PUBLIC"
                    No check on language
        [C]. Check using _type field in case conditions A and B fail, only Groups are
                 to be listed and not GSystems
        [D]. Check using name field in case conditions A and B fail,
                executing condition C then do not display factory Groups.

    '''
    base_unit_cur = node_collection.find({
                                            '$or': [
                                                {
                                                    '$and': [
                                                                {'member_of': ce_gst._id},
                                                                {'status':'PUBLISHED'},
                                                                {'$or':
                                                                    [
                                                                        {'created_by': request.user.id},
                                                                        {'group_admin': request.user.id},
                                                                        {'author_set': request.user.id},
                                                                        {
                                                                            '$and': [
                                                                                {'group_type': 'PUBLIC'},
                                                                                {'language': primary_lang_tuple},
                                                                            ]
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                },
                                                {
                                                    '$and': [
                                                                {'member_of': announced_unit_gst._id},
                                                                {'status':'PUBLISHED'},
                                                                {'$or':
                                                                    [
                                                                        {'created_by': request.user.id},
                                                                        {'group_admin': request.user.id},
                                                                        {'author_set': request.user.id},
                                                                        {'group_type': 'PUBLIC'}
                                                                    ]
                                                                }
                                                            ]
                                                }
                                            ],
                                            '_type': 'Group',
                                            'name': {'$nin': GSTUDIO_DEFAULT_GROUPS_LIST},
                                            '_id': {'$nin': module_unit_ids},
                                              }).sort('last_update', -1)
    # base_unit_page_cur = paginator.Paginator(base_unit_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)

    context_variable.update({'all_modules': all_modules, 'units_cur': base_unit_cur})
    return render_to_response(
        # "ndf/explore.html", changed as per new Clix UI
        "ndf/explore_2017.html",
        # "ndf/lms_explore.html",
        context_variable,
        context_instance=RequestContext(request))

@login_required
@get_execution_time
def explore_drafts(request):
    title = 'drafts'
    modules_sort_list = None
    modules_sort_list = get_attribute_value(group_id, 'items_sort_list')
    context_variable = {
                        'title': title, 
                        'group_id': group_id, 'groupid': group_id,
                        'modules_is_cur': True
                    }
    modules_sort_list = get_attribute_value(group_id, 'items_sort_list')

    all_modules = node_collection.find({'member_of': gst_module_id ,'status':'PUBLISHED'}).sort('last_update', -1)
    if modules_sort_list:
        context_variable.update({'modules_sort_list': modules_sort_list})
    else:
        context_variable.update({'modules_sort_list': list(all_modules)})
        # modules_cur = map(Node,modules_sort_list)
        # context_variable.update({'modules_is_cur': False})
        # modules_node_sort_list = cast_to_node(modules_sort_list)
    all_modules.rewind()
    module_unit_ids = [val for each_module in all_modules for val in each_module.collection_set ]


    gstaff_access = check_is_gstaff(group_id,request.user)
    draft_query = {'member_of': gst_base_unit_id,
              '_id': {'$nin': module_unit_ids},
              'status':'PUBLISHED',
                }
    if not gstaff_access:
        draft_query.update({'$or': [
              {'created_by': request.user.id},
              {'group_admin': request.user.id},
              {'author_set': request.user.id},
              # No check on group-type PUBLIC for DraftUnits.
              # {'group_type': 'PUBLIC'}
              ]})

    base_unit_cur = node_collection.find(draft_query).sort('last_update', -1)
    # print "\nbase: ", base_unit_cur.count()


    '''
    base_unit_cur = node_collection.find({'member_of': gst_base_unit_id,
                                          '_id': {'$nin': module_unit_ids},
                                          'status':'PUBLISHED',
                                        '$or': [
                                          {'created_by': request.user.id},
                                          {'group_admin': request.user.id},
                                          {'author_set': request.user.id},
                                          # {'group_type': 'PUBLIC'}
                                          ]}).sort('last_update', -1)

    '''
#     base_unit_page_cur = paginator.Paginator(base_unit_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)

    # base_unit_page_cur = paginator.Paginator(base_unit_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)
    context_variable.update({'all_modules': all_modules, 'units_cur': base_unit_cur})

    # context_variable.update({'modules_cur': modules_cur,'units_cur': base_unit_cur})

    return render_to_response(
        # "ndf/explore.html", changed as per new Clix UI
        "ndf/explore_2017.html",
        # "ndf/lms_explore.html",
        context_variable,
        context_instance=RequestContext(request))

@get_execution_time
def module_order_list(request):
    response_dict = {"success": False}
    module_id_list = request.POST.get('module_list', [])
    try:
        items_sort_list_gattr_node = triple_collection.one({'_type': 'GAttribute', 'subject': group_id, 
            'attribute_type': at_items_sort_list._id, 'status': u'PUBLISHED'})
        if items_sort_list_gattr_node:
            ga_node = delete_gattribute(node_id=items_sort_list_gattr_node._id, deletion_type=0)

        if module_id_list:
            module_id_list = json.loads(module_id_list)
            module_obj_list = map(lambda each_id: Node.get_node_by_id(ObjectId(each_id)), module_id_list)
            ga_node = create_gattribute(ObjectId(group_id), 'items_sort_list', module_obj_list)
            response_dict["success"] = True

    except Exception as module_order_list_err:
        print "\nError Occurred in module_order_list(). ", module_order_list_err
        pass
    return HttpResponse(json.dumps(response_dict))

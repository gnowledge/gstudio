''' -- imports from python libraries -- '''
import json

''' -- imports from installed packages -- '''
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import GSystemType, Group, Node  # GSystem, Triple
from gnowsys_ndf.ndf.models import node_collection

from gnowsys_ndf.ndf.views.group import CreateGroup
from gnowsys_ndf.ndf.views.methods import get_execution_time, staff_required, create_gattribute
from gnowsys_ndf.ndf.views.ajax_views import get_collection

gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')
gst_lesson_name, gst_lesson_id = GSystemType.get_gst_name_id('lesson')
gst_activity_name, gst_activity_id = GSystemType.get_gst_name_id('activity')


@login_required
@staff_required
@get_execution_time
def unit_create_edit(request, group_id, unit_group_id=None):
    '''
    creation as well as eit of units
    '''

    parent_group_name, parent_group_id = Group.get_group_name_id(group_id)
    unit_node = None
    if request.method == "GET":
        unit_node = node_collection.one({'_id': ObjectId(unit_group_id)})
        template = "ndf/create_unit.html"
        all_groups = node_collection.find({'_type': "Group"},{"name":1})
        all_groups_names = [str(each_group.name) for each_group in all_groups]
        context_variables = {'group_id': parent_group_id,'groupid': parent_group_id, 'all_groups_names': all_groups_names}
        if unit_node:
            context_variables.update({'unit_node': unit_node})
        req_context = RequestContext(request, context_variables)
        return render_to_response(template, req_context)

    elif request.method == "POST":
        group_name = request.POST.get('name', '')
        group_altnames = request.POST.get('altnames', '')
        unit_id_post = request.POST.get('node_id', '')
        unit_altnames = request.POST.get('altnames', '')
        content = request.POST.get('content', '')


        educationallevel_val = request.POST.get('educationallevel', '')
        educationalsubject_val = request.POST.get('educationalsubject', '')
        # unit_group_id = unit_id_post if unit_id_post else unit_group_id
        # unit_group_name, unit_group_id = Group.get_group_name_id(unit_group_id)
        if unit_id_post:
            unit_node = node_collection.one({'_id': ObjectId(unit_id_post)})
        success_flag = False
        if unit_node:
            if unit_node.altnames is not unit_altnames:
                unit_node.altnames = unit_altnames
                unit_node.content = content
                unit_node.save()
                success_flag = True
        else:
            unit_group = CreateGroup(request)
            result = unit_group.create_group(group_name,
                                            group_id=parent_group_id,
                                            member_of=gst_base_unit_id,
                                            node_id=unit_group_id)
            success_flag = result[0]
            unit_node = result[1]

        if educationallevel_val and "choose" not in educationallevel_val.lower():
            educationallevel_at = node_collection.one({'_type': 'AttributeType', 'name': "educationallevel"})
            create_gattribute(unit_node._id, educationallevel_at, educationallevel_val)
        if educationalsubject_val and "choose" not in educationalsubject_val.lower():
            educationalsubject_at = node_collection.one({'_type': 'AttributeType', 'name': "educationalsubject"})
            create_gattribute(unit_node._id, educationalsubject_at, educationalsubject_val)

        if not success_flag:
            return HttpResponseRedirect(reverse('list_units', kwargs={'group_id': parent_group_id, 'groupid': parent_group_id,}))
        return HttpResponseRedirect(reverse('unit_detail',
            kwargs={'group_id': unit_node._id}))


@get_execution_time
def unit_detail(request, group_id):
    '''
    detail of of selected units
    '''
    # parent_group_name, parent_group_id = Group.get_group_name_id(group_id)
    unit_group_obj = Group.get_group_name_id(group_id, get_obj=True)

    unit_structure = _get_unit_hierarchy(unit_group_obj)
    # template = "ndf/unit_structure.html"
    template = 'ndf/gevent_base.html'

    # print unit_structure
    req_context = RequestContext(request, {
                                'title': 'unit_authoring',
                                'group_id': group_id,
                                'groupid': group_id,
                                'unit_obj': unit_group_obj,
                                'unit_structure': json.dumps(unit_structure)
                            })
    return render_to_response(template, req_context)


@get_execution_time
def list_units(request, group_id):
    '''
    listing of units
    '''
    parent_group_name, parent_group_id = Group.get_group_name_id(group_id)
    all_base_units = node_collection.find({
                                    '_type': 'Group',
                                    'group_set': {'$in': [parent_group_id]},
                                    'member_of': {'$in': [gst_base_unit_id]},
                                    '$or':[
                                        {'status': u'PUBLIC'},
                                        {
                                            '$and': [
                                                {'access_policy': u"PRIVATE"},
                                                {'created_by': request.user.id}
                                            ]
                                        }
                                    ]
                                }).sort('last_update', -1)

    template = "ndf/explore_2017.html"
    req_context = RequestContext(request, {
                                'group_id': parent_group_id,
                                'all_unit_objs': all_base_units
                            })
    return render_to_response(template, req_context)


########### LESSON methods ##########

@login_required
@staff_required
@get_execution_time
def lesson_create_edit(request, group_id, unit_group_id=None):
    '''
    creation as well as edit of lessons
    returns following list:
    {'success': <BOOL: 0 or 1>, 'unit_hierarchy': <unit hierarchy json>, 'msg': <error msg or objectid of newly created obj>}
    '''
    # parent_group_name, parent_group_id = Group.get_group_name_id(group_id)

    # parent unit id
    unit_id_post = request.POST.get('unit_id', '')
    unit_group_id = unit_id_post if unit_id_post else unit_group_id
    # getting parent unit object
    unit_group_obj = Group.get_group_name_id(unit_group_id, get_obj=True)
    result_dict = {'success': 0, 'unit_hierarchy': [], 'msg': ''}
    if request.method == "POST":
        # lesson name
        lesson_name = request.POST.get('name', '').strip()
        if not lesson_name:
            msg = 'Name can not be empty.'
            result_dict = {'success': 0, 'unit_hierarchy': [], 'msg': msg}
            # return HttpResponse(0)

        # unit_cs: unit collection_set
        unit_cs_list = unit_group_obj.collection_set
        unit_cs_objs_cur = Node.get_nodes_by_ids_list(unit_cs_list)
        unit_cs_names_list = [u.name for u in unit_cs_objs_cur]

        if lesson_name in unit_cs_names_list:
            msg = u'Activity with same name exists in lesson: ' + unit_group_obj.name
            result_dict = {'success': 0, 'unit_hierarchy': [], 'msg': msg}
            # return HttpResponse(0)
        else:
            user_id = request.user.id
            new_lesson_obj = node_collection.collection.GSystem()
            new_lesson_obj.fill_gstystem_values(name=lesson_name,
                                            member_of=gst_lesson_id,
                                            group_set=unit_group_obj._id,
                                            created_by=user_id,
                                            status='PUBLISHED')
            # print new_lesson_obj
            new_lesson_obj.save(groupid=group_id)
            unit_group_obj.collection_set.append(new_lesson_obj._id)
            unit_group_obj.save(groupid=group_id)

            unit_structure = _get_unit_hierarchy(unit_group_obj)

            msg = u'Added lesson under lesson: ' + unit_group_obj.name
            result_dict = {'success': 1, 'unit_hierarchy': unit_structure, 'msg': str(new_lesson_obj._id)}
            # return HttpResponse(json.dumps(unit_structure))

    # return HttpResponse(1)
    return HttpResponse(json.dumps(result_dict))


# @login_required
@get_execution_time
def activity_create_edit(request, group_id, lesson_id=None):
    '''
    creation as well as edit of activities
    returns following list:
    {'success': <BOOL: 0 or 1>, 'unit_hierarchy': <unit hierarchy json>, 'msg': <error msg or objectid of newly created obj>}
    '''
    # parent_group_name, parent_group_id = Group.get_group_name_id(group_id)
    lesson_id = request.POST.get('lesson_id')
    lesson_obj = Node.get_node_by_id(lesson_id)

    # parent unit id
    unit_id_post = request.POST.get('unit_id', '')
    unit_group_id = unit_id_post if unit_id_post else unit_group_id

    # getting parent unit object
    unit_group_obj = Group.get_group_name_id(unit_group_id, get_obj=True)

    result_dict = {'success': 0, 'unit_hierarchy': [], 'msg': ''}

    if request.method == "POST":
        # activity name
        activity_name = request.POST.get('name', '').strip()
        if not activity_name:
            msg = 'Name can not be empty.'
            result_dict = {'success': 0, 'unit_hierarchy': [], 'msg': msg}
            # return HttpResponse(result_dict)

        # unit_cs: unit collection_set
        lesson_cs_list = lesson_obj.collection_set
        lesson_cs_objs_cur = Node.get_nodes_by_ids_list(lesson_cs_list)
        lesson_cs_names_list = [u.name for u in lesson_cs_objs_cur]

        if activity_name in lesson_cs_names_list:
            msg = u'Activity with same name exists in lesson: ' + lesson_obj.name
            result_dict = {'success': 0, 'unit_hierarchy': [], 'msg': msg}
            # return HttpResponse(0)
        else:
            user_id = request.user.id
            new_activity_obj = node_collection.collection.GSystem()
            new_activity_obj.fill_gstystem_values(name=activity_name,
                                            member_of=gst_activity_id,
                                            group_set=unit_group_obj._id,
                                            created_by=user_id,
                                            status='PUBLISHED')
            new_activity_obj.save(groupid=group_id)

            lesson_obj.collection_set.append(new_activity_obj._id)
            lesson_obj.save(groupid=group_id)
            unit_structure = _get_unit_hierarchy(unit_group_obj)

            msg = u'Added activity under lesson: ' + lesson_obj.name
            result_dict = {'success': 1, 'unit_hierarchy': unit_structure, 'msg': str(new_activity_obj._id)}
            # return HttpResponse(json.dumps(unit_structure))

    return HttpResponse(json.dumps(result_dict))


def _get_unit_hierarchy(unit_group_obj):
    '''
    ARGS: unit_group_obj
    Result will be of following form:
    {
        name: 'Lesson1',
        type: 'lesson',
        id: 'l1',
        activities: [
            {
                name: 'Activity 1',
                type: 'activity',
                id: 'a1'
            },
            {
                name: 'Activity 1',
                type: 'activity',
                id: 'a2'
            }
        ]
    }, {
        name: 'Lesson2',
        type: 'lesson',
        id: 'l2',
        activities: [
            {
                name: 'Activity 1',
                type: 'activity',
                id: 'a1'
            }
        ]
    }
    '''
    unit_structure = []
    for each in unit_group_obj.collection_set:
        lesson_dict ={}
        lesson = Node.get_node_by_id(each)
        if lesson:
            lesson_dict['name'] = lesson.name
            lesson_dict['type'] = 'lesson'
            lesson_dict['id'] = str(lesson._id)
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
            unit_structure.append(lesson_dict)

    return unit_structure

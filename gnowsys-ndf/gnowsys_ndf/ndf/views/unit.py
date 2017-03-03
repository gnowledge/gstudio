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
from gnowsys_ndf.ndf.views.methods import get_execution_time, staff_required
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
    if request.method == "GET":
        template = "ndf/create_unit.html"
        req_context = RequestContext(request, {
                                    'group_id': parent_group_id  #,
                                    # 'unit_obj': unit_group_obj
                                })
        return render_to_response(template, req_context)

    elif request.method == "POST":
        group_name = request.POST.get('name', '')
        group_altnames = request.POST.get('altnames', '')
        unit_id_post = request.POST.get('_id', '')
        unit_group_id = unit_id_post if unit_id_post else unit_group_id
        unit_group_name, unit_group_id = Group.get_group_name_id(unit_group_id)

        if not group_name:
            raise ValueError('Unit Group must accompanied by name.')

        unit_group = CreateGroup(request)
        result = unit_group.create_group(group_name,
                                        group_id=parent_group_id,
                                        member_of=gst_base_unit_id,
                                        node_id=unit_group_id)

        # print result
        # return HttpResponse(int(result[0]))
        if not result[0]:
            return HttpResponseRedirect(reverse('list_units', kwargs={'group_id': group_id}))
        unit_node = result[1]
        return HttpResponseRedirect(reverse('unit_detail', 
            kwargs={'group_id': unit_node._id}))
    

@get_execution_time
def unit_detail(request, group_id):
    '''
    detail of of selected units
    '''
    # parent_group_name, parent_group_id = Group.get_group_name_id(group_id)
    unit_group_obj = Group.get_group_name_id(group_id, get_obj=True)

    # {
    # [{
    # //         name: 'Lesson1',
    # //         type: 'lesson',
    # //         id: 'l1',
    # //         activities: [
    # //             {
    # //                 name: 'Activity 1',
    # //                 type: 'activity',
    # //                 id: 'a1'
    # //             },
    # //             {
    # //                 name: 'Activity 1',
    # //                 type: 'activity',
    # //                 id: 'a2'
    # //             }
    # //         ]
    # //     }]
    # import ipdb; ipdb.set_trace()
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
                    activity = Node.get_node_by_id(lesson._id)
                    if activity:
                        activity_dict['name'] = lesson.name
                        activity_dict['type'] = 'lesson'
                        activity_dict['id'] = str(activity._id)
                        lesson_dict['activities'].append(activity_dict)
            unit_structure.append(lesson_dict)

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
    '''
    # parent_group_name, parent_group_id = Group.get_group_name_id(group_id)
    if request.method == "POST":
        # lesson name
        lesson_name = request.POST.get('name', '')
        if not lesson_name:
            return HttpResponse(0)

        # parent unit id
        unit_id_post = request.POST.get('unit_id', '')
        unit_group_id = unit_id_post if unit_id_post else unit_group_id
        # getting parent unit object
        unit_group_obj = Group.get_group_name_id(unit_group_id, get_obj=True)

        # unit_cs: unit collection_set
        unit_cs_list = unit_group_obj.collection_set
        unit_cs_objs_cur = Node.get_nodes_by_ids_list(unit_cs_list)
        unit_cs_names_list = [u.name for u in unit_cs_objs_cur]

        # print get_collection(request, ObjectId('57927168a6127d01f8e86574'), ObjectId('57927168a6127d01f8e86574'), no_res=False)
        if lesson_name in unit_cs_names_list:
            return HttpResponse(0)
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
                            activity = Node.get_node_by_id(lesson._id)
                            if activity:
                                activity_dict['name'] = lesson.name
                                activity_dict['type'] = 'lesson'
                                activity_dict['id'] = str(activity._id)
                                lesson_dict['activities'].append(activity_dict)
                    unit_structure.append(lesson_dict)

            return HttpResponse(json.dumps(unit_structure))

    return HttpResponse(1)



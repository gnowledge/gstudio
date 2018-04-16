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
from gnowsys_ndf.ndf.models import GSystemType, Group, Node, GSystem  #, Triple
from gnowsys_ndf.ndf.models import node_collection,triple_collection

from gnowsys_ndf.ndf.views.group import CreateGroup
from gnowsys_ndf.ndf.views.translation import get_lang_node,get_unit_hierarchy
from gnowsys_ndf.ndf.views.methods import get_execution_time, staff_required, create_gattribute,get_language_tuple,create_grelation, update_unit_in_modules
from gnowsys_ndf.ndf.views.ajax_views import get_collection

gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')
gst_lesson_name, gst_lesson_id = GSystemType.get_gst_name_id('lesson')
gst_activity_name, gst_activity_id = GSystemType.get_gst_name_id('activity')
gst_module_name, gst_module_id = GSystemType.get_gst_name_id('Module')
rt_translation_of = Node.get_name_id_from_type('translation_of', 'RelationType', get_obj=True)

@login_required
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
        modules = GSystem.query_list('home', 'Module', request.user.id)

        context_variables = {'group_id': parent_group_id,'groupid': parent_group_id, 'all_groups_names': all_groups_names, 
        'modules': modules}
        if unit_node:
            # get all modules which are parent's of this unit/group
            parent_modules = node_collection.find({
                    '_type': 'GSystem',
                    'member_of': gst_module_id,
                    'collection_set': {'$in': [unit_node._id]}
                })
            context_variables.update({'unit_node': unit_node, 'title': 'Create Unit',  'module_val_list': [str(pm._id) for pm in parent_modules]})
        req_context = RequestContext(request, context_variables)
        return render_to_response(template, req_context)

    elif request.method == "POST":
        group_name = request.POST.get('name', '')
        group_altnames = request.POST.get('altnames', '')
        unit_id_post = request.POST.get('node_id', '')
        unit_altnames = request.POST.get('altnames', '')
        content = request.POST.get('content', '')
        tags = request.POST.get('tags', [])
        language = request.POST.get('lan', '')
        group_type = request.POST.get('group_type', u'PUBLIC')

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
                success_flag = True
        else:
            unit_group = CreateGroup(request)
            result = unit_group.create_group(group_name,
                                            group_id=parent_group_id,
                                            member_of=gst_base_unit_id,
                                            node_id=unit_group_id)
            success_flag = result[0]
            unit_node = result[1]

        unit_id = unit_node._id
        if language:
            language_val = get_language_tuple(unicode(language))
            unit_node.language = language_val
        if educationallevel_val and "choose" not in educationallevel_val.lower():
            educationallevel_at = node_collection.one({'_type': 'AttributeType', 'name': "educationallevel"})
            create_gattribute(unit_node._id, educationallevel_at, educationallevel_val)
        if educationalsubject_val and "choose" not in educationalsubject_val.lower():
            educationalsubject_at = node_collection.one({'_type': 'AttributeType', 'name': "educationalsubject"})
            create_gattribute(unit_node._id, educationalsubject_at, educationalsubject_val)

        # modules
        module_val = request.POST.getlist('module', [])
        if module_val:
            update_unit_in_modules(module_val, unit_id)

        if not success_flag:
            return HttpResponseRedirect(reverse('list_units', kwargs={'group_id': parent_group_id, 'groupid': parent_group_id,}))

        # if tags:
        #     if not type(tags) is list:
        #         tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]
        #     unit_node.tags = tags
        if tags:
            tags = json.loads(tags)
        else:
            tags = []
        # unit_node.tags = tags
        unit_node.fill_group_values(group_type=group_type,tags=tags,author_set=unit_node.author_set)
        unit_node.content = content
        tab_name = request.POST.get('tab_name', '')
        resource_name = request.POST.get('resource_name', '')
        blog_name = request.POST.get('blog_name', '')
        section_name = request.POST.get('section_name', '')
        subsection_name = request.POST.get('subsection_name', '')

        if tab_name:
            unit_node['project_config'].update( {"tab_name":tab_name})
        elif "base_unit" in unit_node.member_of_names_list or "announced_unit" in unit_node.member_of_names_list :
            unit_node['project_config'].update( {"tab_name":"Lessons"})
        else:
            unit_node['project_config'].update( {"tab_name":"Tab Name"})

        if resource_name:
            unit_node['project_config'].update( {"resource_name":resource_name})
        elif "base_unit" in unit_node.member_of_names_list or "announced_unit" in unit_node.member_of_names_list :
            unit_node['project_config'].update( {"resource_name":"Resources"})
        else:
            unit_node['project_config'].update( {"resource_name":"Resource Name"})

        if blog_name:
            unit_node['project_config'].update( {"blog_name":blog_name})
        elif "base_unit" in unit_node.member_of_names_list or "announced_unit" in unit_node.member_of_names_list :
            unit_node['project_config'].update( {"blog_name":"e-Notes"})
        else:
            unit_node['project_config'].update( {"blog_name":"blog Name"})
        
        if section_name:
            unit_node['project_config'].update( {"section_name":section_name})
        elif "base_unit" in unit_node.member_of_names_list or "announced_unit" in unit_node.member_of_names_list :
            unit_node['project_config'].update({"section_name":"Lesson"})
        else:
            unit_node['project_config'].update({"section_name":"Section"})

        if subsection_name:
            unit_node['project_config'].update( {"subsection_name":subsection_name})
        elif "base_unit" in unit_node.member_of_names_list or "announced_unit" in unit_node.member_of_names_list :
            unit_node['project_config'].update({"subsection_name":"Add from Activities"})
        else:
            unit_node['project_config'].update({"subsection_name":"Add SubSection"})

        unit_node.save()
        return HttpResponseRedirect(reverse('course_content',
            kwargs={'group_id': unit_node._id}))


@get_execution_time
def unit_detail(request, group_id):
    '''
    detail of of selected units
    '''
    # parent_group_name, parent_group_id = Group.get_group_name_id(group_id)
    unit_group_obj = Group.get_group_name_id(group_id, get_obj=True)

    unit_structure = get_unit_hierarchy(unit_group_obj, request.LANGUAGE_CODE)
    # template = "ndf/unit_structure.html"
    # template = 'ndf/gevent_base.html'
    template = 'ndf/lms.html'

    # print unit_structure
    req_context = RequestContext(request, {
                                'title': 'unit_authoring',
                                'hide_bannerpic': True,
                                'group_id': unit_group_obj._id,
                                'groupid': unit_group_obj._id,
                                'group_name': unit_group_obj.name,
                                'unit_obj': unit_group_obj,
                                'group_obj': unit_group_obj,
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
@get_execution_time
def lesson_create_edit(request, group_id, unit_group_id=None):
    '''
    creation as well as edit of lessons
    returns following:
    {
        'success': <BOOL: 0 or 1>,
        'unit_hierarchy': <unit hierarchy json>,
        'msg': <error msg or objectid of newly created obj>
    }
    '''
    # parent_group_name, parent_group_id = Group.get_group_name_id(group_id)

    # parent unit id
    lesson_id = request.POST.get('lesson_id', None)
    lesson_language = request.POST.get('sel_lesson_lang','')
    unit_id_post = request.POST.get('unit_id', '')
    lesson_content = request.POST.get('lesson_desc', '')
    # print "lesson_id: ", lesson_id
    # print "lesson_language: ", lesson_language
    # print "unit_id_post: ", unit_id_post
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

        # check for uniqueness of name
        # unit_cs: unit collection_set
        unit_cs_list = unit_group_obj.collection_set
        unit_cs_objs_cur = Node.get_nodes_by_ids_list(unit_cs_list)
        if unit_cs_objs_cur:
            unit_cs_names_list = [u.name for u in unit_cs_objs_cur]

        if not lesson_id and unit_cs_objs_cur  and  lesson_name in unit_cs_names_list:  # same name activity
            # currently following logic was only for "en" nodes.
            # commented and expecting following in future:
            # check for uniqueness w.r.t language selected within all sibling lessons's translated nodes

            # lesson_obj = Node.get_node_by_id(lesson_id)
            # if lesson_language != lesson_obj.language[0]:
            #     if lesson_language:
            #         language = get_language_tuple(lesson_language)
            #         lesson_obj.language = language
            #         lesson_obj.save()
            msg = u'Activity with same name exists in lesson: ' + unit_group_obj.name
            result_dict = {'success': 0, 'unit_hierarchy': [], 'msg': msg}

        elif lesson_id and ObjectId.is_valid(lesson_id):  # Update
            # getting default, "en" node:
            if lesson_language != "en":
                node = translated_node_id = None
                grel_node = triple_collection.one({
                                        '_type': 'GRelation',
                                        'subject': ObjectId(lesson_id),
                                        'relation_type': rt_translation_of._id,
                                        'language': get_language_tuple(lesson_language),
                                        # 'status': 'PUBLISHED'
                                    })

                if grel_node:
                    # grelation found.
                    # transalated node exists.
                    # edit of existing translated node.

                    # node = Node.get_node_by_id(grel_node.right_subject)
                    # translated_node_id = node._id
                    lesson_id = grel_node.right_subject
                else:
                    # grelation NOT found.
                    # create transalated node.
                    user_id = request.user.id
                    new_lesson_obj = node_collection.collection.GSystem()
                    new_lesson_obj.fill_gstystem_values(name=lesson_name,
                                                    content=lesson_content,
                                                    member_of=gst_lesson_id,
                                                    group_set=unit_group_obj._id,
                                                    created_by=user_id,
                                                    status=u'PUBLISHED')
                    # print new_lesson_obj
                    if lesson_language:
                        language = get_language_tuple(lesson_language)
                        new_lesson_obj.language = language
                    new_lesson_obj.save(groupid=group_id)
                    
                    trans_grel_list = [ObjectId(new_lesson_obj._id)]
                    trans_grels = triple_collection.find({'_type': 'GRelation', \
                            'relation_type': rt_translation_of._id,'subject': ObjectId(lesson_id)},{'_id': 0, 'right_subject': 1})
                    for each_rel in trans_grels:
                        trans_grel_list.append(each_rel['right_subject'])
                    # translate_grel = create_grelation(node_id, rt_translation_of, trans_grel_list, language=language)

                    create_grelation(lesson_id, rt_translation_of, trans_grel_list, language=language)

            lesson_obj = Node.get_node_by_id(lesson_id)
            if lesson_obj and (lesson_obj.name != lesson_name):
                trans_lesson = get_lang_node(lesson_obj._id,lesson_language)
                if trans_lesson:
                    trans_lesson.name = lesson_name
                else:
                    lesson_obj.name = lesson_name
                # if lesson_language:
                #     language = get_language_tuple(lesson_language)
                #     lesson_obj.language = language
                lesson_obj.save(group_id=group_id)

                unit_structure = get_unit_hierarchy(unit_group_obj, request.LANGUAGE_CODE)
                msg = u'Lesson name updated.'
                result_dict = {'success': 1, 'unit_hierarchy': unit_structure, 'msg': str(lesson_obj._id)}
            else:
                unit_structure = get_unit_hierarchy(unit_group_obj, request.LANGUAGE_CODE)
                msg = u'Nothing to update.'
                result_dict = {'success': 1, 'unit_hierarchy': unit_structure, 'msg': msg}

        else: # creating a fresh lesson object
            user_id = request.user.id
            new_lesson_obj = node_collection.collection.GSystem()
            new_lesson_obj.fill_gstystem_values(name=lesson_name,
                                            content=lesson_content,
                                            member_of=gst_lesson_id,
                                            group_set=unit_group_obj._id,
                                            created_by=user_id,
                                            status=u'PUBLISHED')
            # print new_lesson_obj
            if lesson_language:
                language = get_language_tuple(lesson_language)
                new_lesson_obj.language = language
            new_lesson_obj.save(groupid=group_id)
            unit_group_obj.collection_set.append(new_lesson_obj._id)
            unit_group_obj.save(groupid=group_id)

            unit_structure = get_unit_hierarchy(unit_group_obj, request.LANGUAGE_CODE)

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
                                            status=u'PUBLISHED')
            new_activity_obj.save(groupid=group_id)

            lesson_obj.collection_set.append(new_activity_obj._id)
            lesson_obj.save(groupid=group_id)
            unit_structure = get_unit_hierarchy(unit_group_obj, request.LANGUAGE_CODE)

            msg = u'Added activity under lesson: ' + lesson_obj.name
            result_dict = {'success': 1, 'unit_hierarchy': unit_structure, 'msg': str(new_activity_obj._id)}
            # return HttpResponse(json.dumps(unit_structure))

    return HttpResponse(json.dumps(result_dict))



def _get_unit_hierarchy(unit_group_obj,lang="en"):
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
            trans_lesson = get_lang_node(lesson._id,lang)
            if trans_lesson:
                lesson_dict['name'] = trans_lesson.name
            else:
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
                        trans_act = get_lang_node(activity._id,lang)
                        if trans_act:
                            # activity_dict['name'] = trans_act.name
                            activity_dict['name'] = trans_act.altnames or trans_act.name
                        else:
                            # activity_dict['name'] = activity.name
                            activity_dict['name'] = activity.altnames or activity.name
                        activity_dict['type'] = 'activity'
                        activity_dict['id'] = str(activity._id)
                        lesson_dict['activities'].append(activity_dict)
            unit_structure.append(lesson_dict)

    return unit_structure

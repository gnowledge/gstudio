try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from gnowsys_ndf.ndf.models import Node, GSystem, GSystemType, RelationType, Group
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import get_group_name_id, get_language_tuple, create_grelation
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_LANGUAGE
from gnowsys_ndf.ndf.templatetags.ndf_tags import  get_relation_value


# gst_page_name, gst_page_id = GSystemType.get_gst_name_id(u'Page')
rt_translation_of = Node.get_name_id_from_type('translation_of', 'RelationType', get_obj=True)
supported_languages = ['Hindi', 'Telugu']
trans_node_gst_name, trans_node_gst_id = GSystemType.get_gst_name_id("trans_node")

def all_translations(request, group_id, node_id):
    '''
    returns all translated nodes of provided node.
    '''
    node_obj = Node.get_node_by_id(node_id)
    # node_translation_grels = node_obj.get_relation('translation_of', status='PUBLISHED')
    # return node_translation_grels

    # node_translation_grels = node_obj.get_relation('translation_of')
    all_translation_nodes = node_obj.get_relation_right_subject_nodes('translation_of')

    return render_to_response("ndf/translation_list.html",
                              {
                                'group_id': Group.get_group_name_id(group_id)[1],
                                'groupid': Group.get_group_name_id(group_id)[1],
                                'title': 'Translation',
                                'nodes': all_translation_nodes,
                                'node': node_obj,
                                'source_node_id': node_id,
                                'card_url_name': 'show_translation',
                                'supported_languages': supported_languages                               },
                              context_instance=RequestContext(request))


def show_translation(request, group_id, node_id, lang):
    '''
    for VIEW/READ: show translated provided node to provided LANG CODE
    lang could be either proper/full language-name/language-code
    '''
    node = translated_node_id = None
    grel_node = triple_collection.one({
                            '_type': 'GRelation',
                            'subject': ObjectId(node_id),
                            'relation_type': rt_translation_of._id,
                            'language': get_language_tuple(lang),
                            # 'status': 'PUBLISHED'
                        })

    if grel_node:
        node = Node.get_node_by_id(grel_node.right_subject)
        translated_node_id = node._id

    # code to show other translations
    other_translations_grels = triple_collection.find({
                            '_type': u'GRelation',
                            'subject': ObjectId(node_id),
                            'relation_type': rt_translation_of._id,
                            'right_subject': {'$nin': [translated_node_id]}
                        })

    other_translations = node_collection.find({'_id': {'$in': [r.right_subject for r in other_translations_grels]} })

    # --- END of code to show other translations

    return render_to_response("ndf/translate_detail.html",
                          {
                            'group_id': Group.get_group_name_id(group_id)[1],
                            'groupid': Group.get_group_name_id(group_id)[1],
                            'source_node_id': node_id,
                            'source_node_obj': Node.get_node_by_id(node_id),
                            'node': node,
                            'other_translations': other_translations,
                            'card_url_name': 'show_translation',
                           },
                          context_instance=RequestContext(request))



@login_required
def translate(request, group_id, node_id, lang, translated_node_id=None, **kwargs):
    '''
    for EDIT: translate provided node to provided LANG CODE
    lang could be either proper/full language-name/language-code
    `node_id` is _id of source node.
    '''
    group_name, group_id = Group.get_group_name_id(group_id)
    language = get_language_tuple(lang)
    source_obj = Node.get_node_by_id(node_id)

    existing_grel = translate_grel = translated_node = None

    if translated_node_id:
        translated_node = Node.get_node_by_id(translated_node_id)
    else:
        # get translated_node
        existing_grel = triple_collection.one({
                                            '_type': 'GRelation',
                                            'subject': ObjectId(node_id),
                                            'relation_type': rt_translation_of._id,
                                            'language': language
                                        })

        if existing_grel:
            # get existing translated_node
            translated_node = Node.get_node_by_id(existing_grel.right_subject)
            translate_grel = existing_grel

    if request.method == 'GET':
        return render_to_response("ndf/translate_form.html",
                              {
                                'group_id': group_id,
                                'node_obj': translated_node,
                                'source_obj': source_obj,
                                'post_url': reverse('translate', kwargs={
                                        'group_id': group_id,
                                        'node_id': node_id,
                                        'lang': lang,
                                        }),
                                'cancel_url':reverse('show_translation', kwargs={
                                        'group_id': group_id,
                                        'node_id': node_id,
                                        'lang': lang,
                                        })
                               },
                              context_instance=RequestContext(request))

    elif request.method == 'POST':  # explicit `if` check for `POST`
        if not translated_node:
            # create a new translated new
            # translated_node = node_collection.collection.GSystem()
            # copy source_obj's data into a new
            if source_obj._type == "Group":
                translated_node = node_collection.collection.GSystem()
                exclude_fields = ['_id','member_of','_type','type_of','modified_by','prior_node','post_node']
                for each in translated_node:
                    if each not in exclude_fields:
                        translated_node[each] = source_obj[each]
                translated_node.group_set.append(source_obj._id)
            else:
                translated_node = source_obj.__deepcopy__()
                translated_node['_id'] = ObjectId()

        translated_node.fill_gstystem_values(request=request,
                                            language=language,
                                            **kwargs)
        trans_alt_name = request.POST.get('altnames', None)
        
        translated_node.altnames = unicode(trans_alt_name)
        translated_node.member_of = [ObjectId(trans_node_gst_id)]
        translated_node.save(group_id=group_id)
        if not existing_grel:
            trans_grel_list = [ObjectId(translated_node._id)]
            trans_grels = triple_collection.find({'_type': 'GRelation', \
                            'relation_type': rt_translation_of._id,'subject': ObjectId(node_id)},{'_id': 0, 'right_subject': 1})
            for each_rel in trans_grels:
                trans_grel_list.append(each_rel['right_subject'])
            translate_grel = create_grelation(node_id, rt_translation_of, trans_grel_list, language=language)

    # page_gst_name, page_gst_id = Node.get_name_id_from_type('Page', 'GSystemType')
    # return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': page_gst_id }))
    # return HttpResponseRedirect(reverse('all_translations', kwargs={'group_id': group_id, 'node_id': node_id }))
    return HttpResponseRedirect(reverse('show_translation', kwargs={'group_id': group_id, 'node_id': node_id, 'lang': lang }))
    # return translated_node, translate_grel


def get_lang_node(node_id,lang):
    rel_value = get_relation_value(ObjectId(node_id),"translation_of")
    for each in rel_value['grel_node']:
        if each.language[0] ==  get_language_tuple(lang)[0]:
            trans_node = each
            return trans_node

def get_trans_node_list(node_list,lang):
    trans_node_list = []
    for each in node_list:
        each_node = get_lang_node(each,lang)
        if each_node :  
            trans_node_list.append({ObjectId(each_node._id): {"name":(each_node.altnames or each_node.name),"basenodeid":ObjectId(each)}})
            # trans_node_list.append({ObjectId(each_node._id): {"name": each_node.name, "basenodeid":ObjectId(each)}})
        else:
            node = node_collection.one({"_id":ObjectId(each)})
            trans_node_list.append({ObjectId(node._id): {"name":(node.altnames or node.name),"basenodeid":ObjectId(node._id)}})
            # trans_node_list.append({ObjectId(node._id): {"name": node.name, "basenodeid":ObjectId(node._id)}})
    if trans_node_list:
        return trans_node_list

def get_course_content_hierarchy(unit_group_obj,lang="en"):
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
                lesson_dict['label'] = trans_lesson.name
            else:
                lesson_dict['label'] = lesson.name
            lesson_dict['id'] = lesson._id
            lesson_dict['type'] = 'unit-name'
            lesson_dict['children'] = []
            if lesson.collection_set:
                for each_act in lesson.collection_set:
                    activity_dict ={}
                    activity = Node.get_node_by_id(each_act)
                    if activity:
                        trans_act_name = get_lang_node(each_act,lang)
                        # activity_dict['label'] = trans_act_name.name or activity.name  
                        if trans_act_name:
                            activity_dict['label'] = trans_act_name.altnames or trans_act_name.name
                            # activity_dict['label'] = trans_act_name.name
                        else:
                            # activity_dict['label'] = activity.name
                            activity_dict['label'] = activity.altnames or activity.name
                        activity_dict['type'] = 'activity-group'
                        activity_dict['id'] = str(activity._id)
                        lesson_dict['children'].append(activity_dict)
            unit_structure.append(lesson_dict)
    return unit_structure



def get_unit_hierarchy(unit_group_obj,lang="en"):
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

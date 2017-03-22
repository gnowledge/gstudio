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

from gnowsys_ndf.ndf.models import Node, GSystem, GSystemType, RelationType #, Triple
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import get_group_name_id, get_language_tuple, create_grelation
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_LANGUAGE

# gst_page_name, gst_page_id = GSystemType.get_gst_name_id(u'Page')
rt_translation_of = Node.get_name_id_from_type('translation_of', 'RelationType', get_obj=True)

def all_translations(request, group_id, node_id):
    '''
    returns all translated nodes of provided node.
    '''
    node_obj = Node.get_node_by_id(node_id)
    node_translation_grels = node_obj.get_relation('translation_of', status='PUBLISHED')
    return node_translation_grels


def show_translation(request, group_id, node_id, lang):
    '''
    for VIEW/READ: show translated provided node to provided LANG CODE
    lang could be either proper/full language-name/language-code
    '''
    grel_node = triple_collection.one({
                            '_type': 'GRelation',
                            'subject': ObjectId(node_id),
                            'relation_type': rt_translation_of._id,
                            'language': list(get_language_tuple(lang)),
                            'status': 'PUBLISHED'
                        })

    if grel_node:
        return Node.get_node_by_id(grel_node.right_subject)


# def translate(request, group_id, node_id, lang):
# @login_required
def translate(request, group_id, node_id, lang, translated_node_id=None, **kwargs):
    '''
    for EDIT: translate provided node to provided LANG CODE
    lang could be either proper/full language-name/language-code
    `node_id` is _id of source node.
    '''
    language = get_language_tuple(lang)
    source_obj = Node.get_node_by_id(node_id)

    existing_grel = None
    translate_grel = None
    if translated_node_id:
        translated_node = Node.get_node_by_id(translated_node_id)
    else:
        existing_grel = triple_collection.one({
                                            '_type': 'GRelation',
                                            'subject': ObjectId(node_id),
                                            'relation_type': rt_translation_of._id,
                                            'language': language
                                        })

        if existing_grel:
            translated_node = Node.get_node_by_id(existing_grel.right_subject)
            translate_grel = existing_grel
        else:
            # translated_node = node_collection.collection.GSystem()
            translated_node = source_obj.__deepcopy__()
            translated_node['_id'] = ObjectId()

    translated_node.fill_gstystem_values(request=request,
                                        language=language,
                                        **kwargs)
    translated_node.save(group_id=group_id)
    if not existing_grel:
        translate_grel = create_grelation(node_id, rt_translation_of, translated_node._id, language=language)

    # page_gst_name, page_gst_id = Node.get_name_id_from_type('Page', 'GSystemType')
    # return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': page_gst_id }))
    return translated_node, translate_grel
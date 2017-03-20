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

# gst_asset_name, gst_asset_id = GSystemType.get_gst_name_id(u'Asset')
gst_page_name, gst_page_id = GSystemType.get_gst_name_id(u'Page')
# gst_file_name, gst_file_id = GSystemType.get_gst_name_id(u'File')


def all_translations(request, group_id, node_id):
    '''
    returns all translated nodes of provided node.
    '''
    node_obj = Node.get_node_by_id(node_id)
    node_translation_grels = node_obj.get_relation('translation_of')
    return ''


def show_translation(request, group_id, node_id, lang):
    '''
    for VIEW/READ: show translated provided node to provided LANG CODE
    lang could be either proper/full language-name/language-code
    '''
    pass


# def translate(request, group_id, node_id, lang):
@login_required
def translate(request, group_id, node_id, lang, translated_node_id=None, **kwargs):
    '''
    for EDIT: translate provided node to provided LANG CODE
    lang could be either proper/full language-name/language-code
    `node_id` is _id of source node.
    '''
    language = get_language_tuple(lang)
    source_obj = Node.get_node_by_id(node_id)
    context_variables = { 'title': 'Translate',
                          'group_id': group_id,
                          'groupid': group_id,
                          'node': Node.get_node_by_id(node_id)
                      }
    if request.method == "GET":
        return render_to_response(
                        "ndf/page_create_edit.html",
                        context_variables,
                        context_instance=RequestContext(request)
                    )


    if request.method == "POST":
        existing_grel = None
        if translated_node_id:
            translated_node = Node.get_node_by_id(translated_node_id)
        else:
            rt_translation_of = Node.get_name_id_from_type('translation_of', 'RelationType', get_obj=True)

            existing_grel = triple_collection.one({
                                                '_type': 'GRelation',
                                                'subject': ObjectId(node_id),
                                                'relation_type': rt_translation_of._id,
                                                'language': get_language_tuple(lang)
                                            })

            if existing_grel:
                translated_node = Node.get_node_by_id(existing_grel.right_subject)
            else:
                translated_node = node_collection.collection.GSystem()
                print 'translated_node'
                # import ipdb; ipdb.set_trace()
                translated_node['_id'] = ObjectId()

        translated_node.fill_gstystem_values(request=request, **kwargs)
        translated_node['member_of'] = source_obj.member_of
        translated_node.save()
        print translated_node
        if not existing_grel:
            create_grelation(node_id, rt_translation_of, translated_node._id, language=language)

        page_gst_name, page_gst_id = Node.get_name_id_from_type('Page', 'GSystemType')
        return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': page_gst_id }))
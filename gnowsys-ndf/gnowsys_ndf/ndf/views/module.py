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
from gnowsys_ndf.ndf.models import node_collection

from gnowsys_ndf.ndf.views.group import CreateGroup
from gnowsys_ndf.ndf.views.methods import get_execution_time, staff_required, create_gattribute,get_language_tuple
from gnowsys_ndf.ndf.views.ajax_views import get_collection
from gnowsys_ndf.settings import GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL, GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT
from gnowsys_ndf.ndf.templatetags.ndf_tags import check_is_gstaff
gst_module_name, gst_module_id = GSystemType.get_gst_name_id('Module')
gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')
gst_announced_unit_name, gst_announced_unit_id = GSystemType.get_gst_name_id('announced_unit')


@get_execution_time
def list_modules(request, group_id):
    '''
    listing of modules
    '''
    all_modules = GSystem.query_list(group_id, 'Module', request.user.id)
    template = "ndf/explore_2017.html"

    context_variable = {
                        'title': 'Modules', 'doc_cur': all_modules,
                        'group_id': group_id, 'groupid': group_id,
                        'card': 'ndf/horizontal_card.html', 'card_url_name': 'module_detail'
                    }

    return render_to_response(
        template,
        context_variable,
        context_instance=RequestContext(request))


@login_required
@get_execution_time
def module_create_edit(request, group_id, module_id=None, cancel_url='list_modules'):
    if request.method == "GET":

        template = 'ndf/module_form.html'
        additional_form_fields = {}
        module_attrs = ['educationalsubject', 'educationallevel']
        # ma: module attr
        module_attr_values = {ma: '' for ma in module_attrs}

        if module_id:
            # existing module.
            url_name = 'node_edit'
            url_kwargs={'group_id': group_id, 'node_id': module_id, 'detail_url_name': 'module_detail'}
            # updating module attr dict:
            module_obj = Node.get_node_by_id(module_id)
            module_attr_values = module_obj.get_attributes_from_names_list(module_attrs)

        else:
            # new module
            url_name = 'node_create'
            url_kwargs={'group_id': group_id, 'member_of': 'Module', 'detail_url_name': 'module_detail'}

        additional_form_fields = {
            'attribute': {
                'Subject': {
                    'name' :'educationalsubject',
                    'widget': 'dropdown',
                    'value': module_attr_values['educationalsubject'],
                    'all_options': GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT
                },
                'Grade': {
                    'name' :'educationallevel',
                    'widget': 'dropdown',
                    'widget_attr': 'multiple',
                    'value': module_attr_values['educationallevel'],
                    'all_options': GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL
                }
            }
        }

        req_context = RequestContext(request, {
                                    'title': 'Module', 'node_obj': Node.get_node_by_id(module_id),
                                    'group_id': group_id, 'groupid': group_id,
                                    'additional_form_fields': additional_form_fields,
                                    'post_url': reverse(url_name, kwargs=url_kwargs)
                                })
        return render_to_response(template, req_context)


@get_execution_time
def module_detail(request, group_id, node_id,title=""):
    '''
    detail of of selected module
    '''
    group_name, group_id = Group.get_group_name_id(group_id)

    module_obj = Node.get_node_by_id(node_id)

    # module_detail_query = {'member_of': gst_base_unit_id,
    #           '_id': {'$nin': module_unit_ids},
    #           'status':'PUBLISHED',
    #             }
    # if not gstaff_access:
    #     module_detail_query.update({'$or': [
    #           {'created_by': request.user.id},
    #           {'group_admin': request.user.id},
    #           {'author_set': request.user.id},
    #           # No check on group-type PUBLIC for DraftUnits.
    #           # {'group_type': 'PUBLIC'}
    #           ]})



    gstaff_access = check_is_gstaff(group_id,request.user)
    module_detail_query = {'_id': {'$in': module_obj.collection_set},
    'status':'PUBLISHED'
    }

    if module_obj.collection_set:
        module_detail_query = {'_id': {'$in': module_obj.collection_set},
        'status':'PUBLISHED'
        }
    elif module_obj.post_node:
        module_detail_query = {'_id': {'$in': module_obj.post_node},
        'status':'PUBLISHED'
        }
    

    
    if not gstaff_access:
        module_detail_query.update({'$or': [
        {'$and': [
            {'member_of': gst_base_unit_id},
            {'$or': [
              {'created_by': request.user.id},
              {'group_admin': request.user.id},
              {'author_set': request.user.id},
            ]}
        ]},
        {'member_of': gst_announced_unit_id}
      ]})
    
    if title == "courses":
        module_detail_query.update({'$or': [
        {'$and': [
            {'member_of': gst_announced_unit_id},
            {'$or': [
              {'created_by': request.user.id},
              {'group_admin': request.user.id},
              {'author_set': request.user.id},
            ]}
        ]},
        {'member_of': gst_announced_unit_id }
      ]})

    
    if title == "drafts":
        module_detail_query.update({'$or': [
        {'$and': [
            {'member_of': gst_base_unit_id},
            {'$or': [
              {'created_by': request.user.id},
              {'group_admin': request.user.id},
              {'author_set': request.user.id},
            ]}
        ]},
      ]}) 

    # units_under_module = Node.get_nodes_by_ids_list(module_obj.collection_set)
    '''
    gstaff_access = check_is_gstaff(group_id, request.user)

    if gstaff_access:
        module_detail_query.update({'member_of': {'$in': [gst_announced_unit_id, gst_base_unit_id]}})
    else:
        module_detail_query.update({'member_of': gst_announced_unit_id})
    '''

    units_under_module = node_collection.find(module_detail_query).sort('last_update', -1)
    template = 'ndf/module_detail.html'

    req_context = RequestContext(request, {
                                'title': title,
                                'node': module_obj, 'units_under_module': units_under_module,
                                'group_id': group_id, 'groupid': group_id,
                                'card': 'ndf/event_card.html', 'card_url_name': 'groupchange'
                            })
    return render_to_response(template, req_context)

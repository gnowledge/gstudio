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

gst_module_name, gst_module_id = GSystemType.get_gst_name_id('Module')


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
                        'card': 'ndf/event_card.html', 'card_url_name': 'module_detail'
                    }

    return render_to_response(
        template,
        context_variable,
        context_instance=RequestContext(request))


@login_required
@get_execution_time
def module_create_edit(request, group_id, module_id=None):
    if request.method == "GET":

        template = 'ndf/module_form.html'

        req_context = RequestContext(request, {
                                    'title': 'Module', 'node_obj': Node.get_node_by_id(module_id),
                                    'group_id': group_id, 'groupid': group_id,
                                    'post_url': reverse('node_create', kwargs={
                                        'group_id': group_id,
                                        'member_of': 'Module',
                                        'detail_url_name': 'module_detail',
                                        })
                                })
        return render_to_response(template, req_context)


@get_execution_time
def module_detail(request, group_id, node_id):
    '''
    detail of of selected module
    '''
    group_name, group_id = Group.get_group_name_id(group_id)

    module_obj = Node.get_node_by_id(node_id)

    units_under_module = Node.get_nodes_by_ids_list(module_obj.collection_set)

    template = 'ndf/module_detail.html'

    req_context = RequestContext(request, {
                                'title': 'Module',
                                'node': module_obj, 'units_under_module': units_under_module,
                                'group_id': group_id, 'groupid': group_id,
                                'card': 'ndf/event_card.html', 'card_url_name': 'module_detail'
                            })
    return render_to_response(template, req_context)

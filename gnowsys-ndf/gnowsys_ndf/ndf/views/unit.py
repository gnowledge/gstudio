''' -- imports from python libraries -- '''
#

''' -- imports from installed packages -- '''
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import GSystemType, Group, Node  # GSystem, Triple
from gnowsys_ndf.ndf.models import node_collection

from gnowsys_ndf.ndf.views.group import CreateGroup
from gnowsys_ndf.ndf.views.methods import get_execution_time, staff_required

gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')


@login_required
@staff_required
@get_execution_time
def unit_create_edit(request, group_id_or_name, unit_group_id_or_name=None):
    '''
    creation as well as eit of units
    '''
    group_name = request.POST.get('name', '')
    parent_group_name, parent_group_id = Group.get_group_name_id(group_id_or_name)
    unit_group_name, unit_group_id = Group.get_group_name_id(unit_group_id_or_name)

    if not group_name:
        raise ValueError('Unit Group must accompanied by name.')

    unit_group = CreateGroup(request)
    result = unit_group.create_group(group_name,
                                    group_id=parent_group_id,
                                    member_of=gst_base_unit_id,
                                    node_id=unit_group_id)

    return HttpResponse(int(result[0]))


@get_execution_time
def unit_detail(request, group_id_or_name, unit_name_or_id):
    '''
    detail of of selected units
    '''
    parent_group_name, parent_group_id = Group.get_group_name_id(group_id_or_name)
    unit_group_obj = Group.get_group_name_id(unit_group_id_or_name, get_obj=True)

    template = "ndf/unit_detail.html"
    req_context = RequestContext(request, {
                                'group_id': parent_group_id,
                                'unit_obj': unit_group_obj
                            })
    return render_to_response(template, req_context)


@get_execution_time
def list_units(request, group_id_or_name):
    '''
    listing of units
    '''
    parent_group_name, parent_group_id = Group.get_group_name_id(group_id_or_name)
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

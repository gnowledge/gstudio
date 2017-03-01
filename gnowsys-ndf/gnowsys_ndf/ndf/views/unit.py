''' -- imports from python libraries -- '''

''' -- imports from installed packages -- '''
from django.http import HttpResponse

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.views.group import CreateGroup
from gnowsys_ndf.ndf.models import GSystemType, Group  # GSystem, Triple

gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')

def unit_create_edit(request, group_id_or_name, unit_group_id_or_name=None):

	group_name = request.POST.get('name', '')
	parent_group_name, parent_group_id = Group.get_group_name_id(group_id_or_name)
	unit_group_name, unit_group_id = Group.get_group_name_id(unit_group_id_or_name)

	if not group_name:
		raise ValueError('Unit Group must accompanied by name.')

	unit_group = CreateGroup(request)
	result = unit_group.create_group(group_name,
									group_id=[parent_group_id],
									member_of=[gst_base_unit_id],
									node_id=unit_group_id)

	return HttpResponse(int(result[0]))


def unit_detail(request, group_id_or_name, unit_name_or_id):
	pass


def list_units(request, group_id_or_name):
	pass
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_attribute_value

gst_module_name, gst_module_id = GSystemType.get_gst_name_id('Module')
gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')
gst_announced_unit_name, gst_announced_unit_id = GSystemType.get_gst_name_id('announced_unit')
subject_groups = {}
for gr_name in GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT:
	node_obj = Group.get_group_name_id(gr_name,get_obj=True)
	subject_groups.update({node_obj.name: node_obj})

def update_field(node_obj, attr, field_name, advanced=False):
	if attr in subject_groups.keys():
		if subject_groups[attr] not in node_obj[field_name]:
			node_obj[field_name].append(subject_groups[attr]._id)
		if advanced and node_obj._id not in subject_groups[attr].post_node:
			subject_groups[attr].post_node.append(node_obj._id)
			subject_groups[attr].save()

# Updating Modules
module_cur = node_collection.find({'member_of': gst_module_id})
for each_module in module_cur:
	print "\n Updating group_set of: ", each_module.name
	module_attr_value = get_attribute_value(each_module._id,"educationalsubject")
	if isinstance(module_attr_value, list):
		for each_attr in module_attr_value:
			update_field(each_module, each_attr, field_name='group_set')
	else:
		update_field(each_module, module_attr_value, field_name='group_set')
	each_module.save()


# Updating Units
unit_cur = node_collection.find({'member_of': {'$in': [gst_announced_unit_id, gst_base_unit_id]}})
for each_unit in unit_cur:
	print "\n Updating Unit: ", each_unit.name
	unit_attr_value = get_attribute_value(each_unit._id,"educationalsubject")
	if isinstance(unit_attr_value, list):
		for each_attr in unit_attr_value:
			update_field(each_unit, each_attr, field_name='prior_node', advanced=True)
	else:
		update_field(each_unit, unit_attr_value, field_name='prior_node', advanced=True)
	each_unit.save()


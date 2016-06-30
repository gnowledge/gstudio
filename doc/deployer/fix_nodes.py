from datetime import datetime
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *
incorrect_value_gattr = []

start_time_at = node_collection.one({'_type': "AttributeType", 'name': 'start_time'})

end_time_at = node_collection.one({'_type': "AttributeType", 'name': 'end_time'})

start_enroll_at = node_collection.one({'_type': "AttributeType", 'name': 'start_enroll'})

end_enroll_at = node_collection.one({'_type': "AttributeType", 'name': 'end_enroll'})

all_date_gattr = triple_collection.find({'_type': "GAttribute", 'attribute_type.$id': {'$in': [start_time_at._id, end_time_at._id, start_enroll_at._id, end_enroll_at._id]}})
created_at_long_nodes_cur = node_collection.find({'created_at':{'$type': "long"}})

date_gattr = all_date_gattr.count()

if date_gattr > 0:
	for each in all_date_gattr:
		#print type(each.object_value)
		if type(each.object_value) == long:
			incorrect_value_gattr.append(each)
	print "\n Total nodes to be fixed: ", len(incorrect_value_gattr) + created_at_long_nodes_cur.count()

	for each_created_at_long in created_at_long_nodes_cur:
		old_created_at_val = each_created_at_long.created_at
		new_created_at_val = datetime.fromtimestamp(old_created_at_val/1e3)
		each_created_at_long.created_at = new_created_at_val
		each_created_at_long.save(validate=False)

	if incorrect_value_gattr:
		for each_gattr in incorrect_value_gattr:
			attr_type_name = each_gattr.attribute_type.name
			if attr_type_name == "start_enroll":
				at_node = start_enroll_at
			elif attr_type_name == "end_enroll":
				at_node = end_enroll_at
			elif attr_type_name == "start_time":
				at_node = start_time_at
			elif attr_type_name == "end_time":
				at_node = end_time_at
			old_object_value = each_gattr.object_value
			new_object_value = datetime.fromtimestamp(old_object_value/1e3)
			create_gattribute(each_gattr.subject, at_node, new_object_value)

gr = node_collection.one({'name':'I2C-V2'})
if gr and gr.collection_set:
	gr.collection_set = list(set(gr.collection_set))
	gr.save()
	for cs_id in gr.collection_set:
		cs_node = node_collection.one({'_id': ObjectId(cs_id)})
		if cs_node.collection_set:
			cs_node.collection_set = list(set(cs_node.collection_set))
			cs_node.save()
			for css_id in cs_node.collection_set:
				css_node = node_collection.one({'_id': ObjectId(css_id)})
				if css_node.collection_set:
					css_node.collection_set = list(set(css_node.collection_set))
					css_node.save()
					for cu_id in css_node.collection_set:
						cu_node = node_collection.one({'_id': ObjectId(cu_id)})
						if cu_node.collection_set:
							cu_node.collection_set = list(set(cu_node.collection_set))
							cu_node.save()

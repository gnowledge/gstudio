from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import dig_nodes_field

group_id_str = raw_input("Enter Group_id: ")
group_obj = node_collection.one({'_id': ObjectId(group_id_str)})
if group_obj:
	all_leaf_node_ids = dig_nodes_field(parent_node=n, member_of=['Page'], only_leaf_nodes=True)
	all_leaf_node_cur = node_collection.find({'_id': {'$in': all_leaf_node_ids}})
	print "\nLeaf nodes found: ", all_leaf_node_cur.count()
	for each_node in all_leaf_node_cur:
		name_val = each_node.name 
		print "\n ", each_node.altnames , " --->", name_val
		each_node.altnames = name_val # Unique name --> Display name 
		each_node.save()
else:
	print "\nNo Group found!!"
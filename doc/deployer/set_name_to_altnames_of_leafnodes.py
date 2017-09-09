from gnowsys_ndf.ndf.models import *
group_id_str = raw_input("Enter Group_id: ")
group_obj = node_collection.one({'_id': ObjectId(group_id_str)})
if group_obj:
	all_leaf_node_ids = dig_nodes_field(parent_node=n, member_of=['Page'], only_leaf_nodes=True)
	all_leaf_node_cur = node_collection.find({'_id': {'$in': all_leaf_node_ids}})
	for each_node in all_leaf_node_cur:
		altnames_val = each_node.altnames 
		each_node.name = altnames_val # Display name --> Unique name
		each_node.altnames = each_node.name
else:
	print "\nNo Group found!!"
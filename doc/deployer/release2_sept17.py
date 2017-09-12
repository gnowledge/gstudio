from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import dig_nodes_field, create_gattribute

units_for_renaming_leaf_nodes = []
module_sort_order_ids = []

try:
    home_grp_id = node_collection.one({'_type': 'Group', 'name': 'home'})._id
    create_gattribute(home_grp_id, 'items_sort_list', module_sort_order_ids)
except Exception as module_sort_order_ids_err:
    pass
    print "\nError in module_sort_order_ids. ", module_sort_order_ids_err

units_cur = node_collection.find({'_type': 'Group', '_id': {'$in': units_for_renaming_leaf_nodes}})

for each_unit in units_cur:
    try:
        if each_unit:
            print "\nUnit: ", each_unit.name
            all_leaf_node_ids = dig_nodes_field(parent_node=each_unit, only_leaf_nodes=True)
            all_leaf_node_cur = node_collection.find({'_id': {'$in': all_leaf_node_ids}})
            print "\nLeaf nodes found: ", all_leaf_node_cur.count()
            for each_node in all_leaf_node_cur:
                name_val = each_node.name
                print "\n ", each_node.altnames , " --->", name_val
                each_node.altnames = name_val # Unique name --> Display name
                each_node.save()
        else:
            print "\nNo Group found!!"
    except Exception as units_for_renaming_leaf_nodes_err:
        pass
        print "\nError in units_for_renaming_leaf_nodes. ", units_for_renaming_leaf_nodes_err
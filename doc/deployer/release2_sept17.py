from gnowsys_ndf.ndf.models import Node, node_collection
from gnowsys_ndf.ndf.views.methods import dig_nodes_field, create_gattribute
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

units_for_renaming_leaf_nodes = [ObjectId('5944c6954975ac013e9ee760'),
 ObjectId('5943f3f94975ac013d36fa53'),
 ObjectId('5943ff594975ac013d3701fc'),
 ObjectId('5943fd564975ac013d36fdae'),
 ObjectId('59425be44975ac013cccb909'),
 ObjectId('5943d4a54975ac013f4ddce0'),
 ObjectId('59425c964975ac013cccba9d'),
 ObjectId('5942605d4975ac013cccbe52'),
 ObjectId('59425cc54975ac013cccbae4'),
 ObjectId('59425d1a4975ac013cccbb8b'),
 ObjectId('594260214975ac013d976c55'),
 ObjectId('59425de84975ac013bf0f46e'),
 ObjectId('59425e464975ac013cccbc4d'),
 ObjectId('59425fc64975ac013d976b32'),
 ObjectId('59425f864975ac013d976ac6'),
 ObjectId('59425ead4975ac013bf0f54b'),
 ObjectId('594260a54975ac013d976dc3')]

module_sort_order_ids = [u'59abb47c69602a0156036296', u'5945db6e2c4796014abd1784',\
 u'5945db2e2c4796014ddff67a', u'5945de532c4796014abd181a', u'5945de362c4796014ce12d7f',\
 u'5938ed2369602a014cb67195', u'5945ddca2c4796014ddff735', u'599c139269602a013fe31aa2',\
 u'59816df569602a015784baea', u'594b833869602a013f0cb6ce', u'594cfbea69602a014089845b', \
 u'597ebd7b69602a0154bb417e', u'5945daf42c4796014ce12d2d', u'59aff39869602a0155bfac16']


try:
    module_obj_list = []
    for each_id in module_sort_order_ids:
        try:
            each_node = Node.get_node_by_id(ObjectId(each_id))
            if each_node:
                module_obj_list.append(each_node)
        except Exception as modulde_not_found_err:
            print "\nError in module_not_found for each_id: ", each_id, "\nError: ", modulde_not_found_err
            pass
    print "\nTotal modules: ", len(module_obj_list)
    home_grp_id = node_collection.one({'_type': 'Group', 'name': 'home'})._id
    create_gattribute(home_grp_id, 'items_sort_list', module_obj_list)
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
                if name_val != each_node.altnames:
                    each_node.altnames = name_val # Unique name --> Display name
                    each_node.save()
                    try:
                        print "\n ", each_node.altnames , " --->", each_node.name
                    except Exception as e:
                        pass
        else:
            print "\nNo Group found!!"
    except Exception as units_for_renaming_leaf_nodes_err:
        pass
        print "\nError in units_for_renaming_leaf_nodes. ", units_for_renaming_leaf_nodes_err

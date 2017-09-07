import os
import json
from bson import json_util
from gnowsys_ndf.ndf.models import node_collection, TYPES_LIST
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_GROUPS_LIST
type_json = {"_type": None, "name": None, "source_id": None, "target_id": None }

def create_factory_schema_mapper(path):
    # dump_list = [type_json]
    schema_dump_path = os.path.join(path, 'factory_schema.json')
    
    all_factory_types = node_collection.find({
                                                '$or': [
                                                    {'_type': {'$in': TYPES_LIST }},
                                                    {
                                                        '_type': u'Group',
                                                        'name': {'$in': GSTUDIO_DEFAULT_GROUPS_LIST }
                                                    }
                                                ]
                                            })
    factory_json_list =  []
    for each_type in all_factory_types:
        each_type_json = type_json.copy()
        each_type_json['_type'] = each_type._type
        each_type_json['name'] = each_type.name
        each_type_json['source_id'] = each_type._id
        factory_json_list.append(each_type_json)

    with open(schema_dump_path, 'w+') as schema_file_out:
        schema_file_out.write(json_util.dumps(factory_json_list))


def update_factory_schema_mapper(path):
    SCHEMA_ID_MAP = {} # {ObjectId-on-source: ObjectId-on-target}
    schema_dump_path = os.path.join(path, 'factory_schema.json')
    if os.path.exists(schema_dump_path):
        with open(schema_dump_path, 'r') as schema_file_in:
            factory_json_list = json.loads(schema_file_in.read(), object_hook=json_util.object_hook)
            updated_factory_json_list = []
            for each_type in factory_json_list:
                type_node = node_collection.one({'_type': each_type['_type'], 'name':each_type['name']},{'_id':1})
                if type_node:
                    each_type['target_id'] = type_node._id
                    updated_factory_json_list.append(each_type)
                    if each_type['target_id'] != each_type['source_id']:
                        SCHEMA_ID_MAP[each_type['source_id']] = each_type['target_id']
        with open(schema_dump_path, 'w+') as schema_file_out:
            schema_file_out.write(json_util.dumps(updated_factory_json_list))
            schema_file_out.close()
        return SCHEMA_ID_MAP
    else:
        return SCHEMA_ID_MAP
        print "\n No factory_schema.json file found."

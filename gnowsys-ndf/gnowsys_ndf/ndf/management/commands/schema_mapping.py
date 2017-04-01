import os
from bson import json_util
from gnowsys_ndf.ndf.models import node_collection, TYPES_LIST
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_GROUPS
type_json = {"_type": None, "name": None, "source_id": None, "target_id": None }

def create_factory_schema_mapper(path):
    # dump_list = [type_json]
    schema_dump_path = os.path.join(path, 'factory_schema.json')
    
    all_factory_types = node_collection.find({
                                                '$or': [
                                                    {'_type': {'$in': TYPES_LIST }},
                                                    {
                                                        '_type': u'Group',
                                                        'name': {'$in': GSTUDIO_DEFAULT_GROUPS }
                                                    }
                                                ]
                                            })
    factory_json_list =  []
    for e in all_factory_types:
        each_type_json = type_json.copy()
        each_type_json['_type'] = e._type
        each_type_json['name'] = e.name
        each_type_json['source_id'] = e._id
        factory_json_list.append(each_type_json)

    with open(schema_dump_path, 'w+') as schema_file_out:
        schema_file_out.write(json_util.dumps(factory_json_list))
        #while reading
        # doc = json.loads(in_doc, object_hook=decoder)


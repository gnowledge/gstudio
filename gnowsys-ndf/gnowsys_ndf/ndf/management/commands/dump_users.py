import os
import json
from django.contrib.auth.models import User
from gnowsys_ndf.ndf.models import node_collection

user_json = {"user_id": None, "user_name": None, "user_author_id": None, "user_email": None }

def create_users_dump(path, user_id_list):
    dump_list = [user_json]
    schema_dump_path = os.path.join(path, 'users_dump.json')
    auth_cur = node_collection.find({'_type': 'Author',
                'created_by': {'$in': [1,2,3,4]}},
                {'name':1, 'email': 1, 'created_by': 1})

    user_json_list =  []
    for each_auth in auth_cur:
        each_user_json = user_json.copy()
        each_user_json['user_id'] = each_auth.created_by
        each_user_json['user_name'] = each_auth.name
        each_user_json['user_email'] = each_auth.email
        each_user_json['user_author_id'] = each_auth._id
        user_json_list.append(user_json)

    with open(schema_dump_path, 'w+') as schema_file_out:
        schema_file_out.write(json.dumps(user_json_list))


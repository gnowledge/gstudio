import os
import json
from django.contrib.auth.models import User
from gnowsys_ndf.ndf.models import node_collection

user_json = {"user_id": None, "user_name": None, "user_author_id": None, "user_email": None }
auth_gst = node_collection.one({'_type': u'GSystemType', 'name': u'Author'})
auth_gst_id = auth_gst._id

def create_users_dump(path, user_id_list):
    dump_list = [user_json]
    schema_dump_path = os.path.join(path, 'users_dump.json')
    auth_cur = node_collection.find({'_type': 'Author',
                'created_by': {'$in': user_id_list}},
                {'name':1, 'email': 1, 'created_by': 1})

    user_json_list =  []
    for each_auth in auth_cur:
        each_user_json = user_json.copy()
        each_user_json['user_id'] = each_auth.created_by
        each_user_json['user_name'] = each_auth.name
        each_user_json['user_email'] = each_auth.email
        each_user_json['user_author_id'] = str(each_auth._id)
        user_json_list.append(each_user_json)

    with open(schema_dump_path, 'w+') as schema_file_out:
        schema_file_out.write(json.dumps(user_json_list))

def load_users_dump(user_json_list):
    print "\nuser_json_list: ", user_json_list
    user_obj = None
    for each_user_record in user_json_list:
        try:
            user_obj = User.objects.get(pk=each_user_record["user_id"])
        except Exception as no_user:
            pass
        if user_obj:
            if user_obj.username == each_user_record["user_name"]:
                pass
            else:
                create_user_and_auth_obj(each_user_record)

def create_user_and_auth_obj(each_user_record_dict):
    user_obj = User.objects.create_user(
                username=each_user_record_dict["user_name"],
                email=each_user_record_dict["user_email"],
                password=each_user_record_dict["user_name"])
    user_id = user_obj.id
    
    auth = node_collection.collection.Author()
    auth['name'] = unicode(each_user_record_dict["user_name"])
    auth['email'] = unicode(each_user_record_dict["user_email"])
    auth['member_of'] = [auth_gst_id]
    auth['group_type'] = u"PUBLIC"
    auth['edit_policy'] = u"NON_EDITABLE"
    auth['created_by'] = user_id
    auth['modified_by'] = user_id
    auth['contributors'] = [user_id]
    auth['group_admin'] = [user_id]
    # auth['agency_type'] = "Student"
    auth['_id'] = ObjectId()
    auth.save(groupid=auth['_id'])

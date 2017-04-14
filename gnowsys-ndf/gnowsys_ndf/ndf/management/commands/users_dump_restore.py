import os
import json
import datetime
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from django.contrib.auth.models import User
from gnowsys_ndf.ndf.models import node_collection, GSystemType

user_json = {"user_id": None, "user_name": None, "user_author_id": None, "user_email": None }
gst_author_name, gst_author_id = GSystemType.get_gst_name_id('Author')

def create_users_dump(path, user_id_list):
    dump_list = [user_json]
    schema_dump_path = os.path.join(path, 'users_dump.json')
    auth_cur = node_collection.find({'_type': 'Author',
                'created_by': {'$in': user_id_list}},
                {'name':1, 'email': 1, 'created_by': 1})

    user_json_list =  []
    for each_auth in auth_cur:
        try:
            user_obj = User.objects.get(pk=each_auth.created_by)
        except Exception as no_user:
            pass
        if user_obj:
            each_user_json = user_json.copy()
            each_user_json['user_id'] = user_obj.id
            each_user_json['user_name'] = user_obj.username
            # for email
            user_email_val = user_obj.email
            if user_email_val == '':
                user_email_val = user_obj.username
            each_user_json['user_email'] = user_email_val
            each_user_json['user_author_id'] = str(each_auth._id)
            user_json_list.append(each_user_json)

    with open(schema_dump_path, 'w+') as schema_file_out:
        schema_file_out.write(json.dumps(user_json_list))

def load_users_dump(path, user_json_list):
    USER_ID_MAP = {} # {old-id: new-id}
    user_obj = None
    datetimestamp = datetime.datetime.now().isoformat()
    restore_users_log_file = "user_dump_restoration"+ "_" + str(datetimestamp) +".log"
    user_log_fout = open(os.path.join(path, restore_users_log_file), 'w+')
    user_restore_fout = open(os.path.join(path, "user_dump_restoration.json"), 'w+')
    user_log_fout.write(' -- User Objects Restoration Process Initiated. --')
    users_restorations = []
    for each_user_record in user_json_list:
        user_obj_restore_log = ''
        try:
            user_obj = User.objects.get(pk=each_user_record["user_id"])
        except Exception as no_user:
            pass

        if user_obj:
            user_obj_restore_log += '\nFound User obj with id: ' + \
                                str(each_user_record["user_id"])
            if user_obj.username == each_user_record["user_name"]:
                user_obj_restore_log += '\n\tUsername Check: Matched  ' + \
                                    str(each_user_record["user_name"])
                if user_obj.email:
                    if user_obj.email == each_user_record["user_email"]:
                        user_obj_restore_log += '\n\tUser-email Check: Matched  ' + \
                                            str(each_user_record["user_email"])
                        # ignore auth ObjectId passed in dump.
                        # Do not restore the auth-object.
                        pass
                    else:
                        user_obj_restore_log += '\n\tUser-email Check: Not Matched  ' + \
                                            str(each_user_record["user_email"])
                        # username matched but email not matching
                        # no idea what to do now!
                        pass
                elif "user_email" in each_user_record:
                    # update email of user_obj
                    user_obj.email = each_user_record["user_email"]
                    user_obj.save()
            else:
                user_obj_restore_log += '\n\tUsername Check: Not Matched  ' + \
                                    str(each_user_record["user_name"])
                try:
                    new_user_id, new_auth_id = create_user_and_auth_obj(each_user_record)
                    each_user_record["new_user_id"] = new_user_id
                    each_user_record["new_author_id"] = str(new_auth_id)
                    user_obj_restore_log += '\n\tCreateUser: New Id: ' + \
                                        str(each_user_record["new_user_id"]) + \
                                        "\t New Author Id: " +  \
                                        str(each_user_record["new_user_id"])
                    USER_ID_MAP[each_user_record['user_id']] = new_user_id
                except Exception as user_auth_creation_error:
                    each_user_record["new_user_id"] = "Failed"
                    each_user_record["new_author_id"] = "Failed"
                    user_obj_restore_log += '\n\tCreateUser Failed: ' + \
                                        str(user_auth_creation_error)

        else:
            user_obj_restore_log += '\nNot Found User obj with id : ' + \
                                str(each_user_record["user_id"])

            # user not found
            # print "\nuser_json_list: ", user_json_list
            try:
                new_user_id, new_auth_id = create_user_and_auth_obj(each_user_record)
                each_user_record["new_user_id"] = new_user_id
                each_user_record["new_author_id"] = str(new_auth_id)
                user_obj_restore_log += '\n\tCreateUser: New Id: ' + \
                                    str(each_user_record["new_user_id"]) + \
                                    "\t New Author Id: " +  \
                                    str(each_user_record["new_user_id"])
                USER_ID_MAP[each_user_record['user_id']] = new_user_id
            except Exception as user_auth_creation_error:
                each_user_record["new_user_id"] = "Failed"
                each_user_record["new_author_id"] = "Failed"

                user_obj_restore_log += '\n\tCreateUser Failed: ' + \
                                    str(user_auth_creation_error)

        users_restorations.append(each_user_record)
        user_log_fout.write(user_obj_restore_log)

    user_restore_fout.write(json.dumps(users_restorations))
    return USER_ID_MAP

def create_user_and_auth_obj(each_user_record_dict):
    user_obj = User.objects.create_user(
                username=each_user_record_dict["user_name"],
                email=each_user_record_dict["user_email"],
                password=each_user_record_dict["user_name"])
    user_id = user_obj.id

    auth = node_collection.collection.Author()
    auth['name'] = unicode(each_user_record_dict["user_name"])
    auth['email'] = unicode(each_user_record_dict["user_email"])
    auth['member_of'] = [gst_author_id]
    auth['group_type'] = u"PUBLIC"
    auth['edit_policy'] = u"NON_EDITABLE"
    auth['created_by'] = user_id
    auth['modified_by'] = user_id
    auth['contributors'] = [user_id]
    auth['group_admin'] = [user_id]
    auth['_id'] = ObjectId()
    auth.save(groupid=auth['_id'])
    return (user_id, auth._id)

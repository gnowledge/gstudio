import os

from gnowsys_ndf.ndf.models import *
# from gnowsys_ndf.ndf.views.methods import delete_node

# not_cc_auth = node_collection.find({'_type': u'Author', '$nor': [{'name': {'$regex': 'cc'}}, {'name': 'administrator'}] })
cc_auth = node_collection.find({'_type': u'Author', '$or': [{'name': {'$regex': 'cc'}}, {'name': 'administrator'}] }, timeout=False)


admin_auth_ids_list = [each_cc_auth._id for each_cc_auth in cc_auth]
hp = HistoryManager()

hpp_gst = node_collection.one({'_type': 'RelationType', 'name': 'has_profile_pic'})


hpp = triple_collection.find({'_type':'GRelation', 'relation_type.$id': hpp_gst._id, 'subject': {'$nin': admin_auth_ids_list}}, timeout=False)


print "\n Total GRelatons: ", hpp.count()

print "\n Starting to Delete GRelatons"
for each_hpp in hpp:

    json_file_path = hp.get_file_path(each_hpp)
    version_file_path = json_file_path + ',v'
    try:
        os.remove(version_file_path)
        print "\nDeleted RCS json version file : ", version_file_path
        os.remove(json_file_path)
        print "\nDeleted RCS json file : ", json_file_path
    except Exception, e:
        print "\nException occured while deleting RCS file for node '", each_hpp._id.__str__(), "' : ", e

    node_to_be_deleted = node_collection.one({'_id': ObjectId(each_hpp.right_subject)})

    if node_to_be_deleted:
        fh_original_id = node_to_be_deleted.if_file.original.id
        if node_collection.find({'_type': 'GSystem', 'if_file.original.id': ObjectId(fh_original_id) }).count() == 1:
            for each_file in ['original', 'mid', 'thumbnail']:
                fh_id = node_to_be_deleted.if_file[each_file]['id']
                fh_relurl = node_to_be_deleted.if_file[each_file]['relurl']
                if fh_id or fh_relurl:
                    Filehive.delete_file_from_filehive(fh_id, fh_relurl)

        # Finally delete the node
        node_to_be_deleted.delete()

    each_hpp.delete()

print "\n Successfully Finished Deleting GRelatons"



authp = node_collection.find({'_type': u'Author', '_id': {'$nin': admin_auth_ids_list} }, timeout=False)
print "\n Total Authors: ", authp.count()

print "\n Starting to Delete Authors"
for each_auth in authp:
    json_file_path = hp.get_file_path(each_auth)
    version_file_path = json_file_path + ',v'
    try:
        os.remove(version_file_path)
        print "\nDeleted RCS json version file : ", version_file_path
        os.remove(json_file_path)
        print "\nDeleted RCS json file : ", json_file_path
    except Exception, e:
        print "\nException occured while deleting RCS file for node '", each_auth._id.__str__(), "' : ", e

    each_auth.delete()
print "\n Successfully Finished Deleting Authors"

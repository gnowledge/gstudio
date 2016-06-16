import os
import time
import subprocess
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import *


node_collection_ids = set()
triple_collection_ids = set()
filehives_collection_ids = set()
filehives_media_urls = set()
build_rcs = set()
rcs_paths_found = set()
media_url_not_found = set()
media_url_found = set()
historyMgr = HistoryManager()
# /data/gstudio_data_restore
restore_rcs_data_path = os.path.join(GSTUDIO_DATA_ROOT, 'gstudio_data_restore')
restore_media_path = os.path.join(restore_rcs_data_path, 'media')

if not os.path.exists(restore_rcs_data_path):
    os.makedirs(restore_rcs_data_path)

if not os.path.exists(restore_media_path):
    os.makedirs(restore_media_path)

class Command(BaseCommand):
    def handle(self, *args, **options):
        print "Enter group id: "
        group_id = raw_input()
        group_node = node_collection.one({"_type":"Group","_id":ObjectId(group_id)}) 
        if group_node:
            print "\n Initializing Dump of : ", group_node.name
            nodes_falling_under_grp = node_collection.find({"group_set":ObjectId(group_node._id)})
            for each_node in nodes_falling_under_grp:
                node_collection_ids.add(each_node._id)  
                # if 'GSystem' in each_node.member_of_names_list:
                #     get_page_node_details(each_node)
                if 'File' in each_node.member_of_names_list:
                    get_file_node_details(each_node)

                if each_node.collection_set:
                    get_nested_ids(each_node,'collection_set')

                if each_node.prior_node:
                    get_nested_ids(each_node,'prior_node')

                if each_node.post_node:
                    get_nested_ids(each_node,'post_node')

                if each_node.attribute_set:
                    #fetch attribute_type
                    for each_attr in each_node.attribute_set:
                        if each_attr:
                            each_attr_name = each_attr.keys()[0]
                            if each_attr_name:
                                at_node = node_collection.one({"_type":"AttributeType","name":unicode(each_attr_name)})
                                if at_node:
                                    gattr_node = triple_collection.find({"_type": "GAttribute", "subject": each_node._id, "attribute_type.$id": at_node._id})
                                    if gattr_node:
                                        for each_gattr_node in gattr_node:
                                            triple_collection_ids.add(each_gattr_node._id)
                                            # Get ObjectIds in object_value fields
                                            if type(each_gattr_node.object_value) == list and all(isinstance(each_obj_value, ObjectId) for each_obj_value in each_gattr_node.object_value):
                                                node_collection_ids.extend(each_gattr_node.object_value)
                                            elif isinstance(each_gattr_node.object_value, ObjectId):
                                                node_collection_ids.add(each_gattr_node.object_value)

                if each_node.relation_set:
                    for each_rel in each_node.relation_set:
                        if each_rel:
                            each_rel_name = each_rel.keys()[0]
                            if each_rel_name:
                                rt_node = node_collection.one({"$or":
                                                      [ {"name":unicode(each_rel_name)},  {"inverse_name":unicode(each_rel_name)}],"_type":"RelationType"})
                                if rt_node:
                                    grel_node = triple_collection.find({"_type": "GRelation", "subject": each_node._id, "relation_type.$id": rt_node._id})
                                    if grel_node:   
                                        for each_grel_node in grel_node:
                                            triple_collection_ids.add(each_grel_node._id) 
                                            # Get ObjectIds in right_subject fields
                                            if type(each_grel_node.right_subject) == list and all(isinstance(each_obj_value, ObjectId) for each_obj_value in each_grel_node.right_subject):
                                                node_collection_ids.extend(each_grel_node.right_subject)
                                            elif isinstance(each_grel_node.right_subject, ObjectId):
                                                node_collection_ids.add(each_grel_node.right_subject)


            try:
                # rcs of Nodes collection
                print "*"*90
                print "\n--- Restoring Nodes RCS --- "
                print "*"*90
                dump_node_ids(node_collection_ids,'node_collection')

                # rcs of Triples collection
                print "*"*90
                print "\n--- Restoring Triples RCS --- "
                print "*"*90
                dump_node_ids(triple_collection_ids,'triple_collection')

                # rcs of Filehives collection
                print "*"*90
                print "\n--- Restoring Filehives RCS --- "
                print "*"*90
                dump_node_ids(filehives_collection_ids,'filehive_collection')



                # Copy media file to /data/media location
                print "*"*90
                print "\n--- Restoring Filehives Media --- "
                print "*"*90

                # for each_file_media_url in filehives_media_urls:   
                #     # import ipdb;ipdb.set_trace()
                #     fp = os.path.join(MEDIA_ROOT,each_file_media_url)
                #     if os.path.exists(fp):
                #         cp = "cp  -u " + fp + " " +" --parents " + restore_media_path + "/" 
                #         subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
                #         media_url_found.add(fp)
                #     else:
                #         media_url_not_found.add(fp)

            except Exception as dump_err:
                print '!'*60
                print '\nError found: ',str(dump_err)
                print '!'*60
                pass

            log_file_name = 'data_dump_of_' + str(group_id)+ '.log'
            if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
                os.makedirs(GSTUDIO_LOGS_DIR_PATH)

            log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
            # print log_file_path
            with open(log_file_path, 'a+') as log_file:
                log_file.write("######### Script ran on : " + time.strftime("%c") + " #########\n\n")

                log_file.write("\n*************************************************************")
                log_file.write("\n\nTotal Migrations Expected: "+ str(len(node_collection_ids) + len(triple_collection_ids) + len(filehives_collection_ids) + len(filehives_media_urls)))

                log_file.write("\n*************************************************************")
                log_file.write("\n\nNodes Migrations Expected: "+ str(len(node_collection_ids)))
                log_file.write("\n\nTriple Migrations Expected: "+ str(len(triple_collection_ids)))
                log_file.write("\n\nFilehives Migrations Expected: "+ str(len(filehives_collection_ids)))
                log_file.write("\n\nFile Media Migrations Expected: "+ str(len(filehives_media_urls)))

                log_file.write("\n*************************************************************")
                log_file.write("\n\nSuccessful Migrations: "+ str(len(rcs_paths_found)))
                log_file.write("\n\nUnsuccessful Migrations: "+ str(len(build_rcs)))

                log_file.write("\n*************************************************************")
                log_file.write("\n\nSuccessful Media Migrations: " + str(len(media_url_found)))
                log_file.write("\n\nUnsuccessful Media Migrations: " + str(len(media_url_not_found)))

                log_file.write("\n*************************************************************")
                log_file.write("\n\nDetails of RCS Paths Not Found: " + str(build_rcs))
                log_file.write("\n*************************************************************")
                log_file.write("\n\nDetails of Media Paths Not Found: " + str(media_url_not_found))


def get_file_node_details(node):
    '''
    Check if_file field and update filehives_collection_ids list
    'if_file': {
                    'mime_type': basestring,
                    'original': {'id': ObjectId, 'relurl': basestring},
                    'mid': {'id': ObjectId, 'relurl': basestring},
                    'thumbnail': {'id': ObjectId, 'relurl': basestring}
                },

    '''
    for each_field,each_value in node.items():
        if each_field =='if_file':
            filehives_collection_ids.add(each_value['original']['id'])
            filehives_collection_ids.add(each_value['mid']['id'])
            filehives_collection_ids.add(each_value['thumbnail']['id'])
            filehives_media_urls.add(each_value['original']['relurl'])
            filehives_media_urls.add(each_value['mid']['relurl'])
            filehives_media_urls.add(each_value['thumbnail']['relurl'])

        # if each_field == 'group_set':
        #     for each_grp_id in node.group_set:
        #         group_node = node_collection.find_one({"_id":ObjectId(each_grp_id)})
        #         if group_node and group_node._type != unicode('Author'):
        #             group_set.extend(group_node.group_set)
        # if each_field == 'author_set':
        #     user_list.extend(node.author_set)

def get_nested_ids(node,field_name):
    if node[field_name]:
        for each_id in node[field_name]:
            node_collection_ids.add(each_id)
            each_node = node_collection.one({"_id":ObjectId(each_id)})
            if each_node and each_node[field_name]:
                get_nested_ids(each_node, field_name)


def dump_node_ids(list_of_ids,collection_name):
    print "\n In dump_node_ids"
    print "\n collection_name -- ", collection_name
    for each_id_of_list in list_of_ids:
        if isinstance(each_id_of_list, ObjectId):
            each_node_by_id = None
            if collection_name == "node_collection":
                each_node_by_id = node_collection.find_one({"_id":ObjectId(each_id_of_list)})
            elif collection_name == "triple_collection":
                each_node_by_id = triple_collection.find_one({"_id":ObjectId(each_id_of_list)})
            elif collection_name == "filehive_collection":
                each_node_by_id = filehive_collection.find_one({"_id":ObjectId(each_id_of_list)})
            if each_node_by_id:
                path = historyMgr.get_file_path(each_node_by_id)
                path = path + ",v"
                
                if not os.path.exists(path):
                    each_node_by_id.save(validate=False)
                    path = historyMgr.get_file_path(each_node_by_id)
                    path = path + ",v"
                    build_rcs.add(path)
                cp = "cp  -vu " + path + " " +" --parents " + restore_rcs_data_path + "/" 
                subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
                rcs_paths_found.add(path)


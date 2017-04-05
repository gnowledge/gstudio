import os
import datetime
import subprocess
# from threading import Thread
# import multiprocessing
# import math
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.ndf.models import node_collection, triple_collection, filehive_collection, counter_collection
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.settings import GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIR_PATH, MEDIA_ROOT, GSTUDIO_INSTITUTE_ID
from schema_mapping import create_factory_schema_mapper
from dump_users import create_users_dump
from gnowsys_ndf.ndf.views.methods import get_group_name_id

# global variables declaration
GROUP_CONTRIBUTORS = []
DUMP_PATH = None
DATA_EXPORT_PATH = None
MEDIA_EXPORT_PATH = None
IS_FORK = False
IS_CLONE = False
RESTORE_USER_DATA = False
log_file = None
historyMgr = HistoryManager()

def create_log_file(dump_path):
    '''
        Creates log file in gstudio-logs/ with 
        the name of the dump folder
    '''
    dump_path = dump_path.split("/")[-1]
    log_file_name = 'group_dump_' + str(dump_path)+ '.log'
    if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
        os.makedirs(GSTUDIO_LOGS_DIR_PATH)

    log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
    # print log_file_path
    global log_file
    log_file = open(log_file_path, 'w+')
    log_file.write("\n######### Script ran on : " + str(datetime.datetime.now()) + " #########\n\n")
    return log_file_path

def setup_dump_path(group_name):
    '''
        Creates factory_schema.json which will hold basic info
        like ObjectId, name, type of TYPES_LIST and GSTUDIO_DEFAULT_GROUPS
    '''
    global DUMP_PATH
    global DATA_EXPORT_PATH
    global MEDIA_EXPORT_PATH
    datetimestamp = datetime.datetime.now().isoformat()
    DUMP_PATH = os.path.join(GSTUDIO_DATA_ROOT, 'data_export', group_name + "_" + str(datetimestamp))
    DATA_EXPORT_PATH = os.path.join(DUMP_PATH, 'dump')
    MEDIA_EXPORT_PATH = os.path.join(DATA_EXPORT_PATH, 'media_files')
    if not os.path.exists(DATA_EXPORT_PATH):
        os.makedirs(DATA_EXPORT_PATH)
    if not os.path.exists(MEDIA_EXPORT_PATH):
        os.makedirs(MEDIA_EXPORT_PATH)
    return DATA_EXPORT_PATH

def create_configs_file(group_id):
    global IS_FORK
    global IS_CLONE
    global RESTORE_USER_DATA
    global DUMP_PATH
    configs_file_path = os.path.join(DUMP_PATH, "migration_configs.py")
    with open(configs_file_path, 'w+') as configs_file_out:
        configs_file_out.write("\nFORK=" + str(IS_FORK))
        configs_file_out.write("\nCLONE=" + str(IS_CLONE))
        configs_file_out.write("\nRESTORE_USER_DATA=" + str(RESTORE_USER_DATA))
        configs_file_out.write("\nGSTUDIO_INSTITUTE_ID='" + str(GSTUDIO_INSTITUTE_ID) + "'")
        configs_file_out.write("\nGROUP_ID='" + str(group_id) + "'")
    return configs_file_path

def write_md5_of_dump(group_dump_path, configs_file_path):
    global DUMP_PATH
    from checksumdir import dirhash
    md5hash = dirhash(group_dump_path, 'md5')
    with open(configs_file_path, 'a+') as configs_file_out:
        configs_file_out.write("\nMD5='" + str(md5hash) + "'")

def get_triple_data(node_id):
    '''
    Gets all data stored in triples for this node.
    Fetches GAttrtibutes as wells as GRelations.
    '''
    triple_query = {"_type": {'$in': ["GAttribute", "GRelation"]}, "subject": node_id}

    node_gattr_grel_cur = triple_collection.find(triple_query)
    fetch_value = None
    if node_gattr_grel_cur:

        for each_triple_node in node_gattr_grel_cur:
            dump_node(node=each_triple_node,
                collection_name=triple_collection)
            # Get ObjectIds in object_value fields
            if each_triple_node._type is "GAttribute":
                fetch_value = "object_value"
            elif each_triple_node._type is "GRelation":
                fetch_value = "right_subject"
            if fetch_value:
                if type(each_triple_node[fetch_value]) == list and all(isinstance(each_obj_value, ObjectId) for each_obj_value in each_triple_node[fetch_value]):
                    dump_node(node_id_list=each_triple_node[fetch_value],
                        collection_name=node_collection)
                elif isinstance(each_triple_node[fetch_value], ObjectId):
                    dump_node(node_id=each_triple_node[fetch_value],
                            collection_name=node_collection)


class Command(BaseCommand):
    def handle(self, *args, **options):
        group_name_or_id = raw_input("\n\tPlease enter Name or ObjectID of the Group: ")
        group_node   = get_group_name_id(group_name_or_id.strip(), get_obj=True)

        if group_node:
            print "\tRequest received for Export of : ", group_node.name , ' | ObjectId: ', group_node._id
            fork_clone_opt = "\n\tExport Options:"
            fork_clone_opt += "\n\t\t 1. Fork (What is Fork?"
            fork_clone_opt += " Restore will create instances with NEW Ids)"
            fork_clone_opt += "\n\t\t 2. Clone (What is Clone?"
            fork_clone_opt += " Restore will create instances with OLD Ids)"
            fork_clone_opt += "\n\tEnter options 1 or 2 or any other key to cancel: \t"

            fork_clone_confirm = raw_input(fork_clone_opt)
            global IS_FORK
            global IS_CLONE
            global RESTORE_USER_DATA
            
            if fork_clone_confirm == '1':
                print "\n\t!!! Chosen FORK option !!!"
                IS_FORK = True
                IS_CLONE = False
            elif fork_clone_confirm == '2':
                print "\n\t!!! Chosen CLONE option !!!"
                IS_FORK = False
                IS_CLONE = True
            else:
                call_exit()
            user_data_dump = raw_input("\n\tDo you want to include Users in this export ? Enter y/n:\t ")
            if user_data_dump == 'y' or user_data_dump == 'Y':
                RESTORE_USER_DATA = True
            else:
                RESTORE_USER_DATA = False

            nodes_falling_under_grp = node_collection.find({"group_set":ObjectId(group_node._id)})
            print "\n\tTotal objects found: ", nodes_falling_under_grp.count()
            confirm_export = raw_input("\n\tDo you want to continue? Enter y/n:\t ")
            if confirm_export is 'y' or confirm_export is 'Y':
                print "START : ", str(datetime.datetime.now())
                group_dump_path = setup_dump_path(group_node.name)
                create_factory_schema_mapper(group_dump_path)
                configs_file_path = create_configs_file(group_node._id)
                log_file_path = create_log_file(group_dump_path)

                print "*"*70
                # print "\n Export will be found at: ", DATA_EXPORT_PATH
                print "\n Export will be found at: ", DUMP_PATH
                print "\n Log will be found at: ", log_file_path

                print "\n This will take few minutes. Please be patient.\n"
                print "*"*70

                call_group_export(group_node, nodes_falling_under_grp)
                get_counter_ids(group_node._id)
                # import ipdb; ipdb.set_trace()
                if RESTORE_USER_DATA:
                    print "\n Total GROUP_CONTRIBUTORS: ", len(GROUP_CONTRIBUTORS)
                    create_users_dump(group_dump_path, GROUP_CONTRIBUTORS)

                write_md5_of_dump(group_dump_path, configs_file_path)
                global log_file
                print "*"*70
                print "\n Export will be found at: ", DUMP_PATH
                print "\n Log will be found at: ", log_file_path
                print "*"*70


                log_file.write("\n*************************************************************")
                log_file.write("\n######### Script Completed at : " + str(datetime.datetime.now()) + " #########\n\n")
                print "END : ", str(datetime.datetime.now())
            else:
                call_exit()
        else:
            print "\n Node not found with provided Name or ObjectID"
            call_exit()



def call_exit():
    print "\n Exiting..."
    os._exit(0)

def worker_export(nodes_cur):
    for each_node in nodes_cur:
        print ".",
        dump_node(node=each_node,collection_name=node_collection)
        # node_collection_ids.add(each_node._id)
        if 'File' in each_node.member_of_names_list:
            get_file_node_details(each_node)

        if each_node.collection_set:
            get_nested_ids(each_node,'collection_set')

        if each_node.prior_node:
            get_nested_ids(each_node,'prior_node')

        if each_node.post_node:
            get_nested_ids(each_node,'post_node')

        #fetch triple_data
        get_triple_data(each_node._id)

def call_group_export(group_node, nodes_cur, num_of_processes=5):
    '''
        Introducing multiprocessing to use cores available on the system to 
        take dump of nodes of the entire group.
    '''
    worker_export(nodes_cur)
    # nodes_cur = list(nodes_cur)
    # print "\nlen(nodes_cur): ", len(nodes_cur)
    # Include Group Object.
    # nodes_cur.append(group_node)
    # Each process will get 'chunksize' student_cur and a queue to put his out
    # dict into
    # out_q = multiprocessing.Queue()
    # chunksize = int(math.ceil(len(nodes_cur) / float(num_of_processes)))
    # procs = []
    # print "\n chunk: ", chunksize

    # for i in range(num_of_processes):
    #     list_of_nodes = nodes_cur[chunksize * i:chunksize * (i + 1)]
    #     print "\nlist_of_nodes", len(list_of_nodes)
    #     p = Thread(
    #         target=worker,
    #         args=(list_of_nodes)
    #     )
    #     p.start()

    # Collect all results into a single result list. We know how many lists
    # with results to expect.
    # resultlist = []
    # for i in range(num_of_processes):
    #     resultlist.extend(out_q.get())

    # Wait for all worker processes to finish
    # for p in procs:
    #     p.join()

    # return resultlist


def build_rcs(node, collection_name):
    '''
    Updates the rcs json with the current node's strcuture that 
    might have missed due to update queries.
    Runs a save() method on the node and calls copy_rcs()
    '''
    # import ipdb; ipdb.set_trace()
    if node:
        global log_file
        global GROUP_CONTRIBUTORS
        try:
            if collection_name is triple_collection:
                if 'attribute_type' in node:
                    triple_node_RT_AT = node_collection.one({'_id': node.attribute_type})
                elif 'relation_type' in node:
                    triple_node_RT_AT = node_collection.one({'_id': node.relation_type})
                node.save(triple_node=triple_node_RT_AT, triple_id=triple_node_RT_AT._id)
            else:
                node.save()
                try:
                    global RESTORE_USER_DATA
                    if RESTORE_USER_DATA:
                        print "\n NC: ", len(node.contributors)
                        if "contributors" in node:
                            GROUP_CONTRIBUTORS.extend(node.contributors)
                except Exception as no_contributors_err:
                    pass
            log_file.write("\n RCS Built for " + str(node._id) )
            copy_rcs(node)
        except Exception as buildRCSError:
            error_log = "\n !!! Error found while Building RCS ."
            error_log += "\nError: " + str(buildRCSError)
            log_file.write(error_log)
            print error_log
            pass

def copy_rcs(node):
    '''
    Actual copying of RCS files from /data/rcs-repo/ to export_path/rcs-repo
     of the nodes called from dump_node() and build_rcs()
    '''
    if node:
        global log_file
        try:
            # To update RCS
            path = historyMgr.get_file_path(node)
            path = path + ",v"

            if not os.path.exists(path):
                path = historyMgr.get_file_path(node)
                path = path + ",v"

            cp = "cp  -vu " + path + " " +" --parents " + DATA_EXPORT_PATH + "/"
            subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)

            log_file.write("\n RCS Copied " + str(path) )

        except Exception as copyRCSError:
            error_log = "\n !!! Error found while Copying RCS ."
            error_log += "\nError: " + str(copyRCSError)
            log_file.write(error_log)
            print error_log
            pass

def dump_node(collection_name=node_collection, node=None, node_id=None, node_id_list=None):
    '''
    Receives all nodes pertaining to exporting group belonging to all existing collections.
    Calls build_rcs.
    '''
    try:
        global log_file
        log_file.write("\n dump_node invoked for: " + str(collection_name))
        if node:
            log_file.write("\tNode: " + str(node))
            build_rcs(node, collection_name)
            log_file.write("\n dump node finished for:  " + str(node._id) )
        elif node_id:
            log_file.write("\tNode_id : " + str(node_id))
            node = collection_name.one({'_id': ObjectId(node_id)})
            build_rcs(node, collection_name)
            log_file.write("\n dump node finished for:  " + str(node._id) )
        elif node_id_list:
            node_cur = collection_name.one({'_id': {'$in': node_id_list}})
            log_file.write("\tNode_id_list : " + str(node_id_list))
            for each_node in nodes_cur:
                build_rcs(node, collection_name)
                log_file.write("\n dump node finished for:  " + str(node._id) )

    except Exception as dump_err:
        error_log = "\n !!! Error found while taking dump in dump_node() ."
        error_log += "\nError: " + str(dump_err)
        log_file.write(error_log)
        print error_log
        pass

def dump_media_data(media_path):
    # Copy media file to /data/media location
    # print MEDIA_EXPORT_PATH
    global log_file
    log_file.write("\n--- Media Copying in process --- "+ str(media_path))
    try:
        fp = os.path.join(MEDIA_ROOT,media_path)
        if os.path.exists(fp):
            cp = "cp  -u " + fp + " " +" --parents " + MEDIA_EXPORT_PATH + "/"
            subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
            log_file.write("\n Media Copied:  " + str(fp) )

        else:
            log_file.write("\n Media NOT Copied:  " + str(fp) )
    except Exception as dumpMediaError:
        error_log = "\n !!! Error found while taking dump of Media.\n" +  str(media_path)
        error_log += "\nError: " + str(dumpMediaError)
        log_file.write(error_log)
        print error_log
        pass

def get_file_node_details(node):
    '''
    Check if_file field and take its dump
    'if_file': {
                    'mime_type': basestring,
                    'original': {'id': ObjectId, 'relurl': basestring},
                    'mid': {'id': ObjectId, 'relurl': basestring},
                    'thumbnail': {'id': ObjectId, 'relurl': basestring}
                },

    '''
    print "\n dumping fh -- "
    dump_node(node_id=node.if_file['original']['id'], collection_name=filehive_collection)
    dump_node(node_id=node.if_file['mid']['id'], collection_name=filehive_collection)
    dump_node(node_id=node.if_file['thumbnail']['id'], collection_name=filehive_collection)
    dump_media_data(node.if_file['original']['relurl'])
    dump_media_data(node.if_file['mid']['relurl'])
    dump_media_data(node.if_file['thumbnail']['relurl'])
    # if each_field == 'group_set':
    #     for each_grp_id in node.group_set:
    #         group_node = node_collection.find_one({"_id":ObjectId(each_grp_id)})
    #         if group_node and group_node._type != unicode('Author'):
    #             group_set.extend(group_node.group_set)
    # if each_field == 'author_set':
    #     user_list.extend(node.author_set)

def get_nested_ids(node,field_name):
    '''
        Recursive function to fetch Objectids from a 
        particular field of passed node.
        field_name can be : collection_set, post_node, prior_node
    '''
    if node[field_name]:
        for each_id in node[field_name]:
            each_node = node_collection.one({"_id":ObjectId(each_id)})
            dump_node(node=each_node, collection_name=node_collection)
            if each_node and each_node[field_name]:
                get_nested_ids(each_node, field_name)

def get_counter_ids(group_id):
    '''
    Fetch all the Counter instances of the exporting Group
    '''
    counter_collection_cur = counter_collection.find({'group_id':ObjectId(group_id)})
    if counter_collection_cur :
        for each_obj in counter_collection_cur :
            dump_node(node=each_obj,collection_name=counter_collection)

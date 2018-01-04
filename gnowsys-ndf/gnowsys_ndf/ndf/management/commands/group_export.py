import os
import datetime
import subprocess
import re
# from threading import Thread
# import multiprocessing
# import math
from bs4 import BeautifulSoup

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand, CommandError
from schema_mapping import create_factory_schema_mapper
from users_dump_restore import create_users_dump
from export_logic import dump_node, create_log_file, get_counter_ids, write_md5_of_dump
from gnowsys_ndf.ndf.models import node_collection, triple_collection, filehive_collection, counter_collection
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.settings import GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIR_PATH, MEDIA_ROOT, GSTUDIO_INSTITUTE_ID
from gnowsys_ndf.ndf.views.methods import get_group_name_id
from gnowsys_ndf.ndf.templatetags.simple_filters import get_latest_git_hash, get_active_branch_name

# global variables declaration
GROUP_CONTRIBUTORS = []
DUMP_PATH = None
TOP_PATH = os.path.join(GSTUDIO_DATA_ROOT, 'data_export')
GROUP_ID = None
DATA_EXPORT_PATH = None
MEDIA_EXPORT_PATH = None
RESTORE_USER_DATA = False
SCHEMA_MAP_PATH = None
log_file = None
log_file_path = None
historyMgr = HistoryManager()
DUMP_NODES_LIST = []
DUMPED_NODE_IDS = set()
ROOT_DUMP_NODE_ID = None
ROOT_DUMP_NODE_NAME = None
MULTI_DUMP = False

def setup_dump_path(node_name):
    '''
        Creates factory_schema.json which will hold basic info
        like ObjectId, name, type of TYPES_LIST and GSTUDIO_DEFAULT_GROUPS
    '''
    global DUMP_PATH
    global TOP_PATH
    global DATA_EXPORT_PATH
    global MEDIA_EXPORT_PATH
    # datetimestamp = datetime.datetime.now().isoformat()
    datetimestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    DUMP_PATH = os.path.join(TOP_PATH, node_name + "_" + str(datetimestamp))
    DATA_EXPORT_PATH = os.path.join(DUMP_PATH, 'dump')
    MEDIA_EXPORT_PATH = os.path.join(DATA_EXPORT_PATH, 'media_files')
    if not os.path.exists(DATA_EXPORT_PATH):
        os.makedirs(DATA_EXPORT_PATH)
    if not os.path.exists(MEDIA_EXPORT_PATH):
        os.makedirs(MEDIA_EXPORT_PATH)
    return DATA_EXPORT_PATH

def create_configs_file(group_id):
    global RESTORE_USER_DATA
    global DUMP_PATH
    configs_file_path = os.path.join(DUMP_PATH, "migration_configs.py")
    with open(configs_file_path, 'w+') as configs_file_out:
        configs_file_out.write("\nRESTORE_USER_DATA=" + str(RESTORE_USER_DATA))
        configs_file_out.write("\nGSTUDIO_INSTITUTE_ID='" + str(GSTUDIO_INSTITUTE_ID) + "'")
        configs_file_out.write("\nGROUP_ID='" + str(group_id) + "'")
        configs_file_out.write("\nROOT_DUMP_NODE_ID='" + str(ROOT_DUMP_NODE_ID) + "'")
        configs_file_out.write("\nROOT_DUMP_NODE_NAME='" + str(ROOT_DUMP_NODE_NAME) + "'")
        configs_file_out.write("\nMULTI_DUMP='" + str(MULTI_DUMP) + "'")
        configs_file_out.write("\nGIT_COMMIT_HASH='" + str(get_latest_git_hash()) + "'")
        configs_file_out.write("\nGIT_BRANCH_NAME='" + str(get_active_branch_name()) + "'")
        configs_file_out.write('\nSYSTEM_DETAILS="' + str(os.uname()) + '"')
    return configs_file_path

def core_export(group_node):
    if group_node:
        print "\tRequest received for Export of : ", group_node.name , ' | ObjectId: ', group_node._id
        global RESTORE_USER_DATA
        user_data_dump = raw_input("\n\tDo you want to include Users in this export ? Enter y/Y to continue:\t ")
        if user_data_dump in ['y', 'Y']:
            RESTORE_USER_DATA = True
        else:
            RESTORE_USER_DATA = False

        nodes_falling_under_grp = node_collection.find({
                "group_set":ObjectId(group_node._id),
                "_type": {'$nin': ['Group', 'Author']}})
        print "\n\tTotal objects found: ", nodes_falling_under_grp.count()
        confirm_export = raw_input("\n\tEnter y/Y to Continue or any other key to Abort:\t ")
        if confirm_export in ['y', 'Y']:

            group_dump_path = setup_dump_path(slugify(group_node.name))

            global GROUP_ID
            GROUP_ID = group_node._id
            call_group_export(group_node, nodes_falling_under_grp)
            get_counter_ids(group_id=group_node._id)
            # import ipdb; ipdb.set_trace()
            global GROUP_CONTRIBUTORS
            if RESTORE_USER_DATA:
                GROUP_CONTRIBUTORS = list(set(GROUP_CONTRIBUTORS))
                create_users_dump(group_dump_path, GROUP_CONTRIBUTORS)

            configs_file_path = create_configs_file(group_node._id)
            write_md5_of_dump(group_dump_path, configs_file_path)
            global log_file

            log_file.write("\n*************************************************************")
            log_file.write("\n######### Script Completed at : " + str(datetime.datetime.now()) + " #########\n\n")
        else:
            call_exit()
    else:
        print "\n Node not found with provided Name or ObjectID"
        call_exit()


def call_exit():
    print "\n Exiting..."
    os._exit(0)

def get_nested_ids(node,field_name):
    '''
        Recursive function to fetch Objectids from a 
        particular field of passed node.
        field_name can be : collection_set, post_node, prior_node
    '''
    global GLOBAL_DICT
    if node[field_name]:
        for each_id in node[field_name]:
            each_node = node_collection.one({"_id":ObjectId(each_id), '_type': {'$nin': ['Group', 'Author']}})
            if each_node and (node._id != each_node._id):
                dump_node(node=each_node, collection_name=node_collection, variables_dict=GLOBAL_DICT)
                if each_node and each_node[field_name]:
                    get_nested_ids(each_node, field_name)

def worker_export(nodes_cur):
    global GLOBAL_DICT
    for each_node in nodes_cur:
        print ".",
        dump_node(node=each_node,collection_name=node_collection,variables_dict=GLOBAL_DICT)
        # node_collection_ids.add(each_node._id)

        if each_node.collection_set:
            get_nested_ids(each_node,'collection_set')

        if each_node.prior_node:
            get_nested_ids(each_node,'prior_node')

        if each_node.post_node:
            get_nested_ids(each_node,'post_node')

def update_globals():

    global GLOBAL_DICT
    global GROUP_CONTRIBUTORS
    global DUMP_PATH
    global TOP_PATH
    global GROUP_ID
    global DATA_EXPORT_PATH
    global MEDIA_EXPORT_PATH
    global RESTORE_USER_DATA
    global SCHEMA_MAP_PATH
    global log_file_path
    global DUMP_NODES_LIST
    global DUMPED_NODE_IDS
    global ROOT_DUMP_NODE_ID
    global ROOT_DUMP_NODE_NAME
    global MULTI_DUMP

    GLOBAL_DICT = {
                    "GROUP_CONTRIBUTORS": GROUP_CONTRIBUTORS,
                    "DUMP_PATH": DUMP_PATH,
                    "TOP_PATH": TOP_PATH,
                    "GROUP_ID": GROUP_ID,
                    "DATA_EXPORT_PATH": DATA_EXPORT_PATH,
                    "MEDIA_EXPORT_PATH": MEDIA_EXPORT_PATH,
                    "RESTORE_USER_DATA": RESTORE_USER_DATA,
                    "SCHEMA_MAP_PATH": SCHEMA_MAP_PATH,
                    "log_file_path": log_file_path,
                    "DUMP_NODES_LIST": DUMP_NODES_LIST,
                    "DUMPED_NODE_IDS": DUMPED_NODE_IDS,
                    "ROOT_DUMP_NODE_ID": ROOT_DUMP_NODE_ID,
                    "ROOT_DUMP_NODE_NAME": ROOT_DUMP_NODE_NAME,
                    "MULTI_DUMP": MULTI_DUMP
                    }


def call_group_export(group_node, nodes_cur, num_of_processes=5):
    '''
        Introducing multiprocessing to use cores available on the system to 
        take dump of nodes of the entire group.
    '''
    global GLOBAL_DICT
    global log_file
    update_globals()

    dump_node(node=group_node,collection_name=node_collection, variables_dict=GLOBAL_DICT)
    if group_node.collection_set:
        get_nested_ids(group_node,'collection_set')
    nodes_cur = list(nodes_cur)
    worker_export(nodes_cur)
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



class Command(BaseCommand):
    def handle(self, *args, **options):
        global SCHEMA_MAP_PATH
        global DUMP_PATH
        global ROOT_DUMP_NODE_ID
        global ROOT_DUMP_NODE_NAME
        global MULTI_DUMP
        global GLOBAL_DICT
        global log_file
        global log_file_path
        global TOP_PATH
        global DUMP_NODES_LIST
        input_name_or_id = raw_input("\n\tPlease enter ObjectID of the Group: ")
        dump_node_obj = node_collection.one({'_id': ObjectId(input_name_or_id)})
        group_node = None

        if dump_node_obj:
            datetimestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            log_file_name = 'group_dump_' + slugify(dump_node_obj.name) + "_" + str(datetimestamp)
            log_file_path = create_log_file(log_file_name)
            log_file = open(log_file_path, 'w+')
            log_file.write("\n######### Script ran on : " + str(datetimestamp) + " #########\n\n")

            ROOT_DUMP_NODE_ID = dump_node_obj._id
            ROOT_DUMP_NODE_NAME = dump_node_obj.name

            if dump_node_obj._type == 'Group':
                core_export(dump_node_obj)
                SCHEMA_MAP_PATH = DUMP_PATH
                create_factory_schema_mapper(SCHEMA_MAP_PATH)
            else:
                datetimestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
                TOP_PATH = os.path.join(GSTUDIO_DATA_ROOT, 'data_export', slugify(dump_node_obj.name) + "_"+ str(datetimestamp))
                SCHEMA_MAP_PATH = TOP_PATH
                UNIT_NAMES = []
                print "\n********REQUEST DUMP NODE IS NOT GROUP.*********\n"
                confirm_non_grp_exp = raw_input("\n\tDo you want to continue? Enter y/n:\t ")
                if confirm_non_grp_exp in ['y', 'Y']:
                    MULTI_DUMP = True
                    # Based on the request dump_node_obj member_of and type fields, query for the field contents.
                    # if "module" in dump_node_obj.member_of_names_list:
                    module_units_cur = node_collection.find({
                                        '_id': {'$in': dump_node_obj.collection_set},
                                        '_type': 'Group'})
                    if module_units_cur.count():
                        print "\nFollowing are the Groups part of request dump. \n\tEnter y/Y to select or any other key to skip the group:\t "
                        for each_unit in module_units_cur:
                            select_grp = raw_input(each_unit.name + "("+ each_unit.member_of_names_list[0]+  ") :\t")
                            if select_grp in ['y', 'Y']:
                                DUMP_NODES_LIST.append(each_unit)
                                UNIT_NAMES.append(each_unit.name)
                        dump_grp_list_confirm = raw_input("\n\n\t\tFollowing are the selected Units to be dumped:\n\t\t\t "+ ','.join(UNIT_NAMES)+"\n\n\t\tEnter y/Y to continue:\t ")
                        if dump_grp_list_confirm in ['y', 'Y']:
                            for each_unit in DUMP_NODES_LIST:
                                core_export(each_unit)
                        else:
                            call_exit()
                        dump_node(node=dump_node_obj,collection_name=node_collection, variables_dict=GLOBAL_DICT)
                        create_factory_schema_mapper(SCHEMA_MAP_PATH)
            print "*"*70
            print "\n START : ", str(datetimestamp)
            print "\n Log will be found at: ", log_file_path
            print "\n Dump will be found at: ", SCHEMA_MAP_PATH
            print "\n END : ", str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            print "*"*70
            log_file.close()
            call_exit()
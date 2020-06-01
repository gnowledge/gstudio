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
from export_logic import dump_node
from gnowsys_ndf.ndf.models import node_collection, triple_collection, filehive_collection, counter_collection
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.settings import GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIR_PATH, MEDIA_ROOT, GSTUDIO_INSTITUTE_ID
from gnowsys_ndf.ndf.views.methods import get_group_name_id
from gnowsys_ndf.ndf.templatetags.simple_filters import get_latest_git_hash, get_active_branch_name

# global variables declaration
GROUP_CONTRIBUTORS = []
DUMP_PATH = None
TOP_PATH = os.path.join(GSTUDIO_DATA_ROOT, 'data_export')
node_id = None
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

def create_log_file(dump_node_id):
    '''
        Creates log file in gstudio-logs/ with 
        the name of the dump folder
    '''
    log_file_name = 'node_export_' + str(dump_node_id)+ '.log'
    if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
        os.makedirs(GSTUDIO_LOGS_DIR_PATH)
    global log_file_path
    log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
    # print log_file_path
    global log_file
    log_file = open(log_file_path, 'w+')
    log_file.write("\n######### Script ran on : " + str(datetime.datetime.now()) + " #########\n\n")
    return log_file_path

def setup_dump_path(node_id):
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
    DUMP_PATH = TOP_PATH
    DATA_EXPORT_PATH = os.path.join(DUMP_PATH, 'dump')
    MEDIA_EXPORT_PATH = os.path.join(DATA_EXPORT_PATH, 'media_files')
    if not os.path.exists(DATA_EXPORT_PATH):
        os.makedirs(DATA_EXPORT_PATH)
    if not os.path.exists(MEDIA_EXPORT_PATH):
        os.makedirs(MEDIA_EXPORT_PATH)
    return DATA_EXPORT_PATH

def create_configs_file(node_id):
    global RESTORE_USER_DATA
    global DUMP_PATH
    configs_file_path = os.path.join(DUMP_PATH, "migration_configs.py")
    with open(configs_file_path, 'w+') as configs_file_out:
        configs_file_out.write("\nRESTORE_USER_DATA=" + str(RESTORE_USER_DATA))
        configs_file_out.write("\nGSTUDIO_INSTITUTE_ID='" + str(GSTUDIO_INSTITUTE_ID) + "'")
        configs_file_out.write("\nNODE_ID='" + str(node_id) + "'")
        configs_file_out.write("\nROOT_DUMP_NODE_NAME='" + str(ROOT_DUMP_NODE_NAME) + "'")
        configs_file_out.write("\nGIT_COMMIT_HASH='" + str(get_latest_git_hash()) + "'")
        configs_file_out.write("\nGIT_BRANCH_NAME='" + str(get_active_branch_name()) + "'")
        configs_file_out.write('\nSYSTEM_DETAILS="' + str(os.uname()) + '"')
    return configs_file_path

def write_md5_of_dump(group_dump_path, configs_file_path):
    global DUMP_PATH
    from checksumdir import dirhash
    md5hash = dirhash(group_dump_path, 'md5')
    with open(configs_file_path, 'a+') as configs_file_out:
        configs_file_out.write("\nMD5='" + str(md5hash) + "'")



def call_exit():
    print "\n Exiting..."
    os._exit(0)

def update_globals():
    global GLOBAL_DICT
    global GROUP_CONTRIBUTORS
    global DUMP_PATH
    global TOP_PATH
    global node_id
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
                    "node_id": node_id,
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


class Command(BaseCommand):
    def handle(self, *args, **options):
        global SCHEMA_MAP_PATH
        global DUMP_PATH
        global ROOT_DUMP_NODE_ID
        global ROOT_DUMP_NODE_NAME
        global MULTI_DUMP
        global GLOBAL_DICT
        input_name_or_id = None
        if args:
            input_name_or_id = args[0]
        else:
            input_name_or_id = raw_input("\n\tPlease enter ObjectID of the Node: ")

        dump_node_obj = node_collection.one({'_id': ObjectId(input_name_or_id), '_type': 'GSystem'})

        if dump_node_obj:
            log_file_path = create_log_file(dump_node_obj._id)
            ROOT_DUMP_NODE_ID = dump_node_obj._id
            ROOT_DUMP_NODE_NAME = dump_node_obj.name

            global TOP_PATH
            global DUMP_NODES_LIST
            datetimestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            TOP_PATH = os.path.join(GSTUDIO_DATA_ROOT, 'data_export', str(dump_node_obj._id) + "_"+ str(datetimestamp))
            SCHEMA_MAP_PATH = TOP_PATH
            print "\tRequest received for Export of : \n\t\tObjectId: ", dump_node_obj._id
            try:
                print "\t\tName : ", dump_node_obj.name
            except Exception as e:
                pass
            global RESTORE_USER_DATA
            user_data_dump = raw_input("\n\tDo you want to include Users in this export ? Enter y/Y to continue:\t ")
            if user_data_dump in ['y', 'Y']:
                RESTORE_USER_DATA = True
            else:
                RESTORE_USER_DATA = False

            print "START : ", str(datetime.datetime.now())
            group_dump_path = setup_dump_path(slugify(dump_node_obj._id))

            global node_id
            node_id = dump_node_obj._id
            if RESTORE_USER_DATA:
                create_users_dump(group_dump_path, dump_node_obj.contributors)

            configs_file_path = create_configs_file(dump_node_obj._id)
            global log_file
            update_globals()
            dump_node(node=dump_node_obj,collection_name=node_collection, variables_dict=GLOBAL_DICT)
            create_factory_schema_mapper(SCHEMA_MAP_PATH)

            log_file.write("\n*************************************************************")
            log_file.write("\n######### Script Completed at : " + str(datetime.datetime.now()) + " #########\n\n")
            print "END : ", str(datetime.datetime.now())

            write_md5_of_dump(group_dump_path, configs_file_path)
            print "*"*70
            print "\n This will take few minutes. Please be patient.\n"
            print "\n Log will be found at: ", log_file_path
            print "\n Log will be found at: ", TOP_PATH
            print "*"*70
            log_file.close()
            call_exit()
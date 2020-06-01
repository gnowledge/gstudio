'''
Import can also be called using command line args as following:
    python manage.py node_import <dump_path> <md5-check> <group-availability> <user-objs-restoration>
    for e.g:
        python manage.py node_import <dump_path> y y y
'''
import os
import json
import imp
import subprocess
from bson import json_util
import pathlib2
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

import time
import datetime

# from bson.json_util import dumps,loads,object_hook
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.ndf.management.commands.import_logic import *
from gnowsys_ndf.ndf.models  import node_collection, triple_collection, filehive_collection, counter_collection
from gnowsys_ndf.ndf.models import HistoryManager, RCS
from gnowsys_ndf.settings import GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIR_PATH, MEDIA_ROOT, GSTUDIO_INSTITUTE_ID, RCS_REPO_DIR
from users_dump_restore import load_users_dump
from gnowsys_ndf.settings import RCS_REPO_DIR_HASH_LEVEL
from schema_mapping import update_factory_schema_mapper
from gnowsys_ndf.ndf.views.utils import replace_in_list, merge_lists_and_maintain_unique_ele

# global variables declaration
DATA_RESTORE_PATH = None
DATA_DUMP_PATH = None
DEFAULT_USER_ID = 1
DEFAULT_USER_SET = False
USER_ID_MAP = {}
SCHEMA_ID_MAP = {}
log_file = None
CONFIG_VARIABLES = None
history_manager = HistoryManager()
rcs = RCS()


'''
Following will be available:
    CONFIG_VARIABLES.FORK=True
    CONFIG_VARIABLES.CLONE=False
    CONFIG_VARIABLES.RESTORE_USER_DATA=True
    CONFIG_VARIABLES.GSTUDIO_INSTITUTE_ID='MZ-10'
    CONFIG_VARIABLES.NODE_ID='58dded48cc566201992f6e79'
    CONFIG_VARIABLES.MD5='aeba0e3629fb0443861c699ae327d962'
'''

def core_import(*args):
    global DATA_RESTORE_PATH
    global log_file
    global log_file_path
    global DATA_DUMP_PATH
    global CONFIG_VARIABLES
    datetimestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file_name = 'node_import_' + str(CONFIG_VARIABLES.NODE_ID) + '_' + str(datetimestamp)
    log_file_path = create_log_file(log_file_name)
    log_file = open(log_file_path, 'w+')
    log_file.write('\n######### Script ran on : ' + str(datetime.datetime.now()) + ' #########\n\n')
    log_file.write('\nUpdated CONFIG_VARIABLES: ' + str(CONFIG_VARIABLES))
    print '\n Validating the data-dump'
    log_file.write(validate_data_dump(DATA_DUMP_PATH, CONFIG_VARIABLES.MD5, *args))
    print '\n Node Restoration.'
    user_json_file_path = os.path.join(DATA_DUMP_PATH, 'users_dump.json')
    log_stmt = user_objs_restoration(True, user_json_file_path, DATA_DUMP_PATH, *args)
    log_file.write(log_stmt)
    print '\n Factory Schema Restoration. Please wait..'
    call_group_import(os.path.join(DATA_DUMP_PATH, 'data', 'rcs-repo'), log_file_path, DATA_RESTORE_PATH, None)
    copy_media_data(os.path.join(DATA_DUMP_PATH, 'media_files', 'data', 'media'))
    return


class Command(BaseCommand):

    def handle(self, *args, **options):
        global SCHEMA_ID_MAP
        global DATA_RESTORE_PATH
        global DATA_DUMP_PATH
        global CONFIG_VARIABLES
        if args:
            DATA_RESTORE_PATH = args[0]
        else:
            DATA_RESTORE_PATH = raw_input('\n\tEnter absolute path of data-dump folder to restore:')
        print '\nDATA_RESTORE_PATH: ', DATA_RESTORE_PATH
        if os.path.exists(DATA_RESTORE_PATH):
            if os.path.exists(os.path.join(DATA_RESTORE_PATH, 'dump')):
                DATA_DUMP_PATH = os.path.join(DATA_RESTORE_PATH, 'dump')
                SCHEMA_ID_MAP = update_factory_schema_mapper(DATA_RESTORE_PATH)
                CONFIG_VARIABLES = read_config_file(DATA_RESTORE_PATH)
                core_import(*args)
            print '*' * 70
            print '\n Log will be found at: ', log_file_path
            print '*' * 70
        else:
            print '\n No dump found at entered path.'
            call_exit()


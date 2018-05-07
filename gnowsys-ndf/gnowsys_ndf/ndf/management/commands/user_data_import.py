# uncompyle6 version 2.14.1
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.6 (default, Oct 26 2016, 20:30:19) 
# [GCC 4.8.4]
# Embedded file name: /home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/management/commands/user_data_import.py
# Compiled at: 2018-01-05 11:49:45
"""
Import can also be called using command line args as following:
    python manage.py group_import <dump_path> <md5-check> <group-availability> <user-objs-restoration>
    like:
        python manage.py group_import <dump_path> y y y
"""
import os, json, imp, subprocess
from bson import json_util
import pathlib2
try:
    from bson import ObjectId
except ImportError:
    from pymongo.objectid import ObjectId

import time, datetime
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.ndf.models import node_collection, triple_collection, filehive_collection, counter_collection
from gnowsys_ndf.ndf.models import HistoryManager, RCS
from gnowsys_ndf.settings import GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIR_PATH, MEDIA_ROOT, GSTUDIO_INSTITUTE_ID, RCS_REPO_DIR
from users_dump_restore import load_users_dump
from import_logic import *
from gnowsys_ndf.settings import RCS_REPO_DIR_HASH_LEVEL
from schema_mapping import update_factory_schema_mapper
from gnowsys_ndf.ndf.views.utils import replace_in_list, merge_lists_and_maintain_unique_ele
DATA_RESTORE_PATH = None
DATA_DUMP_PATH = None
DEFAULT_USER_ID = 1
DEFAULT_USER_SET = False
USER_ID_MAP = {}
SCHEMA_ID_MAP = {}
log_file = None
CONFIG_VARIABLES = None
DATE_AT_IDS = []
GROUP_CONTAINERS = ['Module']
date_related_at_cur = node_collection.find({'_type': 'AttributeType','name': {'$in': ['start_time', 'end_time', 'start_enroll', 'end_enroll']}})
for each_date_related_at in date_related_at_cur:
    DATE_AT_IDS.append(each_date_related_at._id)

history_manager = HistoryManager()
rcs = RCS()

def call_exit():
    print '\n Exiting...'
    os._exit(0)


def core_import(*args):
    global DATA_RESTORE_PATH
    global log_file
    global log_file_path
    global DATA_DUMP_PATH
    global CONFIG_VARIABLES
    datetimestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file_name = 'artifacts_restore_' + str(GSTUDIO_INSTITUTE_ID) + '_' + str(datetimestamp)
    log_file_path = create_log_file(log_file_name)
    log_file = open(log_file_path, 'w+')
    log_file.write('\n######### Script ran on : ' + str(datetime.datetime.now()) + ' #########\n\n')
    log_file.write('\nUpdated CONFIG_VARIABLES: ' + str(CONFIG_VARIABLES))
    print '\n Validating the data-dump'
    print '\nDATA_DUMP_PATH: ', DATA_DUMP_PATH
    log_file.write(validate_data_dump(DATA_DUMP_PATH, CONFIG_VARIABLES.MD5, *args))
    print '\n Checking the dump Group-id availability.'
    print '\n User Restoration.'
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
        if args and len(args) == 4:
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
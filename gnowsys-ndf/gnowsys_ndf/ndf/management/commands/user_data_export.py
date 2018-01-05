import os
import datetime
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from functools import reduce 
import operator
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.ndf.models import node_collection, triple_collection, filehive_collection, counter_collection, GSystemType
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.settings import GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIR_PATH, MEDIA_ROOT, GSTUDIO_INSTITUTE_ID, GSTUDIO_INSTITUTE_ID
from schema_mapping import create_factory_schema_mapper
from users_dump_restore import create_users_dump
from export_logic import create_log_file, write_md5_of_dump, get_counter_ids, dump_node
from gnowsys_ndf.ndf.views.methods import get_group_name_id
from gnowsys_ndf.ndf.templatetags.simple_filters import get_latest_git_hash, get_active_branch_name

UNIT_IDS = []
UNIT_NAMES = []
GLOBAL_DICT = None
DUMP_PATH = None
TOP_PATH = None
GROUP_ID = None
DATA_EXPORT_PATH = None
RESTORE_USER_DATA = True
MEDIA_EXPORT_PATH = None
SCHEMA_MAP_PATH = None
log_file_path = None

def call_exit():
    print "\nExiting..."
    os._exit(0)


def setup_dump_path():
    '''
        Creates factory_schema.json which will hold basic info
        like ObjectId, name, type of TYPES_LIST and GSTUDIO_DEFAULT_GROUPS
    '''
    global DUMP_PATH
    global TOP_PATH
    global DATA_EXPORT_PATH
    global MEDIA_EXPORT_PATH
    DUMP_PATH = TOP_PATH
    DATA_EXPORT_PATH = os.path.join(DUMP_PATH, 'dump')
    MEDIA_EXPORT_PATH = os.path.join(DATA_EXPORT_PATH, 'media_files')
    if not os.path.exists(DATA_EXPORT_PATH):
        os.makedirs(DATA_EXPORT_PATH)
    if not os.path.exists(MEDIA_EXPORT_PATH):
        os.makedirs(MEDIA_EXPORT_PATH)
    return DATA_EXPORT_PATH


def update_globals():

    global GLOBAL_DICT
    global DUMP_PATH
    global TOP_PATH
    global DATA_EXPORT_PATH
    global MEDIA_EXPORT_PATH
    global RESTORE_USER_DATA
    global SCHEMA_MAP_PATH
    global log_file_path

    GLOBAL_DICT = {
                    "DUMP_PATH": DUMP_PATH,
                    "TOP_PATH": TOP_PATH,
                    "DATA_EXPORT_PATH": DATA_EXPORT_PATH,
                    "MEDIA_EXPORT_PATH": MEDIA_EXPORT_PATH,
                    "SCHEMA_MAP_PATH": SCHEMA_MAP_PATH,
                    "log_file_path": log_file_path,
                    }

def create_configs_file():
    global DUMP_PATH
    global UNIT_NAMES
    global UNIT_IDS
    configs_file_path = os.path.join(DUMP_PATH, "migration_configs.py")
    with open(configs_file_path, 'w+') as configs_file_out:
        configs_file_out.write("\nGSTUDIO_INSTITUTE_ID='" + str(GSTUDIO_INSTITUTE_ID) + "'")
        configs_file_out.write("\nRESTORE_USER_DATA=" + str(RESTORE_USER_DATA))
        configs_file_out.write('\nUNIT_NAMES="' + str(UNIT_NAMES) + '"')
        configs_file_out.write('\nUNIT_IDS="' + str(UNIT_IDS) + '"')
        configs_file_out.write("\nGIT_COMMIT_HASH='" + str(get_latest_git_hash()) + "'")
        configs_file_out.write("\nGIT_BRANCH_NAME='" + str(get_active_branch_name()) + "'")
        configs_file_out.write('\nSYSTEM_DETAILS="' + str(os.uname()) + '"')
    return configs_file_path

def pull_nodes(user_ids_list):
    user_ids_list = map(int, user_ids_list)
    all_nodes = node_collection.find({'_type': 'GSystem', 'created_by': {'$in': user_ids_list}, 'group_set': {'$in': UNIT_IDS}})
    print "\nArtifacts: ", all_nodes.count()
    update_globals()
    for each_node in all_nodes:
        print ".",
        dump_node(node=each_node,collection_name=node_collection,variables_dict=GLOBAL_DICT)

class Command(BaseCommand):
    def handle(self, *args, **options):
        global UNIT_IDS
        global UNIT_NAMES
        global log_file
        global log_file_path
        global DATA_EXPORT_PATH
        global SCHEMA_MAP_PATH
        global TOP_PATH
        print "\nUSER DATA EXPORT FOR : ", GSTUDIO_INSTITUTE_ID
        ann_unit_gst_name, ann_unit_gst_id = GSystemType.get_gst_name_id(u"announced_unit")
        if args:
          try:
            args_ids = map(ObjectId,args)
          except Exception as e:
            print "\n\nPlease enter Valid ObjectId."
            call_exit()
          all_ann_units_cur = node_collection.find({'_id': {'$in': args_ids}})
          for each_un in all_ann_units_cur:
            UNIT_IDS.append(each_un._id)
            UNIT_NAMES.append(each_un.name)
        else:
          all_ann_units_cur = node_collection.find({'member_of': ann_unit_gst_id})
          print "\nTotal Units : ", all_ann_units_cur.count()
          for ind, each_ann_unit in enumerate(all_ann_units_cur, start=1):
              unit_selection = raw_input("\n\t{0}. Unit: {1} \n\tEnter y/Y to select: ".format(ind, each_ann_unit.name))
              if unit_selection in ['y', 'Y']:
                  print "\t Yes"
                  UNIT_IDS.append(each_ann_unit._id)
                  UNIT_NAMES.append(each_ann_unit.name)
              else:
                  print "\t No"

        print "\nUser Artifacts Data Export of following Units:"
        print ("\n\t".join(["{0}. {1}".format(i,unit_name) for i, unit_name in enumerate(UNIT_NAMES, 1)]))

        proceed_flag = raw_input("\nEnter y/Y to Confirm: ")
        if proceed_flag:
          try:

            datetimestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_file_name = 'artifacts_dump_' + str(GSTUDIO_INSTITUTE_ID) + "_"+ str(datetimestamp)

            TOP_PATH = os.path.join(GSTUDIO_DATA_ROOT, 'data_export',  log_file_name)
            SCHEMA_MAP_PATH = TOP_PATH

            log_file_path = create_log_file(log_file_name)
            setup_dump_path()


            log_file = open(log_file_path, 'w+')
            log_file.write("\n######### Script ran on : " + str(datetime.datetime.now()) + " #########\n\n")
            log_file.write("User Artifacts Data Export for Units: " + str(UNIT_IDS))

            query = {'member_of': ann_unit_gst_id}
            rec = node_collection.collection.aggregate([
              { "$match": query },
              {  "$group":   {
              '_id': 0,
              'count': { '$sum': 1 } ,
              "author_set": {
                "$addToSet":    "$author_set"
              },
              "group_admin": {
                "$addToSet":    "$group_admin"
              }
              },},

              {  "$project": {
              '_id': 0,
              'total': '$count',
              "user_ids": {
                  "$cond":    [
                      {
                          "$eq":  [
                              "$author_set",
                              []
                          ]
                      },
                      [],
                      "$author_set"
                  ]
              },
              "admin_ids": {
                  "$cond":    [
                      {
                          "$eq":  [
                              "$group_admin",
                              []
                          ]
                      },
                      [],
                      "$group_admin"
                  ]
              }

              }
              }
            ])

            for e in rec['result']:
                user_ids_lists = e['user_ids']
                admin_ids_lists = e['admin_ids']
            user_id_list = reduce(operator.concat, user_ids_lists)
            admin_id_list = reduce(operator.concat, admin_ids_lists)
            non_admin_user_id_list = list(set(user_id_list) - set(admin_id_list))

            if non_admin_user_id_list:
              log_file.write("Users ids: " + str(non_admin_user_id_list))
              pull_nodes(non_admin_user_id_list)
              create_users_dump(DATA_EXPORT_PATH, user_id_list)
              get_counter_ids(user_ids=user_id_list)
              create_factory_schema_mapper(SCHEMA_MAP_PATH)
              configs_file_path = create_configs_file()
              write_md5_of_dump(DATA_EXPORT_PATH, configs_file_path)
            else:
              log_file.write("No users with non-admin rights found.")
          except Exception as user_data_export_err:
            log_file.write("Error occurred: " + str(user_data_export_err))
            pass
          finally:
            log_file.write("\n*************************************************************")
            log_file.write("\n######### Script Completed at : " + str(datetime.datetime.now()) + " #########\n\n")
            print "\nSTART : ", str(datetimestamp)
            print "\nEND : ", str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
            print "*"*70
            print "\n Log will be found at: ", log_file_path
            print "*"*70
            log_file.close()
            call_exit()
        else:
          call_exit()
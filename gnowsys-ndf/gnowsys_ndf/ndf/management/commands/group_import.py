import os
import json
import imp

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

import time
import datetime

from bson.json_util import dumps,loads,object_hook
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.ndf.models  import node_collection, triple_collection, filehive_collection, counter_collection
from gnowsys_ndf.settings import GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIR_PATH, MEDIA_ROOT, GSTUDIO_INSTITUTE_ID
from users_dump_restore import load_users_dump
from schema_mapping import update_factory_schema_mapper

from django.core import serializers
# global variables declaration
DATA_RESTORE_PATH = None
DATA_DUMP_PATH = None
DEFAULT_USER_ID = None
DEFAULT_USER_SET = False
USER_ID_MAP = {}
SCHEMA_ID_MAP = {}
log_file = None
CONFIG_VARIABLES = None
'''
Following will be available:
    CONFIG_VARIABLES.FORK=True
    CONFIG_VARIABLES.CLONE=False
    CONFIG_VARIABLES.RESTORE_USER_DATA=True
    CONFIG_VARIABLES.GSTUDIO_INSTITUTE_ID='MZ-10'
    CONFIG_VARIABLES.GROUP_ID='58dded48cc566201992f6e79'
    CONFIG_VARIABLES.MD5='aeba0e3629fb0443861c699ae327d962'
'''

def create_log_file(restore_path):
    '''
        Creates log file in gstudio-logs/ with 
        the name of the dump folder
    '''
    restore_path = restore_path.split("/")[-1]
    log_file_name = 'group_restore_of_dump_' + str(CONFIG_VARIABLES.GROUP_ID)+ '.log'
    if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
        os.makedirs(GSTUDIO_LOGS_DIR_PATH)

    log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
    global log_file
    log_file = open(log_file_path, 'w+')
    log_file.write("\n######### Script ran on : " + str(datetime.datetime.now()) + " #########\n\n")
    return log_file_path


def call_exit():
    print "\n Exiting..."
    os._exit(0)

def read_config_file():
    """
    Read migration_configs.py file generated during
     the export of group and load the variables in 
     CONFIG_VARIABLES to be accessible in entire program
    """
    global log_file
    global CONFIG_VARIABLES
    CONFIG_VARIABLES = imp.load_source('config_variables',
            os.path.join(DATA_RESTORE_PATH,'migration_configs.py'))
    log_file.write("\nUpdated CONFIG_VARIABLES: "+ str(CONFIG_VARIABLES))

def validate_data_dump():
    """
    For validation of the exported dump and the 
     importing data-dump, calculate MD5 and
     check with CONFIG_VARIABLES.MD5
     This will ensure the exported data is NOT altered
     before importing
    """
    global log_file
    from checksumdir import dirhash
    md5hash = dirhash(DATA_DUMP_PATH, 'md5')
    if CONFIG_VARIABLES.MD5 != md5hash:
        print "\n MD5 NOT matching."
        log_file.write("\n Checksum validation Failed on dump data")

        call_exit()
    else:
        log_file.write("\n Checksum validation Success on dump data")
        print "\nValidation Success..!"

def check_group_availability():
    group_node = node_collection.one({'_id': ObjectId(CONFIG_VARIABLES.GROUP_ID)})
    global log_file
    if group_node:
        log_file.write("\n Group with Restore Group ID is FOUND on Target system.")
        print "\n Group with restoration ID already exists."
        call_exit()
    else:
        log_file.write("\n Group with Restore Group ID NOT found on Target system.")
        print "\n Group with restoration ID does not exists."
        print " Proceeding to restore."

def user_objs_restoration():
    global USER_ID_MAP
    global DEFAULT_USER_ID
    global DEFAULT_USER_SET
    global log_file
    user_json_data = None
    # print "CONFIG_VARIABLES.RESTORE_USER_DATA"
    if CONFIG_VARIABLES.RESTORE_USER_DATA:
        user_dump_restore = raw_input("\n\tUser dump is available.  \
            Would you like to restore it (y/n) ?: ")
        if user_dump_restore == 'y' or user_dump_restore == 'Y':
            log_file.write("\n Request for users restoration : Yes.")

            user_json_file_path = os.path.join(DATA_DUMP_PATH, 'users_dump.json')
            with open(user_json_file_path, 'rb+') as user_json_fin:
                user_json_data = json.loads(user_json_fin.read())
                USER_ID_MAP = load_users_dump(DATA_DUMP_PATH, user_json_data)
                log_file.write("\n USER_ID_MAP: "+ str(USER_ID_MAP))
        else:
            log_file.write("\n Request for users restoration : No.")
            DEFAULT_USER_SET = True
            default_user_confirmation = raw_input("\n\tRestoration will use default usre-id=1. \
            \n\tEnter y to continue, or n if you want to use some other id?: ")
            if default_user_confirmation == 'y' or default_user_confirmation == 'Y':
                log_file.write("\n Request for Default user with id=1 : Yes.")
                DEFAULT_USER_ID = 1
            else:
                log_file.write("\n Request for Default user with id=1 : No.")
                DEFAULT_USER_ID = int(raw_input("Enter user-id: "))
                log_file.write("\n Request for Setting Default user with id :" + str(DEFAULT_USER_SET))

def restore_filehive_objects(rcs_filehives_path):
    print "Filehives"
    global log_file
    for dir_, _, files in os.walk(rcs_filehives_path):
        for filename in files:
            filepath =  os.path.join(dir_, filename)
            data = get_json_file(filepath)
            f = filehive_collection.find_one({'_id': ObjectId(data['_id'])})
            log_file.write("\nFound Existing Filehives : \n\tNew: " + "\n\tOld: "+str(data))
            if not f:
                log_file.write("\n : Inserting Filehives doc " + str(data))

                print "Inserting Filehives doc"
                filehive_collection.collection.insert(data)

def restore_node_objects(rcs_nodes_path):
    if path[0] == 'Node':
        # print "\n\n\ndata._id ",data['_id']
        n = node_collection.find_one({'_id': ObjectId(data['_id'])})
        if n:
            log_file.write("\n*************************************************************")
            log_file.write("\nFound Existing Node : " + str(n._id))

            node_changed = False
            print "Updating Node doc"
            print n.name
            if n.author_set != data['author_set'] and data['author_set']:
                print "\n Original author_set --- ", len(n.author_set)
                print "\n New author_set --- ", len(data['author_set']), data['author_set']
                n.author_set.extend(data['author_set'])
                print "\n Updated author_set --- ", len(n.author_set)

                node_changed = True
            if n.relation_set != data['relation_set'] and data['relation_set']:
                n.relation_set.extend(data['relation_set'])
                node_changed = True
            if n.attribute_set != data['attribute_set'] and data['attribute_set']:
                n.attribute_set.extend(data['attribute_set'])
                node_changed = True
            if n.post_node != data['post_node'] and data['post_node']:
                n.post_node.extend(data['post_node'])
                node_changed = True
            if n.prior_node != data['prior_node'] and data['prior_node']:
                n.prior_node.extend(data['prior_node'])
                node_changed = True
            if n.origin != data['origin'] and data['origin']:
                n.origin.extend(data['origin'])
                node_changed = True
            if n.collection_set != data['collection_set'] and data['collection_set']:
                n.collection_set.extend(data['collection_set'])
                node_changed = True
            if node_changed:
                log_file.write("\n Node Updated: \n\t OLD: " + str(n), + "\n\tNew: "+str(data))

                n.save()
        else:
            print "Inserting Node doc"
            log_file.write("\n Inserting Node doc : " + str(data))
            node_collection.collection.insert(data)


def restore_triple_objects(rcs_triples_path):
    if path[0] == 'Triples':
        print "\n\n\ndata._id ",data['_id']
        tr = triple_collection.find_one({'_id': ObjectId(data['_id'])})
        if tr:
            log_file.write("\n*************************************************************")
            log_file.write("\nFound Existing Triples : " + str(tr._id))

            print tr.name
            print "Updating Triples doc"

            if tr._type == "GRelation":
                if tr.right_subject != data['right_subject']:
                    rs = []
                    if type(tr.right_subject) == list:
                        rs.extend(tr.right_subject)
                    else:
                        rs.append(tr.right_subject)
                    if type(data['right_subject']) == list:
                        rs.extend(data['right_subject'])
                    else:
                        rs.append(data['right_subject'])
                    tr.right_subject = rs
                    log_file.write("\n Triples GRelation Updated: \n\t OLD: " + str(tr), + "\n\tNew: "+str(data))

                    tr.save()
            if tr._type == "GAttribute":
                if tr.object_value != data['object_value']:
                    tr.object_value = data['object_value']
                    log_file.write("\n Triples GAttribute Updated: \n\t OLD: " + str(tr), + "\n\tNew: "+str(data))
                    tr.save()
        else:
            print "Inserting GAttribute Triples doc"
            print "\n data['_type'] ",data['_type']
            if data['_type'] == "GRelation":
                rt_id = data['relation_type']['_id']
                rt_node = node_collection.one({'_id': ObjectId(rt_id)})
                data['relation_type'] = rt_node.get_dbref()

                print "Inserting GRelation Triples doc", data
                log_file.write("\n Inserting GRelation Triple doc : " + str(data))
                triple_collection.collection.insert(data)

            if data['_type'] == "GAttribute":
                at_id = data['attribute_type']['_id']
                at_node = node_collection.one({'_id': ObjectId(at_id)})
                data['attribute_type'] = at_node.get_dbref()
                log_file.write("\n Inserting GAttribute Triple doc : " + str(data))

                triple_collection.collection.insert(data)
        # node_collection.collection.insert(data)


def restore_counter_objects(rcs_counters_path):
    print "Counters"
    c = counters_collection.find_one({'_id': ObjectId(data['_id'])})
    if c:
        log_file.write("\n*************************************************************")
        log_file.write("\nFound Existing Counters : " + str(c._id))

        counter_changed = False
        print "Updating Counter doc"
        print c.user_id
        if c.last_update != data['last_update'] :
            c.last_update = data['last_update']
            counter_changed = True

        if c.enrolled != data['enrolled'] :
            c.enrolled = data['enrolled']
            counter_changed = True

        if c.modules_completed != data['modules_completed'] :
            c.modules_completed = data['modules_completed']
            counter_changed = True

        if c.course_score != data['course_score'] :
            c.course_score = data['course_score']
            counter_changed = True

        if c.units_completed != data['units_completed'] :
            c.units_completed = data['units_completed']
            counter_changed = True

        if c.no_comments_by_user != data['no_comments_by_user'] :
            c.no_comments_by_user = data['no_comments_by_user']
            counter_changed = True

        if c.no_comments_for_user != data['no_comments_for_user'] :
            c.no_comments_for_user = data['no_comments_for_user']
            counter_changed = True

        if c.no_files_created != data['no_files_created'] :
            c.no_files_created = data['no_files_created']
            counter_changed = True

        if c.no_visits_gained_on_files != data['no_visits_gained_on_files'] :
            c.no_visits_gained_on_files = data['no_visits_gained_on_files']
            counter_changed = True

        if c.no_comments_received_on_files != data['no_comments_received_on_files'] :
            c.no_comments_received_on_files = data['no_comments_received_on_files']
            counter_changed = True

        if c.no_others_files_visited != data['no_others_files_visited'] :
            c.no_others_files_visited = data['no_others_files_visited']
            counter_changed = True

        if c.no_comments_on_others_files != data['no_comments_on_others_files'] :
            c.no_comments_on_others_files = data['no_comments_on_others_files']
            counter_changed = True

        if c.rating_count_received_on_files != data['rating_count_received_on_files'] :
            c.rating_count_received_on_files = data['rating_count_received_on_files']
            counter_changed = True

        if c.avg_rating_received_on_files != data['avg_rating_received_on_files'] :
            c.avg_rating_received_on_files = data['avg_rating_received_on_files']
            counter_changed = True

        if c.no_questions_attempted != data['no_questions_attempted'] :
            c.no_questions_attempted = data['no_questions_attempted']
            counter_changed = True

        if c.no_correct_answers != data['no_correct_answers'] :
            c.no_correct_answers = data['no_correct_answers']
            counter_changed = True

        if c.no_incorrect_answers != data['no_incorrect_answers'] :
            c.no_incorrect_answers = data['no_incorrect_answers']
            counter_changed = True

        if c.no_notes_written != data['no_notes_written'] :
            c.no_notes_written = data['no_notes_written']
            counter_changed = True

        if c.no_views_gained_on_notes != data['no_views_gained_on_notes'] :
            c.no_views_gained_on_notes = data['no_views_gained_on_notes']
            counter_changed = True

        if c.no_others_notes_visited != data['no_others_notes_visited'] :
            c.no_others_notes_visited = data['no_others_notes_visited']
            counter_changed = True

        if c.no_comments_received_on_notes != data['no_comments_received_on_notes'] :
            c.no_comments_received_on_notes = data['no_comments_received_on_notes']
            counter_changed = True

        if c.no_comments_on_others_notes != data['no_comments_on_others_notes'] :
            c.no_comments_on_others_notes = data['no_comments_on_others_notes']
            counter_changed = True

        if c.rating_count_received_on_notes != data['rating_count_received_on_notes'] :
            c.rating_count_received_on_notes = data['rating_count_received_on_notes']
            counter_changed = True

        if c.avg_rating_received_on_notes != data['avg_rating_received_on_notes'] :
            c.avg_rating_received_on_notes = data['avg_rating_received_on_notes']
            counter_changed = True

        if c.comments_by_others_on_files != data['comments_by_others_on_files'] and data['comments_by_others_on_files']:
            n.comments_by_others_on_files.extend(data['comments_by_others_on_files'])
            counter_changed = True

        if c.comments_by_others_on_notes != data['comments_by_others_on_notes'] and data['comments_by_others_on_notes']:
            n.comments_by_others_on_notes.extend(data['comments_by_others_on_notes'])
            counter_changed = True

        if counter_changed:
            log_file.write("\n Counter Updated: \n\t OLD: " + str(c), + "\n\tNew: "+str(data))
            c.save()
    else:
        print "Inserting Counter doc"
        log_file.write("\n Inserting Counter doc : " + str(data))
        counter_collection.collection.insert(data)

def call_group_import(rcs_repo_path):

    rcs_filehives_path = os.path.join(rcs_repo_path, "Filehives")
    rcs_nodes_path = os.path.join(rcs_repo_path, "Nodes")
    rcs_triples_path = os.path.join(rcs_repo_path, "Triples")
    rcs_counters_path = os.path.join(rcs_repo_path, "Counters")

    # Following sequence is IMPORTANT
    restore_filehive_objects(rcs_filehives_path)
    restore_node_objects(rcs_nodes_path)
    restore_triple_objects(rcs_triples_path)
    restore_counter_objects(rcs_counters_path)

class Command(BaseCommand):
    def handle(self, *args, **options):

        global DATA_RESTORE_PATH
        global DATA_DUMP_PATH
        global SCHEMA_ID_MAP
        DATA_RESTORE_PATH = raw_input("\n\tEnter absolute path of data-dump folder to restore:")
        if os.path.exists(DATA_RESTORE_PATH):
            DATA_DUMP_PATH = os.path.join(DATA_RESTORE_PATH, 'dump')
            log_file_path = create_log_file(DATA_RESTORE_PATH)
            print "*"*70
            # print "\n Export will be found at: ", DATA_EXPORT_PATH
            print "\n Log will be found at: ", log_file_path
            print "\n This will take few minutes. Please be patient.\n"
            print "*"*70
            read_config_file()
            validate_data_dump()
            check_group_availability()
            user_objs_restoration()

            SCHEMA_ID_MAP = update_factory_schema_mapper(DATA_DUMP_PATH)
            # print "\n SCHEMA_ID_MAP: ", len(SCHEMA_ID_MAP)

            call_group_import(os.path.join(DATA_DUMP_PATH, 'data', 'rcs-repo'))
        else:
            print "\n No dump found at entered path."
            call_exit()

def get_json_file(filepath):
    history_manager = HistoryManager()
    rcs = RCS()
    
    # this will create a .json file of the document(node)
    # at manage.py level
    rcs.checkout(filepath)

    try:
        fp = filepath.split('/')[-1]

        if fp.endswith(',v'):
            fp = fp.split(',')[0]
        with open(filepath, 'r') as version_file:
            doc_obj = json.loads(version_file.read(), object_hook=json_util.object_hook)
            rcs.checkin(fp)
        return doc_obj

    except Exception, e:
        print "Exception while getting JSON: ", e
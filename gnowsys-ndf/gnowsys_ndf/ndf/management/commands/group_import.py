import os
import json
import imp

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

import time

from bson.json_util import dumps,loads,object_hook
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.ndf.models  import node_collection, triple_collection, filehive_collection, counter_collection
from gnowsys_ndf.settings import GSTUDIO_DATA_ROOT, GSTUDIO_LOGS_DIR_PATH, MEDIA_ROOT, GSTUDIO_INSTITUTE_ID
from users_dump_restore import load_users_dump
from schema_mapping import update_factory_schema_mapper

from django.core import serializers
# global variables declaration
DATA_RESTORE_PATH = None
CONFIG_VARIABLES = None
DATA_DUMP_PATH = None
DEFAULT_USER_ID = None
DEFAULT_USER_SET = False
USER_ID_MAP = dict
SCHEMA_ID_MAP = dict
'''
Following will be available:
    CONFIG_VARIABLES.FORK=True
    CONFIG_VARIABLES.CLONE=False
    CONFIG_VARIABLES.RESTORE_USER_DATA=True
    CONFIG_VARIABLES.GSTUDIO_INSTITUTE_ID='MZ-10'
    CONFIG_VARIABLES.GROUP_ID='58dded48cc566201992f6e79'
    CONFIG_VARIABLES.MD5='aeba0e3629fb0443861c699ae327d962'
'''

def call_exit():
    print "\n Exiting..."
    os._exit(0)

def read_config_file():
    """
    Read migration_configs.py file generated during
     the export of group and load the variables in 
     CONFIG_VARIABLES to be accessible in entire program
    """
    global CONFIG_VARIABLES
    CONFIG_VARIABLES = imp.load_source('config_variables',
            os.path.join(DATA_RESTORE_PATH,'migration_configs.py'))

def validate_data_dump():
    """
    For validation of the exported dump and the 
     importing data-dump, calculate MD5 and
     check with CONFIG_VARIABLES.MD5
     This will ensure the exported data is NOT altered
     before importing
    """
    from checksumdir import dirhash
    md5hash = dirhash(DATA_DUMP_PATH, 'md5')
    if CONFIG_VARIABLES.MD5 != md5hash:
        print "\n MD5 NOT matching."
        call_exit()
    else:
        print "\nValidation Success..!"

def check_group_availability():
    group_node = node_collection.one({'_id': ObjectId(CONFIG_VARIABLES.GROUP_ID)})
    if group_node:
        print "\n Group with restoration ID already exists."
        call_exit()
    else:
        print "\n Group with restoration ID does not exists."
        print " Proceeding to restore."

def user_objs_restoration():
    global USER_ID_MAP
    user_json_data = None
    print "CONFIG_VARIABLES.RESTORE_USER_DATA"
    if CONFIG_VARIABLES.RESTORE_USER_DATA:
        user_dump_restore = raw_input("User dump is available.  \
            Would you like to restore it (y/n) ?: ")
        if user_dump_restore == 'y' or user_dump_restore == 'Y':
            user_json_file_path = os.path.join(DATA_DUMP_PATH, 'users_dump.json')
            with open(user_json_file_path, 'rb+') as user_json_fin:
                user_json_data = json.loads(user_json_fin.read())
                USER_ID_MAP = load_users_dump(DATA_DUMP_PATH, user_json_data)
                # print "\nUSER_ID_MAP: ", USER_ID_MAP
        else:
            DEFAULT_USER_SET = True
            default_user_confirmation = raw_input("Restoration will use default usre-id=1. \
            Enter y to continue, or n if you want to use some other id?: ")
            if default_user_confirmation == 'y' or default_user_confirmation == 'Y':
                DEFAULT_USER_ID = 1
            else:
                DEFAULT_USER_ID = int(raw_input("Enter user-id: "))


class Command(BaseCommand):
    def handle(self, *args, **options):

        global DATA_RESTORE_PATH
        global DATA_DUMP_PATH
        global SCHEMA_ID_MAP
        DATA_RESTORE_PATH = raw_input("\n\tEnter absolute path of data-dump folder to restore:")
        if os.path.exists(DATA_RESTORE_PATH):
            DATA_DUMP_PATH = os.path.join(DATA_RESTORE_PATH, 'dump')
            read_config_file()
            validate_data_dump()
            check_group_availability()
            user_objs_restoration()

            SCHEMA_ID_MAP = update_factory_schema_mapper(DATA_DUMP_PATH)
            # print "\n SCHEMA_ID_MAP: ", len(SCHEMA_ID_MAP)

        nodes_path = '/data/gstudio_data_restore/data/rcs-repo/Nodes'
        triples_path = '/data/gstudio_data_restore/data/rcs-repo/Triples'
        filehives_path = '/data/gstudio_data_restore/data/rcs-repo/Filehives'
        counters_path = '/data/gstudio_data_restore/data/rcs-repo/Counters'

        log_file_name = 'data_restore.log'
        if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
            os.makedirs(GSTUDIO_LOGS_DIR_PATH)

        log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
        # print log_file_path
        log_file = open(log_file_path, 'a+')
        log_file.write("######### Script ran on : " + time.strftime("%c") + " #########\n\n")
        log_file.write("\n*************************************************************")


        # path_list = [('Node',nodes_path)]
        # path_list = [('Triples',triples_path)]
        path_list = [('Node',nodes_path),('Triples',triples_path), ('Filehives', filehives_path), ('Counters', counters_path)]
        for path in path_list:
            print "\n Path -- ",path[0]
            file_path_exists =  os.path.exists(path[1])
            filenamelist = []

            for dir_, _, files in os.walk(path[1]):
                for filename in files:
                    filepath =  os.path.join(dir_, filename)
                    filenamelist.append(filepath)

            # print "filenamelist: \n\n:", filenamelist

            for i in filenamelist:
                print "\n *********** "
                print i
                data = get_json_file(i)
                print "======= _id : ", data['_id']
                print "\ndata"
                print data
                print "\n *********** "
                # direct insertion of node in database
                if data:
                    # print data
                    try:
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

                        # Import Triples later.
                        # Check dBRef issue
                        # Cannot Ref a dict
                        # In filelds attribute_type/relation_type where ref is to RT and AT nodes.

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


                        if path[0] == "Filehives":
                            print "Filehives"
                            f = filehive_collection.find_one({'_id': ObjectId(data['_id'])})
                            log_file.write("\nFound Existing Filehives : \n\tNew: " + "\n\tOld: "+str(data))
                            if not f:
                                log_file.write("\n*************************************************************")
                                log_file.write("\n : Inserting Filehives doc " + str(data))

                                print "Inserting Filehives doc"
                                filehive_collection.collection.insert(data)

                        if path[0] == "Counters":
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


                    except Exception as e:
                        print "Exception occured while processing: ", e
        log_file.close()


def get_json_file(filepath):

    print "\n============= in get_json_file():\n"
    history_manager = HistoryManager()
    rcs = RCS()
    # version_no = '1.13'
    # print "\n ORIGINAL filepath --- ", filepath
    # print "\n ORIGINAL RCS_REPO_DIR --- ", RCS_REPO_DIR
    # print "RCS -- ",rcs.checkout(filepath)
    rcs.checkout(filepath)
    # nfilepath = filepath.split(',')[0]
    # print "filepath", filepath.split('/')[-1]
    try:
        fp = filepath.split('/')[-1]

        if fp.endswith(',v'):
            fp = fp.split(',')[0]

        with open(fp, 'r') as version_file:
            json_data = version_file.read()
            # print json_data
            json_dict = json.loads(json_data)
            json_data = json.dumps(json_dict)
            doc_obj =  loads(json_data)
            # doc_obj =  dumps(doc_obj)
            # print "\n doc_obj",doc_obj
            # rcs.checkin(RCS_REPO_DIR)
            rcs.checkin(fp)
        #parse the data for perfect json node creation
        return doc_obj

    except Exception, e:
        print "Exception while getting JSON: ", e
        return None

''' imports from python libraries '''
import os
import csv
import json
import datetime
import urllib2
import hashlib
import io
import time

# import ast
# import magic
# import subprocess
# import mimetypes
# from PIL import Image
# from StringIO import StringIO

''' imports from installed packages '''
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.http import HttpRequest
# from django.core.management.base import CommandError

from django_mongokit import get_database
from mongokit import IS

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node, Filehive, gfs
from gnowsys_ndf.ndf.models import GSystemType, AttributeType, RelationType
from gnowsys_ndf.ndf.models import GSystem, GAttribute, GRelation
from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection, filehive_collection
# from gnowsys_ndf.ndf.models import node_collection
# from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.views.methods import create_grelation, create_gattribute, get_language_tuple
from gnowsys_ndf.ndf.management.commands.create_theme_topic_hierarchy import add_to_collection_set
from gnowsys_ndf.ndf.views.tasks import convertVideo

##############################################################################

SCHEMA_ROOT = os.path.join(os.path.dirname(__file__), "schema_files")
csv_file_name = None

script_start_str = "######### Script ran on : " + time.strftime("%c") + " #########\n------------------------------------------------------------\n"
log_file_not_found = []
log_file_not_found.append(script_start_str)

log_list = []  # To hold intermediate errors
log_list.append(script_start_str)

log_error_rows = []
log_error_rows.append(script_start_str)

file_gst = node_collection.one({'_type': 'GSystemType', "name": "File"})
auth_gst = node_collection.one({'_type': u'GSystemType', 'name': u'Author'})
home_group = node_collection.one({"name": "home", "_type": "Group"})
warehouse_group = node_collection.one({"name": 'warehouse', "_type": "Group"})
theme_gst = node_collection.one({'_type': 'GSystemType', "name": "Theme"})
theme_item_gst = node_collection.one({'_type': 'GSystemType', "name": "theme_item"})
topic_gst = node_collection.one({'_type': 'GSystemType', "name": "Topic"})
twist_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Twist'})
rel_resp_at = node_collection.one({'_type': 'AttributeType', 'name': 'release_response'})
thr_inter_type_at = node_collection.one({'_type': 'AttributeType', 'name': 'thread_interaction_type'})
has_thread_rt = node_collection.one({"_type": "RelationType", "name": u"has_thread"})
has_thumbnail_rt = node_collection.one({'_type': "RelationType", 'name': u"has_thumbnail"})
discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})

nroer_team_id = 1
nroer_team_author_id = None

# setting variable:
# If set true, despite of having file nlob in gridfs, it fetches concern File which contains this _id in it's fs_file_ids field and returns it.
# If set False, returns None
update_file_exists_in_filehive = True

# INFO notes:
# http://172.16.0.252/sites/default/files/nroer_resources/ (for room no 012)
# http://192.168.1.102/sites/default/files/nroer_resources/ (for whole ncert campus)
# http://125.23.112.5/sites/default/files/nroer_resources/ (for public i.e outside campus)

resource_link_common = "http://125.23.112.5/sites/default/files/nroer_resources/"

class Command(BaseCommand):
    help = "\n\tFor saving data in gstudio DB from NROER schema files. This will create 'File' type GSystem instances.\n\tCSV file condition: The first row should contain DB names.\n"

    def handle(self, *args, **options):
        try:
            # print "working........" + SCHEMA_ROOT

            # processing each file of passed multiple CSV files as args
            for file_name in args:

                global csv_file_name
                csv_file_name = file_name

                file_path = os.path.join(SCHEMA_ROOT, file_name)

                if os.path.exists(file_path):

                    file_extension = os.path.splitext(file_name)[1]

                    if "csv" in file_extension:

                        total_rows = 0

                        # Process csv file and convert it to json format at first
                        info_message = "\n- CSV File (" + file_path + ") found!!!"
                        print info_message
                        log_list.append(str(info_message))

                        try:
                            csv_file_path = file_path
                            json_file_name = file_name.rstrip("csv") + "json"
                            json_file_path = os.path.join(SCHEMA_ROOT, json_file_name)
                            json_file_content = ""

                            with open(csv_file_path, 'rb') as csv_file:
                                csv_file_content = csv.DictReader(csv_file, delimiter=",")
                                json_file_content = []

                                for row in csv_file_content:
                                    total_rows += 1
                                    json_file_content.append(row)

                                info_message = "\n- File '" + file_name + "' contains : [ " + str(total_rows) + " ] entries/rows (excluding top-header/column-names)."
                                print info_message
                                log_list.append(str(info_message))

                            with open(json_file_path, 'w') as json_file:
                                json.dump(json_file_content, json_file, indent=4, sort_keys=False)

                            if os.path.exists(json_file_path):
                                file_path = json_file_path
                                is_json_file_exists = True
                                info_message = "\n- JSONType: File (" + json_file_path + ") created successfully.\n"
                                print info_message
                                log_list.append(str(info_message))

                        except Exception as e:
                            error_message = "\n!! CSV-JSONError: " + str(e)
                            print error_message
                            log_list.append(str(error_message))
                            # End of csv-json coversion

                    elif "json" in file_extension:
                        is_json_file_exists = True

                    else:
                        error_message = "\n!! FileTypeError: Please choose either 'csv' or 'json' format supported files!!!\n"
                        print error_message
                        log_list.append(str(error_message))
                        raise Exception(error_mesage)

                    if is_json_file_exists:

                        create_user_nroer_team()
                        # print nroer_team_id

                        # Process json file and create required GSystems, GRelations, and GAttributes
                        info_message = "\n------- Initiating task of processing json-file -------\n"
                        print info_message
                        log_list.append(str(info_message))

                        t0 = time.time()
                        parse_data_create_gsystem(file_path)
                        t1 = time.time()

                        time_diff = t1 - t0
                        total_time_minute = round( (time_diff/60), 2) if time_diff else 0
                        total_time_hour = round( (time_diff/(60*60)), 2) if time_diff else 0

                        # End of processing json file

                        info_message = "\n------- Task finised: Successfully processed json-file -------\n"
                        info_message += "- Total time taken for the processing: \n\n\t" + str(total_time_minute) + " MINUTES\n\t=== OR ===\n\t" + str(total_time_hour) + " HOURS\n"
                        print info_message
                        log_list.append(str(info_message))
                        # End of creation of respective GSystems, GAttributes and GRelations for Enrollment

                else:
                    error_message = "\n!! FileNotFound: Following path (" + file_path + ") doesn't exists!!!\n"
                    print error_message
                    log_list.append(str(error_message))
                    raise Exception(error_message)

        except Exception as e:
            print str(e)
            log_list.append(str(e))

        finally:
            if log_list:

                log_list.append("\n ============================================================ End of Iteration ============================================================\n\n\n")
                # print log_list

                log_file_name = args[0].rstrip("csv") + "log"
                log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)
                # print log_file_path
                with open(log_file_path, 'a') as log_file:
                    log_file.writelines(log_list)

            if log_file_not_found != [script_start_str]:

                log_file_not_found.append("============================== End of Iteration =====================================\n")
                log_file_not_found.append("-------------------------------------------------------------------------------------\n")

                log_file_name = args[0].replace('.', '_FILES_NOT_FOUND.').rstrip("csv") + "log"
                log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)
                # print log_file_path
                with open(log_file_path, 'a') as log_file:
                    log_file.writelines(log_file_not_found)

            if log_error_rows != [script_start_str]:

                log_error_rows.append("============================== End of Iteration =====================================\n")
                log_error_rows.append("-------------------------------------------------------------------------------------\n")

                log_file_name = args[0].replace('.', '_ERROR_ROWS.').rstrip("csv") + "log"
                log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)
                # print log_file_path
                with open(log_file_path, 'a') as log_file:
                    log_file.writelines(log_error_rows)

    # --- End of handle() ---


def log_print(log_string):
    try:
        log_list.append(log_string)
        print log_string

    except:
        error_message = '\n !! Error while doing log and print.\n\n'
        print error_message
        log_list.append(error_message)


def create_user_nroer_team():
    '''
    Check for the user: "nroer_team". If it doesn't exists, create one.
    '''
    global nroer_team_id
    global nroer_team_author_id

    if User.objects.filter(username="nroer_team"):
        nroer_team_id = get_user_id("nroer_team")
        try:
            nroer_team_author_id = node_collection.one({'_type': 'Author', 'created_by': nroer_team_id})._id
        except Exception, e:
            print e
            info_message = "\n- Creating Author object: 'nroer_team': "
            nroer_team_author_obj = create_author_object(username='nroer_team', user_id=nroer_team_id, email='nroer_team@example.com')
            nroer_team_author_id = nroer_team_author_obj.get('_id')

            info_message += "\n- Created Author object having _id: " + str(nroer_team_author_id)
            log_print(info_message)

    else:
        info_message = "\n- Creating super user: 'nroer_team': "
        user = User.objects.create_superuser(username='nroer_team', password='nroer_team', email='nroer_team@example.com')

        nroer_team_id = user.id

        info_message += "\n- Created super user with following creadentials: "
        info_message += "\n\n\tusername = 'nroer_team', \n\tpassword = 'nroer_team', \n\temail = 'nroer_team@example.com', \n\tid = '" + str(nroer_team_id) + "'"

        log_print(info_message)


def get_user_id(user_name):
    '''
    Takes the "user name" as an argument and returns:
    - django "user id" as a response.
    else
    - returns False.
    '''
    try:
        user_obj = User.objects.get(username=user_name)
        return int(user_obj.id)

    except Exception as e:
        error_message = e + "\n!! for username: " + user_name
        log_print(error_message)
        return False


def cast_to_data_type(value, data_type):
    '''
    This method will cast first argument: "value" to second argument: "data_type" and returns catsed value.
    '''

    value = value.strip()
    casted_value = value

    if data_type == unicode:
        casted_value = unicode(value)

    elif data_type == basestring:
        casted_value = unicode(value)
        # the casting is made to unicode despite of str;
        # to prevent "authorized type" check error in mongoDB

    elif (data_type == int) and str(value):
        casted_value = int(value) if (str.isdigit(str(value))) else value

    elif (data_type == float) and str(value):
        casted_value = float(value) if (str.isdigit(str(value))) else value

    elif (data_type == long) and str(value):
        casted_value = long(value) if (str.isdigit(str(value))) else value

    elif data_type == bool and str(value): # converting unicode to int and then to bool
        casted_value = bool(int(value)) if (str.isdigit(str(value))) else bool(value)

    elif (data_type == list) or isinstance(data_type, list):
        value = value.replace("\n", "").replace(" and ", ",").split(",")

        # check for complex list type like: [int] or [unicode]
        if isinstance(data_type, list) and len(data_type) and isinstance(data_type[0], type):
            casted_value = [data_type[0](i.strip()) for i in value if i]

        else:  # otherwise normal list
            casted_value = [i.strip() for i in value if i]

    elif data_type == datetime.datetime:
        # "value" should be in following example format
        # In [10]: datetime.datetime.strptime( "11/12/2014", "%d/%m/%Y")
        # Out[10]: datetime.datetime(2014, 12, 11, 0, 0)
        casted_value = datetime.datetime.strptime(value, "%d/%m/%Y")

    return casted_value


def get_id_from_hierarchy(hier_list):
    """
    method to check hierarchy of theme-topic.
    returns - ObjectId or None

    Args:
        hier_list (list):
        # e.g:
        # [u'NCF', u'Biology', u'Living world', u'Biological classification']

    Returns: ObjectId or None
        - If hierarchy found to be correct, _id/ObjectId will be returned.
        - else None will be returned.
    """

    theme = hier_list[0]
    topic = hier_list[-1:][0]
    theme_items_list = hier_list[1:-1]

    theme_node = node_collection.one({'name': {'$regex': "^" + unicode(theme) + "$", '$options': 'i'}, 'group_set': {'$in': [home_group._id]}, 'member_of': theme_gst._id })

    if not theme_node:
        return None

    node_id = theme_node._id
    node = theme_node

    for each_item in theme_items_list:
        node = node_collection.one({
                    'name': {'$regex': "^" + unicode(each_item) + "$", '$options': 'i'},
                    'prior_node': {'$in': [node_id]},
                    'member_of': {'$in': [theme_item_gst._id]},
                    'group_set': {'$in': [home_group._id]}
                })

        # print each_item, "===", node.name
        if not node:
            return None

        node_id = node._id

    # print topic, "node_id : ", node_id

    # fetching a theme-item node
    topic_node = node_collection.one({
                'name': {'$regex': "^" + unicode(topic) + "$", '$options': 'i'},
                'group_set': {'$in': [home_group._id]},
                'member_of': {'$in': [topic_gst._id]},
                'prior_node': {'$in': [node_id]}
            })

    if topic_node:
        return topic_node._id


def parse_data_create_gsystem(json_file_path):
    json_file_content = ""

    try:
        with open(json_file_path) as json_file:
            json_file_content = json_file.read()

        json_documents_list = json.loads(json_file_content)

        # Initiating empty node obj and other related data variables
        node = node_collection.collection.GSystem()
        node_keys = node.keys()
        node_structure = node.structure
        # print "\n\n---------------", node_keys

        json_documents_list_spaces = json_documents_list
        json_documents_list = []

        # Removes leading and trailing spaces from keys as well as values
        for json_document_spaces in json_documents_list_spaces:
            json_document = {}

            for key_spaces, value_spaces in json_document_spaces.iteritems():
                json_document[key_spaces.strip().lower()] = value_spaces.strip()

            json_documents_list.append(json_document)

    except Exception as e:
        error_message = "\n!! While parsing the file ("+json_file_path+") got following error...\n " + str(e)
        log_print(error_message)
        raise error_message

    for i, json_document in enumerate(json_documents_list):

        info_message = "\n\n\n********** Processing row number : ["+ str(i + 2) + "] **********"
        log_print(info_message)

        try:

            parsed_json_document = {}
            attribute_relation_list = []

            for key in json_document.iterkeys():
                parsed_key = key.lower()

                if parsed_key in node_keys:
                    # print parsed_key

                    # adding the default field values e.g: created_by, member_of
                    # created_by:
                    if parsed_key == "created_by":
                        if json_document[key]:
                            temp_user_id = get_user_id(json_document[key].strip())
                            if temp_user_id:
                                parsed_json_document[parsed_key] = temp_user_id
                            else:
                                parsed_json_document[parsed_key] = nroer_team_id
                        else:
                            parsed_json_document[parsed_key] = nroer_team_id
                        # print "---", parsed_json_document[parsed_key]

                    # contributors:
                    elif parsed_key == "contributors":
                        if json_document[key]:
                            contrib_list = json_document[key].split(",")

                            temp_contributors = []
                            for each_user in contrib_list:
                                user_id = get_user_id(each_user.strip())
                                if user_id:
                                    temp_contributors.append(user_id)

                            parsed_json_document[parsed_key] = temp_contributors
                        else:
                            parsed_json_document[parsed_key] = [nroer_team_id]
                            # print "===", parsed_json_document[parsed_key]

                    # tags:
                    elif (parsed_key == "tags") and json_document[key]:
                        parsed_json_document[parsed_key] = cast_to_data_type(json_document[key], node_structure.get(parsed_key))
                        # print parsed_json_document[parsed_key]

                    # member_of:
                    elif parsed_key == "member_of":
                        parsed_json_document[parsed_key] = [file_gst._id]
                        # print parsed_json_document[parsed_key]

                      # --- END of adding the default field values

                    else:
                        # parsed_json_document[parsed_key] = json_document[key]
                        parsed_json_document[parsed_key] = cast_to_data_type(json_document[key], node_structure.get(parsed_key))
                        # print parsed_json_document[parsed_key]

                    # --- END of processing for remaining fields

                else:  # key is not in the node_keys
                    parsed_json_document[key] = json_document[key]
                    attribute_relation_list.append(key)
                    # print "key : ", key

            # --END of for loop ---

            # calling method to create File GSystems
            node_obj = create_resource_gsystem(parsed_json_document, i)
            nodeid = node_obj._id if node_obj else None
            # print "nodeid : ", nodeid

            # ----- for updating language -----
            # node_lang = get_language_tuple(eval(parsed_json_document['language']))
            # print "============= :", node_lang
            # print "============= lang :", node_obj.language

            # if node_obj and node_obj.language != node_lang:

            #     update_res = node_collection.collection.update(
            #                         {'_id': ObjectId(nodeid), 'language': {'$ne': node_lang}},
            #                         {'$set': {'language': node_lang}},
            #                         upsert=False,
            #                         multi=False
            #                     )

            #     if update_res['updatedExisting']:
            #         node_obj.reload()

            #         info_message = "\n\n- Update to language of resource: " + str(update_res)
            #         log_print(info_message)

            #         info_message = "\n\n- Now language of resource updates to: " + str(node_obj.language)
            #         log_print(info_message)
                # print "============= lang :", node_obj.language

            # ----- END of updating language -----

            collection_name = parsed_json_document.get('collection', '')

            if collection_name and nodeid:

                collection_node = node_collection.find_one({
                        # '_type': 'File',
                        'member_of': {'$in': [file_gst._id]},
                        'group_set': {'$in': [home_group._id]},
                        'name': unicode(collection_name)
                    })

                if collection_node:
                    add_to_collection_set(collection_node, nodeid)

            thumbnail_url = parsed_json_document.get('thumbnail')
            # print "thumbnail_url : ", thumbnail_url

            if (thumbnail_url and nodeid) and (thumbnail_url != parsed_json_document.get('thumbnail') ):
                try:
                    info_message = "\n\n- Attaching thumbnail to resource\n"
                    log_print(info_message)
                    attach_resource_thumbnail(thumbnail_url, nodeid, parsed_json_document, i)

                except Exception, e:
                    print e

            # print type(nodeid), "-------", nodeid, "\n"
            if (thumbnail_url == parsed_json_document.get('resource_link')) and (warehouse_group._id in node_obj.group_set) :
                for i,each_groupid in enumerate(node_obj.group_set):
                    if each_groupid == warehouse_group._id:
                        node_obj.group_set.pop(i)
                if home_group._id not in node_obj.group_set:
                    node_obj.group_set.append(home_group._id)
                node_obj.save()

        # create thread node
            if isinstance(nodeid, ObjectId):
                thread_result = create_thread_obj(nodeid)

            # starting processing for the attributes and relations saving
            if isinstance(nodeid, ObjectId) and attribute_relation_list:

                node = node_collection.one({ "_id": ObjectId(nodeid) })

                gst_possible_attributes_dict = node.get_possible_attributes(file_gst._id)
                # print gst_possible_attributes_dict

                relation_list = []
                json_document['name'] = node.name

                # Write code for setting atrributes
                for key in attribute_relation_list:

                    is_relation = True
                    # print "\n", key, "----------\n"

                    for attr_key, attr_value in gst_possible_attributes_dict.iteritems():
                        # print "\n", attr_key,"======", attr_value

                        if key == attr_key:
                            # print key
                            is_relation = False

                            # setting value to "0" for int, float, long (to avoid casting error)
                            # if (attr_value['data_type'] in [int, float, long]) and (not json_document[key]):
                            #     json_document[key] = 0

                            if json_document[key]:
                                # print "key : ", key, "\nvalue : ",json_document[key]

                                info_message = "\n- For GAttribute parsing content | key: '" + attr_key + "' having value: '" + json_document[key]  + "'"
                                log_print(info_message)

                                cast_to_data_type(json_document[key], attr_value['data_type'])

                                if attr_value['data_type'] == "curricular":
                                    # setting int values for CR/XCR
                                    if json_document[key] == "CR":
                                        json_document[key] = 1
                                    elif json_document[key] == "XCR":
                                        json_document[key] = 0
                                    else:  # needs to be confirm
                                        json_document[key] = 0

                                    # json_document[key] = bool(int(json_document[key]))

                                # print attr_value['data_type'], "@@@@@@@@@  : ", json_document[key]
                                json_document[key] = cast_to_data_type(json_document[key], attr_value['data_type'])
                                # print key, " !!!!!!!!!  : ", json_document[key]

                                subject_id = node._id
                                # print "\n-----\nsubject_id: ", subject_id
                                attribute_type_node = node_collection.one({
                                                                '_type': "AttributeType",
                                                                '$or': [
                                                                        {'name':
                                                                            {'$regex': "^"+attr_key+"$",
                                                                            '$options': 'i'}
                                                                        },
                                                                        {'altnames': {'$regex': "^"+attr_key+"$", '$options': 'i'}
                                                                        }
                                                                    ]
                                                               })

                                # print "\nattribute_type_node: ", attribute_type_node.name
                                object_value = json_document[key]
                                # print "\nobject_value: ", object_value
                                ga_node = None

                                info_message = "\n- Creating GAttribute ("+node.name+" -- "+attribute_type_node.name+" -- "+str(json_document[key])+") ...\n"
                                log_print(info_message)

                                ga_node = create_gattribute(subject_id, attribute_type_node, object_value)

                                info_message = "- Created ga_node : "+ str(ga_node.name) + "\n"
                                log_print(info_message)

                                # To break outer for loop as key found
                                break

                            else:
                                error_message = "\n!! DataNotFound: No data found for field ("+str(attr_key)+") while creating GSystem ( -- "+str(node.name)+")\n"
                                log_print(error_message)

                        # ---END of if (key == attr_key)

                    if is_relation:
                        relation_list.append(key)

                if not relation_list:
                    # No possible relations defined for this node
                    info_message = "\n!! ("+str(node.name)+"): No possible relations defined for this node.\n"
                    log_print(info_message)
                    return

                gst_possible_relations_dict = node.get_possible_relations(file_gst._id)

                # processing each entry in relation_list
                # print "=== relation_list : ", relation_list

                for key in relation_list:
                  is_relation = True

                  for rel_key, rel_value in gst_possible_relations_dict.iteritems():
                    if key == rel_key:
                    # if key == "teaches":
                        is_relation = False

                        if json_document[key]:

                            # most often the data is hierarchy sep by ":"
                            if ":" in json_document[key]:
                                formatted_list = []
                                temp_teaches_list = json_document[key].replace("\n", "").split(":")
                                # print "\n temp_teaches", temp_teaches

                                for v in temp_teaches_list:
                                    formatted_list.append(v.strip())

                                right_subject_id = []
                                # print "~~~~~~~~~~~", formatted_list
                                # rsub_id = _get_id_from_hierarchy(formatted_list)
                                rsub_id = get_id_from_hierarchy(formatted_list)
                                # print "=== rsub_id : ", rsub_id
                                hierarchy_output = None

                                # checking every item in hierarchy exist and leaf node's _id found
                                if rsub_id:
                                    right_subject_id.append(rsub_id)
                                    json_document[key] = right_subject_id
                                    # print json_document[key]

                                else:
                                    error_message = "\n!! While creating teaches rel: Any one of the item in hierarchy"+ str(json_document[key]) +"does not exist in Db. \n!! So relation: " + str(key) + " cannot be created.\n"
                                    log_print(error_message)
                                    break

                            # sometimes direct leaf-node may be present without hierarchy and ":"
                            else:
                                formatted_list = list(json_document[key].strip())
                                right_subject_id = []
                                right_subject_id.append(_get_id_from_hierarchy(formatted_list))
                                json_document[key] = right_subject_id

                            # print "\n----------", json_document[key]
                            info_message = "\n- For GRelation parsing content | key: " + str(rel_key) + " -- " + str(json_document[key])
                            log_print(info_message)
                            # print list(json_document[key])

                            # perform_eval_type(key, json_document, "GSystem", "GSystem")

                            for right_subject_id in json_document[key]:
                                # print "\njson_document[key]: ", json_document[key]

                                subject_id = node._id
                                # print "subject_id : ", subject_id
                                # print "node.name: ", node.name
                                # Here we are appending list of ObjectIds of GSystemType's type_of field
                                # along with the ObjectId of GSystemType's itself (whose GSystem is getting created)
                                # This is because some of the RelationType's are holding Base class's ObjectId
                                # and not that of the Derived one's
                                # Delibrately keeping GSystemType's ObjectId first in the list
                                # And hence, used $in operator in the query!
                                rel_subject_type = []
                                rel_subject_type.append(file_gst._id)

                                if file_gst.type_of:
                                    rel_subject_type.extend(file_gst.type_of)

                                relation_type_node = node_collection.one({'_type': "RelationType",
                                                                          '$or': [{'name': {'$regex': "^"+rel_key+"$", '$options': 'i'}},
                                                                                  {'altnames': {'$regex': "^"+rel_key+"$", '$options': 'i'}}],
                                                                          'subject_type': {'$in': rel_subject_type}
                                                                  })

                                right_subject_id_or_list = []
                                right_subject_id_or_list.append(ObjectId(right_subject_id))

                                nodes = triple_collection.find({'_type': "GRelation",
                                            'subject': subject_id,
                                            'relation_type': relation_type_node._id
                                          })

                                # sending list of all the possible right subject to relation
                                for n in nodes:
                                    if not n.right_subject in right_subject_id_or_list:
                                        right_subject_id_or_list.append(n.right_subject)

                                info_message = "\n- Creating GRelation ("+ str(node.name)+ " -- "+ str(rel_key)+ " -- "+ str(right_subject_id_or_list)+") ..."
                                log_print(info_message)

                                gr_node = create_grelation(subject_id, relation_type_node, right_subject_id_or_list)

                                info_message = "\n- Grelation processing done.\n"
                                log_print(info_message)

                            # To break outer for loop if key found
                            break

                        else:
                            error_message = "\n!! DataNotFound: No data found for relation ("+ str(rel_key)+ ") while creating GSystem (" + str(file_gst.name) + " -- " + str(node.name) + ")\n"
                            log_print(error_message)

                            break

              # print relation_list
            else:
                info_message = "\n!! Either resource is already created or file is already saved into filehive/DB or file not found"
                log_print(info_message)

                continue

        except Exception as e:
            error_message = "\n While creating ("+str(json_document['name'])+") got following error...\n " + str(e)
            print "!!!!!!!!!!!!EEEEEEEERRRRRRRRRRRRRROOOOOOORRRRRRRRRRRRR......................"

            # file_error_msg = "\nFile with following details got an error: \n"
            file_error_msg = "\n========================" + " Row No : " + str(i + 2) + " ========================\n"
            # file_error_msg += "- Row No   : " + str(i + 2) + "\n"
            file_error_msg += "- Name     : " + json_document["name"] + "\n"
            file_error_msg += "- File Name: " + json_document["file_name"] + "\n"
            file_error_msg += "- ERROR    : " + str(e) + "\n\n"
            file_error_msg += "- Following are the row details : \n\n" + unicode(json.dumps(json_document, sort_keys=True, indent=4, ensure_ascii=False)) + "\n"
            file_error_msg += "============================================================\n\n\n"
            log_error_rows.append(file_error_msg)

            log_print(error_message)


def create_thread_obj(node_id):
    '''
    Creates thread object.
        RT : has_thread
        AT : release_response, thread_interaction_type
    '''
    try:
        node_obj = node_collection.one({'_id': ObjectId(node_id)})
        release_response_val = True
        interaction_type_val = unicode('Comment')
        thread_obj = None
        thread_obj = node_collection.one({"_type": "GSystem", "member_of": ObjectId(twist_gst._id),"relation_set.thread_of": ObjectId(node_obj._id)})

        if thread_obj == None:
            # print "\n\n Creating new thread node"
            thread_obj = node_collection.collection.GSystem()
            thread_obj.name = u"Thread_of_" + unicode(node_obj.name)
            thread_obj.status = u"PUBLISHED"
            thread_obj.created_by = int(nroer_team_id)
            thread_obj.modified_by = int(nroer_team_id)
            thread_obj.contributors.append(int(nroer_team_id))
            thread_obj.member_of.append(ObjectId(twist_gst._id))
            thread_obj.group_set.append(home_group._id)
            thread_obj.save()
            # creating GRelation
            gr = create_grelation(node_obj._id, has_thread_rt, thread_obj._id)
            create_gattribute(thread_obj._id, rel_resp_at, release_response_val)
            create_gattribute(thread_obj._id, thr_inter_type_at, interaction_type_val)
            create_gattribute(node_obj._id, discussion_enable_at, True)
            thread_obj.reload()
            node_obj.reload()
            # print "\n\n thread_obj", thread_obj.attribute_set, "\n---\n"
            info_message = "\n- Successfully created thread obj - " + thread_obj._id.__str__() +" for - " + node_obj._id.__str__()
            log_print(info_message)

    except Exception as e:
        info_message = "\n- Error occurred while creating thread obj for - " + node_obj._id.__str__() +" - " + str(e)
        log_print(info_message)


def create_resource_gsystem(resource_data, row_no='', group_set_id=None):
    # fetching resource from url

    resource_link = resource_data.get("resource_link")  # actual download file link
    resource_link = resource_link.replace(' ', '%20')

    if not resource_link:
        resource_link = resource_link_common + resource_data.get("file_name")
        # print "---------------",resource_link

    filename = resource_link.split("/")[-1]  # actual download file name with extension. e.g: neuron.jpg

    info_message = "\n- Fetching resource from : '" + resource_link + "'"
    log_print(info_message)

    print "  (Might take some time. please hold on ...)\n"

    try:
        files = urllib2.urlopen(resource_link)
        info_message = "  Fetched the resource successfully!\n"
        log_print(info_message)

    except urllib2.URLError, e:
        error_message = "\n!! File Not Found at: " + resource_link
        log_print(error_message)

        file_not_found_msg = "\nFile with following details not found: \n"
        file_not_found_msg += "- Row No   : " + str(row_no) + "\n"
        file_not_found_msg += "- Name     : " + resource_data["name"] + "\n"
        file_not_found_msg += "- File Name: " + resource_data["file_name"] + "\n"
        file_not_found_msg += "- URL      : " + resource_link + "\n\n"
        file_not_found_msg += "- ERROR    : " + str(e) + "\n\n"
        log_file_not_found.append(file_not_found_msg)
        return None

    files = io.BytesIO(files.read())
    files.name = filename

    name = unicode(resource_data["name"])  # name to be given to gsystem
    userid = resource_data["created_by"]
    # content_org = resource_data["content_org"]
    tags = resource_data["tags"]
    if resource_data['language']:
        language = get_language_tuple(eval(resource_data['language']))
    else:
        language = ('en', 'English')
    group_set_id = ObjectId(group_set_id) if group_set_id else home_group._id

    img_type = None
    access_policy = None
    usrname = "nroer_team"

    files.seek(0)

    fh_obj = filehive_collection.collection.Filehive()

    filehive_obj_exists = fh_obj.check_if_file_exists(files)

    if filehive_obj_exists:
        info_message = "\n- Resource file exists in Filehive collection having id: '" + \
        str(filehive_obj_exists["_id"]) + "'"
        log_print(info_message)

        if update_file_exists_in_filehive:
            file_obj = node_collection.find_one({
                                '_type': 'GSystem',
                                'if_file.original.id': filehive_obj_exists._id
                                })
            # print "file_obj : ", file_obj

            if file_obj:
                info_message = "\n- Returning File GSystem despite of being in filehive having '_id': " + file_obj._id.__str__()
                log_print(info_message)

                return file_obj

        return None

    else:  # creating new resource/file-gsystem

        info_message = "\n- Creating resource: " + str(resource_data["name"])
        log_list.append(str(info_message))
        print info_message

        files.seek(0)

        file_gs_obj = node_collection.collection.GSystem()

        file_gs_obj.fill_gstystem_values(
                                    request=HttpRequest(),
                                    name=resource_data["name"],
                                    group_set=[home_group._id],
                                    language=language,
                                    uploaded_file=files,
                                    created_by=nroer_team_id,
                                    member_of=file_gst._id,
                                    origin={'csv-import':csv_file_name},
                                    unique_gs_per_file=True
                                )
        # print "+++++++++++++++++++++++++++++++++++++",file_gs_obj.content_org,file_gs_obj
        file_gs_obj.content_org = resource_data['content_org']
        file_gs_obj.tags = resource_data["tags"]
        file_gs_obj.content = resource_data['content_org']
        file_gs_obj.status = u"PUBLISHED"
        file_gs_obj.save(groupid=home_group._id)

        if 'video' in file_gs_obj.if_file.mime_type:
            convertVideo.delay(nroer_team_id, str(file_gs_obj._id), resource_data["name"])

        print "\n\n =================| Printing newly created object |=================\n", file_gs_obj
        print "\n ===================================================================\n\n"

        info_message = "\n- Created resource/File-GSystem object of name: '" + unicode(name) + "' having ObjectId: " + unicode(file_gs_obj._id) + "\n- Saved resource into Filehive. \n"
        log_print(info_message)

        # print "\n----------", fileobj
        return file_gs_obj


def attach_resource_thumbnail(thumbnail_url, node_id, resource_data, row_no):

    updated_res_data = resource_data.copy()

    updated_res_data['resource_link'] = thumbnail_url
    updated_res_data['name'] = u'Thumbnail: ' + thumbnail_url.split('/')[-1]

    # updated_res_data['content_org'] = ''
    # updated_res_data['tags'] = []

    # th_id: thumbnail id
    th_obj = create_resource_gsystem(updated_res_data, row_no, group_set_id=warehouse_group._id)
    th_id = th_obj._id

    # th_obj = node_collection.one({'_id': ObjectId(th_id)})

    # # tring to keep mid-size image otherwise thumbnail
    # try:
    #     th_gridfs_id = th_obj.fs_file_ids[2]
    # except:
    #     th_gridfs_id = th_obj.fs_file_ids[1]
    # # print "th_gridfs_id: ", th_gridfs_id

    # node_obj = node_collection.one({'_id': ObjectId(node_id)})

    # print "~~~~~~~~~~", ObjectId(node_id), " : ", has_thumbnail_rt, " : ", ObjectId(th_id)

    info_message = "\n- Creating GRelation ("+ str(node_id)+ " -- has_thumbnail -- "+ str(th_id)+") ..."
    log_print(info_message)

    print '\n Created/Updated GRelation Object:\n'
    create_grelation(ObjectId(node_id), has_thumbnail_rt, ObjectId(th_id))
    print '\n\n'

    info_message = "\n- Grelation processing done for has_thumbnail.\n"
    log_print(info_message)

    # # print "node_obj.fs_file_ids: ", node_obj.fs_file_ids
    # node_fs_file_ids = node_obj.fs_file_ids

    # if len(node_fs_file_ids) == 1:
    th_obj.group_set.append(ObjectId(warehouse_group._id))
    if ObjectId(home_group._id) in th_obj.group_set:
        th_obj.group_set.remove(ObjectId(home_group._id))
    # print "**********************************",th_obj.group_set

    th_obj.save()
    #     node_fs_file_ids.append(ObjectId(th_gridfs_id))
    # elif len(node_fs_file_ids) > 1:
    #     node_fs_file_ids[1] = ObjectId(th_gridfs_id)

    # # print "node_fs_file_ids: ", node_fs_file_ids

    # node_collection.collection.update(
    #                                     {'_id': ObjectId(node_id)},
    #                                     {'$set': {'fs_file_ids': node_fs_file_ids}}
    #                                 )


def create_author_object(username, user_id, email=None):

    auth = node_collection.one({'_type': u"Author", 'created_by': int(user_id)})
    # This will create user document in Author collection to behave user as a group.
    if auth is None:

        if not email:
            email = unicode(username) + u'@example.com'

        print "\n Creating new Author obj for ", username
        auth = node_collection.collection.Author()
        auth.name = unicode(username)
        auth.email = unicode(email)
        auth.password = u""
        auth.member_of.append(auth_gst._id)
        auth.group_type = u"PUBLIC"
        auth.edit_policy = u"NON_EDITABLE"
        auth.subscription_policy = u"OPEN"
        auth.created_by = user_id
        auth.modified_by = user_id
        auth.contributors.append(user_id)
        auth.group_admin.append(user_id)
        auth.preferred_languages = {'primary': ('en', 'English')}
        auth.origin = [{'script': 'nroer_data_entry.py'}]
        auth.agency_type = "Other"
        auth_id = ObjectId()
        auth['_id'] = auth_id
        auth.save(groupid=auth._id)
        home_group_obj = node_collection.one({'_type': u"Group", 'name': unicode("home")})
        if user_id not in home_group_obj.author_set:
            node_collection.collection.update({'_id': home_group_obj._id}, {'$push': {'author_set': user_id }}, upsert=False, multi=False)
            home_group_obj.reload()
        desk_group_obj = node_collection.one({'_type': u"Group", 'name': unicode("desk")})
        if desk_group_obj and user_id not in desk_group_obj.author_set:
            node_collection.collection.update({'_id': desk_group_obj._id}, {'$push': {'author_set': user_id }}, upsert=False, multi=False)
            desk_group_obj.reload()

    return auth

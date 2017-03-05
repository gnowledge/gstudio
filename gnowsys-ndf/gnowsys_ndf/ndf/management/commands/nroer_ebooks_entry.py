''' -- imports from python libraries -- '''
import os
import csv
import json
import datetime
import zipfile
import urllib2
import hashlib
import io
import time

# import subprocess
# import magic
# import ast
# import mimetypes
# from PIL import Image
# from StringIO import StringIO

''' imports from installed packages '''
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

# from django.core.management.base import CommandError
# from django.http import Http404
# from django.template.defaultfilters import slugify

from django_mongokit import get_database
from mongokit import IS

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node, File
from gnowsys_ndf.ndf.models import GSystemType, AttributeType, RelationType
from gnowsys_ndf.ndf.models import GSystem, GAttribute, GRelation
from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection

from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.views.methods import create_grelation, create_gattribute

# from gnowsys_ndf.settings import GAPPS
# from gnowsys_ndf.ndf.models import DATA_TYPE_CHOICES

##############################################################################

SCHEMA_ROOT = os.path.join(os.path.dirname(__file__), "schema_files/nroer_ebooks_csv")
EBOOKS_ROOT = os.path.expanduser("~") + "/nroer_ebooks/"

# needed for getting uploaded documents link in content_org
current_site = Site.objects.get_current()
current_site.domain = "127.0.0.1:8000" if (current_site.domain == u'example.com') else current_site.domain

log_list = []  # To hold intermediate errors

log_list.append("\n######### Script run on : " + time.strftime("%c") + " #########\n############################################################\n")

file_gst = node_collection.one({"name": "File"})
home_group = node_collection.one({"name": "home", "_type": "Group"})
theme_gst = node_collection.one({"name": "Theme"})
theme_item_gst = node_collection.one({"name": "theme_item"})
topic_gst = node_collection.one({"name": "Topic"})
GST_IMAGE = node_collection.one({'name': 'Image', '_type': 'GSystemType'})
nroer_team_id = 1

class Command(BaseCommand):
    help = "\n\tFor saving E-Book data in gstudio DB from NROER E-Book schema files. This will create 'File' type GSystem instances."

    def handle(self, *args, **options):
        try:
            # print "working........" + SCHEMA_ROOT

            # processing each file of passed multiple CSV files as args
            for file_name in args:
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

                        # Process json file and create required GSystems, GRelations, and GAttributes
                        info_message = "\n------- Initiating task of processing json-file -------\n"
                        print info_message
                        log_list.append(str(info_message))

                        t0 = time.time()
                        parse_data_create_gsystem(file_path)
                        t1 = time.time()

                        time_diff = t1 - t0
                        # print time_diff
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

                log_list.append("\n =====================================\
                    ======================= End of Iteration ============\
                    ================================================\n")
                # print log_list
                log_file_name = args[0].rstrip("csv") + "log"
                log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)
                # print log_file_path
                with open(log_file_path, 'a') as log_file:
                    log_file.writelines(log_list)

  # --- End of handle() ---


def create_user_nroer_team():
    '''
    Check for the user: "nroer_team". If it doesn't exists, create one.
    '''
    global nroer_team_id

    if User.objects.filter(username="nroer_team"):
        nroer_team_id = get_user_id("nroer_team")

    else:
        info_message = "\n- Creating super user: 'nroer_team': "
        user = User.objects.create_superuser(username='nroer_team', password='nroer_team', email='nroer_team@example.com')

        nroer_team_id = user.id

        info_message += "\n- Created super user with following creadentials: "
        info_message += "\n\n\tusername = 'nroer_team', \n\tpassword = 'nroer_team', \n\temail = 'nroer_team@example.com', \n\tid = '" + str(nroer_team_id) + "'"
        print info_message
        log_list.append(info_message)


def get_user_id(user_name):
    '''
    Takes the "user name" as an argument and returns:
    - django "use id" as a response.
    else
    - returns False.
    '''
    try:
        user_obj = User.objects.get(username=user_name)
        return int(user_obj.id)
    except Exception as e:
        error_message = e + "\n!! for username: " + user_name
        print error_message
        log_list.append(str(error_message))
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


def parse_data_create_gsystem(json_file_path):
    json_file_content = ""

    try:
        with open(json_file_path) as json_file:
            json_file_content = json_file.read()

        json_documents_list = json.loads(json_file_content)

        # Process data in proper format
        node = node_collection.collection.File()
        node_keys = node.keys()
        node_structure = node.structure

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
        log_list.append(str(error_message))
        raise error_message

    for i, json_document in enumerate(json_documents_list):

        info_message = "\n\n\n******************** Processing row number : ["+ str(i)+ "] ********************"
        print info_message
        log_list.append(str(info_message))

        try:

            # print "base_folder : ", json_document["base_folder"]
            # print "file_name : ", json_document["file_name"]
            is_base_folder = check_folder_exists(json_document["file_name"], json_document["base_folder"])
            # print "is_base_folder : ", is_base_folder

            if is_base_folder:
                info_message = "- File gsystem holding collection is created. Having name : '" + str(json_document["base_folder"]) + "' and ObjectId : '" + str(is_base_folder) + "'"
                print info_message
                log_list.append(info_message)

            parsed_json_document = {}
            attribute_relation_list = []

            for key in json_document.iterkeys():
                parsed_key = key.lower()

                if parsed_key in node_keys:
                    # print parsed_key
                    # adding the default field values like: created_by, member_of, ...

                    # created_by:
                    if parsed_key == "created_by":
                        if json_document[key]:
                            temp_user_id = get_user_id(json_document[key].strip())
                            if temp_user_id:
                                parsed_json_document[parsed_key] = temp_user_id
                            else:
                                parsed_json_document[parsed_key] = nroer_team_id
                        else:
                            # parsed_json_document[parsed_key] = get_user_id("nroer_team")
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

                        # tag_list = json_document[key].replace("\n", "").split(",")
                        # temp_tag_list = []
                        # for each_tag in tag_list:
                        #   if each_tag:
                        #     temp_tag_list.append(each_tag.strip())
                        # parsed_json_document[parsed_key] = temp_tag_list
                        # print parsed_json_document[parsed_key]

                    # member_of:
                    elif parsed_key == "member_of":
                        parsed_json_document[parsed_key] = [file_gst._id]
                        # print parsed_json_document[parsed_key]

                    else:
                        # parsed_json_document[parsed_key] = json_document[key]
                        parsed_json_document[parsed_key] = cast_to_data_type(json_document[key], node_structure.get(parsed_key))

                    # --- END of processing for remaining fields

                else:
                    parsed_json_document[key] = json_document[key]
                    attribute_relation_list.append(key)

            # calling method to create File GSystems
            nodeid = create_resource_gsystem(parsed_json_document)
            # print type(nodeid), "nodeid ------- : ", nodeid, "\n"

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

                                info_message = "\n- For GAttribute parsing content | key: '" + attr_key + "' having value: '" + json_document[key]  + "'"
                                print info_message
                                log_list.append(str(info_message))

                                cast_to_data_type(json_document[key], attr_value['data_type'])

                                if attr_value['data_type'] == "curricular":
                                    # setting int values for CR/XCR
                                    if json_document[key] == "CR":
                                        json_document[key] = 1
                                    elif json_document[key] == "XCR":
                                        json_document[key] = 0
                                    else:  # needs to be confirm
                                        json_document[key] = 0

                                json_document[key] = cast_to_data_type(json_document[key], attr_value['data_type'])

                                # if attr_value['data_type'] == basestring:

                                #     info_message = "\n- For GAttribute parsing content | key: " + attr_key + " -- value: " + json_document[key]
                                #     print info_message
                                #     log_list.append(str(info_message))

                                # elif attr_value['data_type'] == unicode:
                                #     json_document[key] = unicode(json_document[key])

                                # elif attr_value['data_type'] == bool:
                                #     # setting int values for CR/XCR
                                #     if json_document[key] == "CR":
                                #       json_document[key] = 1
                                #     elif json_document[key] == "XCR":
                                #       json_document[key] = 0

                                #     json_document[key] = bool(int(json_document[key]))

                                # elif attr_value['data_type'] == datetime.datetime:
                                #     json_document[key] = datetime.datetime.strptime(json_document[key], "%d/%m/%Y")

                                # elif attr_value['data_type'] == int:
                                #     json_document[key] = int(json_document[key])
                                # elif attr_value['data_type'] == float:
                                #     json_document[key] = float(json_document[key])
                                # elif attr_value['data_type'] == long:
                                #     json_document[key] = long(json_document[key])

                                # elif type(attr_value['data_type']) == IS:
                                #     for op in attr_value['data_type']._operands:
                                #         if op.lower() == json_document[key].lower():
                                #             json_document[key] = op

                                # elif (attr_value['data_type'] in [list, dict]) or (type(attr_value['data_type']) in [list, dict]):
                                #     if "," not in json_document[key]:
                                #         # Necessary to inform perform_eval_type() that handle this value as list
                                #         json_document[key] = "\"" + json_document[key] + "\", "

                                #     else:
                                #         formatted_value = ""
                                #         for v in json_document[key].split(","):
                                #             formatted_value += "\""+v.strip(" ")+"\", "
                                #             json_document[key] = formatted_value

                                #     perform_eval_type(key, json_document, "GSystem")

                                subject_id = node._id
                                # print "\n-----\nsubject_id: ", subject_id
                                attribute_type_node = node_collection.one({'_type': "AttributeType",
                                                   '$or': [{'name': {'$regex': "^"+attr_key+"$", '$options': 'i'}},
                                                   {'altnames': {'$regex': "^"+attr_key+"$", '$options': 'i'}}]
                                                   })
                                # print "\nattribute_type_node: ", attribute_type_node.name
                                object_value = json_document[key]
                                # print "\nobject_value: ", object_value
                                ga_node = None

                                info_message = "\n- Creating GAttribute ("+node.name+" -- "+attribute_type_node.name+" -- "+str(json_document[key])+") ...\n"
                                print info_message
                                log_list.append(str(info_message))

                                ga_node = create_gattribute(subject_id, attribute_type_node, object_value)

                                info_message = "- Created ga_node : "+ str(ga_node.name) + "\n"
                                print info_message
                                log_list.append(str(info_message))

                                # To break outer for loop as key found
                                break

                            else:
                                error_message = "\n!! DataNotFound: No data found for field ("+str(attr_key)+") while creating GSystem ( -- "+str(node.name)+")\n"
                                print error_message
                                log_list.append(str(error_message))

                        # ---END of if (key == attr_key)

                    if is_relation:
                        relation_list.append(key)

                # print "relation_list : ", relation_list
                if not relation_list:
                    # No possible relations defined for this node
                    info_message = "\n!! ("+str(node.name)+"): No possible relations defined for this node.\n"
                    print info_message
                    log_list.append(str(info_message))
                    return

                gst_possible_relations_dict = node.get_possible_relations(file_gst._id)

                # processing each entry in relation_list
                for key in relation_list:
                  is_relation = True

                  for rel_key, rel_value in gst_possible_relations_dict.iteritems():
                    if key == rel_key: # commented because teaches is only relation being used for time being
                    # if key == "teaches":
                      is_relation = False

                      if json_document[key]:

                        # -----------------------------
                        hierarchy_output = None
                        def _get_id_from_hierarchy(hier_list, oid=None):
                          '''
                          Returns the last hierarchical element's ObjectId.
                          Arguments to be passes is list of unicode names.
                          e.g.
                          hier_list = [u'NCF', u'Science', u'Physical world', u'Materials', u'States of matter', u'Liquids']
                          '''

                          if len(hier_list) >= 2:
                            # print hier_list, "len(hier_list) : ", len(hier_list)
                            try:

                              if oid:
                                curr_oid = node_collection.one({ "_id": oid })
                                # print "curr_oid._id", curr_oid._id

                              else:
                                curr_oid = node_collection.one({ "name": hier_list[0], 'group_set': {'$all': [ObjectId(home_group._id)]}, 'member_of': {'$in': [ObjectId(theme_gst._id), ObjectId(theme_item_gst._id), ObjectId(topic_gst._id)]} })

                              if curr_oid:
                                next_oid = node_collection.one({
                                                          "name": hier_list[1],
                                                          'group_set': {'$all': [ObjectId(home_group._id)]},
                                                          'member_of': {'$in': [ObjectId(theme_item_gst._id), ObjectId(topic_gst._id)]},
                                                          '_id': {'$in': curr_oid.collection_set }
                                                          })

                                # print "||||||", next_oid.name
                                hier_list.remove(hier_list[0])
                                # print "calling _get_id_from_hierarchy(", hier_list,", ", next_oid._id,")"

                                _get_id_from_hierarchy(hier_list, next_oid._id)
                              else:
                                error_message = "!! ObjectId of curr_oid does not found."
                                print error_message
                                log_list.append(error_message)

                            except Exception as e:
                              error_message = "\n!! Error in getting _id from teaches hierarchy. " + str(e)
                              print error_message
                              log_list.append(error_message)

                          else:
                            global hierarchy_output
                            hierarchy_output = oid if oid else None

                          return hierarchy_output
                          # -----------------------------

                        # most often the data is hierarchy sep by ":"
                        if ":" in json_document[key]:
                          formatted_list = []
                          temp_teaches_list = json_document[key].replace("\n", "").split(":")
                          # print "\n temp_teaches", temp_teaches
                          for v in temp_teaches_list:
                            formatted_list.append(v.strip())

                          right_subject_id = []
                          rsub_id = _get_id_from_hierarchy(formatted_list) if formatted_list else None
                          # print hierarchy_output," |||||||||||||||||||", rsub_id

                          # checking every item in hierarchy exist and leaf node's _id found
                          if rsub_id:
                            right_subject_id.append(rsub_id)
                            json_document[key] = right_subject_id
                            # print json_document[key]
                          else:
                            error_message = "\n!! While creating teaches rel: Any one of the item in hierarchy"+ str(json_document[key]) +"does not exist in Db. \n!! So relation: " + str(key) + "cannot be created.\n"
                            log_list.append(error_message)
                            break

                        # sometimes direct leaf-node may be present without hierarchy and ":"
                        else:
                          formatted_list = list(json_document[key].strip())
                          right_subject_id = []
                          right_subject_id.append(_get_id_from_hierarchy(formatted_list))
                          json_document[key] = right_subject_id

                        # print "\n----------", json_document[key]
                        info_message = "\n- For GRelation parsing content | key: " + str(rel_key) + " -- " + str(json_document[key])
                        print info_message
                        log_list.append(str(info_message))
                        # print list(json_document[key])

                        # perform_eval_type(key, json_document, "GSystem", "GSystem")

                        for right_subject_id in json_document[key]:
                          # print "\njson_document[key]: ", json_document[key]

                          subject_id = node._id

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
                          print info_message
                          log_list.append(str(info_message))
                          gr_node = create_grelation(subject_id, relation_type_node, right_subject_id_or_list)

                          info_message = "\n- Grelation processing done.\n"
                          print info_message
                          log_list.append(str(info_message))

                        # To break outer for loop if key found
                        break

                      else:
                        error_message = "\n!! DataNotFound: No data found for relation ("+ str(rel_key)+ ") while creating GSystem (" + str(file_gst.name) + " -- " + str(node.name) + ")\n"
                        print error_message
                        log_list.append(str(error_message))

                        break

              # print relation_list

            else:  # node object or attribute_relation_list does not exist.
                info_message = "\n!! Either resource is already created -- OR -- file is already saved into gridfs/DB -- OR -- file does not exists."
                print info_message
                log_list.append(str(info_message))

                continue

        except Exception as e:
            error_message = "\n While creating ("+str(json_document['name'])+") got following error...\n " + str(e)
            print error_message # Keep it!
            log_list.append(str(error_message))


def check_folder_exists(resource_link, base_folder_name):

    resource_code = resource_link[:5]
    ebook_zip_file = EBOOKS_ROOT + resource_code + "dd.zip"
    # print "ebook_zip_file : ", ebook_zip_file

    if (os.path.exists(ebook_zip_file)):  # check if .zip exists
        ebook_unzip_folder = EBOOKS_ROOT + resource_code + "dd"
        # print "ebook_unzip_folder", ebook_unzip_folder

        if (not (os.path.isdir(ebook_unzip_folder))) and zipfile.is_zipfile(ebook_zip_file):
            # creating the folder for the first time

            info_message = "- Folder does NOT exists. So extracting and creating a new one"
            print info_message
            log_list.append(str(info_message))

            # calling method to unzip the zip file
            unzip(ebook_zip_file, ebook_unzip_folder)

            # ----------------------- for cover page -----------------------
            files_subfolder = ebook_unzip_folder + "/" + os.walk(ebook_unzip_folder).next()[1][0]
            files_list = os.listdir(files_subfolder)
            # print "files_list : ", files_list

            # gathering the cover page with .jpg/.png format
            cover_page_list = [i for i in files_list if i.lower().endswith(('.jpg', '.png'))]
            # print "cover_page_list : ", cover_page_list

            if cover_page_list:
                cover_page_name = cover_page_list[0]
                # print "cover_page_name : ", cover_page_name
                cover_page_path = files_subfolder + "/" + cover_page_name
                # print "cover_page_path : ", cover_page_path

                if os.path.exists(cover_page_path):

                    info_message = "\n- Cover page found for : '" + str(base_folder_name) + "' found. Having name : '" + cover_page_name + "'."
                    print info_message
                    log_list.append(str(info_message))

                    cover_pg_link = "file://" + cover_page_path
                    files = urllib2.urlopen(cover_pg_link)
                    files = io.BytesIO(files.read())
                    files.name = cover_page_name # as per requirements in save_file()

                    filemd5 = hashlib.md5(files.read()).hexdigest()
                    fileobj = node_collection.collection.File()

                    if fileobj.fs.files.exists({"md5": filemd5}):
                        info_message = "\n- Cover page resource exists in DB: '" + str(cur_oid._id) + "'"
                        print info_message
                        log_list.append(str(info_message))
                    else:
                        files.seek(0)
                        content_org = ""
                        tags = []
                        img_type = None
                        language = ""

                        cover_page_oid, video = save_file(files, cover_page_name, nroer_team_id, home_group._id, content_org, tags, img_type, language, "nroer_team", u"PUBLIC", count=0, first_object="")

                        cover_page_url = update_url_field(cover_page_oid, cover_page_name)
                        # cover_page_in_content_org = "[[http://" + current_site.domain + "/" + os.getlogin() + "/file/readDoc/" + cover_page_oid.__str__() + "/" + cover_page_name + "]]"
                        # print "cover_page_in_content_org : ", cover_page_in_content_org
            else:
                cover_page_url = None
                cover_page_oid = None

                info_message = "\n- NO cover page found for : '" + str(base_folder_name) + "'"
                print info_message
                log_list.append(str(info_message))

            # ----------------------- END cover page processing -----------------------

            # overwritting resource link
            resource_link = ebook_zip_file
            # print "resource_link : ", resource_link

            name = base_folder_name
            content_org = cover_page_url if cover_page_url else ""

            resource_link = "file://" + resource_link
            files = urllib2.urlopen(resource_link)
            files = io.BytesIO(files.read())
            files.name = resource_code + "dd.zip" # as per requirements in save_file()

            filemd5 = hashlib.md5(files.read()).hexdigest()
            fileobj = node_collection.collection.File()

            if fileobj.fs.files.exists({"md5": filemd5}):
                gridfs_obj_by_md5 = gridfs_collection.find_one({"md5":filemd5})

                check_obj_by_name_n_fs_ids = collection.File.find_one({
                                        "_type":"File",
                                        'member_of': {'$all': [ObjectId(file_gst._id)]},
                                        'group_set': {'$all': [ObjectId(home_group._id)]},
                                        "name": unicode(base_folder_name),
                                        "fs_file_ids": {"$in":[ gridfs_obj_by_md5["_id"] ]}
                                    })

                if check_obj_by_name_n_fs_ids:
                    # printing appropriate error message
                    info_message = "\n- Resource with same name of '"+ str(base_folder_name) +"' and _type 'File' exist in the group. Ref _id: "+ str(check_obj_by_name_n_fs_ids._id)
                    print info_message
                    log_list.append(str(info_message))
                    return None

            # else process for saving/creating new object
            files.seek(0)
            language = ""

            fileobj_oid, video = save_file(files, name, nroer_team_id, home_group._id, content_org, [], None, language, "nroer_team", u"PUBLIC", count=0, first_object="")

            # creating grelation "has_cover_page"
            if fileobj_oid and cover_page_oid:

                update_url_field(fileobj_oid, resource_code + "dd.zip")
                relation_type_node = node_collection.one({'_type': "RelationType", 'name': "has_cover_page", 'subject_type': {'$in': [file_gst._id]} })
                gr_node = create_grelation(fileobj_oid, relation_type_node, cover_page_oid)

                if gr_node:
                    info_message = "\n- GRelation 'has_cover_page' processing done."
                    print info_message
                    log_list.append(str(info_message))
                else:
                    info_message = "\n!! GRelation 'has_cover_page' could not be created successfully."
                    print info_message
                    log_list.append(str(info_message))

            return fileobj_oid

        elif os.path.isdir(ebook_unzip_folder):
            # Folder already created.
            # print "----------- folder already exists"
            return None

    else:
        # otherwise return None and break the flow
        errror_message = "\n!! Resource with name of : '"+ str(base_folder_name) +"' cannot be created. \n\t - Because resource file containing ZIP : '" + ebook_zip_file + "' does not exists."
        print errror_message
        log_list.append(str(errror_message))
        return None


def create_resource_gsystem(resource_data):

    # fetching resource from url
    resource_link = resource_data.get("file_name")  # actual download file name
    ebook_unzip_folder = EBOOKS_ROOT + resource_link[:5] + "dd"

    if os.path.isdir(ebook_unzip_folder):
        # Folder already created.
        # print "folder already exists"

        resource_link = ebook_unzip_folder + "/" + str(os.listdir(ebook_unzip_folder)[0]) + "/" + resource_link
        # overwritting resource link
        # print "resource_link : ", resource_link

        if os.path.exists(resource_link):
            # checking if file path exists
            resource_link = "file://" + resource_link
            files = urllib2.urlopen(resource_link)
            files = io.BytesIO(files.read())
        else:
            # otherwise return None and break the flow
            errror_message = "\n!! Resource with name of : '"+ str(resource_data["name"]) +"' cannot be created. \n\t - Because resource file : '" + str(resource_link) + "' does not exists."
            print errror_message
            log_list.append(str(errror_message))
            return None
    else:
        # otherwise return None and break the flow
        errror_message = "\n!! Resource with name of : '"+ str(resource_data["name"]) +"' cannot be created. \n\t - Because resource file contained in folder : '" + str(ebook_unzip_folder) + "' does not exists."
        print errror_message
        log_list.append(str(errror_message))
        return None

    filename = resource_link.split("/")[-1]  # actual download file name with extension. e.g: neuron.jpg
    name = unicode(resource_data["name"])  # name to be given to gsystem
    files.name = filename # as per requirements in save_file()

    userid = nroer_team_id
    content_org = resource_data["content_org"]

    tags = resource_data["tags"]

    img_type = None
    language = resource_data["language"]
    usrname = "nroer_team"
    access_policy = None

    filemd5 = hashlib.md5(files.read()).hexdigest()

    fileobj = node_collection.collection.File()

    if fileobj.fs.files.exists({"md5":filemd5}):

        gridfs_obj_by_md5 = gridfs_collection.find_one({"md5":filemd5})

        check_obj_by_name_n_fs_ids = node_collection.find_one({
                                        "_type":"File",
                                        'member_of': {'$all': [ObjectId(file_gst._id)]},
                                        'group_set': {'$all': [ObjectId(home_group._id)]},
                                        "name": unicode(resource_data["name"]),
                                        "fs_file_ids": {"$in":[ gridfs_obj_by_md5["_id"] ]}
                                    })

        if check_obj_by_name_n_fs_ids:
            # printing appropriate error message
            info_message = "\n- Resource with same name of '"+ str(resource_data["name"]) +"' and _type 'File' exist in the group. Ref _id: "+ str(check_obj_by_name_n_fs_ids._id)
            print info_message
            log_list.append(str(info_message))

            return check_obj_by_name_n_fs_ids._id

    else:
        # creating new resource
        files.seek(0)

        info_message = "\n- Creating resource: " + str(resource_data["name"])
        log_list.append(str(info_message))
        print info_message

        fileobj_oid, video = save_file(files, name, userid, home_group._id, content_org, tags, img_type, language, usrname, access_policy=u"PUBLIC")

        # print "\n------------ fileobj_oid : ", fileobj_oid, "--- ", video

        if fileobj_oid:
            # resource is saved in to gridfs along with gsystem creation successfully.

            # featured value
            resource_data["featured"] = True if (resource_data["featured"] == 1) else False

            # adding remaining fields
            node_collection.collection.update(
                                {"_id": fileobj_oid},
                                {'$set':
                                    {
                                        'status': u"PUBLISHED",
                                        'altnames': resource_data["altnames"].strip(),
                                        'featured': resource_data["featured"]
                                    }
                                },
                                upsert=False, multi=False
                            )

            update_url_field(fileobj_oid, filename)

            info_message = "\n- Created resource/GSystem object of name: '" + unicode(name) + "' having ObjectId: " + unicode(fileobj_oid)
            log_list.append(info_message)
            print info_message

            log_list.append("\n- Saved resource into gridfs. \n")
            # print "\n----------", fileobj

            # fileobj_oid is ObjectId("68jhgc..........") and not whole document
            return fileobj_oid

        else:
            return None


def unzip(source_filename, dest_dir):
    '''
    extracts given source .zip file to destination directory.
    '''
    with zipfile.ZipFile(source_filename, "r") as zf:
        zf.extractall(dest_dir)


def update_url_field(oid, name):

    url = "http://" + str(current_site.domain) + "/" + home_group.name.replace(" ","%20").encode('utf8') + "/file/readDoc/" + oid.__str__() + "/" + str(name)

    # adding remaining fields
    node_collection.collection.update({"_id": oid}, {'$set': {'url': unicode(url)} }, upsert=False, multi=False )

    return "[[" + url + "]]"


# relations to be created:
# has_cover_page
# cover_page_of

# things noticed in CSV as contrast to resources CSV :

# - fields that have in resources CSV and not in e-book CSV:
#     - created_by, legal, translation_of, adaptation_of, contributors, prior_node

# - fields that have in e-book and not in CSV resources CSV :
#     - base_folder (contains subject name. e.g: Mathematics-XI)

# - difference in the field:
#     - file_name :
#         - In resources.csv: http://nroer.gov.in/gstudio/resources/images/show/34615/
#         - In e-book.csv: kemh101.pdf

# first five characters from .zip file will be checked with file_name
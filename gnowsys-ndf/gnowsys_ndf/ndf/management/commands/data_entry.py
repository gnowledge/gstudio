''' -- imports from python libraries -- '''
import os
import csv
import json
import ast
import time
import datetime

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from mongokit import IS

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import DATA_TYPE_CHOICES
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.models import GSystemType, AttributeType, RelationType
from gnowsys_ndf.ndf.models import GSystem, GAttribute, GRelation
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, create_college_group_and_setup_data
from gnowsys_ndf.ndf.views.methods import get_student_enrollment_code, create_thread

####################################################################################################################

# TODO:
# 1) Name of attributes/relation in property_order field needs to be replaced with their respective ObjectIds
# 2) regex query needs to be modified because in current situation it's not considering names with space
#    - searching for terms till it finds first space

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files" )

log_list = [] # To hold intermediate errors
log_list.append("\n######### Script run on : " + time.strftime("%c") + " #########\n############################################################\n")

is_json_file_exists = False

gsystem_type_node = None
gsystem_type_id = None
gsystem_type_name = ""
home_grp = node_collection.one({'_type': "Group", 'name': "home"})
group_id = home_grp._id
user_id = 1
mis_group = node_collection.one({
    '_type': "Group",
    '$or': [{
        'name': {'$regex': u"MIS_admin", '$options': 'i'}
    }, {
        'altnames': {'$regex': u"MIS_admin", '$options': 'i'}
    }],
    'group_type': "PRIVATE"
}, {
    'created_by': 1
})

if mis_group is not None:
    group_id = mis_group._id
    user_id = mis_group.created_by  # User who created the above private group

college_gst = node_collection.one({
    "_type": "GSystemType", "name": "College"
})
college_dict = {}
college_name_dict = {}
attr_type_dict = {}
rel_type_dict = {}
create_student_enrollment_code = False
create_private_college_group = False
node_repeated = False


class Command(BaseCommand):
    help = "Based on "

    def handle(self, *args, **options):
        try:
            for file_name in args:
                file_path = os.path.join(SCHEMA_ROOT, file_name)

                global gsystem_type_node
                global gsystem_type_id
                global gsystem_type_name

                gsystem_type_node = None
                gsystem_type_id = None
                gsystem_type_name = ""

                if os.path.exists(file_path):
                    gsystem_type_name = os.path.basename(file_path)
                    gsystem_type_name = os.path.splitext(gsystem_type_name)[0]
                    gsystem_type_name = gsystem_type_name.replace("_", " ")

                    if gsystem_type_name == u"Student":
                        global create_student_enrollment_code
                        create_student_enrollment_code = True
                    elif gsystem_type_name == u"College":
                        global create_private_college_group
                        create_private_college_group = True

                    gsystem_type_node = node_collection.one({
                        "_type": "GSystemType",
                        "$or": [{
                            "name": {"$regex": "^"+gsystem_type_name+"$", '$options': 'i'}
                        }, {
                            "altnames": {"$regex": "^"+gsystem_type_name+"$", '$options': 'i'}
                        }]
                    })

                    if gsystem_type_node:
                        gsystem_type_id = gsystem_type_node._id
                    else:
                        error_message = "\n GSystemTypeError: This GSystemType ("+gsystem_type_name+") doesn't exists for creating it's own GSystem !!!"
                        log_list.append(error_message)
                        raise Exception(error_message)

                    file_extension = os.path.splitext(file_name)[1]

                    if "csv" in file_extension:
                        # Process csv file and convert it to json format at first

                        total_rows = 0
                        info_message = "\n CSVType: Following file (" + file_path + ") found!!!"
                        log_list.append(info_message)

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

                                info_message = "\n- File '" + file_name + "' contains : " + str(total_rows) + " entries/rows (excluding top-header/column-names)."
                                print info_message
                                log_list.append(str(info_message))

                            with open(json_file_path, 'w') as json_file:
                                json.dump(json_file_content,
                                          json_file,
                                          indent=4,
                                          sort_keys=False)

                            if os.path.exists(json_file_path):
                                file_path = json_file_path
                                is_json_file_exists = True
                                info_message = "\n JSONType: Following file (" + json_file_path + ") created successfully.\n"
                                log_list.append(info_message)

                        except Exception as e:
                            error_message = "\n CSV-JSONError: " + str(e)
                            log_list.append(error_message)
                        # End of csv-json coversion

                    elif "json" in file_extension:
                        is_json_file_exists = True

                    else:
                        error_message = "\n FileTypeError: Please choose either 'csv' or 'json' format supported files!!!\n"
                        log_list.append(error_message)
                        raise Exception(error_mesage)

                    if is_json_file_exists:
                        # Process json file and create required GSystems, GRelations, and GAttributes
                        info_message = "\n Task initiated: Processing json-file...\n"
                        log_list.append(info_message)

                        t0 = time.time()
                        parse_data_create_gsystem(file_path, file_name)
                        t1 = time.time()
                        time_diff = t1 - t0
                        # print time_diff
                        total_time_minute = round( (time_diff/60), 2) if time_diff else 0
                        total_time_hour = round( (time_diff/(60*60)), 2) if time_diff else 0
                        # End of processing json file
                        info_message = "\n------- Task finised: Successfully processed json-file -------\n"
                        info_message += "- Total time taken for the processing: \n\n\t" + str(total_time_minute) + " MINUTES\n\t=== OR ===\n\t" + str(total_time_hour) + " HOURS\n"
                        log_list.append(str(info_message))

                        # End of processing json file
                else:
                    error_message = "\n FileNotFound: Following path (" + file_path + ") doesn't exists!!!\n"
                    log_list.append(error_message)
                    raise Exception(error_message)

        except Exception as e:
            error_message = str(e)
            print "\n >>> >>>> >>>>>" + error_message

        finally:
            if log_list:

                log_list.append("\n ============================================================ End of Iteration ============================================================\n")

                log_file_name = gsystem_type_name + ".log"
                log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)
                with open(log_file_path, 'a') as log_file:
                    log_file.writelines(log_list)

        # --- End of handle() ---

# -----------------------------------------------------------------------------------------------------------------
# Function that process json data according to the structure field
# -----------------------------------------------------------------------------------------------------------------


def parse_data_create_gsystem(json_file_path, file_name):
    json_file_content = ""

    try:
        print "\n file_name == ",file_name

        with open(json_file_path) as json_file:
            json_file_content = json_file.read()

        json_documents_list = json.loads(json_file_content)

        # Process data in proper format
        node = node_collection.collection.GSystem()
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
        error_message = "\n While parsing the file ("+json_file_path+") got following error...\n " + str(e)
        log_list.append(error_message)
        print error_message
        raise error_message


    for i, json_document in enumerate(json_documents_list):
        try:
            if file_name in ["QuizItem.csv", "QuizItemEvent.csv"]:
                print "\n\n *******************"
                try:
                    question_content = json_document['content']
                    question_content = question_content.split(' ')
                    question_content = question_content[:4]
                    question_content = ' '.join(question_content)
                    print "\nquestion_content: ", question_content 
                    json_document['name'] = unicode(question_content)
                    json_document['altnames'] = json_document['content']
                    group_id =  ObjectId(json_document['group_id'])
                    group_obj = node_collection.one({'_id': group_id})
                    if group_obj:
                        group_id = group_obj._id
                    else:
                        group_id = home_grp._id
                    json_document['group_id'] = group_id
                    json_document['user_id'] = user_id = int(json_document['user_id'])
                    # options = json_document['options']
                    # json_document['options'] = options.split(' ')
                    # json_document['options'] = ','.join(json_document['options'])
                    # correct_answer = json_document['correct_answer']
                    # json_document['correct_answer']  = correct_answer.split(' ')
                    # json_document['correct_answer'] = ','.join(json_document['correct_answer'])
                    # json_document['max_attempts'] = int(json_document['max_attempts'])
                    # json_document['problem_weight'] = int(json_document['problem_weight'])
                except Exception as de:
                    print "Error: ",de
                print "\n\n NAME ======= ", json_document, group_id, user_id
            global node_repeated
            node_repeated = False
            n_name = ""
            if "first name" in json_document:
                n_name = json_document["first name"] + " "
                if json_document["middle name"]:
                    n_name += json_document["middle name"]
                    if json_document["last name"]:
                        n_name += " "
                n_name += json_document["last name"]
                json_document["name"] = n_name.title()

            info_message = "\n ============ #"+ str(i+1) +" : Start of "+gsystem_type_name+"'s GSystem ("+json_document['name']+") creation/updation ============\n"
            log_list.append(info_message)

            parsed_json_document = {}
            attribute_relation_list = []
            for key in json_document.iterkeys():
                # print "\n key ",key
                parsed_key = key.lower()
                parsed_key = parsed_key.replace(" ", "_")
                if parsed_key in node_keys:
                    if node_structure[parsed_key] == unicode:
                        parsed_json_document[parsed_key] = unicode(json_document[key])
                    elif node_structure[parsed_key] == datetime.datetime:
                        parsed_json_document[parsed_key] = datetime.datetime.strptime(json_document[key], "%d/%m/%Y")
                    else:
                        parsed_json_document[parsed_key] = json_document[key]
                else:
                    parsed_json_document[key] = json_document[key]
                    attribute_relation_list.append(key)
            # print "\nparsed_json_document: ", parsed_json_document
            info_message = "\n Creating "+gsystem_type_name+" ("+parsed_json_document["name"]+")..."
            log_list.append(info_message)
            print "\n HERE == "
            node = create_edit_gsystem(gsystem_type_id, gsystem_type_name, parsed_json_document, user_id)
            print "\n node created === ", node._id, " === ", node.name, node.altnames
            # print "attribute_relation_list == ",attribute_relation_list
            if node:
                if not attribute_relation_list:
                    # Neither possible attribute fields, nor possible relations defined for this node
                    info_message = "\n "+gsystem_type_name+" ("+node.name+"): Neither possible attribute fields, nor possible relations defined for this node !\n"
                    log_list.append(info_message)
                    continue

                gst_possible_attributes_dict = node.get_possible_attributes(gsystem_type_id)
                print "\n gsystem_type_id ===",gst_possible_attributes_dict
                relation_list = []
                json_document['name'] = node.name

                # Write code for setting atrributes
                for key in attribute_relation_list:
                    is_relation = True

                    for attr_key, attr_value in gst_possible_attributes_dict.iteritems():
                        # print "\n\n attr_key === ", attr_key
                        # print "\n\n altnames --  === ", attr_value['altnames']
                        if attr_value['altnames'] and key == attr_value['altnames'].lower() or key == attr_key.lower():
                            is_relation = False

                            if json_document[key]:
                                try:
                                    if attr_value['data_type'] == basestring:
                                        if u"\u2013" in json_document[key]:
                                            json_document[key] = json_document[key].replace(u"\u2013", "-")

                                    info_message = "\n For GAttribute parsing content | key: " + attr_key + " -- " + json_document[key]
                                    log_list.append(info_message)

                                    if attr_value['data_type'] == unicode:
                                        json_document[key] = unicode(json_document[key])

                                    elif attr_value['data_type'] == bool: 
                                        if json_document[key].lower() == "yes":
                                            json_document[key] = True
                                        elif json_document[key].lower() == "no":
                                            json_document[key] = False
                                        else:
                                            json_document[key] = None

                                    elif attr_value['data_type'] == datetime.datetime:

                                        # Use small-case altnames
                                        if key in ["dob", "date of birth", "date of registration"]:
                                            if json_document[key]:
                                                json_document[key] = datetime.datetime.strptime(json_document[key], "%d/%m/%Y")
                                        else:
                                            if json_document[key]:
                                                json_document[key] = datetime.datetime.strptime(json_document[key], "%Y")

                                    elif attr_value['data_type'] in [int, float, long]:
                                        if not json_document[key]:
                                            json_document[key] = 0
                                        else:
                                            if attr_value['data_type'] == int:
                                                json_document[key] = int(json_document[key])
                                            elif attr_value['data_type'] == float:
                                                json_document[key] = float(json_document[key])
                                            else:
                                                json_document[key] = long(json_document[key])

                                    elif type(attr_value['data_type']) == IS:
                                        for op in attr_value['data_type']._operands:
                                            if op.lower() == json_document[key].lower():
                                                json_document[key] = op

                                    elif (attr_value['data_type'] in [list, dict]) or (type(attr_value['data_type']) in [list, dict]):
                                        if "," not in json_document[key]:
                                            # Necessary to inform perform_eval_type() that handle this value as list
                                            json_document[key] = "\"" + json_document[key] + "\", "

                                        else:
                                            formatted_value = ""
                                            for v in json_document[key].split(","):
                                                formatted_value += "\""+v.strip(" ")+"\", "
                                            json_document[key] = formatted_value

                                        perform_eval_type(key, json_document, "GSystem")

                                    subject_id = node._id

                                    attribute_type_node = None
                                    if attr_key in attr_type_dict:
                                        attribute_type_node = attr_type_dict[attr_key]
                                    else:
                                        attribute_type_node = node_collection.one({
                                            '_type': "AttributeType",
                                            '$or': [{
                                                'name': {'$regex': "^" + attr_key + "$", '$options': 'i'}
                                            }, {
                                                'altnames': {'$regex': "^" + attr_key + "$", '$options': 'i'}
                                            }]
                                        })
                                        attr_type_dict[attr_key] = attribute_type_node

                                    object_value = json_document[key]

                                    ga_node = None

                                    info_message = "\n Creating GAttribute (" + node.name + " -- " + attribute_type_node.name + " -- " + str(json_document[key]) + ") ...\n"
                                    log_list.append(info_message)
                                    ga_node = create_gattribute(subject_id, attribute_type_node, object_value)
                                except Exception as e:
                                    error_message = "\n While creating GAttribute (" + attr_key + ") for "+gsystem_type_name+"'s GSystem ("+json_document['name']+") got following error...\n " + str(e) + "\n"
                                    log_list.append(error_message)
                                    print error_message # Keep it!

                                # To break outer for loop as key found
                                break

                            else:
                                error_message = "\n DataNotFound: No data found for field ("+attr_key+") while creating GSystem (" + gsystem_type_name + " -- " + node.name + ") !!!\n"
                                log_list.append(error_message)

                    if is_relation:
                        relation_list.append(key)

                if not relation_list:
                    # No possible relations defined for this node
                    info_message = "\n "+gsystem_type_name+" ("+node.name+"): No possible relations defined for this node !!!\n"
                    log_list.append(info_message)

                else:
                    gst_possible_relations_dict = node.get_possible_relations(gsystem_type_id)

                    # Write code for setting relations
                    for key in relation_list:
                        is_relation = True

                        for rel_key, rel_value in gst_possible_relations_dict.iteritems():
                            if key == rel_value['altnames'].lower() or key == rel_key.lower():
                                is_relation = False

                                if json_document[key]:
                                    # Here semi-colon(';') is used instead of comma(',')
                                    # Beacuse one of the value may contain comma(',') which causes problem in finding required value in database
                                    try:
                                        if ";" not in json_document[key]:
                                            # Necessary to inform perform_eval_type() that handle this value as list
                                            json_document[key] = "\""+json_document[key]+"\", "

                                        else:
                                            formatted_value = ""
                                            for v in json_document[key].split(";"):
                                                formatted_value += "\""+v.strip(" ")+"\", "
                                            json_document[key] = formatted_value

                                        info_message = "\n For GRelation parsing content | key: " + rel_key + " -- " + json_document[key]
                                        log_list.append(info_message)

                                        perform_eval_type(key, json_document, "GSystem", "GSystem")

                                        # for right_subject_id in json_document[key]:
                                        subject_id = node._id

                                        # Here we are appending list of ObjectIds of GSystemType's type_of field 
                                        # along with the ObjectId of GSystemType's itself (whose GSystem is getting created)
                                        # This is because some of the RelationType's are holding Base class's ObjectId
                                        # and not that of the Derived one's
                                        # Delibrately keeping GSystemType's ObjectId first in the list
                                        # And hence, used $in operator in the query!
                                        rel_subject_type = []
                                        rel_subject_type.append(gsystem_type_id)
                                        if gsystem_type_node.type_of:
                                            rel_subject_type.extend(gsystem_type_node.type_of)

                                        relation_type_node = None
                                        if rel_key in rel_type_dict:
                                            relation_type_node = rel_type_dict[rel_key]
                                        else:
                                            relation_type_node = node_collection.one({
                                                '_type': "RelationType",
                                                '$or': [{
                                                    'name': {'$regex': "^" + rel_key + "$", '$options': 'i'}
                                                }, {
                                                    'altnames': {'$regex': "^" + rel_key + "$", '$options': 'i'}
                                                }],
                                                'subject_type': {'$in': rel_subject_type}
                                            })
                                            rel_type_dict[rel_key] = relation_type_node

                                        info_message = "\n Creating GRelation ("+node.name+" -- "+rel_key+" -- "+str(json_document[key])+") ...\n"
                                        log_list.append(info_message)
                                        gr_node = create_grelation(subject_id, relation_type_node, json_document[key])
                                    except Exception as e:
                                        error_message = "\n While creating GRelation (" + rel_key + ") for "+gsystem_type_name+"'s GSystem ("+json_document['name']+") got following error...\n" + str(e) + "\n"
                                        log_list.append(error_message)
                                        pass

                                    if college_gst._id in relation_type_node.object_type:
                                        # Fetch college node's group id
                                        # Append it to node's group_set
                                        node_group_set = node.group_set
                                        is_group_set_changed = False

                                        # Iterate through each college
                                        # Find it's corresponding group's ObjectId
                                        # Append it to node's group_set
                                        for each in json_document[key]:
                                            each = ObjectId(each)
                                            each_str = str(each)
                                            if each_str in college_dict:
                                                college_group_id = college_dict[each_str]
                                                if college_group_id not in node_group_set:
                                                    node_group_set.append(college_group_id)
                                                    is_group_set_changed = True
                                            else:
                                                # If not found in college_dict
                                                # Then find and update college_dict
                                                college_node = node_collection.collection.aggregate([{
                                                    "$match": {"_id": each}
                                                }, {
                                                    "$project": {"group_id": "$relation_set.has_group"}
                                                }])

                                                college_node = college_node["result"]
                                                if college_node:
                                                    college_node = college_node[0]
                                                    college_group_id = college_node["group_id"]
                                                    if college_group_id:
                                                        college_group_id = college_group_id[0][0]
                                                        college_dict[each_str] = college_group_id
                                                        node_group_set.append(college_group_id)
                                                        is_group_set_changed = True

                                        # Update node's group_set with updated list
                                        # if changed
                                        if is_group_set_changed:
                                            node_collection.collection.update({
                                                "_id": subject_id
                                            }, {
                                                "$set": {"group_set": node_group_set}
                                            },
                                                upsert=False, multi=False
                                            )

                                    # To break outer for loop if key found
                                    break

                                else:
                                    error_message = "\n DataNotFound: No data found for relation ("+rel_key+") while creating GSystem ("+gsystem_type_name+" -- "+node.name+") !!!\n"
                                    log_list.append(error_message)
                                    # print error_message

                                    break

                # Create enrollment code (Only for Student)
                if create_student_enrollment_code and not node_repeated:
                    enrollment_code_at = node_collection.one({
                        "_type": "AttributeType", "name": "enrollment_code"
                    })

                    node_exist = node_collection.one({"_id": node._id, "attribute_set.enrollment_code": {"$exists": True}})
                    if not node_exist:
                        # It means enrollment_code is not set for given student node
                        # Then set it
                        try:
                            college_id = None
                            group_id = None
                            for k, v in college_dict.items():
                                college_id = ObjectId(k)
                                group_id = ObjectId(v)

                            student_enrollment_code = get_student_enrollment_code(college_id, node._id, json_document["date of registration"], group_id)

                            info_message = "\n Creating GAttribute (" + node.name + " -- " + enrollment_code_at.name + " -- " + str(student_enrollment_code) + ") ...\n"
                            log_list.append(info_message)
                            ga_node = create_gattribute(node._id, enrollment_code_at, student_enrollment_code)
                        except Exception as e:
                            error_message = "\n StudentEnrollmentCreateError: " + str(e) + "!!!"
                            log_list.append(error_message)

                elif create_private_college_group:
                    # Create a private group for respective college node
                    node_exist = node_collection.one({"_id": node._id, "relation_set.has_group": {"$exists": True}})
                    if not node_exist:
                        try:
                            info_message = "\n Creating private group for given college (" + node.name + ") via RelationType (has_group)...\n"
                            log_list.append(info_message)
                            college_group, college_group_gr = create_college_group_and_setup_data(node)
                        except Exception as e:
                            error_message = "\n CollegeGroupCreateError: " + str(e) + "!!!"
                            log_list.append(error_message)
                if file_name in ["QuizItem.csv", "QuizItemEvent.csv"]:
                    therad_node = create_thread(group_id=group_id, node=node, user_id=user_id, 
                        release_response_val=False, interaction_type_val=None, start_time=None, end_time=None)


        except Exception as e:
            error_message = "\n While creating "+gsystem_type_name+"'s GSystem ("+json_document['name']+") got following error...\n " + str(e)
            log_list.append(error_message)
            print error_message # Keep it!
            import sys
            print "\n ****\n"
            print 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno)


def create_edit_gsystem(gsystem_type_id, gsystem_type_name, json_document, user_id):
    """Creates/Updates respective GSystem and it's related GAttribute(s)
    and GRelation(s)
    """
    node = None
    if "(" in json_document['name'] or ")" in json_document['name']:
        query = {
            "_type": "GSystem",
            'name': json_document['name'],
            'member_of': gsystem_type_id
        }

    else:
        query = {
            "_type": "GSystem",
            '$or': [{
                'name': {'$regex': "^"+json_document['name']+"$", '$options': 'i'}
            }, {
                'altnames': {'$regex': "^"+json_document['name']+"$", '$options': 'i'}
            }],
            'member_of': gsystem_type_id
        }

    if "date of birth" in json_document:
        dob = json_document["date of birth"]
        if dob:
            query.update({"attribute_set.dob": datetime.datetime.strptime(dob, "%d/%m/%Y")})

    if "contact number (mobile)" in json_document:
        mobile_number = json_document["contact number (mobile)"]
        if mobile_number:
            query.update({"attribute_set.mobile_number": long(mobile_number)})

    if "degree name / highest degree" in json_document:
        degree_name = json_document["degree name / highest degree"]
        if degree_name:
            query.update({"attribute_set.degree_name": degree_name})

    if "year of study" in json_document:
        degree_year = json_document["year of study"]
        if degree_year:
            query.update({"attribute_set.degree_year": degree_year})


    if "college ( graduation )" in json_document:
        college_name = json_document["college ( graduation )"]

        if college_name not in college_name_dict:
            college_node = node_collection.one({
                "member_of": college_gst._id, "name": college_name
            }, {
                "name": 1
            })
            college_name_dict[college_name] = college_node

        query.update({"relation_set.student_belongs_to_college": college_name_dict[college_name]._id})

    info_message = "\n query for " + json_document['name'] + " : " + str(query) +  "\n"
    log_list.append(info_message)
    if "QuizItem" not in gsystem_type_name:
        node = node_collection.one(query)

    if node is None:
        try:
            node = node_collection.collection.GSystem()

            personal_details = []
            address_details = []
            details_12 = []
            graduation_details = []
            work_experience = []
            education_details = []
            tot_details = []
            property_order = []

            # TODO: Name of attributes/relation to be replaced with their respective ObjectIds
            if gsystem_type_name in ["Student", "Voluntary Teacher"]:
                personal_details = [
                    ("first_name", "First Name"), 
                    ("middle_name", "Middle Name"), 
                    ("last_name", "Last Name"),
                    ("gender", "Gender"),
                    ("dob", "Date of Birth"),
                    ("religion", "Religion"),
                    ("languages_known", "Languages Known"),
                    ("mobile_number", "Contact Number (Mobile)"),
                    ("alternate_number", "Alternate Number / Landline"),
                    ("email_id", "Email ID")
                ]

            if gsystem_type_name in ["College", "University", "Student", "Voluntary Teacher"]:
                address_details = [
                    ("house_street", "House / Street"),
                    ("village", "Village"),
                    ("taluka", "Taluka"),
                    ("town_city", "Town / City"),
                    ("pin_code", "Pin Code")
                ]

            if gsystem_type_name in ["Voluntary Teacher"]:
                work_experience = [
                    ("key_skills", "Key Skills"),
                    ("profession", "Profession"),
                    ("designation", "Profession"),
                    ("work_exp", "Year of Experience (if Any)")
                ]

                education_details = [
                    ("degree_name", "Degree Name / Highest Degree"),
                    ("degree_specialization", "Degree Specialization"),
                    ("degree_passing_year", "Year of Passing Degree"),
                    ("other_qualifications", "Any other Qualification")
                ]

                tot_details = [
                    ("trainer_of_college", "Volunteer to teach College(s) [At max. 2]"),
                    ("trainer_of_course", "Volunteer to teach Course(s) [At max. 2]"),
                    ("is_tot_attended", "Did you attend TOT?"),
                    ("tot_when", "When did you attend TOT?"),
                ]

            if gsystem_type_name in ["Student"]:
                details_12 = [
                    ("student_has_domicile", "State/Union Territory of Domicile"),
                    ("12_passing_year", "Year of Passing XII")
                ]

                graduation_details = [
                    ("student_belongs_to_college", "College (Graduation)"),
                    ("degree_name", "Degree Name / Highest Degree"),
                    ("degree_year", "Year of Study"),
                    ("college_enroll_num", "College Enrolment Number / Roll No"),
                    ("student_belongs_to_university", "University"),
                    ("is_nss_registered", "Are you registered for NSS?"),
                    ("is_dropout_student", "Are you a dropout student?")
                ]

            if gsystem_type_name in ["College", "University"]:
                address_details.insert(4, ("organization_belongs_to_country", "Country"))
                address_details.insert(4, ("organization_belongs_to_state", "State"))
                address_details.insert(4, ("organization_belongs_to_district", "District"))

                property_order = [
                    ["Address", address_details]
                ]

            if gsystem_type_name in ["University"]:
                affiliated_college_details = [
                    ("affiliated_college", "Affiliated Colleges")
                ]

                property_order.append(["Affiliated Colleges", affiliated_college_details])

            if gsystem_type_name in ["Voluntary Teacher"]:
                address_details.insert(4, ("person_belongs_to_country", "Country"))
                address_details.insert(4, ("person_belongs_to_state", "State"))
                address_details.insert(4, ("person_belongs_to_district", "District"))

                property_order = [
                    ["Personal", personal_details],
                    ["Address", address_details],
                    ["Education", education_details],
                    ["Work Experience", work_experience],
                    ["TOT Details", tot_details],

                ]
            if gsystem_type_name in ["Student"]:
                personal_details.insert(6, ("student_of_caste_category", "Caste Category"))

                address_details.insert(4, ("person_belongs_to_country", "Country"))
                address_details.insert(4, ("person_belongs_to_state", "State"))
                address_details.insert(4, ("person_belongs_to_district", "District"))

                property_order = [
                    ["Personal", personal_details],
                    ["Address", address_details],
                    ["XII", details_12],
                    ["Graduation", graduation_details]
                ]

            node.property_order = property_order

            # Save Node first with it's basic attribute fields
            for key in json_document.keys():
                if node.has_key(key):
                    node[key] = json_document[key]

            node.created_by = user_id
            node.modified_by = user_id
            if user_id not in node.contributors:
                node.contributors.append(user_id)

            node.member_of.append(gsystem_type_id)
            if 'group_id' in json_document:
                group_id = json_document['group_id']
            node.group_set.append(group_id)
            node.status = u"PUBLISHED"

            node.save()
            info_message = "\n "+gsystem_type_name+" ("+node.name+") created successfully.\n"
            log_list.append(info_message)

        except Exception as e:
            error_message = "\n "+gsystem_type_name+"Error: Failed to create ("+json_document['name']+") as " + str(e) + "\n"
            log_list.append(error_message)
            raise Exception(error_message)

    else:
        # Code for updation
        is_node_changed = False

        global node_repeated
        node_repeated = True

        try:
            for key in json_document.iterkeys():
                if key in node:
                    if type(node[key]) == list:
                        if set(node[key]) != set(json_document[key]):
                            node[key] = json_document[key]
                            is_node_changed = True

                    elif type(node[key]) == dict:
                        if cmp(node[key], json_document[key]) != 0:
                            node[key] = json_document[key]
                            is_node_changed = True

                    else:
                        if node[key] != json_document[key]:
                            node[key] = json_document[key]
                            is_node_changed = True

            if is_node_changed:
                node.modified_by = user_id
                if user_id not in node.contributors:
                    node.contributors.append(user_id)

                node.status = u"PUBLISHED"

                node.save()
                info_message = "\n "+gsystem_type_name+" ("+node.name+") updated successfully.\n"
                log_list.append(info_message)

            else:
                info_message = "\n "+gsystem_type_name+" ("+node.name+") already exists (Nothing updated) !\n"
                log_list.append(info_message)

        except Exception as e:
            error_message = "\n "+gsystem_type_name+"Error: Failed to update ("+node.name+") as " + str(e) + "\n"
            log_list.append(error_message)
            raise Exception(error_message)

    return node


def perform_eval_type(eval_field, json_document, type_to_create, type_convert_objectid=None):
    """Converts eval_field's data in json-type to it's corresponding python-type, and
    resets eval_field with that converted data
    """

    try:
        json_document[eval_field] = ast.literal_eval(json_document[eval_field])

    except Exception as e:
        if u"\u201c" in json_document[eval_field]:
            json_document[eval_field] = json_document[eval_field].replace(u"\u201c", "\"")

        if u"\u201d" in json_document[eval_field]:
            json_document[eval_field] = json_document[eval_field].replace(u"\u201d", "\"")

        if u"\u2013" in json_document[eval_field]:
            json_document[eval_field] = json_document[eval_field].replace(u"\u2013", "-")

        try:
            json_document[eval_field] = ast.literal_eval(json_document[eval_field])
        except Exception as e:
            error_message = "\n InvalidDataError: For " + type_to_create + " ("+json_document['name']+") invalid data found -- " + str(e) + "!!!\n"
            log_list.append(error_message)
            raise Exception(error_message)

    type_list = []
    for data in json_document[eval_field]:
        if type_convert_objectid is None:
          if eval_field == "when did you attend tot?":
            type_list.append(datetime.datetime.strptime(data, "%d/%m/%Y"))
          else:
            type_list.append(data)

        else:
            if "(" in data or ")" in data:
                node = node_collection.one({'_type': type_convert_objectid, 
                                            'name': data, 
                                            'group_set': group_id
                                           }, 
                                           {'_id': 1}
                                       )

            else:
                node = node_collection.one({'_type': type_convert_objectid, 
                                            '$or': [{'name': {'$regex': "^"+data+"$", '$options': 'i'}}, 
                                                    {'altnames': {'$regex': "^"+data+"$", '$options': 'i'}}],
                                            'group_set': group_id
                                           }, 
                                           {'_id': 1}
                                       )
        
            if node:
                type_list.append(node._id)
            else:
                error_message = "\n "+type_convert_objectid+"Error ("+eval_field+"): This "+type_convert_objectid+" (" + data + ") doesn't exists for creating "+type_to_create+" (" + json_document['name'] + ") !!!\n"
                log_list.append(error_message)
                raise Exception(error_message)

    # Sets python-type converted list
    json_document[eval_field] = type_list


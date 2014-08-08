''' -- imports from python libraries -- '''
import os
import csv
import json
import ast
import datetime

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database
from mongokit import IS

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import DATA_TYPE_CHOICES
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.models import GSystemType, AttributeType, RelationType
from gnowsys_ndf.ndf.models import GSystem, GAttribute, GRelation


####################################################################################################################

# TODO: 
# 1) Name of attributes/relation in property_order field needs to be replaced with their respective ObjectIds
# 2) regex query needs to be modified because in current situation it's not considering names with space 
#    - searching for terms till it finds first space

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files" )

log_list = [] # To hold intermediate errors

collection = get_database()[Node.collection_name]
is_json_file_exists = False

gsystem_type_node = None
gsystem_type_id = None
gsystem_type_name = ""

mis_group = collection.Node.one({'_type': "Group", 
                                 '$or': [{'name': {'$regex': u"MIS_admin", '$options': 'i'}}, 
                                         {'altnames': {'$regex': u"MIS_admin", '$options': 'i'}}],
                                 'group_type': "PRIVATE"
                                }, 
                                {'created_by': 1})
if(mis_group != None):                            
	group_id =  mis_group._id
	user_id =  mis_group.created_by  # User who created the above private group


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

                    gsystem_type_node = collection.Node.one({'_type': "GSystemType", 
                                                             '$or': [{'name': {'$regex': "^"+gsystem_type_name+"$", '$options': 'i'}}, 
                                                                     {'altnames': {'$regex': "^"+gsystem_type_name+"$", '$options': 'i'}}]
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
                                    json_file_content.append(row)

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

                        parse_data_create_gsystem(file_path)
                    
                        # End of processing json file

                        info_message = "\n Task finised: Successfully processed json-file.\n"
                        log_list.append(info_message)

                        # End of creation of respective GSystems, GAttributes and GRelations for Enrollment

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

def parse_data_create_gsystem(json_file_path):
    json_file_content = ""

    try:
        with open(json_file_path) as json_file:
            json_file_content = json_file.read()

        json_documents_list = json.loads(json_file_content)

        # Process data in proper format
        node = collection.GSystem()
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
        raise error_message

    for i, json_document in enumerate(json_documents_list):
        try:
            n_name = ""
            if json_document.has_key("first name"):
                n_name = json_document["first name"] + " "
                if json_document["middle name"]:
                    n_name += json_document["middle name"] + " "
                n_name += json_document["last name"]
                json_document["name"] = n_name

            info_message = "\n ============ #"+ str(i+1) +" : Start of "+gsystem_type_name+"'s GSystem ("+json_document['name']+") creation/updation ============\n"
            log_list.append(info_message)

            parsed_json_document = {}
            attribute_relation_list = []
            for key in json_document.iterkeys():
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

            info_message = "\n Creating "+gsystem_type_name+" ("+parsed_json_document["name"]+")..."
            log_list.append(info_message)
            node = create_edit_gsystem(gsystem_type_id, gsystem_type_name, parsed_json_document, user_id)

            if node:
                if not attribute_relation_list:
                    # Neither possible attribute fields, nor possible relations defined for this node
                    info_message = "\n "+gsystem_type_name+" ("+node.name+"): Neither possible attribute fields, nor possible relations defined for this node !\n"
                    log_list.append(info_message)
                    continue

                gst_possible_attributes_dict = node.get_possible_attributes(gsystem_type_id)

                relation_list = []
                json_document['name'] = node.name

                # Write code for setting atrributes
                for key in attribute_relation_list:
                    is_relation = True

                    for attr_key, attr_value in gst_possible_attributes_dict.iteritems():
                        if key == attr_value['altnames'].lower() or key == attr_key.lower():
                            is_relation = False

                            if json_document[key]:
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

                                    if key == "dob" or key == "date of birth":
                                        json_document[key] = datetime.datetime.strptime(json_document[key], "%d/%m/%Y")
                                    else:
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
                                attribute_type_node = collection.Node.one({'_type': "AttributeType", 
                                                                           '$or': [{'name': {'$regex': "^"+attr_key+"$", '$options': 'i'}}, 
                                                                                   {'altnames': {'$regex': "^"+attr_key+"$", '$options': 'i'}}]
                                                                       })
                                object_value = json_document[key]

                                ga_node = None

                                info_message = "\n Creating GAttribute ("+node.name+" -- "+attribute_type_node.name+" -- "+str(json_document[key])+") ...\n"
                                log_list.append(info_message)
                                ga_node = create_gattribute(subject_id, attribute_type_node, object_value)

                                # To break outer for loop as key found
                                break

                            else:
                                error_message = "\n DataNotFound: No data found for field ("+attr_key+") while creating GSystem ("+gsystem_type_name+" -- "+node.name+") !!!\n"
                                log_list.append(error_message)

                    if is_relation:
                        relation_list.append(key)

                if not relation_list:
                    # No possible relations defined for this node
                    info_message = "\n "+gsystem_type_name+" ("+node.name+"): No possible relations defined for this node !!!\n"
                    log_list.append(info_message)
                    return

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

                                for right_subject_id in json_document[key]:
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

                                    relation_type_node = collection.Node.one({'_type': "RelationType", 
                                                                              '$or': [{'name': {'$regex': "^"+rel_key+"$", '$options': 'i'}}, 
                                                                                      {'altnames': {'$regex': "^"+rel_key+"$", '$options': 'i'}}],
                                                                              'subject_type': {'$in': rel_subject_type}
                                                                      })

                                    info_message = "\n Creating GRelation ("+node.name+" -- "+rel_key+" -- "+str(right_subject_id)+") ...\n"
                                    log_list.append(info_message)
                                    gr_node = create_grelation(subject_id, relation_type_node, right_subject_id)

                                # To break outer for loop if key found
                                break

                            else:
                                error_message = "\n DataNotFound: No data found for relation ("+rel_key+") while creating GSystem ("+gsystem_type_name+" -- "+node.name+") !!!\n"
                                log_list.append(error_message)
                                # print error_message

                                break


        except Exception as e:
            error_message = "\n While creating "+gsystem_type_name+"'s GSystem ("+json_document['name']+") got following error...\n " + str(e)
            log_list.append(error_message)
            print error_message # Keep it!


def create_edit_gsystem(gsystem_type_id, gsystem_type_name, json_document, user_id):
    """Creates/Updates respective GSystem and it's related GAttribute(s)
    and GRelation(s)
    """
    node = None

    node = collection.Node.one({'_type': "GSystem", 
                                '$or': [{'name': {'$regex': "^"+json_document['name']+"$", '$options': 'i'}}, 
                                        {'altnames': {'$regex': "^"+json_document['name']+"$", '$options': 'i'}}],
                                'member_of': gsystem_type_id
                            })

    if node is None:
        try:
            node = collection.GSystem()

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

        try:
            for key in json_document.iterkeys():
                if node.has_key(key):
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
            node = collection.Node.one({'_type': type_convert_objectid, 
                                        '$or': [{'name': {'$regex': "^"+data+"$", '$options': 'i'}}, 
                                                {'altnames': {'$regex': "^"+data+"$", '$options': 'i'}}]
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


def create_gattribute(subject_id, attribute_type_node, object_value):
    ga_node = None

    ga_node = collection.Triple.one({'_type': "GAttribute", 'subject': subject_id, 'attribute_type': attribute_type_node.get_dbref()})

    if ga_node is None:
        # Code for creation
        try:
            ga_node = collection.GAttribute()

            ga_node.subject = subject_id
            ga_node.attribute_type = attribute_type_node
            ga_node.object_value = object_value
            
            ga_node.status = u"PUBLISHED"
            ga_node.save()
            info_message = " GAttribute ("+ga_node.name+") created successfully.\n"
            log_list.append(info_message)

        except Exception as e:
            error_message = "\n GAttributeCreateError: " + str(e) + "\n"
            log_list.append(error_message)
            raise Exception(error_message)

    else:
        # Code for updation
        is_ga_node_changed = False

        try:
            if type(ga_node.object_value) == list:
                if set(ga_node.object_value) != set(object_value):
                    ga_node.object_value = object_value
                    is_ga_node_changed = True

            elif type(ga_node.object_value) == dict:
                if cmp(ga_node.object_value, object_value) != 0:
                    ga_node.object_value = object_value
                    is_ga_node_changed = True

            else:
                if ga_node.object_value != object_value:
                    ga_node.object_value = object_value
                    is_ga_node_changed = True

            if is_ga_node_changed:
                ga_node.status = u"PUBLISHED"
                ga_node.save()
                info_message = " GAttribute ("+ga_node.name+") updated successfully.\n"
                log_list.append(info_message)

            else:
                info_message = " GAttribute ("+ga_node.name+") already exists (Nothing updated) !\n"
                log_list.append(info_message)

        except Exception as e:
            error_message = "\n GAttributeUpdateError: " + str(e) + "\n"
            log_list.append(error_message)
            raise Exception(error_message)

    return ga_node


def create_grelation(subject_id, relation_type_node, right_subject_id):
    gr_node = None

    gr_node = collection.Triple.one({'_type': "GRelation", 
                                     'subject': subject_id, 
                                     'relation_type': relation_type_node.get_dbref(),
                                     'right_subject': right_subject_id
                                 })

    if gr_node is None:
        # Code for creation
        try:
            gr_node = collection.GRelation()

            gr_node.subject = subject_id
            gr_node.relation_type = relation_type_node
            gr_node.right_subject = right_subject_id

            gr_node.status = u"PUBLISHED"
            
            gr_node.save()
            info_message = " GRelation ("+gr_node.name+") created successfully.\n"
            log_list.append(info_message)

        except Exception as e:
            error_message = "\n GRelationCreateError: " + str(e) + "\n"
            log_list.append(error_message)
            raise Exception(error_message)

    else:
        info_message = " GRelation ("+gr_node.name+") already exists !\n"
        log_list.append(info_message)

    return gr_node

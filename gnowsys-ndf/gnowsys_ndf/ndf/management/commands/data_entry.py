''' -- imports from python libraries -- '''
import os
import csv
import json
import ast
import mimetypes

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

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

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files" )

collection = get_database()[Node.collection_name]
is_json_file_exists = False
user_id = 1  # Very first user (considering superuser/admin)

column_to_field = {
    "First Name": "first_name",
    "Middle Name": "middle_name",
    "Last Name": "last_name",
    "DOB": "dob",
    "Gender": "gender",
    "Religion": "religion",
    "H.No/Street": "street",
    "Village": "town_village",
    "Taluka": "city_taluka",
    "Town/City": "city_taluka",
    "District": "district",
    "Pin": "pincode",
    "Contact Number (Mobile )": "mobile_number",
    "Alternate Contact Number / Landline": "alternate_number",
    "Email Id": "email_id",
    "Languages Known": "languages",
    "Year of Passing 12th Standard": "12_passing_year",
    "Are you part of NSS activities ": "nss_registration",

    #"Country": ["person_belongs_to_country", "organization_belongs_to_country"],
    #"State": ["person_belongs_to_state", "organization_belongs_to_state"],
    "Category": "student_of_caste",
    "Name of College ( Graduation )": "person_belongs_to_college",
    # "Name of University": (need to calculate from relationship [person_belongs_to_college])
    "Registered College Course": "selected_course",
    "Are you one of the following?": "person_has_profession" # / person_has_designation (Check what should come?)
    
}


class Command(BaseCommand):
    help = "Based on "

    def handle(self, *args, **options):
        for file_name in args:
            file_path = os.path.join(SCHEMA_ROOT, file_name)

            if os.path.exists(file_path):
                file_extension = mimetypes.guess_type(file_name)[0]

                if "csv" in file_extension:
                    # Process csv file and convert it to json format at first
                    print "\n CSVType: Follwoing file (", file_path, ") found!!!"
                    
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

                        '''
                        for key in json_file_content[0]:
                            if column_to_field.has_key(key):
                                print "\n ", key, " -- ", column_to_field[key]
                            else:
                                print "\n ", key, " -- ???"
                        '''

                        # print "\n len: ", len(json_file_content)
                        # print "\n ", json_file_content[207]

                        # json_file_content_new = []
                        # for json_dict in json_file_content:
                        #     json_dict_new = {}
                        #     for key in json_dict.iterkeys():
                        #         if column_to_field.has_key(key):
                        #             json_dict_new[column_to_field[key]] = json_dict[key]
                        #         else:
                        #             json_dict_new[key] = json_dict[key]
                            
                        #     # json_file_content.remove(json_dict)
                        #     # json_file_content.append(json_dict_new)
                        #     json_file_content_new.append(json_dict_new)

                        # print "\n len: ", len(json_file_content)
                        # print "\n ", json_file_content[207]
                        # print "\n ", json_file_content_new[207]

                        # print "\n json_file_path: ", json_file_path
                        with open(json_file_path, 'w') as json_file:
                            json.dump(json_file_content, 
                                      json_file, 
                                      indent=4, 
                                      sort_keys=False)

                        if os.path.exists(json_file_path):
                            file_path = json_file_path
                            is_json_file_exists = True
                            print "\n JSONType: Following file (", json_file_path, ") created successfully."

                    except Exception, e:
                        print "\n CSV-JSONError: ", str(e)
                    # End of csv-json coversion

                elif "json" in file_extension:
                    is_json_file_exists = True

                else:
                    print "\n FileTypeError: Please choose either 'csv' or 'json' format supported files!!!\n"
                    return 

                if is_json_file_exists:
                    # Process json file and create required GSystems, GRelations, and GAttributes
                    print "\n Do processing json file task..."

                    parse_data_create_gsystem(file_path)
                    
                    # End of processing json file

                print "\n Done everything...\n"

                # End of creation of respective GSystems, GAttributes and GRelations for Enrollment

            else:
                print "\n FileNotFound: Following path (", file_path, ") doesn't exists!!!\n"

        # --- End of handle() ---

# -----------------------------------------------------------------------------------------------------------------
# Function that process json data according to the structure field
# -----------------------------------------------------------------------------------------------------------------

def parse_data_create_gsystem(json_file_path):
    json_file_content = ""

    with open(json_file_path) as json_file:
        json_file_content = json_file.read()

    json_documents_list = json.loads(json_file_content)

    gsystem_type_name = os.path.basename(json_file_path)
    gsystem_type_name = gsystem_type_name.rstrip(".json")
    # print "\n gsystem_type_name: ", gsystem_type_name

    gsystem_type_id = None
    try:
        gsystem_type_id = collection.Node.one({'_type': "GSystemType", 'name': gsystem_type_name})
        if gsystem_type_id:
            # print "\n ", gsystem_type_id.name, 
            gsystem_type_id = gsystem_type_id._id
            # print " -- ", gsystem_type_id
        else:
            error_message = "\n GSystemTypeError: This GSystemType ("+gsystem_type_name+") doesn't exists for creating it's own GSystem !!!"
            raise Exception(error_message)
    except Exception as e:
        print str(e)

    json_file_content_new = []
    for json_dict in json_documents_list:
        json_dict_new = {}
        for key in json_dict.iterkeys():
            if column_to_field.has_key(key):
                json_dict_new[column_to_field[key]] = json_dict[key]
            else:
                json_dict_new[key] = json_dict[key]
                
        # json_file_content.remove(json_dict)
        # json_file_content.append(json_dict_new)
        json_file_content_new.append(json_dict_new)

    for n in json_file_content_new:
        print "\n json_file_content_new: ", n, "\n"

    # Process data in proper format
    for json_document in json_documents_list:
        if json_document.has_key("first_name"):
            json_document["name"] = json_document["first_name"] + " "
            if json_document["middle_name"]:
                json_document["name"] += json_document["middle_name"] + " "
            json_document["name"] += json_document["last_name"]

        print "\n Creating GSystem(", json_document['name'], ") of GSystemType ("+gsystem_type_name+")..."

        json_document['name'] = unicode(json_document['name'])

        #create_edit_gsystem(gsystem_type_id, gsystem_type_name, json_document, user_id)
    

def create_edit_gsystem(gsystem_type_id, gsystem_type_name, json_document, user_id):
    """Creates/Updates respective GSystem and it's related GAttribute(s)
    and GRelation(s)
    """
    attribute_relation_list = []
    node = None

    if json_document.has_key("first_name"):
        n_name = json_document["first_name"] + " "
        if json_document["middle_name"]:
            n_name += json_document["middle_name"] + " "
        n_name += json_document["last_name"]
        n_name = unicode(n_name)
        node = collection.Node.one({'_type': "GSystem", 'name': json_document['name']})
    else:
        node = collection.Node.one({'_type': "GSystem", 'name': json_document['name']})

    if node is None:

        try:
            node = collection.GSystem()

            gst_possible_attributes_dict = node.get_possible_attributes(gsystem_type_id)
            gst_possible_relations_dict = RelationType.get_possible_relations(gsystem_type_id)[0]

            # print "\n gst_possible_attributes_dict: ", gst_possible_attributes_dict
            # print "\n gst_possible_relations_dict: ", gst_possible_relations_dict

            #print "\n possible_attributes: ", gst_possible_attributes_dict.keys()
        
            # for key in gst_possible_relations_dict.iterkeys():
            #     print "\n relation_name: ", gst_possible_relations_dict[key]["name"]


            # Save Node first with it's basic attribute fields
            for key in json_document.keys():
                if node.has_key(key):
                    node[key] = json_document[key]
                else:
                    attribute_relation_list.append(key)

            if not node.name:
                if json_document.has_key("first_name"):
                    node.name = json_document["first_name"] + " "
                    if json_document["middle_name"]:
                        node.name += json_document["middle_name"] + " "
                    node.name += json_document["last_name"]
                    node.name = unicode(node.name)
                else:
                    node.name = unicode("Instance of " + gsystem_type_name)

            node.created_by = user_id
            node.modified_by = user_id
            if user_id not in node.contributors:
                node.contributors.append(user_id)

            node.member_of.append(gsystem_type_id)

            node.status = u"PUBLISHED"

            node.save()
            print " node.name: ", node.name
            print " node.member_of: ", node.member_of, "\n"

            print "\n "+gsystem_type_name+" ("+node.name+") created successfully."

            if not attribute_relation_list:
                # Neither possible attribute fields, nor possible relations defined for this node
                print "\n "+gsystem_type_name+" ("+node.name+"): Neither possible attribute fields, nor possible relations defined for this node\n"
                return

            # Now save Node's user-defined attribute fields and relations under GAttribute and GRelation respectively
            #for key in json_document.keys():
            for key in attribute_relation_list:
                if not node.has_key(key):
                    is_attribute_relation = collection.Node.one({'name': key})

                    if is_attribute_relation:

                        if is_attribute_relation._type == "AttributeType":
                            if key in gst_possible_attributes_dict.keys():
                                print "\n User defined attribute (" +key+ ") found..."
                                if type(gst_possible_attributes_dict[key][0]) in [list, dict]:
                                    perform_eval_type(key, json_document, "GSystem")

                                elif gst_possible_attributes_dict[key][0] in [int, float, long] and not json_document[key]:
                                    json_document[key] = 0

                            # Create/Edit GAttribute for this node
                            subject_id = node._id
                            attribute_type_node = is_attribute_relation
                            object_value = json_document[key]
                            if key == "languages":
                                print "\n\n json_document[eval_field]: ", json_document[key]
                                print "\n object_value: ", object_value

                            ga_node = create_gattribute(subject_id, attribute_type_node, object_value)
                            print "\n GAttribute ("+ga_node.name+") for GSystem ("+node.name+") created successfully."

                        elif is_attribute_relation._type == "RelationType":
                            for rel_key in gst_possible_relations_dict.iterkeys():
                                if rel_key == is_attribute_relation._id:
                                    print "\n User defined relation (" +key+ ") found..."
                                    perform_eval_type(key, json_document, "GSystem", "GSystem")
                                    for right_subject_id in json_document[key]:
                                        # Create GRelation for this node
                                        subject_id = node._id
                                        relation_type_node = is_attribute_relation
                                        gr_node = create_grelation(subject_id, relation_type_node, right_subject_id)
                                        print "\n GRelation ("+gr_node.name+") for GSystem ("+node.name+") created successfully."

                        else:
                            error_message = "\n InvalidType: Key ("+key+") with invalid type ("+is_attribute_relation._type+") found !!!\n"
                            raise Exception(error_message)

                    else:
                        error_message = "\n UnknownValue: Undefined ("+key+") attribute-field or relation found !!!\n"
                        # raise Exception(error_message)

        except Exception as e:
            print str(e)
            return
    
    else:
        # Code for updation
        print "\n GSystem (", node.name, ") already exists (Nothing updated) !!!"



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

        try:
            json_document[eval_field] = ast.literal_eval(json_document[eval_field])
        except Exception as e:
            error_message = "\n InvalidDataError: For " + type_to_create + " (" + json_document['name'] + ") invalid data found -- " + str(e) + "!!!"
            raise Exception(error_message)


    type_list = []
    for data in json_document[eval_field]:
        # if (eval_field == "complex_data_type") and ((data in DATA_TYPE_CHOICES) or (json_document['data_type'] == "IS()")):
        #     type_list.append(unicode(data))
        if type_convert_objectid is None:
            type_list.append(data)

        else:
            node = collection.Node.one({'_type': type_convert_objectid, 'name': data}, {'_id': 1})
        
            if node:
                type_list.append(node._id)
            else:
                error_message = "\n "+type_convert_objectid+"Error ("+eval_field+"): This "+type_convert_objectid+" (" + data + ") doesn't exists for creating "+type_to_create+" (" + json_document['name'] + ") !!!\n"
                raise Exception(error_message)

    # Sets python-type converted list
    json_document[eval_field] = type_list
    if eval_field == "languages":
        print "\n json_document[eval_field]: ", json_document[eval_field]


def create_gattribute(subject_id, attribute_type_node, object_value):
    try:
        ga_node = collection.GAttribute()

        ga_node.subject = subject_id
        ga_node.attribute_type = attribute_type_node
        print "\n object_value (Inside): ", object_value

        ga_node.object_value = object_value

        ga_node.status = u"PUBLISHED"

        ga_node.save()

    except Exception as e:
        error_message = "\n GAttributeCreateError: " + str(e) + "\n"
        raise Exception(error_message)

    return ga_node


def create_grelation(subject_id, relation_type_node, right_subject_id):
    try:
        gr_node = collection.GRelation()

        gr_node.subject = subject_id
        gr_node.relation_type = relation_type_node
        gr_node.right_subject = right_subject_id

        gr_node.status = u"PUBLISHED"

        gr_node.save()

    except Exception as e:
        error_message = "\n GRelationCreateError: " + str(e) + "\n"
        raise Exception(error_message)

    return gr_node

''' -- imports from python libraries -- '''
import os
import csv
import json
import ast
import mimetypes
import datetime

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
    gsystem_type_name = gsystem_type_name.replace("_", " ")
    # print "\n gsystem_type_name: ", gsystem_type_name

    gsystem_type_id = None
    try:
        gsystem_type_id = collection.Node.one({'_type': "GSystemType", 'name': gsystem_type_name})
        if gsystem_type_id:
            print "\n ", gsystem_type_id.name, 
            gsystem_type_id = gsystem_type_id._id
            print " -- ", gsystem_type_id
        else:
            error_message = "\n GSystemTypeError: This GSystemType ("+gsystem_type_name+") doesn't exists for creating it's own GSystem !!!"
            raise Exception(error_message)


        # Process data in proper format
        node = collection.GSystem()
        node_keys = node.keys()
        node_structure = node.structure


        for json_document in json_documents_list:
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
                    elif node_structure[parsed_key] in [list, dict]:
                        perform_eval_type("complex_data_type", json_document, "AttributeType", "AttributeType")
                    else:
                        parsed_json_document[parsed_key] = json_document[key]
                else:
                    attribute_relation_list.append(key)

            node = create_edit_gsystem(gsystem_type, parsed_json_document, user_id)

            if not attribute_relation_list:
                # Neither possible attribute fields, nor possible relations defined for this node
                print "\n "+gsystem_type_name+" ("+node.name+"): Neither possible attribute fields, nor possible relations defined for this node\n"
                return

            gst_possible_attributes_dict = node.get_possible_attributes(gsystem_type_id)
            gst_possible_relations_dict = node.get_possible_relations(gsystem_type_id)

            # Write code for setting atrributes / relations

    except Exception as e:
        print str(e)

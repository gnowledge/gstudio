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
from gnowsys_ndf.ndf.models import Node, GSystemType, AttributeType, RelationType



####################################################################################################################

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files" )

collection = get_database()[Node.collection_name]
is_json_file_exists = False
user_id = 1  # Very first user (considering superuser/admin)


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
                    # Process json file and create required SystemTypes, RelationTypes, and AttributeTypes
                    print "\n Do processing json file task..."

                    create_type(file_path)
                    
                    # End of processing json file

                print "\n Done everything...\n"

                # End of creation of respective Types for Enrollment

            else:
                print "\n FileNotFound: Following path (", file_path, ") doesn't exists!!!\n"

        # --- End of handle() ---

# -----------------------------------------------------------------------------------------------------------------
# Function that process json data according to the structure field
# -----------------------------------------------------------------------------------------------------------------

def create_type(json_file_path):
    """Depending upon file name, calls respective function
    to create types and pass processed data to it
    """

    types_not_created = []

    json_file_content = ""

    with open(json_file_path) as json_file:
        json_file_content = json_file.read()

    json_documents_list = json.loads(json_file_content)

    if "ST" in json_file_path:
        for json_document in json_documents_list:
            print "\n Creating GSystemType(", json_document['name'], ") ..."

            # Process data in proper format
            json_document['name'] = unicode(json_document['name'])

            try:
                perform_eval_type("type_of", json_document, "GSystemType", "GSystemType")
                perform_eval_type("member_of", json_document, "GSystemType", "MetaType")
                perform_eval_type("collection_set", json_document, "GSystemType", "GSystemType")
            except Exception as e:
                print e
                return

            create_edit_type("GSystemType", json_document, user_id)
        
    elif "AT" in json_file_path:
        for json_document in json_documents_list:
            print "\n Creating AttributeType(", json_document['name'], ") ..."

            # Process data in proper format
            json_document['name'] = unicode(json_document['name'])
            json_document['altnames'] = unicode(json_document['altnames'])
            
            if not json_document['required'].istitle():
                json_document['required'] = ast.literal_eval(json_document['required'].title())
            if json_document['required'] not in [True, False]:
                error_message = "\n InvalidDataError: For AttributeType (" + json_document['name'] + ") invalid data found in \"required\" field !!!"
                print error_message
                return

            if json_document['data_type'] not in DATA_TYPE_CHOICES:
                error_message = "\n InvalidDataTypeError: For AttributeType (" + json_document['name'] + ") invalid data-type found!!!"
                error_message += "\n Must be one of the following: ", DATA_TYPE_CHOICES
                print error_message
                return

            try:
                perform_eval_type("complex_data_type", json_document, "AttributeType", "AttributeType")
                perform_eval_type("subject_type", json_document, "AttributeType", "GSystemType")
            except Exception as e:
                print e
                return

            create_edit_type("AttributeType", json_document, user_id)
        
    elif "RT" in json_file_path:
        for json_document in json_documents_list:
            print "\n Creating RelationType(", json_document['name'], ") ..."

            # Process data in proper format
            json_document['name'] = unicode(json_document['name'])
            json_document['inverse_name'] = unicode(json_document['inverse_name'])

            try:
                perform_eval_type("subject_type", json_document, "RelationType", "GSystemType")
                perform_eval_type("object_type", json_document, "RelationType", "GSystemType")
            except Exception as e:
                print e
                return

            create_edit_type("RelationType", json_document, user_id)


def perform_eval_type(eval_field, json_document, type_to_create, type_convert_objectid):
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
        if eval_field == "complex_data_type" and [(data in DATA_TYPE_CHOICES) or (json_document['data_type'] == "IS()")]:
            type_list.append(unicode(data))

        else:
            node = collection.Node.one({'_type': type_convert_objectid, 'name': data}, {'_id': 1})
        
            if node:
                type_list.append(node._id)
            else:
                if eval_field == "complex_data_type":
                    type_convert_objectid = "Sub-" + type_convert_objectid

                error_message = "\n "+type_convert_objectid+"Error ("+eval_field+"): This "+type_convert_objectid+" (" + data + ") doesn't exists for creating "+type_to_create+" (" + json_document['name'] + ") !!!\n"
                raise Exception(error_message)

    # Sets python-type converted list
    json_document[eval_field] = type_list


# -----------------------------------------------------------------------------------------------------------------
# Create/Edit Function Defined for creating GSystemTypes, AttributeTypes, RelationTypes
# -----------------------------------------------------------------------------------------------------------------

def create_edit_type(type_name, json_document, user_id):
    """Creates factory Types' (including GSystemType, AttributeType, RelationType)
    """

    node = collection.Node.one({'_type': type_name, 'name': json_document['name']})
    if node is None:
        try:
            node = eval("collection"+"."+type_name)()
            
            for key in json_document.iterkeys():
                node[key] = json_document[key]

            node.created_by = user_id
            node.modified_by = user_id
            if user_id not in node.contributors:
                node.contributors.append(user_id)

            node.status = u"PUBLISHED"

            node.save()
            print "\n "+type_name+" (", node.name, ") created successfully."

        except Exception as e:
            print "\n "+type_name+"Error: Failed to create (", node.name, ") as ", e
            
    else:
        is_node_changed = False

        for key in json_document.iterkeys():
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
            print "\n "+type_name+" (", node.name, ") updated successfully."

        else:
            print "\n "+type_name+" (", node.name, ") already exists (Nothing updated) !!!"


'''
def create_edit_gsystem_type(json_document, user_id):
    """Creates factory GSystemTypes'
    """

    node = collection.Node.one({'_type': u"GSystemType", 'name': json_document['name']})
    if node is None:
        try:
            node = collection.GSystemType()
            
            for key in json_document.iterkeys():
                node[key] = json_document[key]

            node.created_by = user_id
            node.modified_by = user_id
            if user_id not in node.contributors:
                node.contributors.append(user_id)

            node.status = u"PUBLISHED"

            node.save()
            print "\n GSystemType (", node.name, ") created successfully."

        except Exception as e:
            print "\n GSystemTypeError: Failed to create (", node.name, ") as ", e
            
    else:
        is_node_changed = False

        for key in json_document.iterkeys():
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

        if is_node_updated:
            node.modified_by = user_id
            if user_id not in node.contributors:
                node.contributors.append(user_id)

            node.status = u"PUBLISHED"

            node.save()
            print "\n GSystemType (", node.name, ") updated successfully."

        else:
            print "\n GSystemType (", node.name, ") already exists (Nothing updated) !!!"


def create_edit_attribute_type(json_document, user_id):
    """Creates factory AttributeTypes'
    """

    node = collection.Node.one({'_type': u"AttributeType", 'name': json_document['name']})
    if node is None:
        try:
            node = collection.AttributeType()
            
            for key in json_document.iterkeys():
                node[key] = json_document[key]

            node.created_by = user_id
            node.modified_by = user_id
            if user_id not in node.contributors:
                node.contributors.append(user_id)

            node.status = u"PUBLISHED"

            node.save()
            print "\n AttributeType (", node.name, ") created successfully."

        except Exception as e:
            print "\n AttributeTypeError: Failed to create (", node.name, ") as ", e

    else:
        print "\n AttributeType (", node.name, ") already exists!"


def create_edit_relation_type(json_document, user_id):
    """Creates factory RelationTypes'
    """

    node = collection.Node.one({'_type': u"RelationType", 'name': json_document['name']})
    if node is None:
        try:
            node = collection.RelationType()

            for key in json_document.iterkeys():
                node[key] = json_document[key]

            node.created_by = user_id
            node.modified_by = user_id
            if user_id not in node.contributors:
                node.contributors.append(user_id)

            node.status = u"PUBLISHED"

            node.save()
            print "\n RelationType (", node.name, ") created successfully."

        except Exception as e:
            print "\n RelationTypeError: Failed to create (", node.name, ") as ", e

    else:
        print "\n RelationType (", node.name, ") already exists!"
'''


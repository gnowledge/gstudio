''' -- imports from python libraries -- '''
import os
import csv
import json
import ast
# import mimetypes

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

log_list = [] # To hold intermediate errors

collection = get_database()[Node.collection_name]
is_json_file_exists = False
user_id = 1  # Very first user (considering superuser/admin)

class Command(BaseCommand):
    help = "Based on "

    def handle(self, *args, **options):
    	try:
            for file_name in args:
                file_path = os.path.join(SCHEMA_ROOT, file_name)

                if os.path.exists(file_path):
                    # if not ("ST" in file_path or "AT" in file_path or "RT" in file_path):
                    if file_name not in ["STs.csv", "STs.json", "ATs.csv", "ATs.json", "RTs.csv", "RTs.json"]:
                        error_message = "\n InvalidSchemaFile ("+file_path+") : Please select a valid file for creating schema !!!\n"
                        log_list.append(error_message)
                        raise Exception(error_message)

	                # file_extension = mimetypes.guess_type(file_name)[0]
                    file_extension = os.path.splitext(file_name)[1]

                    if "csv" in file_extension:
                        # Process csv file and convert it to json format at first
                        info_message = "\n CSVType: Follwoing file (" + file_path + ") found !"
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
                                info_message = "\n JSONType: Following file (" + json_file_path + ") created successfully."
                                log_list.append(info_message)

                        except Exception as e:
                            error_message = "\n CSV-JSONError: " + str(e)
                            log_list.append(error_message)
	                
                        # End of csv-json coversion

                    elif "json" in file_extension:
                        is_json_file_exists = True

                    else:
                        error_message = "\n FileTypeError: Please choose either 'csv' or 'json' format supported files !!!\n"
                        log_list.append(error_message)
                        raise Exception(error_message)

                    if is_json_file_exists:
                        # Process json file and create required SystemTypes, RelationTypes, and AttributeTypes
                        info_message = "\n Task initiated: Processing json-file...\n"
                        log_list.append(info_message)

                        parse_data_create_gtype(file_path)
	                
                        # End of processing json file

                        info_message = "\n Task finised: Successfully processed json-file.\n"
                        log_list.append(info_message)

                    # End of creation of respective Types for Enrollment

                else:
                    error_message = "\n FileNotFound: Following path (" + file_path + ") doesn't exists!!!\n"
                    log_list.append(error_message)
                    raise Exception(error_message)

        except Exception as e:
            error_message = str(e)
            print "\n >>> >>>> >>>>>\n " + error_message
                            
        finally:
            if log_list:

                log_list.append("\n ============================================================ End of Iteration ============================================================\n")

                log_file_name = os.path.splitext(file_name)[0] + ".log"
                log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)

                with open(log_file_path, 'a') as log_file:
                    log_file.writelines(log_list)
        # --- End of handle() ---

# -----------------------------------------------------------------------------------------------------------------
# Function that process json data according to the structure field
# -----------------------------------------------------------------------------------------------------------------

def parse_data_create_gtype(json_file_path):
    """Depending upon file name, processes data and passes it along
    with necessary information to create respective GTypes
    """

    json_file_content = ""

    with open(json_file_path) as json_file:
        json_file_content = json_file.read()

    json_documents_list = json.loads(json_file_content)

    if "ST" in json_file_path:
    	type_name = "GSystemType"

        for json_document in json_documents_list:
            # Process data in proper format
            try:
                json_document['name'] = unicode(json_document['name'])
                
                perform_eval_type("type_of", json_document, type_name, "GSystemType")
                perform_eval_type("member_of", json_document, type_name, "MetaType")
                perform_eval_type("attribute_type_set", json_document, type_name, "AttributeType")
                perform_eval_type("relation_type_set", json_document, type_name, "RelationType")
                perform_eval_type("collection_set", json_document, type_name, "GSystemType")

            except Exception as e:
            	error_message = "\n While parsing "+type_name+"(" + json_document['name'] + ") got following error...\n " + str(e)
            	log_list.append(error_message)
            	print error_message # Keep it!
            	# continue

            try:
                info_message = "\n Creating "+type_name+"(" + json_document['name'] + ") ..."
                log_list.append(info_message)
                create_edit_type(type_name, json_document, user_id)

            except Exception as e:
                error_message = "\n While creating "+type_name+" ("+json_document['name']+") got following error...\n " + str(e)
                log_list.append(error_message)
                print error_message # Keep it!

    elif "AT" in json_file_path:
    	type_name = "AttributeType"

        for json_document in json_documents_list:
            # Process data in proper format
            try:
                json_document['name'] = unicode(json_document['name'])
                json_document['altnames'] = unicode(json_document['altnames'])
	            
                if not json_document['required'].istitle():
                    json_document['required'] = ast.literal_eval(json_document['required'].title())

                if json_document['required'] not in [True, False]:
                    error_message = "\n InvalidDataError: For "+type_name+" (" + json_document['name'] + ") invalid data found in \"required\" field !!!"
                    log_list.append(error_message)
                    raise Exception(error_message)

                if json_document['data_type'] not in DATA_TYPE_CHOICES:
                    error_message = "\n InvalidDataTypeError: For "+type_name+" (" + json_document['name'] + ") invalid data-type found!!!"
                    error_message += "\n Must be one of the following: " + DATA_TYPE_CHOICES
                    log_list.append(error_message)
                    raise Exception(error_message)

                perform_eval_type("complex_data_type", json_document, type_name, "AttributeType")
                perform_eval_type("subject_type", json_document, type_name, "GSystemType")

            except Exception as e:
            	error_message = "\n While parsing "+type_name+"(" + json_document['name'] + ") got following error...\n " + str(e)
            	log_list.append(error_message)
            	print error_message # Keep it!
            	# continue

            try:
                info_message = "\n Creating "+type_name+"(" + json_document['name'] + ") ..."
                log_list.append(info_message)
                create_edit_type(type_name, json_document, user_id)

            except Exception as e:
                error_message = "\n While creating "+type_name+" ("+json_document['name']+") got following error...\n " + str(e)
                log_list.append(error_message)
                print error_message # Keep it!

        
    elif "RT" in json_file_path:
    	type_name = "RelationType"

        for json_document in json_documents_list:
            # Process data in proper format
            try:
                json_document['name'] = unicode(json_document['name'])
                json_document['inverse_name'] = unicode(json_document['inverse_name'])

                perform_eval_type("subject_type", json_document, type_name, "GSystemType")
                perform_eval_type("object_type", json_document, type_name, "GSystemType")

            except Exception as e:
            	error_message = "\n While parsing "+type_name+"(" + json_document['name'] + ") got following error...\n " + str(e)
            	log_list.append(error_message)
            	print error_message # Keep it!
            	# continue

            try:
                info_message = "\n Creating "+type_name+"(" + json_document['name'] + ") ..."
                log_list.append(info_message)
                create_edit_type(type_name, json_document, user_id)

            except Exception as e:
                error_message = "\n While creating "+type_name+" ("+json_document['name']+") got following error...\n " + str(e)
                log_list.append(error_message)
                print error_message # Keep it!

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
            error_message = " InvalidDataError: For " + type_to_create + " (" + json_document['name'] + ") invalid data found -- " + str(e) + "!!!\n"
            raise Exception(error_message)


    type_list = []
    for data in json_document[eval_field]:
        if (eval_field == "complex_data_type") and ((data in DATA_TYPE_CHOICES) or (json_document['data_type'] == "IS()")):
            type_list.append(unicode(data))

        else:
            node = collection.Node.one({'_type': type_convert_objectid, 'name': data})
        
            if node:
                if eval_field == "complex_data_type":
                    type_list.append(unicode(node._id))
                elif eval_field in ["attribute_type_set", "relation_type_set"]:
                    type_list.append(node)
                else:
                    type_list.append(node._id)

            else:
                if eval_field == "complex_data_type":
                    type_convert_objectid = "Sub-" + type_convert_objectid

                elif eval_field in ["attribute_type_set", "relation_type_set"]:
                	json_document[eval_field] = type_list
               		error_message = "\n "+type_convert_objectid+"Error ("+eval_field+"): This "+type_convert_objectid+" (" + data + ") doesn't exists for creating "+type_to_create+" (" + json_document['name'] + ") !!!\n"
               		log_list.append(error_message)
               		continue

                error_message = "\n "+type_convert_objectid+"Error ("+eval_field+"): This "+type_convert_objectid+" (" + data + ") doesn't exists for creating "+type_to_create+" (" + json_document['name'] + ") !!!\n"
                log_list.append(error_message)
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
            info_message = "\n "+type_name+" ("+node.name+") created successfully." + "\n"
            log_list.append(info_message)

        except Exception as e:
            error_message = "\n "+type_name+"Error: Failed to create ("+node.name+") as " + str(e) + "\n"
            log_list.append(error_message)
            raise Exception(error_message)
            
    else:
        is_node_changed = False

        try:
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
                info_message = "\n "+type_name+" ("+node.name+") updated successfully." + "\n"
                log_list.append(info_message)

            else:
                info_message = "\n "+type_name+" ("+node.name+") already exists (Nothing updated) !" + "\n"
                log_list.append(info_message)

        except Exception as e:
            error_message = "\n "+type_name+"Error: Failed to update ("+node.name+") as " + str(e) + "\n"
            log_list.append(error_message)
            raise Exception(error_message)

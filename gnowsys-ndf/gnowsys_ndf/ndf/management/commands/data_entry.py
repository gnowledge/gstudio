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

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files" )

collection = get_database()[Node.collection_name]
is_json_file_exists = False
mis_group = collection.Node.one({'_type': "Group", 
                                 '$or': [{'name': {'$regex': u"MIS_admin", '$options': 'i'}}, 
                                         {'altnames': {'$regex': u"MIS_admin", '$options': 'i'}}],
                                 'group_type': "PRIVATE"
                                }, 
                                {'created_by': 1}
                            )
group_id = mis_group._id
user_id = mis_group.created_by  # User who created the above private group

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
    gsystem_type_node = None
    gsystem_type_id = None
    gsystem_type_name = ""
    try:
        with open(json_file_path) as json_file:
            json_file_content = json_file.read()

        json_documents_list = json.loads(json_file_content)

        gsystem_type_name = os.path.basename(json_file_path)
        gsystem_type_name = gsystem_type_name.rstrip(".json")
        gsystem_type_name = gsystem_type_name.replace("_", " ")
        # print "\n gsystem_type_name: ", gsystem_type_name

        gsystem_type_node = collection.Node.one({'_type': "GSystemType", 
                                                 '$or': [{'name': {'$regex': "^"+gsystem_type_name+"$", '$options': 'i'}}, 
                                                         {'altnames': {'$regex': "^"+gsystem_type_name+"$", '$options': 'i'}}]
                                             })
        if gsystem_type_node:
            # print "\n ", gsystem_type_node.name, 
            gsystem_type_id = gsystem_type_node._id
            # print " -- ", gsystem_type_id
        else:
            error_message = "\n GSystemTypeError: This GSystemType ("+gsystem_type_name+") doesn't exists for creating it's own GSystem !!!"
            raise Exception(error_message)

        # Process data in proper format
        node = collection.GSystem()
        node_keys = node.keys()
        node_structure = node.structure

        # for json_document in json_documents_list:
        #     print "\n\n before", json_document

        json_documents_list_spaces = json_documents_list
        json_documents_list = []
        # Removes leading and trailing spaces from keys as well as values
        for json_document_spaces in json_documents_list_spaces:
            json_document = {}

            for key_spaces, value_spaces in json_document_spaces.iteritems():
                json_document[key_spaces.strip().lower()] = value_spaces.strip()

            json_documents_list.append(json_document)

        # for json_document in json_documents_list:
        #     print "\n\n after", json_document

    except Exception as e:
        print "\n While parsing the file ("+json_file_path+") got following error...\n " + str(e)

    '''
    for json_document in json_documents_list:
        if json_document.has_key("first name"):
            n_name = json_document["first name"] + " "
            if json_document["middle name"]:
                n_name += json_document["middle name"] + " "
            n_name += json_document["last name"]
            json_document["name"] = n_name
        print "\n json_document: ", json_document
        print "\n name: ", json_document['name']
    '''

    for json_document in json_documents_list:
        try:
            n_name = ""
            if json_document.has_key("first name"):
                n_name = json_document["first name"] + " "
                if json_document["middle name"]:
                    n_name += json_document["middle name"] + " "
                n_name += json_document["last name"]
                json_document["name"] = n_name

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

            print "\n Creating "+gsystem_type_name+" ("+parsed_json_document["name"]+")...\n"
            node = create_edit_gsystem(gsystem_type_id, gsystem_type_name, parsed_json_document, user_id)

            if node:
                if not attribute_relation_list:
                    # Neither possible attribute fields, nor possible relations defined for this node
                    print "\n "+gsystem_type_name+" ("+node.name+"): Neither possible attribute fields, nor possible relations defined for this node !!!\n"
                    continue

                gst_possible_attributes_dict = node.get_possible_attributes(gsystem_type_id)
                # print "\n gst_possible_attributes_dict: ", gst_possible_attributes_dict

                relation_list = []
                json_document['name'] = node.name

                # Write code for setting atrributes
                for key in attribute_relation_list:
                    is_relation = True

                    for attr_key, attr_value in gst_possible_attributes_dict.iteritems():
                        # print "\n ", key, " -- (attr_key: "+attr_key+") -- (atlnm"+attr_value['altnames']+")" 
                        if key == attr_value['altnames'].lower() or key == attr_key.lower():
                            is_relation = False

                            #print "\n For GAttribute parsing content ", key," -- ", (type(attr_value['data_type']) == IS), " -- ", json_document[key], "\n"
                            if json_document[key]:
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
                                    if key == "dob":
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
                                    # print "\n ************** ", key, " -- ", json_document[key]
                                    # print "\n attr_value['data_type']: ", attr_value['data_type']._operands
                                    for op in attr_value['data_type']._operands:
                                        if op.lower() == json_document[key].lower():
                                            json_document[key] = op

                                elif (attr_value['data_type'] in [list, dict]) or (type(attr_value['data_type']) in [list, dict]):
                                    if "," not in json_document[key]:
                                        # Necessary to inform perform_eval_type() that handle this value as list
                                        json_document[key] = "\"" + json_document[key] + "\", "

                                        perform_eval_type(key, json_document, "GSystem")

                                subject_id = node._id
                                attribute_type_node = collection.Node.one({'_type': "AttributeType", 
                                                                           '$or': [{'name': {'$regex': "^"+attr_key+"$", '$options': 'i'}}, 
                                                                                   {'altnames': {'$regex': "^"+attr_key+"$", '$options': 'i'}}]
                                                                       })
                                object_value = json_document[key]
                                ga_node = None
                                print "\n Creating GAttribute ("+node.name+" -- "+attribute_type_node.name+" -- "+str(json_document[key])+") ...\n"
                                ga_node = create_gattribute(subject_id, attribute_type_node, object_value)

                                # To break outer for loop as key found
                                break

                            else:
                                error_message = "\n DataNotFound: No data found for field ("+attr_key+") while creating GSystem ("+gsystem_type_name+" -- "+node.name+") !!!\n"
                                print error_message
                                # raise Exception(error_message)

                    if is_relation:
                        relation_list.append(key)

                if not relation_list:
                    # No possible relations defined for this node
                    print "\n "+gsystem_type_name+" ("+node.name+"): No possible relations defined for this node !!!\n"
                    return

                gst_possible_relations_dict = node.get_possible_relations(gsystem_type_id)
                # print "\n gst_possible_relations_dict: ", gst_possible_relations_dict

                # print "\n relation_list: ", relation_list, "\n"

                # Write code for setting relations
                for key in relation_list:
                    is_relation = True

                    for rel_key, rel_value in gst_possible_relations_dict.iteritems():
                        # print "\n ", key, " == ", rel_value['altnames'], " -- ", rel_key, "\n"
                        # print "\n check: ", key in rel_value['altnames'], "\n"

                        # if key in rel_value['altnames']:
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

                                # print "\n For GRelation parsing content ", key," -- ", json_document[key], "\n"
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
                                    # print "\n subject_id: ", subject_id, " -- ", node.name,"\n"
                                    # print "\n relation_type_node: \n", relation_type_node, "\n"
                                    # print "\n right_subject_id: ", right_subject_id, "\n"
                                    print "\n Creating GRelation ("+node.name+" -- "+rel_key+" -- "+str(right_subject_id)+") ...\n"
                                    gr_node = create_grelation(subject_id, relation_type_node, right_subject_id)

                                # To break outer for loop as key found
                                break

                            else:
                                error_message = "\n DataNotFound: No data found for relation ("+rel_key+") while creating GSystem ("+gsystem_type_name+" -- "+node.name+") !!!\n"
                                print error_message
                                # raise Exception(error_message)

                                break

        except Exception as e:
            print "\n While creating "+gsystem_type_name+"'s GSystem ("+json_document['name']+") got following error...\n " + str(e)
            

def create_edit_gsystem(gsystem_type_id, gsystem_type_name, json_document, user_id):
    """Creates/Updates respective GSystem and it's related GAttribute(s)
    and GRelation(s)
    """
    node = None

    # if json_document.has_key("First Name"):
    #     n_name = json_document["First Name"] + " "
    #     if json_document["Middle Name"]:
    #         n_name += json_document["Middle Name"] + " "
    #     n_name += json_document["Last Name"]
    #     n_name = unicode(n_name)
    #     node = collection.Node.one({'_type': "GSystem", 'name': n_name})
    # else:
    #     node = collection.Node.one({'_type': "GSystem", 'name': unicode(json_document['name'])})

    node = collection.Node.one({'_type': "GSystem", 
                                '$or': [{'name': {'$regex': "^"+json_document['name']+"$", '$options': 'i'}}, 
                                        {'altnames': {'$regex': "^"+json_document['name']+"$", '$options': 'i'}}]
                            })

    if node is None:
        try:
            node = collection.GSystem()

            # Save Node first with it's basic attribute fields
            for key in json_document.keys():
                if node.has_key(key):
                    node[key] = json_document[key]

            # if not node.name:
            #     if json_document.has_key("First Name"):
            #         node.name = json_document["First Name"] + " "
            #         if json_document["Middle Name"]:
            #             node.name += json_document["Middle Name"] + " "
            #         node.name += json_document["Last Name"]
            #         node.name = unicode(n_name)
            #     else:
            #         node.name = unicode("Instance of " + gsystem_type_name)

            node.created_by = user_id
            node.modified_by = user_id
            if user_id not in node.contributors:
                node.contributors.append(user_id)

            node.member_of.append(gsystem_type_id)
            node.group_set.append(group_id)
            node.status = u"PUBLISHED"

            node.save()
            print "\n "+gsystem_type_name+" ("+node.name+") created successfully.\n"

        except Exception as e:
            error_message = "\n "+gsystem_type_name+"Error: Failed to create ("+json_document['name']+") as " + str(e) + "\n"
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
                print "\n "+gsystem_type_name+" ("+node.name+") updated successfully.\n"

            else:
                print "\n "+gsystem_type_name+" ("+node.name+") already exists (Nothing updated) !\n"

        except Exception as e:
            error_message = "\n "+gsystem_type_name+"Error: Failed to update ("+node.name+") as " + str(e) + "\n"
            raise Exception(error_message)

    return node


def perform_eval_type(eval_field, json_document, type_to_create, type_convert_objectid=None):
    """Converts eval_field's data in json-type to it's corresponding python-type, and
    resets eval_field with that converted data
    """

    try:
        # print "\n ", eval_field, " -- ", json_document[eval_field], " === ", type(json_document[eval_field])
        json_document[eval_field] = ast.literal_eval(json_document[eval_field])

    except Exception as e:
        if u"\u201c" in json_document[eval_field]:
            json_document[eval_field] = json_document[eval_field].replace(u"\u201c", "\"")
            
        if u"\u201d" in json_document[eval_field]:
            json_document[eval_field] = json_document[eval_field].replace(u"\u201d", "\"")

        try:
            json_document[eval_field] = ast.literal_eval(json_document[eval_field])
        except Exception as e:
            error_message = "\n InvalidDataError: For " + type_to_create + " ("+json_document['name']+") invalid data found -- " + str(e) + "!!!\n"
            raise Exception(error_message)


    type_list = []
    for data in json_document[eval_field]:
        # if (eval_field == "complex_data_type") and ((data in DATA_TYPE_CHOICES) or (json_document['data_type'] == "IS()")):
        #     type_list.append(unicode(data))
        if type_convert_objectid is None:
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
                raise Exception(error_message)

    # Sets python-type converted list
    json_document[eval_field] = type_list
    # print "\n after == ", json_document[eval_field], "\n"


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
            print "\n GAttribute ("+ga_node.name+") created successfully.\n"

        except Exception as e:
            error_message = "\n GAttributeCreateError: " + str(e) + "\n"
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
                print "\n GAttribute ("+ga_node.name+") updated successfully.\n"

            else:
                print "\n GAttribute ("+ga_node.name+") already exists (Nothing updated) !\n"

        except Exception as e:
            error_message = "\n GAttributeUpdateError: " + str(e) + "\n"
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
            # print "\n subject_id: ", gr_node.subject, "\n"
            # print "\n relation_type_node: \n", gr_node.relation_type, "\n"
            # print "\n object_value: ", gr_node.right_subject, "\n"

            gr_node.status = u"PUBLISHED"
            
            gr_node.save()
            print "\n GRelation ("+gr_node.name+") created successfully.\n"

        except Exception as e:
            error_message = "\n GRelationCreateError: " + str(e) + "\n"
            raise Exception(error_message)

    else:
        print "\n GRelation ("+gr_node.name+") already exists !\n"

    return gr_node

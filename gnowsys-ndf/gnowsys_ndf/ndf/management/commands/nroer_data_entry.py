''' -- imports from python libraries -- '''
import os
import csv
import json
import ast
import datetime
import urllib2

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

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
from gnowsys_ndf.ndf.views.file import save_file

####################################################################################################################

# TODO: 
# 1) Name of attributes/relation in property_order field needs to be replaced with their respective ObjectIds
# 2) regex query needs to be modified because in current situation it's not considering names with space 
#    - searching for terms till it finds first space

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files" )

collection = get_database()[Node.collection_name]
file_gst = collection.GSystemType.one({"name": "File"})
home_group = collection.Group.one({"name": "home", "_type":"Group"})

class Command(BaseCommand):
    help = "\n\tFor saving data in gstudio DB from NROER schema files. This will create 'File' type GSystem instances.\n\tCSV file condition: The first row should contain DB names.\n"

    def handle(self, *args, **options):
        try:
        	# print "working........" + SCHEMA_ROOT

			for file_name in args:
				file_path = os.path.join(SCHEMA_ROOT, file_name)

				if os.path.exists(file_path):

				    file_extension = os.path.splitext(file_name)[1]

				    if "csv" in file_extension:

				        # Process csv file and convert it to json format at first
				        info_message = "\n CSVType: Following file (" + file_path + ") found!!!"
				        print info_message
									    
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
				                print info_message

				        except Exception as e:
				            error_message = "\n CSV-JSONError: " + str(e)
				            print error_message
				        # End of csv-json coversion

				    elif "json" in file_extension:
				        is_json_file_exists = True

				    else:
				        error_message = "\n FileTypeError: Please choose either 'csv' or 'json' format supported files!!!\n"
				        print error_message
				        raise Exception(error_mesage)

				    if is_json_file_exists:
				        # Process json file and create required GSystems, GRelations, and GAttributes
				        info_message = "\n Task initiated: Processing json-file...\n"
				        print info_message

				        parse_data_create_gsystem(file_path)
				    
				        # End of processing json file

				        info_message = "\n Task finised: Successfully processed json-file.\n"
				        print info_message
				        # End of creation of respective GSystems, GAttributes and GRelations for Enrollment

				else:
				    error_message = "\n FileNotFound: Following path (" + file_path + ") doesn't exists!!!\n"
				    print error_message
				    raise Exception(error_message)


        except Exception as e:
        	print str(e)


def get_user_id(user_name):
  try:
    user_obj = User.objects.get(username=user_name)
    return int(user_obj.id)
  except Exception as e:
    print e, "for username: ", user_name 
    return False


def parse_data_create_gsystem(json_file_path):
    json_file_content = ""

    try:
        with open(json_file_path) as json_file:
          json_file_content = json_file.read()

        json_documents_list = json.loads(json_file_content)

        # Process data in proper format
        node = collection.File()
        node_keys = node.keys()
        node_structure = node.structure
        # print "\n\n---------------", node_keys

        # for index, strtype in node_structure.items():
        #   if type(strtype) == type:
        #     strtype = strtype.__name__
        #   else:
        #     strtype = strtype.__str__()
        #     # print "~~~~" + strtype

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
        raise error_message

    for i, json_document in enumerate(json_documents_list):
        try:

          parsed_json_document = {}
          node_field_json = {}
          attribute_relation_list = []
          
          for key in json_document.iterkeys():
            parsed_key = key.lower()
            # print parsed_key
            # parsed_key = parsed_key.replace(" ", "_")
            
            if parsed_key in node_keys:
              # print "~~~~" + key

              # adding the default field values e.g: created_by, member_of
              
              # created_by
              if parsed_key == "created_by":
                if json_document[key]:
                  temp_user_id = get_user_id(json_document[key].strip())
                  if temp_user_id:
                    parsed_json_document[parsed_key] = temp_user_id
                else:
                  parsed_json_document[parsed_key] = get_user_id("nroer_team")
                # print "---", parsed_json_document[parsed_key]
              # contributors
              elif parsed_key == "contributors":
                if json_document[key]:
                  contrib_list = json_document[key].split(",")

                  temp_contributors = []
                  for each_user in contrib_list:
                    user_id = get_user_id(each_user.strip())
                    if user_id:
                      temp_contributors.append(user_id)
                  parsed_json_document[parsed_key] = temp_contributors
                  # print "===", parsed_json_document[parsed_key]
              # tags
              elif (parsed_key == "tags") and json_document[key]:
                tag_list = json_document[key].replace("\n", "").split(",")
                temp_tag_list = []
                for each_tag in tag_list:
                  if each_tag:
                    temp_tag_list.append(each_tag.strip())
                parsed_json_document[parsed_key] = temp_tag_list
                # print parsed_json_document[parsed_key]
              #member_of
              elif parsed_key == "member_of":
                parsed_json_document[parsed_key] = [file_gst._id]
                # print parsed_json_document[parsed_key]

              # --- END of addind the default field values


              if node_structure[parsed_key] == unicode:
                parsed_json_document[parsed_key] = unicode(json_document[key])
              elif node_structure[parsed_key] == basestring:
                parsed_json_document[parsed_key] = str(json_document[key])
              elif (node_structure[parsed_key] == int) and (type(json_document[key]) == int):
                parsed_json_document[parsed_key] = int(json_document[key])
              elif node_structure[parsed_key] == bool: # converting unicode to int and then to bool
                parsed_json_document[parsed_key] = bool(int(json_document[key]))
              elif node_structure[parsed_key] == datetime.datetime:
                parsed_json_document[parsed_key] = datetime.datetime.strptime(json_document[key], "%d/%m/%Y")
              else:
                parsed_json_document[parsed_key] = json_document[key]

                    # creating file gst instance and feeding the values
               # file_obj = collection.File()

            else:
              parsed_json_document[key] = json_document[key]
              attribute_relation_list.append(key)
            
            # print "\n----------\n", parsed_key , "\t" , parsed_json_document[parsed_key]
              # print "\n\n-----======-\n", attribute_relation_list
              
              # print "\n\n",parsed_json_document#.get(name)
          node = create_resource_gsystem(parsed_json_document)
              
              # if node:
              #     if not attribute_relation_list:
              #         # Neither possible attribute fields, nor possible relations defined for this node
              #         info_message = "\n "+gsystem_type_name+" ("+node.name+"): Neither possible attribute fields, nor possible relations defined for this node !\n"
              #         log_list.append(info_message)
              #         continue
              
              #     gst_possible_attributes_dict = node.get_possible_attributes(gsystem_type_id)
              
              #     relation_list = []
              #     json_document['name'] = node.name
              
              #     # Write code for setting atrributes
              #     for key in attribute_relation_list:
              #         is_relation = True
              
              #         for attr_key, attr_value in gst_possible_attributes_dict.iteritems():
              #             if key == attr_value['altnames'].lower() or key == attr_key.lower():
              #                 is_relation = False
            
              #                 if json_document[key]:
              #                     if attr_value['data_type'] == basestring:
              #                         if u"\u2013" in json_document[key]:
              #                             json_document[key] = json_document[key].replace(u"\u2013", "-")
              
              #                     info_message = "\n For GAttribute parsing content | key: " + attr_key + " -- " + json_document[key]
              #                     log_list.append(info_message)
              
              
              #                     if attr_value['data_type'] == unicode:
              #                         json_document[key] = unicode(json_document[key])
              
              #                     elif attr_value['data_type'] == bool: 
              #                         if json_document[key].lower() == "yes":
              #                             json_document[key] = True
              #                         elif json_document[key].lower() == "no":
              #                             json_document[key] = False
              #                         else:
              #                             json_document[key] = None
              
              #                     elif attr_value['data_type'] == datetime.datetime:
              
              #                         if key == "dob" or key == "date of birth":
              #                             json_document[key] = datetime.datetime.strptime(json_document[key], "%d/%m/%Y")
              #                         else:
              #                             json_document[key] = datetime.datetime.strptime(json_document[key], "%Y")
              
              #                     elif attr_value['data_type'] in [int, float, long]:
              #                         if not json_document[key]:
              #                             json_document[key] = 0
              #                         else:
              #                             if attr_value['data_type'] == int:
              #                                 json_document[key] = int(json_document[key])
              #                             elif attr_value['data_type'] == float:
              #                                 json_document[key] = float(json_document[key])
              #                             else:
              #                                 json_document[key] = long(json_document[key])

              #                     elif type(attr_value['data_type']) == IS:
              #                         for op in attr_value['data_type']._operands:
              #                             if op.lower() == json_document[key].lower():
              #                                 json_document[key] = op
              
              #                     elif (attr_value['data_type'] in [list, dict]) or (type(attr_value['data_type']) in [list, dict]):
              #                         if "," not in json_document[key]:
              #                             # Necessary to inform perform_eval_type() that handle this value as list
              #                             json_document[key] = "\"" + json_document[key] + "\", "
              
              #                         else:
              #                             formatted_value = ""
              #                             for v in json_document[key].split(","):
              #                                 formatted_value += "\""+v.strip(" ")+"\", "
              #                             json_document[key] = formatted_value
              
              #                         perform_eval_type(key, json_document, "GSystem")
              
              #                     subject_id = node._id
              #                     attribute_type_node = collection.Node.one({'_type': "AttributeType", 
              #                                                                '$or': [{'name': {'$regex': "^"+attr_key+"$", '$options': 'i'}}, 
              #                                                                        {'altnames': {'$regex': "^"+attr_key+"$", '$options': 'i'}}]
              #                                                            })
              #                     object_value = json_document[key]
              
              #                     ga_node = None
              
              #                     info_message = "\n Creating GAttribute ("+node.name+" -- "+attribute_type_node.name+" -- "+str(json_document[key])+") ...\n"
              #                     log_list.append(info_message)
              #                     ga_node = create_gattribute(subject_id, attribute_type_node, object_value)
              
              #                     # To break outer for loop as key found
              #                     break
              
              #                 else:
              #                     error_message = "\n DataNotFound: No data found for field ("+attr_key+") while creating GSystem ("+gsystem_type_name+" -- "+node.name+") !!!\n"
              #                     log_list.append(error_message)
              
              #         if is_relation:
              #             relation_list.append(key)
              
              #     if not relation_list:
              #         # No possible relations defined for this node
              #         info_message = "\n "+gsystem_type_name+" ("+node.name+"): No possible relations defined for this node !!!\n"
              #         log_list.append(info_message)
              #         return
              
              #     gst_possible_relations_dict = node.get_possible_relations(gsystem_type_id)
              
              #     # Write code for setting relations
              #     for key in relation_list:
              #         is_relation = True
              
              #         for rel_key, rel_value in gst_possible_relations_dict.iteritems():
              #             if key == rel_value['altnames'].lower() or key == rel_key.lower():
              #                 is_relation = False
              
              #                 if json_document[key]:
              #                     # Here semi-colon(';') is used instead of comma(',')
              #                     # Beacuse one of the value may contain comma(',') which causes problem in finding required value in database
              #                     if ";" not in json_document[key]:
              #                         # Necessary to inform perform_eval_type() that handle this value as list
              #                         json_document[key] = "\""+json_document[key]+"\", "

            #                     else:
            #                         formatted_value = ""
            #                         for v in json_document[key].split(";"):
            #                             formatted_value += "\""+v.strip(" ")+"\", "
            #                         json_document[key] = formatted_value

            #                     info_message = "\n For GRelation parsing content | key: " + rel_key + " -- " + json_document[key]
            #                     log_list.append(info_message)

            #                     perform_eval_type(key, json_document, "GSystem", "GSystem")

            #                     for right_subject_id in json_document[key]:
            #                         subject_id = node._id

            #                         # Here we are appending list of ObjectIds of GSystemType's type_of field 
            #                         # along with the ObjectId of GSystemType's itself (whose GSystem is getting created)
            #                         # This is because some of the RelationType's are holding Base class's ObjectId
            #                         # and not that of the Derived one's
            #                         # Delibrately keeping GSystemType's ObjectId first in the list
            #                         # And hence, used $in operator in the query!
            #                         rel_subject_type = []
            #                         rel_subject_type.append(gsystem_type_id)
            #                         if gsystem_type_node.type_of:
            #                             rel_subject_type.extend(gsystem_type_node.type_of)

            #                         relation_type_node = collection.Node.one({'_type': "RelationType", 
            #                                                                   '$or': [{'name': {'$regex': "^"+rel_key+"$", '$options': 'i'}}, 
            #                                                                           {'altnames': {'$regex': "^"+rel_key+"$", '$options': 'i'}}],
            #                                                                   'subject_type': {'$in': rel_subject_type}
            #                                                           })

            #                         info_message = "\n Creating GRelation ("+node.name+" -- "+rel_key+" -- "+str(right_subject_id)+") ...\n"
            #                         log_list.append(info_message)
            #                         gr_node = create_grelation(subject_id, relation_type_node, right_subject_id)

            #                     # To break outer for loop if key found
            #                     break

            #                 else:
            #                     error_message = "\n DataNotFound: No data found for relation ("+rel_key+") while creating GSystem ("+gsystem_type_name+" -- "+node.name+") !!!\n"
            #                     log_list.append(error_message)
            #                     # print error_message

            #                     break


        except Exception as e:
            # error_message = "\n While creating "+gsystem_type_name+"'s GSystem ("+json_document['name']+") got following error...\n " + str(e)
            # print error_message # Keep it!
            print e


def create_resource_gsystem(resource_data):
  
  resource_link = resource_data.get("resource_link")
  # print "\n----------\n", resource_link
  files = urllib2.urlopen(resource_link)
  # print files.read(100)

  title = resource_data["name"]
  userid = resource_data["created_by"]
  group_id = home_group._id
  content_org = resource_data["content_org"]
  tags = resource_data["tags"]
  # img_type = resource_data[]
  language = resource_data["language"]
  # usrname = resource_data[]
  # page_url = resource_data[]
  access_policy = "PUBLIC"


  # for storing location in the file

  # location = []
  # location.append(json.loads(request.POST.get("location", "{}")))
  # obs_image = save_file(each,title,userid,group_id, content_org, tags, img_type, language, usrname, access_policy, oid=True, location=location)

  # obs_image = save_file(each,title,userid,group_id, content_org, tags, img_type, language, usrname, access_policy, oid=True)
  return ""
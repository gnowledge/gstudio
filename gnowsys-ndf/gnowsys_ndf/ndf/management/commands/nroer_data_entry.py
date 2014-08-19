''' -- imports from python libraries -- '''
import os
import csv
import json
import ast
import datetime
import urllib2
import hashlib
import magic  #for this install python-magic example:pip install python-magic
import subprocess
import mimetypes
from PIL import Image, ImageDraw, ImageFile #install PIL example:pip install PIL
from StringIO import StringIO
import os
import subprocess
import ox
import threading
import io
from django.http import Http404

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
from gnowsys_ndf.ndf.models import Node, File
from gnowsys_ndf.ndf.models import GSystemType, AttributeType, RelationType
from gnowsys_ndf.ndf.models import GSystem, GAttribute, GRelation
from gnowsys_ndf.ndf.management.commands.data_entry import create_grelation, create_gattribute
# from gnowsys_ndf.ndf.views.file import save_file, getFileSize
# from gnowsys_ndf.ndf.views.methods import create_gattribute

####################################################################################################################

# TODO: 
# 1) Name of attributes/relation in property_order field needs to be replaced with their respective ObjectIds
# 2) regex query needs to be modified because in current situation it's not considering names with space 
#    - searching for terms till it finds first space

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files" )

collection = get_database()[Node.collection_name]
file_gst = collection.GSystemType.one({"name": "File"})
home_group = collection.Group.one({"name": "home", "_type":"Group"})
theme_gst = collection.GSystemType.one({ "name": "Theme" })
theme_item_gst = collection.GSystemType.one({ "name": "theme_item" })
topic_gst = collection.GSystemType.one({ "name": "Topic" })

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
				        info_message = "\n- CSVType: Following file (" + file_path + ") found!!!"
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
				                info_message = "\n- JSONType: Following file (" + json_file_path + ") created successfully.\n"
				                print info_message

				        except Exception as e:
				            error_message = "\n!! CSV-JSONError: " + str(e)
				            print error_message
				        # End of csv-json coversion

				    elif "json" in file_extension:
				        is_json_file_exists = True

				    else:
				        error_message = "\n!! FileTypeError: Please choose either 'csv' or 'json' format supported files!!!\n"
				        print error_message
				        raise Exception(error_mesage)

				    if is_json_file_exists:
				        # Process json file and create required GSystems, GRelations, and GAttributes
				        info_message = "\n------- Task initiated: Processing json-file -------\n"
				        print info_message

				        parse_data_create_gsystem(file_path)
				    
				        # End of processing json file

				        info_message = "\n------- Task finised: Successfully processed json-file -------\n"
				        print info_message
				        # End of creation of respective GSystems, GAttributes and GRelations for Enrollment

				else:
				    error_message = "\n!! FileNotFound: Following path (" + file_path + ") doesn't exists!!!\n"
				    print error_message
				    raise Exception(error_message)


        except Exception as e:
        	print str(e)


def get_user_id(user_name):
  try:
    user_obj = User.objects.get(username=user_name)
    return int(user_obj.id)
  except Exception as e:
    print e, "\n!! for username: ", user_name 
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
        error_message = "\n!! While parsing the file ("+json_file_path+") got following error...\n " + str(e)
        raise error_message

    for i, json_document in enumerate(json_documents_list):
      
      print "\n\n********** Processing row number : [", i, "] **********"

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
                parsed_json_document[parsed_key] = get_user_id("nroer_team")
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
                parsed_json_document[parsed_key] = []
                # print "===", parsed_json_document[parsed_key]
            
            # tags:
            elif (parsed_key == "tags") and json_document[key]:
              tag_list = json_document[key].replace("\n", "").split(",")
              temp_tag_list = []
              for each_tag in tag_list:
                if each_tag:
                  temp_tag_list.append(each_tag.strip())
              parsed_json_document[parsed_key] = temp_tag_list
              # print parsed_json_document[parsed_key]
            
            #member_of:
            elif parsed_key == "member_of":
              parsed_json_document[parsed_key] = [file_gst._id]
              # print parsed_json_document[parsed_key]
            
            # --- END of adding the default field values


            # processing for remaining fields
            elif node_structure[parsed_key] == unicode:
              parsed_json_document[parsed_key] = unicode(json_document[key])
            elif node_structure[parsed_key] == basestring:
              parsed_json_document[parsed_key] = str(json_document[key])
            elif (node_structure[parsed_key] == int) and (type(json_document[key]) == int):
              parsed_json_document[parsed_key] = int(json_document[key])
            elif node_structure[parsed_key] == bool: # converting unicode to int and then to bool
              parsed_json_document[parsed_key] = bool(int(json_document[key]))
            # elif node_structure[parsed_key] == list:
              # parsed_json_document[parsed_key] = list(json_document[key])
            elif node_structure[parsed_key] == datetime.datetime:
              parsed_json_document[parsed_key] = datetime.datetime.strptime(json_document[key], "%d/%m/%Y")
            else:
              parsed_json_document[parsed_key] = json_document[key]

            # --- END of processing for remaining fields

          else:
            parsed_json_document[key] = json_document[key]
            attribute_relation_list.append(key)
          
        # calling method to create File GSystems
        node = create_resource_gsystem(parsed_json_document)
        # node = collection.File.one({ "_id": ObjectId('') })
        # print node, "\n"


        # starting processing for the attributes and relations saving
        if node and attribute_relation_list:

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
                if (attr_value['data_type'] in [int, float, long]) and (not json_document[key]):
                  json_document[key] = 0

                if json_document[key]:

                  if attr_value['data_type'] == basestring:

                    info_message = "\n For GAttribute parsing content | key: " + attr_key + " -- value: " + json_document[key]
                    # print info_message

                  elif attr_value['data_type'] == unicode:
                    json_document[key] = unicode(json_document[key])

                  elif attr_value['data_type'] == bool: 
                    # setting int values for CR/XCR
                    if json_document[key] == "CR":
                      json_document[key] = 1
                    elif json_document[key] == "XCR":
                      json_document[key] = 0
                    
                    json_document[key] = bool(int(json_document[key]))
                    
                  elif attr_value['data_type'] == datetime.datetime:
                    json_document[key] = datetime.datetime.strptime(json_document[key], "%d/%m/%Y")

                  elif attr_value['data_type'] == int:
                    json_document[key] = int(json_document[key])
                  elif attr_value['data_type'] == float:
                    json_document[key] = float(json_document[key])
                  elif attr_value['data_type'] == long:
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
                  # print "\n-----\nsubject_id: ", subject_id
                  attribute_type_node = collection.Node.one({'_type': "AttributeType", 
                                     '$or': [{'name': {'$regex': "^"+attr_key+"$", '$options': 'i'}}, 
                                     {'altnames': {'$regex': "^"+attr_key+"$", '$options': 'i'}}]
                                     })
                  # print "\nattribute_type_node: ", attribute_type_node.name
                  object_value = json_document[key]
                  # print "\nobject_value: ", object_value
                  ga_node = None

                  info_message = "\n- Creating GAttribute ("+node.name+" -- "+attribute_type_node.name+" -- "+str(json_document[key])+") ...\n"
                  print info_message
                  ga_node = create_gattribute(subject_id, attribute_type_node, object_value)
                  print "\nga_node : \n", ga_node.name
                  # To break outer for loop as key found
                  break

                else:
                  error_message = "\n!! DataNotFound: No data found for field ("+attr_key+") while creating GSystem ( -- "+node.name+")\n"

            if is_relation:
              relation_list.append(key)

          if not relation_list:
            # No possible relations defined for this node
            info_message = "\n!! ("+node.name+"): No possible relations defined for this node.\n"
            # log_list.append(info_message)
            return

          gst_possible_relations_dict = node.get_possible_relations(file_gst._id)

          # Write code for setting relations
          for key in relation_list:
            is_relation = True

            for rel_key, rel_value in gst_possible_relations_dict.iteritems():
              if key == rel_key: # commented because teaches is only relation being used for time being
              # if key == "teaches":
                is_relation = False

                if json_document[key]:
                  # Here semi-colon(';') is used instead of comma(',')
                  # Beacuse one of the value may contain comma(',') which causes problem in finding required value in database
                  # if ";" not in json_document[key]:
                  #   # Necessary to inform perform_eval_type() that handle this value as list
                  #   json_document[key] = "\""+json_document[key]+"\", "

                  # else:
                  #   formatted_value = ""
                  #   for v in json_document[key].split(";"):
                  #       formatted_value += "\""+v.strip(" ")+"\", "
                  #   json_document[key] = formatted_value

                  # -----------------------------
                  def _get_id_from_hierarchy(hier_list, oid=None):
                    '''
                    Returns the last hierarchical element's ObjectId.
                    Arguments to be passes is list of unicode names.
                    e.g.
                    hier_list = [u'NCF', u'Science', u'Physical world', u'Materials', u'States of matter', u'Liquids']
                    '''
                    # print oid
                    if len(hier_list) >= 2:
                      if oid:
                        curr_oid = collection.GSystem.one({ "_id": oid })
                        # print curr_oid.name
                      else:
                        curr_oid = collection.GSystem.one({ "name": hier_list[0], 'group_set': {'$all': [ObjectId(home_group._id)]}, 'member_of': {'$in': [ObjectId(theme_gst._id), ObjectId(theme_item_gst._id), ObjectId(topic_gst._id)]} })

                      next_oid = collection.GSystem.one({ 
                                                "name": hier_list[1],
                                                'group_set': {'$all': [ObjectId(home_group._id)]},
                                                'member_of': {'$in': [ObjectId(theme_item_gst._id), ObjectId(topic_gst._id)]},
                                                '_id': {'$in': curr_oid.collection_set }
                                                })

                      # print "||||||", next_oid.name
                      hier_list.remove(hier_list[0])
                      _get_id_from_hierarchy(hier_list, next_oid._id)
                    
                    if len(hier_list) == 1:
                      if oid:
                        # print "oid: ", oid
                        return oid
                      else:
                        return collection.GSystem.one({ "name": hier_list[0], 'group_set': {'$all': [ObjectId(home_group._id)]}, 'member_of': {'$in': [ObjectId(theme_gst._id), ObjectId(theme_item_gst._id), ObjectId(topic_gst._id)]} }, {"_id": 1} )
                    # -----------------------------                  


                  if ":" in json_document[key]:
                    formatted_list = []
                    temp_teaches_list = json_document[key].replace("\n", "").split(":")
                    # print "\n temp_teaches", temp_teaches
                    for v in temp_teaches_list:
                      formatted_list.append(v.strip())

                    right_subject_id = []
                    right_subject_id.append(_get_id_from_hierarchy(formatted_list)._id)
                    json_document[key] = right_subject_id
                    # print json_document[key]
                  
                  else:
                    formatted_list = list(json_document[key].strip())
                    right_subject_id = []
                    right_subject_id.append(_get_id_from_hierarchy(formatted_list)._id)
                    json_document[key] = right_subject_id


                  # print "\n----------", json_document[key]
                  info_message = "\n- For GRelation parsing content | key: " , rel_key , " -- " , json_document[key]
                  print info_message
                  # print list(json_document[key])

                  # perform_eval_type(key, json_document, "GSystem", "GSystem")

                  for right_subject_id in json_document[key]:
                    print "\njson_document[key]: ", json_document[key]

                    subject_id = node._id
                    print "subject_id : ", subject_id
                    print "node.name: ", node.name
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

                    relation_type_node = collection.Node.one({'_type': "RelationType", 
                                                              '$or': [{'name': {'$regex': "^"+rel_key+"$", '$options': 'i'}}, 
                                                                      {'altnames': {'$regex': "^"+rel_key+"$", '$options': 'i'}}],
                                                              'subject_type': {'$in': rel_subject_type}
                                                      })

                    info_message = "\n- Creating GRelation (", node.name, " -- ", rel_key, " -- ", str(right_subject_id),") ...\n"
                    print info_message
                    gr_node = create_grelation(subject_id, relation_type_node, right_subject_id)
                    print "\n gr_node: \n", gr_node.name                  
                  # To break outer for loop if key found
                  break

                else:
                  error_message = "\n!! DataNotFound: No data found for relation (", rel_key, ") while creating GSystem (",file_gst.name, " -- ", node.name,")\n"
                  print error_message

                  break

          # print relation_list
        else:
            print "\n!! Either resource is already created or file is already saved into gridfs/DB"
            continue

      except Exception as e:
          # error_message = "\n While creating "+gsystem_type_name+"'s GSystem ("+json_document['name']+") got following error...\n " + str(e)
          # print error_message # Keep it!
          print e


def create_resource_gsystem(resource_data):
  
  # fetching resource from url
  resource_link = resource_data.get("resource_link")
  files = urllib2.urlopen(resource_link)
  files = io.BytesIO(files.read())
  filename = resource_link.split("/")[-1]
  filemd5 = hashlib.md5(files.read()).hexdigest()
  size, unit = getFileSize(files)
  size = {'size':round(size, 2), 'unit':unicode(unit)}
  
  fcol = get_database()[File.collection_name]
  fileobj = fcol.File()

  check_obj_by_name = collection.File.find_one({"_type":"File", 'member_of': {'$all': [ObjectId(file_gst._id)]}, 'group_set': {'$all': [ObjectId(home_group._id)]}, "name": unicode(resource_data["name"]) })
  # print "\n====", check_obj_by_name

  if fileobj.fs.files.exists({"md5":filemd5}) or check_obj_by_name:
    
    coll_oid = get_database()['fs.files']
    cur_oid = coll_oid.find_one({"md5":filemd5})
    # printing appropriate error message
    if check_obj_by_name:
      print "\nResource with same name of ", resource_data["name"] ," and _type 'File' exist in the group. Ref _id: ", check_obj_by_name._id
    else:      
      print "\nResource file exists in DB: ", cur_oid
    return None

  else:
    print "\n- Creating resource: ", unicode(resource_data["name"])
    
    filetype = magic.from_buffer(files.read(100000), mime = 'true')               #Gusing filetype by python-magic

    # filling values in fileobj
    fileobj.name = resource_data["name"]
    fileobj.created_by = resource_data["created_by"]
    fileobj.group_set.append(home_group._id)
    fileobj.member_of.append(file_gst._id)
    fileobj.content_org = resource_data["content_org"]
    fileobj.tags = resource_data["tags"]
    fileobj.language = resource_data["language"]
    # username = User.objects.get(id=userid).username
    fileobj.access_policy = u"PUBLIC"
    # print title, "\n----------\n", userid, "\n", group_id, "\n", content_org, "\n", tags, "\n", language, "\n", access_policy
    fileobj.altnames = resource_data["altnames"]
    fileobj.featured = resource_data["featured"]
    fileobj.contributors = resource_data["contributors"] if resource_data["contributors"] else []
    fileobj.license = resource_data["license"]
    fileobj.status = u"PUBLISHED"

    fileobj.file_size = size
    fileobj.mime_type = filetype
    fileobj.save()

    files.seek(0)
    objectid = fileobj.fs.files.put(files.read(), filename=filename, content_type=filetype) #store files into gridfs
    collection.File.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':objectid}})
    # print "\n----------", fileobj

    # filetype1 = mimetypes.guess_type(filename)[0]
    # print filetype1

    # calling save_file()
    # resource_save_reply = save_file(files, title, userid, group_id, content_org, tags, img_type, language, username, access_policy, oid=True)
    # print type(resource_save_reply), "=====", resource_save_reply

    # resource_obj = collection.File.one({"_id":ObjectId(str(resource_save_reply[0]))})
    
    # resource_obj.save()

    return fileobj


def getFileSize(File):
    """
    obtain file size if provided file object
    """
    try:
        File.seek(0,os.SEEK_END)
        num=int(File.tell())
        for x in ['bytes','KB','MB','GB','TB']:
            if num < 1024.0:
                return  (num, x)
            num /= 1024.0
    except Exception as e:
        print "Unabe to calucalate size",e
        return 0,'bytes'

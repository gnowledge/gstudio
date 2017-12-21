''' -- imports from python libraries -- '''
import os
from sys import exc_info
import csv
import json
import ast
import time
from itertools import chain
# import mimetypes

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import DATA_TYPE_CHOICES
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.models import Node, GSystemType, AttributeType, RelationType
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_SYSTEM_TYPES_LIST

####################################################################################################################

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files" )

log_list = [] # To hold intermediate errors
log_list.append("\n######### Script run on : " + time.strftime("%c") + " #########\n############################################################\n")

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
          if file_name not in ["STs_run1.csv", "STs_run1.json","STs_run2.csv", "STs_run2.json", "ATs.csv", "ATs.json", "RTs.csv", "RTs.json"]:
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
        json_document['help_text'] = unicode(json_document['help_text'])
        json_document["object_scope"] = eval(json_document['object_scope'])
        json_document["subject_scope"] = eval(json_document['subject_scope'])
        json_document["attribute_type_scope"] = eval(json_document['attribute_type_scope'])

        if json_document["attribute_type_scope"]:
          json_document["attribute_type_scope"] = map(unicode,json_document["attribute_type_scope"])
        if json_document["subject_scope"]:
          json_document["subject_scope"] = map(unicode,json_document["subject_scope"])
        if json_document["object_scope"]:
          json_document["object_scope"] = map(unicode,json_document["object_scope"])

        if (json_document['max_digits']):
          json_document['max_digits'] = int(json_document['max_digits'])
        else:
          json_document['max_digits'] = None

        if not json_document['required'].istitle():
          json_document['required'] = ast.literal_eval(json_document['required'].title())

          if json_document['required'] not in [True, False]:
            error_message = "\n InvalidDataError: For "+type_name+" (" + json_document['name'] + ") invalid data found in \"required\" field !!!"
            log_list.append(error_message)
            raise Exception(error_message)

        if not json_document['editable'].istitle():
          json_document['editable'] = ast.literal_eval(json_document['editable'].title())

          if json_document['editable'] not in [True, False]:
            error_message = "\n InvalidDataError: For "+type_name+" (" + json_document['name'] + ") invalid data found in \"editable\" field !!!"
            log_list.append(error_message)
            raise Exception(error_message)

        if json_document['data_type'] not in DATA_TYPE_CHOICES:
          error_message = "\n InvalidDataTypeError: For "+type_name+" (" + json_document['name'] + ") invalid data-type found!!!"
          error_message += "\n Must be one of the following: " + DATA_TYPE_CHOICES
          log_list.append(error_message)
          raise Exception(error_message)


        perform_eval_type("complex_data_type", json_document, type_name, "AttributeType")
        perform_eval_type("subject_type", json_document, type_name, "GSystemType")
        perform_eval_type("validators", json_document, type_name, "AttributeType")

        # if GSTUDIO_DEFAULT_SYSTEM_TYPES_LIST:
        #   json_document["subject_type"] = update_default_st(json_document["subject_type"])

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
        json_document['object_cardinality'] = int(json_document['object_cardinality'])

        json_document["object_scope"] = eval(json_document['object_scope'])
        json_document["subject_scope"] = eval(json_document['subject_scope'])
        json_document["relation_type_scope"] = eval(json_document['relation_type_scope'])

        if json_document["relation_type_scope"]:
          json_document["relation_type_scope"] = map(unicode,json_document["relation_type_scope"])
        if json_document["subject_scope"]:
          json_document["subject_scope"] = map(unicode,json_document["subject_scope"])
        if json_document["object_scope"]:
          json_document["object_scope"] = map(unicode,json_document["object_scope"])

        json_document["is_reflexive"] = ast.literal_eval(json_document['is_reflexive'].title())
        json_document["is_transitive"] = ast.literal_eval(json_document['is_transitive'].title())
        json_document["is_symmetric"] = ast.literal_eval(json_document['is_symmetric'].title())

        perform_eval_type("subject_type", json_document, type_name, "GSystemType")
        perform_eval_type("object_type", json_document, type_name, "GSystemType")
        perform_eval_type("member_of", json_document, type_name, "MetaType")

        # if GSTUDIO_DEFAULT_SYSTEM_TYPES_LIST:
        #   json_document["subject_type"] = update_default_st(json_document["subject_type"])
        #   json_document["object_type"] = update_default_st(json_document["object_type"])

      except Exception as e:
        error_message = "\n While parsing "+type_name+"(" + json_document['name'] + ") got following error at line #" + str(exc_info()[-1].tb_lineno) + "...\n " + str(e)
        log_list.append(error_message)
        print error_message # Keep it!
        # continue

      try:
        info_message = "\n Creating "+type_name+"(" + json_document['name'] + ") ..."
        log_list.append(info_message)

        create_edit_type(type_name, json_document, user_id)

      except Exception as e:
        error_message = "\n While creating "+type_name+" ("+json_document['name']+") got following error at line #" + str(exc_info()[-1].tb_lineno) + "...\n " + str(e)
        print error_message # Keep it!


def update_default_st(field):
  default_st_cur = node_collection.find({'_type': 'GSystemType',
                    'name': {'$in': GSTUDIO_DEFAULT_SYSTEM_TYPES_LIST}})
  default_st_ids = [st._id for st in default_st_cur]
  if default_st_ids:
    field.extend(default_st_ids)
  return field

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
    elif eval_field == "validators":
      type_list.append(data)

    else:
      def _append_to_type_list(eval_field, json_document, type_to_create, type_convert_objectid, data, inner_type_list):
        node = node_collection.one({'_type': type_convert_objectid, 'name': data})

        if node:
          if eval_field == "complex_data_type":
            inner_type_list.append(unicode(node._id))
          elif eval_field in ["attribute_type_set", "relation_type_set"]:
            inner_type_list.append(node)
          else:
            inner_type_list.append(node._id)

        else:
          if eval_field == "complex_data_type":
            type_convert_objectid = "Sub-" + type_convert_objectid

          elif eval_field in ["attribute_type_set", "relation_type_set"]:
            json_document[eval_field] = inner_type_list
            error_message = "\n "+type_convert_objectid+"Error ("+eval_field+"): This "+type_convert_objectid+" (" + data + ") doesn't exists for creating "+type_to_create+" (" + json_document['name'] + ") !!!\n"
            log_list.append(error_message)

          error_message = "\n "+type_convert_objectid+"Error ("+eval_field+"): This "+type_convert_objectid+" (" + data + ") doesn't exists for creating "+type_to_create+" (" + json_document['name'] + ") !!!\n"
          log_list.append(error_message)
          raise Exception(error_message)

      if type_to_create == "RelationType" and type(data) == list:
          inner_type_list = []
          for each in data:
            _append_to_type_list(eval_field, json_document, type_to_create, type_convert_objectid, each, inner_type_list)
          type_list.append(inner_type_list)
      else:
        _append_to_type_list(eval_field, json_document, type_to_create, type_convert_objectid, data, type_list)
  # Sets python-type converted list
  json_document[eval_field] = type_list


# -----------------------------------------------------------------------------------------------------------------
# Create/Edit Function Defined for creating GSystemTypes, AttributeTypes, RelationTypes
# -----------------------------------------------------------------------------------------------------------------


def create_edit_type(type_name, json_document, user_id):
  """Creates factory Types' (including GSystemType, AttributeType, RelationType)
  """
  node = node_collection.one({'_type': type_name, 'name': json_document['name']})
  if node is None:
    try:
      node = eval("node_collection.collection"+"."+type_name)()
      
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
        old_data = node[key]
        new_data = json_document[key]
        if type(old_data) == list:
          if len(old_data) and len(new_data):
              if type(old_data[0]) == list:
                  old_data = list(chain.from_iterable(old_data))
                  new_data = list(chain.from_iterable(new_data))
          if [] in old_data:
            old_data.remove([])
          if [] in new_data:
            new_data.remove([])

          old_data_refined = []
          new_data_refined = []
          for each_odata in old_data:
              if isinstance(each_odata,list):
                  old_data_refined.extend(each_odata)
              else:
                  old_data_refined.append(each_odata)
          for each_ndata in new_data:
              if isinstance(each_ndata,list):
                  new_data_refined.extend(each_ndata)
              else:
                  new_data_refined.append(each_ndata)
          old_data = old_data_refined
          new_data = new_data_refined
          if set(old_data) != set(new_data):
            # node[key].extend(json_document[key])
            # Avoiding extend's use
            # Because despite of whether that value exists or not in the list,
            # it adds value to the list

            if key == "subject_type" and node['name'] in [u"start_time", u"end_time"]:
              # Don't empty list
              # Because these are the only ATs for which values are set in factory_type.py file
              # as well as in ATs.csv used setting up schema for MIS GAPP
              # So, in this script values of factory.py file's values get overridden by ATs.csv
              # and this is causing problem
              # Instead making empty and refilling new entries as per ATs.csv file,
              # Keep existing values and append those of ATS.csv file!
              pass
            else:
              node[key] = []

            for each in json_document[key]:
              if each not in node[key]:
                node[key].append(each)
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

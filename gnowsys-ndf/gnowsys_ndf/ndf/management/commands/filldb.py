''' -- imports from python libraries -- '''
import os
import time
import sys
import json
from datetime import datetime

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option

from mongokit import IS

from django_mongokit import get_database

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node, GSystemType, ToReduceDocs, ReducedDocs, IndexedWordList
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.ndf.models import DATA_TYPE_CHOICES, QUIZ_TYPE_CHOICES_TU
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.settings import META_TYPE
from gnowsys_ndf.settings import GSTUDIO_TASK_TYPES
from gnowsys_ndf.factory_type import factory_gsystem_types, factory_attribute_types, factory_relation_types

###############################################################################
# Global variables
db = get_database()
collection = db[Node.collection_name]

filename = sys.argv[-1]
f = filename.split("/")
if f[-1] == "ATs.json" or f[-1] == "RTs.json" or f[-1] == "STs.json":
  json_file = open(filename)
else:
  json_file = ""

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files")

log_list = [] # To hold intermediate error and information messages
log_list.append("\n######### Script run on : " + time.strftime("%c") + " #########\n############################################################\n")

###############################################################################

class Command(BaseCommand):
  help = "This performs activities required for setting up default structure or updating it." 

  option_list = BaseCommand.option_list

  user_defined_option_list = (
    make_option('-s', '--setup-structure', action='store_true', dest='setup_structure', default=True, help='This performs activities required for setting up default structure or updating it.'),
    make_option('-n', '--no-structure', action='store_false', dest='setup_structure', default=True, help='This skips performing any activities required for updating structure.'),
    make_option('-c', '--clean-structure', action='store_true', dest='clean_structure', default=False, help='This performs activities required for cleaning inconsistent data in structure.'),
  )

  option_list = option_list + user_defined_option_list

  def handle(self, *args, **options):
    if options["setup_structure"]:
      try:
        info_message = "\n Performing structure create/update...\n"
        print info_message
        log_list.append(info_message)

        user_id = 1 
        node_doc = None
        meta_type_name = META_TYPE[0]

        for each in META_TYPE:
          meta_type = collection.GSystemType.one({'$and':[{'_type':'MetaType'},{'name':each}]})
          if meta_type == None:                
            create_meta_type(user_id,each)

          else:
            print "Meta_Type",each,"already created"

        meta_type = collection.GSystemType.one({'$and':[{'_type':'MetaType'},{'name':meta_type_name}]}) # getting MetaType Object
        if meta_type == None:
          meta_type = create_meta_type(user_id) #creating MetaType
        
        for each in GAPPS:
          # Temporarily made this change for renaming "Browse Topic & Browse Resource" untill all servers will be updated
          if each == "Topics":
            br_topic = collection.Node.one({'_type':'GSystemType', 'name': 'Browse Topic'})
            if br_topic:
              br_topic.name = unicode(each)
              br_topic.status = u"PUBLISHED"
              br_topic.save()

          if each == "E-Library":
            br_resource = collection.Node.one({'_type':'GSystemType', 'name': 'Browse Resource'})
            if br_resource:
              br_resource.name = unicode(each)
              br_resource.status = u"PUBLISHED"
              br_resource.save()
          # Keep above part untill all servers updated
          
          node_doc = collection.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':each}]})
          if (node_doc == None or each != node_doc['name']):
            gst_node=collection.GSystemType()
            gst_node.name = unicode(each)
            gst_node.created_by = user_id
            gst_node.modified_by = user_id

            if user_id not in gst_node.contributors:
              gst_node.contributors.append(user_id)

            gst_node.member_of.append(meta_type._id) # appending metatype to the GSystemType
            gst_node.status = u"PUBLISHED"
            gst_node.save()

          elif(meta_type._id not in node_doc.member_of):
            node_doc.member_of.append(meta_type._id)
            node_doc.status = u"PUBLISHED"
            node_doc.save()
                   
        # Create default group 'home'
        node_doc =collection.GSystemType.one({'$and':[{'_type': u'Group'},{'name': u'home'}]})
        if node_doc is None:
          gs_node = collection.Group()
          gs_node.name = u'home'
          gs_node.created_by = user_id
          gs_node.modified_by = user_id

          if user_id not in gs_node.contributors:
            gs_node.contributors.append(user_id)

          gs_node.member_of.append(collection.Node.one({'name': "Group"})._id)
          gs_node.disclosure_policy=u'DISCLOSED_TO_MEM'
          gs_node.subscription_policy=u'OPEN'
          gs_node.visibility_policy=u'ANNOUNCED'
          gs_node.encryption_policy=u'NOT_ENCRYPTED'
          gs_node.group_type= u'PUBLIC'
          gs_node.edit_policy =u'NON_EDITABLE'
          gs_node.save()
        
        # Creating factory GSystemType's 
        create_sts(factory_gsystem_types,user_id)

        # Creating factory RelationType's 
        create_rts(factory_relation_types,user_id)

        # Creating factory AttributeType's
        create_ats(factory_attribute_types,user_id)

        # Creating  AttributeType's, RelationType's and SystemType's by json file as input
        if json_file:
          a = json_file.name.split('/')
          if a[-1] == 'ATs.json':
            json_data = json.loads(json_file.read())
            create_ats(json_data,user_id)

          elif a[-1] == 'RTs.json':
            json_data = json.loads(json_file.read())
            #print json_data,"Test_RTS json"
            create_rts(json_data,user_id)

          elif a[-1] == "STs.json":
            json_data = json.loads(json_file.read())
            #print json_data,"Test_STs json"
            create_sts(json_data,user_id)

          else:
            print 'file name should be ATs.json,STs.json or RTs.json to load Ats,STs or RTs of json'
        
        # Retrieve 'Quiz' GSystemType's id -- in order to append it to 'meta_type_set' for 'QuizItem' GSystemType
        quiz_type = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Quiz'})
        quiz_item_type = collection.Node.one({'_type': u'GSystemType', 'name': u'QuizItem'})
        
        # Append quiz_type, options & correct_answer to attribute_type_set of 'QuizItem'
        if not quiz_item_type.attribute_type_set:
          quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'quiz_type'}))
          quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'options'}))
          quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'correct_answer'}))
          quiz_item_type.save()
        
        # Append start_time & end_time to attribute_type_set of 'Quiz'
        if not quiz_type.attribute_type_set:
          quiz_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'start_time'}))
          quiz_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'end_time'}))
          quiz_type.save()

        #Creation Gsystem Eventtype as a container to hold the Event types
        glist = collection.Node.one({'_type': "GSystemType", 'name': "GList"})
        GlistItem=collection.Node.one({'_type': "GSystemType","name":"GListItem"})
        #create super container list Eventlist
        #First check if EventList Exist or not
        #Eventtype and College Type Glist Creation
        Eventtype=collection.Node.one({'member_of':ObjectId(glist._id),"name":"Eventtype"})
        if Eventtype is None:
          glist_container = collection.GSystem()
          glist_container.name=u"Eventtype"
          glist_container.status = u"PUBLISHED"
          glist_container.created_by=user_id
          glist_container.member_of.append(glist._id)
          glist_container.save()
          print "\n Eventtype Created."
        collegeevent=collection.Node.one({"member_of":ObjectId(glist._id),"name":"CollegeEvents"})
        if not collegeevent:
            node = collection.GSystem()
            node.name=u"CollegeEvents"
            node.status = u"PUBLISHED"
            node.created_by=user_id
            node.member_of.append(glist._id)
            node.save()
            print "\n CollegeEvents Created."
  
        Event=collection.Node.find_one({'_type':"GSystemType","name":"Event"})  
        All_Event_Types=collection.Node.find({"type_of": ObjectId(Event._id)})
        Eventtype=collection.Node.one({'member_of':ObjectId(glist._id),"name":"Eventtype"})
        CollegeEvents=collection.Node.one({"name":"CollegeEvents"})
        Event_type_list=[]
        College_type_list=[]
        for i in All_Event_Types:
            
            if (GlistItem._id not in i.member_of): 
                i.member_of.append(GlistItem._id)
                i.save()
            if i.name not in ['Classroom Session','Exam']:
               Event_type_list.append(i._id)
            if i.name in ['Classroom Session','Exam']:
               College_type_list.append(i._id)
                
        collection.update({'_id': ObjectId(Eventtype._id)}, {'$set': {'collection_set': Event_type_list}}, upsert=False, multi=False)
        
        collection.update({'_id': ObjectId(CollegeEvents._id)}, {'$set': {'collection_set': College_type_list}}, upsert=False, multi=False)
        
        #End of adding Event Types and CollegeEvents
        
        # Creating GSystem(s) of GList for GSTUDIO_TASK_TYPES
        # Divided in two parts:
        # 1) Creating Types as GList nodes from GSTUDIO_TASK_TYPES
        # 2) Create "TaskType" which again is going to be GList node;
        #    that will act as container i.e. hold above Types in its collection_set
        glist = collection.Node.one({'_type': "GSystemType", 'name': "GList"})
        task_type_ids = []
        # First: Creating Types as GList nodes from GSTUDIO_TASK_TYPES
        print "\n"
        info_message = "\n"
        for gl_node_name in GSTUDIO_TASK_TYPES:
          gl_node = collection.Node.one({'_type': "GSystem", 'member_of':glist._id, 'name': gl_node_name})

          if gl_node is None:
            gl_node = collection.GSystem()
            gl_node.name = unicode(gl_node_name)
            gl_node.created_by = user_id
            gl_node.modified_by = user_id

            if user_id not in gl_node.contributors:
              gl_node.contributors.append(user_id)

            gl_node.member_of.append(glist._id)
            gl_node.status = u"PUBLISHED"
            gl_node.save()
            print " Created ("+gl_node_name+") as GList required for TaskType."
            info_message += "\n Created ("+gl_node_name+") as GList required for TaskType."

            if gl_node._id not in task_type_ids:
              task_type_ids.append(gl_node._id)

          else:
            print " GList ("+gl_node_name+") already created !"
            info_message += "\n GList ("+gl_node_name+") already created !"

        # Second: Create "TaskType" (GList container)
        glc_node_name = u"TaskType"
        glc_node = collection.Node.one({'_type': "GSystem", 'member_of': glist._id, 'name': glc_node_name})
        if glc_node is None:
          glc_node = collection.GSystem()
          glc_node.name = unicode(glc_node_name)
          glc_node.created_by = user_id
          glc_node.modified_by = user_id

          if user_id not in glc_node.contributors:
            glc_node.contributors.append(user_id)

          glc_node.member_of.append(glist._id)
          glc_node.collection_set = task_type_ids
          glc_node.status = u"PUBLISHED"
          glc_node.save()
          print " Created ("+glc_node_name+") as GList (container)."
          info_message += "\n Created ("+glc_node_name+") as GList (container)."

        else:
          print " GList ("+glc_node_name+") container already created !"
          info_message += "\n GList ("+glc_node_name+") container already created !"
        
        print "\n"
        info_message += "\n\n"
        log_list.append(info_message)

        info_message = " Structure updated succesfully.\n"
        print info_message
        log_list.append(info_message)

      except Exception as e:
        error_message = "SetupStructureError: " + str(e)
        print "\n " + error_message
        log_list.append(error_message)
        # raise Exception(error_message)
        pass

      finally:
        if log_list:
          log_list.append("\n ============================ End of Iteration ============================\n")

          log_file_name = os.path.splitext(os.path.basename(__file__))[0] + ".log"
          log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)

          with open(log_file_path, 'a') as log_file:
            log_file.writelines(log_list)
      
    if options["clean_structure"]:
      try:
        info_message = "\n Performing structure cleaning activities...\n"
        print info_message
        log_list.append(info_message)

        clean_structure()

        info_message = "\n\n Structure cleaning activities completed succesfully.\n"
        print info_message
        log_list.append(info_message)
      except Exception as e:
        error_message = "\n\n StructureCleaningError: " + str(e) + "!!!\n"
        print "\n " + error_message
        log_list.append(error_message)
        # raise Exception(error_message)
        pass
      finally:
        if log_list:
          log_list.append("\n ============================ End of Iteration ============================\n")

          log_file_name = os.path.splitext(os.path.basename(__file__))[0] + ".log"
          log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)

          with open(log_file_path, 'a') as log_file:
            log_file.writelines(log_list)

    # --- End of handle() ---

# Functions defined ===========================================================

def create_meta_type(user_id,meta_type):
  '''
  Creating meta_type in database
  '''
  meta = collection.MetaType()
  meta.name = meta_type
  meta.created_by = user_id # default hardcode
  meta.modified_by = user_id
  if user_id not in meta.contributors:
    meta.contributors.append(user_id)
  meta.status = u"PUBLISHED"
  meta.save()
  print "succesfully created META_TYPE:",meta_type

def create_gsystem_type(st_name, user_id, meta_type_id = None):
  '''
  creating factory GSystemType's 
  '''
  node = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name':st_name}]})
  if node is None:
    try:
      gs_node = collection.GSystemType()
      gs_node.name = unicode(st_name)
      gs_node.created_by = user_id
      gs_node.modified_by = user_id
      if meta_type_id:
        gs_node.member_of.append(meta_type_id)
      if user_id not in gs_node.contributors:
        gs_node.contributors.append(user_id)
      gs_node.status = u"PUBLISHED"
      gs_node.save()
      print 'created', st_name, 'as', 'GSystemType'
    except Exception as e:
      print 'GsystemType',st_name,'fails to create because:',e
  else:
    if not node.member_of:
      if meta_type_id:
        node.member_of.append(meta_type_id)
        print "Edited member_of",node.name
        node.save()
    print 'GSystemType',st_name,'already created'

def create_attribute_type(at_name, user_id, data_type, system_type_id_list, meta_type_id = None):
  '''
  creating factory AttributeType's
  '''
  node = collection.Node.one({'$and':[{'_type': u'AttributeType'},{'name':at_name}]})
  if node is None:
    try:
      at = collection.AttributeType()
      at.name = unicode(at_name)
      at.created_by = user_id
      at.modified_by = user_id
      if meta_type_id:
        at.member_of.append(meta_type_id)

      if user_id not in at.contributors:
        at.contributors.append(user_id)
      at.data_type = data_type              
      for each in system_type_id_list:
        at.subject_type.append(each)
      at.status = u"PUBLISHED"
      at.save()
      print 'created', at_name, 'as', 'AttributeType'
    except Exception as e:
      print 'AttributeType',at_name,'fails to create because:',e
  else:
    #Editing already existing document
    edited=False
    if not node.member_of:
      if meta_type_id:
        node.member_of.append(meta_type_id)
        print "Edited member_of",node.name
        edited=True
    if not node.subject_type == system_type_id_list:
      node.subject_type=system_type_id_list
      edited=True
      print "Edited subject_type of",node.name,"Earlier it was",node.subject_type,"now it is ",system_type_id_list
    if not node.data_type == data_type:
      node.data_type=data_type
      edited=True
      print "Edited data_type of",node.name,"Earlier it was",node.data_type,"now it is ",data_type
    if edited:
      node.status = u"PUBLISHED"
      node.save()
    else:
      print 'AttributeType',at_name,'already created'

def create_relation_type(rt_name, inverse_name, user_id, subject_type_id_list, object_type_id_list, meta_type_id=None, object_cardinality=None):
  '''
  creating factory RelationType's
  '''
  rt_node = collection.RelationType.one({'_type': u'RelationType', 'name': rt_name}) 
  if rt_node is None:
    try:
      rt_node = collection.RelationType()
      rt_node.name = unicode(rt_name)
      rt_node.inverse_name = unicode(inverse_name)
      rt_node.object_cardinality = object_cardinality
      
      for st_id in subject_type_id_list:
        rt_node.subject_type.append(st_id)
      
      for ot_id in object_type_id_list:
        rt_node.object_type.append(ot_id)
      
      rt_node.created_by = user_id
      rt_node.modified_by = user_id
      if meta_type_id:
        rt_node.member_of.append(meta_type_id)

      if user_id not in rt_node.contributors:
        rt_node.contributors.append(user_id)
      rt_node.status = u"PUBLISHED"
      rt_node.save()
      print 'created', rt_name, 'as', 'RelationType'
    except Exception as e:
      print 'RelationType',rt_name,'fails to create because:',e
  
  else:
    # Edit already existing document
    edited=False
    if not rt_node.member_of:
      if meta_type_id:
        print "Edited member_of",rt_node.name
        rt_node.member_of.append(meta_type_id)
        edited=True
    
    if rt_node.object_cardinality != object_cardinality:
      print "Edited object_cardinality of ", rt_node.name, " Earlier it was ", rt_node.object_cardinality, " now it is ", object_cardinality
      rt_node.object_cardinality = object_cardinality
      edited = True

    if not rt_node.subject_type == subject_type_id_list:
      print "Edited subject_type of",rt_node.name,"Earlier it was ",rt_node.subject_type,"now it is",subject_type_id_list
      rt_node.subject_type=subject_type_id_list
      edited=True
    
    if not rt_node.object_type == object_type_id_list:
      print "Edited object_type of",rt_node.name,"Earlier it was",rt_node.object_type,"now it is",object_type_id_list
      rt_node.object_type=object_type_id_list
      edited=True
    
    if edited :
      rt_node.status = u"PUBLISHED"
      rt_node.save()
    
    else:
      print 'RelationType',rt_node.name,'already created'

def create_ats(factory_attribute_types,user_id):
  meta_type_id = ""
  for each in factory_attribute_types:
    gsystem_id_list = []
    for key,value in each.items():
      at_name = key
      data_type = value['data_type']

      if value.has_key("meta_type"):
        meta_type_name = value['meta_type']
        meta_type = collection.GSystemType.one({'$and':[{'_type':'MetaType'},{'name':meta_type_name}]})
        if meta_type:
          meta_type_id = meta_type._id

      for e in value['gsystem_names_list']:
        node = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name': e}]})
        if node is not None:
          gsystem_id_list.append(node._id)
        else:
          print e,"as GSystemType not present in database"
    create_attribute_type(at_name, user_id, data_type, gsystem_id_list, meta_type_id)

def create_rts(factory_relation_types,user_id):
  meta_type_id = ""
  for each in factory_relation_types:
    subject_type_id_list = []
    object_type_id_list = []
    object_cardinality = None

    for key,value in each.items():
      at_name = key
      inverse_name = value['inverse_name']

      if value.has_key("meta_type"):
        meta_type_name = value['meta_type']
        meta_type = collection.GSystemType.one({'$and':[{'_type':'MetaType'},{'name':meta_type_name}]})
        if meta_type:
          meta_type_id = meta_type._id

      for s in value['subject_type']:
        node_s = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name': s}]})
        if node_s is None:
          node_s = collection.Node.one({'$and':[{'_type': u'MetaType'},{'name': s}]})
          
        subject_type_id_list.append(node_s._id)
       
      for rs in value['object_type']:
        node_rs = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name': rs}]})
        if node_rs is None:
          node_rs =collection.Node.one({'$and':[{'_type': u'MetaType'},{'name': rs}]})
  
        object_type_id_list.append(node_rs._id)
      
      if value.has_key("object_cardinality"):
        object_cardinality = value["object_cardinality"]

    create_relation_type(at_name, inverse_name, user_id, subject_type_id_list, object_type_id_list, meta_type_id, object_cardinality)

def create_sts(factory_gsystem_types,user_id):
  meta_type_id = ""
  for each in factory_gsystem_types:
    name = each['name']
    meta_type_name = each['meta_type']
    meta_type = collection.GSystemType.one({'$and':[{'_type':'MetaType'},{'name':meta_type_name}]})
    if meta_type:
      meta_type_id = meta_type._id
    create_gsystem_type(name, user_id, meta_type_id)

  # For creating Topics as a collection of Theme & Topic
  theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
  topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
  topics = collection.Node.one({'_type': 'GSystemType', 'name': 'Topics'})
  if not topics.collection_set:
    topics.collection_set.append(theme_GST._id)
    topics.collection_set.append(topic_GST._id)
    topics.created_by = 1
    topics.modified_by = 1
    topics.status = u"PUBLISHED"
    topics.save()

def clean_structure():
  '''
  This function perform cleaning activities.
  '''
  # Setting email_id field of Author class =========================================
  info_message = "\n\nSetting email_id field of following document(s) of Author class...\n"
  print info_message
  log_list.append(info_message)

  users = User.objects.all()
  for each in users:
    try:
      auth_node = collection.Node.one({'_type': "Author", 'created_by': each.id})

      if auth_node:
        res = collection.update(
          {'_id': auth_node._id},
          {'$set': {'email': each.email}},
          upsert=False, multi=False
        )

        if res['n']:
          auth_node.reload()
          info_message = "\n Author node's (" + str(auth_node._id) + " -- " + auth_node.name + ") email field updated with following value: " + auth_node.email

        else:
          info_message = "\n Author node's (" + str(auth_node._id) + " -- " + auth_node.name + ") email field update failed !!!"
      
        log_list.append(info_message)

      else:
        info_message = "\n No author node exists with this name (" + auth_node.name + ") !!!"
        log_list.append(info_message)
    
    except Exception as e:
      error_message = "\n Author node has multiple records... " + str(e) + "!!!"
      log_list.append(error_message)
      continue

  # Setting attribute_set & relation_set ==================
  info_message = "\n\nSetting attribute_set & relation_set for following document(s)...\n"
  print info_message
  log_list.append(info_message)
  # ------------------------------------------------------------------------------------
  # Fetch all GSystems (including File, Group & Author as well; as these are sub-types of GSystem)
  # ------------------------------------------------------------------------------------
  # Keeping timeout=False, as cursor may exceeds it's default time i.e. 10 mins for which it remains alive
  # Needs to be expicitly close

  # to fix broken documents which are having partial/outdated attributes/relations in their attribute_set/relation_set. 
  # first make their attribute_set and relation_set empty and them fill them with latest key-values. 
  collection.update(
    {'_type': {'$in': ["GSystem", "File", "Group", "Author"]}, 'attribute_set': {'$exists': True}, 'relation_set': {'$exists': True}},
    {'$set': {'attribute_set': [], 'relation_set': []}}, 
    upsert=False, multi=True
  )

  gs = collection.Node.find({'_type': {'$in': ["GSystem", "File", "Group", "Author"]}, 
                              '$or': [{'attribute_set': []}, {'relation_set': []}] 
                            }, timeout=False)

  for each_gs in gs:
    attr_list = []  # attribute-list
    rel_list = []   # relation-list

    print " .",
    if each_gs.member_of_names_list:
      info_message = "\n\n >>> " + str(each_gs.name) + " ("+str(each_gs.member_of_names_list[0])+")"
    else:
      info_message = "\n\n >>> " + str(each_gs.name) + " (ERROR: member_of field is not set properly for this document -- "+str(each_gs._id)+")"
    log_list.append(info_message)
    # ------------------------------------------------------------------------------------
    # Fetch all attributes, if created in GAttribute Triple
    # Key-value pair will be appended only for those whose entry would be found in GAttribute Triple
    # ------------------------------------------------------------------------------------
    ga = collection.aggregate([{'$match': {'subject': each_gs._id, '_type': "GAttribute", 'status': u"PUBLISHED"}}, 
                              {'$project': {'_id': 0, 'key_val': '$attribute_type', 'value_val': '$object_value'}}
                            ])

    # ------------------------------------------------------------------------------------
    # Fetch all relations, if created in GRelation Triple
    # Key-value pair will be appended only for those whose entry would be found in GRelation Triple
    # ------------------------------------------------------------------------------------
    gr = collection.aggregate([{'$match': {'subject': each_gs._id, '_type': "GRelation", 'status': u"PUBLISHED"}},
                              {'$project': {'_id': 0, 'key_val': '$relation_type', 'value_val': '$right_subject'}}
                            ])
    if ga:
      # If any GAttribute found
      # ------------------------------------------------------------------------------------
      # Setting up attr_list
      # ------------------------------------------------------------------------------------
      # print "\n"
      for each_gar in ga["result"]:
        if each_gar:
          key_node = get_database().dereference(each_gar["key_val"])
          # print "\t", key_node["name"], " -- ", each_gar["value_val"]
          # Append corresponding GAttribute as key-value pair in given attribute-list
          # key: attribute-type name
          # value: object_value from GAttribute document
          attr_list.append({key_node["name"]: each_gar["value_val"]})

    if gr:
      # If any GRelation found
      # ------------------------------------------------------------------------------------
      # Setting up rel_list
      # ------------------------------------------------------------------------------------
      # print "\n"
      for each_grr in gr["result"]:
        if each_grr:
          key_node = get_database().dereference(each_grr["key_val"])
          # print "\t", key_node["name"], " -- ", each_grr["value_val"]
          # Append corresponding GRelation as key-value pair in given relation-list
          # key: relation-type name
          # value: right_subject from GRelation document
          if not rel_list:
            rel_list.append({key_node["name"]: [each_grr["value_val"]]})

          else:
            key_found = False
            for each in rel_list:
              if each.has_key(key_node["name"]):
                each[key_node["name"]].append(each_grr["value_val"])
                key_found = True

            if not key_found:
              rel_list.append({key_node["name"]: [each_grr["value_val"]]})

    info_message = ""
    if attr_list:
      info_message += "\n\n\tAttributes: " + str(attr_list)
    else:
      info_message += "\n\n\tAttributes: No attribute found!"
    
    if rel_list:
      info_message += "\n\n\tRelations: " + str(rel_list)
    else:
      info_message += "\n\n\tRelations: No relation found!"
    log_list.append(info_message)

    # ------------------------------------------------------------------------------------
    # Finally set attribute_set & relation_set of current GSystem with modified attr_list & rel_list respectively
    # ------------------------------------------------------------------------------------
    res = collection.update({'_id': each_gs._id}, {'$set': {'attribute_set': attr_list, 'relation_set': rel_list}}, upsert=False, multi=False)
    if res['n']:
      info_message = "\n\n\t" + str(each_gs.name) + " updated succesfully !"
      log_list.append(info_message)
      # print " -- attribute_set & relation_set updated succesfully !"

  # ------------------------------------------------------------------------------------
  # Close cursor object if still alive
  # ------------------------------------------------------------------------------------
  if gs.alive:
    info_message = "\n\n GSystem-Cursor state (before): " + str(gs.alive)
    log_list.append(info_message)
    gs.close()
    info_message = "\n\n GSystem-Cursor state (after): " + str(gs.alive)
    log_list.append(info_message)
    print "\n Setting attribute_set & relation_set completed succesfully !"

  # Rectify start_time & end_time of task ==================
  start_time = collection.Node.one({'_type': "AttributeType", 'name': "start_time"})
  end_time = collection.Node.one({'_type': "AttributeType", 'name': "end_time"})

  info_message = "\n\nRectifing start_time & end_time of following task(s)...\n"
  print info_message
  log_list.append(info_message)
  
  invalid_dates_cur = collection.Triple.find({'attribute_type.$id': {'$in': [start_time._id, end_time._id]}, 'object_value': {'$not': {'$type': 9}}})
  for each in invalid_dates_cur:
    date_format_string = ""
    old_value = ""
    new_value = ""
    attribute_type_node = each.attribute_type
    
    if "-" in each.object_value and ":" in each.object_value:
      date_format_string = "%m-%d-%Y %H:%M"
    elif "/" in each.object_value and ":" in each.object_value:
      date_format_string = "%m/%d/%Y %H:%M"
    elif "-" in each.object_value:
      date_format_string = "%m-%d-%Y"
    elif "/" in each.object_value:
      date_format_string = "%m/%d/%Y"
    
    if date_format_string:
      old_value = each.object_value
      info_message = "\n\n\t" + str(each._id) + " -- " + str(old_value)

      res = collection.update({'_id': each._id}, 
              {'$set': {'object_value': datetime.strptime(each.object_value, date_format_string)}}, 
              upsert=False, multi=False
            )
  
      if res['n']:
        print " .",
        each.reload()
        new_value = each.object_value

        info_message += " >> " + str(new_value)
        log_list.append(info_message)

        res = collection.update({'_id': each.subject, 'attribute_set.'+attribute_type_node.name: old_value}, 
                {'$set': {'attribute_set.$.'+attribute_type_node.name: new_value}}, 
                upsert=False, multi=False
              )

        if res["n"]:
          info_message = "\n\n\tNode's (" + str(each.subject) + ") attribute_set (" + attribute_type_node.name + ") updated succesfully."
          log_list.append(info_message)


  # Update type_of field to list
  type_of_cursor=collection.find({'type_of':{'$exists':True}})
  for object_cur in type_of_cursor:
    if type(object_cur['type_of']) == ObjectId or object_cur['type_of'] == None:
      if type(object_cur['type_of']) == ObjectId :
        collection.update({'_id':object_cur['_id']},{'$set':{'type_of':[object_cur['type_of']]}})
      else :
        collection.update({'_id':object_cur['_id']},{'$set':{'type_of':[]}})

  # Removes n attribute if created accidently in existsing documents
  collection.update({'n': {'$exists': True}}, {'$unset': {'n': ""}}, upsert=False, multi=True)

  # Updates wherever modified_by field is None with default value as either first contributor or the creator of the resource
  modified_by_cur = collection.Node.find({'_type': {'$nin': ['GAttribute', 'GRelation', 'node_holder', 'ToReduceDocs', 'ReducedDocs', 'IndexedWordList']}, 'modified_by': None})
  if modified_by_cur.count > 0:
    for n in modified_by_cur:
      if u'required_for' not in n.keys():
        if n.has_key("contributors"):
          if n.contributors:
            collection.update({'_id': n._id}, {'$set': {'modified_by': n.contributors[0]}}, upsert=False, multi=False)
          else:
            if n.created_by:
              collection.update({'_id': n._id}, {'$set': {'modified_by': n.created_by, 'contributors': [n.created_by]}}, upsert=False, multi=False)
            else:
              print "\n Please set created_by value for node (", n._id, " -- ", n._type, " : ", n.name, ")\n"

  # Updating faulty modified_by and contributors values (in case of user-group and file documents)
  cur = collection.Node.find({'_type': {'$nin': ['node_holder', 'ToReduceDocs', 'ReducedDocs', 'IndexedWordList']}, 'modified_by': {'$exists': True}})
  for n in cur:
    # By faulty, it means modified_by and contributors has 1 as their values
    # 1 stands for superuser
    # Instead of this value should be the creator of that resource 
    # (even this is applicable only if created_by field of that resource holds some value)
    if u'required_for' not in n.keys():
      if not n.created_by:
        print "\n Please set created_by value for node (", n._id, " -- ", n._type, " : ", n.name, ")"
      else:
        if n.created_by not in n.contributors:
          collection.update({'_id': n._id}, {'$set': {'modified_by': n.created_by, 'contributors': [n.created_by]} }, upsert=False, multi=False)

  # For delete the profile_pic as GST 
  profile_pic_obj = collection.Node.one({'_type': 'GSystemType','name': u'profile_pic'})
  if profile_pic_obj:
    profile_pic_obj.delete()
    print "\n Deleted GST document of profile_pic.\n"

  # For adding visited_location field (default value set as []) in User Groups.
  try:
    author = collection.Node.one({'_type': "GSystemType", 'name': "Author"})
    if author:
      auth_cur = collection.Node.find({'_type': 'Group', 'member_of': author._id })
      if auth_cur.count() > 0:
        for each in auth_cur:
          collection.update({'_id': each._id}, {'$set': {'_type': "Author"} }, upsert=False, multi=False)    
          print "\n Updated user group: ", each.name
          
      cur = collection.Node.find({'_type': "Author", 'visited_location': {'$exists': False}})
      author_cur = collection.Node.find({'_type': 'Author'})
      if author_cur.count() > 0:
        for each in author_cur:
          if each.group_type == None:
            collection.update({'_id': each._id}, {'$set': {'group_type': u"PUBLIC", 'edit_policy': u"NON_EDITABLE", 'subscription_policy': u"OPEN"} }, upsert=False, multi=False)    
            print "\n Updated user group policies: ", each.name

      if cur.count():
        print "\n"
        for each in cur:
          collection.update({'_type': "Author", '_id': each._id}, {'$set': {'visited_location': []}}, upsert=False, multi=True)
          print " 'visited_location' field added to Author group (" + each.name + ")\n"

    else:
      error_message = "\n Exception while creating 'visited_location' field in Author class.\n Author GSystemType doesn't exists!!!\n"
      raise Exception(error_message)

  except Exception as e:
    print str(e)

  # INSERTED FOR MAP_REDUCE
  allIndexed = collection.IndexedWordList.find({"required_for" : "storing_indexed_words"})
  if allIndexed.count() == 0:
    print "\n Inserting indexes"
    j=1
    while j<=27:
      obj = collection.IndexedWordList()
      obj.word_start_id = float(j)
      obj.words = {}
      obj.required_for = u'storing_indexed_words'
      obj.save()
      j+=1

  # Adding Task GST into start_time and end_time ATs subject_type
  start_time = collection.Node.one({'_type': u'AttributeType', 'name': u'start_time'})
  end_time = collection.Node.one({'_type': u'AttributeType', 'name': u'end_time'})
  task = collection.Node.find_one({'_type':u'GSystemType', 'name':u'Task'})
  if task:
    if start_time:
      if not task._id in start_time.subject_type :
        start_time.subject_type.append(task._id)
        start_time.save()
    if end_time:
      if not task._id in end_time.subject_type :
        end_time.subject_type.append(task._id)
        end_time.save()


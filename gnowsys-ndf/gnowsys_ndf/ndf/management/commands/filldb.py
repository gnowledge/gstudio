''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

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
from gnowsys_ndf.factory_type import factory_gsystem_types, factory_attribute_types, factory_relation_types

####################################################################################################################
#global variables
db = get_database()
collection = db[Node.collection_name]



#for taking input json file
import json
import sys

filename = sys.argv[-1]
print filename,"test"
f = filename.split("/")
if f[-1] == "ATs.json" or f[-1] == "RTs.json" or f[-1] == "STs.json":
    json_file = open(filename)
else:
    json_file = ""

class Command(BaseCommand):
    help = "Based on GAPPS list, inserts few documents (consisting of dummy values) into the following collections:\n\n" \
           "\tGSystemType, AttributeType"

    def handle(self, *args, **options):
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
            node_doc = collection.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':each}]})
            if (node_doc == None or each != node_doc['name']):
                gst_node=collection.GSystemType()
                gst_node.name = unicode(each)
                gst_node.created_by = user_id
                gst_node.modified_by = user_id
                if user_id not in gst_node.contributors:
                    gst_node.contributors.append(user_id)
                gst_node.member_of.append(meta_type._id) # appending metatype to the GSystemType
                gst_node.save()
            elif(meta_type._id not in node_doc.member_of):
                 node_doc.member_of.append(meta_type._id)
                 node_doc.save()
                   
        #Create default group 'home'
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
        
        #creating factory GSystemType's 
        create_sts(factory_gsystem_types,user_id)
        #creating factory RelationType's 
        create_rts(factory_relation_types,user_id)

        #creating factory AttributeType's
        create_ats(factory_attribute_types,user_id)
        

        #creating  AttributeType's, RelationType's and SystemType's by json file as input
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
            
        
        # # Retrieve 'Quiz' GSystemType's id -- in order to append it to 'meta_type_set' for 'QuizItem' GSystemType
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


        # --- End of handle() ---

def create_meta_type(user_id,meta_type):
    '''
    creating meta_type in database
    '''
    meta = collection.MetaType()
    meta.name = meta_type
    meta.created_by = user_id # default hardcode
    meta.modified_by = user_id
    if user_id not in meta.contributors:
        meta.contributors.append(user_id)
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
            node.save()
        else:
            print 'AttributeType',at_name,'already created'


def create_relation_type(rt_name, inverse_name, user_id, subject_type_id_list, object_type_id_list, meta_type_id = None):
    '''
    creating factory RelationType's
    '''
    rt_node = collection.RelationType.one({'_type': u'RelationType', 'name': rt_name}) 
    if rt_node is None:
        try:
            rt_node = collection.RelationType()
            rt_node.name = unicode(rt_name)
            rt_node.inverse_name = unicode(inverse_name)
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
            rt_node.save()
            print 'created', rt_name, 'as', 'RelationType'
        except Exception as e:
            print 'RelationType',rt_name,'fails to create because:',e
    else:
        # Edit already existing document
        edited=False
        if not rt_node.member_of:
            if meta_type_id:
                rt_node.member_of.append(meta_type_id)
                edited=True
                print "Edited member_of",rt_node.name
        if not rt_node.subject_type == subject_type_id_list:
            rt_node.subject_type=subject_type_id_list
            edited=True
            print "Edited subject_type of",rt_node.name,"Earlier it was ",rt_node.subject_type,"now it is",subject_type_id_list
        if not rt_node.object_type == object_type_id_list:
            rt_node.object_type=object_type_id_list
            edited=True
            print "Edited object_type of",rt_node.name,"Earlier it was",rt_node.object_type,"now it is",object_type_id_list
        if edited :
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
                subject_type_id_list.append(node_s._id)
            for rs in value['object_type']:
                node_rs = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name': rs}]})
                object_type_id_list.append(node_rs._id)
        create_relation_type(at_name, inverse_name, user_id, subject_type_id_list, object_type_id_list, meta_type_id)

def create_sts(factory_gsystem_types,user_id):
    meta_type_id = ""
    for each in factory_gsystem_types:
        name = each['name']
        meta_type_name = each['meta_type']
        meta_type = collection.GSystemType.one({'$and':[{'_type':'MetaType'},{'name':meta_type_name}]})
        if meta_type:
            meta_type_id = meta_type._id
        create_gsystem_type(name, user_id, meta_type_id)


    # For creating Browse Topic as a collection of Theme & Topic
    theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
    topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
    br_topic = collection.Node.one({'_type': 'GSystemType', 'name': 'Browse Topic'})
    if not br_topic.collection_set:
        br_topic.collection_set.append(theme_GST._id)
        br_topic.collection_set.append(topic_GST._id)
        br_topic.created_by = 1
        br_topic.modified_by = 1
        br_topic.save()

# Update type_of field to list
type_of_cursor=collection.find({'type_of':{'$exists':True}})
for object_cur in type_of_cursor:
    if type(object_cur['type_of']) == ObjectId or object_cur['type_of'] == None:
	if type(object_cur['type_of']) == ObjectId :
		collection.update({'_id':object_cur['_id']},{'$set':{'type_of':[object_cur['type_of']]}})
	else :
		collection.update({'_id':object_cur['_id']},{'$set':{'type_of':[]}})

# ===============================================================================================

# Removes n attribute if created accidently in existsing documents
collection.update({'n': {'$exists': True}}, {'$unset': {'n': ""}}, upsert=False, multi=True)

# Updates wherever modified_by field is None with default value as either first contributor or the creator of the resource
modified_by_cur = collection.Node.find({'_type': {'$nin': ['GAttribute', 'GRelation', 'node_holder', 'ToReduceDocs', 'ReducedDocs', 'IndexedWordList']}, 'modified_by': None})
if modified_by_cur.count > 0:
    for n in modified_by_cur:
	#print n, "\n"
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
    print "Deleted GST document of profile_pic"




# For adding visited_location field (default value set as []) in User Groups.
try:
    author = collection.Node.one({'_type': "GSystemType", 'name': "Author"})
    if author:
        auth_cur = collection.Node.find({'_type': 'Group', 'member_of': author._id })

        if auth_cur.count() > 0:
            for each in auth_cur:
                collection.update({'_id': each._id}, {'$set': {'_type': "Author"} }, upsert=False, multi=False)    
                print "Updated user group : ", each.name
            
        cur = collection.Node.find({'_type': "Author", 'visited_location': {'$exists': False}})

        author_cur = collection.Node.find({'_type': 'Author'})

        if author_cur.count() > 0:
            for each in author_cur:
                if each.group_type == None:
                    collection.update({'_id': each._id}, {'$set': {'group_type': u"PUBLIC", 'edit_policy': u"NON_EDITABLE", 'subscription_policy': u"OPEN"} }, upsert=False, multi=False)    
                    print "Updated user group policies :", each.name

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


## INSERTED FOR MAP_REDUCE
allIndexed = collection.IndexedWordList.find({"required_for" : "storing_indexed_words"})
if allIndexed.count() == 0:
	print "Inserting indexes"
	j=1
	while j<=27:
		obj = collection.IndexedWordList()
		obj.word_start_id = float(j)
		obj.words = {}
		obj.required_for = u'storing_indexed_words'
		obj.save()
		j+=1

# adding Task GST into start_time and end_time ATs subject_type
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


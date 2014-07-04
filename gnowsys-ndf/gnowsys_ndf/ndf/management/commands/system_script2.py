''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError


#from mongokit import IS
from gnowsys_ndf.ndf.models import *
from django_mongokit import get_database

#defining global variables
database = get_database()
collection = database[Node.collection_name]
user_id = 1
"""
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

'''imports from application folders/files '''
"""

from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.settings import META_TYPE
from gnowsys_ndf.factory_type import factory_gsystem_types, factory_attribute_types, factory_relation_types

####################################################################################################################
#global variables
#db = get_database()
#collection = db[Node.collection_name]



#for taking input json file
import json
import sys
wiki_base_url="http://en.wikipedia.org/wiki/"

def create_WikiData_WikiTopic():
	"""
	creates GSystemType: WikiData(a member_of GAPP), GSystemType Theme and Topic(a member_of factory_settings) 
	"""
	GAPP = collection.Node.one({"name": u"GAPP"})
	cursor = collection.Node.one({"_type":u"GSystemType", "name":u"WikiData"}) #change -am
	if (cursor!=None):
		print "Wikidata already exists"
		wiki_id = cursor._id
	else:
		
		GAPP_id = GAPP._id
		wiki = collection.GSystemType()
		wiki.name = u"WikiData"
		wiki.created_by = int(user_id)
		wiki.member_of.append = GAPP_id
		wiki.save()
		wiki_id = wiki._id
		print "Created a GSystemType for----> WikiData \n"
	
	cursor = collection.Node.one({"_type": u"GSystemType", "name": u"Theme"})
	if (cursor!=None):
		print "theme already exists"
		
	else:
		factory = collection.Node.one({"name": u"factory_types"})
		factory_id = factory._id
		obj = collection.GSystemType()
		obj.name = u"Theme"
		obj.created_by = int(1)
		obj.type_of.append(wiki_id)
		obj.member_of.append(factory_id)
		obj.save()
		print "Created an object of GSystem Type --> Theme \n"
	
	cursor = collection.Node.one({"_type":u"GSystemType", "name": u"WikiTopic"}) #change -am
	if(cursor!=None):
		print "WikiTopic already exists"
	else:	
		factory = collection.Node.one({"name": u"factory_types"})
                factory_id = factory._id
		obj1 = collection.GSystemType()
		obj1.name = u"WikiTopic"
		obj1.created_by = int(1)
		obj1.type_of.append(wiki_id)
		obj1.member_of.append(factory_id)
		obj1.save()
		print "Created an object of GSystemtype"


def create_AttributeType(name, data_type, user_id):
	"""
	This method creates an attribute type of given name and which will be for the given system_type(WikiData)
	The following data_types are possible:
	DATA_TYPE_CHOICES = (
    	"None",
    	"bool",
    	"basestring",
    	"unicode",
    	"int",
    	"float",
    	"long",
    	"datetime.datetime",
    	"list",
    	"dict",
    	"ObjectId",
    	"IS()"
	)
	User Id will be used for filling the created_by field.
	"""
	print "Creating an Attribute Type"
	cursor = collection.Node.one({"name":unicode(name),"_type":"AttributeType"})
	if (cursor != None):
		print "The AttributeType already exists."
	else:
		attribute_type = collection.AttributeType()
		attribute_type.name = unicode(name)
		attribute_type.data_type = data_type
		system_type = collection.Node.one({"name":u"WikiTopic","_type":"GSystemType"})
		attribute_type.subject_type.append(system_type._id)
		attribute_type.created_by = user_id
		attribute_type.modified_by = user_id
		factory_id = collection.Node.one({"name":u"factory_types","_type":"MetaType"})._id
		attribute_type.member_of.append(factory_id)
		attribute_type.save()
		"""	
		Adding the attribute type to the WikiData GSytemType attribute_set"
		"""
		system_type.attribute_type_set.append(attribute_type._id)
		print "Created the Attribute_Type " + str(name)
		
		
def create_Attribute(subject_name, attribute_type_name, object_value):
	"""
	Creating an Attribute with specified name, subject_id, attribute_type and value.
	This will create an attribute iff the attribute is not present for the same subject
	"""

	print "Creating an attribute"
	subject = collection.Node.find_one({"name":unicode(subject_name),"_type":"GSystem"})
	attribute_type_obj = collection.Node.find_one({"name": unicode(attribute_type_name), "_type": u"AttributeType"})
	#print attribute_type
	cursor = collection.Node.find_one({"_type" : "GAttribute","subject":subject._id,"attribute_type.$id":attribute_type_obj._id})
	if cursor!= None: #change-am
		print "The attribute " + unicode(cursor.name) + " already exists."
		print "-----------------------!!!!!!!!!!!!!--------------------------next---------"
	else:
		att = collection.GAttribute()
		att.subject = subject._id
		#DBref = {"$ref":Node.collection_name, "$id":attribute_type._id, "$name": attribute_type.name}
		att.attribute_type = attribute_type_obj
		att.object_value = unicode(object_value)
		print "About to create"
		att.save()
		print "Created attribute " + unicode(att.name)




	
def create_Topic(label, description, alias_list, topic_title, last_update_datetime, user_id):
	"""
	Creates a topic if it does not exist
	"""
	print "Creating a GSystem Topic"
	topic_type = collection.Node.one({"name": u"WikiTopic"})
	obj = collection.Node.one({"name": unicode(label), "_type": u"GSystem"}) #pick the topic related to wikidata

	if (obj!=None):
		print "Topic already exists"
		return
	else:
		topic_type_id = topic_type._id
		topic = collection.GSystem()
		topic.name = label
		#topic.tags = alias_list  # tags are supposed to be info about structure , categories etc , aliases are supposed to be stored into altnames
		topic.content_org= unicode(description) #content in being left untouched and content_org has descriptions in english
		topic.url = unicode(wiki_base_url)+unicode(label)
		#topic.altnames = unicode(topic_title)
		topic.created_by = int(user_id)
		topic.member_of.append(topic_type_id)
		
		string_alias=""
		for alias in alias_list:
			string_alias=string_alias+alias+"," #altnames is a comma separated list of english aliases

		topic.altnames =unicode(string_alias)
		topic.status=unicode('PUBLISHED') #by default status of each item is PUBLISHED
		topic.language=unicode('en')      #by default language is english
		topic.access_policy=unicode('PUBLIC')
		topic.save()
		
		print "Created a topic -->" + label + "\n"
		

	

def create_RelationType(name, inverse_name, subject_type_name, object_type_name, user_id):

	"""	
	Creating a RelationType with the following parameters.
	1. name - inherits Node class.
	2. inverse_name  - This is the name of the inverse of the relation.
	3. subject_type - Which Systemtype is the relation defined under.
	4. object_type - which object is the relation type defined for?
	5. User_id - the id which creates the WikiTopic RelationType.
	"""
        print "Creating a Relation Type"
        cursor = collection.Node.one({"name":unicode(name)})
        if cursor!=None:
                print "The RelationType already exists."
        else:
     	        relation_type = collection.RelationType()
                relation_type.name = unicode(name)
                system_type = collection.Node.one({"name":u"WikiTopic"})
                relation_type.subject_type.append(system_type._id)
                relation_type.inverse_name = unicode(inverse_name)
		relation_type.created_by = user_id
                relation_type.modified_by = user_id
		subject_type = collection.Node.one({"name":unicode(subject_type_name)})
		relation_type.subject_type.append(ObjectId(subject_type._id))
		object_type = collection.Node.one({"name":unicode(object_type_name)})
		relation_type.object_type.append(ObjectId(object_type._id))
                factory_id = collection.Node.one({"name":u"factory_types"})._id
                relation_type.member_of.append(factory_id)
		#relation_type.subject_applicable_nodetype('GSystem Types')
		#relation_type.object_applicable_nodetype('GSystem Types')
                relation_type.save()
                """     
                Adding the attribute type to the WikiTopic GSytemType attribute_set"
                """
                system_type.relation_type_set.append(ObjectId(relation_type._id))
                print "Created the Relation_Type " + str(name)
 

def create_Relation(subject_name, relation_type_name, right_subject_name, user_id):
	"""
	Creates a GRelation with following parameters:
	1. Subject: which GSytem class object
	2. Relation Type: The type of relation
	3. Right Subject: The subject on the right. The object related to the current object.
	"""
	print "Creating a Relation."
	relation_type = collection.Node.one({"_type":u"RelationType", "name": unicode(relation_type_name)})
	subject = collection.Node.one({"_type": u"GSystem", "name": unicode(subject_name)})
	cursor = collection.Node.find({"_type":u"GRelation", "relation_type.$id":ObjectId(relation_type._id), "subject": ObjectId(subject._id)})
>>>>>>> 2da217a01a0b8b7704c798f019ac97d67e48beec
	if cursor.count()!=0:
		print "The Relation Already exists"
	else:
		relation = collection.GRelation()
		relation.created_by = user_id
		relation.modified_by = user_id
		left_system = collection.Node.one({"name":unicode(subject_name)})
		relation.subject = ObjectId(left_system._id)
		relation_type = collection.Node.one({"name":unicode(relation_type_name), "_type":u"RelationType"})
		relation.relation_type = relation_type
		right_system = collection.Node.one({"name":unicode(right_subject_name)})
		relation.right_subject = ObjectId(right_system._id)
		relation.lang = u"en"
		relation.status = u"PUBLISHED"
		relation.save()
		print "Created a Relation " + str(relation.name)

def display_objects():
	cursor = collection.Node.find()
	for a in cursor:
		print a.name
		

class Command(BaseCommand):
	def handle(self, *args, **options):
		create_WikiData_WikiTopic()
		create_Topic(u"topic11", u"topic1desc", [u"Alias1", u"Alias2"], "Test1", None, user_id)
		create_Topic(u"topic21", u"topic2desc", [u"Alias1"], "Test2", None, user_id)
		create_AttributeType("wiki_attr11", "unicode", user_id)
		create_Attribute("topic11", "wiki_attr11", "This is the value of the wiki_attr1 field")
		create_RelationType("same_tag11", "-same_tag11", "WikiTopic", "WikiTopic", user_id) 
		create_Relation("topic11", "same_tag11", "topic21", user_id)
		create_Relation("topic21", "same_tag11", "topic11", user_id)
		print "All objects\n"
                display_objects()
beec








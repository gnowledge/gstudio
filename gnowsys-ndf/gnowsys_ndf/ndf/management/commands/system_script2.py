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
	creates GSystemType: WikiData(a member_of GAPP), GSystemType WikiTopic(a member_of factory_settings and type_of WikiData) 
	Helper method to create the WikiData GAPP and WikiTopic GSystemType.
	"""
	GAPP = collection.Node.one({"name": u"GAPP","_type":u"MetaType"})
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
	
	cursor = collection.Node.one({"_type":u"GSystemType", "name": u"WikiTopic"}) #change -am
	if(cursor!=None):
		print "WikiTopic already exists"
	else:	
		factory = collection.Node.one({"name": u"factory_types","_type":u"MetaType"})
                factory_id = factory._id
		obj1 = collection.GSystemType()
		obj1.name = u"WikiTopic"
		obj1.created_by = int(1)
		obj1.type_of.append(wiki_id)
		obj1.member_of.append(factory_id)
		obj1.save()
		print "Created an object of GSystemtype"



def create_AttributeType_for_class(name, data_type, description, property_id, language, user_id):
	"""
	FOR CLASS - GSYSTEMTYPEs
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
	Parameters:
		1. name - The name of the AttributeType that the user wants to create.
		2. data_type - The data_type of the attribute type is given here.
		3. description - The descriptive content of the AttributeType - like help_text.
		4. property_id - The unique id to refer to this attribute_type.
		5. language - What is the language that the user wants to harvest.
		6. User Id: Which user is creating the topic.
	"""
	print "Creating an Attribute Type"
	data_type_list = ["None","bool","basestring","unicode",	"int", "float", "long",	"datetime.datetime", "list", "dict", "ObjectId", "IS()"]
	cursor = collection.Node.one({"label":unicode(property_id),"_type":"AttributeType"})
	if (cursor != None):
		print "The AttributeType already exists."
		return True
	else:
		attribute_type = collection.AttributeType()
		attribute_type.name = unicode(name)
		if data_type in data_type_list: 
			attribute_type.data_type = data_type
		else:
			attribute_type.data_type = "unicode"
		system_type = collection.Node.one({"name":u"WikiData","_type":"GSystemType"})
		attribute_type.subject_type.append(system_type._id)
		system_type_2 = collection.Node.one({"name":u"WikiTopic","_type":"GSystemType"})
		attribute_type.subject_type.append(system_type_2._id)
		attribute_type.created_by = user_id
		attribute_type.modified_by = user_id
		factory_id = collection.Node.one({"name":u"factory_types","_type":u"MetaType"})._id
		attribute_type.member_of.append(factory_id)
		attribute_type.verbose_name = name
		attribute_type.altnames = unicode(property_id)
		attribute_type.null = True
		attribute_type.blank = True
		attribute_type.help_text = unicode(description)
		attribute_type.label = unicode(property_id) #Adding property_id pcode
		attribute_type.unicode = False
		attribute_type.default = unicode("None")
		attribute_type.auto_now = False
		attribute_type.language=unicode(language)
		attribute_type.save()
		"""	
		Adding the attribute type to the WikiData GSytemType attribute_set"
		"""
		system_type.attribute_type_set.append(attribute_type._id)
		system_type_2.attribute_type_set.append(attribute_type._id)
		print "Created the Attribute_Type " + unicode(name)
		return False
		


def create_AttributeType(name, data_type, description, property_id,language, user_id):
	"""
	FOR TOPIC - GSYSTEMs
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

	Parameters:
		1. name - The name of the AttributeType that the user wants to create.
		2. data_type - The data_type of the attribute type is given here.
		3. description - The descriptive content of the AttributeType - like help_text.
		4. property_id - The unique id to refer to this attribute_type.
		5. language - What is the language that the user wants to harvest.
		6. User Id: Which user is creating the topic.
	"""
	print "Creating an Attribute Type"
	data_type_list = ["None","bool","basestring","unicode",	"int", "float", "long",	"datetime.datetime", "list", "dict", "ObjectId", "IS()"]
	cursor = collection.Node.one({"label":unicode(property_id),"_type":"AttributeType"})
	if (cursor != None):
		print "The AttributeType already exists."
		return True
	else:
		attribute_type = collection.AttributeType()
		attribute_type.name = unicode(name)
		if data_type in data_type_list:
			attribute_type.data_type = data_type
		else:
			attribute_type.data_type = "unicode"
		system_type = collection.Node.one({"name":u"WikiData","_type":"GSystemType"})
		attribute_type.subject_type.append(system_type._id)
		system_type_2 = collection.Node.one({"name":u"WikiTopic","_type":"GSystemType"})
		attribute_type.subject_type.append(system_type_2._id)
		attribute_type.created_by = user_id
		attribute_type.modified_by = user_id
		factory_id = collection.Node.one({"name":u"factory_types","_type":"MetaType"})._id
		attribute_type.member_of.append(factory_id)
		attribute_type.verbose_name = name
		attribute_type.altnames = unicode(property_id)
		attribute_type.null = True
		attribute_type.blank = True
		attribute_type.help_text = unicode(description)
		attribute_type.label = unicode(property_id) #Adding property_id pcode
		attribute_type.unicode = False
		attribute_type.default = unicode("None")
		attribute_type.auto_now = False
		attribute_type.language=unicode(language)
		attribute_type.save()
		"""	
		Adding the attribute type to the WikiData GSytemType attribute_set"
		"""
		system_type.attribute_type_set.append(attribute_type._id)
		system_type_2.attribute_type_set.append(attribute_type._id)
		print "Created the Attribute_Type " + unicode(name)
		return False

		
		
def create_Attribute(subject_name, attribute_type_name, object_value, language, user_id):
	"""
	Creating an Attributpe with specified name, subject_id, attribute_type and value.
	This will create an attribute iff the attribute is not present for the same subject
		1. subject_name - The name of the topic for which the user wants to create the attribute.
		2. attribute_type_name - The name of the attribute_type for which the user wants to create the attribute value.
		3. object_value - The Value of the object.
		4. language - What is the language that the user wants to harvest.
		5. User Id: Which user is creating the topic.
		Returns -
		False :  as the topic already existed. 
		True:If the topic created during the function call.
	"""

	print "Creating an attribute"
	#subject = collection.Node.find_one({"name":unicode(subject_name),"_type":"GSystem"})
	#it's me
	subject = collection.Node.find_one({"name":unicode(subject_name)})
	#it's me
	#print "Subject::\n" + str(subject)
	attribute_type_obj = collection.Node.find_one({"name": unicode(attribute_type_name), "_type": u"AttributeType"})
	#print "Attribute_type::\n" + str(attribute_type_obj)	
	if subject is None:
		print "The attribute " + unicode(subject_name) + "--" + unicode(attribute_type_name) + "--" + unicode(object_value) + " could not be created."
		#print "-----------------------!!!!!!!!!!!!!--------------------------next---------"
		return True
	
	elif attribute_type_obj is None:
		print "The attribute " + unicode(subject_name) + "--" + unicode(attribute_type_name) + "--" + unicode(object_value) + " could not be created."
		#print "-----------------------!!!!!!!!!!!!!--------------------------next---------"
		return True

	
	cursor = collection.Node.find_one({"_type" : u"GAttribute","subject": ObjectId(subject._id),"attribute_type.$id":ObjectId(attribute_type_obj._id)})
	if cursor!= None:
		print "The attribute " + unicode(cursor.name) + " already exists."
		#print "-----------------------!!!!!!!!!!!!!--------------------------next---------"
		return True
	
	
	else:
		att = collection.GAttribute()
		att.created_by = user_id
		att.modified_by = user_id
		att.subject = ObjectId(subject._id)
		att.lang = language
		att.status = u"PUBLISHED"
		#DBref = {"$ref":Node.collection_name, "$id":attribute_type._id, "$name": attribute_type.name}
		att.attribute_type = attribute_type_obj
		att.object_value = unicode(object_value)
		#print "About to create"
		#it's me	
		try:
			att.save()
			print "Created attribute " + unicode(att.name)
		except Exception as e:
			print "Could not create an attribute" + unicode(att.name)
			print e
			#call log file method
			return True

		return False
		#it's me



	
def create_Topic(label, description, alias_list, topic_title, last_update_datetime, user_id):
	"""

	Creates a topic if it does not exist.
		Returns -
		True : false as the topic already existed. 
		False:If the topic created during the function call.
	Parameters:
		1. label - The name of the topic which the user wants to create.
		2. description - The descriptive content of the topic.
		3. alias_list - The Aliases or the Alternate names of the topic.
		4. class_id - The unique Q id of the topic.
		5. last_update_datetime - can be used to identify whether the object was existing previously. Helpful in incremental dumps. This makes this script an incremental script.
		6. User Id: Which user is creating the topic.
	"""
	print "Creating a GSystem Topic"
	topic_type = collection.Node.one({"name": u"WikiTopic","_type":u"GSystemType"})
	obj = collection.Node.find_one({"name": unicode(label)}) #pick the topic related to wikidata

	if (obj!=None):
		print "Topic already exists"
		return True
	else:
		topic_type_id = topic_type._id
		topic = collection.GSystem()
		topic.name = label
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
		return False
		
def create_Class(label, description, alias_list, class_id, last_update_datetime, user_id):
	"""
	Creates a Class if it does not exist
	Parameters:
		1. label - The name of the class which the user wants to create.
		2. description - The descriptive content of the class.
		3. alias_list - The Aliases or the Alternate names of the class
		4. class_id - The unique Q id of the class.
		5. last_update_datetime - can be used to identify whether the object was existing previously. Helpful in incremental dumps. This makes this script an incremental script.
		6. User Id: Which user is creating the Class.
	"""
	print "Creating a GSystemType Class"
	topic_type = collection.Node.one({"name": u"WikiData","_type":u"GSystemType"})
	topic_type_id = topic_type._id
	obj = collection.Node.find_one({"name": unicode(label), "_type": u"GSystemType"}) #pick a class which is a member of wikidata

	if (obj!=None):
		print "Class already exists"
		return True
	else:		
		class_obj = collection.GSystemType()
		class_obj.name = unicode(label)
		class_obj.content_org= unicode(description) #content in being left untouched and content_org has descriptions in english
		class_obj.created_by = int(user_id)
		class_obj.modified_by = int(user_id)
		class_obj.url = unicode(wiki_base_url)+unicode(label)
		class_obj.status=unicode('PUBLISHED') #by default status of each item is PUBLISHED
		class_obj.language=unicode('en')      #by default language is english
		string_alias=""
		for alias in alias_list:
			string_alias=string_alias+alias+"," #altnames is a comma separated list of english aliases

		class_obj.altnames = unicode(string_alias)
		class_obj.type_of.append(topic_type_id) #The GSystemType of class that is being created should be a part of the WikiData GApp.
		class_obj.access_policy=unicode('PUBLIC')
		factory = collection.Node.one({"name": u"factory_types","_type":u"MetaType"})
                factory_id = factory._id
		wikidata = collection.Node.one({"name":u"WikiData", "_type":"GSystemType"})
		class_obj.member_of.append(ObjectId(wikidata._id))
		class_obj.member_of.append(ObjectId(factory_id))	
		#Adding the WikiData GSystemType as a member of the class resolves the problem of creating attributes for a GSystemType(i.e. the class))
		class_obj.last_update = last_update_datetime
		class_obj.save()
		
		print "Created a class -->" + label + "\n"
		return False
		




def create_RelationType(name, inverse_name, subject_type_name, object_type_name,property_id,language, user_id):

	"""	
	Creating a RelationType with the following parameters.
	1. name - inherits Node class.
	2. inverse_name  - This is the name of the inverse of the relation.
	3. subject_type_name - Which Systemtype is the relation defined under.
	4. object_type_name - which object is the relation type defined for?
	5. property_id - The uniques Id of the attribute
	6. language - What is the language that the user wants to harvest.
	7. User_id - the id which creates the WikiTopic RelationType.
	"""
        print "Creating a Relation Type"
        cursor = collection.Node.one({"name":unicode(name),"_type":u"RelationType"})
        if cursor!=None:
                print "The RelationType already exists."
		return True
        else:
     	        relation_type = collection.RelationType()
                relation_type.name = unicode(name)
                system_type = collection.Node.one({"name":u"WikiTopic","_type":u"GSystemType"})
                relation_type.subject_type.append(system_type._id)
		system_type_2 = collection.Node.one({"name":u"WikiData","_type":u"GSystemType"})
                relation_type.subject_type.append(system_type_2._id)
                relation_type.inverse_name = unicode(inverse_name)
		relation_type.created_by = user_id
                relation_type.modified_by = user_id
		subject_type = collection.Node.one({"name":unicode(subject_type_name),"_type":u"GSystemType"})
		relation_type.subject_type.append(ObjectId(subject_type._id))
		object_type = collection.Node.one({"name":unicode(object_type_name),"_type":u"GSystemType"})
		#print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"+ str(object_type._id) +" ,",object_type.name
		relation_type.object_type.append(ObjectId(object_type._id))
                factory_id = collection.Node.one({"name":u"factory_types","_type":u"MetaType"})._id
                relation_type.member_of.append(factory_id)

                relation_type.language=unicode(language)
                relation_type.altnames=unicode(property_id)
		#relation_type.subject_applicable_nodetype('GSystem Types')
		#relation_type.object_applicable_nodetype('GSystem Types')
                relation_type.save()
                """     
                Adding the attribute type to the WikiTopic GSytemType attribute_set"
                """
                system_type.relation_type_set.append(ObjectId(relation_type._id))
		system_type_2.relation_type_set.append(ObjectId(relation_type._id))
                print "Created the Relation_Type " + unicode(name)
		return False

 

def create_Relation(subject_name, relation_type_name, right_subject_name, user_id):
	"""
	Creates a GRelation with following parameters:
	1. Subject: which GSytem class object
	2. Relation Type: The type of relation
	3. Right Subject: The subject on the right. The object related to the current object.
	4. User Id: Which user is creating the Relation.
	
	IMPORTANT: The same method s used to cerate relations between 2 GSystemTypes or a GSystemType and a GSystem.
	"""
	print "Creating a Relation."
	relation_type = collection.Node.one({"_type":u"RelationType", "name": unicode(relation_type_name)})
	subject = collection.Node.one({"_type": u"GSystem", "name": unicode(subject_name)})
	
	if subject is None:
		print "The relation " + unicode(subject_name) + "--" + unicode(relation_type_name) + "--" + unicode(right_subject_name) + " could not be created."
		#print "-----------------------!!!!!!!!!!!!!--------------------------next---------"
		return True
	
	elif relation_type is None:
		print "The relation " + unicode(subject_name) + "--" + unicode(relation_type_name) + "--" + unicode(right_subject_name) + " could not be created."
		#print "-----------------------!!!!!!!!!!!!!--------------------------next---------"
		return True


	cursor = collection.Node.find({"_type":u"GRelation", "relation_type.$id":ObjectId(relation_type._id), "subject": ObjectId(subject._id)})
	if cursor.count()!=0:
		print "The Relation Already exists"
		return True
	else:
		relation = collection.GRelation()
		relation.created_by = user_id
		relation.modified_by = user_id
		left_system = collection.Node.find_one({"name":unicode(subject_name)})
		relation.subject = ObjectId(left_system._id)
		relation_type = collection.Node.find_one({"name":unicode(relation_type_name), "_type":u"RelationType"})
		relation.relation_type = relation_type
		right_system = collection.Node.find_one({"name":unicode(right_subject_name)})
		relation.right_subject = ObjectId(right_system._id)
		relation.lang = u"en"
		relation.status = u"PUBLISHED"
		#it's me
		try:
			relation.save()
			print "Created a Relation " + unicode(relation.name)
		except Exception as e:
			print "Could not create a relation-->" + unicode(relation.name)
	
			print e
			#call log file method
			return True

		return False
		#it's me

def populate_tags(label,property_value_for_relation):
	"""
	To populate tags of the object given by label.tags is a list field and the values will be appended
	in the list.(actually the right_subject_name of P31 and P279 are being appended as tags to give a sense 
	of theme, category hierarchy etc.)
	Parameter passed to the function -
	1)label - name of item for which tag is to eb appended.
	2)property_value_for_relation - value to be appended in tag.It is a human readable english value.
	"""
	obj = collection.Node.find_one({"name":unicode(label)})
	if obj:
		obj.tags.append(unicode(property_value_for_relation))
		obj.modified_by=int(1)
		obj.save()



def populate_location(label,property_id,property_value,user_id):
	obj = collection.Node.find_one({"_type":u"GSystem","name":unicode(label)})
	geo_json=[
    	{
        	"geometry": 
        	{
            	"type": "Point",
            	"coordinates": []
       		},
        	"type": "Feature",
        	"properties": 
        	{
            	"description":"",
            	"id": ""
        	}
    	}
	]

	geo_json[0]["geometry"]["coordinates"].append(property_value["longitude"])
	geo_json[0]["geometry"]["coordinates"].append(property_value["latitude"])
	geo_json[0]["properties"]["description"]=label	
	geo_json[0]["properties"]["id"]=property_id
	obj.location =geo_json
	obj.modified_by =user_id
	obj.save()








def item_exists(label):
	"""	
	Returns boolean value to indicate if a GSystem with the given name exists or not"
	"""	

	object = collection.Node.find_one({"type":u"GSystem","name":unicode(label)})
	if object !=None:
		return True
	else:
		return False


def display_objects():
	"""
	This is a helper method for debugging the code. This displays all the objects existing in the database so that the user does not have to use the shell to debug.
	"""
	cursor = collection.Node.find()
	for a in cursor:
		print a.name
		
def item_exists(label):
	"""	
	Returns boolean value to indicate if a GSystem with the given name exists or not
	"""	

	obj = collection.Node.find_one({"_type":u"GSystem","name":unicode(label)})
	if obj !=None:
		return True
	else:
		#It may be the case that a class is the item
		obj = collection.Node.find_one({"_type": u"GSystemType", "name": unicode(label)})
		if obj != None:
			return True
		else:
			return False



def populate_tags(label,property_value_for_relation):
	"""
	To populate tags of the object given by label.tags is a list field and the values will be appended
	in the list.(actually the right_subject_name of P31 and P279 are being appended as tags to give a sense 
	of theme, category hierarchy etc.)
	Parameter passed to the function 
	
		1)label - name of item for which tag is to eb appended.
		2)property_value_for_relation - value to be appended in tag.It is a human readable english value.
	"""
	obj = collection.Node.find_one({"name":unicode(label)})
	if obj:
		obj.tags.append(unicode(property_value_for_relation))
		obj.modified_by=int(1)
		obj.save()



def populate_location(label,property_id,property_value,user_id):
	"""
	This method helps populate the Location in the Topic in the specific GeoJSON format used in the MongoDB database of the GSystem structure.
	Parameters:
		1. label - label/name of the topic
		2. property_id - What is the id of the Location property
		3. property_value - The actual longitude, latitude values
		4. User Id - Which user is running the script and creating the topic.

	"""
	obj = collection.Node.find_one({"_type":u"GSystem","name":unicode(label)})
	geo_json=[
    	{
        	"geometry": 
        	{
            	"type": "Point",
            	"coordinates": []
       		},
        	"type": "Feature",
        	"properties": 
        	{
            	"description":"",
            	"id": ""
        	}
    	}
	]

	geo_json[0]["geometry"]["coordinates"].append(property_value["longitude"])
	geo_json[0]["geometry"]["coordinates"].append(property_value["latitude"])
	geo_json[0]["properties"]["description"]=label		
	geo_json[0]["properties"]["id"]=property_id
	obj.location = geo_json

	obj.modified_by =user_id
	obj.save()


def get_class(label, class_id):
	"""
	Helper function to return the class with the specified name/label
	"""
	obj = collection.Node.find_one({"_type":u"GSystemType","name":unicode(label)})
	if obj:
		return obj

def get_topic(label):
	"""
	Helper function to return the Topic with the specified name/label
	"""
	obj = collection.Node.find_one({"_type":u"GSystem","name":unicode(label)})
	if obj:
		return obj


class Command(BaseCommand):
	def handle(self, *args, **options):
		"""
		Some test cases that are not a part of the main harvesting script

		"""
		create_WikiData_WikiTopic()
		create_Topic(u"topic11", u"topic1desc", [u"Alias1", u"Alias2"], "Test1", None, user_id)
		create_Topic(u"topic21", u"topic2desc", [u"Alias1"], "Test2", None, user_id)
		create_Class(u"class1", u"Description for class1", [u"ClassAlias1"], "Test-Q0", None, user_id)
		create_AttributeType("wiki_attr11", "unicode", "This is the desc.", "P<id>12","en", user_id)
		create_AttributeType_for_class("class_wiki_attr1", "unicode", "This is the desc for wiki_attr1.", "P<id>1","en", user_id)
		create_Attribute("topic11", "wiki_attr11", "This is the value of the wiki_attr1 field", "en", user_id)
		create_Attribute("topic21", "wiki_attr11", "This is the value of the wiki_attr2 field", "en", user_id)
		create_RelationType("same_tag11", "-same_tag11", "WikiTopic", "WikiTopic", "P<id>1", "en", user_id) 
		create_Relation("topic11", "same_tag11", "topic21", user_id)
		create_Relation("topic21", "same_tag11", "topic11", user_id)
		print "All objects\n"
                display_objects()









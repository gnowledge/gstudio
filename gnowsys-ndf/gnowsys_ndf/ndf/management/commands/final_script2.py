''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from mongokit import IS

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node, GSystemType
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.ndf.models import DATA_TYPE_CHOICES, QUIZ_TYPE_CHOICES_TU
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.settings import META_TYPE
from gnowsys_ndf.factory_type import factory_gsystem_types, factory_attribute_types, factory_relation_types


import datetime
#from dateutil.parser import parse
from mongokit import Collection
from gnowsys_ndf.ndf.models import *

db = get_database()
collection = get_database()[GSystem.collection_name]
import csv
import os
import urllib2
import json
import pprint

from system_script2 import *



#relative path of file
fn = os.path.join(os.path.dirname(__file__), '../../static/ndf/wikidata/list_of_objects')
log_file_path = os.path.join(os.path.dirname(__file__), '../../static/ndf/wikidata/wikidata_log.txt')
my_log = open(log_file_path, "w")
log_flag = 0
gen_url_json="http://www.wikidata.org/wiki/Special:EntityData/"
gen_url_page="http://www.wikidata.org/wiki/"
language ="en" #this script is scalable and can be run for any given language .All relevant extracting functions will extract info in that language only.

commonsMedia_base_link="http://commons.wikimedia.org/wiki/File:"
#url="http://www.wikidata.org/wiki/Special:EntityData"

def json_parse(url_json):
	'''
	This function simply print out the url being passed to it as a parameter.
	It then extracts the json availbale  at that url and prints out the json in indented form.
	'''
	js={}
	try:
		j = urllib2.urlopen(url_json)
		js = json.load(j)
	except (ValueError, KeyError, TypeError):
   		print "JSON format error"
	
	return js

def log_topic_created(label, log_flag):	
	captcha = "#"
	while log_flag != 0:
		captcha += "#"
		log_flag-=1
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
	my_log.write(str(captcha) + unicode(mylabel) + "---Topic CREATED\n")

def log_topic_exists(label, log_flag):
        captcha = "#"
        while log_flag != 0:
                captcha += "#"
                log_flag-=1
        mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
	my_log.write(str(captcha) + unicode(mylabel) + "---Topic EXISTS\n")

def log_attributeType_created(label, log_flag):
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
	captcha += "-"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---AttributeType CREATED\n")

def log_attributeType_exists(label, log_flag):
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
	captcha += "-"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---AttributeType EXISTS\n")

def log_attribute_created(label, log_flag):
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "@"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---Attribute CREATED\n")

def log_attribute_exists(label, log_flag):
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "@"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---Attribute EXISTS\n")


def log_relationType_created(label, log_flag):
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "$"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---RelationType CREATED\n")

def log_relationType_exists(label, log_flag):
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "$"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---RelationType EXISTS\n")

def log_relation_created(label, log_flag):
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "*"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---Relation CREATED\n")

def log_relation_exists(label, log_flag):
        captcha = " "
        while log_flag != 1:
                captcha += " "
                log_flag-=1
        captcha += "*"
	mylabel = u' '.join((label, ' ')).encode('utf-8').strip()
        my_log.write(str(captcha) + unicode(mylabel) + "---Relation EXISTS\n")


def log_inner_topic_start(log_flag):
        captcha = "-"
        my_log.write("\n")
        while log_flag != 0:
                captcha += "-"
                log_flag-=1
        my_log.write(str(captcha) + "-----------------------------------------------------------------------\n")

def log_inner_topic_end(log_flag):
        captcha = "-"
        my_log.write("\n")
        while log_flag != 0:
                captcha += "-"
                log_flag-=1
        my_log.write(str(captcha) + "_______________________________________________________________________\n")



def log_outer_topic(log_flag):
        captcha = "-"
        my_log.write("\n")
        while log_flag != 0:
                captcha += "-"
                log_flag-=1
        my_log.write(str(captcha) + "-----------------------------------------------------------------------\n")
	my_log.write(str(captcha) + "-----------------------------------------------------------------------\n")

def json_parse(url_json):
	'''
	This function simply print out the url being passed to it as a parameter.
	It then extracts the json availbale  at that url and prints out the json in indented form.
	'''
	js={}
	try:
		j = urllib2.urlopen(url_json)
		js = json.load(j)
	except (ValueError, KeyError, TypeError):
   		print "JSON format error"
	
	return js


def extract_aliases(json_obj,topic_title,language_choice):
	alias_dict={}
	en_list=[]

	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="aliases":
			alias_dict=v
	
	for key,value in alias_dict.items():
		if key == language_choice:
			for dict1 in value:
				for key1,value1 in dict1.items():
					if key1=="value":
						en_list.append(value1)

	return en_list  # returns a list of english aliases for the given item


def extract_labels(json_obj,topic_title,language_choice):
	

	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="labels":
			label_dict=v
	
	
	#code to extract labels
	
	for key,val in label_dict.items():
		if key.startswith(language_choice)==True:
			for key1,val1 in val.items():
				if key1=="value":
					return val1 # returns an english label for the item
					


def extract_modified(json_obj,topic_title):
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():
		if k=="modified":
			return v #return date time of last update of wiki data page but data type is still not clear



def extract_type(json_obj,topic_title):
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():
		if k=="type":
			return v #return type of entity like say "item"

def extract_pageid(json_obj,topic_title):
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():
		if k=="pageid":
			return v #return pageid of the item


def extract_namespace(json_obj,topic_title):
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():
		if k=="ns":
			return v #return  namespace of the item

"""
def extract_claims(json_obj,topic_title):
	prop_dict={}
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="claims":
			prop_dict=v
			break

	if prop_dict!={}:
		for key,val in prop_dict.items():
    		url_prop= gen_url_json+key+".json"
    		#print url_prop

"""


def extract_descriptions(json_obj,topic_title,language_choice):
	
	description=""
	description_dict={}
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="descriptions":
			description_dict=v

	for key,value in description_dict.items():
		if key.startswith(language_choice):
			for key1,val1 in value.items():
				if key1=="value":
						description+=" - "+val1
	
	return description	




		

def extract_datatype_from_property(property_value_list):
	"""
	property_value_list is a list that has been extracted from the object's json
	This function returns the datatype of one particular property , that property whose value has been passed to this function as a list
	"""
	for element in property_value_list:
		if(type(element)) == type({}):
			for k,v in element.items():
				if k=="mainsnak":
					for k1,v1 in v.items():
						if k1=="datatype":
							return v1

def extract_from_property_value(property_value_list):
	"""
	property_value_list is a list that has been extracted from the object's json
	"""
	for element in property_value_list:
		if(type(element)) == type({}):
			for k,v in element.items():
				if k=="mainsnak":
					for k1,v1 in v.items():
						if k1=="datatype":
							if v1=="wikibase-item":
								return 3  # RelationType and Relation will have to be created
							elif v1=="globe-coordinate" :
								return 2  # location field of the GSystemType will have to filled
							else:
								return 1 #all others for which AttributeType and Attributes will be created



def extract_property_value(property_value_list):
	for element in property_value_list:
		if(type(element)) == type({}):
			for k,v in element.items():
				if k=="mainsnak":
					for k1,v1 in v.items():
						if k1=="datavalue":
							for k2,v2 in v1.items():
								if k2=="value":
									return v2


def extract_value_for_relation(property_value_list):
	for element in property_value_list:
		if(type(element)) == type({}):
			for k,v in element.items():
				if k=="mainsnak":
					for k1,v1 in v.items():
						if k1=="datavalue":
							for k2,v2 in v1.items():
								if k2=="value":
									for k3,v3 in v2.items():
										if k3=="numeric-id":
											return v3


def property_create_AttributeType(property_id,property_data_type,json_obj):
	"""
	json_obj is actually the json object of that property
	TO DO :mapping of property)_data_type is to be done so that all data types of wikidata correspond to mongodb types
	eg -time -datetime.datetime()

	"""
	if(json_obj):
		property_alias_list=extract_aliases(json_obj,property_id,language)
		property_label =extract_labels(json_obj,property_id,language)
		property_description =extract_descriptions(json_obj,property_id,language)
		property_last_update =extract_modified(json_obj,property_id)
		property_entity_type =extract_type(json_obj,property_id)
		property_namespace =extract_namespace(json_obj,property_id)
		attribute_type_exists = create_AttributeType(property_label, property_data_type,property_description,property_id,language, user_id)
		if attribute_type_exists:
			log_attributeType_exists(property_label, log_flag)
		else:
			log_attributeType_created(property_label, log_flag)

		



def property_create_Attribute(label,property_id,property_value,property_json):
	property_label =extract_labels(property_json,property_id,language)
	attribute_exists = create_Attribute(label, property_label, property_value, language, user_id)
	if attribute_exists:
        	log_attribute_exists(property_label, log_flag)
        else:
                log_attribute_created(property_label, log_flag)



def property_create_RelationType(property_id,property_json):
	property_label = extract_labels(property_json,property_id,language)
	inverse_name="-"+property_label
	relation_type_exists = create_RelationType(property_label, inverse_name, "WikiTopic", "WikiTopic",property_id,language, user_id)
	if relation_type_exists:
        	log_relationType_exists(property_label, log_flag)
       	else:
        	log_relationType_created(property_label, log_flag)





def property_create_Relation(label,property_id,property_value,property_json):
	property_label=extract_labels(property_json,property_id,language)
	property_value =unicode("Q")+unicode(property_value)
	right_json_url=gen_url_json+str(property_value)+".json"

	print property_id+"%%%%%%%%%%%%%%",right_json_url
	right_json=json_parse(right_json_url) #property_value is supposed to be the id of the right subject in case of a relation

	right_subject_name=extract_labels(right_json,property_value,language)
	print "$$$$$$$$",right_subject_name," ",property_value
	log_inner_topic_start(log_flag)
	if right_subject_name!=None:
		intitiate_new_topic_creation(right_json,property_value,language)
		log_inner_topic_end(log_flag)
		relation_exists = create_Relation(label, property_label, right_subject_name, user_id)
			if relation_exists:
                log_relation_exists(property_label, log_flag)
        	else:
                log_relation_created(property_label, log_flag)

	else:
		print "the right subject is not an item of english, is not supposed to be created"
		#create a log function








def extract_property_json(json_obj,label,topic_title):
	claim_dict={}
	Result =json_obj['entities'][str(topic_title)]

	for k,v in Result.items():	
		if k =="claims":
			claim_dict=v


	for k,v in claim_dict.items():
		property_id = k
		property_json_url =gen_url_json+property_id+".json"
		property_json =json_parse(property_json_url)
		property_value_list =v
		flag=-1
		flag=extract_from_property_value(property_value_list)
		property_value =extract_property_value(property_value_list) #property_value has the value of that property fpr a particular object
		global log_flag
		log_flag += 1

		if flag==1: #attribute has to be made
			property_data_type = extract_datatype_from_property(property_value_list)
			#print topic_title," ",property_id," ",label," - ",property_data_type ," :",property_value
			#print property_data_type

			property_create_AttributeType(property_id,property_data_type,property_json) #assuming that the name of the attribute type id the property id like say P131
			property_create_Attribute(label,property_id,property_value,property_json) #entire triple is being passed as a parameter
		
		
		if flag==3: #relation has to be made
			property_value_for_relation=extract_value_for_relation(property_value_list)
			property_create_RelationType(property_id,property_json)
			property_create_Relation(label,property_id,property_value_for_relation,property_json)

		log_flag -= 1
		
			if property_id=="P31" or property_id=="P279":
				populate_tags(label,property_value_for_relation)
			

def create_topic_id():
	"""
	This function is just called once , directly from main so that the topic_id is created as a AttributeType
	"""

	attribute_type_name ="topic_id"
	attribute_type_data_type ="unicode"
	user_id =int(1)
	create_AttributeType(attribute_type_name, attribute_type_data_type,"_id referred in Wikidata","topic_id","en", user_id)
	


def initiate_new_topic_creation(json_obj,topic_title,language):
	alias_list=extract_aliases(json_obj,topic_title,language)
	label=extract_labels(json_obj,topic_title,language)	
	description =extract_descriptions(json_obj,topic_title,language)
	#extract_claims(json_obj,topic_title)
	last_update =extract_modified(json_obj,topic_title)
	entity_type =extract_type(json_obj,topic_title)
	page_id =extract_pageid(json_obj,topic_title)
	namespace =extract_namespace(json_obj,topic_title)
	global log_flag
	log_flag += 1

	if label!=None:
		topic_exists = create_Topic(label, description, alias_list, topic_title, None, int(1))
		if topic_exists== True:
			log_topic_exists(label, log_flag)
		if topic_exists == False:
			log_topic_created(label, log_flag)
			create_Attribute(label, "topic_id", topic_title, language, user_id)
			extract_property_json(json_obj,label,topic_title)


def read_file():
	with open(fn,'rb') as f:
		r = csv.reader(f,delimiter ='\n')
		for row in r:
			for topic_title in row:
				if topic_title.startswith('Q')==True: #first line of wiki file has some metadata
					url_json= gen_url_json+topic_title+".json"	#creating url of json by appending words to it to make a proper link
					url_page=gen_url_page+topic_title #creating url of the wikidata page itself
					json_obj=json_parse(url_json)
					if(json_obj):
						global log_flag
						log_flag = 0
						intitiate_new_topic_creation(json_obj,topic_title,language)
						log_outer_topic(log_flag)


					else:
						print "empty json returned"
						continue


class Command(BaseCommand):
	def handle(self, *args, **options):

		create_WikiData_WikiTopic()
		create_topic_id()

		read_file()		# read the file with list of items starting with Q
		

		


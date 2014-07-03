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


def extract_claims(json_obj,topic_title):
	
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="claims":
			prop_dict=v
			break


	for key,val in prop_dict.items():
    		url_prop= gen_url_json+key+".json"
    		#print url_prop




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
								return 0  # RelationType and Relation will have to be created
							elif v1=="globe-coordinate" :
								return 1  # location field of the GSystemType will have to filled
							else:
								return 2 #all others for which AttributeType and Attributes will be created



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

		create_AttributeType(property_label, property_data_type, user_id)

def extract_property_json(json_obj,label,topic_title):
	claim_dict={}
	Result =json_obj['entities'][str(topic_title)]
	
	for k,v in Result.items():	
		if k =="claims":
			claim_dict=v


	for k,v in claim_dict.items():
		property_id =k
		property_json_url =gen_url_json+property_id+".json"
		property_json =json_parse(property_json_url)
		property_value_list =v
		label = extract_labels(property_json,property_id,language)
		flag=-1
		flag=extract_from_property_value(property_value_list)
		property_value =extract_property_value(property_value_list) #property_value has the value of that property fpr a particular object
		if flag==2: #relation has to be made
			property_data_type=extract_datatype_from_property(property_value_list)
			#print topic_title," ",property_id," ",label," - ",property_data_type ," :",property_value
			print property_data_type
			#property_create_AttributeType(property_id,property_datatype,property_json) #assuming that the name of the attribute type id the property id like say P131
			#property_create_Attribute(label,property_id,property_value) #entire triple is being passed as a parameter
		





def create_topic_id():
	"""
	This function is just called once , directly from main so that the topic_id is created as a AttributeType
	"""

	attribute_type_name ="topic_id"
	attribute_type_data_type ="unicode"
	user_id =int(1)
	create_AttributeType(attribute_type_name, attribute_type_data_type, user_id)





>>>>>>> aa314071f624dec1cd30b10a50a481fe8d24854f

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
						alias_list=extract_aliases(json_obj,topic_title,language)
						#print alias_en_list
						label=extract_labels(json_obj,topic_title,language)
						#print label_en	
						description =extract_descriptions(json_obj,topic_title,language)
						extract_claims(json_obj,topic_title)
						last_update =extract_modified(json_obj,topic_title)
						entity_type =extract_type(json_obj,topic_title)
						page_id =extract_pageid(json_obj,topic_title)
						namespace =extract_namespace(json_obj,topic_title)

						
						if label!=None :
							#create_Topic(label, description, alias_list, topic_title, None, int(1))
							#	create_Attribute(label, "topic_id", topic_title)
							
							extract_property_json(json_obj,label,topic_title)


					else:
						print "empty json returned"
						continue


class Command(BaseCommand):
	def handle(self, *args, **options):

		#create_WikiData_Theme_Topic()
		#create_topic_id()

		read_file()		# read the file with list of items starting with Q
		

		


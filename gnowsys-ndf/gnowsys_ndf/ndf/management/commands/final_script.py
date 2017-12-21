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
from system_script import *


#relative path of file
fn = os.path.join(os.path.dirname(__file__), '../../static/ndf/wikidata/list_of_objects')

gen_url_json="http://www.wikidata.org/wiki/Special:EntityData/"
gen_url_page="http://www.wikidata.org/wiki/"
#url="http://www.wikidata.org/wiki/Special:EntityData"



def extract_aliases(json_obj,topic_title):
	alias_dict={}
	en_list=[]

	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="aliases":
			alias_dict=v
	
	for key,value in alias_dict.items():
		if key == "en":
			for dict_en in value:
				for key1,value1 in dict_en.items():
					if key1=="value":
						en_list.append(value1)

	return en_list  # returns a list of english aliases for the given item


def extract_labels(json_obj,topic_title):
	

	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="labels":
			label_dict=v
	
	
	#code to extract labels
	
	for key,val in label_dict.items():
		if key.startswith("en")==True:
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




def extract_descriptions(json_obj,topic_title):
	
	en_description=""
	Result =json_obj['entities'][str(topic_title)]
	for k,v in Result.items():	
		if k =="descriptions":
			description_dict=v

	for key,value in description_dict.items():
		if key.startswith("en"):
			for key1,val1 in value.items():
				if key1=="value":
						en_description+=" - "+val1
	
	return en_description	


def json_parse(url_json	):
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


#list_of_urls =[]

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
						alias_en_list=extract_aliases(json_obj,topic_title)
						#print alias_en_list
						label_en=extract_labels(json_obj,topic_title)
						print label_en	
						en_description =extract_descriptions(json_obj,topic_title)
						extract_claims(json_obj,topic_title)
						last_update =extract_modified(json_obj,topic_title)
						entity_type =extract_type(json_obj,topic_title)
						page_id =extract_pageid(json_obj,topic_title)
						namespace =extract_namespace(json_obj,topic_title)

						if label_en !=None:
							print ""
							create_Topic(label_en, en_description, alias_en_list, topic_title, None, int(1))

					else:
						print "empty json returned"
						continue


class Command(BaseCommand):
	def handle(self, *args, **options):
		create_WikiData_Theme_Topic()
		read_file()		# read the file with list of items starting with Q
		

		
							
'''
remove en from all variable  names
try passing the language as a parameter to the functions too
next try to code up the properties code
'''
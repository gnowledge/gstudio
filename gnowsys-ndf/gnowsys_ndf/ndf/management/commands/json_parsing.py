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

from mongokit import Collection
from gnowsys_ndf.ndf.models import *
db = get_database()
collection = get_database()[GSystem.collection_name]

import urllib2
import json

url="http://www.wikidata.org/wiki/Special:EntityData/Q17.json"
	
def json_parse(url):
	j = urllib2.urlopen(url)
	js = json.load(j)
	Result =js['entities']['Q17']
	for k,v in Result.items():
		if k!="aliases" and k!="descriptions" and k!="sitelinks" and k!="claims" and k!="labels":
			print k,"  ",v
		if k =="aliases":
			dict1 =v
			
	for key,value in dict1.items():
		if key == "en":
			en_list = value

	for obj in en_list:
		for key1, val1 in obj.items():
			print key1, " ", val1			
	


	"""
	for key,val in v:
		if key == "en":
			en_list = val

			
	for obj in en_list:
		for key1, val1 in obj.items:
			print key1, " ", val1
	"""

class Command(BaseCommand):
	def handle(self, *args, **options):
        	json_parse(url)	
		


	




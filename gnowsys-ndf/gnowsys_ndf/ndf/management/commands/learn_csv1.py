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
import csv
import os
import urllib2
import json
import pprint

fn = os.path.join(os.path.dirname(__file__), '../../static/ndf/wikidata/list_of_objects')


url="http://www.wikidata.org/wiki/Special:EntityData"

def json_parse(url2):
	'''
	This function simply print out the url being passed to it as a parameter.
	It then extracts the json availbale  at that url and prints out the json in indented form.


	'''
	try:
		j = urllib2.urlopen(url2)
		js = json.load(j)
	#print url2	
		print json.dumps(js,indent=2) # code to print json in a readable format

	except (ValueError, KeyError, TypeError):
   		print "JSON format error"
	'''
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
	

	'''




class Command(BaseCommand):
	def handle(self, *args, **options):
			
		with open(fn,'rb') as f:
			r = csv.reader(f,delimiter ='\n')
			for row in r:
				for a in row:
					if a.startswith('Q')==True: #first line of wiki file has some metadata
						print (a)
						url1= url +"/"+a+".json"	#creating url of json by appending words to it to make a proper link
						json_parse(url1)
						print url1						

		
		'''
	tutFile = open("/home/aditya/Desktop/data.csv","rb")
	reader = csv.reader(tutFile)

	rownum=0
	for row in reader:
		if rownum==0:
			header=row
		else:
			colnum=0
			for col in row:
				print'%-8s: %s' % (header[colnum],col)
				colnum+=1
		
		rownum+=1

	tutFile.close()
	'''

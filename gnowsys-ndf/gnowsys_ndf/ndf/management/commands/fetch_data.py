import subprocess
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.factory_type import *
from gnowsys_ndf.ndf.models import *
from bson.json_util import dumps,loads
from bson import json_util
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.views.methods import capture_data
from gnowsys_ndf.local_settings import SYNCDATA_KEY_PUB
import json
import datetime
rcs = RCS()
hr = HistoryManager()
Parent_collection_ids = []
child_collection_ids = []
processing_list_ids = []	

class Command(BaseCommand):

	def handle(self,*args,**options):
		#temprory time stamp
		t = "2015-09-25T14:29:16"
		print t
		#Read time stamp from the file
		root_path =  os.path.abspath(os.path.dirname(os.pardir))
		tym_scan =  os.path.join(root_path, 'Last_Scan.txt') 
		file_output = open(tym_scan)
		last_scan = file_output.readline()
		if last_scan:
			index = last_scan.find(":")
			str1 = last_scan[index+1:]
			t = str1.strip("\t\n\r ")
		else:
			print "itha"	
			t = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))	
		print " \"%s\"" % t
			
		log_output =  os.popen("cat  /var/log/mongodb/mongod.log|awk '$0 > \"%s\" '|grep 'WRITE'|grep 'studio-dev.Nodes\|studio-dev.Triples'" % str(t))
		print "somgin here"
		for line in log_output:
			'''raw string processing code'''
			str_start = line.find('_id')
			str_start = (line[str_start:].find('ObjectId')) + str_start
			if str_start !=  -1:
				try:
					str_end	  = (line[str_start:].find(')')) + str_start 
					raw_string = line[str_start:str_end+1]
					
					'''	
					if line.find('.Triples') != -1:	
						if raw_string not in child_collection_ids:
							processing_list_ids.append(raw_string)
					if line.find('.Nodes') != -1:
						if raw_string not in Parent_collection_ids:
							Parent_collection_ids.append(raw_string)	
					'''	
					if line.find("ToReduceDocs") == -1:	
						if line.find('.Triples') != -1 or line.find('.Nodes') != -1 :	
							if raw_string not in processing_list_ids:
								processing_list_ids.append(raw_string)
				except Exception as e:
					print e

		process_parent_node(processing_list_ids)
		#process_dependent_collection(child_collection_ids)			
		datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		with open("Last_Scan.txt","w") as outfile:
			outfile.write(str("Last Scan time:" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))))	
def process_parent_node(Parent_collection_ids):
	for i in Parent_collection_ids:
		i = (i[i.find('\''):i[i.find('\''):].find(')') + i.find('\'')]).strip('\'')
		if i != '':
			node = node_collection.find_one({"_id":ObjectId(str(i))})
		if node:
			capture_data(file_object=node, file_data=None, content_type='Genral')
		else:
			node = triple_collection.find_one({"_id":ObjectId(str(i))})	
			capture_data(file_object=node, file_data=None, content_type='Genral')
		#create log file
		if node:
			with open("Registry.txt", 'a') as outfile:
				outfile.write(str("_id:" + str(node["_id"]) + "," +"Snapshot"+ str(node.get("snapshot",0)) +  ", Public key:" +SYNCDATA_KEY_PUB + ",Synced:{0}" +"\n" ))
			
		
def process_dependent_collection(dependent_collection):
	for i in dependent_collection:
		i = (i[i.find('\''):i[i.find('\''):].find(')') + i.find('\'')]).strip('\'')
		if i != '':
			node = triple_collection.find_one({"_id":ObjectId(str(i))})
		capture_data(file_object=node, file_data=None, content_type='Genral')
        

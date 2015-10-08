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
		print tym_scan
		if os.path.exists(tym_scan):
			file_output = open(tym_scan)
			last_scan = file_output.readline()
			index = last_scan.find(":")
			str1 = last_scan[index+1:]
			t = str1.strip("\t\n\r ")
		else:
			t = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))	
		print " \"%s\"" % t
				
		log_output =  os.popen("cat  /var/log/mongodb/mongod.log|awk '$0 > \"%s\" '|grep 'WRITE'|grep 'recv-data.Nodes\|recv-data.Triples'" % str(t))
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
							if (raw_string) not in processing_list_ids:
								processing_list_ids.append((raw_string,line[0:line.find(' ')]))
				except Exception as e:
					print e

		process_parent_node(processing_list_ids,t)
		#process_dependent_collection(child_collection_ids)			
		datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
		slice_registry(t)
		with open("Last_Scan.txt","w") as outfile:
			outfile.write(str("Last Scan time:" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))))
def process_parent_node(Parent_collection_ids,last_scan):
	root_path =  os.path.abspath(os.path.dirname(os.pardir))
	file_scan =  os.path.join(root_path, 'receivedfile')
	node_skipped_after_capture = []
	for i in Parent_collection_ids:
		id = i[0]
		id = (id[id.find('\''):id[id.find('\''):].find(')') + id.find('\'')]).strip('\'')
		time = i[1]
		time = time.split('.')[0]
		#After last scan of this machine if that data reside in this system 
		#check its insertion tym
		#if nodes log tym is more tha insert tym add it to the new log file
		#log_output =  os.popen("cat  %s|awk '$0 > \"%s\"'|grep '%s'|awk '$0 > \"%s\"'" %  (file_scan,str(last_scan),id,time))
		#print node_skipped_after_capture,id
		if id not in node_skipped_after_capture: 
			log_output =  os.popen("cat  %s|awk '$0 > \"%s\"'|grep '%s'" %  (file_scan,str(last_scan),id)).readlines()
			if log_output:
				allowed = False
				for i in log_output:
					registrytime = i[0:i.index(',')]
					if time > registrytime:
						print "the time that matched",time,registrytime	
						allowed = True
						break	
				if  allowed ==  True:
						print "id",id,log_output
						capture_id_data(id,time)
						node_skipped_after_capture.append(id)
			else:
					print "Nodes Generated from this server",id
					capture_id_data(id,time)
					node_skipped_after_capture.append(id)
						
				
		
def process_dependent_collection(dependent_collection):
	for i in dependent_collection:
		i = (i[i.find('\''):i[i.find('\''):].find(')') + i.find('\'')]).strip('\'')
		if i != '':
			node = triple_collection.find_one({"_id":ObjectId(str(i))})
		capture_data(file_object=node, file_data=None, content_type='Genral')


def capture_id_data(id,time):
	if id != '':
		node = node_collection.find_one({"_id":ObjectId(str(id))})
		if node:
			pass
		else:
			node = triple_collection.find_one({"_id":ObjectId(str(id))})	
			
		#create log file

		if node:
			with open("Registry.txt", 'a') as outfile:
				outfile.write(str(time + ", _id:" + str(node["_id"]) + ", " +"Snapshot"+ str(node.get("snapshot",0)) +  ", Public key:" +SYNCDATA_KEY_PUB + ",Synced:{1}" +"\n" ))
		capture_data(file_object=node, file_data=None, content_type='Genral')       


def slice_registry(time):
	manage_path =  os.path.abspath(os.path.dirname(os.pardir))
	registry_path =  os.path.join(manage_path, 'Registry.txt') 
	if time == "":
		time = "0000-00-00T00:00:00"
	'''	
	file_output = open(registry_path)
	current_line = ""
	previouse_line = ""
	last_line = ""
	a = True
	#Old code to create previouse and post node information
	#with every sending node
	
	while a:
			previouse_line = current_line
			current_line = file_output.readline()
			c = current_line.find(str(node_id))      
			if c != -1:
				a = False
			if current_line == "":	
				break
	last_line = file_output.readline() 		
	file_output.close()
	'''
	log_output =  os.popen("cat  %s|awk '$0 > \"%s\"'" %  (registry_path,str(time))).read()
	with open(manage_path + "/Info_Registry.txt","w") as outfile:
		outfile.write(log_output)	
	
  

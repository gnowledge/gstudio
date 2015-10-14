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
import shutil
rcs = RCS()
hr = HistoryManager()
Parent_collection_ids = []
child_collection_ids = []
processing_list_ids = []	

class Command(BaseCommand):

	def handle(self,*args,**options):
		#temprory time stamp
		collection_list = ['.Triples','.Nodes','.fs.files','.fs.chunks']
		collection = '.Nodes'
		#Read time stamp from the file
		root_path =  os.path.abspath(os.path.dirname(os.pardir))
		tym_scan =  os.path.join(root_path, 'Last_Scan.txt') 
		if os.path.exists(tym_scan):
			file_output = open(tym_scan)
			last_scan = file_output.readline()
			index = last_scan.find(":")
			str1 = last_scan[index+1:]
			t = str1.strip("\t\n\r ")
		else:
			ti = datetime.time(0,0,0,0)
			date1 = datetime.date.today()
			t = str(datetime.datetime.combine(date1,ti).strftime("%Y-%m-%dT%H:%M:%S"))	
		log_output =  os.popen("cat  /var/log/mongodb/mongod.log|awk '$0 > \"%s\" '|grep 'WRITE'|grep '.Nodes\|.Triples\|.fs.files\|.fs.chunks'" % str(t))
		for line in log_output:
			'''raw string processing code'''
			str_start = line.find('_id')
			str_start = (line[str_start:].find('ObjectId')) + str_start
			if str_start !=  -1:
				try:
					str_end	  = (line[str_start:].find(')')) + str_start 
					raw_string = line[str_start:str_end+1]
					if line.find("ToReduceDocs") == -1:	
						if line.find('.Triples') != -1:       	
							collection = '.Triples'
							if (raw_string) not in processing_list_ids:
								processing_list_ids.append((raw_string,line[0:line.find(' ')],collection))
						elif line.find('.Nodes') != -1:
							collection = '.Nodes'	
							if (raw_string) not in processing_list_ids:
								processing_list_ids.append((raw_string,line[0:line.find(' ')],collection))
						elif line.find('.fs.files') != -1:
							collection = '.fs.files'
							if (raw_string) not in processing_list_ids:
								processing_list_ids.append((raw_string,line[0:line.find(' ')],collection))
						elif line.find('.fs.chunks') != -1:
							collection = '.fs.chunks'
							if (raw_string) not in processing_list_ids:
								processing_list_ids.append((raw_string,line[0:line.find(' ')],collection))
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
	for k,i in enumerate(Parent_collection_ids):
		packet_sequence = "%06d" % k
		id = i[0]
		id = (id[id.find('\''):id[id.find('\''):].find(')') + id.find('\'')]).strip('\'')
		time_with_microsec = i[1]
		time = time_with_microsec.split('.')[0]
		collection = i[2]
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
						allowed = True
						break	
				if  allowed ==  True:
						print "id",id,log_output
						capture_id_data(id,time_with_microsec,collection)
						node_skipped_after_capture.append(id)
			else:
					print "Nodes Generated from this server",id
					capture_id_data(id,time_with_microsec,collection)
					node_skipped_after_capture.append(id)
						
				
		
def process_dependent_collection(dependent_collection):
	for i in dependent_collection:
		i = (i[i.find('\''):i[i.find('\''):].find(')') + i.find('\'')]).strip('\'')
		if i != '':
			node = triple_collection.find_one({"_id":ObjectId(str(i))})
		capture_data(file_object=node, file_data=None, content_type='Genral')


def capture_id_data(id,time_with_microsec,collection):
	if id != '':
		if collection == '.Nodes':
			node = node_collection.find_one({"_id":ObjectId(str(id))})
		if collection == '.Triples':
			node = triple_collection.find_one({"_id":ObjectId(str(id))})
		if collection == '.fs.files':
			node = gridfs_collection.find_one({"_id":ObjectId(str(id))})
		if collection == '.fs.chunks':
			node = chunk_collection.find_one({"_id":ObjectId(str(id))})
 			
			
			
		#create log file

		if node:
			with open("Registry.txt", 'a') as outfile:
				outfile.write(str(time_with_microsec + "_" + str(node["_id"]) + ", " +"Snapshot"+ str(node.get("snapshot",0)) +  ", Public key:" +SYNCDATA_KEY_PUB + ",Synced:{1}" +"\n" ))
		capture_data(file_object=node, file_data=None, content_type='Genral',time=time_with_microsec)       


def slice_registry(time):
	manage_path =  os.path.abspath(os.path.dirname(os.pardir))
	registry_path =  os.path.join(manage_path, 'Registry.txt') 
	if time == "":
		ti = datetime.time(0,0,0,0)
		date1 = datetime.date.today()
		time = str(datetime.datetime.combine(date1,ti).strftime("%Y-%m-%dT%H:%M:%S"))
	log_output =  os.popen("cat  %s|awk '$0 > \"%s\"'" %  (registry_path,str(time))).read()
	with open(manage_path + "/Info_Registry.txt","w") as outfile:
		outfile.write("Start")
		outfile.write("\n")		
		outfile.write(log_output)
		outfile.write("End")	
	log_output =  os.popen("cat  %s|awk '$0 > \"%s\"'" %  (registry_path,str(time))).readlines()
	manage_path =  os.path.abspath(os.path.dirname(os.pardir))
	#file to copy
	manage_path =  os.path.abspath(os.path.dirname(os.pardir))
	registry_path = os.path.join(manage_path,'Info_Registry.txt')
	#loop around to fill the destination data
	for i,j in enumerate(log_output):
		dst = str(manage_path) + "/gnowsys_ndf/ndf/MailClient/syncdata"
		file_name = j[0:j.index(',')]
		dst = dst +"/" +str(file_name)
		if  file_name not in ['Start','End']:
			data=get_neighbours(file_name,registry_path)
			file_path = create_file(dst,data)
			'''
			cp = "cp  -u " + str(file_path) + " " + dst + "/"  
			subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
			'''
	#delete the Info_Registry after copying
	#os.remove(registry_path)
def create_file(file_path,data,mode="w"):
	#create_file with given data
	with open(file_path + "/Info.txt",mode) as outfile:
		for i in data:
			outfile.write(i)
	return file_path + "/Info.txt"
	
def get_neighbours(file_name,registry_path):
	#get previouse and next line of the match 
	# from the defined file path
	file_output = open(registry_path)
	current_line = ""
	previouse_line = ""
	last_line = ""
	a = True
	data = []
	#Old code to create previouse and post node information
	#with every sending node
	while a:
			previouse_line = current_line
			current_line = file_output.readline()
			c = current_line.find(str(file_name))      
			if c != -1:
				a = False
			if current_line == "":	
				break
	last_line = file_output.readline()
	file_output.close()
	#written file path to copy
	data.append(previouse_line)
	data.append(current_line)
	data.append(last_line)	
	return data 
	

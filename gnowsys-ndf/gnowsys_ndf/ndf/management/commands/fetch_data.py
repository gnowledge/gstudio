import subprocess
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.ndf.models import *
from bson.json_util import dumps,loads
from bson import json_util
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.views.methods import capture_data
from gnowsys_ndf.local_settings import SYNCDATA_KEY_PUB
from gnowsys_ndf.settings import TARSIZE
from pymongo import Connection
import json
import datetime
import shutil
import zipfile
import os
import time
Parent_collection_ids = []
child_collection_ids = []
processing_list_ids = []    

class Command(BaseCommand):

    def handle(self,*args,**options):
        root_path =  os.path.abspath(os.path.dirname(os.pardir))
        lock =  os.path.join(root_path, 'lock')         
        if  os.path.exists(lock) == False:
            fl = open("lock", "wb")
            fl.close()
            op = fetch_data()
            if op == 0:
                os.remove(lock)
        

def fetch_data():
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
        date1 = datetime.datetime(2015,12,1)
        t = str(datetime.datetime.combine(date1,ti).strftime("%Y-%m-%dT%H:%M:%S"))  
        print t
    log_output =  os.popen("cat  /var/log/mongodb/mongod.log|awk '$0 > \"%s\" '|grep 'WRITE'|grep '.Nodes\|.Triples\|.fs.files\|.fs.chunks'" % str(t))
    for line in log_output:
        '''raw string processing code'''
        str_start = line.find('_id')
        str_start = (line[str_start:].find('ObjectId')) + str_start
        if str_start !=  -1:
            try:
                str_end   = (line[str_start:].find(')')) + str_start 
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
        
    if processing_list_ids:
        #only update the last scan tym if some data is feched 
        slice_registry(t)
        manage_path =  os.path.abspath(os.path.dirname(os.pardir))
        sync_dir =  str(manage_path) + "/gnowsys_ndf/ndf/MailClient/syncdata" 
        #Zip the files in sync_dir
        zip_directories(sync_dir)
        time.sleep(1)
        with open("Last_Scan.txt","w") as outfile:
            outfile.write(str("Last Scan time:" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))))        
    return 0        
def process_parent_node(Parent_collection_ids,last_scan):
    root_path =  os.path.abspath(os.path.dirname(os.pardir))
    file_scan =  os.path.join(root_path, 'receivedfile')
    node_skipped_after_capture = []
    for k,i in enumerate(Parent_collection_ids):
        packet_sequence = "%06d" % k
        id = i[0]
        id = (id[id.find('\''):id[id.find('\''):].find(')') + id.find('\'')]).strip('\'')
        #time to cross check with database insetion time to avoid resending of data
        time_with_microsec = i[1]
        time = time_with_microsec.split('.')[0]
        #time stamp to create unique file name
        timestamp = datetime.datetime.now()
        timestamp = timestamp.isoformat()
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
                        print "node here",id
                        capture_id_data(id,timestamp,collection)
                        node_skipped_after_capture.append(id)
            else:
                    print "Nodes Generated from this server",id
                    capture_id_data(id,timestamp,collection)
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
                print "every node passing through it","the id",id
                capture_data(file_object=node, file_data=None, content_type='Genral',time=time_with_microsec)
                with open("Registry.txt", 'a') as outfile:
                    outfile.write(str(time_with_microsec + "_" + str(node["_id"]) + ", " +"Snapshot"+ str(node.get("snapshot",0)) +  ", Public key:" +SYNCDATA_KEY_PUB + ",Synced:{1}" +"\n" ))
                       


def slice_registry(time):
    print "coming here",time
    data = []
    current_line = ""
    previouse_line = ""
    last_line = ""
    manage_path =  os.path.abspath(os.path.dirname(os.pardir))
    registry_path =  os.path.join(manage_path, 'Registry.txt') 
    if time == "":
        ti = datetime.time(0,0,0,0)
        date1 = datetime.datetime(2014,12,1)
        time = str(datetime.datetime.combine(date1,ti).strftime("%Y-%m-%dT%H:%M:%S"))
    log_output =  os.popen("cat  %s|awk '$0 > \"%s\"'" %  (registry_path,str(time))).read()
    with open(manage_path + "/Info_Registry.txt","w") as outfile:
        outfile.write("Start")
        outfile.write("\n")     
        outfile.write(log_output)
        outfile.write("End")
    
    registry_path = os.path.join(manage_path,'Info_Registry.txt')
    log_output =  os.popen("cat  %s" %  registry_path).readlines()
    
    #loop around to fill the destination data
    for i,j in enumerate(log_output):
        dst = str(manage_path) + "/gnowsys_ndf/ndf/MailClient/syncdata"
        file_name = j.strip()
        if  (file_name not in ['Start','End']) == True:
            file_name = j[0:j.index(',')]
            dst = dst +"/" +str(file_name)
            current_line = j
            try:
                last_line = log_output[i+1]
            except:
                last_line = ""

            #data=get_neighbours(file_name,registry_path)
            data.append(previouse_line)
            data.append(current_line)
            data.append(last_line)
            file_path = create_file(dst,data)
            '''
            cp = "cp  -u " + str(file_path) + " " + dst + "/"  
            subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
            '''
        previouse_line = j
        data = []
            
    #delete the Info_Registry after copying
    #os.remove(registry_path)
def create_file(file_path,data,mode="w"):
    #create_file with given data
    with open(file_path + "/Info.txt",mode) as outfile:
        for i in data:
            outfile.write(i)
    return file_path + "/Info.txt"
    

def zip_directories(sync_dir):
    #code to walk through the /ndf/Mailclient/sync_data/ directory
    #scan all the folder, pick then and create zip files of size 1Mb

    zip_list = []
    dir_list = []
    total_size = 0
    list_of_tuples = []
    last_packet_number = 0
    dirname  = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S').replace(" ","_").replace("/","_") + "_" + str(datetime.datetime.now().microsecond)           
    root_path =  os.path.abspath(os.path.dirname(os.pardir))
    packet_sequnce_scan =  os.path.join(root_path, 'last_packet_number.txt')
    if os.path.exists(packet_sequnce_scan):
        with open(packet_sequnce_scan,"r") as outfile:
                    last_packet_number = outfile.read()
        last_packet_number = last_packet_number.strip()            
    else:
        last_packet_number = 0
    print "the scan",last_packet_number    
    for dir,subdir,file in sorted(os.walk(sync_dir)):
        #print dir,"\n",subdir,"\n",file,"\n"
        for f in file:
                fp = os.path.join(dir, f)
                total_size += os.path.getsize(fp)
                
        #zip_list.remove('/home/glab/Desktop/pythonzipfoldercode')
        if total_size/1024 > TARSIZE:
            total_size = 0
            #os.mkdir(dirname)
            #path = os.path.abspath(dirname)
            syncdir_path = os.path.join(sync_dir,dirname)
            for i in zip_list:
                if os.path.exists(syncdir_path) == False:
                    os.makedirs(syncdir_path)
                shutil.move(i,syncdir_path+"/")
            total_size = 0  
            dir_list.append(syncdir_path)        
            dirname  = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S').replace(" ","_").replace("/","_") + "_" + str(datetime.datetime.now().microsecond)
            zip_list = []
        
        if dir != sync_dir:
            zip_list.append(dir)    

    if zip_list:
        for i in zip_list:
                #path = os.path.abspath(dirname)
                #print sync_dir,"",path
                syncdir_path = os.path.join(sync_dir,dirname)
                if os.path.exists(syncdir_path) == False:
                    os.makedirs(syncdir_path)
                shutil.move(i,syncdir_path+"/")
        dir_list.append(syncdir_path)        
        
    for v,i in enumerate(dir_list):
        send_counter = "%06d" % int(last_packet_number)
        shutil.make_archive(sync_dir+"/"+send_counter,'gztar',os.path.abspath(i))
        shutil.rmtree(i)
        last_packet_number = int(last_packet_number) + 1 
        with open(packet_sequnce_scan,"w") as outfile:
                outfile.write(str(last_packet_number))
    


def mongorotate():
    #rotate the mongolog 
    #check if the file size if greater than 20MB Rotate
    #if yes Rotate
    #20480 is 20MB in bytes if file size is greater than that rotate
    if os.path.getsize('/var/log/mongodb/mongod.log')/1000 >= 20480:
        conn = Connection()
        database = conn['admin']
        #logRotate command can be executed on mongo shell with admin database
        database.command({"logRotate":1})
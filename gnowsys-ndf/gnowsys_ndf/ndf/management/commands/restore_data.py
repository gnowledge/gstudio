from gnowsys_ndf.ndf.models  import *
import os
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from bson.json_util import dumps,loads,object_hook
import json
class Command(BaseCommand):
    help = "Based on "

    def handle(self, *args, **options):


        path  = os.path.abspath(os.path.dirname(os.pardir))
        path = os.path.join(path,'home/')
        print path
        file_path_exists =  os.path.exists(path)
        
        filenamelist = []
        for dir_, _, files in os.walk(path):
            for filename in files:
                filepath =  os.path.join(dir_, filename)
                filenamelist.append(filepath)
        for i in filenamelist:      
           data = get_json_file(i)
           final_data = check_data(data) 



def get_json_file(filepath):

    history_manager = HistoryManager()
    rcs = RCS()
    version_no = '1.15'
    path = '55b0da90f87f070bb518c33e.json'
    rcs.checkout(filepath)
    with open(path, 'r') as version_file:
            json_data = version_file.read()
    #print json_data
    json_dict = json.loads(json_data)
    json_data = json.dumps(json_dict)
    # Converts the json-formatted data into python-specific format
    doc_obj =  loads(json_data)
    #doc_obj = node_collection.from_json(json_data)
    #parse the data for perfect json node creation
    return doc_obj  

    

def check_data(data):
    ''' method to check if all the system types relations and pre dependencies
        are present in the system before pushing them to the current system 
    '''
    print data
    temp_node = node_collection.collection.Group()
    temp_dict = {}
    ''' dictionary creation '''
    for key, values in data.items():
        temp_dict[key] = values

    temp_node.update(temp_dict)
    temp_node.save()	
	

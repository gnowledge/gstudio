import os
import json

from bson.json_util import dumps,loads,object_hook

from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

from gnowsys_ndf.ndf.models  import *

class Command(BaseCommand):

    help = "setup the initial database"

    def handle(self, *args, **options):
        # import ipdb; ipdb.set_trace()
        # path  = os.path.abspath(os.path.dirname(os.pardir))
        path  = '/data/restore/rcs-repo'
        nodes_path = '/data/restore/rcs-repo/Nodes'
        triples_path = '/data/restore/rcs-repo/Triples'

        path_list = [('Node',nodes_path),('Triples',triples_path)]

        for path in path_list:
            # print path[1]
            file_path_exists =  os.path.exists(path[1])
            filenamelist = []

            for dir_, _, files in os.walk(path[1]):
                for filename in files:
                    filepath =  os.path.join(dir_, filename)
                    filenamelist.append(filepath)

            # print "filenamelist: \n\n:", filenamelist

            for i in filenamelist:
                data = self.get_json_file(i)
                # print "======= _id : ", data['_id']
                # final_data = check_data(data)
                # direct insertion of node in database
                if data:
                    try:
                        if path[0] == 'Node':
                            print "111111111111111111111111111111111"
                            print "===", node_collection.collection.insert(data)
                        if path[0] == 'Triples':
                            print "2222222222222222222222222222222"
                            print "===", triple_collection.collection.insert(data)
                    except Exception as e:
                        print "Exception occured while processing: ", e

    def get_json_file(self, filepath):

        print "\n============= in get_json_file():\n"
        history_manager = HistoryManager()
        rcs = RCS()
        # version_no = '1.13'
        rcs.checkout((filepath))
        filepath = filepath.split(',')[0]
        print "filepath", filepath.split('/')[-1]

        try:
            with open(filepath.split('/')[-1], 'r') as version_file:
                json_data = version_file.read()
                json_dict = json.loads(json_data)
                json_data = json.dumps(json_dict)
                doc_obj =  loads(json_data)
                # doc_obj =  dumps(doc_obj)
                # doc_obj = node_collection.from_json(doc_obj)
                rcs.checkin((filepath))
            #parse the data for perfect json node creation
            return doc_obj

        except Exception, e:
            print "Exception while getting JSON: ", e
            return None


    def check_data(self, data):
        ''' method to check if all the system types relations and pre dependencies
            are present in the system before pushing them to the current system
        '''
        temp_node = node_collection.collection.Group()
        temp_dict = {}
        ''' dictionary creation '''
        '''
        for key, values in data.items():
            temp_dict[key] = values

        temp_node.update(temp_dict)
        '''
        #temp_node.save()












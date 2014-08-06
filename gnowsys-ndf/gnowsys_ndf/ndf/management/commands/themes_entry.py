''' -- imports from python libraries -- '''
import os
import csv
import json
import ast
import datetime

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database
from mongokit import IS

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import *


####################################################################################################################

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files")

print "\nschema root: ", SCHEMA_ROOT,"\n"

log_list = [] # To hold intermediate errors
collection = get_database()[Node.collection_name]

theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme' })
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
br_topic = collection.Node.one({'_type': 'GSystemType', 'name': 'Browse Topic'})

class Command(BaseCommand):
    help = "creating themes"

    def handle(self, *args, **options):
        for file_name in args:
            file_path = os.path.join(SCHEMA_ROOT, file_name)
            with open(file_path, 'rb') as f:
                reader = csv.reader(f)
                try:
                    i = 1
                    for ind, row in enumerate(reader):
                        print "\n #", (ind + 1), " --- ", row

                        for index, obj in enumerate(row):
                            if obj:
                                # Bounds-checking
                                print "\nindex: ",index, " -- ", len(row)
                                if index > 0:
                                    prev = row[index - 1]
                                else:
                                    prev = ""
                                
                                if index < (len(row) - 1):
                                    nex = row[index + 1]
                                else:
                                    nex = ""

                                if not prev:
                                    print "\n Its a theme -- ", obj
                                elif prev and nex:
                                    print "\n Its a theme item -- ", obj
                                elif prev and not nex:
                                    print "\n Its a topic -- ", obj
                            else:
                                break

                        i = i + 1
                        print " ======================================================="

                        # if (i == 2):
                        #     break
                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e)) 
        
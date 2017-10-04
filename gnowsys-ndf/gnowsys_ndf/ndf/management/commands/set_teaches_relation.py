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
from django.contrib.auth.models import User

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import create_grelation


####################################################################################################################

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files")

collection = get_database()[Node.collection_name]
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
RT_teaches = collection.Node.one({'_type':'RelationType', 'name': 'teaches'})
auth_id = User.objects.get(username='nroer_team').pk

grp = collection.Node.one({'_type': 'Group', 'name': 'home'})

if grp:
	group_id = grp._id

class Command(BaseCommand):
    help = "Updating teaches relation to topics of all resources"

    def handle(self, *args, **options):
        for file_name in args:
            file_path = os.path.join(SCHEMA_ROOT, file_name)
            with open(file_path, 'rb') as f:
                reader = csv.reader(f)
                try:
                    i = 1
                    for ind, row in enumerate(reader):
                        # print "\n row: ", row
                        file_name = row[0]
                        teaches = row[1]

                        if ":" in teaches:
                          formatted_list = []
                          temp_teaches_list = teaches.replace("\n", "").split(":")
                          for v in temp_teaches_list:
                            formatted_list.append(v.strip())

                          teaches = formatted_list

                        update_teaches(file_name, teaches)

                        i = i + 1

                        print "\n", i ," rows successfully compiled"
                        print " ======================================================="

                        # if (i == 60):
                            # break
                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))


def update_teaches(file_name, teaches):

  # print file_name, teaches,"\n"
  changed = ""

  file_obj = collection.Node.one({'_type': 'File', 'group_set': ObjectId(group_id) ,'name':unicode(file_name), 'created_by': auth_id})
  if file_obj:

    rel_objs = collection.Triple.find({'_type':'GRelation','subject': ObjectId(file_obj._id), 'relation_type': RT_teaches._id})

    if rel_objs.count() > 0:
      for rel_obj in rel_objs:
        rel_obj.delete()
        print "\n Relation ",rel_obj.name," deleted !!!\n"


    topic = teaches[len(teaches) - 1]
    topic_obj = collection.Node.find({'name':unicode(topic), 'group_set': ObjectId(group_id),'member_of': topic_GST._id })
    if topic_obj.count() > 0:
      for k in topic_obj:
        if k.prior_node:
          for each in k.prior_node:
            obj = collection.Node.one({'_id': ObjectId(each) })
            if obj.name == teaches[len(teaches) - 2]:
              create_grelation(file_obj._id, RT_teaches, k._id)
              print "\n Grelation created for ",file_obj.name,"\n"


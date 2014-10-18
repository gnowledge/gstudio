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
from gnowsys_ndf.ndf.models import Node
####################################################################################################################

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files")

# print "\nschema root for terms entry: ", SCHEMA_ROOT,"\n"

collection = get_database()[Node.collection_name]
gapp_GST = collection.Node.one({'_type':'MetaType', 'name':'GAPP' })
term_GST = collection.Node.one({'_type': 'GSystemType', 'name':'Term', 'member_of':ObjectId(gapp_GST._id) })
grp = collection.Node.one({'_type': 'Group', 'name': 'ATLAS'})

if grp:
	group_id = grp._id

class Command(BaseCommand):
    help = "creating term instances"

    def handle(self, *args, **options):
    	for file_name in args:
          file_path = os.path.join(SCHEMA_ROOT, file_name)
          with open(file_path, 'rb') as f:
            reader = csv.reader(f)
            try:
              i = 1
              k = None
              for ind, row in enumerate(reader):
                # print "\n row: ", row
                
                for index, obj in enumerate(row):
					# print index," ",obj,"\n"
					if index == 1:
						val = obj
					elif index == 2:
						if val:
							if obj in ["instanceof","subtypeof"]:
								create_term_obj(val)
							else:
								k = obj

					elif index == 3:
						if obj:
							if k == "dependson":
								add_prior_node(val, obj)


                i = i + 1
                
                print "\n", i ," rows successfully compiled"
                print " ======================================================="
                
                # if (i == 6):
                #   break
                  
            except csv.Error as e:
              sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e)) 


def create_term_obj(val):
	# print "\ninside create_term_obj\n"
	term_obj = collection.Node.one({'_type': 'GSystem','member_of': ObjectId(term_GST._id), 'name':unicode(val) })
	if not term_obj:
		term_obj = collection.GSystem()
		term_obj.name = unicode(val)
		term_obj.access_policy = u"PUBLIC"
		term_obj.status = u"PUBLISHED"
		term_obj.contributors.append(1)
		term_obj.created_by = 1
		term_obj.modified_by = 1
		term_obj.group_set.append(group_id)
		term_obj.language = u"en"
		term_obj.member_of.append(term_GST._id)
		term_obj.save()
		print "Term ",val," created successfully\n"

	else:
		print "Term ",val," already created\n"

def add_prior_node(val, obj):
	# print "\nadd_prior_node to this obj: ",val," depends on ",obj,"\n"
	term_obj1 = collection.Node.one({'_type': 'GSystem','member_of': ObjectId(term_GST._id), 'name':unicode(val) })
	term_obj2 = collection.Node.one({'_type': 'GSystem','member_of': ObjectId(term_GST._id), 'name':unicode(obj) })

	if term_obj1 and term_obj2:
		if term_obj2._id not in term_obj1.prior_node:

			collection.update({'_id': term_obj1._id}, {'$set': {'prior_node': [term_obj2._id] }}, upsert=False, multi=False)
			# term_obj1.prior_node.append(term_obj2._id)
			# term_obj1.save()
			print "Term ",obj," added to prior node of term ",val," successfully !!!\n"

		else:
			print "Term ",obj," already added to prior node of term ",val,"\n"

	else:
		print "Terms doesnot exists\n"
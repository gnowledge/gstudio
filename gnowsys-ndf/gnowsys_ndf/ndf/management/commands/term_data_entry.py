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
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
grp = collection.Node.one({'_type': 'Group', 'name': 'atlas'})

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
              for ind, row in enumerate(reader):
                # print "\n row: ", row
                
                for index, obj in enumerate(row):
                	# Index = 0 means first column
					if index == 1:
						# index = 1 means its second column
						second_col = obj
					elif index == 2:
						# index = 2 means its third column
						if second_col:
							third_col = obj

					elif index == 3:
						# index = 3 means its fourth column
						if obj:
							fourth_col = obj
							if fourth_col != "dependson" and fourth_col in ["concept","activity"]:
								if third_col in ["instanceof","subtypeof"]:
									create_term_obj(second_col)

							if third_col == "dependson":
								add_prior_node(second_col, fourth_col)


                i = i + 1
                
                print "\n", i ," rows successfully compiled"
                print " ======================================================="
                
                # if (i == 6):
                  # break
                  
            except csv.Error as e:
              sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e)) 


def create_term_obj(second_col):
	# print "\ninside create_term_obj\n"
	term_obj = collection.Node.one({'_type': 'GSystem','member_of': {'$all': [ObjectId(term_GST._id), ObjectId(topic_GST._id)]}, 'name':unicode(second_col) })
	if not term_obj:
		term_obj = collection.GSystem()
		term_obj.name = unicode(second_col)
		term_obj.access_policy = u"PUBLIC"
		term_obj.status = u"PUBLISHED"
		term_obj.contributors.append(1)
		term_obj.created_by = 1
		term_obj.modified_by = 1
		term_obj.group_set.append(group_id)
		term_obj.language = u"en"
		term_obj.member_of.append(term_GST._id)
		term_obj.member_of.append(topic_GST._id)
		term_obj.save()
		print "Term ",second_col," created successfully\n"

	else:
		print "Term ",second_col," already created\n"

def add_prior_node(second_col, fourth_col):
	# print "\nadd_prior_node to this obj: ",val," depends on ",obj,"\n"
	term_obj1 = collection.Node.one({'_type': 'GSystem','member_of': {'$all': [ObjectId(term_GST._id), ObjectId(topic_GST._id)]}, 'name':unicode(second_col) })
	term_obj2 = collection.Node.one({'_type': 'GSystem','member_of': {'$all': [ObjectId(term_GST._id), ObjectId(topic_GST._id)]}, 'name':unicode(fourth_col) })

	if term_obj1 and term_obj2:
		if term_obj2._id not in term_obj1.prior_node:

			collection.update({'_id': term_obj1._id}, {'$set': {'prior_node': [term_obj2._id] }}, upsert=False, multi=False)
			print "Term ",fourth_col," added to prior node of term ",second_col," successfully !!!\n"

		else:
			print "Term ",fourth_col," already added to prior node of term ",second_col,"\n"

	else:
		print "Terms doesnot exists\n"
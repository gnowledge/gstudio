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

# print "\nschema root: ", SCHEMA_ROOT,"\n"

collection = get_database()[Node.collection_name]

theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme' })
theme_item_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'theme_item' })
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
br_topic = collection.Node.one({'_type': 'GSystemType', 'name': 'Browse Topic'})

#grp = collection.Node.one({'_type': 'Group', '_id': ObjectId('53747277c1704121fe54be46')})
grp = collection.Node.one({'_type': 'Group', 'name': 'home'})

if grp:
	group_id = grp._id

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
                        # print "\n row: ", row

                        for index, obj in enumerate(row):
                            if obj:
                                # Bounds-checking
                                if index > 0:
                                    prev = row[index - 1]
                                else:
                                    prev = ""
                                
                                if index < (len(row) - 1):
                                    nex = row[index + 1]
                                else:
                                    nex = ""

                                if not prev:
                               		create_theme(obj)

                                elif prev and nex:
                                	create_theme_item(obj, prev, row)
                                	
                                elif prev and not nex:
                                	create_topic(obj, prev, row)

                            else:
                                break

                        i = i + 1

                        print "\n", i ," rows successfully compiled"
                        print " ======================================================="

                        # if (i == 294):
                            # break
                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e)) 
        

def create_theme(obj):
	# print "\n Its a theme -- ", obj
	themes_list = []

	# To find the root themes to maintain the uniquness while creating new themes
	nodes = collection.Node.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
	for each in nodes:
		themes_list.append(each.name)


	if obj not in themes_list:
		name = obj

		theme_node = collection.GSystem()
		theme_node.name = unicode(name).strip()
		theme_node.access_policy = u"PUBLIC"
		theme_node.contributors.append(1)
		theme_node.created_by = 1
		theme_node.group_set.append(group_id)
		theme_node.language = u"en"
		theme_node.member_of.append(theme_GST._id)
		theme_node.modified_by = 1
		theme_node.status = u"DRAFT"

		theme_node.save()

	else:
		print "\nTheme ", obj," already available"
	


def create_theme_item(obj, prev, row):
	# print "\n Its a theme item -- ", obj
	theme_items_list = []	
	prev_node_list = []
	# Taking pre-prev item in a row to identify uniqueness and hierarchy level of theme item
	pre_prev_name = row[row.index(prev) - 1]

	if prev:
		# To find the prev item in a row as its already created 
		prev_node_cur = collection.GSystem.find({'name': unicode(prev),'group_set': group_id, 'member_of': {'$in': [ theme_item_GST._id, theme_GST._id]}  })	

		# To identify the exact prev element and its hierarchy level of theme item when we found multiple results of same theme item
		if prev_node_cur.count() > 1:
			for each in prev_node_cur:
				# This will return the pre-prev node in the hierarchy level of incoming prev node
				pre_prev_node = collection.Node.one({'collection_set': ObjectId(each._id) })
				# if prev node is the theme item of pre-prev node, then we found the exact hierarchy level.
				if pre_prev_node.name == pre_prev_name:
					prev_node_list.append(each)

			prev_node = prev_node_list[0]
					

		else:
			prev_node = prev_node_cur[0]


		# To find the uniqueness of incoming obj in its prev node's hierarchy level 
		if prev_node.collection_set:
			for item in prev_node.collection_set:
				theme_item = collection.Node.one({'_id': ObjectId(item) })
				theme_items_list.append(theme_item.name)				


	if obj not in theme_items_list:
		# Save the theme item 
		theme_item_node = collection.GSystem()
		theme_item_node.name = unicode(obj).strip()
		theme_item_node.access_policy = u"PUBLIC"
		theme_item_node.contributors.append(1)
		theme_item_node.created_by = 1
		theme_item_node.group_set.append(group_id)
		theme_item_node.language = u"en"
		theme_item_node.member_of.append(theme_item_GST._id)
		theme_item_node.modified_by = 1
		theme_item_node.status = u"DRAFT"

		theme_item_node.save()

		# after saving successfully add into the collection_set of its prev node
		prev_node.collection_set.append(theme_item_node._id)
		prev_node.save()

	else:
		print "\n Theme Item ", obj," already available"
		

def create_topic(obj, prev, row):
	# print "\n Its a topic -- ", obj
	theme_items_list = []
	prev_node_list = []
	# Taking pre-prev item in a row to identify uniqueness and hierarchy level of topic
	pre_prev_name = row[row.index(prev) - 1]

	if prev:
		# To find the prev item in a row as its already created 
		prev_node_cur = collection.GSystem.find({'name': unicode(prev),'group_set': group_id, 'member_of': {'$in': [ theme_item_GST._id, theme_GST._id]}  })
		
		# To identify the exact prev element and its hierarchy level of theme item when we found multiple results of same theme item
		if prev_node_cur.count() > 1:
			for each in prev_node_cur:
				# This will return the pre-prev node in the hierarchy level of incoming prev node
				pre_prev_node = collection.Node.one({'collection_set': ObjectId(each._id) })
				# if prev node is the theme item of pre-prev node, then we found the exact hierarchy level.
				if pre_prev_node.name == pre_prev_name:
					prev_node_list.append(each)

			prev_node = prev_node_list[0]

		else:
			prev_node = prev_node_cur[0]


		# To find the uniqueness of incoming obj in its prev node's hierarchy level 
		if prev_node.collection_set:
			for item in prev_node.collection_set:
				theme_item = collection.Node.one({'_id': ObjectId(item) })
				theme_items_list.append(theme_item.name)


	if obj not in theme_items_list:
		# Save the topic 
		topic_node = collection.GSystem()
		topic_node.name = unicode(obj).strip()
		topic_node.access_policy = u"PUBLIC"
		topic_node.contributors.append(1)
		topic_node.created_by = 1
		topic_node.group_set.append(group_id)
		topic_node.language = u"en"
		topic_node.member_of.append(topic_GST._id)
		topic_node.modified_by = 1
		topic_node.status = u"DRAFT"

		topic_node.save()

		# after saving successfully add into the collection_set of its prev node
		prev_node.collection_set.append(topic_node._id)
		prev_node.save()

	else:
		print "\n Topic ", obj," already available"

''' -- imports from python libraries -- '''
import os
import csv
import json
import ast
import datetime

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database
from django.template.defaultfilters import slugify
# from gnowsys_ndf.ndf.org2any import org2html
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

theme_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Theme' })
theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item' })
topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
nroer_team=User.objects.get(username = "nroer_team")
#grp = collection.Node.one({'_type': 'Group', '_id': ObjectId('53747277c1704121fe54be46')})
grp = node_collection.one({'_type': 'Group', 'name': 'home'})

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

                    	descrp = row[0]
                    	row = row[1:]

                    	r = []
                    	for each in row:
                    		r.append(each.strip())

                    	row = r
                        # print "\n row: ", row
                        # print "\n descrp: ",descrp,"\n"
                        create_theme(row, descrp)

                        i = i + 1

                        print "\n", i ," rows successfully compiled"
                        print " ======================================================="

                        # if (i == 3):
                            # break
                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))


def create_theme(row, descrp):
	# print "\n Its a theme -- ", obj
	# print "\n row: ", row,"\n"

	# To find the root themes to maintain the uniquness while creating new themes

	theme = row[0]
	theme_node = node_collection.one({'name': unicode(theme), 'group_set': group_id, 'member_of': theme_GST._id })
	if not theme_node:

		theme_node = node_collection.collection.GSystem()
		theme_node.name = unicode(theme)
		theme_node.access_policy = u"PUBLIC"
		theme_node.contributors.append(nroer_team.id)
		theme_node.created_by = nroer_team.id
		theme_node.group_set.append(group_id)
		theme_node.language = u"en"
		theme_node.member_of.append(theme_GST._id)
		theme_node.modified_by = nroer_team.id
		theme_node.status = u"PUBLISHED"

		theme_node.save()
	else:
		print "\nTheme ", theme_node.name," already available"


	if len(row) > 2:
		theme_items_list = row[1:-1]

		prev_node = theme_node

		for each in theme_items_list:
			theme_item_node = node_collection.one({'name': unicode(each), 'group_set': group_id, 'member_of': theme_item_GST._id, 'prior_node': prev_node._id })
			if not theme_item_node:
				theme_item_node = node_collection.collection.GSystem()
				theme_item_node.name = unicode(each)
				theme_item_node.access_policy = u"PUBLIC"
				theme_item_node.contributors.append(nroer_team.id)
				theme_item_node.created_by = nroer_team.id
				theme_item_node.group_set.append(group_id)
				theme_item_node.language = u"en"
				theme_item_node.member_of.append(theme_item_GST._id)
				theme_item_node.modified_by = nroer_team.id

				theme_item_node.prior_node.append(prev_node._id)
				theme_item_node.status = u"PUBLISHED"

				theme_item_node.save()
				# after saving successfully add into the collection_set of its prev node
				prev_node.collection_set.append(theme_item_node._id)
				prev_node.save()

				# Add this theme item as prior node for next theme item in for loop
				prev_node = theme_item_node

			else:
				prev_node = theme_item_node
				print "\n Theme Item ", theme_item_node.name," already available"



		topic = row[-1]
		topic_node = node_collection.one({'name': unicode(topic), 'group_set': group_id, 'member_of': topic_GST._id, 'prior_node': prev_node._id })
		if not topic_node:
			topic_node = node_collection.collection.GSystem()
			topic_node.name = unicode(topic)
			topic_node.access_policy = u"PUBLIC"
			topic_node.contributors.append(nroer_team.id)
			topic_node.created_by = nroer_team.id
			topic_node.group_set.append(group_id)
			if descrp:
				topic_node.content_org = unicode(descrp)
				# Required to link temporary files with the current user who is
				# modifying this document
				usrname = nroer_team.username
				filename = slugify(topic) + "-" + usrname + "-" + ObjectId().__str__()
				# topic_node.content = org2html(descrp, file_prefix=filename)
				topic_node.content = unicode(descrp)

			topic_node.language = u"en"
			topic_node.member_of.append(topic_GST._id)
			topic_node.modified_by = nroer_team.id
			topic_node.prior_node.append(prev_node._id)
			topic_node.status = u"PUBLISHED"

			topic_node.save()

			# after saving successfully add into the collection_set of its prev node
			prev_node.collection_set.append(topic_node._id)
			prev_node.save()

		else:
			print "\n Topic ", topic_node.name," already available"


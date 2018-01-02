''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.views.methods import filter_drawer_nodes
###################################################################################################################################################################################
collection = get_database()[Node.collection_name]  
page_gst = collection.Node.one({'_type': 'GSystemType', 'name': 'Page'})
file_gst = collection.Node.one({'_type': 'GSystemType', 'name': 'File'})
Pandora_video_gst = collection.Node.one({'_type': 'GSystemType', 'name': 'Pandora_video'})
quiz_gst = collection.Node.one({'_type': 'GSystemType', 'name': 'Quiz'})
quizItem_gst = collection.Node.one({'_type': "GSystemType", 'name': "QuizItem"})

class Command(BaseCommand):

    help = " This script will remove the loop from nodes collection_set "

    def handle(self, *args, **options):
    	
    	nodes = collection.Node.find({'_type': {'$in': ['GSystem', 'File']}, 
                              'collection_set': {'$exists': True, '$not': {'$size': 0} },
                              'member_of': {'$in': [page_gst._id,file_gst._id,Pandora_video_gst._id,quiz_gst._id,quizItem_gst._id] }
                            })

    	print "\nTotal ",nodes.count()," collections available which needs to be processed\n"
    	for each in nodes:
    		parents = filter_drawer_nodes(each._id)
    		for k in parents:
    			
    			if k in each.collection_set:
    				obj = collection.Node.one({'_id': ObjectId(k) })
    				collection.update({'_id': each._id}, {'$pull': {'collection_set': ObjectId(k) }}, upsert=False, multi=False)      
    				print "'",obj.name,"' removed successfully from '",each.name,"' collection\n"
    				print "#####################################################\n"

    		each.reload()
    		
    	print "sucessfully processed all collections\n"

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import node_collection,triple_collection
###################################################################################################################################################################################

class Command(BaseCommand):

    help = " This script will delete the pandora videos from 'home' group "

    def handle(self, *args, **options):


        pandora_video_st = node_collection.one({'_type': 'GSystemType','name': 'Pandora_video'})
        source_id_at=node_collection.one({'$and':[{'name':'source_id'},{'_type':'AttributeType'}]})

        if pandora_video_st and source_id_at:

            member_set=node_collection.find({'$and':[{'member_of': {'$all': [ObjectId(pandora_video_st._id)]}}, {'_type':'File'}]})
            gattribute=triple_collection.find({'_type':'GAttribute', 'attribute_type':source_id_at._id })
            for each in member_set:
                each.delete()
                print "Video ",each.name," removed from member_of successfully !!\n"

            for each in gattribute:
                each.delete()
                print "Video ",each.name," removed from attribute_set successfully !!\n"



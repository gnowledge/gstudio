''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node

####################################################################################################################

class Command(BaseCommand):

    help = " This script will add the new field(s) into already existing documents (only if they doesn't exists) in your database."

    def handle(self, *args, **options):
        collection = get_database()[Node.collection_name]
        # Keep latest fields to be added at top

        # -------------------------------------------------------------------------------------------------------------
        # Adding "location" field with no default value
        # -------------------------------------------------------------------------------------------------------------
        collection.update({'location': {'$exists': False}}, {'$set': {'location': {}}}, upsert=False, multi=True)
        collection.update({'language': {'$exists': False}}, {'$set': {'language': u''}}, upsert=False, multi=True)
        
        # -------------------------------------------------------------------------------------------------------------
        # Adding "access_policy" field
        # -------------------------------------------------------------------------------------------------------------
        # For Group documents, access_policy value is set depending upon their 
        # group_type values, i.e. either PRIVATE/PUBLIC whichever is there
        collection.update({'_type': 'Group', 'group_type': 'PRIVATE'}, {'$set': {'access_policy': u"PRIVATE"}}, upsert=False, multi=True)
        collection.update({'_type': 'Group', 'group_type': 'PUBLIC'}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)
        
        # For Non-Group documents which doesn't consits of access_policy field, add it with PUBLIC as it's default value
        collection.update({'_type': {'$nin': ['Group']}, 'access_policy': {'$exists': False}}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)
        
        collection.update({'_type': {'$nin': ['Group']}, 'access_policy': {'$in': [None, "PUBLIC"]}}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)
        collection.update({'_type': {'$nin': ['Group']}, 'access_policy': "PRIVATE"}, {'$set': {'access_policy': u"PRIVATE"}}, upsert=False, multi=True)

  		

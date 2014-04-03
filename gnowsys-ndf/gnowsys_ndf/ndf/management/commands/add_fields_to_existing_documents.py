''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node

###################################################################################################################################################################################

class Command(BaseCommand):

    help = " This script will add the new field(s) into already existing documents (only if they doesn't exists) in your database."

    def handle(self, *args, **options):
        collection = get_database()[Node.collection_name]
        # Keep latest fields to be added at top

        # Adding "modified_by" field with None as it's default value
        collection.update({'_type': {'$nin': ['GAttribute', 'GRelation']}, 'modified_by': {'$exists': False}}, {'$set': {'modified_by': None}}, upsert=False, multi=True)

        # Adding "property_order" field with empty list as it's default value
        collection.update( {'_type': 'GSystemType', 'property_order': {'$exists': False}}, {'$set': {'property_order': []}}, upsert=False, multi=True )

        # Adding "complex_data_type" field with empty list as it's default value
        collection.update( {'_type': 'AttributeType', 'complex_data_type': {'$exists': False}}, {'$set': {'complex_data_type': []}}, upsert=False, multi=True )

        # Adding "post_node" field with empty list as it's default value
        collection.update({'_type': {'$nin': ['GAttribute', 'GRelation']}, 'post_node': {'$exists': False}}, {'$set': {'post_node': []}}, upsert=False, multi=True)

        # Adding "collection_set" field with empty list as it's default value
        collection.update({'_type': {'$nin': ['GAttribute', 'GRelation']}, 'collection_set': {'$exists': False}}, {'$set': {'collection_set': []}}, upsert=False, multi=True)

        # Adding "location" field with no default value
        collection.update({'_type': {'$nin': ['GAttribute', 'GRelation']}, 'location': {'$exists': False}}, {'$set': {'location': []}}, upsert=False, multi=True)

        # Adding "language" field with no default value
        collection.update({'_type': {'$nin': ['GAttribute', 'GRelation']}, 'language': {'$exists': False}}, {'$set': {'language':unicode('')}}, upsert=False, multi=True)
        
        # Adding "access_policy" field
        # For Group documents, access_policy value is set depending upon their 
        # group_type values, i.e. either PRIVATE/PUBLIC whichever is there
        collection.update({'_type': 'Group', 'group_type': 'PRIVATE'}, {'$set': {'access_policy': u"PRIVATE"}}, upsert=False, multi=True)
        collection.update({'_type': 'Group', 'group_type': 'PUBLIC'}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)
        
        # For Non-Group documents which doesn't consits of access_policy field, add it with PUBLIC as it's default value
        collection.update({'_type': {'$nin': ['Group', 'GAttribute', 'GRelation']}, 'access_policy': {'$exists': False}}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)
        
        collection.update({'_type': {'$nin': ['Group', 'GAttribute', 'GRelation']}, 'access_policy': {'$in': [None, "PUBLIC"]}}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)
        collection.update({'_type': {'$nin': ['Group', 'GAttribute', 'GRelation']}, 'access_policy': "PRIVATE"}, {'$set': {'access_policy': u"PRIVATE"}}, upsert=False, multi=True)

  		

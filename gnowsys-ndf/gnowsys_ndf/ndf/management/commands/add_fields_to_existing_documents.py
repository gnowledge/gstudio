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

    # Removing existing "cr_or_xcr" field with no default value
    res = collection.update({'_type': {'$in': ['Group']}, 'cr_or_xcr': {'$exists': True}}, 
                            {'$unset': {'cr_or_xcr': False }}, 
                            upsert=False, multi=True
    )
    if res['n']:
           print "\n Already existing 'cr_or_xcr' field removed from documents totalling to : ", res['n']

    # Adding "curricular" field with no default value
    res = collection.update({'_type': {'$in': ['Group']}, 'curricular': {'$exists': False}}, 
                            {'$set': {'curricular': False }}, 
                            upsert=False, multi=True
    )
    print "\n 'curricular' field added to all Group documents totalling to : ", res['n']

    # Removing existing "partners" field with no default value
    res = collection.update({'_type': {'$in': ['Group']}, 'partners': {'$exists': True}}, 
                            {'$unset': {'partners': False }}, 
                            upsert=False, multi=True
    )
    if res['n']:
           print "\n Already existing 'partners' field removed from documents totalling to : ", res['n']

    # Adding "partner" field with no default value
    res = collection.update({'_type': {'$in': ['Group']}, 'partner': {'$exists': False}}, 
                            {'$set': {'partner': False }}, 
                            upsert=False, multi=True
    )
    print "\n 'partner' field added to all Group documents totalling to : ", res['n']



    # Adding "preferred_languages" field with no default value
    res = collection.update({'_type': {'$in': ['Author']}, 'preferred_languages': {'$exists': False}}, 
                            {'$set': {'preferred_languages': {}}}, 
                            upsert=False, multi=True
    )
    print "\n 'preferred_languages' field added to all author documents totalling to : ", res['n']
    


    # Adding "rating" field with no default value
    res = collection.update({'_type': {'$nin': ['GAttribute', 'GRelation']}, 'rating': {'$exists': False}}, 
                            {'$set': {'rating': []}}, 
                            upsert=False, multi=True
    )
    print "\n 'rating' field added to following no. of documents: ", res['n']
    
    # Adds 'subject_scope', 'attribute_type_scope', 'object_value_scope' field (with default value as "") to all documents which belongs to GAttribute
    res = collection.update({'_type': {'$in': ["Group", "Author"]}, 'group_admin': {'$exists': False}}, 
                            {'$set': {'group_admin': []}}, 
                            upsert=False, multi=True
    )
    print "\n 'group_admin' field added to following no. of documents: ", res['n']

    # Adds 'subject_scope', 'attribute_type_scope', 'object_value_scope' field (with default value as "") to all documents which belongs to GAttribute
    res = collection.update({'_type': "GAttribute", 'subject_scope': {'$exists': False}, 'attribute_type_scope': {'$exists': False}, 'object_value_scope': {'$exists': False}}, 
                            {'$set': {'subject_scope':"", 'attribute_type_scope':"", 'object_value_scope': ""}}, 
                            upsert=False, multi=True
    )
    print "\n 'subject_scope', 'attribute_type_scope', 'object_value_scope' fields added to following no. of documents: ", res['n']

    # Adds 'subject_scope', 'relation_type_scope', 'right_subject_scope' field (with default value as "") to all documents which belongs to GRelation
    res = collection.update({'_type': "GRelation", 'subject_scope': {'$exists': False}, 'relation_type_scope': {'$exists': False}, 'right_subject_scope': {'$exists': False}}, 
                            {'$set': {'subject_scope':"", 'relation_type_scope':"", 'right_subject_scope': ""}}, 
                            upsert=False, multi=True
    )
    print "\n 'subject_scope', 'relation_type_scope', 'right_subject_scope' fields added to following no. of documents: ", res['n']

    # Adds "annotations" field (with default value as []) to all documents belonging to GSystems
    res = collection.update({'_type': {'$nin': ["MetaType", "GSystemType", "RelationType", "AttributeType", "GRelation", "GAttribute"]}, 'annotations': {'$exists': False}}, 
                            {'$set': {'annotations': []}}, 
                            upsert=False, multi=True
    )
    print "\n annotations field added to following no. of documents: ", res['n']

    # Adds "group_set" field (with default value as []) to all documents except those which belongs to either GAttribute or GRelation
    res = collection.update({'_type': {'$nin': ["GAttribute", "GRelation"]}, 'group_set': {'$exists': False}}, 
                            {'$set': {'group_set': []}}, 
                            upsert=False, multi=True
    )
    print "\n group_set field added to following no. of documents: ", res['n']

    # Adds "property_order" field (with default value as []) to all documents except those which belongs to either GAttribute or GRelation
    res = collection.update({'_type': {'$nin': ["GAttribute", "GRelation"]}, 'property_order': {'$exists': False}}, 
                            {'$set': {'property_order': []}}, 
                            upsert=False, multi=True
    )
    print "\n property_order field added to following no. of documents: ", res['n']

    # Adding "modified_by" field with None as it's default value
    res = collection.update({'_type': {'$nin': ['GAttribute', 'GRelation']}, 'modified_by': {'$exists': False}}, 
                            {'$set': {'modified_by': None}}, 
                            upsert=False, multi=True
    )
    print "\n modified_by field added to following no. of documents: ", res['n']

    # Adding "complex_data_type" field with empty list as it's default value
    res = collection.update({'_type': 'AttributeType', 'complex_data_type': {'$exists': False}}, 
                            {'$set': {'complex_data_type': []}}, 
                            upsert=False, multi=True
    )
    print "\n complex_data_type field added to following no. of documents: ", res['n']

    # Adding "post_node" field with empty list as it's default value
    res = collection.update({'_type': {'$nin': ['GAttribute', 'GRelation']}, 'post_node': {'$exists': False}}, 
                            {'$set': {'post_node': []}}, 
                            upsert=False, multi=True
    )
    print "\n post_node field added to following no. of documents: ", res['n']

    # Adding "collection_set" field with empty list as it's default value
    res = collection.update({'_type': {'$nin': ['GAttribute', 'GRelation']}, 'collection_set': {'$exists': False}}, 
                            {'$set': {'collection_set': []}}, 
                            upsert=False, multi=True
    )
    print "\n collection_set field added to following no. of documents: ", res['n']

    # Adding "location" field with no default value
    res = collection.update({'_type': {'$nin': ['GAttribute', 'GRelation']}, 'location': {'$exists': False}}, 
                            {'$set': {'location': []}}, 
                            upsert=False, multi=True
    )
    print "\n location field added to following no. of documents: ", res['n'], "\n"

    # Adding "language" field with no default value
    res = collection.update({'_type': {'$nin': ['GAttribute', 'GRelation']}, 'language': {'$exists': False}}, 
                            {'$set': {'language': unicode('')}}, 
                            upsert=False, multi=True
    )
    
    # Adding "access_policy" field
    # For Group documents, access_policy value is set depending upon their 
    # group_type values, i.e. either PRIVATE/PUBLIC whichever is there
    collection.update({'_type': 'Group', 'group_type': 'PRIVATE'}, {'$set': {'access_policy': u"PRIVATE"}}, upsert=False, multi=True)
    collection.update({'_type': 'Group', 'group_type': 'PUBLIC'}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)
    
    # For Non-Group documents which doesn't consits of access_policy field, add it with PUBLIC as it's default value
    collection.update({'_type': {'$nin': ['Group', 'GAttribute', 'GRelation']}, 'access_policy': {'$exists': False}}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)
    
    collection.update({'_type': {'$nin': ['Group', 'GAttribute', 'GRelation']}, 'access_policy': {'$in': [None, "PUBLIC"]}}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)
    collection.update({'_type': {'$nin': ['Group', 'GAttribute', 'GRelation']}, 'access_policy': "PRIVATE"}, {'$set': {'access_policy': u"PRIVATE"}}, upsert=False, multi=True)

    

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
collection = get_database()[Node.collection_name]


class Command(BaseCommand):
  """This update-script updates fields' data-types or their values.
  """

  help = "\tThis update-script updates fields' data-types or their values."

  def handle(self, *args, **options):
    # Updates author_set field -- Appends creator's user-id to author_set field for existing Groups
    print "\n"
    for gn in collection.Node.find({'_type': {'$in': ["Group", "Author"]}}):
      # res = collection.update({'_id': gn._id, 'author_set': {'$nin': [gn.created_by]}}, 
      #                         {'$push': 
      #                                 {'author_set': 
      #                                               {'$each': [gn.created_by], 
      #                                               '$position': 0
      #                                               }
      #                                 }
      #                         }, 
      #                         upsert=False, multi=False)
      if gn.created_by not in gn.author_set:
        gn.author_set.insert(0, gn.created_by)
        res = collection.update({'_id': gn._id}, {'$set': {'author_set': gn.author_set}}, upsert=False, multi=False)
        if res['n']:
          print " Updated author_set field (appended created_by field's value at 0th index) for ", gn.name, "(", gn._id,")."

    # Renames field: 'modified_by' to 'contributors', if contributors field doesn't exists
    res = collection.update({'_type': {'$nin': ["GAttribute", "GRelation"]}, 'modified_by': {'$exists': True}, 'contributors': {'$exists': False}}, 
                            {'$rename': {'modified_by': "contributors"}}, 
                            upsert=False, multi=True)
    print "\n modified_by field updated (renamed with 'contributors') in following no. of documents: ", res['n']

    # Updates location fields' values from '{}' (empty dictionary) to '[]' (empty list)
    collection.update({'location': {}}, {'$set': {'location': []}}, upsert=False, multi=True)
    print "\n location field updated ({} to []}) in following no. of documents: ", res['n']
    
    print "\n"
    # --- End of handle() ---


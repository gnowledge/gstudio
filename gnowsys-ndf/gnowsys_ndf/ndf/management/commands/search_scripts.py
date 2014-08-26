from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.search_views import to_reduce_doc_requirement

collection = get_database()[Node.collection_name]

class Command(BaseCommand):
  option_list = BaseCommand.option_list

  user_defined_option_list = (
    make_option('-c', '--clean', action='store_true', dest='clean', default=False, help='Updates structure of existing ReducedDocs, ToReduceDocs & IndexedWordList documents whose structure gets affected by sync_existing_documents'),
    make_option('-r', '--reduce', action='store_true', dest='reduce', default=True, help='Creates map-reduced document and sets up url for various documents'),
    make_option('-s', '--no-reduce', action='store_false', dest='reduce', default=True, help='Dont map-reduce documents and set up url for various documents'),
  )

  option_list = option_list + user_defined_option_list

  def handle(self, *args, **options):
    try:
      if options['clean']:
        print "\n Updates structure of existing ReducedDocs, ToReduceDocs & IndexedWordList documents whose structure gets affected by sync_existing_documents"
        update_structure()
    except Exception as e:
      print "\n SearchScriptCleanError: " + str(e)
      pass

    try:
      if options['reduce']:
        print "\n Creates map-reduced document and sets up url for various documents \n"
        map_reduce_docs()

        print "\n **** Search script executed successfully. ****\n"
    except Exception as e:
      print "\n SearchScriptReduceError: " + str(e)
      pass


def update_structure():
  '''
  Updates structure of existing ReducedDocs, ToReduceDocs & IndexedWordList documents whose structure gets affected by sync_existing_documents
  '''

  # For ReducedDocs
  rd_cur = collection.ReducedDocs.find({'is_indexed': {'$exists': True}, 'license': {'$exists': True}})
  print "\n No. of ReducedDocs document(s) with invalid structure found: ", rd_cur.count()
  if rd_cur.count():
    c = 0
    print " Updating:"
    for i, each in enumerate(rd_cur):
      res = collection.update({'_id': each._id}, 
                              {'$unset': {'access_policy': "", 'annotations': "", 'collection_set': "", 'group_set': "", 'language': "", 'license': "", 'location': "", 'modified_by': "", 'post_node': "", 'property_order': "", 'rating': ""},
                                '$set': {'_type': u'ReducedDocs'}
                              },
                              upsert=False, multi=False
                              )
      if res['n']:
        c = c + 1
        print " .",

    print "\n No. of ReducedDocs documents' structure cleaned (& added _type field): ", c, "\n"

  # For ToReduceDocs
  trd_cur = collection.ToReduceDocs.find({'doc_id': {'$exists': True}, 'license': {'$exists': True}})
  print "\n No. of ToReduceDocs document(s) with invalid structure found: ", trd_cur.count()
  if trd_cur.count():
    c = 0
    print " Updating:"
    for i, each in enumerate(trd_cur):
      res = collection.update({'_id': each._id}, 
                              {'$unset': {'access_policy': "", 'annotations': "", 'collection_set': "", 'group_set': "", 'language': "", 'license': "", 'location': "", 'modified_by': "", 'post_node': "", 'property_order': "", 'rating': ""},
                                '$set': {'_type': u'ToReduceDocs'}
                              },
                              upsert=False, multi=False
                              )
      if res['n']:
        c = c + 1
        print " .",

    print "\n No. of ToReduceDocs document(s)' structure cleaned (& added _type field): ", c, "\n"

  # For IndexedWordList
  iwl_cur = collection.IndexedWordList.find({'word_start_id': {'$exists': True}, 'license': {'$exists': True}})
  print "\n No. of IndexedWordList document(s) with invalid structure found: ", iwl_cur.count()
  if iwl_cur.count():
    c = 0
    print " Updating:"
    for i, each in enumerate(iwl_cur):
      res = collection.update({'_id': each._id}, 
                              {'$unset': {'access_policy': "", 'annotations': "", 'collection_set': "", 'group_set': "", 'language': "", 'license': "", 'location': "", 'modified_by': "", 'post_node': "", 'property_order': "", 'rating': ""},
                                '$set': {'_type': u'IndexedWordList'}
                              },
                              upsert=False, multi=False
                              )
      if res['n']:
        c = c + 1
        print " .",

    print "\n No. of IndexedWordList document(s)' structure cleaned (& added _type field): ", c, "\n"

def map_reduce_docs():
  '''
  Creates map-reduced document and sets up url for various documents
  '''
  # I'm assuming this section creates reduced doc and sets up url

  # to_reduce_doc_requirement = u'storing_to_be_reduced_doc' 

  allNulls = collection.Node.find({"_type":"GSystem", "access_policy":None})
  for obj in allNulls:
    old_doc = collection.ToReduceDocs.find_one({'required_for':to_reduce_doc_requirement,'doc_id':ObjectId(obj._id)})
    if  old_doc is None:
      obj.access_policy = u'PUBLIC'
      obj.save()

  allGSystems = collection.Node.find({"_type":"GSystem"})
  Gapp_obj = collection.Node.one({"_type":"MetaType", "name":"GAPP"})
  factory_obj = collection.Node.one({"_type":"MetaType", "name":"factory_types"})
  for gs in allGSystems:
    old_doc = collection.ToReduceDocs.find_one({'required_for':to_reduce_doc_requirement,'doc_id':ObjectId(gs._id)})
    if old_doc is None:
      gsType = gs.member_of[0]
      gsType_obj = collection.Node.one({"_id":ObjectId(gsType)})
      if Gapp_obj._id in gsType_obj.member_of:
        if gsType_obj.name == u"Quiz":
          gs.url = u"quiz/details"
        else:
          gs.url = gsType_obj.name.lower()
      elif factory_obj._id in gsType_obj.member_of:
        if gsType_obj.name == u"QuizItem":
          gs.url = u"quiz/details"
        if gsType_obj.name == u"Twist":
          gs.url = u"forum/thread"
        else:
          gs.url = gsType_obj.name.lower()
      else:
        gs.url = u"None"
      gs.save()
    else:
      print "\n This document ("+str(gs._id)+") is already map-reduced."   

  allGSystems = collection.Node.find({"$or": [ {"_type":"GSystem"}, {"_type":"File"} ] })
  for gs in allGSystems:
    old_doc = collection.ToReduceDocs.find_one({'required_for':to_reduce_doc_requirement,'doc_id':ObjectId(gs._id)})
    if old_doc is None:  
      gs.save()


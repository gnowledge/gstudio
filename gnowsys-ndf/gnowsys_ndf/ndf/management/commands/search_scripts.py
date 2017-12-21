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
        print "\n Sets up url of documents for GSystem and File \n"
        setup_urls()

        print "\n **** Search script executed successfully. ****\n"
    except Exception as e:
      print "\n SearchScriptReduceError: " + str(e)
      pass


def update_structure():
  '''
  Updates structure of existing ReducedDocs, ToReduceDocs & IndexedWordList documents whose structure gets affected by sync_existing_documents
  '''

  # For ReducedDocs
  rd_cur = collection.ReducedDocs.find({'is_indexed': {'$exists': True}, 'legal': {'$exists': True}})
  print "\n No. of ReducedDocs document(s) with invalid structure found: ", rd_cur.count()
  if rd_cur.count():
    c = 0
    print " Updating:"
    for i, each in enumerate(rd_cur):
      res = collection.update({'_id': each._id}, 
                              {'$unset': {'access_policy': "", 'annotations': "", 'collection_set': "", 'group_set': "", 'language': "", 'legal': "", 'location': "", 'modified_by': "", 'post_node': "", 'property_order': "", 'rating': ""},
                                '$set': {'_type': u'ReducedDocs'}
                              },
                              upsert=False, multi=False
                              )
      if res['n']:
        c = c + 1
        print " .",

    print "\n No. of ReducedDocs documents' structure cleaned (& added _type field): ", c, "\n"

  # For ToReduceDocs
  trd_cur = collection.ToReduceDocs.find({'doc_id': {'$exists': True}, 'legal': {'$exists': True}})
  print "\n No. of ToReduceDocs document(s) with invalid structure found: ", trd_cur.count()
  if trd_cur.count():
    c = 0
    print " Updating:"
    for i, each in enumerate(trd_cur):
      res = collection.update({'_id': each._id}, 
                              {'$unset': {'access_policy': "", 'annotations': "", 'collection_set': "", 'group_set': "", 'language': "", 'legal': "", 'location': "", 'modified_by': "", 'post_node': "", 'property_order': "", 'rating': ""},
                                '$set': {'_type': u'ToReduceDocs'}
                              },
                              upsert=False, multi=False
                              )
      if res['n']:
        c = c + 1
        print " .",

    print "\n No. of ToReduceDocs document(s)' structure cleaned (& added _type field): ", c, "\n"

  # For IndexedWordList
  iwl_cur = collection.IndexedWordList.find({'word_start_id': {'$exists': True}, 'legal': {'$exists': True}})
  print "\n No. of IndexedWordList document(s) with invalid structure found: ", iwl_cur.count()
  if iwl_cur.count():
    c = 0
    print " Updating:"
    for i, each in enumerate(iwl_cur):
      res = collection.update({'_id': each._id}, 
                              {'$unset': {'access_policy': "", 'annotations': "", 'collection_set': "", 'group_set': "", 'language': "", 'legal': "", 'location': "", 'modified_by': "", 'post_node': "", 'property_order': "", 'rating': ""},
                                '$set': {'_type': u'IndexedWordList'}
                              },
                              upsert=False, multi=False
                              )
      if res['n']:
        c = c + 1
        print " .",

    print "\n No. of IndexedWordList document(s)' structure cleaned (& added _type field): ", c, "\n"

def setup_urls():
  '''
  Sets up url of documents for GSystem and File
  '''
  # I'm assuming this section sets up url
  # to_reduce_doc_requirement = u'storing_to_be_reduced_doc' 

  # Replacing access_policy value from None to "PUBLIC" of all documents for GSystems and Files
  allNulls = collection.Node.find({"_type": {'$in': [u"GSystem", u"File"]}, "access_policy": {'$in': [None, u"None"]}})
  ap_cnt = allNulls.count()
  ap_c = 0
  if ap_cnt:
    print "\n Updating access_policy: "
    for obj in allNulls:
      if obj.access_policy == None or obj.access_policy == u"None":
        obj.access_policy = u'PUBLIC'
        obj.save()
        ap_c = ap_c + 1
        print " .",

  # Setting up urls
  allGSystems = collection.Node.find({"_type": {'$in': [u"GSystem", u"File"]}})
  Gapp_obj = collection.Node.one({"_type": "MetaType", "name": "GAPP"})
  factory_obj = collection.Node.one({"_type":"MetaType", "name":"factory_types"})
  u_cnt = allGSystems.count()
  u_c = 0
  if u_cnt:
    print " Updating url: "
    for gs in allGSystems:
      gsType = gs.member_of[0]
      gsType_obj = collection.Node.one({"_id": ObjectId(gsType)})
      is_url_changed = False

      if Gapp_obj._id in gsType_obj.member_of:
        if gsType_obj.name == u"Quiz":
          url = u"quiz/details"
          if gs.url != url:
            gs.url = url
            is_url_changed = True
        else:
          url = gsType_obj.name.lower()
          if gs.url != url:
            gs.url = url
            is_url_changed = True

      elif factory_obj._id in gsType_obj.member_of:
        if gsType_obj.name == u"QuizItem":
          url = u"quiz/details"
          if gs.url != url:
            gs.url = url
            is_url_changed = True

        if gsType_obj.name == u"Twist":
          url = u"forum/thread"
          if gs.url != url:
            gs.url = url
            is_url_changed = True
        else:
          url = gsType_obj.name.lower()
          if gs.url != url:
            gs.url = url
            is_url_changed = True

      else:
        if gs.url != None:
          gs.url = None
          is_url_changed = True

      # Save document only when it's url is changed
      if is_url_changed:
        gs.save()
        u_c = u_c + 1
        print " .",

  print "\n Document(s) found with None as access_policy: ", ap_cnt
  print " No. of document(s) whose 'access_policy' field updated: ", ap_c, "\n"

  print "\n No. of GSystem(s) [including File(s)] found: ", u_cnt
  print " No. of document(s) whose 'url' field updated: ", u_c, "\n"


  # Avadoot: I didn't got what the below piece of code does, so commenting it!
  # allGSystems = collection.Node.find({"_type": {'$in': [u"GSystem", u"File"]}})
  # for gs in allGSystems:
  #   gs.save()


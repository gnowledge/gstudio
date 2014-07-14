from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.search_views import *
from django.core.management.base import BaseCommand, CommandError

col = get_database()[Node.collection_name]
allNulls = col.Node.find({"_type":"GSystem", "access_policy":None})
for obj in allNulls:
    obj.access_policy = u'PUBLIC'
    obj.save()
    

allGSystems = col.Node.find({"_type":"GSystem"})
Gapp_obj = col.Node.one({"_type":"MetaType", "name":"GAPP"})
factory_obj = col.Node.one({"_type":"MetaType", "name":"factory_types"})

for gs in allGSystems:
    gsType = gs.member_of[0]
    gsType_obj = col.Node.one({"_id":ObjectId(gsType)})
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
    
allGSystems = col.Node.find({"$or": [ {"_type":"GSystem"}, {"_type":"File"} ] })
for gs in allGSystems:
	gs.save()

"""
dltr=list(collection.ToReduceDocs.find({'required_for':to_reduce_doc_requirement}))

for doc in dltr:
	doc_id = doc.doc_id
	orignal_doc = collection.Node.find_one({"_id":doc_id})
	content_dict = dict(map_reduce(orignal_doc.content_org,mapper,reducer))
	
	dord = collection.ReducedDocs.find_one({"orignal_id":doc_id,'required_for':reduced_doc_requirement}) #doc of reduced docs
	if dord:
		dord.content=content_dict
		dord.is_indexed = False
		dord.save()
	else:
		new_doc = collection.ReducedDocs()
		new_doc.content = content_dict
		new_doc.orignal_id = doc_id
		new_doc.required_for = reduced_doc_requirement
		new_doc.is_indexed = False
		new_doc.save()
	doc.delete()	
"""
class Command(BaseCommand):
	def handle(self, *args, **options):
		print "search script executed."

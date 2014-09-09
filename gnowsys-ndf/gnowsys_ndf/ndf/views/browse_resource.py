
''' -- imports from installed packages -- ''' 
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django_mongokit import get_database
from gnowsys_ndf.ndf.org2any import org2html

try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import Node, GRelation,GSystemType,File,Triple
from gnowsys_ndf.ndf.views.file import *

#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
collection_tr = db[Triple.collection_name]
GST_browse_resource = collection.GSystemType.one({'_type':'GSystemType', 'name': 'Browse Resource'})
app = collection.GSystemType.one({'_type':'GSystemType', 'name': 'Browse Resource'})
pandoravideoCollection=collection.Node.find({'member_of':pandora_video_st._id})

#######################################################################################################################################

def resource_list(request,group_id,app_id=None):

	ins_objectid  = ObjectId()
	is_video = request.GET.get('is_video', "")
	if ins_objectid.is_valid(group_id) is False :
		group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		if group_ins:
		    group_id = str(group_ins._id)
		else :
		    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		    if auth :
		        group_id = str(auth._id)
	else :
	    pass
	if app_id is None:
	    app_ins = collection.Node.find_one({'_type':'GSystemType', 'name': 'Browse Resource'})
	    if app_ins:
	        app_id = str(app_ins._id)


	# if GST_browse_resource._id == ObjectId(app_id):
	"""
	* Renders a list of all 'Resources(XCR)' available within the database.
	"""
	title = GST_browse_resource.name

	file_id = GST_FILE._id
	datavisual = []
	 
	files = collection.Node.find({'$or':[{'member_of': {'$all': [ObjectId(file_id)]}, 
	                                '_type': 'File', 'fs_file_ids':{'$ne': []}, 
	                                'group_set': {'$all': [ObjectId(group_id)]},
	                                '$or': [
	                                  {'access_policy': u"PUBLIC"},
	                                  {'$and': [
	                                      {'access_policy': u"PRIVATE"}, 
	                                      {'created_by': request.user.id}
	                                    ]
	                                  }
	                                ]
	                              },
                                    {'member_of': {'$all': [pandora_video_st._id]}}
                                       ]}).sort("last_update", -1)

	# docCollection = collection.Node.find({'member_of': {'$nin': [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id)]}, 
	#                                         '_type': 'File','fs_file_ids': {'$ne': []}, 
	#                                         'group_set': {'$all': [ObjectId(group_id)]},
	#                                         '$or': [
	#                                           {'access_policy': u"PUBLIC"},
	#                                           {'$and': [
	#                                             {'access_policy': u"PRIVATE"}, 
	#                                             {'created_by': request.user.id}
	#                                             ]
	#                                           }
	#                                         ]
	#                                       }).sort("last_update", -1)
	  
	imageCollection = collection.Node.find({'member_of': {'$all': [ObjectId(GST_IMAGE._id)]}, 
	                                          '_type': 'File','fs_file_ids': {'$ne': []}, 
	                                          'group_set': {'$all': [ObjectId(group_id)]},
	                                          '$or': [
	                                            {'access_policy': u"PUBLIC"},
	                                            {'$and': [
	                                              {'access_policy': u"PRIVATE"}, 
	                                              {'created_by': request.user.id}
	                                              ]
	                                            }
	                                          ]
	                                        }).sort("last_update", -1)
	  
	videoCollection = collection.Node.find({'member_of': {'$all': [ObjectId(GST_VIDEO._id)]}, 
	                                          '_type': 'File','fs_file_ids': {'$ne': []}, 
	                                          'group_set': {'$all': [ObjectId(group_id)]},
	                                          '$or': [
	                                            {'access_policy': u"PUBLIC"},
	                                            {'$and': [
	                                              {'access_policy': u"PRIVATE"}, 
	                                              {'created_by': request.user.id}
	                                              ]
	                                            }
	                                          ]
	                                        }).sort("last_update", -1)


	# Interactives
	coll = []
	for each in files:
		coll.append(each._id)

	gattr = collection.Node.one({'_type': 'AttributeType', 'name': u'educationaluse'})
	interCollection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id, "subject": {'$in': coll} ,"object_value": "Interactives"}).sort("last_update", -1)
	d_Collection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id, "subject": {'$in': coll} ,"object_value": "Documents"}).sort("last_update", -1)
	aud_Collection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id, "subject": {'$in': coll} ,"object_value": "Audios"}).sort("last_update", -1)

	# For manipulating documents
	doc = []
	for e in d_Collection:
		doc.append(e.subject)

	docCollection = collection.Node.find({'_id': {'$in': doc} })    
	# End of fetching the documents

	# For manipulating interactives
	interactive = []
	for e in interCollection:
		interactive.append(e.subject)

	interactiveCollection = collection.Node.find({'_id': {'$in': interactive} })    
	# End of fetching the interactives

	# For manipulating documents
	audio = []
	for e in aud_Collection:
		audio.append(e.subject)

	audioCollection = collection.Node.find({'_id': {'$in': audio} })    
	# End of fetching the documents
	
	files.rewind()
	already_uploaded = request.GET.getlist('var', "")

	get_member_set = collection.Node.find({'$and':[{'member_of': {'$all': [ObjectId(pandora_video_st._id)]}},{'_type':'File'}]})

	datavisual.append({"name":"Doc", "count":docCollection.count()})
	datavisual.append({"name":"Image","count":imageCollection.count()})
	datavisual.append({"name":"Video","count":videoCollection.count()})
	datavisual.append({"name":"Interactives","count":interactiveCollection.count()})
	datavisual.append({"name":"Audios","count":audioCollection.count()})
	datavisual = json.dumps(datavisual)

	print "\ntitle: ",title,"\n"
	return render_to_response("ndf/resource_list.html", 
                                {'title': title, 
                                 'appId':app._id,
                                 'already_uploaded': already_uploaded,
                                 'files': files, 'docCollection': docCollection, 'imageCollection': imageCollection,
                                 'videoCollection': videoCollection, 'pandoravideoCollection':pandoravideoCollection,
                                 'pandoraCollection':get_member_set,'interactiveCollection': interactiveCollection,
                                 'audioCollection':audioCollection,
                                 'is_video':is_video,'groupid': group_id, 'group_id':group_id,"datavisual":datavisual
                                }, 
                                context_instance = RequestContext(request))

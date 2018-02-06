''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
import subprocess

''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from django.http import Http404, HttpResponse

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection, NodeJSONEncoder


import re
import urllib

''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response
from django.template import RequestContext
from mongokit import paginator
from django.core.paginator import Paginator


try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
# from gnowsys_ndf.ndf.models import Node, GRelation,GSystemType,File,Triple
from gnowsys_ndf.ndf.models import Node, GRelation,GSystemType, Triple
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.file import *


from gnowsys_ndf.ndf.views.methods import get_group_name_id, cast_to_data_type, get_execution_time
from gnowsys_ndf.ndf.views.methods import get_filter_querydict
from elasticsearch import Elasticsearch

es = Elasticsearch("http://elastic:changeme@gsearch:9200", timeout=100, retry_on_timeout=True)

#GST_PAGE = node_collection.one({'_type':'GSystemType', 'name': 'page'})
#GST_IMAGE = node_collection.one({'_type':'GSystemType', 'name': 'image'})
##GST_VIDEO = node_collection.one({'_type':'GSystemType', 'name': GAPPS[4]})
#e_library_GST = node_collection.one({'_type':'GSystemType', 'name': 'E-Library'})
#pandora_video_st = node_collection.one({'_type':'GSystemType', 'name': 'Pandora_video'})
#app = node_collection.one({'_type':'GSystemType', 'name': 'E-Library'})
#wiki_page = node_collection.one({'_type': 'GSystemType', 'name': 'Wiki page'})
#GST_JSMOL = node_collection.one({"_type":"GSystemType","name":"Jsmol"})
GST_FILE =  res = es.search(index="nodes", doc_type="gsystemtype", body={
                        "query":   {"bool":{"must":  [ {"term":  {"name":"file"}  }]  }}})
print "----------------------"
print GST_FILE

GST_PAGE =  res = es.search(index="nodes", doc_type="gsystemtype", body={
                        "query":   {"bool":{"must":  [ {"term":  {"name":"page"}  }]  }}})

GST_IMAGE =  res = es.search(index="nodes", doc_type="gsystemtype", body={
                        "query":   {"bool":{"must":  [ {"term":  {"name":"image"}  }]  }}})
#print ebook_gst
GST_VIDEO =   es.search(index="nodes", doc_type="gsystemtype", body={
                        "query": {"bool": {"must": [{"term": {"name":"video"}}]}}})
e_library_GST =  es.search(index="nodes", doc_type="gsystemtype", body={
                        "query": {"bool": {"must": [{"term": {"name":"library"}}]}}})
#print e_library_GST
pandora_video_st = es.search(index="nodes", doc_type="gsystemtype", body={
                        "query":   {"bool":{"must":  [ {"term":  {"name":"pandora"}  }]  }}})

app  = es.search(index="nodes", doc_type="gsystemtype", body={
                        "query":   {"bool":{"must":  [ {"term":  {"name":"library"}  }]  }}})

#print ebook_gst
wiki_page =   es.search(index="nodes", doc_type="gsystemtype", body={
                        "query": {"bool": {"must": [{"term": {"name":"wiki"}}]}}})
GST_JSMOL =  es.search(index="nodes", doc_type="gsystemtype", body={
                        "query": {"bool": {"must": [{"term": {"name":"Jsmol"}}]}}})

def query_doc(request, doc_id_or_name=None, option=None):

	if ObjectId.is_valid(doc_id_or_name):
		doc_id_or_name = ObjectId(doc_id_or_name)

	query_res = node_collection.find({
								'$or': [
										{'_id': doc_id_or_name},
										{'name': unicode(doc_id_or_name)}
									]
								})

	result = []
	for each_doc in query_res:
		if option in ['nbh', 'NBH', 'get_neighbourhood']:
			each_doc.get_neighbourhood(each_doc.member_of)
		result.append(json.dumps(each_doc, cls=NodeJSONEncoder, sort_keys=True))

	return render_to_response('ndf/dev_query_doc.html',
					        {'result': result, 'query': doc_id_or_name, 'count': query_res.count()},
					        context_instance=RequestContext(request)
						    )


def render_test_template(request,group_id='home', app_id=None, page_no=1):

	is_video = request.GET.get('is_video', "")


	try:
		group_id = ObjectId(group_id)
		#print group_id
	except:
		group_name, group_id = get_group_name_id(group_id)
		#print group_id, group_name
	temp=[]


	for a in app['hits']['hits']:
		temp1=ObjectId(a['_source']['id'])
		temp.append(temp1)

	app_gst_name=[]
	for a in app['hits']['hits']:
		temp1=a['_source']['name']
		app_gst_name.append(temp1)

	if app_id is None:
		 app_id = str(temp)

	e_library_GST_temp=[]

	for a in e_library_GST['hits']['hits']:
		temp1=a['_source']['name']
		e_library_GST_temp.append(temp1)

	
	#print e_library_GST_temp
	#title = e_library_GST.name
	title = e_library_GST_temp
	#print title

	GST_FILE_temp=[]
	for a in GST_FILE['hits']['hits']:
		#temp1=ObjectId(a['_source']['id'])
		temp1=a['_source']['id']
		GST_FILE_temp.append(temp1)

	#file_id = GST_FILE._id
	GST_JSMOL_temp=[]
	for a in GST_JSMOL['hits']['hits']:
		temp1=ObjectId(a['_source']['id'])
		GST_JSMOL_temp.append(temp1)

	GST_PAGE_temp=[]
	for a in GST_PAGE['hits']['hits']:
		temp1=ObjectId(a['_source']['id'])
		GST_PAGE_temp.append(temp1)
	


	file_id = GST_FILE_temp
	#print file_id
	datavisual = []
	no_of_objs_pp = 24

	query_dict = []
	# query_dict = filters

	selfilters = urllib.unquote(request.GET.get('selfilters', ''))
	if selfilters:
		selfilters = json.loads(selfilters)
		query_dict = get_filter_querydict(selfilters)

	query_dict.append({'attribute_set.educationaluse': {'$ne': 'eBooks'}})



	files = node_collection.find({
									# 'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
									#'member_of': {'$in': [GST_FILE._id,GST_JSMOL._id]},
									'member_of': {'$in': [GST_FILE_temp,GST_JSMOL_temp]},

									# '_type': 'File',
									# 'fs_file_ids': {'$ne': []},
									'group_set': {'$all': [ObjectId(group_id)]},
									'$and': query_dict,
									'$or': [
											{ 'access_policy': u"PUBLIC" },
											{ '$and': [
														{'access_policy': u"PRIVATE"},
														{'created_by': request.user.id}
													]
											}
										]
									}).sort("last_update", -1)

	print GST_FILE_temp
	files1 =  res = es.search(index="nodes", doc_type="gsystemtype,gsystem", body={
                        "query":   {"bool": { "must":  [ {"term":  {"group_set": str(ObjectId(group_id))}  },{"term": {"access_policy": "public"}}],
     										 "must_not":  [ {"term":  {"attribute_set.educationaluse": "ebooks" } } ],
     										 "must":  [ {"terms":  {"member_of": GST_FILE_temp } } ],
     										 "must":[  {"term": {'access_policy':'public'}} ]

     										 #"must":  [ {"term":  {'created_by': request.user.id}}],

     } }} )
	files1_temp = []
	for each in files1['hits']['hits']:
		files1_temp=each['_source']

	

	print "----------------------------------------------------------"
	#print files1
	# print "files.count : ", files.count()

  	# pageCollection=node_collection.find({'member_of':GST_PAGE._id, 'group_set': ObjectId(group_id),
  	# 									'$or': [
			# 									{ 'access_policy': u"PUBLIC" },
			# 									{ '$and': [
			# 												{'access_policy': u"PRIVATE"},
			# 												{'created_by': request.user.id}
			# 											]
			# 									}
			# 								],
			# 							'type_of': {'$in': [wiki_page._id]}
			# 							}).sort("last_update", -1)

	images_count =   es.search(index="gsystem", doc_type="image", body={
                        "query":   {"bool":{"must":  [ {"term":  {"status":"published"}  }]  }}})
	audios_count =   es.search(index="gsystem", doc_type="audio", body={
                        "query":   {"bool":{"must":  [ {"term":  {"status":"published"}  }]  }}})
	videos_count =   es.search(index="gsystem", doc_type="video", body={
                        "query":   {"bool":{"must":  [ {"term":  {"status":"published"}  }]  }}})
	applications_count =  es.search(index="gsystem", doc_type="application", body={
                        "query":   {"bool":{"must":  [ {"term":  {"status":"published"}  }]  }}})
	all_count =   es.search(index="gsystem", doc_type="images,audios,videos,application", body={
                        "query":   {"bool":{"must":  [ {"term":  {"status":"published"}  }]  }}})



	educationaluse_stats = {}


	if files1_temp:
		eu_list = []  # count
		#for each in files1_temp:
		#	eu_list += [i.get("educationaluse") for i in each.attribute_type_set if i.has_key("educationaluse")]

		#files1_temp.rewind()

		if set(eu_list):
			if len(set(eu_list)) > 1:
				educationaluse_stats = dict((x, eu_list.count(x)) for x in set(eu_list))
			elif len(set(eu_list)) == 1:
				educationaluse_stats = { eu_list[0]: eu_list.count(eu_list[0])}
			educationaluse_stats["all"] = files.count()
		

		# print educationaluse_stats
		result_paginated_cur = files
		result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)


	#print request.user.id
	#print "--------------"
	

	collection_pages_cur = node_collection.find({
									'member_of': {'$in': [GST_FILE_temp, GST_PAGE_temp ]},
                                    'group_set': {'$all': [ObjectId(group_id)]},
                                    '$and': query_dict,
                                    '$or': [
                                        {'access_policy': u"PUBLIC"},
                                        {'$and': [
                                            {'access_policy': u"PRIVATE"},
                                            {'created_by': request.user.id}
                                        ]
                                     }
                                    ],
                                    'collection_set': {'$exists': "true", '$not': {'$size': 0} }
                                }).sort("last_update", -1)

	GST_PAGE_collection=[]
	for a in GST_PAGE['hits']['hits']:
		temp1=a['_source']['id']
		GST_PAGE_collection.append(temp1)



	collection_pages_cur1 =  res = es.search(index="nodes", doc_type="gsystemtype,gsystem", body={
                        "query":   {"bool": { "must":  [ {"term":  {"group_set": str(ObjectId(group_id))}  },{"term": {"access_policy": "public"}}],
     										 "must_not":  [ {"term":  {"attribute_set.educationaluse": "ebooks" } } ],
     										 #"must":  [ {"term":  {'created_by': request.user.id}}],
     										 "must":  [ {"terms":  {'member_of': GST_FILE_temp }}],
     										 "must":  [ {"terms":  {'member_of': GST_PAGE_collection}}],
     										 "must": {"exists": {"field":"collection_set"}},
     } }} )
	print collection_pages_cur

	#coll_page_count = collection_pages_cur.count() if collection_pages_cur else 0
	coll_page_count = collection_pages_cur1['hits']['total'] if collection_pages_cur1 else 0
	collection_pages = paginator.Paginator(collection_pages_cur, page_no, no_of_objs_pp)
	datavisual.append({"name":"Doc", "count": educationaluse_stats.get("Documents", 0)})
	datavisual.append({"name":"Page", "count": educationaluse_stats.get("Pages", 0)})
	datavisual.append({"name":"Image","count": educationaluse_stats.get("Images", 0)})
	datavisual.append({"name":"Video","count": educationaluse_stats.get("Videos", 0)})
	datavisual.append({"name":"Interactives","count": educationaluse_stats.get("Interactives", 0)})
	datavisual.append({"name":"Audios","count": educationaluse_stats.get("Audios", 0)})
	datavisual.append({"name":"eBooks","count": educationaluse_stats.get("eBooks", 0)})
	if collection_pages_cur:
		datavisual.append({"name":"Collections","count": coll_page_count})
	datavisual = json.dumps(datavisual)

	title=''.join(title)
	#test_node = node_collection.one({"name":"home", '_type':"Group"})
	app_gst=''.join(app_gst_name)
	

	return render_to_response(
        'ndf/test_template.html',
        {'title': title, 'app':e_library_GST,
								 'appId':app_id, "app_gst": app_gst,
								 # 'already_uploaded': already_uploaded,'shelf_list': shelf_list,'shelves': shelves,
								 'files': files1_temp,
								 "detail_urlname": "file_detail",
								 'ebook_pages': educationaluse_stats.get("eBooks", 0),
								 # 'page_count': pageCollection.count(),
								 # 'page_nodes':pageCollection
								 'file_pages': result_pages,
								 'image_pages': images_count['hits']['total'],
								 'interactive_pages': educationaluse_stats.get("Interactives", 0),
								 'educationaluse_stats': json.dumps(educationaluse_stats),
								 #'doc_pages': educationaluse_stats.get("Documents", 0),
								 #'video_pages': educationaluse_stats.get("Videos", 0),
								 #'audio_pages': educationaluse_stats.get("Audios", 0),
								 'doc_pages': applications_count['hits']['total'],
								 'video_pages': videos_count['hits']['total'],
								 'audio_pages': audios_count['hits']['total'],
								 'collection_pages': collection_pages,
								 'collection': collection_pages_cur1['hits']['hits'],

								 'collection_count': collection_pages_cur1['hits']['total'],
								 'groupid': group_id, 'group_id':group_id,
								 "datavisual":datavisual},
        context_instance=RequestContext(request)
    )


def git_branch(request):
	return HttpResponse(subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']),
		content_type="text/plain")
	
def git_misc(request, git_command):
	response = "Unsupported"
	if git_command in ['log', 'branch', 'status', 'tag', 'show', 'diff']:
		response = subprocess.check_output(['git', git_command])
	return HttpResponse(response, content_type="text/plain")

	

import json

''' -- imports from installed packages -- ''' 
from django.shortcuts import render_to_response
from django.template import RequestContext
# from django.core.urlresolvers import reverse
from mongokit import paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
# from gnowsys_ndf.ndf.models import Node, GRelation, GSystemType, File, Triple
from gnowsys_ndf.ndf.models import node_collection
# from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id, cast_to_data_type, get_execution_time
from gnowsys_ndf.ndf.views.methods import get_filter_querydict
from elasticsearch import Elasticsearch

# GST_IMAGE = node_collection.one({'_type':'GSystemType', 'name': u"Image"})

es = Elasticsearch("http://elastic:changeme@gsearch:9200", timeout=100, retry_on_timeout=True)

#ebook_gst = node_collection.one({'_type':'GSystemType', 'name': u"E-Book"})
#GST_FILE = node_collection.one({'_type':'GSystemType', 'name': u"File"})
#GST_PAGE = node_collection.one({'_type':'GSystemType', 'name': u'Page'})

ebook_gst =  res = es.search(index="nodes", doc_type="gsystemtype", body={
                        "query":   {"bool":{"must":  [ {"term":  {"name":"book"}  }]  }}},size=20)
#print ebook_gst


GST_FILE =   es.search(index="nodes", doc_type="gsystemtype", body={
                        "query": {"bool": {"must": [{"term": {"name":"file"}}]}}})
GST_PAGE =  es.search(index="nodes", doc_type="gsystemtype", body={
                        "query": {"bool": {"must": [{"term": {"name":"page" }}]}}})


#print GST_FILE
@get_execution_time
def ebook_listing(request, group_id, page_no=1):
	from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP
	import urllib

	try:
		group_id = ObjectId(group_id) 
	except: 
		group_name, group_id = get_group_name_id(group_id)

	selfilters = urllib.unquote(request.GET.get('selfilters', ''))
	# print "===\n", selfilters, "===\n"
	query_dict = [{}]
	if selfilters:
		selfilters = json.loads(selfilters)
		query_dict = get_filter_querydict(selfilters)
	# else:
	# 	query_dict.append({'collection_set': {'$exists': "true", '$not': {'$size': 0} }})
        
	# print "\n----\n", query_dict
	# all_ebooks = node_collection.find({
	# 		# "_type": "File",
	# 		# "attribute_set.educationaluse": "eBooks",
	# 		'$and': query_dict,
	# 		'collection_set': {'$exists': "true", '$not': {'$size': 0} }
	# 	})

	#print GST_FILE._id
	GST_FILE_temp=[]


	for a in GST_FILE['hits']['hits']:
		temp1=ObjectId(a['_source']['id'])
		GST_FILE_temp.append(temp1)

	#print temp
	GST_PAGE_temp=[]

	for a in GST_PAGE['hits']['hits']:
		temp1=ObjectId(a['_source']['id'])
		GST_PAGE_temp.append(temp1)

	ebook_gst_temp=[]
	for a in ebook_gst['hits']['hits']:
		temp1=ObjectId(a['_source']['id'])
		ebook_gst_temp.append(temp1)

	
	ebook_gst1 = [doc['_source'] for doc in ebook_gst['hits']['hits']]


	print "----------------------------------------================================================"
	#print ebook_gst1
	#all_ebooks1=es.search(index="nodes", doc_type="metatype,gsystemtype,gsystem", body={
    #                    "query": {"bool": {"filter":{ "terms":{ "member_of": temp  }} }}})

	all_ebooks1 =es.search(index="gsystem", doc_type="application", body={
                        "query":   {"bool": { "must":  [ {"term":  {"group_set": str(ObjectId(group_id))}  },{"term": {"access_policy": "public"}}],
     										 "must":  [ {"term":  {"attribute_set.educationaluse": "ebooks" } } ],
     										 "must":  [ {"terms":  {"member_of": GST_FILE_temp } } ],
     										 "must":  [ {"terms":  {"member_of": GST_PAGE_temp } } ],
     										 "must":[  {"term": {'access_policy':'public'}} ]

     										 #"must":  [ {"term":  {'created_by': request.user.id}}],

     } }} )

	#print all_ebooks1

	#all_ebooks = node_collection.find({
	#							'member_of': {'$in': temp },
	#							'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},


								# '_type': 'File',
								# 'fs_file_ids': {'$ne': []}, 
	#							'group_set': {'$in': [ObjectId(group_id)]},
	#							'attribute_set.educationaluse': 'eBooks',
	#							'$and': query_dict,
	#							'$or': [
	#									{ 'access_policy': u"PUBLIC" },
	#									{ '$and': [
	#												{'access_policy': u"PRIVATE"}, 
	#												{'created_by': request.user.id}
	#											]
	#									}
	#								],
	#							'collection_set': {'$exists': "true", '$not': {'$size': 0} }
	#							}).sort("last_update", -1)

	all_ebooks1_temp = []

	all_ebooks1_count=all_ebooks1['hits']['total']


	all_ebooks1 = [doc['_source'] for doc in all_ebooks1['hits']['hits']]

	#ebooks_page_info = paginator.Paginator(all_ebooks1, page_no, GSTUDIO_NO_OF_OBJS_PP)

	result_paginated_cur = tuple(all_ebooks1)
	
	
	ebooks_page_info = Paginator(result_paginated_cur,16)
	#print ebooks_page_info
	page = request.GET.get('page')
	
	try:
		results = ebooks_page_info.page(page)
	except PageNotAnInteger:
		results = ebooks_page_info.page(1)
	except EmptyPage:
		results = ebooks_page_info.page(ebooks_page_info.num_page)

	return render_to_response("ndf/ebook.html", {
								"all_ebooks": all_ebooks1, "ebook_gst": ebook_gst1,
								"page_info": results, "title": "eBooks",
								"group_id": group_id, "groupid": group_id,"all_ebooks1_count":all_ebooks1_count
								}, context_instance = RequestContext(request))

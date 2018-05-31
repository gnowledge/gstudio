import json

''' -- imports from installed packages -- ''' 
from django.shortcuts import render_to_response
from django.template import RequestContext
# from django.core.urlresolvers import reverse
from mongokit import paginator

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
from elasticsearch_dsl import *
from gnowsys_ndf.ndf.gstudio_es.paginator import Paginator ,EmptyPage, PageNotAnInteger
from gnowsys_ndf.settings import GSTUDIO_ELASTIC_SEARCH
from gnowsys_ndf.ndf.gstudio_es.es import *


if GSTUDIO_ELASTIC_SEARCH :
	q = Q('bool', must=[Q('match', name='e-book')])
	ebook_gst =Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
	ebook_gst = ebook_gst.execute()

	for temp in ebook_gst:
		ebook_gst = temp
		break;

	q = Q('bool', must=[Q('match', name='file')])
	GST_FILE =Search(using=es, index="nodes",doc_type="gsystemtype").query(q)

	q = Q('bool', must=[Q('match', name='page')])
	GST_PAGE =Search(using=es, index="nodes",doc_type="gsystemtype").query(q)

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
		if "?selfilters" in selfilters:
			temp_list = selfilters.split("?selfilters")
			selfilters = temp_list[0]

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

		search_text = request.GET.get("search_text",None)


		#print GST_FILE._id
		#GST_FILE_temp=[]
		GST_FILE_ID=None

		for a in GST_FILE:
			GST_FILE_ID = a.id

		GST_PAGE_ID=None

		for a in GST_PAGE:
			GST_PAGE_ID = a.id

		if selfilters:
			lists = esearch.es_filters(query_dict)

			strconcat1 = ""
			for value in lists:
				print value
				strconcat1 = strconcat1+'eval(str("'+ value +'")),'
			if search_text:

				all_ebooks1 = eval("Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match', attribute_set__educationaluse ='ebooks'),Q('exists',field='collection_set'),"+strconcat1[:-1]+"],"
						+"should=[Q('match',member_of=GST_FILE_ID),Q('match',name=search_text),Q('match',altnames=search_text),Q('match',tags=search_text),Q('match',content=search_text) ],minimum_should_match=1)")
				all_ebooks =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(all_ebooks1)
			else:
				all_ebooks1 = eval("Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match', attribute_set__educationaluse ='ebooks'),Q('exists',field='collection_set'),"+strconcat1[:-1]+"],"
						+"should=[Q('match',member_of=GST_FILE_ID),Q('match',member_of=GST_PAGE_ID) ],minimum_should_match=1)")
				all_ebooks =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(all_ebooks1)
			


		else:
			if search_text:

				all_ebooks1 = Q('bool', must=[Q('match', group_set=str(group_id)),Q('match',access_policy='public'),Q('match', attribute_set__educationaluse ='ebooks'),Q('exists',field='collection_set'),
								Q('bool',should=[Q('match',name=search_text),Q('match',altnames=search_text),Q('match',tags=search_text),Q('match',content=search_text)])]
							,should=[Q('match',member_of=GST_FILE_ID),Q('match',member_of=GST_PAGE_ID) ],minimum_should_match=1)
				all_ebooks =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(all_ebooks1)
			else:
				all_ebooks1 = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match', attribute_set__educationaluse ='ebooks'),Q('exists',field='collection_set')]
							,should=[Q('match',member_of=GST_FILE_ID),Q('match',member_of=GST_PAGE_ID) ],minimum_should_match=1)
				all_ebooks =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(all_ebooks1)

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

		result_paginated_cur = all_ebooks

		if page_no == 1:
			all_ebooks=all_ebooks[0:24]
					
		else:
			temp=( int(page_no) - 1) * 24
			all_ebooks=all_ebooks[temp:temp+24]
					
		paginator = Paginator(all_ebooks, 24)
		
		try:
			results = paginator.page(int(page_no))
		except PageNotAnInteger:
			results = paginator.page(1)
		except EmptyPage:
			results = paginator.page(paginator.num_pages)

		return render_to_response("ndf/ebook.html", {
									"all_ebooks": all_ebooks, "ebook_gst": ebook_gst,
									"page_info": results, "title": "eBooks",
									"group_id": group_id, "groupid": group_id,"all_ebooks_count":all_ebooks.count(),
									"GSTUDIO_ELASTIC_SEARCH":GSTUDIO_ELASTIC_SEARCH,
									}, context_instance = RequestContext(request))
else:
	ebook_gst = node_collection.one({'_type':'GSystemType', 'name': u"E-Book"})
	GST_FILE = node_collection.one({'_type':'GSystemType', 'name': u"File"})
	GST_PAGE = node_collection.one({'_type':'GSystemType', 'name': u'Page'})

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

		all_ebooks = node_collection.find({												
									'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
									# '_type': 'File',
									# 'fs_file_ids': {'$ne': []}, 
									'group_set': {'$in': [ObjectId(group_id)]},
									'attribute_set.educationaluse': 'eBooks',
									'$and': query_dict,
									'$or': [
											{ 'access_policy': u"PUBLIC" },
											{ '$and': [
														{'access_policy': u"PRIVATE"}, 
														{'created_by': request.user.id}
													]
											}
										],
									'collection_set': {'$exists': "true", '$not': {'$size': 0} }
									}).sort("last_update", -1)

		ebooks_page_info = paginator.Paginator(all_ebooks, page_no, GSTUDIO_NO_OF_OBJS_PP)

		return render_to_response("ndf/ebook.html", {
									"all_ebooks": all_ebooks, "ebook_gst": ebook_gst,
									"page_info": ebooks_page_info, "title": "eBooks",
									"group_id": group_id, "groupid": group_id
									}, context_instance = RequestContext(request))
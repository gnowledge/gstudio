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
#from mongokit import paginator
from gnowsys_ndf.ndf.paginator import Paginator ,EmptyPage, PageNotAnInteger
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
from elasticsearch_dsl import *
from gnowsys_ndf.local_settings import GSTUDIO_ELASTIC_SEARCH


es = Elasticsearch("http://elastic:changeme@gsearch:9200", timeout=100, retry_on_timeout=True)

#GST_PAGE = node_collection.one({'_type':'GSystemType', 'name': 'page'})
#GST_IMAGE = node_collection.one({'_type':'GSystemType', 'name': 'image'})
##GST_VIDEO = node_collection.one({'_type':'GSystemType', 'name': GAPPS[4]})
#e_library_GST = node_collection.one({'_type':'GSystemType', 'name': 'E-Library'})
#pandora_video_st = node_collection.one({'_type':'GSystemType', 'name': 'Pandora_video'})
#app = node_collection.one({'_type':'GSystemType', 'name': 'E-Library'})
#wiki_page = node_collection.one({'_type': 'GSystemType', 'name': 'Wiki page'})
#GST_JSMOL111 = node_collection.one({"_type":"GSystemType","name":"Jsmol"})

#GST_FILE =  res = es.search(index="nodes", doc_type="gsystemtype", body={
#                        "query":   {"bool":{"must":  [ {"term":  {"name":"file"}  }]  }}})
#print "----------------------"
#print GST_FILE

es_client = Search(using=es)

GST_FILE = Search(using=es, index="nodes",doc_type="gsystemtype").query("match", name="file")
GST_FILE1=GST_FILE.execute()


q = Q('bool', must=[Q('match', name='file')],should=[ Q('match', name='file1')])
GST_FILE_new1 =Search(using=es, index="nodes",doc_type="gsystemtype").query(q)

q = Q('match',name=dict(query="e-book", type="phrase"))
GST_FILE_new11 =Search(using=es, index="nodes",doc_type="gsystemtype").query(q)

print "e-book ids"
for a in GST_FILE_new11:
	print a.id

print "--------------------------------------------"
print GST_FILE_new11.to_dict()


GST_PAGE= Search(using=es, index="nodes",doc_type="gsystemtype").query("match", name="page")
GST_PAGE1=GST_PAGE.execute()   

GST_IMAGE = Search(using=es, index="nodes",doc_type="gsystemtype").query("match", name="image")
GST_IMAGE1=GST_IMAGE.execute()

GST_VIDEO = Search(using=es, index="nodes",doc_type="gsystemtype").query("match", name="video")
GST_VIDEO1=GST_VIDEO.execute()

e_library_GST = Search(using=es, index="nodes",doc_type="gsystemtype").query("match", name="library")
e_library_GST1=e_library_GST.execute()

pandora_video_st = Search(using=es, index="nodes",doc_type="gsystemtype").query("match", name="pandora")
pandora_video_st1=pandora_video_st.execute()

app = Search(using=es, index="nodes",doc_type="gsystemtype").query("match", name="library")
app1=app.execute()
wiki_page = Search(using=es, index="nodes",doc_type="gsystemtype").query("match", name="wiki")
wiki_page1=wiki_page.execute()

GST_JSMOL = Search(using=es, index="nodes",doc_type="gsystemtype").query("match", name="jsmol")
GST_JSMOL1=GST_JSMOL.execute()

print GST_JSMOL1.hits.total

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

	print GST_FILE1
	print "----------------------------------print GST_FILE1"
	try:
		group_id = ObjectId(group_id)
		#print group_id
	except:
		group_name, group_id = get_group_name_id(group_id)
		#print group_id, group_name

	if app_id is None:
		app_id = app1.hits[0].id

	title = e_library_GST1.hits[0].name
	
	GST_FILE_temp=[]
	

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

	#query_dict.append({'attribute_set.educationaluse': {'$ne': 'eBooks'}})
	i=-1
	strconcat=""
	endstring=""
	temp_dict={}
	#print query_dict

	for each in list(query_dict):
		for temp in each.values():
			for a in temp:
				for key,value in a.items():
					if isinstance(value, dict): 
						#print value["$in"][0]
						if value["$in"]:
							key = list(key)
							key[13]='__'
							t="".join(key)
							print t
							print "-----------------------------"
							temp_dict[t]=value["$in"][0]
							#strconcat=strconcat+"Q('match',"+ t+"='"+value["$in"][0]+"'),"
							#Q('match',name=dict(query="e-book", type="phrase"))
							strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value["$in"][0]+"',type='phrase'))$$"

						elif value["$or"]:
							key = list(key)
							key[13]='__'
							t="".join(key)
							print t
							print "------------------------"
							temp_dict[t]=value["$or"][0]
							#strconcat=strconcat+"Q('match',"+t+"='"+value["$or"][0]+"') "
							strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value["$or"][0]+"',type='phrase'))$$"
					elif isinstance(value, tuple):
						temp_dict["language"]= value[1]	
						#strconcat=strconcat+"Q('match',"+key+"='"+value[1]+"') "
						strconcat=strconcat+"Q('match',"+key+"=dict(query='"+value[1]+"',type='phrase'))$$"
					else:
						if key != "source":
							key = list(key)
							key[13]='__'
							t="".join(key)
							temp_dict[t]=value
							#strconcat=strconcat+"Q('match',"+ t+"='"+value+"') "
							strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value+"',type='phrase'))$$"	
						else:
							temp_dict[key]=value
							#strconcat=strconcat+"Q('match',"+ key+"='"+value+"') "
							strconcat=strconcat+"Q('match',"+key+"=dict(query='"+value+"',type='phrase'))$$"	

	print temp_dict
	#strconcat=strconcat
	print strconcat

	#files = node_collection.find({
									# 'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
									#'member_of': {'$in': [GST_FILE._id,GST_JSMOL._id]},
	#								'member_of': {'$in': [GST_FILE1.hits[0].id,GST_JSMOL1.hits[0].id]},

									# '_type': 'File',
									# 'fs_file_ids': {'$ne': []},
	#								'group_set': {'$all': [ObjectId(group_id)]},
	#								'$and': query_dict,
	#								'$or': [
	#										{ 'access_policy': u"PUBLIC" },
	#										{ '$and': [
	#													{'access_policy': u"PRIVATE"},
	#													{'created_by': request.user.id}
	#												]
	#										}
	#									]
	#								}).sort("last_update", -1)


	#files1 =   es.search(index="nodes", doc_type="gsystem", body={
    #                    "query":   {"bool": { "must":  [ {"term":  {"group_set": str(ObjectId(group_id))}  },{"term": {"access_policy": "public"}}
    #                    					,{"term":  {"member_of": GST_FILE1.hits[0].id } } ],
    # 										 "must_not":  [ {"term":  {"attribute_set.educationaluse": "ebooks" } } ],
     										 #"must":  [ {"term":  {"member_of": GST_FILE1.hits[0].id } } ],
     										 #"must":  [ {"terms":  {"member_of": GST_JSMOL1.hits[0].id } } ],
    # 										 "must":[  {"term": {'access_policy':'public'}} ]

     										 #"must":  [ {"term":  {'created_by': request.user.id}}],

    #} }} )
	a,b,c,d,e = ([] for i in range(5))

	if selfilters:
		if strconcat.count('match') == 1:
			a=strconcat.split("$$") #give list output
			a="".join(a) # we convert list to string 
			print a
			q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) , eval(str(a))],
			must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

			collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')
								,eval(str(a))],
			should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
			must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

			q_images_count = Q('bool', must=[Q('match', attribute_set__educationaluse='images'),eval(str(a))])
			q_audios_count = Q('bool', must=[Q('match', attribute_set__educationaluse='audios'),eval(str(a))])
			q_videos_count = Q('bool', must=[Q('match', attribute_set__educationaluse='videos'),eval(str(a))])
			q_intercatives_count = Q('bool', must=[Q('match', attribute_set__educationaluse='interactives'),eval(str(a))])
			q_applications_count = Q('bool', must=[Q('match', attribute_set__educationaluse='documents'),eval(str(a))])
			q_ebooks_count = Q('bool', must=[Q('match', attribute_set__educationaluse='ebooks'),eval(str(a))])
			q_all_count=  Q('bool', must=[Q('terms',attribute_set__educationaluse=['documents','images','audios','videos','interactives']),eval(str(a))])
			
		elif strconcat.count('match') == 2:

			a,b = strconcat.split("$$",1)
			a="".join(a)
			b="".join(b[:-2])

			q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) , eval(str(a)), eval(str(b))],
			must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

			collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')
								,eval(str(a)), eval(str(b))],
			should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
			must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

			q_images_count = Q('bool', must=[Q('match', attribute_set__educationaluse='images'),eval(str(a)),eval(str(b))])
			q_audios_count = Q('bool', must=[Q('match', attribute_set__educationaluse='audios'),eval(str(a)),eval(str(b))])
			q_videos_count = Q('bool', must=[Q('match', attribute_set__educationaluse='videos'),eval(str(a)),eval(str(b))])
			q_intercatives_count = Q('bool', must=[Q('match', attribute_set__educationaluse='interactives'),eval(str(a)),eval(str(b))])
			q_applications_count = Q('bool', must=[Q('match', attribute_set__educationaluse='documents'),eval(str(a)),eval(str(b))])
			q_ebooks_count = Q('bool', must=[Q('match', attribute_set__educationaluse='ebooks'),eval(str(a)),eval(str(b))])
			q_all_count=  Q('bool', must=[Q('terms',attribute_set__educationaluse=['documents','images','audios','videos','interactives']),eval(str(a)),eval(str(b))])


		elif strconcat.count('match') == 3:
			a,b,c=strconcat.split("$$",2)
			a="".join(a)
			b="".join(b)
			c="".join(c[:-2])

			
			q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) , eval(str(a)),eval(str(b)),eval(str(c))],
			must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
			collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')
								,eval(str(a)), eval(str(b)), eval(str(c))],
			should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
			must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

			q_images_count = Q('bool', must=[Q('match', attribute_set__educationaluse='images'),eval(str(a)),eval(str(b)),eval(str(c))])
			q_audios_count = Q('bool', must=[Q('match', attribute_set__educationaluse='audios'),eval(str(a)),eval(str(b)),eval(str(c))])
			q_videos_count = Q('bool', must=[Q('match', attribute_set__educationaluse='videos'),eval(str(a)),eval(str(b)),eval(str(c))])
			q_intercatives_count = Q('bool', must=[Q('match', attribute_set__educationaluse='interactives'),eval(str(a)),eval(str(b)),eval(str(c))])
			q_applications_count = Q('bool', must=[Q('match', attribute_set__educationaluse='documents'),eval(str(a)),eval(str(b)),eval(str(c))])
			q_ebooks_count = Q('bool', must=[Q('match', attribute_set__educationaluse='ebooks'),eval(str(a)),eval(str(b)),eval(str(c))])
			q_all_count=  Q('bool', must=[Q('terms',attribute_set__educationaluse=['documents','images','audios','videos','interactives']),eval(str(a)),eval(str(b)),eval(str(c))])


		elif strconcat.count('match') == 4:
			a,b,c,d=strconcat.split("$$",3)
			a="".join(a)
			b="".join(b)
			c="".join(c)
			d="".join(d[:-2])
			q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) , eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d))],
			must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
			collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')
								,eval(str(a)), eval(str(b)), eval(str(c)), eval(str(d))],
			should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
			must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

			q_images_count = Q('bool', must=[Q('match', attribute_set__educationaluse='images'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d))])
			q_audios_count = Q('bool', must=[Q('match', attribute_set__educationaluse='audios'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d))])
			q_videos_count = Q('bool', must=[Q('match', attribute_set__educationaluse='videos'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d))])
			q_intercatives_count = Q('bool', must=[Q('match', attribute_set__educationaluse='interactives'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d))])
			q_applications_count = Q('bool', must=[Q('match', attribute_set__educationaluse='documents'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d))])
			q_ebooks_count = Q('bool', must=[Q('match', attribute_set__educationaluse='ebooks'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d))])
			q_all_count=  Q('bool', must=[Q('terms',attribute_set__educationaluse=['documents','images','audios','videos','interactives']),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d))])



		elif strconcat.count('match') == 5:
			a,b,c,d,e=strconcat.split("$$",4)
			a="".join(a)
			b="".join(b)
			c="".join(c)
			d="".join(d)
			e="".join(e[:-2])

			q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) , eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d)),eval(str(e))],
			must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
			collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')
								,eval(str(a)), eval(str(b)), eval(str(c)), eval(str(d)), eval(str(e))],
			should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
			must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

			q_images_count = Q('bool', must=[Q('match', attribute_set__educationaluse='images'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d)),eval(str(e))])
			q_audios_count = Q('bool', must=[Q('match', attribute_set__educationaluse='audios'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d)),eval(str(e))])
			q_videos_count = Q('bool', must=[Q('match', attribute_set__educationaluse='videos'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d)),eval(str(e))])
			q_intercatives_count = Q('bool', must=[Q('match', attribute_set__educationaluse='interactives'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d)),eval(str(e))])
			q_applications_count = Q('bool', must=[Q('match', attribute_set__educationaluse='documents'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d)),eval(str(e))])
			q_ebooks_count = Q('bool', must=[Q('match', attribute_set__educationaluse='ebooks'),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d)),eval(str(e))])
			q_all_count=  Q('bool', must=[Q('terms',attribute_set__educationaluse=['documents','images','audios','videos','interactives']),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d)),eval(str(e))])



	else:
		
		q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match',member_of=GST_FILE1.hits[0].id)],
		must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

	files_new = Search(using=es, index="nodes",doc_type="gsystem").query(q)
	files_new = files_new[0:24]

	print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	print files_new.count()
	print files_new.to_dict()


	#files1_temp = [doc['_source'] for doc in files1['hits']['hits']]

	#for a in files_new.scan():
	#	print a.id

	#print "----------------------------------------------------------"
	#print all_files_count
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

	#images_count =   es.search(index="gsystem", doc_type="image", body={
    ##                    "query":   {"bool":{"must":  [ {"term":  {"status":"published"}  }]  }}})
	#audios_count =   es.search(index="gsystem", doc_type="audio", body={
    #                    "query":   {"bool":{"must":  [ {"term":  {"status":"published"}  }]  }}})
	#videos_count =   es.search(index="gsystem", doc_type="video", body={
    #                    "query":   {"bool":{"must":  [ {"term":  {"status":"published"}  }]  }}})
	#applications_count =  es.search(index="gsystem", doc_type="application", body={
    #                    "query":   {"bool":{"must":  [ {"term":  {"status":"published"}  }]  }}})
	#all_count =   es.search(index="gsystem", doc_type="images,audios,videos,application", body={
    #                    "query":   {"bool":{"must":  [ {"term":  {"status":"published"}  }]  }}})
	temp111 = ""
	if selfilters in (None,'',""):
		q_images_count = Q('bool', must=[Q('match', attribute_set__educationaluse='images')])
		q_audios_count = Q('bool', must=[Q('match', attribute_set__educationaluse='audios')])
		q_videos_count = Q('bool', must=[Q('match', attribute_set__educationaluse='videos')])
		q_intercatives_count = Q('bool', must=[Q('match', attribute_set__educationaluse='interactives')])
		q_applications_count = Q('bool', must=[Q('match', attribute_set__educationaluse='documents')])
		q_ebooks_count = Q('bool', must=[Q('match', attribute_set__educationaluse='ebooks')])
		q_all_count=  Q('bool', must=[Q('terms',attribute_set__educationaluse=['documents','images','audios','videos','interactives'])])

	images_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_images_count)
	audios_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_audios_count)
	videos_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_videos_count)
	intercatives_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_intercatives_count)
	applications_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_applications_count)
	ebooks_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_ebooks_count)
	all_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_all_count)
	#q = Q('bool', should=[Q('match', attribute_set__educationaluse='images'),Q('match', attribute_set__educationaluse='videos'),
	#	Q('match', attribute_set__educationaluse='audios'),Q('match', attribute_set__educationaluse='documents'),
	#	Q('match', attribute_set__educationaluse='interactives')])
	
	

	#print all_count.to_dict()
	educationaluse_stats = {}

	#print all_count.count()

	if files_new:
		eu_list = []  # count
		#for each in files1_temp:
		#	eu_list += [i.get("educationaluse") for i in each.attribute_set if i.has_key("educationaluse")]

		#files1_temp.rewind()

		if set(eu_list):
			if len(set(eu_list)) > 1:
				educationaluse_stats = dict((x, eu_list.count(x)) for x in set(eu_list))
				print educationaluse_stats
			elif len(set(eu_list)) == 1:
				educationaluse_stats = { eu_list[0]: eu_list.count(eu_list[0])}
			educationaluse_stats["all"] = files.count()
		

		# print educationaluse_stats
		#result_paginated_cur = files1_temp
		#result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)
		#result_paginated_cur = tuple(files1_temp)
		

   
	

	#collection_pages_cur = node_collection.find({
	#								'member_of': {'$in': [GST_FILE_temp, GST_PAGE1.hits[0].id ]},
     #                               'group_set': {'$all': [ObjectId(group_id)]},
      #                              '$and': query_dict,
       #                             '$or': [
    #                                    {'access_policy': u"PUBLIC"},
    #                                    {'$and': [
    #                                        {'access_policy': u"PRIVATE"},
    #                                        {'created_by': request.user.id}
     #                                   ]
    #                                 }
    #                                ],
    #                               'collection_set': {'$exists': "true", '$not': {'$size': 0} }
    #                            }).sort("last_update", -1)


	#print GST_FILE_temp

	#print GST_PAGE_collection

	#collection_pages_cur1 =  es.search(index="nodes", doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author", 
	#					body={ "query":   {"bool": { "must":  [ {"term":  {"group_set": str(ObjectId(group_id))}  },{"term": {"status": "published"}}],
    # 										 "must_not":  [ {"term":  {"attribute_set.educationaluse": "ebooks" } } ],
    # 										 #"must":  [ {"term":  {'created_by': request.user.id}}],
    # 										 "must":  [ {"term":  {'member_of': GST_FILE1.hits[0].id }}],
    # 										 "must":  [ {"terms":  {'member_of': GST_PAGE1.hits[0].id}}],
    # 										 "must": {"exists": {"field":"collection_set"}},
    # } }} )
	if selfilters:
		collection_pages_cur =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(collection_query)
	else:
		q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')],
		should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
		must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
		collection_pages_cur =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)



	print collection_pages_cur.count()
	print "cccccccccccccccccccccccccccccccccccccccccccccccccccc"
	#print collection_pages_cur.to_dict()

	if int(page_no)==1:
		collection_pages_cur=collection_pages_cur[0:24]
	else:
		temp=( int(page_no) - 1) * 24
		collection_pages_cur=collection_pages_cur[temp:temp+24]

	paginator = Paginator(collection_pages_cur, 24)


	#page_no = request.GET.get('page_no')
	try:
		results = paginator.page(page_no)
	except PageNotAnInteger:
		results = paginator.page(1)
	except EmptyPage:
		results = paginator.page(paginator.num_pages)

	#	print collection_pages_cur1

	#coll_page_count = collection_pages_cur.count() if collection_pages_cur else 0
	coll_page_count = collection_pages_cur.count() if collection_pages_cur else 0


	#collection_pages_cur1_temp = [doc['_source'] for doc in collection_pages_cur1['hits']['hits']]

	#results = paginator.Paginator(collection_pages_cur, page_no, no_of_objs_pp)
	datavisual.append({"name":"Doc", "count": educationaluse_stats.get("Documents", 0)})
	datavisual.append({"name":"Page", "count": educationaluse_stats.get("Pages", 0)})
	datavisual.append({"name":"Image","count": educationaluse_stats.get("Images", 0)})
	datavisual.append({"name":"Video","count": educationaluse_stats.get("Videos", 0)})
	datavisual.append({"name":"Interactives","count": educationaluse_stats.get("Interactives", 0)})
	datavisual.append({"name":"Audios","count": educationaluse_stats.get("Audios", 0)})
	datavisual.append({"name":"eBooks","count": educationaluse_stats.get("eBooks", 0)})
	#if collection_pages_cur:	
	#	datavisual.append({"name":"Collections","count": coll_page_count})
	datavisual = json.dumps(datavisual)

	#title=''.join(title)
	#test_node = node_collection.one({"name":"home", '_type':"Group"})
	#app_gst=''.join(app_gst_name)
	print group_id
	

	return render_to_response(
        'ndf/test_template.html',
        {'title': title, 'app':e_library_GST1.hits[0].name,
								 'appId':app_id, "app_gst": app1.hits[0].name,
								 # 'already_uploaded': already_uploaded,'shelf_list': shelf_list,'shelves': shelves,
								 'files': files_new,
								 "detail_urlname": "file_detail",
								 'ebook_pages': ebooks_count.count(),
								 #'ebook_pages': educationaluse_stats.get("eBooks", 0),
								 # 'page_count': pageCollection.count(),
								 # 'page_nodes':pageCollection
								 'all_files_count':all_count.count(),
								 'file_pages': files_new,
								 'image_pages': images_count.count(),
								 'interactive_pages': intercatives_count.count(),
								 'educationaluse_stats': json.dumps(educationaluse_stats),
								 #'doc_pages': educationaluse_stats.get("Documents", 0),
								 #'video_pages': educationaluse_stats.get("Videos", 0),
								 #'audio_pages': educationaluse_stats.get("Audios", 0),
								 'doc_pages': applications_count.count(),
								 'video_pages': videos_count.count(),
								 'audio_pages': audios_count.count(),
								 'collection_pages': results,
								 'collection': collection_pages_cur,

								 'collection_count': collection_pages_cur.count(),
								 'groupid': group_id, 'group_id':group_id,
								 "datavisual":datavisual,
								 "GSTUDIO_ELASTIC_SEARCH":GSTUDIO_ELASTIC_SEARCH,
								 },

        context_instance=RequestContext(request)
    )


def elib_paged_file_objects(request, group_id, filetype, page_no):
	'''
	Method to implement pagination in File and E-Library app.
	'''

	if request.method == "POST":

		group_name, group_id = get_group_name_id(group_id)

		no_of_objs_pp = 24
		result_pages = None
		results = None

		filters = request.POST.get("filters", "")
		filters = json.loads(filters)
		filters = get_filter_querydict(filters)

		print filters
		print "0000000000000000000000000000000000000000000"
		query_dict = filters

		selfilters = urllib.unquote(request.GET.get('selfilters', ''))
		if selfilters:
			selfilters = json.loads(selfilters)
			query_dict = get_filter_querydict(selfilters)

		#query_dict.append({'attribute_set.educationaluse': {'$ne': u'eBooks'}})
		i=-1

		strconcat=""
		endstring=""
		temp_dict={}
		#print query_dict

		for each in list(query_dict):
			for temp in each.values():
				for a in temp:
					for key,value in a.items():
						if isinstance(value, dict): 
							#print value["$in"][0]
							if value["$in"]:
								key = list(key)
								key[13]='__'
								t="".join(key)
								print t
								print "-----------------------------"
								temp_dict[t]=value["$in"][0]
								#strconcat=strconcat+"Q('match',"+ t+"='"+value["$in"][0]+"'),"
								#strconcat=strconcat+"Q('match',"+ t+"='"+value["$in"][0]+"') "
								strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value["$in"][0]+"',type='phrase'))$$"
							elif value["$or"]:
								key = list(key)
								key[13]='__'
								t="".join(key)
								print t
								print "------------------------"
								temp_dict[t]=value["$or"][0]
								#strconcat=strconcat+"Q('match',"+ t+"='"+value["$or"][0]+"') "
								strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value["$or"][0]+"',type='phrase'))$$"
						elif isinstance(value, tuple):
							temp_dict["language"]= value[1]	
							#strconcat=strconcat+"Q('match',"+ key+"='"+value[1]+"') "
							strconcat=strconcat+"Q('match',"+key+"=dict(query='"+value[1]+"',type='phrase'))$$"
						else:
							if key != "source":
								key = list(key)
								key[13]='__'
								t="".join(key)
								temp_dict[t]=value
								#strconcat=strconcat+"Q('match',"+ t+"='"+value+"') "
								strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value+"',type='phrase'))$$"	
							else:
								temp_dict[key]=value
								#strconcat=strconcat+"Q('match',"+ key+"='"+value+"') "
								strconcat=strconcat+"Q('match',"+key+"=dict(query='"+value+"',type='phrase'))$$"	

		print temp_dict
		#strconcat=strconcat
		print strconcat
		print 



		detail_urlname = "file_detail"
		#if filetype != "all":
			

			# elif filetype == "Collections":
		#	if filetype == "Collections":
		#		pass
	
		#	else:
				#query_dict.append({"attribute_set.educationaluse": filetype})
		#		pass

		

		#GST_FILE_temp=[]
		#for a in GST_FILE['hits']['hits']:
		#temp1=ObjectId(a['_source']['id'])
		#	temp1=a['_source']['id']
		#	GST_FILE_temp.append(temp1)
		#files = node_collection.find({
		#								'member_of': {'$in': [GST_FILE._id,GST_JSMOL._id]},
										# 'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
										# '_type': 'File',
										# 'fs_file_ids': {'$ne': []},
		#								'group_set': {'$all': [ObjectId(group_id)]},
		#								'$and': query_dict,
		#								'$or': [
		#										{ 'access_policy': u"PUBLIC" },
		#										{ '$and': [
		#													{'access_policy': u"PRIVATE"},
		#													{'created_by': request.user.id}
		#												]
		#										}
		#									]
		#								}).sort("last_update", -1)
		print filetype


		collection_query = None
		q= None

			

		if filetype != "all":

			filetype = str(filetype)

			if filters:

				if strconcat.count('match') == 1:

					a=strconcat.split("$$")
					a="".join(a)
					print a
					q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) , Q('match', attribute_set__educationaluse =filetype), eval(str(a))],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

					collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set'), Q('match', attribute_set__educationaluse =filetype)
										,eval(str(a))],
					should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

			
				elif strconcat.count('match') == 2:

					a,b = strconcat.split("$$",1)
					a="".join(a)
					b="".join(b[:-2])

					q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) ,  Q('match', attribute_set__educationaluse =filetype),eval(str(a)), eval(str(b))],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

					collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set'), Q('match', attribute_set__educationaluse =filetype)
										,eval(str(a)), eval(str(b))],
					should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
				elif strconcat.count('match') == 3:
					a,b,c=strconcat.split("$$",2)
					a="".join(a)
					b="".join(b)
					c="".join(c[:-2])

					
					q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) ,Q('match', attribute_set__educationaluse =filetype), eval(str(a)),eval(str(b)),eval(str(c))],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
					collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set'), Q('match', attribute_set__educationaluse =filetype)
										,eval(str(a)), eval(str(b)), eval(str(c))],
					should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
				elif strconcat.count('match') == 4:
					a,b,c,d=strconcat.split("$$",3)
					a="".join(a)
					b="".join(b)
					c="".join(c)
					d="".join(d[:-2])
					q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) , Q('match', attribute_set__educationaluse =filetype), eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d))],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
					collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set'), Q('match', attribute_set__educationaluse =filetype)
										,eval(str(a)), eval(str(b)), eval(str(c)), eval(str(d))],
					should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
				elif strconcat.count('match') == 5:
					a,b,c,d,e=strconcat.split("$$",4)
					a="".join(a)
					b="".join(b)
					c="".join(c)
					d="".join(d)
					e="".join(e[:-2])

					q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) , Q('match', attribute_set__educationaluse =filetype),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d)),eval(str(e))],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
					collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set'), Q('match', attribute_set__educationaluse =filetype)
										,eval(str(a)), eval(str(b)), eval(str(c)), eval(str(d)), eval(str(e))],
					should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])	
			else:
				print "----------11111111111111111111111111-----------------------------"
				
				q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match', attribute_set__educationaluse =filetype)],
				should=[Q('match',member_of=GST_FILE1.hits[0].id)])
			
				collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')],
				should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
				must_not=[Q('match', attribute_set__educationaluse ='ebooks')])	

				

			files1 =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)
			print files1.count()
			if int(page_no)==1:
				files1=files1[0:24]
			else:
				temp=( int(page_no) - 1) * 24
				files1=files1[temp:temp+24]
			#files1  = es.search(index="gsystem,nodes", doc_type="image,video,audio,application,gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author", body={
            #            "query":   {"bool": { "must":[ {"terms":  {"group_set": str(ObjectId(group_id))}  } ],
     		#								 #"must":  [ {"match":  {"attribute_set.educationaluse": "imag" } } ],
     		#								 "must":[ { "terms":  {'member_of': GST_FILE1.hits[0].id } } ],
     										 #"must":[ {"terms":  {'member_of': GST_JSMOL.hits[0].id } } ],
     		#								 "must":[ {"term": {'access_policy':'public'}} ] ,
     										 #"must":[ {"terms": {'attribute_set.educationaluse': filetype }} ] ,
     		#								 "must": [ {'term': {'attribute_set.educationaluse': filetype}} ],
     		#								 } }  },  size=20 )
		
		else:
			print "else execute"
			if filters:
				if strconcat.count('match') == 1:
					a=strconcat.split("$$")
					a="".join(a)
					print a
					print "```````````````````````````````````````"
					q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) ,Q('terms',attribute_set__educationaluse=['documents','images','audios','videos']), eval(str(a))],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

					collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')
										,eval(str(a))],
					should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

			
				elif strconcat.count('match') == 2:

					a,b = strconcat.split("$$",1)
					a="".join(a)
					b="".join(b[:-2])

					q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) ,Q('terms',attribute_set__educationaluse=['documents','images','audios','videos']), eval(str(a)), eval(str(b))],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

					collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')
										,eval(str(a)), eval(str(b))],
					should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
				elif strconcat.count('match') == 3:
					a,b,c=strconcat.split("$$",2)
					a="".join(a)
					b="".join(b)
					c="".join(c[:-2])

					
					q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) ,Q('terms',attribute_set__educationaluse=['documents','images','audios','videos']), eval(str(a)),eval(str(b)),eval(str(c))],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
					collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')
										,eval(str(a)), eval(str(b)), eval(str(c))],
					should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
				elif strconcat.count('match') == 4:
					a,b,c,d=strconcat.split("$$",3)
					a="".join(a)
					b="".join(b)
					c="".join(c)
					d="".join(d[:-2])
					q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) ,Q('terms',attribute_set__educationaluse=['documents','images','audios','videos']), eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d))],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
					collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')
										,eval(str(a)), eval(str(b)), eval(str(c)), eval(str(d))],
					should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
				elif strconcat.count('match') == 5:
					a,b,c,d,e=strconcat.split("$$",4)
					a="".join(a)
					b="".join(b)
					c="".join(c)
					d="".join(d)
					e="".join(e[:-2])

					q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id) ,Q('terms',attribute_set__educationaluse=['documents','images','audios','videos']),eval(str(a)),eval(str(b)),eval(str(c)),eval(str(d)),eval(str(e))],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
					collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')
										,eval(str(a)), eval(str(b)), eval(str(c)), eval(str(d)), eval(str(e))],
					should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
			else:

				q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match',member_of=GST_FILE1.hits[0].id),Q('terms',attribute_set__educationaluse=['documents','images','audios','videos'])],
				)
				

				collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')],
					should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
					must_not=[Q('match', attribute_set__educationaluse ='ebooks')])



			print query_dict
			

			files1 =Search(using=es, index="gsystem",doc_type="image,video,audio,application").query(q)
			if int(page_no)==1:
				files1=files1[0:24]
			else:
				temp=( int(page_no) - 1) * 24
				files1=files1[temp:temp+24]
			#filetype = [ "images","videos","documents","audios"]
			print files1.count()
			

			#files1  = es.search(index="gsystem", doc_type="image,video,audio,application", body={
            #            "query":   {"bool": { "must":[ {"terms":  {"group_set": str(ObjectId(group_id))}  } ],
     										 #"must":  [ {"match":  {"attribute_set.educationaluse": "imag" } } ],
     		#								 "must":[ { "terms":  {'member_of': GST_FILE1.hits[0].id } } ],
     										 #"must":[ {"terms":  {'member_of': GST_JSMOL.hits[0].id } } ],
     		#								 "must":[ {"term": {'access_policy':'public'}} ] ,
     										 #"must":[ {"terms": {'attribute_set.educationaluse': filetype }} ] ,
     		#								 "must": [ {'terms': {'attribute_set.educationaluse': filetype}} ],
     		#								 } }  }
     		#								 , size=20 )
		

		#all_files_count=files1['hits']['total']


		#files1_temp = [doc['_source'] for doc in files1['hits']['hits']]

		#print files1_temp

		educationaluse_stats = {}

		if files1:# and not result_pages:
			# print "=======", educationaluse_stats
			
			eu_list = []  # count
			collection_set_count = 0
			#for each in files:
			#	eu_list += [i.get("educationaluse") for i in each.attribute_set if i.has_key("educationaluse")]
			#	collection_set_count += 1 if each.collection_set else 0

			#files.rewind()

			#if set(eu_list):
			#	if len(set(eu_list)) > 1:
			#		educationaluse_stats = dict((x, eu_list.count(x)) for x in set(eu_list))
			#	elif len(set(eu_list)) == 1:
			#		educationaluse_stats = { eu_list[0]: eu_list.count(eu_list[0])}
			#	educationaluse_stats["all"] = files.count()
			#	educationaluse_stats["Collections"] = collection_set_count

			result_paginated_cur = files1
			#result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)
			#result_paginated_cur = tuple(files1_temp)
			
			paginator = Paginator(result_paginated_cur, 24)
			#page_no = request.GET.get('page_no')
			try:
				results = paginator.page(page_no)
			except PageNotAnInteger:
				results = paginator.page(1)
			except EmptyPage:
				results = paginator.page(paginator.num_pages)

		filter_result = "True" if (files1.count() > 0) else "False"


		if filetype == "Collections":

			detail_urlname = "page_details"
				#result_cur = node_collection.find({
				#					'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
                #                    'group_set': {'$all': [ObjectId(group_id)]},
				#					'$and': query_dict,
                ##                   '$or': [
                 #                       {'access_policy': u"PUBLIC"},
                #                        {'$and': [
                #                            {'access_policy': u"PRIVATE"},
                #                            {'created_by': request.user.id}
                #                        ]
                #                     }
                #                    ],
                #                    'collection_set': {'$exists': "true", '$not': {'$size': 0} }
                #                }).sort("last_update", -1)
				#q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')],
				#should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
				#must_not=[Q('match', attribute_set__educationaluse ='ebooks')])

			result_cur =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(collection_query)

			print filters
			#print "=============================================================", result_cur.count()
			#print page_no
			if int(page_no) == 1:
				result_cur=result_cur[0:24]
				
			else:
				temp=int(( int(page_no) - 1) * 24)
				result_cur=result_cur[temp:temp+24]
				

			result_paginated_cur = result_cur
				#result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

			print result_cur
			paginator = Paginator(result_paginated_cur, 24)
				#page = request.GET.get('page')
			
			try:
				results = paginator.page(int(page_no))
			except PageNotAnInteger:
				results = paginator.page(1)
			except EmptyPage:
				results = paginator.page(paginator.num_pages)
		

	return render_to_response ("ndf/file_list_tab.html", {
			"filter_result": filter_result,
			"group_id": group_id, "group_name_tag": group_id, "groupid": group_id,
			'title': "E-Library", "educationaluse_stats": json.dumps(educationaluse_stats),
			"resource_type": result_paginated_cur, "detail_urlname": detail_urlname,
			"filetype": filetype, "res_type_name": "", "page_info": results,
			"GSTUDIO_ELASTIC_SEARCH":GSTUDIO_ELASTIC_SEARCH,
			},
			context_instance = RequestContext(request))

def git_branch(request):
	return HttpResponse(subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']),
		content_type="text/plain")
	
def git_misc(request, git_command):
	response = "Unsupported"
	if git_command in ['log', 'branch', 'status', 'tag', 'show', 'diff']:
		response = subprocess.check_output(['git', git_command])
	return HttpResponse(response, content_type="text/plain")


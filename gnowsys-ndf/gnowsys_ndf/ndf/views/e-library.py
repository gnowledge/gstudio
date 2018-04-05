import re
import urllib

''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response
from django.template import RequestContext
from mongokit import paginator


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
from gnowsys_ndf.ndf.models.es import *
from gnowsys_ndf.ndf.paginator import Paginator ,EmptyPage, PageNotAnInteger


if GSTUDIO_ELASTIC_SEARCH:
	search_text = None
	##############################################################################
	q = Q('match',name=dict(query='File',type='phrase'))
	GST_FILE = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
	GST_FILE1 = GST_FILE.execute()

	q = Q('match',name=dict(query='Page',type='phrase'))
	GST_PAGE = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
	GST_PAGE1 = GST_PAGE.execute()

	q = Q('match',name=dict(query='Image',type='phrase'))
	GST_IMAGE = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
	GST_IMAGE1 = GST_IMAGE.execute()

	q = Q('match',name=dict(query='Video',type='phrase'))
	GST_VIDEO = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
	GST_VIDEO1 = GST_VIDEO.execute()

	q = Q('match',name=dict(query='E-Library',type='phrase'))
	e_library_GST = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
	e_library_GST1 = e_library_GST.execute()
		
	q = Q('match',name=dict(query='Pandora_video',type='phrase'))
	pandora_video_st = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
	pandora_video_st1 = pandora_video_st.execute()

	q = Q('match',name=dict(query='E-Library',type='phrase'))
	app = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
	app1 = app.execute()
		
	q = Q('match',name=dict(query='Wiki page',type='phrase'))
	wiki_page = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
	wiki_page1 = wiki_page.execute()

	q = Q('match',name=dict(query='Jsmol',type='phrase'))
	GST_JSMOL = Search(using=es, index="nodes",doc_type="gsystemtype").query(q)
	GST_JSMOL1 = GST_JSMOL.execute()
	##############################################################################
	@get_execution_time
	def resource_list(request, group_id="home", app_id=None, page_no=1):

		print request.get_full_path()


		is_video = request.GET.get('is_video', "")

		search_text = request.GET.get('search_text', "")
		
		#if search_text != None:
		with open("Output.txt", "w") as text_file:
			text_file.write(search_text)
			text_file.close()
		print search_text
		print "-------------------------------"

		print GST_FILE1
		try:
			group_id = ObjectId(group_id)
		except:
			group_name, group_id = get_group_name_id(group_id)

		if app_id is None:
			app_id = app1.hits[0].id
			print app_id


		title = e_library_GST1.hits[0].name
		
		GST_FILE_temp=[]
		

		file_id = GST_FILE_temp
		datavisual = []
		no_of_objs_pp = 24

		query_dict = []
		selfilters = urllib.unquote(request.GET.get('selfilters', ''))
		if selfilters:
			selfilters = json.loads(selfilters)
			query_dict = get_filter_querydict(selfilters)

		#query_dict.append({'attribute_set.educationaluse': {'$ne': 'eBooks'}})
		i=-1
		strconcat=""
		endstring=""
		temp_dict={}
		lists = []
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
								#strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value["$in"][0]+"',type='phrase'))$$"
								lists.append("Q('match',"+t+"=dict(query='"+value["$in"][0]+"',type='phrase'))")
							elif value["$or"]:
								key = list(key)
								key[13]='__'
								t="".join(key)
								print t
								print "------------------------"
								temp_dict[t]=value["$or"][0]
								#strconcat=strconcat+"Q('match',"+t+"='"+value["$or"][0]+"') "
								#strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value["$or"][0]+"',type='phrase'))$$"
								lists.append("Q('match',"+t+"=dict(query='"+value["$or"][0]+"',type='phrase'))")
						elif isinstance(value, tuple):
							temp_dict["language"]= value[1]	
							#strconcat=strconcat+"Q('match',"+key+"='"+value[1]+"') "
							strconcat=strconcat+"Q('match',"+key+"=dict(query='"+value[1]+"',type='phrase'))$$"
							lists.append("Q('match',"+key+"=dict(query='"+value[1]+"',type='phrase'))")
						else:
							if key != "source":
								key = list(key)
								key[13]='__'
								t="".join(key)
								temp_dict[t]=value
								#strconcat=strconcat+"Q('match',"+ t+"='"+value+"') "
								#strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value+"',type='phrase'))$$"
								lists.append("Q('match',"+t+"=dict(query='"+value+"',type='phrase'))")	
							else:
								temp_dict[key]=value
								#strconcat=strconcat+"Q('match',"+ key+"='"+value+"') "
								#strconcat=strconcat+"Q('match',"+key+"=dict(query='"+value+"',type='phrase'))$$"	
								lists.append("Q('match',"+key+"=dict(query='"+value+"',type='phrase'))")

		print temp_dict
		#strconcat=strconcat
		print strconcat
		print lists
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
			strconcat1 = ""
			for value in lists:
				strconcat1 = strconcat1+'eval(str("'+ value +'")),'

			if search_text in (None,'',""):

				q = eval("Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id),"+strconcat1[:-1]+"],must_not=[Q('match', attribute_set__educationaluse ='ebooks')])")

				collection_query = eval("Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set'),"+strconcat1[:-1]+"],"
									+ "should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],"
									+ "must_not=[Q('match', attribute_set__educationaluse ='ebooks')],minimum_should_match=1)")

				q_images_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='images'),"+strconcat1[:-1]+"])")
				q_audios_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='audios'),"+strconcat1[:-1]+"])")
				q_videos_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='videos'),"+strconcat1[:-1]+"])")
				q_intercatives_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='interactives'),"+strconcat1[:-1]+"])")
				q_applications_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='documents'),"+strconcat1[:-1]+"])")
				q_ebooks_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='ebooks'),"+strconcat1[:-1]+"])")
				q_all_count = eval("Q('bool', must=["+strconcat1[:-1]+"],"
									+"should=[Q('match', attribute_set__educationaluse='documents'),Q('match', attribute_set__educationaluse='images'),Q('match', attribute_set__educationaluse='videos'),"
									"Q('match', attribute_set__educationaluse='interactives')])")

			else:

				q = eval("Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id),Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"],must_not=[Q('match', attribute_set__educationaluse ='ebooks')])")

				collection_query = eval("Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('multi_match', query=search_text, fields=['content','name','tags']),Q('exists',field='collection_set'),"+strconcat1[:-1]+"],"
									+ "should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],"
									+ "must_not=[Q('match', attribute_set__educationaluse ='ebooks')],minimum_should_match=1)")

				q_images_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='images'),Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"])")
				q_audios_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='audios'),Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"])")
				q_videos_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='videos'),Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"])")
				q_intercatives_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='interactives'),Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"])")
				q_applications_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='documents'),Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"])")
				q_ebooks_count = eval("Q('bool', must=[Q('match', attribute_set__educationaluse='ebooks'),Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"])")
				q_all_count = eval("Q('bool', must=[Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"],"
									+"should=[Q('match', attribute_set__educationaluse='documents'),Q('match', attribute_set__educationaluse='images'),Q('match', attribute_set__educationaluse='videos'),"
									"Q('match', attribute_set__educationaluse='interactives')])")

		else:
			if search_text in (None,'',""):
				q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match',member_of=GST_FILE1.hits[0].id)],
				must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
			else:
				q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match',member_of=GST_FILE1.hits[0].id),Q('multi_match', query=search_text, fields=['content','name','tags'])],
				must_not=[Q('match', attribute_set__educationaluse ='ebooks')])


		files_new = Search(using=es, index="nodes",doc_type="gsystem").query(q)
		files_new = files_new[0:24]


		if int(page_no)==1:
			files_new=files_new[0:24]
		else:
			temp=( int(page_no) - 1) * 24
			files_new=files_new[temp:temp+24]

		temp111 = ""
		if selfilters in (None,'',"") and search_text in (None,'',""):
			q_images_count = Q('bool', must=[Q('match', attribute_set__educationaluse='images'),Q('match', access_policy='public'),Q('match', group_set=str(group_id))])
			q_audios_count = Q('bool', must=[Q('match', attribute_set__educationaluse='audios'),Q('match', access_policy='public'),Q('match', group_set=str(group_id))])
			q_videos_count = Q('bool', must=[Q('match', attribute_set__educationaluse='videos'),Q('match', access_policy='public'),Q('match', group_set=str(group_id))])
			q_intercatives_count = Q('bool', must=[Q('match', attribute_set__educationaluse='interactives'),Q('match', access_policy='public'),Q('match', group_set=str(group_id))])
			q_applications_count = Q('bool', must=[Q('match', attribute_set__educationaluse='documents'),Q('match', access_policy='public'),Q('match', group_set=str(group_id))])
			q_ebooks_count = Q('bool', must=[Q('match', attribute_set__educationaluse='ebooks'),Q('match', access_policy='public'),Q('match', group_set=str(group_id))])
			q_all_count=  Q('bool', must=[Q('terms',attribute_set__educationaluse=['documents','images','audios','videos','interactives','maps','audio','select','teachers'])])

		elif selfilters in (None,'',"") and search_text is not None:
			q_images_count = Q('bool', must=[Q('match', attribute_set__educationaluse='images'),Q('match', access_policy='public'),Q('match', group_set=str(group_id)),Q('multi_match', query=search_text, fields=['content','name','tags'])])
			q_audios_count = Q('bool', must=[Q('match', attribute_set__educationaluse='audios'),Q('match', access_policy='public'),Q('match', group_set=str(group_id)),Q('multi_match', query=search_text, fields=['content','name','tags'])])
			q_videos_count = Q('bool', must=[Q('match', attribute_set__educationaluse='videos'),Q('match', access_policy='public'),Q('match', group_set=str(group_id)),Q('multi_match', query=search_text, fields=['content','name','tags'])])
			q_intercatives_count = Q('bool', must=[Q('match', attribute_set__educationaluse='interactives'),Q('match', access_policy='public'),Q('match', group_set=str(group_id)),Q('multi_match', query=search_text, fields=['content','name','tags'])])
			q_applications_count = Q('bool', must=[Q('match', attribute_set__educationaluse='documents'),Q('match', access_policy='public'),Q('match', group_set=str(group_id)),Q('multi_match', query=search_text, fields=['content','name','tags'])])
			q_ebooks_count = Q('bool', must=[Q('match', attribute_set__educationaluse='ebooks'),Q('match', access_policy='public'),Q('match', group_set=str(group_id)),Q('multi_match', query=search_text, fields=['content','name','tags'])])
			q_all_count=  Q('bool', must=[Q('terms',attribute_set__educationaluse=['documents','images','audios','videos','interactives','maps','audio','select','teachers']),Q('multi_match', query=search_text, fields=['content','name','tags'])])


		images_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_images_count)
		audios_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_audios_count)
		videos_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_videos_count)
		intercatives_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_intercatives_count)
		applications_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_applications_count)
		ebooks_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_ebooks_count)
		all_count =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q_all_count)
		q = Q('bool', should=[Q('match', attribute_set__educationaluse='images'),Q('match', attribute_set__educationaluse='videos'),
			Q('match', attribute_set__educationaluse='audios'),Q('match', attribute_set__educationaluse='documents'),
			Q('match', attribute_set__educationaluse='interactives')])
		
		
		educationaluse_stats = {}

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
			
			paginator = Paginator(files_new, 24)


		#page_no = request.GET.get('page_no')
			try:
				result_pages = paginator.page(page_no)
			except PageNotAnInteger:
				result_pages = paginator.page(1)
			except EmptyPage:
				result_pages = paginator.page(paginator.num_pages)
			# print educationaluse_stats
			#result_paginated_cur = files1_temp
			#result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)
			#result_paginated_cur = tuple(files1_temp)
			

		if selfilters:
			collection_pages_cur =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(collection_query)
		else:
			if search_text in (None,'',""):
				q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')],
				should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
				must_not=[Q('match', attribute_set__educationaluse ='ebooks')], minimum_should_match=1)
				collection_pages_cur =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)
			else:
				q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set'),Q('multi_match', query=search_text, fields=['content','name','tags'])],
				should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
				must_not=[Q('match', attribute_set__educationaluse ='ebooks')], minimum_should_match=1)
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
		datavisual.append({"name":"Doc", "count":  applications_count.count()})
		#datavisual.append({"name":"Page", "count": educationaluse_stats.get("Pages", 0)})
		datavisual.append({"name":"Image","count": images_count.count()})
		datavisual.append({"name":"Video","count": videos_count.count()})
		datavisual.append({"name":"Interactives","count": intercatives_count.count()})
		datavisual.append({"name":"Audios","count": audios_count.count()})
		datavisual.append({"name":"eBooks","count": ebooks_count.count()})
		if collection_pages_cur:	
			datavisual.append({"name":"Collections","count": collection_pages_cur.count()})
		datavisual = json.dumps(datavisual)
		

		return render_to_response(
	        'ndf/resource_list.html',
	        {'title': title, 'app':e_library_GST1.hits[0].name,
									 'appId':app_id, "app_gst": app1.hits[0],
									 'files': files_new,
									 "detail_urlname": "file_detail",
									 'ebook_pages': ebooks_count.count(),
									 #'ebook_pages': educationaluse_stats.get("eBooks", 0),
									 # 'page_count': pageCollection.count(),
									 # 'page_nodes':pageCollection
									 'all_files_count':files_new.count(),
									 'file_pages': result_pages,
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
									 "search_text":search_text
									 },

	        context_instance=RequestContext(request)
	    )

	@get_execution_time
	def elib_paged_file_objs(request, group_id, filetype, page_no):
		'''
		Method to implement pagination in File and E-Library app.
		'''
		#search_text = request.GET.get("search_text", None)

		if request.method == "POST":
			with open("Output.txt", "r") as text_file:
				search_text = text_file.read()
				text_file.close()

			print search_text
			
			group_name, group_id = get_group_name_id(group_id)

			no_of_objs_pp = 24
			result_pages = None
			results = None

			filters = request.POST.get("filters", "")
			filters = json.loads(filters)
			filters = get_filter_querydict(filters)

			query_dict = filters

			selfilters = urllib.unquote(request.GET.get('selfilters', ''))
			if "?selfilters" in selfilters:
				temp_list = selfilters.split("?selfilters")
				selfilters = temp_list[0]

			if selfilters:
				selfilters = json.loads(selfilters)
				query_dict = get_filter_querydict(selfilters)

			#query_dict.append({'attribute_set.educationaluse': {'$ne': u'eBooks'}})
			detail_urlname = "file_detail"
			i=-1
			strconcat=""
			endstring=""
			temp_dict={}
			lists = []
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
									#strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value["$in"][0]+"',type='phrase'))$$"
									lists.append("Q('match',"+t+"=dict(query='"+value["$in"][0]+"',type='phrase'))")
								elif value["$or"]:
									key = list(key)
									key[13]='__'
									t="".join(key)
									print t
									print "------------------------"
									temp_dict[t]=value["$or"][0]
									#strconcat=strconcat+"Q('match',"+t+"='"+value["$or"][0]+"') "
									#strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value["$or"][0]+"',type='phrase'))$$"
									lists.append("Q('match',"+t+"=dict(query='"+value["$or"][0]+"',type='phrase'))")
							elif isinstance(value, tuple):
								temp_dict["language"]= value[1]	
								#strconcat=strconcat+"Q('match',"+key+"='"+value[1]+"') "
								strconcat=strconcat+"Q('match',"+key+"=dict(query='"+value[1]+"',type='phrase'))$$"
								lists.append("Q('match',"+key+"=dict(query='"+value[1]+"',type='phrase'))")
							else:
								if key != "source":
									key = list(key)
									key[13]='__'
									t="".join(key)
									temp_dict[t]=value
									#strconcat=strconcat+"Q('match',"+ t+"='"+value+"') "
									#strconcat=strconcat+"Q('match',"+t+"=dict(query='"+value+"',type='phrase'))$$"
									lists.append("Q('match',"+t+"=dict(query='"+value+"',type='phrase'))")	
								else:
									temp_dict[key]=value
									#strconcat=strconcat+"Q('match',"+ key+"='"+value+"') "
									#strconcat=strconcat+"Q('match',"+key+"=dict(query='"+value+"',type='phrase'))$$"	
									lists.append("Q('match',"+key+"=dict(query='"+value+"',type='phrase'))")

			print temp_dict
			#strconcat=strconcat
			print strconcat
			print lists


			
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

			collection_query = None
			q= None

			strconcat1 = ""
			for value in lists:
				print value
				strconcat1 = strconcat1+'eval(str("'+ value +'")),'

			if filetype != "all":

				filetype = str(filetype)
				if filters:

					
					if search_text in (None,'',""):

						q = eval("Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id),Q('match', attribute_set__educationaluse=filetype),"+strconcat1[:-1]+"])")

						collection_query = eval("Q('bool', must=[Q('match', group_set=str(group_id)),Q('match',access_policy='public'),Q('exists',field='collection_set'),"+strconcat1[:-1]+"],"
											+ "should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],"
											+ "must_not=[Q('match', attribute_set__educationaluse ='ebooks')], minimum_should_match=1)")
					else:
						q = eval("Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id),Q('match', attribute_set__educationaluse=filetype),Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"])")

						collection_query = eval("Q('bool', must=[Q('match', group_set=str(group_id)),Q('match',access_policy='public'),Q('exists',field='collection_set'),Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"],"
											+ "should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],"
											+ "must_not=[Q('match', attribute_set__educationaluse ='ebooks')], minimum_should_match=1)")


				else:
					if search_text in (None,'',""):
					
						q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match', attribute_set__educationaluse =filetype)],
						should=[Q('match',member_of=GST_FILE1.hits[0].id)], minimum_should_match=1)
					
						collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')],
						should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
						must_not=[Q('match', attribute_set__educationaluse ='ebooks')], minimum_should_match=1)	
					else:
						q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match', attribute_set__educationaluse =filetype),Q('multi_match', query=search_text, fields=['content','name','tags'])],
						should=[Q('match',member_of=GST_FILE1.hits[0].id)], minimum_should_match=1)
					
						collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set'),Q('multi_match', query=search_text, fields=['content','name','tags'])],
						should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
						must_not=[Q('match', attribute_set__educationaluse ='ebooks')], minimum_should_match=1)	

					

				files1 =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)
				if int(page_no)==1:
					files1=files1[0:24]
				else:
					temp=( int(page_no) - 1) * 24
					files1=files1[temp:temp+24]
		
			else:
				if filters:
					if search_text in (None,'',""):

						q = eval("Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id),Q('terms',attribute_set__educationaluse=['documents','images','audios','videos']),"+strconcat1[:-1]+"])")

						collection_query = eval("Q('bool', must=[Q('match', group_set=str(group_id)),Q('match',access_policy='public'),Q('exists',field='collection_set'),"+strconcat1[:-1]+"],"
											+ "should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],"
											+ "must_not=[Q('match', attribute_set__educationaluse ='ebooks')], minimum_should_match=1)")

					else:

						q = eval("Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',member_of=GST_FILE1.hits[0].id),Q('terms',attribute_set__educationaluse=['documents','images','audios','videos']),Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"])")

						collection_query = eval("Q('bool', must=[Q('match', group_set=str(group_id)),Q('match',access_policy='public'),Q('multi_match', query=search_text, fields=['content','name','tags']),Q('exists',field='collection_set'),"+strconcat1[:-1]+"],"
											+ "should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],"
											+ "must_not=[Q('match', attribute_set__educationaluse ='ebooks')], minimum_should_match=1)")



				else:
					if search_text in (None,'',""):
						q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match',member_of=GST_FILE1.hits[0].id),Q('terms',attribute_set__educationaluse=['documents','images','audios','videos'])],
						)
						
						collection_query = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('exists',field='collection_set')],
							should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
							must_not=[Q('match', attribute_set__educationaluse ='ebooks')])
					else:
						q = Q('bool', must=[Q('match', group_set=str(group_id)), Q('match',access_policy='public'),Q('match',member_of=GST_FILE1.hits[0].id),Q('multi_match', query=search_text, fields=['content','name','tags']),Q('terms',attribute_set__educationaluse=['documents','images','audios','videos'])],
						)
						
						collection_query = Q('bool', must=[Q('match', group_set=str(group_id)),Q('multi_match', query=search_text, fields=['content','name','tags']), Q('match',access_policy='public'),Q('exists',field='collection_set')],
							should=[Q('match',member_of=GST_FILE1.hits[0].id),Q('match',member_of=GST_PAGE1.hits[0].id) ],
							must_not=[Q('match', attribute_set__educationaluse ='ebooks')])


				files1 =Search(using=es, index="gsystem",doc_type="image,video,audio,application").query(q)
				if int(page_no)==1:
					files1=files1[0:24]
				else:
					temp=( int(page_no) - 1) * 24
					files1=files1[temp:temp+24]
				print files1.count()
				

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
				print "collections if block"
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

				if int(page_no) == 1:
					result_cur=result_cur[0:24]
					
				else:
					temp=int(( int(page_no) - 1) * 24)
					result_cur=result_cur[temp:temp+24]
					

				result_paginated_cur = result_cur

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
		


else:
	print "mongo E-Library Running"
	##############################################################################

	GST_FILE = node_collection.one({'_type':'GSystemType', 'name': "File"})
	GST_PAGE = node_collection.one({'_type':'GSystemType', 'name': 'Page'})
	GST_IMAGE = node_collection.one({'_type':'GSystemType', 'name': GAPPS[3]})
	GST_VIDEO = node_collection.one({'_type':'GSystemType', 'name': GAPPS[4]})
	e_library_GST = node_collection.one({'_type':'GSystemType', 'name': 'E-Library'})
	pandora_video_st = node_collection.one({'_type':'GSystemType', 'name': 'Pandora_video'})
	app = node_collection.one({'_type':'GSystemType', 'name': 'E-Library'})
	wiki_page = node_collection.one({'_type': 'GSystemType', 'name': 'Wiki page'})
	GST_JSMOL = node_collection.one({"_type":"GSystemType","name":"Jsmol"})

	##############################################################################

	@get_execution_time
	def resource_list(request, group_id, app_id=None, page_no=1):
		"""
		* Renders a list of all 'Resources' available within the database (except eBooks).
		"""

		is_video = request.GET.get('is_video', "")



		try:
			group_id = ObjectId(group_id)
			#print group_id
		except:
			group_name, group_id = get_group_name_id(group_id)
			print group_name

		if app_id is None:
			app_id = str(app._id)

		# # Code for displaying user shelf
		# shelves = []
		# shelf_list = {}
		# auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })

		# if auth:
		#   has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })
		#   dbref_has_shelf = has_shelf_RT.get_dbref()
		#   shelf = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_has_shelf })
		#   shelf_list = {}

		#   if shelf:
		# 	for each in shelf:
		# 		shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)})
		# 		shelves.append(shelf_name)

		# 		shelf_list[shelf_name.name] = []
		# 		for ID in shelf_name.collection_set:
		# 		  shelf_item = node_collection.one({'_id': ObjectId(ID) })
		# 		  shelf_list[shelf_name.name].append(shelf_item.name)

		#   else:
		# 	shelves = []
		# # End of user shelf

		# pandoravideoCollection = node_collection.find({'member_of':pandora_video_st._id, 'group_set': ObjectId(group_id) })

		# if e_library_GST._id == ObjectId(app_id):
		title = e_library_GST.name
		file_id = GST_FILE._id
		datavisual = []
		no_of_objs_pp = 24

		# filters = request.POST.get("filters", "")
		# filters = json.loads(filters)
		# filters = get_filter_querydict(filters)

		# print "filters in E-Library : ", filters

		# declaring empty (deliberately to avoid errors), query dict to be pass-on in query
		query_dict = []
		# query_dict = filters

		selfilters = urllib.unquote(request.GET.get('selfilters', ''))
		if selfilters:
			selfilters = json.loads(selfilters)
			query_dict = get_filter_querydict(selfilters)

		query_dict.append({'attribute_set.educationaluse': {'$ne': 'eBooks'}})
		

		# files = node_collection.find({
		# 								'member_of': ObjectId(GST_FILE._id),
		# 								'_type': 'File',
		# 								'fs_file_ids': {'$ne': []},
		# 								'group_set': ObjectId(group_id),
		# 								'$and': query_dict,
		# 								'$or': [
		# 										{ 'access_policy': u"PUBLIC" },
		# 										{ '$and': [
		# 													{'access_policy': u"PRIVATE"},
		# 													{'created_by': request.user.id}
		# 												]
		# 										}
		# 									]

		# 								}).sort("last_update", -1)

		files = node_collection.find({
										# 'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
										'member_of': {'$in': [GST_FILE._id,GST_JSMOL._id]},
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


		educationaluse_stats = {}


		if files:
			eu_list = []  # count
			for each in files:
				eu_list += [i.get("educationaluse") for i in each.attribute_set if i.has_key("educationaluse")]

			files.rewind()

			if set(eu_list):
				if len(set(eu_list)) > 1:
					educationaluse_stats = dict((x, eu_list.count(x)) for x in set(eu_list))
				elif len(set(eu_list)) == 1:
					educationaluse_stats = { eu_list[0]: eu_list.count(eu_list[0])}
				educationaluse_stats["all"] = files.count()
			

			# print educationaluse_stats
			result_paginated_cur = files
			result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

		collection_pages_cur = node_collection.find({
										'member_of': {'$in': [GST_FILE._id, GST_PAGE._id ]},
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

		coll_page_count = collection_pages_cur.count() if collection_pages_cur else 0
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

		return render_to_response("ndf/resource_list.html",
									{'title': title, 'app':e_library_GST,
									 'appId':app._id, "app_gst": app,
									 # 'already_uploaded': already_uploaded,'shelf_list': shelf_list,'shelves': shelves,
									 'files': files,
									 "detail_urlname": "file_detail",
									 'ebook_pages': educationaluse_stats.get("eBooks", 0),
									 # 'page_count': pageCollection.count(),
									 # 'page_nodes':pageCollection
									 'file_pages': result_pages,
									 'image_pages': educationaluse_stats.get("Images", 0),
									 'interactive_pages': educationaluse_stats.get("Interactives", 0),
									 'educationaluse_stats': json.dumps(educationaluse_stats),
									 'doc_pages': educationaluse_stats.get("Documents", 0),
									 'video_pages': educationaluse_stats.get("Videos", 0),
									 'audio_pages': educationaluse_stats.get("Audios", 0),
									 'collection_pages': collection_pages,
									 'collection': collection_pages_cur,
									 'groupid': group_id, 'group_id':group_id,
									 "datavisual":datavisual,
									},
									context_instance = RequestContext(request))

	@get_execution_time
	def elib_paged_file_objs(request, group_id, filetype, page_no):
		'''
		Method to implement pagination in File and E-Library app.
		'''
		if request.is_ajax() and request.method == "POST":
			group_name, group_id = get_group_name_id(group_id)

			no_of_objs_pp = 24
			result_pages = None

			filters = request.POST.get("filters", "")
			filters = json.loads(filters)
			filters = get_filter_querydict(filters)

			# print "filters in E-Library : ", filters

			# declaring empty (deliberately to avoid errors), query dict to be pass-on in query
			# query_dict = [{}]
			query_dict = filters

			selfilters = urllib.unquote(request.GET.get('selfilters', ''))
			if selfilters:
				selfilters = json.loads(selfilters)
				query_dict = get_filter_querydict(selfilters)

			query_dict.append({'attribute_set.educationaluse': {'$ne': u'eBooks'}})

			detail_urlname = "file_detail"
			if filetype != "all":
				# if filetype == "Pages":
				# 	detail_urlname = "page_details"
				# 	result_cur = node_collection.find({'member_of': GST_PAGE._id,
	   #                                  '_type': 'GSystem',
	   #                                  'group_set': {'$all': [ObjectId(group_id)]},
	   #                                  '$or': [
	   #                                      {'access_policy': u"PUBLIC"},
	   #                                      {'$and': [
	   #                                          {'access_policy': u"PRIVATE"},
	   #                                          {'created_by': request.user.id}
	   #                                      ]
	   #                                   }
	   #                                  ]
	   #                              }).sort("last_update", -1)

				# 	result_paginated_cur = result_cur
				# 	result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

				# elif filetype == "Collections":
				if filetype == "Collections":
					pass
					# detail_urlname = "page_details"
					# result_cur = node_collection.find({
					# 					'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
	    #                                 'group_set': {'$all': [ObjectId(group_id)]},
	    #                                 '$or': [
	    #                                     {'access_policy': u"PUBLIC"},
	    #                                     {'$and': [
	    #                                         {'access_policy': u"PRIVATE"},
	    #                                         {'created_by': request.user.id}
	    #                                     ]
	    #                                  }
	    #                                 ],
	    #                                 'collection_set': {'$exists': "true", '$not': {'$size': 0} }
	    #                             }).sort("last_update", -1)
					# # print "=====================", result_cur.count()

					# result_paginated_cur = result_cur
					# result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)
					# # print "=====================", result_pages

					# query_dict.append({ 'collection_set': {'$exists': "true", '$not': {'$size': 0} } })
				else:
					query_dict.append({"attribute_set.educationaluse": filetype})

			# print filters
			# if filters:
			# 	temp_list = []
			# 	for each in filters:
			# 		filter_grp = each["or"]
			# 		for each_filter in filter_grp:
			# 			temp_dict = {}
			# 			each_filter["selFieldText"] = cast_to_data_type(each_filter["selFieldText"], each_filter["selFieldPrimaryType"])

			# 			if each_filter["selFieldPrimaryType"] == unicode("list"):
			# 				each_filter["selFieldText"] = {"$in": each_filter["selFieldText"]}

			# 			if each_filter["selFieldGstudioType"] == "attribute":

			# 				temp_dict["attribute_set." + each_filter["selFieldValue"]] = each_filter["selFieldText"]
			# 				temp_list.append(temp_dict)
			# 				# print "temp_list : ", temp_list
			# 			elif each_filter["selFieldGstudioType"] == "field":
			# 				temp_dict[each_filter["selFieldValue"]] = each_filter["selFieldText"]
			# 				temp_list.append(temp_dict)

			# 		if temp_list:
			# 			query_dict.append({ "$or": temp_list})

			# print "query_dict : ", query_dict

			
			files = node_collection.find({
											'member_of': {'$in': [GST_FILE._id,GST_JSMOL._id]},
											# 'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
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


			educationaluse_stats = {}
			# print "files_count: ", files.count()

			# if filetype == "Pages":
			# 	filter_result = "True" if (result_cur.count() > 0) else "False"
			# else:
			if files:# and not result_pages:
				# print "=======", educationaluse_stats

				eu_list = []  # count
				collection_set_count = 0
				for each in files:
					eu_list += [i.get("educationaluse") for i in each.attribute_set if i.has_key("educationaluse")]
					collection_set_count += 1 if each.collection_set else 0

				files.rewind()

				if set(eu_list):
					if len(set(eu_list)) > 1:
						educationaluse_stats = dict((x, eu_list.count(x)) for x in set(eu_list))
					elif len(set(eu_list)) == 1:
						educationaluse_stats = { eu_list[0]: eu_list.count(eu_list[0])}
					educationaluse_stats["all"] = files.count()
					educationaluse_stats["Collections"] = collection_set_count

				result_paginated_cur = files
				result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

			filter_result = "True" if (files.count() > 0) else "False"

			if filetype == "Collections":
					detail_urlname = "page_details"
					result_cur = node_collection.find({
										'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
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
					# print "=====================", result_cur.count()

					result_paginated_cur = result_cur
					result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

			# if filetype == "all":
			#     if files:
			#         result_paginated_cur = files
			#         result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

			# # else:
			# elif filetype == "Documents":
			#     d_Collection = node_collection.find({'_type': "GAttribute", 'attribute_type': gattr._id,"subject": {'$in': coll} ,"object_value": "Documents"}).sort("last_update", -1)

			#     doc = []
			#     for e in d_Collection:
			#         doc.append(e.subject)

			#     result_paginated_cur = node_collection.find({ '$or':[{'_id': {'$in': doc}},

			#                 {'member_of': {'$nin': [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id),ObjectId(pandora_video_st._id)]},
			#                                     '_type': 'File', 'group_set': {'$all': [ObjectId(group_id)]},
			#                                     # 'mime_type': {'$not': re.compile("^audio.*")},
			#                                     '$or': [
			#                                           {'access_policy': u"PUBLIC"},
			#                                             {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
			#                                            ]
			#                                     }]

			#         }).sort("last_update", -1)

			#     result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

			# print "educationaluse_stats: ", educationaluse_stats

			return render_to_response ("ndf/file_list_tab.html", {
					"filter_result": filter_result,
					"group_id": group_id, "group_name_tag": group_id, "groupid": group_id,
					'title': "E-Library", "educationaluse_stats": json.dumps(educationaluse_stats),
					"resource_type": result_paginated_cur, "detail_urlname": detail_urlname,
					"filetype": filetype, "res_type_name": "", "page_info": result_pages
				},
				context_instance = RequestContext(request))

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
	except:
		group_name, group_id = get_group_name_id(group_id)

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

''' -- imports from installed packages -- ''' 
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django_mongokit import get_database
from gnowsys_ndf.ndf.org2any import org2html

import re

try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId
from mongokit import paginator

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import Node, GRelation,GSystemType,File,Triple
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id

#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
collection_tr = db[Triple.collection_name]
GST_FILE = collection.GSystemType.one({'name': "File", '_type':'GSystemType'})
GST_IMAGE = collection.GSystemType.one({'name': GAPPS[3], '_type':'GSystemType'})
GST_VIDEO = collection.GSystemType.one({'name': GAPPS[4], '_type':'GSystemType'})
e_library_GST = collection.GSystemType.one({'_type':'GSystemType', 'name': 'E-Library'})
pandora_video_st = collection.GSystemType.one({'_type':'GSystemType', 'name': 'Pandora_video'})
app = collection.GSystemType.one({'_type':'GSystemType', 'name': 'E-Library'})

#######################################################################################################################################

def resource_list(request, group_id, app_id=None, page_no=1):

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
		app_ins = collection.Node.find_one({'_type':'GSystemType', 'name': 'E-Library'})
		if app_ins:
			app_id = str(app_ins._id)

	# Code for displaying user shelf 
	shelves = []
	shelf_list = {}
	auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) }) 

	if auth:
	  has_shelf_RT = collection.Node.one({'_type': 'RelationType', 'name': u'has_shelf' })
	  dbref_has_shelf = has_shelf_RT.get_dbref()
	  shelf = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_has_shelf })        
	  shelf_list = {}

	  if shelf:
		for each in shelf:
			shelf_name = collection.Node.one({'_id': ObjectId(each.right_subject)}) 
			shelves.append(shelf_name)

			shelf_list[shelf_name.name] = []         
			for ID in shelf_name.collection_set:
			  shelf_item = collection.Node.one({'_id': ObjectId(ID) })
			  shelf_list[shelf_name.name].append(shelf_item.name)

	  else:
		shelves = []
	# End of user shelf

	pandoravideoCollection=collection.Node.find({'member_of':pandora_video_st._id, 'group_set': ObjectId(group_id) })

	# if e_library_GST._id == ObjectId(app_id):
	"""
	* Renders a list of all 'Resources(XCR)' available within the database.
	"""
	title = e_library_GST.name

	file_id = GST_FILE._id
	datavisual = []
	no_of_objs_pp = 24

	# files = collection.Node.find({'$or':[{'member_of': ObjectId(file_id), 
	#                                 	  '_type': 'File', 'fs_file_ids':{'$ne': []}, 
	#                                 	  'group_set': ObjectId(group_id),
	#                                 	  '$or': [{'access_policy': u"PUBLIC"},
	#                                   				{'$and': [{'access_policy': u"PRIVATE"}, 
	#                                       					  {'created_by': request.user.id}
	#                                     					 ]
	#                                   				}
	#                                 			]
	#                                 	 },
	#                                          {'member_of': ObjectId(pandora_video_st._id), 'accesss_policy': u"PUBLIC",
	#                                 	  'group_set': ObjectId(group_id)
	#                                 	 }]

	#                               }).sort("last_update", -1)

	
	files = collection.Node.find({
									'$or':[
											{
												'member_of': ObjectId(GST_FILE._id), 
												'_type': 'File',
												'fs_file_ids': {'$ne': []}, 
												'group_set': ObjectId(group_id), 
												# '$and': query_dict,
												'$or': [
														{ 'access_policy': u"PUBLIC" },
														{ '$and': [
																	{'access_policy': u"PRIVATE"}, 
																	{'created_by': request.user.id}
																]
														}
													]
											}, 
											{ 
												'member_of': ObjectId(pandora_video_st._id), 
												'group_set': ObjectId(group_id) 
											}
										],
										'status': u"PUBLISHED"
									}).sort("last_update", -1)

	# print "files.count : ", files.count()

	# coll = []
	# for each in files:
	#     coll.append(each._id)

	# files.rewind()
	# gattr = collection.Node.one({'_type': 'AttributeType', 'name': u'educationaluse'})
  
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

		# print "educationaluse_stats : ", educationaluse_stats
		# print "eu_list : ", len(eu_list)
		
		result_paginated_cur = files
		result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)


	# All files list
	# coll = []
	# for each in files:
	# 	coll.append(each._id)

	# files.rewind()
	# file_pages = paginator.Paginator(files, page_no, no_of_objs_pp)

	# gattr = collection.Node.one({'_type': 'AttributeType', 'name': u'educationaluse'})
	# interCollection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id, "subject": {'$in': coll} ,"object_value": "Interactives"}).sort("last_update", -1)
	# d_Collection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id,"subject": {'$in': coll} ,"object_value": "Documents"}).sort("last_update", -1)
	# aud_Collection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id,"subject": {'$in': coll} ,"object_value": "Audios"}).sort("last_update", -1)
	# img_Collection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id,"subject": {'$in': coll} ,"object_value": "Images"}).sort("last_update", -1)
	# vid_Collection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id,"subject": {'$in': coll} ,"object_value": "Videos"}).sort("last_update", -1)

	# # For manipulating documents
	# doc = []
	# for e in d_Collection:
	# 	doc.append(e.subject)

	# docCollection = collection.Node.find({ '$or':[{'_id': {'$in': doc}},

	# 											   {'member_of': {'$nin': [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id),ObjectId(pandora_video_st._id)]},
	# 	                                            '_type': 'File', 'group_set': {'$all': [ObjectId(group_id)]},
	# 	                                             'mime_type': {'$not': re.compile("^audio.*")},
	# 	                                            '$or': [
	# 	                                                 	{'access_policy': u"PUBLIC"},
	# 	                                                  	{'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
	# 	                                                   ]
	# 	                                           	}]

	# 									}).sort("last_update", -1)


	# doc_pages = paginator.Paginator(docCollection, page_no, no_of_objs_pp)
	# # End of fetching the documents

	# # For manipulating interactives
	# interactive = []
	# for e in interCollection:
	# 	interactive.append(e.subject)

	# interactiveCollection = collection.Node.find({'_id': {'$in': interactive} })    
	# interactive_pages = paginator.Paginator(interactiveCollection, page_no, no_of_objs_pp)
	# # End of fetching the interactives

	# # For manipulating audios
	# audio = []
	# for e in aud_Collection:
	# 	audio.append(e.subject)

	# # audioCollection = collection.Node.find({'_id': {'$in': audio} })  
	# audioCollection = collection.Node.find({ '$or':[{'_id': {'$in': audio}},

	# 										{'member_of': {'$nin': [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id)]},
	# 	                                            '_type': 'File','group_set': {'$all': [ObjectId(group_id)]},
	# 	                                            'mime_type': {'$regex': 'audio','$options': "i"},
	# 	                                            '$or': [
	# 	                                                 	{'access_policy': u"PUBLIC"},
	# 	                                                  	{'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
	# 	                                                   ]
	# 	                                           	}]

	# 									}).sort("last_update", -1)


	# audio_pages = paginator.Paginator(audioCollection, page_no, no_of_objs_pp)
	# # End of fetching the audios

	# # For manipulating images
	# image = []
	# for e in img_Collection:
	# 	image.append(e.subject)

	# # imageCollection = collection.Node.find({'_id': {'$in': image} }) 
	# imageCollection = collection.Node.find({'$or': [{'_id': {'$in': image} }, 

	# 												{'member_of': {'$all': [ObjectId(GST_IMAGE._id)]}, 
	# 	                                             '_type': 'File', 'group_set': {'$all': [ObjectId(group_id)]},
	# 	                                             '$or': [
	# 	                                                 	{'access_policy': u"PUBLIC"},
	# 	                                                  	{'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
	# 	                                                   ]
	# 	                                           	}]

	# 									}).sort("last_update", -1)


	# image_pages = paginator.Paginator(imageCollection, page_no, no_of_objs_pp)
	# # End of fetching the images

	# # For manipulating videos
	# video = []
	# for e in vid_Collection:
	# 	video.append(e.subject)

	# # videoCollection = collection.Node.find({'_id': {'$in': video} }) 

	# videoCollection = collection.Node.find({'$or': [{'_id': {'$in': video} }, 
														
 #                                                        {'member_of': {'$in': [ObjectId(GST_VIDEO._id),ObjectId(pandora_video_st._id)]}, 
	# 	                                             '_type': 'File', 'access_policy': {'$ne': u"PRIVATE"}, 'group_set': {'$all': [ObjectId(group_id)]},
	# 	                                             '$or': [
	# 	                                                 	{'access_policy': u"PUBLIC"},
	# 	                                                  	{'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
	# 	                                                   ]
	# 	                                           	}]

	# 									}).sort("last_update", -1)


	# video_pages = paginator.Paginator(videoCollection, page_no, no_of_objs_pp)
	# # End of fetching the images
	
	# # files.rewind()
	# already_uploaded = request.GET.getlist('var', "")

	# get_member_set = collection.Node.find({'$and':[{'member_of': {'$all': [ObjectId(pandora_video_st._id)]}},{'group_set': ObjectId(group_id)},{'_type':'File'}]})

	# datavisual.append({"name":"Doc", "count":docCollection.count()})
	# datavisual.append({"name":"Image","count":imageCollection.count()})
	# datavisual.append({"name":"Video","count":videoCollection.count()})
	# datavisual.append({"name":"Interactives","count":interactiveCollection.count()})
	# datavisual.append({"name":"Audios","count":audioCollection.count()})
	# datavisual = json.dumps(datavisual)

	datavisual.append({"name":"Doc", "count": educationaluse_stats.get("Documents", 0)})
	datavisual.append({"name":"Image","count": educationaluse_stats.get("Images", 0)})
	datavisual.append({"name":"Video","count": educationaluse_stats.get("Videos", 0)})
	datavisual.append({"name":"Interactives","count": educationaluse_stats.get("Interactives", 0)})
	datavisual.append({"name":"Audios","count": educationaluse_stats.get("Audios", 0)})
	datavisual = json.dumps(datavisual)

	return render_to_response("ndf/resource_list.html", 
								{'title': title, 
								 'appId':app._id,
								 # 'already_uploaded': already_uploaded,'shelf_list': shelf_list,'shelves': shelves,
								 'files': files,
								 # 'docCollection': docCollection, 'imageCollection': imageCollection,
								 # 'videoCollection': videoCollection, 'pandoravideoCollection':pandoravideoCollection,
								 # 'pandoraCollection':get_member_set,'interactiveCollection': interactiveCollection,
								 # 'audioCollection':audioCollection, 
								 "detail_urlname": "file_detail",
								 'file_pages': result_pages, 'image_pages': educationaluse_stats.get("Images", 0), 'interactive_pages': educationaluse_stats.get("Interactives", 0), 'educationaluse_stats': json.dumps(educationaluse_stats),
								 'doc_pages': educationaluse_stats.get("Documents", 0), 'video_pages': educationaluse_stats.get("Videos", 0), 'audio_pages': educationaluse_stats.get("Audios", 0),
								 # 'is_video':is_video,
								 'groupid': group_id, 'group_id':group_id,"datavisual":datavisual
								}, 
								context_instance = RequestContext(request))


def elib_paged_file_objs(request, group_id, filetype, page_no):
	'''
	Method to implement pagination in File and E-Library app.
	'''
	if request.is_ajax() and request.method == "POST":
		
		group_name, group_id = get_group_name_id(group_id)

		no_of_objs_pp = 24

		filters = request.POST.get("filters", "")
		filters = json.loads(filters)
		# print "filters in E-Library : ", filters

		# declaring empty (deliberately to avoid errors), query dict to be pass-on in query
		query_dict = [{}]

		if filetype != "all":
			query_dict.append({"attribute_set.educationaluse": filetype})

		if filters:
			for each in filters:
				filter_grp = each["$or"]
				temp_list = []
				for each_filter in filter_grp:
					temp_dict = {}
					if each_filter["selFieldGstudioType"] == "attribute":
						if each_filter["selFieldPrimaryType"] == unicode("bool"):
							if (each_filter["selFieldText"] == "True"):
								each_filter["selFieldText"] = True
							elif (each_filter["selFieldText"] == "False"):
								each_filter["selFieldText"] = False
						temp_dict["attribute_set." + each_filter["selFieldValue"]] = each_filter["selFieldText"]
						temp_list.append(temp_dict)
						# print "temp_list : ", temp_list
					elif each_filter["selFieldGstudioType"] == "field":
						temp_dict[each_filter["selFieldValue"]] = each_filter["selFieldText"]
						temp_list.append(temp_dict)
				
				if temp_list:			        	
					query_dict.append({ "$or": temp_list})

		# print "query_dict : ", query_dict

		files = collection.Node.find({
										'$or':[
												{
													'member_of': ObjectId(GST_FILE._id), 
													'_type': 'File',
													'fs_file_ids': {'$ne': []}, 
													'group_set': ObjectId(group_id), 
													'$and': query_dict,
													'$or': [
															{ 'access_policy': u"PUBLIC" },
															{ '$and': [
																		{'access_policy': u"PRIVATE"}, 
																		{'created_by': request.user.id}
																	]
															}
														]
												}, 
												{ 
													'member_of': ObjectId(pandora_video_st._id), 
													'group_set': ObjectId(group_id) 
												}
											],
											'status': u"PUBLISHED"
										}).sort("last_update", -1)

		# print "files.count : ", files.count()

		# coll = []
		# for each in files:
		#     coll.append(each._id)

		# files.rewind()
		# gattr = collection.Node.one({'_type': 'AttributeType', 'name': u'educationaluse'})
	  
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

			# print "educationaluse_stats : ", educationaluse_stats
			# print "eu_list : ", len(eu_list)
			
			result_paginated_cur = files
			result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)
				
		# if filetype == "all":
		#     if files:
		#         result_paginated_cur = files
		#         result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

		# # else:
		# elif filetype == "Documents":
		#     d_Collection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id,"subject": {'$in': coll} ,"object_value": "Documents"}).sort("last_update", -1)

		#     doc = []
		#     for e in d_Collection:
		#         doc.append(e.subject)

		#     result_paginated_cur = collection.Node.find({ '$or':[{'_id': {'$in': doc}},

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

		# elif filetype == "Images":
		#     img_Collection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id,"subject": {'$in': coll} ,"object_value": "Images"}).sort("last_update", -1)
		#     image = []
		#     for e in img_Collection:
		#         image.append(e.subject)

		#     # result_paginated_cur = collection.Node.find({'_id': {'$in': image} })    
		#     result_paginated_cur = collection.Node.find({'$or': [{'_id': {'$in': image} }, 

		#                 {'member_of': {'$all': [ObjectId(GST_IMAGE._id)]}, 
		#                                      '_type': 'File', 'group_set': {'$all': [ObjectId(group_id)]},
		#                                      '$or': [
		#                                           {'access_policy': u"PUBLIC"},
		#                                             {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
		#                                            ]
		#                                     }]

		#         }).sort("last_update", -1)

		#     result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)                

		# elif filetype == "Videos":
		#     vid_Collection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id,"subject": {'$in': coll} ,"object_value": "Videos"}).sort("last_update", -1)
		#     video = []
		#     for e in vid_Collection:
		#         video.append(e.subject)

		#     result_paginated_cur = collection.Node.find({'$or': [{'_id': {'$in': video} }, 

		#               {'member_of': {'$in': [ObjectId(GST_VIDEO._id),ObjectId(pandora_video_st._id)]}, 
		#                                      '_type': 'File', 'access_policy': {'$ne':u"PRIVATE"}, 'group_set': {'$all': [ObjectId(group_id)]},
		#                                      '$or': [
		#                                           {'access_policy': u"PUBLIC"},
		#                                             {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
		#                                            ]
		#                                     }]

		#         }).sort("last_update", -1)


		#     result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

		# elif filetype == "Interactives":
		#     interCollection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id, "subject": {'$in': coll} ,"object_value": "Interactives"}).sort("last_update", -1)
		#     interactive = []
		#     for e in interCollection:
		#         interactive.append(e.subject)

		#     result_paginated_cur = collection.Node.find({'_id': {'$in': interactive} })    
		#     result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

		# elif filetype == "Audios":
		#     aud_Collection = collection.Node.find({'_type': "GAttribute", 'attribute_type.$id': gattr._id,"subject": {'$in': coll} ,"object_value": "Audios"}).sort("last_update", -1)

		#     audio = []
		#     for e in aud_Collection:
		#         audio.append(e.subject)

		#     # result_paginated_cur = collection.Node.find({'_id': {'$in': audio} })  

		#     result_paginated_cur = collection.Node.find({ '$or':[{'_id': {'$in': audio}},

		#               {'member_of': {'$nin': [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id)]},
		#                                         '_type': 'File', 'group_set': {'$all': [ObjectId(group_id)]},
		#                                         'mime_type': {'$regex': 'audio','$options': "i"},
		#                                         '$or': [
		#                                               {'access_policy': u"PUBLIC"},
		#                                                 {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
		#                                                ]
		#                                         }]

		#             }).sort("last_update", -1)


		#     result_pages = paginator.Paginator(result_paginated_cur, page_no, no_of_objs_pp)

		
		return render_to_response ("ndf/file_list_tab.html", {
				"group_id": group_id, "group_name_tag": group_id, "groupid": group_id,
				'title': "E-Library", "educationaluse_stats": json.dumps(educationaluse_stats),
				"resource_type": result_paginated_cur, "detail_urlname": "file_detail", 
				"filetype": filetype, "res_type_name": "", "page_info": result_pages
			}, 
			context_instance = RequestContext(request))

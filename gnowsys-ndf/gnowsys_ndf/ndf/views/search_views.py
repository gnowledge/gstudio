from django.shortcuts import render
from django.http import HttpResponse
from gnowsys_ndf.ndf.models import *
from django.template import RequestContext
from stemming.porter2 import stem
# from bson.json_util import dumps
import json
from collections import OrderedDict
import difflib
import string
import datetime
import itertools
#############
collection = get_database()[Node.collection_name]
#############

class Encoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, ObjectId):
			return str(obj)
		else:
			return obj

def insert_all_links():
        col = get_database()[Node.collection_name] 	
	all_GSystemTypes = col.Node.find({"_type":"GSystemType"}, {"name":1, "_id":1})

	for GSystem in all_GSystemTypes:
		instance = col.allLinks()
		instance.link = GSystem.name
		instance.member_of = ObjectId(GSystem._id)
		instance.required_for = u"Links"
		instance.save()
	
def search_query(request, group_id):
	"""Renders a list of all 'Page-type-GSystems' available within the database.
	"""
	# Check if no link objects are added and add them if required	
	col = get_database()[Node.collection_name]
	link_instances = col.Node.find({"required_for":"Links"}, {"name":1})
	
	if (link_instances.count() == 0):
		print "Adding links\n"
		insert_all_links()

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
		group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		if group_ins:
			group_id = str(group_ins._id)
		else:
	    		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    		if auth :
				group_id = str(auth._id)
	else:
		pass

	# print "In search form the request " + request.GET['search_text']
	memList = populate_list_of_members()
	print "list: ", memList
	return render(request, 'ndf/search_home.html', {"groupid":group_id, "authors":memList}, context_instance=RequestContext(request))


def search_query_group(request, group_id):
	"""Renders a list of all 'Page-type-GSystems' available within the database.
	"""
	# Check if no link objects are added and add them if required	
	col = get_database()[Node.collection_name]
	link_instances = col.Node.find({"required_for":"Links"}, {"name":1})
	
	if (link_instances.count() == 0):
		print "Adding links\n"
		insert_all_links()

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
		group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		if group_ins:
			group_id = str(group_ins._id)
		else:
	    		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    		if auth :
				group_id = str(auth._id)
	else:
		pass

	# print "In search form the request " + request.GET['search_text']
	memList = populate_list_of_members()
	print "list: ", memList
	return render(request, 'ndf/search_home.html', {"groupid":group_id, "authors":memList}, context_instance=RequestContext(request))



def results_search(request, group_id):
	
	# DECLARE THE VARIABLES
	search_by_name = 0
	search_by_tags = 0
	search_by_contents = 0
	user = ""
	user_reqd = -1

#	try:
	if request.method == "GET":
		# PRINT THE VALUES TO SEE IF STEMMING, ARTICLE REMOVAL IS RIGHT
		print "all users: ", str(request.GET['users'])		
		user_reqd_name = str(request.GET['users'])
		if user_reqd_name != "all":
			user_reqd = int(User.objects.get(username = 'siddhant').pk)
 		
		search_str_user = str(request.GET['search_text'])
		print "\noriginal search string:", search_str_user, "\n"
		search_str_user = search_str_user.lower()

		search_str_noArticles = list(removeArticles(str(search_str_user)))
		print "\narticles removed:",search_str_noArticles,"\n"

		search_str_stemmed = list(stemWords(search_str_noArticles, search_str_user))
		print "\nwords stemmed:",search_str_stemmed,"\n\n\n"

		# -------------------------------------------------------
		print "Search string lowercase:", search_str_user

		# GET THE LIST OF CHECKBOXES TICKED AND SET CORR. FLAGS
		checked_fields = request.GET.getlist('search_fields')
		nam = "name"
	
		print "\n\nfields: ", checked_fields, "\n\n"	
		if (nam in checked_fields):
			print "by_name"
			search_by_name = 1

		nam = "tags"
		if (nam in checked_fields):
			print "by_tags"
			search_by_tags = 1
		
		nam = "contents"
		if (nam in checked_fields):
			print "by_contents"
			search_by_contents = 1

		#user = str(request.GET['author'])				# GET THE VALUE OF AUTHOR FROM THE FORM

		col = get_database()[Node.collection_name]			# COLLECTION NAME


		# FORMAT OF THE RESULTS RETURNED
		search_results_ex = {'name':[], 'tags':[], 'content':[], 'user':[]}
		search_results_st = {'name':[], 'tags':[], 'content':[], 'user':[]}
		search_results_li = {'name':[], 'tags':[], 'content':[], 'user':[]}
		
		# ALL SORTED SEARCH RESULTS
		search_results = {'exact':search_results_ex, 'stemmed':search_results_st, 'like':search_results_li}

		# STORES OBJECTID OF EVERY SEARCH RESULT TO CHECK FOR DUPLICATES
		all_ids = []

		# GET A CURSOR ON ALL THE GSYSTEM TYPES 
		all_GSystemTypes = col.Node.find({"_type":"GSystemType"}, {"_id":1})
		len1 = all_GSystemTypes.count()
		
		if (search_by_name == 1):					# IF 1, THEN SEARCH BY NAME
			all_GSystemTypes.rewind()
			count = 0

			for GSType in all_GSystemTypes:

				# EXACT MATCH OF SEARCH_USER_STR IN NAME OF GSYSTEMS OF ONE GSYSTEM TYPE
				if user_reqd != -1:				
					exact_match = col.Node.find({"member_of":GSType._id, "created_by":user_reqd, "access_policy":"PUBLIC", "name":{"$regex":search_str_user, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
				else:
					exact_match = col.Node.find({"member_of":GSType._id, "access_policy":"PUBLIC", "name":{"$regex":search_str_user, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})					

				# SORT THE NAMES ACCORDING TO THEIR SIMILARITY WITH THE SEARCH STRING
				exact_match = list(exact_match)				
				#exact_match = sort_names_by_similarity(exact_match, search_str_user)

				for j in exact_match:
					if j._id not in all_ids:
						j = addType(j)
						search_results_ex['name'].append(j)
						all_ids.append(j['_id'])
				search_results_ex['name'] = sort_names_by_similarity(search_results_ex['name'], search_str_user)
				
				# split stemmed match
				split_stem_match = []
				len_stemmed = len(search_str_stemmed)
				c = 0								# GEN. COUNTER 

				while c < len_stemmed:
					word = search_str_stemmed[c]
					if user_reqd != -1:
						temp = col.Node.find({"member_of":GSType._id, "created_by":user_reqd, "access_policy":"PUBLIC", "name":{"$regex":word, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
					else:
						temp = col.Node.find({"member_of":GSType._id, "access_policy":"PUBLIC", "name":{"$regex":word, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
					#temp_sorted = sort_names_by_similarity(temp, search_str_user)
					split_stem_match.append(temp)#temp_sorted)
					c += 1
				
				for j in split_stem_match:
					c = 0
					for k in j:
						if (k._id not in all_ids):
							k = addType(k)
							search_results_st['name'].append(k)
							all_ids.append(k['_id'])
							c += 1
				search_results_st['name'] = sort_names_by_similarity(search_results_st['name'], search_str_user)


		if (search_by_tags == 1):						# IF 1, THEN SEARCH BY TAGS

			all_GSystemTypes.rewind()
			count = 0

			for GSType in all_GSystemTypes:

				# EXACT MATCH OF SEARCH_USER_STR IN NAME OF GSYSTEMS OF ONE GSYSTEM TYPE
				if user_reqd != -1:				
					exact_match = col.Node.find({"member_of":GSType._id, "created_by":user_reqd, "access_policy":"PUBLIC", "tags":search_str_user}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
				else:
					exact_match = col.Node.find({"member_of":GSType._id, "access_policy":"PUBLIC", "tags":search_str_user}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
				#exact_match = sort_names_by_similarity(exact_match, search_str_user)
				
				for j in exact_match:
					if j._id not in all_ids:
						j = addType(j)
						search_results_ex['tags'].append(j)
						all_ids.append(j['_id'])
				search_results_ex['tags'] = sort_names_by_similarity(search_results_ex['tags'], search_str_user)

				# split stemmed match
				split_stem_match = []
				c = 0						# GEN. COUNTER 
				len_stemmed = len(search_str_stemmed)

				while c < len_stemmed:
					word = search_str_stemmed[c]
					if user_reqd != -1:					
						temp = col.Node.find({"member_of":GSType._id, "tags":word, "created_by":user_reqd, "access_policy":"PUBLIC"}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
					else:
						temp = col.Node.find({"member_of":GSType._id, "tags":word, "access_policy":"PUBLIC"}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
					#temp_sorted = sort_names_by_similarity(temp, search_str_user)
					
					split_stem_match.append(temp)#_sorted)
					c += 1
				search_results_st['tags'] = sort_names_by_similarity(search_results_st['tags'], search_str_user)
				
				for j in split_stem_match:
					c = 0
					for k in j:
						if k._id not in all_ids:
							k = addType(k)
							search_results_st['tags'].append(k)
							all_ids.append(k['_id'])
							c += 1

		content_docs = []
		content_match_pairs = []
		sorted_content_match_pairs = []

		if (search_by_contents == 1):
			all_Reduced_documents = collection.Node.find({"required_for":"map_reduce_reduced"}, {"content_org":1, "_id":0, "orignal_doc_id":1})
			#print "cursor: ", all_Reduced_documents, all_Reduced_documents.count()
			
			for singleDoc in all_Reduced_documents:
				if singleDoc.orignal_doc_id not in all_ids:
					content = singleDoc.content_org
					print "Content: ", content, "\n"
				
					match_count = 0
					for word in search_str_stemmed:
						if word in content.keys():
							match_count += content[word]

					if match_count > 0:
						all_ids.append(singleDoc.orignal_doc_id)
						content_match_pairs.append({'doc_id':singleDoc.orignal_doc_id, 'matches':match_count})	
	
			match_counts = []
			for pair in content_match_pairs:	
				c = 0
				while ((c < len(match_counts)) and (pair['matches'] < match_counts[c])):
					c += 1
				match_counts.insert(c, pair['matches'])
				sorted_content_match_pairs.insert(c, pair)
				
			#sorted_content_match_pairs = OrderedDict(sorted(content_match_pairs.items(), key=lambda t: t[1]))
			print "sorted pairs: ", sorted_content_match_pairs

			for docId in sorted_content_match_pairs:
				doc = col.Node.find_one({"_id":docId['doc_id'], "access_policy":"PUBLIC"}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
				doc = addType(doc)
				print "type added  ", doc['created_by'], "value: ", User.objects.get(username=doc['created_by']).pk == 1
				if user_reqd != -1:
					if User.objects.get(username=doc['created_by']).pk == 1:
						search_results_st['content'].append(doc)
				else:
					search_results_st['content'].append(doc)

			#print "stemmed results: ", search_results_st

		search_results = json.dumps(search_results, cls=Encoder)
		print "final results: ", search_results
		memList = populate_list_of_members()
	
		return render(request, 'ndf/search_results.html', {'processed':1, 'search_results':search_results, "groupid":group_id, "authors":memList})


def results_search_group(request, group_id):

	group_ins = {}
	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
		group_ins = collection.Node.find_one({'_type': "Group","name": group_id})._id
		group_id = ObjectId(group_ins)
	else:
		pass
	group_id = ObjectId(group_id)
	print "group: ", group_id
	
	# DECLARE THE VARIABLES
	search_by_name = 0
	search_by_tags = 0
	search_by_contents = 0
	user = ""
	user_reqd = -1

#	try:
	if request.method == "GET":
		# PRINT THE VALUES TO SEE IF STEMMING, ARTICLE REMOVAL IS RIGHT
		print "all users: ", str(request.GET['users'])		
		user_reqd_name = str(request.GET['users'])
		if user_reqd_name != "all":
			user_reqd = int(User.objects.get(username = 'siddhant').pk)
 		
		search_str_user = str(request.GET['search_text'])
		print "\noriginal search string:", search_str_user, "\n"
		search_str_user = search_str_user.lower()

		search_str_noArticles = list(removeArticles(str(search_str_user)))
		print "\narticles removed:",search_str_noArticles,"\n"

		search_str_stemmed = list(stemWords(search_str_noArticles, search_str_user))
		print "\nwords stemmed:",search_str_stemmed,"\n\n\n"

		# -------------------------------------------------------
		print "Search string lowercase:", search_str_user

		# GET THE LIST OF CHECKBOXES TICKED AND SET CORR. FLAGS
		checked_fields = request.GET.getlist('search_fields')
		nam = "name"
	
		print "\n\nfields: ", checked_fields, "\n\n"	
		if (nam in checked_fields):
			print "by_name"
			search_by_name = 1

		nam = "tags"
		if (nam in checked_fields):
			print "by_tags"
			search_by_tags = 1
		
		nam = "contents"
		if (nam in checked_fields):
			print "by_contents"
			search_by_contents = 1

		#user = str(request.GET['author'])				# GET THE VALUE OF AUTHOR FROM THE FORM

		col = get_database()[Node.collection_name]			# COLLECTION NAME


		# FORMAT OF THE RESULTS RETURNED
		search_results_ex = {'name':[], 'tags':[], 'content':[], 'user':[]}
		search_results_st = {'name':[], 'tags':[], 'content':[], 'user':[]}
		search_results_li = {'name':[], 'tags':[], 'content':[], 'user':[]}
		
		# ALL SORTED SEARCH RESULTS
		search_results = {'exact':search_results_ex, 'stemmed':search_results_st, 'like':search_results_li}

		# STORES OBJECTID OF EVERY SEARCH RESULT TO CHECK FOR DUPLICATES
		all_ids = []

		# GET A CURSOR ON ALL THE GSYSTEM TYPES 
		all_GSystemTypes = col.Node.find({"_type":"GSystemType"}, {"_id":1})
		len1 = all_GSystemTypes.count()
		
		if (search_by_name == 1):					# IF 1, THEN SEARCH BY NAME
			all_GSystemTypes.rewind()
			count = 0

			for GSType in all_GSystemTypes:

				# EXACT MATCH OF SEARCH_USER_STR IN NAME OF GSYSTEMS OF ONE GSYSTEM TYPE
				if user_reqd != -1:				
					exact_match = col.Node.find({"member_of":GSType._id, "created_by":user_reqd, "access_policy":"PUBLIC", "group_set":group_id, "name":{"$regex":search_str_user, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
				else:
					exact_match = col.Node.find({"member_of":GSType._id, "access_policy":"PUBLIC", "group_set":group_id, "name":{"$regex":search_str_user, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})					

				# SORT THE NAMES ACCORDING TO THEIR SIMILARITY WITH THE SEARCH STRING
				exact_match = list(exact_match)				
				#exact_match = sort_names_by_similarity(exact_match, search_str_user)

				for j in exact_match:
					if j._id not in all_ids:
						j = addType(j)
						search_results_ex['name'].append(j)
						all_ids.append(j['_id'])
				search_results_ex['name'] = sort_names_by_similarity(search_results_ex['name'], search_str_user)
				
				# split stemmed match
				split_stem_match = []
				len_stemmed = len(search_str_stemmed)
				c = 0								# GEN. COUNTER 

				while c < len_stemmed:
					word = search_str_stemmed[c]
					if user_reqd != -1:
						temp = col.Node.find({"member_of":GSType._id, "group_set":group_id, "created_by":user_reqd, "access_policy":"PUBLIC", "name":{"$regex":word, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
					else:
						temp = col.Node.find({"member_of":GSType._id, "group_set":group_id, "access_policy":"PUBLIC", "name":{"$regex":word, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
					#temp_sorted = sort_names_by_similarity(temp, search_str_user)
					split_stem_match.append(temp)#temp_sorted)
					c += 1
				
				for j in split_stem_match:
					c = 0
					for k in j:
						if (k._id not in all_ids):
							k = addType(k)
							search_results_st['name'].append(k)
							all_ids.append(k['_id'])
							c += 1
				search_results_st['name'] = sort_names_by_similarity(search_results_st['name'], search_str_user)


		if (search_by_tags == 1):						# IF 1, THEN SEARCH BY TAGS

			all_GSystemTypes.rewind()
			count = 0

			for GSType in all_GSystemTypes:

				# EXACT MATCH OF SEARCH_USER_STR IN NAME OF GSYSTEMS OF ONE GSYSTEM TYPE
				if user_reqd != -1:				
					exact_match = col.Node.find({"member_of":GSType._id, "group_set":group_id, "created_by":user_reqd, "access_policy":"PUBLIC", "tags":search_str_user}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
				else:
					exact_match = col.Node.find({"member_of":GSType._id, "access_policy":"PUBLIC", "group_set":group_id,  "tags":search_str_user}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
				#exact_match = sort_names_by_similarity(exact_match, search_str_user)
				
				for j in exact_match:
					if j._id not in all_ids:
						j = addType(j)
						search_results_ex['tags'].append(j)
						all_ids.append(j['_id'])
				search_results_ex['tags'] = sort_names_by_similarity(search_results_ex['tags'], search_str_user)

				# split stemmed match
				split_stem_match = []
				c = 0						# GEN. COUNTER 
				len_stemmed = len(search_str_stemmed)

				while c < len_stemmed:
					word = search_str_stemmed[c]
					if user_reqd != -1:					
						temp = col.Node.find({"member_of":GSType._id, "group_set":group_id, "tags":word, "created_by":user_reqd, "access_policy":"PUBLIC"}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
					else:
						temp = col.Node.find({"member_of":GSType._id, "group_set":group_id, "access_policy":"PUBLIC", "tags":word}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
					#temp_sorted = sort_names_by_similarity(temp, search_str_user)
					
					split_stem_match.append(temp)#_sorted)
					c += 1
				search_results_st['tags'] = sort_names_by_similarity(search_results_st['tags'], search_str_user)
				
				for j in split_stem_match:
					c = 0
					for k in j:
						if k._id not in all_ids:
							k = addType(k)
							search_results_st['tags'].append(k)
							all_ids.append(k['_id'])
							c += 1

		content_docs = []
		content_match_pairs = []
		sorted_content_match_pairs = []

		if (search_by_contents == 1):
			all_Reduced_documents = collection.Node.find({"required_for":"map_reduce_reduced"}, {"content_org":1, "_id":0, "orignal_doc_id":1})
			#print "cursor: ", all_Reduced_documents, all_Reduced_documents.count()
			
			for singleDoc in all_Reduced_documents:
				if singleDoc.orignal_doc_id not in all_ids:
					content = singleDoc.content_org
					print "Content: ", content, "\n"
				
					match_count = 0
					for word in search_str_stemmed:
						if word in content.keys():
							match_count += content[word]

					if match_count > 0:
						all_ids.append(singleDoc.orignal_doc_id)
						content_match_pairs.append({'doc_id':singleDoc.orignal_doc_id, 'matches':match_count})	
	
			match_counts = []
			for pair in content_match_pairs:	
				c = 0
				while ((c < len(match_counts)) and (pair['matches'] < match_counts[c])):
					c += 1
				match_counts.insert(c, pair['matches'])
				sorted_content_match_pairs.insert(c, pair)
				
			#sorted_content_match_pairs = OrderedDict(sorted(content_match_pairs.items(), key=lambda t: t[1]))
			print "sorted pairs: ", sorted_content_match_pairs

			for docId in sorted_content_match_pairs:
				doc = col.Node.find_one({"_id":docId['doc_id'], "group_set":group_id, "access_policy":"PUBLIC"}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
				if (doc != None):
					doc = addType(doc)
					print "type added  ", doc['created_by'], "value: ", User.objects.get(username=doc['created_by']).pk == 1
					if user_reqd != -1:
						if User.objects.get(username=doc['created_by']).pk == 1:
							search_results_st['content'].append(doc)
					else:
						search_results_st['content'].append(doc)

			#print "stemmed results: ", search_results_st

		search_results = json.dumps(search_results, cls=Encoder)
		print "final results: ", search_results
		memList = populate_list_of_members()
	
		return render(request, 'ndf/search_results.html', {'processed':1, 'search_results':search_results, "groupid":group_id, "authors":memList})



def advanced_search(request, group_id):

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
		group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		if group_ins:
			group_id = str(group_ins._id)
		else:
	    		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    		if auth :
				group_id = str(auth._id)
	else:
		pass

	print "Group id is: ", group_id
	col = get_database()[Node.collection_name]
	temp = col.Node.find({"_type":"GSystemType"}, {"name":1, "_id":0})

	allGSystems = []
	for gs in temp:
		allGSystems.append(gs.name)

	allGroups = get_public_groups()
	print "groups: ", allGroups

	allUsers = populate_list_of_group_members(allGroups)
	print "members: ", allUsers
	#print allGSystems

	return render(request, 'ndf/advanced_search2.html', {"allGSystems":allGSystems, "groupid":group_id, "allGroups":allGroups, "allUsers":allUsers, "group_id":group_id})


def get_attributes(request, group_id):
	col = get_database()[Node.collection_name]
	attributes = []

	#print request.GET['GSystem']
	print "names: ", request.GET.get('GSystem',"")
	#print "testing !: ", request.GET['tex']
	list_of_keys = ['name', 'created_by', 'last_update', 'tags', 'content_org']
	
	#try:
	GSystem_names = request.GET['GSystem']
	GSystem_names = GSystem_names.split(',')
	print "name of GSystem", GSystem_names

	for GSystem_name in GSystem_names:
		print GSystem_name
		test_obj = col.Node.find_one({"_type":"GSystemType", "name":GSystem_name})
		#print test_obj.keys()
		for sg_key in list_of_keys:
			if sg_key in test_obj.keys():
				if sg_key not in attributes:
					attributes.append(sg_key)

		print "\n\nattr: ", attributes, "\n\n"
		temp = col.Node.one({"_type":"GSystemType", "name":GSystem_name})
		
		for attr in temp.attribute_type_set:
			attributes.append(attr.name)

	#except Exception:
	#	print "Exception occurred"
	#	pass
	
	print attributes
	return HttpResponse(json.dumps(attributes, cls=Encoder))


def user_name_to_id(userNames):
	allUsers = []
	for user in userNames:
		sg_id = User.objects.get(username=user).pk
		allUsers.append(sg_id)

	return allUsers


def group_name_to_id(groupNames):
	allGroups = []
	col = get_database()[Node.collection_name]

	for gr in groupNames:
		sg_gr = col.Node.one({"_type":"Group", "name":gr})
		allGroups.append(sg_gr._id)

	return allGroups


def advanced_search_results(request, group_id): 

	col = get_database()[Node.collection_name]

	# READ THE GET VALUES
	search_str_user = request.GET['search_text']
	search_groups = request.GET.getlist('Groups')
	search_users = request.GET.getlist('Users')
	GSystem_names = request.GET.getlist('GSystems')
	attr_name = request.GET.getlist('attribs')

	print "name of GSystems: ", GSystem_names
	print "name of Groups: ", search_groups
	print "name of Authors: ", search_users
	
	all_users = 0		
	if search_users != "all":
		all_users = user_name_to_id(search_users)
	else:
		temp1 = get_public_groups()
		temp2 = populate_list_of_group_members(temp1)
		all_users = user_name_to_id(temp2)
	
	if search_groups != "all":
		all_groups = group_name_to_id(search_groups)
	
	print "name of Authors: ", all_users
	print "name of Groups: ", all_groups

	search_results = []
	all_ids = []

	for at_name in attr_name:
		print "attr: ", at_name
		# CASE 1 -- SEARCH IN THE STRUCTURE OF THE GSYSTEM
		for GSystem_name in GSystem_names:
			GSystem_obj = col.Node.one({"_type":"GSystemType", "name":GSystem_name})
			print GSystem_obj

			if GSystem_obj.has_key(at_name):
				if all_users != 0:
					res = col.Node.find({"_type":"GSystem", "member_of":GSystem_obj._id, at_name:{"$regex":search_str_user, "$options":"i" }}, {"name":1, "created_by":1, "last_update":1, "member_of":1 })
				else:
					res = col.Node.find({"_type":"GSystem", "created_by":{"$in":all_users}, "member_of":GSystem_obj._id, at_name:{"$regex":search_str_user, "$options":"i" }}, {"name":1, "created_by":1, "last_update":1, "member_of":1 })	
				for obj in res:
					print obj.name
					if obj._id not in all_ids:
						#link_obj = collection.Node.one({"member_of":GSystem_obj._id, "required_for":"Links"}, {"link":1})
						link_obj = addType(obj)
						search_results.append({'name':obj.name, 'link':link_obj['link'], 'created_by':link_obj['created_by'], 'last_update':link_obj['last_update'], '_id':link_obj['_id']})
						#search_results.append({'name':obj.name, 'link':link_obj.link}) 	
						all_ids.append(obj._id)
			continue			

		# CASE 2 -- SEARCH THE GATTRIBUTES
		try:
			attr_id = col.Node.one({"_type":"AttributeType", "name":at_name}, {"_id":1})
			res = col.Node.find({"_type":"GAttribute", "attribute_type.$id":ObjectId(attr_id._id), "object_value":{"$regex":search_str_user, "$options":"i"}}, {"name":1, "object_value":1, "subject":1})
			for obj in res: 
				if all_users == 0:
					GSystem = col.Node.one({"_id":obj.subject}, {"name":1, "created_by":1, "last_update":1, "member_of":1 })
				else:
					GSystem = col.Node.one({"_id":obj.subject, "created_by":{"$in":all_users}}, {"name":1, "created_by":1, "last_update":1, "member_of":1 })

				if GSystem._id not in all_ids:
					# THE FOLLOWING CODE MAY BE WRONG IF THE RETURNED NODE IS A MEMBER OF MORE THAN ONE GSYSTEM_TYPE
					#link_obj = collection.Node.one({"member_of":GSystem.member_of[0], "required_for":"Links"}, {"link":1})
					link_obj = addType(GSystem)
					search_results.append({'name':GSystem.name, 'link':link_obj['link'], 'created_by':link_obj['created_by'], 'last_update':link_obj['last_update'], '_id':link_obj['_id']})
					all_ids.append(GSystem._id)
		except:
			continue

	search_results = json.dumps(search_results, cls=Encoder)
	return render(request, 'ndf/adv_search_results.html', {'groupid':group_id, 'search_results':search_results})


def get_public_groups():
	col = get_database()[Node.collection_name]	
	cur = col.Node.find({"_type":"Group", "group_type":"PUBLIC"}, {"name":1})
	allGroups = []
	for obj in cur:
		allGroups.append(obj.name)

	return allGroups


def addType(obj):
	print "received: ", obj.member_of[0]
	i = ObjectId(obj.member_of[0])
	links = collection.Node.find({"member_of":i, "required_for":"Links"}, {"link":1})
	obj2 = {}
	#print "links count", links.count(), "\n"

	for ob in links:
		obj2['_id'] = obj._id
		obj2['name'] = obj.name
		obj2['link'] = ob.link
		obj2['created_by'] = User.objects.get(pk=obj.created_by).username
		#print "lst update: ", type(obj.last_update)
		obj2['last_update'] = str(obj.last_update.date())
		#datetime.datetime.strptime(obj.last_update, "%Y-%m-%dT%H:%M:%S.%fZ").date()
		print "obj", obj2
	return obj2


def sort_names_by_similarity(exact_match, search_str_user):
	matches = []					# TO STORE A LIST OF SORTED MATCH PERCENTAGE
	final_list = []					# FINAL LIST OF SORTED OBJECTS

	print exact_match
	for obj in exact_match:
		#print obj
		match = difflib.SequenceMatcher(None, obj['name'], search_str_user)
		per_match = match.ratio()
		#print "sorting", obj['name'], ": ", per_match, "\n"

		if len(matches) == 0:
			matches.append(per_match)
			final_list.append(obj)
		else:
			c = 0
			while ((c < len(matches)) and (per_match < matches[c])):
				c += 1
			matches.insert(c, per_match)
			final_list.insert(c, obj)

	return final_list


def removeArticles(text):
	words = text.split()
	articles=['a', 'an', 'and', 'the', 'i', 'is', 'this', 'that', 'there', 'here', 'am', 'on', 'at', 'of']
	for w in articles:
		if w in words:
			words.remove(w)
	words = removeDuplicateWords(words)
	return words


def removeDuplicateWords(words):
	return list(OrderedDict.fromkeys(words))


def stemWords(words, search_str_user):
	stemmed = []
	l = len(words)
	c = 0	
	
	while (c < l):
		temp = stem(words[c])
		#if (temp != search_str_user):
		stemmed.append(temp)
		c+=1
	
	print stemmed
	return stemmed


def perform_map_reduce(request,group_id):
	#This function shall perform map reduce on all the objects which are present in the ToReduce() class Collection
	all_instances = list(collection.ToReduce.find({'required_for':'map_reduce_to_reduce'}))
	for particular_instance in all_instances:
		print particular_instance._id,'\n'
		particular_instance_id  = particular_instance.id_of_document_to_reduce
		#Now Pick up a node from the Node Collection class
		orignal_node = collection.Node.find_one({"_id":particular_instance_id})		
		map_reduce_node = collection.MyReduce.find_one({'required_for':'map_reduce_reduced','orignal_doc_id':particular_instance_id})
		if map_reduce_node:
			map_reduce_node.content_org = dict(map_reduce(orignal_node.content_org,mapper,reducer))
			map_reduce_node.save()
		else:
			z = collection.MyReduce()
			z.content_org = dict(map_reduce(orignal_node.content_org,mapper,reducer))
			z.orignal_doc_id = particular_instance_id
			z.required_for = u'map_reduce_reduced'
			z.save()
		#After performing MapReduce that particular instance should be removed from the ToReduce() class collection
		particular_instance.delete()		
	return HttpResponse("Map Reduce was performed successfully")
	

def remove_punctuation(s):
	if not isinstance(s,unicode):
			s = unicode(s)			
	translate_table = dict((ord(c),None) for c in string.punctuation)	
	return s.translate(translate_table)


def mapper(input_value):
	#Step1: Remove all the punctuation from the content
	#Step2: Remove unnecessay words from the content
	#Step3: Convert these words to lower case and stem these words
	
	#This map functions converts all the words to lower case and then stems these words
	input_value = remove_punctuation(input_value)
	input_value_l = removeArticles(input_value)
	l = []
	for i in input_value_l:
		l.append([stem(i.lower()),1])

	return l
	
def reducer(intermediate_key,intermediate_value_list):
	return (intermediate_key,sum(intermediate_value_list))

def map_reduce(x,mapper,reducer):
	intermediate = mapper(x)
	groups = {}
	for key,group in itertools.groupby(sorted(intermediate),lambda x:x[0]):
		groups[key] = list([y for x,y in group])
		
	reduced_list = [reducer(intermediate_key,groups[intermediate_key]) for intermediate_key in groups ]
	print reduced_list,'\n'
	return reduced_list

def populate_list_of_members():
	members = User.objects.all()
	memList = []
	for mem in members:
		memList.append(mem.username)	
	return memList


def populate_list_of_group_members(group_ids):
	col = get_database()[Node.collection_name]
	memList = []
	print group_ids

	try:
		for gr in group_ids:
			# THIS CODE WILL CAUSE PROBLEMS IF THERE ARE MANY GROUPS WITH THE SAME NAME
			print "sg_group: ", gr
			group_id = col.Node.find_one({"_type":"Group", "name":gr}, {"_id":1})
			print group_id
			author_list = col.Node.one({"_type":"Group", "_id":group_id._id}, {"author_set":1, "_id":0})

			for author in author_list.author_set:
				name_author = User.objects.get(pk=author).username
				if name_author not in memList:
					memList.append(name_author)
	except:
		pass

	print "members in group: ", memList
	return memList


def get_users(request, group_id):
	group_ids = request.GET['Groups']
	allUsers = populate_list_of_group_members([group_ids])
	return HttpResponse(json.dumps(allUsers, cls=Encoder))


def get_node_info(request, group_id, node_name):

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
		group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		if group_ins:
			group_id = str(group_ins._id)
		else:
	    		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    		if auth :
				group_id = str(auth._id)
	else:
		pass


	is_list = False
	col = get_database()[Node.collection_name]

	#print "Node name: ", node_name

	list_of_nodes = col.Node.find({"name":node_name}, {"_id":1})

	if list_of_nodes.count() > 1:
		list_of_nodes.rewind()
		is_list = True
		list_nodes = []

		for obj in list_of_nodes:
			list_nodes.append(obj._id)

		list_nodes = json.dumps(list_nodes, cls=Encoder)
		return render(request, 'ndf/node_details.html', {'is_list':1, 'list_nodes':list_nodes, 'all_fields':'', 'groupid':group_id})
	else:
		sg_node = col.Node.one({"name":node_name})
		#print "Node data: \n", sg_node
		GSTypes = sg_node.member_of

		#print "member of: ", GSTypes, "\n"
		attrs = []
		results = {}
		results['name'] = sg_node.name
		results['created_by'] = sg_node.created_by
		results['last_update'] = str(sg_node.last_update.date())

		for GSType in GSTypes:
			obj = col.Node.one({"_id":ObjectId(GSType)})

			for attr in obj.attribute_type_set:
				custom_attrs = col.Node.find({"_type":"GAttribute", "subject":ObjectId(sg_node._id), "attribute_type.$id":ObjectId(attr._id)}, {"name":1, "object_value":1})
				for sg_attr in custom_attrs:
					temp = sg_attr.name
					i1 = temp.index('--') + 3
					temp = temp[i1:]
					i1 = temp.index('--') - 1
					temp = temp[:i1]
					results[temp] = sg_attr.object_value

		results = json.dumps(results, cls=Encoder)
		return render(request, 'ndf/node_details.html', {'is_list':0, 'list_nodes':'', 'all_fields':results, 'groupid':group_id})



def get_node_info2(request, group_id, node_id):

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
		group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		if group_ins:
			group_id = str(group_ins._id)
		else:
	    		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    		if auth :
				group_id = str(auth._id)
	else:
		pass

	print "ID is: ", node_id
	col = get_database()[Node.collection_name]
	sg_node = col.Node.one({"_id":ObjectId(node_id)})
	GSTypes = sg_node.member_of

	attrs = []
	results = {}
	results['name'] = sg_node.name
	results['created_by'] = sg_node.created_by
	results['last_update'] = str(sg_node.last_update.date())

	for GSType in GSTypes:
		obj = col.Node.one({"_id":ObjectId(GSType)})

		for attr in obj.attribute_type_set:
			custom_attrs = col.Node.find({"_type":"GAttribute", "subject":ObjectId(sg_node._id), "attribute_type.$id":ObjectId(attr._id)}, {"name":1, "object_value":1})
			for sg_attr in custom_attrs:
				temp = sg_attr.name
				i1 = temp.index('--') + 3
				temp = temp[i1:]
				i1 = temp.index('--') - 1
				temp = temp[:i1]
				results[temp] = sg_attr.object_value

	results = json.dumps(results, cls=Encoder)
	return render(request, 'ndf/node_details.html', {'is_list':0, 'list_nodes':'', 'all_fields':results, 'groupid':group_id})
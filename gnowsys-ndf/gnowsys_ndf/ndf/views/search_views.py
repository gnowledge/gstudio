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

#		print "Checking USER:"

		#if (user != ""):
		#	user = User.objects.get(username = user).pk	# GET THE PK CORRESPONDING TO THE USERNAME IF IT EXISTS
		#else:
		#	user = "None"

		#print "USER:", user

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
					exact_match = col.Node.find({"member_of":GSType._id, "created_by":user_reqd, "name":{"$regex":search_str_user, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
				else:
					exact_match = col.Node.find({"member_of":GSType._id, "name":{"$regex":search_str_user, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})					

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
						temp = col.Node.find({"member_of":GSType._id, "created_by":user_reqd, "name":{"$regex":word, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
					else:
						temp = col.Node.find({"member_of":GSType._id, "name":{"$regex":word, "$options":"i"}}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
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
					exact_match = col.Node.find({"member_of":GSType._id, "created_by":user_reqd, "tags":search_str_user}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
				else:
					exact_match = col.Node.find({"member_of":GSType._id, "tags":search_str_user}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
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
						temp = col.Node.find({"member_of":GSType._id, "tags":word, "created_by":user_reqd}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
					else:
						temp = col.Node.find({"member_of":GSType._id, "tags":word}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
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
				doc = col.Node.find_one({"_id":docId['doc_id']}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1})
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
	

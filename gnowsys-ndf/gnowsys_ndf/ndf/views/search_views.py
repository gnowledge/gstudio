from django.shortcuts import render
from django.http import HttpResponse
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_execution_time,create_gattribute, create_grelation, get_group_name_id
from django.template import RequestContext
#from stemming.porter2 import stem

try:
        from collections import OrderedDict
except ImportError:
        # python 2.6 or earlier, use backport
        from ordereddict import OrderedDict

import json
import difflib
import string
import datetime
import itertools
import nltk
import multiprocessing as mp

from mongokit import paginator
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.models import *
my_doc_requirement = u'storing_orignal_doc'
reduced_doc_requirement = u'storing_reduced_doc'
to_reduce_doc_requirement = u'storing_to_be_reduced_doc'
indexed_word_list_requirement = u'storing_indexed_words'
KEYWORD_SEARCH = u'KEYWORD_SEARCH'
ADVANCED_SEARCH = u'ADVANCED_SEARCH'
RELATION_SEARCH = u'RELATION_SEARCH'
SEMANTIC_SEARCH = u'SEMANTIC_SEARCH'
POSSIBLE_SEARCH_TYPES = ["GSystem", "File"]

# CLASS FOR ENCODING INTO JSON - OBJECTID TO STRING CONVERSION
class Encoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, ObjectId):
			return str(obj)
		else:
			return obj


# DISPLAYS THE SEARCH PAGE - USEFUL ONLY IF COMING TO THE SEARCH PAGE FROM THE OUTSIDE
def search_page(request, group_id):
	# ins_objectid  = ObjectId()
	# if ins_objectid.is_valid(group_id) is False :
	# 	group_ins = node_collection.find_one({'_type': "Group","name": group_id})
	# 	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	# 	if group_ins:
	# 		group_id = str(group_ins._id)
	# 	else:
	#     		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	#     		if auth :
	# 			group_id = str(auth._id)
	# else:
	# 	pass
	try:
		group_id = ObjectId(group_id)
	except:
		group_name, group_id = get_group_name_id(group_id)



	context_to_return = getRenderableContext(group_id)
	return render(request, 'ndf/search_page.html', context_to_return)


# FUNCTION THAT RETURNS A MINIMUM COMMON CONTEXT THAT ALL SEARCH RESULTS RETURN
def getRenderableContext(group_id):
	temp = node_collection.find({"_type":"GSystemType"}, {"name":1, "_id":0})
        ins_objectid = ObjectId()
	allGSystems = []
        allGroups=[]
	for gs in temp:
		allGSystems.append(gs.name)

	#allGroups = get_public_groups()								# LIST OF ALL PUBLIC GROUPS
  
        if ins_objectid.is_valid(group_id) is False :
                group_ins = node_collection.find_one({'_type': "Group","name": group_id})
                auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
                if group_ins:
                        group_id = str(group_ins._id)
                else:
                        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
                        if auth :
                                      group_id = str(auth._id)
                                      group_ins=auth
	else:
                group_ins = node_collection.find_one({'_type': "Group", "_id": ObjectId(group_id)})     
                
        if not group_ins:
                
                group_ins = node_collection.find_one({'_type': "Author", "_id": ObjectId(group_id)})        
        allGroups.append(group_ins.name)
	allUsers = populate_list_of_group_members(allGroups)		# LIST OF ALL USERS IN PUBLIC GROUPS
	memList = populate_list_of_members()						# LIST OF ALL USERS
        
	return {"allGSystems":allGSystems, "groupid":group_id, "allGroups":allGroups, "authors":memList, "allUsers":allUsers, "group_id":group_id}
	

# VIEW FOR KEYWORD SEARCH
def search_query(request, group_id):
	col = get_database()[Node.collection_name]

	# SCRIPT FOR CONVERTING GROUP NAME RECEIVED TO OBJECTID 
	# ins_objectid  = ObjectId()
	# if ins_objectid.is_valid(group_id) is False :
	# 	group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
	# 	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	# 	if group_ins:
	# 		group_id = str(group_ins._id)
	# 	else:
	#     		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	#     		if auth :
	# 			group_id = str(auth._id)
	# else:
	# 	pass

	try:
	    group_id = ObjectId(group_id)
	except:
	    group_name, group_id = get_group_name_id(group_id)

	memList = populate_list_of_members()						# memList holds the list of all authors 
	return render(request, 'ndf/search_home.html', {"groupid":group_id, "authors":memList}, context_instance=RequestContext(request))


# View for returning the search results according to group search
# def search_query_group(request, group_id):

# 	# SCRIPT FOR CONVERTING GROUP NAME RECEIVED TO OBJECTID 
# 	ins_objectid  = ObjectId()
# 	if ins_objectid.is_valid(group_id) is False :
# 		group_ins = node_collection.find_one({'_type': "Group","name": group_id})
# 		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
# 		if group_ins:
# 			group_id = str(group_ins._id)
# 		else:
# 	    		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
# 	    		if auth :
# 				group_id = str(auth._id)
# 	else:
# 		pass

# 	# CHANGE THIS TO GROUP SPECIFIC MEMBERS
# 	memList = populate_list_of_members()						# memList holds the list of all authors
# 	return render(request, 'ndf/search_home.html', {"groupid":group_id, "authors":memList}, context_instance=RequestContext(request))


@get_execution_time
def results_search(request, group_id, page_no=1, return_only_dict = None):
	"""
	This view returns the results for global search on all GSystems by name, tags and contents.
	Only publicly accessible GSystems are returned in results.
	"""
	
	userid = request.user.id
	# print "\n------\n", request.GET

	# ins_objectid  = ObjectId()
	# if ins_objectid.is_valid(group_id) is False :
	# 	group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
	# 	if group_ins:
	# 		group_id = str(group_ins._id)
	# 	else: 
	# 		auth = node_collection.one({'_type': 'Author', 'created_by': unicode(userid) })
 #    		if auth :
	# 			group_id = str(auth._id)
	try:
		group_id = ObjectId(group_id)
	except:group_name, group_id = get_group_name_id(group_id)
	

	# INTIALISE THE FLAGS FOR SEARCHING BY NAME / TAGS / CONTENTS
	user = ""		# stores username
	user_reqd = -1 	# user_reqd = -1 => search all users else user_reqd = pk of the user in user table

	# GET THE LIST OF CHECKBOXES TICKED AND SET CORR. FLAGS
	checked_fields = request.GET.getlist('search_fields')
	if checked_fields:
		search_by_name = True if ("name" in checked_fields) else False
		search_by_tags = True if ("tags" in checked_fields) else False
		search_by_contents = True if ("contents" in checked_fields) else False
	else:
		search_by_name = search_by_tags = search_by_contents = True

	# FORMAT OF THE RESULTS TO BE RETURNED
	search_results_ex = {'name': [], 'tags': [], 'content': []}
	search_results_st = {'name': [], 'tags': [], 'content': []}
	# search_results_li = {'name':[], 'tags':[], 'content':[], 'user':[]}

	# ALL SORTED SEARCH RESULTS
	search_results = {'exact': search_results_ex, 'stemmed': search_results_st}

	# STORES OBJECTID OF EVERY SEARCH RESULT TO CHECK FOR DUPLICATES
	all_ids = []
	
        if request.method == "GET":
			try:
				user_reqd_name = str(request.GET['users'])
			except Exception:
				# IF USERNAME IS NOT RECEIVED OR ANY INCORRECT USERNAME IS RECEIVED SEARCH ALL USERS
				user_reqd_name = "all" 

			# CONVERT USERNAME TO INTEGER
			if user_reqd_name != "all": 
				#Query writtent o avoid the error due to User.Object 
				auth = node_collection.one({'_type': 'Author', 'name': user_reqd_name})
				if auth: 
					user_reqd = int(auth.created_by)
	 		
			search_str_user = str(request.GET['search_text']).strip()  # REMOVE LEADING / TRAILING SPACES
			search_str_user = search_str_user.lower()  # CONVERT TO LOWERCASE
			search_str_noArticles = list(removeArticles(str(search_str_user)))  # REMOVES ARTICLES
			search_str_stemmed = list(stemWords(search_str_noArticles, search_str_user))  # STEMS THE WORDS

			#Check if the user is the super User
			Access_policy=""
			if  request.user.is_superuser:
			    Access_policy=["PUBLIC","PRIVATE"]
			else:
			    Access_policy=["PUBLIC"]    
			# GET A CURSOR ON ALL THE GSYSTEM TYPES 
			all_GSystemTypes = node_collection.find({"_type":"GSystemType"}, {"_id":1})
			
			#public_groups = get_public_groups()					# GET LIST OF PUBLIC GROUPS
			#public_groups = group_name_to_id(public_groups)		# CONVERT GROUP NAMES TO OBJECTIDS

			if (search_by_name == True):						# IF TRUE, THEN SEARCH BY NAME
				all_GSystemTypes.rewind()
				count = 0

			if (search_by_name == True):						# IF TRUE, THEN SEARCH BY NAME
				all_GSystemTypes.rewind()							# amn Corrected

				"""
				Following lines search for all GSystemTypes and then all GSystems in those GSystem types created by the selected user
				of public access policy in case insensitive regex match. If no user is specified, then it searches for GSystems created
				by any user
				"""
                                 
				# Search in all GSystem types
				all_list = [ each_gst._id for each_gst in all_GSystemTypes ]

				# EXACT MATCH OF SEARCH_USER_STR IN NAME OF GSYSTEMS OF ONE GSYSTEM TYPE
                # print "group id", group_id
				
				if user_reqd != -1:

					exact_match = node_collection.find({'$and':[
									   {"member_of":{'$in':all_list}},	    	
									   {"created_by":user_reqd},
									   {"group_set":ObjectId(group_id)},
									   {'$or':[{"access_policy":{"$in":Access_policy}},{'created_by':request.user.id}]},
									   {"name":search_str_user}]},
					        {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "group_set":1, "url":1}).sort('last_update',-1)
				else:
				  exact_match = node_collection.find({'$and':[
									    {"member_of":{'$in':all_list}},		
									    {'$or':[{"access_policy":{"$in":Access_policy}},{'created_by':request.user.id}]},
									    {"group_set":ObjectId(group_id)},
									    {"name":{"$regex":search_str_user,"$options":"i"}}]},
					        {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "group_set":1, "url":1}).sort('last_update',-1)
                                                
                                # SORT THE NAMES ACCORDING TO THEIR SIMILARITY WITH THE SEARCH STRING
                                #exact_match.rewind()
                                
				exact_match = list(exact_match)				

				"""
				For each matching GSystem, see if the GSystem has already been added to the list of ids and add if not added.
				result is added only if belongs to the list of public groups
				"""
				#temp. variables which stores the lookup for append method
                                all_ids_append_temp=all_ids.append
                                search_results_ex_name_append_temp=search_results_ex['name'].append
				for j in exact_match: 
					j.name=(j.name).replace('"',"'") 
					if j._id not in all_ids:
                                        	grps = j.group_set 
                                        	#for gr in public_groups: 
                                        	#	if gr in grps: 
                                        	j = addType(j) 
                                        	search_results_ex_name_append_temp(j) 
                                        	all_ids_append_temp(j['_id'])
                                                        
				# SORTS THE SEARCH RESULTS BY SIMILARITY WITH THE SEARCH QUERY
				#search_results_ex['name'] = sort_names_by_similarity(search_results_ex['name'], search_str_user)
				# split stemmed match
				split_stem_match = []					# will hold all the split stem match results
				len_stemmed = len(search_str_stemmed)	
				c = 0							# GEN. COUNTER 
                                #a temp. variable which stores the lookup for append method
                                split_stem_match_append_temp=split_stem_match.append
				while c < len_stemmed:	
						word = search_str_stemmed[c]
						temp=""
						if user_reqd != -1:	# user_reqd = -1  =>  search all users, else user_reqd = pk of user
							temp = node_collection.find({'$and':[
									   {"member_of":{'$in':all_list}},	    	 										   {"created_by":user_reqd},
									   {"group_set":ObjectId(group_id)},
									   {'$or':[{"access_policy":{"$in":Access_policy}},{'created_by':request.user.id}]},	
									   {"name":{"$regex":word, "$options":"i"}}]},
						{"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "group_set":1, "url":1}).sort('last_update',-1)
						else:		
						  			# search all users in created by
						  temp = node_collection.find({'$and':[
									   {"member_of":{'$in':all_list}},
									   {"group_set":ObjectId(group_id)},
									   {'$or':[{"access_policy":{"$in":Access_policy}},{'created_by':request.user.id}]},
									    {"name":{"$regex":str(word), "$options":"i"}}] },
						{"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "group_set":1, "url":1}).sort('last_update',-1)
                                                split_stem_match_append_temp(temp)
						c += 1
					
				"""
				For each matching GSystem, see if the GSystem has already been returned in search results and add if not 					already added.
				Result is added only if belongs to the list of public groups and has public access policy
				"""
                                #a temp. variable which stores the lookup for append method
				search_results_st_name_append=search_results_st['name'].append
				for j in split_stem_match:
				                c = 0
                                                for k in j:
                                                        k.name=(k.name).replace('"',"'")
							if (k._id not in all_ids):# check if this GSYstem has already been added to search 											    results
								#grps = k.group_set		
								# group_set holds all the groups that the current GSystem is published in
								#for gr in public_groups:			
								# for each public group
								#	if gr in grps:			
								# check that the GSystem should belong to at least one public group
                                                                k = addType(k) # adds the link and datetime to the 
                                                                
                                                                search_results_st_name_append(k)
                                                                all_ids_append_temp(k['_id'])#append to the list of all ids of GSYstems in the 												results
                                                                c += 1
                                # SORTS THE SEARCH RESULTS BY SIMILARITY WITH THE SEARCH QUERY	

                                #search_results_st['name'] = sort_names_by_similarity(search_results_st['name'], search_str_user)
				

			if (search_by_tags == True):						# IF True, THEN SEARCH BY TAGS
				all_GSystemTypes.rewind()						# Rewinds the cursor to first result
				count = 0
				
				# EXACT MATCH OF SEARCH_USER_STR IN NAME OF GSYSTEMS OF ONE GSYSTEM TYPE
				if user_reqd != -1:				
						exact_match = node_collection.find({'$and':[
									   {"member_of":{'$in':all_list}},	    		
									   {"created_by":user_reqd},
									   {"group_set":ObjectId(group_id)},
									   {'$or':[{"access_policy":{"$in":Access_policy}},{'created_by':request.user.id}]},
									   {"tags":search_str_user}]},
					        {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "group_set":1, "url":1}).sort('last_update',-1)
				else:
						exact_match = node_collection.find({'$and':[
										{"member_of":{'$in':all_list}},	    											{'$or':[{"access_policy":{"$in":Access_policy}},{'created_by':request.user.id}]},
									   {"group_set":ObjectId(group_id)},
									   {"tags":search_str_user}]},
						{"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "group_set":1, "url":1}).sort('last_update',-1)
                                # temp. variables which stores the lookup for append method
                                all_ids_append_temp=all_ids.append
                                search_results_ex_tags_append_temp=search_results_ex['tags'].append
				for j in exact_match:
						j.name=(j.name).replace('"',"'")
						if j._id not in all_ids:
							
							#grps = j.group_set
							#for gr in public_groups:
							#	if gr in grps:
                                                        j = addType(j)
                                                        search_results_ex_tags_append_temp(j)
                                                        all_ids_append_temp(j['_id'])
                                                        

				#search_results_ex['tags'] = sort_names_by_similarity(search_results_ex['tags'], search_str_user)

				# split stemmed match
				split_stem_match = []
				c = 0						# GEN. COUNTER 
				len_stemmed = len(search_str_stemmed)
				#a temp. variable which stores the lookup for append method
                                split_stem_match_append_temp=split_stem_match.append
				while c < len_stemmed:
						word = search_str_stemmed[c]
						if user_reqd != -1:					
							temp = node_collection.find({'$and':[{"tags":word},
									     {"member_of":{'$in':all_list}},	    		 	
									     {"created_by":user_reqd},
									     {"group_set":ObjectId(group_id)},
									     {'$or':[{"access_policy":{"$in":Access_policy}},{'created_by':request.user.id}]}]}, 
						{"name":1, "_id":1, "member_of":1, "created_by":1, "group_set":1, "last_update":1, "url":1}).sort('last_update',-1)
						else:
							temp = node_collection.find({'$and':[{"tags":word},
									    {"member_of":{'$in':all_list}},	    			
									    {'$or':[{"access_policy":{"$in":Access_policy}},{'created_by':request.user.id}]},
									    {"group_set":ObjectId(group_id)}]},
						{"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "group_set":1, "url":1}).sort('last_update',-1)
						
						split_stem_match_append_temp(temp)
						c += 1
				#search_results_st['tags'] = sort_names_by_similarity(search_results_st['tags'], search_str_user)
					
				"""
				For each matching GSystem, see if the GSystem has already been returned in search results and add if not already added.
				Result is added only if belongs to the list of public groups and has public access policy
				"""
				#a temp. variable which stores the lookup for append method
				search_results_st_tags_append=search_results_st['tags'].append
				for j in split_stem_match:
						c = 0
						for k in j:
                                                        k.name=(k.name).replace('"',"'")
							if k._id not in all_ids:
								#grps = k.group_set
								#for gr in public_groups:
								#	if gr in grps:
                                                                k = addType(k)
                                                                search_results_st_tags_append(k)
                                                                all_ids_append_temp(k['_id'])
                                                                c += 1
                                                                
			"""
			The following lines implement search over the contents of all GSystems.
			It uses the Map Reduce algorithm to keep track of which GSystems contain which words and how many times.
			The more the count of matches, the more relevant the search result is for the user.
			"""
			#print "stemmed query: ", search_str_stemmed			
			content_docs = []
			content_match_pairs = []	# STORES A DICTIONARY OF MATCHING DOCUMENTS AND NO_OF_WORDS THAT MATCH SEARCH QUERY
			sorted_content_match_pairs = []				# STORES THE ABOVE DICTIONARY IN A SORTED MANNER
                        #a temp. variable which stores the lookup for append method
			content_match_pairs_append_temp=content_match_pairs.append
			if (search_by_contents == True):
				# FETCH ALL THE GSYSTEMS THAT HAVE BEEN MAP REDUCED.
				all_Reduced_documents = node_collection.find({"required_for": reduced_doc_requirement}, {"content": 1, "_id": 0, "orignal_id": 1})
				# ABOVE LINE DOES NOT RETURN ALL GSYSTEMS. IT RETURNS OBJECTS OF "ToReduceDocs" class. 

				for singleDoc in all_Reduced_documents:
					if singleDoc.orignal_id not in all_ids:	# IF THE GSYSTEM HAS NOT ALREADY BEEN ADDED TO SEARCH RESULTS
						content = singleDoc.content
						match_count = 0	# KEEPS A CUMMULATIVE COUNT OF MATCHES OF ALL SEARCH QUERY WORDS IN THE 									CURRENT GSYSTEM CONTENTS
						for word in search_str_stemmed:
							if word in content.keys():# IF THE WORD EXISTS IN THE CURRENT DOCUMENT
								match_count += content[word]	# ADD IT TO THE MATCHES COUNT
						if match_count > 0:
							all_ids.append(singleDoc.orignal_id)
							content_match_pairs_append_temp({'doc_id':singleDoc.orignal_id, 'matches':match_count})	
		
				match_counts = []			# KEEPS A SORTED LIST OF COUNT OF MATCHES IN RESULT DOCUMENTS
				for pair in content_match_pairs:	
					c = 0
					while ((c < len(match_counts)) and (pair['matches'] < match_counts[c])):# INSERT IN SORTED ORDER BY 															INCREASING ORDER
						c += 1
					match_counts.insert(c, pair['matches'])
					sorted_content_match_pairs.insert(c, pair)	# SORTED INSERT (INCREASING ORDER)
                                #a temp. variable which stores the lookup for append method
				search_results_st_content_append_temp=search_results_st['content'].append
				for docId in sorted_content_match_pairs:
					doc = node_collection.find_one({"_id":docId['doc_id'], "access_policy":Access_policy}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "group_set":1, "url":1})
                                        try:
                                                grps = doc.group_set
					
                                                """
                                                For each matching GSystem, see if the GSystem has already been returned in search results and add if not already added.
                                                Result is added only if belongs to the list of public groups and has public access policy
                                                """
                                                #for gr in public_groups:
                                                #	if gr in grps:
                                                doc = addType(doc)
                                                #matching for current group Only
                                                if ObjectId(group_id) in grps:
                                                        if user_reqd != -1:
								if User.objects.get(username=doc['created_by']).pk == user_reqd:
									search_results_st_content_append_temp(doc)
                                                        else:
								search_results_st_content_append_temp(doc)
                                        except:
                                                pass
			#search_results = json.dumps(search_results, cls=Encoder)
                        memList = populate_list_of_members()
	
	search_results = json.dumps(search_results, cls=Encoder)



	# print "search_results:", search_results

	GST_FILE = node_collection.one({'_type':'GSystemType', 'name': 'File'})
	GST_PAGE = node_collection.one({'_type':'GSystemType', 'name': 'Page'})
	GST_THREAD = node_collection.one({'_type':'GSystemType', 'name': 'Twist'})
	GST_REPLY = node_collection.one({'_type':'GSystemType', 'name': 'Reply'})
	json_results = json.loads(search_results)
	stemmed_values = json_results["stemmed"]["name"]
	exact_values = json_results["exact"]["name"]
	stemmed_results = []
	
	for each in stemmed_values:
		stemmed_results.append(ObjectId(each["_id"]))
	
	for each in exact_values:
		stemmed_results.append(ObjectId(each["_id"]))
	getcurr = node_collection.find({'$and':[{'_id':{'$in' : stemmed_results }},{'member_of':{'$nin':[GST_THREAD._id,GST_REPLY._id]}}]}).sort("last_update", -1)

	# from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP
	# search_pagination_curr = paginator.Paginator(getcurr, page_no, GSTUDIO_NO_OF_OBJS_PP)
	
	if return_only_dict:
		return search_results
	else:
		context_to_return = getRenderableContext(group_id)			# RETURNS BASIC CONTEXT
		context_to_return['search_results'] = search_results 		# ADD SEARCH RESULTS TO CONTEXT
		context_to_return['processed'] = "1" 							
		context_to_return['search_type'] = KEYWORD_SEARCH			# TYPE OF SEARCH IS KEYWORD SEARCH
		context_to_return['search_curr'] = getcurr			# TYPE OF SEARCH IS KEYWORD SEARCH
		# context_to_return['search_pagination_curr'] = search_pagination_curr			# TYPE OF SEARCH IS KEYWORD SEARCH

		return render(request, 'ndf/search_page.html', context_to_return)


# KEYWORD SEARCH FOR A SPECIFIC GROUP
def results_search_group(request, group_id):
	"""
	This view returns the results for search on all GSystems by name, tags and contents in the group currently chosen.
	Only publicly accessible GSystems are returned in results.
	"""

	group_ins = {}
	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
		group_ins = node_collection.find_one({'_type': "Group", "name": group_id})._id
		group_id = ObjectId(group_ins)
	else:
		pass
	group_id = ObjectId(group_id)
	
	# DECLARE THE VARIABLES
	search_by_name = 0
	search_by_tags = 0
	search_by_contents = 0
	user = ""
	user_reqd = -1
        
	try:
		if request.method == "GET":
			try:
				user_reqd_name = str(request.GET['users'])
			except Exception:
				user_reqd_name = "all"

			if user_reqd_name != "all":
				user_reqd = int(User.objects.get(username = user_reqd_name).pk)
		 		
			search_str_user = str(request.GET['search_text']).strip()
			##print "\noriginal search string:", search_str_user, "\n"
			search_str_user = search_str_user.lower()

			search_str_noArticles = list(removeArticles(str(search_str_user)))
			##print "\narticles removed:",search_str_noArticles,"\n"

			search_str_stemmed = list(stemWords(search_str_noArticles, search_str_user))
			##print "\nwords stemmed:",search_str_stemmed,"\n\n\n"

			# -------------------------------------------------------
			##print "Search string lowercase:", search_str_user

			# GET THE LIST OF CHECKBOXES TICKED AND SET CORR. FLAGS
			checked_fields = request.GET.getlist('search_fields')
			nam = "name"
		
			##print "\n\nfields: ", checked_fields, "\n\n"	
			if (nam in checked_fields):
				##print "by_name"
				search_by_name = 1

			nam = "tags"
			if (nam in checked_fields):
				##print "by_tags"
				search_by_tags = 1
			
			nam = "contents"
			if (nam in checked_fields):
				##print "by_contents"
				search_by_contents = 1

			#user = str(request.GET['author'])				# GET THE VALUE OF AUTHOR FROM THE FORM

			# FORMAT OF THE RESULTS RETURNED
			search_results_ex = {'name':[], 'tags':[], 'content':[], 'user':[]}
			search_results_st = {'name':[], 'tags':[], 'content':[], 'user':[]}
			search_results_li = {'name':[], 'tags':[], 'content':[], 'user':[]}
			
			# ALL SORTED SEARCH RESULTS
			search_results = {'exact':search_results_ex, 'stemmed':search_results_st, 'like':search_results_li}

			# STORES OBJECTID OF EVERY SEARCH RESULT TO CHECK FOR DUPLICATES
			all_ids = []

			# GET A CURSOR ON ALL THE GSYSTEM TYPES 
			all_GSystemTypes = node_collection.find({"_type":"GSystemType"}, {"_id":1})
			len1 = all_GSystemTypes.count()
			
			if (search_by_name == 1):					# IF 1, THEN SEARCH BY NAME
				all_GSystemTypes.rewind()
				count = 0

				for GSType in all_GSystemTypes:

					# EXACT MATCH OF SEARCH_USER_STR IN NAME OF GSYSTEMS OF ONE GSYSTEM TYPE
					if user_reqd != -1:				
						exact_match = node_collection.find({'$and':[{"member_of":GSType._id},{"created_by":user_reqd}, {"access_policy":Access_policy},{"group_set":group_id},{"name":{"$regex":search_str_user, "$options":"i"}}]}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "url":1})
					else:
						exact_match = node_collection.find({'$and':[{"member_of":GSType._id},{ "access_policy":Access_policy}, {"group_set":group_id}, {"name":{"$regex":search_str_user, "$options":"i"}}]}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "url":1})					

					# SORT THE NAMES ACCORDING TO THEIR SIMILARITY WITH THE SEARCH STRING
					exact_match = list(exact_match)				
					#exact_match = sort_names_by_similarity(exact_match, search_str_user)

					for j in exact_match:
                                                j.name=(j.name).replace('"',"'")
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
							temp = node_collection.find({'$and':[{"member_of":GSType._id},{ "group_set":group_id},{ "created_by":user_reqd},{ "access_policy":Access_policy},{ "name":{"$regex":word, "$options":"i"}}]}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "url":1})
						else:
							temp = node_collection.find({'$and':[{"member_of":GSType._id},{ "group_set":group_id}, {"access_policy":Access_policy}, {"name":{"$regex":word, "$options":"i"}}]}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "url":1})
						#temp_sorted = sort_names_by_similarity(temp, search_str_user)
						split_stem_match.append(temp)#temp_sorted)
						c += 1
					
					for j in split_stem_match:
						c = 0
						for k in j:
                                                        k.name=(k.name).replace('"',"'")
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
						exact_match = node_collection.find({"member_of":GSType._id, "group_set":group_id, "created_by":user_reqd, "access_policy":Access_policy, "tags":search_str_user}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "url":1})
					else:
						exact_match = node_collection.find({"member_of":GSType._id, "access_policy":Access_policy, "group_set":group_id,  "tags":search_str_user}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "url":1})
					#exact_match = sort_names_by_similarity(exact_match, search_str_user)
					
					for j in exact_match:
                                                j.name=(j.name).replace('"',"'")
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
							temp = node_collection.find({"member_of":GSType._id, "group_set":group_id, "tags":word, "created_by":user_reqd, "access_policy":Access_policy}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "url":1})
						else:
							temp = node_collection.find({"member_of":GSType._id, "group_set":group_id, "access_policy":Access_policy, "tags":word}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "url":1})
						#temp_sorted = sort_names_by_similarity(temp, search_str_user)
						
						split_stem_match.append(temp)#_sorted)
						c += 1
					search_results_st['tags'] = sort_names_by_similarity(search_results_st['tags'], search_str_user)
					
					for j in split_stem_match:
						c = 0
						for k in j:
                                                        k.name=(k.name).replace('"',"'")
							if k._id not in all_ids:
								k = addType(k)
								search_results_st['tags'].append(k)
								all_ids.append(k['_id'])
								c += 1

			content_docs = []
			content_match_pairs = []
			sorted_content_match_pairs = []

			if (search_by_contents == 1):
				all_Reduced_documents = node_collection.find({"required_for": reduced_doc_requirement}, {"content": 1, "_id": 0, "orignal_id": 1})
				##print "cursor: ", all_Reduced_documents, all_Reduced_documents.count()
				
				for singleDoc in all_Reduced_documents:
					if singleDoc.orignal_id not in all_ids:
						content = singleDoc.content
						#print "Content: ", content, "\n\n"
					
						match_count = 0
						for word in search_str_stemmed:
							if word in content.keys():
								match_count += content[word]

						if match_count > 0:
							all_ids.append(singleDoc.orignal_id)
							content_match_pairs.append({'doc_id':singleDoc.orignal_id, 'matches':match_count})	
		
				match_counts = []
				for pair in content_match_pairs:	
					c = 0
					while ((c < len(match_counts)) and (pair['matches'] < match_counts[c])):
						c += 1
					match_counts.insert(c, pair['matches'])
					sorted_content_match_pairs.insert(c, pair)
					
				#sorted_content_match_pairs = OrderedDict(sorted(content_match_pairs.items(), key=lambda t: t[1]))
				#print "sorted pairs: ", sorted_content_match_pairs

				for docId in sorted_content_match_pairs:
					doc = node_collection.find_one({"_id":docId['doc_id'], "group_set":group_id, "access_policy":Access_policy}, {"name":1, "_id":1, "member_of":1, "created_by":1, "last_update":1, "url":1})
					if (doc != None):
						doc = addType(doc)
						#print "type added  ", doc['created_by'], "value: ", User.objects.get(username=doc['created_by']).pk == 1
						if user_reqd != -1:
							if User.objects.get(username=doc['created_by']).pk == user_reqd:
								search_results_st['content'].append(doc)
						else:
							search_results_st['content'].append(doc)

				##print "stemmed results: ", search_results_st

			#search_results = json.dumps(search_results, cls=Encoder)
			#print "final results: ", search_results
			#memList = populate_list_of_members()
	except Exception:
		pass

	search_results = json.dumps(search_results, cls=Encoder)
	context_to_return = getRenderableContext(group_id)
	context_to_return['search_results'] = search_results
	context_to_return['processed'] = 1
	context_to_return['search_type'] = KEYWORD_SEARCH

	return render(request, 'ndf/search_page.html', context_to_return)



# def advanced_search(request, group_id):

# 	ins_objectid  = ObjectId()
# 	if ins_objectid.is_valid(group_id) is False :
# 		group_ins = node_collection.find_one({'_type': "Group","name": group_id})
# 		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
# 		if group_ins:
# 			group_id = str(group_ins._id)
# 		else:
# 	    		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
# 	    		if auth :
# 				group_id = str(auth._id)
# 	else:
# 		pass

# 	#print "Group id is: ", group_id
# 	temp = node_collection.find({"_type":"GSystemType"}, {"name":1, "_id":0})

# 	allGSystems = []
# 	for gs in temp:
# 		allGSystems.append(gs.name)

# 	allGroups = get_public_groups()
# 	#print "groups: ", allGroups

# 	allUsers = populate_list_of_group_members(allGroups)
# 	#print "members: ", allUsers
# 	##print allGSystems

# 	return render(request, 'ndf/advanced_search2.html', {"allGSystems":allGSystems, "groupid":group_id, "allGroups":allGroups, "allUsers":allUsers, "group_id":group_id})



def get_attributes(request, group_id):
	attributes = []

	##print request.GET['GSystem']
	#print "names: ", request.GET.get('GSystem',"")
	##print "testing !: ", request.GET['tex']
	list_of_keys = ['name', 'last_update', 'tags']
	
	#try:
	GSystem_names = request.GET['GSystem']
	GSystem_names = GSystem_names.split(',')
	#print "name of GSystem", GSystem_names

	for GSystem_name in GSystem_names:
		#print GSystem_name
		test_obj = node_collection.find_one({"_type":"GSystemType", "name":GSystem_name})
		##print test_obj.keys()
		for sg_key in list_of_keys:
			if sg_key in test_obj.keys():
				if sg_key not in attributes:
					attributes.append(sg_key)

		#print "\n\nattr: ", attributes, "\n\n"
		temp = node_collection.one({"_type":"GSystemType", "name":GSystem_name})
		
		for attr in temp.attribute_type_set:
			attributes.append(attr.name)

	#except Exception:
	#	#print "Exception occurred"
	#	pass
	
	#print attributes
	return HttpResponse(json.dumps(attributes, cls=Encoder))


def user_name_to_id(userNames):
	allUsers = []
	for user in userNames:
		sg_id = User.objects.get(username=user).pk
		allUsers.append(sg_id)

	return allUsers


def group_name_to_id(groupNames):
	allGroups = []

	for gr in groupNames:
		sg_gr = node_collection.find({"_type":"Group", "name":gr})
		for each in sg_gr:
                        allGroups.append(each._id)

	return allGroups


def advanced_search_results(request, group_id): 

	# READ THE GET VALUES
	search_str_user = str(request.GET['search_text']).strip()
	search_groups = request.GET.getlist('Groups')
	search_users = request.GET.getlist('Users')
	GSystem_names = request.GET.getlist('GSystems')
	attr_name = request.GET.getlist('attribs')
	all_groups = []
	all_users = []

	split_query = search_str_user.split()
	#print "name of GSystems: ", GSystem_names
	#print "name of Groups: ", search_groups
	#print "name of Authors: ", search_users
	
	all_users = 0		
	if search_users[0] != "all":
		all_users = user_name_to_id(search_users)
	else:
		temp1 = get_public_groups()
		temp2 = populate_list_of_group_members(temp1)
		#print "publics: ", temp1, temp2
		all_users = user_name_to_id(temp2)
	
	if search_groups[0] != "all":
		all_groups = group_name_to_id(search_groups)
	else:
		all_groups = group_name_to_id(get_public_groups())


	#print "name of Authors: ", all_users
	#print "name of Groups: ", all_groups

	search_results = []
	all_ids = []

	for word in split_query:
		for at_name in attr_name:
			#print "attr: ", at_name
			# CASE 1 -- SEARCH IN THE STRUCTURE OF THE GSYSTEM
			for GSystem_name in GSystem_names:
				GSystem_obj = node_collection.one({"_type":"GSystemType", "name":GSystem_name})
				##print GSystem_obj

				if at_name in GSystem_obj:
					if all_users != 0:
						res = node_collection.find({"_type":{"$in":POSSIBLE_SEARCH_TYPES}, "member_of":GSystem_obj._id, at_name:{"$regex":word, "$options":"i" }}, {"name":1, "created_by":1, "last_update":1, "member_of":1 , "group_set":1, "url":1})
					else:
						res = node_collection.find({"_type":{"$in":POSSIBLE_SEARCH_TYPES}, "created_by":{"$in":all_users}, "member_of":GSystem_obj._id, at_name:{"$regex":word, "$options":"i" }}, {"name":1, "created_by":1, "last_update":1, "member_of":1, "group_set":1, "url":1})	
					for obj in res:
						flag = False
						#print obj.name
						if obj._id not in all_ids:
							GSystem_groups = obj.group_set
							#print "groups: ", GSystem_groups
							
							for gr_id in all_groups:
								if gr_id in GSystem_groups:
									link_obj = addType(obj)
									search_results.append({'name':obj.name, 'link':link_obj['link'], 'created_by':link_obj['created_by'], 'last_update':link_obj['last_update'], '_id':link_obj['_id']})
									all_ids.append(obj._id)
									break
				continue			

			# CASE 2 -- SEARCH THE GATTRIBUTES
			try:
				attr_id = node_collection.one({"_type":"AttributeType", "name":at_name}, {"_id":1})
				res = triple_collection.find({"_type":"GAttribute", "attribute_type":ObjectId(attr_id._id), "object_value":{"$regex":word, "$options":"i"}}, {"name":1, "object_value":1, "subject":1})
				#print "Sttr type: ", attr_id
				for obj in res: 
					if all_users == 0:
						GSystem = node_collection.one({"_id":obj.subject}, {"name":1, "created_by":1, "last_update":1, "member_of":1 , "group_set":1, "url":1})
					else:
						GSystem = node_collection.one({"_id":obj.subject, "created_by":{"$in":all_users}}, {"name":1, "created_by":1, "last_update":1, "member_of":1, "group_set":1, "url":1})

					if GSystem._id not in all_ids:
						#print "adding: ", GSystem._id
						# THE FOLLOWING CODE MAY BE WRONG IF THE RETURNED NODE IS A MEMBER OF MORE THAN ONE GSYSTEM_TYPE
						#link_obj = node_collection.one({"member_of":GSystem.member_of[0], "required_for":"Links"}, {"link":1})
						#print "731"
						GSystem_groups = GSystem.group_set
						#print "groups: ", GSystem_groups
						
						for gr_id in all_groups:
							if gr_id in GSystem_groups:
								link_obj = addType(GSystem)
								search_results.append({'name':GSystem.name, 'link':link_obj['link'], 'created_by':link_obj['created_by'], 'last_update':link_obj['last_update'], '_id':link_obj['_id']})
								all_ids.append(GSystem._id)
								break
			except:
				continue

	search_results = sort_names_by_similarity(search_results, search_str_user)
	#print search_results
	search_results = json.dumps(search_results, cls=Encoder)

	context_to_return = getRenderableContext(group_id)
	context_to_return['search_results'] = search_results
	context_to_return['processed'] = 1
	context_to_return['search_type'] = ADVANCED_SEARCH

	return render(request, 'ndf/search_page.html', context_to_return)


def get_public_groups():
	cur = node_collection.find({"_type": "Group", "group_type": "PUBLIC"}, {"name": 1})
	allGroups = []
	for obj in cur:
		allGroups.append(obj.name)

	return allGroups


def addType(obj):
	##print "received: ", obj.member_of[0]
	#i = ObjectId(obj.member_of[0])
	#links = node_collection.find({"member_of":i, "required_for":"Links"}, {"link":1})
	##print "links count", links.count(), "\n"
        
        auth = node_collection.one({'_type': 'Author', 'created_by': obj.created_by})
        
	#for ob in links:
	obj2 = {}
        
	obj2['_id'] = obj._id
	obj2['name'] = obj.name
	obj2['link'] = obj.url
	if auth:
                obj2['created_by'] = auth.name
	##print "lst update: ", type(obj.last_update)
	obj2['last_update'] = str(obj.last_update.date())
	#datetime.datetime.strptime(obj.last_update, "%Y-%m-%dT%H:%M:%S.%fZ").date()
	#print "obj", obj2
	return obj2


def sort_names_by_similarity(exact_match, search_str_user):
	matches = []					# TO STORE A LIST OF SORTED MATCH PERCENTAGE
	final_list = []					# FINAL LIST OF SORTED OBJECTS

	#print exact_match
	for obj in exact_match:
		##print obj
		match = difflib.SequenceMatcher(None, obj['name'], search_str_user)
		per_match = match.ratio()
		##print "sorting", obj['name'], ": ", per_match, "\n"

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
	articles=['a', 'an', 'and', 'the', 'i', 'is', 'this', 'that', 'there', 'here', 'am', 'on', 'at', 'of', 'where']
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
	stemmer = nltk.stem.porter.PorterStemmer()

	while (c < l):
		temp = words[c].lower() 			#THE WORD IS CONVERTED INTO LOWER CASE IN THIS STEP
		temp = stemmer.stem_word(temp)
		stemmed.append(temp)
		c+=1
		#temp = stem(words[c])
		#if (temp != search_str_user):
	
	#print stemmed
	return stemmed	

"""
This function returns a list of all authors.
"""
def populate_list_of_members():
	members = User.objects.all()
	memList = []
	for mem in members:
		memList.append(mem.username)	
	return memList

def populate_list_of_group_members(group_ids):
	"""
	This function returns a list of users in a given list of groups.
	Groups should be given as a list of group ids.
	"""
	memList = []

	try:
		for gr in group_ids:
			# THIS CODE WILL CAUSE PROBLEMS IF THERE ARE MANY GROUPS WITH THE SAME NAME
			group_id = node_collection.find_one({"_type":"Group", "name":gr}, {"_id":1})
			author_list = node_collection.one({"_type":"Group", "_id":group_id._id}, {"author_set":1, "_id":0})

			for author in author_list.author_set:
				name_author = User.objects.get(pk=author).username
				if name_author not in memList:
					memList.append(name_author)
	except:
		pass

	return memList


def get_users(request, group_id):
	group_ids = str(request.GET['Groups'])
	group_ids = group_ids.split(",")
	#print group_ids

	if group_ids[0] == "all":
		#print "hi there"
		allGroups = get_public_groups()
		allUsers = populate_list_of_group_members(allGroups)
	else:
		allUsers = populate_list_of_group_members(group_ids)
	return HttpResponse(json.dumps(allUsers, cls=Encoder))


def get_node_info(request, group_id, node_name):

	# ins_objectid  = ObjectId()
	# if ins_objectid.is_valid(group_id) is False :
	# 	group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
	# 	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	# 	if group_ins:
	# 		group_id = str(group_ins._id)
	# 	else:
	#     		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	#     		if auth :
	# 			group_id = str(auth._id)
	# else:
	# 	pass

	try:
	    group_id = ObjectId(group_id)
	except:
	    group_name, group_id = get_group_name_id(group_id)


	is_list = False
	list_of_nodes = node_collection.find({"name": node_name}, {"_id": 1})

	if list_of_nodes.count() > 1:
		list_of_nodes.rewind()
		is_list = True
		list_nodes = []

		for obj in list_of_nodes:
			list_nodes.append(obj._id)

		list_nodes = json.dumps(list_nodes, cls=Encoder)
		return render(request, 'ndf/node_details.html', {'is_list':1, 'list_nodes':list_nodes, 'all_fields':'', 'groupid':group_id})
	else:
		sg_node = node_collection.one({"name": node_name})
		GSTypes = sg_node.member_of

		attrs = []
		results = {}
		results['name'] = sg_node.name
		results['created_by'] = sg_node.created_by
		results['last_update'] = str(sg_node.last_update.date())

		for GSType in GSTypes:
			obj = node_collection.one({"_id": ObjectId(GSType)})

			for attr in obj.attribute_type_set:
				custom_attrs = triple_collection.find({"_type": "GAttribute", "subject": ObjectId(sg_node._id), "attribute_type": ObjectId(attr._id)}, {"name":1, "object_value":1})
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
	"""
	This view displays the info about a node - the basic fields - name, created_by, last_update as well as all the GAttributes.
	Useful for GSystems that dont have an output .html template
	"""
	# ins_objectid  = ObjectId()
	# if ins_objectid.is_valid(group_id) is False :
	# 	group_ins = node_collection.find_one({'_type': "Group","name": group_id})
	# 	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	# 	if group_ins:
	# 		group_id = str(group_ins._id)
	# 	else:
	#     		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	#     		if auth :
	# 			group_id = str(auth._id)
	# else:
	# 	pass

	try:
	    group_id = ObjectId(group_id)
	except:
	    group_name, group_id = get_group_name_id(group_id)
        

	sg_node = node_collection.one({"_id": ObjectId(node_id)})
	GSTypes = sg_node.member_of

	attrs = []
	results = {}
	results['name'] = sg_node.name
	results['created_by'] = sg_node.created_by
	results['last_update'] = str(sg_node.last_update.date())

	for GSType in GSTypes:
		obj = node_collection.one({"_id": ObjectId(GSType)})

		for attr in obj.attribute_type_set:
			custom_attrs = triple_collection.find({"_type": "GAttribute", "subject": ObjectId(sg_node._id), "attribute_type": ObjectId(attr._id)}, {"name":1, "object_value":1})
			for sg_attr in custom_attrs:
				temp = sg_attr.name
				i1 = temp.index('--') + 3
				temp = temp[i1:]
				i1 = temp.index('--') - 1
				temp = temp[:i1]
				results[temp] = sg_attr.object_value

	results = json.dumps(results, cls=Encoder)
	return render(request, 'ndf/node_details.html', {'is_list':0, 'list_nodes':'', 'all_fields':results, 'groupid':group_id})


def get_relations_for_autoSuggest(request, group_id):
	"""
	This function returns a list of names of RelationsTypes, GSystemTypes and GSYstems in the database according to the search query already typed by the user.
	This function is repeatedly called by an ajax call as the user types.
	"""
	col = get_database()[Node.collection_name]
	x = request.GET['sVal']						# CURRENT WORD BEING TYPED
	prefix = request.GET['prefix']				# ALREADY TYPED WORDS
	ins = []									# HOLDS LIST OF SUGGESTIONS TO RETURN

	# FIND NAMES OF ALL GSYSTEMTYPES OR RELATIONTYPES THAT START WITH WHAT HAS BEEN TYPED BY THE USER
	instances = node_collection.find({ "$or": [{ "_type": "RelationType"}, {"_type": "GSystemType"}], "name":{'$regex':"^"+x, "$options":"i"}}, {"name":1})
	for inst in instances:
		ins.append(prefix + ' ' + inst.name)
	
	instances = node_collection.find({"_type": "GSystem", "name":{'$regex':"^"+x, "$options":"i"}}, {"name":1})
	for inst in instances:
		ins.append(prefix + ' ' + inst.name)

	# NOTE: RESULTS FOR AUTO SUGGEST HAVE THE USER TYPED QUERY APPENDED AS PREFIX
	return HttpResponse(json.dumps(ins))



# def ra_search(request, group_id):
# 	# GET VALUE FROM TEXT BOX
# 	ins_objectid  = ObjectId()
# 	if ins_objectid.is_valid(group_id) is False :
# 		group_ins = node_collection.find_one({'_type': "Group","name": group_id})
# 		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
# 		if group_ins:
# 			group_id = str(group_ins._id)
# 		else:
# 	    		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
# 	    		if auth :
# 				group_id = str(auth._id)
# 	else:
# 		pass

# 	return render(request, 'ndf/ra_search.html', {"groupid":group_id})


def ra_search_results(request, group_id):
	"""
	This function implements the graph search.
	We have implemented the search in two cases:

	Case 1: <relation_type> <GSystem>
	In this case we look for a matching "relation type" from the left of the search query.
	Then the rest of the search query is matched with the GSystem names.
	In effect this case looks for GRelations with the matched Relation type and having the matched GSystem as either left or right subject.

	Case 2a: <GSystem_type> <Relation_Type> <GSystem>
	Case 2b: <GSystem> <Relation_Type> <GSystem_Type>
	In this case we look for a matching "GSystem type" from the left of the search query.
	Then all GSystems which are "member_of" the matched "GSystemType" are fetched.
	Then the rest of the search query is matched with the "GSystem" names.
	In effect this case looks for GRelations with the matched "GSystem" as one subject and any of the GSystems which are "member_of" the matched "GSystemType" as the other subject.
	"""
	
	sq = str(request.GET['search_text']).strip()						# SEARCH QUERY
	relations = node_collection.find({"_type": "RelationType"}, {"name": 1, "inverse_name": 1})	

	CASE_TWO_THRESHOLD = 0.6
	GSYSTEM_MIN_THRESHOLD_CASE1 = 0.69
	
	result_members = []
	sorted_rel = {}
	max_length = 0

	for rel in relations:
		length = len(rel.name.split('_'))
		if str(length) in sorted_rel.keys():
			sorted_rel[str(length)].append(rel.name)
		else:
			sorted_rel[str(length)] = [rel.name]
		
		length = len(rel.inverse_name.split('_'))
		if str(length) in sorted_rel.keys():
			sorted_rel[str(length)].append(rel.inverse_name)
		else:
			sorted_rel[str(length)] = [rel.inverse_name]

		if length > max_length:
			max_length = length

	split_word = sq.split()

	c = 0
	max_match = 0
	max_match_rel = ""
	rel_word_count = 0

	while c < len(split_word):
		cur_word = ""
		i = 0
		while i<c:
			cur_word += split_word[i]
			i += 1
		
		(max_m, max_m_rel, rel_w_count) = get_max_match(sorted_rel, cur_word, max_length)	
		if max_m > max_match:
			max_match = max_m
			max_match_rel = max_m_rel
			rel_word_count = rel_w_count
		c += 1

	GSystem_name = "" 
	c = rel_word_count
	while c < len(split_word):
		GSystem_name += split_word[c] + " "
		c += 1

	try:
		relationType_obj = node_collection.one({"_type": "RelationType", "$or": [{"name": max_match_rel}, {"inverse_name": max_match_rel} ] }, {"_id": 1, "name": 1})

		GRelation_objs = triple_collection.find({"_type": "GRelation", "relation_type": relationType_obj._id})

		#subjects = []
		#right_subjects = []

		for gr_obj in GRelation_objs:
			name_Grel = gr_obj.name
			left_sub = name_Grel[:name_Grel.index('--')-1]
			right_sub = name_Grel[name_Grel.rfind('--')+3:] 

			if difflib.SequenceMatcher(None, GSystem_name, left_sub).ratio() > GSYSTEM_MIN_THRESHOLD_CASE1: 
				reqd_obj = node_collection.one({"_id":gr_obj.right_subject, "access_policy":"PUBLIC"}, {"_id":1, "name":1, "created_by":1, "last_update":1, "url":1})
				#subjects.append(gr_obj.subject)
				#right_subjects.append(gr_obj.name)
				reqd_obj = addType(reqd_obj)
				result_members.append(reqd_obj)
				#print "match %: ", difflib.SequenceMatcher(None, GSystem_name, left_sub).ratio()
			elif difflib.SequenceMatcher(None, GSystem_name, right_sub).ratio() > GSYSTEM_MIN_THRESHOLD_CASE1: 
				reqd_obj = node_collection.one({"_id":gr_obj.subject, "access_policy":"PUBLIC"}, {"_id":1, "name":1, "created_by":1, "last_update":1, "url":1})
				#subjects.append(gr_obj.subject)
				#right_subjects.append(gr_obj.name)
				reqd_obj = addType(reqd_obj)
				result_members.append(reqd_obj)	
				#print "match %: ", difflib.SequenceMatcher(None, GSystem_name, right_sub).ratio()
	except Exception:
		pass
 

	##############################################   CASE - 2 - A  ##########################################
	if max_match < CASE_TWO_THRESHOLD:

		# LOOK FOR GSYSTEM_TYPE IN SEARCH QUERY
		GSystemTypes = node_collection.find({"_type": "GSystemType"}, {"name": 1})

		sorted_gst = {}
		max_length = 0

		for gst in GSystemTypes:
			length = len(gst.name.split())
			if str(length) in sorted_gst.keys():
				sorted_gst[str(length)].append(gst.name)
			else:
				sorted_gst[str(length)] = [gst.name]

			if length > max_length:
				max_length = length

		split_word = sq.split()

		c = 0
		max_match_gst = 0
		max_match_rel_gst = ""
		rel_word_count_gst = 0

		while c < len(split_word):
			cur_word = ""
			i = 0
			while i <= c:
				if i!= 0:
					cur_word += ' ' + split_word[i]
				else:
					cur_word = split_word[i]
				i += 1
			
			(max_m, max_m_rel, rel_w_count) = get_max_match(sorted_gst, cur_word, max_length)	
			if max_m > max_match_gst:
				max_match_gst = max_m
				max_match_rel_gst = max_m_rel
				rel_word_count_gst = rel_w_count
			c += 1

		# LOOK FOR GSYSTEM IN THE SEARCH QUERY
		sorted_gs = {}
		max_length = 0

		GSystems_sq = node_collection.find({"_type": {"$in": POSSIBLE_SEARCH_TYPES}}, {"name": 1})

		for gs in GSystems_sq:
			length = len(gs.name.split())
			if str(length) in sorted_gs.keys():
				sorted_gs[str(length)].append(gs.name)
			else:
				sorted_gs[str(length)] = [gs.name]

			if length > max_length:
				max_length = length

		split_word = sq.split()

		c = len(split_word)-1
		max_match_gs = 0
		max_match_rel_gs = ""
		rel_word_count_gs = 0

		while c >= rel_word_count_gst:
			cur_word = ""
			i = len(split_word)-1
			while i >= c:
				cur_word = split_word[i] + ' ' + cur_word
				i -= 1
			
			(max_m, max_m_rel, rel_w_count) = get_max_match(sorted_gs, cur_word, max_length)	
			if max_m > max_match_gs:
				max_match_gs = max_m
				max_match_rel_gs = max_m_rel
				rel_word_count_gs = rel_w_count
			c -= 1
		
		try:
			GStype = node_collection.one({"name": max_match_rel_gst}, {"_id": 1})
			GS_sq = node_collection.find_one({"name": "GSystem", "name": max_match_rel_gs}, {"_id": 1})

			allMembers = node_collection.find({"_type": {"$in": POSSIBLE_SEARCH_TYPES}, "member_of": GStype._id}, {"_id": 1, "name": 1})
			
			# LOOK FOR GRELATIONS WITH BOTH GSYSTEMS ON EITHER SIDE
			relations = triple_collection.find({"_type": "GRelation", "right_subject": GS_sq._id}, {"subject": 1})

			relations.rewind()
			for rel in relations:
				allMembers.rewind()
				for member in allMembers:
					if rel.subject == member._id:
						member = addType(member)
						result_members.append(member)	

			allMembers.rewind()
			relations = triple_collection.find({"_type": "GRelation", "subject": GS_sq._id}, {"right_subject": 1})
			for rel in relations:
				for member in allMembers:
					if rel.right_subject == member._id:
						member = addType(member)
						result_members.append(member)
		except Exception:
			pass

		######################################## CASE 2 - B ######################################

		# LOOK FOR GSYSTEM IN THE SEARCH QUERY
		sorted_gs = {}
		max_length = 0

		GSystems_sq = node_collection.find({"_type": {"$in": POSSIBLE_SEARCH_TYPES}}, {"name": 1})

		for gs in GSystems_sq:
			length = len(gs.name.split())
			if str(length) in sorted_gs.keys():
				sorted_gs[str(length)].append(gs.name)
			else:
				sorted_gs[str(length)] = [gs.name]

			if length > max_length:
				max_length = length

		split_word = sq.split()

		c = 0
		max_match_gs = 0
		max_match_rel_gs = ""
		rel_word_count_gs = 0

		while c < len(split_word):
			cur_word = ""
			i = 0
			while i <= c:
				cur_word += split_word[i]
				i += 1
			
			(max_m, max_m_rel, rel_w_count) = get_max_match(sorted_gs, cur_word, max_length)	
			if max_m > max_match_gs:
				max_match_gs = max_m
				max_match_rel_gs = max_m_rel
				rel_word_count_gs = rel_w_count
			c += 1

		# LOOK FOR GSYSTEM_TYPE IN SEARCH QUERY
		GSystemTypes = node_collection.find({"_type": "GSystemType"}, {"name": 1})

		sorted_gst = {}
		max_length = 0

		for gst in GSystemTypes:
			length = len(gst.name.split())
			if str(length) in sorted_gst.keys():
				sorted_gst[str(length)].append(gst.name)
			else:
				sorted_gst[str(length)] = [gst.name]

			if length > max_length:
				max_length = length

		split_word = sq.split()

		c = len(split_word)-1
		max_match_gst = 0
		max_match_rel_gst = ""
		rel_word_count_gst = 0

		while c >= rel_word_count_gs:
			cur_word = ""
			i = len(split_word)-1
			while i >= c:
				cur_word = split_word[i] + ' ' + cur_word
				i -= 1
			
			(max_m, max_m_rel, rel_w_count) = get_max_match(sorted_gst, cur_word, max_length)	
			if max_m > max_match_gst:
				max_match_gst = max_m
				max_match_rel_gst = max_m_rel
				rel_word_count_gst = rel_w_count
			c -= 1

		try:
			GStype = node_collection.one({"name": max_match_rel_gst}, {"_id": 1})
			GS_sq = node_collection.find_one({"name": "GSystem", "name": max_match_rel_gs}, {"_id": 1})

			allMembers = node_collection.find({"_type": {"$in": POSSIBLE_SEARCH_TYPES}, "member_of": GStype._id}, {"_id": 1, "name": 1, "created_by": 1, "last_update": 1, "url": 1})
			
			# LOOK FOR GRELATIONS WITH BOTH GSYSTEMS ON EITHER SIDE
			relations = triple_collection.find({"_type": "GRelation", "right_subject": GS_sq._id}, {"subject": 1})

			relations.rewind()
			for rel in relations:
				allMembers.rewind()
				for member in allMembers:
					if rel.subject == member._id:
						member = addType(member)
						result_members.append(member)	

			relations = triple_collection.find({"_type": "GRelation", "subject": GS_sq._id}, {"right_subject": 1})
			for rel in relations:
				allMembers.rewind()
				for member in allMembers:
					if rel.right_subject == member._id:
						member = addType(member)
						result_members.append(member)
		except Exception:
			pass

	#print result_members
	result_members = json.dumps(result_members, cls=Encoder)
	
	context_to_return = getRenderableContext(group_id)				# BASIC CONTEXT
	context_to_return['search_results'] = result_members			# ADD SEARCH RESULTS TO CONTEXT
	context_to_return['search_type'] = RELATION_SEARCH				# ADD SEARCH TYPE TO CONTEXT

	return render(request, 'ndf/search_page.html', context_to_return)


def get_max_match(sorted_rel, word_reqd, max_length):
	"""
	Helper function for the graph search function.
	It takes as input a dictionary having names grouped by their lengths.
	It returns the maximum matching word from the list to a required word.
	"""
	i = 1
	max_match = 0
	max_match_rel = ""
	rel_word_count = 0

	while i <= max_length:
		if str(i) in sorted_rel.keys():
			temp_list = sorted_rel[str(i)]

			for rel in temp_list:
				match_per = difflib.SequenceMatcher(None, word_reqd.lower(), rel.lower()).ratio()
				
				if match_per > max_match:
					max_match = match_per
					max_match_rel = rel
					rel_word_count = i
				if max_match == 1.0:
					return (max_match, max_match_rel, rel_word_count)
		i += 1

	return (max_match, max_match_rel, rel_word_count)			



#######################################################################################################################################

#######################################################SEMANTIC SEARCH 8TH JULY########################################################

################################### PRE PROCESSING FOR MAP REDUCE #################################################################	

def pre_process_for_map_reduce(text):
	
	grammar = r"""
	    NBAR:
		{<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns
		
	    NP:
		{<NBAR>}
		{<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
	"""
	chunker = nltk.RegexpParser(grammar)	#This is the chunker for nltk.It chunks values accordingly	
	toks = nltk.word_tokenize(text)		#This shall tokenize the words
	postoks = nltk.tag.pos_tag(toks)	#This shall perform tagging of words with their respective parts of speech
	tree = chunker.parse(postoks)	#It makes a tree of the tags and the words which are associated with that particular tag
	
	terms = get_terms(tree) 
	return terms


def leaves(tree):
    """Finds NP (nounphrase) leaf nodes of a chunk tree."""
    for subtree in tree.subtrees(filter = lambda t: t.node == 'NP'):
	#print "SUBTREE:",subtree
        yield subtree.leaves()

def normalise(word):
    """Normalises words to lowercase and stems and lemmatizes it.
       Lemmatization and stemming of the words both are necessary in order to make sure that the words are properly indexed	
    """
    
    lemmatizer = nltk.WordNetLemmatizer()
    stemmer = nltk.stem.porter.PorterStemmer()
    word = word.lower() 	#THE WORD IS CONVERTED INTO LOWER CASE IN THIS STEP
    word = stemmer.stem_word(word)
    word = lemmatizer.lemmatize(word)
    
    return word
    
from nltk.corpus import stopwords
stopwords = stopwords.words('english')
def acceptable_word(word):
    """Checks conditions for acceptable word: length, stopword.
       A word is acceptable if 
       		1. It is not a stopword
       		2. The length of the word is less than 40 characters
       		This is because, there is no point in storing a word more than 40chars long.This is because, user is not expected to 
       		type words which are 40 chars long   
    """
    max_word_length = 40
    accepted = bool(2 <= len(word) <= max_word_length and word.lower() not in stopwords)
    return accepted
    
def get_terms(tree):
    result = []	
    ALLOWED_LIST = ['CD','FW','JJ','JJR','JJS','NN','NNS','NNP','NNPS','VB','VBD','VBG','VBN','VBP','VBZ']	
    #print tree.leaves()
    for leaf in tree.leaves():
	#print leaf	
    	#for (w,t) in leaf:
	w = leaf[0]
	t = leaf[1]
	if acceptable_word(w) and t in ALLOWED_LIST:
		term = normalise(w)
		result.append(term)        
    return result
############################################################################################################################

######################################PRE PROCESSING FOR MAP REDUCE ########################################################	
def remove_punctuation(s):
	if not isinstance(s,unicode):
			s = unicode(s)			
	translate_table = dict((ord(c),None) for c in string.punctuation)	
	return s.translate(translate_table)

def mapper(input_value):
	input_value = remove_punctuation(input_value)	
	input_value_l = pre_process_for_map_reduce(input_value)		#This performs pre_processing for map reduce
	#This pre_processing is very important in order to save space
	#This pre_processing function makes the map_reduce function slow
	l = []
	for i in input_value_l:
		l.append([i,1])

	return l
	

def reducer(intermediate_key,intermediate_value_list):
	return(intermediate_key,sum(intermediate_value_list))

def map_reduce(x,mapper,reducer):
	groups = {}
	for key,group in itertools.groupby(sorted(mapper(x)),lambda x:x[0]):
		groups[key] = list([y for x,y in group])
	reduced_list = [reducer(intermediate_key,groups[intermediate_key]) for intermediate_key in groups ]
	return reduced_list
"""
def perform_map_reduce(request,group_id):
	#This function shall perform map reduce on all the objects which are present in the ToReduce() class Collection
	all_instances = list(node_collection.collection.ToReduce.find({'required_for':'map_reduce_to_reduce'}))
	for particular_instance in all_instances:
		#print particular_instance._id,'\n'
		particular_instance_id  = particular_instance.id_of_document_to_reduce
		#Now Pick up a node from the Node Collection class
		orignal_node = node_collection.find_one({"_id":particular_instance_id})		
		map_reduce_node = node_collection.find_one({'required_for':'map_reduce_reduced','orignal_doc_id':particular_instance_id})
		if map_reduce_node:
			map_reduce_node.content_org = dict(map_reduce(orignal_node.content_org,mapper,reducer))
			map_reduce_node.save()
		else:
			z = node_collection.collection.MyReduce()
			z.content_org = dict(map_reduce(orignal_node.content_org,mapper,reducer))
			z.orignal_doc_id = particular_instance_id
			z.required_for = u'map_reduce_reduced'
			z.save()
		#After performing MapReduce that particular instance should be removed from the ToReduce() class collection
		particular_instance.delete()		
	return HttpResponse("Map Reduce was performed successfully")
"""

def perform_map_reduce(request,group_id):
	#connection.register([MyDocs])
	#connection.register([ReducedDocs])
	#connection.register([ToReduceDocs])
	
	dltr=list(node_collection.find({'required_for':to_reduce_doc_requirement}))	#document_list_to_reduce
	
	for doc in dltr:
		doc_id = doc.doc_id
		#print "DOC ID LN 1504::",doc_id
		#orignal_doc = node_collection.find_one({"_id": doc_id,'required_for': my_doc_requirement})
		orignal_doc = node_collection.find_one({"_id": doc_id})
		content_dict = dict(map_reduce(orignal_doc.content_org,mapper,reducer))
		
		dord = node_collection.find_one({"orignal_id": doc_id, 'required_for': reduced_doc_requirement}) #doc of reduced docs
		if dord:
			dord.content=content_dict
			dord.is_indexed = False
			dord.save()
		else:
			new_doc = node_collection.collection.ReducedDocs()
			new_doc.content = content_dict
			new_doc.orignal_id = doc_id
			new_doc.required_for = reduced_doc_requirement
			new_doc.is_indexed = False
			new_doc.save()
		doc.delete()	
	#return render(request,'cf/thankYou.html',{})
	return HttpResponse("Map Reduce was performed successfully")


############################################################################################################################


############################################################################################################################

################################################## POST PROCESSING FOR MAP REDUCE ############################################
#The code till above was to perform map_reduce
#The code below this will try and perform semantic search
#import scipy.sparse
import numpy
#import sparsesvd
from math import sqrt


def td_doc():
	"""
	#{'word':{'ObjectId':number_of_occurances,'ObjectId':number_of_occurances}}
	This is the kind of dictionary which is required and will be created on the fly
	Since we have already stored the map reduced documents, this function will be pretty fast.
	The only thing which shall take time in our code is the MapReduce function	
	"""
	
	#connection.register([IndexedWordList])
	#connection.register([ReducedDocs])
	
	#This is the list of documents which contains the indexed words
	
	lod = node_collection.find({'required_for': indexed_word_list_requirement})	#list_of_documents_cursor
	
	"""
		What does indexing mean?
		In our scenario,indexing simply means to store the number if occurances of a particular word in each and every document.
		
	"""
	mrd = node_collection.find({'required_for': reduced_doc_requirement})	#map_reduced_documents
	mrdl = list(mrd)
	
		
	for pwdl in lod:	
		#particulat_word_list
		start_int = int(pwdl.word_start_id)
		start_char = str(unichr(96+start_int)) 	#This tells what is the starting character of the word
		wod = pwdl.words	#word_object_dictionary		
		
		for pmrd in mrdl:
			#particular_map_reduced_document
			if not pmrd.is_indexed:
				wd = pmrd.content
				
				for i in wd:
					if i.startswith(start_char):
						
						if i not in wod:
							wod[i] = {}
						wod[i][str(pmrd.orignal_id)]=wd[i]
		pwdl.words = wod
		pwdl.save()
	
	for pmrd in mrdl:
		pmrd.is_indexed = True
		pmrd.save()
		
def generate_big_dict():
	#This function will generate a big dictionary i.e. it will simply go and combine all the dictionaries together
	#connection.register([IndexedWordList])
	
	lod = node_collection.find({'required_for': indexed_word_list_requirement})
	lodl = list(lod)
	
	prefs = {} #prefs ==> Preferences
	
	for x in lodl:
		if x.words:
			prefs.update(x.words)		
	##print prefs
	return prefs	
	
####
#There are two kinds of similarity functions which we have defined and on whose basis recommendations are given
#If logic for semantic search needs to be changed then the only thing which is to be changed is this similarity function
####
def sim_distance(prefs,d1,d2):
	#This fucntion simply finds the distance between two words. It works very well
	si = {}

	if d1 not in prefs.keys():
		return 0	#NO RESULTS HAVE BEEN YET FOUND

	for item in prefs[d1]:	#This item is a dictionary containing book id and rating of that book for a user
		##print prefs[person1]
		if item in prefs[d2]:
			si[item] = 1
			
	if len(si) == 0:
		return 0
		
	#We know add the squares of all the differences
	sum_of_squares = 0
	
	for item in prefs[d1]:
		##print prefs[person1]
		if item in prefs[d2]:
			##print prefs[person2]
			##print "PERSON1 ITEM",item,prefs[d1][item]
			##print "PERSON2 ITEM",item,prefs[d2][item]	
			##print "SUBTRACT",prefs[d1][item] - prefs[d2][item]		
			sum_of_squares += pow(prefs[d1][item] - prefs[d2][item],2)
			##print sum_of_squares
	#Tags
	##print "SUM OF SQUARES :):)",sum_of_squares,(1.0/(1+sum_of_squares))
	return (1.0/(1+sum_of_squares))	

	
def sim_pearson(prefs,d1,d2):
	#Theoretically --- The results of pearson similarity should be better, but practically the results are much worse
	#Get the list of mutually rated items
	si = {}
	try:	
		for term in prefs[d1]:			
			if term in prefs[d2]: 
				si[term] = 1
	except KeyError:	
		return 0
	
	#sum calculations
	n = len(si)
	
	#sum of all preferences
	sum1 = sum([prefs[d1][it] for it in si])	
	sum2 = sum([prefs[d2][it] for it in si])

	#Sum of the squares
	sum1Sq = sum([pow(prefs[d1][it],2) for it in si])
	sum2Sq = sum([pow(prefs[d2][it],2) for it in si])

	#Sum of the products
	pSum = sum([prefs[d1][it] * prefs[d2][it] for it in si])
	num = pSum - (sum1 * sum2/n)
	den = sqrt((sum1Sq - pow(sum1,2)/n) * (sum2Sq - pow(sum2,2)/n))
	
	if den == 0:
		return 0

	r = num/den		
	return r

def topMatches(prefs,document,n=5,similarity=sim_distance):
	#This function returns the words which are closest to the word which are given to this function
	scores = [(similarity(prefs,document,other),other) for other in prefs if other != document]
	scores.sort()
	scores.reverse()
	return scores[0:n]
	
def recommend(prefs,term,similarity = sim_distance):
	#This function returns the documents which will be closer to the given document
	each_item_total = {}
	similarity_total_for_each_item = {}
	
	for other in prefs:
		if other == term:
			continue
		else:
			sim = similarity(prefs,term,other)
			
		if sim==0:
			continue
		
		for single_ObjectId in prefs[other]:
			if single_ObjectId in prefs[term]:				
				if single_ObjectId not in each_item_total:
					each_item_total[single_ObjectId] = 0				
				each_item_total[single_ObjectId] += sim * prefs[other][single_ObjectId]
			
				if single_ObjectId not in similarity_total_for_each_item:
					similarity_total_for_each_item[single_ObjectId] = 0
				similarity_total_for_each_item[single_ObjectId] += sim

	rankings = []
	
	for single_ObjectId,total_value in each_item_total.items():
		rankings.append((total_value/similarity_total_for_each_item[single_ObjectId],single_ObjectId))
	
	rankings.sort()
	rankings.reverse()
	
	return rankings	

################## FUNCTIONS FOR CALLING/TESTING SEMANTIC SEARCH ########################################

# def generate_term_document_matrix(request,group_id):
# 	td_doc()
# 	return HttpResponse("Thank You")

# def cf_search(request, group_id):
# 	ins_objectid  = ObjectId()
# 	if ins_objectid.is_valid(group_id) is False :
# 		group_ins = node_collection.find_one({'_type': "Group","name": group_id})
# 		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
# 		if group_ins:
# 			group_id = str(group_ins._id)
# 		else:
# 	    		auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
# 	    		if auth :
# 				group_id = str(auth._id)
# 	else:
# 		pass

	
# 	return render(request,'ndf/semantic_search.html',{"groupid":group_id})

def get_nearby_words(request,group_id):
	td_doc()
	prefs = generate_big_dict()
	
	search_text = str(request.GET['search_text']).strip()
	search_text_l = search_text.split()
	##print search_text_l
	word_set = set()
	ranking_list = []
	
	stemmer = nltk.stem.porter.PorterStemmer()
		
	for i in search_text_l:
		score = topMatches(prefs,stemmer.stem_word(i.lower()),n=30,similarity=sim_distance)
		for _,word in score:
			word_set.add(word)
		
		rankings = recommend(prefs,stemmer.stem_word(i.lower()),similarity = sim_distance)
		ranking_list.extend(rankings[0:5])
		# "5" -- It is the maximum number of documents which will be returned per word in search query
		# Change this number to that number which you want i.e. the number of documents per word you want
		
	final_ranking_list = sort_n_avg(ranking_list)
	final_ranking_list.sort()
	final_ranking_list.reverse()
	
	result_array = []
	for (relevance,each_id) in final_ranking_list:
		obj = node_collection.find_one({"_id": ObjectId(each_id)}, {"name": 1, "_id": 1, "member_of": 1, "created_by": 1, "last_update": 1, "group_set": 1, "url": 1})
		obj = addType(obj)
		obj["relevance"]=relevance
		result_array.append(obj)

	result_array = json.dumps(result_array, cls=Encoder)
	
	context_to_return = getRenderableContext(group_id)
	context_to_return['search_results'] = result_array
	context_to_return['search_type'] = SEMANTIC_SEARCH

	return render(request, 'ndf/search_page.html', context_to_return)
	
def sort_n_avg(l):
	"""
		Helper Function for: get_nearby_words()
		Parameters: List containing documents and their ratings
		Return Value:List in which the ratings of the documents have been averaged out
		
		INPUT:l = [(2,'alpha'),(3,'beta'),(1,'alpha'),(4,'alpha'),(5,'gamma'),(1,'alpha'),(2,'beta'),(3,'alpha')]
		OUTPUT:[(2.2, 'alpha'), (2.5, 'beta'), (5.0, 'gamma')]
		
	"""
	visited_list = []
	final_ranking_list = []
	
	for (value,obj_id) in l:
		if obj_id not in visited_list:
			visited_list.append(obj_id)
		
			i = 0
			req_sum = 0
		
			for (val,obj_id_added) in l:
				if obj_id_added == obj_id:
					i = i+1
					req_sum += val			
			if i!=0:
				final_ranking_list.append((float(req_sum)/i,obj_id))
			
	return final_ranking_list
#################################################################################################################	

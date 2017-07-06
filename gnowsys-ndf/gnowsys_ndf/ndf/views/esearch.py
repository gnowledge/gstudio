from bson import json_util
import re
import json
import os
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from elasticsearch import Elasticsearch		
from gnowsys_ndf.ndf.forms import SearchForm, AdvancedSearchForm
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME
name_index = GSTUDIO_SITE_NAME
es = Elasticsearch(['http://elsearch:changeit@gsearch:9200'])
author_map = {}
group_map = {}


if(os.path.isdir('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings')):
	with open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings/authormap_clix.json') as fe:
		author_map = json.load(fe)

	with open('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/mappings/groupmap_clix.json') as fe:
		group_map = json.load(fe)

else:
	print("No mapping found!")

hits = ""
med_list = []		 #contains all the search results
res_list = []		 #contains the header of the search results
results = []		 #contains a single page's results
author_index = "author_" + GSTUDIO_SITE_NAME

def get_search(request): 
	global med_list
	global res_list
	global results
	form = SearchForm(request.GET)
	query = request.GET.get("query")
	if(query):
		page = request.GET.get("page")
		if(page is None):
			print(query)
			query_display = ""
			group = request.GET.get('group')
			select = request.GET.get('select')
			
			if(select=="Author"):
				resultSet = search_query(author_index, select, group, query)
				hits =  "<h3> No of docs found: <b>%d</b></h3> " % len(resultSet)
				med_list = get_search_results(resultSet)
				if(group == "all"):
					res_list = ['<h3>  Showing contributions of user <b>%s</b> in all groups:</h3> ' % (query), hits]
				else:
					res_list = ['<h3>  Showing contributions of user <b>%s</b> in group <b>%s</b>":</h3> ' % (query,group_map[str(group)]), hits]
				
			else:
				if(select=="all"):
					select = "Author,image,video,text,application,audio,NotMedia"

				phsug_name = get_suggestion_body(query, field_value = "name.trigram", slop_value = 2, field_name_value = "name")
				phsug_content = get_suggestion_body(query, field_value = "content.trigram", slop_value = 3, field_name_value = "content")
				phsug_tags = get_suggestion_body(query, field_value = "tags.trigram", slop_value = 2, field_name_value = "tags")

				queryNameInfo = [0, 0.0, "", ""] #[queryNameInfo[0],queryNameInfo[1],queryNameInfo[2],query_display_name]
				queryContentInfo = [0, 0.0, "", ""]
				queryTagsInfo = [0, 0.0, "", ""]

				dqlis = [] 			# a list containing all the text inserted within double quotes
				q = "" 				# a string to hold the text not enclosed within ""

				#including quotes
				if('"' in query):
					l = re.split('(")', query) # this will split the query into tokens where delemiter is " and the delimiter is itself a token 
					qlist = list(filter(lambda a: a!='', l))
					
					itr = 0
					while(itr<len(qlist)):
						if(qlist[itr]=='"'):
							if(itr+2<len(qlist) and qlist[itr+2]=='"'):
								dqlis.append(qlist[itr+1])
								itr+=2
						else:
							q += qlist[itr]
						itr += 1

				print(dqlis, q)

				#dealing with the case when the user has given "" in the query
				if(len(dqlis)>0):
					query_body = '{ "query": {"bool": { "should": ['
					for quot in dqlis:
						query_body += ('{"multi_match": {"query": "%s", "fields": ["name^3", "altnames", "content^2", "tags"], "type": "phrase"}},' % (quot))
					if(q!=''):
						query_body += ('{"multi_match": {"query": "%s", "fields": ["name^3", "altnames", "content^2", "tags"], "type": "best_fields"}},' % (q))
					query_body += (']}}, "from": 0, "size": 100}')
					query_body = eval(query_body)	
					query_display = query

				else:

					get_suggestion(phsug_name, queryNameInfo, select, query, "name")
					if(queryNameInfo[2]!=query):
						get_suggestion(phsug_content, queryContentInfo, select, query, "content")
					if(queryNameInfo[2]!=query and queryContentInfo[2]!=query):
						get_suggestion(phsug_tags, queryTagsInfo, select, query, "tags")

					print (queryNameInfo[0],queryContentInfo[0],queryTagsInfo[0])
					query_display = ""

					#what if all are 1 and 2/3 names are same but the third one has higher score
					if((queryNameInfo[0]==1 and queryNameInfo[2]==query) or (queryContentInfo[0]==1 and queryContentInfo[2]==query) or (queryTagsInfo[0]==1 and queryTagsInfo[2]==query)): 
						#if the original query is the query to be searched
						query_display = query
					elif(queryNameInfo[0]==0 and queryContentInfo[0]==0 and queryTagsInfo[0]==0):																		
						#if we didnt find any suggestion, neither did we find the query already indexed->query remains same
						query_display = query
					else: #if we found a suggestion 
						res1_list = ['Search instead for <a href="">%s</a>'%(query)] #if the user still wants to search for the original query he asked for
						if(queryNameInfo[1]>=queryContentInfo[1] and queryNameInfo[1]>=queryTagsInfo[1]):						 #comparing the scores of name,content,tags suggestions and finding the max of the three
							query = queryNameInfo[2]
							query_display = queryNameInfo[3]					 #what query to display on the search result screen
						if(queryContentInfo[1]>queryNameInfo[1] and queryContentInfo[1]>=queryTagsInfo[1]):
							query = queryContentInfo[2]
							query_display = queryContentInfo[3]
						if(queryTagsInfo[1]>queryContentInfo[1] and queryTagsInfo[1]>queryNameInfo[1]):
							query = queryTagsInfo[2]
							query_display = queryTagsInfo[3]



				if(queryNameInfo[0]==0 and queryContentInfo[0]==0 and queryTagsInfo[0]==0):#if we didnt find any suggestion, neither did we find the query already indexed
					query_body = {"query": {
										"multi_match": { 											#first do a multi_match
											"query" : query,
											"type": "best_fields",									#when multiple words are there in the query, try to search for those words in a single field
											"fields": ["name^3", "altnames", "content^2", "tags"],	#in which field to search the query
											"minimum_should_match": "30%"
											}
										},
									"rescore": {													#rescoring the top 50 results of multi_match
										"window_size": 50,
										"query": {
											"rescore_query": {
												"bool": {											#rescoring using match phrase
													"should": [
														{"match_phrase": {"name": { "query": query, "slop":2}}},
														{"match_phrase": {"altnames": { "query": query, "slop": 2}}},
														{"match_phrase": {"content": { "query": query, "slop": 4}}}
													]
												}
											}
										}
									},
									"from": 0,
									"size": 100
								}

				else: #if we found a suggestion or if the query exists as a phrase in one of the name/content/tags field
					query_body = {"query": {
										"multi_match": {
											"query": query,
											"fields": ["name^3", "altnames", "content^2", "tags"],
											"type": "phrase", #we are doing a match phrase on multi field.
											"slop": 5
										}
									},
									"from": 0,
									"size": 100
								}

				query_display = query
				resultSet = search_query(GSTUDIO_SITE_NAME, select, group, query_body)
				hits = "<h3>No of docs found: <b>%d</b></h3>" % len(resultSet)
				if(group=="all"):
					res_list = ['<h3>Showing results for <b>%s</b> :</h3' % query_display, hits]
				else:
					res_list = ['<h3>Showing results for <b>%s</b> in group <b>"%s"</b>:</h3>' % (query_display,group_map[str(group)]), hits]
				med_list = get_search_results(resultSet)
				
		paginator = Paginator(med_list, 10)
		page = request.GET.get('page')
		print(page)
		try:
			results = paginator.page(page)
		except PageNotAnInteger:
			results = paginator.page(1)
		except EmptyPage:
			results = paginator.page(paginator.num_pages)


		return render(request, 'ndf/sform.html', {'form': form, 'header':res_list, 'content': results})

	return render(request, 'ndf/sform.html', {'form': form})
	

def get_suggestion_body(query, field_value, slop_value, field_name_value):
	phrase_suggest = {												#json body of phrase suggestion in name field
		"suggest": {
			"text": query,										#the query for which we want to find suggestion
				"phrase": {											
					"field": field_value,					#in which indexed field to find the suggestion
					"gram_size": 3,								#this is the max shingle size
					"max_errors": 2,							#the maximum number of terms that can be misspelt in the query
					"direct_generator": [ {
			          "field": field_value,
			          #"suggest_mode": "missing",
			          "min_word_length": 2,
					  "prefix_length": 0,						#misspelling in a single word may exist in the first letter itself
			          "suggest_mode":"missing"					#search for suggestions only if the query isnt present in the index
			        } ],
			        "highlight": {								#to highlight the suggested word
			          "pre_tag": "<em>",
			          "post_tag": "</em>"
			        },
			        "collate": {								#this is used to check if the returned suggestion exists in the index
			        	"query": {
			        		"inline": {
			        			"match_phrase": {				#matching the returned suggestions with the existing index
			        				"{{field_name}}": {
				        				"query": "{{suggestion}}",
				        				"slop": slop_value					
				        			}
			        			}
			        		}
			        	},
			        	"params": {"field_name": field_name_value},
			        	"prune": True							#to enable collate_match of suggestions
			        }
				},
			}
		}
	return phrase_suggest

def get_suggestion(suggestion_body, queryInfo, doc_types, query,field):
	res = es.suggest(body=suggestion_body, index=GSTUDIO_SITE_NAME)						#first we search for suggestion in the name field as it has the highest priority
	print(res)																					
	if(len(res['suggest'][0]['options'])>0):									#if we get a suggestion means the phrase doesnt exist in the index
		for sugitem in res['suggest'][0]['options']:
			if sugitem['collate_match'] == True:								#we find the suggestion with collate_match = True
				queryInfo[0] = 1
				queryInfo[1] = sugitem['score']
				queryInfo[2] = sugitem['text']				
				queryInfo[3] = sugitem['highlighted']						#the query to be displayed onto the search results screen
				break
	else:						#should slop be included in the search part here?
		query_body = {"query":{"match_phrase":{field: query,}}}
		if(es.search(index=GSTUDIO_SITE_NAME, doc_type=doc_types, body=query_body)['hits']['total']>0):
			queryInfo[0] = 1							#set queryNameInfo[0] = 1 when we found a suggestion or we found a hit in the indexed data
			queryInfo[2] = query


def get_search_results(resultArray):
	reslist = [doc['_source'] for doc in resultArray]
	return reslist

def resources_in_group(res,group):
	results = []
	group_id = str(group)
	for i in res["hits"]["hits"]:
		if "group_set" in i["_source"].keys():
			k = []
			for g_id in (i["_source"]["group_set"]):
				k.append(g_id["$oid"]) 
			if group_id in k:
					results.append(i)
	return results

def search_query(index_name, select, group, query):
	siz = 100
	if(index_name == author_index):
		try:
			doctype = author_map[str(query)]
		except:
			return []
		else:
			body = {
						"query":{
							"match_all":{}
						},
						"from": 0,
						"size": siz
					} 

	elif(index_name == GSTUDIO_SITE_NAME):
		doctype = select
		print(doctype)
		body = query
	
	resultSet = []
	temp = []
	i = 0
	
	while(True):
		body['from'] = i
		res = es.search(index = index_name, doc_type=doctype, body = body)
		l = len(res["hits"]["hits"])
		print (body)
		if(l==0):
			return []
		if l > 0 and l <= siz:
			if(group == "all"):
				resultSet.extend(res["hits"]["hits"])
			else:
				temp = resources_in_group(res,group)
				resultSet.extend(temp)
			if l < siz:
				break		
			i+=siz	

	return resultSet

def advanced_search(request):
	form = AdvancedSearchForm(request.GET)
	query = request.GET.get("query")
	if(query):
		pass
	else:
		return render(request, 'ndf/advanced_search1.html', {'form': form})

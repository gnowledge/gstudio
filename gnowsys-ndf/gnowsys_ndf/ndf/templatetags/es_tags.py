from datetime import datetime
from gnowsys_ndf.settings import *
from gnowsys_ndf.ndf.gstudio_es.es import *
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *
from django.template import Library
from django.template import RequestContext,loader
from django.shortcuts import render_to_response, render


register = Library()

#convert 13 digit number to slash date format 

@get_execution_time
@register.filter
def convert_date_string_to_date(your_timestamp):

	if your_timestamp:
		date = str(datetime.fromtimestamp( your_timestamp / 1000))
		temp1 = date[8:10]
		temp2 = date[5:7]
		temp3 = date[0:4]
		date = temp1 + "/"+ temp2 +"/"+ temp3
	else:
		pass

	return date


@get_execution_time
@register.filter
def cal_length(string):
	return len(str(string))

@get_execution_time
@register.assignment_tag
def get_member_of_list(node_ids):

	node_obj = None
	from gnowsys_ndf.ndf.models.gsystem_type import GSystemType
	temp_list =[]
	for each in node_ids:
		node_obj = node_collection.find_one({"_id":ObjectId(each)})
		if node_obj:
			temp_list.append(node_obj.name)

	if node_obj:
		return temp_list
	else:
		return None
@task
@get_execution_time
@register.assignment_tag
def top_pages():
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	user_field = A('terms', field='calling_url',size="2147483647")
	search_query.aggs.bucket('user_agg', user_field)
	execute_query = search_query.execute()
	response_of_top_users = execute_query.aggregations.user_agg.buckets
	temp_list = []
	count = 1
	for each_dict in response_of_top_users:
		#print each_dict.key ,each_dict.doc_count
		if each_dict :
			#print each_dict.key
			line = str(each_dict.key)
			if re.search( r'get_thread_comments_count', line, re.M|re.I):
				pass
			elif re.search( r'('',)', line, re.M|re.I):
				pass
			elif re.search( r'ajax', line, re.M|re.I):
				pass
			elif re.search( r'^/$', line, re.M|re.I):
				pass
			elif re.search( r'page-no', line, re.M|re.I):
				pass
			elif re.search( r'filter', line, re.M|re.I):
				pass
			elif re.search( r'searchresults', line, re.M|re.I):
				pass
			elif re.search( r'welcome', line, re.M|re.I):
				pass
			elif re.search( r'readDoc', line, re.M|re.I):
				pass			
			else:
				temp_list.append({"key":each_dict.key,"doc_count":each_dict.doc_count})
				count =count +1
				if count > 20:
					break
	return temp_list


@get_execution_time
@register.assignment_tag
def top_users():
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	user_field = A('terms', field='user',size="2147483647")
	search_query.aggs.bucket('user_agg', user_field)
	execute_query = search_query.execute()
	response_of_top_users = execute_query.aggregations.user_agg.buckets
	temp_list = []
	count = 1

	for each_dict in response_of_top_users:	
		if each_dict:
			line = str(each_dict.key)
			if re.search( r'nroer_team', line, re.M|re.I):
				pass
			elif re.search( r'mahesh777', line, re.M|re.I):
				pass
			elif re.search( r'nagarjuna', line, re.M|re.I):
				pass
			elif re.search( r'siddhu', line, re.M|re.I):
				pass
			elif re.search( r'rubina', line, re.M|re.I):
				pass
			elif re.search( r'1186', line, re.M|re.I):
				pass
			elif re.search( r'sadaqat', line, re.M|re.I):
				pass
			elif re.search( r'('',)', line, re.M|re.I):
				pass
			else:
				temp_list.append({"key":each_dict.key,"doc_count":each_dict.doc_count})
				count =count +1
				if count > 10:
					break	

	return temp_list

@task
@get_execution_time
@register.assignment_tag
def top_downloads():
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark").query('query_string', query='readDoc')
	user_field = A('terms', field='calling_url',size="2147483647")
	search_query.aggs.bucket('user_agg', user_field)
	execute_query = search_query.execute()
	response_of_top_users = execute_query.aggregations.user_agg.buckets

	temp_list = []
	count = 1

	for each_dict in response_of_top_users:
	#print each_dict.key ,each_dict.doc_count
		if each_dict :
			#print each_dict.key
			line = str(each_dict.key)
			if re.search( r'readdoc', line, re.M|re.I):
				temp_list.append({"key":each_dict.key,"doc_count":each_dict.doc_count})
				count =count +1
				if count > 10:
					break
	return temp_list

@task
@get_execution_time
@register.assignment_tag
def top_resources():
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	user_field = A('terms', field='calling_url',size="2147483647")
	search_query.aggs.bucket('user_agg', user_field)
	execute_query = search_query.execute()
	response_of_top_users = execute_query.aggregations.user_agg.buckets

	temp_list = []
	count = 1
	resource_extention_list=['mp4','webm','jpe','jpeg','png','mp3','epub','pdf']
	for each_dict in response_of_top_users:
		line = str(each_dict.key)
		for each in resource_extention_list:
			if re.search( eval(r'each'), line, re.M|re.I):
				temp_list.append({"key":each_dict.key,"doc_count":each_dict.doc_count})
				count =count+1
		if count > 10:
			break
	return temp_list

@task
@get_execution_time
@register.assignment_tag
def top_videos():
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	user_field = A('terms', field='calling_url',size="2147483647")
	search_query.aggs.bucket('user_agg', user_field)
	execute_query = search_query.execute()
	response_of_top_users = execute_query.aggregations.user_agg.buckets

	temp_list = []
	count = 1
	resource_extention_list=['mp4','webm']
	for each_dict in response_of_top_users:
		line = str(each_dict.key)
		for each in resource_extention_list:
			if re.search( eval(r'each'), line, re.M|re.I):
				temp_list.append({"key":each_dict.key,"doc_count":each_dict.doc_count})
				count =count+1
		if count > 10:
			break
	return temp_list

@task
@get_execution_time
@register.assignment_tag
def top_audios():
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	user_field = A('terms', field='calling_url',size="2147483647")
	search_query.aggs.bucket('user_agg', user_field)
	execute_query = search_query.execute()
	response_of_top_users = execute_query.aggregations.user_agg.buckets

	temp_list = []
	count = 1
	resource_extention_list=['mp3']
	for each_dict in response_of_top_users:
		line = str(each_dict.key)
		for each in resource_extention_list:
			if re.search( eval(r'each'), line, re.M|re.I):
				temp_list.append({"key":each_dict.key,"doc_count":each_dict.doc_count})
				count =count+1
		if count > 10:
			break
	return temp_list

@task
@get_execution_time
@register.assignment_tag
def top_images():
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	user_field = A('terms', field='calling_url',size="2147483647")
	search_query.aggs.bucket('user_agg', user_field)
	execute_query = search_query.execute()
	response_of_top_users = execute_query.aggregations.user_agg.buckets

	temp_list = []
	count = 1
	resource_extention_list=['jpe','jpeg','png']
	for each_dict in response_of_top_users:
		line = str(each_dict.key)
		for each in resource_extention_list:
			if re.search( eval(r'each'), line, re.M|re.I):
				temp_list.append({"key":each_dict.key,"doc_count":each_dict.doc_count})
				count =count+1
		if count > 10:
			break
	return temp_list


@task
@get_execution_time
@register.assignment_tag
def each_file_download_count(url,group_name_tag,node,download_filename):
	temp_list = []
	try:
		if url == "read_file" and node:
			url = "/home/file/readDoc/"+str(node._id)+"/"+download_filename
			search_query = Search(using=es, index="benchmarks",doc_type="benchmark").query('query_string', query='readDoc')
			user_field = A('terms', field='calling_url',size="2147483647")
			search_query.aggs.bucket('user_agg', user_field)
			execute_query = search_query.execute()
			response_of_top_users = execute_query.aggregations.user_agg.buckets
			
			count = 1

			for each_dict in response_of_top_users:
				if each_dict :
					#print each_dict.key
					line = str(each_dict.key)
					#search_q = eval("r'"+str(url)+"', line, re.M|re.I")
					if re.search(str(url), line, 10):
						temp_list.append({"key":each_dict.key,"doc_count":each_dict.doc_count})

		if temp_list:
			# print temp_list[0]['doc_count']
			return temp_list[0]['doc_count']
		else:
			return 0
	except Exception as e:
		print "Issue in download count of file:"+str(e)
		print len(temp_list)
		return "ERROR"
	return temp_list
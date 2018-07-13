from datetime import datetime
from gnowsys_ndf.settings import *
from gnowsys_ndf.ndf.gstudio_es.es import *
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *
from django.template import Library
from django.template import RequestContext,loader
from django.shortcuts import render_to_response, render
import datetime
from bs4 import BeautifulSoup
from functionOutput import *

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



#this function is the convert the date type object to days so as to ascertain the difference between 2 dates
def getDayNum(date_Obj):
	return 365*date_Obj.year + 30*date_Obj.month + date_Obj.day

def getDateDiff(date1, date2):
	return abs(getDayNum(date1)-getDayNum(date2))



@get_execution_time
@register.assignment_tag
def getDate(strDate):
	#the date is like DD/MM/YYYY
	day = int(strDate[0]+strDate[1])
	month = int(strDate[3]+strDate[4])
	year = int(strDate[6]+strDate[7]+strDate[8]+strDate[9])
	date = datetime.date(year,month,day)
	return date

def write_json(fname, datadict):
	with open(str(datetime.date.today())+str(fname)+'userwise','w') as fp1:
		json.dump(datadict,fp1)
	count_list = datadict.values()
	total_count = sum(count_list)
	file_count = {'total'+str(fname):total_count}
	with open(str(datetime.date.today())+str(fname)+'total_count','w') as fp2:
		json.dump(file_count,fp2)

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

def get_download_name(download_url):
	#gets the download name from the download url
	last_slash = download_url.rfind('/')
	last_colon = download_url.rfind('.')
	download = download_url[last_slash+1:last_colon]
	return download

def get_resource_name(resource_url):
    #gets the resource name from the resource url
	last_slash = resource_url.rfind('/')
	last_colon = resource_url.rfind('.')
	resource = resource_url[last_slash+1:last_colon]
	return resource

def get_video_name(video_url):
    #gets the video name from the video url
	last_slash = video_url.rfind('/')
	last_colon = video_url.rfind('.')
	video = video_url[last_slash+1:last_colon]
	return video

def get_audio_name(audio_url):
    #gets the audio name from the audio url
	last_slash = audio_url.rfind('/')
	last_colon = audio_url.rfind('.')
	audio = audio_url[last_slash+1:last_colon]
	return audio

def get_image_name(image_url):
    #gets the image name from the image url
	last_slash = image_url.rfind('/')
	last_colon = image_url.rfind('.')
	image = image_url[last_slash+1:last_colon]
	return image

def get_page_name(page_url):
	r = requests.get('https://nroer.gov.in'+str(page_url))
	soup = BeautifulSoup(r.text,'html.parser')
	s = soup.find("h3", "text-gray")
	if s is None:
		return None
	else:
		return s.string

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
				name = get_page_name(str(each_dict.key))
				if not name is None:
					temp_list.append({"key":name,"doc_count":each_dict.doc_count})
					count =count +1
				if count > 20:
					break
	top_pages_op(temp_list)
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
	top_users_op(temp_list)
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
				temp_list.append({"key":get_download_name(str(each_dict.key)),"doc_count":each_dict.doc_count})
				count =count +1
				if count > 10:
					break
	top_downloads_op(temp_list)
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
				temp_list.append({"key":get_resource_name(str(each_dict.key)),"doc_count":each_dict.doc_count})
				count =count+1
		if count > 10:
			break
	top_resources_op(temp_list)
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
				temp_list.append({"key":get_video_name(str(each_dict.key)),"doc_count":each_dict.doc_count})
				count =count+1
		if count > 10:
			break
	top_videos_op(temp_list)
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
				temp_list.append({"key":get_audio_name(str(each_dict.key)),"doc_count":each_dict.doc_count})
				count =count+1
		if count > 10:
			break
	top_audios_op(temp_list)
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
				temp_list.append({"key":get_image_name(str(each_dict.key)),"doc_count":each_dict.doc_count})
				count =count+1
		if count > 10:
			break
	top_images_op(temp_list)
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

#from here we start new functions
      

@get_execution_time
@register.assignment_tag

def anon_activity():
	# to bucket the activities based on user_id. 
	# if NULL, then the activity is anonymouse
	# if not NULL, then to see that it's not the poeple of the org
	search_query = Search(using=es,index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['user'])
	user_field = A('terms', field='user',size="2147483647")
	search_query.aggs.bucket('user_agg', user_field)
	execute_query = search_query.execute()
	response_of_anon_users = execute_query.aggregations.user_agg.buckets
	activity = {"NonAnonymousUsers":0, "Anonymous":0,"Percent-anonymous":0}
	for each_dict in response_of_anon_users:
			if each_dict.key == None:
				activity["Anonymous"] = each_dict.doc_count
			else:
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
				    activity["NonAnonymousUsers"] += each_dict.doc_count	
	activity["Percent-anonymous"] = 100.0*activity["Anonymous"]/(activity["Anonymous"]+activity["NonAnonymousUsers"])
	return activity


# this function is to find the top 10 users in the last month
#returns a dictionary of 10 items, where each item is {user:frequency}
#PS: There is no tie-breaker for users with the exact same frequency, and hence all will be listed
#in case there's a tie, even if the number exceeds 10
@get_execution_time
@register.assignment_tag
def top_users_lastWeek():
	fname = 'top_users_lastWeek'
	search_query = Search(using=es,index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['user','last_update'])
	#print search_query.count()
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_query[0:100000]:

		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<7):
			temp_list.append(str(each_dict.user))
	user_dict = {}
	freq_list = []
	for user in temp_list:
		if re.search( r'nroer_team', user, re.M|re.I):
			pass
		elif re.search( r'mahesh777', user, re.M|re.I):
			pass
		elif re.search( r'nagarjuna', user, re.M|re.I):
		    pass
		elif re.search( r'siddhu', user, re.M|re.I):	
			    pass
		elif re.search( r'rubina', user, re.M|re.I):
		    pass
		elif re.search( r'1186', user, re.M|re.I):
		    pass
		elif re.search( r'sadaqat', user, re.M|re.I):
		    pass
		elif re.search( r'('',)', user, re.M|re.I):
		    pass
		elif (user in user_dict):
			user_dict[user] += 1
		else:
			user_dict[user] = 1
	write_json(fname, user_dict)
	freq_list = list(set(user_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for user,user_freq in user_dict.items():
				if(user_freq==freq):
					count = count+1
					top_list[user] = user_freq
	top_users_lastWeekop(top_list)
	return top_list


# this function is to find the top 10 users in the last month
#returns a dictionary of 10 items, where each item is {user:frequency}
#PS: There is no tie-breaker for users with the exact same frequency, and hence all will be listed
#in case there's a tie, even if the number exceeds 10
@get_execution_time
@register.assignment_tag
def top_users_lastMonth():
	fname = 'top_users_lastMonth'
	search_query = Search(using=es,index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['user','last_update'])
	#print search_query.count()
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<30):
			temp_list.append(str(each_dict.user))
	user_dict = {}
	freq_list = []
	for user in temp_list:
		if re.search( r'nroer_team', user, re.M|re.I):
			pass
		elif re.search( r'mahesh777', user, re.M|re.I):
			pass
		elif re.search( r'nagarjuna', user, re.M|re.I):
		    pass
		elif re.search( r'siddhu', user, re.M|re.I):	
			    pass
		elif re.search( r'rubina', user, re.M|re.I):
		    pass
		elif re.search( r'1186', user, re.M|re.I):
		    pass
		elif re.search( r'sadaqat', user, re.M|re.I):
		    pass
		elif re.search( r'('',)', user, re.M|re.I):
		    pass
		elif (user in user_dict):
			user_dict[user] += 1
		else:
			user_dict[user] = 1
	write_json(fname, user_dict)
	freq_list = list(set(user_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for user,user_freq in user_dict.items():
				if(user_freq==freq):
					count = count+1
					top_list[user] = user_freq
	top_users_lastMonthop(top_list)
	return top_list


# this function is to find the top 10 users in the last month
#returns a dictionary of 10 items, where each item is {user:frequency}
#PS: There is no tie-breaker for users with the exact same frequency, and hence all will be listed
#in case there's a tie, even if the number exceeds 10
@get_execution_time
@register.assignment_tag
def top_users_lastYear():
	fname = 'top_users_lastYear'
	search_query = Search(using=es,index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['user','last_update'])
	#print search_query.count()
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<365):
			temp_list.append(str(each_dict.user))
	user_dict = {}
	freq_list = []
	for user in temp_list:
		if re.search( r'nroer_team', user, re.M|re.I):
			pass
		elif re.search( r'mahesh777', user, re.M|re.I):
			pass
		elif re.search( r'nagarjuna', user, re.M|re.I):
		    pass
		elif re.search( r'siddhu', user, re.M|re.I):	
			    pass
		elif re.search( r'rubina', user, re.M|re.I):
		    pass
		elif re.search( r'1186', user, re.M|re.I):
		    pass
		elif re.search( r'sadaqat', user, re.M|re.I):
		    pass
		elif re.search( r'('',)', user, re.M|re.I):
		    pass
		elif (user in user_dict):
			user_dict[user] += 1
		else:
			user_dict[user] = 1
	write_json(fname, user_dict)
	freq_list = list(set(user_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for user,user_freq in user_dict.items():
				if(user_freq==freq):
					count = count+1
					top_list[user] = user_freq
	top_users_lastYearop(top_list)
	return top_list


# this function is to find the top 10 pages in the last week
#returns a dictionary of 10 items, where each item is {page:frequency}
#PS: There is no tie-breaker for pages with the exact same frequency, and hence all will be listed
#in case there's a tie, even if the number exceeds 10
@get_execution_time
@register.assignment_tag
def top_pages_lastWeek():
	fname = 'top_pages_lastWeek'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<7):
			temp_list.append(str(each_dict.calling_url))
	page_dict = {}
	freq_list = []
	for page in temp_list:
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
		elif page in page_dict:			
			page_dict[page] += 1
		else:
			page_dict[page] = 1
	write_json(fname, page_dict)
	freq_list = list(set(page_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for page,page_freq in page_dict:
				if(page_freq==freq):
					name = get_page_name(str(page))
					if not name is None:
						count = count+1
						top_list[name] = page_freq
	top_pages_lastWeekop(top_list)
	return top_list


# this function is to find the top 10 pages in the last month
#returns a dictionary of 10 items, where each item is {page:frequency}
#PS: There is no tie-breaker for pages with the exact same frequency, and hence all will be listed
#in case there's a tie, even if the number exceeds 10
@get_execution_time
@register.assignment_tag
def top_pages_lastMonth():
	fname = 'top_pages_lastMonth'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_quer[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<30):
			temp_list.append(str(each_dict.calling_url))
	page_dict = {}
	freq_list = []
	for page in temp_list:
		if re.search( r'get_thread_comments_count', page, re.M|re.I):
			pass
		elif re.search( r'('',)', page, re.M|re.I):
			pass
		elif re.search( r'ajax', page, re.M|re.I):
			pass
		elif re.search( r'^/$', page, re.M|re.I):
			pass
		elif re.search( r'page-no', page, re.M|re.I):
			pass
		elif re.search( r'filter', page, re.M|re.I):
			pass
		elif re.search( r'searchresults', page, re.M|re.I):
			pass
		elif re.search( r'welcome', page, re.M|re.I):
			pass
		elif re.search( r'readDoc', page, re.M|re.I):
			pass
		elif page in page_dict:			
			page_dict[page] += 1
		else:
			page_dict[page] = 1

	write_json(fname, page_dict)
	freq_list = list(set(page_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for page,page_freq in page_dict.items():
				if(page_freq==freq):
					name = get_page_name(str(page))
					if not name is None:
						count = count+1
						top_list[name] = page_freq
	top_pages_lastMonthop(top_list)
	return top_list


# this function is to find the top 10 pages in the last year
#returns a dictionary of 10 items, where each item is {page:frequency}
#PS: There is no tie-breaker for pages with the exact same frequency, and hence all will be listed
#in case there's a tie, even if the number exceeds 10
@get_execution_time
@register.assignment_tag
def top_pages_lastYear():
	fname = 'top_pages_lastYear'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<365):
			temp_list.append(str(each_dict.calling_url))
	page_dict = {}
	freq_list = []
	for page in temp_list:
		if re.search( r'get_thread_comments_count', page, re.M|re.I):
			pass
		elif re.search( r'('',)', page, re.M|re.I):
			pass
		elif re.search( r'ajax', page, re.M|re.I):
			pass
		elif re.search( r'^/$', page, re.M|re.I):
			pass
		elif re.search( r'page-no', page, re.M|re.I):
			pass
		elif re.search( r'filter', page, re.M|re.I):
			pass
		elif re.search( r'searchresults', page, re.M|re.I):
			pass
		elif re.search( r'welcome', page, re.M|re.I):
			pass
		elif re.search( r'readDoc', page, re.M|re.I):
			pass
		elif page in page_dict:			
			page_dict[page] += 1
		else:
			page_dict[page] = 1
	write_json(fname, page_dict)
	freq_list = list(set(page_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for page,page_freq in page_dict.items():
				if(page_freq==freq):
					name = get_page_name(str(page))
					if not name is None:
						count = count+1
						top_list[name] = page_freq
	top_pages_lastYearop(top_list)
	return top_list


@get_execution_time
@register.assignment_tag
def top_downloads_lastWeek():
	fname = 'top_downloads_lastWeek'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark").query('query_string', query='readDoc')
	#print search_query.count()
	#print "!!!!!!!!!!!!!!!!!"
	search_query = search_query.source(["calling_url",'last_update'])
	execute_query = search_query.execute()

	temp_list = []
	for each_dict in search_query[0:10000]:
	
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())< 7):
			temp_list.append(str(each_dict.calling_url))
	download_dict = {}
	freq_list = []
	for download in temp_list:
		if re.search(r'readDoc', download, re.M|re.I):
			if download in download_dict:			
				download_dict[download] += 1
			else:
				download_dict[download] = 1
	write_json(fname, download_dict)
	freq_list = list(set(download_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for download,download_freq in download_dict.items():
				if(download_freq==freq):
					count = count+1
					top_list[get_download_name(str(download))] = download_freq
	top_downloads_lastWeekop(top_list)
	return top_list	


@get_execution_time
@register.assignment_tag
def top_downloads_lastMonth():
	fname = 'top_downloads_lastMonth'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark").query('query_string', query='readDoc')
	#print search_query.count()
	#print "!!!!!!!!!!!!!!!!!"
	search_query = search_query.source(["calling_url",'last_update'])
	execute_query = search_query.execute()

	temp_list = []
	for each_dict in search_query[0:10000]:
	
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())< 30):
			temp_list.append(str(each_dict.calling_url))
	download_dict = {}
	freq_list = []
	for download in temp_list:
		if re.search(r'readDoc', download, re.M|re.I):
			if download in download_dict:			
				download_dict[download] += 1
			else:
				download_dict[download] = 1
	write_json(fname, download_dict)
	freq_list = list(set(download_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for download,download_freq in download_dict.items():
				if(download_freq==freq):
					count = count+1
					top_list[get_download_name(str(download))] = download_freq
	top_downloads_lastYearop(top_list)
	return top_list	


@get_execution_time
@register.assignment_tag
def top_downloads_lastYear():
	fname = 'top_downloads_lastYear'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark").query('query_string', query='readDoc')
	#print search_query.count()
	#print "!!!!!!!!!!!!!!!!!"
	search_query = search_query.source(["calling_url",'last_update'])
	execute_query = search_query.execute()

	temp_list = []
	for each_dict in search_query[0:10000]:
	
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())< 365):
			temp_list.append(str(each_dict.calling_url))
	download_dict = {}
	freq_list = []
	for download in temp_list:
		if re.search(r'readDoc', download, re.M|re.I):
			if download in download_dict:			
				download_dict[download] += 1
			else:
				download_dict[download] = 1

	write_json(fname, download_dict)
	freq_list = list(set(download_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for download,download_freq in download_dict.items():
				if(download_freq==freq):
					count = count+1
					top_list[get_download_name(str(download))] = download_freq
	top_downloads_lastYearop(top_list)
	return top_list	


@get_execution_time
@register.assignment_tag
def top_resources_lastWeek():
	fname = 'top_resources_lastWeek'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	count = 1
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<7):
			temp_list.append(str(each_dict.calling_url))
	resource_dict = {}
	freq_list = []
	resource_extension_list=['mp4','webm','jpe','jpeg','png','mp3','epub','pdf']	
	for resource in temp_list:
		for each in resource_extension_list:
			if re.search( eval(r'each'), resource, re.M|re.I):
				if resource in resource_dict:
					resource_dict[resource] += 1
				else:
					resource_dict[resource] = 1
				break

	write_json(fname, resource_dict)
	freq_list = list(set(resource_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for resource,resource_freq in resource_dict.items():
				if(resource_freq==freq):
					count = count+1
					top_list[get_resource_name(str(resource))] = resource_freq
	top_resources_lastWeekop(top_list)
	return top_list


@get_execution_time
@register.assignment_tag
def top_resources_lastMonth():
	fname = 'top_resources_lastMonth'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	count = 1
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<30):
			temp_list.append(str(each_dict.calling_url))
	resource_dict = {}
	freq_list = []
	resource_extension_list=['mp4','webm','jpe','jpeg','png','mp3','epub','pdf']	
	for resource in temp_list:
		for each in resource_extension_list:
			if re.search( eval(r'each'), resource, re.M|re.I):
				if resource in resource_dict:
					resource_dict[resource] += 1
				else:
					resource_dict[resource] = 1
				break

	write_json(fname, resource_dict)
	freq_list = list(set(resource_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for resource,resource_freq in resource_dict.items():
				if(resource_freq==freq):
					count = count+1
					top_list[get_resource_name(str(resource))] = resource_freq
	top_resources_lastMonthop(top_list)
	return top_list


@get_execution_time
@register.assignment_tag
def top_resources_lastYear():
	fname = 'top_resources_lastYear'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	count = 1
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<365):
			temp_list.append(str(each_dict.calling_url))
	resource_dict = {}
	freq_list = []
	resource_extension_list=['mp4','webm','jpe','jpeg','png','mp3','epub','pdf']	
	for resource in temp_list:
		for each in resource_extension_list:
			if re.search( eval(r'each'), resource, re.M|re.I):
				if resource in resource_dict:
					resource_dict[resource] += 1
				else:
					resource_dict[resource] = 1
				break

	write_json(fname, resource_dict)
	freq_list = list(set(resource_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for resource,resource_freq in resource_dict.items():
				if(resource_freq==freq):
					count = count+1
					top_list[get_resource_name(str(resource))] = resource_freq
	top_resources_lastYearop(top_list)
	return top_list


@get_execution_time
@register.assignment_tag
def top_videos_lastWeek():
	fname = 'top_videos_lastWeek'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<7):
			temp_list.append(str(each_dict.calling_url))
	video_dict = {}
	freq_list = []
	video_extension_list=['mp4','webm']
	for video in temp_list:
		for each in video_extension_list:
			if re.search( eval(r'each'), video, re.M|re.I):
				if video in video_dict:
					video_dict[video] += 1
				else:
					video_dict[video] = 1
				break

	write_json(fname, video_dict)
	freq_list = list(set(video_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for video,video_freq in video_dict.items():
				if(video_freq==freq):
					count = count+1
					top_list[get_video_name(str(video))] = video_freq
	top_videos_lastWeekop(top_list)
	return top_list


@get_execution_time
@register.assignment_tag
def top_videos_lastMonth():
	fname = 'top_videos_lastWeek'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<30):
			temp_list.append(str(each_dict.calling_url))
	video_dict = {}
	freq_list = []
	video_extension_list=['mp4','webm']
	for video in temp_list:
		for each in video_extension_list:
			if re.search( eval(r'each'), video, re.M|re.I):
				if video in video_dict:
					video_dict[video] += 1
				else:
					video_dict[video] = 1
				break

	write_json(fname, video_dict)
	freq_list = list(set(video_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for video,video_freq in video_dict.items():
				if(video_freq==freq):
					count = count+1
					top_list[get_video_name(str(video))] = video_freq
	top_videos_lastMonthop(top_list)
	return top_list


@get_execution_time
@register.assignment_tag
def top_videos_lastYear():
	fname = 'top_videos_lastYear'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<365):
			temp_list.append(str(each_dict.calling_url))
	video_dict = {}
	freq_list = []
	video_extension_list=['mp4','webm']
	for video in temp_list:
		for each in video_extension_list:
			if re.search( eval(r'each'), video, re.M|re.I):
				if video in video_dict:
					video_dict[video] += 1
				else:
					video_dict[video] = 1
				break

	write_json(fname, video_dict)
	freq_list = list(set(video_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for video,video_freq in video_dict.items():
				if(video_freq==freq):
					count = count+1
					top_list[get_video_name(str(video))] = video_freq
	top_videos_lastYearop(top_list)
	return top_list


@get_execution_time
@register.assignment_tag
def top_audios_lastWeek():
	fname = 'top_audios_lastWeek'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<7):
			temp_list.append(str(each_dict.calling_url))
	audio_dict = {}
	freq_list = []
	audio_extension_list=['mp3']
	for audio in temp_list:
		for each in audio_extension_list:
			if re.search( eval(r'each'), audio, re.M|re.I):
				if audio in audio_dict:
					audio_dict[audio] += 1
				else:
					audio_dict[audio] = 1

	write_json(fname, audio_dict)
	freq_list = list(set(audio_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for audio,audio_freq in audio_dict.items():
				if(audio_freq==freq):
					count = count+1
					top_list[get_audio_name(str(audio))] = audio_freq
	top_audios_lastWeekop(top_list)
	return top_list


@get_execution_time
@register.assignment_tag
def top_audios_lastMonth():
	fname = 'top_audios_lastMonth'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())< 30):
			temp_list.append(str(each_dict.calling_url))
	audio_dict = {}
	freq_list = []
	audio_extension_list=['mp3']
	for audio in temp_list:
		for each in audio_extension_list:
			if re.search( eval(r'each'), audio, re.M|re.I):
				if audio in audio_dict:
					audio_dict[audio] += 1
				else:
					audio_dict[audio] = 1
	write_json(fname, audio_dict)
	freq_list = list(set(audio_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for audio,audio_freq in audio_dict.items():
				if(audio_freq==freq):
					count = count+1
					top_list[get_audio_name(str(audio))] = audio_freq
	top_audios_topMonthop(top_list)
	return top_list


@get_execution_time
@register.assignment_tag
def top_audios_lastYear():
	fname = 'top_audios_lastYear'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<365):
			temp_list.append(str(each_dict.calling_url))
	audio_dict = {}
	freq_list = []
	audio_extension_list=['mp3']
	for audio in temp_list:
		for each in audio_extension_list:
			if re.search( eval(r'each'), audio, re.M|re.I):
				if audio in audio_dict:
					audio_dict[audio] += 1
				else:
					audio_dict[audio] = 1

	write_json(fname, audio_dict)
	freq_list = list(set(audio_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for audio,audio_freq in audio_dict.items():
				if(audio_freq==freq):
					count = count+1
					top_list[get_audio_name(str(audio))] = audio_freq
	top_audios_lastYearop(top_list)
	return top_list

	
@get_execution_time
@register.assignment_tag
def top_images_lastWeek():
	fname = 'top_audios_lastWeek'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	count = 1
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<7):
			temp_list.append(str(each_dict.calling_url))
	image_dict = {}
	freq_list = []
	image_extension_list=['jpe','jpeg','png']
	for image in temp_list:
		for each in image_extension_list:
			if re.search( eval(r'each'), image, re.M|re.I):
				if image in image_dict:
					image_dict[image] += 1
				else:
					image_dict[image] = 1
				break

	write_json(fname, image_dict)
	freq_list = list(set(image_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for image,image_freq in image_dict.items():
				if(image_freq==freq):
					count = count+1
					top_list[get_image_name(str(image))] = image_freq
	top_images_lastWeekop(top_list)
	return top_list

	
@get_execution_time
@register.assignment_tag
def top_images_lastMonth():
	fname = 'top_images_lastMonth'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	count = 1
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<30):
			temp_list.append(str(each_dict.calling_url))
	image_dict = {}
	freq_list = []
	image_extension_list=['jpe','jpeg','png']
	for image in temp_list:
		for each in image_extension_list:
			if re.search( eval(r'each'), image, re.M|re.I):
				if image in image_dict:
					image_dict[image] += 1
				else:
					image_dict[image] = 1
				break

	write_json(fname, image_dict)
	freq_list = list(set(image_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for image,image_freq in image_dict.items():
				if(image_freq==freq):
					count = count+1
					top_list[get_image_name(str(image))] = image_freq
	top_images_lastMonthop(top_list)
	return top_list


@get_execution_time
@register.assignment_tag
def top_images_lastYear():
	fname = 'top_images_lastYear'
	search_query = Search(using=es, index="benchmarks",doc_type="benchmark")
	search_query = search_query.source(['calling_url','last_update'])
	execute_query = search_query.execute()
	temp_list = []
	count = 1
	for each_dict in search_query[0:10000]:
		that_date = getDate(each_dict.last_update)
		if(getDateDiff(that_date,datetime.date.today())<365):
			temp_list.append(str(each_dict.calling_url))
	image_dict = {}
	freq_list = []
	image_extension_list=['jpe','jpeg','png']
	for image in temp_list:
		for each in image_extension_list:
			if re.search( eval(r'each'), image, re.M|re.I):
				if image in image_dict:
					image_dict[image] += 1
				else:
					image_dict[image] = 1
				break

	write_json(fname, image_dict)
	freq_list = list(set(image_dict.values()))
	freq_list = sorted(freq_list,reverse=True)
	count = 0
	top_list = {}
	for freq in freq_list:
		if(count<10):
			for image,image_freq in image_dict.items():
				if(image_freq==freq):
					count = count+1
					top_list[get_image_name(str(image))] = image_freq
	top_images_lastYearop(top_list)
	return top_list

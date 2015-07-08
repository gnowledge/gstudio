''' -- Imports from python libraries -- '''
import datetime
import json
import pymongo
import re


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import get_valid_filename
from django.core.files.move import file_move_safe
from django.core.files.temp import gettempdir
from django.core.files.uploadedfile import UploadedFile # django file handler
from mongokit import paginator
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.models import *
from pymongo import Connection


try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId

from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection
from gnowsys_ndf.ndf.views.methods import get_node_metadata, get_node_common_fields, set_all_urls  # , get_page
from gnowsys_ndf.ndf.views.methods import create_gattribute, get_group_name_id

benchmark_collection = db[Benchmark.collection_name]
analytics_collection = db[Analytics.collection_name]
ins_objectid = ObjectId()


'''
FUNCTION TO REGISTER CUSTOM ACTIVITIES USING AJAX
'''

def custom_events(request):
	transaction = { 'status' : None, 'message' : None}

	analytics_event = analytics_collection.Analytics()
	analytics_event['user'] = request.user.username
	
	try : 
		analytics_event['session_key'] = request.session.session_key
	except :
		transaction['status'] = 0
		transaction['message'] = 'Error retrieving the session key.'
	
	analytics_event['timestamp'] = datetime.datetime.now();
	
	try : 
		analytics_event['group_id'] = Gid(request.POST['group_id'])
		analytics_event['action'] = json.loads(request.POST['action'])
		analytics_event['obj'][request.POST['obj']] = json.loads(request.POST['obj_properties'])
	except : 
		transaction['status'] = 0
		transaction['message'] = 'Incomplete Data.'

	if transaction['status'] is None :
		analytics_event.save()
		transaction['status'] = 1
		transaction['message'] = 'Transaction Successful !'

	return HttpResponse(json.dumps(transaction))

'''
USER ANALYTICS VIEWS
'''

def default_user(request):
	return redirect('/analytics/summary')

def user_list_activities(request):
	'''
	Lists the detailed activities of the user
	'''

	try :
		start_date = request.POST['start_date']
		end_date = request.POST['end_date']
	except:
		start_date = datetime.datetime.now() - datetime.timedelta(7)
		end_date = datetime.datetime.now()
	
	query("user",{ "username" : request.user.username })
	cursor = analytics_collection.find({"user" : request.user.username}).sort("timestamp",-1)
	
	lst = []
	for doc in cursor :
		lst.append(doc)
	
	return render_to_response ("ndf/analytics_list_details.html", { "data" : lst})

def get_user_sessions(user) :
	'''
	Returns the user activities grouped by sessions
	'''

	cursor = analytics_collection.find({"user" : user}).sort("timestamp",-1)

	lst = []
	sessions_list =[]
	d={}
	i=-1
	
	for doc in cursor :
		sk = str(doc['session_key'])
		if i!=-1 and d['session_key']==sk :
			sessions_list[i]["start_date"] = doc['timestamp']	
			sessions_list[i]["activities"]	+= 1
			sessions_list[i]["duration"] = sessions_list[i]["end_date"] - sessions_list[i]["start_date"]
		else :
			d= {}
			i+=1
			d["session_key"]=sk
			d["end_date"]	= doc['timestamp']
			d["start_date"]	= doc['timestamp']
			d["duration"] = d["end_date"] - d["start_date"]
			d["activities"]	= 1
			d["user"]	= doc['user']
			sessions_list.append(d)

	return sessions_list
	
def user_summary(request):
	'''
	Renders the summary of the User activities on the Metastudio 
	'''

	query("user",{ "username" : request.user.username })
	
	session_info = get_user_sessions(request.user.username)

	data = {}

	data['num_of_sessions'] = len(session_info)
	data['latest_activity'] = session_info[0]['end_date']
	duration = datetime.timedelta(0, 0)
	data['total_activities'] = 0
	for session in session_info :
		duration += session['duration']
		data['total_activities'] += session['activities']

	data['avg_session_duration'] = duration/data['num_of_sessions']

	data['num_of_pages'] = analytics_collection.find({ "action.key" : "create", "obj.page" : { '$exists' : 'true'}}).count()
	data['num_of_files'] = analytics_collection.find({ "action.key" : "create", "obj.file" : { '$exists' : 'true'}}).count()
	data['num_of_forums_created'] = analytics_collection.find({ "action.key" : "create", "obj.forum" : { '$exists' : 'true'}}).count()
	data['num_of_threads_created'] = analytics_collection.find({ "action.key" : "create", "obj.thread" : { '$exists' : 'true'}}).count()
	data['num_of_replies'] = analytics_collection.find({ "action.key" : "add", "obj.reply" : { '$exists' : 'true'}}).count()
	
	# More statistics can be queried from the anlytics_collection and added here.
	
	return render_to_response("ndf/analytics_summary.html",
															{ "data" : data})

'''
GROUP ANALYTICS VIEWS
'''

def default_group(request,group_id):
	return redirect('/analytics/'+group_id+'/summary')

def group_summary(request,group_id):

	'''
	Renders the summary of all the activities done by the members of the Group
	'''

	group_id=ObjectId("55717125421aa91eecbf8843")

	query("group",{ "group_id" : group_id })
	
	'''
	grouping the data  on the basis of user name
	'''
	pipe = [{'$match' : { 'group_id' : str(group_id)}}, {'$group': {'_id': '$user', 'num_of_activities': {'$sum': 1}}}]
	sorted_list = analytics_collection.aggregate(pipeline=pipe)
	sorted_list_acc_activities = sorted(sorted_list['result'],key = lambda k:k[u'num_of_activities'],reverse=True)
	
	'''
	To store the most active users in the group.
	The user with more number of activities are considered to be more active.
	'''
	active_users = []
	i=0
	for doc in sorted_list_acc_activities :
		active_users.append({ "name" : (doc[u'_id']) , "activities" : doc[u'num_of_activities'] } )
		i+=1
		if i==3:
			break


	num_of_forums=db['Nodes'].find({"url":"forum", "group_set":group_id, "status":"DRAFT"}).count()	

	num_of_threads=db['Nodes'].find({"url":"forum/thread", "group_set":group_id, "status":"DRAFT"}).count()

	regx=re.compile("^Reply of:.*")
	num_of_replies=db['Nodes'].find({"name": regx,"group_set":group_id, "status":"DRAFT"}).count()

	num_of_files=db['Nodes'].find({"url":"file", "group_set":group_id, "status":"PUBLISHED"}).count()
	
	num_of_pages=db['Nodes'].find({"url":"page", "group_set":group_id, "status":"PUBLISHED"}).count()
	
	return render_to_response("ndf/analytics_group_summary.html",{"data" : active_users,'forums' : num_of_forums,'threads' : num_of_threads,'replies' : num_of_replies,'files' : num_of_files,'pages' : num_of_pages})
	
def group_list_activities(request,group_id):
	'''
	Renders the list of activities of all the members of the group
	'''

	group_id=ObjectId("55717125421aa91eecbf8843")

	query("group",{ "group_id" : group_id })
	cursor = analytics_collection.find({"group_id" : str(group_id)}).sort("timestamp",-1)
	lst=[]

	for doc in cursor:
		lst.append(doc)

	return render_to_response("ndf/analytics_list_group_details.html",
															{ "data" : lst})

def group_members(request, group_id) :

	'''
	Renders the list of members sorted on the basis of their contributions in the group
	'''

	group_id=ObjectId("55717125421aa91eecbf8843")

	query("group",{ "group_id" : group_id })
	
	'''
	grouping the data  on the basis of user name
	'''
	pipe = [{'$match' : { 'group_id' : str(group_id)}}, {'$group': {'_id': '$user', 'num_of_activities': {'$sum': 1}}}]
	sorted_list = analytics_collection.aggregate(pipeline=pipe)
	sorted_list_acc_activities = sorted(sorted_list['result'],key = lambda k:k[u'num_of_activities'],reverse=True)
	
	computing_urls = [
		{ 'key' : 'forums', 'url' : 'forum', 'status' : 'DRAFT' }, 
		{ 'key' : 'threads', 'url' : 'forum/thread', 'status' : 'DRAFT' },
		{ 'key' : 'files', 'url' : 'file', 'status' : 'PUBLISHED' },
		{ 'key' : 'pages', 'url' : 'page', 'status' : 'PUBLISHED' },
		{ 'key' : 'replies', 'name' : re.compile("^Reply of:.*"), 'status' : 'DRAFT' }
	]

	list_of_members = []

	for member in sorted_list_acc_activities : 
		try :
			member_doc = {}
			member_doc['count'] = member[u'num_of_activities']

			author = node_collection.find_one({ "_type" : "Author" , "name" : member[u'_id']})
			
			member_doc['name'] = member[u'_id']

			for entity in computing_urls :
				member_doc[entity['key']] = []
				if entity['key'] == 'replies' :
					try :
						nodes = node_collection.find({"name":entity['name'], "group_set":group_id, "created_by" : author[u'created_by'], "status": entity[u'status']})	
						for node in nodes :
							member_doc[entity['key']].append({ 'name' : node[u'name'], "id" : node[u'name']})
					except :
						pass
				else :
					try :
						nodes = node_collection.find({"url":entity['url'], "group_set":group_id, "created_by" : author[u'created_by'], "status": entity[u'status']})	
						for node in nodes :
							member_doc[entity['key']].append({ 'name' : node[u'name'], "id" : node[u'_id']})
					except :
						pass

			list_of_members.append(member_doc)

		except : 
			return HttpResponse('Fatal Error')

	return render_to_response("ndf/analytics_group_members.html",{"data" : list_of_members })


'''
ANALYTICS PROCESSING 
'''

def query(analytics_type,details) :
	'''
	This function checks the Analytics data(for a user) in Analytic_col and gets the time to which the query set is updated. 
	Based on the time, it fetches raw data from Benchmark collection and hands over to normalize to do the filtering and 
	redundancy check.
	
	In case, the analytics_type is 'group', the function resolves the members of the group and calls itself recursively for each user,
	 to update the Analytic_col.
	
	'''

	if analytics_type == "user" :
		cursor = analytics_collection.find({"user" : str(details['username']) }).sort("timestamp",-1).limit(1)
		latest_timestamp = datetime.datetime(1900,1,1)
		if cursor is None :
			pass
		else :
			for doc in cursor :
				latest_timestamp = doc['timestamp']
				break
		
		raw_data = benchmark_collection.find({"user" : details['username'], "last_update": {"$gt":latest_timestamp}}).sort("last_update",-1)
		if raw_data is None:
			pass
		else :
			normalize(raw_data)

	else :
		group_id = details['group_id']	
		group_node = node_collection.find_one({"_id" : group_id})
		if group_node is not None :
			member_list = group_node[u'author_set'] + group_node[u'group_admin']
			for member in member_list :
				author = node_collection.find_one({"_type" : "Author", "created_by" : int(member)})
				if author is not None :
					query("user",{"username" : author[u'name'] })

	return 1

def normalize(cursor) :
	'''
		Normailizes the raw data from Benchmark collection so as to filter irrelevent content - 
		* filtering_list is the list of unwanted actions that gets filtered out
		* for documents having the same structure, only one is taken to remove redundancy

		Based on the GAPP name, the document is passed to functions in 'gapp_list' for further analysis

	'''

	cursor = cursor.sort("last_update",1)
	def gapp_list(gapp):
		return {
				"page": page_activity,
				"file": file_activity,
				"course": course_activity,
				"forum": forum_activity,
				"task": task_activity,
				"event": event_activity,
				"dashboard": dashbard_activity,
				"group": group_activity,
		}.get(gapp,default_activity)

	filtering_list = ["file/thumbnail",'None','',"home", "image/get_mid_size_img"]

	temp_doc = { u"calling_url" : None , u'last_update' : datetime.datetime(1900, 1, 1, 11, 19, 54)}
	for doc in cursor :
		if 'ajax' in str(doc[u'action']) or str(doc[u'action']) in filtering_list :
			pass
		else :
			if temp_doc[u'calling_url'] == doc[u'calling_url'] and temp_doc[u'session_key'] == doc[u'session_key'] and (doc[u'last_update'] - temp_doc[u'last_update'] < datetime.timedelta(0,300)):
				if u'has_data' in doc.keys() and bool(doc[u'has_data']) == 1 :
					if doc[u'has_data']["POST"] == True :
						temp_doc = doc
					elif doc[u'has_data']["GET"] == True :
							temp_doc = doc
					else :
						temp_doc[u'last_update'] = doc[u'last_update']
				else :
					temp_doc = doc
			
			else :
				if temp_doc[u'calling_url'] != None :
					url = str(temp_doc[u'calling_url']).split("/")
					group_id = Gid(url[1])
					gapp = url[2]
					gapp_list(gapp)(group_id,url,temp_doc)
				temp_doc = doc

	if temp_doc[u'calling_url'] != None :
		url = str(temp_doc[u'calling_url']).split("/")
		group_id = Gid(url[1])
		gapp = url[2]
		gapp_list(gapp)(group_id,url,temp_doc)

	return 1	


'''
ANALYSIS OF ACTIVITIES BY INDIVIDUAL GAPPS
'''

def initialize_analytics_obj(doc, group_id, obj) :
	'''
	Returns a new initialized object of the Analytics class
	'''

	analytics_doc=analytics_collection.Analytics()
	analytics_doc.timestamp=doc[u'last_update']
	analytics_doc.user = doc[u'user'] 
	analytics_doc.session_key = doc[u'session_key']
	analytics_doc.group_id = group_id
	analytics_doc.obj = { obj : { 'id' : None} } 
	
	return analytics_doc

def page_activity(group_id,url,doc):
	'''
	This function updates the Analytic_col database with the new activities done on the 
	page of MetaStudio, and also to see whether the page is published,deleted we
    check the status in the Nodes collection of database.
	And also we are assuming here that if the difference between the last update and created at 
	is less than 5 seconds then we should have created the page else we must have viewed the page.
	'''

	analytics_doc = initialize_analytics_obj(doc, group_id, 'page')
	
	if url[3] == "delete":
		if ins_objectid.is_valid(url[4]) is True:
			n = node_collection.find_one({"_id":ObjectId(url[4])})
			if n['status']=="HIDDEN" or n['status']=="DELETED":
				analytics_doc.action = { 'key' : 'delete', "phrase" : "deleted a" }
				analytics_doc.obj['page']['id'] = url[4]
				analytics_doc.obj['page']['name'] = n[u'name']
				analytics_doc.save()
				return 1

	elif  url[3] == "page_publish" :
		if ins_objectid.is_valid(url[4]) is True:
			n=node_collection.find_one({"_id":ObjectId(url[4])})
			if n['status']=="PUBLISHED" :
				analytics_doc.action = { 'key' : 'publish', "phrase" : "published a" }
				analytics_doc.obj['page']['id'] = url[4]
				analytics_doc.obj['page']['name'] = n[u'name']
				analytics_doc.save()
				return 1

	elif url[3] =="edit" :
		if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
			n=node_collection.find_one({"_id":ObjectId(url[4])})
			analytics_doc.action = { 'key' : 'edit' , "phrase" : "edited a" }
			analytics_doc.obj['page']['id'] = url[4]
			analytics_doc.obj['page']['name'] = n[u'name']
			analytics_doc.save()
			return 1
		
	else:
		try : 
			n = node_collection.find_one({"_id":ObjectId(url[3])})
			author_id = n[u'created_by']
			auth=node_collection.find_one({"_type": "Author", "created_by": author_id})
			if auth[u'name']==doc[u'user']:
				if (doc[u'last_update'] - n[u'created_at']).seconds < 5 :
					analytics_doc.action = {  "key" : "create" , "phrase" : "created a" }
					analytics_doc.obj['page']['id'] = ObjectId(url[3])
					analytics_doc.obj['page']['name'] = n[u'name']
					analytics_doc.save()
					return 1
				else :
					analytics_doc.action = { 'key' : "view" , "phrase" : "viewed a" }
					analytics_doc.obj['page']['id'] = ObjectId(url[3])
					analytics_doc.obj['page']['name'] = n[u'name']
					analytics_doc.save()
					return 1
			else :
				analytics_doc.action = { 'key' : "view" , "phrase" : "viewed a" }
				analytics_doc.obj['page']['id'] = ObjectId(url[3])
				analytics_doc.obj['page']['name'] = n[u'name']
				analytics_doc.save()
				return 1

		except Exception :
			pass
		
	return 0

def course_activity(group_id,url,doc):
	'''
	This function updates the analytics_collection database with the new activities done on the 
	courses of MetaStudio, and also to see whether the course is created, edited or viewed.We
    check the status in the Nodes collection of database.
	And also we are assuming here that if the difference between the last update and created at 
	is less than 5 seconds then we should have created the course.
	
	'''

	analytics_doc = initialize_analytics_obj(doc, group_id, 'course')
	if(url[3]=="create"):
		if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
			try :
				author = node_collection.find_one({'_type' : 'Author','name' : doc[u'user']})
				cursor = node_collection.find({'url' : 'course','created_by' : author[u'created_by']})
				for course_created in cursor :
					if (doc[u'last_update'] - course_created[u'created_at']).seconds < 5 :
						analytics_doc.action = { 'key' : 'create', 'phrase' : 'created a'}
						analytics_doc.obj['course']['id'] = ObjectId(course_created[u'_id'])
						analytics_doc.obj['course']['name'] = str(course_created[u"name"]) 
						analytics_doc.save()
			except :
				return 0

	elif(url[3]=="course_detail"):
		if(ins_objectid.is_valid(url[4])):
			n=node_collection.find_one({"_id":ObjectId(url[4])})
			try :
				analytics_doc.action = { 'key' : 'view', 'phrase' : 'viewed a'}
				analytics_doc.obj['course']['id'] = ObjectId(url[4])
				analytics_doc.obj['course']['name'] = str(n[u"name"]) 
				analytics_doc.save()
			except Exception :
				return 0

	elif(url[3]=="edit") :
		if(ins_objectid.is_valid(url[4])):
			if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
				n=node_collection.find_one({"_id":ObjectId(url[4])})
				try :
					analytics_doc.action = { 'key' : 'edit', 'phrase' : 'edited a'}
					analytics_doc.obj['course']['id'] = ObjectId(url[4])
					analytics_doc.obj['course']['name'] = str(n[u"name"]) 
					analytics_doc.save()
				except Exception :
					return 0
				
	elif(ins_objectid.is_valid(url[3])):
		n=node_collection.find_one({"_id":ObjectId(url[3])})
		try :
			analytics_doc.action = { 'key' : 'view', 'phrase' : 'viewed a'}
			analytics_doc.obj['course']['id'] = ObjectId(url[4])
			analytics_doc.obj['course']['name'] = str(n[u"name"]) 
			analytics_doc.save()
		except Exception :
			return 0
	

	return 0

def file_activity(group_id,url,doc):
	'''
	This function updates the analytics_collection database with the new activities done on the 
	files of MetaStudio, and also to see whether the file is viewed,edited, deleted, uploaded . 
	We check the status in the Nodes collection of database.
	And also we are assuming here that if the difference between the last update and created at 
	is less than 5 seconds then we should have uploaded the file. 
	
	'''
	
	analytics_doc = initialize_analytics_obj(doc, group_id, 'file')

	if(url[3]=="submit"):
		try :
			author = node_collection.find_one({'_type' : 'Author','name' : doc[u'user']})
			cursor = node_collection.find({'url' : 'file','created_by' : author[u'created_by']})
			for file_created in cursor :
				if (doc[u'last_update'] - file_created[u'created_at']).seconds < 5 :
					analytics_doc.action = { 'key' : 'create', 'phrase' : 'created a'}
					analytics_doc.obj['file']['id'] = ObjectId(file_created[u'_id'])
					analytics_doc.obj['file']['type'] = str(file_created[u"mime_type"])
					analytics_doc.obj['file']['name'] = str(file_created[u"name"]) 
					analytics_doc.save()
		except :
			return 0

	elif(url[3]=="readDoc"):
		n=node_collection.find_one({"_id":ObjectId(url[4])})
		try :
			analytics_doc.action = { 'key' : 'download', 'phrase' : 'downloaded a'}
			analytics_doc.obj['file']['id'] = ObjectId(url[4])
			analytics_doc.obj['file']['type'] = str(n[u"mime_type"])
			analytics_doc.obj['file']['name'] = str(n[u"name"]) 
			analytics_doc.save()
		except Exception :
			return 0


	elif url[3]=="details":
		if(ins_objectid.is_valid(url[4])):
			n=node_collection.find_one({"_id":ObjectId(url[4])})
			try :
				analytics_doc.action = { 'key' : 'view', 'phrase' : 'viewed a'}
				analytics_doc.obj['file']['id'] = ObjectId(url[4])
				analytics_doc.obj['file']['type'] = str(n[u"mime_type"])
				analytics_doc.obj['file']['name'] = str(n[u"name"]) 
				analytics_doc.save()
			except Exception :
				return 0

	elif(ins_objectid.is_valid(url[3])):
		n=node_collection.find_one({"_id":ObjectId(url[3])})
		try :
			analytics_doc.action = { 'key' : 'view', 'phrase' : 'viewed a'}
			analytics_doc.obj['file']['id'] = ObjectId(url[4])
			analytics_doc.obj['file']['type'] = str(n[u"mime_type"])
			analytics_doc.obj['file']['name'] = str(n[u"name"]) 
			analytics_doc.save()
		except Exception :
			return 0

	elif(url[3]=="delete"):
		if ins_objectid.is_valid(url[4]) is True:
			n=node_collection.find_one({"_id":ObjectId(url[4])})
			if n['status']=="HIDDEN" or n['status']=="DELETED":
				analytics_doc.action = { 'key' : 'delete', 'phrase' : 'deleted a'}
				analytics_doc.obj['file']['id'] = ObjectId(url[4])
				analytics_doc.obj['file']['type'] = str(n[u"mime_type"])
				analytics_doc.obj['file']['name'] = str(n[u"name"]) 
				analytics_doc.save()
	
	elif(url[3]=="edit" or url[3]=="edit_file"):
		if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
			if ins_objectid.is_valid(url[4]) is True:
				n=node_collection.find_one({"_id":ObjectId(url[4])})
				analytics_doc.action = { 'key' : 'edit', 'phrase' : 'edited'}
				analytics_doc.obj['file']['id'] = str(url[4])
				analytics_doc.obj['file']['type'] = str(n[u"mime_type"])
				analytics_doc.obj['file']['name'] = str(n[u"name"]) 
				analytics_doc.save()
	return 1

def forum_activity(group_id,url,doc):
	'''
	The function analyzes the forum activities of the user. 
	It takes in the raw normalized document from the normalize() function and analyzes the doc for activities like create, delete, view forums, thread, reply etc.  
	The analyzed data is stored in the Analytics collection.
	'''
	
	if ins_objectid.is_valid(url[3]) is False:
		if(url[3]=="delete"):
			if ins_objectid.is_valid(url[4]) is True:
				n=node_collection.find_one({"_id":ObjectId(url[4])})
				if n['status']=="HIDDEN" or n['status']=="DELETED":
					analytics_doc = initialize_analytics_obj(doc, group_id, 'forum')
					analytics_doc.action = { 'key' : 'delete', 'phrase' : 'deleted a' }
					analytics_doc.obj['forum']['id'] = url[4];
					analytics_doc.save();
					return 1

			elif url[4]=="thread":
				if ins_objectid.is_valid(url[6]) is True:
					n=node_collection.find_one({"_id":ObjectId(url[6])})
					if n['status']=="HIDDEN" or n['status']=="DELETED":
						analytics_doc = initialize_analytics_obj(doc, group_id, 'thread')
						analytics_doc.action = { 'key' : 'delete', 'phrase' : 'deleted a' }
						analytics_doc.action[2] = 'thread'
						analytics_doc.args['thread']['id'] = ObjectId(url[6]);
						analytics_doc.obj['thread']['forum'] = ObjectId(url[5]);
						analytics_doc.save();
						return 1

			elif url[4]=="reply":
				if ins_objectid.is_valid(url[7]) is True:
					n=node_collection.find_one({"_id":ObjectId(url[7])})
					if n['status']=="HIDDEN" or n['status']=="DELETED":
						analytics_doc = initialize_analytics_obj(doc, group_id, 'reply')
						analytics_doc.action = { 'key' : 'delete', 'phrase' : 'deleted a' }
						analytics_doc.obj['reply']['id'] = url[7];
						analytics_doc.obj['reply']['thread'] = url[6];
						analytics_doc.obj['reply']['forum'] = url[5];
						analytics_doc.save();
						return 1

		elif url[3]=="thread" :
			try :
				if ins_objectid.is_valid(url[4]) is True:
					analytics_doc = initialize_analytics_obj(doc, group_id, 'thread')
					analytics_doc.action = { 'key' : 'view', 'phrase' : 'viewed a' }
					analytics_doc.obj['thread']['id'] = ObjectId(url[4]);
					analytics_doc.save();
					return 1
			except :
				pass

		elif url[3]=="edit_forum" :
			if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
				analytics_doc = initialize_analytics_obj(doc, group_id, 'forum')
				analytics_doc.action = { 'key' : 'edit', 'phrase' : 'edited a' }
				analytics_doc.obj['forum']['id'] = ObjectId(url[4]);
				analytics_doc.save();
				return 1


		elif url[3]=="edit_thread" :
			if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
				analytics_doc = initialize_analytics_obj(doc, group_id, 'thread')
				analytics_doc.action = { 'key' : 'edit', 'phrase' : 'edited a' }
				analytics_doc.obj['thread']['forum'] = ObjectId(url[4]);
				analytics_doc.obj['thread']['id'] = ObjectId(url[5]);
				analytics_doc.save();
				return 1

		elif url[3] == 'add_node' :
			if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
				analytics_doc = initialize_analytics_obj(doc, group_id, 'reply')
				analytics_doc.action = { 'key' : 'add', 'phrase' : 'added a' }
				analytics_doc.save();
				return 1

	else:
		n=node_collection.find_one({"_id":ObjectId(url[3])})
		try :
			if url[4] == 'thread' :
				if url[5] == 'create' :
					if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
						try :
							author = node_collection.find_one({"_type" : "Author", "name" : doc[u'user']})
						except : 
							pass
						if author : 
							try : 
								threads = node_collection.find({"url" : "forum/thread" , "created_by" : author[u'created_by']})
								
								for created_thread in threads : 
									if (doc[u'last_update'] - created_thread[u'created_at']).seconds < 5 : 
										analytics_doc = initialize_analytics_obj(doc, group_id, 'thread')
										analytics_doc.action = { 'key' : 'create', 'phrase' : 'created a' }
										analytics_doc.obj['thread']['id'] = str(created_thread[u'_id']);
										analytics_doc.obj['thread']['forum'] = ObjectId(url[3]);
										analytics_doc.save();
										return 1
							except : 
								pass

		except :
			author_id=n[u'created_by']
			auth=node_collection.find_one({"_type": "Author", "created_by": author_id})
			if auth[u'name']==doc[u'user']:
				created_at = n[u'created_at']
				if (doc[u'last_update'] - created_at).seconds < 5 :
					analytics_doc = initialize_analytics_obj(doc, group_id, 'forum')
					analytics_doc.action = { 'key' : 'create', 'phrase' : 'created a' }
					analytics_doc.obj['forum']['id'] = ObjectId(url[3]);
					analytics_doc.save();
					return 1
				else :
					analytics_doc = initialize_analytics_obj(doc, group_id, 'forum')
					analytics_doc.action = { 'key' : 'view', 'phrase' : 'viewed a' }
					analytics_doc.obj['forum']['id'] = ObjectId(url[3]);
					analytics_doc.save();
					return 1

	return 0

def task_activity(group_id,url,doc):
	
	analytics_doc = initialize_analytics_obj(doc, group_id, 'task')
	
	if ins_objectid.is_valid(url[3]) is False:
		if(url[3]=="delete_task"):
			if ins_objectid.is_valid(url[4]) is True:
				analytics_doc.action = {  "key" : "delete" , "phrase" : "deleted a" }
				analytics_doc.obj['task']['id'] = url[4]
				analytics_doc.save();
				return 1


		elif url[3]=="edit":
			if ins_objectid.is_valid(url[4]) is True:
				if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
					analytics_doc.action = {  "key" : "edit" , "phrase" : "edited a" }
					analytics_doc.obj['task']['id'] = url[4]
					analytics_doc.save();
					return 1

		elif url[3]=="task" :
			if url[4] == "saveimage" :
				if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
					analytics_doc.action = {  "key" : "save_image" , "phrase" : "saved an" }
					#analytics_doc.obj['task']['id'] = url[4]
					return 1

	else:
		n=node_collection.find_one({"_id":ObjectId(url[3])})
		try :
			author_id=n[u'created_by']
			auth=node_collection.find_one({"_type": "Author", "created_by": author_id})
			if auth[u'name']==doc[u'user']:
				created_at = n[u'created_at']
				if (doc[u'last_update'] - created_at).seconds < 5 :
					analytics_doc.action = {  "key" : "create" , "phrase" : "created a" }
					analytics_doc.obj['task']['id'] = url[3]
					analytics_doc.save();
					return 1
				else :
					analytics_doc.action = {  "key" : "view" , "phrase" : "viewed a" }
					analytics_doc.obj['task']['id'] = url[3]
					analytics_doc.save();
					return 1
		except : 
			analytics_doc.action = {  "key" : "view" , "phrase" : "viewed a" }
			analytics_doc.obj['task']['id'] = url[3]
			analytics_doc.save();
			return 1

	return 0

def dashbard_activity(group_id,url,doc):
	analytics_doc = initialize_analytics_obj(doc, group_id, 'dashboard')
	try :
		if(url[3] == 'group') :
			try :
				group_name, group_id = get_group_name_id(url[1])
				if group_name != None :
					analytics_doc.action = {  "key" : "view" , "phrase" : "viewed dashboard of" }
					analytics_doc.obj['dashboard']['id'] = group_id
					analytics_doc.obj['dashboard']['name'] = group_name
					analytics_doc.save()
					return 1
				else :
					analytics_doc.action = {  "key" : "view" , "phrase" : "viewed User group's Dashboard" }
					analytics_doc.obj['dashboard']['id'] = url[1]
					analytics_doc.obj['dashboard']['name'] = doc[u'user']
					analytics_doc.save()
					return 1
			except :
				pass

	except :
		try :
			user = node_collection.find_one({ "_type": "Author", "created_by" : int(url[1])})
			try :
				analytics_doc.action = {  "key" : "view" , "phrase" : "viewed profile of" }
				analytics_doc.obj['dashboard']['id'] = url[1]
				analytics_doc.obj['dashboard']['name'] = user[u'name']
				analytics_doc.save();
				return 1

			except :
				pass
		except :
			pass
	return 0

def default_activity(group_id,url,doc):
	pass
	return 0

		













def event_activity(group_id,url,doc):
	return 0

def group_activity(group_id,url,doc):
	return 0

def image_activity(group_id,url,doc):
	return 0

def video_activity(group_id,url,doc):
	return 0




def Gid(group):
	group_id = group;
	ins_objectid = ObjectId()
	if ins_objectid.is_valid(group_id) is False:
		group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
		#auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
		if group_ins:
			group_id = str(group_ins._id)
		else:
			auth = node_collection.one({'_type': 'Author', 'name': group_id })
			if auth:
				group_id = str(auth._id)
			pass
	else:
		pass

	return group_id	


				
			
			



''' -- Imports from python libraries -- '''
import datetime
import json
import logging
import pymongo


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
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

	from gnowsys_ndf.settings import GSTUDIO_SITE_VIDEO, MEDIA_ROOT, WETUBE_USERNAME, WETUBE_PASSWORD  # , EXTRA_LANG_INFO, GAPPS
from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection
# from gnowsys_ndf.ndf.models import Node, GSystemType, File, GRelation, STATUS_CHOICES, Triple
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.methods import get_node_metadata, get_node_common_fields, set_all_urls  # , get_page
from gnowsys_ndf.ndf.views.methods import create_gattribute

col = db[Analytics.collection_name]


#logger = logging.getLogger(__name__)


def page_view(request):
	pass
	'''
	event = col.Benchmark()
	event["_type"] = u"analytics"
	event["name"] = u"analytics"

	transaction = { 'status' : None}

	try : 
		event.session_key = request.session.session_key
	except :
		transaction['status'] = 0
		transaction['message'] = 'Error retrieving the session key.'

	event.user = request.user.username
	event.time_taken = unicode(str(datetime.datetime.now()))
	
	try : 
		event.action = request.POST['action']
		event.calling_url = request.POST['resource']
	except : 
		transaction['status'] = 0
		transaction['message'] = 'Connot find action details.'

	if transaction['status'] == None : 
		transaction['status'] = 1
		transaction['message'] = 'transaction successful.'
		#transaction['event'] = event
	
	#inserting the event object in the Analytics collection.

	event.save()
	'''
	return HttpResponse("0")

def default(request, group_id):
	return HttpResponse(group_id)

connection = Connection()
db = connection['studio-dev']
collection = db['Benchmarks']

'''
db = get_database()
benchmark_collection = db['Benchmarks'].Benchmark
'''

def list_activities(request):
	try :
		start_date = request.POST['start_date']
		end_date = request.POST['end_date']
	except:
		start_date = datetime.datetime.now() - datetime.timedelta(7)
		end_date = datetime.datetime.now()
	
	query("user",{ "username" : request.user.username })
	a = db['Analytic_col'].find({"user" : request.user.username}).sort("timestamp",-1)
	
	lst = []
	for doc in a :
		lst.append(doc)
	
	return render_to_response ("ndf/analytics_list_details.html", { "data" : lst})


def session_summary(request):
	query("user",{ "username" : request.user.username })
	a = db['Analytic_col'].find({"user" : request.user.username}).sort("timestamp",-1)

	lst = []
	sessions_list =[]
	d={}
	i=-1
	
	for doc in a :
		print '\n'+str(doc)
		'''
		sk = str(doc.session_key)
		if i!=-1 and d['session_key']==sk :
			sessions_list[i]["end_date"] = doc.timestamp	
			sessions_list[i]["activities"]	+= 1
			sessions_list[i]["duration"] = sessions_list[i]["end_date"] - sessions_list[i]["start_date"]
		else :
			d= {}
			i+=1
			d["session_key"]=sk
			d["start_date"]	= doc.timestamp
			d["activities"]	= 1
			d["user"]	= doc.user
			sessions_list.append(d)
		'''
	
	return render_to_response("ndf/analytics_summary.html",
															{ "data" : sessions_list})




def group_analytics(request):
	query("group",{"group_id" : ObjectId("55717125421aa91eecbf8843")})

	return(HttpResponse ("Hi"))



	
Analytics_collection = db['Analytic_col']														
															
	


def query(analytics_type,details) :
	'''
	This function checks the Analytics data(for a user) in Analytic_col and gets the time to which the query set is updated. 
	Based on the time, it fetches raw data from Benchmark collection and hands over to normalize to do the filtering and redundancy check.
	
	In case, the analytics_type is 'group', the function resolves the members of the group and calls itself recursively for each user, to update the Analytic_col.
	
	'''

	if analytics_type == "user" :
		cursor = Analytics_collection.find({"user" : str(details['username']) }).sort("timestamp",-1).limit(1)
		latest_timestamp = datetime.datetime(1900,1,1)
		if cursor is None :
			pass
		else :
			for doc in cursor :
				latest_timestamp = doc['timestamp']
				break
		
		raw_data = collection.find({"user" : details['username'], "last_update": {"$gt":latest_timestamp}}).sort("last_update",-1)
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
					else :
						if doc[u'has_data']["GET"] == True :
							temp_doc = doc
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

				
def page_activity(group_id,url,doc):
	'''
	This function updates the Analytic_col database with the new activities done on the 
	page of MetaStudio, and also to see whether the page is published,deleted we
    check the status in the Nodes collection of database.
	And also we are assuming here that if the difference between the last update and created at 
	is less than 5 seconds then we should have created the page else we must have viewed the page.
	'''

	ins_objectid = ObjectId()
	analytics_doc=col.Analytics()
	analytics_doc.timestamp=doc[u'last_update']
	analytics_doc.user = doc[u'user'] 
	analytics_doc.session_key = doc[u'session_key']
	analytics_doc.group_id = group_id
	analytics_doc.action = [None]*5
	analytics_doc.args = [None]*5
	analytics_doc.action[1] = 'page'

	if ins_objectid.is_valid(url[3]) is False :
		if url[3] == "delete":
			if ins_objectid.is_valid(url[4]) is True:
				n = node_collection.find_one({"_id":ObjectId(url[4])})
				if n['status']=="HIDDEN" or n['status']=="DELETED":
					analytics_doc.action = ["deleted","page"]
					analytics_doc.args[1] = str(url[3])
					analytics_doc.save()
					return 1
	else :
		try : 
			n = node_collection.find_one({"_id":ObjectId(url[3])})
			author_id = n[u'created_by']
			auth=node_collection.find_one({"_type": "Author", "created_by": author_id})
			if auth[u'name']==doc[u'user']:
				created_at = n[u'created_at']
					
			if (doc[u'last_update'] - created_at).seconds < 5 :
				analytics_doc.action[0] = "created"
				analytics_doc.args[1] = str(url[3])
				analytics_doc.save()
				return 1
			else :
				analytics_doc.action[0] = "viewed"
				analytics_doc.args[1] = str(url[3])
				analytics_doc.save()
				return 1
		
			if  url[3] == "page_publish" :
				if ins_objectid.is_valid(url[4]) is True:
					n=node_collection.find_one({"_id":ObjectId(url[4])})
					if n['status']=="PUBLISHED" :
						analytics_doc.action[0] = "published"
						analytics_doc.args[1] = str(url[3])
						analytics_doc.save()
						return 1

			if url[3] =="edit" :
				if doc[u'has_data'] and doc[u'has_data']["POST"] == True :
					analytics_doc.action[0] = 'edit'
					analytics_doc.args[3] = str(url[4]);
					analytics_doc.save();
					return 1
		except Exception :
			analytics_doc.action = ["no action"]
			analytics_doc.save()
			return 1

		
	return 0

	
def file_activity(group_id,url,doc):
	ins_objectid= ObjectId()
	analytics_doc=col.Analytics()
	analytics_doc.timestamp=doc[u'last_update']
	analytics_doc.user = doc[u'user'] 
	analytics_doc.group_id = group_id
	analytics_doc.action=[None]*5
	analytics_doc.args=[None]*5
	analytics_doc.action[2]="file"

	
	
	if(url[3]=="submit"):
		analytics_doc.action[0]="upload"
		
		
	elif(url[3]=="readDoc"):
		analytics_doc.action[0]="download"
		analytics_doc.action[3]=url[5]
		analytics_doc.args[2]=str(url[4])

	elif url[3]=="details":
		if(ins_objectid.is_valid(url[4])):
			n=node_collection.find_one({"_id":ObjectId(url[4])})
			try :
				analytics_doc.args[2]=str(url[4])
				analytics_doc.action[0]="view"
				analytics_doc.action[1]=str(n[u"mime_type"])
				analytics_doc.action[3]=str(n[u"name"]) 
			except Exception :
				return 0

	elif(ins_objectid.is_valid(url[3])):
		n=node_collection.find_one({"_id":ObjectId(url[3])})
		try :
			analytics_doc.action[0] = "view"
			analytics_doc.args[2] = str(url[3])
			analytics_doc.action[1] = str(n[u"mime_type"]) 
			analytics_doc.action[3] = str(n[u"name"]) 
		except Exception :
			return 0

	elif(url[3]=="delete"):
			if ins_objectid.is_valid(url[4]) is True:
				n=node_collection.find_one({"_id":ObjectId(url[4])})
				if n['status']=="HIDDEN" or n['status']=="DELETED":
					analytics_doc.action[0]="delete"
					analytics_doc.args[2]=str(url[4])
	
	elif(url[3]=="edit" or url[3]=="edit_file"):
			if ins_objectid.is_valid(url[4]) is True:
				analytics_doc.action[0] = "edit"
				analytics_doc.args[2] = str(url[4])
	else:
		return 0

	
	analytics_doc.save()
	return 0

def forum_activity(group_id,url,doc):
	ins_objectid = ObjectId()
	analytics_doc=col.Analytics()
	analytics_doc.timestamp=doc[u'last_update']
	analytics_doc.user = doc[u'user'] 
	analytics_doc.session_key = doc[u'session_key']
	analytics_doc.group_id = group_id
	analytics_doc.action = [None]*5
	analytics_doc.args = [None]*5
	analytics_doc.action[3] = 'forum'
	
	if ins_objectid.is_valid(url[3]) is False:
		if(url[3]=="delete"):
			if ins_objectid.is_valid(url[4]) is True:
				n=node_collection.find_one({"_id":ObjectId(url[4])})
				if n['status']=="HIDDEN" or n['status']=="DELETED":
					analytics_doc.action[0] = 'delete'
					analytics_doc.args[3] = url[4];
					analytics_doc.save();
					return 1
			elif url[4]=="thread":
				if ins_objectid.is_valid(url[6]) is True:
					n=node_collection.find_one({"_id":ObjectId(url[6])})
					if n['status']=="HIDDEN" or n['status']=="DELETED":
						analytics_doc.action[0] = 'delete'
						analytics_doc.action[2] = 'thread'
						analytics_doc.args[2] = url[6];
						analytics_doc.args[3] = url[5];
						analytics_doc.save();
						return 1

			elif url[4]=="reply":
				if ins_objectid.is_valid(url[7]) is True:
					n=node_collection.find_one({"_id":ObjectId(url[7])})
					if n['status']=="HIDDEN" or n['status']=="DELETED":
						analytics_doc.action[0] = 'delete'
						analytics_doc.action[2] = 'thread'
						analytics_doc.action[1] = 'reply'
						analytics_doc.args[1] = url[7];
						analytics_doc.args[2] = url[6];
						analytics_doc.args[3] = url[5];
						analytics_doc.save();
						return 1

		elif url[3]=="thread" :
			try :
				if ins_objectid.is_valid(url[4]) is True:
					analytics_doc.action[0] = 'view'
					analytics_doc.action[2] = 'thread'
					analytics_doc.args[2] = str(url[4]);
					analytics_doc.save();
					return 1
			except :
				pass

		elif url[3]=="edit_forum" :
			if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
				analytics_doc.action[0] = 'edit'
				analytics_doc.args[3] = str(url[4]);
				analytics_doc.save();
				return 1

		elif url[3]=="edit_thread" :
			if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
				analytics_doc.action[0] = 'edit'
				analytics_doc.action[2] = 'thread'
				analytics_doc.args[3] = str(url[4]);
				analytics_doc.args[2] = str(url[5]);
				analytics_doc.save();
				return 1

		elif url[3] == 'add_node' :
			if u'has_data' in doc.keys() and doc[u'has_data']["POST"] == True :
				analytics_doc.action[0] = 'add'
				analytics_doc.action[3] = 'reply'
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
								forums = node_collection.find({"url" : "forum/thread" , "created_by" : author[u'created_by']})
								print forums;
								for created_forums in forums : 
									if (doc[u'last_update'] - created_forums[u'created_at']).seconds < 5 : 
										analytics_doc.action[0] = 'crete'
										analytics_doc.action[2] = 'thread'
										analytics_doc.args[2] = str(created_forums[u'_id']);
										analytics_doc.args[3] = url[3];
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
					analytics_doc.action[0] = 'create'
					analytics_doc.args[3] = url[3];
					analytics_doc.save();
					return 1
				else :
					analytics_doc.action[0] = 'view'
					analytics_doc.args[3] = url[3];
					analytics_doc.save();
					return 1

	return 0

def course_activity(group_id,url,doc):
	return 0

def task_activity(group_id,url,doc):
	return 0

def event_activity(group_id,url,doc):
	return 0

def dashbard_activity(group_id,url,doc):
	return 0

def group_activity(group_id,url,doc):
	return 0

def image_activity(group_id,url,doc):
	return 0

def video_activity(group_id,url,doc):
	return 0

def default_activity(group_id,url,doc):
	pass
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


				
			
			



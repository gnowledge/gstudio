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
	
	a = collection.find({"user" : request.user.username, "last_update": {"$gt":start_date,"$lt":end_date}}).sort("last_update",-1)
	
	lst = []
	for doc in a :
		lst.append(doc)
	#print a

	#print(lst[0][u'user'])
	#print(a.toArray())



	return render_to_response ("ndf/analytics_list_details.html",
															{ "data" : lst})

def session_summary(request):
	a = collection.find({"user" : request.user.username}).sort("last_update",-1)
	print a
	lst = []
	sessions_list =[]
	d={}
	i=-1
	#normalize(a)
	'''
	for doc in a :
		#print '\n'+str(doc)
		lst.append(doc)
		sk = str(doc[u"session_key"])
		if i!=-1 and d['session_key']==sk :
			sessions_list[i]["end_date"]	= doc[u"last_update"]		
			sessions_list[i]["activities"]	+= 1
			sessions_list[i]["duration"] = sessions_list[i]["end_date"] - sessions_list[i]["start_date"]
		else :
			d= {}
			i+=1
			d["session_key"]=sk
			d["start_date"]	= doc[u"last_update"]
			d["activities"]	= 1
			d["user"]	= doc[u"user"]
			sessions_list.append(d)
	'''
	query("user", {"username" : request.user.username})

	return render_to_response("ndf/analytics_summary.html",
															{ "data" : sessions_list})

	
Analytics_collection = db['Analytic_col']														
															
						
# to see the data in analytics  
def query(analytics_type,details) :
	
	if analytics_type == "user" :
		a = Analytics_collection.find({"user" : str(details['username']) }).sort("timestamp",-1).limit(1)
		timestamp = datetime.datetime(1900,1,1)
		if a is None :
			pass
		else :
			for doc in a :
				#print doc['timestamp']
				timestamp = doc['timestamp']
				break
		a = collection.find({"user" : details['username'], "last_update": {"$gt":timestamp}}).sort("last_update",-1)
		if a is None:
			print "your Analytics is up to date"
		else :
			normalize(a)

	else :
		group_id = details['group_id']	
		n = node_collection.find_one({"_id" : group_id})
		if n is not None :
			member_list = n[u'author_set'] + n[u'group_admin']
			for member in member_list :
				author_name = node_collection.find_one({"_type" : "Author", "created_by" : int(member)})
				if author_name is not None :
					#print author_name[u'name']
					query("user",{"username" : author_name[u'name'] })

def group_analytics(request):
	query("group",{"group_id" : ObjectId("5583c42b9e745633325439d0")})

	return(HttpResponse ("Hi"))





															
def normalize(a) :
	a=a.sort("last_update",1)
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
				#"image": image_activity,
				#"video": video_activity,
		}.get(gapp,default_activity)

	segre1 = ["file/thumbnail",'None','',"home", "image/get_mid_size_img"]
	temp_doc = { u"calling_url" : None , u'last_update' : datetime.datetime(1900, 1, 1, 11, 19, 54)}
	for doc in a :
		#removing the doc with useless urls
		if 'ajax' in str(doc[u'action']) or str(doc[u'action']) in segre1 :
			pass
		else :
			# removing the redundant sequence of docs

			# refining the data based on the calling url, session key, and the time between accessing reourse
			if temp_doc[u'calling_url'] == doc[u'calling_url']  and (doc[u'last_update'] - temp_doc[u'last_update'] < datetime.timedelta(0,300)):
				
				# prioritizing between the docs based on the POST and GET data
				if u'has_data' in doc.keys() and bool(doc[u'has_data']) == 1 :
					if doc[u'has_data']["POST"] :
						temp_doc = doc
					else :
						if doc[u'has_data']["GET"] :
							temp_doc = doc
				else :
					temp_doc = doc
			
			else :
				if temp_doc[u'calling_url'] != None :
					#print temp_doc[u'calling_url']
					try :
						pass
						#print temp_doc[u'has_data']
					except : 
						pass
					url = str(temp_doc[u'calling_url']).split("/")
					group_id = Gid(url[1])
					gapp = url[2]
					gapp_list(gapp)(group_id,url,temp_doc)
				
				temp_doc = doc
			
		

					
		#gapp_list(gapp)(url,prev_url,doc[u'last_update'],doc[u'user'])
				
		
				



			
	return 0


def page_activity(group_id,url,doc):
	pass
	'''
	ins_objectid = ObjectId()
	if ins_objectid.is_valid(url[3]) is False:
		if url[3] == "delete":
			if ins_objectid.is_valid(url[4]) is True:
				n=node_collection.find_one({"_id":ObjectId(url[4])})
				if n['status']=="HIDDEN" or n['status']=="DELETED":
					print "you deleted a page"


	else :
		try : 
			n = node_collection.find_one({"_id":ObjectId(url[3])})
			author_id = n[u'created_by']
			auth=node_collection.find_one({"_type": "Author", "created_by": author_id})
			if auth[u'name']==user:
				created_at = n[u'created_at']
			#print (last_update - created_at).seconds
			
			if (last_update - created_at).seconds < 5 :
				print "You created a page"
			else :
				print "You viewed a page"
		except :
			pass
	
		if  url[3] == "page_publish" :
			if ins_objectid.is_valid(url[4]) is True:
				n=node_collection.find_one({"_id":ObjectId(url[4])})
				if n['status']=="PUBLISHED" :
					print "you published a page"


		
		'''

		
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
		analytics_doc.action[0]="Uploaded "
		
		

	elif(url[3]=="readDoc"):
		analytics_doc.action[0]="Downloaded "
		analytics_doc.action[3]=url[5]
		analytics_doc.args[2]=str(url[4])

	elif url[3]=="details":
		if(ins_objectid.is_valid(url[4])):
			n=node_collection.find_one({"_id":ObjectId(url[4])})
			try :
				analytics_doc.args[2]=str(url[4])
				analytics_doc.action[0]="viewed "
				analytics_doc.action[1]=str(n[u"mime_type"]) + "  "
				analytics_doc.action[3]=str(n[u"name"]) + " "
			except Exception :
				return 0

	elif(ins_objectid.is_valid(url[3])):
		n=node_collection.find_one({"_id":ObjectId(url[3])})
		try :
			analytics_doc.action[0] = "viewed "
			analytics_doc.args[2] = str(url[3])
			analytics_doc.action[1] = str(n[u"mime_type"]) + "  "
			analytics_doc.action[3] = str(n[u"name"]) + " "
		except Exception :
			return 0

	elif(url[3]=="delete"):
			if ins_objectid.is_valid(url[4]) is True:
				n=node_collection.find_one({"_id":ObjectId(url[4])})
				if n['status']=="HIDDEN" or n['status']=="DELETED":
					analytics_doc.action[0]="Deleted "
					analytics_doc.args[2]=str(url[4])
	
	elif(url[3]=="edit" or url[3]=="edit_file"):
			if ins_objectid.is_valid(url[4]) is True:
				analytics_doc.action[0] = "Edited"
				analytics_doc.args[2] = str(url[4])
	else:
		return 0

	
	analytics_doc.save()
	
	return 0


def forum_activity(group_id,url,doc):
	pass
	'''ins_objectid= ObjectId()
	analytics_doc=col.Analytics()
	analytics_doc.timestamp=doc[u'last_update']
	analytics_doc.user = doc[u'user'] 
	

	if ins_objectid.is_valid(url[3]) is False:
		if(url[3]=="delete"):
			if ins_objectid.is_valid(url[4]) is True:
				n=node_collection.find_one({"_id":ObjectId(url[4])})
				if n['status']=="HIDDEN" or n['status']=="DELETED":
					analytics_doc.action="Deleted a forum"
					 

			elif url[4]=="thread":
				if ins_objectid.is_valid(url[6]) is True:
					n=node_collection.find_one({"_id":ObjectId(url[6])})
					if n['status']=="HIDDEN" or n['status']=="DELETED":
						analytics_doc.action="Deleted a forum ka thread"

			elif url[4]=="reply":
				if ins_objectid.is_valid(url[7]) is True:
					n=node_collection.find_one({"_id":ObjectId(url[7])})
					if n['status']=="HIDDEN" or n['status']=="DELETED":
						analytics_doc.action="Deleted a forum ka thread ka reply"

	else:
		n=node_collection.find_one({"_id":ObjectId(url[3])})
		author_id=n[u'created_by']
		auth=node_collection.find_one({"_type": "Author", "created_by": author_id})
		if auth[u'name']==user:
			created_at = n[u'created_at']
			#print (last_update - created_at).seconds
			if (last_update - created_at).seconds < 5 :
				print "You created a forum"
			else :
				print "You viewed a forum"
'''
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


				
			
			



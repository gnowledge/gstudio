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
	#print a
	lst = []
	sessions_list =[]
	d={}
	i=-1
	normalize(a)
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


	return render_to_response("ndf/analytics_summary.html",
															{ "data" : sessions_list})
															
															
															
															
def normalize(a) :
	a=a.sort("last_update",1)
	def gapp_list(gapp):
		return {
				"page": page_acti,
				"file": file_acti,
				"course": course_acti,
				"forum": forum_acti,
				"task": task_acti,
				"event": event_acti,
				"dashboard": dashbard_acti,
				"group": group_acti,
				#"image": image_acti,
				#"video": video_acti,
		}.get(gapp,default_acti)

	segre1 = ["file/thumbnail",'None','']
	prev_calling_url=""
	for doc in a :
		
		if 'ajax' in str(doc[u'action']) or str(doc[u'action']) in segre1 :
			pass

		else :

			if doc[u'calling_url']==prev_calling_url :
				pass
			else :
				#prev_url = prev_calling_url.split("/")
				url = str(doc[u'calling_url']).split("/")			
				group_id = Gid(url[1])
				gapp = url[2]

				#print gapp
				#print doc[u'calling_url']

				
				#gapp_list(gapp)(url,prev_url,doc[u'last_update'],doc[u'user'])
			
				gapp_list(gapp)(url,doc[u'last_update'],doc[u'user'])
				prev_calling_url=doc[u'calling_url']


	return 0


def page_acti(url,last_update,user):
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
			print (last_update - created_at).seconds
			print last_update
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


		''' elif ins_objectid.is_valid(url[3]) is True:
				n=node_collection.find_one({"_id":ObjectId(url[3])})
				if url[4] == "translate" :
					print "you translated a page"
	'''


		
	return 0

	
def file_acti(url,last_update,user):
	ins_objectid= ObjectId()
	analytics_doc=col.Analytics()
	analytics_doc.timestamp=last_update
	print last_update

	if(url[3]=="submit"):
		print "you uploaded a file"
		analytics_doc.action="you uploaded a file"
		

	#elif(url[3]=="uploadDoc"):
		#pass
	elif(url[3]=="readDoc"):
		print "you downloaded the doc "+ url[5]
		analytics_doc.action="you downloaded a file"

	elif url[3]=="details":
		if(ins_objectid.is_valid(url[4])):
			n=node_collection.find_one({"_id":ObjectId(url[4])})
			try :
				print "you viewed a " + str(n[u"mime_type"]) + "  " + str(n[u"name"])
				analytics_doc.action="you viewed a file"
			except Exception :
				pass

	elif(ins_objectid.is_valid(url[3])):
		n=node_collection.find_one({"_id":ObjectId(url[3])})
		try :
			print "you viewed a " + str(n[u"mime_type"]) + "  " + str(n[u"name"])
			analytics_doc.action="you viewed a file"
		except Exception :
			pass
	elif(url[3]=="delete"):
			if ins_objectid.is_valid(url[4]) is True:
				n=node_collection.find_one({"_id":ObjectId(url[4])})
				if n['status']=="HIDDEN" or n['status']=="DELETED":
					print "you deleted a file"
					analytics_doc.action="you deleted a file"
	elif(url[3]=="edit" or url[3]=="edit_file"):
			if ins_objectid.is_valid(url[4]) is True:
				print "you edited a file"
				analytics_doc.action="you edited a file"
	else:
		analytics_doc.action="no action"
	analytics_doc.save()
	
	return 0


def forum_acti(url,last_update,user):
	
	ins_objectid = ObjectId()
	if ins_objectid.is_valid(url[3]) is False:
		if(url[3]=="delete"):
			if ins_objectid.is_valid(url[4]) is True:
				n=node_collection.find_one({"_id":ObjectId(url[4])})
				if n['status']=="HIDDEN" or n['status']=="DELETED":
					print "you deleted a forum"

			elif url[4]=="thread":
				if ins_objectid.is_valid(url[6]) is True:
					n=node_collection.find_one({"_id":ObjectId(url[6])})
					if n['status']=="HIDDEN" or n['status']=="DELETED":
						print "you deleted a forum ka thread"

			elif url[4]=="reply":
				if ins_objectid.is_valid(url[7]) is True:
					n=node_collection.find_one({"_id":ObjectId(url[7])})
					if n['status']=="HIDDEN" or n['status']=="DELETED":
						print "you deleted a forum ka thread ka reply"

	else:
		n=node_collection.find_one({"_id":ObjectId(url[3])})
		author_id=n[u'created_by']
		auth=node_collection.find_one({"_type": "Author", "created_by": author_id})
		if auth[u'name']==user:
			created_at = n[u'created_at']
			print (last_update - created_at).seconds
			if (last_update - created_at).seconds < 5 :
				print "You created a forum"
			else :
				print "You viewed a forum"

	return 0

def course_acti(url,last_update,user):
	return 0

def task_acti(url,last_update,user):
	return 0

def event_acti(url,last_update,user):
	return 0

def dashbard_acti(url,last_update,user):
	return 0

def group_acti(url,last_update,user):
	return 0

def image_acti(url,last_update,user):
	return 0

def video_acti(url,last_update,user):
	return 0

def default_acti(url,last_update,user):
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


				
			
			



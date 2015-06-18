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

col = db[Benchmark.collection_analytics]
#logger = logging.getLogger(__name__)


def page_view(request):

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

	return HttpResponse(json.dumps(transaction))

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
'''
def activities_summary(request):
	a = collection.find({"user" : request.user.username}).sort("last_update",1)
	lst = []
	sessions_list ={}
	for doc in a :
		#print '\n'+str(doc)
		lst.append(doc)
		sk = str(doc[u"session_key"])	
		if sk in sessions_list.keys():
			sessions_list[sk]["end_date"]	= doc[u"last_update"]		
			sessions_list[sk]["activities"]	+= 1
			sessions_list[sk]["duration"] = sessions_list[sk]["end_date"] - sessions_list[sk]["start_date"]
		else :
			sessions_list[sk]	= {}
			sessions_list[sk]["start_date"]	= doc[u"last_update"]
			sessions_list[sk]["activities"]	= 1
			#print str(sessions_list)+'\n'

	#print sessions_list

	return render_to_response("ndf/analytics_summary.html",
															{ "data" : sessions_list})
'''
def activities_summary(request):
	a = collection.find({"user" : request.user.username}).sort("last_update",1)
	lst = []
	sessions_list =[]
	d={}
	i=-1
	
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
			sessions_list.append(d)


	return render_to_response("ndf/analytics_summary.html",
															{ "data" : sessions_list})

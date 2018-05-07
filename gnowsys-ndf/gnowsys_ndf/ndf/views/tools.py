''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
import os
from django.http import StreamingHttpResponse

''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from django.http import Http404
from collections import OrderedDict
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.ndf.views.methods import get_execution_time
''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection, NodeJSONEncoder,Author, Buddy

def tools_logging(request):

	#Method for tools logging
	userdata = request.POST.get('payload',None)
	user_data_old_strategy = request.POST.get('user_data',None)
	if userdata!= None:
		userdata = json.loads(userdata)
		# app_name = request.POST.get('app_name',' ')
		app_name = userdata['appName']
		sessionid = ""
		sessionid = request.COOKIES.get("sessionid")
		old_data = []
		buddies_authid_list = request.session.get('buddies_authid_list', [])
		buddy_id_list = []
		buddy_id_list.append(userdata['userId'])
		userdata['sessionId'] = sessionid 
		if buddies_authid_list:
		    buddy_id_list = buddy_id_list +  Author.get_user_id_list_from_author_oid_list(buddies_authid_list)
		if userdata['userId'] and userdata['userId']!= "None":
		    if not os.path.exists('/data/gstudio_tools_logs/'+app_name):
		        os.makedirs('/data/gstudio_tools_logs/'+app_name)
		   
		    for each_id in buddy_id_list:
		        old_data = []
		        if os.path.exists('/data/gstudio_tools_logs/'+app_name+'/'+str(each_id)+"-"+app_name+'.json'):
		            with open('/data/gstudio_tools_logs/'+app_name+'/'+str(each_id)+"-"+app_name+'.json' ) as rfile:
		                if os.stat('/data/gstudio_tools_logs/'+app_name+'/'+str(each_id)+"-"+app_name+'.json').st_size != 0:
		                    old_data = json.load(rfile)
		       
		        with open('/data/gstudio_tools_logs/'+app_name+'/'+str(each_id)+"-"+app_name+'.json', 'w'): pass
		           
		       
		        with open('/data/gstudio_tools_logs/'+app_name+'/'+str(each_id)+"-"+app_name+'.json', 'w') as wrfile:
		            old_data.append(userdata)
		            json.dump(old_data, wrfile)   

		return StreamingHttpResponse("Success")    	


	elif user_data_old_strategy != None:
		userdata = json.loads(user_data_old_strategy,object_pairs_hook=OrderedDict)
		app_name = request.POST.get('app_name','')
		old_data = []
		sessionid = ""
		sessionid = request.COOKIES.get("sessionid")
		userdata['sessionId'] = sessionid
		buddies_authid_list = request.session.get('buddies_authid_list', [])
		buddy_id_list = []
		buddy_id_list.append(userdata['user_id'])
		if buddies_authid_list:
		    buddy_id_list = buddy_id_list +  Author.get_user_id_list_from_author_oid_list(buddies_authid_list)
		if userdata['user_id'] and userdata['user_id']!= "None":
		    if not os.path.exists('/data/gstudio_tools_logs/'+app_name):
		        os.makedirs('/data/gstudio_tools_logs/'+app_name)
		   
		    for each_id in buddy_id_list:
		        old_data = []
		        if os.path.exists('/data/gstudio_tools_logs/'+app_name+'/'+str(each_id)+'-'+app_name+'.json'):
		            with open('/data/gstudio_tools_logs/'+app_name+'/'+str(each_id)+'-'+app_name+'.json') as rfile:
		                if os.stat('/data/gstudio_tools_logs/'+app_name+'/'+str(each_id)+'-'+app_name+'.json').st_size != 0:
		                    old_data = json.load(rfile)
		       
		        with open('/data/gstudio_tools_logs/'+app_name+'/'+str(each_id)+'-'+app_name+'.json', 'w'): pass
		           
		       
		        with open('/data/gstudio_tools_logs/'+app_name+'/'+str(each_id)+'-'+app_name+'.json', 'w') as wrfile:
		            old_data.append(userdata)
		            json.dump(old_data, wrfile)   
		return StreamingHttpResponse("Success")
	else:
		return StreamingHttpResponse("Failure")
@get_execution_time
def tools_temp(request):
    context_variables = {'title' : "tools"}
    return render_to_response(
        'ndf/tools_list.html',
                                  context_variables,
        context_instance=RequestContext(request)
    )


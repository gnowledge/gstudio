''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
import os
from django.http import StreamingHttpResponse

''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from django.http import Http404

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection, NodeJSONEncoder

def tools_logging(request):

	#test method for tools logging
	userdata = json.loads(request.GET.get('user_data',' '))
	print "userdata++++++++++++++++",userdata
	app_name = request.GET.get('app_name',' ')
	old_data = []
	new_data = []
	if userdata['user_id']:
		if not os.path.exists('/data/gstudio_tools_logs/'+app_name+'/'+userdata['params']['language']):
			os.makedirs('/data/gstudio_tools_logs/'+app_name+'/'+userdata['params']['language'])
		
		if os.path.exists('/data/gstudio_tools_logs/'+app_name+'/'+userdata['params']['language']+'/'+userdata['user_id']+'.json'):
			with open('/data/gstudio_tools_logs/'+app_name+'/'+userdata['params']['language']+'/'+userdata['user_id']+'.json') as rfile:
				if os.stat('/data/gstudio_tools_logs/'+app_name+'/'+userdata['params']['language']+'/'+userdata['user_id']+'.json').st_size != 0:
					old_data = json.load(rfile)
					print "old_data--------------------",old_data,type(old_data)
		with open('/data/gstudio_tools_logs/'+app_name+'/'+userdata['params']['language']+'/'+userdata['user_id']+'.json', 'w') as wrfile:
			new_data = old_data.append(userdata)
			print "new_data--------------------",new_data,type(new_data),old_data
			json.dump(old_data, wrfile)
			# if not old_data:
			# 	json.dump(userdata, wrfile)
			# else:
	
	return StreamingHttpResponse("Success")	

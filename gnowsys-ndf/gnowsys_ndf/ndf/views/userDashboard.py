''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext


from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_drawers


#######################################################################################################################################

db = get_database()
gs_collection = db[GSystem.collection_name]


#######################################################################################################################################
#                                                                     V I E W S   D E F I N E D   F O R   U S E R   D A S H B O A R D
#######################################################################################################################################

def dashboard(request, group_id, user):	

  	ID = User.objects.get(username=user).pk

	date_of_join = User.objects.get(username=user).date_joined
	group=gs_collection.GSystem.one({'_id':ObjectId(group_id)})
	page_drawer = get_drawers(group.name,None,None,"Page")
	image_drawer = get_drawers(group.name,None,None,"Image")
	video_drawer = get_drawers(group.name,None,None,"Video")
	file_drawer = get_drawers(group.name,None,None,"File")
	quiz_drawer = get_drawers(group.name,None,None,"OnlyQuiz")
	group_drawer = get_drawers(None,None,None,"Group")
	forum_drawer = get_drawers(group.name,None,None,"Forum")
	
	obj = gs_collection.GSystem.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'created_by': int(ID) ,'group_set': {'$all': [group.name]}})
	collab_drawer = []	

	for each in obj.sort('last_update', -1):  	# To populate collaborators according to their latest modification of particular resource
		for val in each.modified_by:
			name = User.objects.get(pk=val).username 		
			collab_drawer.append(name)			
		

	return render_to_response("ndf/userDashboard.html",{'username': user, 'user_id': ID, 'DOJ': date_of_join, 
														'page_drawer':page_drawer,'image_drawer': image_drawer,
														'video_drawer':video_drawer,'file_drawer': file_drawer,
														'quiz_drawer':quiz_drawer,'group_drawer': group_drawer,														
														'forum_drawer':forum_drawer,'collab_drawer': collab_drawer
														},context_instance=RequestContext(request))

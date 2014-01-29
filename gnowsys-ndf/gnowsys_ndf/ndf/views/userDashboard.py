''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.methods import get_node_common_fields
from gnowsys_ndf.ndf.views.methods import get_drawers


#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
gst_page = collection.Node.one({'_type': u'GSystemType', 'name': GAPPS[0]})
history_manager = HistoryManager()
rcs = RCS()

#######################################################################################################################################
#                                                                     V I E W S   D E F I N E D   F O R   U S E R   D A S H B O A R D
#######################################################################################################################################

def dashboard(request, group_name, user):

	page_created = None
  	page_contributed = None
  	image_created = None 
  	image_contributed = None

  	ID = User.objects.get(username=user).pk

	date_of_join = User.objects.get(username=user).date_joined
	
	page_drawer = get_drawers(None,None,None,"Page")
	image_drawer = get_drawers(None,None,None,"Image")
	video_drawer = get_drawers(None,None,None,"Video")
	file_drawer = get_drawers(None,None,None,"File")

	

	return render_to_response("ndf/userDashboard.html",{'username': user, 'user_id': ID, 'DOJ': date_of_join, 
														'page_drawer': page_drawer,'image_drawer': image_drawer,
														'video_drawer':video_drawer,'file_drawer': file_drawer
														},context_instance=RequestContext(request))
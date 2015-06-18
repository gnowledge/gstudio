''' -- Imports from python libraries -- '''
import datetime
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import get_valid_filename
from django.core.files.move import file_move_safe
from django.core.files.temp import gettempdir
from django.core.files.uploadedfile import UploadedFile # django file handler
# from django.contrib.auth.models import User
from mongokit import paginator
from gnowsys_ndf.settings import GSTUDIO_SITE_VIDEO, EXTRA_LANG_INFO, GAPPS, MEDIA_ROOT, WETUBE_USERNAME, WETUBE_PASSWORD
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.methods import get_node_metadata, get_page, get_node_common_fields, set_all_urls,get_execution_time
from gnowsys_ndf.ndf.views.methods import get_group_name_id
from gnowsys_ndf.ndf.models import Node, GSystemType, File, GRelation, STATUS_CHOICES, Triple

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

def page_view(request):
	transaction = { 'status' : None}
	event = {}

	try : 
		event['session_key'] = request.session.session_key
	except :
		transaction['status'] = 0
		transaction['message'] = 'Error retrieving the session key.'

	event['user'] = request.user.username
	event['timestamp'] = str(datetime.datetime.now())
	
	try : 
		event['action'] = request.POST['action']
		event['resource'] = request.POST['resource']
	except : 
		transaction['status'] = 0
		transaction['message'] = 'Connot find action details.'

	if transaction['status'] == None : 
		transaction['status'] = 1
		transaction['message'] = 'transaction successfull.'
		transaction['event'] = event
	

	return HttpResponse(json.dumps(transaction))

def default(request, group_id):
	return HttpResponse(group_id)
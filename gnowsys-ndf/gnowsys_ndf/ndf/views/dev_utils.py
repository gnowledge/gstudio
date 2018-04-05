''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
import subprocess

''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from django.http import Http404, HttpResponse

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection, NodeJSONEncoder


import re
import urllib

''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response
from django.template import RequestContext
#from mongokit import paginator
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
# from gnowsys_ndf.ndf.models import Node, GRelation,GSystemType,File,Triple
from gnowsys_ndf.ndf.models import Node, GRelation,GSystemType, Triple
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.file import *


from gnowsys_ndf.ndf.views.methods import get_group_name_id, cast_to_data_type, get_execution_time
from gnowsys_ndf.ndf.views.methods import get_filter_querydict


GST_PAGE = node_collection.one({'_type':'GSystemType', 'name': 'page'})
GST_IMAGE = node_collection.one({'_type':'GSystemType', 'name': 'image'})
GST_VIDEO = node_collection.one({'_type':'GSystemType', 'name': GAPPS[4]})
e_library_GST = node_collection.one({'_type':'GSystemType', 'name': 'E-Library'})
pandora_video_st = node_collection.one({'_type':'GSystemType', 'name': 'Pandora_video'})
app = node_collection.one({'_type':'GSystemType', 'name': 'E-Library'})
wiki_page = node_collection.one({'_type': 'GSystemType', 'name': 'Wiki page'})
GST_JSMOL = node_collection.one({"_type":"GSystemType","name":"Jsmol"})


def query_doc(request, doc_id_or_name=None, option=None):

	if ObjectId.is_valid(doc_id_or_name):
		doc_id_or_name = ObjectId(doc_id_or_name)

	query_res = node_collection.find({
								'$or': [
										{'_id': doc_id_or_name},
										{'name': unicode(doc_id_or_name)}
									]
								})

	result = []
	for each_doc in query_res:
		if option in ['nbh', 'NBH', 'get_neighbourhood']:
			each_doc.get_neighbourhood(each_doc.member_of)
		result.append(json.dumps(each_doc, cls=NodeJSONEncoder, sort_keys=True))

	return render_to_response('ndf/dev_query_doc.html',
					        {'result': result, 'query': doc_id_or_name, 'count': query_res.count()},
					        context_instance=RequestContext(request)
						    )


def render_test_template(request,group_id='home', app_id=None, page_no=1):



	return render_to_response(
        'ndf/test_template.html',
        {'title': title		 },

        context_instance=RequestContext(request)
    )


def git_branch(request):
	return HttpResponse(subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']),
		content_type="text/plain")
	
def git_misc(request, git_command):
	response = "Unsupported"
	if git_command in ['log', 'branch', 'status', 'tag', 'show', 'diff']:
		response = subprocess.check_output(['git', git_command])
	return HttpResponse(response, content_type="text/plain")


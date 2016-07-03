''' -- Imports from python libraries -- '''
import datetime
import json
import pymongo
import re

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, render
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
from django.views.decorators.csrf import csrf_exempt
from gnowsys_ndf.ndf.models import *
from pymongo import Connection
from gnowsys_ndf.ndf.views.methods import create_grelation

def map_view(request,group_id):
	return render_to_response("ndf/map_india.html",{ 'group_id':group_id, 'groupid':group_id}
		, context_instance=RequestContext(request))

@csrf_exempt
def add_organization(request,group_id,node_id=None):
	org_node = node_collection.find({'_type':'GSystemType','name':'Organization'});
	if request.method=="POST":
			organization = json.loads(request.body)
			organization_node = ""
			if node_id:
				organization_node = node_collection.find({'_id':ObjectId(str(node_id))})
			if not organization_node:
				organization_node = node_collection.collection.GSystem();
				organization_node['member_of'] = [org_node[0]._id]
				organization_node['created_by'] = request.user.id
				organization_node['tags'].append(u'state_analytics')
				organization_node['group_set'] = group_id
			state_id = request.POST.get('state_id','')
			if state_id:
				state_node = node_collection.one({'_id': ObjectId(state_id)})
				organization_belongs_to_state_rt = node_collection.one({'_type': 'RelationType', 'name': u'organization_belongs_to_state'})
				create_grelation(organization_node._id, organization_belongs_to_state_rt  ,state_node._id)

			organization_node['name'] = organization['properties']['name']
			organization_node['modified_by'] = request.user.id
			organization_node['location'] = organization['coordinates']
			organization_node.save()
			return HttpResponse(json.dumps({'status':200,'message':'OK'}))
	else:
		return HttpResponse("Not POST")
				
@csrf_exempt
def fetch_organization(request,group_id=None):
	organization_list = node_collection.find({'tags':[u'state_analytics']})
	result = []
	temp = {
		'id':'',
		'properties':{},
		'coordinates':[]
	}
	for organization in organization_list:
		temp['id'] = str(organization._id)
		temp['properties']['name'] = organization.name
		temp['coordinates'] = organization.origin
		result.append(json.dumps(temp))
	return HttpResponse(json.dumps(result))
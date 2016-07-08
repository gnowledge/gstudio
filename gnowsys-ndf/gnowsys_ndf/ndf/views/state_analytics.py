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
from django.contrib.admin.views.decorators import staff_member_required
from gnowsys_ndf.ndf.models import *
from pymongo import Connection
from gnowsys_ndf.ndf.views.methods import create_grelation,get_group_name_id, delete_node

def map_view(request,group_id):
	return render_to_response("ndf/map_india.html",{ 'group_id':group_id, 'groupid':group_id}
		, context_instance=RequestContext(request))

@staff_member_required
def add_organization(request,group_id,node_id=None):
	try:
		group_id = ObjectId(group_id)
	except:
		group_name, group_id = get_group_name_id(group_id)

	org_node = node_collection.find({'_type':'GSystemType','name':'Organization'});
	if request.method=="POST":
			organization = json.loads(request.body)
			# print organization
			organization_node = None
			if node_id:
				organization_node = node_collection.find({'_id':ObjectId(str(node_id))})[0]
			if not organization_node:
				organization_node = node_collection.collection.GSystem();
				organization_node['member_of'] = [org_node[0]._id]
				organization_node['created_by'] = request.user.id
				organization_node['tags'].append(u'state_analytics')
				organization_node['group_set'].append(ObjectId(group_id))

			organization_node['name'] = organization['properties']['name']
			organization_node['modified_by'] = request.user.id
			organization_node['origin'] = organization['coordinates']
			organization_node.save()
			state_id = organization['properties']['state']
			if state_id:
				state_node = node_collection.one({'attribute_set.state_code':state_id})
				organization_belongs_to_state_rt = node_collection.one({'_type': 'RelationType', 'name': u'organization_belongs_to_state'})
				create_grelation(organization_node._id, organization_belongs_to_state_rt  ,state_node._id)

			return HttpResponse(json.dumps({'status':1,'id':str(organization_node._id)}))
	else:
		return HttpResponse("Not POST")
				
def fetch_organization(request,group_id=None):

	state_gst = node_collection.find({'_type':'GSystemType','name':'State'})
	states_nodes = node_collection.find({'member_of':{'$in':[state_gst[0]._id]}})
	states_id = [doc._id for doc in states_nodes]

	organization_belongs_to_state_rel = triple_collection.find({'right_subject':{'$in':states_id},'status':{'$ne':u'DELETED'}})
	organization_ids = [doc.subject for doc in organization_belongs_to_state_rel]
	organization_list = node_collection.find({'_id':{'$in':organization_ids},'tags':{'$in': ['state_analytics']}})
	result = [] 
	temp = {
		'id':'',
		'properties':{},
		'coordinates':[],
	}
	for organization in organization_list:
		state = None
		for relation in organization.relation_set:
			if 'organization_belongs_to_state' in relation.keys() and relation['organization_belongs_to_state']:
				state = node_collection.find({'_id':relation['organization_belongs_to_state'][0]})
		if state:
			temp['id'] = str(organization._id).encode('ascii','ignore')
			temp['properties']['name'] = organization.name.encode('ascii','ignore')
			temp['properties']['state'] = state[0].attribute_set[0]['state_code'].encode('ascii','ignore')
			temp['coordinates'] = organization.origin
			result.append(json.dumps(temp))

	return HttpResponse(json.dumps(result))

@staff_member_required
def delete_organization(request, group_id=None,node_id=None):
	if not node_id:
		return HttpResponse({'status':0,'message':'Node id not sent'})
	else:
		status,status_message = delete_node(ObjectId(node_id), deletion_type=0)
		print status
		return HttpResponse(json.dumps({'status':status,'message':''}))

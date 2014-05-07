''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''

from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.views.methods import get_node_common_fields

#######################################################################################################################################
db = get_database()
collection = db[Node.collection_name]
#######################################################################################################################################

def themes(request, group_id, app_id=None, app_set_id=None):

	app_collection_set = [] 
	appName = "browse topic"
   	title = appName
   	nodes_dict = []
   	themes_list_items = ""
   	themes_hierarchy = ""
   	node = ""

	app = collection.Node.find_one({"_id":ObjectId(app_id)})

	if app: 
		
		for each in app.collection_set:
			app_set = collection.Node.find_one({"_id":each})
			app_collection_set.append({"id":str(app_set._id),"name":app_set.name}) 	

	if app_set_id:
		themes_list_items = True

		app_GST = collection.Node.find_one({"_id":ObjectId(app_set_id)})  # This will return GST created for Browse Topic 
		if app_GST:
			title = app_GST.name

			nodes = list(collection.Node.find({'member_of': {'$all': [app_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}}))

	        nodes_dict = []
	        for each in nodes:
	            nodes_dict.append({"id":str(each._id), "name":each.name, "created_by":User.objects.get(id=each.created_by).username, "created_at":each.created_at})

	else:
		# This will show Themes Hierarchy  
		themes_hierarchy = True
		ST_theme = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
		if ST_theme:
			node = ST_theme

	return render_to_response("ndf/theme.html",
                               {'app_collection_set':app_collection_set,
                               'group_id': group_id,'groupid': group_id,'node': node,
                               'nodes':nodes_dict,'app_id': app_id,'app_name': appName,
                               'title': title,'themes_list_items': themes_list_items,
                               'themes_hierarchy': themes_hierarchy
                               },
                             
                              context_instance = RequestContext(request)
    )       


def theme_topic_create_edit(request, group_id, app_id=None, app_set_id=None):

	app_collection_set = [] 
	nodes_dict = []
 	create_edit = True
 	themes_list_items = ""
 	title = ""

 	app_GST = collection.Node.find_one({"_id":ObjectId(app_set_id)})
 	if app_GST:
 		available_nodes = collection.Node.find({'_type': u'GSystem', 'member_of': ObjectId(app_GST._id) })

	nodes_list = []
	for each in available_nodes:
			nodes_list.append(each.name)

	nodes_list = json.dumps(nodes_list)

 	app = collection.Node.find_one({"_id":ObjectId(app_id)})
	if app: 
		for each in app.collection_set:
			app_set = collection.Node.find_one({"_id":each})
			app_collection_set.append({"id":str(app_set._id),"name":app_set.name}) 	


	if request.method == "POST":

		theme_topic_node = collection.GSystem()
		if app_GST:

			get_node_common_fields(request, theme_topic_node, group_id, app_GST)
			theme_topic_node.save() 
			create_edit = False
			themes_list_items = True

			nodes = list(collection.Node.find({'member_of': {'$all': [app_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}}))

	        nodes_dict = []
	        for each in nodes:
	            nodes_dict.append({"id":str(each._id), "name":each.name, "created_by":User.objects.get(id=each.created_by).username, "created_at":each.created_at})

	else:
		app_node = None
		app_GST = collection.Node.find_one({"_id":ObjectId(app_set_id)})
		if app_GST:
			title = app_GST.name

	return render_to_response("ndf/theme.html",
	                           {'app_collection_set':app_collection_set,
	                           	'group_id': group_id,'groupid': group_id, 
	                           	'create_edit': create_edit,'app_id': app_id,
	                           	'nodes_list': nodes_list,'title': title,
	                           	'themes_list_items': themes_list_items,'nodes':nodes_dict
	                           },context_instance = RequestContext(request)

	)
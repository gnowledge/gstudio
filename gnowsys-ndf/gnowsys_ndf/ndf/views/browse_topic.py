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
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, get_drawers

#######################################################################################################################################
db = get_database()
collection = db[Node.collection_name]
theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
#######################################################################################################################################

def themes(request, group_id, app_id=None, app_set_id=None):

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
		group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		if group_ins:
		    group_id = str(group_ins._id)
		else :
		    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		    if auth :
		        group_id = str(auth._id)
	else :
	    pass
	if app_id is None:
	    app_ins = collection.Node.find_one({'_type':'GSystemType', 'name': 'Browse Topic'})
	    if app_ins:
	        app_id = str(app_ins._id)


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
 	themes_hierarchy = False
 	themes_list_items = ""
 	title = ""
 	node = ""
 	theme_topic_node = ""
 	drawers = None
	drawer = None

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

		if app_GST:

			create_edit = True
			themes_list_items = ""

			if app_GST.name == "Theme" or app_GST.name == "Topic":
				themes_list_items = False				
				create_edit = False
				themes_hierarchy = True

				theme_topic_node = collection.GSystem()
				get_node_common_fields(request, theme_topic_node, group_id, app_GST)
				theme_topic_node.save()

				# This will return to Themes Hierarchy  
				if theme_GST:
					node = theme_GST
				
			else:
				theme_topic_node = collection.Node.one({'_id': ObjectId(app_GST._id)})

				if theme_GST._id in app_GST.member_of:
					get_node_common_fields(request, theme_topic_node, group_id, theme_GST)
					theme_topic_node.save() 
					title = theme_GST.name
					node = theme_topic_node
					# To display the theme-topic drawer while create or edit theme
					checked = "Theme"
					drawers = get_drawers(group_id, node._id, node.collection_set, checked)
					drawer = drawers['2']

				elif topic_GST._id in app_GST.member_of:
					get_node_common_fields(request, theme_topic_node, group_id, topic_GST)
					theme_topic_node.save()
					title = topic_GST.name 
					node = theme_topic_node


	else:
		app_node = None
		
		app_GST = collection.Node.find_one({"_id":ObjectId(app_set_id)})
		if app_GST:
			if app_GST.name == "Theme" or app_GST.name == "Topic":
				title = app_GST.name
				node = ""
			else:
				if theme_GST._id in app_GST.member_of:
					title = theme_GST.name
					node = app_GST 
					# To display the theme-topic drawer while create or edit theme
					checked = "Theme"
					drawers = get_drawers(group_id, node._id, node.collection_set, checked)
					drawer = drawers['2']

				elif topic_GST._id in app_GST.member_of:
					title = topic_GST.name
					node = app_GST



	return render_to_response("ndf/theme.html",
	                           {'app_collection_set':app_collection_set,
	                           	'group_id': group_id,'groupid': group_id, 'drawer': drawer,
	                           	'create_edit': create_edit, 'themes_hierarchy': themes_hierarchy,'app_id': app_id,
	                           	'nodes_list': nodes_list,'title': title,'node': node,
	                           	'theme_GST_id': theme_GST._id, 'topic_GST_id': topic_GST._id,
	                           	'themes_list_items': themes_list_items,'nodes':nodes_dict
	                           },context_instance = RequestContext(request)

	)

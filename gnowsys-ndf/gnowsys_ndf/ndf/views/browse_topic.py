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
from gnowsys_ndf.settings import LANGUAGES

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


	appName = "browse topic"
   	title = appName
   	nodes_dict = []
   	themes_list_items = ""
   	themes_hierarchy = ""
   	node = ""
	
       	if app_set_id:
		themes_list_items = True
		app_GST = collection.Node.find_one({"_id":ObjectId(app_set_id)})

		if app_GST:
			title = theme_GST.name

			nodes = list(collection.Node.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}}))

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
                               {'theme_GST_id':theme_GST._id,
                               'group_id': group_id,'groupid': group_id,'node': node,
                               'nodes':nodes_dict,'app_id': app_id,'app_name': appName,
                               'title': title,'themes_list_items': themes_list_items,
                               'themes_hierarchy': themes_hierarchy
                               },
                             
                              context_instance = RequestContext(request)
    )       

def theme_topic_create_edit(request, group_id, app_id=None, app_set_id=None):

	nodes_dict = []
 	create_edit = True
 	themes_hierarchy = False
 	themes_list_items = ""
 	title = ""
 	node = ""
 	theme_topic_node = ""
 	drawers = None
	drawer = None
	nodes_list = []
	parent_nodes_collection = ""
        translate=request.GET.get('translate','')
        appsetid=request.GET.get('appid','')
        if request.method == "POST":
                
 		app_GST = collection.Node.find_one({"_id":ObjectId(app_set_id)})
                if translate:
                    app_GST = collection.Node.find_one({"_id":ObjectId(appsetid)})
                    node1=collection.Node.find_one({"_id":ObjectId(app_set_id)})
		if app_GST or translate == True:

			create_edit = True
			themes_list_items = ""
			root_themes = []
                        name = request.POST.get('name')
                        collection_list = request.POST.get('collection_list','')

			# To find the root nodes to maintain the uniquness while creating and editing themes
			nodes = collection.Node.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
			for each in nodes:
				if each.collection_set:
					for k in each.collection_set:
						nodes_list.append(k)

			nodes.rewind()
			for each in nodes:
				if each._id not in nodes_list:
					root_themes.append(each.name)


			if app_GST.name == "Theme" or app_GST.name == "Topic" or translate == "True":
				# For creating new themes & Topics
				themes_list_items = False				
				create_edit = False
				themes_hierarchy = True
				
				if name :
					if not name.upper() in (theme_name.upper() for theme_name in root_themes):

						theme_topic_node = collection.GSystem()
						get_node_common_fields(request, theme_topic_node, group_id, app_GST)
						theme_topic_node.save()

				# This will return to Themes Hierarchy  
				if theme_GST:
					node = theme_GST
				
			else:
				themes_list_items = False				
				create_edit = False
				themes_hierarchy = True

				theme_topic_node = collection.Node.one({'_id': ObjectId(app_GST._id)})

				# For edititng themes 
				if theme_GST._id in app_GST.member_of and translate != "True" :
                                        
					# To find themes uniqueness within the context of its parent Theme collection, while editing theme name
					prior_theme_collection = [] 
					nodes = collection.Node.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
					for each in nodes:
						if app_GST._id in each.collection_set:
							for k in each.collection_set:
								prior_theme = collection.Node.one({'_id': ObjectId(k) })
								prior_theme_collection.append(prior_theme.name)


					if name:
						if not name.upper() in (theme_name.upper() for theme_name in prior_theme_collection):
							get_node_common_fields(request, theme_topic_node, group_id, theme_GST)
							theme_topic_node.save() 

					# For storing and maintaning collection order
					theme_topic_node.collection_set = []
					if collection_list != '':
					    collection_list = collection_list.split(",")

					i = 0
					while (i < len(collection_list)):
						node_id = ObjectId(collection_list[i])
					    
						if collection.Node.one({"_id": node_id}):
							theme_topic_node.collection_set.append(node_id)

						i = i+1
					theme_topic_node.save() 
					# End of storing collection

					title = theme_GST.name
					# This will return to Themes Hierarchy  
					if theme_GST:
						node = theme_GST

				# For editing topics
				elif topic_GST._id in app_GST.member_of:
					root_topics = []
					nodes_list = []

					# To find the root nodes to maintain the uniquness while creating and editing topics
					nodes = collection.Node.find({'member_of': {'$all': [topic_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
					for each in nodes:
						if each.collection_set:
							for k in each.collection_set:
								nodes_list.append(k)

					nodes.rewind()
					for each in nodes:
						if each._id not in nodes_list:
							root_topics.append(each.name)

					# End of finding the root nodes

					if name:
						if not name.upper() in (theme_name.upper() for theme_name in root_topics):
							get_node_common_fields(request, theme_topic_node, group_id, topic_GST)
							theme_topic_node.save() 


					title = topic_GST.name 

					# This will return to Themes Hierarchy  
					if theme_GST:
						node = theme_GST


	else:
		app_node = None
		nodes_list = []
		app_GST = collection.Node.find_one({"_id":ObjectId(app_set_id)})
                if translate:
                    app_GST = collection.Node.find_one({"_id":ObjectId(appsetid)})
                    node1=collection.Node.find_one({"_id":ObjectId(app_set_id)})

		if app_GST:
                    app_GST = collection.Node.find_one({"_id":ObjectId(app_set_id)})
                    # For adding new Theme & Topic
                 
                    if app_GST.name == "Theme" or app_GST.name == "Topic" or translate == True:
                                title = app_GST.name
				node = ""
				root_themes = []

				# To find the root nodes to maintain the uniquness while creating new themes
				nodes = collection.Node.find({'member_of': {'$all': [app_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
				for each in nodes:
					if each.collection_set:
						for k in each.collection_set:
							nodes_list.append(k)

				nodes.rewind()
				for each in nodes:
					if each._id not in nodes_list:
						root_themes.append(each.name)


				root_themes = json.dumps(root_themes)
				nodes_list = root_themes
				# End of finding unique root level Themes

                    else:
				# For editing theme & topic
				if theme_GST._id in app_GST.member_of:
				        title = theme_GST.name
					node = app_GST
					prior_theme_collection = [] 
					parent_nodes_collection = ""
					# To display the theme-topic drawer while create or edit theme
					checked = "Theme"
					drawers = get_drawers(group_id, node._id, node.collection_set, checked)
					drawer = drawers['2']

					# To find themes uniqueness within the context of its parent Theme collection, while editing theme name
					nodes = collection.Node.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
					for each in nodes:
						if app_GST._id in each.collection_set:
							for k in each.collection_set:
								prior_theme = collection.Node.one({'_id': ObjectId(k) })
								prior_theme_collection.append(prior_theme.name)

					parent_nodes_collection = json.dumps(prior_theme_collection)	
 					# End of finding unique theme names for editing name

 					# For adding a sub-themes and maintianing their uniqueness within their context
 					for each in app_GST.collection_set:
			 			sub_theme = collection.Node.one({'_id': ObjectId(each) })
 						nodes_list.append(sub_theme.name)

 					nodes_list = json.dumps(nodes_list)
 					# End of finding unique sub themes

				elif topic_GST._id in app_GST.member_of:
					title = topic_GST.name
					node = app_GST
					prior_theme_collection = [] 
					parent_nodes_collection = ""

					# To find topics uniqueness within the context of its parent Theme collection, while editing topic name
					nodes = collection.Node.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
					for each in nodes:
						if app_GST._id in each.collection_set:
							for k in each.collection_set:
								prior_theme = collection.Node.one({'_id': ObjectId(k) })
								prior_theme_collection.append(prior_theme.name)

					parent_nodes_collection = json.dumps(prior_theme_collection)
					# End of finding unique theme names for editing name
        if translate:
            return render_to_response("ndf/translation_page.html",
	                           {'group_id': group_id,'groupid': group_id, 'drawer': drawer,
	                           	'create_edit': create_edit, 'themes_hierarchy': themes_hierarchy,'app_id': app_id,
	                           	'nodes_list': nodes_list,'title': title,'node': node1, 'parent_nodes_collection': parent_nodes_collection,
	                           	'theme_GST_id': theme_GST._id, 'topic_GST_id': topic_GST._id,
	                                'themes_list_items': themes_list_items,'nodes':nodes_dict,'translate':translate
	                           },context_instance = RequestContext(request)
            )
        else :

            return render_to_response("ndf/theme.html",
	                           {'group_id': group_id,'groupid': group_id, 'drawer': drawer,
	                           	'create_edit': create_edit, 'themes_hierarchy': themes_hierarchy,'app_id': app_id,
	                           	'nodes_list': nodes_list,'title': title,'node': node, 'parent_nodes_collection': parent_nodes_collection,
	                           	'theme_GST_id': theme_GST._id, 'topic_GST_id': topic_GST._id,
	                           	'themes_list_items': themes_list_items,'nodes':nodes_dict
	                           },context_instance = RequestContext(request)
                                      
	)

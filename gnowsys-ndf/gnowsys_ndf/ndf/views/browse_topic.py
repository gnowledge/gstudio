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

from gnowsys_ndf.ndf.models import Node, Triple
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, get_drawers,create_grelation_list
from gnowsys_ndf.ndf.views.methods import get_node_metadata
#######################################################################################################################################
db = get_database()
collection = db[Node.collection_name]
theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
#######################################################################################################################################
list_trans_coll = []
coll_set_dict={}

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
    nodes = ""
    unfold_tree = request.GET.get('unfold','')
    unfold = "false"
    
    if unfold_tree:
        unfold = unfold_tree
	
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
                               'themes_hierarchy': themes_hierarchy, 'unfold': unfold
                               },
                             
                              context_instance = RequestContext(request)
    )       


def theme_topic_create_edit(request, group_id, app_set_id=None):

    #####################
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
    ###################### 
    
    nodes_dict = []
    create_edit = True
    themes_hierarchy = False
    themes_list_items = ""
    title = ""
    node = ""
    theme_topic_node = ""
    drawers = None
    drawer = None
    app_id = None
    nodes_list = []
    parent_nodes_collection = ""
    translate=request.GET.get('translate','')
    
    app_GST = collection.Node.find_one({"_id":ObjectId(app_set_id)})
    if app_GST._id != theme_GST._id:
    	app_obj = collection.Node.one({'_id': ObjectId(app_GST.member_of[0])})
    else:
    	app_obj = theme_GST

    if app_obj:
        app_id = app_obj._id
	
    if request.method == "POST":
 
        if app_GST:
            
            create_edit = True
            themes_list_items = ""
            root_themes = []
            root_themes_id = []
            name = request.POST.get('name')
            collection_list = request.POST.get('collection_list','')
	    prior_node_list = request.POST.get('prior_node_list','')
	    teaches_list = request.POST.get('teaches_list','')
	    assesses_list = request.POST.get('assesses_list','')
	    
            
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
                    root_themes_id.append(each._id)

            
            if app_GST.name == "Theme" or app_GST.name == "Topic" or translate == "true":
                # For creating new themes & Topics
                themes_list_items = False				
                create_edit = False
                themes_hierarchy = True

                if name or translate == "true":
                    if not name.upper() in (theme_name.upper() for theme_name in root_themes) or translate == "true":
                      	if translate != "true":
                            theme_topic_node = collection.GSystem()
                            # get_node_common_fields(request, theme_topic_node, group_id, app_GST)
                            theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, app_GST))
                        if translate == "true":
                            global list_trans_coll
                            list_trans_coll = []
                            coll_set1=get_coll_set(app_GST._id)
                            for each in coll_set1:
                                theme_topic_node = collection.GSystem()
                            
                                if "Theme" in each.member_of_names_list:
                                    app_obj = theme_GST
                                    get_node_common_fields(request, theme_topic_node, group_id, app_obj, each)
                                    theme_topic_node.save()
                                    coll_set_dict[each._id]=theme_topic_node._id
                                # relation_type=collection.Node.one({'$and':[{'name':'translation_of'},{'_type':'RelationType'}]})
                                # grelation=collection.GRelation()
                                # grelation.relation_type=relation_type
                                # grelation.subject=each._id
                                # grelation.right_subject=theme_topic_node._id
                                # grelation.name=u""
                                # grelation.save()
                            for each in coll_set1:
                                if "Theme" in each.member_of_names_list:
                                    if each.collection_set:
                                        for collset in each.collection_set:
                                            p=coll_set_dict[each._id]
                                            parent_node=collection.Node.one({'_id':ObjectId(str(p))})
                                            n= coll_set_dict[collset]
                                            sub_node=collection.Node.one({'_id':ObjectId(str(n))})
                                            parent_node.collection_set.append(sub_node._id)
                                            parent_node.save()
                        
                # This will return to Themes Hierarchy  
                if theme_GST:
                    node = theme_GST
				
            else:
                themes_list_items = False				
                create_edit = False
                themes_hierarchy = True
                
                theme_topic_node = collection.Node.one({'_id': ObjectId(app_GST._id)})
                
                # For edititng themes 
                if theme_GST._id in app_GST.member_of and translate != "true":
                    # To find themes uniqueness within the context of its parent Theme collection, while editing theme name
                    prior_theme_collection = [] 
                    nodes = collection.Node.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
                    for each in nodes:
                        if app_GST._id in each.collection_set:
                            for k in each.collection_set:
                                prior_theme = collection.Node.one({'_id': ObjectId(k) })
                                prior_theme_collection.append(prior_theme.name)
                                
                    if name:
                        if theme_topic_node._id in root_themes_id:	
                            if not name.upper() in (theme_name.upper() for theme_name in root_themes):
                                # get_node_common_fields(request, theme_topic_node, group_id, theme_GST)
                                theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, theme_GST))
                                
                        else:						
                            if not name.upper() in (theme_name.upper() for theme_name in prior_theme_collection): 
                                # get_node_common_fields(request, theme_topic_node, group_id, theme_GST)
                                theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, theme_GST)) 
                                

                    if translate != "true":
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
                        if theme_topic_node.name == name:
                            theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, topic_GST))
                        else:
                            if not name.upper() in (theme_name.upper() for theme_name in root_topics):
                                theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, topic_GST))


                        if collection_list:
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
                            
                        title = topic_GST.name 
                        #ash #currently working #prior,teaching
			
			get_node_metadata(request,theme_topic_node,topic_GST)
			
			
			theme_topic_node.prior_node = []
  			if prior_node_list != '':
    				prior_node_list = prior_node_list.split(",")

  			i = 0
  			while (i < len(prior_node_list)):
	    			node_id = ObjectId(prior_node_list[i])
	    			if collection.Node.one({"_id": node_id}):
      					theme_topic_node.prior_node.append(node_id)
    
    				i = i+1
			theme_topic_node.save()
		
			if teaches_list !='':
					teaches_list=teaches_list.split(",")
					
			create_grelation_list(theme_topic_node._id,"teaches",teaches_list)
					

			
			if assesses_list !='':
					assesses_list=assesses_list.split(",")
					
			create_grelation_list(theme_topic_node._id,"assesses",assesses_list)

				
                        # This will return to Themes Hierarchy  
                        if theme_GST:
                            node = theme_GST
                           
    	
    else:
        app_node = None
        nodes_list = []
        
        app_GST = collection.Node.find_one({"_id":ObjectId(app_set_id)})

	
        
        if app_GST:
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
                    node.get_neighbourhood(node.member_of)
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
                global list_trans_coll
                list_trans_coll = []
                trans_coll_list = get_coll_set(str(app_GST._id))
                return render_to_response("ndf/translation_page.html",
	                                  {'group_id': group_id,'groupid': group_id,'title': title, 'node': app_GST, 'lan':LANGUAGES, 'list1':trans_coll_list
	                           },context_instance = RequestContext(request)
	        )
        
        
    return render_to_response("ndf/theme.html",
                       {'group_id': group_id,'groupid': group_id, 'drawer': drawer,
                            'create_edit': create_edit, 'themes_hierarchy': themes_hierarchy,'app_id': app_id,
                            'nodes_list': nodes_list,'title': title,'node': node, 'parent_nodes_collection': parent_nodes_collection,
                            'theme_GST_id': theme_GST._id, 'topic_GST_id': topic_GST._id,
                            'themes_list_items': themes_list_items,'nodes':nodes_dict,'lan':LANGUAGES
                       },context_instance = RequestContext(request)
                              
    )

def get_coll_set(node):
  obj=collection.Node.one({'_id':ObjectId(node)})
  if "Theme" in obj.member_of_names_list:  
      if  obj.collection_set:
          if obj not in list_trans_coll:
              list_trans_coll.append(obj)
      for each in obj.collection_set:
          n=collection.Node.one({'_id':each})
          if "Theme" in n.member_of_names_list:  
  
              if n not in list_trans_coll:
                  list_trans_coll.append(n)
                  if n.collection_set:
                      if "Theme" in n.member_of_names_list:  
  
                          get_coll_set(n._id)
                  
  #new_list=list_trans_coll
  #list_trans_coll = []
  return list_trans_coll

def topic_detail_view(request, group_id, app_Id=None):

  #####################
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
  ###################### 

  collection_tr = db[Triple.collection_name]
  obj = collection.Node.one({'_id': ObjectId(app_Id)})
  app = collection.Node.one({'_id': ObjectId(obj.member_of[0])})
  app_id = app._id
  topic = "Topic"

  ##breadcrumbs##
  # First time breadcrumbs_list created on click of page details
  breadcrumbs_list = []
  # Appends the elements in breadcrumbs_list first time the resource which is clicked
  breadcrumbs_list.append( (str(obj._id), obj.name) )

  ###shelf###
  shelves = []
  shelf_list = {}
  auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) }) 

  if auth:
	  has_shelf_RT = collection.Node.one({'_type': 'RelationType', 'name': u'has_shelf' })
	  dbref_has_shelf = has_shelf_RT.get_dbref()
	  shelf = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_has_shelf })        
	  shelf_list = {}

	  if shelf:
	    for each in shelf:
	        shelf_name = collection.Node.one({'_id': ObjectId(each.right_subject)}) 
	        shelves.append(shelf_name)

	        shelf_list[shelf_name.name] = []         
	        for ID in shelf_name.collection_set:
	        	shelf_item = collection.Node.one({'_id': ObjectId(ID) })
	        	shelf_list[shelf_name.name].append(shelf_item.name)

	  else:
	    shelves = []
  
  return render_to_response('ndf/topic_details.html', 
	                                { 'node': obj,'app_id': app_id,'breadcrumbs_list': breadcrumbs_list,
	                                  'group_id': group_id,'shelves': shelves,'topic': topic,
	                                  'groupid':group_id,'shelf_list': shelf_list
	                                },
	                                context_instance = RequestContext(request)
  )




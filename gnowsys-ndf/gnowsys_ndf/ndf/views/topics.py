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

from mongokit import paginator

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import LANGUAGES
from gnowsys_ndf.ndf.models import Node, Triple
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, get_drawers,create_grelation_list,get_execution_time, get_group_name_id, get_node_metadata,create_grelation, get_language_tuple
from gnowsys_ndf.ndf.views.methods import get_filter_querydict
from gnowsys_ndf.ndf.templatetags.simple_filters import get_dict_from_list_of_dicts
#######################################################################################################################################
theme_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Theme'})
topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item'})
app = node_collection.one({'name': u'Topics', '_type': 'GSystemType'})
#######################################################################################################################################

@get_execution_time
def themes(request, group_id, app_id=None, app_set_id=None):

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    theme_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Theme'})

    if app_id is None:
        # app_ins = node_collection.find_one({'_type': 'GSystemType', 'name': 'Topics'})
        app_ins = app
        # if app_ins:
        app_id = str(app_ins._id)

    # Code for user shelf
    shelves = []
    shelf_list = {}
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
    
    # --- shelf commented for time being ---
    # 
    # if auth:
    #   has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })
    #   shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': has_shelf_RT._id})
    #   shelf_list = {}

    #   if shelf:
    #     for each in shelf:
    #         shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)}) 
    #         shelves.append(shelf_name)

    #         shelf_list[shelf_name.name] = []
    #         for ID in shelf_name.collection_set:
    #           shelf_item = node_collection.one({'_id': ObjectId(ID)})
    #           shelf_list[shelf_name.name].append(shelf_item.name)

    #   else:
    #     shelves = []
    # End of user shelf

    appName = "topics"
    title = appName
    nodes_dict = []
    themes_list_items = ""
    themes_hierarchy = ""
    themes_cards = ""
    node = ""
    nodes = ""
    unfold_tree = request.GET.get('unfold','')
    selected = request.GET.get('selected','')
    # print "selected: ", selected
    tree = request.GET.get('tree', 'hierarchical')
    unfold = "false"

    # topics_GST = node_collection.find_one({'_type': 'GSystemType', 'name': 'Topics'})
    topics_GST = app
    
    if unfold_tree:
        unfold = unfold_tree
    
    if app_set_id:
        themes_list_items = True
        app_GST = node_collection.find_one({"_id": ObjectId(app_set_id)})
        
        if app_GST:
            title = theme_GST.name
            nodes = list(node_collection.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}}))
            
            nodes_dict = []
            for each in nodes:
                nodes_dict.append({"id":str(each._id), "name":each.name, "created_by":User.objects.get(id=each.created_by).username, "created_at":each.created_at})

    # to display the tree hierarchy of themes items inside particular theme(Here app_id defines the Theme id)
    elif ObjectId(app_id) != topics_GST._id:
        themes_hierarchy = True
        themes_cards = ""
        Theme_obj = node_collection.one({'_id': ObjectId(app_id)})
        if Theme_obj:
            node = Theme_obj

    else:
        # This will show Themes as a card view on landing page of Topics
        themes_cards = True
        # if request.user.username:
        #     nodes_dict = node_collection.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
        # else:
        #     nodes_dict = node_collection.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
        
    lang = list(get_language_tuple(request.LANGUAGE_CODE))
    nodes_dict = node_collection.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}, 'language': lang})

    return render_to_response("ndf/theme.html",
                               {'theme_GST_id':theme_GST._id, 'theme_GST':theme_GST, 'themes_cards': themes_cards, 'theme_GST':theme_GST,
                               'group_id': group_id,'groupid': group_id,'node': node,'shelf_list': shelf_list,'shelves': shelves, 'tree': tree,
                               'nodes':nodes_dict,'app_id': app_id,'app_name': appName,"selected": selected,
                               'title': title,'themes_list_items': themes_list_items,
                               'themes_hierarchy': themes_hierarchy, 'unfold': unfold,
                                'appId':app._id,
                               },
                             
                              context_instance = RequestContext(request)
    )       


def list_themes(request, group_id):

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    title = theme_GST.name
    
    nodes = node_collection.find({
        'member_of': {'$all': [theme_GST._id]},
        'group_set':{'$all': [ObjectId(group_id)]}
        },
        {'_id': 1, 'name': 1, 'created_by': 1, 'created_at': 1})
    
    return render_to_response("ndf/list_themes.html",
                            { 
                                'groupid': group_id,
                                'group_id': group_id,
                                'nodes': nodes,
                                'theme_GST': theme_GST
                            },
                            context_instance = RequestContext(request) )


def delete_theme(request, group_id, theme_id):

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    trash_group = node_collection.one({'_type': 'Group', 'name': 'Trash'})

    theme_to_be_deleted = node_collection.one({'_id': ObjectId(theme_id)})
    theme_to_be_deleted.group_set = [ObjectId(trash_group._id)]
    theme_to_be_deleted.save()
    # print trash_group._id,"  ", theme_to_be_deleted.group_set

    return HttpResponseRedirect( reverse('list_themes', kwargs={"group_id": group_id} ))


global list_trans_coll
list_trans_coll = []
coll_set_dict={}

@get_execution_time
def theme_topic_create_edit(request, group_id, app_set_id=None):

    #####################
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    ###################### 
    
    nodes_dict = []
    create_edit = True
    themes_hierarchy = False
    themes_list_items = ""
    themes_cards = ""
    title = ""
    node = ""
    theme_topic_node = ""
    drawers = None
    drawer = None
    app_id = None
    nodes_list = []
    parent_nodes_collection = ""
    translate=request.GET.get('translate','')
    
    app_GST = node_collection.find_one({"_id":ObjectId(app_set_id)})
    if app_GST._id != theme_GST._id:
    	app_obj = node_collection.one({'_id': ObjectId(app_GST.member_of[0])})
    else:
    	app_obj = theme_GST

    if app_obj:
        app_id = app_obj._id


    shelves = []
    shelf_list = {}
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 
    
    if auth:
      has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })
      shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': has_shelf_RT._id})
      shelf_list = {}

      if shelf:
        for each in shelf:
            shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)}) 
            shelves.append(shelf_name)

            shelf_list[shelf_name.name] = []         
            for ID in shelf_name.collection_set:
              shelf_item = node_collection.one({'_id': ObjectId(ID) })
              shelf_list[shelf_name.name].append(shelf_item.name)

      else:
        shelves = []

	
    if request.method == "POST":
 
        if app_GST:
            
            create_edit = True
            themes_list_items = ""
            root_themes = []
            root_themes_id = []
            nodes_list = []
            name = request.POST.get('name')
            collection_list = request.POST.get('collection_list','')
            prior_node_list = request.POST.get('prior_node_list','')
            teaches_list = request.POST.get('teaches_list','')
            assesses_list = request.POST.get('assesses_list','')
	    
            
            # To find the root nodes to maintain the uniquness while creating and editing themes
            nodes = node_collection.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
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
                themes_hierarchy = False
                themes_cards = True

                if name or translate == "true":
                    if not name.upper() in (theme_name.upper() for theme_name in root_themes) or translate == "true":
                      	if translate != "true":
                            theme_topic_node = node_collection.collection.GSystem()
                            # get_node_common_fields(request, theme_topic_node, group_id, app_GST)
                            theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, app_GST),groupid=group_id)
                        if translate == "true":
                            global list_trans_coll
                            list_trans_coll = []
                            coll_set1=get_coll_set(app_GST._id)
                            for each in coll_set1:
                                theme_topic_node = node_collection.collection.GSystem()
                            
                                if "Theme" in each.member_of_names_list:
                                    app_obj = theme_GST
                                if "theme_item" in each.member_of_names_list:
                                    app_obj = theme_item_GST
                                if "topic" in each.member_of_names_list:
                                    app_obj = topic_GST
                                theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, app_obj, each),groupid=group_id)
                                coll_set_dict[each._id]=theme_topic_node._id
                                relation_type = node_collection.one({'_type':'RelationType', 'name':'translation_of'})
                                # grelation=collection.GRelation()
                                # grelation.relation_type=relation_type
                                # grelation.subject=each._id
                                # grelation.right_subject=theme_topic_node._id
                                # grelation.name=u""
                                # grelation.save()
                                gr_node = create_grelation(each._id, relation_type, theme_topic_node._id)

                            for each in coll_set1:
                                #if "Theme" in each.member_of_names_list:
                                if each.collection_set:
                                    for collset in each.collection_set:
                                        p=coll_set_dict[each._id]
                                        parent_node = node_collection.one({'_id':ObjectId(str(p))})
                                        n= coll_set_dict[collset]
                                        sub_node = node_collection.one({'_id':ObjectId(str(n))})
                                        parent_node.collection_set.append(sub_node._id)
                                        parent_node.save(groupid=group_id)
                                        

                        
                
                # To return themes card view for listing theme nodes after creating new Themes
                nodes.rewind()
                nodes_dict = nodes
				
            else:
                themes_list_items = False				
                create_edit = False
                themes_hierarchy = True

                theme_topic_node = node_collection.one({'_id': ObjectId(app_GST._id)})
                
                # For edititng themes 
                if theme_GST._id in app_GST.member_of and translate != "true":
                    # To find themes uniqueness within the context of its parent Theme collection, while editing theme name
                    root_themes = [] 
                    nodes = node_collection.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
                    for each in nodes:
                        root_themes.append(each.name)
                                
                    if name:
                        if name.upper() != theme_topic_node.name.upper():
                            if not name.upper() in (theme_name.upper() for theme_name in root_themes):
                                # get_node_common_fields(request, theme_topic_node, group_id, theme_GST)
                                theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, theme_GST),groupid=group_id)
                                
                        else:
                            theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, theme_GST),groupid=group_id)
                            

                    if translate != "true":
                        # For storing and maintaning collection order
                        if collection_list != '':
                            theme_topic_node.collection_set = []
                            collection_list = collection_list.split(",")
                            
                        i = 0
                        while (i < len(collection_list)):
                            node_id = ObjectId(collection_list[i])
                            
                            if node_collection.one({"_id": node_id}):
                                theme_topic_node.collection_set.append(node_id)
                                
                            i = i+1
                            
                        theme_topic_node.save(groupid=group_id) 
                       
                        # End of storing collection

                    title = theme_GST.name
                    nodes.rewind()
                    nodes_dict = nodes
                    # This will return to Themes Hierarchy  
                    themes_list_items = False               
                    create_edit = False
                    themes_hierarchy = False
                    themes_cards = True


                elif theme_item_GST._id in app_GST.member_of and translate != "true":

                    title = "Theme Item"
                    dict_drawer = {}
                    dict2 = []
                    node = app_GST
                    prior_theme_collection = [] 
                    parent_nodes_collection = ""
                    # To display the theme-topic drawer while create or edit theme
                    checked = "theme_item"
                    # drawers = get_drawers(group_id, node._id, node.collection_set, checked)

                    # Code for fetching drawer2 
                    for k in node.collection_set:
                        obj = node_collection.one({'_id': ObjectId(k) })
                        dict2.append(obj)

                    dict_drawer['2'] = dict2

                    # drawers = dict_drawer
                    # End of code for drawer2

                    drawer = dict_drawer['2']
                    
                    # To find themes uniqueness within the context of its parent Theme collection, while editing theme item
                    nodes = node_collection.find({'member_of': {'$all': [theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
                    for each in nodes:
                        if app_GST._id in each.collection_set:
                            for k in each.collection_set:
                                prior_theme = node_collection.one({'_id': ObjectId(k) })
                                prior_theme_collection.append(prior_theme.name)
                                
                    parent_nodes_collection = json.dumps(prior_theme_collection)   

                    if not prior_theme_collection:
                        root_nodes = node_collection.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})     
                        for k in root_nodes:
                            if app_GST._id in k.collection_set:
                                root_themes = []
                                root_themes_id = []
                                for l in k.collection_set:
                                    objs = node_collection.one({'_id': ObjectId(l)})
                                    root_themes.append(objs.name)
                                    root_themes_id.append(objs._id) 
                    # End of finding unique theme names for editing name
                    
                    # For adding a sub-theme-items and maintianing their uniqueness within their context
                    nodes_list = []
                    for each in app_GST.collection_set:
                        sub_theme = node_collection.one({'_id': ObjectId(each) })
                        nodes_list.append(sub_theme.name)
                    
                    nodes_list = json.dumps(nodes_list)
                    # End of finding unique sub themes

                                
                    if name:
                        if name.upper() != theme_topic_node.name.upper():
                            # If "Name" has changed 

                            if theme_topic_node._id in root_themes_id:  
                                # If editing node in root theme items
                                if not name.upper() in (theme_name.upper() for theme_name in root_themes):
                                    # get_node_common_fields(request, theme_topic_node, group_id, theme_GST)
                                    theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, theme_item_GST),groupid=group_id)
                            else:
                                # If editing theme item in prior_theme_collection hierarchy 
                                if not name.upper() in (theme_name.upper() for theme_name in prior_theme_collection): 
                                    # get_node_common_fields(request, theme_topic_node, group_id, theme_GST)
                                    theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, theme_item_GST),groupid=group_id) 
                           
                        else:
                            # If name not changed but other fields has changed
                            theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, theme_item_GST),groupid=group_id)  


                    if translate != "true" and collection_list:
                        # For storing and maintaning collection order         
                        if collection_list != '':
                            theme_topic_node.collection_set = []
                            collection_list = collection_list.split(",")
                            
                        i = 0
                        while (i < len(collection_list)):
                            node_id = ObjectId(collection_list[i])
                            
                            if node_collection.one({"_id": node_id}):
                                theme_topic_node.collection_set.append(node_id)
                                
                            i = i+1
                        theme_topic_node.save(groupid=group_id) 
                        # End of storing collection

                    # This will return to Themes items edit  
                    if theme_topic_node:
                        theme_topic_node.reload()
                        node = theme_topic_node
                        create_edit = True
                        themes_hierarchy = False
                        
                        
                # For editing topics
                elif topic_GST._id in app_GST.member_of:
                    root_topics = []
                    nodes_list = []
                    
                    # To find the root nodes to maintain the uniquness while creating and editing topics
                    nodes = node_collection.find({'member_of': {'$all': [topic_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
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
                        if theme_topic_node.name != name:
                            topic_name = theme_topic_node.name
                            if not name.upper() in (theme_name.upper() for theme_name in root_topics):

                                theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, topic_GST),groupid=group_id)
                                
                            elif topic_name.upper() == name.upper():
                                theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, topic_GST),groupid=group_id)               
                                
                        else:
                            theme_topic_node.save(is_changed=get_node_common_fields(request, theme_topic_node, group_id, topic_GST),groupid=group_id)
                                                                                                                
                        if collection_list:
                            # For storing and maintaning collection order
                            if collection_list != '':
                                theme_topic_node.collection_set = []
                                collection_list = collection_list.split(",")
            
                            i = 0
                            while (i < len(collection_list)):
                                node_id = ObjectId(collection_list[i])
                                
                                if node_collection.one({"_id": node_id}):
                                    theme_topic_node.collection_set.append(node_id)
                                    
                                i = i+1
                            theme_topic_node.save(groupid=group_id)
                            
                        title = topic_GST.name 
                        
                        # To fill the metadata info while creating and editing topic node
                        metadata = request.POST.get("metadata_info", '') 
                        if metadata:
                          # Only while metadata editing
                          if metadata == "metadata":
                            if theme_topic_node:
                              get_node_metadata(request,theme_topic_node)
                        # End of filling metadata
                        
                        
                        if prior_node_list != '':
                            theme_topic_node.prior_node = []
                            prior_node_list = prior_node_list.split(",")
                            
                        i = 0
                        while (i < len(prior_node_list)):
                            node_id = ObjectId(prior_node_list[i])
                            if node_collection.one({"_id": node_id}):
                                theme_topic_node.prior_node.append(node_id)
                                
                            i = i+1
                        

                        theme_topic_node.save(groupid=group_id)
                        
                        if teaches_list !='':
                            teaches_list=teaches_list.split(",")
                            
                            create_grelation_list(theme_topic_node._id,"teaches",teaches_list)
                        
                        
                        
                        if assesses_list !='':
                            assesses_list=assesses_list.split(",")
                            
                            create_grelation_list(theme_topic_node._id,"assesses",assesses_list)
				

                        # This will return to edit topic  
                        if theme_topic_node:
                            theme_topic_node.reload()
                            node = theme_topic_node
                            create_edit = True
                            themes_hierarchy = False


    else:
        app_node = None
        nodes_list = []
        
        app_GST = node_collection.find_one({"_id":ObjectId(app_set_id)})
        # print "\napp_GST in else: ",app_GST.name,"\n"
        
        if app_GST:
            # For adding new Theme & Topic
            if app_GST.name == "Theme" or app_GST.name == "Topic" or translate == True:
                print "22222"
                title = app_GST.name
                node = ""
                root_themes = []
            
                # To find the root nodes to maintain the uniquness while creating new themes
                nodes = node_collection.find({'member_of': {'$all': [app_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
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

                if theme_GST._id in app_GST.member_of:
                    title = "Theme"
                    node = app_GST
                    prior_theme_collection = [] 
                    parent_nodes_collection = ""
                    drawer = []
                # End of editing Themes
                    
                
                # For editing theme item
                if theme_item_GST._id in app_GST.member_of:
                    title = "Theme Item"
                    dict_drawer = {}
                    dict2 = []
                    node = app_GST
                    prior_theme_collection = [] 
                    parent_nodes_collection = ""
                    # To display the theme-topic drawer while create or edit theme
                    checked = "theme_item"
                    # drawers = get_drawers(group_id, node._id, node.collection_set, checked)
                    for k in node.collection_set:
                        obj = node_collection.one({'_id': ObjectId(k) })
                        dict2.append(obj)

                    dict_drawer['2'] = dict2

                    drawer = dict_drawer['2']
                    
                    # To find themes uniqueness within the context of its parent Theme collection, while editing theme name
                    nodes = node_collection.find({'member_of': {'$all': [theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
                    for each in nodes:
                        if app_GST._id in each.collection_set:
                            for k in each.collection_set:
                                prior_theme = node_collection.one({'_id': ObjectId(k) })
                                prior_theme_collection.append(prior_theme.name)
                                
                    parent_nodes_collection = json.dumps(prior_theme_collection)	
                    # End of finding unique theme names for editing name
                    
                    # For adding a sub-themes and maintianing their uniqueness within their context
                    for each in app_GST.collection_set:
                        sub_theme = node_collection.one({'_id': ObjectId(each) })
                        nodes_list.append(sub_theme.name)
                        
                    nodes_list = json.dumps(nodes_list)
                    # End of finding unique sub themes
                    
                # for editing topic
                elif topic_GST._id in app_GST.member_of:
                    title = topic_GST.name
                    node = app_GST
                    prior_theme_collection = [] 
                    parent_nodes_collection = ""

                    node.get_neighbourhood(node.member_of)

                    # To find topics uniqueness within the context of its parent Theme item collection, while editing topic name
                    nodes = node_collection.find({'member_of': {'$all': [theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})
                    for each in nodes:
                        if app_GST._id in each.collection_set:
                            for k in each.collection_set:
                                prior_theme = node_collection.one({'_id': ObjectId(k) })
                                prior_theme_collection.append(prior_theme.name)
                                
                    parent_nodes_collection = json.dumps(prior_theme_collection)
                    # End of finding unique theme names for editing name

	    if translate:
                global list_trans_coll
                list_trans_coll = []
                trans_coll_list = get_coll_set(str(app_GST._id))
                print LANGUAGES 
                return render_to_response("ndf/translation_page.html",
	                                  {'group_id': group_id,'groupid': group_id,'title': title, 'node': app_GST, 'lan':LANGUAGES, 'list1':trans_coll_list
	                           },context_instance = RequestContext(request)
	        )
        
    if title == "Topic":
        return render_to_response("ndf/node_edit_base.html",
                       {'group_id': group_id,'groupid': group_id, 'drawer': drawer, 'themes_cards': themes_cards,
                        'shelf_list': shelf_list,'shelves': shelves,
                        'create_edit': create_edit, 'themes_hierarchy': themes_hierarchy,'app_id': app_id,'appId':app._id,
                        'nodes_list': nodes_list,'title': title,'node': node, 'parent_nodes_collection': parent_nodes_collection,
                        'theme_GST_id': theme_GST._id,'theme_item_GST_id': theme_item_GST._id, 'topic_GST_id': topic_GST._id,
                        'themes_list_items': themes_list_items,'nodes':nodes_dict,'lan':LANGUAGES

                       },context_instance = RequestContext(request)
                              
        )

    return render_to_response("ndf/theme.html",
                       {'group_id': group_id,'groupid': group_id, 'drawer': drawer, 'themes_cards': themes_cards, 'theme_GST':theme_GST, 'theme_GST':theme_GST,
                            'shelf_list': shelf_list,'shelves': shelves,
                            'create_edit': create_edit, 'themes_hierarchy': themes_hierarchy,'app_id': app_id,'appId':app._id,
                            'nodes_list': nodes_list,'title': title,'node': node, 'parent_nodes_collection': parent_nodes_collection,
                            'theme_GST_id': theme_GST._id,'theme_item_GST_id': theme_item_GST._id, 'topic_GST_id': topic_GST._id,
                            'themes_list_items': themes_list_items,'nodes':nodes_dict,'lan':LANGUAGES

                       },context_instance = RequestContext(request)
                              
    )


@get_execution_time
def get_coll_set(node):
  obj = node_collection.one({'_id': ObjectId(node)})
  #print obj.member_of_names_list
  if "Topic" not in obj.member_of_names_list:  
      if  obj.collection_set:
          if obj not in list_trans_coll:
              list_trans_coll.append(obj)
          for each in obj.collection_set:
              n = node_collection.one({'_id':each})
              if "Topic" not in n.member_of_names_list:  
  
                  if n not in list_trans_coll:
                      list_trans_coll.append(n)
                      if n.collection_set:
                          if "Topic" not in n.member_of_names_list:  
  
                              get_coll_set(n._id)
  return list_trans_coll


@get_execution_time
def topic_detail_view(request, group_id, app_Id=None):

  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)

  obj = node_collection.one({'_id': ObjectId(app_Id)})
  app = node_collection.one({'_id': ObjectId(obj.member_of[0])})
  app_id = app._id
  topic = "Topic"
  theme_id = None
  prior_obj = None
  # First get the navigation list till topic from theme map
  nav_l=request.GET.get('nav_li','')
  breadcrumbs_list = []
  nav_li = ""
  #a temp. variable which stores the lookup for append method
  breadcrumbs_list_append_temp=breadcrumbs_list.append
  if nav_l:
    nav_li = nav_l
    nav_l = str(nav_l).split(",")

    # create beadcrumbs list from navigation list sent from template.
    for each in nav_l:
        each_obj = node_collection.one({'_id': ObjectId(each) })
        # Theme object needs to be added in breadcrumbs for full navigation path from theme to topic
        # "nav_l" doesnt includes theme object since its not in tree hierarchy level, 
        # hence Match the first element and get its prior node which is theme object, to include it in breadcrumbs list
        # print "!!!!!!!!! ", each_obj.name
        if each == nav_l[0]:
            if each_obj.prior_node:
                theme_obj = node_collection.one({'_id': ObjectId(each_obj.prior_node[0] ) })
                theme_id = theme_obj._id
                breadcrumbs_list_append_temp( (str(theme_obj._id), theme_obj.name) )

        breadcrumbs_list_append_temp( (str(each_obj._id), each_obj.name) )



  if obj:
    if obj.prior_node:
        prior_obj = node_collection.one({'_id': ObjectId(obj.prior_node[0]) })


  ###shelf###
  shelves = []
  #a temp. variable which stores the lookup for append method
  shelves_append_temp=shelves.append
  shelf_list = {}
  auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) }) 

  if auth:
	  has_shelf_RT = node_collection.one({'_type': 'RelationType', 'name': u'has_shelf' })
	  shelf = triple_collection.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': has_shelf_RT._id})
	  shelf_list = {}

	  if shelf:
	    for each in shelf:
	        shelf_name = node_collection.one({'_id': ObjectId(each.right_subject)}) 
	        shelves_append_temp(shelf_name)

	        shelf_list[shelf_name.name] = []
	        #a temp. variable which stores the lookup for append method
                shelf_list_shlefname_append_temp=shelf_list[shelf_name.name].append
	        for ID in shelf_name.collection_set:
	        	shelf_item = node_collection.one({'_id': ObjectId(ID) })
	        	shelf_list_shlefname_append_temp(shelf_item.name)

	  else:
	    shelves = []
  
  # print "theme_id: ", theme_id
  return render_to_response('ndf/topic_details.html', 
	                                { 'node': obj,'app_id': app_id,"theme_id": theme_id, "prior_obj": prior_obj,
	                                  'group_id': group_id,'shelves': shelves,'topic': topic, 'nav_list':nav_li,
	                                  'groupid':group_id,'shelf_list': shelf_list,'breadcrumbs_list': breadcrumbs_list 
	                                },
	                                context_instance = RequestContext(request)
  )


def get_filtered_topic_resources(request, group_id, node_id):

    selfilters = request.POST.get('filters', None)
    query_dict = get_filter_querydict(json.loads(selfilters)) if selfilters else {}
    # print query_dict

    node_rel_cur = node_collection.one(
                                    {
                                        '_id': ObjectId( node_id ),
                                        'relation_set.taught_by': {'$exists': 'true'}
                                    },
                                    {
                                        'relation_set.taught_by': 1, '_id': 0
                                    }
                                )
    
    node_rel_list = node_rel_cur.relation_set[0].get('taught_by', [])

    filtered_taught_by_res = node_collection.find({
                        '_id': {'$in': node_rel_list},
                        '$and': query_dict
                    })

    primary_lang_resources = {}
    other_lang_resources = {}
    all_educationaluse = []
    language_selected = list(get_language_tuple(request.LANGUAGE_CODE))
    # print language_selected,"request.LANGUAGE_CODE: ", request.LANGUAGE_CODE

    # print filtered_taught_by_res.count()
    for each_res in filtered_taught_by_res:
        # if each_res.language :
        #     pass
        att_set_dict = get_dict_from_list_of_dicts(each_res.attribute_set)
        educationaluse = att_set_dict['educationaluse']

        all_educationaluse.append(educationaluse)

        if language_selected == each_res.language:
            temp = primary_lang_resources.get(educationaluse, [])
            temp.append(each_res)
            primary_lang_resources[educationaluse] = temp
            temp = ""
        else:
            temp = other_lang_resources.get(educationaluse, [])
            temp.append(each_res)
            other_lang_resources[educationaluse] = temp
            temp = ""

    # print "primary_lang_resources : ", primary_lang_resources
    # print "other_lang_resources: ", other_lang_resources

    all_educationaluse = list(set(all_educationaluse))

    # data = json.dumps({'primary_lang_resources': primary_lang_resources, 'other_lang_resources': other_lang_resources, 'all_educationaluse': all_educationaluse })

    # return HttpResponse(data)

    # return HttpResponse({'primary_lang_resources': primary_lang_resources, 'other_lang_resources': other_lang_resources, 'all_educationaluse': all_educationaluse })


    return render_to_response('ndf/topic_resources_listing.html', 
                                    { 
                                    'primary_lang_resources': primary_lang_resources, 'other_lang_resources': other_lang_resources, 'all_educationaluse': all_educationaluse,
                                    # 'node': obj,'app_id': app_id,"theme_id": theme_id, "prior_obj": prior_obj,
                                      'group_id': group_id,'groupid':group_id,
                                      'filtered_topics': 'filtered_topics'
                                      # 'shelves': shelves,'topic': topic, 'nav_list':nav_li,
                                      # 'shelf_list': shelf_list,'breadcrumbs_list': breadcrumbs_list
                                    },
                                    context_instance = RequestContext(request)
                            )

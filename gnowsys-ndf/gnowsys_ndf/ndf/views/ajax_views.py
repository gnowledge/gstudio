''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json  
import datetime
from operator import itemgetter

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.http import Http404
from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
import ast

from stemming.porter2 import stem

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.ndf.views.file import * 
from gnowsys_ndf.ndf.views.methods import check_existing_group, get_drawers, get_node_common_fields, create_grelation
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.mobwrite.models import ViewObj
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_profile_pic
from gnowsys_ndf.ndf.org2any import org2html

import json
from bson.objectid import ObjectId



 
db = get_database()
gs_collection = db[GSystem.collection_name]
collection = db[Node.collection_name]
theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
theme_item_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'theme_item'})
#This function is used to check (while creating a new group) group exists or not
#This is called in the lost focus event of the group_name text box, to check the existance of group, in order to avoid duplication of group names.

class Encoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, ObjectId):
			return str(obj)
		else:
			return obj

def checkgroup(request,group_name):
    titl=request.GET.get("gname","")
    retfl=check_existing_group(titl)
    if retfl:
        return HttpResponse("success")
    else:
        return HttpResponse("failure")
    


def select_drawer(request, group_id):
    
    if request.is_ajax() and request.method == "POST":
        
        checked = request.POST.get("homo_collection", '')
        selected_collection_list = request.POST.get("collection_list", '')
        node_id = request.POST.get("node_id", '')

        gcollection = db[Node.collection_name]

        if node_id:
            node_id = ObjectId(node_id)
        else:
            node_id = None

        if selected_collection_list:
            selected_collection_list = selected_collection_list.split(",")
            collection_list_ids = []
        
            i = 0
            while (i < len(selected_collection_list)):
                cn_node_id = ObjectId(selected_collection_list[i])
                
                if gcollection.Node.one({"_id": cn_node_id}):
                    collection_list_ids.append(cn_node_id)

                i = i+1

            drawer = get_drawers(group_id, node_id, collection_list_ids, checked)
        
            drawer1 = drawer['1']
            drawer2 = drawer['2']
                                      
            return render_to_response("ndf/drawer_widget.html", 
                                      {"widget_for": "collection",
                                       "drawer1": drawer1, 
                                       "drawer2": drawer2,
                                       "groupid": group_id
                                      },
                                      context_instance=RequestContext(request)
            )
          
        else:          
            
          # For creating a resource collection   
          if node_id is None:                             
            drawer = get_drawers(group_id, node_id, [], checked)  

            return render_to_response("ndf/drawer_widget.html", 
                                       {"widget_for": "collection", 
                                        "drawer1": drawer, 
                                        "groupid": group_id
                                       }, 
                                       context_instance=RequestContext(request)
            )

          # For editing a resource collection   
          else:

            drawer = get_drawers(group_id, node_id, [], checked)  
       
            return render_to_response("ndf/drawer_widget.html", 
                                       {"widget_for": "collection", 
                                        "drawer1": drawer['1'], 
                                        "groupid": group_id
                                       }, 
                                       context_instance=RequestContext(request)
            )

            
# This ajax view renders the output as "node view" by clicking on collections
def collection_nav(request, group_id):
    
    if request.is_ajax() and request.method == "POST":    
      node_id = request.POST.get("node_id", '')
      
      collection = db[Node.collection_name]

      node_obj = collection.Node.one({'_id': ObjectId(node_id)})
      return render_to_response('ndf/node_ajax_view.html', 
                                  { 'node': node_obj,
                                    'group_id': group_id,
                                    'groupid':group_id
                                  },
                                  context_instance = RequestContext(request)
      )

# This view handles the collection list of resource and its breadcrumbs
def collection_view(request, group_id):

  if request.is_ajax() and request.method == "POST":    
    node_id = request.POST.get("node_id", '')
    modify_option = request.POST.get("modify_option", '')
    breadcrumbs_list = request.POST.get("breadcrumbs_list", '')

    collection = db[Node.collection_name]
    node_obj = collection.Node.one({'_id': ObjectId(node_id)})
    print "\n\n------", node_obj, "\n\n"

    breadcrumbs_list = breadcrumbs_list.replace("&#39;","'")
    breadcrumbs_list = ast.literal_eval(breadcrumbs_list)

    # This is for breadcrumbs on collection which manipulates the breadcrumbs list (By clicking on breadcrumbs_list elements)
    if modify_option:
      tupl = ( str(node_obj._id), node_obj.name )
      Index = breadcrumbs_list.index(tupl) + 1
      # Arranges the breadcrumbs according to the breadcrumbs_list indexes
      breadcrumbs_list = [i for i in breadcrumbs_list if breadcrumbs_list.index(i) in range(Index)]  
      # Removes the adjacent duplicate elements in breadcrumbs_list
      breadcrumbs_list = [ breadcrumbs_list[i] for i in range(len(breadcrumbs_list)) if i == 0 or breadcrumbs_list[i-1] != breadcrumbs_list[i] ]

    else:
      # This is for adding the collection elements in breadcrumbs_list from navigation through collection of resource.
      breadcrumbs_list.append( (str(node_obj._id), node_obj.name) )

    return render_to_response('ndf/collection_ajax_view.html', 
                                  { 'node': node_obj,
                                    'group_id': group_id,
                                    'groupid':group_id,
                                    'breadcrumbs_list':breadcrumbs_list
                                  },
                                 context_instance = RequestContext(request)
    )

@login_required
def shelf(request, group_id):
    
    if request.is_ajax() and request.method == "POST":    
      shelf = request.POST.get("shelf_name", '')
      shelf_add = request.POST.get("shelf_add", '')
      shelf_remove = request.POST.get("shelf_remove", '')
      shelf_item_remove = request.POST.get("shelf_item_remove", '')

      shelf_available = ""
      shelf_item_available = ""
      collection= db[Node.collection_name]
      collection_tr = db[Triple.collection_name]

      shelf_gst = collection.Node.one({'_type': u'GSystemType', 'name': u'Shelf'})

      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      has_shelf_RT = collection.Node.one({'_type': u'RelationType', 'name': u'has_shelf'}) 
      dbref_has_shelf = has_shelf_RT.get_dbref()

      if shelf:
        shelf_gs = collection.Node.one({'name': unicode(shelf), 'member_of': [ObjectId(shelf_gst._id)] })
        if shelf_gs is None:
          shelf_gs = collection.GSystem()
          shelf_gs.name = unicode(shelf)
          shelf_gs.created_by = int(request.user.id)
          shelf_gs.member_of.append(shelf_gst._id)
          shelf_gs.save()

          shelf_R = collection_tr.GRelation()        
          shelf_R.subject = ObjectId(auth._id)
          shelf_R.relation_type = has_shelf_RT
          shelf_R.right_subject = ObjectId(shelf_gs._id)
          shelf_R.save()
        else:
          if shelf_add:
            shelf_item = ObjectId(shelf_add)  

            if shelf_item in shelf_gs.collection_set:
              shelf_Item = collection.Node.one({'_id': ObjectId(shelf_item)}).name       
              shelf_item_available = shelf_Item
              return HttpResponse("failure")

            else:
              collection.update({'_id': shelf_gs._id}, {'$push': {'collection_set': ObjectId(shelf_item) }}, upsert=False, multi=False)
              shelf_gs.reload()

          elif shelf_item_remove:
            shelf_item = collection.Node.one({'name': unicode(shelf_item_remove)})._id
            collection.update({'_id': shelf_gs._id}, {'$pull': {'collection_set': ObjectId(shelf_item) }}, upsert=False, multi=False)      
            shelf_gs.reload()
          
          else:
            shelf_available = shelf

      elif shelf_remove:
        shelf_gs = collection.Node.one({'name': unicode(shelf_remove), 'member_of': [ObjectId(shelf_gst._id)] })
        shelf_rel = collection.Node.one({'_type': 'GRelation', 'subject': ObjectId(auth._id),'right_subject': ObjectId(shelf_gs._id) })

        shelf_rel.delete()
        shelf_gs.delete()

      else:
        shelf_gs = None

      shelves = []
      shelf_list = {}

      if auth:
        shelf = collection_tr.Triple.find({'_type': 'GRelation','subject': ObjectId(auth._id), 'relation_type': dbref_has_shelf })        
        
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

      return render_to_response('ndf/shelf.html', 
                                  { 'shelf_obj': shelf_gs,'shelf_list': shelf_list,'shelves': shelves,
                                    'groupid':group_id
                                  },
                                  context_instance = RequestContext(request)
      )


def drawer_widget(request, group_id):
  if request.is_ajax() and request.method == "POST":
    drawers = None
    drawer1 = None
    drawer2 = None

    node = request.POST.get("node_id", '')
    field = request.POST.get("field", '')
    app = request.POST.get("app", '')
    # print "\nfield: ", field
    # print "\n app: ", app
   

    if node:
      node = collection.Node.one({'_id': ObjectId(node) })
      if field == "prior_node":
        app = None
	
        drawers = get_drawers(group_id, node._id, node.prior_node, app)
      elif field == "teaches":
	app = None
	nlist=[]
	relationtype = collection.Node.one({"_type":"RelationType","name":"teaches"})
	list_grelations = collection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
	for relation in list_grelations:
		nlist.append(ObjectId(relation.right_subject))
		
	
	drawers = get_drawers(group_id, node._id, nlist, app)
      elif field == "assesses":
	app = None
	nlist=[]
	relationtype = collection.Node.one({"_type":"RelationType","name":"assesses"})
	list_grelations = collection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
	for relation in list_grelations:
		nlist.append(ObjectId(relation.right_subject))
		
	
	drawers = get_drawers(group_id, node._id, nlist, app)
      elif field == "collection":
        if app == "Quiz":
          app = "QuizItem"
        elif app == "Theme":
          app = "Theme"
        elif app == "Theme Item":
          app == "theme_item"
        elif app == "Topic":
          app = "Topic"
        elif app == "Module":
          app = "Module"
        else:
          app = None

        drawers = get_drawers(group_id, node._id, node.collection_set, app)
      
      drawer1 = drawers['1']
      drawer2 = drawers['2']

    else:
      if field == "collection" and app == "Quiz":
        app = "QuizItem"
      elif field == "collection" and app == "Theme":
        app = "Theme"
      elif field == "collection" and app == "Theme Item":
        app = "theme_item"
      elif field == "collection" and app == "Course":
        app = "Module"
      else:
        app = None

      drawer1 = get_drawers(group_id, None, [], app)


    return render_to_response('ndf/drawer_widget.html', 
                                { 'widget_for': field,'drawer1': drawer1, 'drawer2': drawer2,
                                  'group_id': group_id,'groupid': group_id
                                },
                                context_instance = RequestContext(request)
    )


def get_collection_list(collection_list, node):
  inner_list = []
  error_list = []
  
  if node.collection_set:
    for each in node.collection_set:
      col_obj = collection.Node.one({'_id': ObjectId(each)})
      if col_obj:
        if theme_item_GST._id in col_obj.member_of or topic_GST._id in col_obj.member_of:
          for cl in collection_list:
            if cl['id'] == node.pk:
              node_type = collection.Node.one({'_id': ObjectId(col_obj.member_of[0])}).name
              inner_sub_dict = {'name': col_obj.name, 'id': col_obj.pk , 'node_type': node_type}
              inner_sub_list = [inner_sub_dict]
              inner_sub_list = get_collection_list(inner_sub_list, col_obj)

              if inner_sub_list:
                inner_list.append(inner_sub_list[0])
              else:
                inner_list.append(inner_sub_dict)

              cl.update({'children': inner_list })
      else:
        error_message = "\n TreeHierarchyError: Node with given ObjectId ("+ str(each) +") not found!!!\n"
        print "\n " + error_message

    return collection_list

  else:
    return collection_list


def get_tree_hierarchy(request, group_id, node_id):

    node = collection.Node.one({'_id':ObjectId(node_id)})
    data = ""
    collection_list = []
    themes_list = []

    theme_node = collection.Node.one({'_id': ObjectId(node._id) })
    # print "\ntheme_node: ",theme_node.name,"\n"
    if theme_node.collection_set:

      for e in theme_node.collection_set:
        objs = collection.Node.one({'_id': ObjectId(e) })
        for l in objs.collection_set:
          themes_list.append(l)


      for each in theme_node.collection_set:
        obj = collection.Node.one({'_id': ObjectId(each) })
        if obj._id not in themes_list:
          if theme_item_GST._id in obj.member_of or topic_GST._id in obj.member_of:

            node_type = collection.Node.one({'_id': ObjectId(obj.member_of[0])}).name
            collection_list.append({'name': obj.name, 'id': obj.pk, 'node_type': node_type})
            collection_list = get_collection_list(collection_list, obj)

    data = collection_list

    return HttpResponse(json.dumps(data))


def add_sub_themes(request, group_id):

  if request.is_ajax() and request.method == "POST":    

    context_node_id = request.POST.get("context_node", '')
    sub_theme_name = request.POST.get("sub_theme_name", '')
    themes_list = request.POST.get("nodes_list", '')
    themes_list = themes_list.replace("&quot;","'")
    themes_list = ast.literal_eval(themes_list)

    theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'theme_item'})
    context_node = collection.Node.one({'_id': ObjectId(context_node_id) })
    
    # Save the sub-theme first  
    if sub_theme_name:
      if not sub_theme_name.upper() in (theme_name.upper() for theme_name in themes_list):

        node = collection.GSystem()
        # get_node_common_fields(request, node, group_id, theme_GST)
      
        node.save(is_changed=get_node_common_fields(request, node, group_id, theme_item_GST))
        node.reload()
        # Add this sub-theme into context nodes collection_set
        collection.update({'_id': context_node._id}, {'$push': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)
        context_node.reload()

        return HttpResponse("success")

      return HttpResponse("failure")

    return HttpResponse("None")


def add_theme_item(request, group_id):

  if request.is_ajax() and request.method == "POST":    

    context_theme_id = request.POST.get("context_theme", '')
    name =request.POST.get('name','')

    context_theme = collection.Node.one({'_id': ObjectId(context_theme_id) })

    list_theme_items = []
    if name and context_theme:

      for each in context_theme.collection_set:
        obj = collection.Node.one({'_id': ObjectId(each) })
        if obj.name == name:
          return HttpResponse("failure")

      theme_item_node = collection.GSystem()

      theme_item_node.save(is_changed=get_node_common_fields(request, theme_item_node, group_id, theme_item_GST))
      theme_item_node.reload()

      # Add this theme item into context theme's collection_set
      collection.update({'_id': context_theme._id}, {'$push': {'collection_set': ObjectId(theme_item_node._id) }}, upsert=False, multi=False)
      context_theme.reload()

    return HttpResponse("success")

def add_topics(request, group_id):
  if request.is_ajax() and request.method == "POST":    
    # print "\n Inside add_topics ajax view\n"
    context_node_id = request.POST.get("context_node", '')
    add_topic_name = request.POST.get("add_topic_name", '')
    topics_list = request.POST.get("nodes_list", '')
    topics_list = topics_list.replace("&quot;","'")
    topics_list = ast.literal_eval(topics_list)

    topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
    context_node = collection.Node.one({'_id': ObjectId(context_node_id) })


    # Save the topic first  
    if add_topic_name:
      # print "\ntopic name: ", add_topic_name
      if not add_topic_name.upper() in (topic_name.upper() for topic_name in topics_list):
        node = collection.GSystem()
        # get_node_common_fields(request, node, group_id, topic_GST)
      
        node.save(is_changed=get_node_common_fields(request, node, group_id, topic_GST))
        node.reload()        
        # Add this topic into context nodes collection_set
        collection.update({'_id': context_node._id}, {'$push': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)
        context_node.reload()

        return HttpResponse("success")

      return HttpResponse("failure")

    return HttpResponse("None")


def add_page(request, group_id):
  if request.is_ajax() and request.method == "POST":    

    context_node_id = request.POST.get("context_node", '')
    gst_page = collection.Node.one({'_type': "GSystemType", 'name': "Page"})
    context_node = collection.Node.one({'_id': ObjectId(context_node_id)})
    name =request.POST.get('name','')

    collection_list = []
    if context_node:
      for each in context_node.collection_set:
        obj = collection.Node.one({'_id': ObjectId(each), 'group_set': ObjectId(group_id)})
        collection_list.append(obj.name)

      if name not in collection_list:

        page_node = collection.GSystem()
        page_node.save(is_changed=get_node_common_fields(request, page_node, group_id, gst_page))

        context_node.collection_set.append(page_node._id)
        context_node.save()

        return HttpResponse("success")

      else:
        return HttpResponse("failure")

    return HttpResponse("None")


def add_file(request, group_id):
  # this is context node getting from the url get request
  context_node_id=request.GET.get('context_node','')

  if request.method == "POST":   

    new_list = []
    # For checking the node is already available in gridfs or not
    for index, each in enumerate(request.FILES.getlist("doc[]", "")):
      fcol = get_database()[File.collection_name]
      fileobj = fcol.File()
      filemd5 = hashlib.md5(each.read()).hexdigest()
      if not fileobj.fs.files.exists({"md5":filemd5}):
        # If not available append to the list for making the collection for topic bellow
        new_list.append(each)
      else:
        # If availbale ,then return to the topic page
        var1 = "/"+group_id+"/topic_details/"+context_node_id+""
        return HttpResponseRedirect(var1)

    # After taking new_lst[] , now go for saving the files 
    submitDoc(request, group_id)

  # After file gets saved , that file's id should be saved in collection_set of context topic node
  context_node = collection.Node.one({'_id': ObjectId(context_node_id)})
  for k in new_list:
    file_obj = collection.Node.one({'_type': 'File', 'name': unicode(k) })

    context_node.collection_set.append(file_obj._id)
    context_node.save()

  var1 = "/"+group_id+"/topic_details/"+context_node_id+""

  return HttpResponseRedirect(var1)



def node_collection(node=None, group_id=None):

    theme_item_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'theme_item'})

    if node.collection_set:
      for each in node.collection_set:
        
        each_node = collection.Node.one({'_id': ObjectId(each)})
        
        if each_node.collection_set:
          
          node_collection(each_node, group_id)
        else:
          # After deleting theme instance it's should also remove from collection_set
          cur = collection.Node.find({'member_of': {'$all': [theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

          for e in cur:
            if each_node._id in e.collection_set:
              collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(each_node._id) }}, upsert=False, multi=False)      


          # print "\n node ", each_node.name ,"has been deleted \n"
          each_node.delete()


      # After deleting theme instance it's should also remove from collection_set
      cur = collection.Node.find({'member_of': {'$all': [theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

      for e in cur:
        if node._id in e.collection_set:
          collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)      

      # print "\n node ", node.name ,"has been deleted \n"
      node.delete()

    else:

      # After deleting theme instance it's should also remove from collection_set
      cur = collection.Node.find({'member_of': {'$all': [theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

      for e in cur:
        if node._id in e.collection_set:
          collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)      


      # print "\n node ", node.name ,"has been deleted \n"
      node.delete()

    return True


def theme_node_collection(node=None, group_id=None):

    theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
    theme_item_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'theme_item'})

    if node.collection_set:
      for each in node.collection_set:
        
        each_node = collection.Node.one({'_id': ObjectId(each)})
        
        if each_node.collection_set:
          
          node_collection(each_node, group_id)
        else:
          # After deleting theme instance it's should also remove from collection_set
          cur = collection.Node.find({'member_of': {'$all': [theme_GST._id,theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

          for e in cur:
            if each_node._id in e.collection_set:
              collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(each_node._id) }}, upsert=False, multi=False)      


          # print "\n node ", each_node.name ,"has been deleted \n"
          each_node.delete()

      # After deleting theme instance it's should also remove from collection_set
      cur = collection.Node.find({'member_of': {'$all': [theme_GST._id,theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

      for e in cur:
        if node._id in e.collection_set:
          collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)      

      # print "\n node ", node.name ,"has been deleted \n"
      node.delete()

    else:

      # After deleting theme instance it's should also remove from collection_set
      cur = collection.Node.find({'member_of': {'$all': [theme_GST._id,theme_item_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

      for e in cur:
        if node._id in e.collection_set:
          collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)      

      # print "\n node ", node.name ,"has been deleted \n"
      node.delete()

    return True


def delete_themes(request, group_id):
  '''delete themes objects'''
  send_dict = []
  deleteobjects = ""
  deleteobj = ""
  if request.is_ajax() and request.method =="POST":
    context_node_id=request.POST.get('context_theme','') 
    if context_node_id:
      context_theme_node = collection.Node.one({'_id': ObjectId(context_node_id)}) 

     
    confirm = request.POST.get("confirm","")
    deleteobj = request.POST.get('deleteobj',"")
    theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
    theme_item_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'theme_item'})

    if deleteobj:
      obj = collection.Node.one({'_id': ObjectId(deleteobj) })
      obj.delete()          
      node = collection.Node.one({'member_of': {'$in':[theme_GST._id, theme_item_GST._id]}, 'collection_set': ObjectId(deleteobj) })
      collection.update({'_id': node._id}, {'$pull': {'collection_set': ObjectId(deleteobj) }}, upsert=False, multi=False)      

    else:
      deleteobjects = request.POST['deleteobjects']

    if deleteobjects:
      for each in  deleteobjects.split(","):
          node = collection.Node.one({ '_id': ObjectId(each)})
          # print "\n confirmed objects: ", node.name

          if confirm:
            
            if context_node_id:
              node_collection(node, group_id)
              if node._id in context_theme_node.collection_set:
                collection.update({'_id': context_theme_node._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)      


            else:
              theme_node_collection(node, group_id)

          else:
            send_dict.append({"title":node.name})

  return StreamingHttpResponse(json.dumps(send_dict).encode('utf-8'),content_type="text/json", status=200)

  

@login_required
def change_group_settings(request,group_id):
    '''
	changing group's object data
    '''
    if request.is_ajax() and request.method =="POST":
        try:
            edit_policy = request.POST['edit_policy']
            group_type = request.POST['group_type']
            subscription_policy = request.POST['subscription_policy']
            visibility_policy = request.POST['visibility_policy']
            disclosure_policy = request.POST['disclosure_policy']
            encryption_policy = request.POST['encryption_policy']
           # group_id = request.POST['group_id']
            group_node = gs_collection.GSystem.one({"_id": ObjectId(group_id)})
            if group_node :
                group_node.edit_policy = edit_policy
                group_node.group_type = group_type
                group_node.subscription_policy = subscription_policy
                group_node.visibility_policy = visibility_policy
                group_node.disclosure_policy = disclosure_policy
                group_node.encryption_policy = encryption_policy
                group_node.modified_by = int(request.user.id)
                group_node.save()
                return HttpResponse("changed successfully")
        except:
            return HttpResponse("failed")
    return HttpResponse("failed") 

def get_module_set_list(node):
    '''
        Returns the list of collection inside the collections with hierarchy as they are in collection
    '''
    list = []
    for each in node.collection_set:
        each = collection.Node.one({'_id':each})
        dict = {}
        dict['id'] = unicode(each._id)
        dict['version_no'] = hm_obj.get_current_version(each)
        if each._id not in list_of_collection:
            list_of_collection.append(each._id)
            if each.collection_set :                                   #checking that same collection can'not be called again
                dict['collection'] = get_module_set_list(each)         #calling same function recursivaly
        list.append(dict)
    return list


list_of_collection = []
hm_obj = HistoryManager()
GST_MODULE = gs_collection.GSystemType.one({'name': GAPPS[8]})

@login_required
def make_module_set(request, group_id):
    '''
    This methode will create module of collection and stores objectid's with version number's
    '''
    if request.is_ajax():
        try:
            _id = request.GET.get("_id","")
            if _id:
                node = collection.Node.one({'_id':ObjectId(_id)})
                if node:
                    list_of_collection.append(node._id)
                    dict = {}
                    dict['id'] = unicode(node._id)
                    dict['version_no'] = hm_obj.get_current_version(node)
                    if node.collection_set:
                        dict['collection'] = get_module_set_list(node)     #gives the list of collection with proper hierarchy as they are

                    #creating new Gsystem object and assining data of collection object
                    gsystem_obj = collection.GSystem()
                    gsystem_obj.name = unicode(node.name)
                    gsystem_obj.content = unicode(node.content)
                    gsystem_obj.member_of.append(GST_MODULE._id)
                    gsystem_obj.group_set.append(ObjectId(group_id))
                    # if usrname not in gsystem_obj.group_set:        
                    #     gsystem_obj.group_set.append(int(usrname))
                    user_id = int(request.user.id)
                    gsystem_obj.created_by = user_id
                    gsystem_obj.modified_by = user_id
                    if user_id not in gsystem_obj.contributors:
                        gsystem_obj.contributors.append(user_id)
                    gsystem_obj.module_set.append(dict)
                    module_set_md5 = hashlib.md5(str(gsystem_obj.module_set)).hexdigest() #get module_set's md5
                    check =check_module_exits(module_set_md5)          #checking module already exits or not
                    if(check == 'True'):
                        return HttpResponse("This module already Exists")
                    else:
                        gsystem_obj.save()
                        create_relation_of_module(node._id, gsystem_obj._id)
                        create_version_of_module(gsystem_obj._id,node._id)
                        check1 = sotore_md5_module_set(gsystem_obj._id, module_set_md5)
                        if (check1 == 'True'):
                            return HttpResponse("module succesfull created")
                        else:
                            gsystem_obj.delete()
                            return HttpResponse("Error Occured while storing md5 of object in attribute'")
                else:
                    return HttpResponse("Object not present corresponds to this id")

            else:
                return HttpResponse("Not a valid id passed")
        except Exception as e:
            print "Error:",e
            return HttpResponse(e)

def sotore_md5_module_set(object_id,module_set_md5):
    '''
    This method will store md5 of module_set of perticular GSystem into an Attribute
    '''
    node_at = collection.Node.one({'$and':[{'_type': 'AttributeType'},{'name': 'module_set_md5'}]}) #retrving attribute type
    if node_at is not None:
        try:
            attr_obj =  collection.GAttribute()                #created instance of attribute class
            attr_obj.attribute_type = node_at
            attr_obj.subject = object_id
            attr_obj.object_value = unicode(module_set_md5)
            attr_obj.save()
        except Exception as e:
            print "Exception:",e
            return 'False'
        return 'True'
    else:
        print "Run 'python manage.py filldb' commanad to create AttributeType 'module_set_md5' "
        return 'False'

#-- under construction
def create_version_of_module(subject_id,node_id):
    '''
    This method will create attribute version_no of module with at type version
    '''
    rt_has_module = collection.Node.one({'_type':'RelationType', 'name':'has_module'})
    relation = collection.Triple.find({'_type':'GRelation','relation_type.$id':rt_has_module._id,'subject':node_id})
    at_version = collection.Node.one({'_type':'AttributeType', 'name':'version'})
    attr_versions = []
    if relation.count() > 0:
        for each in relation:
            module_id = collection.Triple.one({'_id':each['_id']})
            if module_id:
                attr = collection.Triple.one({'_type':'GAttribute','attribute_type.$id':at_version._id,'subject':ObjectId(module_id.right_subject)})
            if attr:
                attr_versions.append(attr.object_value)
    print attr_versions,"Test version"
    if attr_versions:
        attr_versions.sort()
        attr_ver = float(attr_versions[-1])
        attr = collection.GAttribute()
        attr.attribute_type = at_version
        attr.subject = subject_id
        attr.object_value = round((attr_ver+0.1),1)
        attr.save()
    else:
        attr = collection.GAttribute()
        attr.attribute_type = at_version
        attr.subject = ObjectId(subject_id)
        attr.object_value = 1
        print "berfore save",attr
        attr.save()
            

def create_relation_of_module(subject_id, right_subject_id):
    rt_has_module = collection.Node.one({'_type':'RelationType', 'name':'has_module'})
    if rt_has_module and subject_id and right_subject_id:
        relation = collection.GRelation()                         #instance of GRelation class
        relation.relation_type = rt_has_module
        relation.right_subject = right_subject_id
        relation.subject = subject_id
        relation.save()

    

def check_module_exits(module_set_md5):
    '''
    This method will check is module already exits ?
    '''
    node_at = collection.Node.one({'$and':[{'_type': 'AttributeType'},{'name': 'module_set_md5'}]})
    attribute = collection.Triple.one({'_type':'GAttribute', 'attribute_type.$id':node_at._id, 'object_value':module_set_md5}) 
    if attribute is not None:
        return 'True'
    else:
        return 'False'
        


def walk(node):
    hm = HistoryManager()
    list = []
    for each in node:
       dict = {}
       node = collection.Node.one({'_id':ObjectId(each['id'])})
       n = hm.get_version_document(node,each['version_no'])
       dict['label'] = n.name
       dict['id'] = each['id']
       dict['version_no'] = each['version_no']
       if "collection" in each.keys():
             dict['children'] = walk(each['collection'])
       list.append(dict)
    return list

def get_module_json(request, group_id):
    _id = request.GET.get("_id","")
    node = collection.Node.one({'_id':ObjectId(_id)})
    data = walk(node.module_set)
    return HttpResponse(json.dumps(data))



# ------------- For generating graph json data ------------
def graph_nodes(request, group_id):

  collection = db[Node.collection_name]
  page_node = collection.Node.one({'_id':ObjectId(request.GET.get("id"))})
  page_node.get_neighbourhood(page_node.member_of)
  # print page_node.keys()
  coll_relation = { 'relation_name':'has_collection', 'inverse_name':'member_of_collection' }

  prior_relation = { 'relation_name':'prerequisite', 'inverse_name':'is_required_for' }

  def _get_node_info(node_id):
    node = collection.Node.one( {'_id':node_id}  )
    # mime_type = "true"  if node.structure.has_key('mime_type') else 'false'

    return node.name

  # def _get_username(id_int):
    # return User.objects.get(id=id_int).username

  # def _get_node_url(node_id):

  #   node_url = '/' + str(group_id)
  #   node = collection.Node.one({'_id':node_id})

  #   if len(node.member_of) > 1:
  #     if node.mime_type == 'image/jpeg':
  #       node_url += '/image/image_detail/' + str(node_id)
  #     elif node.mime_type == 'video':
  #       node_url += '/video/video_detail/' + str(node_id)

  #   elif len(node.member_of) == 1:
  #     gapp_name = (collection.Node.one({'_id':node.member_of[0]}).name).lower()

  #     if gapp_name == 'forum':
  #       node_url += '/forum/show/' + str(node_id)

  #     elif gapp_name == 'file':
  #       node_url += '/image/image_detail/' + str(node_id)

  #     elif gapp_name == 'page':
  #       node_url += '/page/details/' + str(node_id)

  #     elif gapp_name == 'quiz' or 'quizitem':
  #       node_url += '/quiz/details/' + str(node_id)
      
  #   return node_url


  # page_node_id = str(id(page_node._id))
  node_metadata ='{"screen_name":"' + page_node.name + '",  "title":"' + page_node.name + '",  "_id":"'+ str(page_node._id) +'", "refType":"GSystem"}, '
  node_relations = ''
  exception_items = [
                      "name", "content", "_id", "login_required", "attribute_set",
                      "member_of", "status", "comment_enabled", "start_publication",
                      "_type", "contributors", "created_by", "modified_by", "last_update", "url", "featured",
                      "created_at", "group_set", "type_of", "content_org", "author_set",
                      "fs_file_ids", "file_size", "mime_type", "location", "language",
                      "property_order", "rating", "apps_list", "annotations", "instance of"
                    ]

  # username = User.objects.get(id=page_node.created_by).username

  i = 1
  for key, value in page_node.items():
    
    if (key in exception_items) or (not value):      
      pass

    elif isinstance(value, list):

      if len(value):

        # node_metadata +='{"screen_name":"' + key + '", "_id":"'+ str(i) +'_r"}, '
        node_metadata +='{"screen_name":"' + key + '", "_id":"'+ str(abs(hash(key+str(page_node._id)))) +'_r"}, '
        node_relations += '{"type":"'+ key +'", "from":"'+ str(page_node._id) +'", "to": "'+ str(abs(hash(key+str(page_node._id)))) +'_r"},'
        # key_id = str(i)
        key_id = str(abs(hash(key+str(page_node._id))))
        # i += 1
        
        # if key in ("modified_by", "author_set"):
        #   for each in value:
        #     node_metadata += '{"screen_name":"' + _get_username(each) + '", "_id":"'+ str(i) +'_n"},'
        #     node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(i) +'_n"},'
        #     i += 1

        # else:

        for each in value:
          # print "\n====", key, "------", type(each)

          if isinstance(each, ObjectId):
            node_name = _get_node_info(each)
            if key == "collection_set":
              inverse = coll_relation['inverse_name'] 
            elif key == "prior_node":
              inverse = prior_relation['inverse_name'] 
            else:
              inverse = ""

            node_metadata += '{"screen_name":"' + node_name + '", "title":"' + page_node.name + '", "_id":"'+ str(each) +'", "refType":"Relation", "inverse":"' + inverse + '", "flag":"1"},'
            # node_metadata += '{"screen_name":"' + node_name + '", "_id":"'+ str(each) +'", "refType":"relation"},'
            node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(each) +'"},'
            i += 1

          # if "each" is Object of GSystem
          elif isinstance(each, GSystem):           
            
            node_metadata += '{"screen_name":"' + each.name + '", "title":"' + page_node.name + '", "_id":"'+ str(each._id) + '", "refType":"Relation"},'
            node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(each._id) +'"},'            

          else:

            node_metadata += '{"screen_name":"' + unicode(each) + '", "_id":"'+ unicode(each) +'_n"},'
            node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ unicode(each) +'_n"},'
            i += 1
    
    else:
      # possibly gives GAttribute
      node_metadata +='{"screen_name":"' + key + '", "_id":"'+ str(abs(hash(key+str(page_node._id)))) +'_r"},'
      node_relations += '{"type":"'+ key +'", "from":"'+ str(page_node._id) +'", "to": "'+ str(abs(hash(key+str(page_node._id)))) +'_r"},'

      # key_id = str(i)     
      key_id = str(abs(hash(key+str(page_node._id))))

      if isinstance( value, list):
        for each in value:
          node_metadata += '{"screen_name":"' + each + '", "_id":"'+ str(i) +'_n"},'
          node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(i) +'_n"},'
          i += 1 
      
      else:
        node_metadata += '{"screen_name":"' + str(value) + '", "_id":"'+ str(i) +'_n"},'
        node_relations += '{"type":"'+ key +'", "from":"'+ str(abs(hash(key+str(page_node._id)))) +'_r", "to": "'+ str(i) +'_n"},'
        
        i += 1
    # End of if - else
  # End of for loop


  # # getting all the relations of current node
  # node_rel = page_node.get_possible_relations(page_node.member_of)
  # # print "\n\n", node_rel
  # for keyy, vall in node_rel.iteritems():

  #   if vall['subject_or_right_subject_list']:

  #     for eachnode in vall['subject_or_right_subject_list']:
    
    # if keyy == "event_organised_by":
    #   pass
    #   # node_metadata +='{"screen_name":"' + keyy + '", "_id":"'+ str(abs(hash(keyy+str(page_node._id)))) +'_r"},'
    #   # node_relations += '{"type":"'+ keyy +'", "from":"'+ str(page_node._id) +'", "to": "'+ str(abs(hash(keyy+str(page_node._id)))) +'_r"},'

    #   # node_metadata += '{"screen_name":"' + str(vall) + '", "_id":"'+ str(i) +'_n"},'
    #   # node_relations += '{"type":"'+ keyy +'", "from":"'+ str(abs(hash(keyy+str(page_node._id)))) +'_r", "to": "'+ str(i) +'_n"},'
    
    # else:

    #   node_metadata +='{"screen_name":"' + keyy + '", "_id":"'+ str(abs(hash(keyy+str(page_node._id)))) +'_r"},'
    #   node_relations += '{"type":"'+ keyy +'", "from":"'+ str(page_node._id) +'", "to": "'+ str(abs(hash(keyy+str(page_node._id)))) +'_r"},'
      
    #   vall = vall.altnames if ( len(vall['altnames'])) else _get_node_info(vall['subject_or_right_subject_list'][0])
    #   node_metadata += '{"screen_name":"' + str(vall) + '", "_id":"'+ str(i) +'_n"},'
    #   node_relations += '{"type":"'+ keyy +'", "from":"'+ str(abs(hash(keyy+str(page_node._id)))) +'_r", "to": "'+ str(i) +'_n"},'
    # print "\nkey : ", key, "=====", val


  node_metadata = node_metadata[:-1]
  node_relations = node_relations[:-1]

  node_graph_data = '{ "node_metadata": [' + node_metadata + '], "relations": [' + node_relations + '] }'

  # print node_graph_data

  return StreamingHttpResponse(node_graph_data)

# ------ End of processing for graph ------



def get_data_for_switch_groups(request,group_id):
    coll_obj_list = []
    node_id = request.GET.get("object_id","")
    st = collection.Node.find({"_type":"Group"})
    node = collection.Node.one({"_id":ObjectId(node_id)})
    for each in node.group_set:
        coll_obj_list.append(collection.Node.one({'_id':each}))
    data_list=set_drawer_widget(st,coll_obj_list)
    return HttpResponse(json.dumps(data_list))



def get_data_for_drawer(request, group_id):
    '''
    designer module's drawer widget function
    '''
    coll_obj_list = []
    node_id = request.GET.get("id","")
    st = collection.Node.find({"_type":"GSystemType"})
    node = collection.Node.one({"_id":ObjectId(node_id)})
    for each in node.collection_set:
        coll_obj_list.append(collection.Node.one({'_id':each}))
    data_list=set_drawer_widget(st,coll_obj_list)
    return HttpResponse(json.dumps(data_list))

# This method is not in use
def get_data_for_user_drawer(request, group_id,):
    '''
    This method will return data for user widget 
    '''
    d1 = []
    d2 = []
    draw1 = {}
    draw2 = {}
    drawer1 = []
    drawer2 = []
    data_list = []
    all_batch_user = []
    users = []
    st_batch_id = request.GET.get('st_batch_id','')
    node_id = request.GET.get('_id','')
    if st_batch_id:
        batch_coll = collection.GSystem.find({'member_of': {'$all': [ObjectId(st_batch_id)]}, 'group_set': {'$all': [ObjectId(group_id)]}})
        group = collection.Node.one({'_id':ObjectId(group_id)})
        if batch_coll:
            for each in batch_coll:
                users = users+each.author_set
        else:
            users = []
        user_list = list(set(group.author_set) - set(users))
        for each in user_list:
            user= User.objects.get(id=each)
            dic = {}
            dic['id'] = user.id   
            dic['name'] = user.username
            d1.append(dic)
        draw1['drawer1'] = d1
        data_list.append(draw1)
        if node_id:
            for each in collection.Node.one({'_id':ObjectId(node_id)}).author_set:
                user= User.objects.get(id=each)
                dic = {}
                dic['id'] = user.id   
                dic['name'] = user.username
                d2.append(dic)
        draw2['drawer2'] = d2
        data_list.append(draw2)
        return HttpResponse(json.dumps(data_list))
    else:
        return HttpResponse("GSystemType for batch required")


def set_drawer_widget_for_users(st,coll_obj_list):
    '''
    NOTE : this method is used only for user drwers (Django user class)
    '''
    draw2={}
    draw1={}
    data_list=[]
    d1=[]
    d2=[]
    for each in st:
       dic = {}
       dic['id'] = str(each.id)
       dic['name'] = each.username
       d1.append(dic)
    draw1['drawer1'] = d1
    data_list.append(draw1)
    
    for each in coll_obj_list:
       dic = {}
       dic['id'] = str(each.id)
       dic['name'] = each.username
       d2.append(dic)
    draw2['drawer2'] = d2
    data_list.append(draw2)
    return data_list 



def get_data_for_batch_drawer(request, group_id):
    '''
    This method will return data for batch drawer widget
    '''
    d1 = []
    d2 = []
    draw1 = {}
    draw2 = {}
    drawer1 = []
    drawer2 = []
    data_list = []
    st = collection.Node.one({'_type':'GSystemType','name':'Student'})
    node_id = request.GET.get('_id','')
    batch_coll = collection.GSystem.find({'member_of': {'$all': [st._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
    if node_id:
        rt_has_batch_member = collection.Node.one({'_type':'RelationType','name':'has_batch_member'})
        relation_coll = collection.Triple.find({'_type':'GRelation','relation_type.$id':rt_has_batch_member._id,'right_subject':ObjectId(node_id)})
        for each in relation_coll:
            dic = {}
            n = collection.Node.one({'_id':ObjectId(each.subject)})
            drawer2.append(n)
    for each in batch_coll:
        drawer1.append(each)
    drawer_set1 = set(drawer1) - set(drawer2)
    print len(drawer_set1),"drawer1-count"
    drawer_set2 = drawer2
    for each in drawer_set1:
        dic = {}
        dic['id'] = str(each._id)
        dic['name'] = each.name
        d1.append(dic)
    draw1['drawer1'] = d1
    data_list.append(draw1)
    for each in drawer_set2:
        dic = {}
        dic['id'] = str(each._id)
        dic['name'] = each.name
        d2.append(dic)
    draw2['drawer2'] = d2
    data_list.append(draw2)
    return HttpResponse(json.dumps(data_list))
        

def set_drawer_widget(st,coll_obj_list):
    '''
    this method will set data for drawer widget
    '''
    stobjs=[]
    coll_objs=[]
    data_list = []
    d1 = []
    d2 = []
    draw1 = {}
    draw2 = {}
    drawer1=[]
    drawer2=[]
    for each in st:
        stobjs.append(each['_id'])
    for each in coll_obj_list:
        coll_objs.append(each['_id'])
    drawer1_set = set(stobjs) - set(coll_objs)
    lstset=[]
    for each in drawer1_set:
        obj=collection.Node.one({'_id':each})
        lstset.append(obj)
    drawer1=lstset
    drawer2 = coll_obj_list
    for each in drawer1:
       dic = {}
       dic['id'] = str(each['_id'])
       dic['name'] = each['name']
       d1.append(dic)
    draw1['drawer1'] = d1
    data_list.append(draw1)
    for each in drawer2:
       dic = {}
       dic['id'] = str(each['_id'])
       dic['name'] = each['name']
       d2.append(dic)
    draw2['drawer2'] = d2
    data_list.append(draw2)
    return data_list 

def get_data_for_drawer_of_attributetype_set(request, group_id):
    '''
    this method will fetch data for designer module's drawer widget
    '''
    data_list = []
    d1 = []
    d2 = []
    draw1 = {}
    draw2 = {}
    node_id = request.GET.get("id","")
    coll_obj_list = []
    st = collection.Node.find({"_type":"AttributeType"})
    node = collection.Node.one({"_id":ObjectId(node_id)})
    for each in node.attribute_type_set:
        coll_obj_list.append(each)
    drawer1 = list(set(st) - set(coll_obj_list))
    drawer2 = coll_obj_list
    for each in drawer1:
       dic = {}
       dic['id'] = str(each._id)
       dic['name'] = str(each.name)
       d1.append(dic)
    draw1['drawer1'] = d1
    data_list.append(draw1)
    for each in drawer2:
       dic = {}
       dic['id'] = str(each._id)
       dic['name'] = str(each.name)
       d2.append(dic)
    draw2['drawer2'] = d2
    data_list.append(draw2)
    return HttpResponse(json.dumps(data_list))

def get_data_for_drawer_of_relationtype_set(request, group_id):
    '''
    this method will fetch data for designer module's drawer widget
    '''
    data_list = []
    d1 = []
    d2 = []
    draw1 = {}
    draw2 = {}
    node_id = request.GET.get("id","")
    coll_obj_list = []
    st = collection.Node.find({"_type":"RelationType"})
    node = collection.Node.one({"_id":ObjectId(node_id)})
    for each in node.relation_type_set:
        coll_obj_list.append(each)
    drawer1 = list(set(st) - set(coll_obj_list))
    drawer2 = coll_obj_list
    for each in drawer1:
       dic = {}
       dic['id'] = str(each._id)
       dic['name'] = str(each.name)
       d1.append(dic)
    draw1['drawer1'] = d1
    data_list.append(draw1)
    for each in drawer2:
       dic = {}
       dic['id'] = str(each._id)
       dic['name'] = str(each.name)
       d2.append(dic)
    draw2['drawer2'] = d2
    data_list.append(draw2)
    return HttpResponse(json.dumps(data_list))

@login_required
def deletion_instances(request, group_id):
    '''delete class's objects'''
    send_dict = []
    if request.is_ajax() and request.method =="POST":
       deleteobjects = request.POST['deleteobjects']
       confirm = request.POST.get("confirm","")
    for each in  deleteobjects.split(","):
        delete_list = []
        node = collection.Node.one({ '_id': ObjectId(each)})
        left_relations = collection.Node.find({"_type":"GRelation", "subject":node._id})
        right_relations = collection.Node.find({"_type":"GRelation", "right_subject":node._id})
        attributes = collection.Node.find({"_type":"GAttribute", "subject":node._id})
        if confirm:
            all_associates = list(left_relations)+list(right_relations)+list(attributes)
            for eachobject in all_associates:
                eachobject.delete()
            node.delete()
        else:
            if left_relations :
                list_rel = []
                for each in left_relations:
                    rname = collection.Node.find_one({"_id":each.right_subject}).name
                    list_rel.append(each.relation_type.name+" : "+rname)
                delete_list.append({'left_relations':list_rel})
            if right_relations :
                list_rel = []
                for each in right_relations:
                    lname = collection.Node.find_one({"_id":each.subject}).name
                    list_rel.append(each.relation_type.name+" : "+lname)
                delete_list.append({'right_relations':list_rel})
            if attributes :
                list_att = []
                for each in attributes:
                    list_att.append(each.attribute_type.name+" : "+each.object_value)
                delete_list.append({'attributes':list_att})
            send_dict.append({"title":node.name,"content":delete_list})
    if confirm:
        return StreamingHttpResponse(str(len(deleteobjects.split(",")))+" objects deleted")         
    return StreamingHttpResponse(json.dumps(send_dict).encode('utf-8'),content_type="text/json", status=200)

def get_visited_location(request, group_id):

  usrid = request.user.id
  visited_location = ""

  if(usrid):

    usrid = int(request.user.id)
    usrname = unicode(request.user.username)
        
    author = collection.Node.one({'_type': "GSystemType", 'name': "Author"})
    user_group_location = collection.Node.one({'_type': "Author", 'member_of': author._id, 'created_by': usrid, 'name': usrname})
    
    if user_group_location:
      visited_location = user_group_location.visited_location
  
  return StreamingHttpResponse(json.dumps(visited_location))

@login_required
def get_online_editing_user(request, group_id):
    '''
    get user who is currently online and editing the node
    '''
    if request.is_ajax() and request.method =="POST":
        editorid = request.POST.get('editorid',"")
    viewobj = ViewObj.objects.filter(filename=editorid)
    userslist = []
    if viewobj:
        for each in viewobj:
            if not each.username == request.user.username:
                blankdict = {}
                blankdict['username']=each.username
                get_profile =  get_profile_pic(each.username)
                if get_profile :
                    blankdict['pro_img'] = "/"+str(group_id)+"/image/thumbnail/"+str(get_profile._id)
                else :
                    blankdict['pro_img'] = "no";
                userslist.append(blankdict)
        if len(userslist) == 0:
            userslist.append("No users")
    else :
        userslist.append("No users")

    return StreamingHttpResponse(json.dumps(userslist).encode('utf-8'),content_type="text/json")
def view_articles(request, group_id):
  if request.is_ajax():
    # extracting all the bibtex entries from database
    GST_one=collection.Node.one({'_type':'AttributeType','name':'Citation'})
    list_item=['article','book','booklet','conference','inbook','incollection','inproceedings','manual','masterthesis','misc','phdthesis','proceedings','techreport','unpublished_entry']
    response_dict=[]

    for each in list_item:
      dict2={}
      ref=collection.Node.one({'_type':'GSystemType','name':each})
  
      ref_entry=collection.GSystem.find({'member_of':{'$all':[ref._id]},'group_set':{'$all':[ObjectId(group_id)]},'status':u'PUBLISHED'})
      
      list_entry=[]
      for every in ref_entry:
        
        id=every._id
        gst_attribute=collection.Node.one({'subject':ObjectId(every._id),'attribute_type.$id':ObjectId(GST_one._id)})
        cite=gst_attribute.object_value
        dict1 = {'name': every.name,'cite':cite}
        list_entry.append(dict1)
      dict2[each]=list_entry
      response_dict.append(dict2)
  return StreamingHttpResponse(json.dumps(response_dict))      

def get_author_set_users(request, group_id):
    '''
    This ajax function will give all users present in node's author_set field
    '''
    user_list = []
    can_remove = False

    if request.is_ajax():
        _id = request.GET.get('_id',"")
        node = collection.Node.one({'_id':ObjectId(_id)})
        course_name = ""
        rt_has_course = collection.Node.one({'_type':'RelationType', 'name':'has_course'})
        if rt_has_course and node._id:
            course = collection.Triple.one({'relation_type.$id':rt_has_course._id,'right_subject':node._id})
            if course:
                course_name = collection.Node.one({'_id':ObjectId(course.subject)}).name
        if node.created_by == request.user.id:
            can_remove = True
        if node.author_set:
            for each in node.author_set:
                user_list.append(User.objects.get(id = each))
            return render_to_response("ndf/refresh_subscribed_users.html", 
                                       {"user_list":user_list,'can_remove':can_remove,'node_id':node._id,'course_name':course_name}, 
                                       context_instance=RequestContext(request)
            )
        else:
            return StreamingHttpResponse("Empty")
    else:
        return StreamingHttpResponse("Invalid ajax call")

@login_required
def remove_user_from_author_set(request, group_id):
    '''
    This ajax function remove the user from athor_set
    '''
    user_list = []
    can_remove = False
    if request.is_ajax():
        _id = request.GET.get('_id',"")
        user_id = int(request.GET.get('user_id',""))
        node = collection.Node.one({'_id':ObjectId(_id)})
        if node.created_by == request.user.id:
            node.author_set.remove(user_id)
            can_remove = True
            node.save()
            print node.author_set,"TEst author"
            if node.author_set:
                for each in node.author_set:
                    user_list.append(User.objects.get(id = each))
            return render_to_response("ndf/refresh_subscribed_users.html", 
                                      {"user_list":user_list,'can_remove':can_remove,'node_id':node._id}, 
                                      context_instance=RequestContext(request)
            )
        else:
            return StreamingHttpResponse("You are not authorised to remove user")
    else:
        return StreamingHttpResponse("Invalid Ajax call")
    
def get_filterd_user_list(request, group_id):
    '''
    This function will return (all user's) - (subscribed user for perticular group) 
    '''
    user_list = []
    if request.is_ajax():
        _id = request.GET.get('_id',"")
        node = collection.Node.one({'_id':ObjectId(_id)})
        all_users_list =  [each.username for each in User.objects.all()]
        if node._type == 'Group':
            for each in node.author_set:
                user_list.append(User.objects.get(id = each).username)
        print all_users_list,set(user_list)
        filtered_users = list(set(all_users_list) - set(user_list))
        return HttpResponse(json.dumps(filtered_users))

def search_tasks(request, group_id):
    '''
    This function will return (all task's) 
    '''
    user_list = []
    app_id = collection.Node.find_one({'_type':"GSystemType", "name":"Task"})
    if request.is_ajax():
        term = request.GET.get('term',"")
        task_nodes = collection.Node.find({
                                          'member_of': {'$all': [app_id._id]},
					  'name': {'$regex': term, '$options': 'i'}, 
                                          'group_set': {'$all': [ObjectId(group_id)]},
                                          'status': {'$nin': ['HIDDEN']}
                                      }).sort('last_update', -1)
	for each in task_nodes :
		user_list.append({"label":each.name,"value":each.name,"id":str(each._id)})	
        return HttpResponse(json.dumps(user_list))
    else:
	raise Http404

def get_group_member_user(request, group_id):
    '''
    This function will return (all task's) 
    '''
    user_list = []
    group = collection.Node.find_one({'_id':ObjectId(group_id)})
    if request.is_ajax():
        if group.author_set:
            for each in group.author_set:
                user_list.append(User.objects.get(id = each).username)
        return HttpResponse(json.dumps(user_list))
    else:
	raise Http404


def annotationlibInSelText(request, group_id):
  """
  This view parses the annotations field of the currently selected node_id and evaluates if entry corresponding this selectedText already exists.
  If it does, it appends the comment to this entry else creates a new one.   

  Arguments:
  group_id - ObjectId of the currently selected group
  obj_id - ObjectId of the currently selected node_id
  comment - The comment added by user
  selectedText - text for which comment was added

 Returns:
  The updated annoatations field
  """
  
  obj_id = str(request.POST["node_id"])
  col = get_database()[Node.collection_name]
  sg_obj = col.Node.one({"_id":ObjectId(obj_id)})
  
  comment = request.POST ["comment"]
  comment = json.loads(comment)
  comment_modified = {
                        'authorAvatarUrl' : comment['authorAvatarUrl'],
                        'authorName'      : comment['authorName'],
                        'comment'         : comment['comment']
  }
  selectedText = request.POST['selectedText']
    
  # check if annotations for this text already exist!
  flag = False
  
  for entry in sg_obj.annotations:
    if (entry['selectedText'].lower() == selectedText.lower()):
      entry['comments'].append(comment_modified)
      flag = True
      break

  if(not(flag)):
    comment_list = []
    comment_list.append(comment_modified)
    ann = {
          'selectedText' : selectedText,
          'sectionId'    : str(comment['sectionId']),
          'comments'     : comment_list
    }
    sg_obj.annotations.append(ann)
  
  sg_obj.save()

  return HttpResponse(json.dumps(sg_obj.annotations))

def delComment(request, group_id):
  '''
  Delete comment from thread
  '''
  print "Inside del comments"
  return HttpResponse("comment deleted")

# Views related to STUDIO.TISS =======================================================================================

def set_user_link(request, group_id):
  """
  This view creates a relationship (has_login) between the given node (node_id) and the author node (username);
  and also subscribes the user to his/her respective college group

  Arguments:
  group_id - ObjectId of the currently selected group
  node_id - ObjectId of the currently selected node_id
  username - Username of the user

  Returns:
  A dictionary consisting of following key:-
  result - a bool variable indicating whether link is created or not and subscribed to group or not
  message - a string variable giving the status of the link (also reason if any error occurs)
  """
  gr_node = None

  try:
    if request.is_ajax() and request.method =="POST":
      node_id = request.POST.get("node_id", "")
      username = request.POST.get("username", "")

      # Creating link between user-node and it's login credentials
      author = collection.Node.one({'_type': "Author", 'name': unicode(username)}, {'created_by': 1})
      rt_has_login = collection.Node.one({'_type': "RelationType", 'name': u"has_login"})

      gr_node = create_grelation(node_id, rt_has_login, author._id)

      if gr_node:
        # Assigning the userid to respective private college groups's author_set,
        # i.e. making user, member of college group to which he/she belongs
        # Only after the given user's link (i.e., has_login relation) gets created
        node = collection.Node.one({'_id': ObjectId(node_id)}, {'member_of': 1})
        node_type = node.member_of_names_list

        has_group = collection.Node.one({'_type': "RelationType", 'name': "has_group"}, {'_id': 1})

        if "Student" in node_type:
          student_belonds_to_college = collection.Node.one({'_type': "RelationType", 'name': "student_belongs_to_college"}, {'_id': 1})

          colleges = collection.Node.find({'_type': "GRelation", 'subject': node._id, 'relation_type.$id': student_belonds_to_college._id})

          for each in colleges:
            g = collection.Node.one({'_type': "GRelation", 'subject': each.right_subject, 'relation_type.$id': has_group._id})
            collection.update({'_id': g.right_subject}, {'$addToSet': {'author_set': author.created_by}}, upsert=False, multi=False)

        elif "Voluntary Teacher" in node_type:
          trainer_of_college = collection.Node.one({'_type': "RelationType", 'name': "trainer_of_college"}, {'_id': 1})

          colleges = collection.Node.find({'_type': "GRelation", 'subject': node._id, 'relation_type.$id': trainer_of_college._id})

          for each in colleges:
            g = collection.Node.one({'_type': "GRelation", 'subject': each.right_subject, 'relation_type.$id': has_group._id})
            collection.update({'_id': g.right_subject}, {'$addToSet': {'author_set': author.created_by}}, upsert=False, multi=False)


      return HttpResponse(json.dumps({'result': True, 'message': " Link successfully created. \n\n Also subscribed to respective college group(s)."}))

    else:
      error_message = " UserLinkSetUpError: Either not an ajax call or not a POST request!!!"
      return HttpResponse(json.dumps({'result': False, 'message': " Link not created - Something went wrong in ajax call !!! \n\n Please contact system administrator."}))

  except Exception as e:
    error_message = "\n UserLinkSetUpError: " + str(e) + "!!!"
    result = False

    if gr_node:
      # collection.remove({'_id': gr_node._id})
      result = True
      error_message = " Link created successfully. \n\n But facing problem(s) in subscribing to respective college group(s)!!!\n Please use group's 'Subscribe members' button to do so !!!"

    else:
      result = False
      error_message = " Link not created - May be invalid username entered !!!"
      
    return HttpResponse(json.dumps({'result': result, 'message': error_message}))

def set_enrollment_code(request, group_id):
  """
  """
  if request.is_ajax() and request.method == "POST":
    print "\n From set_enrollment_code... \n"
    return HttpResponse("Five digit code")

  else:
    error_message = " EnrollementCodeError: Either not an ajax call or not a POST request!!!"
    raise Exception(error_message)

def get_students_assignments(request, group_id):
  """

  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  """
  gr_node = None

  try:
    if request.is_ajax() and request.method =="GET":
      user_id = 0

      if request.GET.has_key("user_id"):
        user_id = int(request.GET.get("user_id", ""))

      # Fetching college group
      college_group = collection.Node.one({'_id': ObjectId(group_id)}, {'name': 1, 'tags': 1, 'author_set': 1, 'created_by': 1})
      page_res = collection.Node.one({'_type': "GSystemType", 'name': "Page"}, {'_id': 1})
      # print "\n page_res: ", page_res._id
      file_res = collection.Node.one({'_type': "GSystemType", 'name': "File"}, {'_id': 1})
      # print " file_res: ", file_res._id
      image_res = collection.Node.one({'_type': "GSystemType", 'name': "Image"}, {'_id': 1})
      # print " image_res: ", image_res._id
      video_res = collection.Node.one({'_type': "GSystemType", 'name': "Video"}, {'_id': 1})
      # print " video_res: ", video_res._id

      student_list = []
      # print " college_group (author_set): ", college_group.author_set, "\n"

      if user_id:
        # Fetch assignment details of a given student
        student_dict = {}
        num_pages = []
        num_images = []
        num_videos = []
        num_files = []

        # Fetch student's user-group
        user_group = collection.Node.one({'_type': "Author", 'created_by': user_id})
        student_dict["username"] = user_group.name

        # Fetch all resources from student's user-group
        resources = collection.Node.find({'group_set': user_group._id}, {'name': 1, 'member_of': 1, 'created_at': 1})

        for res in resources:
          if page_res._id in res.member_of:
            num_pages.append(res)

          elif image_res._id in res.member_of:
            num_images.append(res)

          elif video_res._id in res.member_of:
            num_videos.append(res)

          elif file_res._id in res.member_of:
            num_files.append(res)

        student_dict["Pages"] = num_pages
        # print "\n student_dict['Pages']: ", student_dict["Pages"], "\n"
        student_dict["Images"] = num_images
        # print "\n student_dict['Images']: ", student_dict["Images"], "\n"
        student_dict["Videos"] = num_videos
        # print "\n student_dict['Videos']: ", student_dict["Videos"], "\n"
        student_dict["Files"] = num_files
        # print "\n student_dict['Files']: ", student_dict["Files"], "\n"

        return HttpResponse(json.dumps(student_dict, cls=NodeJSONEncoder))

      else:
        # Fetch assignment details of all students belonging to the college group
        for user_id in college_group.author_set:
          if user_id == college_group.created_by:
            continue

          student_dict = {}
          num_pages = 0
          num_images = 0
          num_videos = 0
          num_files = 0

          # Fetch student's user-group
          user_group = collection.Node.one({'_type': "Author", 'created_by': user_id})

          # Fetch student's node from his/her has_login relationship
          student_has_login_rel = collection.Node.one({'_type': "GRelation", 'right_subject': user_group._id})
          student_node = collection.Node.one({'_id': student_has_login_rel.subject}, {'name': 1})
          # print " student_node: ", student_node.name
          student_dict["Name"] = student_node.name
          student_dict["user_id"] = user_id

          # Fetch all resources from student's user-group
          resources = collection.Node.find({'group_set': user_group._id}, {'member_of': 1})

          for res in resources:
            if page_res._id in res.member_of:
              num_pages = num_pages + 1

            elif image_res._id in res.member_of:
              num_images = num_images + 1

            elif video_res._id in res.member_of:
              num_videos = num_videos + 1

            elif file_res._id in res.member_of:
              num_files = num_files + 1

          student_dict["Pages"] = num_pages
          student_dict["Images"] = num_images
          student_dict["Videos"] = num_videos
          student_dict["Files"] = num_files
          student_dict["Total"] = num_pages + num_images + num_videos + num_files

          # print "\n student_dict: ", student_dict
          student_list.append(student_dict)

        # Outside of above for loop

        return render_to_response("ndf/student_statistics.html",
                                  {'node': college_group,'student_list': student_list},
                                  context_instance = RequestContext(request)
                                )
    
    else:
      error_message = "StudentDataGetError: Invalid ajax call!!!"
      # raise Exception(error_message)
      return StreamingHttpResponse(error_message)

  except Exception as e:
    print "\n StudentDataGetError: " + str(e)
    raise Http404(e)

def get_districts(request, group_id):
  """
  This view fetches district(s) belonging to given state.

  Arguments:
  group_id - ObjectId of the currently selected group
  state_id - ObjectId of the currently selected state`

  Returns:
  A dictionary consisting of following key:-
  districts - a list variable consisting of two elements i.e., 
              first-element: subject (District's ObjectId), second-element: manipulated-name-value (District's name)
  message - a string variable giving the error-message
  """
  gr_node = None

  try:
    if request.is_ajax() and request.method == "GET":
      state_id = request.GET.get("state_id", "")

      # districts -- [first-element: subject (District's ObjectId), second-element: manipulated-name-value (District's name)]
      districts = []

      # Fetching RelationType: District - district_of (name) | has_district (inverse_name) - State
      rt_district_of = collection.Node.one({'_type': "RelationType", 'name': "district_of"})

      # Fetching all districts belonging to given state in sorted order by name
      if rt_district_of:
        cur_districts = collection.Triple.find({'_type': "GRelation", 
                                                'relation_type.$id': rt_district_of._id, 
                                                'right_subject': ObjectId(state_id)
                                              }).sort('name', 1)

        if cur_districts.count():
          for d in cur_districts:
            districts.append([str(d.subject), d.name.split(" -- ")[0]])

        else:
          error_message = "No districts found"
          raise Exception(error_message)

      else:
        error_message = "RelationType (district_of) doesn't exists"
        raise Exception(error_message)
      
      return HttpResponse(json.dumps(districts))

    else:
      error_message = " DistrictFetchError: Either not an ajax call or not a GET request!!!"
      return HttpResponse(json.dumps({'message': " DistrictFetchError - Something went wrong in ajax call !!! \n\n Please contact system administrator."}))

  except Exception as e:
    error_message = "\n DistrictFetchError: " + str(e) + "!!!"
    return HttpResponse(json.dumps({'message': error_message}))

# ====================================================================================================

def edit_task_title(request, group_id):
    '''
    This function will edit task's title 
    '''
    if request.is_ajax() and request.method =="POST":
        taskid = request.POST.get('taskid',"")
        title = request.POST.get('title',"")
	task = collection.Node.find_one({'_id':ObjectId(taskid)})
        task.name = title
	task.save()
        return HttpResponse(task.name)
    else:
	raise Http404

def edit_task_content(request, group_id):
    '''
    This function will edit task's title 
    '''
    if request.is_ajax() and request.method =="POST":
        taskid = request.POST.get('taskid',"")
        content_org = request.POST.get('content_org',"")
	task = collection.Node.find_one({'_id':ObjectId(taskid)})
        task.content_org = unicode(content_org)
    
  	# Required to link temporary files with the current user who is modifying this document
    	usrname = request.user.username
    	filename = slugify(task.name) + "-" + usrname + "-"
    	task.content = org2html(content_org, file_prefix=filename)
	task.save()
        return HttpResponse(task.content)
    else:
	raise Http404

# =============================================================================

def get_announced_courses(request, group_id):
  """
  This view returns list of announced-course(s) that match given criteria
  along with NUSSD-Course(s) for which match doesn't exists.

  Arguments:
  group_id - ObjectId of the currently selected group
  start_time - Basestring representing start-time (format: MM/YYYY)
  end_time - Basestring representing end-time (format: MM/YYYY)
  nussd_course_type - Type of NUSSD course

  Returns:
  A dictionary consisting of following key-value pairs:-
  success - Boolean giving the state of ajax call
  message - Basestring giving the error/information message
  unset_nc - dictionary consisting of announced-course(s) [if match found] and/or 
             NUSSD-Courses [if match not found]
  """
  response_dict = {'success': False, 'message': ""}

  try:
    if request.is_ajax() and request.method == "GET":
      # Fetch field(s) from GET object
      start_time = request.GET.get("start_time", "")
      end_time = request.GET.get("end_time", "")
      nussd_course_type = request.GET.get("nussd_course_type", "")

      # Check whether any field has missing value or not
      if start_time == "" or end_time == "" or nussd_course_type == "":
        error_message = "Invalid data: No data found in any of the field(s)!!!"
        raise Exception(error_message)

      # Fetch "Announced Course" GSystemType
      announced_course_gt = collection.Node.one({'_type': "GSystemType", 'name': "Announced Course"})
      if not announced_course_gt:
        # If not found, throw exception
        error_message = "'Announced Course' (GSystemType) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Type-cast fetched field(s) into their appropriate type
      start_time = datetime.datetime.strptime(start_time, "%m/%Y")
      end_time = datetime.datetime.strptime(end_time, "%m/%Y")
      nussd_course_type = unicode(nussd_course_type)

      # Fetch registered NUSSD-Courses of given type
      # For that first fetch GAttribute(s) whose having value of 'object_type' field
      # as given type (nussd_course_type)
      # From that you will get NUSSD-Courses (ObjectId) via 'subject' field
      # And for name, you need to extract from GAttributes 'name' field
      nc_cur = collection.Triple.find({'_type': "GAttribute", 'object_value': nussd_course_type})

      # This below dict holds
      # > key as ObjectId (string representation) of the given NUSSD course
      #   >> String representation because it's going to be used in json.dumps() & it
      #      requires keys to be in string format only
      # > value as name of the given NUSSD course
      nc_dict = {}

      if nc_cur.count():
        # If found, append them to a dict
        for each in nc_cur:
          if each.name.split(" -- ")[1] == "nussd_course_type":
            nc_dict[str(each.subject)] = each.name.split(" -- ")[0]
  
      else:
        # Otherwise, throw exception
        error_message = "No such ("+nussd_course_type+") type of course(s) exists... register them first"
        raise Exception(error_message)

      # Search for already created announced-courses with given criteria
      ac_cur = collection.Node.find({'member_of': announced_course_gt._id,
                                    '$and': [
                                      {'name': {'$regex': str(start_time), '$options': "i"}},
                                      # {'name': {'$regex': str(end_time), '$options': "i"}},
                                      {'name': {'$regex': str(nussd_course_type), '$options': "i"}}
                                    ]
                                    })

      if ac_cur.count():
        # Iterate already existing announced-course(s)' instances
        # > Iterate registered NUSSD-courses 
        #   >> If match found between both of them
        #   >> Then
        #      >>> delete registered NUSSD-course entry from dict
        #      >>> Add already existing Announced-course entry in it
        #      >>> break inner for-loop, continue with next announced-course value
        for each in ac_cur:
          for k, v in nc_dict.iteritems():
            if v in each.name:
              del nc_dict[k]
              nc_dict[str(each._id)] = each.name
              break

        response_dict["success"] = True
        response_dict["message"] = "NOTE: Some announced-course(s) found which match given criteria."
        response_dict["unset_nc"] = nc_dict

      else:
        response_dict["success"] = True
        response_dict["message"] = "NOTE: No match found of announced-course instance(s) with given criteria."
        response_dict["unset_nc"] = nc_dict

      return HttpResponse(json.dumps(response_dict))

    else:
      error_message = "AnnouncedCourseError: Either not an ajax call or not a GET request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "AnnouncedCourseError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

def get_anncourses_allstudents(request, group_id):
  """
  This view returns ...

  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  A dictionary consisting of following key-value pairs:-
  success - Boolean giving the state of ajax call
  message - Basestring giving the error/information message
  """
  response_dict = {'success': False, 'message': ""}
  all_students_text = ""

  try:
    if request.is_ajax() and request.method == "GET":
      # Fetch field(s) from GET object
      nussd_course_type = request.GET.get("nussd_course_type", "")
      registration_year = request.GET.get("registration_year", "")
      degree_year = request.GET.get("degree_year", "")
      college = request.GET.get("college", "")
      all_students = request.GET.get("all_students", "")

      # Check whether any field has missing value or not
      if nussd_course_type == "" or registration_year == "" or degree_year == "" or all_students == "":
        error_message = "Invalid data: No data found in any of the field(s)!!!"
        raise Exception(error_message)

      # Fetch "Announced Course" GSystemType
      announced_course_gt = collection.Node.one({'_type': "GSystemType", 'name': "Announced Course"}, {'name': 1})
      if not announced_course_gt:
        # If not found, throw exception
        error_message = "'Announced Course' (GSystemType) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Fetch "start_time" AttributeType
      start_time_AT = collection.Node.one({'_type': "AttributeType", 'name': "start_time"}, {'_id': 1})
      if not start_time_AT:
        # If not found, throw exception
        error_message = "'start_time' (AttributeType) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Fetch "has_group" RelationType
      has_group_RT = collection.Node.one({'_type': "RelationType", 'name': "has_group"}, {'_id': 1})
      if not has_group_RT:
        # If not found, throw exception
        error_message = "'has_group' (RelationType) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Type-cast fetched field(s) into their appropriate type
      nussd_course_type = unicode(nussd_course_type)
      # registration_year = datetime.datetime.strptime(registration_year, "%Y")
      degree_year = unicode(degree_year)
      college_group = collection.Triple.one({'_type': "GRelation", 'subject': ObjectId(college), 'relation_type.$id': has_group_RT._id})

      # Based on registration_year, fetch corresponding Announced Course(s)
      ac_cur = collection.Node.find({'_type': "GSystem", 
                                      'member_of': announced_course_gt._id, 
                                      '$and': [
                                        {'name': {'$regex': str(nussd_course_type), '$options': "i"}},
                                        {'name': {'$regex': registration_year, '$options': "i"}}
                                      ]
                                    })
      if not ac_cur.count():
        # If no documents found, throw exception
        error_message = "'Announced Course' of given type ("+nussd_course_type+") doesn't exists for given year ("+registration_year+")... Please create it first"
        raise Exception(error_message)

      # As there is no proper mechanism to search on datetime object in mongodb
      # Preparing greater than equal to and less than equal to values
      date_lte = datetime.datetime.strptime("31/12/"+registration_year, "%d/%m/%Y")
      date_gte = datetime.datetime.strptime("1/1/"+registration_year, "%d/%m/%Y")
      ac_list = []
      for each in ac_cur:
        # For found Announced Courses
        # Finding start_time which falls between above date range 
        each_st = collection.Triple.one({'_type': "GAttribute", 'subject': each._id, 
                                      'attribute_type.$id': start_time_AT._id,
                                      'object_value': {'$gte': date_gte, '$lte': date_lte}
                                    })
        if each_st:
          # If match found, append that Announced Course into a list
          val = [str(each._id), each.name]
          if val not in ac_list:
            ac_list.append(val)

      # Sort list based on Announced Course's name field
      # which is 2nd element in each entry
      ac_list.sort(key=itemgetter(1))

      if all_students == u"true":
        all_students_text = "All students (including enrolled ones)"

      elif all_students == u"false":
        all_students_text = "Only non-enrolled students"

      response_dict["announced_courses"] = ac_list

      response_dict["success"] = True
      response_dict["message"] = "NOTE: " + all_students_text + " are listed along with announced courses ("+nussd_course_type+")"

      return HttpResponse(json.dumps(response_dict))

    else:
      error_message = "EnrollInCourseError: Either not an ajax call or not a GET request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "EnrollInCourseError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

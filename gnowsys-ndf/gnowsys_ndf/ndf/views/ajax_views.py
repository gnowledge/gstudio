''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json  
import datetime
from operator import itemgetter
import csv
import time
import ast


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.http import Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User

from django_mongokit import get_database

from mongokit import paginator

from stemming.porter2 import stem

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.settings import STATIC_ROOT, STATIC_URL
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.file import * 
from gnowsys_ndf.ndf.views.methods import check_existing_group, get_drawers, get_node_common_fields, get_node_metadata, create_grelation
from gnowsys_ndf.ndf.views.methods import get_widget_built_up_data, parse_template_data
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_profile_pic
from gnowsys_ndf.ndf.templatetags.ndf_tags import edit_drawer_widget

from gnowsys_ndf.mobwrite.models import ViewObj

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


def terms_list(request, group_id):
  
    if request.is_ajax() and request.method == "POST":
      # page number which have clicked on pagination
      page_no = request.POST.get("page_no", '')
      terms = []
      gapp_GST = collection.Node.one({'_type':'MetaType', 'name':'GAPP' })
      term_GST = collection.Node.one({'_type': 'GSystemType', 'name':'Term', 'member_of':ObjectId(gapp_GST._id) })

      # To list all term instances
      terms_list = collection.Node.find({'_type':'GSystem','member_of': ObjectId(term_GST._id),
                                         'group_set': ObjectId(group_id) 
                                        }).sort('name', 1)

      paged_terms = paginator.Paginator(terms_list, page_no, 25) 
      
      # Since "paged_terms" returns dict ,we append the dict items in a list to forwarded into template
      for each in paged_terms.items:
        terms.append(each)

         
      return render_to_response('ndf/terms_list.html', 
                            {'group_id': group_id,'groupid': group_id,"paged_terms": terms, 
                             'page_info': paged_terms
                            },context_instance = RequestContext(request)
      )


            
# This ajax view renders the output as "node view" by clicking on collections
def collection_nav(request, group_id):
    imageCollection=""
    if request.is_ajax() and request.method == "POST":    
      node_id = request.POST.get("node_id", '')
      
      # collection = db[Node.collection_name]
      # imageCollection = collection.Node.find({'member_of': {'$all': [ObjectId(GST_IMAGE._id)]}, 
      #                                         '_type': 'File', 
      #                                         '$or': [
      #                                             {'$or': [
      #                                               {'access_policy': u"PUBLIC"},
      #                                                 {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
      #                                               ]
      #                                             }
      #                                           ,
      #                                           {'$and': [
      #                                             {'$or': [
      #                                               {'access_policy': u"PUBLIC"},
      #                                               {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
      #                                               ]
      #                                             }
      #                                             ]
      #                                           }
      #                                         ],
      #                                         'group_set': {'$all': [ObjectId(group_id)]}
      #                                       }).sort("last_update", -1)


      node_obj = collection.Node.one({'_id': ObjectId(node_id)})

      node_obj.get_neighbourhood(node_obj.member_of)

      return render_to_response('ndf/node_ajax_view.html', 
                                  { 'node': node_obj,
                                    'group_id': group_id,
                                    'groupid':group_id
                                    # 'imageCollection':imageCollection
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
    
    drawer = None
    drawers = None
    drawer1 = None
    drawer2 = None
    dict_drawer = {}
    dict1 = {}
    dict2 = []
    nlist=[]
    node = None
    
    node_id = request.POST.get("node_id", '')
    field = request.POST.get("field", '')
    app = request.POST.get("app", '')
    page_no = request.POST.get("page_no", '')

    if node_id:
      node = collection.Node.one({'_id': ObjectId(node_id) })
      if field == "prior_node":
        app = None
        nlist = node.prior_node	       
        drawer, paged_resources = get_drawers(group_id, node._id, nlist, page_no, app)

      elif field == "teaches":
        app = None
        relationtype = collection.Node.one({"_type":"RelationType","name":"teaches"})
        list_grelations = collection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
        for relation in list_grelations:
          nlist.append(ObjectId(relation.right_subject))

        drawer, paged_resources = get_drawers(group_id, node._id, nlist, page_no, app)

      elif field == "assesses":
        app = field
        relationtype = collection.Node.one({"_type":"RelationType","name":"assesses"})
        list_grelations = collection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
        for relation in list_grelations:
          nlist.append(ObjectId(relation.right_subject))

        drawer, paged_resources = get_drawers(group_id, node._id, nlist, page_no, app)

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

        nlist = node.collection_set
        drawer, paged_resources = get_drawers(group_id, node._id, nlist, page_no, app)
        

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

      nlist = []
      drawer, paged_resources = get_drawers(group_id, None, nlist, page_no, app)

    drawers = drawer
    if not node_id:
      drawer1 = drawers

    else:
      drawer1 = drawers['1']
      drawer2 = drawers['2']

    return render_to_response('ndf/drawer_widget.html', 
                              { 'widget_for': field,'drawer1': drawer1, 'drawer2': drawer2,'node_id': node_id,
                                'group_id': group_id,'groupid': group_id,"page_info": paged_resources
                              },
                              context_instance = RequestContext(request)
    )



def select_drawer(request, group_id):
    
    if request.is_ajax() and request.method == "POST":

        drawer = None
        drawers = None
        drawer1 = None
        drawer2 = None
        node = None
        dict_drawer = {}
        dict1 = {}
        dict2 = []
        nlist=[]
        check = ""
        checked = ""
        relationtype = "" 

        selected_collection_list = request.POST.get("collection_list", '')
        node_id = request.POST.get("node_id", '')
        page_no = request.POST.get("page_no", '')
        selection_save = request.POST.get("selection_save", '')
        field = request.POST.get("field", '')
        checked = request.POST.get("homo_collection", '')

        if checked:
          if checked == "QuizObj" :
            quiz = collection.Node.one({'_type': 'GSystemType', 'name': "Quiz" })
            quizitem = collection.Node.one({'_type': 'GSystemType', 'name': "QuizItem" })

          elif checked == "Pandora Video":
            check = collection.Node.one({'_type': 'GSystemType', 'name': 'Pandora_video' })

          else:
            check = collection.Node.one({'_type': 'GSystemType', 'name': unicode(checked) })

        

        if node_id:
            node_id = ObjectId(node_id)
            node = collection.Node.one({'_id': ObjectId(node_id) })            
            if selected_collection_list:
              selected_collection_list = [ObjectId(each.strip()) for each in selected_collection_list.split(",")]

            if field:
              if field == "teaches":
                relationtype = collection.Node.one({"_type":"RelationType","name":"teaches"})
                list_grelations = collection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
                for relation in list_grelations:
                  nlist.append(ObjectId(relation.right_subject))
              elif field == "assesses":
                relationtype = collection.Node.one({"_type":"RelationType","name":"assesses"})
                list_grelations = collection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
                for relation in list_grelations:
                  nlist.append(ObjectId(relation.right_subject))
              elif field == "prior_node":
                nlist = node.prior_node
              elif field == "collection":
                nlist = node.collection_set


        else:
            node_id = None


        if selection_save:
          if field == "collection":
            if set(nlist) != set(selected_collection_list):              
              for each in selected_collection_list:
                if each not in nlist:
                  collection.update({'_id': node._id}, {'$push': {'collection_set': ObjectId(each) }}, upsert=False, multi=False)
            
          elif field == "prior_node":    
            if set(nlist) != set(selected_collection_list):            
              for each in selected_collection_list:
                if each not in nlist:
                  collection.update({'_id': node._id}, {'$push': {'prior_node': ObjectId(each) }}, upsert=False, multi=False)

          elif field == "teaches" or "assesses":
            if set(nlist) != set(selected_collection_list):
              create_grelation(node._id,relationtype,selected_collection_list)

          node.reload()


        if node_id:
          if selected_collection_list:
            if field == "collection":
              if set(nlist) != set(selected_collection_list):  
                return HttpResponse("Warning");
            elif field == "prior_node":
              if set(nlist) != set(selected_collection_list):            
                return HttpResponse("Warning");
            elif field == "teaches" or "assesses":
              if set(nlist) != set(selected_collection_list):
                return HttpResponse("Warning");

        
          if node.collection_set:
            if checked:              
              for k in node.collection_set:
                obj = collection.Node.one({'_id': ObjectId(k) })
                if check:
                  if check._id in obj.member_of:
                    nlist.append(k)
                else:
                  if quiz._id in obj.member_of or quizitem._id in obj.member_of:
                    nlist.append(k)

            else:
              nlist = node.collection_set
              if field == "assesses":
                checked = field
              checked = None

        drawer, paged_resources = get_drawers(group_id, node_id, nlist, page_no, checked)#get_drawers(group_id, node_id, nlist, checked)

        drawers = drawer
        if not node_id:
          drawer1 = drawers

        else:
          drawer1 = drawers['1']
          drawer2 = drawers['2']

        if not field:
          field = "collection"

        return render_to_response("ndf/drawer_widget.html", 
                                  {"widget_for": field, "page_info": paged_resources,
                                   "drawer1": drawer1, 'selection': True, 'node_id':node_id,
                                   "drawer2": drawer2, 
                                   "groupid": group_id
                                  },
                                  context_instance=RequestContext(request)
        )
         
  

def search_drawer(request, group_id):
    
    if request.is_ajax() and request.method == "POST":

      search_name = request.POST.get("search_name", '')
      node_id = request.POST.get("node_id", '')
      selection = request.POST.get("selection", '')
      field = request.POST.get("field", '')

      search_drawer = None
      drawers = None
      drawer1 = None
      drawer2 = None
      dict_drawer = {}
      dict1 = {}
      dict2 = []
      nlist=[]
      node = None
      page_no = 1

      theme_GST_id = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
      topic_GST_id = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})    
      theme_item_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'theme_item'})
      forum_GST_id = collection.Node.one({'_type': 'GSystemType', 'name': 'Forum'}, {'_id':1})
      reply_GST_id = collection.Node.one({'_type': 'GSystemType', 'name': 'Reply'}, {'_id':1})

      if node_id:
        node = collection.Node.one({'_id': ObjectId(node_id) })
        node_type = collection.Node.one({'_id': ObjectId(node.member_of[0]) })
        diff_types = [theme_GST_id ,topic_GST_id, theme_item_GST, forum_GST_id, reply_GST_id]

        if field: 
          if field == "teaches":
            relationtype = collection.Node.one({"_type":"RelationType","name":"teaches"})
            list_grelations = collection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
            for relation in list_grelations:
              nlist.append(ObjectId(relation.right_subject))

          elif field == "assesses":
            relationtype = collection.Node.one({"_type":"RelationType","name":"assesses"})
            list_grelations = collection.Node.find({"_type":"GRelation","subject":node._id,"relation_type":relationtype.get_dbref()})
            for relation in list_grelations:
              nlist.append(ObjectId(relation.right_subject))

          elif field == "prior_node":
            nlist = node.prior_node

          elif field == "collection":
            nlist = node.collection_set

          node.reload()

        if node_type._id in diff_types:
          search_drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]},
                                          'member_of':{'$nin':[theme_GST_id._id,theme_item_GST._id, topic_GST_id._id, reply_GST_id._id, forum_GST_id._id]}, 
                                          '$and': [
                                            {'name': {'$regex': str(search_name), '$options': "i"}},
                                            {'group_set': {'$all': [ObjectId(group_id)]} }
                                          ]
                                        })   
        
        else:
          search_drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 
                                          '$and': [
                                            {'name': {'$regex': str(search_name), '$options': "i"}},
                                            {'group_set': {'$all': [ObjectId(group_id)]} }
                                          ]                                          
                                        })

      else:
          search_drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 
                                          '$and': [
                                            {'name': {'$regex': str(search_name), '$options': "i"}},
                                            {'group_set': {'$all': [ObjectId(group_id)]} }
                                          ]                                          
                                        })      


      if node_id:
        
        for each in search_drawer:
          if each._id != node._id:
            if each._id not in nlist:  
              dict1[each._id] = each
            
        for oid in nlist: 
          obj = collection.Node.one({'_id': oid })           
          dict2.append(obj)            
        
        dict_drawer['1'] = dict1
        dict_drawer['2'] = dict2

      else:
        if (node is None) and (not nlist):
          for each in search_drawer:               
            dict_drawer[each._id] = each



      drawers = dict_drawer
      if not node_id:
        drawer1 = drawers
      else:

        drawer1 = drawers['1']
        drawer2 = drawers['2']
      
      return render_to_response("ndf/drawer_widget.html", 
                                {"widget_for": field, 
                                 "drawer1": drawer1, 'selection': selection,
                                 "drawer2": drawer2, 'search_name': search_name,
                                 "groupid": group_id, 'node_id': node_id
                                },
                                context_instance=RequestContext(request)
      )    
      

####Bellow part is for manipulating theme topic hierarchy####
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

####End of manipulating theme topic hierarchy####

##### bellow part is for manipulating nodes collections#####
def get_inner_collection(collection_list, node):
  inner_list = []
  error_list = []

  if node.collection_set:
    for each in node.collection_set:
      col_obj = collection.Node.one({'_id': ObjectId(each)})
      if col_obj:
        for cl in collection_list:
          if cl['id'] == node.pk:
            node_type = collection.Node.one({'_id': ObjectId(col_obj.member_of[0])}).name
            inner_sub_dict = {'name': col_obj.name, 'id': col_obj.pk,'node_type': node_type}
            inner_sub_list = [inner_sub_dict]
            inner_sub_list = get_inner_collection(inner_sub_list, col_obj)

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


def get_collection(request, group_id, node_id):

  node = collection.Node.one({'_id':ObjectId(node_id)})
  # print "\nnode: ",node.name,"\n"

  collection_list = []

  if node:
    if node.collection_set:
      for each in node.collection_set:
        obj = collection.Node.one({'_id': ObjectId(each) })
        if obj:
          node_type = collection.Node.one({'_id': ObjectId(obj.member_of[0])}).name
          collection_list.append({'name': obj.name, 'id': obj.pk,'node_type': node_type})
          collection_list = get_inner_collection(collection_list, obj)


  data = collection_list
  return HttpResponse(json.dumps(data))

####End of manipulating nodes collection####

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
def get_data_for_event_task(request,group_id):
    #date creation for task type is date month and year
    day_list=[]
    event = collection.Node.one({'_type': "GSystemType", 'name': "Event"})
    obj = collection.Node.find({'type_of': event._id})
    event_count={}
    list31=[1,3,5,7,8,10,12]
    list30=[4,6,9,11]
    #create the date format in unix format for querying it from data 
    #Task attribute_type start time's object value takes the only date 
    #in month/date/year format 
    #As events are quried from the nodes which store the date time in unix format
    
    month=request.GET.get('start','')[5:7]
    year=request.GET.get('start','')[0:4]
    start = datetime.datetime(2014, int(month), 1)
    task_start=str(int(month))+"/"+"01"+"/"+str(int(year))
    
    if int(month) in list31:
     end=datetime.datetime(2014,int(month), 31)
     task_end=str(int(month))+"/"+"31"+"/"+str(int(year))
    elif int(month) in list30:
     end=datetime.datetime(2014,int(month), 30)
     task_end=str(int(month))+"/"+"30"+"/"+str(int(year))
    else:
     end=datetime.datetime(2014,int(month), 28)
     task_end=str(int(month))+"/"+"28"+"/"+str(int(year)) 
    #day_list of events  
    
    for j in obj:
        nodes = collection.Node.find({'member_of': j._id,'attribute_set.start_time':{'$gte':start,'$lt': end}})
        for i in nodes:
          attr_value={}
          event_url="/"+str(group_id)+"/mis/54451151697ee12b7e222076/"+str(j._id) +"/"+str(i._id)
          attr_value.update({'url':event_url})
          attr_value.update({'id':i._id})
          attr_value.update({'title':i.name})
          date=i.attribute_set[0]['start_time']
          formated_date=date.strftime("%Y-%m-%dT%H:%M:%S")
          attr_value.update({'start':formated_date})
          day_list.append(dict(attr_value))

    count=0
    dummylist=[]
    date=""
    sorted_month_list=[]
    changed="false"
    recount=0
    user_assigned=[]
    #day_list of task
    groupname=collection.Node.find_one({"_id":ObjectId(group_id)})
    attributetype_assignee = collection.Node.find_one({"_type":'AttributeType', 'name':'Assignee'})
    attributetype_key1 = collection.Node.find_one({"_type":'AttributeType', 'name':'start_time'})
    attr_assignee = collection.Node.find({"_type":"GAttribute", "attribute_type.$id":attributetype_assignee._id,                                "object_value":request.user.username}).sort('last_update',-1)
    for attr in attr_assignee :
     task_node = collection.Node.one({'_id':attr.subject})
     if task_node:
                  attr1=collection.Node.find_one({"_type":"GAttribute", "subject":task_node._id, "attribute_type.$id":attributetype_key1._id
                  ,'object_value':{'$gte':task_start,'$lte':task_end}
                   })	
                  attr_value={}
                  task_url="/" + groupname.name +"/" + "task"+"/" + str(task_node._id)
                  
                  attr_value.update({'id':task_node._id})
                  attr_value.update({'title':task_node.name})
                  if attr1:
                        date=datetime.datetime(int(attr1.object_value[6:10]),int(attr1.object_value[0:2]),int(attr1.object_value[3:5]))
                        formated_date=date.strftime("%Y-%m-%dT%H:%M:%S")
                        attr_value.update({'start':formated_date})
                  else: 
                        date=task_node.created_at
                        formated_date=date.strftime("%Y-%m-%dT%H:%M:%S")
                        attr_value.update({'start':formated_date})     
                  attr_value.update({'url':task_url})
                  user_assigned.append(attr_value) 
    day_lists=[]
    date=""
    listdate=[]
    #Sorting of events and task's
    #below code is used to replace more than 3 event or task on the particular date 
    #value +3 so instead of all the task and events on the single day it would show 
    #+3 
    for i in user_assigned:
        day_list.append(dict(i))
    day_list.sort(key=lambda item:item['start'])
    
    date_changed=[]
    if request.GET.get('view','') == 'month':
     for i in day_list:
        
        if date == i['start'] or date == "":
           if date_changed:
             dummylist=date_changed
             date_changed=[]  
           dummylist.append(i)
           count=count +  1
           changed="false"
        else:
            changed="true"
            recount=count
            count=0
            count=count +  1
            date_changed=[]
            date_changed.append(i)
            if len(dummylist) > 3:
             attr_value={}
             dummylist=[]
             attr_value.update({'id':i['id']})
             attr_value.update({'title':'+3'})
             attr_value.update({'start':date})
             dummylist.append(dict(attr_value)) 
        date=i['start']    
        if changed == "true" :
              for i in dummylist:
                   sorted_month_list.append(i)
              changed="false"
              dummylist=[]
                   
     final_changed_dates=[]
     if date_changed:
       final_changed_dates=date_changed
     else:
       final_changed_dates=dummylist
       
     dummylist=[]
     date_changed=[]
     if len(final_changed_dates)>3 :
             attr_value={}
             attr_value.update({'id':final_changed_dates[0]['id']})
             attr_value.update({'title':'+3'})
             attr_value.update({'start':final_changed_dates[0]['start']})
             dummylist.append(dict(attr_value))
             final_changed_dates=[]
             final_changed_dates=dummylist 
     for i in final_changed_dates:
           sorted_month_list.append(i)  
     return HttpResponse(json.dumps(sorted_month_list,cls=NodeJSONEncoder))
    else:
     return HttpResponse(json.dumps(day_list,cls=NodeJSONEncoder)) 
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
  """
  Deletes the given node(s) and associated GAttribute(s) & GRelation(s) 
  or provides all information before deleting for confirmation.
  """
  send_dict = []
  if request.is_ajax() and request.method =="POST":
    deleteobjects = request.POST['deleteobjects']
    confirm = request.POST.get("confirm", "")

    for each in  deleteobjects.split(","):
      delete_list = []
      node = collection.Node.one({ '_id': ObjectId(each)})
      left_relations = collection.Node.find({"_type":"GRelation", "subject":node._id})
      right_relations = collection.Node.find({"_type":"GRelation", "right_subject":node._id})
      attributes = collection.Node.find({"_type":"GAttribute", "subject":node._id})

      # When confirm holds "yes" value, all given node(s) is/are deleted.
      # Otherwise, required information is provided for confirmation before deletion.
      if confirm:
        # Deleting GRelations where given node is used as right subject
        for eachobject in right_relations:
          # If given node is used in relationship with any other node (as right_subject)
          # Then this node's ObjectId must be removed from relation_set field of other node
          collection.update({'_id': eachobject.subject, 'relation_set.'+eachobject.relation_type.name: {'$exists': True}}, 
            {'$pull': {'relation_set.$.'+eachobject.relation_type.name: node._id}}, 
            upsert=False, multi=False
          )
          eachobject.delete()

        all_associates = list(left_relations)+list(attributes)
        # Deleting GAttributes and GRelations where given node is used as left subject
        for eachobject in all_associates:
          eachobject.delete()
        
        # Finally deleting given node
        node.delete()
      
      else:
        if left_relations :
          list_rel = []
          for each in left_relations:
            rname = collection.Node.find_one({"_id":each.right_subject})
            if not rname:
              continue
            rname = rname.name
            alt_names = each.relation_type.name
            if each.relation_type.altnames:
              if ";" in each.relation_type.altnames:
                alt_names = each.relation_type.altnames.split(";")[0]
            list_rel.append(alt_names + ": " + rname)

          delete_list.append({'left_relations':list_rel})
        
        if right_relations :
          list_rel = []
          for each in right_relations:
            lname = collection.Node.find_one({"_id":each.subject})
            if not lname:
              continue
            lname = lname.name
            alt_names = each.relation_type.name
            if each.relation_type.altnames:
              if ";" in each.relation_type.altnames:
                alt_names = each.relation_type.altnames.split(";")[1]
            list_rel.append(alt_names + ": " + lname)

          delete_list.append({'right_relations':list_rel})
        
        if attributes :
          list_att = []
          for each in attributes:
            alt_names = each.attribute_type.name
            if each.attribute_type.altnames:
              alt_names = each.attribute_type.altnames
            list_att.append(alt_names + ": " + str(each.object_value))

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
  return HttpResponse("comment deleted")

# Views related to MIS -------------------------------------------------------------

def get_students(request, group_id):
  """
  This view returns list of students along with required data based on selection criteria.

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
    if request.is_ajax() and request.method == "POST":
      groupid = request.POST.get("groupid", None)
      app_id = request.POST.get("app_id", None)
      app_set_id = request.POST.get("app_set_id", None)

      person_gst = collection.Node.one({'_type': "GSystemType", 'name': "Student"}, {'name': 1, 'type_of': 1})

      widget_for = []
      person_gs = collection.GSystem()
      person_gs.member_of.append(person_gst._id)
      person_gs.get_neighbourhood(person_gs.member_of)
      rel_univ = collection.Node.one({'_type': "RelationType", 'name': "student_belongs_to_university"}, {'_id'})
      rel_colg = collection.Node.one({'_type': "RelationType", 'name': "student_belongs_to_college"}, {'_id'})
      attr_deg_yr = collection.Node.one({'_type': "AttributeType", 'name': "degree_year"}, {'_id'})

      widget_for = ["name", 
                    rel_univ._id, 
                    rel_colg._id, 
                    attr_deg_yr._id
                  ]
                  #   'status'
                  # ]
      widget_for = get_widget_built_up_data(widget_for, person_gs)

      # Fetch field(s) from POST object
      query = {}
      university_id = None
      for each in widget_for:
        field_name = each["name"]
  
        if each["_type"] == "BaseField":
          if request.POST.has_key(field_name):
            query_data = request.POST.get(field_name, "")
            query_data = parse_template_data(each["data_type"], query_data)
            if field_name == "name":
              query.update({field_name: {'$regex': query_data, '$options': "i"}})
            else:
              query.update({field_name: query_data})

        elif each["_type"] == "AttributeType":
          if request.POST.has_key(field_name):
            query_data = request.POST.get(field_name, "")
            query_data = parse_template_data(each["data_type"], query_data)
            query.update({"attribute_set."+field_name: query_data})

        elif each["_type"] == "RelationType":
          if request.POST.has_key(field_name):
            query_data = request.POST.get(field_name, "")
            query_data = parse_template_data(each["data_type"], query_data, field_instance=each)
            if field_name == "student_belongs_to_university":
              university_id = query_data
            else:
              query.update({"relation_set."+field_name: query_data})

      student = collection.Node.one({'_type': "GSystemType", 'name': "Student"}, {'_id': 1})
      query["member_of"] = student._id

      date_lte = datetime.datetime.strptime("31/12/2014", "%d/%m/%Y")
      date_gte = datetime.datetime.strptime("1/1/2014", "%d/%m/%Y")
      query["attribute_set.registration_date"] = {'$gte': date_gte, '$lte': date_lte}

      mis_admin = collection.Node.one({'_type': "Group", 'name': "MIS_admin"}, {'_id': 1})

      # Get selected college's groupid, where given college should belongs to MIS_admin group
      college_groupid = collection.Node.one({'_id': query["relation_set.student_belongs_to_college"], 'group_set': mis_admin._id, 'relation_set.has_group': {'$exists': True}}, 
                                            {'relation_set.has_group': 1}
                                          )

      if college_groupid:
        for each in college_groupid.relation_set:
          if "has_group" in each.keys():
            college_groupid = each["has_group"][0]
            break
      else:
        college_groupid = None

      groupid = ObjectId(groupid)
      group_set_to_check = []
      if groupid == college_groupid or groupid == mis_admin._id:
        # It means group is either a college group or MIS_admin group
        # In either case append MIS_admin group's ObjectId
        # and if college_groupid exists, append it's ObjectId too!
        if college_groupid:
          group_set_to_check.append(college_groupid)
        group_set_to_check.append(mis_admin._id)

      else:
        # Otherwise, append given group's ObjectId
        group_set_to_check.append(groupid)

      query.update({'group_set': {'$in': group_set_to_check}})

      rec = collection.aggregate([{'$match': query},
                                  {'$project': {'_id': 0,
                                                'stud_id': '$_id', 
                                                'Name': '$name',
                                                # 'First Name': '$attribute_set.first_name',
                                                # 'Middle Name': '$attribute_set.middle_name',
                                                # 'Last Name': '$attribute_set.last_name',
                                                'Reg# Date': '$attribute_set.registration_date',
                                                'Gender': '$attribute_set.gender',
                                                'Birth Date': '$attribute_set.dob',
                                                'Religion': '$attribute_set.religion',
                                                'Email ID': '$attribute_set.email_id',
                                                'Languages Known': '$attribute_set.languages_known',
                                                'Caste': '$relation_set.student_of_caste_category',
                                                'Contact Number (Mobile)': '$attribute_set.mobile_number',
                                                'Alternate Number / Landline': '$attribute_set.alternate_number',
                                                'House / Street': '$attribute_set.house_street',
                                                'Village': '$attribute_set.village',
                                                'Taluka': '$attribute_set.taluka',
                                                'Town / City': '$attribute_set.town_city',
                                                'District': '$relation_set.person_belongs_to_district',
                                                'State': '$relation_set.person_belongs_to_state',
                                                'Pin Code': '$attribute_set.pin_code',
                                                'Year of Passing 12th Standard': '$attribute_set.12_passing_year',
                                                'Degree Name / Highest Degree': '$attribute_set.degree_name',
                                                'Year of Study': '$attribute_set.degree_year',
                                                'Stream / Degree Specialization': '$attribute_set.degree_specialization',
                                                'College Enrolment Number / Roll No': '$attribute_set.college_enroll_num',
                                                'College ( Graduation )': '$relation_set.student_belongs_to_college',
                                                'Are you registered for NSS?': '$attribute_set.is_nss_registered'
                                  }},
                                  {'$sort': {'Name': 1}}
            ])

      json_data = []
      filename = ""
      column_header = []
      if len(rec["result"]):
        for each_dict in rec["result"]:
          new_dict = {}
          
          for each_key in each_dict:
            if each_dict[each_key]:
              if type(each_dict[each_key]) == list:
                data = each_dict[each_key][0]
              else:
                data = each_dict[each_key]

              if type(data) == list:
                # Perform parsing
                if type(data) == list:
                  # Perform parsing
                  if type(data[0]) in [unicode, basestring, int]:
                    new_dict[each_key] = ', '.join(str(d) for d in data)
                
                  elif type(data[0]) in [ObjectId]:
                    # new_dict[each_key] = str(data)
                    d_list = []
                    for oid in data:
                      d = collection.Node.one({'_id': oid}, {'name': 1})
                      d_list.append(str(d.name))
                    new_dict[each_key] = ', '.join(str(n) for n in d_list)
                
                elif type(data) == datetime.datetime:
                  new_dict[each_key] = data.strftime("%d/%m/%Y")
                
                elif type(data) == long:
                  new_dict[each_key] = str(data)
                
                elif type(data) == bool:
                  if data:
                    new_dict[each_key] = "Yes"
                  else:
                    new_dict[each_key] = "No"
                
                else:
                  new_dict[each_key] = str(data)

              else:
                # Perform parsing
                if type(data) == list:
                  # Perform parsing
                  if type(data[0]) in [unicode, basestring, int]:
                    new_dict[each_key] = ', '.join(str(d) for d in data)
                  elif type(data[0]) in [ObjectId]:
                    new_dict[each_key] = str(data)

                elif type(data) == datetime.datetime:
                  new_dict[each_key] = data.strftime("%d/%m/%Y")

                elif type(data) == long:
                  new_dict[each_key] = str(data)

                elif type(data) == bool:
                  if data:
                    new_dict[each_key] = "Yes"
                  else:
                    new_dict[each_key] = "No"

                else:
                  new_dict[each_key] = str(data)

            else:
              new_dict[each_key] = ""
          
          json_data.append(new_dict)

        # Start: CSV file processing -------------------------------------------
        column_header = [u'Name', u'Reg# Date', u'Gender', u'Birth Date', u'Religion', u'Email ID', u'Languages Known', u'Caste', u'Contact Number (Mobile)', u'Alternate Number / Landline', u'House / Street', u'Village', u'Taluka', u'Town / City', u'District', u'State', u'Pin Code', u'Year of Passing 12th Standard', u'Degree Name / Highest Degree', u'Year of Study', u'Stream / Degree Specialization', u'College Enrolment Number / Roll No', u'College ( Graduation )', u'Are you registered for NSS?']

        t = time.strftime("%c").replace(":", "_").replace(" ", "_")
        filename = "csv/" + "student_registration_data_" + t + ".csv"
        filepath = os.path.join(STATIC_ROOT, filename)
        filedir = os.path.dirname(filepath)

        if not os.path.exists(filedir):
          os.makedirs(filedir)
          
        with open(filepath, 'wb') as csv_file:
          fw = csv.DictWriter(csv_file, delimiter=',', fieldnames=column_header)
          fw.writerow(dict((col,col) for col in column_header))
          for row in json_data:
            v = {}
            v["stud_id"] = row.pop("stud_id")
            fw.writerow(row)
            row.update(v)
        # End: CSV file processing ----------------------------------------------
        
        column_header = ['Name', "Reg# Date", "Gender", "Birth Date", "Email ID", 'stud_id']

        for i, each in enumerate(json_data):
          data = []
          for ch in column_header:
            data.append(each[ch])

          json_data[i] = data

      university = collection.Node.one({'_id': ObjectId(university_id)}, {'name': 1})
      college = collection.Node.one({'_id': ObjectId(query["relation_set.student_belongs_to_college"])})
      students_count = len(json_data)

      student_list = render_to_string('ndf/student_data_review.html', 
                                        {'groupid': groupid, 'app_id': app_id, 'app_set_id': app_set_id, 
                                         'university': university, 'college': college, 'students_count': students_count, 'half_count': students_count/2,
                                         'column_header': column_header, 'students_list': json_data, 'filename': filename
                                        },
                                        context_instance = RequestContext(request)
                                    )

      response_dict["success"] = True
      response_dict["students_data_review"] = student_list

      return HttpResponse(json.dumps(response_dict))

    else:
      error_message = "StudentFindError: Either not an ajax call or not a POST request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except OSError as oe:
    error_message = "StudentFindError: " + str(oe) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "StudentFindError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

def get_college_wise_students_data(request, group_id):
  """
  This view returns a download link of CSV created consisting of students statistical data based on degree_year for each college.

  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  A dictionary consisting of following key-value pairs:-
  success - Boolean giving the state of ajax call
  message - Basestring giving the error/information message
  download_link - file path of CSV created
  """
  response_dict = {'success': False, 'message': ""}
  all_students_text = ""

  try:
    if request.is_ajax() and request.method == "GET":
      groupid = request.GET.get("groupid", None)

      mis_admin = collection.Node.one({'_type': "Group", 'name': "MIS_admin"}, {'_id': 1})
      college_gst = collection.Node.one({'_type': "GSystemType", 'name': "College"}, {'_id': 1})
      student = collection.Node.one({'_type': "GSystemType", 'name': "Student"})

      date_lte = datetime.datetime.strptime("31/12/2014", "%d/%m/%Y")
      date_gte = datetime.datetime.strptime("1/1/2014", "%d/%m/%Y")

      college_cur = collection.Node.find({'member_of': college_gst._id, 'group_set': mis_admin._id}, 
                                         {'_id': 1, 'name': 1, 'relation_set': 1}).sort('name', 1)

      json_data = []
      for i, each in enumerate(college_cur):
        data = {}
        college_group_id = None
        for each_dict in each.relation_set:
          if u"has_group" in each_dict.keys():
            college_group_id = each_dict["has_group"]
            break

        rec = collection.aggregate([{'$match': {'member_of': student._id,
                                                'group_set': {'$in': [college_group_id, mis_admin._id]},
                                                'relation_set.student_belongs_to_college': each._id,
                                                'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte}
                                    }},
                                    {'$group': {
                                      '_id': {'College': '$each.name', 'Degree Year': '$attribute_set.degree_year'},
                                      'No of students': {'$sum': 1}
                                    }}
                                  ])

        data["College"] = each.name
        for res in rec["result"]:
          data[res["_id"]["Degree Year"][0]] = res["No of students"]
        if not data.has_key("I"):
          data["I"] = 0
        if not data.has_key("II"):
          data["II"] = 0
        if not data.has_key("III"):
          data["III"] = 0

        data["Total"] = data["I"] + data["II"] + data["III"]

        json_data.append(data)

      t = time.strftime("%c").replace(":", "_").replace(" ", "_")
      filename = "csv/" + "college_wise_student_data_" + t + ".csv"
      filepath = os.path.join(STATIC_ROOT, filename)
      filedir = os.path.dirname(filepath)

      if not os.path.exists(filedir):
        os.makedirs(filedir)

      column_header = [u"College", u"Program Officer", u"I", u"II", u"III", u"Total"]

      PO = {
        "Agra College": ["Mr. Rajaram Yadav"],
        "Arts College Shamlaji": ["Mr. Ashish Varia"],
        "Baba Bhairabananda Mahavidyalaya": ["Mr. Mithilesh Kumar"],
        "Balugaon College": ["Mr. Pradeep Pradhan"],
        "City Women's College": ["Ms. Rajni Sharma"],
        "Comrade Godavari Shamrao Parulekar College of Arts, Commerce & Science": ["Mr. Rahul Sable"],
        "Faculty of Arts": ["Mr. Jokhim", "Ms. Tusharika Kumbhar"],
        "Gaya College":  ["Ms. Rishvana Sheik"],
        "Govt. M. H. College of Home Science & Science for Women, Autonomous": [], 
        "Govt. Mahakoshal Arts and Commerce College": ["Ms. Davis Yadav"],
        "Govt. Mahaprabhu Vallabhacharya Post Graduate College": ["Mr. Gaurav Sharma"],
        "Govt. Rani Durgavati Post Graduate College": ["Mr. Asad Ullah"],
        "Jamshedpur Women's College": ["Mr. Arun Agrawal"],
        "Kalyan Post Graduate College": ["Mr. Praveen Kumar"],
        "Kamla Nehru College for Women": ["Ms. Tusharika Kumbhar", "Ms. Thaku Pujari"],
        "L. B. S. M. College": ["Mr. Charles Kindo"],
        "Mahila College": ["Mr. Sonu Kumar"],
        "Marwari College": ["Mr. Avinash Anand"],
        "Matsyodari Shikshan Sanstha's Arts, Commerce & Science College": ["Ms. Jyoti Kapale"],
        "Ranchi Women's College": ["Mr. Avinash Anand"],
        "Shiv Chhatrapati College": ["Mr. Swapnil Sardar"],
        "Shri & Smt. PK Kotawala Arts College": ["Mr. Sawan Kumar"],
        "Shri VR Patel College of Commerce": ["Mr. Sushil Mishra"],
        "Sree Narayana Guru College of Commerce": ["Ms. Bharti Bhalerao"],
        "Sri Mahanth Shatanand Giri College": ["Mr. Narendra Singh"],
        "St. John's College": ["Mr. Himanshu Guru"],
        "The Graduate School College For Women": ["Mr. Pradeep Gupta"],
        "Vasant Rao Naik Mahavidyalaya": ["Mr. Dayanand Waghmare"],
        "Vivekanand Arts, Sardar Dalip Singh Commerce & Science College": ["Mr. Anis Ambade"]
      }

      with open(filepath, 'wb') as csv_file:
        fw = csv.DictWriter(csv_file, delimiter=',', fieldnames=column_header)
        fw.writerow(dict((col,col) for col in column_header))
        for row in json_data:
          row[u"Program Officer"] = ", ".join(PO[row[u"College"]])
          fw.writerow(row)

      response_dict["success"] = True
      response_dict["download_link"] = (STATIC_URL + filename)
      return HttpResponse(json.dumps(response_dict))

    else:
      error_message = "CollegeSummaryDataError: Either not an ajax call or not a POST request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except OSError as oe:
    error_message = "CollegeSummaryDataError: " + str(oe) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "CollegeSummaryDataError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

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
      file_res = collection.Node.one({'_type': "GSystemType", 'name': "File"}, {'_id': 1})
      image_res = collection.Node.one({'_type': "GSystemType", 'name': "Image"}, {'_id': 1})
      video_res = collection.Node.one({'_type': "GSystemType", 'name': "Video"}, {'_id': 1})

      student_list = []

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
        student_dict["Images"] = num_images
        student_dict["Videos"] = num_videos
        student_dict["Files"] = num_files

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

          student_list.append(student_dict)

        # Outside of above for loop

        return render_to_response("ndf/student_statistics.html",
                                  {'node': college_group,'student_list': student_list},
                                  context_instance = RequestContext(request)
                                )
    
    else:
      error_message = "StudentDataGetError: Invalid ajax call!!!"
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

def get_affiliated_colleges(request, group_id):
  """
  This view returns list of colleges affiliated to given university.

  Each element of the list is again a list where,
  0th index-element: ObjectId of college
  1st index-element: Name of college

  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  A dictionary consisting of following key-value pairs:-
  success - Boolean giving the state of ajax call
  message - Basestring giving the error/information message
  affiliated_colleges - List consisting of affiliated colleges (ObjectIds & names)
  """
  response_dict = {'success': False, 'message': ""}
  all_students_text = ""

  try:
    if request.is_ajax() and request.method == "GET":
      # Fetch field(s) from GET object
      university_id = request.GET.get("university_id", "")
      req_university = None
      req_affiliated_colleges = None

      # Check whether any field has missing value or not
      if university_id == "":
        error_message = "AffiliatedCollegeFindError: Invalid data (No university selected)!!!"
        raise Exception(error_message)

      # Type-cast fetched field(s) into their appropriate type
      university_id = ObjectId(university_id)

      # Fetch required university
      req_university = collection.Node.one({'_id': university_id})

      if not req_university:
        error_message = "AffiliatedCollegeFindError: No university exists with given ObjectId("+university_id+")!!!"
        raise Exception(error_message)

      for each in req_university["relation_set"]:
        if u"affiliated_college" in each.keys():
          req_affiliated_colleges = collection.Node.find({'_id': {'$in': each[u"affiliated_college"]}}, {'name': 1}).sort('name', 1)
      
      req_affiliated_colleges_list = []
      for each in req_affiliated_colleges:
        req_affiliated_colleges_list.append([str(each._id), each.name])

      response_dict["affiliated_colleges"] = req_affiliated_colleges_list

      response_dict["success"] = True
      response_dict["message"] = "This university ("+req_university.name+") has following list of affiliated colleges:"
      for i, each in enumerate(req_affiliated_colleges_list):
        response_dict["message"] += "\n\n " + str(i+1) + ". " + each[1]

      return HttpResponse(json.dumps(response_dict))

    else:
      error_message = "AffiliatedCollegeFindError: Either not an ajax call or not a GET request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "AffiliatedCollegeFindError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

def get_courses(request, group_id):
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
      college_groups = []

      # Check whether any field has missing value or not
      if start_time == "" or end_time == "" or nussd_course_type == "":
        error_message = "Invalid data: No data found in any of the field(s)!!!"
        raise Exception(error_message)

      # Fetch "Announced Course" GSystemType
      mis_admin = collection.Node.one({'_type': "Group", 'name': "MIS_admin"}, {'name': 1})
      if not mis_admin:
        # If not found, throw exception
        error_message = "'MIS_admin' (Group) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Fetch "has_group" RelationType
      has_group_RT = collection.Node.one({'_type': "RelationType", 'name': "has_group"}, {'_id': 1})
      if not has_group_RT:
        # If not found, throw exception
        error_message = "'has_group' (RelationType) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Fetch "Announced Course" GSystemType
      nussd_course_gt = collection.Node.one({'_type': "GSystemType", 'name': "NUSSD Course"})
      if not nussd_course_gt:
        # If not found, throw exception
        error_message = "'NUSSD Course' (GSystemType) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Fetch "Announced Course" GSystemType
      announced_course_gt = collection.Node.one({'_type': "GSystemType", 'name': "Announced Course"})
      if not announced_course_gt:
        # If not found, throw exception
        error_message = "'Announced Course' (GSystemType) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Fetch all college groups
      college = collection.Node.one({'_type': "GSystemType", 'name': "College"}, {'name': 1})
      if not college:
        # If not found, throw exception
        error_message = "'College' (GSystemType) doesn't exists... Please create it first"
        raise Exception(error_message)
      else:
        college_gs = collection.Node.find({'member_of': college._id, 'group_set': mis_admin._id}, {'_id': 1})
        for each in college_gs:
          cg = collection.Triple.one({'_type': "GRelation", 'subject': each._id, 'relation_type.$id': has_group_RT._id}, {'right_subject': 1})
          if cg:
            college_groups.append(cg.right_subject)

      # Type-cast fetched field(s) into their appropriate type
      start_time = datetime.datetime.strptime(start_time, "%m/%Y")
      end_time = datetime.datetime.strptime(end_time, "%m/%Y")
      nussd_course_type = unicode(nussd_course_type)

      groups_to_search_from = []
      if ObjectId(group_id) == mis_admin._id or ObjectId(group_id) in college_groups:
        groups_to_search_from = college_groups
        groups_to_search_from.append(mis_admin._id)

      else:
        groups_to_search_from = [ObjectId(group_id)]

      # Fetch registered NUSSD-Courses of given type
      nc_cur = collection.Node.find({'member_of': nussd_course_gt._id, 
                                      'group_set': {'$in': groups_to_search_from},
                                      'attribute_set.nussd_course_type': nussd_course_type
                                    },
                                    {'name': 1}
                                  )

      # For that first fetch GAttribute(s) whose having value of 'object_type' field
      # as given type (nussd_course_type)
      # From that you will get NUSSD-Courses (ObjectId) via 'subject' field
      # And for name, you need to extract from GAttributes 'name' field
      # nc_cur = collection.Triple.find({'_type': "GAttribute", 'object_value': nussd_course_type})

      # This below dict holds
      # > key as ObjectId (string representation) of the given NUSSD course
      #   >> String representation because it's going to be used in json.dumps() & it
      #      requires keys to be in string format only
      # > value as name of the given NUSSD course
      nc_dict = {}
      if nc_cur.count():
        # If found, append them to a dict
        for each in nc_cur:
          nc_dict[str(each._id)] = each.name
  
      else:
        # Otherwise, throw exception
        error_message = "No such ("+nussd_course_type+") type of course exists... register it first"
        raise Exception(error_message)

      # Search for already created announced-courses with given criteria
      # ac_cur = collection.Node.find({'member_of': announced_course_gt._id, 
      #                                 'group_set': {'$in': groups_to_search_from},
      #                                 'attribute_set.start_time': start_time, 
      #                                 'attribute_set.end_time': end_time,
      #                                 'attribute_set.nussd_course_type': nussd_course_type
      #                               })

      # if ac_cur.count():
      #   # Iterate already existing announced-course(s)' instances
      #   # > Iterate registered NUSSD-courses 
      #   #   >> If match found between both of them
      #   #   >> Then
      #   #      >>> delete registered NUSSD-course entry from dict
      #   #      >>> Add already existing Announced-course entry in it
      #   #      >>> break inner for-loop, continue with next announced-course value
      #   for each in ac_cur:
      #     for k, v in nc_dict.iteritems():
      #       if v in each.name:
      #         del nc_dict[k]
      #         nc_dict[str(each._id)] = each.name
      #         break

      #   response_dict["success"] = True
      #   response_dict["message"] = "NOTE: Some announced-course(s) found which match given criteria."
      #   response_dict["unset_nc"] = nc_dict

      # else:
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

def get_announced_courses_with_ctype(request, group_id):
  """
  This view returns list of announced-course(s) that match given criteria
  along with NUSSD-Course(s) for which match doesn't exists.

  Arguments:
  group_id - ObjectId of the currently selected group
  nussd_course_type - Type of NUSSD course

  Returns:
  A dictionary consisting of following key-value pairs:-
  acourse_ctype_list - dictionary consisting of announced-course(s) [if match found] and/or 
             NUSSD-Courses [if match not found]
  """

  try:
    if request.is_ajax() and request.method == "GET":
      # Fetch field(s) from GET object
      nussd_course_type = request.GET.get("nussd_course_type", "")
      acourse_ctype_list = []

      # Fetch "Announced Course" GSystemType
      nussd_course_gt = collection.Node.one({'_type': "GSystemType", 'name': "NUSSD Course"})
      if not nussd_course_gt:
        # If not found, throw exception
        error_message = "'NUSSD Course' (GSystemType) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Fetch "Announced Course" GSystemType
      announced_course_gt = collection.Node.one({'_type': "GSystemType", 'name': "Announced Course"})
      if not announced_course_gt:
        # If not found, throw exception
        error_message = "'Announced Course' (GSystemType) doesn't exists... Please create it first"
        raise Exception(error_message)
      
      # Type-cast fetched field(s) into their appropriate type
      nussd_course_type = unicode(nussd_course_type)

      groups_to_search_from = [ObjectId(group_id)]
                                    
      ac_cur = collection.Node.find({'member_of': announced_course_gt._id, 
                                      'group_set': {'$in': groups_to_search_from},
                                      'attribute_set.nussd_course_type': nussd_course_type
                                    },{'name':1})

      if ac_cur.count():
        for d in ac_cur:
          acourse_ctype_list.append(d.name)

      else:
        error_message = "No Announced Course found"
        raise Exception(error_message)
      
      return HttpResponse(json.dumps(acourse_ctype_list))

    else:
      error_message = " AnnouncedCourseFetchError: Either not an ajax call or not a GET request!!!"
      return HttpResponse(json.dumps({'message': " AnnouncedCourseFetchError - Something went wrong in ajax call !!! \n\n Please contact system administrator."}))

  except Exception as e:
    error_message = "\n AnnouncedCourseFetchError: " + str(e) + "!!!"
    return HttpResponse(json.dumps({'message': error_message}))

def get_enroll_duration_of_ac(request, group_id):
  """
  This view returns list of announced-course(s) that match given criteria
  along with NUSSD-Course(s) for which match doesn't exists.

  Arguments:
  group_id - ObjectId of the currently selected group
  announced_course_id - ObjectId of currently selected Announced Course

  Returns:
  A dictionary consisting of following key-value pairs:-
  acourse_ctype_list - dictionary consisting of announced-course(s) [if match found] and/or 
             NUSSD-Courses [if match not found]
  """
  response_dict = {'success': False, 'message': ""}
  try:
    if request.is_ajax() and request.method == "GET":
      # Fetch field(s) from GET object
      acourse_name = request.GET.get("acourse_name", "")
      acourse_name_id = ""
      # Fetch "Announced Course" GSystemType
      announced_course_gst = collection.Node.one({'_type': "GSystemType", 'name': "Announced Course"})
      try:
        acourse_node = collection.Node.one({'member_of':announced_course_gst._id,u'name':unicode(acourse_name)})
        
      except:
        acourse_node = collection.Node.find({'member_of':announced_course_gst._id,u'name':unicode(acourse_name)})
        print acourse_node,"\n\nMultiple Announced Course with same name exists"

      se= acourse_node.attribute_set[3]
      se = se[u'start_enroll'].strftime("%m-%d-%Y")
      response_dict["start_enroll"]=se

      ee= acourse_node.attribute_set[4]
      ee = ee[u'end_enroll'].strftime("%m-%d-%Y")
      response_dict["end_enroll"]=ee
      return HttpResponse(json.dumps(response_dict))
    else:
      error_message = " EnrollDurationFetchError: Either not an ajax call or not a GET request!!!"
      return HttpResponse(json.dumps({'message': " EnrollDurationFetchError - Something went wrong in ajax call !!! \n\n Please contact system administrator."}))

  except Exception as e:
    error_message = "\n EnrollDurationFetchError: " + str(e) + "!!!"
    return HttpResponse(json.dumps({'message': error_message}))

def get_colleges(request,group_id):
  """
  This view returns list of college(s) that are affiliated to 
  the selected University

  Arguments:
  group_id - ObjectId of the currently selected group
  univ_id - ObjectId of currently selected University
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
      univ_id = request.GET.get("univ_id", "")
      # all_univs = request.GET.get("all_univs", "")
      
      # Check whether any field has missing value or not
      if univ_id == "":
        error_message = "Invalid data: No data found in any of the field(s)!!!"
        raise Exception(error_message)

      # Fetch "Announced Course" GSystemType
      mis_admin = collection.Node.one({'_type': "Group", 'name': "MIS_admin"}, {'name': 1})
      if not mis_admin:
        # If not found, throw exception
        error_message = "'MIS_admin' (Group) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Fetch all college groups
      college = collection.Node.one({'_type': "GSystemType", 'name': "College"}, {'name': 1})
      if not college:
        # If not found, throw exception
        error_message = "'College' (GSystemType) doesn't exists... Please create it first"
        raise Exception(error_message)
      
      # Type-cast fetched field(s) into their appropriate type
      univ_id = ObjectId(univ_id)

      # Fetch the node of selected university
      univGST = collection.Node.one({'_type': "GSystemType", 'name': "University"}, {'_id': 1})
      university_node = collection.Node.one({'_id': univ_id}, {'relation_set': 1,'name':1})

      # Fetch the list of colleges that are affiliated by the selected university
      college_ids = []
      for each in university_node.relation_set:
        if each.has_key("affiliated_college"):
          college_ids = each["affiliated_college"]
          
      #If "Select All" checkbox is True, display all colleges from all universities
      # if all_univs == u"true":
      #   colg_under_univ_id = collection.Node.find({'member_of': college._id},{'name': 1}).sort('name',1)
      #   msg_string = " List of colleges in ALL Universities."
      # else:
      colg_under_univ_id = collection.Node.find({'member_of': college._id, '_id': {'$in': college_ids}},{'_id': 1, 'name': 1, 'member_of': 1, 'created_by': 1, 'created_at': 1, 'content': 1}).sort('name',1)
      msg_string = " List of colleges in " +university_node.name+"."
      
      list_colg=[]                           
      for each in colg_under_univ_id:
        list_colg.append(each)

      nc_dict = {}
      if colg_under_univ_id.count():
        # If found, append them to a dict
        for each in colg_under_univ_id:
          nc_dict[str(each._id)] = each.name

      response_dict["unset_nc"] = nc_dict
      drawer_template_context = edit_drawer_widget("RelationType", group_id, None, None, checked="announced_course_create_edit", left_drawer_content=list_colg)
      drawer_template_context["widget_for"] = "announced_course_create_edit"
      drawer_widget = render_to_string('ndf/drawer_widget.html', 
                                        drawer_template_context,
                                        context_instance = RequestContext(request)
                                      )
      response_dict["drawer_widget"] = drawer_widget
      response_dict["success"] = True
      response_dict["message"] = msg_string
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
      registration_year = request.GET.get("registration_year", "")
      all_students = request.GET.get("all_students", "")
      college_groups = []   # List of ObjectIds

      # Check whether any field has missing value or not
      if registration_year == "" or all_students == "":
        error_message = "Invalid data: No data found in any of the field(s)!!!"
        raise Exception(error_message)

      # Fetch "MIS_admin" Group
      mis_admin = collection.Node.one({'_type': "Group", 'name': "MIS_admin"}, {'name': 1})
      if not mis_admin:
        # If not found, throw exception
        error_message = "'MIS_admin' (Group) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Fetch "Announced Course" GSystemType
      announced_course_gt = collection.Node.one({'_type': "GSystemType", 'name': "Announced Course"}, {'name': 1})
      if not announced_course_gt:
        # If not found, throw exception
        error_message = "'Announced Course' (GSystemType) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Fetch "selected_course_RT" RelationType
      selected_course_RT = collection.Node.one({'_type': "RelationType", 'name': "selected_course"}, {'_id': 1})
      if not selected_course_RT:
        # If not found, throw exception
        error_message = "'selected_course' (RelationType) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Fetch "has_group" RelationType
      has_group_RT = collection.Node.one({'_type': "RelationType", 'name': "has_group"}, {'_id': 1})
      if not has_group_RT:
        # If not found, throw exception
        error_message = "'has_group' (RelationType) doesn't exists... Please create it first"
        raise Exception(error_message)

      # Type-cast fetched field(s) into their appropriate type
      
      date_lte = datetime.datetime.strptime("31/12/"+registration_year, "%d/%m/%Y")
      date_gte = datetime.datetime.strptime("1/1/"+registration_year, "%d/%m/%Y")

      groups_to_search_from = []
      groups_to_search_from = [ObjectId(group_id)]

      student = collection.Node.one({'_type': "GSystemType", 'name': "Student"})

      if all_students == u"true":
        all_students_text = "All students (including enrolled ones)"

        res = collection.Node.find({'member_of': student._id, 
                                      'group_set': {'$in': groups_to_search_from},
                                      'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte},
                                    },
                                    {'_id': 1, 'name': 1, 'member_of': 1, 'created_by': 1, 'created_at': 1, 'content': 1}
                                  ).sort("name", 1) 
        all_students_text += " [Count("+str(res.count())+")]"
        # drawer_template_context = edit_drawer_widget("", group_id, None, list(res))
        # page_no = 1
        checked = "student_enroll"
        drawer_template_context = edit_drawer_widget("RelationType", group_id, None, page_no, checked, left_drawer_content=res)

      elif all_students == u"false":
        all_students_text = "Only non-enrolled students"

        res = collection.Node.find({'member_of': student._id, 
                                      'group_set': {'$in': groups_to_search_from},
                                      'relation_set.selected_course': {'$exists': False},
                                      'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte},
                                    },
                                    {'_id': 1,'name': 1, 'member_of': 1, 'created_by': 1, 'created_at': 1, 'content': 1}
                                  ).sort("name", 1)
        all_students_text += " [Count("+str(res.count())+")]"
        checked = "student_enroll"
        # drawer_template_context = edit_drawer_widget("RelationType", group_id, None, page_no, checked, left_drawer_content=res)
        drawer_template_context = edit_drawer_widget("RelationType", group_id, checked=checked, left_drawer_content=res)

      
      drawer_template_context["widget_for"] = "student_enroll"
      drawer_widget = render_to_string('ndf/drawer_widget.html', 
                                        drawer_template_context,
                                        context_instance = RequestContext(request)
                                      )

      response_dict["announced_courses"] = []
      response_dict["drawer_widget"] = drawer_widget

      response_dict["success"] = True
      response_dict["message"] = "NOTE: " + all_students_text + " are listed along with announced courses"

      return HttpResponse(json.dumps(response_dict))

    else:
      error_message = "EnrollInCourseError: Either not an ajax call or not a GET request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "EnrollInCourseError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

def get_course_details_for_trainer(request, group_id):
  """
  This view returns a dictionary holding data required for trainer's enrollment
  into given announced course(s).

  Arguments:
  group_id - ObjectId of the currently selected group

  Returns:
  A dictionary consisting of following key-value pairs:-
  success - Boolean giving the state of ajax call
  message - Basestring giving the error/information message
  course_enrollement_details - Dictionary that has following structure:
    Key: Course-name
    Value: A list of dictionary where this dictionary's structure is as follows:
      1) Key: ann_course_id; Value: ObjectId of corresponding Announced Course
      2) Key: university; Value: University-name
      3) Key: college; Value: College GSystem's document
  """
  response_dict = {'success': False, 'message': ""}
  all_students_text = ""

  try:
    if request.is_ajax() and request.method == "GET":
      course_type = request.GET.get("course_type", "")
      trainer_type = request.GET.get("trainer_type", "")

      # Check whether any field has missing value or not
      if course_type == "" or trainer_type == "":
        error_message = "Invalid data: No data found in any of the field(s)!!!"
        raise Exception(error_message)

      # Fetch required GSystemTypes (NUSSD Course, Announced Course, University, College)
      course_gst = collection.Node.one({'_type': "GSystemType", 'name': "NUSSD Course"}, {'_id': 1})
      ann_course_gst = collection.Node.one({'_type': "GSystemType", 'name': "Announced Course"}, {'_id': 1})
      college_gst = collection.Node.one({'_type': "GSystemType", 'name': "College"}, {'_id': 1})
      university_gst = collection.Node.one({'_type': "GSystemType", 'name': "University"}, {'_id': 1})
      mis_admin = collection.Node.one({'_type': "Group", 'name': "MIS_admin"}, {'_id': 1})

      # Query that fetches Announced Course GSystems
      # Group by Course
      # Populate a list of Announced Course & College ObjectIds
      op = collection.aggregate([
        {'$match': {
          'member_of': ann_course_gst._id, 
          'group_set': mis_admin._id,
          'status': u"PUBLISHED", 
          'attribute_set.nussd_course_type': course_type
        }},
        {'$group': {
          '_id': {'course_id': "$relation_set.announced_for"},
          'college_wise_data': {'$addToSet': {'ann_course_id': "$_id", 'college_id': "$relation_set.acourse_for_college"}}
        }}
      ])

      if op["result"]:
        course_enrollement_details = {}
        course_requirements = {}
        college_dict = {}
        university_dict = {}


        for each in op["result"]:
          course = None
          if trainer_type == "Voluntary Teacher":
            course = collection.Node.one({'member_of': course_gst._id, '_id': {'$in': each["_id"]["course_id"][0]}}, {'_id': 1, 'name': 1, 'attribute_set.voln_tr_qualifications': 1})

            for requirement in course.attribute_set:
              if requirement:
                course_requirements[course.name] = requirement["voln_tr_qualifications"]
          
          elif trainer_type == "Master Trainer":
            course = collection.Node.one({'member_of': course_gst._id, '_id': {'$in': each["_id"]["course_id"][0]}}, {'_id': 1, 'name': 1, 'attribute_set.mast_tr_qualifications': 1})

            for requirement in course.attribute_set:
              if requirement:
                course_requirements[course.name] = requirement["mast_tr_qualifications"]

          course_enrollement_details[course.name] = []

          if course:
            for each_data in each["college_wise_data"]:
              data_dict = {}
              data_dict['ann_course_id'] = each_data["ann_course_id"]

              college_gs = None
              college_id = each_data["college_id"][0][0]
              if college_id not in college_dict:
                college_gs = collection.Node.one({'member_of': college_gst._id, '_id': college_id}, {'_id': 1, 'name': 1, 'member_of': 1, 'created_by': 1, 'created_at': 1, 'content': 1})
                college_dict[college_id] = college_gs
              else:
                college_gs = college_dict[college_id]
              data_dict['college'] = college_gs.name
              
              university_gs = None
              if college_id not in university_dict:
                university_gs = collection.Node.one({'member_of': university_gst._id, 'relation_set.affiliated_college': college_gs._id}, {'_id': 1, 'name': 1})
                university_dict[college_id] = university_gs
              else:
                university_gs = university_dict[college_id]
              data_dict['university'] = university_gs.name

              course_enrollement_details[course.name].append(data_dict)
              
          else:
            error_message = "No Course exists with such ObjectId(" + str(each["_id"]["course_id"])
            raise Exception(error_message)

      else:
        error_message = "No Course(s) announced of given type ("+course_type+") "
        raise Exception(error_message)

      response_dict["course_enrollement_details"] = course_enrollement_details
      response_dict["course_requirements"] = course_requirements

      response_dict["success"] = True
      response_dict["message"] = ""

      return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

    else:
      error_message = "TrainerCourseDetailError: Either not an ajax call or not a GET request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "TrainerCourseDetailError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

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

def insert_picture(request, group_id):
    if request.is_ajax():
        resource_list=collection.Node.find({'_type' : 'File', 'mime_type' : u"image/jpeg" },{'_id': 0, 'name': 1})
        resources=list(resource_list)
    return StreamingHttpResponse(json.dumps(resources))


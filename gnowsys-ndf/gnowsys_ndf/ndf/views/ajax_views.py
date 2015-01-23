''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import datetime
import csv
import time
import ast
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.http import Http404
from django.core.paginator import Paginator
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django_mongokit import get_database
from mongokit import paginator
from django.contrib.sites.models import Site

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
from gnowsys_ndf.ndf.views.methods import check_existing_group, get_drawers, get_node_common_fields, get_node_metadata, create_grelation,create_gattribute,create_task
from gnowsys_ndf.ndf.views.methods import get_widget_built_up_data, parse_template_data
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_profile_pic, edit_drawer_widget, get_contents
from gnowsys_ndf.ndf.views.methods import create_gattribute
#from datetime import date,time,timedelta
from gnowsys_ndf.mobwrite.models import ViewObj

 
db = get_database()
gs_collection = db[GSystem.collection_name]
collection = db[Node.collection_name]
theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
theme_item_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'theme_item'})
# This function is used to check (while creating a new group) group exists or not
# This is called in the lost focus event of the group_name text box, to check the existance of group, in order to avoid duplication of group names.

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
  '''
  This ajax function retunrs the node on main template, when clicked on collection hierarchy
  '''
  if request.is_ajax() and request.method == "POST":    
    node_id = request.POST.get("node_id", '')

    topic = ""
    node_obj = collection.Node.one({'_id': ObjectId(node_id)})
    topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
    if topic_GST._id in node_obj.member_of:
      topic = "topic"


    # node_obj.get_neighbourhood(node_obj.member_of)

    return render_to_response('ndf/node_ajax_view.html', 
                                { 'node': node_obj,
                                  'group_id': group_id,
                                  'groupid':group_id,
                                  'app_id': node_id, 'topic':topic
                                },
                                context_instance = RequestContext(request)
    )

# This view handles the collection list of resource and its breadcrumbs
def collection_view(request, group_id):
  '''
  This ajax function returns breadcrumbs_list for clicked node in collection hierarchy
  '''
  if request.is_ajax() and request.method == "POST":    
    node_id = request.POST.get("node_id", '')
    breadcrumbs_list = request.POST.get("breadcrumbs_list", '')

    node_obj = collection.Node.one({'_id': ObjectId(node_id)})
    breadcrumbs_list = breadcrumbs_list.replace("&#39;","'")
    breadcrumbs_list = ast.literal_eval(breadcrumbs_list)

    b_list = []
    for each in breadcrumbs_list:
      b_list.append(each[0])
    
    if str(node_obj._id) not in b_list:
      # Add the tuple if clicked node is not there in breadcrumbs list
      breadcrumbs_list.append( (str(node_obj._id), node_obj.name) )
    else:
      # To remove breadcrumbs untill clicked node have not reached(Removal starts in reverse order)
      for e in reversed(breadcrumbs_list):
        if node_id in e:
          break
        else:
          breadcrumbs_list.remove(e)
        

  # print "\nbreadcrumbs_list: ",breadcrumbs_list,"\n"

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

        node_id = request.POST.get("node_id", '')
        page_no = request.POST.get("page_no", '')
        field = request.POST.get("field", '')
        checked = request.POST.get("homo_collection", '')
        node_type = request.POST.get("node_type", '')
          
        if node_id:
          node_id = ObjectId(node_id)
          node = collection.Node.one({'_id': ObjectId(node_id) })  
          if node_type:
            if len(node.member_of) > 1:
              n_type = collection.Node.one({'_id': ObjectId(node.member_of[1]) })
            else:
              n_type = collection.Node.one({'_id': ObjectId(node.member_of[0]) })
            checked = n_type.name

        if checked:
          if checked == "QuizObj" :
            quiz = collection.Node.one({'_type': 'GSystemType', 'name': "Quiz" })
            quizitem = collection.Node.one({'_type': 'GSystemType', 'name': "QuizItem" })

          elif checked == "Pandora Video":
            check = collection.Node.one({'_type': 'GSystemType', 'name': 'Pandora_video' })

          else:
            check = collection.Node.one({'_type': 'GSystemType', 'name': unicode(checked) })

        if node_id:

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


        if node_id:

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
                                   "drawer2": drawer2, "checked": checked,
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

      Page = collection.Node.one({'_type': 'GSystemType', 'name': 'Page'})
      File = collection.Node.one({'_type': 'GSystemType', 'name': 'File'})
      Quiz = collection.Node.one({'_type': "GSystemType", 'name': "Quiz"})

      if node_id:
        node = collection.Node.one({'_id': ObjectId(node_id) })
        node_type = collection.Node.one({'_id': ObjectId(node.member_of[0]) })

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

        search_drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]},
                                        'member_of':{'$in':[Page._id,File._id,Quiz._id]}, 
                                        '$and': [
                                          {'name': {'$regex': str(search_name), '$options': "i"}},
                                          {'group_set': {'$all': [ObjectId(group_id)]} }
                                        ]
                                      })   
        

      else:
          search_drawer = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 
                                          'member_of':{'$in':[Page._id,File._id,Quiz._id]}, 
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
      

def get_topic_contents(request, group_id):
    
  if request.is_ajax() and request.method == "POST":
    node_id = request.POST.get("node_id", '')
    selected = request.POST.get("selected", '')
    choice = request.POST.get("choice", '')
    # node = collection.Node.one({'_id': ObjectId(node_id) })

    contents = get_contents(node_id, selected, choice)

    return HttpResponse(json.dumps(contents))
      

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
    Collapsible = request.GET.get("collapsible", "");

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


    if Collapsible:
      data = { "name": theme_node.name, "children": collection_list }
    else:
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
       dic['name'] = each.email  # username
       d1.append(dic)
    draw1['drawer1'] = d1
    data_list.append(draw1)
    
    for each in coll_obj_list:
       dic = {}
       dic['id'] = str(each.id)
       dic['name'] = each.email  # username
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
    batch_coll = collection.GSystem.find({'member_of':st._id, 'group_set': {'$all': [ObjectId(group_id)]}})
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
    currentYear = datetime.datetime.now().year
    #create the date format in unix format for querying it from data 
    #Task attribute_type start time's object value takes the only date 
    #in month/date/year format 
    #As events are quried from the nodes which store the date time in unix format
    month=request.GET.get('start','')[5:7]
    year=request.GET.get('start','')[0:4]
    start = datetime.datetime(int(currentYear), int(month), 1)
    task_start=str(int(month))+"/"+"01"+"/"+str(int(year))
    
    if int(month) in list31:
     end=datetime.datetime(int(currentYear),int(month), 31)
     task_end=str(int(month))+"/"+"31"+"/"+str(int(year))
    elif int(month) in list30:
     end=datetime.datetime(int(currentYear),int(month), 30)
     task_end=str(int(month))+"/"+"30"+"/"+str(int(year))
    else:
     end=datetime.datetime(int(currentYear),int(month), 28)
     task_end=str(int(month))+"/"+"28"+"/"+str(int(year)) 
    #day_list of events  
    for j in obj:
        nodes = collection.Node.find({'member_of': ObjectId(j._id),'attribute_set.start_time':{'$gte':start,'$lt': end},'group_set':ObjectId(group_id)})
        for i in nodes:
          attr_value={}
          event_url="/"+str(group_id)+"/event/"+str(j._id) +"/"+str(i._id)
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
    #check wheather the group is author group or the common group
    if groupname._type == "Group":
          GST_TASK = collection.Node.one({'_type': "GSystemType", 'name': 'Task'})
          task_nodes = collection.GSystem.find({'member_of': {'$all': [GST_TASK._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
    if groupname._type == "Author":
          task_nodes = collection.Node.find({"_type":"GAttribute", "attribute_type.$id":attributetype_assignee._id,                                "object_value":request.user.id}).sort('last_update',-1)
    for attr in task_nodes:
     if groupname._type == "Group": 
         task_node = collection.Node.one({'_id':attr._id})
     if groupname._type == "Author":
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
        if date == (i['start'].split("T")[0]) or date == "":
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
        date=i['start'].split("T")[0]    
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
      node = collection.Node.one({'_id': ObjectId(each)})
      left_relations = collection.Node.find({"_type":"GRelation", "subject":node._id})
      right_relations = collection.Node.find({"_type":"GRelation", "right_subject":node._id})
      attributes = collection.Node.find({"_type":"GAttribute", "subject":node._id})

      # When confirm holds "yes" value, all given node(s) is/are deleted.
      # Otherwise, required information is provided for confirmation before deletion.
      if confirm:
        # Deleting GRelation(s) where given node is used as "subject"
        for each_left_gr in left_relations:
          # Special case
          if each_left_gr.relation_type.name == "has_login":
            auth_node = collection.Node.one(
              {'_id': each_left_gr.right_subject},
              {'created_by': 1}
            )

            if auth_node:
              collection.update(
                {'_type': "Group", '$or': [{'group_admin': auth_node.created_by}, {'author_set': auth_node.created_by}]},
                {'$pull': {'group_admin': auth_node.created_by, 'author_set': auth_node.created_by}},
                upsert=False, multi=True
              )

          # If given node is used in relationship with any other node (as subject)
          # Then given node's ObjectId must be removed from "relation_set" field 
          # of other node, referred under key as inverse-name of the RelationType
          collection.update(
            {'_id': each_left_gr.right_subject, 'relation_set.'+each_left_gr.relation_type.inverse_name: {'$exists': True}}, 
            {'$pull': {'relation_set.$.'+each_left_gr.relation_type.inverse_name: node._id}}, 
            upsert=False, multi=False
          )
          each_left_gr.delete()

        # Deleting GRelation(s) where given node is used as "right_subject"
        for each_right_gr in right_relations:
          # If given node is used in relationship with any other node (as subject)
          # Then given node's ObjectId must be removed from "relation_set" field 
          # of other node, referred under key as name of the RelationType
          collection.update({'_id': each_right_gr.subject, 'relation_set.'+each_right_gr.relation_type.name: {'$exists': True}}, 
            {'$pull': {'relation_set.$.'+each_right_gr.relation_type.name: node._id}}, 
            upsert=False, multi=False
          )
          each_right_gr.delete()

        # Deleting GAttribute(s)
        for each_ga in attributes:
          each_ga.delete()
        
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
            list_rel.append(alt_names + " (Relation): " + rname)

          delete_list.append({'left_relations': list_rel})
        
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
            list_rel.append(alt_names + " (Inverse-Relation): " + lname)

          delete_list.append({'right_relations': list_rel})
        
        if attributes :
          list_att = []
          for each in attributes:
            alt_names = each.attribute_type.name
            if each.attribute_type.altnames:
              alt_names = each.attribute_type.altnames
            list_att.append(alt_names + " (Attribute): " + str(each.object_value))

          delete_list.append({'attributes': list_att})
        
        send_dict.append({"title": node.name, "content": delete_list})
    
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
  """Returns member(s) of the group excluding (group-admin(s)) in form of
  dictionary that consists of key-value pair:

  key: Primary key from Django's User table
  value: User-name of that User record
  """
  user_list = {}
  group = collection.Node.find_one({'_id':ObjectId(group_id)})
  if request.is_ajax():
    if group.author_set:
      for each in group.author_set:
        user_list[each] = User.objects.get(id=each).username
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
  This view returns list of students along with required data based on selection criteria
  to student_data_review.html

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
      stud_reg_year = str(request.POST.get("reg_year", None))

      person_gst = collection.Node.one({'_type': "GSystemType", 'name': "Student"}, {'name': 1, 'type_of': 1})

      widget_for = []
      person_gs = collection.GSystem()
      person_gs.member_of.append(person_gst._id)
      person_gs.get_neighbourhood(person_gs.member_of)
      rel_univ = collection.Node.one({'_type': "RelationType", 'name': "student_belongs_to_university"}, {'_id': 1})
      rel_colg = collection.Node.one({'_type': "RelationType", 'name': "student_belongs_to_college"}, {'_id': 1})
      attr_deg_yr = collection.Node.one({'_type': "AttributeType", 'name': "degree_year"}, {'_id': 1})

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

      date_lte = datetime.datetime.strptime("31/12/"+stud_reg_year, "%d/%m/%Y")
      date_gte = datetime.datetime.strptime("1/1/"+stud_reg_year, "%d/%m/%Y")
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
      query.update({'status': u"PUBLISHED"})
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

      response_dict["success"] = True
      student_list = render_to_string('ndf/student_data_review.html', 
                                        {'groupid': groupid, 'app_id': app_id, 'app_set_id': app_set_id, 
                                         'university': university, 'college': college, 'students_count': students_count, 'half_count': students_count/2,
                                         'column_header': column_header, 'students_list': json_data, 'filename': filename
                                        },
                                        context_instance = RequestContext(request)
                                    )
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


def get_statewise_data(request, group_id):
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

    try:
        if request.is_ajax() and request.method == "GET":
            # Fetching selected state's name
            state_val = request.GET.get("state_val", None)

            mis_admin = collection.Node.one(
                {'_type': "Group", 'name': "MIS_admin"},
                {'_id': 1}
            )

            # Fetching selected state's node
            state_gst = collection.Node.one(
                {'_type': "GSystemType", 'name': "State"}
            )
            state_gs = collection.Node.one(
                {
                    'member_of': state_gst._id,
                    'name': {'$regex': state_val, '$options': "i"},
                    'group_set': mis_admin._id
                }
            )

            # Fetching universities belonging to that state
            university_gst = collection.Node.one(
                {'_type': "GSystemType", 'name': "University"}
            )
            university_cur = collection.Node.find(
                {
                    'member_of': university_gst._id,
                    'group_set': mis_admin._id,
                    'relation_set.organization_belongs_to_state': state_gs._id
                },
                {
                    'name': 1,
                    'relation_set.affiliated_college': 1
                }
            ).sort('name', 1)

            student_gst = collection.Node.one(
                {'_type': "GSystemType", 'name': "Student"}
            )

            university_wise_data = {}
            # Fetching university-wise data
            for each_univ in university_cur:
                university_wise_data[each_univ.name] = {}

                # Fetching college(s) affiliated to given university
                colleges_id_list = []
                for rel in each_univ.relation_set:
                    if rel and "affiliated_college" in rel:
                        colleges_id_list = rel["affiliated_college"]
                        break

                # Fetching college-wise data
                college_cur = collection.Node.find(
                    {'_id': {'$in': colleges_id_list}}
                ).sort('name', 1)

                for each_college in college_cur:
                    university_wise_data[each_univ.name][each_college.name] = {}
                    rec = collection.aggregate([
                        {
                            '$match': {
                                'member_of': student_gst._id,
                                'relation_set.student_belongs_to_college': each_college._id,
                                # 'attribute_set.registration_date': {
                                #     '$gte': date_gte, '$lte': date_lte
                                # },
                                'status': u"PUBLISHED"
                            }
                        },
                        {
                            '$group': {
                                '_id': {
                                    'College': '$each_college.name',
                                    'Degree Year': '$attribute_set.degree_year'
                                },
                                'No of students': {'$sum': 1}
                            }
                        }
                    ])

                    data = {}
                    for res in rec["result"]:
                        if res["_id"]["Degree Year"]:
                            data[res["_id"]["Degree Year"][0]] = \
                                res["No of students"]

                    if "I" not in data:
                        data["I"] = 0
                    if "II" not in data:
                        data["II"] = 0
                    if "III" not in data:
                        data["III"] = 0

                    data["Total"] = data["I"] + data["II"] + data["III"]

                    university_wise_data[each_univ.name][each_college.name] = data

            response_dict["success"] = True
            response_dict["university_wise_data"] = university_wise_data
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
                                                'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte},
                                                'status': u"PUBLISHED"
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
        "Gaya College": ["Ms. Rishvana Sheik"],
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
        "Nirmala College": [],
        "Ranchi College": [],
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
          if row[u"College"] not in PO or not PO[row[u"College"]]:
            row[u"Program Officer"] = "Not assigned yet"
          else:
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
    This view returns list of NUSSD-Course(s) belonging to given course type.

    Arguments:
    group_id - ObjectId of the currently selected group
    nussd_course_type - Type of NUSSD Course

    Returns:
    A dictionary consisting of following key-value pairs:-
    success - Boolean giving the state of ajax call
    message - Basestring giving the error/information message
    unset_nc - dictionary consisting of NUSSD-Course(s)
    """
    response_dict = {'success': False, 'message': ""}

    try:
        if request.is_ajax() and request.method == "GET":
            # Fetch field(s) from GET object
            nussd_course_type = request.GET.get("nussd_course_type", "")

            # Check whether any field has missing value or not
            if nussd_course_type == "":
                error_message = "Invalid data: No data found in any of the " \
                    + "field(s)!!!"
                raise Exception(error_message)

            # Fetch "Announced Course" GSystemType
            mis_admin = collection.Node.one(
                {'_type': "Group", 'name': "MIS_admin"},
                {'name': 1}
            )
            if not mis_admin:
                # If not found, throw exception
                error_message = "'MIS_admin' (Group) doesn't exists... " \
                    + "Please create it first!"
                raise Exception(error_message)

            # Fetch "Announced Course" GSystemType
            nussd_course_gt = collection.Node.one(
                {'_type': "GSystemType", 'name': "NUSSD Course"}
            )
            if not nussd_course_gt:
                # If not found, throw exception
                error_message = "'NUSSD Course' (GSystemType) doesn't exists... " \
                    + "Please create it first!"
                raise Exception(error_message)

            # Type-cast fetched field(s) into their appropriate type
            nussd_course_type = unicode(nussd_course_type)

            # Fetch registered NUSSD-Courses of given type
            nc_cur = collection.Node.find(
                {
                    'member_of': nussd_course_gt._id,
                    'group_set': mis_admin._id,
                    'attribute_set.nussd_course_type': nussd_course_type
                },
                {'name': 1}
            )

            nc_dict = {}
            if nc_cur.count():
                # If found, append them to a dict
                for each in nc_cur:
                    nc_dict[str(each._id)] = each.name

                response_dict["success"] = True
                response_dict["unset_nc"] = nc_dict

            else:
                response_dict["message"] = "No " + nussd_course_type + " type of course exists." \
                    + " Please register"
                response_dict["success"] = False

            return HttpResponse(json.dumps(response_dict))

        else:
            error_message = "AnnouncedCourseError: Either not an ajax call or" \
                " not a GET request!!!"
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
    acourse_ctype_list - list consisting of announced-course(s) [if match found] and/or 
               NUSSD-Courses [if match not found]
    """
    response_dict = {'success': False, 'message': ""}
    try:
      if request.is_ajax() and request.method == "GET":
        # Fetch field(s) from GET object
        nussd_course_type = request.GET.get("nussd_course_type", "")
        acourse_ctype_list = []
        ac_of_colg = []
        # curr_date = datetime.datetime.now()

        # Fetch "Announced Course" GSystemType
        announced_course_gt = collection.Node.one({'_type': "GSystemType", 'name': "Announced Course"})
        if not announced_course_gt:
          # If not found, throw exception
          error_message = "'Announced Course' (GSystemType) doesn't exists... Please create it first!"
          raise Exception(error_message)

        mis_admin = collection.Node.one({'_type': "Group", 'name': "MIS_admin"})
        selected_course_RT = collection.Node.one({'_type': "RelationType", 'name': "selected_course"})

        if(ObjectId(group_id) == mis_admin._id):
          ac_cur = collection.Node.find(
            {'member_of': announced_course_gt._id, 'group_set':ObjectId(group_id), 'attribute_set.nussd_course_type': nussd_course_type}
          )
        else:
          colg_gst = collection.Node.one({'_type': "GSystemType", 'name': 'College'})

          # Fetch Courses announced for given college (or college group)

          # Get college node & courses announced for it from college group's ObjectId
          req_colg_id = collection.Node.one(
            {'member_of':colg_gst._id, 'relation_set.has_group': ObjectId(group_id)},
            {'relation_set.college_has_acourse': 1}
          )

          for rel in req_colg_id.relation_set:
            if rel and rel.has_key("college_has_acourse"):
              ac_of_colg = rel["college_has_acourse"]

          # Type-cast fetched field(s) into their appropriate type
          nussd_course_type = unicode(nussd_course_type)
          
          # Keeping only those announced courses which are active (i.e. PUBLISHED)
          ac_cur = collection.Node.find(
            {
              '_id': {'$in': ac_of_colg}, 'member_of': announced_course_gt._id, 
              'attribute_set.nussd_course_type': nussd_course_type,
              # 'relation_set.course_selected': {'$exists': True, '$not': {'$size': 0}},
              'status': u"PUBLISHED"
              # 'attribute_set.start_enroll':{'$lte': curr_date},
              # 'attribute_set.end_enroll':{'$gte': curr_date}
            }
          )

        if ac_cur.count():
          for each_ac in ac_cur:
            # NOTE: This ajax-call is used in various templates
            # Following is used especially only in new_create_batch.html
            # Fetch enrolled students count from announced course node's course_selected
            enrolled_stud_count = 0
            for rel in each_ac.relation_set:
              if rel and rel.has_key("course_selected"):
                enrolled_stud_count = len(rel["course_selected"])
                break

            each_ac["enrolled_stud_count"] = enrolled_stud_count
            acourse_ctype_list.append(each_ac)
          
          response_dict["success"] = True      
          info_message = "Announced Courses are available"
       
        else:
          response_dict["success"] = False
          info_message = "No Announced Courses are available"

        response_dict["message"] = info_message
        response_dict["acourse_ctype_list"] = json.dumps(acourse_ctype_list, cls=NodeJSONEncoder)

        return HttpResponse(json.dumps(response_dict))

      else:
        error_message = " AnnouncedCourseFetchError: Either not an ajax call or not a GET request!!!"
        return HttpResponse(json.dumps({'message': " AnnouncedCourseFetchError - Something went wrong in ajax call !!! \n\n Please contact system administrator."}))

    except Exception as e:
      error_message = "\n AnnouncedCourseFetchError: Either you are in user group or something went wrong!!!"
      return HttpResponse(json.dumps({'message': error_message}))


def get_colleges(request, group_id):
    """This view returns HttpResponse with following data:
      - List of college(s) affiliated to given university where
        Program Officer is not subscribed
      - List of college(s) affiliated to given university where
        Course(s) is/are already announced for given duration
      - List of college(s) affiliated to given university where
        Course(s) is/are not announced for given duration

    Arguments:
    group_id - ObjectId of the currently selected group
    univ_id - ObjectId of currently selected University
    start_time - Start time of announcement (MM/YYYY)
    end_time - End time of announcement (MM/YYYY)
    dc_courses_id_list - List of ObjectId(s) of Course(s)

    Returns:
    A dictionary consisting of following key-value pairs:-
    success - Boolean giving the state of ajax call
    message - Basestring giving the error/information message
    unassigned_PO_colg_list - List of college(s) affiliated to given university
      where Program Officer is not subscribed
    already_announced_in_colg_list - List of college(s) affiliated to given
      university where Course(s) is/are already announced for given duration
    drawer_widget - Drawer containing list of college(s) affiliated to given
      university where Course(s) is/are not announced for given duration
    """

    response_dict = {'success': False, 'message': ""}
    try:
        if request.is_ajax() and request.method == "GET":
            # Fetch field(s) from GET object
            univ_id = request.GET.get("univ_id", "")
            start_time = request.GET.get("start_time", "")
            end_time = request.GET.get("end_time", "")
            dc_courses_id_list = request.GET.getlist("dc_courses_id_list[]")
            # all_univs = request.GET.get("all_univs", "")

            # Check whether any field has missing value or not
            if univ_id == "" or start_time == "" or end_time == "":
                error_message = "Invalid data: " \
                    "No data found in any of the field(s)!!!"
                raise Exception(error_message)

            # Fetch "Announced Course" GSystemType
            mis_admin = collection.Node.one(
                {'_type': "Group", 'name': "MIS_admin"}, {'name': 1}
            )
            if not mis_admin:
                # If not found, throw exception
                error_message = "'MIS_admin' (Group) doesn't exists... " \
                    "Please create it first!"
                raise Exception(error_message)

            # Fetch all college groups
            college = collection.Node.one(
                {'_type': "GSystemType", 'name': "College"}, {'name': 1}
            )
            if not college:
                # If not found, throw exception
                error_message = "'College' (GSystemType) doesn't exists... "\
                    "Please create it first!"
                raise Exception(error_message)

            # Type-cast fetched field(s) into their appropriate type
            univ_id = ObjectId(univ_id)
            start_time = datetime.datetime.strptime(start_time, "%m/%Y")
            end_time = datetime.datetime.strptime(end_time, "%m/%Y")
            dc_courses_id_list = [ObjectId(dc) for dc in dc_courses_id_list]

            # Fetch the node of selected university
            # university_node = collection.Node.one(
            #     {'_id': univ_id},
            #     {'relation_set': 1, 'name': 1}
            # )

            # Fetch the list of colleges that are affiliated to
            # the selected university (univ_id)
            colg_under_univ_id = collection.Node.find(
                {
                    'member_of': college._id,
                    'relation_set.college_affiliated_to': univ_id
                },
                {
                    'name': 1, 'member_of': 1, 'created_by': 1,
                    'created_at': 1, 'content': 1,
                    'relation_set.has_officer_incharge': 1,
                    'relation_set.college_has_acourse': 1
                }
            ).sort('name', 1)

            list_colg = []
            unassigned_PO_colg_list = []
            already_announced_in_colg_list = []
            for each in colg_under_univ_id:
                is_PO_exists = False
                if each.relation_set:
                    for rel in each.relation_set:
                        if rel and "has_officer_incharge" in rel:
                            if rel["has_officer_incharge"]:
                                is_PO_exists = True

                        if rel and "college_has_acourse" in rel:
                            if rel["college_has_acourse"]:
                                if dc_courses_id_list:
                                    acourse_exists = collection.Node.find_one(
                                        {'_id': {'$in': rel["college_has_acourse"]}, 'relation_set.announced_for': {'$in': dc_courses_id_list}, 'attribute_set.start_time': start_time, 'attribute_set.end_time': end_time}
                                    )
                                else:
                                    acourse_exists = collection.Node.find_one(
                                        {'_id': {'$in': rel["college_has_acourse"]}, 'attribute_set.start_time': start_time, 'attribute_set.end_time': end_time}
                                    )

                                if acourse_exists:
                                    if each._id not in already_announced_in_colg_list:
                                        already_announced_in_colg_list.append(each.name)

                if each.name in already_announced_in_colg_list:
                    continue

                elif is_PO_exists:
                    if each not in list_colg:
                        list_colg.append(each)

                else:
                    if each not in unassigned_PO_colg_list:
                        unassigned_PO_colg_list.append(each.name)

            response_dict["already_announced_in_colg_list"] = \
                already_announced_in_colg_list

            response_dict["unassigned_PO_colg_list"] = unassigned_PO_colg_list

            if list_colg:
                drawer_template_context = edit_drawer_widget(
                    "RelationType", group_id, None, None,
                    checked="announced_course_create_edit",
                    left_drawer_content=list_colg
                )
                drawer_template_context["widget_for"] = \
                    "announced_course_create_edit"
                drawer_widget = render_to_string(
                    'ndf/drawer_widget.html', drawer_template_context,
                    context_instance=RequestContext(request)
                )
                response_dict["drawer_widget"] = drawer_widget
                msg_string = "Following are the list of colleges where " + \
                    "selected Course(s) should be announced:"

            else:
                msg_string = "There are no colleges under this university " + \
                    "where selected Course(s) could be announced!!!"

            # nc_dict = {}
            if colg_under_univ_id.count():
                response_dict["success"] = True
            else:
                msg_string = "No college is affiliated to under selected " + \
                    "University!!!"
                response_dict["success"] = False

            # response_dict["unset_nc"] = nc_dict
            response_dict["message"] = msg_string

            return HttpResponse(json.dumps(response_dict))

    except Exception as e:
        error_message = "CollegeFetchError: " + str(e) + "!!!"
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
      acourse_val = request.GET.getlist("acourse_val[]", "")

      for i, each in enumerate(acourse_val):
        acourse_val[i] = ObjectId(each)

      # Following parameters to be used for edit_drawer_widget()
      node = None
      checked = None

      lower_year_limit = ""
      upper_year_limit = ""

      enrolled_stud_count = 0
      non_enrolled_stud_count = 0

      colg_of_acourse_id = None

      # Check whether any field has missing value or not
      if registration_year == "" or all_students == "":
        registration_year = datetime.datetime.now().year.__str__()
        all_students = u"false"
        # error_message = "Invalid data: No data found in any of the field(s)!!!"
        # raise Exception(error_message)
      
      student = collection.Node.one({'_type': "GSystemType", 'name': "Student"})

      # From Announced Course node fetch College's ObjectId
      acourse_node = collection.Node.find_one(
        {'_id': {'$in': acourse_val}, 'relation_set.acourse_for_college': {'$exists': True}}, 
        {'attribute_set': 1, 'relation_set.acourse_for_college': 1}
      )
      for rel in acourse_node.relation_set:
        if rel:
          colg_of_acourse_id = rel["acourse_for_college"][0]
          break

      for attr in acourse_node.attribute_set:
        if attr and attr.has_key("start_time"):
          lower_year_limit = attr["start_time"].year.__str__()
        elif attr and attr.has_key("end_time"):
          upper_year_limit = attr["end_time"].year.__str__()

      if not lower_year_limit or not upper_year_limit:
        if not lower_year_limit:
          if upper_year_limit:
            lower_year_limit = upper_year_limit
          else:
            lower_year_limit = datetime.datetime.now().year.__str__()

        if not upper_year_limit:
          if lower_year_limit:
            upper_year_limit = lower_year_limit
          else:
            upper_year_limit = datetime.datetime.now().year.__str__()

      date_gte = datetime.datetime.strptime("1/1/"+lower_year_limit, "%d/%m/%Y")
      date_lte = datetime.datetime.strptime("31/12/"+upper_year_limit, "%d/%m/%Y")

      query = {
        'member_of': student._id, 
        'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte},
        'relation_set.student_belongs_to_college': ObjectId(colg_of_acourse_id)
      }

      # If College's ObjectId exists, fetch respective College's group
      if colg_of_acourse_id:
        colg_of_acourse = collection.Node.one(
          {'_id': colg_of_acourse_id, 'relation_set.has_group': {'$exists': True}},
          {'relation_set.has_group': 1}
        )

        if colg_of_acourse:
          for rel in colg_of_acourse.relation_set:
            if rel:
              # If rel exists, it means it's has_group
              # then update query
              query = {
                '$or': [
                  {
                    'member_of': student._id, 
                    'group_set': rel["has_group"][0], 
                    'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte}
                  },
                  {
                    'member_of': student._id, 
                    'relation_set.student_belongs_to_college': ObjectId(colg_of_acourse_id), 
                    'attribute_set.registration_date': {'$gte': date_gte, '$lte': date_lte}
                  }
                ]
              }
              break

      # Check whether StudentCourseEnrollment created for given acourse_val
      # Set node as StudentCourseEnrollment node
      # and checked as "has_enrolled", i.e. AT of StudentCourseEnrollment node
      sce_gst = collection.Node.one(
        {'_type': "GSystemType", 'name': "StudentCourseEnrollment"}
      )
      if sce_gst:
        sce_gs = collection.Node.one(
          {'member_of': sce_gst._id, 'relation_set.for_acourse': {'$all': acourse_val}, 'attribute_set.has_enrolled': {'$exists': True}},
          {'member_of': 1, 'attribute_set.has_enrolled': 1}
        )

        if sce_gs:
          for attr in sce_gs.attribute_set:
            if attr:
              query.update({'_id': {'$nin': attr["has_enrolled"]}})
              enrolled_stud_count = str(len(attr["has_enrolled"]))

              sce_gs.get_neighbourhood(sce_gs.member_of)
              node = sce_gs
              checked = "has_enrolled"

      drawer_template_context = {}
      drawer_widget = ""
      res = None
      if all_students == u"true":
        all_students_text = "All students (including enrolled ones)"

        res = collection.Node.find(
          query,
          {'_id': 1, 'name': 1, 'member_of': 1, 'created_by': 1, 'created_at': 1, 'content': 1}
        ).sort("name", 1)

        all_students_text += " [Count("+str(res.count())+")]"

      elif all_students == u"false":
        all_students_text = "Only non-enrolled students"

        # Find students which are not enrolled in selected announced course
        query.update({'relation_set.selected_course': {'$ne': acourse_node._id}})

        res = collection.Node.find(
          query,
          {'_id': 1, 'name': 1, 'member_of': 1, 'created_by': 1, 'created_at': 1, 'content': 1}
        ).sort("name", 1)

        non_enrolled_stud_count = str(res.count())
        all_students_text += " [Count("+non_enrolled_stud_count+")]"

      if res.count():
        drawer_template_context = edit_drawer_widget("RelationType", group_id, node, None, checked, left_drawer_content=res)
        drawer_template_context["widget_for"] = "student_enroll"
        drawer_template_context["groupid"] = group_id
        drawer_widget = render_to_string('ndf/drawer_widget.html', 
          drawer_template_context,
          context_instance = RequestContext(request)
        )

      response_dict["announced_courses"] = []
      response_dict["drawer_widget"] = drawer_widget

      response_dict["success"] = True
      # response_dict["message"] = "NOTE: " + all_students_text + " are listed along with announced courses"
      response_dict["enrolled_stud_count"] = enrolled_stud_count
      response_dict["non_enrolled_stud_count"] = non_enrolled_stud_count

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

def get_students_for_approval(request, group_id):
  """This returns data-review list of students that need approval for Course enrollment.
  """
  response_dict = {'success': False, 'message': ""}

  try:
    if request.is_ajax() and request.method == "POST":
      enrollment_id = request.POST.get("enrollment_id", "")

      sce_gst = collection.Node.one({'_type': "GSystemType", 'name': "StudentCourseEnrollment"})
      if sce_gst:
        sce_gs = collection.Node.one(
            {'_id': ObjectId(enrollment_id), 'member_of': sce_gst._id, 'group_set': ObjectId(group_id), 'status': u"PUBLISHED"},
            {'member_of': 1}
        )

        approval_nodes = []
        data = {}
        if sce_gs:
          sce_gs.get_neighbourhood(sce_gs.member_of)

          data["pk"] = str(sce_gs._id)
          data["College"] = sce_gs.for_college[0].name

          course_id_list = []
          for each in sce_gs.for_acourse:
            course_id_list.append(each._id.__str__())
          data["CourseId"] = ",".join(course_id_list)

          if len(sce_gs.for_acourse) > 1:
              # It means it's a Foundation Course's (FC) enrollment
              start_enroll = None
              end_enroll = None
              for each in sce_gs.for_acourse[0].attribute_set:
                  if not each:
                      pass
                  elif each.has_key("start_enroll"):
                      start_enroll = each["start_enroll"]
                  elif each.has_key("end_enroll"):
                      end_enroll = each["end_enroll"]

              data["Course"] = "Foundation_Course" + "_" + start_enroll.strftime("%d-%b-%Y") + "_" + end_enroll.strftime("%d-%b-%Y")

          else:
              # Courses other than FC
              data["Course"] = sce_gs.for_acourse[0].name
          
          data["CompletedOn"] =  sce_gs.completed_on
          data["Enrolled"] = len(sce_gs.has_enrolled)
          approve_task = sce_gs.has_corresponding_task[0]
          approve_task.get_neighbourhood(approve_task.member_of)
          # Code should be written in create_task: rename it create_update_task
          # Patch: doing here only
          # if data["Enrolled"] > 0:
          #   approve_task.Status = u"In Progress"
          # else:
          #   approve_task.Status = u"Resolved"
          # approve_task.save()
          data["Status"] = approve_task.Status

          if sce_gs.has_key("has_approved"):
              if sce_gs.has_approved:
                  data["Approved"] = len(sce_gs.has_approved)
              else:
                  data["Approved"] = None
          
          if sce_gs.has_key("has_rejected"):
              if sce_gs.has_rejected:
                  data["Rejected"] = len(sce_gs.has_rejected)
              else:
                  data["Rejected"] = None

          enrolled_students_list = []
          if sce_gs.has_enrolled:
            enrolled_students_list = sce_gs.has_enrolled

          approved_students_list = []
          if sce_gs.has_approved:
            approved_students_list = sce_gs.has_approved

          rejected_students_list = []
          if sce_gs.has_rejected:
            rejected_students_list = sce_gs.has_rejected

          # Update Enrolled students list
          updated_enrolled_students_list = []
          for each_id in enrolled_students_list:
            if (each_id not in approved_students_list) and (each_id not in rejected_students_list):
              updated_enrolled_students_list.append(each_id)
          
          enrollment_columns = ["Name", "Reg#", "Degree", "Year"]
          for each_id in updated_enrolled_students_list:
            n = collection.Node.one({'_id': ObjectId(each_id)}, {'name': 1, 'member_of': 1})
            n.get_neighbourhood(n.member_of)
            nn = {}
            nn["_id"] = n._id
            nn["Name"] = n.name
            nn["Reg#"] = n.registration_date
            nn["Degree"] = n.degree_name
            nn["Year"] = n.degree_year
            approval_nodes.append(nn)

          half_count = len(approval_nodes) / 2
          approval_list = render_to_string('ndf/approval_data_review.html', 
            {
              'groupid': group_id, 'group_id': group_id,
              'enrollment_details': data, 'enrollment_columns': enrollment_columns, 'approval_nodes': approval_nodes, 'half_count': half_count
            },
            context_instance = RequestContext(request)
          )

          response_dict["success"] = True
          response_dict["approval_data_review"] = approval_list

          return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

  except Exception as e:
    error_message = "StudentCourseApprovalError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

def approve_students(request, group_id):
  """This returns approved and/or rejected students count respectively.
  """
  try:
    response_dict = {'success': False, 'message': ""}

    if request.is_ajax() and request.method == "POST":
      approval_state = request.POST.get("approval_state", "")
      enrollment_id = request.POST.get("enrollment_id", "")

      course_id = request.POST.get("course_id", "")
      course_id = [ObjectId(each.strip()) for each in course_id.split(",")]

      students_selected = request.POST.getlist("students_selected[]", "")

      sce_gs = collection.Node.one(
        {'_id': ObjectId(enrollment_id), 'group_set': ObjectId(group_id), 'relation_set.has_corresponding_task': {'$exists': True}, 'status': u"PUBLISHED"},
        {'name': 1, 'member_of': 1, 'attribute_set': 1, 'relation_set.has_corresponding_task': 1}
      )

      selected_course_RT = collection.Node.one({'_type': "RelationType", 'name': "selected_course"})

      remaining_count = None
      enrolled_list = []
      approved_list = []
      rejected_list = []
      for attr in sce_gs.attribute_set:
        if attr.has_key("has_enrolled"):
          enrolled_list = attr["has_enrolled"]

        elif attr.has_key("has_approved"):
          approved_list = attr["has_approved"]
        
        elif attr.has_key("has_rejected"):
          rejected_list = attr["has_rejected"]

      if approval_state == "Approve":
        has_approved_AT = collection.Node.one(
          {'_type': "AttributeType", 'name': "has_approved"}
        )
        for each in students_selected:
          student_id = ObjectId(each)

          stud_node = collection.Node.one({'_id': student_id}, {'relation_set.selected_course': 1})
          ex_course_id = []
          for each in stud_node.relation_set:
            if each and each.has_key("selected_course"):
              ex_course_id = each["selected_course"]
              break
          new_course_id = list(set(ex_course_id + course_id))
          rel_node = create_grelation(student_id, selected_course_RT, new_course_id)

          if rel_node:
            if student_id not in approved_list:
              approved_list.append(student_id)
        
        attr_node = create_gattribute(ObjectId(enrollment_id), has_approved_AT, approved_list)

      elif approval_state == "Reject":
        has_rejected_AT = collection.Node.one(
          {'_type': "AttributeType", 'name': "has_rejected"}
        )
        for each in students_selected:
          student_id = ObjectId(each)

          if student_id not in rejected_list:
            rejected_list.append(student_id)

        attr_node = create_gattribute(ObjectId(enrollment_id), has_rejected_AT, rejected_list)

      enrolled_count = len(enrolled_list)
      approved_count = len(approved_list)
      rejected_count = len(rejected_list)
      remaining_count = enrolled_count - (approved_count + rejected_count)
      task_status = u"New"

      if remaining_count == 0:
        if enrolled_count == (approved_count + rejected_count):
          for rel in sce_gs.relation_set:
            if rel and ("has_corresponding_task" in rel):
              Status_AT = collection.Node.one(
                {'_type': "AttributeType", 'name': "Status"}
              )
              task_status = u"Closed"
              attr_node = create_gattribute(rel["has_corresponding_task"][0], Status_AT, task_status)
              break

      else:
        for rel in sce_gs.relation_set:
          if rel and ("has_corresponding_task" in rel):
            Status_AT = collection.Node.one(
              {'_type': "AttributeType", 'name': "Status"}
            )
            task_status = u"In Progress"
            attr_node = create_gattribute(rel["has_corresponding_task"][0], Status_AT, task_status)
            break

      response_dict["success"] = True
      response_dict["enrolled"] = enrolled_count
      response_dict["approved"] = approved_count
      response_dict["rejected"] = rejected_count
      response_dict["remaining"] = remaining_count
      response_dict["task_status"] = task_status

      return HttpResponse(json.dumps(response_dict, cls=NodeJSONEncoder))

  except Exception as e:
    error_message = "ApproveStudentsError: " + str(e) + "!!!"
    response_dict["message"] = error_message
    return HttpResponse(json.dumps(response_dict))

def get_students_for_batches(request, group_id):
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
  b_arr=[]
  try:
    if request.is_ajax() and request.method == "GET":
      btn_id = request.GET.get('btn_id', "")
      batch_id = request.GET.get('node_id', "")
      ac_id = request.GET.get('ac_id', "")

      batch_name_index = 1
      batches_for_same_course = []
      all_batches_in_grp = []
      batch_mem_dict = {}
      batch_member_list = []
      
      batch_gst = collection.Node.one({'_type':"GSystemType", 'name':"Batch"})
      batch_for_group = collection.Node.find({'member_of': batch_gst._id, 'relation_set.has_course': ObjectId(ac_id)})
      for each1 in batch_for_group:
        existing_batch = collection.Node.one({'_id': ObjectId(each1._id)})
        batch_name_index += 1
        for each2 in each1.relation_set:
          if each2.has_key("has_batch_member"):
            batch_member_list.extend(each2['has_batch_member'])
            break
        each1.get_neighbourhood(each1.member_of)
        batch_mem_dict[each1.name] = each1
      
      # College's ObjectId is required, if student record can't be found 
      # using group's ObjectId
      # A use-case where records created via csv file apends MIS_admin group's 
      # ObjectId in group_set field & not college-group's ObjectId
      ann_course = collection.Node.one({'_id': ObjectId(ac_id)}, {'relation_set.acourse_for_college': 1})
      college_id = None
      for rel in ann_course.relation_set:
        if rel and rel.has_key("acourse_for_college"):
          college_id = rel["acourse_for_college"][0]
          break

      student = collection.Node.one({'_type': "GSystemType", 'name': "Student"})
      res = collection.Node.find(
        {
          '_id': {'$nin': batch_member_list},
          'member_of': student._id,
          # '$or': [
          #   {'group_set': ObjectId(group_id)},
          #   {'relation_set.student_belongs_to_college': college_id}
          # ],
          'relation_set.selected_course': ObjectId(ac_id)
        },
        {'_id': 1, 'name': 1, 'member_of': 1, 'created_by': 1, 'created_at': 1, 'content': 1}
      ).sort("name", 1) 

      drawer_template_context = edit_drawer_widget("RelationType", group_id, None, None, None, left_drawer_content=res)
      drawer_template_context["widget_for"] = "new_create_batch"
      drawer_widget = render_to_string(
        'ndf/drawer_widget.html', 
        drawer_template_context,
        context_instance = RequestContext(request)
      )

      response_dict["success"] = True
      response_dict["drawer_widget"] = drawer_widget
      response_dict["student_count"] = res.count()
      response_dict["batch_name_index"] = batch_name_index
      response_dict["batches_for_same_course"] = json.dumps(batch_mem_dict,cls=NodeJSONEncoder)

      return HttpResponse(json.dumps(response_dict))
    else:
      error_message = "Batch Drawer: Either not an ajax call or not a GET request!!!"
      response_dict["message"] = error_message
      return HttpResponse(json.dumps(response_dict))

  except Exception as e:
    error_message = "Batch Drawer: " + str(e) + "!!!"
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
        resource_list=collection.Node.find({'_type' : 'File', 'mime_type' : u"image/jpeg" },{'name': 1})
        resources=list(resource_list)
        n=[]
        for each in resources:
            each['_id'] =str(each['_id'])
            file_collection = db[File.collection_name]
            file_obj = file_collection.File.one({'_id':ObjectId(str(each['_id']))})
            if file_obj.fs_file_ids:
                grid_fs_obj =  file_obj.fs.files.get(file_obj.fs_file_ids[0])
                each['fname']=grid_fs_obj.filename
                each['name'] = each['name']
            n.append(each)
        return StreamingHttpResponse(json.dumps(n))
    


# =============================================================================
def close_event(request,group_id,node):
    reschedule_event=collection.Node.one({"_type":"AttributeType","name":"event_edit_reschedule"})
    create_gattribute(ObjectId(node),reschedule_event,{"reschedule_till":datetime.datetime.today(),"reschedule_allow":False})

    return HttpResponse("event closed") 

def reschedule_task(request,group_id,node):
 task_dict={}
 #name of the programe officer who has initiated this task
 '''Required keys: _id[optional], name, group_set, created_by, modified_by, contributors, content_org,
        created_by_name, Status, Priority, start_time, end_time, Assignee, has_type
 '''
 
 task_groupset=collection.Node.one({"_type":"Group","name":"MIS_admin"})
 
 a=[]
 b=[]
 c=[]
 listing=task_groupset.group_admin
 listing.append(1)
 return_message=""
 values=[]
 if request.user.id in listing:
    reschedule_attendance=collection.Node.one({"_type":"AttributeType","name":"reschedule_attendance"})
    marks_entry_completed=collection.Node.find({"_type":"AttributeType","name":"marks_entry_completed"})
    reschedule_type = request.POST.get('reschedule_type','')
    end_time=collection.Node.one({"name":"end_time"})
    from datetime import date,time,timedelta
    date1=datetime.date.today() + timedelta(2)
    ti=datetime.time(0,0)
    b=datetime.datetime.combine(date1,ti)
    #fetch event
    event_node = collection.Node.one({"_id":ObjectId(node)})
    reschedule_dates = []
    
    if  reschedule_type == 'event_reschedule' :
         for i in event_node.attribute_set:
	       if unicode('event_edit_reschedule') in i.keys():
	    	   if unicode ('reschedule_dates') in i['event_edit_reschedule']:
	    	   	  reschedule_dates = i['event_edit_reschedule']['reschedule_dates']

         reschedule_dates.append(b)
         reschedule_event=collection.Node.one({"_type":"AttributeType","name":"event_edit_reschedule"})
         create_gattribute(ObjectId(node),reschedule_event,{"reschedule_till":b,"reschedule_allow":True,"reschedule_dates":reschedule_dates})  
         return_message = "Event Dates Re-Schedule Opened" 

    else:
    	 for i in event_node.attribute_set:
	       if unicode('reschedule_attendance') in i.keys():
	    	   if unicode ('reschedule_dates') in i['reschedule_attendance']:
	    	   	  reschedule_dates = i['reschedule_attendance']['reschedule_dates']
         reschedule_dates.append(b)
         create_gattribute(ObjectId(node),reschedule_attendance,{"reschedule_till":b,"reschedule_allow":True,"reschedule_dates":reschedule_dates})
         create_gattribute(ObjectId(node),marks_entry_completed[0],True)
         return_message="Event Re-scheduled."
 else:
    Mis_admin=collection.Node.find({"name":"MIS_admin"})
    Mis_admin_list=Mis_admin[0].group_admin
    Mis_admin_list.append(Mis_admin[0].created_by)
    path=request.POST.get('path','')
    site = Site.objects.get(pk=1)
    site = site.name.__str__()
    event_reschedule_link = "http://" + site + path
    b.append(task_groupset._id)
    glist_gst = collection.Node.one({'_type': "GSystemType", 'name': "GList"})
    task_type = collection.Node.one({'member_of': glist_gst._id, 'name':"Re-schedule Event"})._id
    task_dict.update({"has_type" : task_type})
    task_dict.update({'name':unicode('Reschedule Task')})
    task_dict.update({'group_set':b})
    task_dict.update({'created_by':request.user.id})
    task_dict.update({'modified_by':request.user.id})
    task_dict.update({'content_org':unicode("Please Re-Schedule the Following event"+"   \t " "\n- Please click [[" + event_reschedule_link + "][here]] to reschedule event")})
    task_dict.update({'created_by_name':request.user.username})
    task_dict.update({'Status':unicode("New")}) 
    task_dict.update({'Priority':unicode('Normal')})
    date1=datetime.date.today()
    ti=datetime.time(0,0)
    Today=datetime.datetime.combine(date1,ti)
    task_dict.update({'start_time':Today})
    task_dict.update({'Assignee':Mis_admin_list})
    create_task(task_dict)
    return_message="Intimation is sent to central office soon you will get update."
 return HttpResponse(return_message)
 

def event_assginee(request, group_id, app_set_instance_id=None):
 Event=   request.POST.getlist("Event","")
 
 Event_attended_by=request.POST.getlist("Event_attended_by[]","")
 
 marks=request.POST.getlist("marks","")
 
 assessmentdone=request.POST.get("assessmentdone","") 
 
 oid=collection.Node.find_one({"_type" : "RelationType","name":"has_attended"})
 
 Assignment_rel=collection.Node.find({"_type":"AttributeType","name":"Assignment_marks_record"})
 
 Assessmentmarks_rel=collection.Node.find({"_type":"AttributeType","name":"Assessment_marks_record"})
 
 performance_record=collection.Node.find({"_type":"AttributeType","name":"performance_record"})
 
 student_details=collection.Node.find({"_type":"AttributeType","name":"attendance_record"})
 
 marks_entry_completed=collection.Node.find({"_type":"AttributeType","name":"marks_entry_completed"})
 
 #code for saving Attendance and Assesment of Assignment And Assesment Session
 attendedlist=[]
 
 for info in Event_attended_by:
     a=ast.literal_eval(info)
     if (a['Name'] != 'undefined'):
      student_dict={}
      if (a['save'] == '2' or a['save'] == '3'):
        student_dict.update({"marks":a['Attendance_marks'],'Event':ObjectId(Event[0])})
        create_gattribute(ObjectId(a['Name']),Assignment_rel[0], student_dict)
      if(a['save'] == '2' or  a['save'] == '4'):
        student_dict.update({"marks":a['Assessment_marks'],'Event':ObjectId(Event[0])})
        create_gattribute(ObjectId(a['Name']),Assessmentmarks_rel[0], student_dict)
      if(a['save'] == '5'):
        student_dict.update({"marks":a['Assessment_marks'],'Event':ObjectId(Event[0])})
        create_gattribute(ObjectId(a['Name']),performance_record[0], student_dict)
      create_gattribute(ObjectId(a['Name']),student_details[0],{"atandance":a['Presence'],'Event':ObjectId(Event[0])})
      if(a['Presence'] == 'True'):
          attendedlist.append(a['Name'])

 if assessmentdone == 'True':
     create_gattribute(ObjectId(app_set_instance_id),marks_entry_completed[0],False)
 create_grelation(ObjectId(app_set_instance_id), oid,attendedlist)
 
 
 return HttpResponse("Details Entered")  
        
def fetch_course_name(request, group_id,Course_type):
  courses=collection.Node.find({"attribute_set.nussd_course_type":unicode(Course_type)})
  
  course_detail={}
  course_list=[]
  for i in courses:
    course_detail.update({"name":i.name})
    course_detail.update({"id":str(i._id)})
    course_list.append(course_detail)
    course_detail={}
    
  return HttpResponse(json.dumps(course_list))
  
def fetch_course_Module(request, group_id,Course_name):
  courses=collection.Node.find({"_id":ObjectId(Course_name)},{'relation_set.announced_for':1})
  courses=collection.Node.find({"_id":ObjectId(courses[0]['relation_set'][0]['announced_for'][0])})
  trainers=collection.Node.find({"relation_set.trainer_of_course":ObjectId(Course_name)})
  superdict={}
  module_Detail={}
  module_list=[]
  course_modules=collection.Node.find({"_id":{'$in':courses[0].collection_set}})
  for i in course_modules:
    module_Detail.update({"name":i.name})
    module_Detail.update({"id":str(i._id)})
    module_list.append(module_Detail)
    module_Detail={}
  
  trainerlist=[]
  trainer_detail={}
  for i in trainers:
    trainer_detail.update({"name":i.name})
    trainer_detail.update({"id":str(i._id)})
    trainerlist.append(trainer_detail)
    trainer_detail={}
  superdict['Module']=json.dumps(module_list,cls=NodeJSONEncoder)    
  superdict['trainer'] = json.dumps(trainerlist,cls=NodeJSONEncoder) 
  return HttpResponse(json.dumps(superdict))

def fetch_batch_student(request, group_id,Course_name):
  try:
    courses=collection.Node.find({"_id":ObjectId(Course_name)},{'relation_set.has_batch_member':1})
    dict1={}
    list1=[]
    a = courses[0].relation_set[0]
    for i in a['has_batch_member']:
     dict1.update({"id":str(i)})
     list1.append(dict1)
     dict1={}
    return HttpResponse(json.dumps(list1))
  except:
    return HttpResponse(json.dumps(list1)) 
def fetch_course_session(request, group_id,Course_name):
  courses=collection.Node.find({"_id":ObjectId(Course_name)})
  dict1={}
  list1=[]
  event_type_id=request.GET.get("app_set_id","")
  event_type_node=collection.Node.one({"_id":ObjectId(event_type_id)})
  
  course_modules=collection.Node.find({"_id":{'$in':courses[0].collection_set}})    
  for i in course_modules:
      dict1.update({"name":i.name})
      dict1.update({"id":str(i._id)})
      for j in i.attribute_set:
          if "course_structure_minutes" in j.keys()  :
              dict1.update({"minutes":str(j["course_structure_minutes"])})
      list1.append(dict1)
      dict1={}
  return HttpResponse(json.dumps(list1))
    
  

def fetch_course_batches(request, group_id,Course_name):
  #courses=collection.Node.one({"_id":ObjectId(Course_name)})
  #courses=collection.Node.find({"relation_set.announced_for":ObjectId(Course_name)})
  try:
    dict1={}
    list1=[]
    batch=collection.Node.find({"_type":"GSystemType","name":"Batch"})
    batches=collection.Node.find({"member_of":batch[0]._id,"relation_set.has_course":ObjectId(Course_name)})
    for i in batches:
        dict1.update({"name":i.name})
        dict1.update({"id":str(i._id)})
        list1.append(dict1)
        dict1={}
    
    return HttpResponse(json.dumps(list1))
  except:
    return HttpResponse(json.dumps(list1))

def save_csv(request,group_id,app_set_instance_id=None):
        #column_header = [u'Name', 'Presence','Attendance_marks','Assessment_marks']
        json_data=request.POST.getlist("attendance[]","")
        column_header=request.POST.getlist("column[]","")
        t = time.strftime("%c").replace(":", "_").replace(" ", "_")
        filename = "csv/" + "Attendance_data_" + t + ".csv"
        filepath = os.path.join(STATIC_ROOT, filename)
        filedir = os.path.dirname(filepath)
        if not os.path.exists(filedir):
          os.makedirs(filedir)
        data={}
        with open(filepath, 'wb') as csv_file:
          fw = csv.DictWriter(csv_file, delimiter=',', fieldnames=column_header)
          fw.writerow(dict((col,col) for col in column_header))
          
          for row in list(json_data):
            v = {}
            fw.writerow(ast.literal_eval(row))
        return HttpResponse((STATIC_URL + filename))
        
def get_assessment(request,group_id,app_set_instance_id):
    node = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    node.get_neighbourhood(node.member_of)
    marks_list=[]
    Assesslist=[]
    val=False
    for i in node.has_attendees:
       dict1={}
       dict1.update({'name':i.name})
       for j in  i.attribute_set:
            if  j.keys()[0] == 'performance_record':
               if (str(j['performance_record']['Event']) == str(app_set_instance_id)) is True:
                  val=True
                  dict1.update({'marks':j['performance_record']['marks']})
               else:
                  dict1.update({'marks':""})
                   
       dict1.update({'id':str(i._id)})
       if val is True:
             marks_list.append(dict1)
       else:
             dict1.update({'marks':"0"})
             marks_list.append(dict1)      
   
    return HttpResponse(json.dumps(marks_list))
def get_attendees(request,group_id,node):
 #get all the ObjectId of the people who would attend the event
 node=collection.Node.one({'_id':ObjectId(node)})
 attendieslist=[]
 #below code would give the the Object Id of Possible attendies
 for i in node.relation_set:
     if ('has_attendees' in i): 
        for j in  i['has_attendees']:
                attendieslist.append(j)
                
 attendee_name=[]
 #below code is meant for if a batch or member of group id  is found, fetch the attendees list-
 #from the members of the batches if members are selected from the interface their names would be returned
 #attendees_id=collection.Node.find({ '_id':{'$in': attendieslist}},{"group_admin":1})
 attendees_id=collection.Node.find({ '_id':{'$in': attendieslist}})
 for i in attendees_id:
    #if i["group_admin"]:
    #  User_info=(collectigeton.Node.find({'_type':"Author",'created_by':{'$in':i["group_admin"]}}))
    #else:
    User_info=(collection.Node.find({'_id':ObjectId(i._id)}))
    for i in User_info:
       attendee_name.append(i)
 attendee_name_list=[]
 for i in attendee_name:
    if i not in attendee_name_list:
        attendee_name_list.append(i)
 a=[]
 d={}
 for i in attendee_name_list:
    d={}
    d.update({'name':i.name})
    d.update({'id':str(i._id)})
    a.append(d)
    
    
 return HttpResponse(json.dumps(a))
 
def get_attendance(request,group_id,node):
 #method is written to get the presence and absence of attendees for the event
 node=collection.Node.one({'_id':ObjectId(node)})
 attendieslist=[]
 #below code would give the the Object Id of Possible attendies
 for i in node.relation_set:
     if ('has_attendees' in i): 
        for j in  i['has_attendees']:
                attendieslist.append(j)
                
 attendee_name=[]
 attendees_id=collection.Node.find({ '_id':{'$in': attendieslist}})
 for i in attendees_id:
    #if i["group_admin"]:
    #  User_info=(collection.Node.find({'_type':"Author",'created_by':{'$in':i["group_admin"]}}))
    #else:
    User_info=(collection.Node.find({'_id':ObjectId(i._id)}))
    for i in User_info:
       attendee_name.append(i)
 attendee_name_list=[]
 for i in attendee_name:
    if i not in attendee_name_list:
        attendee_name_list.append(i)
 a=[]
 d={}
 
 has_attended_event=collection.Node.find({'_id':ObjectId(node.pk)},{'relation_set':1})
 #get all the objectid
 attendieslist=[]
 for i in has_attended_event[0].relation_set:
     if ('has_attended' in i):
           for j in  i['has_attended']:
                attendieslist.append(j)
 #create the table
 count=0
 attendance=[]
 temp_attendance={}
 #the below code would compare between the supposed attendees and has_attended the event
 #and accordingly mark their presence or absence for the event
  
 node.get_neighbourhood(node.member_of)
 Assess_marks_list=[]
 Assign_marks_list=[]
 Assesslist=[]
 marks_list=[]
 val=False
 assign=False
 asses=False
 member_of=collection.Node.one({"_id":{'$in':node.member_of}})
 for i in attendee_name_list:
    if (i._id in attendieslist):
      attendees=collection.Node.one({"_id":ObjectId(i._id)})
      dict1={}
      dict2={}
      for j in  attendees.attribute_set:
         if member_of.name != "Exam":
            if   unicode('Assignment_marks_record') in j.keys():
               if (str(j['Assignment_marks_record']['Event']) == str(node._id)) is True:
                  val=True
                  assign=True
                  dict1.update({'marks':j['Assignment_marks_record']['marks']})
               else:
                  dict1.update({'marks':"0"})
            if  unicode('Assessment_marks_record') in j.keys():
               if(str(j['Assessment_marks_record']['Event']) == str(node._id)) is True:
                  val=True
                  asses=True
                  dict2.update({'marks':j['Assessment_marks_record']['marks']})
               else:
                  dict2.update({'marks':"0"})
         if member_of.name == "Exam":
            dict1.update({'marks':"0"})
            if  unicode('performance_record') in j.keys():
               if(str(j['performance_record']['Event']) == str(node._id)) is True:
                  val=True
                  asses=True
                  dict2.update({'marks':j['performance_record']['marks']}) 
               else:
                  dict2.update({'marks':"0"})               
      temp_attendance.update({'id':str(i._id)})
      temp_attendance.update({'name':i.name})
      temp_attendance.update({'presence':'Present'})
      if dict1.has_key('marks'):
        temp_attendance.update({'Assignment_marks':dict1['marks']})
      if dict2.has_key('marks'):
        temp_attendance.update({'Assessment_marks':dict2['marks']})
      attendance.append(temp_attendance)
    else:
      temp_attendance.update({'id':str(i._id)})
      temp_attendance.update({'name':i.name})
      temp_attendance.update({'presence':'Absent'})
      temp_attendance.update({'Assignment_marks':"0"})
      temp_attendance.update({'Assessment_marks':"0"})
      attendance.append(temp_attendance) 
    temp_attendance={}
 return HttpResponse(json.dumps(attendance))
 
def attendees_relations(request,group_id,node):
 event_has_attended=collection.Node.find({'_id':ObjectId(node)})
 column_list=[]
 column_count=0
 course_assignment=False
 course_assessment=False
 member_of=collection.Node.one({"_id":{'$in':event_has_attended[0].member_of}})
 if member_of.name != "Exam":
   for i in event_has_attended[0].relation_set:
      #True if (has_attended relation is their means attendance is already taken) 
      #False (signifies attendence is not taken yet for the event)
      if ('has_attended' in i):
        a = "True"
      else:
        a = "False"   
      if ('session_of' in i):
         session=collection.Node.one({"_id":{'$in':i['session_of']}})
         for i in session.attribute_set:
              if unicode('course_structure_assignment') in i:   
               if i['course_structure_assignment'] == True:
                  course_assignment=True
              if unicode('course_structure_assessment') in i:    
               if i['course_structure_assessment'] == True:
                  course_assessment=True
                  
   # meaning of the numbers 
   #2 :- populate both assesment and assignment marks columns
   #3 :- popuplate only Asssignment marks Columns
   #4 :- populate only Assesment marks Columns
   #1 :- populate Only Attendance taking part donot populate Assesment and Attendance taking part
   reschedule =True
   marks =True
   if course_assessment == True:
     column_count = 4
   if course_assignment == True:
     column_count = 3
   if (course_assessment == True and course_assignment == True):
     column_count = 2
   if (course_assignment == False and course_assessment == False):                        
     column_count = 1
   column_list.append(a)
   column_list.append(column_count)  
 else:
   column_count=5
   column_list.append('True')
   column_list.append(column_count) 
 node = collection.Node.one({"_id":ObjectId(node)}) 
 for i in node.relation_set:
        if unicode("session_of") in i.keys():
           session_id = collection.Node.one({"_id":i['session_of'][0]}) 
           for j in session_id.attribute_set:
              if unicode('course_structure_assignment') in j:   
                 if j['course_structure_assignment'] == True:
                     marks_enter=True
              if unicode('course_structure_assessment') in j:    
                 if j['course_structure_assessment'] == True:
                     marks_enter=True
 for i in node.attribute_set:
    if unicode("reschedule_attendance") in i.keys():
      if unicode('reschedule_allow') in i['reschedule_attendance']: 
       reschedule=i['reschedule_attendance']['reschedule_allow'] 
    if unicode("marks_entry_completed") in i.keys():
        marks=i["marks_entry_completed"]
 column_list.append(reschedule)
 column_list.append(marks)
 return HttpResponse(json.dumps(column_list)) 

        
def page_scroll(request,group_id,page):
  
 Group_Activity = collection.Node.find(
        {'group_set':ObjectId(group_id)}).sort('last_update', -1)
 
 if Group_Activity.count() >=10:
  paged_resources = Paginator(Group_Activity,10)
 else:
  paged_resources = Paginator(Group_Activity,Group_Activity.count()) 
 files_list = []
 user_activity = []
 tot_page=paged_resources.num_pages
 if int(page) <= int(tot_page):
    if int(page)==1:
       page='1'  
    if int(page) != int(tot_page) and int(page) != int(1):
        page=int(page)+1
    for each in (paged_resources.page(int(page))).object_list:
            # print each.name,"\n"
            if each.created_by == each.modified_by :
               if each.last_update == each.created_at:
                 activity =  'created'
               else:
                 activity =  'modified'
            else:
               activity =  'created'
        
            if each._type == 'Group':
               user_activity.append(each)
            each.update({'activity':activity})
            files_list.append(each)
            
 else:
      page=0           
 
 return render_to_response('ndf/scrolldata.html', 
                                  { 'activity_list': files_list,
                                    'group_id': group_id,
                                    'groupid':group_id,
                                    'page':page
                                    # 'imageCollection':imageCollection
                                  },
                                  context_instance = RequestContext(request)
      )

def get_batches_with_acourse(request, group_id):
  """
  This view returns list of batches that match given criteria
  along with Announced-course for which match doesn't exists.

  Arguments:
  group_id - ObjectId of the currently selected group

  """
  response_dict = {'success': False, 'message': ""}
  batches_list = []
  batch_gst = collection.Node.one({'_type':'GSystemType','name':'Batch'})
  try:
    if request.is_ajax() and request.method == "GET":
      # Fetch field(s) from GET object
      announced_course_id = request.GET.get("ac_id", "")
      mis_admin = collection.Node.one({'_type': "Group", 'name': "MIS_admin"})
      if(ObjectId(group_id) == mis_admin._id):
        pass
      else:
        colg_gst = collection.Node.one({'_type': "GSystemType", 'name': 'College'})
        req_colg_id = collection.Node.one({'member_of':colg_gst._id,'relation_set.has_group':ObjectId(group_id)})
        b = collection.Node.find({'member_of':batch_gst._id,'relation_set.has_course':ObjectId(announced_course_id)})
        for each in b:
          batches_list.append(each)

        response_dict["success"] = True      
        info_message = "Batch for this course is available"
      response_dict["message"] = info_message

      
      response_dict["batches_list"] = json.dumps(batches_list, cls=NodeJSONEncoder)

      return HttpResponse(json.dumps(response_dict))

    else:
      error_message = " BatchFetchError: Either not an ajax call or not a GET request!!!"
      return HttpResponse(json.dumps({'message': " BatchCourseFetchError - Something went wrong in ajax call !!! \n\n Please contact system administrator."}))

  except Exception as e:
    error_message = "\n BatchFetchError: " + str(e) + "!!!"
    return HttpResponse(json.dumps({'message': error_message}))

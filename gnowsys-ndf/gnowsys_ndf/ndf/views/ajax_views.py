
''' -- imports from python libraries -- '''
# import os -- Keep such imports here

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


from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import check_existing_group, get_drawers, get_node_common_fields
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.mobwrite.models import ViewObj
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_profile_pic
import json
 
db = get_database()
gs_collection = db[GSystem.collection_name]
collection = db[Node.collection_name]
theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
#This function is used to check (while creating a new group) group exists or not
#This is called in the lost focus event of the group_name text box, to check the existance of group, in order to avoid duplication of group names.
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
            else:
              collection.update({'_id': shelf_gs._id}, {'$push': {'collection_set': ObjectId(shelf_item) }}, upsert=False, multi=False)
              shelf_gs.reload()

          elif shelf_item_remove:
            shelf_item = collection.Node.one({'name': unicode(shelf_item_remove)})._id
            collection.update({'_id': shelf_gs._id}, {'$pull': {'collection_set': ObjectId(shelf_item) }}, upsert=False, multi=False)      
            shelf_gs.reload()
          
          else:
            shelf_available = shelf

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
                                  { 'shelf_obj': shelf_gs,
                                    'shelf_list': shelf_list, 
                                    'shelves': shelves,
                                    'shelf_available': shelf_available,
                                    'shelf_item_available': shelf_item_available,
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
      elif field == "collection":
        if app == "Quiz":
          app = "QuizItem"
        elif app == "Theme":
          app = "Theme"
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
        if theme_GST._id in col_obj.member_of or topic_GST._id in col_obj.member_of:
          for cl in collection_list:
            if cl['id'] == node.pk:
              inner_sub_dict = {'name': col_obj.name, 'id': col_obj.pk }
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

    cur = collection.Node.find({'member_of': node._id,'group_set':ObjectId(group_id) })

    for e in cur:
      for l in e.collection_set:
        themes_list.append(l)

    cur.rewind()

    for each in cur:
      if each._id not in themes_list:
        if theme_GST._id in each.member_of or topic_GST._id in each.member_of:
          collection_list.append({'name': each.name, 'id': each.pk})
          collection_list = get_collection_list(collection_list, each)

    data = collection_list

    return HttpResponse(json.dumps(data))


def add_sub_themes(request, group_id):

  if request.is_ajax() and request.method == "POST":    

    context_node_id = request.POST.get("context_node", '')
    sub_theme_name = request.POST.get("sub_theme_name", '')
    themes_list = request.POST.get("nodes_list", '')
    themes_list = themes_list.replace("&quot;","'")
    themes_list = ast.literal_eval(themes_list)

    theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})
    context_node = collection.Node.one({'_id': ObjectId(context_node_id) })
    
    # Save the sub-theme first  
    if sub_theme_name:
      if not sub_theme_name.upper() in (theme_name.upper() for theme_name in themes_list):

        node = collection.GSystem()
        get_node_common_fields(request, node, group_id, theme_GST)
      
        node.save()
        node.reload()
        # Add this sub-theme into context nodes collection_set
        collection.update({'_id': context_node._id}, {'$push': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)
        context_node.reload()

        return HttpResponse("success")

      return HttpResponse("failure")

    return HttpResponse("None")


def add_topics(request, group_id):
  if request.is_ajax() and request.method == "POST":    
    print "\n Inside add_topics ajax view\n"
    context_node_id = request.POST.get("context_node", '')
    add_topic_name = request.POST.get("add_topic_name", '')
    topics_list = request.POST.get("nodes_list", '')
    topics_list = topics_list.replace("&quot;","'")
    topics_list = ast.literal_eval(topics_list)

    topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
    context_node = collection.Node.one({'_id': ObjectId(context_node_id) })


    # Save the topic first  
    if add_topic_name:
      print "\ntopic name: ", add_topic_name
      if not add_topic_name.upper() in (topic_name.upper() for topic_name in topics_list):
        node = collection.GSystem()
        get_node_common_fields(request, node, group_id, topic_GST)
      
        node.save()
        node.reload()        
        # Add this topic into context nodes collection_set
        collection.update({'_id': context_node._id}, {'$push': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)
        context_node.reload()

        return HttpResponse("success")

      return HttpResponse("failure")

    return HttpResponse("None")


def topic_detail_view(request, group_id):

  node_id = request.POST.get("node_id", '')
  obj = collection.Node.one({'_id': ObjectId(node_id)})
  app = collection.Node.one({'_id': ObjectId(obj.member_of[0])})
  app_id = app._id
  
  if app.name == "Topic":
    return render_to_response('ndf/node_ajax_view.html', 
                                    { 'node': obj,'app_id': app_id,
                                      'group_id': group_id,
                                      'groupid':group_id
                                    },
                                    context_instance = RequestContext(request)
    )


def node_collection(node=None, group_id=None):

    theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme'})

    if node.collection_set:
      for each in node.collection_set:
        
        each_node = collection.Node.one({'_id': ObjectId(each)})
        
        if each_node.collection_set:
          
          node_collection(each_node, group_id)
        else:
          # After deleting theme instance it's should also remove from collection_set
          cur = collection.Node.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

          for e in cur:
            if each_node._id in e.collection_set:
              collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(each_node._id) }}, upsert=False, multi=False)      


          # print "\n node ", each_node.name ,"has been deleted \n"
          each_node.delete()


      # After deleting theme instance it's should also remove from collection_set
      cur = collection.Node.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

      for e in cur:
        if node._id in e.collection_set:
          collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)      

      # print "\n node ", node.name ,"has been deleted \n"
      node.delete()

    else:

      # After deleting theme instance it's should also remove from collection_set
      cur = collection.Node.find({'member_of': {'$all': [theme_GST._id]},'group_set':{'$all': [ObjectId(group_id)]}})

      for e in cur:
        if node._id in e.collection_set:
          collection.update({'_id': e._id}, {'$pull': {'collection_set': ObjectId(node._id) }}, upsert=False, multi=False)      


      # print "\n node ", node.name ,"has been deleted \n"
      node.delete()

    return True


def delete_themes(request, group_id):
  '''delete themes objects'''
  send_dict = []
  if request.is_ajax() and request.method =="POST":
     deleteobjects = request.POST['deleteobjects']
     confirm = request.POST.get("confirm","")
  for each in  deleteobjects.split(","):
      node = collection.Node.one({ '_id': ObjectId(each)})
      # print "\n confirmed objects: ", node.name

      if confirm:
        node_collection(node, group_id)

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
  
  coll_relation = { 'relation_name':'has_collection', 'inverse_name':'member_of_collection' }

  prior_relation = { 'relation_name':'prerequisite', 'inverse_name':'is_required_for' }

  def _get_node_info(node_id):
    node = collection.Node.one( {'_id':node_id}  )
    node
    # mime_type = "true"  if node.structure.has_key('mime_type') else 'false'

    return node.name

  # def _get_username(id_int):
    # return User.objects.get(id=id_int).username

  def _get_node_url(node_id):

    node_url = '/' + str(group_id)
    node = collection.Node.one({'_id':node_id})

    if len(node.member_of) > 1:
      if node.mime_type == 'image/jpeg':
        node_url += '/image/image_detail/' + str(node_id)
      elif node.mime_type == 'video':
        node_url += '/video/video_detail/' + str(node_id)

    elif len(node.member_of) == 1:
      gapp_name = (collection.Node.one({'_id':node.member_of[0]}).name).lower()

      if gapp_name == 'forum':
        node_url += '/forum/show/' + str(node_id)

      elif gapp_name == 'file':
        node_url += '/image/image_detail/' + str(node_id)

      elif gapp_name == 'page':
        node_url += '/page/details/' + str(node_id)

      elif gapp_name == 'quiz' or 'quizitem':
        node_url += '/quiz/details/' + str(node_id)
      
    return node_url


  # page_node_id = str(id(page_node._id))
  node_metadata ='{"screen_name":"' + page_node.name + '",  "title":"' + page_node.name + '",  "_id":"'+ str(page_node._id) +'", "refType":"GSystem"}, '
  node_relations = ''
  exception_items = [
                      "name", "content", "_id", "login_required", "attribute_set",
                      "member_of", "status", "comment_enabled", "start_publication",
                      "_type", "contributors", "created_by", "modified_by", "last_update", "url", "featured",
                      "created_at", "group_set", "type_of", "content_org", "author_set",
                      "fs_file_ids", "file_size", "mime_type", "location", "language"
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
          if isinstance(each, ObjectId):
            node_name = _get_node_info(each)
            if key == "collection_set":
              inverse = coll_relation['inverse_name'] 
            elif key == "prior_node":
              inverse = prior_relation['inverse_name'] 
            else:
              inverse = ""

            node_metadata += '{"screen_name":"' + node_name + '", "title":"' + page_node.name + '", "_id":"'+ str(each) +'", "url":"'+ _get_node_url(each) +'", "refType":"Relation", "inverse":"' + inverse + '", "flag":"1"},'
            # node_metadata += '{"screen_name":"' + node_name + '", "_id":"'+ str(each) +'", "refType":"relation"},'
            node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(each) +'"},'
            i += 1
          else:
            node_metadata += '{"screen_name":"' + str(each) + '", "_id":"'+ str(each) +'_n"},'
            node_relations += '{"type":"'+ key +'", "from":"'+ key_id +'_r", "to": "'+ str(each) +'_n"},'
            i += 1
    
    else:
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
        node_metadata += '{"screen_name":"' + value + '", "_id":"'+ str(i) +'_n"},'
        node_relations += '{"type":"'+ key +'", "from":"'+ str(abs(hash(key+str(page_node._id)))) +'_r", "to": "'+ str(i) +'_n"},'
        i += 1 
    # End of if - else
  # End of for loop

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

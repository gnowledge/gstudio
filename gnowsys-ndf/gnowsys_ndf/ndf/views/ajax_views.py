''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import check_existing_group, get_drawers
from gnowsys_ndf.settings import GAPPS 
db = get_database()
gs_collection = db[GSystem.collection_name]
collection = db[Node.collection_name]

def checkgroup(request,group_name):
    titl=request.GET.get("gname","")
    retfl=check_existing_group(titl)
    if retfl:
        return HttpResponse("success")
    else:
        return HttpResponse("failure")
    


def select_drawer(request, group_name):
    
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

            drawer = get_drawers(group_name, node_id, collection_list_ids, checked)
        
            drawer1 = drawer['1']
            drawer2 = drawer['2']
                                      
            return render_to_response("ndf/drawer_widget.html", 
                                      {"widget_for": "collection",
                                       "drawer1": drawer1, 
                                       "drawer2": drawer2,
                                       "group_name": group_name
                                      },
                                      context_instance=RequestContext(request)
            )
          
        else:
            
            drawer = get_drawers(group_name, node_id, [], checked)   
       
            return render_to_response("ndf/drawer_widget.html", 
                                      {"widget_for": "collection", 
                                       "drawer1": drawer, 
                                       "group_name": group_name
                                      }, 
                                      context_instance=RequestContext(request)
            )


@login_required
def change_group_settings(request, group_name):
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
            group_id = request.POST['group_id']
            group_node = gs_collection.GSystem.one({"_id": ObjectId(group_id)})
            if group_node :
                group_node.edit_policy = edit_policy
                group_node.group_type = group_type
                group_node.subscription_policy = subscription_policy
                group_node.visibility_policy = visibility_policy
                group_node.disclosure_policy = disclosure_policy
                group_node.encryption_policy = encryption_policy
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
        dict[unicode(each._id)] = hm_obj.get_current_version(each)
        if each._id not in list_of_collection:
            list_of_collection.append(each._id)
            if each.collection_set :                                   #checking that same collection can'not be called again
                dict['collection'] = get_module_set_list(each)         #calling same function recursivaly
        list.append(dict)
    return list

#@login_required
list_of_collection = []
hm_obj = HistoryManager()
GST_MODULE = gs_collection.GSystemType.one({'name': GAPPS[8]})
def make_module_set(_id):
    '''
    This methode will create module of collection and stores objectid's with version number's
    '''
    #if request.is_ajax() and _id:
    node = collection.Node.one({'_id':ObjectId(_id)})
    list_of_collection.append(node._id)
    dict = {}
    dict[unicode(node._id)] =hm_obj.get_current_version(node)
    if node.collection_set:
        dict['collection'] = get_module_set_list(node)          #gives the list of collection with proper hierarchy as they are
    #return dict
    #creating new Gsystem object and assining data of collection object
    gsystem_obj = collection.GSystem()
    gsystem_obj.name = unicode(node.name)
    gsystem_obj.content = unicode(node.content)
    gsystem_obj.gsystem_type.append(GST_MODULE._id)
    gsystem_obj.member_of.append(unicode(GST_MODULE._id))
    gsystem_obj.created_by = 1
    gsystem_obj.module_set.append(dict)
    gsystem_obj.save()
    return "success"

    

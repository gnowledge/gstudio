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

db = get_database()
gs_collection = db[GSystem.collection_name]

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

        if node_id:
            node_id = ObjectId(node_id)
        else:
            node_id = None

        if selected_collection_list:
            selected_collection_list = selected_collection_list.split(",")
            collection_list_ids = []
        
            i = 0
            while (i < len(selected_collection_list)):
                c_name = str(selected_collection_list[i])
                c_name = c_name.replace("'", "")
                collection_list_ids.append(gs_collection.GSystem.one({'name': unicode(c_name)})._id)
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
                                       "drawer1": drawer['1'], 
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

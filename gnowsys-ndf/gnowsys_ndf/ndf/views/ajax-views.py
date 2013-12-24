''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify

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

        if selected_collection_list:
            selected_collection_list = selected_collection_list.split(",")
            collection_list_ids = []
        
            i = 0
            while (i < len(selected_collection_list)):
                c_name = str(selected_collection_list[i])
                c_name = c_name.replace("'", "")
                collection_list_ids.append(gs_collection.GSystem.one({'name': unicode(c_name)})._id)
                i = i+1

            drawer = get_drawers(group_name, None, collection_list_ids, checked)
        
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
            
            drawer = get_drawers(group_name, None, None, checked)   
       
            return render_to_response("ndf/drawer_widget.html", 
                                      {"widget_for": "collection", 
                                       "drawer1": drawer, 
                                       "group_name": group_name
                                      }, 
                                      context_instance=RequestContext(request)
            )

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
from gnowsys_ndf.ndf.views.methods import check_existing_group,get_drawers

def checkgroup(request,group_name):
    titl=request.GET.get("gname","")
    retfl=check_existing_group(titl)
    if retfl:
        return HttpResponse("success")
    else:
        return HttpResponse("failure")
    

def select_drawer(request, group_name):
    
    if request.is_ajax() and request.method == "POST":
        #homo_collection = json.loads(request.POST["hetro_collection"])
        checked = request.POST.get("homo_collection", '')
        
        print "\n=================================================\n"
        print "\n homo_collection : ", checked
        #print "\n type : ", type(homo_collection)
        
        drawer = get_drawers(None,None,checked)
        
        return render_to_response("ndf/drawer_widget.html", {"drawer1":drawer, "group_name": group_name}, 
                                      context_instance=RequestContext(request))
                   
       

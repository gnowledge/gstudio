''' -- imports from python libraries -- '''
from django.template.defaultfilters import slugify
import hashlib # for calculating md5
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response #, render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required


from gnowsys_ndf.ndf.models import *

db = get_database()
collection = db['Nodes']

def custom_app_view(request, group_id, app_name, app_id, app_set_id=None):
    """
    custom view for custom GAPPS
    """
    app_collection_set = [] 
    app = collection.Node.find_one({"_id":ObjectId(app_id)})
    app_set = ""
    for eachset in app.collection_set:
	 app_set = collection.Node.find_one({"_id":eachset})
	 app_collection_set.append({"id":str(app_set._id),"name":app_set.name}) 	
    template = "ndf/custom_template_for_app.html"
    variable = RequestContext(request, {'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set,"app_set_id":app_set_id})
    return render_to_response(template, variable)
      
 

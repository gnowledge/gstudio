''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''

from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.templatetags.ndf_tags import group_type_info


#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]


def all_observations(request, group_id, app_id=None):

	app = collection.Node.find_one({"_id":ObjectId(app_id)})
	app_name = app.name
	app_collection_set = []

	for each in app.collection_set:
		
		app_element = collection.Node.find_one({"_id":each})
		obj_count = ""
		if app_element:
			app_element_content_objects = collection.Node.find({'member_of':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
			obj_count = app_element_content_objects.count()
				
		app_collection_set.append({"id":str(app_element._id),"name":app_element.name, "obj_count": obj_count})

	# print "\napp_name : ", app_name, "\napp_set_id : ", app_set_id

	# print "\n app_collection_set : ", app_collection_set

    # if app_set_id:
    #     classtype = ""
    #     app_set_template = "yes"
    #     systemtype = collection.Node.find_one({"_id":ObjectId(app_set_id)})
    #     systemtype_name = systemtype.name
    #     title = systemtype_name
    #     if request.method=="POST":
    #         search = request.POST.get("search","")
    #         classtype = request.POST.get("class","")
    #         nodes = list(collection.Node.find({'name':{'$regex':search, '$options': 'i'},'member_of': {'$all': [systemtype._id]}}))
    #     else :
    #         nodes = list(collection.Node.find({'member_of': {'$all': [systemtype._id]},'group_set':{'$all': [ObjectId(group_id)]}}))
    #     nodes_dict = []
    #     for each in nodes:
    #         nodes_dict.append({"id":str(each._id), "name":each.name, "created_by":User.objects.get(id=each.created_by).username, "created_at":each.created_at})
    # else :
    #     app_menu = "yes"
    #     title = app_name

	return render_to_response("ndf/observations.html",
							 	{
							 		'app_collection_set': app_collection_set,
							 		'groupid':group_id, 'group_id':group_id,
							 		'app_name':app_name, 'app_id':app_id,
							 		'template_view': 'landing_page_view',
							 		'map_type': 'all_app_markers'
							 	},
							 	context_instance=RequestContext(request) 
							 )

def observations_app(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):

	user_id = int(request.user.id)  			# getting django user id
	user_name = unicode(request.user.username)  # getting django user name

	app = collection.Node.find_one({"_id":ObjectId(app_id)})
	app_name = app.name
	app_collection_set = []

	for each in app.collection_set:
		
		app_element = collection.Node.find_one({"_id":each})
		obj_count = ""
		if app_element:
			app_element_content_objects = collection.Node.find({'member_of':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
			obj_count = app_element_content_objects.count()
				
		app_collection_set.append({"id":str(app_element._id),"name":app_element.name, "obj_count": obj_count})


	return render_to_response("ndf/observations.html",
							 	{
							 		'app_collection_set': app_collection_set,
							 		'groupid':group_id, 'group_id':group_id,
							 		'app_name':app_name, 'app_id':app_id, 'app_set_id':app_set_id,
							 		'user_name':user_name, 'template_view': 'app_set_view'
							 	},
							 	context_instance=RequestContext(request) 
							 )


def save_observation(request, group_id, app_id=None, app_name=None, app_set_id=None, user_name=None):

	marker_geojson = request.POST["marker_geojson"]

	app_set = collection.Node.find_one({"_id":ObjectId(app_set_id)})
	print app_set

	return HttpResponse(json.dumps(marker_geojson))
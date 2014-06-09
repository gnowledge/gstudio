''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json, ast
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

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
	    group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
	    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    if group_ins:
	        group_id = str(group_ins._id)
	    else :
	        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
	        if auth :
	            group_id = str(auth._id)
	else :
	    pass
	if app_id is None:
	    app_ins = collection.Node.find_one({'_type':"GSystemType", "name":"Observation"})
	    if app_ins:
	        app_id = str(app_ins._id)


	app = collection.Node.find_one({"_id":ObjectId(app_id)})
	app_name = app.name
	app_collection_set = []
	file_metadata = []

	for each in app.collection_set:

		app_set_element = collection.Node.find_one({'_id':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
		
		# app_element = collection.Node.find_one({"_id":each})
		if app_set_element:

			locs = len(app_set_element.location)
			locations = app_set_element.location

			for loc in locations:
				files_list = ast.literal_eval(loc["properties"].get("attached_files", '[]'))
				
				for file_id in files_list:

					# for preventing duplicate dict forming
					if not file_id in [d['id'] for d in file_metadata]:

						file_obj = collection.Node.one({'_type':'File', "_id":ObjectId(file_id)})
						# print file_id, "===", type(file_id)
						
						temp_dict = {}
						temp_dict['id'] = file_obj._id.__str__()
						temp_dict['name'] = file_obj.name
						temp_dict['mimetype'] = file_obj.mime_type

						file_metadata.append(temp_dict)

			# app_element_content_objects = collection.Node.find({'member_of':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
			# obj_count = app_element_content_objects.count()
				
			app_collection_set.append({ 
									"id":str(app_set_element._id),
									"name":app_set_element.name,
									"locations": json.dumps(locations),
									"total_locations": locs
								  })

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

	# request.session.flush()
	request.session.set_test_cookie()

	return render_to_response("ndf/observation.html",
							 	{
							 		'app_collection_set': app_collection_set,
							 		'groupid':group_id, 'group_id':group_id,
							 		'app_name':app_name, 'app_id':app_id,
							 		'template_view': 'landing_page_view',
							 		'map_type': 'all_app_markers',
									'file_metadata':json.dumps(file_metadata)
							 	},
							 	context_instance=RequestContext(request) 
							 )

def observations_app(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
	    group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
	    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    if group_ins:
	        group_id = str(group_ins._id)
	    else :
	        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
	        if auth :
	            group_id = str(auth._id)
	else :
	    pass
	if app_id is None:
	    app_ins = collection.Node.find_one({'_type':"GSystemType", "name":"Page"})
	    if app_ins:
	        app_id = str(app_ins._id)


	client_ip = request.META['REMOTE_ADDR']
	request.session.set_test_cookie()

	# getting django user id
	user_id = int(request.user.id)  if request.user.id 	else request.session.set_expiry(0)
	user_name = unicode(request.user.username) if request.user.username  else "" # getting django user name
	

	app = collection.Node.find_one({"_id":ObjectId(app_id)})
	app_name = app.name
	app_collection_set = []
	file_metadata = []

	for each in app.collection_set:

		app_set_element = collection.Node.find_one({'_id':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
		
		# app_element = collection.Node.find_one({"_id":each})
		if app_set_element:

			locs = len(app_set_element.location)
			locations = app_set_element.location
			# file_metadata = []

			# "[{"id":"5384b8f81d41c8399153dba5","name":"sample data","mimetype":""}]"
			if unicode(each) == app_set_id:
				# file_metadata = []
				for loc in locations:
					files_list = ast.literal_eval(loc["properties"].get("attached_files", '[]'))
					
					for file_id in files_list:

						# for preventing duplicate dict forming
						if not file_id in [d['id'] for d in file_metadata]:

							file_obj = collection.Node.one({'_type':'File', "_id":ObjectId(file_id)})
							# print file_id, "===", type(file_id)
							
							temp_dict = {}
							temp_dict['id'] = file_obj._id.__str__()
							temp_dict['name'] = file_obj.name
							temp_dict['mimetype'] = file_obj.mime_type

							file_metadata.append(temp_dict)
							# print file_metadata
			
			app_collection_set.append({ 
									"id":str(app_set_element._id),
									"name":app_set_element.name,
									"locations": json.dumps(locations),
									"total_locations": locs,
									# "file_metadata":file_metadata
								  })

	
	# for each in app.collection_set:
		
	# 	app_element = collection.Node.ifnd_one({"_id":each})
	# 	obj_count = ""
	# 	if app_element:
	# 		app_element_content_objects = collection.Node.find({'member_of':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
	# 		obj_count = app_element_content_objects.count()
				
	# 	app_collection_set.append({"id":str(app_element._id),"name":app_element.name, "obj_count": obj_count})
	
	return render_to_response("ndf/observation.html",
							 	{
							 		'app_collection_set': app_collection_set,
							 		'groupid':group_id, 'group_id':group_id,
							 		'app_name':app_name, 'app_id':app_id, 'app_set_id':app_set_id, 'app_set_name_slug':slug,
							 		'user_name':user_name, 'client_ip':client_ip,
							 		'template_view': 'app_set_view',
							 		"file_metadata":json.dumps(file_metadata)
							 	},
							 	context_instance=RequestContext(request) 
							 )


def save_observation(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):
	user_type = request.POST["user"]
	user_session_id = request.POST["user_session_id"]
	marker_geojson = request.POST["marker_geojson"]
	marker_geojson = ast.literal_eval(marker_geojson)

	is_cookie_supported = request.session.test_cookie_worked()
	operation_performed = ""
	unique_token = str(ObjectId())

	app_set_element = collection.Node.find_one({'_id':ObjectId(app_set_id), 'group_set':{'$all': [ObjectId(group_id)]}})
	
	# to update existing location
	if "ref" in marker_geojson['properties']:
		marker_ref = marker_geojson['properties']['ref']

		if app_set_element:

			# for anonymous user
			anonymous_flag = False

			if (user_type == "anonymous" and is_cookie_supported):

				cookie_added_markers = request.session.get('anonymous_added_markers')

				if (cookie_added_markers != None) and (cookie_added_markers[:cookie_added_markers.find(",")] == user_session_id):
					if cookie_added_markers.find(marker_ref) > 0:
						anonymous_flag = True
					else:
						operation_performed = "You have not created this marker or you had lost your session !"
				else:
					operation_performed = "You have not created this marker or you are had lost your session !"
			else:
				operation_performed = "You have not created this marker or we think you had disabled support for cookies !"


			if (user_type == "authenticated") or anonymous_flag:
			
				for each in app_set_element.location:
					
					if each['properties']['ref'] == marker_ref:
						app_set_element.location.remove(each)
						app_set_element.location.append(marker_geojson)
						app_set_element.save()
						unique_token = marker_ref
						operation_performed = "edit"

	
	# to create/add new location
	else:

		marker_geojson['properties']['ref'] = unique_token

		if app_set_element:
			app_set_element.location.append(marker_geojson)
			app_set_element.save()
			operation_performed = "create_new"
			
		# for anonymous user
		if user_type == "anonymous" and is_cookie_supported:
			cookie_added_markers = request.session.get('anonymous_added_markers')

			if cookie_added_markers == None or cookie_added_markers[:cookie_added_markers.find(",")] != user_session_id:
				cookie_added_markers = user_session_id + "," + unique_token 

			elif cookie_added_markers[:cookie_added_markers.find(",")] == user_session_id:
				cookie_added_markers += "," + unique_token

			request.session['anonymous_added_markers'] = cookie_added_markers
			# HttpResponse.set_cookie('anonymous_added_markers', value=cookie_added_markers)
	
	# print "\n create/save :  ", request.session.items()
			
	response_data = [len(app_set_element.location), unique_token, operation_performed, str(cookie_added_markers)]
	response_data = json.dumps(response_data)

	# response = HttpResponse(response_data)
	# response.cookies['anonymous_added_markers'] = cookie_added_markers

	# return response
	return StreamingHttpResponse(response_data, {'anonymous_added_markers':cookie_added_markers})



def delete_observation(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):

	user_type = request.POST["user"]
	user_session_id = request.POST["user_session_id"]
	marker_geojson = request.POST["marker_geojson"]

	marker_geojson = ast.literal_eval(marker_geojson)
	marker_ref = marker_geojson['properties']['ref']

	is_cookie_supported = request.session.test_cookie_worked()
	operation_performed = ""

	app_set_element = collection.Node.find_one({'_id':ObjectId(app_set_id), 'group_set':{'$all': [ObjectId(group_id)]}})

	# for anonymous user
	anonymous_flag = False

	if (user_type == "anonymous" and is_cookie_supported):

		cookie_added_markers = request.session.get('anonymous_added_markers')

		if (cookie_added_markers != None) and (cookie_added_markers[:cookie_added_markers.find(",")] == user_session_id):
			if cookie_added_markers.find(marker_ref) > 0:
				anonymous_flag = True
			else:
				operation_performed = "You have not created this marker or you had lost your session !"
		else:
			operation_performed = "You have not created this marker or you had lost your session !"
	else:
		operation_performed = "You have not created this marker or we think you had disabled support for cookies !"


	if (user_type == "authenticated") or anonymous_flag:
			
		for each in app_set_element.location:
			
			if each['properties']['ref'] == marker_ref:
				app_set_element.location.remove(each)
				app_set_element.save()

				operation_performed = "marker_deleted"	

	response_data = [len(app_set_element.location), operation_performed]
	response_data = json.dumps(response_data)

	return StreamingHttpResponse(response_data)


def save_image(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):

	if request.method == "POST" :
		# for uploaded images saving
		# print "\n\n=========", request.FILES.getlist("doc[]", ""), "\n\n"
		for index, each in enumerate(request.FILES.getlist("doc[]", "")):
		    
		    fcol = db[File.collection_name]
		    fileobj = fcol.File()
		    filemd5 = hashlib.md5(each.read()).hexdigest()
		    # print "\nmd5 : ", filemd5

		    if fileobj.fs.files.exists({"md5":filemd5}):

		        coll = get_database()['fs.files']
		        a = coll.find_one({"md5":filemd5})
		        # prof_image takes the already available document of uploaded image from its md5 
		        prof_image = collection.Node.one({'_type': 'File', '_id': ObjectId(a['docid']) })
		        # print "======= ||| =====", prof_image
		    else:
			    # print "\n\n index : ", index
			    # If uploaded image is not found in gridfs stores this new image 
			    submitDoc(request, group_id)
			    
			    # prof_image takes the already available document of uploaded image from its name
			    coll = get_database()['fs.files']
			    a = coll.find_one({"md5":filemd5})
			    prof_image = collection.Node.one({'_type': 'File', '_id': ObjectId(a['docid']) })
			    # prof_image = collection.Node.one({'_type': 'File', 'name': unicode(each) })
			    # print "------------", prof_image
			    
			    # --- END of images saving
		        
		    return StreamingHttpResponse(str(prof_image._id))	

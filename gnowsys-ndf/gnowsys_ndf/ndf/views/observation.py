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
from django.contrib.auth.decorators import login_required

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.templatetags.ndf_tags import group_type_info

#######################################################################################################################################


@get_execution_time
def all_observations(request, group_id, app_id=None):

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
	    group_ins = node_collection.find_one({'_type': "Group","name": group_id})
	    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    if group_ins:
	        group_id = str(group_ins._id)
	    else :
	        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	        if auth :
	            group_id = str(auth._id)
	else :
	    pass
	if app_id is None:
	    app_ins = node_collection.find_one({'_type':"GSystemType", "name":"Observation"})
	    if app_ins:
	        app_id = str(app_ins._id)


	# app is GSystemType Observation
	app = node_collection.find_one({"_id":ObjectId(app_id)})

	app_name = app.name
	app_collection_set = []
	file_metadata = []

	# retriving each GSystemType in Observation e.g.Plant Obs.., Rain Fall etc.
	for each in app.collection_set:

		app_set_element = node_collection.find_one({'_id': ObjectId(each), 'group_set': {'$all': [ObjectId(group_id)]}})

		# Individual observations e.g. Rain Fall
		if app_set_element:

			locs = len(app_set_element.location)
			locations = app_set_element.location

			for loc in locations:

				# creating list of ObjectId's of file GSystem.
				files_list = ast.literal_eval(loc["properties"].get("attached_files", '[]'))

				for file_id in files_list: # executes only if files_list has at least ObjectId

					if ObjectId.is_valid(file_id) and file_id:

						# for preventing duplicate dict forming
						if not file_id in [d['id'] for d in file_metadata]:

							file_obj = node_collection.one({'_type': 'File', "_id": ObjectId(file_id)})
							# print file_id, "===", type(file_id)

							temp_dict = {}
							temp_dict['id'] = file_obj._id.__str__()
							temp_dict['name'] = file_obj.name
							temp_dict['mimetype'] = file_obj.mime_type

							file_metadata.append(temp_dict)

			# app_element_content_objects = node_collection.find({'member_of':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})
			# obj_count = app_element_content_objects.count()

			app_collection_set.append({
									"id":str(app_set_element._id),
									"name":app_set_element.name,
									"locations": json.dumps(locations),
									"total_locations": locs
								  })

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
@get_execution_time
def observations_app(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
	    group_ins = node_collection.find_one({'_type': "Group","name": group_id})
	    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    if group_ins:
	        group_id = str(group_ins._id)
	    else :
	        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	        if auth :
	            group_id = str(auth._id)
	else :
	    pass
	if app_id is None:
	    app_ins = node_collection.find_one({'_type':"GSystemType", "name":"Page"})
	    if app_ins:
	        app_id = str(app_ins._id)


	client_ip = request.META['REMOTE_ADDR']
	request.session.set_test_cookie()

	# getting django user id
	user_id = int(request.user.id)  if request.user.id 	else request.session.set_expiry(0)
	user_name = unicode(request.user.username) if request.user.username  else "" # getting django user name


	app = node_collection.find_one({"_id":ObjectId(app_id)})
	app_name = app.name
	app_collection_set = []
	file_metadata = []

	for each in app.collection_set:

		app_set_element = node_collection.find_one({'_id':ObjectId(each), 'group_set':{'$all': [ObjectId(group_id)]}})

		# app_element = node_collection.find_one({"_id":each})
		if app_set_element:

			locs = len(app_set_element.location)
			locations = app_set_element.location

			# file_metadata = []

			# "[{"id":"5384b8f81d41c8399153dba5","name":"sample data","mimetype":""}]"
			if unicode(each) == app_set_id:
				# file_metadata = []

				for loc in locations:

					# creating list of ObjectId's of file GSystem.
					files_list = ast.literal_eval(loc["properties"].get("attached_files", '[]'))

					for file_id in files_list: # executes only if files_list has at least ObjectId

						# check if file_id is valid ObjectId or not
						if ObjectId.is_valid(file_id) and file_id:

							# for preventing duplicate dict forming
							if not file_id in [d['id'] for d in file_metadata]:

								file_obj = node_collection.one({'_type': 'File', "_id": ObjectId(file_id)})
								# print file_id, "===", type(file_id)

								temp_dict = {}
								temp_dict['id'] = file_obj._id.__str__()
								temp_dict['name'] = file_obj.name
								temp_dict['mimetype'] = file_obj.mime_type

								file_metadata.append(temp_dict)


			app_collection_set.append({
									"id":str(app_set_element._id),
									"name":app_set_element.name,
									"locations": json.dumps(locations),
									"total_locations": locs,
									# "file_metadata":file_metadata
								  })

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

@get_execution_time
def save_observation(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):
	user_type = request.POST["user"]
	user_session_id = request.POST["user_session_id"]
	marker_geojson = request.POST["marker_geojson"]
	marker_geojson = ast.literal_eval(marker_geojson)

	is_cookie_supported = request.session.test_cookie_worked()
	operation_performed = ""
	unique_token = str(ObjectId())
        cookie_added_markers = ""

	app_set_element = node_collection.find_one({'_id': ObjectId(app_set_id), 'group_set': {'$all': [ObjectId(group_id)]}})

	# to update existing location
	if "ref" in marker_geojson['properties']:
		marker_ref = marker_geojson['properties']['ref']

		if app_set_element:

			# for anonymous user
			anonymous_flag = False

			if (user_type == "anonymous" and is_cookie_supported):

				cookie_added_markers = request.session.get('anonymous_added_markers', "")

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
						app_set_element.save(groupid=group_id)
						unique_token = marker_ref
						operation_performed = "edit"


	# to create/add new location
	else:

		marker_geojson['properties']['ref'] = unique_token

		if app_set_element:
			app_set_element.location.append(marker_geojson)
			app_set_element.save(groupid=group_id)
			operation_performed = "create_new"

		# for anonymous user
		if user_type == "anonymous" and is_cookie_supported:
			cookie_added_markers = request.session.get('anonymous_added_markers', "")

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


@get_execution_time
def delete_observation(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):

	user_type = request.POST["user"]
	user_session_id = request.POST["user_session_id"]
	marker_geojson = request.POST["marker_geojson"]

	marker_geojson = ast.literal_eval(marker_geojson)
	marker_ref = marker_geojson['properties']['ref']

	is_cookie_supported = request.session.test_cookie_worked()
	operation_performed = ""

	app_set_element = node_collection.find_one({'_id': ObjectId(app_set_id), 'group_set': {'$all': [ObjectId(group_id)]}})

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
				app_set_element.save(groupid=group_id)

				operation_performed = "marker_deleted"

	response_data = [len(app_set_element.location), operation_performed]
	response_data = json.dumps(response_data)

	return StreamingHttpResponse(response_data)

@get_execution_time
def save_image(request, group_id, app_id=None, app_name=None, app_set_id=None, slug=None):

    if request.method == "POST" :

        for index, each in enumerate(request.FILES.getlist("doc[]", "")):

            title = each.name
            userid = request.POST.get("user", "")
            content_org = request.POST.get('content_org', '')
            tags = request.POST.get('tags', "")
            img_type = request.POST.get("type", "")
            language = request.POST.get("lan", "")
            usrname = request.user.username
            page_url = request.POST.get("page_url", "")
            access_policy = request.POST.get("login-mode", '') # To add access policy(public or private) to file object

            # for storing location in the file

            # location = []
            # location.append(json.loads(request.POST.get("location", "{}")))
            # obs_image = save_file(each,title,userid,group_id, content_org, tags, img_type, language, usrname, access_policy, oid=True, location=location)

            obs_image = save_file(each,title,userid,group_id, content_org, tags, img_type, language, usrname, access_policy, oid=True)
            # Sample output of (type tuple) obs_image: (ObjectId('5357634675daa23a7a5c2900'), 'True')

            # if image sucessfully get uploaded then it's valid ObjectId
            if obs_image[0] and ObjectId.is_valid(obs_image[0]):

            	return StreamingHttpResponse(str(obs_image[0]))

            else: # file is not uploaded sucessfully or uploaded with error

            	return StreamingHttpResponse("UploadError")

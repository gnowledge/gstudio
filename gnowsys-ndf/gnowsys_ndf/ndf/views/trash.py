from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.models import node_collection
# from gnowsys_ndf.ndf.views.page import page
# from gnowsys_ndf.ndf.views.file import file
from gnowsys_ndf.ndf.views.group import *
from gnowsys_ndf.ndf.views.methods import *
from django.core.urlresolvers import reverse
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME

trash_group = node_collection.one({'_type': 'Group', "name": u"Trash"});

@get_execution_time
def trash_resource(request,group_id,node_id):
	'''
	Delete Action.
	This method removes the group_id from the node's group_set.
	Iff node's group_set is empty, send to Trash group.
	'''


	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	gst_base_unit = node_collection.one({'_type': 'GSystemType', 'name': 'base_unit'})

	node_obj = node_collection.find_one({"_id":ObjectId(node_id)})
	group_obj = node_collection.find_one({"_id":ObjectId(group_id)})
	trash_group = node_collection.find_one({"name":"Trash"});
	response_dict = {}
	response_dict['success'] = False

	if trash_group._id in node_obj.group_set:
		try:
			if node_obj._id:
				delete_node(ObjectId(node_obj._id),deletion_type=1)
				response_dict['success'] = True
		except Exception as e:
			pass
		return HttpResponse(json.dumps(response_dict))

	if ObjectId(group_id) in node_obj.group_set:
		node_obj.group_set.remove(ObjectId(group_id))
		if ObjectId(auth._id) in node_obj.group_set:
			node_obj.group_set.remove(ObjectId(auth._id))
		node_obj.save()
	if not node_obj.group_set:
		# Add Trash group _id to node_obj's group_set
		if trash_group._id not in node_obj.group_set:
			node_obj.group_set.append(trash_group._id)
		node_obj.status = u"DELETED"
	if node_obj.collection_set:
		if trash_group._id not in node_obj.group_set:
			node_obj.group_set.append(trash_group._id)
		node_obj.status = u"DELETED"
	node_obj.save()
	# print "\n\n\nnode_obj.status",node_obj.status

	# get_member_of = node_collection.find_one({"_id":{'$in':node_obj.member_of}})
	# if get_member_of.name == 'Page':
	if gst_base_unit._id in  node_obj.group_set:
		return HttpResponse("True")
	elif "Page" in node_obj.member_of_names_list and not "CourseEventGroup" in group_obj.member_of_names_list:
		return HttpResponseRedirect(reverse('page', kwargs={'group_id': group_id}))
		# return (eval('page')(request, group_id))
	elif "File" in node_obj.member_of_names_list and not "CourseEventGroup" in group_obj.member_of_names_list :
		return HttpResponse(json.dumps(response_dict))
		# elif get_member_of.name == 'File':
		# return(eval('file')(request, group_id))
	elif "CourseEventGroup" in group_obj.member_of_names_list:
		response_dict = {'success': True }
		return HttpResponse(json.dumps(response_dict))
	else:
		return HttpResponseRedirect(reverse('group_dashboard', kwargs={'group_id': group_id}))
		# return(eval('group_dashboard')(request, group_id))

@get_execution_time
# @staff_required
def delete_group(request, group_id, url_name='groupchange'):
    response_dict = {'success': False}
    group_obj = get_group_name_id(group_id, get_obj=True)
    del_s,del_msg = delete_node(group_obj._id, deletion_type=0)
    group_obj.reload()

    if 'base_unit' in group_obj.member_of_names_list and 'announced_unit' in group_obj.member_of_names_list:
      linked_modules = node_collection.find({'collection_set': group_obj._id })
      for each in linked_modules:
        each.collection_set.remove(ObjectId(group_obj._id))
        each.save()

    if trash_group._id not in group_obj.group_set:
		group_obj.group_set.append(trash_group._id)
		group_obj.save(groupid=group_obj._id)
    if del_s:
    	try:
	        return HttpResponseRedirect(reverse(url_name, kwargs={'group_id': 'home'}))
    	except:
	        return HttpResponseRedirect(reverse(url_name))


@get_execution_time
def delete_resource(request,group_id):
	# NOTE: purge of themes need to be handled differently.
	# all the collection hierarchy needs to be purged in this case.
	response_dict = {'success': False}
	node_id = request.GET.getlist('node_id','')[0]
	try:
		if node_id:
			delete_node(ObjectId(node_id),deletion_type=1)
			response_dict['success'] = True
	except Exception as e:
		pass
	return HttpResponse(json.dumps(response_dict))


@get_execution_time
def restore_resource(request, group_id):
	group_name, group_id = get_group_name_id(group_id)
	response_dict = {'success': False}
	node_id = request.GET.getlist('node_id', '')[0]
	try:
		if node_id:

			node_to_be_restore = node_collection.one({'_id': ObjectId(node_id)})
			if node_to_be_restore.snapshot.keys():

				node_to_be_restore.group_set = [ObjectId(i) for i in node_to_be_restore.snapshot.keys()]
				node_to_be_restore.status = u'PUBLISHED'
				node_to_be_restore.save(groupid=group_id)
				response_dict['success'] = True
	except Exception as e:
		pass
	return HttpResponse(json.dumps(response_dict))


@get_execution_time
def delete_multiple_resources(request,group_id):
	files_list = request.POST.getlist("collection[]", '')
	auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	group_obj = node_collection.find_one({"_id":ObjectId(group_id)})
	trash_group = node_collection.find_one({"name":"Trash"})
	files_list_obj = []
	for each in files_list:
		node_obj = node_collection.find_one({"_id":ObjectId(each)})
		if ObjectId(group_id) in node_obj.group_set:
			node_obj.group_set.remove(ObjectId(group_id))
			if ObjectId(auth._id) in node_obj.group_set:
				node_obj.group_set.remove(ObjectId(auth._id))
			node_obj.save()
		if not node_obj.group_set:
			# Add Trash group _id to node_obj's group_set
			if trash_group._id not in node_obj.group_set:
				node_obj.group_set.append(trash_group._id)
			node_obj.status = u"DELETED"
		if node_obj.collection_set:
			if trash_group._id not in node_obj.group_set:
				node_obj.group_set.append(trash_group._id)
			node_obj.status = u"DELETED"
		node_obj.save()

	return HttpResponse(json.dumps(files_list))

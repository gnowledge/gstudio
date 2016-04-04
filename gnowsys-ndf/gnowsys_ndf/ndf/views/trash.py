from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from gnowsys_ndf.ndf.models import *
# from gnowsys_ndf.ndf.views.page import page
# from gnowsys_ndf.ndf.views.file import file
from gnowsys_ndf.ndf.views.group import group_dashboard
from gnowsys_ndf.ndf.views.methods import *
from django.core.urlresolvers import reverse
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME

@get_execution_time
def trash_resource(request,group_id,node_id):
	'''
	Delete Action.
	This method removes the group_id from the node's group_set.
	Iff node's group_set is empty, send to Trash group. 
	'''

	node_obj = node_collection.find_one({"_id":ObjectId(node_id)})
	trash_group = node_collection.find_one({"name":"Trash"});
	if ObjectId(group_id) in node_obj.group_set: 		 
		node_obj.group_set.remove(ObjectId(group_id))
	if not node_obj.group_set:
		# Add Trash group _id to node_obj's group_set
		if trash_group._id not in node_obj.group_set:	
			node_obj.group_set.append(trash_group._id)
		node_obj.status = u"DELETED"
	node_obj.save()

	# get_member_of = node_collection.find_one({"_id":{'$in':node_obj.member_of}})
	# if get_member_of.name == 'Page':
	if "Page" in node_obj.member_of_names_list:
		return HttpResponseRedirect(reverse('page', kwargs={'group_id': group_id}))
		# return (eval('page')(request, group_id))
	elif "File" in node_obj.member_of_names_list:
		if GSTUDIO_SITE_NAME == "NROER":
			return HttpResponseRedirect(reverse('e-library', kwargs={'group_id': group_id}))
		return HttpResponseRedirect(reverse('file', kwargs={'group_id': group_id}))
		# elif get_member_of.name == 'File':
		# return(eval('file')(request, group_id))
	else: 
		return HttpResponseRedirect(reverse('group_dashboard', kwargs={'group_id': group_id}))
		# return(eval('group_dashboard')(request, group_id))   

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
	response_dict = {'success': False}
	node_id = request.GET.getlist('node_id', '')[0]
	try:
		if node_id:

			node_to_be_restore = node_collection.one({'_id': ObjectId(node_id)})
			# print "==========", node_to_be_restore.snapshot.keys()
			# print "\n\n node_to_be_restore === ", node_to_be_restore._id
			if node_to_be_restore.snapshot.keys():
			
				node_to_be_restore.group_set = [ObjectId(i) for i in node_to_be_restore.snapshot.keys()]
				node_to_be_restore.save()
				# print "--- ", node_to_be_restore.group_set
				response_dict['success'] = True
	except Exception as e:
		# print "\n Resore Exception ===== ", str(e)
		pass
	return HttpResponse(json.dumps(response_dict))

from django.http import HttpResponse
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.page import page
from gnowsys_ndf.ndf.views.file import file
from gnowsys_ndf.ndf.views.group import group_dashboard
from gnowsys_ndf.ndf.views.methods import *


def trash_resource(request,group_id,node_id):
 node = node_collection.find_one({"_id":ObjectId(node_id)})
 trash_node = node_collection.find_one({"name":"Trash"});
 if ObjectId(group_id) in node.group_set: 		 
	 node.group_set.remove(ObjectId(group_id))
 #fetch the tarsh group id
 if trash_node._id not in node.group_set:	
	 node.group_set.append(trash_node._id)
 node.save()
 get_member_of = node_collection.find_one({"_id":{'$in':node.member_of}})
 if get_member_of.name == 'Page':
    return (eval('page')(request, group_id))
 elif get_member_of.name == 'File':
    return(eval('file')(request, group_id))
 else: 
    return(eval('group_dashboard')(request, group_id))   
   

def delete_resource(request,group_id):
	node_id = request.GET.getlist('node_id','')[0]
	if node_id:
		delete_node(ObjectId(node_id),deletion_type=1)
	else:
		return HttpResponse("Nothing Deleted.")
	return HttpResponse("Deleted Successfully")


def restore_resource(request, group_id):
	# NOTE: purge of themes need to be handled differently.
	# all the collection hierarchy needs to be purged in this case.

	node_id = request.GET.getlist('node_id', '')[0]

	if node_id:

		node_to_be_restore = node_collection.one({'_id': ObjectId(node_id)})
		# print "==========", node_to_be_restore.snapshot.keys()
		
		if node_to_be_restore.snapshot.keys():
		
			node_to_be_restore.group_set = [ObjectId(i) for i in node_to_be_restore.snapshot.keys()]
			node_to_be_restore.save()
			# print "--- ", node_to_be_restore.group_set
		
			return HttpResponse(1)

	return HttpResponse(0)

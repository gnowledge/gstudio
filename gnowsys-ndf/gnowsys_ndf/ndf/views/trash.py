
from django.http import HttpResponse
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.page import *
from gnowsys_ndf.ndf.views.methods import *




def trash_resource(request,group_id,node_id):
 node = node_collection.find_one({"_id":ObjectId(node_id)})
 trash_node = node_collection.find_one({"name":"Trash"});
 if ObjectId(group_id) in node.group_set: 		 
	 node.group_set.remove(ObjectId(group_id))
 #fetch the tarsh group id
 if trash_node._id not in node.group_set:	
	 node.group_set.append(trash_node._id)
 print "node",node.group_set	
 node.save()
 return (eval('page')(request, group_id))


def delete_resource(request,group_id):
	node_id = request.GET.getlist('node_id','')[0]
	delete_node(ObjectId(node_id),deletion_type=1)
	return HttpResponse("Deleted Successfully")

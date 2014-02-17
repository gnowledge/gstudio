''' -- imports from installed packages -- '''

from django.http import StreamingHttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django_mongokit import get_database

from gnowsys_ndf.ndf.views.methods import *
import json

db = get_database()
collection = db[File.collection_name]

@user_passes_test(lambda u: u.is_superuser)
def adminDashboard(request):
    '''
    methods for class view 
    '''
    objects_details = []
    nodes = collection.Node.find({'_type':"GSystem"})
    for each in nodes:
	objects_details.append({"Id":each._id,"Title":each.name,"Type":each.type_of,"Author":User.objects.get(id=each.created_by).username,"Group":",".join(each.group_set)})
    template = "ndf/adminDashboard.html"
    variable = RequestContext(request, {'class_name':"GSystem","nodes":objects_details})
    return render_to_response(template, variable)

@user_passes_test(lambda u: u.is_superuser)
def adminDashboardClass(request, class_name):
    '''
    fetching class's objects
    '''
    objects_details = []
    nodes = collection.Node.find({'_type':class_name})
    for each in nodes:
	if class_name in ("GSystem","File"):
		objects_details.append({"Id":each._id,"Title":each.name,"Type":",".join(each.member_of),"Author":User.objects.get(id=each.created_by).username,"Group":",".join(each.group_set),"Creation":each.created_at})
	else :
		objects_details.append({"Id":each._id,"Title":each.name,"Type":",".join(each.member_of),"Author":User.objects.get(id=each.created_by).username,"Creation":each.created_at})
    groups = []
    group = collection.Node.find({'_type':"Group"})
    for each in group:
        groups.append({'id':each._id,"title":each.name})
    systemtypes = []
    systemtype = collection.Node.find({'_type':"GSystemType"})
    for each in systemtype:
        systemtypes.append({'id':each._id,"title":each.name})

    template = "ndf/adminDashboard.html"
    variable = RequestContext(request, {'class_name':class_name,"nodes":objects_details,"Groups":groups,"systemtypes":systemtypes})
    return render_to_response(template, variable)


@user_passes_test(lambda u: u.is_superuser)
def adminDashboardEdit(request):
    '''
    edit class's objects
    '''
    if request.is_ajax() and request.method =="POST":
       objectjson = json.loads(request.POST['objectjson'])
    node = collection.Node.one({ '_id': ObjectId(objectjson['id'])})
    node.name =  objectjson['fields']['title']
    for key,value in objectjson['fields'].items():
         if key == "group":
            node['group_set'] = value.split(",")
         if key == "type":
            node['member_of'] = value.split(",")
    node.save()     
    return StreamingHttpResponse(node.name+" edited successfully")



@user_passes_test(lambda u: u.is_superuser)
def adminDashboardDelete(request):
    '''
    delete class's objects
    '''
    if request.is_ajax() and request.method =="POST":
       deleteobjects = request.POST['deleteobjects']
    for each in  deleteobjects.split(","):
        node = collection.Node.one({ '_id': ObjectId(each)})
        node.delete()

    return StreamingHttpResponse(len(deleteobjects.split(","))+" objects deleted")

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
    group_obj= collection.Node.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})
    groupid = ""
    if group_obj:
	groupid = str(group_obj[0]._id)
    for each in nodes:
	objects_details.append({"Id":each._id,"Title":each.name,"Type":each.type_of,"Author":User.objects.get(id=each.created_by).username,"Group":",".join(each.group_set)})
    template = "ndf/adminDashboard.html"
    variable = RequestContext(request, {'class_name':"GSystem","nodes":objects_details,"groupid":groupid})
    return render_to_response(template, variable)

@user_passes_test(lambda u: u.is_superuser)
def adminDashboardClass(request, class_name):
    '''
    fetching class's objects
    '''
    if request.method=="POST":
        search = request.POST.get("search","")
        classtype = request.POST.get("class","")
        nodes = collection.Node.find({'name':{'$regex':search, '$options': 'i' },'_type':classtype})
    else :
        nodes = collection.Node.find({'_type':class_name})
    objects_details = []
    for each in nodes:
        member = []
        for members in each.member_of:
            member.append(collection.Node.one({ '_id': members}).name+" - "+str(members))
	if class_name in ("GSystem","File"):
		objects_details.append({"Id":each._id,"Title":each.name,"Type":",".join(member),"Author":User.objects.get(id=each.created_by).username,"Group":",".join(each.group_set),"Creation":each.created_at})
	else :
		objects_details.append({"Id":each._id,"Title":each.name,"Type":",".join(member),"Author":User.objects.get(id=each.created_by).username,"Creation":each.created_at})
    groups = []
    group = collection.Node.find({'_type':"Group"})
    for each in group:
        groups.append({'id':each._id,"title":each.name})
    systemtypes = []
    systemtype = collection.Node.find({'_type':"GSystemType"})
    for each in systemtype:
        systemtypes.append({'id':each._id,"title":each.name})
    groupid = ""
    group_obj= collection.Node.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})
    if group_obj:
	groupid = str(group_obj[0]._id)
    template = "ndf/adminDashboard.html"
    variable = RequestContext(request, {'class_name':class_name, "nodes":objects_details, "Groups":groups, "systemtypes":systemtypes, "url":"data", "groupid":groupid})
    return render_to_response(template, variable)


@user_passes_test(lambda u: u.is_superuser)
def adminDashboardEdit(request):
    '''
    edit class's objects
    '''
    try:
        if request.is_ajax() and request.method =="POST":
            objectjson = json.loads(request.POST['objectjson'])
        node = collection.Node.one({ '_id': ObjectId(objectjson['id'])})
	print objectjson['id'],node
        node.name =  objectjson['fields']['title']
        for key,value in objectjson['fields'].items():
            if key == "group":
                node['group_set'] = value.split(",")
            if key == "type":
                typelist = []
		if value :
                	for eachvalue in  value.split(","):
                    		typelist.append(ObjectId(eachvalue.split(" ")[-1]))
                	node['member_of'] = typelist
        node.save()     
        return StreamingHttpResponse(node.name+" edited successfully")
    except Exception as e:
          return StreamingHttpResponse(e)




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

    return StreamingHttpResponse(str(len(deleteobjects.split(",")))+" objects deleted")

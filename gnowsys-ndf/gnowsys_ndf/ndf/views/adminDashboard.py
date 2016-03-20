''' -- imports from installed packages -- '''

from django.http import StreamingHttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test

from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import *

import json

GAPP = node_collection.one({'$and':[{'_type':'MetaType'},{'name':'GAPP'}]}) # fetching MetaType name GAPP

@user_passes_test(lambda u: u.is_superuser)
def adminDashboard(request):
    '''
    methods for class view 
    '''
    objects_details = []
    nodes = node_collection.find({'_type':"GSystem"})
    group_obj= node_collection.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})
    groupid = ""
    if group_obj:
	groupid = str(group_obj[0]._id)
    for each in nodes:
	objects_details.append({"Id":each._id,"Title":each.name,"Type":each.type_of,"Author":User.objects.get(id=each.created_by).username,"Group":",".join(each.group_set)})
    template = "ndf/adminDashboard.html"

    variable = RequestContext(request, {'class_name':"GSystem","nodes":objects_details,"groupid":groupid})
    return render_to_response(template, variable)

@user_passes_test(lambda u: u.is_superuser)
def adminDashboardClass(request, class_name="GSystem"):
    '''
    fetching class's objects
    '''
    group_set = ""
    if request.method=="POST":
        search = request.POST.get("search","")
        classtype = request.POST.get("class","")
        nodes = node_collection.find({'name':{'$regex':search, '$options': 'i' },'_type':classtype})
    else :
        nodes = node_collection.find({'_type':class_name})
    objects_details = []
    for each in nodes:
        member = []
        # for members in each.member_of:
        #     obj = node_collection.one({ '_id': members})
        #     if obj:
        #         member.append(obj.name+" - "+str(members))

        member = []
        member_of_list = []
        collection_list = []
        attribute_type_set = []
        relation_type_set = []
        if class_name == "GSystemType":
            for members in each.member_of:
                member.append(node_collection.one({ '_id': members}).name)
                # member_of_list.append(node_collection.one({'_id':members}).name+" - "+str(members))
            for coll in each.collection_set:
                collection_list.append(node_collection.one({ '_id': coll}).name)
                # collection_list.append(node_collection.one({ '_id': coll}).name+" - "+str(coll))
            for at_set in each.attribute_type_set:
                attribute_type_set.append(at_set.name)
                # attribute_type_set.append(at_set.name+" - "+str(at_set._id))
            for rt_set in each.relation_type_set:
                relation_type_set.append(rt_set.name)
                # relation_type_set.append(rt_set.name+" - "+str(rt_set._id))

	if class_name in ("GSystem","File"):
      		group_set = [node_collection.find_one({"_id":eachgroup}).name for eachgroup in each.group_set if node_collection.find_one({"_id":eachgroup}) ]
		objects_details.append({"Id":each._id,"Title":each.name,"Type":", ".join(member),"Author":User.objects.get(id=each.created_by).username,"Group":", ".join(group_set),"Creation":each.created_at})
        elif class_name in ("GAttribute","GRelation"):
            objects_details.append({"Id":each._id,"Title":each.name,"Type":"","Author":"","Creation":""})
	else :
		objects_details.append({"Id":each._id,"Title":each.name,"Type":", ".join(member),"Author":User.objects.get(id=each.created_by).username,"Creation":each.created_at,'member_of':", ".join(member_of_list), "collection_list":", ".join(collection_list), "attribute_type_set":", ".join(attribute_type_set), "relation_type_set":", ".join(relation_type_set)})
    groups = []
    group = node_collection.find({'_type':"Group"})
    for each in group:
        groups.append({'id':each._id,"title":each.name})
    systemtypes = []
    systemtype = node_collection.find({'_type':"GSystemType"})
    for each in systemtype:
        systemtypes.append({'id':each._id,"title":each.name})
    groupid = ""
    group_obj= node_collection.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})
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
        node = node_collection.one({ '_id': ObjectId(objectjson['id'])})
        node.name =  objectjson['fields']['title']
        for key,value in objectjson['fields'].items():
            if key == "group":
                typelist = []
                for eachvalue in  value.split(","):
		    if eachvalue:
                    	typelist.append(ObjectId(eachvalue.split(" ")[-1]))
                node['group_set'] = typelist
            # if key == "type":
            #     typelist = []
            #     for eachvalue in  value.split(","):
            #         typelist.append(ObjectId(eachvalue.split(" ")[-1]))
            #     node['member_of'] = typelist
            if key == "member_of":
                typelist = []
                for eachvalue in  value.split(","):
		    if eachvalue:
                    	typelist.append(ObjectId(eachvalue.split(" ")[-1]))
                node['member_of'] = typelist
            if key == "collection_set":
                typelist = []
	        for eachvalue in  value.split(","):
		    if eachvalue:
                    	typelist.append(ObjectId(eachvalue.split(" ")[-1]))
                node['collection_set'] = typelist
            if key == "attribute_type_set":
                typelist = []
	        for eachvalue in  value.split(","):
		    if eachvalue:
                    	typelist.append(node_collection.find_one(ObjectId(eachvalue.split(" ")[-1])))
                node['attribute_type_set'] = typelist
            if key == "relation_type_set":
                typelist = []
	        for eachvalue in  value.split(","):
		    if eachvalue:
                    	typelist.append(node_collection.find_one(ObjectId(eachvalue.split(" ")[-1])))
                node['relation_type_set'] = typelist


        node.save(groupid=group_id)     
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
        node = node_collection.one({ '_id': ObjectId(each)})
        node.delete()

    return StreamingHttpResponse(str(len(deleteobjects.split(",")))+" objects deleted")

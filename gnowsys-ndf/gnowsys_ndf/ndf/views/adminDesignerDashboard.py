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
def adminDesignerDashboardClass(request, class_name):
    '''
    fetching class's objects
    '''
    if request.method=="POST":
        search = request.POST.get("search","")
        classtype = request.POST.get("class","")
        nodes = collection.Node.find({'name':{'$regex':search},'_type':classtype})
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

    template = "ndf/adminDashboard.html"
    variable = RequestContext(request, {'class_name':class_name,"nodes":objects_details,"Groups":groups,"systemtypes":systemtypes,"url":"designer"})
    return render_to_response(template, variable)


@user_passes_test(lambda u: u.is_superuser)
def adminDesignerDashboardClassCreate(request,class_name):
    '''
    delete class's objects
    '''
    definitionlist = []
    contentlist = []
    dependencylist = []
    options = []
    class_structure = eval(class_name).structure
    # if class_name == 'GSystemType':
    #     class_structure = collection.GSystemType.structure
    # if class_name == 'RelationType':
    #     class_structure = collection.RelationType.structure
    # if class_name == 'AttributeType':
    #     class_structure = collection.AttributeType.structure

    newdict = {}
    for key,value in class_structure.items():
        if value == bool:
            newdict[key] = "bool"
        elif value == unicode:
            newdict[key] = "unicode"
        elif value == list:
            newdict[key] = "list"
        elif type(value) == list:
            newdict[key] = "list"
        elif value == datetime.datetime:
            newdict[key] = "datetime"
        else: 
            newdict[key] = value
    #        print value, key
    class_structure = newdict    
    if class_name == "AttributeType":
        definitionlist = ['name','altnames','subject_type','applicable_node_type','data_type','member_of','verbose_name','null','blank','help_text','max_digit','decimal_places','auto_now','auto_now_add','path','verify_exist','status']
        contentlist = ['content','content_org']
        dependencylist = ['prior_node']
        options = ['featured','created_by','created_at','start_publication','tags','url','last_update','login_required']
    elif class_name == "GSystemType":
        definitionlist = ['name','altnames','status','meta_type_set','attribute_type_set','relation_type_set','process_type_set']
        contentlist = ['content','content_org']
        dependencylist = ['prior_node']
        options = ['featured','created_by','created_at','start_publication','tags','url','last_update','login_required']
    elif class_name == "RelationType":
        definitionlist = ['name','altnames','subject_type','applicable_node_type','data_type','verbose_name','null','blank','help_text','max_digit','decimal_places','auto_now','auto_now_add','path','verify_exist','status']
        contentlist = ['content','content_org']
        dependencylist = ['prior_node']
        options = ['featured','created_by','created_at','start_publication','tags','url','last_update','login_required']
    else :
        definitionlist = []
        contentlist = []
        dependencylist = []
        options = []

    template = "ndf/adminDashboardCreate.html"
    variable = RequestContext(request, {'class_name':class_name,"url":"designer","class_structure":class_structure,'definitionlist':definitionlist,'contentlist':contentlist,'dependencylist':dependencylist,'options':options})
    return render_to_response(template, variable)


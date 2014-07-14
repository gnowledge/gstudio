''' -- imports from installed packages -- '''
from django.http import StreamingHttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django_mongokit import get_database

from gnowsys_ndf.settings import LANGUAGES
from gnowsys_ndf.ndf.views.methods import *

import json
import datetime

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
        nodes = collection.Node.find({'name':{'$regex':search,'$options': 'i' },'_type':classtype}).sort('last_update', -1)
    else :
        nodes = collection.Node.find({'_type':class_name}).sort('last_update', -1)

    objects_details = []
    for each in nodes:
        member = []
        member_of_list = []
        collection_list = []
        attribute_type_set = []
        relation_type_set = [] 
        for e in each.member_of:
            member_of_list.append(collection.Node.one({'_id':e}).name+" - "+str(e))
        
        for members in each.member_of:
            member.append(collection.Node.one({ '_id': members}).name+" - "+str(members))
        
        for coll in each.collection_set:
            collection_list.append(collection.Node.one({ '_id': coll}).name+" - "+str(coll))
        
        if class_name in ("GSystemType"):
            for at_set in each.attribute_type_set:
                attribute_type_set.append(at_set.name+" - "+str(at_set._id))
            for rt_set in each.relation_type_set:
                relation_type_set.append(rt_set.name+" - "+str(rt_set._id))
            objects_details.append({"Id":each._id,"Title":each.name,"Type":",".join(member),"Author":User.objects.get(id=each.created_by).username,"Creation":each.created_at,'member_of':",".join(member_of_list), "collection_list":",".join(collection_list), "attribute_type_set":",".join(attribute_type_set), "relation_type_set":",".join(relation_type_set)})
        else :
		objects_details.append({"Id":each._id,"Title":each.name,"Type":",".join(member),"Author":User.objects.get(id=each.created_by).username,"Creation":each.created_at,'member_of':",".join(member_of_list), "collection_list":",".join(collection_list)})
    groups = []
    group = collection.Node.find({'_type':"Group"})
    for each in group:
        groups.append({'id':each._id,"title":each.name})
    
    systemtypes = []
    systemtype = collection.Node.find({'_type':"GSystemType"})
    for each in systemtype:
        systemtypes.append({'id':each._id,"title":each.name})


    meta_types = []
    meta_type = collection.Node.find({'_type':"MetaType"})
    for each in meta_type:
        meta_types.append({'id':each._id,"title":each.name})

    groupid = ""
    group_obj= collection.Node.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})
    if group_obj:
	groupid = str(group_obj[0]._id)

    template = "ndf/adminDashboard.html"
    variable = RequestContext(request, {'class_name':class_name,"nodes":objects_details,"Groups":groups,"systemtypes":systemtypes,"url":"designer","groupid":groupid,'meta_types':meta_types})
    return render_to_response(template, variable)


@user_passes_test(lambda u: u.is_superuser)
def adminDesignerDashboardClassCreate(request, class_name, node_id=None):
    '''
    delete class's objects
    '''
    new_instance_type = None

    definitionlist = []
    contentlist = []
    dependencylist = []
    options = []
    translate=request.GET.get('translate','')
    if class_name == "AttributeType":
        definitionlist = ['name','altnames','language','subject_type','data_type','applicable_node_type','member_of','verbose_name','null','blank','help_text','max_digits','decimal_places','auto_now','auto_now_add','path','verify_exist','status']
        contentlist = ['content_org']
        dependencylist = ['prior_node']
        options = ['featured','created_at','start_publication','tags','url','last_update','login_required']
    elif class_name == "GSystemType":
        definitionlist = ['name','altnames','language','status','member_of','meta_type_set','attribute_type_set','relation_type_set','type_of']
        contentlist = ['content_org']
        dependencylist = ['prior_node']
        options = ['featured','created_at','start_publication','tags','url','last_update','login_required']
    elif class_name == "RelationType":
        definitionlist = ['name','inverse_name','altnames','language','subject_type','object_type','subject_cardinality','object_cardinality','subject_applicable_nodetype','object_applicable_nodetype','is_symmetric','is_reflexive','is_transitive','status','member_of']
        contentlist = ['content_org']
        dependencylist = ['prior_node']
        options = ['featured','created_at','start_publication','tags','url','last_update','login_required']
    else :
        definitionlist = []
        contentlist = []
        dependencylist = []
        options = []

    class_structure = eval(class_name).structure
    required_fields = eval(class_name).required_fields
    newdict = {}
    if node_id:
        new_instance_type = collection.Node.one({'_type': unicode(class_name), '_id': ObjectId(node_id)})

    else:
        new_instance_type = eval("collection"+"."+class_name)()

    if request.method=="POST":
        if translate:
            new_instance_type = eval("collection"+"."+class_name)()
            
        for key,value in class_structure.items():
            if value == bool:
                if request.POST.get(key,""):
                    if request.POST.get(key,"") in ('1','2'):
                        if request.POST.get(key,"") == '1':
                            new_instance_type[key] = True
                        else :
                            new_instance_type[key] = False  
                            
            elif value == unicode:
                if request.POST.get(key,""):
                    
                    if key == "content_org":
                        new_instance_type[key] = unicode(request.POST.get(key,""))
                        # Required to link temporary files with the current user who is modifying this document
                        usrname = request.user.username
                        filename = slugify(new_instance_type['name']) + "-" + usrname + "-"
                        new_instance_type['content'] = org2html(new_instance_type[key], file_prefix=filename)
                    else :
                        if translate:
                            if key in ("name","inverse_name"):
                                new_instance_type[key] = unicode(request.POST.get(key+"_trans",""))
                                                
                                
                            else:
                                new_instance_type[key] = unicode(request.POST.get(key,""))
                        else:
                            new_instance_type[key] = unicode(request.POST.get(key,""))

            elif value == list:
                if request.POST.get(key,""):
                    new_instance_type[key] = request.POST.get(key,"").split(",")

            elif type(value) == list:
                if request.POST.get(key,""):
                    if key in ("tags","applicable_node_type"):
                        new_instance_type[key] = request.POST.get(key,"").split(",")
                    elif key in ["meta_type_set","attribute_type_set","relation_type_set"]:
                        listoflist = []
                        for each in request.POST.get(key,"").split(","):
                            listoflist.append(collection.Node.one({"_id":ObjectId(each)}))
                        new_instance_type[key] = listoflist
                    else :
                        listoflist = []
                        for each in request.POST.get(key,"").split(","):
                            listoflist.append(ObjectId(each))
                        new_instance_type[key] = listoflist

            elif value == datetime.datetime:
                if key == "last_update":
                    new_instance_type[key] = datetime.datetime.now()
                
            elif key == "status":
                if request.POST.get(key,""):
                    new_instance_type[key] = unicode(request.POST.get(key,""))

            # elif key == "created_by":
            #     new_instance_type[key] = request.user.id

            elif value == int:
                if request.POST.get(key,""):
                    new_instance_type[key] = int(request.POST.get(key,""))

            else: 
                if request.POST.get(key,""):
                    new_instance_type[key] = request.POST.get(key,"")

        user_id = request.user.id

        if not new_instance_type.has_key('_id'):
            new_instance_type.created_by = user_id

        new_instance_type.modified_by = user_id

        if user_id not in new_instance_type.contributors:
            new_instance_type.contributors.append(user_id)

        new_instance_type.save()
        if translate:        
            relation_type=collection.Node.one({'$and':[{'name':'translation_of'},{'_type':'RelationType'}]})
            grelation=collection.GRelation()
            grelation.relation_type=relation_type
            grelation.subject=new_instance_type['_id']
            grelation.right_subject=ObjectId(node_id)
            grelation.name=u""
            grelation.save()
            
        return HttpResponseRedirect("/admin/designer/"+class_name)


    # If GET request ---------------------------------------------------------------------------------------

    for key,value in class_structure.items():
        if value == bool:
            # newdict[key] = "bool"
            newdict[key] = ["bool", new_instance_type[key]]
        elif value == unicode:
            if key == "language":
                newdict[key] = ["list", new_instance_type[key]]
            else:
                # newdict[key] = "unicode"
                newdict[key] = ["unicode", new_instance_type[key]]
              
        elif value == list:
            # newdict[key] = "list"
            
            newdict[key] = ["list", new_instance_type[key]]
        elif type(value) == list:
            # newdict[key] = "list"
            newdict[key] = ["list", new_instance_type[key]]
        elif value == datetime.datetime:
            # newdict[key] = "datetime"
            newdict[key] = ["datetime", new_instance_type[key]]
        elif value == int:
            # newdict[key] = "int"
            newdict[key] = ["int", new_instance_type[key]]
        elif key == "status":
            # newdict[key] = "status"
            newdict[key] = ["status", new_instance_type[key]]
        else: 
            # newdict[key] = value
            newdict[key] = [value, new_instance_type[key]]

    class_structure = newdict
    groupid = ""
    group_obj= collection.Node.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})
    if group_obj:
	groupid = str(group_obj[0]._id)

    template = "ndf/adminDashboardCreate.html"

    variable =  None
    class_structure_with_values = {}
    if node_id:
        
        for key, value in class_structure.items():
            class_structure_with_values[key] = [class_structure[key][0], new_instance_type[key]]

        variable = RequestContext(request, {'node': new_instance_type,
                                            'class_name': class_name, 'class_structure': class_structure_with_values, 'url': "designer", 
                                            'definitionlist': definitionlist, 'contentlist': contentlist, 'dependencylist': dependencylist, 
                                            'options': options, 'required_fields': required_fields,"translate":translate,"lan":LANGUAGES,
                                            'groupid': groupid
                                        })
    else:
        variable = RequestContext(request, {'class_name':class_name, "url":"designer", "class_structure":class_structure, 'definitionlist':definitionlist, 'contentlist':contentlist, 'dependencylist':dependencylist, 'options':options, "required_fields":required_fields,"groupid":groupid,"translate":translate,"lan":LANGUAGES,})

    return render_to_response(template, variable)


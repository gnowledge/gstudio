''' -- imports from installed packages -- '''
from django.http import StreamingHttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test

from gnowsys_ndf.settings import LANGUAGES
from gnowsys_ndf.settings import GSTUDIO_HELP_TIP,GSYSTEMTYPE_DEFINITIONLIST,ATTRIBUTETYPE_DEFINITIONLIST,RELATIONTYPE_DEFINITIONLIST,CONTENTLIST,DEPENDENCYLIST,OPTIONLIST
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import *

import json
import datetime

@user_passes_test(lambda u: u.is_superuser)
def adminDesignerDashboardClass(request, class_name='GSystemType'):
    '''
    fetching class's objects
    '''
    if request.method == "POST":
        search = request.POST.get("search","")
        classtype = request.POST.get("class","")
        nodes = node_collection.find({'name':{'$regex':search,'$options': 'i' },'_type':classtype}).sort('last_update', -1)
    else :
        nodes = node_collection.find({'_type':class_name}).sort('last_update', -1)


    objects_details = []
    for each in nodes:

        try:
            user_name = User.objects.get(id=each.created_by).username
        except Exception, e:
            print e
            user_name = None

        member = []
        member_of_list = []
        collection_list = []
        attribute_type_set = []
        relation_type_set = []
        if class_name in ("GSystemType","AttributeType","RelationType") :
            for e in each.member_of:
                member_of_list.append(node_collection.one({'_id':e}).name)
                # member_of_list.append(node_collection.one({'_id':e}).name+" - "+str(e))

            for members in each.member_of:
                member.append(node_collection.one({ '_id': members}).name)
                # member.append(node_collection.one({ '_id': members}).name+" - "+str(members))

        # for coll in each.collection_set:
        #     collection_list.append(node_collection.one({ '_id': coll}).name+" - "+str(coll))

        if class_name == "GSystemType" :
            for at_set in each.attribute_type_set:
                attribute_type_set.append(at_set.name)
                # attribute_type_set.append(at_set.name+" - "+str(at_set._id))
            for rt_set in each.relation_type_set:
                relation_type_set.append(rt_set.name)
                # relation_type_set.append(rt_set.name+" - "+str(rt_set._id))
            objects_details.append({"Id":each._id,"Title":each.name,"Type":", ".join(member),"Author":user_name,"Creation":each.created_at,'member_of':", ".join(member_of_list), "collection_list":", ".join(collection_list), "attribute_type_set":", ".join(attribute_type_set), "relation_type_set":", ".join(relation_type_set)})
        else :
            if class_name in ("AttributeType","RelationType"):
                objects_details.append({"Id":each._id,"Title":each.name,"Type":", ".join(member),"Author":user_name,"Creation":each.created_at,'member_of':", ".join(member_of_list), "collection_list":", ".join(collection_list)})

            else:
                if class_name == "GSystem" :
                    group_set = [node_collection.find_one({"_id":eachgroup}).name for eachgroup in each.group_set if node_collection.find_one({"_id":eachgroup}) ]
                    mem_ty=[]
                    if each.member_of:
                        for e in each.member_of:
                            mem_ty.append(str(e))
                            # find = node_collection.one({ '_id': ObjectId(e),'_type':"GSystem"})
                            # find_name = find.name
                            # member.append(find_name)
                            # print e,find,"here\n\n"
                        k = mem_ty[0]
                    else:
                        k = None
                        member = []
                    objects_details.append({"Id":each._id,"Title":each.name, "Alt_Title":each.altnames, "Mem":k ,"Type":", ".join(member), "collection_list":", ".join(collection_list), "Type":", ".join(member),"Author":user_name,"Group":", ".join(group_set),"Creation":each.created_at })

    groups = []
    group = node_collection.find({'_type':"Group"})
    for each in group:
        groups.append({'id':each._id,"title":each.name})

    systemtypes = []
    systemtype = node_collection.find({'_type':"GSystemType"})
    for each in systemtype:
        systemtypes.append({'id':each._id,"title":each.name})

    meta_types = []
    meta_type = node_collection.find({'_type':"MetaType"})
    for each in meta_type:
        meta_types.append({'id':each._id,"title":each.name})

    groupid = ""
    group_obj= node_collection.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})
    if group_obj:
        groupid = str(group_obj[0]._id)
        group_name = group_obj[0].name

    template = "ndf/adminDashboard.html"
    variable = RequestContext(request, {'class_name':class_name,"nodes":objects_details,"Groups":groups,"systemtypes":systemtypes,"url":"designer","groupid":groupid,'meta_types':meta_types,'group_id':groupid, "group_name":group_name })
    return render_to_response(template, variable)


@user_passes_test(lambda u: u.is_superuser)
def adminDesignerDashboardClassCreate(request, class_name='GSystemType', node_id=None):
    '''
    delete class's objects
    '''
    global LANGUAGES
    new_instance_type = None
    LANGUAGES = '' if not LANGUAGES else LANGUAGES
    definitionlist = []
    contentlist = []
    dependencylist = []
    options = []

    translate=request.GET.get('translate','')
    if class_name == "AttributeType":
        definitionlist = ATTRIBUTETYPE_DEFINITIONLIST
        contentlist = CONTENTLIST
        dependencylist = DEPENDENCYLIST
        options = OPTIONLIST
        # definitionlist = ['name','altnames','language','subject_type','data_type','member_of','verbose_name','null','blank','help_text','max_digits','decimal_places','auto_now','auto_now_add','path','verify_exist','status']
        # definitionlist = {'name':'Name : ' ,'altnames':'Alternate Name : ' ,'language':'Language : ' ,'subject_type':'Subject Type : ' ,'data_type':'Data Type : ' ,'member_of':'Member of MetaType : ' ,'verbose_name':'Verbose Name : ' ,'null':'Null : ' ,'blank':'Blank : ' ,'help_text':'Help Text : ' ,'max_digits':'Maximum Digits : ' ,'decimal_places':'Decimal Places : ' ,'auto_now':'Auto Now : ' ,'auto_now_add':'Auto Now Add : ' ,'path':'Path : ' ,'verify_exist':'Verify Existence : ' ,'status':'Status : ' }
        # definitionlist = [{'name':'Name '} ,{'altnames':'Alternate Name '} ,{'language':'Language ' },{'subject_type':'Subject Type '} ,{'data_type':'Data Type '} ,{'member_of':'Member of MetaType ' },{'verbose_name':'Verbose Name '} ,{'null':'Null '} ,{'blank':'Blank '} ,{'help_text':'Help Text ' },{'max_digits':'Maximum Digits ' },{'decimal_places':'Decimal Places ' },{'auto_now':'Auto Now '} ,{'auto_now_add':'Auto Now Add '} ,{'path':'Path '} ,{'verify_exist':'Verify Existence '} ,{'status':'Status ' }]
        # contentlist = ['content_org']
        # contentlist = {'content_org':'content organization' }
        # dependencylist = ['prior_node']
        # dependencylist = {'prior_node':'Prior Node : ' }
        # options = ['featured','created_at','start_publication','tags','url','last_update','login_required']
        # options = {'featured':'Featured : ' ,'created_at':'Created At : ' ,'start_publication':'Start Publication : ' ,'tags':'Tags : ' ,'url':'URL : ' ,'last_update':'Last Update : ' ,'login_required':'Login Required : ' }
    elif class_name == "GSystemType":
        definitionlist = GSYSTEMTYPE_DEFINITIONLIST
        contentlist = CONTENTLIST
        dependencylist = DEPENDENCYLIST
        options = OPTIONLIST
        # definitionlist = ['name','altnames','language','status','member_of','meta_type_set','attribute_type_set','relation_type_set','type_of']
        # definitionlist = [{'name':'Name : '} ,{'altnames':'Alternate Name : '} ,{'language':'Language : ' },{'status':'Status : '} ,{'member_of':'Member of MetaType : '} ,{'meta_type_set':'Select the MetaType : ' },{'attribute_type_set':'Select the AttributeType : ' },{'relation_type_set':'Select the RelationType : ' },{'type_of':'Type Of GSystemType : '} ]
        # definitionlist = {'name':'Name : ' ,'altnames':'Alternate Name : ' ,'language':'Language : ' ,'status':'Status : ' ,'member_of':'Member of MetaType : ' ,'meta_type_set':'Select the MetaType : ' ,'attribute_type_set':'Select the AttributeType : ' ,'relation_type_set':'Select the RelationType : ' ,'type_of':'Type Of GSystemType : ' }
        # contentlist = ['content_org']
        # contentlist = {'content_org':'content organization' }
        # dependencylist = ['prior_node']
        # dependencylist = {'prior_node':'Prior Node : ' }
        # options = ['featured','created_at','start_publication','tags','url','last_update','login_required']
        # options = {'featured':'Featured : ' ,'created_at':'Created At : ' ,'start_publication':'Start Publication : ' ,'tags':'Tags : ' ,'url':'URL : ' ,'last_update':'Last Update : ' ,'login_required':'Login Required : ' }
    elif class_name == "RelationType":
        definitionlist = RELATIONTYPE_DEFINITIONLIST
        contentlist = CONTENTLIST
        dependencylist = DEPENDENCYLIST
        options = OPTIONLIST
        # definitionlist = ['name','inverse_name','altnames','language','subject_type','object_type','subject_cardinality','object_cardinality','subject_applicable_nodetype','object_applicable_nodetype','is_symmetric','is_reflexive','is_transitive','status','member_of']
        # definitionlist = [{'name':'Name '} ,{'inverse_name':'Inverse Name '} ,{'altnames':'Alternate Name '} ,{'language':'Language '} ,{'subject_type':'Subject Type '}  ,{'object_type':'Object Type '} ,{'subject_cardinality':'Subject Cardinality '} ,{'object_cardinality':'Object Cardinality '} ,{'subject_applicable_nodetype':'Subject Applicable Node Type '} ,{'object_applicable_nodetype':'Object Applicable Node Type '} ,{'is_symmetric':'Is Symmetric '} ,{'is_reflexive':'Is Reflexive '} ,{'is_transitive':'Is Transitive '} ,{'status':'Status '} ,{'member_of':'Member of MetaType '}]
        # definitionlist = {'name':'Name : ' ,'inverse_name':'Inverse Name : ' ,'altnames':'Alternate Name : ' ,'language':'Language : ' ,'subject_type':'Subject Type : '  ,'object_type':'Object Type : ' ,'subject_cardinality':'Subject Cardinality : ' ,'object_cardinality':'Object Cardinality : ' ,'subject_applicable_nodetype':'Subject Applicable Node Type : ' ,'object_applicable_nodetype':'Object Applicable Node Type : ' ,'is_symmetric':'Is Symmetric : ' ,'is_reflexive':'Is Reflexive : ' ,'is_transitive':'Is Transitive : ' ,'status':'Status : ' ,'member_of':'Member of MetaType : '}
        # definitionlist = ['name','inverse_name','altnames','language','subject_type','object_type','subject_cardinality','object_cardinality','is_symmetric','is_reflexive','is_transitive','status','member_of']
        # contentlist = ['content_org']
        # contentlist = {'content_org':'content organization' }
        # dependencylist = ['prior_node']
        # dependencylist = {'prior_node':'Prior Node : ' }
        # options = ['featured','created_at','start_publication','tags','url','last_update','login_required']
        # options = {'featured':'Featured : ' ,'created_at':'Created At : ' ,'start_publication':'Start Publication : ' ,'tags':'Tags : ' ,'url':'URL : ' ,'last_update':'Last Update : ' ,'login_required':'Login Required : ' }
    else :
        definitionlist = []
        contentlist = []
        dependencylist = []
        options = []

    class_structure = eval(class_name).structure
    required_fields = eval(class_name).required_fields

    help_tip = GSTUDIO_HELP_TIP

    newdict = {}
    if node_id:
        new_instance_type = node_collection.one({'_type': unicode(class_name), '_id': ObjectId(node_id)})
    else:
        new_instance_type = eval("node_collection.collection"+"."+class_name)()

    if request.method=="POST":
        if translate:
            new_instance_type = eval("node_collection.collection"+"."+class_name)()
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
                        # new_instance_type['content'] = org2html(new_instance_type[key], file_prefix=filename)
                        new_instance_type['content'] = unicode(new_instance_type[key])
                    else :
                        if translate:
                            if key in ("name","inverse_name"):
                                new_instance_type[key] = unicode(request.POST.get(key+"_trans",""))
                                language= request.POST.get('lan')
                                new_instance_type.language = get_language_tuple(language)

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
                            listoflist.append(node_collection.one({"_id":ObjectId(each)}))
                        new_instance_type[key] = listoflist

                    elif key in ["member_of","prior_node","type_of"]:
                        new_mem = request.POST.get(key,"").split(",")
                        new_mem_list = [ObjectId(each) for each in new_mem]
                        new_instance_type[key] = new_mem_list

                    else :
                        listoflist = []
                        for each in request.POST.get(key,"").split(","):
                            listoflist.append(ObjectId(each))
                        new_instance_type[key] = listoflist
                else:
                    listoflist=[]
                    new_instance_type[key]=listoflist


            elif type(value) == tuple:
                new_instance_type[key] = tuple(eval(request.POST.get(key,"")))

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
        parent_node=node_collection.one({'_id':ObjectId(node_id)})
        if translate and class_name == "RelationType":
            new_instance_type.subject_type = parent_node.subject_type
            new_instance_type.object_type = parent_node.object_type
        if translate and class_name == "AttributeType":
            new_instance_type.data_type = parent_node.data_type
            new_instance_type.subject_type = parent_node.subject_type

        new_instance_type.save()
        if translate:
            relation_type=node_collection.one({'$and':[{'name':'translation_of'},{'_type':'RelationType'}]})
            grelation=node_collection.collection.GRelation()
            grelation.relation_type=relation_type._id
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
    group_obj= node_collection.find({'$and':[{"_type":u'Group'},{"name":u'home'}]})
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
                                            'groupid': groupid,'group_id':groupid ,'help_tip':help_tip
                                        })

    else:

        variable = RequestContext(request, {'class_name':class_name, "url":"designer", "class_structure":class_structure, 'definitionlist':definitionlist, 'contentlist':contentlist, 'dependencylist':dependencylist, 'options':options, "required_fields":required_fields,"groupid":groupid,"translate":translate,"lan":LANGUAGES,'group_id':groupid, 'help_tip':help_tip })

    return render_to_response(template, variable)
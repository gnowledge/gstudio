''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response #, render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required


import ast

from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *

from gnowsys_ndf.ndf.views.file import *

db = get_database()
collection = db['Nodes']

@get_execution_time
def custom_app_view(request, group_id, app_name, app_id=None, app_set_id=None, app_set_instance_id=None):
    """
    custom view for custom GAPPS
    """
    #ins_objectid  = ObjectId()
    #if ins_objectid.is_valid(group_id) is False :
        #group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        #auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        #if group_ins:
            #group_id = str(group_ins._id)
        #else :
            #auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            #if auth :
                #group_id = str(auth._id)
    #else :
        #pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    if app_id is None:
        if app_name == "partners":
            app_name = "Partners"
        app_ins = node_collection.find_one({'_type':"GSystemType", "name":app_name})
        if app_ins:
            app_id = str(app_ins._id)
    app_collection_set = []
    nodes_dict = []
    atlist = []
    rtlist = []
    app = node_collection.find_one({"_id":ObjectId(app_id)})
    app_set = ""
    nodes = ""
    nodes_dict = ""
    app_menu = ""
    app_set_template = ""
    app_set_instance_template = ""
    app_set_instance_name = ""
    app_set_name = ""
    title = ""
    tags = ""
    content = ""
    location = ""
    system = None
    system_id = ""
    system_type = ""
    system_mime_type = ""
    property_display_order = []

    for eachset in app.collection_set:
         app_set = node_collection.find_one({"_id":eachset})
         app_collection_set.append({"id": str(app_set._id), "name": app_set.name})

    if app_set_id:
        classtype = ""
        app_set_template = "yes"
        systemtype = node_collection.find_one({"_id":ObjectId(app_set_id)})
        systemtype_name = systemtype.name
        title = systemtype_name
        if request.method=="POST":
            search = request.POST.get("search","")
            classtype = request.POST.get("class","")
            nodes = list(node_collection.find({'name':{'$regex':search, '$options': 'i'},'member_of': {'$all': [systemtype._id]}}))
        else :
            nodes = list(node_collection.find({'member_of': {'$all': [systemtype._id]},'group_set':{'$all': [ObjectId(group_id)]}}))

        nodes_dict = []
        for each in nodes:
            nodes_dict.append({"id":str(each._id), "name":each.name, "created_by":User.objects.get(id=each.created_by).username, "created_at":each.created_at})

    else :

        app_menu = "yes"
        title = app_name

    if app_set_instance_id :
        app_set_instance_template = "yes"
        app_set_template = ""
        systemtype_attributetype_set = []
        systemtype_relationtype_set = []
        system = node_collection.find_one({"_id":ObjectId(app_set_instance_id)})
        systemtype = node_collection.find_one({"_id":ObjectId(app_set_id)})
        for each in systemtype.attribute_type_set:
            systemtype_attributetype_set.append({"type":each.name,"type_id":str(each._id),"value":each.data_type})
        for each in systemtype.relation_type_set:
            systemtype_relationtype_set.append({"rt_name":each.name,"type_id":str(each._id)})

        for eachatset in systemtype_attributetype_set :
            for eachattribute in triple_collection.find({"_type":"GAttribute", "subject":system._id, "attribute_type":ObjectId(eachatset["type_id"])}):
                atlist.append({"type":eachatset["type"],"type_id":eachatset["type_id"],"value":eachattribute.object_value})
        for eachrtset in systemtype_relationtype_set :
            for eachrelation in triple_collection.find({"_type":"GRelation", "subject":system._id, "relation_type":ObjectId(eachrtset["type_id"])}):
                right_subject = node_collection.find_one({"_id":ObjectId(eachrelation.right_subject)})
                rtlist.append({"type":eachrtset["rt_name"],"type_id":eachrtset["type_id"],"value_name": right_subject.name,"value_id":str(right_subject._id)})

        # To support consistent view

        property_order = system.property_order
        system.get_neighbourhood(systemtype._id)

        for tab_name, fields_order in property_order:
            display_fields = []
            for field, altname in fields_order:
                if system.structure[field] == bool:
                    display_fields.append((altname, ("Yes" if system[field] else "No")))

                elif not system[field]:
                    display_fields.append((altname, system[field]))
                    continue

                elif system.structure[field] == datetime.datetime:
                    display_fields.append((altname, system[field].date()))

                elif type(system.structure[field]) == list:
                    if system[field]:
                        if type(system.structure[field][0]) == ObjectId:
                            name_list = []
                            for right_sub_dict in system[field]:
                                name_list.append(right_sub_dict.name)
                            display_fields.append((altname, ", ".join(name_list)))
                        else:
                            display_fields.append((altname, ", ".join(system[field])))

                else:
                    display_fields.append((altname, system[field]))

            property_display_order.append((tab_name, display_fields))

        # End of code

        tags = ",".join(system.tags)
        content = system.content
        location = system.location
        app_set_name = systemtype.name
        system_id = system._id
        system_type = system._type

        if system_type == 'File':
            system_mime_type = system.mime_type

        app_set_instance_name = system.name
        title =  systemtype.name +"-" +system.name

    template = "ndf/custom_template_for_app.html"

    variable = RequestContext(request, {'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set,"app_set_id":app_set_id,"nodes":nodes_dict, "app_menu":app_menu, "app_set_template":app_set_template, "app_set_instance_template":app_set_instance_template, "app_set_name":app_set_name, "app_set_instance_name":app_set_instance_name, "title":title, "app_set_instance_atlist":atlist, "app_set_instance_rtlist":rtlist, 'tags':tags, 'location':location, "content":content, "system_id":system_id,"system_type":system_type,"mime_type":system_mime_type, "app_set_instance_id":app_set_instance_id

                                        , "node":system, 'group_id':group_id, "property_display_order": property_display_order})

    return render_to_response(template, variable)

@login_required
@get_execution_time
def custom_app_new_view(request, group_id, app_name, app_id, app_set_id=None, app_set_instance_id=None):
    """
    create new instance of app_set of apps view for custom GAPPS
    """
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
        # group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        # auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        # if group_ins:
            # group_id = str(group_ins._id)
        # else :
            # auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            # if auth :
                # group_id = str(auth._id)
    # else :
        # pass


    try:
        group_id = ObjectId(group_id)

    except:
        group_name, group_id = get_group_name_id(group_id)

    if app_id is None:
        app_ins = node_collection.find_one({'_type':"GSystemType", "name":app_name})
        if app_ins:
            app_id = str(app_ins._id)
    app_collection_set = []
    app = node_collection.find_one({"_id":ObjectId(app_id)})
    app_set = ""
    app_set_instance_name = ""
    nodes = ""
    systemtype = ""
    title = ""
    tags = ""
    location=""
    content_org = ""
    system_id = ""
    system_type = ""
    system_mime_type = ""
    systemtype_name = ""
    systemtype_attributetype_set = []
    systemtype_relationtype_set = []
    title = ""
    file_st_ids = []
    app_type_of_id = ""
    File = 'False'
    obj_id_ins = ObjectId()

    user_id = int(request.user.id)  # getting django user id
    user_name = unicode(request.user.username)  # getting django user name

    for eachset in app.collection_set:
      app_set = node_collection.find_one({"_id":eachset})
      app_collection_set.append({"id": str(app_set._id), "name": app_set.name})

    if app_set_id:
        systemtype = node_collection.find_one({"_id":ObjectId(app_set_id)})
        systemtype_name = systemtype.name
        title = systemtype_name + " - new"
        for each in systemtype.attribute_type_set:
            systemtype_attributetype_set.append({"type":each.name,"type_id":str(each._id),"value":each.data_type})

        for eachrt in systemtype.relation_type_set:
            # object_type = [ {"name":rtot.name, "id":str(rtot._id)} for rtot in node_collection.find({'member_of': {'$all': [ node_collection.find_one({"_id":eachrt.object_type[0]})._id]}}) ]
            object_type_cur = node_collection.find({'member_of': {'$in': eachrt.object_type}})
            object_type = []
            for each in object_type_cur:
              object_type.append({"name":each.name, "id":str(each._id)})
            systemtype_relationtype_set.append({"rt_name": eachrt.name, "type_id": str(eachrt._id), "object_type": object_type})

    request_at_dict = {}
    request_rt_dict = {}

    files_sts = ['File','Image','Video']
    if app_set_id:
        app = node_collection.one({'_id':ObjectId(app_set_id)})
        for each in files_sts:
            node_id = node_collection.one({'name':each,'_type':'GSystemType'})._id
            if node_id in app.type_of:
                File = 'True'

    if app_set_instance_id : # at and rt set editing instance
        system = node_collection.find_one({"_id":ObjectId(app_set_instance_id)})
        for eachatset in systemtype_attributetype_set :
            eachattribute = node_collection.find_one({"_type":"GAttribute", "subject":system._id, "attribute_type":ObjectId(eachatset["type_id"])})
            if eachattribute :
                eachatset['database_value'] = eachattribute.object_value
                eachatset['database_id'] = str(eachattribute._id)
            else :
                eachatset['database_value'] = ""
                eachatset['database_id'] = ""
        for eachrtset in systemtype_relationtype_set :

            eachrelation = node_collection.find_one({"_type":"GRelation", "subject":system._id, "relation_type":ObjectId(eachrtset["type_id"])})
            if eachrelation:
                right_subject = node_collection.find_one({"_id":ObjectId(eachrelation.right_subject)})
                eachrtset['database_id'] = str(eachrelation._id)
                eachrtset["database_value"] = right_subject.name
                eachrtset["database_value_id"] = str(right_subject._id)
            else :
                eachrtset['database_id'] = ""
                eachrtset["database_value"] = ""
                eachrtset["database_value_id"] = ""

        tags = ",".join(system.tags)
        content_org = system.content_org
        location = system.location
        system_id = system._id
        system_type = system._type
        if system_type == 'File':
            system_mime_type = system.mime_type
        app_set_instance_name = system.name
        title =  system.name+"-"+"edit"


    if request.method=="POST": # post methods
        tags = request.POST.get("tags","")
        content_org = unicode(request.POST.get("content_org",""))
        name = request.POST.get("name","")
        map_geojson_data = request.POST.get('map-geojson-data') # getting markers
        user_last_visited_location = request.POST.get('last_visited_location') # getting last visited location by user
        file1 = request.FILES.get('file', '')

        for each in systemtype_attributetype_set:
            if request.POST.get(each["type_id"],"") :
                request_at_dict[each["type_id"]] = request.POST.get(each["type_id"],"")
        for eachrtset in systemtype_relationtype_set:
            if request.POST.get(eachrtset["type_id"],""):
                request_rt_dict[eachrtset["type_id"]] = request.POST.get(eachrtset["type_id"],"")

        if File == 'True':
            if file1:
                f = save_file(file1, name, request.user.id, group_id, content_org, tags)
                if obj_id_ins.is_valid(f):
                    newgsystem = node_collection.one({'_id':f})
                else:
                    template = "ndf/custom_template_for_app.html"
                    variable = RequestContext(request, {'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set, "app_set_id":app_set_id, "nodes":nodes, "systemtype_attributetype_set":systemtype_attributetype_set, "systemtype_relationtype_set":systemtype_relationtype_set, "create_new":"yes", "app_set_name":systemtype_name, 'title':title, 'File':File, 'already_uploaded_file':f})
                    return render_to_response(template, variable)
            else:
                newgsystem = node_collection.collection.File()
        else:
            newgsystem = node_collection.collection.GSystem()
        if app_set_instance_id :
            newgsystem = node_collection.find_one({"_id":ObjectId(app_set_instance_id)})

        newgsystem.name = name
        newgsystem.member_of=[ObjectId(app_set_id)]

        if not app_set_instance_id :
            newgsystem.created_by = request.user.id

        newgsystem.modified_by = request.user.id
        newgsystem.status = u"PUBLISHED"

        newgsystem.group_set.append(ObjectId(group_id))

        if tags:
             newgsystem.tags = tags.split(",")

        if content_org:
            usrname = request.user.username
            filename = slugify(newgsystem.name) + "-" + usrname
            # newgsystem.content = org2html(content_org, file_prefix=filename)
            newgsystem.content = unicode(content_org)
            newgsystem.content_org = unicode(content_org)

        # check if map markers data exist in proper format then add it into newgsystem
        if map_geojson_data:
            map_geojson_data = map_geojson_data + ","
            map_geojson_data = list(ast.literal_eval(map_geojson_data))
            newgsystem.location = map_geojson_data
            location = map_geojson_data
        else:
            map_geojson_data = []
            location = []
            newgsystem.location = map_geojson_data

        # check if user_group_location exist in proper format then add it into newgsystem
        if user_last_visited_location:

            user_last_visited_location = list(ast.literal_eval(user_last_visited_location))

            author = node_collection.one({'_type': "GSystemType", 'name': "Author"})
            user_group_location = node_collection.one({'_type': "Author", 'member_of': author._id, 'created_by': user_id, 'name': user_name})

            if user_group_location:
                user_group_location['visited_location'] = user_last_visited_location
                user_group_location.save(groupid=group_id)

        newgsystem.save(groupid=group_id)

        if not app_set_instance_id :
            for key,value in request_at_dict.items():
                attributetype_key = node_collection.find_one({"_id":ObjectId(key)})
                newattribute = triple_collection.collection.GAttribute()
                newattribute.subject = newgsystem._id
                newattribute.attribute_type = attributetype_key._id
                newattribute.object_value = value
                newattribute.save(groupid=group_id)
            for key,value in request_rt_dict.items():
                if key:
                    relationtype_key = node_collection.find_one({"_id":ObjectId(key)})
                if value:
                    right_subject = node_collection.find_one({"_id":ObjectId(value)})
                    newrelation = triple_collection.collection.GRelation()
                    newrelation.subject = newgsystem._id
                    newrelation.relation_type = relationtype_key._id
                    newrelation.right_subject = right_subject._id
                    newrelation.save(groupid=group_id)

        if app_set_instance_id : # editing instance
            for each in systemtype_attributetype_set:
                if each["database_id"]:
                    attribute_instance = node_collection.find_one({"_id":ObjectId(each['database_id'])})
                    attribute_instance.object_value = request.POST.get(each["database_id"],"")
                    attribute_instance.save(groupid=group_id)
                else :
                    if request.POST.get(each["type_id"],""):
                        attributetype_key = node_collection.find_one({"_id":ObjectId(each["type_id"])})
                        newattribute = triple_collection.collection.GAttribute()
                        newattribute.subject = newgsystem._id
                        newattribute.attribute_type = attributetype_key._id
                        newattribute.object_value = request.POST.get(each["type_id"],"")
                        newattribute.save(groupid=group_id)

            for eachrt in systemtype_relationtype_set:
                if eachrt["database_id"]:
                    relation_instance = node_collection.find_one({"_id":ObjectId(eachrt['database_id'])})
                    relation_instance.right_subject = ObjectId(request.POST.get(eachrt["database_id"],""))
                    relation_instance.save(groupid=group_id)
                else :
                    if request.POST.get(eachrt["type_id"],""):
                        relationtype_key = node_collection.find_one({"_id":ObjectId(eachrt["type_id"])})
                        right_subject = node_collection.find_one({"_id":ObjectId(request.POST.get(eachrt["type_id"],""))})
                        newrelation = triple_collection.collection.GRelation()
                        newrelation.subject = newgsystem._id
                        newrelation.relation_type = relationtype_key._id
                        newrelation.right_subject = right_subject._id
                        newrelation.save(groupid=group_id)


        return HttpResponseRedirect(reverse('GAPPS_set', kwargs={'group_id': group_id, 'app_name': app_name, "app_id":app_id, "app_set_id":app_set_id}))

    template = "ndf/custom_template_for_app.html"
    variable = RequestContext(request, {'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set, "app_set_id":app_set_id, "nodes":nodes, "systemtype_attributetype_set":systemtype_attributetype_set, "systemtype_relationtype_set":systemtype_relationtype_set, "create_new":"yes", "app_set_name":systemtype_name, 'title':title, 'File':File, 'tags':tags, "content_org":content_org, "system_id":system_id,"system_type":system_type,"mime_type":system_mime_type, "app_set_instance_name":app_set_instance_name, "app_set_instance_id":app_set_instance_id, 'location':location})
    return render_to_response(template, variable)



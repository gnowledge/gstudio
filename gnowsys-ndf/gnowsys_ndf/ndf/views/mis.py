''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response #, render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

import ast

from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *

from gnowsys_ndf.ndf.views.file import *

collection = get_database()[Node.collection_name]

def mis_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    custom view for custom GAPPS
    """

    if ObjectId.is_valid(group_id) is False :
      group_ins = collection.Node.one({'_type': "Group","name": group_id})
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if group_ins:
        group_id = str(group_ins._id)
      else :
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :
          group_id = str(auth._id)
    else :
      pass

    app = None
    if app_id is None:
      app = collection.Node.one({'_type': "GSystemType", 'name': app_name})
      if app:
        app_id = str(app._id)
    else:
      app = collection.Node.one({'_id': ObjectId(app_id)})

    app_name = app.name 

    app_collection_set = [] 
    atlist = []
    rtlist = []
    
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
    template = ""
    property_display_order = []

    template_prefix = ""
    if app_name == "MIS":
      template_prefix = "mis"
    else:
      template_prefix = "mis_po"

    for eachset in app.collection_set:
      app_collection_set.append(collection.Node.one({"_id":eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))
      # app_set = collection.Node.find_one({"_id":eachset})
      # app_collection_set.append({"id": str(app_set._id), "name": app_set.name, 'type_of'})

    if app_set_id:
      classtype = ""
      app_set_template = "yes"
      template = "ndf/"+template_prefix+"_list.html"

      systemtype = collection.Node.find_one({"_id":ObjectId(app_set_id)})
      systemtype_name = systemtype.name
      title = systemtype_name

      if request.method=="POST":
        search = request.POST.get("search","")
        classtype = request.POST.get("class","")
        nodes = list(collection.Node.find({'name':{'$regex':search, '$options': 'i'},'member_of': {'$all': [systemtype._id]}}))
      else :
        nodes = list(collection.Node.find({'member_of': {'$all': [systemtype._id]},'group_set':{'$all': [ObjectId(group_id)]}}))

      nodes_dict = []
      for each in nodes:
        nodes_dict.append({"id":str(each._id), "name":each.name, "created_by":User.objects.get(id=each.created_by).username, "created_at":each.created_at})
                         
    else :
      app_menu = "yes"
      template = "ndf/"+template_prefix+"_list.html"
      title = app_name

    if app_set_instance_id :
        app_set_instance_template = "yes"
        template = "ndf/"+template_prefix+"_details.html"

        app_set_template = ""
        systemtype_attributetype_set = []
        systemtype_relationtype_set = []
        system = collection.Node.find_one({"_id":ObjectId(app_set_instance_id)})
        systemtype = collection.Node.find_one({"_id":ObjectId(app_set_id)})
        for each in systemtype.attribute_type_set:
            systemtype_attributetype_set.append({"type":each.name,"type_id":str(each._id),"value":each.data_type})
        for each in systemtype.relation_type_set:
            systemtype_relationtype_set.append({"rt_name":each.name,"type_id":str(each._id)})

        for eachatset in systemtype_attributetype_set :
            for eachattribute in collection.Node.find({"_type":"GAttribute", "subject":system._id, "attribute_type.$id":ObjectId(eachatset["type_id"])}):
                atlist.append({"type":eachatset["type"],"type_id":eachatset["type_id"],"value":eachattribute.object_value})
        for eachrtset in systemtype_relationtype_set :
            for eachrelation in collection.Node.find({"_type":"GRelation", "subject":system._id, "relation_type.$id":ObjectId(eachrtset["type_id"])}):
                right_subject = collection.Node.find_one({"_id":ObjectId(eachrelation.right_subject)})
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
                        elif system.structure[field][0] == datetime.datetime:
                            date_list = []
                            for dt in system[field]:
                                date_list.append(dt.strftime("%d/%m/%Y"))
                            display_fields.append((altname, ", ".join(date_list)))
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

    variable = RequestContext(request, {
                                        'groupid':group_id, 'app_name':app_name, 'app_id':app_id,
                                        "app_collection_set":app_collection_set, "app_set_id":app_set_id, 
                                        "nodes":nodes_dict, "app_menu":app_menu, "app_set_template":app_set_template,
                                        "app_set_instance_template":app_set_instance_template, "app_set_name":app_set_name,
                                        "app_set_instance_name":app_set_instance_name, "title":title,
                                        "app_set_instance_atlist":atlist, "app_set_instance_rtlist":rtlist, 
                                        'tags':tags, 'location':location, "content":content, "system_id":system_id,
                                        "system_type":system_type,"mime_type":system_mime_type, "app_set_instance_id":app_set_instance_id,
                                        "node":system, 'group_id':group_id, "property_display_order": property_display_order
                                        })

    return render_to_response(template, variable)
      
@login_required
def mis_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    create new instance of app_set of apps view for custom GAPPS
    """

    if ObjectId.is_valid(group_id) is False :
      group_ins = collection.Node.one({'_type': "Group","name": group_id})
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if group_ins:
        group_id = str(group_ins._id)
      else :
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :
          group_id = str(auth._id)
    else :
      pass

    app = None
    if app_id is None:
      app = collection.Node.one({'_type': "GSystemType", 'name': app_name})
      if app:
        app_id = str(app._id)
    else:
      app = collection.Node.one({'_id': ObjectId(app_id)})

    app_name = app.name 

    # app_name = "mis"
    app_collection_set = [] 
    # app = collection.Node.find_one({"_id":ObjectId(app_id)})
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

    template_prefix = ""
    if app_name == "MIS":
      template_prefix = "mis"
    else:
      template_prefix = "mis_po"

    user_id = int(request.user.id)  # getting django user id
    user_name = unicode(request.user.username)  # getting django user name

    for eachset in app.collection_set:
      app_collection_set.append(collection.Node.one({"_id":eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))
      # app_set = collection.Node.find_one({"_id":eachset})
      # app_collection_set.append({"id": str(app_set._id), "name": app_set.name, 'type_of'})

    if app_set_id:
        systemtype = collection.Node.find_one({"_id":ObjectId(app_set_id)})
        systemtype_name = systemtype.name
        title = systemtype_name + " - new"
        for each in systemtype.attribute_type_set:
            systemtype_attributetype_set.append({"type":each.name,"type_id":str(each._id),"value":each.data_type})

        for eachrt in systemtype.relation_type_set:
            # object_type = [ {"name":rtot.name, "id":str(rtot._id)} for rtot in collection.Node.find({'member_of': {'$all': [ collection.Node.find_one({"_id":eachrt.object_type[0]})._id]}}) ]
            object_type_cur = collection.Node.find({'member_of': {'$in': eachrt.object_type}})
            object_type = []
            for each in object_type_cur:
              object_type.append({"name":each.name, "id":str(each._id)})
            systemtype_relationtype_set.append({"rt_name": eachrt.name, "type_id": str(eachrt._id), "object_type": object_type})
    
    request_at_dict = {}
    request_rt_dict = {}

    files_sts = ['File','Image','Video']
    if app_set_id:
        app = collection.Node.one({'_id':ObjectId(app_set_id)})
        for each in files_sts:
            node_id = collection.Node.one({'name':each,'_type':'GSystemType'})._id
            if node_id in app.type_of:
                File = 'True'

    if app_set_instance_id : # at and rt set editing instance
        system = collection.Node.find_one({"_id":ObjectId(app_set_instance_id)})
        for eachatset in systemtype_attributetype_set :
            eachattribute = collection.Node.find_one({"_type":"GAttribute", "subject":system._id, "attribute_type.$id":ObjectId(eachatset["type_id"])})
            if eachattribute :
                eachatset['database_value'] = eachattribute.object_value
                eachatset['database_id'] = str(eachattribute._id)
            else :
                eachatset['database_value'] = ""
                eachatset['database_id'] = ""
        for eachrtset in systemtype_relationtype_set :
            eachrelation = collection.Node.find_one({"_type":"GRelation", "subject":system._id, "relation_type.$id":ObjectId(eachrtset["type_id"])})       
            if eachrelation:
                right_subject = collection.Node.find_one({"_id":ObjectId(eachrelation.right_subject)})
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
                    newgsystem = collection.Node.one({'_id':f})
                else:
                    template = "ndf/mis_list.html"
                    variable = RequestContext(request, {'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set, "app_set_id":app_set_id, "nodes":nodes, "systemtype_attributetype_set":systemtype_attributetype_set, "systemtype_relationtype_set":systemtype_relationtype_set, "create_new":"yes", "app_set_name":systemtype_name, 'title':title, 'File':File, 'already_uploaded_file':f})
                    return render_to_response(template, variable)
            else:
                newgsystem = collection.File()
        else:
            newgsystem = collection.GSystem()
        if app_set_instance_id :
            newgsystem = collection.Node.find_one({"_id":ObjectId(app_set_instance_id)})

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
            newgsystem.content = org2html(content_org, file_prefix=filename)
            newgsystem.content_org = content_org

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

            author = collection.Node.one({'_type': "GSystemType", 'name': "Author"})
            user_group_location = collection.Node.one({'_type': "Author", 'member_of': author._id, 'created_by': user_id, 'name': user_name})

            if user_group_location:
                user_group_location['visited_location'] = user_last_visited_location
                user_group_location.save()

        newgsystem.save()

        if not app_set_instance_id :
            for key,value in request_at_dict.items():
                attributetype_key = collection.Node.find_one({"_id":ObjectId(key)})
                newattribute = collection.GAttribute()
                newattribute.subject = newgsystem._id
                newattribute.attribute_type = attributetype_key
                newattribute.object_value = value
                newattribute.save()
            for key,value in request_rt_dict.items():
                if key:
                    relationtype_key = collection.Node.find_one({"_id":ObjectId(key)})
                if value:
                    right_subject = collection.Node.find_one({"_id":ObjectId(value)})
                    newrelation = collection.GRelation()
                    newrelation.subject = newgsystem._id
                    newrelation.relation_type = relationtype_key
                    newrelation.right_subject = right_subject._id
                    newrelation.save()

        if app_set_instance_id : # editing instance
            for each in systemtype_attributetype_set:
                if each["database_id"]:
                    attribute_instance = collection.Node.find_one({"_id":ObjectId(each['database_id'])})
                    attribute_instance.object_value = request.POST.get(each["database_id"],"")
                    attribute_instance.save()
                else :
                    if request.POST.get(each["type_id"],""):
                        attributetype_key = collection.Node.find_one({"_id":ObjectId(each["type_id"])})
                        newattribute = collection.GAttribute()
                        newattribute.subject = newgsystem._id
                        newattribute.attribute_type = attributetype_key
                        newattribute.object_value = request.POST.get(each["type_id"],"")
                        newattribute.save()

            for eachrt in systemtype_relationtype_set:
                if eachrt["database_id"]:
                    relation_instance = collection.Node.find_one({"_id":ObjectId(eachrt['database_id'])})
                    relation_instance.right_subject = ObjectId(request.POST.get(eachrt["database_id"],""))
                    relation_instance.save()
                else :
                    if request.POST.get(eachrt["type_id"],""):
                        relationtype_key = collection.Node.find_one({"_id":ObjectId(eachrt["type_id"])})
                        right_subject = collection.Node.find_one({"_id":ObjectId(request.POST.get(eachrt["type_id"],""))})
                        newrelation = collection.GRelation()
                        newrelation.subject = newgsystem._id
                        newrelation.relation_type = relationtype_key
                        newrelation.right_subject = right_subject._id
                        newrelation.save()
        

        return HttpResponseRedirect(reverse(template_prefix+'_app_detail', kwargs={'group_id': group_id, 'app_name': app_name, "app_id":app_id, "app_set_id":app_set_id}))
    
    template = "ndf/"+template_prefix+"_create_edit.html"
    variable = RequestContext(request, {'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set, "app_set_id":app_set_id, "nodes":nodes, "systemtype_attributetype_set":systemtype_attributetype_set, "systemtype_relationtype_set":systemtype_relationtype_set, "create_new":"yes", "app_set_name":systemtype_name, 'title':title, 'File':File, 'tags':tags, "content_org":content_org, "system_id":system_id,"system_type":system_type,"mime_type":system_mime_type, "app_set_instance_name":app_set_instance_name, "app_set_instance_id":app_set_instance_id, 'location':location})
    return render_to_response(template, variable)
      
 

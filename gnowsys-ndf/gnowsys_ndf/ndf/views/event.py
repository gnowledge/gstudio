''' -- imports from python libraries -- '''
import os
import ast
from datetime import datetime

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response #, render  uncomment when to use
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation

collection = get_database()[Node.collection_name]

def event_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    custom view for custom GAPPS
    """
    print "\n Found event_detail n gone inn this...\n\n"

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
    default_template = ""
    property_display_order = []
    events_arr = []

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
      template = "ndf/event_list.html"
      default_template = "ndf/"+template_prefix+"_list.html"
      # print "\n template (if): ", template, "\n"

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
      template = "ndf/event_list.html"
      default_template = "ndf/"+template_prefix+"_list.html"
      # print "\n template: ", template, "\n"
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

        # array of dict for events ---------------------
                
        if system.has_key('organiser_of_event') and len(system.organiser_of_event): # gives list of events

            for event in system.organiser_of_event:
                event.get_neighbourhood(event.member_of)
                
                tempdict = {}
                tempdict['title'] = event.name
                
                if event.start_time and len(event.start_time) == 16:
                    dt = datetime.datetime.strptime(event.start_time , '%m/%d/%Y %H:%M')
                    tempdict['start'] = dt
                if event.end_time and len(event.end_time) == 16:
                    dt = datetime.datetime.strptime(event.end_time , '%m/%d/%Y %H:%M')
                    tempdict['end'] = dt
                tempdict['id'] = str(event._id)
                events_arr.append(tempdict)

        elif system.has_key('event_organised_by'): # gives list of colleges/host of events

            for host in system.event_organised_by:
                host.get_neighbourhood(host.member_of)

                tempdict = {}
                tempdict['title'] = host.name

                if system.start_time and len(system.start_time) == 16:
                    dt = datetime.datetime.strptime(system.start_time , '%m/%d/%Y %H:%M')
                    tempdict['start'] = dt
                if system.end_time and len(system.start_time) == 16:
                    dt = datetime.datetime.strptime(system.end_time , '%m/%d/%Y %H:%M')
                    tempdict['end'] = dt
                
                tempdict['id'] = str(host._id)
                events_arr.append(tempdict)

        # print json.dumps(events_arr)

        # END --- array of dict for events ---------------------

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

        # print "\n app_set_instance_name: ", app_set_instance_name
        # print "\n app_set_name: ", app_set_name

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
                                        "node":system, 'group_id':group_id, "property_display_order": property_display_order,
                                        "events_arr":events_arr
                                        })
    # print "\n template (finally): ", template, "\n"

    try:
        # print "\n template-list: ", [template, default_template]
        # template = "ndf/fgh.html"
        # default_template = "ndf/dsfjhk.html"
        return render_to_response([template, default_template], variable)
    
    except TemplateDoesNotExist as tde:
        # print "\n ", tde
        error_message = "\n EventDetailViewError: " + str(tde) + " not found !!!\n"
        raise Http404(error_message)
    
    except Exception as e:
        error_message = "\n EventDetailViewError: " + str(e) + " !!!\n"
        raise Exception(error_message)
      
@login_required
def event_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  Creates/Modifies document of given event-type.
  """
  print "\n Found event_create_edit n gone inn this...\n\n"

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
  app_set = ""
  app_collection_set = []
  title = ""

  event_gst = None
  event_gs = None

  property_order_list = []

  template_prefix = ""
  if app_name == "MIS":
    template_prefix = "mis"
  else:
    template_prefix = "mis_po"

  for eachset in app.collection_set:
    app_collection_set.append(collection.Node.one({"_id":eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))

  if app_set_id:
    event_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    title = event_gst.name
    # print "\n event_gst:\n", event_gst, "\n"
    event_gs = collection.GSystem()
    event_gs.member_of.append(event_gst._id)

  if app_set_instance_id:
    event_gs = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})

  property_order_list = event_gs.property_order
  # print "\n property_order_list: ", property_order_list, "\n"
  
  # print "\n event_gs: \n", event_gs, "\n"
  
  if request.method == "POST":
    # [A] Save event-node's base-field(s)
    # print "\n Going before....", type(event_gs), "\n event_gs.keys(): ", event_gs.keys()
    get_node_common_fields(request, event_gs, group_id, event_gst)
    # print "\n Going after....", type(event_gs), "\n event_gs.keys(): ", event_gs.keys()
    # print "\n event_gs: \n", event_gs.keys()
    # for k, v in event_gs.items():
    #   print "\n ", k, " -- ", v
    event_gs.save()
    print "\n Event: ", event_gs._id, " -- ", event_gs.name, "\n"
  
    # [B] Store AT and/or RT field(s) of given event-node (i.e., event_gs)
    for tab_details in property_order_list:
      print "\n "
      for field_set in tab_details[1]:
        # field_set pattern -- [field_set[0]:node_structure, field_set[1]:field_base/AT/RT_instance, field_set[2]:node_value]
        # print " ", field_set[1]["name"], " -- ", type(field_set[1]), " -- ", (type(field_set[1]) in [AttributeType, RelationType])

        # * Fetch only Attribute field(s) / Relation field(s)
        field_instance = field_set[1]
        field_instance_type = type(field_instance)
        if field_instance_type in [AttributeType, RelationType]:

          if field_instance["name"] == "attendees":
            continue

          # 1) Fetch corresponding AT/RT-fields value from request object
          field_value = request.POST[field_instance["name"]]
          # print " ", field_instance["name"], " -- ", field_value

          field_data_type = field_set[0][field_instance["name"]]
          # print " --> ", field_set[0][field_instance["name"]], " -- ", type(field_data_type)

          # 2) Parse fetched-value depending upon AT/RT--fields' data-type
          if field_instance_type == AttributeType:
            field_instance_type = "GAttribute"
            field_value = parse_template_data(field_data_type, field_value, date_format_string="%m/%d/%Y %H:%M")
            # print "\n ", type(collection.AttributeType(field_instance)), " -- \n", collection.AttributeType(field_instance)
            event_gs_triple_instance = create_gattribute(event_gs._id, collection.AttributeType(field_instance), field_value)

            print "\n event_gs_triple_instance: ", event_gs_triple_instance._id, " -- ", event_gs_triple_instance.name

          else:
            field_instance_type = "GRelation"
            field_value = parse_template_data(field_data_type, field_value, field_instance=field_instance, date_format_string="%m/%d/%Y %H:%M")
            # print "\n ", type(collection.AttributeType(field_instance)), " -- \n", collection.AttributeType(field_instance)
            event_gs_triple_instance = create_grelation(event_gs._id, collection.RelationType(field_instance), field_value)

            print "\n event_gs_triple_instance: ", event_gs_triple_instance._id, " -- ", event_gs_triple_instance.name
          # print "\n ", field_instance["name"], " -- ", field_value, " -- ", type(field_value), "\n"

          # 3) Create an empty corresponding triple's instance
          # event_gs_triple_instance = eval("collection." + field_instance_type)()
          # print " ", field_instance["name"], " -- event triple keys: ", event_gs_triple_instance.keys()
          
          # if type(field_data_type) == type:
          #   # 4.1) AT-field identified
          #   field_data_type = field_data_type.__name__
          #   # print " (if)--> ", field_data_type, (field_data_type == "datetime"), "\n"

          #   if field_data_type == "datetime":
          #     if field_value:
          #       field_value = datetime.strptime(field_value, "%m/%d/%Y %H:%M")
          #     # print "\n parsed field_value: ", field_value

          # else:
          #   # 4.2) RT-field identified
          #   field_data_type = field_data_type.__str__()
          #   # print " (else)--> ", field_data_type, "\n"
          #   print "\n ", field_instance["name"], " -- ", field_value
          #   field_value = collection.Triple.one({'_id': ObjectId(field_value), 'member_of': {'$in': field_instance["object_type"]}})
          #   if field_value:
          #     print "\n ", field_value._id, " -- ", field_value.name


    # return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': page_node._id }))
  
  template = "ndf/event_create_edit.html"
  default_template = "ndf/"+template_prefix+"_create_edit.html"
  context_variables = { 'groupid': group_id, 
                        'app_id': app_id, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'property_order_list': property_order_list
                      }

  if app_set_instance_id:
    context_variables['node'] = event_gs

  try:
    # print "\n template-list: ", [template, default_template]
    # template = "ndf/fgh.html"
    # default_template = "ndf/dsfjhk.html"
    return render_to_response([template, default_template], 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    # print "\n ", tde
    error_message = "\n EventCreateEditViewError: " + str(tde) + " not found !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n EventCreateEditViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)

  # request_at_dict = {}
  # request_rt_dict = {}

  # files_sts = ['File','Image','Video']
  # if app_set_id:
  #     app = collection.Node.one({'_id':ObjectId(app_set_id)})
  #     for each in files_sts:
  #         node_id = collection.Node.one({'name':each,'_type':'GSystemType'})._id
  #         if node_id in app.type_of:
  #             File = 'True'

  # if app_set_instance_id : # at and rt set editing instance
  #     system = collection.Node.find_one({"_id":ObjectId(app_set_instance_id)})
  #     for eachatset in systemtype_attributetype_set :
  #         eachattribute = collection.Node.find_one({"_type":"GAttribute", "subject":system._id, "attribute_type.$id":ObjectId(eachatset["type_id"])})
  #         if eachattribute :
  #             eachatset['database_value'] = eachattribute.object_value
  #             eachatset['database_id'] = str(eachattribute._id)
  #         else :
  #             eachatset['database_value'] = ""
  #             eachatset['database_id'] = ""
  #     for eachrtset in systemtype_relationtype_set :
  #         eachrelation = collection.Node.find_one({"_type":"GRelation", "subject":system._id, "relation_type.$id":ObjectId(eachrtset["type_id"])})       
  #         if eachrelation:
  #             right_subject = collection.Node.find_one({"_id":ObjectId(eachrelation.right_subject)})
  #             eachrtset['database_id'] = str(eachrelation._id)
  #             eachrtset["database_value"] = right_subject.name
  #             eachrtset["database_value_id"] = str(right_subject._id)
  #         else :
  #             eachrtset['database_id'] = ""
  #             eachrtset["database_value"] = ""
  #             eachrtset["database_value_id"] = ""

  #     tags = ",".join(system.tags)
  #     content_org = system.content_org
  #     location = system.location
  #     system_id = system._id
  #     system_type = system._type
  #     if system_type == 'File':
  #         system_mime_type = system.mime_type
  #     app_set_instance_name = system.name
  #     title =  system.name+"-"+"edit"

      
  # if request.method=="POST": # post methods
  #     tags = request.POST.get("tags","")
  #     content_org = unicode(request.POST.get("content_org",""))
  #     name = request.POST.get("name","")
  #     map_geojson_data = request.POST.get('map-geojson-data') # getting markers
  #     user_last_visited_location = request.POST.get('last_visited_location') # getting last visited location by user
  #     file1 = request.FILES.get('file', '')

  #     for each in systemtype_attributetype_set:
  #         if request.POST.get(each["type_id"],"") :
  #             request_at_dict[each["type_id"]] = request.POST.get(each["type_id"],"")
  #     for eachrtset in systemtype_relationtype_set:
  #         if request.POST.get(eachrtset["type_id"],""):
  #             request_rt_dict[eachrtset["type_id"]] = request.POST.get(eachrtset["type_id"],"")
      
  #     if File == 'True':
  #         if file1:
  #             f = save_file(file1, name, request.user.id, group_id, content_org, tags)
  #             if obj_id_ins.is_valid(f):
  #                 newgsystem = collection.Node.one({'_id':f})
  #             else:
  #                 template = "ndf/mis_list.html"
  #                 variable = RequestContext(request, {'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set, "app_set_id":app_set_id, "nodes":nodes, "systemtype_attributetype_set":systemtype_attributetype_set, "systemtype_relationtype_set":systemtype_relationtype_set, "create_new":"yes", "app_set_name":systemtype_name, 'title':title, 'File':File, 'already_uploaded_file':f})
  #                 return render_to_response(template, variable)
  #         else:
  #             newgsystem = collection.File()
  #     else:
  #         newgsystem = collection.GSystem()
  #     if app_set_instance_id :
  #         newgsystem = collection.Node.find_one({"_id":ObjectId(app_set_instance_id)})

  #     newgsystem.name = name
  #     newgsystem.member_of=[ObjectId(app_set_id)]
      
  #     if not app_set_instance_id :
  #         newgsystem.created_by = request.user.id
      
  #     newgsystem.modified_by = request.user.id
  #     newgsystem.status = u"PUBLISHED"

  #     newgsystem.group_set.append(ObjectId(group_id))

  #     if tags:
  #          newgsystem.tags = tags.split(",")

  #     if content_org:
  #         usrname = request.user.username
  #         filename = slugify(newgsystem.name) + "-" + usrname
  #         newgsystem.content = org2html(content_org, file_prefix=filename)
  #         newgsystem.content_org = content_org

  #     # check if map markers data exist in proper format then add it into newgsystem
  #     if map_geojson_data:
  #         map_geojson_data = map_geojson_data + ","
  #         map_geojson_data = list(ast.literal_eval(map_geojson_data))
  #         newgsystem.location = map_geojson_data
  #         location = map_geojson_data
  #     else:
  #         map_geojson_data = []
  #         location = []
  #         newgsystem.location = map_geojson_data

  #     # check if user_group_location exist in proper format then add it into newgsystem
  #     if user_last_visited_location:
  
  #         user_last_visited_location = list(ast.literal_eval(user_last_visited_location))

  #         author = collection.Node.one({'_type': "GSystemType", 'name': "Author"})
  #         user_group_location = collection.Node.one({'_type': "Author", 'member_of': author._id, 'created_by': user_id, 'name': user_name})

  #         if user_group_location:
  #             user_group_location['visited_location'] = user_last_visited_location
  #             user_group_location.save()

  #     newgsystem.save()

  #     if not app_set_instance_id :
  #         for key,value in request_at_dict.items():
  #             attributetype_key = collection.Node.find_one({"_id":ObjectId(key)})
  #             newattribute = collection.GAttribute()
  #             newattribute.subject = newgsystem._id
  #             newattribute.attribute_type = attributetype_key
  #             newattribute.object_value = value
  #             newattribute.save()
  #         for key,value in request_rt_dict.items():
  #             if key:
  #                 relationtype_key = collection.Node.find_one({"_id":ObjectId(key)})
  #             if value:
  #                 right_subject = collection.Node.find_one({"_id":ObjectId(value)})
  #                 newrelation = collection.GRelation()
  #                 newrelation.subject = newgsystem._id
  #                 newrelation.relation_type = relationtype_key
  #                 newrelation.right_subject = right_subject._id
  #                 newrelation.save()

  #     if app_set_instance_id : # editing instance
  #         for each in systemtype_attributetype_set:
  #             if each["database_id"]:
  #                 attribute_instance = collection.Node.find_one({"_id":ObjectId(each['database_id'])})
  #                 attribute_instance.object_value = request.POST.get(each["database_id"],"")
  #                 attribute_instance.save()
  #             else :
  #                 if request.POST.get(each["type_id"],""):
  #                     attributetype_key = collection.Node.find_one({"_id":ObjectId(each["type_id"])})
  #                     newattribute = collection.GAttribute()
  #                     newattribute.subject = newgsystem._id
  #                     newattribute.attribute_type = attributetype_key
  #                     newattribute.object_value = request.POST.get(each["type_id"],"")
  #                     newattribute.save()

  #         for eachrt in systemtype_relationtype_set:
  #             if eachrt["database_id"]:
  #                 relation_instance = collection.Node.find_one({"_id":ObjectId(eachrt['database_id'])})
  #                 relation_instance.right_subject = ObjectId(request.POST.get(eachrt["database_id"],""))
  #                 relation_instance.save()
  #             else :
  #                 if request.POST.get(eachrt["type_id"],""):
  #                     relationtype_key = collection.Node.find_one({"_id":ObjectId(eachrt["type_id"])})
  #                     right_subject = collection.Node.find_one({"_id":ObjectId(request.POST.get(eachrt["type_id"],""))})
  #                     newrelation = collection.GRelation()
  #                     newrelation.subject = newgsystem._id
  #                     newrelation.relation_type = relationtype_key
  #                     newrelation.right_subject = right_subject._id
  #                     newrelation.save()
      

  #     return HttpResponseRedirect(reverse(template_prefix+'_app_detail', kwargs={'group_id': group_id, 'app_name': app_name, "app_id":app_id, "app_set_id":app_set_id}))

  # template = "ndf/"+template_prefix+"_create_edit.html"
  # variable = RequestContext(request, {'groupid':group_id, 
  #                                     'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set, 
  #                                     "app_set_id":app_set_id, "nodes":nodes, 
  #                                     "systemtype_attributetype_set":systemtype_attributetype_set, "systemtype_relationtype_set":systemtype_relationtype_set, 
  #                                     "app_set_name":systemtype_name, 'title':title, 
  #                                     'File':File, 'tags':tags, "content_org":content_org, 'location':location,
  #                                     "system_id":system_id,"system_type":system_type,"mime_type":system_mime_type, 
  #                                     "app_set_instance_name":app_set_instance_name, "app_set_instance_id":app_set_instance_id})
  # return render_to_response(template, variable)

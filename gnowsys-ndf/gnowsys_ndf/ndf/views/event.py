''' -- imports from python libraries -- '''
# from datetime import datetime

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect #, HttpResponse uncomment when to use
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response #, render  uncomment when to use
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation

collection = get_database()[Node.collection_name]
def event(request, group_id):
 
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
 #view written just to show the landing page of the events
 Group_type=collection.Node.one({'_id':ObjectId(group_id)})
 Group_name=collection.Node.one({'_type':'GSystem','name':unicode(Group_type.name)})
 Eventtype='Eventtype'
 if Group_name:
      if (any( unicode('has_group') in d for d in Group_name.relation_set)) == True:
           Eventtype='CollegeEvents'     
      else:
           Eventtype='Eventtype'
      
 Glisttype=collection.Node.find({"name":"GList"})
 #bug
 #Event_Types = collection.Node.one({"member_of":ObjectId(Glisttype[0]["_id"]),"name":"Eventtype"},{'collection_set': 1})
 #buggy
 Event_Types = collection.Node.one({"member_of":ObjectId(Glisttype[0]["_id"]),"name":unicode(Eventtype)},{'collection_set': 1})
 
 app_collection_set=[]
 if Event_Types:
    for eachset in Event_Types.collection_set:
          app_collection_set.append(collection.Node.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      
 return render_to_response('ndf/event.html',{'app_collection_set':app_collection_set,
                                             'groupid':group_id,
                                             'group_id':group_id,
                                             'group_name':group_id
                                                        
                                            },
                              context_instance = RequestContext(request)
                          )


def event_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None):
  """
  View for handling Event and it's sub-types detail-view
  """
  auth = None
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
  '''if app_id is None:
    app = collection.Node.one({'_type': "GSystemType", 'name': app_name})
    if app:
      app_id = str(app._id)
  else:'''
  app = collection.Node.one({'_id': ObjectId(app_id)})

  #app_name = app.name 

  app_set = ""
  app_collection_set = []
  title = ""

  event_gst = None
  event_gs = None

  property_order_list = []

  #template_prefix = "mis"

  if request.user:
    if auth is None:
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username)})
  '''  agency_type = auth.agency_type
    Event_Types = collection.Node.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
    if Event_Types:
      for eachset in Event_Types.collection_set:
        app_collection_set.append(collection.Node.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      
  '''
  # for eachset in app.collection_set:
  #   app_collection_set.append(collection.Node.one({"_id":eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))
  Group_type=collection.Node.one({'_id':ObjectId(group_id)})
  Group_name=collection.Node.one({'_type':'GSystem','name':unicode(Group_type.name)})
  Eventtype='Eventtype'
  if Group_name:
      if (any( unicode('has_group') in d for d in Group_name.relation_set)) == True:
           Eventtype='CollegeEvents'     
      else:
           Eventtype='Eventtype'

  Glisttype=collection.Node.find({"name":"GList"})
  Event_Types = collection.Node.one({"member_of":ObjectId(Glisttype[0]["_id"]),"name":Eventtype},{'collection_set': 1})
  app_collection_set=[]
  if Event_Types:
    for eachset in Event_Types.collection_set:
          app_collection_set.append(collection.Node.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      

  
  nodes = None
  if app_set_id:
    event_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    title = event_gst.name
  
    template = "ndf/event_list.html"

    if request.method=="POST":
      search = request.POST.get("search","")
      classtype = request.POST.get("class","")
      # nodes = list(collection.Node.find({'name':{'$regex':search, '$options': 'i'},'member_of': {'$all': [event_gst._id]}}))
      nodes = collection.Node.find({'member_of': event_gst._id, 'name': {'$regex': search, '$options': 'i'}})
    else:
      nodes = collection.Node.find({'member_of': event_gst._id, 'group_set': ObjectId(group_id)})
      
  node = None
  marks_list=[]
  Assesslist=[]
  batch=[]
  if app_set_instance_id :
    template = "ndf/event_details.html"

    node = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    # property_order_list = get_property_order_with_value(node)
    # print "\n property_order_list: ", property_order_list, "\n"
    
    node.get_neighbourhood(node.member_of)
    course=[]
    val=False
    for i in node.relation_set:
       if unicode('event_has_batch') in i.keys():
            batch=collection.Node.one({'_type':"GSystem",'_id':ObjectId(i['event_has_batch'][0])})
            batch_relation=collection.Node.one({'_type':"GSystem",'_id':ObjectId(batch._id)},{'relation_set':1})
            for i in batch_relation['relation_set']:
               if  unicode('has_course') in i.keys(): 
                   announced_course =collection.Node.one({"_type":"GSystem",'_id':ObjectId(i['has_course'][0])})
                   for i in  announced_course.relation_set:
                      if unicode('announced_for') in i.keys():
                            course=collection.Node.one({"_type":"GSystem",'_id':ObjectId(i['announced_for'][0])})
                             
            batch=batch.name
            
       #   print "\n node.keys(): ", node.keys(), "\n"
  # default_template = "ndf/"+template_prefix+"_create_edit.html"
  context_variables = { 'groupid': group_id, 
                        'app_id': app_id,'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'nodes': nodes, 'node': node,
                        'event_gst':event_gst.name
                        # 'property_order_list': property_order_list
                      }

  if batch :
      context_variables.update({'batch':batch}) 
      if course:
          context_variables.update({'course':course})
  else  :    
      context_variables.update({'Assesslist':Assesslist}) 
    # print "\n template-list: ", [template, default_template]
    # template = "ndf/fgh.html"
    # default_template = "ndf/dsfjhk.html"
    # return render_to_response([template, default_template], 
  return render_to_response(template, 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  
      
@login_required
def event_create_edit(request, group_id, app_set_id=None, app_set_instance_id=None):
  """
  View for handling Event and it's sub-types create-edit-view
  """
  auth = None
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
  ''' 
  app = None
  if app_id is None:
    app = collection.Node.one({'_type': "GSystemType", 'name': app_name})
    if app:
      app_id = str(app._id)
  else:
    app = collection.Node.one({'_id': ObjectId(app_id)})

  app_name = app.name 
  '''
  app_set = ""
  app_collection_set = []
  title = ""

  event_gst = None
  event_gs = None

  property_order_list = []

  template_prefix = "mis"

  '''if request.user:
    if auth is None:
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username)})
    agency_type = auth.agency_type
    Event_Types = collection.Node.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
    if Event_Types:
      for eachset in Event_Types.collection_set:
        app_collection_set.append(collection.Node.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      
  '''
  Group_type=collection.Node.one({'_id':ObjectId(group_id)})
  Group_name=collection.Node.one({'_type':'GSystem','name':unicode(Group_type.name)})
  Eventtype='Eventtype'
  if Group_name:

      if (any( unicode('has_group') in d for d in Group_name.relation_set)) == True:
           Eventtype='CollegeEvents'     
      else:
           Eventtype='Eventtype'

  Glisttype=collection.Node.find({"name":"GList"})
  Event_Types = collection.Node.one({"member_of":ObjectId(Glisttype[0]["_id"]),"name":Eventtype},{'collection_set': 1})
  app_collection_set=[]
  if Event_Types:
    for eachset in Event_Types.collection_set:
          app_collection_set.append(collection.Node.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      

  # for eachset in app.collection_set:
  #   app_collection_set.append(collection.Node.one({"_id":eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))
  iteration=request.POST.get("iteration","")
  for i in range(1):
   if app_set_id:
     event_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
     title = event_gst.name
     event_gs = collection.GSystem()
     event_gs.member_of.append(event_gst._id)

   if app_set_instance_id:
     event_gs = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
   property_order_list = get_property_order_with_value(event_gs)#.property_order
  
   if request.method == "POST":
    # [A] Save event-node's base-field(s)
    # print "\n Going before....", type(event_gs), "\n event_gs.keys(): ", event_gs.keys()
    # get_node_common_fields(request, event_gs, group_id, event_gst)
    # print "\n Going after....", type(event_gs), "\n event_gs.keys(): ", event_gs.keys()
    # print "\n event_gs: \n", event_gs.keys()
    # for k, v in event_gs.items():
    #   print "\n ", k, " -- ", v
    is_changed = get_node_common_fields(request, event_gs, group_id, event_gst)
    if is_changed:
      # Remove this when publish button is setup on interface
      event_gs.status = u"PUBLISHED"
    if (request.POST.get("name","")) == "":
        name=slugify(request.POST.get("course_type",""))+ "--"+ slugify(request.POST.get("course_name",""))+ "--"+slugify           (request.POST.get("Module_name",""))+ "--"+slugify(request.POST.get("Session",""))
        event_gs.name=name 
    
    event_gs.save(is_changed=is_changed)
    # print "\n Event: ", event_gs._id, " -- ", event_gs.name, "\n"
  
    # [B] Store AT and/or RT field(s) of given event-node (i.e., event_gs)
    for tab_details in property_order_list:
      for field_set in tab_details[1]:
        # field_set pattern -- {[field_set[0]:node_structure, field_set[1]:field_base/AT/RT_instance{'_id':, 'name':, 'altnames':}, field_set[2]:node_value]}
        # field_set pattern -- {'_id', 'data_type', 'name', 'altnames', 'value'}
        # print " ", field_set["name"]

        # * Fetch only Attribute field(s) / Relation field(s)
        if field_set.has_key('_id'):
          field_instance = collection.Node.one({'_id': field_set['_id']})
          field_instance_type = type(field_instance)

          if field_instance_type in [AttributeType, RelationType]:
            
            if field_instance["name"] == "attendees":
              continue

            field_data_type = field_set['data_type']

            # Fetch field's value depending upon AT/RT and Parse fetched-value depending upon that field's data-type
            if field_instance_type == AttributeType:
              if "File" in field_instance["validators"]:
                # Special case: AttributeTypes that require file instance as it's value in which case file document's ObjectId is used
                
                if field_instance["name"] in request.FILES:
                  field_value = request.FILES[field_instance["name"]]
                  
                else:
                  field_value = ""
                
                # Below 0th index is used because that function returns tuple(ObjectId, bool-value)
                if field_value != '' and field_value != u'':
                  file_name = event_gs.name + " -- " + field_instance["altnames"]
                  content_org = ""
                  tags = ""
                  field_value = save_file(field_value, file_name, request.user.id, group_id, content_org, tags, oid=True)[0]

              if "date_month_day_year" in field_instance["validators"]:
                     if i>0:
                       field_value=request.POST.get(field_instance["name"]+"_"+"1")  
                     else:
                        field_value = request.POST[field_instance["name"]]
                        
              else:
                # Other AttributeTypes 
                field_value = request.POST[field_instance["name"]]
              # field_instance_type = "GAttribute"
              # print "\n Parsing data for: ", field_instance["name"]
              if field_instance["name"] in ["12_passing_year", "degree_passing_year"]: #, "registration_year"]:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%Y")
              elif field_instance["name"] in ["dob", "registration_date"]:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y")
              else:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y %H:%M")
              
              if field_value:
                event_gs_triple_instance = create_gattribute(event_gs._id, collection.AttributeType(field_instance), field_value)
                # print "\n event_gs_triple_instance: ", event_gs_triple_instance._id, " -- ", event_gs_triple_instance.name

            else:
              field_value_list = request.POST.getlist(field_instance["name"])
              # field_instance_type = "GRelation"
              #code for creation of relation Session of 
              for i, field_value in enumerate(field_value_list):
                field_value = parse_template_data(field_data_type, field_value, field_instance=field_instance, date_format_string="%d/%m/%Y %H:%M")
                field_value_list[i] = field_value

              event_gs_triple_instance = create_grelation(event_gs._id, collection.RelationType(field_instance), field_value_list)
              # if isinstance(event_gs_triple_instance, list):
              #   print "\n"
              #   for each in event_gs_triple_instance:
              #     print " event_gs_triple_instance: ", each._id, " -- ", each.name
              #   print "\n"

              # else:
              #   print "\n event_gs_triple_instance: ", event_gs_triple_instance._id, " -- ", event_gs_triple_instance.name
    # return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': page_node._id }))
    '''return HttpResponseRedirect(reverse(app_name.lower()+":"+template_prefix+'_app_detail', kwargs={'group_id': group_id, "app_id":app_id, "app_set_id":app_set_id}))'''
    if i==0:
     return HttpResponseRedirect(reverse('event_app_instance_detail', kwargs={'group_id': group_id,"app_set_id":app_set_id,"app_set_instance_id":event_gs._id}))
  event_gs.get_neighbourhood(event_gs.member_of)
  course=[]
  val=False
  for i in event_gs.relation_set:
       if unicode('event_has_batch') in i.keys():
            batch=collection.Node.one({'_type':"GSystem",'_id':ObjectId(i['event_has_batch'][0])})
            batch_relation=collection.Node.one({'_type':"GSystem",'_id':ObjectId(batch._id)},{'relation_set':1})
            for i in batch_relation['relation_set']:
               if  unicode('has_course') in i.keys(): 
                   announced_course =collection.Node.one({"_type":"GSystem",'_id':ObjectId(i['has_course'][0])})
                   for i in  announced_course.relation_set:
                      if unicode('announced_for') in i.keys():
                            course=collection.Node.one({"_type":"GSystem",'_id':ObjectId(i['announced_for'][0])})
       if unicode('session_of') in i.keys(): 
                session_of=collection.Node.one({'_type':"GSystem",'_id':ObjectId(i['session_of'][0])})                     
                module=collection.Node.one({'_type':"GSystem",'_id':{'$in':session_of.prior_node}})
  event_gs.event_coordinator
    
  if event_gst.name == u'Classroom Session' or event_gst.name == u'Exam':
     template="ndf/Nussd_event_Schedule.html"
  else:
      template = "ndf/event_create_edit.html"
  # default_template = "ndf/"+template_prefix+"_create_edit.html"
  context_variables = { 'group_id': group_id, 'groupid': group_id, 
                        'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'property_order_list': property_order_list
                        
                      }

  if app_set_instance_id:
    event_detail={}
    events={}
    event_detail["cordinatorname"]=str(event_gs.event_coordinator[0].name) 
    event_detail["cordinatorid"]=str(event_gs.event_coordinator[0]._id)
    events["cordinator"]=event_detail
    event_detail["course"]=str(announced_course.name) 
    event_detail["course_id"]=str(announced_course._id)
    events["course"]=event_detail
    event_detail={}
    event_detail["batchname"]=str(batch.name)
    event_detail["batchid"]=str(batch._id)
    events["batch"]=event_detail
    event_detail={}
    event_detail["sessionname"]=str(session_of.name)
    event_detail["sessionid"]=str(session_of._id)
    events["session"]=event_detail
    event_detail={}
    event_detail["Modulename"]=str(module.name)
    event_detail["Moduleid"]=str(module._id)
    events["Module"]=event_detail

    context_variables['node'] = event_gs
    context_variables['edit_details']=events
    
    # print "\n template-list: ", [template, default_template]
    # template = "ndf/fgh.html"
    # default_template = "ndf/dsfjhk.html"
    # return render_to_response([template, default_template], 

  return render_to_response(template, 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  

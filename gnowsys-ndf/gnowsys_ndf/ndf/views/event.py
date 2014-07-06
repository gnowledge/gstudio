''' -- imports from python libraries -- '''
# from datetime import datetime

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect #, HttpResponse uncomment when to use
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
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
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

  print "\n coming in event detail... \n"
  # app_name = "mis"
  app_set = ""
  app_collection_set = []
  title = ""

  event_gst = None
  event_gs = None

  property_order_list = []

  template_prefix = "mis"

  for eachset in app.collection_set:
    app_collection_set.append(collection.Node.one({"_id":eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))

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
  if app_set_instance_id :
    template = "ndf/event_details.html"

    node = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    # property_order_list = get_property_order_with_value(node)
    # print "\n property_order_list: ", property_order_list, "\n"
    node.get_neighbourhood(node.member_of)
  #   print "\n node.keys(): ", node.keys(), "\n"

  # print "\n event_gst._id: ", event_gst._id

  # default_template = "ndf/"+template_prefix+"_create_edit.html"
  context_variables = { 'groupid': group_id, 
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'nodes': nodes, 'node': node
                        # 'property_order_list': property_order_list
                      }

  try:
    # print "\n template-list: ", [template, default_template]
    # template = "ndf/fgh.html"
    # default_template = "ndf/dsfjhk.html"
    # return render_to_response([template, default_template], 
    return render_to_response(template, 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    # print "\n ", tde
    error_message = "\n EventDetailListViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n EventDetailListViewError: " + str(e) + " !!!\n"
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

  template_prefix = "mis"

  for eachset in app.collection_set:
    app_collection_set.append(collection.Node.one({"_id":eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))

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
    event_gs.save(is_changed=get_node_common_fields(request, event_gs, group_id, event_gst))
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

            # Fetch corresponding AT/RT-fields value from request object
            field_value = request.POST[field_instance["name"]]
            # print " ", field_instance["name"], " -- ", field_value

            field_data_type = field_set['data_type']
            # print " --> ", type(field_data_type)

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
              # print "\n ", type(collection.RelationType(field_instance)), " -- \n", collection.RelationType(field_instance)
              event_gs_triple_instance = create_grelation(event_gs._id, collection.RelationType(field_instance), field_value)
              print "\n event_gs_triple_instance: ", event_gs_triple_instance._id, " -- ", event_gs_triple_instance.name
    
    # return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': page_node._id }))
    return HttpResponseRedirect(reverse(app_name.lower()+":"+template_prefix+'_app_detail', kwargs={'group_id': group_id, "app_id":app_id, "app_set_id":app_set_id}))
  
  template = "ndf/event_create_edit.html"
  # default_template = "ndf/"+template_prefix+"_create_edit.html"
  context_variables = { 'groupid': group_id, 
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
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
    # return render_to_response([template, default_template], 

    return render_to_response(template, 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    # print "\n ", tde
    error_message = "\n EventCreateEditViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n EventCreateEditViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)


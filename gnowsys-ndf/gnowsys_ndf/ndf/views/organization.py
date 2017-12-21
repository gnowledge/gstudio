''' -- imports from python libraries -- '''
# from datetime import datetime
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect  #, HttpResponse uncomment when to use
from django.http import Http404
from django.shortcuts import render_to_response  #, render  uncomment when to use
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import AttributeType, RelationType
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, create_task
from gnowsys_ndf.ndf.views.methods import create_college_group_and_setup_data,get_execution_time
from gnowsys_ndf.ndf.views.methods import get_group_name_id


@login_required
@get_execution_time
def organization_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  custom view for custom GAPPS
  """
  auth = None
  # if ObjectId.is_valid(group_id) is False :
  #   group_ins = node_collection.one({'_type': "Group", "name": group_id})
  #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #   if group_ins:
  #     group_id = str(group_ins._id)
  #   else :
  #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #     if auth :
  #       group_id = str(auth._id)
  # else :
  #   pass
  group_name,group_id = get_group_name_id(group_id)
  app = None
  if app_id is None:
    app = node_collection.one({'_type': "GSystemType", 'name': app_name})
    if app:
      app_id = str(app._id)
  else:
    app = node_collection.one({'_id': ObjectId(app_id)})

  app_name = app.name 

  # app_name = "mis"
  app_set = ""
  app_collection_set = []
  title = ""

  organization_gst = None
  organization_gs = None

  nodes = None
  nodes_keys = []
  response_dict = {'success': False}
  node = None
  property_order_list = []
  widget_for = []
  is_link_needed = True         # This is required to show Link button on interface that link's Student's/VoluntaryTeacher's node with it's corresponding Author node

  template_prefix = "mis"
  context_variables = {}

  if request.user:
    if auth is None:
      auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username)})
    agency_type = auth.agency_type
    agency_type_node = node_collection.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
    if agency_type_node:
      for eachset in agency_type_node.collection_set:
        app_collection_set.append(node_collection.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      

  if app_set_id:
    organization_gst = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)})#, {'name': 1, 'type_of': 1})
    title = organization_gst.name

    query = {}
    ac_data_set = []
    records_list = []
    query = {
        "member_of": organization_gst._id,
        "group_set": ObjectId(group_id),
    }
    if organization_gst.name == "College":
      res = node_collection.collection.aggregate([
          {
              '$match': query
          }, {
              '$project': {
                  '_id': 0,
                  'org_id': "$_id",
                  'name': '$name',
                  'enrollment_code': '$attribute_set.enrollment_code',
                  'state': '$relation_set.organization_belongs_to_state',
                  'university': '$relation_set.college_affiliated_to',
                  # 'college_group': '$relation_set.college_group',
                  'po': '$relation_set.has_officer_incharge',
                  'created_at': "$created_at"
              }
          },
          {
              '$sort': {'created_at': 1}
          }
      ])

      records_list = res["result"]
      if records_list:
          for each in res["result"]:
              if each["university"]:
                if each["university"][0]:
                    univ_id = each["university"][0][0]
                    u = node_collection.one({"_id": univ_id}, {"name": 1})
                    each["university"] = u.name

              if each["state"]:
                if each["state"][0]:
                    state_id = each["state"][0][0]
                    each["state"] = node_collection.one({"_id": state_id}).name

              if each["po"]:
                if each["po"][0]:
                    po_id = each["po"][0][0]
                    each["po"] = node_collection.one({"_id": po_id}).name

              ac_data_set.append(each)
      column_headers = [
                  ("org_id", "Edit"),
                  ("name", "College"),
                  ("enrollment_code", "Code"),
                  # ("college_group", "Group"),
                  ("po", "Program Officer"),
                  ("university", "University"),
                  ("state", "State"),
      ]

      response_dict["column_headers"] = column_headers
      response_dict["success"] = True
      response_dict["students_data_set"] = ac_data_set

    elif organization_gst.name == "University":
      res = node_collection.collection.aggregate([
          {
              '$match': query
          }, {
              '$project': {
                  '_id': 0,
                  'org_id': "$_id",
                  'name': '$name',
                  'state': '$relation_set.organization_belongs_to_state',
                  'created_at': "$created_at"
              }
          },
          {
              '$sort': {'created_at': 1}
          }
      ])

      records_list = res["result"]
      if records_list:
          for each in res["result"]:
              if each["state"]:
                if each["state"][0]:
                    state_id = each["state"][0][0]
                    each["state"] = node_collection.one({"_id": state_id}).name

              ac_data_set.append(each)
      column_headers = [
                  ("org_id", "Edit"),
                  ("name", "University"),
                  ("state", "State"),
      ]

      response_dict["column_headers"] = column_headers
      response_dict["success"] = True
      response_dict["students_data_set"] = ac_data_set
    response_dict["groupid"] = group_id
    response_dict["app_id"] = app_id
    response_dict["app_set_id"] = app_set_id

    nodes = list(node_collection.find(query).sort('name', 1))

    nodes_keys = [('name', "Name")]

    # template = "ndf/" + organization_gst.name.strip().lower().replace(' ', '_') + "_list.html"
    template = "ndf/organization_list.html"
    # default_template = "ndf/mis_list.html"

  if app_set_instance_id:

    template = "ndf/organization_details.html"
    # default_template = "ndf/mis_details.html"

    node = node_collection.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    property_order_list = get_property_order_with_value(node)
    node.get_neighbourhood(node.member_of)

  context_variables = { 'groupid': group_id,'group_id':group_id,
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title': title,
                        'nodes': nodes, "nodes_keys": nodes_keys, 'node': node,
                        'property_order_list': property_order_list, 'lstFilters': widget_for,
                        'is_link_needed': is_link_needed,
                        'response_dict':json.dumps(response_dict, cls=NodeJSONEncoder)
                      }

  try:
    return render_to_response(template, 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    error_message = "\n OrganizationDetailListViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n OrganizationDetailListViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)

@login_required
@get_execution_time
def organization_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  Creates/Modifies document of given organization-type.
  """
  auth = None
  # if ObjectId.is_valid(group_id) is False :
  #   group_ins = node_collection.one({'_type': "Group","name": group_id})
  #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #   if group_ins:
  #     group_id = str(group_ins._id)
  #   else :
  #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #     if auth :
  #       group_id = str(auth._id)
  # else :
  #   pass
  group_name, group_id = get_group_name_id(group_id)
  app = None
  if app_id is None:
    app = node_collection.one({'_type': "GSystemType", 'name': app_name})
    if app:
      app_id = str(app._id)
  else:
    app = node_collection.one({'_id': ObjectId(app_id)},{'_id':1, 'name':1})
  app_name = app.name

  # app_name = "mis"
  app_set = ""
  app_collection_set = []
  title = ""

  organization_gst = None
  organization_gs = None

  property_order_list = []

  template = ""
  template_prefix = "mis"

  if request.user:
    if auth is None:
      auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username)})
    agency_type = auth.agency_type
    agency_type_node = node_collection.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
    if agency_type_node:
      for eachset in agency_type_node.collection_set:
        app_collection_set.append(node_collection.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      
  # for eachset in app.collection_set:
  #   app_collection_set.append(node_collection.one({"_id":eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))

  if app_set_id:
    organization_gst = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    template = "ndf/organization_create_edit.html"
    title = organization_gst.name
    organization_gs = node_collection.collection.GSystem()
    organization_gs.member_of.append(organization_gst._id)

  if app_set_instance_id:
    organization_gs = node_collection.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
  property_order_list = get_property_order_with_value(organization_gs)#.property_order
  if request.method == "POST":
    # [A] Save organization-node's base-field(s)
    is_changed = get_node_common_fields(request, organization_gs, group_id, organization_gst)

    if is_changed:
      # Remove this when publish button is setup on interface
      organization_gs.status = u"PUBLISHED"

    organization_gs.save(is_changed=is_changed,groupid=group_id)

    # [B] Store AT and/or RT field(s) of given organization-node (i.e., organization_gs)
    for tab_details in property_order_list:
      for field_set in tab_details[1]:
        # Fetch only Attribute field(s) / Relation field(s)
        if '_id' in field_set:
          field_instance = node_collection.one({'_id': field_set['_id']})
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
                  file_name = organization_gs.name + " -- " + field_instance["altnames"]
                  content_org = ""
                  tags = ""
                  field_value = save_file(field_value, file_name, request.user.id, group_id, content_org, tags, access_policy="PRIVATE", count=0, first_object="", oid=True)[0]

              else:
                # Other AttributeTypes 
                field_value = request.POST[field_instance["name"]]

              # field_instance_type = "GAttribute"
              if field_instance["name"] in ["12_passing_year", "degree_passing_year"]: #, "registration_year"]:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%Y")
              elif field_instance["name"] in ["dob", "registration_date"]:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y")
              else:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y %H:%M")

              if field_value:
                organization_gs_triple_instance = create_gattribute(organization_gs._id, node_collection.collection.AttributeType(field_instance), field_value)

            else:
              if field_instance["object_cardinality"] > 1:
                field_value_list = request.POST.get(field_instance["name"], "")
                if "[" in field_value_list and "]" in field_value_list:
                  field_value_list = json.loads(field_value_list)
                else:
                  field_value_list = request.POST.getlist(field_instance["name"])

              else:
                field_value_list = request.POST.getlist(field_instance["name"])

              # field_instance_type = "GRelation"
              for i, field_value in enumerate(field_value_list):
                field_value = parse_template_data(field_data_type, field_value, field_instance=field_instance, date_format_string="%m/%d/%Y %H:%M")
                field_value_list[i] = field_value

              organization_gs_triple_instance = create_grelation(organization_gs._id, node_collection.collection.RelationType(field_instance), field_value_list)

    # [C] Create private group only for College GSystems
    if "College" in organization_gs.member_of_names_list:
      # Create a group for respective college node
      college_group, college_group_gr = create_college_group_and_setup_data(organization_gs)

    return HttpResponseRedirect(
      reverse(
        app_name.lower()+":"+template_prefix+'_app_detail',
        kwargs={'group_id': group_id, "app_id": app_id, "app_set_id": app_set_id}
      )
    )

  # default_template = "ndf/"+template_prefix+"_create_edit.html"
  context_variables = { 'groupid': group_id, 'group_id': group_id,
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title': title,
                        'property_order_list': property_order_list
                      }
  if app_set_instance_id:
    #   organization_gs.get_neighbourhood(organization_gs.member_of)
    #   context_variables['node'] = organization_gs
    context_variables['node_id'] = organization_gs._id
    context_variables['node_name'] = organization_gs.name

  try:
    return render_to_response(template,
                              context_variables,
                              context_instance = RequestContext(request)
                            )

  except TemplateDoesNotExist as tde:
    error_message = "\n OrganizationCreateEditViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)

  except Exception as e:
    error_message = "\n OrganizationCreateEditViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)

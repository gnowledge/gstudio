''' -- imports from python libraries -- '''
# from datetime import datetime
import datetime
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect #, HttpResponse uncomment when to use
from django.http import Http404
from django.shortcuts import render_to_response #, render  uncomment when to use
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site

from django_mongokit import get_database

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

from mongokit import IS

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data
from gnowsys_ndf.ndf.views.methods import get_widget_built_up_data, get_property_order_with_value
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, create_task

collection = get_database()[Node.collection_name]

def organization_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  custom view for custom GAPPS
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

  organization_gst = None
  organization_gs = None

  nodes = None
  nodes_keys = []
  node = None
  property_order_list = []
  widget_for = []
  is_link_needed = True         # This is required to show Link button on interface that link's Student's/VoluntaryTeacher's node with it's corresponding Author node

  template_prefix = "mis"
  context_variables = {}

  if request.user:
    if auth is None:
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username)})
    agency_type = auth.agency_type
    agency_type_node = collection.Node.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
    if agency_type_node:
      for eachset in agency_type_node.collection_set:
        app_collection_set.append(collection.Node.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      

  if app_set_id:
    organization_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)})#, {'name': 1, 'type_of': 1})
    title = organization_gst.name

    query = {}
    if request.method == "POST":
      search = request.POST.get("search","")
      query = {'member_of': organization_gst._id, 'group_set': ObjectId(group_id), 'name': {'$regex': search, '$options': 'i'}}
    
    else:
      query = {'member_of': organization_gst._id, 'group_set': ObjectId(group_id)}

    nodes = list(collection.Node.find(query).sort('name', 1))

    nodes_keys = [('name', "Name")]

    template = "ndf/" + organization_gst.name.strip().lower().replace(' ', '_') + "_list.html"
    default_template = "ndf/mis_list.html"

  if app_set_instance_id:
    template = "ndf/" + organization_gst.name.strip().lower().replace(' ', '_') + "_details.html"
    default_template = "ndf/mis_details.html"

    node = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    property_order_list = get_property_order_with_value(node)
    node.get_neighbourhood(node.member_of)

  context_variables = { 'groupid': group_id, 
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title': title,
                        'nodes': nodes, "nodes_keys": nodes_keys, 'node': node,
                        'property_order_list': property_order_list, 'lstFilters': widget_for,
                        'is_link_needed': is_link_needed
                      }

  try:
    return render_to_response([template, default_template], 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    error_message = "\n O rganizationDetailListViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n OrganizationDetailListViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)

@login_required
def organization_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  Creates/Modifies document of given organization-type.
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

  organization_gst = None
  organization_gs = None

  property_order_list = []

  template = ""
  template_prefix = "mis"

  if request.user:
    if auth is None:
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username)})
    agency_type = auth.agency_type
    agency_type_node = collection.Node.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
    if agency_type_node:
      for eachset in agency_type_node.collection_set:
        app_collection_set.append(collection.Node.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      

  # for eachset in app.collection_set:
  #   app_collection_set.append(collection.Node.one({"_id":eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))

  if app_set_id:
    organization_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    template = "ndf/" + organization_gst.name.strip().lower().replace(' ', '_') + "_create_edit.html"
    title = organization_gst.name
    organization_gs = collection.GSystem()
    organization_gs.member_of.append(organization_gst._id)

  if app_set_instance_id:
    organization_gs = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})

  property_order_list = get_property_order_with_value(organization_gs)#.property_order

  if request.method == "POST":
    # [A] Save organization-node's base-field(s)
    is_changed = get_node_common_fields(request, organization_gs, group_id, organization_gst)

    if is_changed:
      # Remove this when publish button is setup on interface
      organization_gs.status = u"PUBLISHED"

    organization_gs.save(is_changed=is_changed)
  
    # [B] Store AT and/or RT field(s) of given organization-node (i.e., organization_gs)
    for tab_details in property_order_list:
      for field_set in tab_details[1]:
        # Fetch only Attribute field(s) / Relation field(s)
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
                  file_name = organization_gs.name + " -- " + field_instance["altnames"]
                  content_org = ""
                  tags = ""
                  field_value = save_file(field_value, file_name, request.user.id, group_id, content_org, tags, oid=True)[0]

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
                organization_gs_triple_instance = create_gattribute(organization_gs._id, collection.AttributeType(field_instance), field_value)

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

              organization_gs_triple_instance = create_grelation(organization_gs._id, collection.RelationType(field_instance), field_value_list)

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

  default_template = "ndf/organization_create_edit.html"
  # default_template = "ndf/"+template_prefix+"_create_edit.html"
  context_variables = { 'groupid': group_id, 'group_id': group_id,
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'property_order_list': property_order_list
                      }

  if app_set_instance_id:
    organization_gs.get_neighbourhood(organization_gs.member_of)
    context_variables['node'] = organization_gs

  try:
    return render_to_response([template, default_template], 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    error_message = "\n OrganizationCreateEditViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n OrganizationCreateEditViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)


def create_college_group_and_setup_data(college_node):
    """
    Creates private group for given college; establishes relationship
    between them via "has_group" RelationType.

    Also populating data into it needed for registrations.

    Arguments:
    college_node -- College node (or document)

    Returns:
    College group node
    GRelation node
    """

    gfc = None
    gr_gfc = None

    # [A] Creating group
    group_gst = collection.Node.one(
        {'_type': "GSystemType", 'name': "Group"},
        {'_id': 1}
    )
    creator_and_modifier = college_node.created_by

    gfc = collection.Node.one(
        {'_type': "Group", 'name': college_node.name},
        {'_id': 1, 'name': 1, 'group_type': 1}
    )

    if not gfc:
        gfc = collection.Group()
        gfc._type = u"Group"
        gfc.name = college_node.name
        gfc.altnames = college_node.name
        gfc.member_of = [group_gst._id]
        gfc.group_type = u"PRIVATE"
        gfc.created_by = creator_and_modifier
        gfc.modified_by = creator_and_modifier
        gfc.contributors = [creator_and_modifier]
        gfc.status = u"PUBLISHED"
        gfc.save()

    if "_id" in gfc:
        has_group_rt = collection.Node.one(
            {'_type': "RelationType", 'name': "has_group"}
        )
        gr_gfc = create_grelation(college_node._id, has_group_rt, gfc._id)

        # [B] Setting up data into college group
        if gr_gfc:
            # List of Types (names) whose data needs to be populated
            # in college group
            gst_list = [
                "Country", "State", "District", "University",
                "College", "Caste", "NUSSD Course"
            ]

            gst_cur = collection.Node.find(
                {'_type': "GSystemType", 'name': {'$in': gst_list}}
            )

            # List of Types (ObjectIds)
            gst_list = []
            for each in gst_cur:
                gst_list.append(each._id)

            mis_admin = collection.Node.one(
                {
                    '_type': "Group",
                    '$or': [
                        {'name': {'$regex': u"MIS_admin", '$options': 'i'}},
                        {'altnames': {'$regex': u"MIS_admin", '$options': 'i'}}
                    ],
                    'group_type': "PRIVATE"
                },
                {'_id': 1}
            )

            # Update GSystem node(s) of GSystemType(s) specified in gst_list
            # Append newly created college group's ObjectId in group_set field
            collection.update(
                {
                    '_type': "GSystem", 'member_of': {'$in': gst_list},
                    'group_set': mis_admin._id
                },
                {'$addToSet': {'group_set': gfc._id}},
                upsert=False, multi=True
            )

    return gfc, gr_gfc

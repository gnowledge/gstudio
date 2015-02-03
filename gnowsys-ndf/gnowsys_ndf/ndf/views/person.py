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
from gnowsys_ndf.settings import GSTUDIO_TASK_TYPES
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data
from gnowsys_ndf.ndf.views.methods import get_widget_built_up_data, get_property_order_with_value
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, create_task

collection = get_database()[Node.collection_name]

def person_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None, app_name=None):
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

  person_gst = None
  person_gs = None

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
    person_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)})#, {'name': 1, 'type_of': 1})
    title = person_gst.name

    if title == "Student":
      person_gs = collection.GSystem()
      person_gs.member_of.append(person_gst._id)
      person_gs.get_neighbourhood(person_gs.member_of)
      rel_univ = collection.Node.one({'_type': "RelationType", 'name': "student_belongs_to_university"}, {'_id': 1})
      rel_colg = collection.Node.one({'_type': "RelationType", 'name': "student_belongs_to_college"}, {'_id': 1})
      attr_deg_yr = collection.Node.one({'_type': "AttributeType", 'name': "degree_year"}, {'_id': 1})

      widget_for = ["name", 
                    rel_univ._id,
                    rel_colg._id,
                    attr_deg_yr._id
                  ]
                  #   'status'
                  # ]
      widget_for = get_widget_built_up_data(widget_for, person_gs)
  
    else:
      query = {}
      if request.method == "POST":
        search = request.POST.get("search","")
        query = {'member_of': person_gst._id, 'group_set': ObjectId(group_id), 'name': {'$regex': search, '$options': 'i'}}
      
      else:
        query = {'member_of': person_gst._id, 'group_set': ObjectId(group_id)}

      rec = collection.aggregate([{'$match': query},
                            {'$project': {'_id': 1,
                                          'name': '$name',
                                          'gender': '$attribute_set.gender',
                                          'dob': '$attribute_set.dob',
                                          'email_id': '$attribute_set.email_id',
                            }},
                            {'$sort': {'name': 1}}
      ])

      nodes = []
      if len(rec["result"]):
        for each_dict in rec["result"]:
          new_dict = {}
          
          for each_key in each_dict:
            if each_dict[each_key]:
              if type(each_dict[each_key]) == list:
                data = each_dict[each_key][0]
              else:
                data = each_dict[each_key]

              if type(data) == list:
                # Perform parsing
                if type(data) == list:
                  # Perform parsing
                  if type(data[0]) in [unicode, basestring, int]:
                    new_dict[each_key] = ', '.join(str(d) for d in data)
                
                  elif type(data[0]) in [ObjectId]:
                    # new_dict[each_key] = str(data)
                    d_list = []
                    for oid in data:
                      d = collection.Node.one({'_id': oid}, {'name': 1})
                      d_list.append(str(d.name))
                    new_dict[each_key] = ', '.join(str(n) for n in d_list)
                
                elif type(data) == datetime.datetime:
                  new_dict[each_key] = data.strftime("%d/%m/%Y")
                
                elif type(data) == long:
                  new_dict[each_key] = str(data)
                
                elif type(data) == bool:
                  if data:
                    new_dict[each_key] = "Yes"
                  else:
                    new_dict[each_key] = "No"
                
                else:
                  new_dict[each_key] = str(data)

              else:
                # Perform parsing
                if type(data) == list:
                  # Perform parsing
                  if type(data[0]) in [unicode, basestring, int]:
                    new_dict[each_key] = ', '.join(str(d) for d in data)
                  elif type(data[0]) in [ObjectId]:
                    new_dict[each_key] = str(data)

                elif type(data) == datetime.datetime:
                  new_dict[each_key] = data.strftime("%d/%m/%Y")

                elif type(data) == long:
                  new_dict[each_key] = str(data)

                elif type(data) == bool:
                  if data:
                    new_dict[each_key] = "Yes"
                  else:
                    new_dict[each_key] = "No"

                else:
                  new_dict[each_key] = str(data)

            else:
              new_dict[each_key] = ""
          
          nodes.append(new_dict)

      nodes_keys = [('name', "Name"),
        ('gender', "Gender"),
        ('dob', 'Birth Date'),
        ('email_id', 'Email ID')
      ]

    template = "ndf/" + person_gst.name.strip().lower().replace(' ', '_') + "_list.html"
    default_template = "ndf/person_list.html"

  if app_set_instance_id:
    template = "ndf/" + person_gst.name.strip().lower().replace(' ', '_') + "_details.html"
    default_template = "ndf/person_details.html"

    node = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    property_order_list = get_property_order_with_value(node)
    node.get_neighbourhood(node.member_of)

  context_variables = { 'groupid': group_id, 
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
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
    error_message = "\n PersonDetailListViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n PersonDetailListViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)

@login_required
def person_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  Creates/Modifies document of given person-type.
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

  person_gst = None
  person_gs = None

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
    person_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    template = "ndf/" + person_gst.name.strip().lower().replace(' ', '_') + "_create_edit.html"
    title = person_gst.name
    person_gs = collection.GSystem()
    person_gs.member_of.append(person_gst._id)

  if app_set_instance_id:
    person_gs = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})

  property_order_list = get_property_order_with_value(person_gs)#.property_order

  if request.method == "POST":
    # [A] Save person-node's base-field(s)
    is_changed = get_node_common_fields(request, person_gs, group_id, person_gst)

    if is_changed:
      # Remove this when publish button is setup on interface
      person_gs.status = u"PUBLISHED"

    person_gs.save(is_changed=is_changed)
  
    # [B] Store AT and/or RT field(s) of given person-node (i.e., person_gs)
    for tab_details in property_order_list:
      for field_set in tab_details[1]:
        # Fetch only Attribute field(s) / Relation field(s)
        if field_set.has_key('_id'):
          field_instance = collection.Node.one({'_id': field_set['_id']})
          field_instance_type = type(field_instance)

          if field_instance_type in [AttributeType, RelationType]:
            field_data_type = field_set['data_type']

            # Fetch field's value depending upon AT/RT and Parse fetched-value depending upon that field's data-type
            if field_instance_type == AttributeType:
              if "File" in field_instance["validators"]:
                # Special case: AttributeTypes that require file instance as it's value in which case file document's ObjectId is used
                user_id = request.user.id
                if field_instance["name"] in request.FILES:
                  field_value = request.FILES[field_instance["name"]]

                else:
                  field_value = ""
                
                # Below 0th index is used because that function returns tuple(ObjectId, bool-value)
                if field_value != '' and field_value != u'':
                  file_name = person_gs.name + " -- " + field_instance["altnames"]
                  content_org = ""
                  tags = ""
                  field_value = save_file(field_value, file_name, user_id, group_id, content_org, tags, oid=True)[0]

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
                person_gs_triple_instance = create_gattribute(person_gs._id, collection.AttributeType(field_instance), field_value)

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

              person_gs_triple_instance = create_grelation(person_gs._id, collection.RelationType(field_instance), field_value_list)

    # [C] Code to link GSystem Node and Author node via "has_login" relationship;
    #     and Subscribe the Author node to College group if user "Program Officer"
    person_gs.reload()
    auth_node = None
    for attr in person_gs.attribute_set:
      if "email_id" in attr:
        if attr["email_id"]:
          auth_node = collection.Node.one({'_type': "Author", 'email': attr["email_id"]})
          break

    if auth_node:
      has_login_rt = collection.Node.one({'_type': "RelationType", 'name': "has_login"})
      if has_login_rt:
        # Linking GSystem Node and Author node via "has_login" relationship;
        gr_node = create_grelation(person_gs._id, has_login_rt, auth_node._id)
      
      if "Program Officer" in person_gs.member_of_names_list:
        # If Person node (GSystem) is of Program Officer type
        # then only go for subscription
        college_id_list = []
        # Fetch College's ObjectId to which Program Officer is assigned (via "officer_incharge_of")
        for rel in person_gs.relation_set:
          if "officer_incharge_of" in rel:
            if rel["officer_incharge_of"]:
              for college_id in rel["officer_incharge_of"]:
                if college_id not in college_id_list:
                  college_id_list.append(college_id)
              
              break  # break outer-loop (of relation_set)

        if college_id_list:
          # If College's ObjectId exists (list as PO might be assigned to more than one college)
          # Then prepare a list of their corresponding private group(s) (via "has_group")
          college_cur = collection.Node.find(
            {'_id': {'$in': college_id_list}},
            {'relation_set.has_group': 1}
          )

          college_group_id_list = []
          for college in college_cur:
            for rel in college.relation_set:
              if rel and "has_group" in rel:
                if rel["has_group"]:
                  if rel["has_group"][0] not in college_group_id_list:
                    college_group_id_list.append(rel["has_group"][0])
                  
                  break  # break inner-loop (college.relation_set)

          if college_group_id_list:
            # If college-group list exists
            # Then update their group_admin field (append PO's created_by)
            res = collection.update(
              {'_id': {'$in': college_group_id_list}},
              {'$addToSet': {'group_admin': auth_node.created_by}},
              upsert=False, multi=True
            )

    return HttpResponseRedirect(reverse(app_name.lower()+":"+template_prefix+'_app_detail', kwargs={'group_id': group_id, "app_id":app_id, "app_set_id":app_set_id}))
  
  default_template = "ndf/person_create_edit.html"
  # default_template = "ndf/"+template_prefix+"_create_edit.html"
  context_variables = { 'groupid': group_id, 'group_id': group_id,
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'property_order_list': property_order_list
                      }

  if person_gst and person_gst.name in ["Voluntary Teacher", "Master Trainer"]:
    nussd_course_type = collection.Node.one({'_type': "AttributeType", 'name': "nussd_course_type"}, {'_type': 1, '_id': 1, 'data_type': 1, 'complex_data_type': 1, 'name': 1, 'altnames': 1})

    if nussd_course_type["data_type"] == "IS()":
      # Below code does little formatting, for example:
      # data_type: "IS()" complex_value: [u"ab", u"cd"] dt:
      # "IS(u'ab', u'cd')"
      dt = "IS("
      for v in nussd_course_type.complex_data_type:
          dt = dt + "u'" + v + "'" + ", " 
      dt = dt[:(dt.rfind(", "))] + ")"
      nussd_course_type["data_type"] = dt

    nussd_course_type["data_type"] = eval(nussd_course_type["data_type"])
    nussd_course_type["value"] = None
    context_variables['nussd_course_type'] = nussd_course_type

  if app_set_instance_id:
    person_gs.get_neighbourhood(person_gs.member_of)
    context_variables['node'] = person_gs

  try:
    return render_to_response([template, default_template], 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    error_message = "\n PersonCreateEditViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n PersonCreateEditViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)



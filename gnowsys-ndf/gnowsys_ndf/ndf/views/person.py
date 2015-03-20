''' -- imports from python libraries -- '''
# from datetime import datetime
import datetime
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect, HttpResponse  # uncomment when to use
from django.http import Http404
from django.shortcuts import render_to_response  #, render  uncomment when to use
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from mongokit import IS

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import AttributeType, RelationType
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data
from gnowsys_ndf.ndf.views.methods import get_widget_built_up_data, get_property_order_with_value,get_execution_time
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, create_task
from gnowsys_ndf.ndf.views.methods import get_student_enrollment_code
collection = get_database()[Node.collection_name]
@get_execution_time
def person_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  custom view for custom GAPPS
  """

  auth = None
  if ObjectId.is_valid(group_id) is False :
    group_ins = node_collection.one({'_type': "Group","name": group_id})
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    if group_ins:
      group_id = str(group_ins._id)
    else :
      auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth :
        group_id = str(auth._id)
  else :
    pass

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

  person_gst = None
  person_gs = None

  nodes = None
  nodes_keys = []
  node = None
  property_order_list = []
  widget_for = []
  is_link_needed = True         # This is required to show Link button on interface that link's Student's/VoluntaryTeacher's node with it's corresponding Author node
  univ_list = []
  colg_list = []
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
    person_gst = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)})#, {'name': 1, 'type_of': 1})
    title = person_gst.name

    if title == "Student":
      person_gs = node_collection.collection.GSystem()
      person_gs.member_of.append(person_gst._id)
      person_gs.get_neighbourhood(person_gs.member_of)
      university_gst = node_collection.one({'_type': "GSystemType", 'name': "University"})
      mis_admin = node_collection.one({"_type": "Group", "name": "MIS_admin"}, {"_id": 1})

      univ_cur = node_collection.find({"member_of": university_gst._id, 'group_set': mis_admin._id}, {'name': 1, "_id": 1})
      attr_deg_yr = node_collection.one({'_type': "AttributeType", 'name': "degree_year"}, {'_id': 1})

      widget_for = ["name", 
                    attr_deg_yr._id
                  ]
      widget_for = get_widget_built_up_data(widget_for, person_gs)

      for each in univ_cur:
        univ_list.append(each)
  
    else:
      query = {}
      if request.method == "POST":
        search = request.POST.get("search","")
        query = {'member_of': person_gst._id, 'group_set': ObjectId(group_id), 'name': {'$regex': search, '$options': 'i'}}
      
      else:
        query = {'member_of': person_gst._id, 'group_set': ObjectId(group_id)}

      rec = node_collection.collection.aggregate([{'$match': query},
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
                      d = node_collection.one({'_id': oid}, {'name': 1})
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

    node = node_collection.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    property_order_list = get_property_order_with_value(node)
    node.get_neighbourhood(node.member_of)

  context_variables = { 'groupid': group_id, 
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'nodes': nodes, "nodes_keys": nodes_keys, 'node': node,
                        'property_order_list': property_order_list, 'lstFilters': widget_for,
                        'univ_list':json.dumps(univ_list, cls=NodeJSONEncoder),
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
@get_execution_time
def person_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  Creates/Modifies document of given person-type.
  """
  auth = None
  if ObjectId.is_valid(group_id) is False :
    group_ins = node_collection.one({'_type': "Group", "name": group_id})
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    if group_ins:
      group_id = str(group_ins._id)
    else :
      auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth :
        group_id = str(auth._id)
  else :
    pass

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

  person_gst = None
  person_gs = None
  college_node = None
  college_id = None
  student_enrollment_code = u""
  create_student_enrollment_code = False
  registration_date = None

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
  college_node = node_collection.one({
      "_id": ObjectId(group_id),
      "relation_set.group_of": {"$exists": True}
  }, {
      "relation_set.group_of": 1
  })

  if app_set_id:
    person_gst = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    template = "ndf/" + person_gst.name.strip().lower().replace(' ', '_') + "_create_edit.html"
    title = person_gst.name
    person_gs = node_collection.collection.GSystem()
    person_gs.member_of.append(person_gst._id)

  if app_set_instance_id:
    person_gs = node_collection.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})

  property_order_list = get_property_order_with_value(person_gs)#.property_order

  if request.method == "POST":
    if person_gst.name == "Student" and "_id" not in person_gs:
      create_student_enrollment_code = True

    # [A] Save person-node's base-field(s)
    is_changed = get_node_common_fields(request, person_gs, group_id, person_gst)

    if is_changed:
      # Remove this when publish button is setup on interface
      person_gs.status = u"PUBLISHED"

    person_gs.save(is_changed=is_changed)

    if college_node:
        mis_admin = node_collection.one({
            "_type": "Group",
            "name": "MIS_admin"
        }, {
            "_id": 1
        }
        )

        node_collection.collection.update({
            "_id": person_gs._id
        }, {
            "$addToSet": {"group_set": mis_admin._id}
        },
        upsert=False, multi=False
        )

    # [B] Store AT and/or RT field(s) of given person-node (i.e., person_gs)
    for tab_details in property_order_list:
      for field_set in tab_details[1]:
        # Fetch only Attribute field(s) / Relation field(s)
        if '_id' in field_set:
          field_instance = node_collection.one({'_id': field_set['_id']})
          fi_name = field_instance["name"]
          field_instance_type = type(field_instance)

          if field_instance_type in [AttributeType, RelationType]:
            field_data_type = field_set['data_type']

            # Fetch field's value depending upon AT/RT and Parse fetched-value depending upon that field's data-type
            if field_instance_type == AttributeType:
              if "File" in field_instance["validators"]:
                # Special case: AttributeTypes that require file instance as it's value in which case file document's ObjectId is used
                user_id = request.user.id
                if fi_name in request.FILES:
                  field_value = request.FILES[fi_name]

                else:
                  field_value = ""

                # Below 0th index is used because that function returns tuple(ObjectId, bool-value)
                if field_value != '' and field_value != u'':
                  file_name = person_gs.name + " -- " + field_instance["altnames"]
                  content_org = ""
                  tags = ""
                  field_value = save_file(field_value, file_name, user_id, group_id, content_org, tags, access_policy="PRIVATE", count=0, first_object="", oid=True)[0]

              else:
                # Other AttributeTypes
                if fi_name in request.POST:
                    field_value = request.POST[fi_name]

              # field_instance_type = "GAttribute"
              if fi_name in ["12_passing_year", "degree_passing_year"]: #, "registration_year"]:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%Y")
              elif fi_name in ["dob", "registration_date"]:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y")
                registration_date = field_value
              else:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y %H:%M")

              if field_value:
                person_gs_triple_instance = create_gattribute(person_gs._id, node_collection.collection.AttributeType(field_instance), field_value)

            else:
              if field_instance["object_cardinality"] > 1:
                field_value_list = request.POST.get(fi_name, "")
                if "[" in field_value_list and "]" in field_value_list:
                  field_value_list = json.loads(field_value_list)
                else:
                  field_value_list = request.POST.getlist(fi_name)

              else:
                field_value_list = request.POST.getlist(fi_name)

              # field_instance_type = "GRelation"
              for i, field_value in enumerate(field_value_list):
                field_value = parse_template_data(field_data_type, field_value, field_instance=field_instance, date_format_string="%m/%d/%Y %H:%M")
                field_value_list[i] = field_value

              person_gs_triple_instance = create_grelation(person_gs._id, node_collection.collection.RelationType(field_instance), field_value_list)

    # Setting enrollment code for student node only while creating it
    if create_student_enrollment_code:
        # Create enrollment code for student node only while registering a new node
        for rel in college_node.relation_set:
          if rel and "group_of" in rel:
            college_id = rel["group_of"][0]

        student_enrollment_code = get_student_enrollment_code(college_id, person_gs._id, registration_date, ObjectId(group_id))

        enrollment_code_at = node_collection.one({
            "_type": "AttributeType", "name": "enrollment_code"
        })

        try:
            ga_node = create_gattribute(person_gs._id, enrollment_code_at, student_enrollment_code)
        except Exception as e:
            print "\n StudentEnrollmentCreateError: " + str(e) + "!!!"

    # [C] Code to link GSystem Node and Author node via "has_login" relationship;
    #     and Subscribe the Author node to College group if user "Program Officer"
    person_gs.reload()
    auth_node = None
    for attr in person_gs.attribute_set:
      if "email_id" in attr:
        if attr["email_id"]:
          auth_node = node_collection.one({'_type': "Author", 'email': attr["email_id"]})
          break

    if auth_node:
      has_login_rt = node_collection.one({'_type': "RelationType", 'name': "has_login"})
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
          college_cur = node_collection.find(
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
            res = node_collection.collection.update(
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
    nussd_course_type = node_collection.one({'_type': "AttributeType", 'name': "nussd_course_type"}, {'_type': 1, '_id': 1, 'data_type': 1, 'complex_data_type': 1, 'name': 1, 'altnames': 1})

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



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
    has_login_rt = collection.Node.one({'_type': "RelationType", 'name': "has_login"})

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
                  file_name = person_gs.name + " -- " + field_instance["altnames"]
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

    # [C] Code to link GSystem Node and Author node via "has_login" relationship
    person_gs.reload()
    for each in person_gs.attribute_set:
      if "email_id" in each:
        auth_node = collection.Node.one({'_type': "Author", 'email': each["email_id"]})
        if auth_node:
          gr_node = create_grelation(person_gs._id, has_login_rt, auth_node._id)

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

@login_required
def person_enroll(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    Student enrollment
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

    app_collection_set = [] 
    app_set = ""
    nodes = ""
    title = ""
    template_prefix = "mis"

    user_id = int(request.user.id)  # getting django user id
    user_name = unicode(request.user.username)  # getting django user name

    if request.user.id:
      if auth is None:
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username)})
      agency_type = auth.agency_type
      agency_type_node = collection.Node.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
      if agency_type_node:
        for eachset in agency_type_node.collection_set:
          app_collection_set.append(collection.Node.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      

    if request.method == "POST":
      enrollState = request.POST.get("enrollState", "")

      task_id = request.POST.get("task_id", "")
      if task_id:
        task_id = ObjectId(task_id)
      
      announced_courses_id = request.POST.get("announced_courses_list", "")
      if announced_courses_id != '':
        announced_courses_id = ObjectId(announced_courses_id.strip())

        # Fetch announced course
        acourse = collection.Node.one(
          {'_id': announced_courses_id}, 
          {'name': 1, 'relation_set.acourse_for_college': 1}
        )

        at_rt_list = ["for_acourse", "for_college", "for_university", "has_enrolled", "completed_on", "has_corresponding_task"]
        at_rt_dict = {}
        if acourse:
          # Announced Course
          at_rt_dict["for_acourse"] = acourse._id

          # Announced Course -> College
          college_id = None
          for rel in acourse.relation_set:
            if rel:
              college_id = rel["acourse_for_college"][0]
              break
          at_rt_dict["for_college"] = college_id

          # Announced Course -> College -> University (On hold)
          university_id = None
          # Fetch university's ObjectId from college node's relation_set once it's set up
          at_rt_dict["for_university"] = university_id

          # Students Enrolled list
          at_rt_dict["has_enrolled"] = []
          student_enroll_list = request.POST.get("student_enroll_list", "")

          if student_enroll_list:
            student_enroll_list = [ObjectId(each.strip()) for each in student_enroll_list.split(",")]
          at_rt_dict["has_enrolled"] = student_enroll_list
          
          # Date of Enrollment completion -> Set the date on which Complete button is clicked
          at_rt_dict["completed_on"] = None
          if enrollState == "Complete":
            at_rt_dict["completed_on"] = datetime.datetime.now()

          # Create/Update StudentCourseEnrollment node
          sce_gst = collection.Node.one({'_type': "GSystemType", 'name': "StudentCourseEnrollment"})
          
          sce_gs_name = "StudentCourseEnrollment_" + acourse.name
          sce_gs = collection.Node.one(
            {'member_of': sce_gst._id, 'name': sce_gs_name, 'status': {'$in': [u"DRAFT", u"PUBLISHED"]}}
          )

          # If not found, create it
          if not sce_gs:
            sce_gs = collection.GSystem()
            sce_gs.name = sce_gs_name
            if sce_gst._id not in sce_gs.member_of:
              sce_gs.member_of.append(sce_gst._id)
            
            if mis_admin._id not in sce_gs.group_set:
              sce_gs.group_set.append(mis_admin._id)

            user_id = request.user.id
            sce_gs.created_by = user_id
            sce_gs.modified_by = user_id
            if user_id not in sce_gs.contributors:
              sce_gs.contributors.append(user_id)

            # This node will get PUBLISHED only when enrollState is found as "Complete"
            sce_gs.status = u"DRAFT"
            sce_gs.save()

          if enrollState == "Complete":
            # For Student-Course Enrollment Approval
            # Create a task for admin(s) of the MIS_admin group
            task_dict = {}
            mis_admin = collection.Node.one(
              {'_type': "Group", 'name': "MIS_admin"}, 
              {'_id': 1, 'name': 1, 'group_admin': 1}
            )
            task_dict["name"] = unicode("StudentCourseApproval_Task_" + acourse.name)
            task_dict["created_by"] = mis_admin.group_admin[0]
            admin_user = User.objects.get(id=mis_admin.group_admin[0])
            task_dict["created_by_name"] = admin_user.username
            task_dict["modified_by"] = mis_admin.group_admin[0]
            task_dict["contributors"] = [mis_admin.group_admin[0]]
            
            MIS_GAPP = collection.Node.one({'_type': "GSystemType", 'name': "MIS"}, {'_id': 1})
            student_course_approval_url_link = ""
            if MIS_GAPP:
              site = Site.objects.get(pk=1)
              site = site.name.__str__()
              student_course_approval_url_link = "http://" + site + "/" + mis_admin.name.replace(" ","%20").encode('utf8') + "/dashboard/group" 
            task_dict["content_org"] = unicode("\n- Please click [[" + student_course_approval_url_link + "][here]] to approve students.")

            task_dict["start_time"] = at_rt_dict["completed_on"]
            task_dict["end_time"] = None
            task_dict["Status"] = u"New"
            task_dict["Priority"] = u"High"

            task_dict["group_set"] = [mis_admin._id]

            task_dict["Assignee"] = []
            for each_admin_id in mis_admin.group_admin:
              task_dict["Assignee"].append(each_admin_id)

            task_node = create_task(task_dict)

            at_rt_dict["has_corresponding_task"] = [task_node._id]

          if sce_gs.has_key("_id"):
            # Save/Update GAttribute(s) and/or GRelation(s)

            for at_rt_name in at_rt_list:
              at_rt_type_node = collection.Node.one(
                {'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': at_rt_name}
              )

              if at_rt_type_node:
                at_rt_node = None
                
                if at_rt_dict.has_key(at_rt_name) and at_rt_dict[at_rt_name]:
                  if at_rt_type_node._type == "AttributeType" and at_rt_dict[at_rt_name]:
                    at_rt_node = create_gattribute(sce_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])

                  elif at_rt_type_node._type == "RelationType" and at_rt_dict[at_rt_name]:
                    at_rt_node = create_grelation(sce_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])

                  # Very important 
                  sce_gs.reload()

              else:
                raise Exception("\n StudentCourseEnrollmentUpdateError: No AttributeType/RelationType found with given name ("+at_rt_name+") !!!\n")

          # Publish enrollment node & update the enrollment task as "In Progress/Closed"
          # task_node = collection.Node.one({'_id': task_id})
          task_dict = {}
          if enrollState == "Complete":
            sce_gs.status = u"PUBLISHED"
            sce_gs.save()

            task_dict["_id"] = task_id
            task_dict["Status"] = u"Closed"
            task_dict["modified_by"] = request.user.id
            task_node = create_task(task_dict)

          elif enrollState == "In Progress":
            task_dict["_id"] = task_id
            task_dict["Status"] = u"In Progress"
            task_dict["modified_by"] = request.user.id
            task_node = create_task(task_dict)

        else:
          raise Exception("\n StudentCourseEnrollmentError: No Announced Course exists with given ObjectId ("+announced_courses_id+") !!! \n")

      else:
        raise Exception("\n StudentCourseEnrollmentError: No Announced Course selected !!! \n")

      return HttpResponseRedirect(reverse(app_name.lower()+":"+template_prefix+'_app_detail', kwargs={'group_id': group_id, "app_id":app_id, "app_set_id":app_set_id}))

    else:
      task_id = request.GET.get("task_id", "")
      nussd_course_type = request.GET.get("nussd_course_type", "")
      ann_course_id = request.GET.get("ann_course_id", "")

      # Fetch announced course for which enrollment is open
      sce_gst = collection.Node.one({'_type': "GSystemType", 'name': "StudentCourseEnrollment"})
      enrollment_open_ann_course_ids = []
      if sce_gst:
        sce_cur = collection.Node.find(
          {'member_of': sce_gst._id, 'attribute_set.completed_on': {'$exists': False}, 'relation_set.has_corresponding_task': {'$exists': False}},
          {'relation_set.for_acourse': 1}
        )

        if sce_cur.count():
          for ac in sce_cur:
            for rel in ac.relation_set:
              if rel and rel.has_key("for_acourse"):
                ac_id = rel["for_acourse"][0]
                if ac_id not in enrollment_open_ann_course_ids:
                  enrollment_open_ann_course_ids.append(ac_id.__str__())

      # Fetch required list of AttributeTypes
      fetch_ATs = ["nussd_course_type", "degree_year"]
      req_ATs = []

      for each in fetch_ATs:
        each = collection.Node.one({'_type': "AttributeType", 'name': each}, {'_type': 1, '_id': 1, 'data_type': 1, 'complex_data_type': 1, 'name': 1, 'altnames': 1})

        if each["data_type"] == "IS()":
          # Below code does little formatting, for example:
          # data_type: "IS()" complex_value: [u"ab", u"cd"] dt:
          # "IS(u'ab', u'cd')"
          dt = "IS("
          for v in each.complex_data_type:
              dt = dt + "u'" + v + "'" + ", " 
          dt = dt[:(dt.rfind(", "))] + ")"
          each["data_type"] = dt

        each["data_type"] = eval(each["data_type"])
        each["value"] = None
        req_ATs.append(each)

      # Fetch required list of Colleges
      college_cur = None
      
      template = "ndf/student_enroll.html"
      variable = RequestContext(request, {'groupid': group_id, 'group_id': group_id,
                                          'title': title, 
                                          'app_id':app_id, 'app_name': app_name, 
                                          'app_collection_set': app_collection_set, 'app_set_id': app_set_id,
                                          'ATs': req_ATs, 'colleges': college_cur,
                                          'task_id': task_id, 'nussd_course_type': nussd_course_type, 'ann_course_id': ann_course_id,
                                          'enrollment_open_ann_course_ids': enrollment_open_ann_course_ids
                                          # 'nodes':nodes, 
                                          })
      return render_to_response(template, variable)


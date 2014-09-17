''' -- imports from python libraries -- '''
# from datetime import datetime
import datetime

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

from mongokit import IS

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation

collection = get_database()[Node.collection_name]

def person_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  custom view for custom GAPPS
  """
  # print "\n Found person_detail n gone inn this...\n\n"

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

  # print "\n coming in person detail... \n"
  # app_name = "mis"
  app_set = ""
  app_collection_set = []
  title = ""

  person_gst = None
  person_gs = None

  nodes = None
  node = None
  property_order_list = []
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
    person_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    title = person_gst.name
  
    template = "ndf/" + person_gst.name.strip().lower().replace(' ', '_') + "_list.html"
    default_template = "ndf/person_list.html"

    if request.method=="POST":
      search = request.POST.get("search","")
      classtype = request.POST.get("class","")
      nodes = collection.Node.find({'member_of': person_gst._id, 'name': {'$regex': search, '$options': 'i'}})
    else:
      nodes = collection.Node.find({'member_of': person_gst._id, 'group_set': ObjectId(group_id)})

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
                        'nodes': nodes, 'node': node,
                        'property_order_list': property_order_list,
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
  # print "\n Found person_create_edit n gone inn this...\n\n"

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
  # print "\n property_order_list: ", property_order_list, "\n"

  if request.method == "POST":
    # [A] Save person-node's base-field(s)
    # print "\n Going before....", type(person_gs), "\n person_gs.keys(): ", person_gs.keys()
    # get_node_common_fields(request, person_gs, group_id, person_gst)
    # print "\n Going after....", type(person_gs), "\n person_gs.keys(): ", person_gs.keys()
    # print "\n person_gs: \n", person_gs.keys()
    # for k, v in person_gs.items():
    #   print "\n ", k, " -- ", v
    is_changed = get_node_common_fields(request, person_gs, group_id, person_gst)

    if is_changed:
      # Remove this when publish button is setup on interface
      person_gs.status = u"PUBLISHED"

    person_gs.save(is_changed=is_changed)
  
    # [B] Store AT and/or RT field(s) of given person-node (i.e., person_gs)
    for tab_details in property_order_list:
      for field_set in tab_details[1]:
        # field_set pattern -- {[field_set[0]:node_structure, field_set[1]:field_base/AT/RT_instance{'_id':, 'name':, 'altnames':}, field_set[2]:node_value]}
        # field_set pattern -- {'_id', 'data_type', 'name', 'altnames', 'value'}
        # print " ", field_set["name"]

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
              # print "\n Parsing data for: ", field_instance["name"]
              if field_instance["name"] in ["12_passing_year", "degree_passing_year"]: #, "registration_year"]:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%Y")
              elif field_instance["name"] in ["dob", "registration_date"]:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%m/%d/%Y")
              else:
                field_value = parse_template_data(field_data_type, field_value, date_format_string="%m/%d/%Y %H:%M")

              if field_value:
                person_gs_triple_instance = create_gattribute(person_gs._id, collection.AttributeType(field_instance), field_value)
                # print "\n person_gs_triple_instance: ", person_gs_triple_instance._id, " -- ", person_gs_triple_instance.name

            else:
              field_value_list = request.POST.getlist(field_instance["name"])

              # field_instance_type = "GRelation"
              for i, field_value in enumerate(field_value_list):
                field_value = parse_template_data(field_data_type, field_value, field_instance=field_instance, date_format_string="%m/%d/%Y %H:%M")
                field_value_list[i] = field_value

              person_gs_triple_instance = create_grelation(person_gs._id, collection.RelationType(field_instance), field_value_list)
              # if isinstance(person_gs_triple_instance, list):
              #   print "\n"
              #   for each in person_gs_triple_instance:
              #     print " person_gs_triple_instance: ", each._id, " -- ", each.name
              #   print "\n"

              # else:
              #   print "\n person_gs_triple_instance: ", person_gs_triple_instance._id, " -- ", person_gs_triple_instance.name
    
    # return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'app_id': page_node._id }))
    return HttpResponseRedirect(reverse(app_name.lower()+":"+template_prefix+'_app_detail', kwargs={'group_id': group_id, "app_id":app_id, "app_set_id":app_set_id}))
  
  default_template = "ndf/person_create_edit.html"
  # default_template = "ndf/"+template_prefix+"_create_edit.html"
  context_variables = { 'groupid': group_id, 
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'property_order_list': property_order_list
                      }

  if app_set_instance_id:
    context_variables['node'] = person_gs

  try:
    # print "\n template-list: ", [template, default_template]
    # template = "ndf/fgh.html"
    # default_template = "ndf/dsfjhk.html"
    # return render_to_response([template, default_template], 
    return render_to_response([template, default_template], 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    # print "\n ", tde
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
    college = collection.Node.one({'_type': "GSystemType", 'name': "College"}, {'_id': 1})
    mis_admin = collection.Node.one({'_type': "Group", 'name': "MIS_admin"}, {'_id': 1})
    college_cur = collection.Node.find({'member_of': college._id, 'group_set': mis_admin._id}, {'name': 1}).sort('name', 1)

    template = "ndf/student_enroll.html"
    variable = RequestContext(request, {'groupid': group_id, 'group_id': group_id,
                                        'title': title, 
                                        'app_id':app_id, 'app_name': app_name, 
                                        'app_collection_set': app_collection_set, 'app_set_id': app_set_id,
                                        'ATs': req_ATs, 'colleges': college_cur
                                        # 'nodes':nodes, 
                                        })
    return render_to_response(template, variable)

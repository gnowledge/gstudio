''' -- imports from python libraries -- '''
# from datetime import datetime
import datetime

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
from django.contrib.sites.models import Site

from django_mongokit import get_database
import json  
try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data
from gnowsys_ndf.ndf.views.notify import set_notif_val
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, create_task

collection = get_database()[Node.collection_name]
GST_COURSE = collection.Node.one({'_type': "GSystemType", 'name': GAPPS[7]})
app = collection.Node.one({'_type': "GSystemType", 'name': GAPPS[7]})

def course(request, group_id, course_id=None):
    """
    * Renders a list of all 'courses' available within the database.
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
      group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if group_ins:
        group_id = str(group_ins._id)
      else :
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :
          group_id = str(auth._id)
    else :
        pass
    
    if course_id is None:
      course_ins = collection.Node.find_one({'_type':"GSystemType", "name":"Course"})
      if course_ins:
        course_id = str(course_ins._id)

    if request.method == "POST":
      # Course search view
      title = GST_COURSE.name
      
      search_field = request.POST['search_field']
      course_coll = collection.Node.find({'member_of': {'$all': [ObjectId(GST_COURSE._id)]},
                                         '$or': [
                                            {'$and': [
                                              {'name': {'$regex': search_field, '$options': 'i'}}, 
                                              {'$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                ]
                                              }
                                              ]
                                            },
                                            {'$and': [
                                              {'tags': {'$regex':search_field, '$options': 'i'}},
                                              {'$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                ]
                                              }
                                              ]
                                            }
                                          ],
                                         'group_set': {'$all': [ObjectId(group_id)]}
                                     }).sort('last_update', -1)

      # course_nodes_count = course_coll.count()

      return render_to_response("ndf/course.html",
                                {'title': title,
                                 'appId':app._id,
                                 'searching': True, 'query': search_field,
                                 'course_coll': course_coll, 'groupid':group_id, 'group_id':group_id
                                }, 
                                context_instance=RequestContext(request)
                                )

    elif GST_COURSE._id == ObjectId(course_id):
      # Course list view
      title = GST_COURSE.name
      course_coll = collection.GSystem.find({'member_of': {'$all': [ObjectId(course_id)]}, 
                                             'group_set': {'$all': [ObjectId(group_id)]},
                                             '$or': [
                                              {'access_policy': u"PUBLIC"},
                                              {'$and': [
                                                {'access_policy': u"PRIVATE"}, 
                                                {'created_by': request.user.id}
                                                ]
                                              }
                                             ]
                                            })
      template = "ndf/course.html"
      variable = RequestContext(request, {'title': title, 'course_nodes_count': course_coll.count(), 'course_coll': course_coll, 'groupid':group_id, 'appId':app._id, 'group_id':group_id})
      return render_to_response(template, variable)

@login_required
def create_edit(request, group_id, node_id = None):
    """Creates/Modifies details about the given quiz-item.
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    context_variables = { 'title': GST_COURSE.name,
                          'group_id': group_id,
                          'groupid':group_id
                      }

    if node_id:
        course_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
    else:
        course_node = collection.GSystem()

    if request.method == "POST":
        # get_node_common_fields(request, course_node, group_id, GST_COURSE)
        course_node.save(is_changed=get_node_common_fields(request, course_node, group_id, GST_COURSE))
        return HttpResponseRedirect(reverse('course', kwargs={'appId':app._id,'group_id': group_id}))
        
    else:
        if node_id:
            context_variables['node'] = course_node
            context_variables['groupid']=group_id
            context_variables['group_id']=group_id
            context_variables['appId']=app._id
        return render_to_response("ndf/course_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )

def course_detail(request, group_id, _id):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    course_node = collection.Node.one({"_id": ObjectId(_id)})
    if course_node._type == "GSystemType":
      return course(request, group_id, _id)
    return render_to_response("ndf/course_detail.html",
                                  { 'node': course_node,
                                    'groupid': group_id,
                                    'group_id':group_id,
                                    'appId':app._id
                                  },
                                  context_instance = RequestContext(request)
        )

# ===================================================================================

@login_required
def course_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  Creates/Modifies document of given sub-types of Course(s).
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

  app_set = ""
  app_collection_set = []
  title = ""

  course_gst = None
  course_gs = None

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

  if app_set_id:
    course_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    template = "ndf/" + course_gst.name.strip().lower().replace(' ', '_') + "_create_edit.html"
    title = course_gst.name
    course_gs = collection.GSystem()
    course_gs.member_of.append(course_gst._id)

  if app_set_instance_id:
    course_gs = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})

  property_order_list = get_property_order_with_value(course_gs)

  if request.method == "POST":
    # [A] Save course-node's base-field(s)

    start_time = ""
    if request.POST.has_key("start_time"):
      #convert string into datetime object
      start_time = request.POST.get("start_time", "")
      start_time = datetime.datetime.strptime(start_time,"%m/%Y")
      #get month name (%b for abbreviation and %B for full name) and year and convert to str


    end_time = ""
    if request.POST.has_key("end_time"):
      end_time = request.POST.get("end_time", "")
      end_time = datetime.datetime.strptime(end_time,"%m/%Y")

    start_enroll = ""
    if request.POST.has_key("start_enroll"):
      start_enroll = request.POST.get("start_enroll", "")
      start_enroll = datetime.datetime.strptime(start_enroll,"%d/%m/%Y")

    end_enroll = ""
    if request.POST.has_key("end_enroll"):
      end_enroll = request.POST.get("end_enroll", "")
      end_enroll = datetime.datetime.strptime(end_enroll,"%d/%m/%Y")
      
    nussd_course_type = ""
    if request.POST.has_key("nussd_course_type"):
      nussd_course_type = request.POST.get("nussd_course_type", "")
      nussd_course_type = unicode(nussd_course_type)

    unset_ac_options = []
    if request.POST.has_key("unset-ac-options"):
      unset_ac_options = request.POST.getlist("unset-ac-options")

    else:
      unset_ac_options = ["dummy"] # Just to execute loop at least once for Course Sub-Types other than 'Announced Course'
    
    if course_gst.name == u"Announced Course":

      if app_set_instance_id: 
        course_gs.get_neighbourhood(course_gs.member_of)
        course_gs.keys()
        collection.update({'_id':course_gs._id,'attribute_set.end_enroll': course_gs.attribute_set[4]["end_enroll"]},
                          {'$set':{'attribute_set.$.end_enroll': end_enroll}},upsert= False, multi = False)
        course_gs.reload()

      else:
        announce_to_colg_list = request.POST.get("announce_to_colg_list", "")
        colg_names = []
        colg_names = announce_to_colg_list.split(',')
        colg_gst = collection.Node.one({'_type': "GSystemType", 'name': 'College'})
        colg_list_cur = collection.Node.find(
          {'name': {'$in': colg_names}, 'member_of': colg_gst._id}, 
          {'_id':1, 'name':1, 'attribute_set': 1, 'relation_set': 1}
        )

        officer_incharge_of_rt = collection.Node.one({'_type': "RelationType", 'name': "officer_incharge_of"})
        for colg_ids in colg_list_cur: 
          # For each selected college
          for each in unset_ac_options:
            # each is ObjecId of the course.
            # For each selected course to Announce
            nm = ""
            if course_gst.name == u"Announced Course":
              # Code to be executed only for 'Announced Course' GSystem(s)
              sid, nm = each.split(">>")
              course_gs = collection.Node.one({'_type': "GSystem", '_id': ObjectId(sid), 'member_of': course_gst._id})
              if not course_gs:
                course_gs = collection.GSystem()
              else:
                if " -- " in nm:
                  nm = nm.split(" -- ")[0].lstrip().rstrip()

              course_node = collection.Node.one({'_id':ObjectId(sid)})
              c_name = unicode(course_node.attribute_set[1][u'course_code'] + "_" + colg_ids.attribute_set[0][u"enrollment_code"]+"_" +start_time.strftime("%b_%Y") + "_" + end_time.strftime("%b_%Y"))
              request.POST["name"] = c_name
            
            is_changed = get_node_common_fields(request, course_gs, group_id, course_gst)
            if is_changed:
              # Remove this when publish button is setup on interface
              course_gs.status = u"PUBLISHED"
            
            course_gs.save(is_changed=is_changed)

            # [B] Store AT and/or RT field(s) of given course-node (i.e., course_gs)
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
                        if field_instance["name"] in request.FILES:
                          field_value = request.FILES[field_instance["name"]]

                        else:
                          field_value = ""
                        
                        # Below 0th index is used because that function returns tuple(ObjectId, bool-value)
                        if field_value != '' and field_value != u'':
                          file_name = course_gs.name + " -- " + field_instance["altnames"]
                          content_org = ""
                          tags = ""
                          field_value = save_file(field_value, file_name, request.user.id, group_id, content_org, tags, oid=True)[0]

                      else:
                        # Other AttributeTypes 
                        field_value = request.POST.get(field_instance["name"], "")

                      if field_instance["name"] in ["start_time","end_time"]: #Course Duration 
                        field_value = parse_template_data(field_data_type, field_value, date_format_string="%m/%Y")

                      elif field_instance["name"] in ["start_enroll", "end_enroll"]: #Student Enrollment DUration
                        field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y")

                      elif field_instance["name"] in ["mast_tr_qualifications", "voln_tr_qualifications"]:
                        # Needs sepcial kind of parsing
                        field_value = []
                        tr_qualifications = request.POST.get(field_instance["name"], '')
                        
                        if tr_qualifications:
                          qualifications_dict = {}
                          tr_qualifications = [each.strip() for each in tr_qualifications.split(",")]
                          
                          for i, each in enumerate(tr_qualifications):
                            if (i % 2) == 0:
                              if each == "true":
                                qualifications_dict["mandatory"] = True
                              elif each == "false":
                                qualifications_dict["mandatory"] = False
                            else:
                              qualifications_dict["text"] = unicode(each)
                              field_value.append(qualifications_dict)
                              qualifications_dict = {}
                      
                      elif field_instance["name"] in ["max_marks", "min_marks"]:
                        # Needed because both these fields' values are dependent upon evaluation_type field's value
                        evaluation_type = request.POST.get("evaluation_type", "")
                        if evaluation_type == u"Continuous":
                          field_value = None
                        field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y %H:%M")

                      else:
                        field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y %H:%M")
                      course_gs_triple_instance = create_gattribute(course_gs._id, collection.AttributeType(field_instance), field_value)

                    else:
                      #i.e if field_instance_type == RelationType
                      if field_instance["name"] == "announced_for":
                        field_value = ObjectId(sid)
                        #Pass ObjectId of selected Course

                      elif field_instance["name"] == "acourse_for_college":
                        field_value = colg_ids._id
                        #Pass ObjectId of selected College
                      
                      course_gs_triple_instance = create_grelation(course_gs._id, collection.RelationType(field_instance), field_value)

            # Create task for PO of respective college 
            # for Student-Course Enrollment
            task_dict = {}
            task_dict["name"] = unicode(colg_ids.attribute_set[0]["enrollment_code"] + " -- " + nm + " -- " + "Student-Course_Enrollment" + " -- " + start_enroll.strftime("%d/%m/%Y") + " -- " + end_enroll.strftime("%d/%m/%Y"))
            task_dict["created_by"] = request.user.id
            task_dict["created_by_name"] = request.user.username
            task_dict["modified_by"] = request.user.id
            task_dict["contributors"] = [request.user.id]
            
            MIS_GAPP = collection.Node.one({'_type': "GSystemType", 'name': "MIS"}, {'_id': 1})
            Student = collection.Node.one({'_type': "GSystemType", 'name': "Student"}, {'_id': 1})
            college_enrollment_url_link = ""
            if MIS_GAPP and Student:
              site = Site.objects.get(pk=1)
              site = site.name.__str__()
              college_enrollment_url_link = "http://" + site + "/" + colg_ids.name.replace(" ","%20").encode('utf8') + "/mis/" + str(MIS_GAPP._id) + "/" + str(Student._id) + "/enroll/" 
            task_dict["content_org"] = "\n- Please click [[" + college_enrollment_url_link + "][here]] to enroll students in " + nm + " course.\n\n- This enrollment procedure is open for duration between " + start_time.strftime("%b %Y") + " and " + end_time.strftime("%b %Y") + "."

            # Reload required so that updated attribute_set & relation_set appears
            course_gs.reload()
            task_dict["start_time"] = course_gs.attribute_set[3]["start_enroll"]
            task_dict["end_time"] = course_gs.attribute_set[4]["end_enroll"]
            task_dict["Status"] = u"New"
            task_dict["Priority"] = u"High"

            task_dict["Assignee"] = []
            # Fetch Program Officers' ObjectIds from
            # College's inverse GRelation "officer_incharge_of"
            PO_list = collection.Triple.find(
              {'_type': "GRelation", 'relation_type.$id': officer_incharge_of_rt._id, 'right_subject': colg_ids._id},
              {'subject': 1}
            )

            # From 'subject' fetch corresponding Program Officer node
            # From that node's 'has_login' relation fetch corresponding Author node
            for each in PO_list:
              PO = collection.Node.one(
                {'_id': each.subject, 'attribute_set.email_id': {'$exists': True}, 'relation_set.has_login': {'$exists': True}},
                {'name': 1, 'attribute_set.email_id': 1, 'relation_set.has_login': 1}
              )

              PO_auth = None
              for rel in PO.relation_set:
                if rel:
                  PO_auth = collection.Node.one({'_type': "Author", '_id': ObjectId(rel["has_login"][0])})
                  if PO_auth:
                    task_dict["Assignee"].append(PO_auth.name)
                    task_dict["group_set"] = [PO_auth._id]

            task_node = create_task(task_dict)

    else:
      is_changed = get_node_common_fields(request, course_gs, group_id, course_gst)
      
      if is_changed:
        # Remove this when publish button is setup on interface
        course_gs.status = u"PUBLISHED"
      
      course_gs.save(is_changed=is_changed)
  
      # [B] Store AT and/or RT field(s) of given course-node (i.e., course_gs)
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
                  if field_instance["name"] in request.FILES:
                    field_value = request.FILES[field_instance["name"]]

                  else:
                    field_value = ""
                  
                  # Below 0th index is used because that function returns tuple(ObjectId, bool-value)
                  if field_value != '' and field_value != u'':
                    file_name = course_gs.name + " -- " + field_instance["altnames"]
                    content_org = ""
                    tags = ""
                    field_value = save_file(field_value, file_name, request.user.id, group_id, content_org, tags, oid=True)[0]

                else:
                  # Other AttributeTypes 
                  field_value = request.POST.get(field_instance["name"], "")

                if field_instance["name"] in ["start_time","end_time"]: #Course Duration 
                  field_value = parse_template_data(field_data_type, field_value, date_format_string="%m/%Y")

                elif field_instance["name"] in ["start_enroll", "end_enroll"]: #Student Enrollment DUration
                  field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y")

                elif field_instance["name"] in ["mast_tr_qualifications", "voln_tr_qualifications"]:
                  # Needs sepcial kind of parsing
                  field_value = []
                  tr_qualifications = request.POST.get(field_instance["name"], '')
                  
                  if tr_qualifications:
                    qualifications_dict = {}
                    tr_qualifications = [each.strip() for each in tr_qualifications.split(",")]
                    
                    for i, each in enumerate(tr_qualifications):
                      if (i % 2) == 0:
                        if each == "true":
                          qualifications_dict["mandatory"] = True
                        elif each == "false":
                          qualifications_dict["mandatory"] = False
                      else:
                        qualifications_dict["text"] = unicode(each)
                        field_value.append(qualifications_dict)
                        qualifications_dict = {}
                
                elif field_instance["name"] in ["max_marks", "min_marks"]:
                  # Needed because both these fields' values are dependent upon evaluation_type field's value
                  evaluation_type = request.POST.get("evaluation_type", "")
                  if evaluation_type == u"Continuous":
                    field_value = None
                  field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y %H:%M")

                else:
                  field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y %H:%M")
                course_gs_triple_instance = create_gattribute(course_gs._id, collection.AttributeType(field_instance), field_value)

              else:
                #i.e if field_instance_type == RelationType
                if field_instance["name"] == "announced_for":
                  field_value = ObjectId(sid)
                  #Pass ObjectId of selected Course

                elif field_instance["name"] == "acourse_for_college":
                  field_value = colg_ids._id
                  #Pass ObjectId of selected College
                
                course_gs_triple_instance = create_grelation(course_gs._id, collection.RelationType(field_instance), field_value)

    return HttpResponseRedirect(reverse(app_name.lower()+":"+template_prefix+'_app_detail', kwargs={'group_id': group_id, "app_id":app_id, "app_set_id":app_set_id}))
  univ = collection.Node.one({'_type': "GSystemType", 'name': "University"}, {'_id': 1})
  university_cur = collection.Node.find({'member_of': univ._id}, {'name': 1}).sort('name', 1)
  

  default_template = "ndf/course_create_edit.html"
  context_variables = { 'groupid': group_id, 'group_id': group_id,
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'university_cur':university_cur,
                        'property_order_list': property_order_list,
                      }

  if app_set_instance_id:
    course_gs.get_neighbourhood(course_gs.member_of)
    course_gs.keys()
    context_variables['node'] = course_gs
    for each_in in course_gs.attribute_set:
      for eachk,eachv in each_in.items():
        context_variables[eachk] = eachv
    for each_in in course_gs.relation_set:
      for eachk,eachv in each_in.items():
        get_node_name = collection.Node.one({'_id':eachv[0]})
        context_variables[eachk] = get_node_name.name

  try:
    return render_to_response([template, default_template], 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    error_message = "\n CourseCreateEditViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n CourseCreateEditViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)


def course_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  custom view for custom GAPPS
  """
  # print "\n Found course_detail n gone inn this...\n\n"

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

  course_gst = None
  course_gs = None

  nodes = None
  node = None
  property_order_list = []
  is_link_needed = True         # This is required to show Link button on interface that link's Student's/VoluntaryTeacher's node with it's corresponding Author node

  template_prefix = "mis"
  context_variables = {}

  #Course structure collection _dict
  course_collection_dict = {}
  course_collection_dict_exists = False

  if request.user:
    if auth is None:
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username)})
    agency_type = auth.agency_type
    agency_type_node = collection.Node.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
    if agency_type_node:
      for eachset in agency_type_node.collection_set:
        app_collection_set.append(collection.Node.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      

  if app_set_id:
    course_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    title = course_gst.name
  
    template = "ndf/course_list.html"
    if request.method=="POST":
      search = request.POST.get("search","")
      classtype = request.POST.get("class","")
      # nodes = list(collection.Node.find({'name':{'$regex':search, '$options': 'i'},'member_of': {'$all': [course_gst._id]}}))
      nodes = collection.Node.find({'member_of': course_gst._id, 'name': {'$regex': search, '$options': 'i'}})
    else:
      nodes = collection.Node.find({'member_of': course_gst._id, 'group_set': ObjectId(group_id)})


  cs_gst = collection.Node.one({'_type': "GSystemType", 'name':"CourseSection"})
  css_gst = collection.Node.one({'_type': "GSystemType", 'name':"CourseSubSection"})

  if app_set_instance_id :
    template = "ndf/course_details.html"

    node = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    property_order_list = get_property_order_with_value(node)
    node.get_neighbourhood(node.member_of)

    #get the course structure
    for eachcs in node.collection_set:
      coll_node_cs = collection.Node.one({'_id':eachcs,'member_of':cs_gst._id},{'name':1,'collection_set':1})
      css_dict = {}
      for eachcss in coll_node_cs.collection_set:
        coll_node_css = collection.Node.one({'_id':eachcss, 'member_of':css_gst._id},{'name':1,'collection_set':1,'attribute_set':1})
        css_dict[coll_node_css.name] = {}
        css_dict[coll_node_css.name]["course_structure_minutes"] = coll_node_css.attribute_set[0]["course_structure_minutes"]
        course_collection_dict[coll_node_cs.name] = css_dict
    print course_collection_dict,"course_collection_dict"
    if course_collection_dict:
      course_collection_dict_exists = True

  context_variables = { 'groupid': group_id, 
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'course_collection_dict':course_collection_dict,
                        'course_collection_dict_exists':course_collection_dict_exists,
                        'nodes': nodes, 'node': node,
                        'property_order_list': property_order_list,
                        'is_link_needed': is_link_needed
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
    error_message = "\n CourseDetailListViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n CourseDetailListViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)


def create_course_struct(request, group_id,node_id):
    """
    This view is to create the structure of the Course.
    A Course holds CourseSection, which further holds CourseSubSection
    in their respective collection_set.

    A tree depiction to this is as follows:
      Course Name:
        1. CourseSection1
          1.1. CourseSubSection1
          1.2. CourseSubSection2
        2. CourseSection2
          2.1. CourseSubSection3

    """

    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass

    property_order_list_cs = []
    property_order_list_css = []
    course_collection_dict = {}
    course_collection_dict_exists = False
    coll_node_cs = None
    coll_node_css = None

    title = "Course Structure"

    course_node = collection.Node.one({"_id": ObjectId(node_id)})

    cs_gst = collection.Node.one({'_type': "GSystemType", 'name':"CourseSection"})
    cs_gs = collection.GSystem()
    cs_gs.member_of.append(cs_gst._id)
    property_order_list_cs = get_property_order_with_value(cs_gs)

    css_gst = collection.Node.one({'_type': "GSystemType", 'name':"CourseSubSection"})
    css_gs = collection.GSystem()
    css_gs.member_of.append(css_gst._id)
    property_order_list_css = get_property_order_with_value(css_gs)

    #get the course structure
    for eachcs in course_node.collection_set:
      coll_node_cs = collection.Node.one({'_id':eachcs,'member_of':cs_gst._id},{'name':1,'collection_set':1})
      css_dict = {}
      for eachcss in coll_node_cs.collection_set:
        coll_node_css = collection.Node.one({'_id':eachcss, 'member_of':css_gst._id},{'name':1,'collection_set':1,'attribute_set':1})
        css_dict[coll_node_css.name] = {}
        css_dict[coll_node_css.name]["course_structure_minutes"] = coll_node_css.attribute_set[0]["course_structure_minutes"]
        course_collection_dict[coll_node_cs.name] = css_dict

    if course_collection_dict:
      course_collection_dict_exists = True

    eval_type = course_node.attribute_set[5][u"evaluation_type"]
    #If evaluation_type flag is True, it is Final. If False, it is Continous
    if(eval_type==u"Final"):
        eval_type_flag = True
    else:
        eval_type_flag = False
    at_cs_hours = collection.Node.one({'_type':'AttributeType', 'name':'course_structure_minutes'})
    if request.method=="POST":
        course_sec_dict = request.POST.get("course_sec_dict_ele","")
        course_sec_dict = json.loads(course_sec_dict)
        cs_ids = []

        #creating course structure GSystems
        if not course_collection_dict_exists:
          for cs,v in course_sec_dict.items():
            cs_new = collection.GSystem()
            cs_new.member_of.append(cs_gst._id)
            #set name
            cs_new.name = cs
            cs_new.modified_by=int(request.user.id)
            cs_new.created_by=int(request.user.id)
            cs_new.contributors.append(int(request.user.id))
            #save the cs gs
            cs_new.prior_node.append(course_node._id)
            cs_new.save()
            cs_ids.append(cs_new._id)
            css_ids = []
            for css,val in v.items():
              css_new = collection.GSystem()
              css_new.member_of.append(css_gst._id)
              #set name
              css_new.name = css
              css_new.modified_by=int(request.user.id)
              css_new.created_by=int(request.user.id)
              css_new.contributors.append(int(request.user.id))
              #save the css gs
              css_new.prior_node.append(cs_new._id)
              css_new.save()
              #add to cs collection_set
              css_ids.append(css_new._id)
              for propk, propv in val.items():
                # add attributes to css gs
                create_gattribute(css_new._id,at_cs_hours,int(propv))
            #append CSS to CS
            collection.update({'_id':cs_new._id},{'$set':{'collection_set':css_ids}},upsert=False,multi=False)
            # cs_new.save()
        else:
          if (course_collection_dict==course_sec_dict):
            pass
          else:
            for k in course_sec_dict:#loops over course sections
              if course_collection_dict.has_key(k):
                if(course_sec_dict[k]==course_collection_dict[k]):
                  pass
                else:
                  for k1 in course_sec_dict[k]:#loops over course sub sections
                    if course_collection_dict[k].has_key(k1):
                      if(course_sec_dict[k][k1]==course_collection_dict[k][k1]):
                        pass
                      else:
                        for k2 in course_sec_dict[k][k1]:
                          
                          create_gattribute(css_node._id,at_cs_hours,int(course_sec_dict[k][k1][k2]))
                    else:
                      css_new = collection.GSystem()
                      css_new.member_of.append(css_gst._id)
                      #set name
                      css_new.name = k1
                      css_new.modified_by=int(request.user.id)
                      css_new.created_by=int(request.user.id)
                      css_new.contributors.append(int(request.user.id))
                      #save the css gs
                      cs_node = collection.Node.one({"name":k,"member_of":cs_gst._id,'prior_node':course_node._id},{'collection_set':1})
                      css_new.prior_node.append(cs_node._id)
                      css_new.save()

                      #adding course section node as prior node to course sub section node
                      for k2 in course_sec_dict[k][k1]:#loops over course sub sections' value dict that holds properties
                        if(k2=="course_structure_minutes"):
                          create_gattribute(css_new._id,at_cs_hours,int(course_sec_dict[k][k1][k2]))
                      #add to cs collection_set
                      collection.update({'_id':cs_node._id},{'$push':{'collection_set':css_new._id}}, upsert=False, multi=False)
              else:

                cs_new = collection.GSystem()
                cs_new.member_of.append(cs_gst._id)
                #set name
                cs_new.name = k
                cs_new.modified_by=int(request.user.id)
                cs_new.created_by=int(request.user.id)
                cs_new.contributors.append(int(request.user.id))
                #save the cs gs
                cs_new.prior_node.append(course_node._id)
                cs_new.save()
                cs_ids.append(cs_new._id)
                for k1 in course_sec_dict[k]:
                  css_new = collection.GSystem()
                  css_new.member_of.append(css_gst._id)
                  #set name
                  css_new.name = k1
                  css_new.modified_by=int(request.user.id)
                  css_new.created_by=int(request.user.id)
                  css_new.contributors.append(int(request.user.id))
                  #save the css gs
                  css_new.prior_node(cs_new._id)
                  css_new.save()
                  for k2 in course_sec_dict[k][k1]:
                    if(k2=="course_structure_minutes"):
                      create_gattribute(css_new._id,at_cs_hours,int(course_sec_dict[k][k1][k2]))
                  #add to cs collection_set
                  collection.update({'_id':cs_new._id},{'$push':{'collection_set':css_new._id}},upsert=False,multi=False)


        course_node_coll_set = course_node.collection_set
        for each in cs_ids:
          if each not in course_node_coll_set:
            course_node_coll_set.append(each)
        collection.update({'_id':course_node._id},{'$set':{'collection_set':course_node_coll_set}},upsert=False,multi=False)


    return render_to_response("ndf/create_course_structure.html",
                                  { 'cnode': course_node,
                                    'groupid': group_id,
                                    'group_id':group_id,
                                    'title':title,
                                    'appId':app._id,
                                    'node':None,
                                    'coll_node_cs':coll_node_cs,
                                    'coll_node_css':coll_node_css,
                                    'course_collection_dict':course_collection_dict,
                                    'property_order_list':property_order_list_cs,
                                    'property_order_list_css':property_order_list_css,
                                    'eval_type_flag': eval_type_flag
                                  },
                                  context_instance = RequestContext(request)
        )

  
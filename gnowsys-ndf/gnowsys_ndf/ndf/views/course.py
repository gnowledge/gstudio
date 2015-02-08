''' -- imports from python libraries -- '''
# from datetime import datetime
import datetime
import json

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
try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT, GSTUDIO_TASK_TYPES
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data
from gnowsys_ndf.ndf.views.notify import set_notif_val
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, create_task

collection = get_database()[Node.collection_name]
GST_COURSE = collection.Node.one({'_type': "GSystemType", 'name': GAPPS[7]})
app = collection.Node.one({'_type': "GSystemType", 'name': GAPPS[7]})

@login_required
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


@login_required
def course_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    Creates/Modifies document of given sub-types of Course(s).
    """

    auth = None
    if ObjectId.is_valid(group_id) is False:
        group_ins = collection.Node.one({'_type': "Group", "name": group_id})
        auth = collection.Node.one({
            '_type': 'Author', 'name': unicode(request.user.username)
        })

        if group_ins:
            group_id = str(group_ins._id)
        else:
            auth = collection.Node.one({
                '_type': 'Author', 'name': unicode(request.user.username)
            })
            if auth:
                group_id = str(auth._id)
    else:
        pass

    app = None
    if app_id is None:
        app = collection.Node.one({'_type': "GSystemType", 'name': app_name})
        if app:
            app_id = str(app._id)
    else:
        app = collection.Node.one({'_id': ObjectId(app_id)})

    app_name = app.name
    # app_set = ""
    app_collection_set = []
    title = ""

    course_gst = None
    course_gs = None
    mis_admin = None

    property_order_list = []

    template = ""
    template_prefix = "mis"

    if request.user:
        if auth is None:
            auth = collection.Node.one({
                '_type': 'Author', 'name': unicode(request.user.username)
            })

        agency_type = auth.agency_type
        agency_type_node = collection.Node.one({
            '_type': "GSystemType", 'name': agency_type
        }, {
            'collection_set': 1
        })
        if agency_type_node:
            for eachset in agency_type_node.collection_set:
                app_collection_set.append(
                    collection.Node.one({
                        "_id": eachset
                    }, {
                        '_id': 1, 'name': 1, 'type_of': 1
                    })
                )

    if app_set_id:
        course_gst = collection.Node.one({
            '_type': "GSystemType", '_id': ObjectId(app_set_id)
        }, {
            'name': 1, 'type_of': 1
        })

        template = "ndf/" + course_gst.name.strip().lower().replace(' ', '_') \
            + "_create_edit.html"
        title = course_gst.name

    if app_set_instance_id:
        course_gs = collection.Node.one({
            '_type': "GSystem", '_id': ObjectId(app_set_instance_id)
        })
    else:
        course_gs = collection.GSystem()
        course_gs.member_of.append(course_gst._id)

    property_order_list = get_property_order_with_value(course_gs)

    if request.method == "POST":
        # [A] Save course-node's base-field(s)
        start_time = ""
        if "start_time" in request.POST:
            start_time = request.POST.get("start_time", "")
            start_time = datetime.datetime.strptime(start_time, "%m/%Y")

        end_time = ""
        if "end_time" in request.POST:
            end_time = request.POST.get("end_time", "")
            end_time = datetime.datetime.strptime(end_time, "%m/%Y")

        nussd_course_type = ""
        if "nussd_course_type" in request.POST:
            nussd_course_type = request.POST.get("nussd_course_type", "")
            nussd_course_type = unicode(nussd_course_type)

        unset_ac_options = []
        if "unset-ac-options" in request.POST:
            unset_ac_options = request.POST.getlist("unset-ac-options")
        else:
            # Just to execute loop at least once for Course Sub-Types
            # other than 'Announced Course'
            unset_ac_options = ["dummy"]

        if course_gst.name == u"Announced Course":
            announce_to_colg_list = request.POST.get(
                "announce_to_colg_list", ""
            )

            announce_to_colg_list = [ObjectId(colg_id) for colg_id in announce_to_colg_list.split(",")]

            colg_ids = []
            # Parsing ObjectId -- from string format to ObjectId
            for each in announce_to_colg_list:
                if each and ObjectId.is_valid(each):
                    colg_ids.append(ObjectId(each))

            # Fetching college(s)
            colg_list_cur = collection.Node.find({
                '_id': {'$in': colg_ids}
            }, {
                'name': 1, 'attribute_set.enrollment_code': 1
            })

            if "_id" in course_gs:
                # It means we are in editing mode of given Announced Course GSystem
                unset_ac_options = [course_gs._id]

            ac_nc_code_list = []
            # Prepare a list
            # 0th index (ac_node): Announced Course node,
            # 1st index (nc_id): NUSSD Course node's ObjectId,
            # 2nd index (nc_course_code): NUSSD Course's code
            for cid in unset_ac_options:
                ac_node = None
                nc_id = None
                nc_course_code = ""

                # Here course_gst is Announced Course GSytemType's node
                ac_node = collection.Node.one({
                    '_id': ObjectId(cid), 'member_of': course_gst._id
                })

                # If ac_node found, means
                # (1) we are dealing with creating Announced Course
                # else,
                # (2) we are in editing phase of Announced Course
                course_node = None
                if not ac_node:
                    # In this case, cid is of NUSSD Course GSystem
                    # So fetch that to extract course_code
                    # Set to nc_id
                    ac_node = None
                    course_node = collection.Node.one({
                        '_id': ObjectId(cid)
                    })
                else:
                    # In this case, fetch NUSSD Course from
                    # Announced Course GSystem's announced_for relationship
                    for rel in ac_node.relation_set:
                        if "announced_for" in rel:
                            course_node_ids = rel["announced_for"]
                            break

                    # Fetch NUSSD Course GSystem
                    if course_node_ids:
                        course_node = collection.Node.find_one({
                            "_id": {"$in": course_node_ids}
                        })

                # If course_code doesn't exists then
                # set NUSSD Course GSystem's name as course_code
                if course_node:
                    nc_id = course_node._id
                    for attr in course_node.attribute_set:
                        if "course_code" in attr:
                            nc_course_code = attr["course_code"]
                            break
                    if not nc_course_code:
                        nc_course_code = course_node.name.replace(" ", "-")

                # Append to ac_nc_code_list
                ac_nc_code_list.append([ac_node, nc_id, nc_course_code])

            # For each selected college
            # Create Announced Course GSystem
            for college_node in colg_list_cur:
                # Fetch Enrollment code from "enrollment_code" (Attribute)
                college_enrollment_code = ""
                if college_node:
                    for attr in college_node.attribute_set:
                        if attr and "enrollment_code" in attr:
                            college_enrollment_code = attr["enrollment_code"]
                            break

                ann_course_id_list = []
                # For each selected course to Announce
                for ac_nc_code in ac_nc_code_list:
                    course_gs = ac_nc_code[0]
                    nc_id = ac_nc_code[1]
                    nc_course_code = ac_nc_code[2]

                    if not course_gs:
                        # Create new Announced Course GSystem
                        course_gs = collection.GSystem()
                        course_gs.member_of.append(course_gst._id)

                    # Prepare name for Announced Course GSystem
                    c_name = unicode(
                        nc_course_code + "_" + college_enrollment_code + "_"
                        + start_time.strftime("%b_%Y") + "-"
                        + end_time.strftime("%b_%Y")
                    )
                    request.POST["name"] = c_name

                    is_changed = get_node_common_fields(
                        request, course_gs, group_id, course_gst
                    )
                    if is_changed:
                        # Remove this when publish button is setup on interface
                        course_gs.status = u"PUBLISHED"

                    course_gs.save(is_changed=is_changed)

                    # [B] Store AT and/or RT field(s) of given course-node
                    for tab_details in property_order_list:
                        for field_set in tab_details[1]:
                            # Fetch only Attribute field(s) / Relation field(s)
                            if '_id' in field_set:
                                field_instance = collection.Node.one({
                                    '_id': field_set['_id']
                                })
                                field_instance_type = type(field_instance)

                                if (field_instance_type in
                                        [AttributeType, RelationType]):
                                    field_data_type = field_set['data_type']

                                    # Fetch field's value depending upon AT/RT
                                    # and Parse fetched-value depending upon
                                    # that field's data-type
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

                                        if field_instance["name"] in ["start_time", "end_time"]:
                                            # Course Duration
                                            field_value = parse_template_data(field_data_type, field_value, date_format_string="%m/%Y")
                                        else:
                                            field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y %H:%M")

                                        course_gs_triple_instance = create_gattribute(course_gs._id, collection.AttributeType(field_instance), field_value)

                                    else:
                                        # i.e if field_instance_type == RelationType
                                        if field_instance["name"] == "announced_for":
                                            field_value = ObjectId(nc_id)
                                            # Pass ObjectId of selected Course

                                        elif field_instance["name"] == "acourse_for_college":
                                            field_value = college_node._id
                                            # Pass ObjectId of selected College

                                        course_gs_triple_instance = create_grelation(course_gs._id, collection.RelationType(field_instance), field_value)

                    ann_course_id_list.append(course_gs._id)

        else:
            is_changed = get_node_common_fields(request, course_gs, group_id, course_gst)

            if is_changed:
                # Remove this when publish button is setup on interface
                course_gs.status = u"PUBLISHED"

            course_gs.save(is_changed=is_changed)

            # [B] Store AT and/or RT field(s) of given course-node
            for tab_details in property_order_list:
                for field_set in tab_details[1]:
                    # Fetch only Attribute field(s) / Relation field(s)
                    if '_id' in field_set:
                        field_instance = collection.Node.one({'_id': field_set['_id']})
                        field_instance_type = type(field_instance)

                        if field_instance_type in [AttributeType, RelationType]:
                            field_data_type = field_set['data_type']

                            # Fetch field's value depending upon AT/RT
                            # and Parse fetched-value depending upon
                            # that field's data-type
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

                                # if field_instance["name"] in ["start_time","end_time"]:
                                #     field_value = parse_template_data(field_data_type, field_value, date_format_string="%m/%Y")
                                # elif field_instance["name"] in ["start_enroll", "end_enroll"]: #Student Enrollment DUration
                                #     field_value = parse_template_data(field_data_type, field_value, date_format_string="%d/%m/%Y")
                                if field_instance["name"] in ["mast_tr_qualifications", "voln_tr_qualifications"]:
                                    # Needs sepcial kind of parsing
                                    field_value = []
                                    tr_qualifications = request.POST.get(field_instance["name"], '')

                                    if tr_qualifications:
                                        qualifications_dict = {}
                                        tr_qualifications = [qual.strip() for qual in tr_qualifications.split(",")]

                                        for i, qual in enumerate(tr_qualifications):
                                            if (i % 2) == 0:
                                                if qual == "true":
                                                    qualifications_dict["mandatory"] = True
                                                elif qual == "false":
                                                    qualifications_dict["mandatory"] = False
                                            else:
                                                qualifications_dict["text"] = unicode(qual)
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

                                course_gs_triple_instance = create_gattribute(
                                    course_gs._id,
                                    collection.AttributeType(field_instance),
                                    field_value
                                )

                            else:
                                #i.e if field_instance_type == RelationType
                                if field_instance["name"] == "announced_for":
                                    field_value = ObjectId(cid)
                                    #Pass ObjectId of selected Course

                                elif field_instance["name"] == "acourse_for_college":
                                    field_value = college_node._id
                                    #Pass ObjectId of selected College

                                course_gs_triple_instance = create_grelation(
                                    course_gs._id,
                                    collection.RelationType(field_instance),
                                    field_value
                                )

        return HttpResponseRedirect(
            reverse(
                app_name.lower() + ":" + template_prefix + '_app_detail',
                kwargs={
                    'group_id': group_id, "app_id": app_id,
                    "app_set_id": app_set_id
                }
            )
        )

    univ = collection.Node.one({
        '_type': "GSystemType", 'name': "University"
    }, {
        '_id': 1
    })
    university_cur = None

    if not mis_admin:
        mis_admin = collection.Node.one(
            {'_type': "Group", 'name': "MIS_admin"},
            {'_id': 1, 'name': 1, 'group_admin': 1}
        )

    if univ and mis_admin:
        university_cur = collection.Node.find(
            {'member_of': univ._id, 'group_set': mis_admin._id},
            {'name': 1}
        ).sort('name', 1)

    default_template = "ndf/course_create_edit.html"
    context_variables = {
        'groupid': group_id, 'group_id': group_id,
        'app_id': app_id, 'app_name': app_name,
        'app_collection_set': app_collection_set,
        'app_set_id': app_set_id,
        'title': title,
        'university_cur': university_cur,
        'property_order_list': property_order_list
    }

    if app_set_instance_id:
        course_gs.get_neighbourhood(course_gs.member_of)
        context_variables['node'] = course_gs
        for attr in course_gs.attribute_set:
            for eachk, eachv in attr.items():
                context_variables[eachk] = eachv

        for rel in course_gs.relation_set:
            for eachk, eachv in rel.items():
                get_node_name = collection.Node.one({'_id': eachv[0]})
                context_variables[eachk] = get_node_name.name

    try:
        return render_to_response(
            [template, default_template],
            context_variables, context_instance=RequestContext(request)
        )

    except TemplateDoesNotExist as tde:
        error_message = "\n CourseCreateEditViewError: This html template (" \
            + str(tde) + ") does not exists !!!\n"
        raise Http404(error_message)

    except Exception as e:
        error_message = "\n CourseCreateEditViewError: " + str(e) + " !!!\n"
        raise Exception(error_message)


@login_required
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
  course_collection_list = []
  course_collection_dict_exists = False

  if request.user:
    if auth is None:
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username)})

    if auth:
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
  at_cs_hours = collection.Node.one({'_type':'AttributeType', 'name':'course_structure_minutes'})
  at_cs_assessment = collection.Node.one({'_type':'AttributeType', 'name':'course_structure_assessment'})
  at_cs_assignment = collection.Node.one({'_type':'AttributeType', 'name':'course_structure_assignment'})
  at_cs_min_marks = collection.Node.one({'_type':'AttributeType', 'name':'min_marks'})
  at_cs_max_marks = collection.Node.one({'_type':'AttributeType', 'name':'max_marks'})

  if app_set_instance_id :
    template = "ndf/course_details.html"

    node = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    property_order_list = get_property_order_with_value(node)
    node.get_neighbourhood(node.member_of)


    #Course structure as list of dicts
    
    for eachcs in node.collection_set:
      cs_dict = {}
      coll_node_cs = collection.Node.one({'_id':ObjectId(eachcs),'member_of':cs_gst._id},{'name':1,'collection_set':1})
      cs_dict[coll_node_cs.name]=[]
      course_collection_list.append(cs_dict)
      for eachcss in coll_node_cs.collection_set:
        css_dict = {}
        coll_node_css = collection.Node.one({'_id':ObjectId(eachcss), 'member_of':css_gst._id},{'name':1,'collection_set':1,'attribute_set':1})
        css_dict[coll_node_css.name]={}
        for eachattr in coll_node_css.attribute_set:
          for eachk,eachv in eachattr.items():
            if (eachk=="course_structure_minutes"):
              css_dict[coll_node_css.name]["Minutes"] = eachv
            elif (eachk=="course_structure_assignment"):
              css_dict[coll_node_css.name]["Assignment"] = eachv
            elif (eachk=="course_structure_assessment"):
              css_dict[coll_node_css.name]["Assessment"] = eachv
            elif (eachk=="min_marks"):
              css_dict[coll_node_css.name]["Minimum-marks"] = eachv
            elif (eachk=="max_marks"):
              css_dict[coll_node_css.name]["Maximum-marks"] = eachv
        cs_dict[coll_node_cs.name].append(css_dict)

    if course_collection_list:
      course_collection_dict_exists = True


  context_variables = { 'groupid': group_id, 
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'course_gst_name':course_gst.name,
                        'title':title,
                        'course_collection_dict':json.dumps(course_collection_list),
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


@login_required
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
    app_id = None
    app_set_id = None
    property_order_list_cs = []
    property_order_list_css = []
    course_collection_dict = {}
    course_collection_list = []
    cs_names = []
    css_names = []
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

    at_cs_hours = collection.Node.one({'_type':'AttributeType', 'name':'course_structure_minutes'})
    at_cs_assessment = collection.Node.one({'_type':'AttributeType', 'name':'course_structure_assessment'})
    at_cs_assignment = collection.Node.one({'_type':'AttributeType', 'name':'course_structure_assignment'})
    at_cs_min_marks = collection.Node.one({'_type':'AttributeType', 'name':'min_marks'})
    at_cs_max_marks = collection.Node.one({'_type':'AttributeType', 'name':'max_marks'})


    #Course structure as list of dicts
    for eachcs in course_node.collection_set:
      cs_dict = {}
      coll_node_cs = collection.Node.one({'_id':ObjectId(eachcs),'member_of':cs_gst._id},{'name':1,'collection_set':1})
      cs_names.append(coll_node_cs.name)
      cs_dict[coll_node_cs.name]=[]
      course_collection_list.append(cs_dict)
      for eachcss in coll_node_cs.collection_set:
        css_dict = {}
        coll_node_css = collection.Node.one({'_id':ObjectId(eachcss), 'member_of':css_gst._id},{'name':1,'collection_set':1,'attribute_set':1})
        css_names.append(coll_node_css.name)
        css_dict[coll_node_css.name]={}
        for eachattr in coll_node_css.attribute_set:
          for eachk,eachv in eachattr.items():
            css_dict[coll_node_css.name][eachk] = eachv
        cs_dict[coll_node_cs.name].append(css_dict)
    
    if course_collection_list:
      course_collection_dict_exists = True

    # for attr in course_node.attribute_set:
    #   if attr.has_key("evaluation_type"):
    #     eval_type = attr["evaluation_type"]

    #If evaluation_type flag is True, it is Final. If False, it is Continous
    # if(eval_type==u"Final"):
    #     eval_type_flag = True
    # else:
    #     eval_type_flag = False

    if request.method=="POST":
        listdict = request.POST.get("course_sec_dict_ele","")
        changed_names = request.POST.get("changed_names","")
        listdict = json.loads(listdict)
        changed_names = json.loads(changed_names)
        cs_ids = []
        cs_reorder_ids = []
        # print "\n\n Sent from template\n\n",listdict
        #creating course structure GSystems
        if not course_collection_dict_exists:
          for course_sec_dict in listdict:
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
              cs_reorder_ids.append(cs_new._id)
              css_ids = []
              for index2 in v:
                for css,val in index2.items():
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
                    if(propk=="course_structure_minutes"):
                      create_gattribute(css_new._id,at_cs_hours,int(propv))
                    elif(propk=="course_structure_assessment"):
                      create_gattribute(css_new._id,at_cs_assessment,propv)
                    elif(propk=="course_structure_assignment"):
                      create_gattribute(css_new._id,at_cs_assignment,propv)
                    elif(propk=="min_marks"):
                      create_gattribute(css_new._id,at_cs_min_marks,int(propv))
                    elif(propk=="max_marks"):
                      create_gattribute(css_new._id,at_cs_max_marks,int(propv))
              #append CSS to CS
              collection.update({'_id':cs_new._id},{'$set':{'collection_set':css_ids}},upsert=False,multi=False)
            course_node_coll_set = course_node.collection_set
            collection.update({'_id':course_node._id},{'$set':{'collection_set':cs_reorder_ids}},upsert=False,multi=False)
        else:
          #if there is change in existing and modified course structure
          if not course_collection_list == listdict:
            #for every course section dict
            for course_sec_dict in listdict:
              #k is course section name and v is list of its each course subsection as dict
              for k,v in course_sec_dict.items():#loops over course sections
                var = [k in val_list for val_list in changed_names.values()]

                if k in cs_names  or True in var:
                  for cs_old_name,cs_new_name in changed_names.items():
                    if k is not cs_old_name and k in cs_new_name:
                      name_edited_node = collection.Node.one({'name':cs_old_name,'prior_node':course_node._id,'member_of':cs_gst._id})
                      collection.update({'_id':name_edited_node._id},{'$set':{'name':cs_new_name[0]}})
                      name_edited_node.reload()
                    else:
                      pass

                  #IMP Fetch node with name 'k' as above code, if name changed, changes oldname to k 
                  cs_node = collection.Node.one({'name':k,'member_of':cs_gst._id,'prior_node':course_node._id},{'name':1,'collection_set':1})
                  css_reorder_ids = []
                  var1 = False
                  for cssd in v:
                    for cssname,cssdict in cssd.items():
                      ab = [listings for listings in changed_names.values()]
                      for cs_nodename in ab:
                        if cs_node.name in cs_nodename:
                          if cssname in cs_nodename[1].values():
                            var1 = True
                        else:
                          var1 = False

                      if cssname in css_names or var1 is True: 
                        for cs_old_n,cs_val_list in changed_names.items():
                          if len(cs_val_list)==2:
                            if( cs_val_list[0]==k and type(cs_val_list[1]) is dict):
                              for oldcssname,newcssname in cs_val_list[1].items():
                                if (cssname==newcssname):
                                  css_name_edited_node = collection.Node.one({'name':oldcssname,'prior_node':cs_node._id,'member_of':css_gst._id})
                                  collection.update({'_id':css_name_edited_node._id},{'$set':{'name':newcssname}})
                                  css_name_edited_node.reload()

                        css_node=collection.Node.one({'name':cssname,'member_of':css_gst._id,'prior_node':cs_node._id})
                        for propk,propv in cssdict.items():
                          if(propk==u"course_structure_minutes"):
                            create_gattribute(css_node._id,at_cs_hours,int(propv))
                          elif(propk==u"course_structure_assessment"):
                            create_gattribute(css_node._id,at_cs_assessment,propv)
                          elif(propk==u"course_structure_assignment"):
                            create_gattribute(css_node._id,at_cs_assignment,propv)
                          elif(propk==u"min_marks"):
                            create_gattribute(css_node._id,at_cs_min_marks,int(propv))
                          elif(propk==u"max_marks"):
                            create_gattribute(css_node._id,at_cs_max_marks,int(propv))


                        css_reorder_ids.append(css_node._id)
                      else:
                        #create new css in existing cs
                        css_new = collection.GSystem()
                        css_new.member_of.append(css_gst._id)
                        #set name
                        css_new.name = cssname
                        css_new.modified_by=int(request.user.id)
                        css_new.created_by=int(request.user.id)
                        css_new.contributors.append(int(request.user.id))
                        #save the css gs
                        css_new.prior_node.append(cs_node._id)
                        css_new.save()
                        for propk,propv in cssdict.items():
                          if(propk==u"course_structure_minutes"):
                            create_gattribute(css_new._id,at_cs_hours,int(propv))
                          elif(propk==u"course_structure_assessment"):
                            create_gattribute(css_new._id,at_cs_assessment,propv)
                          elif(propk==u"course_structure_assignment"):
                            create_gattribute(css_new._id,at_cs_assignment,propv)
                          elif(propk==u"min_marks"):
                            create_gattribute(css_new._id,at_cs_min_marks,int(propv))
                          elif(propk==u"max_marks"):
                            create_gattribute(css_new._id,at_cs_max_marks,int(propv))
                        css_reorder_ids.append(css_new._id)

                        #add to cs collection_set
                    
                  if cs_node.collection_set != css_reorder_ids:
                    collection.update({'_id':cs_node._id},{'$set':{'collection_set':css_reorder_ids}}, upsert=False, multi=False)
                    cs_node.reload()
                  else:
                    pass
                  cs_reorder_ids.append(cs_node._id)
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
                  cs_reorder_ids.append(cs_new._id)
                  for index2 in v:
                    for css,val in index2.items():
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
                      for propk, propv in val.items():
                        # add attributes to css gs
                        if(propk==u"course_structure_minutes"):
                          create_gattribute(css_new._id,at_cs_hours,int(propv))
                        elif(propk==u"course_structure_assessment"):
                          create_gattribute(css_new._id,at_cs_assessment,propv)
                        elif(propk==u"course_structure_assignment"):
                          create_gattribute(css_new._id,at_cs_assignment,propv)
                        elif(propk==u"min_marks"):
                          create_gattribute(css_new._id,at_cs_min_marks,int(propv))
                        elif(propk==u"max_marks"):
                          create_gattribute(css_new._id,at_cs_max_marks,int(propv))

                    #add to cs collection_set
                    collection.update({'_id':cs_new._id},{'$push':{'collection_set':css_new._id}},upsert=False,multi=False)
            course_node_coll_set = course_node.collection_set
            # for each in cs_ids:
            #   if each not in course_node_coll_set:
            #     course_node_coll_set.append(each)
            collection.update({'_id':course_node._id},{'$set':{'collection_set':cs_reorder_ids}},upsert=False,multi=False)
          else:
            print "No change"
        app_id = request.POST.get("app_id","")
        app_set_id = request.POST.get("app_set_id","")

        return HttpResponseRedirect(reverse('mis:mis_app_instance_detail',kwargs={'group_id':group_id,'app_id':app_id,'app_set_id':app_set_id,'app_set_instance_id':course_node._id}))
    elif request.method=="GET":
      app_id = request.GET.get("app_id","")
      app_set_id = request.GET.get("app_set_id","")

    return render_to_response("ndf/create_course_structure.html",
                                  { 'cnode': course_node,
                                    'groupid': group_id,
                                    'group_id':group_id,
                                    'title':title,
                                    'node':None,
                                    'app_id':app_id, 'app_set_id':app_set_id,
                                    'coll_node_cs':coll_node_cs,
                                    'coll_node_css':coll_node_css,
                                    'course_collection_list':json.dumps(course_collection_list),
                                    'property_order_list':property_order_list_cs,
                                    'property_order_list_css':property_order_list_css
                                    #'eval_type_flag': eval_type_flag
                                  },
                                  context_instance = RequestContext(request)
        )

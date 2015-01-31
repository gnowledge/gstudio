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

from mongokit import IS

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
app = collection.Node.one({'_type': "GSystemType", 'name': GAPPS[7]})


@login_required
def enrollment_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    Creates/Modifies document of given sub-types of Course(s).
    """

    auth = None
    if ObjectId.is_valid(group_id) is False:
        group_ins = collection.Node.one({'_type': "Group", "name": group_id})
        auth = collection.Node.one(
            {'_type': 'Author', 'name': unicode(request.user.username)}
        )
        if group_ins:
            group_id = str(group_ins._id)
        else:
            auth = collection.Node.one(
                {'_type': 'Author', 'name': unicode(request.user.username)}
            )
            if auth:
                group_id = str(auth._id)

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

    enrollment_gst = None
    enrollment_gs = None
    mis_admin = None

    property_order_list = []

    template = ""
    template_prefix = "mis"

    if request.user:
        if auth is None:
            auth = collection.Node.one(
                {'_type': 'Author', 'name': unicode(request.user.username)}
            )
        agency_type = auth.agency_type
        agency_type_node = collection.Node.one(
            {'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1}
        )
        if agency_type_node:
            for eachset in agency_type_node.collection_set:
                app_collection_set.append(
                    collection.Node.one(
                        {"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}
                    )
                )

    if app_set_id:
        enrollment_gst = collection.Node.one(
            {'_type': "GSystemType", '_id': ObjectId(app_set_id)},
            {'name': 1, 'type_of': 1}
        )
        template = "ndf/" \
            + enrollment_gst.name.strip().lower().replace(' ', '_') \
            + "_create_edit.html"

        title = enrollment_gst.name
        enrollment_gs = collection.GSystem()
        enrollment_gs.member_of.append(enrollment_gst._id)

    if app_set_instance_id:
        enrollment_gs = collection.Node.one(
            {'_type': "GSystem", '_id': ObjectId(app_set_instance_id)}
        )

    property_order_list = get_property_order_with_value(enrollment_gs)

    if request.method == "POST":
        start_enroll = ""
        if "start_enroll" in request.POST:
            start_enroll = request.POST.get("start_enroll", "")
            start_enroll = datetime.datetime.strptime(start_enroll, "%d/%m/%Y")

        end_enroll = ""
        if "end_enroll" in request.POST:
            end_enroll = request.POST.get("end_enroll", "")
            end_enroll = datetime.datetime.strptime(end_enroll, "%d/%m/%Y")

        nussd_course_type = ""
        if "nussd_course_type" in request.POST:
            nussd_course_type = request.POST.get("nussd_course_type", "")
            nussd_course_type = unicode(nussd_course_type)

        at_rt_list = ["start_enroll", "end_enroll", "for_acourse", "for_college", "for_university", "enrollment_status", "has_enrolled", "has_enrollment_task", "has_approval_task"]
        at_rt_dict = {}

        ac_cname_cl_uv_ids = ""
        ann_course_ids = None
        course_name = None
        college_id = None
        university_id = None

        college_po = {}
        mis_admin = collection.Node.one(
            {'_type': "Group", 'name': "MIS_admin"}, {'name': 1}
        )

        if "ac_cname_cl_uv_ids" in request.POST:
            ac_cname_cl_uv_ids = request.POST.get("ac_cname_cl_uv_ids", "")
            ac_cname_cl_uv_ids = json.loads(ac_cname_cl_uv_ids)

            for each_set in ac_cname_cl_uv_ids:
                if each_set:
                    ann_course_ids = each_set[0]
                    ann_course_name = each_set[1]
                    course_name = each_set[2]
                    college_id = each_set[3]
                    university_id = each_set[4]

        if nussd_course_type == "Foundation Course":
            print "\n needs to be done"
        else:
            for each_set in ac_cname_cl_uv_ids:
                acourse_id = ObjectId(each_set[0][0])
                at_rt_dict["for_acourse"] = acourse_id
                at_rt_dict["enrollment_status"] = u"OPEN"
                at_rt_dict["start_enroll"] = start_enroll
                at_rt_dict["end_enroll"] = end_enroll
                ann_course_name = each_set[1]
                course_name = each_set[2]

                college_id = ObjectId(each_set[3])
                at_rt_dict["for_college"] = college_id

                task_group_set = []
                if college_id not in college_po:
                    college_node = collection.Node.one({
                        "_id": college_id
                    }, {
                        "name": 1,
                        "relation_set.has_group": 1,
                        "relation_set.has_officer_incharge": 1
                    })

                    for rel in college_node.relation_set:
                        if rel and "has_officer_incharge" in rel:
                            college_po[college_id] = rel["has_officer_incharge"]
                        if rel and "has_group" in rel:
                            task_group_set.append(rel["has_group"][0])

                at_rt_dict["for_university"] = ObjectId(each_set[4])
                enrollment_gst = collection.Node.one({
                    '_type': "GSystemType", 'name': "StudentCourseEnrollment"
                })

                enrollment_gs_name = "StudentCourseEnrollment" + "_" \
                    + start_enroll.strftime("%d-%b-%Y") + "_" + end_enroll.strftime("%d-%b-%Y") \
                    + "_" + ann_course_name
                enrollment_gs = collection.Node.one({
                    'member_of': enrollment_gst._id, 'name': enrollment_gs_name,
                    'status': u"PUBLISHED"
                })

                # If not found, create it
                if not enrollment_gs:
                    enrollment_gs = collection.GSystem()
                    enrollment_gs.name = enrollment_gs_name
                    if enrollment_gst._id not in enrollment_gs.member_of:
                        enrollment_gs.member_of.append(enrollment_gst._id)

                    if mis_admin._id not in enrollment_gs.group_set:
                        enrollment_gs.group_set.append(mis_admin._id)

                    user_id = request.user.id
                    enrollment_gs.created_by = user_id
                    enrollment_gs.modified_by = user_id
                    if user_id not in enrollment_gs.contributors:
                        enrollment_gs.contributors.append(user_id)

                    enrollment_gs.status = u"PUBLISHED"
                    enrollment_gs.save()

                if "_id" in enrollment_gs:
                    # [2] Create task for PO of respective college
                    # for Student-Course Enrollment
                    task_dict = {}
                    task_name = "StudentCourseEnrollment_Task" + "_" + \
                        start_enroll.strftime("%d-%b-%Y") + "_" + end_enroll.strftime("%d-%b-%Y") + \
                        "_" + ann_course_name
                    task_name = unicode(task_name)
                    task_dict["name"] = task_name
                    task_dict["created_by"] = request.user.id
                    task_dict["created_by_name"] = request.user.username
                    task_dict["modified_by"] = request.user.id
                    task_dict["contributors"] = [request.user.id]

                    task_node = None

                    task_dict["start_time"] = start_enroll
                    task_dict["end_time"] = end_enroll

                    glist_gst = collection.Node.one({'_type': "GSystemType", 'name': "GList"})
                    task_type_node = None
                    # Here, GSTUDIO_TASK_TYPES[3] := 'Student-Course Enrollment'
                    task_dict["has_type"] = []
                    if glist_gst:
                        task_type_node = collection.Node.one(
                            {'member_of': glist_gst._id, 'name': GSTUDIO_TASK_TYPES[3]},
                            {'_id': 1}
                        )

                        if task_type_node:
                            task_dict["has_type"].append(task_type_node._id)

                    task_dict["Status"] = u"New"
                    task_dict["Priority"] = u"High"

                    task_dict["content_org"] = u""

                    task_dict["Assignee"] = []
                    task_dict["group_set"] = []

                    # From Program Officer node(s) assigned to college using college_po[college_id]
                    # From each node's 'has_login' relation fetch corresponding Author node
                    po_cur = collection.Node.find({
                        '_id': {'$in': college_po[college_id]},
                        'attribute_set.email_id': {'$exists': True},
                        'relation_set.has_login': {'$exists': True}
                    }, {
                        'name': 1, 'attribute_set.email_id': 1,
                        'relation_set.has_login': 1
                    })
                    for PO in po_cur:
                        po_auth = None
                        for rel in PO.relation_set:
                            if rel and "has_login" in rel:
                                po_auth = collection.Node.one({'_type': "Author", '_id': ObjectId(rel["has_login"][0])})
                                if po_auth:
                                    if po_auth.created_by not in task_dict["Assignee"]:
                                        task_dict["Assignee"].append(po_auth.created_by)
                                    if po_auth._id not in task_dict["group_set"]:
                                        task_dict["group_set"].append(po_auth._id)

                    # Appending college group's ObjectId to group_set
                    task_dict["group_set"].extend(task_group_set)

                    task_node = create_task(task_dict)

                    MIS_GAPP = collection.Node.one({
                        "_type": "GSystemType", "name": "MIS"
                    })

                    Student = collection.Node.one({
                        "_type": "GSystemType", "name": "Student"
                    })

                    # Set content_org for the task with link having ObjectId of it's own
                    if MIS_GAPP and Student:
                        site = Site.objects.get(pk=1)
                        site = site.name.__str__()
                        college_enrollment_url_link = "http://" + site + "/" + \
                            college_node.name.replace(" ", "%20").encode('utf8') + \
                            "/mis/" + str(MIS_GAPP._id) + "/" + str(Student._id) + "/enroll" + \
                            "/" + str(enrollment_gs._id) + \
                            "?task_id=" + str(task_node._id) + "&nussd_course_type=" + \
                            nussd_course_type + "&ann_course_id=" + str(acourse_id)

                        task_dict = {}
                        task_dict["_id"] = task_node._id
                        task_dict["name"] = task_name
                        task_dict["created_by_name"] = request.user.username
                        task_dict["content_org"] = "\n- Please click [[" + college_enrollment_url_link + "][here]] to enroll students in " + \
                            ann_course_name + " course." + "\n\n- This enrollment procedure is open for duration between " + \
                            start_enroll.strftime("%d-%b-%Y") + " and " + end_enroll.strftime("%d-%b-%Y") + "."

                        task_node = create_task(task_dict)

                    enrollment_task_dict = {}
                    for each_enrollment in enrollment_gs.attribute_set:
                        if "has_enrollment_task" in each_enrollment:
                            if each_enrollment["has_enrollment_task"]:
                                enrollment_task_dict = each_enrollment["has_enrollment_task"]
                                break

                    if str(task_node._id) not in enrollment_task_dict:
                        enrollment_task_dict[str(task_node._id)] = {}

                    at_rt_dict["has_enrollment_task"] = enrollment_task_dict
                    # Save/Update GAttribute(s) and/or GRelation(s)
                    for at_rt_name in at_rt_list:
                        if at_rt_name in at_rt_dict:
                            at_rt_type_node = collection.Node.one({
                                '_type': {'$in': ["AttributeType", "RelationType"]},
                                'name': at_rt_name
                            })

                            if at_rt_type_node:
                                at_rt_node = None

                                if at_rt_type_node._type == "AttributeType" and at_rt_dict[at_rt_name]:
                                    at_rt_node = create_gattribute(enrollment_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])

                                elif at_rt_type_node._type == "RelationType" and at_rt_dict[at_rt_name]:
                                    at_rt_node = create_grelation(enrollment_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])

    default_template = "ndf/enrollment_create_edit.html"
    context_variables = {
        'groupid': group_id, 'group_id': group_id,
        'app_id': app_id, 'app_name': app_name,
        'app_collection_set': app_collection_set,
        'app_set_id': app_set_id,
        'title': title,
        'property_order_list': property_order_list
    }

    if app_set_instance_id:
        enrollment_gs.get_neighbourhood(enrollment_gs.member_of)
        context_variables['node'] = enrollment_gs
        for each_in in enrollment_gs.attribute_set:
            for eachk, eachv in each_in.items():
                context_variables[eachk] = eachv

        for each_in in enrollment_gs.relation_set:
            for eachk, eachv in each_in.items():
                get_node_name = collection.Node.one({'_id': eachv[0]})
                context_variables[eachk] = get_node_name.name

    try:
        return render_to_response(
            [template, default_template],
            context_variables,
            context_instance=RequestContext(request)
        )

    except TemplateDoesNotExist as tde:
        error_message = "\n EnrollmentCreateEditViewError: This html template (" \
            + str(tde) + ") does not exists !!!\n"
        raise Http404(error_message)

    except Exception as e:
        error_message = "\n EnrollmentCreateEditViewError: " + str(e) + " !!!\n"
        raise Exception(error_message)

''' -- imports from python libraries -- '''
# from datetime import datetime
import datetime
# import time
import json
import math
import multiprocessing

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
# from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response  # , render  uncomment when to use
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site

from mongokit import IS  # Don't delete used indirectly inside eval()

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, GSTUDIO_TASK_TYPES  # , MEDIA_ROOT
# from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.models import NodeJSONEncoder
# from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.views.methods import get_execution_time  # , parse_template_data, get_node_common_fields
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation
from gnowsys_ndf.ndf.views.methods import create_task

app = node_collection.one({'_type': "GSystemType", 'name': GAPPS[7]})


@login_required
@get_execution_time
def enrollment_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    Creates/Modifies document of given sub-types of Course(s).
    """
    user_id = request.user.id
    user_name = request.user.username

    auth = None
    if ObjectId.is_valid(group_id) is False:
        group_ins = node_collection.one({'_type': "Group", "name": group_id})
        auth = node_collection.one(
            {'_type': 'Author', 'name': unicode(user_name)}
        )
        if group_ins:
            group_id = str(group_ins._id)
        else:
            auth = node_collection.one(
                {'_type': 'Author', 'name': unicode(user_name)}
            )
            if auth:
                group_id = str(auth._id)

    app = None
    if app_id is None:
        app = node_collection.one({'_type': "GSystemType", 'name': app_name})
        if app:
            app_id = str(app._id)
    else:
        app = node_collection.one({'_id': ObjectId(app_id)})

    app_name = app.name

    app_collection_set = []
    title = ""

    enrollment_gst = None
    enrollment_gs = None
    # sce_gs = None
    mis_admin = None
    college_group_id = None
    latest_completed_on = None
    # unlock_enroll = False # Will only be True while editing (i.e. Re-opening Enrollment)
    old_current_approval_task = None
    approval_task_dict = {}
    reopen_task_id = None
    enrollment_id = None
    enrollment_last_date = None
    property_order_list = []

    template = ""
    template_prefix = "mis"

    if request.user:
        if auth is None:
            auth = node_collection.one(
                {'_type': 'Author', 'name': unicode(user_name)}
            )
        agency_type = auth.agency_type
        agency_type_node = node_collection.one(
            {'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1}
        )
        if agency_type_node:
            for eachset in agency_type_node.collection_set:
                app_collection_set.append(
                    node_collection.one(
                        {"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}
                    )
                )

    if app_set_id:
        enrollment_gst = node_collection.one(
            {'_type': "GSystemType", '_id': ObjectId(app_set_id)},
            {'name': 1, 'type_of': 1}
        )
        template = "ndf/" \
            + enrollment_gst.name.strip().lower().replace(' ', '_') \
            + "_create_edit.html"

        title = enrollment_gst.name
        enrollment_gs = node_collection.collection.GSystem()
        enrollment_gs.member_of.append(enrollment_gst._id)

    if app_set_instance_id:
        enrollment_gs = node_collection.one({
            '_type': "GSystem", '_id': ObjectId(app_set_instance_id)
        })

        enrollment_id = enrollment_gs._id

        for rel in enrollment_gs.relation_set:
            if rel and "has_current_approval_task" in rel:
                old_current_approval_task = rel["has_current_approval_task"][0]

        for attr in enrollment_gs.attribute_set:
            if attr and "has_enrollment_task" in attr:
                td = attr["has_enrollment_task"]
                latest_completed_on = None  # Must hold latest completed_on
                for k, completed_by_on in td.items():
                    if latest_completed_on:
                        if "completed_on" in completed_by_on and latest_completed_on < completed_by_on["completed_on"]:
                            # Put latest changed date
                            latest_completed_on = completed_by_on["completed_on"]
                    else:
                        if "completed_on" in completed_by_on and completed_by_on["completed_on"]:
                            latest_completed_on = completed_by_on["completed_on"]
            elif attr and "end_enroll" in attr:
                enrollment_last_date = attr["end_enroll"]
            elif attr and "has_approval_task" in attr:
                approval_task_dict = attr["has_approval_task"]

    property_order_list = get_property_order_with_value(enrollment_gs)

    # if enrollment_last_date:
    #     enrollment_last_date = enrollment_last_date.date()
    #     current_date = datetime.datetime.now().date()
    #     if enrollment_last_date <= current_date:
    #         unlock_enroll = True

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

        # Only exists while updating StudentCourseEnrollment node's duration
        if "reopen_task_id" in request.POST:
            reopen_task_id = request.POST.get("reopen_task_id", "")
            reopen_task_id = ObjectId(reopen_task_id)

        admin_update = None
        if "admin_update" in request.POST:
            admin_update = request.POST.get("admin_update", "")

        at_rt_list = ["start_enroll", "end_enroll", "for_acourse", "for_college", "for_university", "enrollment_status", "has_enrolled", "has_enrollment_task", "has_approval_task"]
        at_rt_dict = {}

        ac_cname_cl_uv_ids = []
        ann_course_ids = None
        course_name = None
        college_id = None
        university_id = None

        college_po = {}
        mis_admin = node_collection.one(
            {'_type': "Group", 'name': "MIS_admin"}, {'name': 1}
        )

        if "ac_cname_cl_uv_ids" in request.POST:
            ac_cname_cl_uv_ids = request.POST.get("ac_cname_cl_uv_ids", "")
            ac_cname_cl_uv_ids = json.loads(ac_cname_cl_uv_ids)

        else:
            if enrollment_gs:
                ac_cname_cl_uv_ids = []

                for rel in enrollment_gs.relation_set:
                    if rel and "for_acourse" in rel:
                        ann_course_ids_set = rel["for_acourse"]

                if len(ann_course_ids_set) > 1 or "Foundation_Course" in enrollment_gs.name:
                    # Foundation
                    ann_course_ids = ann_course_ids_set

                    ann_course_node = node_collection.one({
                        "_id": ObjectId(ann_course_ids[0])
                    })

                    ann_course_node.get_neighbourhood(ann_course_node.member_of)

                    start_time_ac = ann_course_node.start_time.strftime("%Y")
                    end_time_ac = ann_course_node.end_time.strftime("%Y")

                    for each_attr in ann_course_node.announced_for[0].attribute_set:
                        if each_attr and "nussd_course_type" in each_attr:
                            nussd_course_type = each_attr["nussd_course_type"]
                            break

                    # College
                    college_id = ann_course_node.acourse_for_college[0]["_id"]

                    # University
                    for colg_rel in ann_course_node.acourse_for_college[0].relation_set:
                        if colg_rel and "college_affiliated_to" in colg_rel:
                            university_id = colg_rel["college_affiliated_to"][0]
                            break

                    colg_code = ""
                    for colg_attr in ann_course_node.acourse_for_college[0].attribute_set:
                        if colg_attr and "enrollment_code" in colg_attr:
                            colg_code = colg_attr["enrollment_code"]
                            break

                    # Ann course name
                    ann_course_name = "Foundation Course - " + str(colg_code) + " - " + str(start_time_ac) + " - " + str(end_time_ac)

                    # course name
                    course_name = nussd_course_type

                    ac_cname_cl_uv_ids.append([ann_course_ids, ann_course_name, course_name, college_id, university_id])

                else:
                    # Domain
                    for each_ac in ann_course_ids_set:
                        ann_course_ids = [each_ac]

                        ann_course_node = node_collection.one({
                            "_id": ObjectId(each_ac)
                        })

                        ann_course_node.get_neighbourhood(ann_course_node.member_of)

                        # Ann course name
                        ann_course_name = ann_course_node.name

                        # course name
                        course_name = ann_course_node.announced_for[0].name

                        for each_attr in ann_course_node.announced_for[0].attribute_set:
                            if each_attr and "nussd_course_type" in each_attr:
                                nussd_course_type = each_attr["nussd_course_type"]
                                break

                        # College
                        college_id = ann_course_node.acourse_for_college[0]["_id"]

                        # University
                        for colg_rel in ann_course_node.acourse_for_college[0].relation_set:
                            if colg_rel and "college_affiliated_to" in colg_rel:
                                university_id = colg_rel["college_affiliated_to"][0]
                                break

                        ac_cname_cl_uv_ids.append([ann_course_ids, ann_course_name, course_name, college_id, university_id])

        enrollment_gst = node_collection.one({
            '_type': "GSystemType", 'name': "StudentCourseEnrollment"
        })
        if nussd_course_type == "Foundation Course":
            # FC
            for each_fc_set in ac_cname_cl_uv_ids:
                fc_set = each_fc_set[0]
                ann_course_name = each_fc_set[1]
                course_name = each_fc_set[2]
                college_id = each_fc_set[3]
                university_id = each_fc_set[4]
                fc_set = [ObjectId(each_fc) for each_fc in each_fc_set[0]]
                at_rt_dict["for_acourse"] = fc_set
                acourse_id = fc_set
                at_rt_dict["for_acourse"] = acourse_id
                at_rt_dict["enrollment_status"] = u"OPEN"
                at_rt_dict["start_enroll"] = start_enroll
                at_rt_dict["end_enroll"] = end_enroll
                at_rt_dict["for_college"] = college_id
                # announced_course_list = [u"Announced Course"]

                task_group_set = []
                if college_id not in college_po:
                    college_node = node_collection.one({
                        "_id": ObjectId(college_id)
                    }, {
                        "name": 1,
                        "relation_set.has_group": 1,
                        "relation_set.has_officer_incharge": 1
                    })

                    for rel in college_node.relation_set:
                        if rel and "has_officer_incharge" in rel:
                            college_po[college_id] = rel["has_officer_incharge"]
                        elif rel and "has_group" in rel:
                            college_group_id = rel["has_group"][0]
                            task_group_set.append(college_group_id)

                at_rt_dict["for_university"] = ObjectId(university_id)

                if enrollment_gs and "_id" in enrollment_gs:
                    enrollment_gs_name = enrollment_gs.name
                else:
                    enrollment_gs_name = "Student Course Enrollment" \
                        + " - " + ann_course_name

                    enrollment_gs = node_collection.one({
                        'member_of': enrollment_gst._id, 'name': enrollment_gs_name,
                        "group_set": [mis_admin._id, college_group_id],
                        'status': u"PUBLISHED"
                    })

                # If not found, create it
                if not enrollment_gs:
                    enrollment_gs = node_collection.collection.GSystem()
                    enrollment_gs.name = enrollment_gs_name
                    if enrollment_gst._id not in enrollment_gs.member_of:
                        enrollment_gs.member_of.append(enrollment_gst._id)

                    if mis_admin._id not in enrollment_gs.group_set:
                        enrollment_gs.group_set.append(mis_admin._id)
                    if college_group_id not in enrollment_gs.group_set:
                        enrollment_gs.group_set.append(college_group_id)

                    enrollment_gs.created_by = user_id
                    enrollment_gs.modified_by = user_id
                    if user_id not in enrollment_gs.contributors:
                        enrollment_gs.contributors.append(user_id)

                    enrollment_gs.last_update = datetime.datetime.today()
                    enrollment_gs.status = u"PUBLISHED"
                    enrollment_gs.save(groupid=group_id)

                enrollment_task_ids = None
                each_enrollment_task_node = None
                list_of_task_status = [u'New', u'In Progress']
                task_status = None
                updated_one_task = False
                if "_id" in enrollment_gs and admin_update is not None:
                    for each_enrollment in enrollment_gs.attribute_set:
                        if "has_enrollment_task" in each_enrollment:
                            if each_enrollment["has_enrollment_task"]:
                                enrollment_task_dict = each_enrollment["has_enrollment_task"]
                                break
                    enrollment_task_ids = enrollment_task_dict.keys()
                    for each_enrollment_task in enrollment_task_ids:
                        if not updated_one_task:
                            each_enrollment_task_node = node_collection.one({'_id': ObjectId(each_enrollment_task)})
                            if each_enrollment_task_node.attribute_set:
                                for each_attr_task in each_enrollment_task_node.attribute_set:
                                    if each_attr_task and 'Status' in each_attr_task:
                                        task_status = each_attr_task['Status']
                            # task_status = each_enrollment_task_node.attribute_set[0]['Status']

                            if task_status in list_of_task_status:
                                task_dict = {}
                                task_dict["_id"] = each_enrollment_task_node._id
                                task_dict["modified_by"] = user_id
                                task_dict["created_by_name"] = user_name
                                content_text = each_enrollment_task_node['content_org']
                                content_text += "\n\n- New enrollment dates are from : "+start_enroll.strftime("%d-%b-%Y")+" to " +end_enroll.strftime("%d-%b-%Y")
                                task_dict["content_org"] = unicode(content_text)
                                task_dict["start_time"] = start_enroll
                                task_dict["end_time"] = end_enroll
                                task_node = create_task(task_dict)

                                enrollment_status_at = node_collection.one({
                                    '_type': "AttributeType",
                                    'name': u"enrollment_status"
                                })
                                end_enroll_at = node_collection.one({
                                    '_type': "AttributeType",
                                    'name': u"end_enroll"
                                })
                                at_status_node = create_gattribute(enrollment_gs._id, enrollment_status_at, u"OPEN")
                                at_enroll_node = create_gattribute(enrollment_gs._id, end_enroll_at, end_enroll)
                                updated_one_task = True

                if not updated_one_task:
                    admin_update = None
                if "_id" in enrollment_gs and admin_update is None:
                    # [2] Create task for PO of respective college
                    # for Student-Course Enrollment
                    task_dict = {}
                    task_name = "Student Course Enrollment Task " + \
                        start_enroll.strftime("%d/%b/%Y") + " - " + \
                        end_enroll.strftime("%d/%b/%Y") + " - " + \
                        ann_course_name
                    task_name = unicode(task_name)
                    task_dict["name"] = task_name
                    task_dict["created_by"] = user_id
                    task_dict["created_by_name"] = user_name
                    task_dict["modified_by"] = user_id
                    task_dict["contributors"] = [user_id]

                    task_node = None

                    task_dict["start_time"] = start_enroll
                    task_dict["end_time"] = end_enroll

                    glist_gst = node_collection.one({'_type': "GSystemType", 'name': "GList"})
                    task_type_node = None
                    # Here, GSTUDIO_TASK_TYPES[3] := 'Student-Course Enrollment'
                    task_dict["has_type"] = []
                    if glist_gst:
                        task_type_node = node_collection.one(
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
                    po_cur = node_collection.find({
                        '_id': {'$in': college_po[college_id]},
                        # 'attribute_set.email_id': {'$exists': True},
                        'relation_set.has_login': {'$exists': True}
                    }, {
                        'name': 1, 'relation_set.$.has_login': 1
                        # 'attribute_set.email_id': 1
                    })
                    for PO in po_cur:
                        po_auth = None
                        for rel in PO.relation_set:
                            if rel and "has_login" in rel:
                                po_auth = node_collection.one({'_type': "Author", '_id': ObjectId(rel["has_login"][0])})
                                if po_auth:
                                    if po_auth.created_by not in task_dict["Assignee"]:
                                        task_dict["Assignee"].append(po_auth.created_by)
                                    if po_auth._id not in task_dict["group_set"]:
                                        task_dict["group_set"].append(po_auth._id)

                    # Appending college group's ObjectId to group_set
                    task_dict["group_set"].extend(task_group_set)
                    task_node = create_task(task_dict)

                    MIS_GAPP = node_collection.one({
                        "_type": "GSystemType", "name": "MIS"
                    })

                    Student = node_collection.one({
                        "_type": "GSystemType", "name": "Student"
                    })

                    # Set content_org for the task with link having ObjectId of it's own
                    if MIS_GAPP and Student:
                        site = Site.objects.get(pk=1)
                        site = site.name.__str__()
                        college_enrollment_url_link = "http://" + site + "/" + \
                            college_node.name.replace(" ", "%20").encode('utf8') + \
                            "/mis/" + str(MIS_GAPP._id) + "/" + str(enrollment_gst._id) + "/enroll" + \
                            "/" + str(enrollment_gs._id) + \
                            "?task_id=" + str(task_node._id) + "&nussd_course_type=" + \
                            nussd_course_type

                        task_dict = {}
                        task_dict["_id"] = task_node._id
                        task_dict["name"] = task_name
                        task_dict["created_by_name"] = user_name
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
                            at_rt_type_node = node_collection.one({
                                '_type': {'$in': ["AttributeType", "RelationType"]},
                                'name': at_rt_name
                            })

                            if at_rt_type_node:
                                at_rt_node = None

                                if at_rt_type_node._type == "AttributeType" and at_rt_dict[at_rt_name]:
                                    at_rt_node = create_gattribute(enrollment_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])

                                elif at_rt_type_node._type == "RelationType" and at_rt_dict[at_rt_name]:
                                    at_rt_node = create_grelation(enrollment_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])
                enrollment_gs = None
        else:
            # Domain
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
                    college_node = node_collection.one({
                        "_id": ObjectId(college_id)
                    }, {
                        "name": 1,
                        "relation_set.has_group": 1,
                        "relation_set.has_officer_incharge": 1
                    })

                    for rel in college_node.relation_set:
                        if rel and "has_officer_incharge" in rel:
                            college_po[college_id] = rel["has_officer_incharge"]
                        elif rel and "has_group" in rel:
                            college_group_id = rel["has_group"][0]
                            task_group_set.append(college_group_id)

                at_rt_dict["for_university"] = ObjectId(each_set[4])

                if enrollment_gs and "_id" in enrollment_gs :
                    enrollment_gs_name = enrollment_gs.name
                else:
                    enrollment_gs_name = "Student Course Enrollment" \
                        + " - " + ann_course_name

                    enrollment_gs = node_collection.one({
                        'member_of': enrollment_gst._id, 'name': enrollment_gs_name,
                        "group_set": [mis_admin._id, college_group_id],
                        'status': u"PUBLISHED"
                    })

                # If not found, create it
                if not enrollment_gs:
                    enrollment_gs = node_collection.collection.GSystem()
                    enrollment_gs.name = enrollment_gs_name
                    if enrollment_gst._id not in enrollment_gs.member_of:
                        enrollment_gs.member_of.append(enrollment_gst._id)

                    if mis_admin._id not in enrollment_gs.group_set:
                        enrollment_gs.group_set.append(mis_admin._id)
                    if college_group_id not in enrollment_gs.group_set:
                        enrollment_gs.group_set.append(college_group_id)

                    enrollment_gs.created_by = user_id
                    enrollment_gs.modified_by = user_id
                    if user_id not in enrollment_gs.contributors:
                        enrollment_gs.contributors.append(user_id)

                    enrollment_gs.last_update = datetime.datetime.today()
                    enrollment_gs.status = u"PUBLISHED"
                    enrollment_gs.save(groupid=group_id)

                enrollment_task_ids = None
                each_enrollment_task_node = None
                list_of_task_status = [u'New', u'In Progress']
                task_status = None
                updated_one_task = False
                if "_id" in enrollment_gs and admin_update is not None:
                    for each_enrollment in enrollment_gs.attribute_set:
                        if "has_enrollment_task" in each_enrollment:
                            if each_enrollment["has_enrollment_task"]:
                                enrollment_task_dict = each_enrollment["has_enrollment_task"]
                                break
                    enrollment_task_ids = enrollment_task_dict.keys()
                    for each_enrollment_task in enrollment_task_ids:
                        if not updated_one_task:
                            each_enrollment_task_node = node_collection.one({'_id': ObjectId(each_enrollment_task)})
                            task_status = each_enrollment_task_node.attribute_set[0]['Status']

                            if task_status in list_of_task_status:
                                task_dict = {}
                                task_dict["_id"] = each_enrollment_task_node._id
                                task_dict["modified_by"] = user_id
                                task_dict["created_by_name"] = user_name
                                content_text = each_enrollment_task_node['content_org']
                                content_text += "\n- The duration for this enrollment task has been extended to "+end_enroll.strftime("%d-%b-%Y")+"."
                                task_dict["content_org"] = unicode(content_text)
                                task_dict["start_time"] = start_enroll
                                task_dict["end_time"] = end_enroll
                                task_node = create_task(task_dict)

                                enrollment_status_at = node_collection.one({
                                    '_type': "AttributeType",
                                    'name': u"enrollment_status"
                                })
                                end_enroll_at = node_collection.one({
                                    '_type': "AttributeType",
                                    'name': u"end_enroll"
                                })
                                at_status_node = create_gattribute(enrollment_gs._id, enrollment_status_at, u"OPEN")
                                at_enroll_node = create_gattribute(enrollment_gs._id, end_enroll_at, end_enroll)
                                updated_one_task = True

                if not updated_one_task:
                    admin_update = None
                if "_id" in enrollment_gs and admin_update is None:
                    # [2] Create task for PO of respective college
                    # for Student-Course Enrollment
                    task_dict = {}
                    task_name = "Student Course Enrollment Task " + \
                        start_enroll.strftime("%d/%b/%Y") + " - " + \
                        end_enroll.strftime("%d/%b/%Y") + " - " + \
                        ann_course_name
                    task_name = unicode(task_name)
                    task_dict["name"] = task_name
                    task_dict["created_by"] = user_id
                    task_dict["created_by_name"] = user_name
                    task_dict["modified_by"] = user_id
                    task_dict["contributors"] = [user_id]

                    task_node = None

                    task_dict["start_time"] = start_enroll
                    task_dict["end_time"] = end_enroll

                    glist_gst = node_collection.one({'_type': "GSystemType", 'name': "GList"})
                    task_type_node = None
                    # Here, GSTUDIO_TASK_TYPES[3] := 'Student-Course Enrollment'
                    task_dict["has_type"] = []
                    if glist_gst:
                        task_type_node = node_collection.one(
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
                    po_cur = node_collection.find({
                        '_id': {'$in': college_po[college_id]},
                        # 'attribute_set.email_id': {'$exists': True},
                        'relation_set.has_login': {'$exists': True}
                    }, {
                        'name': 1, 'relation_set.$.has_login': 1
                        # 'attribute_set.email_id': 1
                    })
                    for PO in po_cur:
                        po_auth = None
                        for rel in PO.relation_set:
                            if rel and "has_login" in rel:
                                po_auth = node_collection.one({'_type': "Author", '_id': ObjectId(rel["has_login"][0])})
                                if po_auth:
                                    if po_auth.created_by not in task_dict["Assignee"]:
                                        task_dict["Assignee"].append(po_auth.created_by)
                                    if po_auth._id not in task_dict["group_set"]:
                                        task_dict["group_set"].append(po_auth._id)

                    # Appending college group's ObjectId to group_set
                    task_dict["group_set"].extend(task_group_set)

                    task_node = create_task(task_dict)

                    MIS_GAPP = node_collection.one({
                        "_type": "GSystemType", "name": "MIS"
                    })

                    Student = node_collection.one({
                        "_type": "GSystemType", "name": "Student"
                    })

                    # Set content_org for the task with link having ObjectId of it's own
                    if MIS_GAPP and Student:
                        site = Site.objects.get(pk=1)
                        site = site.name.__str__()
                        college_enrollment_url_link = "http://" + site + "/" + \
                            college_node.name.replace(" ", "%20").encode('utf8') + \
                            "/mis/" + str(MIS_GAPP._id) + "/" + str(enrollment_gst._id) + "/enroll" + \
                            "/" + str(enrollment_gs._id) + \
                            "?task_id=" + str(task_node._id) + "&nussd_course_type=" + \
                            nussd_course_type + "&ann_course_id=" + str(acourse_id)

                        task_dict = {}
                        task_dict["_id"] = task_node._id
                        task_dict["name"] = task_name
                        task_dict["created_by_name"] = user_name
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
                            at_rt_type_node = node_collection.one({
                                '_type': {'$in': ["AttributeType", "RelationType"]},
                                'name': at_rt_name
                            })

                            if at_rt_type_node:
                                at_rt_node = None

                                if at_rt_type_node._type == "AttributeType" and at_rt_dict[at_rt_name]:
                                    at_rt_node = create_gattribute(enrollment_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])

                                elif at_rt_type_node._type == "RelationType" and at_rt_dict[at_rt_name]:
                                    at_rt_node = create_grelation(enrollment_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])



                enrollment_gs = None

        if reopen_task_id:
            # Update the Re-open enrollment task as "Closed"
            task_dict = {}
            task_dict["_id"] = reopen_task_id
            task_dict["Status"] = u"Closed"
            task_dict["modified_by"] = user_id
            task_dict["created_by_name"] = user_name
            task_dict["content_org"] = "\n This Student-Course Re-Open Enrollment Task is no longer valid!!!"
            task_dict["content_org"] = unicode(task_dict["content_org"])
            task_node = create_task(task_dict)

        if reopen_task_id or admin_update is None:
            # Update the current approval task as "Closed"
            if old_current_approval_task and not approval_task_dict[str(old_current_approval_task)]:
                old_app_task_dict = {}
                old_app_task_dict["_id"] = old_current_approval_task
                old_app_task_dict["Status"] = u"Closed"
                old_app_task_dict["modified_by"] = user_id
                old_app_task_dict["created_by_name"] = user_name
                old_app_task_dict["content_org"] = "\n This Student-Course Approval Task is no longer valid!!!"
                old_app_task_dict["content_org"] = unicode(old_app_task_dict["content_org"])
                old_task_node_updated = create_task(old_app_task_dict)

                # Set interuppted status for closed approval task in StudentCourseEnrollment node's has_enrollment_task
                completed_on = datetime.datetime.now()

                approval_task_dict[str(old_current_approval_task)] = {
                    "interuppted_on": completed_on, "interuppted_by": user_id
                }
                at_type_node = None
                at_type_node = node_collection.one({
                    '_type': "AttributeType",
                    'name': u"has_approval_task"
                })

                if at_type_node:
                    attr_node = create_gattribute(enrollment_id, at_type_node, approval_task_dict)

        return HttpResponseRedirect(reverse(
            app_name.lower() + ":" + template_prefix + '_app_detail',
            kwargs={'group_id': group_id, "app_id": app_id, "app_set_id": app_set_id}
        ))

    else:
        # GET request
        if "reopen_task_id" in request.GET:
            reopen_task_id = request.GET.get("reopen_task_id", "")
            reopen_task_id = ObjectId(reopen_task_id)

    default_template = "ndf/enrollment_create_edit.html"
    context_variables = {
        'groupid': group_id, 'group_id': group_id,
        'app_id': app_id, 'app_name': app_name,
        'app_collection_set': app_collection_set,
        'app_set_id': app_set_id,
        'title': title,
        'property_order_list': property_order_list
        # 'unlock_enroll':unlock_enroll
    }

    if app_set_instance_id:
        enrollment_gs.get_neighbourhood(enrollment_gs.member_of)
        context_variables['node'] = enrollment_gs
        context_variables['reopen_task_id'] = reopen_task_id
        for each_in in enrollment_gs.attribute_set:
            for eachk, eachv in each_in.items():
                context_variables[eachk] = eachv

        for each_in in enrollment_gs.relation_set:
            for eachk, eachv in each_in.items():
                l_labels = []
                if eachk == "for_acourse":
                    for every_ac in eachv:
                        get_node_name = node_collection.one({'_id': every_ac})
                        l_labels.append(get_node_name.name)
                else:
                    get_node_name = node_collection.one({'_id': eachv[0]})
                    l_labels.append(get_node_name.name)
                context_variables[eachk] = l_labels

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


@login_required
@get_execution_time
def enrollment_detail(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
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

  sce_gst = None
  sce_gs = None
  response_dict = {'success': False}
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
      auth = node_collection.one({'_type': 'Author', 'created_by': int(request.user.id)})
    agency_type = auth.agency_type
    agency_type_node = node_collection.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
    if agency_type_node:
      for eachset in agency_type_node.collection_set:
        app_collection_set.append(node_collection.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      

  if app_set_id:
    sce_gst = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)})#, {'name': 1, 'type_of': 1})
    title = sce_gst.name
    if title == "StudentCourseEnrollment":
        query = {}
        college = {}
        course = {}
        ac_data_set = []
        records_list = []
        query = {'member_of': sce_gst._id, 'group_set': ObjectId(group_id)}

        res = node_collection.collection.aggregate([
            {
                '$match': query
            }, {
                '$project': {
                    '_id': 0,
                    'sce_id': "$_id",
                    'name': '$name',
                    'college': '$relation_set.for_college',
                    'start_enroll': '$attribute_set.start_enroll',
                    'end_enroll': '$attribute_set.end_enroll',
                    'start_date': '$attribute_set.start_enroll',
                    'end_date': '$attribute_set.end_enroll',
                    'enrollment_status': '$attribute_set.enrollment_status',
                    'enrollment_stud': '$attribute_set.has_enrolled',
                    'approved_stud': '$attribute_set.has_approved',
                    'for_course': '$relation_set.for_acourse'
                }
            },
            {
                '$sort': {'name': 1}
            }
        ])

        records_list = res["result"]
        if records_list:
            for each in res["result"]:
                if each["college"]:
                    if each["college"][0]:
                        colg_list_name = []
                        for each_col in each["college"][0]:
                            colg_id = each_col
                            colg_node = node_collection.one({'_id':ObjectId(colg_id)})
                            colg_list_name.append(colg_node.name)
                each["college"] = colg_list_name

                enrollment_stud_count = 0
                if each["enrollment_stud"]:
                    if each["enrollment_stud"][0]:
                        enrollment_stud_count = len(each["enrollment_stud"][0])
                each["enrollment_stud"] = enrollment_stud_count

                approved_stud_count = 0
                if each["approved_stud"]:
                    if each["approved_stud"][0]:
                        approved_stud_count = len(each["approved_stud"][0])
                each["approved_stud"] = approved_stud_count

                if each["start_date"]:
                    if each["start_date"][0]:
                        each["start_date"] = each["start_date"][0].strftime("%d/%m/%Y")

                if each["end_date"]:
                    if each["end_date"][0]:
                        each["end_date"] = each["end_date"][0].strftime("%d/%m/%Y")

                if each["for_course"]:
                    if each["for_course"][0]:
                        each["for_course"] = each["for_course"][0]
                        course_len = len(each['for_course'])
                        if course_len > 1:
                            each['for_course'] = "FoundationCourse"
                        elif course_len == 1:
                            course_node = node_collection.one({'_id':ObjectId(each['for_course'][0])})
                            if course_node:
                                for attr in course_node.attribute_set:
                                    if attr and 'nussd_course_type' in attr:
                                        each['for_course'] = attr['nussd_course_type']
                                    break
                                        

                ac_data_set.append(each)

        column_headers = [
                    ("sce_id", "Action"),
                    ("name", "Name"),
                    ("for_course", "Course Type"),
                    ("college", "College"),
                    ("start_date", "Enrollment Start-Date"),
                    ("end_date", "Enrollment End-Date"),
                    ("enrollment_stud", "Enrolled"),
                    ("approved_stud", "Approved"),
                    ("enrollment_status", "Status"),
        ]

        response_dict["column_headers"] = column_headers
        response_dict["success"] = True
        response_dict["students_data_set"] = ac_data_set
        response_dict["groupid"] = group_id
        response_dict["app_id"] = app_id
        response_dict["app_set_id"] = app_set_id
    else:
        if request.method == "POST":
          search = request.POST.get("search", "")
          query = {'member_of': sce_gst._id, 'group_set': ObjectId(group_id), 'name': {'$regex': search, '$options': 'i'}}

        else:
          query = {'member_of': sce_gst._id, 'group_set': ObjectId(group_id)}

        nodes = list(node_collection.find(query).sort('name', 1))

        nodes_keys = [('name', "Name")]
        template = ""
    template = "ndf/" + sce_gst.name.strip().lower().replace(' ', '_') + "_list.html"
    default_template = "ndf/mis_list.html"

  if app_set_instance_id:
    template = "ndf/" + sce_gst.name.strip().lower().replace(' ', '_') + "_details.html"
    default_template = "ndf/mis_details.html"

    node = node_collection.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    property_order_list = get_property_order_with_value(node)
    node.get_neighbourhood(node.member_of)

  context_variables = { 'groupid': group_id, 
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title': title,
                        'nodes': nodes, "nodes_keys": nodes_keys, 'node': node,
                        'property_order_list': property_order_list, 'lstFilters': widget_for,
                        'is_link_needed': is_link_needed,
                        'response_dict':json.dumps(response_dict, cls=NodeJSONEncoder)
                      }
  try:
    return render_to_response([template, default_template], 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    error_message = "\n StudentCourseEnrollmentDetailListViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n StudentCourseEnrollmentDetailListViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)


@login_required
def enrollment_enroll(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    Student enrollment
    """
    user_id = int(request.user.id)  # getting django user's id
    user_name = request.user.username  # getting django user's username

    auth = None
    if ObjectId.is_valid(group_id) is False:
        group_ins = node_collection.one({'_type': "Group", "name": group_id})
        auth = node_collection.one({'_type': 'Author', 'name': unicode(user_name) })
        if group_ins:
            group_id = str(group_ins._id)
        else:
            auth = node_collection.one({'_type': 'Author', 'name': unicode(user_name) })
            if auth:
                group_id = str(auth._id)

    app = None
    if app_id is None:
        app = node_collection.one({'_type': "GSystemType", 'name': app_name})
        if app:
            app_id = str(app._id)
    else:
        app = node_collection.one({'_id': ObjectId(app_id)})

    app_name = app.name

    app_collection_set = []
    # app_set = ""
    # nodes = ""
    title = ""
    template_prefix = "mis"

    if user_id:
        if auth is None:
            auth = node_collection.one({
                '_type': 'Author', 'created_by': int(user_id)
            })

        agency_type = auth.agency_type
        agency_type_node = node_collection.one({
            '_type': "GSystemType", 'name': agency_type
        }, {
            'collection_set': 1
        })
        if agency_type_node:
            for eachset in agency_type_node.collection_set:
                app_collection_set.append(node_collection.one({
                    "_id": eachset
                }, {
                    '_id': 1, 'name': 1, 'type_of': 1
                }))

    sce_gs = None
    sce_last_update = None
    ann_course_list = []
    ann_course_ids = []
    ann_course_name = ""
    nussd_course_type = ""
    start_time = ""
    end_time = ""
    start_enroll = ""
    end_enroll = ""
    enrollment_task = {}
    enrollment_status_val = ""
    enrollment_closed = False
    enrollment_reopen = False
    total_student_enroll_list = []
    student_enroll_list = []
    college_enrollment_code = ""
    task_dict = {}
    task_id = None
    at_rt_dict = {}
    req_ats = []

    if app_set_instance_id:
        if ObjectId.is_valid(app_set_instance_id):
            sce_gs = node_collection.one({
                '_id': ObjectId(app_set_instance_id)
            }, {
                'member_of': 1, 'name': 1,
                'last_update': 1, 'attribute_set.start_enroll': 1,
                'attribute_set.end_enroll': 1,
                'attribute_set.enrollment_status': 1,
                'attribute_set.has_enrollment_task': 1
            })

            for attr in sce_gs.attribute_set:
                if attr and "start_enroll" in attr:
                    start_enroll = attr["start_enroll"]
                elif attr and "end_enroll" in attr:
                    end_enroll = attr["end_enroll"]
                elif attr and "enrollment_status" in attr:
                    enrollment_status_val = attr["enrollment_status"]
                elif attr and "has_enrollment_task" in attr:
                    enrollment_task = attr["has_enrollment_task"]

            # Fetch on going enrollment task's id, in order to close and
            # set it's status, if sce_gs node's duration gets expired
            # Keep it here only as it is also being used
            # below to close it's status on proper completion of process
            for task_objectid, task_details_dict in enrollment_task.items():
                if not task_details_dict:
                    task_id = ObjectId(task_objectid)

            # Check the end_enroll date on landing, if its' past,
            # And if sce_gs status is "OPEN";
            # Then set status of sce_gs to "Closed"
            if end_enroll:
                end_enroll = end_enroll.date()
                current_date = datetime.datetime.now().date()
                if (end_enroll < current_date) and (enrollment_status_val == u"OPEN"):
                    # Close sce_gs
                    at_type_node = node_collection.one({
                        '_type': "AttributeType",
                        'name': u"enrollment_status"
                    })
                    if at_type_node:
                        at_node = None
                        at_node = create_gattribute(sce_gs._id, at_type_node, u"CLOSED")
                        if at_node:
                            # Change status of enrollment Task to Closed
                            task_at_type_node = node_collection.one({
                                '_type': "AttributeType",
                                'name': u"Status"
                            })
                            if task_at_type_node:
                                task_dict = {}
                                task_dict["_id"] = task_id
                                task_dict["Status"] = u"Closed"
                                task_dict["modified_by"] = user_id
                                task_dict["created_by_name"] = user_name
                                task_dict["content_org"] = "\n This Student-Course Enrollment Task is no longer valid (Enrollment duration expired)!!!"
                                task_dict["content_org"] = unicode(task_dict["content_org"])

                                task_node = create_task(task_dict)

                                if task_node:
                                    # Set expiration status for closed enrollment task in StudentCourseEnrollment node's has_enrollment_task
                                    expired_on = datetime.datetime.now()

                                    enrollment_task[str(task_id)] = {
                                        "expired_on": expired_on
                                    }
                                    at_type_node = None
                                    at_type_node = node_collection.one({
                                        '_type': "AttributeType",
                                        'name': u"has_enrollment_task"
                                    })

                                    if at_type_node:
                                        attr_node = create_gattribute(sce_gs._id, at_type_node, enrollment_task)

                            # Important as updated status is gtting used below
                            sce_gs.reload()

            sce_gs.get_neighbourhood(sce_gs.member_of)

            for each in sce_gs.for_acourse:
                ann_course_list.append([str(each._id), each.name])
                ann_course_ids.append(each._id)
                ann_course_name = each.name

            if sce_gs.enrollment_status in [u"APPROVAL", u"CLOSED"]:
                enrollment_closed = True
            elif sce_gs.enrollment_status in u"PENDING":
                enrollment_reopen = True
            total_student_enroll_list = sce_gs.has_enrolled

            for attr in sce_gs.for_acourse[0].attribute_set:
                if attr and "start_time" in attr:
                    start_time = attr["start_time"]
                if attr and "end_time" in attr:
                    end_time = attr["end_time"]
                if attr and "nussd_course_type" in attr:
                    nussd_course_type = attr["nussd_course_type"]

            for attr in sce_gs.for_college[0].attribute_set:
                if attr and "enrollment_code" in attr:
                    college_enrollment_code = attr["enrollment_code"]
                    break

    if request.method == "POST":
        enroll_state = request.POST.get("enrollState", "")
        at_rt_list = ["start_enroll", "end_enroll", "for_acourse", "for_college", "for_university", "enrollment_status", "has_enrolled", "has_enrollment_task", "has_approval_task", "has_current_approval_task"]

        mis_admin = node_collection.one({
            '_type': "Group", 'name': "MIS_admin"
        })

        if enroll_state == "Re-open Enrollment":
            task_dict["name"] = ""
            if nussd_course_type == "Foundation Course":
                task_dict["name"] = "Student Course ReOpen Enrollment Task "+ \
                    start_enroll.strftime("%d/%b/%Y") + " - " + end_enroll.strftime("%d/%b/%Y") + \
                    " - FC - " + college_enrollment_code + " - " + start_time.strftime("%b %Y") + " - " + end_time.strftime("%b %Y")

            else:
                task_dict["name"] = "Student Course ReOpen Enrollment Task "+ \
                    start_enroll.strftime("%d/%b/%Y") + " - " + end_enroll.strftime("%d/%b/%Y") + \
                    " - " + ann_course_name

            task_dict["name"] = unicode(task_dict["name"])
            task_dict["created_by"] = user_id
            task_dict["created_by_name"] = user_name
            task_dict["modified_by"] = user_id
            task_dict["contributors"] = [user_id]

            MIS_GAPP = node_collection.one({
                '_type': "GSystemType", 'name': "MIS"
            }, {
                '_id': 1
            })

            sce_gst = node_collection.one({
                "_type": "GSystemType", "name": "StudentCourseEnrollment"
            })

            task_dict["start_time"] = datetime.datetime.now()
            task_dict["end_time"] = None

            glist_gst = node_collection.one({'_type': "GSystemType", 'name': "GList"})
            task_type_node = None
            # Here, GSTUDIO_TASK_TYPES[7] := 'Re-open Student-Course Enrollment'
            task_dict["has_type"] = []
            if glist_gst:
                task_type_node = node_collection.one({
                    'member_of': glist_gst._id, 'name': GSTUDIO_TASK_TYPES[7]
                }, {
                    '_id': 1
                })

                if task_type_node:
                    task_dict["has_type"].append(task_type_node._id)

            task_dict["Status"] = u"New"
            task_dict["Priority"] = u"High"
            task_dict["content_org"] = u""

            task_dict["group_set"] = [mis_admin._id]

            task_dict["Assignee"] = []
            for each_admin_id in mis_admin.group_admin:
                task_dict["Assignee"].append(each_admin_id)

            task_node = create_task(task_dict)

            # Set content for Re-open task (having it's own ObjectId)
            task_dict = {}
            task_dict["_id"] = task_node._id
            task_dict["created_by_name"] = user_name
            student_course_reopen_enrollment_url_link = ""
            site = Site.objects.get(pk=1)
            site = site.name.__str__()
            student_course_reopen_enrollment_url_link = "http://" + site + "/" + \
                mis_admin.name.replace(" ", "%20").encode('utf8') + \
                "/mis/" + str(MIS_GAPP._id) + "/" + str(sce_gst._id) + "/edit" + \
                "/" + str(sce_gs._id) + "?reopen_task_id=" + str(task_node._id)

            task_dict["content_org"] = "\n- Please click [[" + \
                student_course_reopen_enrollment_url_link + "][here]] to re-open enrollment."

            task_dict["content_org"] = unicode(task_dict["content_org"])
            task_node = create_task(task_dict)

            # Update StudentCourseEnrollment node's enrollment_status to "PENDING"
            # PENDING means in a state where admin should reset enrollment duration
            at_rt_dict["enrollment_status"] = u"PENDING"

            for at_rt_name in at_rt_list:
                if at_rt_name in at_rt_dict:
                    at_rt_type_node = node_collection.one({
                        '_type': {'$in': ["AttributeType", "RelationType"]},
                        'name': at_rt_name
                    })

                    if at_rt_type_node:
                        at_rt_node = None

                        if at_rt_type_node._type == "AttributeType" and at_rt_dict[at_rt_name]:
                            at_rt_node = create_gattribute(sce_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])

                        elif at_rt_type_node._type == "RelationType" and at_rt_dict[at_rt_name]:
                            at_rt_node = create_grelation(sce_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])

            return HttpResponseRedirect(reverse(app_name.lower() + ":" + template_prefix + '_enroll',
                kwargs={'group_id': group_id, "app_id": app_id, "app_set_id": app_set_id, "app_set_instance_id": app_set_instance_id}
            ))

        else:
            # enroll_state is either "Complete"/"InProgress"
            sce_last_update = sce_gs.last_update

            # Students Enrolled list
            at_rt_dict["has_enrolled"] = []

            if not total_student_enroll_list:
                total_student_enroll_list = []

            student_enroll_list = request.POST.get("student_enroll_list", "")
            if student_enroll_list:
                for each_student_id in student_enroll_list.split(","):
                    each_student_id = ObjectId(each_student_id.strip())
                    if each_student_id not in total_student_enroll_list:
                        total_student_enroll_list.append(each_student_id)
            else:
                student_enroll_list = []

            at_rt_dict["has_enrolled"] = total_student_enroll_list
            if enroll_state == "Complete":
                # For Student-Course Enrollment Approval
                # Create a task for admin(s) of the MIS_admin group
                completed_on = datetime.datetime.now()

                if nussd_course_type == "Foundation Course":
                    task_dict["name"] = "Student Course Approval Task "+ \
                        start_enroll.strftime("%d/%b/%Y") + " - " + end_enroll.strftime("%d/%b/%Y") + \
                        " - FC - " + college_enrollment_code + " - " + start_time.strftime("%b %Y") + " - " + end_time.strftime("%b %Y")

                else:
                    task_dict["name"] = "Student Course Approval Task "+ \
                        start_enroll.strftime("%d/%b/%Y") + " - " + end_enroll.strftime("%d/%b/%Y") + \
                        " - " + ann_course_name

                task_dict["name"] = unicode(task_dict["name"])
                task_dict["created_by"] = mis_admin.group_admin[0]
                admin_user = User.objects.get(id=mis_admin.group_admin[0])
                task_dict["created_by_name"] = admin_user.username
                task_dict["modified_by"] = mis_admin.group_admin[0]
                task_dict["contributors"] = [mis_admin.group_admin[0]]

                MIS_GAPP = node_collection.one({
                    '_type': "GSystemType", 'name': "MIS"
                }, {
                    '_id': 1
                })
                student_course_approval_url_link = ""
                site = Site.objects.get(pk=1)
                site = site.name.__str__()
                student_course_approval_url_link = "http://" + site + "/" + \
                    mis_admin.name.replace(" ", "%20").encode('utf8') + "/dashboard/group"
                task_dict["content_org"] = "\n- Please click [[" + \
                    student_course_approval_url_link + "][here]] to approve students."
                task_dict["content_org"] = unicode(task_dict["content_org"])

                task_dict["start_time"] = completed_on
                task_dict["end_time"] = None

                glist_gst = node_collection.one({'_type': "GSystemType", 'name': "GList"})
                task_type_node = None
                # Here, GSTUDIO_TASK_TYPES[4] := 'Student-Course Enrollment Approval'
                task_dict["has_type"] = []
                if glist_gst:
                    task_type_node = node_collection.one({
                        'member_of': glist_gst._id, 'name': GSTUDIO_TASK_TYPES[4]
                    }, {
                        '_id': 1
                    })

                    if task_type_node:
                        task_dict["has_type"].append(task_type_node._id)

                task_dict["Status"] = u"New"
                task_dict["Priority"] = u"High"

                task_dict["group_set"] = [mis_admin._id]

                task_dict["Assignee"] = []
                for each_admin_id in mis_admin.group_admin:
                    task_dict["Assignee"].append(each_admin_id)

                task_node = create_task(task_dict)

                enrollment_task_dict = {}
                approval_task_dict = {}
                if "has_approval_task" in sce_gs:
                    approval_task_dict = sce_gs["has_approval_task"]
                    approval_task_dict = approval_task_dict if approval_task_dict else {}

                if "has_enrollment_task" in sce_gs:
                    enrollment_task_dict = sce_gs["has_enrollment_task"]
                    enrollment_task_dict = enrollment_task_dict if enrollment_task_dict else {}

                if str(task_node._id) not in approval_task_dict:
                    approval_task_dict[str(task_node._id)] = {}

                at_rt_dict["has_approval_task"] = approval_task_dict
                at_rt_dict["has_current_approval_task"] = [task_node._id]

                # Update the enrollment task as "Closed"
                task_dict = {}
                task_dict["_id"] = task_id
                task_dict["Status"] = u"Closed"
                task_dict["modified_by"] = user_id
                task_node = create_task(task_dict)

                # Set completion status for closed enrollment task in StudentCourseEnrollment node's has_enrollment_task
                if str(task_id) in enrollment_task_dict:
                    enrollment_task_dict[str(task_id)] = {
                        "completed_on": completed_on, "completed_by": user_id
                    }
                    at_rt_dict["has_enrollment_task"] = enrollment_task_dict

                # Update StudentCourseEnrollment node's enrollment_status to "APPROVAL" state
                at_rt_dict["enrollment_status"] = u"APPROVAL"

                # Update StudentCourseEnrollment node's last_update field
                sce_gs.last_update = datetime.datetime.today()

            elif enroll_state == "In Progress":
                # Update the enrollment task as "In Progress"
                task_dict["_id"] = task_id
                task_dict["Status"] = u"In Progress"
                task_dict["modified_by"] = user_id
                task_node = create_task(task_dict)

                # Update StudentCourseEnrollment node's last_update field
                sce_gs.last_update = datetime.datetime.today()

            # Set course enrollment status of each announced course for each student
            # 1) Append to "selected_course" (RelationType)
            # 2) Set enrollment status for that announce course
            #    in "course_enrollment_status" (AttributeType) as "Enrolled"

            # Fetch students which are not enrolled to given announced course(s)
            student_cur = node_collection.collection.aggregate([{
                "$match": {
                    "_id": {"$in": total_student_enroll_list},
                    "relation_set.selected_course": {"$nin": ann_course_ids}
                }
            }, {
                "$project": {
                    "_id": 1,
                    "selected_course": "$relation_set.selected_course",
                    "course_enrollment_status": "$attribute_set.course_enrollment_status",
                }
            }])

            selected_course_rt = node_collection.one({
                "_type": "RelationType", "name": "selected_course"
            })
            course_enrollment_status_at = node_collection.one({
                "_type": "AttributeType", "name": "course_enrollment_status"
            })

            # Performing multiprocessing to fasten out the below processing of
            # for loop; that is, enrolling students into given course(s)
            mp_enroll_students(
                student_cur["result"], ann_course_ids,
                selected_course_rt, course_enrollment_status_at,
                num_of_processes=multiprocessing.cpu_count()
            )

        # Save/Update GAttribute(s) and/or GRelation(s)
        for at_rt_name in at_rt_list:
            if at_rt_name in at_rt_dict:
                at_rt_type_node = node_collection.one({
                    '_type': {'$in': ["AttributeType", "RelationType"]},
                    'name': at_rt_name
                })

                if at_rt_type_node:
                    at_rt_node = None

                    if at_rt_type_node._type == "AttributeType" and at_rt_dict[at_rt_name]:
                        at_rt_node = create_gattribute(sce_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])

                    elif at_rt_type_node._type == "RelationType" and at_rt_dict[at_rt_name]:
                        at_rt_node = create_grelation(sce_gs._id, at_rt_type_node, at_rt_dict[at_rt_name])

        if sce_last_update < sce_gs.last_update:
            node_collection.collection.update(
                {"_id": sce_gs._id},
                {"$set": {"last_update": sce_gs.last_update}},
                upsert=False, multi=False
            )

        # Very important
        #sce_gs.reload()

        return HttpResponseRedirect(reverse(app_name.lower() + ":" + template_prefix + '_app_detail', kwargs={'group_id': group_id, "app_id":app_id, "app_set_id":app_set_id}))

    else:
        # Populate Announced courses of given enrollment
        if not enrollment_closed:
            # Fetch required list of AttributeTypes
            fetch_ats = ["nussd_course_type", "degree_year","degree_name"]

            for each in fetch_ats:
                each = node_collection.one({
                    '_type': "AttributeType", 'name': each
                }, {
                    '_type': 1, '_id': 1, 'data_type': 1, 'complex_data_type': 1, 'name': 1, 'altnames': 1
                })

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
                req_ats.append(each)

        # Fetch required list of Colleges
        college_cur = None

        title = sce_gs.name

        template = "ndf/student_enroll.html"
        variable = RequestContext(request, {
            'groupid': group_id, 'group_id': group_id,
            'title': title,
            'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set,
            'app_set_id': app_set_id, 'app_set_instance_id': app_set_instance_id,
            'ATs': req_ats, 'colleges': college_cur,
            'ann_course_list': ann_course_list, "start_enroll": start_enroll, "end_enroll": end_enroll,
            "enrollment_closed": enrollment_closed, "enrollment_reopen": enrollment_reopen
            # 'enrollment_open_ann_course_ids': enrollment_open_ann_course_ids
            # 'nodes':nodes,
        })

        return render_to_response(template, variable)


@get_execution_time
def mp_enroll_students(student_cur, ann_course_ids, selected_course_rt, course_enrollment_status_at, num_of_processes=4):
    def worker(student_cur, ann_course_ids, selected_course_rt, course_enrollment_status_at):
        for each_student in student_cur:
            prev_selected_course_ids = []
            selected_course_ids = []
            if each_student["selected_course"]:
                prev_selected_course_ids = each_student["selected_course"][0]
            else:
                prev_selected_course_ids = each_student["selected_course"]

            selected_course_ids = ann_course_ids + prev_selected_course_ids
            try:
                gr_node = create_grelation(each_student["_id"], selected_course_rt, selected_course_ids)
                # try block is used to avoid "Multiple results found" error
                try:
                    course_enrollment_status = {}
                    if each_student["course_enrollment_status"]:
                        course_enrollment_status = each_student["course_enrollment_status"][0]

                    for each_course_id in selected_course_ids:
                        str_course_id = str(each_course_id)
                        if str_course_id not in course_enrollment_status:
                            course_enrollment_status.update({str_course_id: u"Enrolled"})
                    at_node = create_gattribute(each_student["_id"], course_enrollment_status_at, course_enrollment_status)
                except Exception as e:
                    gr_node = create_grelation(each_student["_id"], selected_course_rt, prev_selected_course_ids)
                    # continue
            except Exception as e:
                print "\n " + str(e)

    # Each process will get 'chunksize' student_cur and a queue to put his out
    # dict into
    chunksize = int(math.ceil(len(student_cur) / float(num_of_processes)))
    procs = []

    for i in range(num_of_processes):
        p = multiprocessing.Process(
            target=worker,
            args=(student_cur[chunksize * i:chunksize * (i + 1)], ann_course_ids, selected_course_rt, course_enrollment_status_at)
        )
        procs.append(p)
        p.start()

    # Wait for all worker processes to finish
    for p in procs:
        p.join()

''' -- imports from python libraries -- '''
# from datetime import datetime
import datetime
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect  # , HttpResponse uncomment when to use
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response  # , render  uncomment when to use
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from mongokit import IS
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT, GSTUDIO_TASK_TYPES
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.templatetags.ndf_tags import edit_drawer_widget, get_disc_replies, get_all_replies,user_access_policy, get_relation_value, check_is_gstaff
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data, get_execution_time, delete_node, replicate_resource
from gnowsys_ndf.ndf.views.notify import set_notif_val
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value, get_group_name_id
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, create_task, delete_grelation
from gnowsys_ndf.notification import models as notification


GST_COURSE = node_collection.one({'_type': "GSystemType", 'name': "Course"})
GST_ACOURSE = node_collection.one({'_type': "GSystemType", 'name': "Announced Course"})

app = GST_COURSE


@get_execution_time
def course(request, group_id, course_id=None):
    """
    * Renders a list of all 'courses' available within the database.
    """
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    group_obj = node_collection.one({'_id': ObjectId(group_id)})

    group_obj_post_node_list = []
    app_id = None
    app_id = app._id
    course_coll = None
    all_course_coll = None
    ann_course_coll = None
    enrolled_course_coll = []
    enr_ce_coll = []
    course_enrollment_status = None
    app_set_id = None
    query = {}

    course_ins = node_collection.find_one({'_type': "GSystemType", "name": "Course"})

    if course_ins:
        course_id = str(course_ins._id)

    group_obj_post_node_list = group_obj.post_node
    app_set = node_collection.one({'_type': "GSystemType", 'name': "Announced Course"})
    app_set_id = app_set._id
    ce_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseEventGroup"})

    # Course search view
    # title = GST_COURSE.name
    # if GST_COURSE.name == "Course":
    title = "eCourses"
    
    query = {'member_of': ce_gst._id,'_id':{'$in': group_obj_post_node_list}}
    gstaff_access = False
    if request.user.id:
        # if user is admin then show all ce
        gstaff_access = check_is_gstaff(group_id,request.user)
        if not gstaff_access:
            query.update({'author_set':{'$ne':int(request.user.id)}})

        course_coll = node_collection.find({'member_of': GST_COURSE._id,'group_set': ObjectId(group_id),'status':u"DRAFT"}).sort('last_update', -1)
        enr_ce_coll = node_collection.find({'member_of': ce_gst._id,'author_set': int(request.user.id),'_id':{'$in': group_obj_post_node_list}}).sort('last_update', -1)

        user_access =  user_access_policy(group_id ,request.user)
        if user_access == "allow":
            # show PRIVATE CourseEvent
            query.update({'group_type': {'$in':[u"PRIVATE",u"PUBLIC"]}})

    ce_coll = node_collection.find(query).sort('last_update', -1)
    # print "\n\n ce_coll",ce_coll.count()
    return render_to_response("ndf/course.html",
                            {'title': title,
                             'app_id': app_id, 'course_gst': GST_COURSE,
                            'req_from_course':True,
                             'app_set_id': app_set_id,
                             'searching': True, 'course_coll': course_coll,
                             'groupid': group_id, 'group_id': group_id,
                             'all_course_coll': all_course_coll,
                             'ce_coll':ce_coll,
                             'enr_ce_coll':enr_ce_coll,
                             'enrolled_course_coll': enrolled_course_coll,
                             'ann_course_coll': ann_course_coll
                            },
                            context_instance=RequestContext(request)
                            )

@login_required
@get_execution_time
def create_edit(request, group_id, node_id=None):
    """Creates/Modifies details about the given quiz-item.
    """
    # ins_objectid = ObjectId()
    # if ins_objectid.is_valid(group_id) is False:
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else:
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth:
    #             group_id = str(auth._id)
    # else:
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    logo_img_node = None
    grel_id = None
    fileobj = None
    at_course_type = node_collection.one({'_type': 'AttributeType', 'name': 'nussd_course_type'})
    context_variables = {'title': GST_COURSE.name,
                        'group_id': group_id,
                        'groupid': group_id
                    }
    if node_id:
        course_node = node_collection.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
        # logo_img_node, grel_id = get_relation_value(node_id,'has_logo')
        grel_dict = get_relation_value(node_id,'has_logo')
        is_cursor = grel_dict.get("cursor",False)
        if not is_cursor:
            logo_img_node = grel_dict.get("grel_node")
            grel_id = grel_dict.get("grel_id")

    else:
        course_node = node_collection.collection.GSystem()
    available_nodes = node_collection.find({'_type': u'GSystem', 'member_of': ObjectId(GST_COURSE._id),'group_set': ObjectId(group_id),'status':{"$in":[u"DRAFT",u"PUBLISHED"]}})

    nodes_list = []
    for each in available_nodes:
      nodes_list.append(str((each.name).strip().lower()))


    if request.method == "POST":
        # get_node_common_fields(request, course_node, group_id, GST_COURSE)
        course_node.save(is_changed=get_node_common_fields(request, course_node, group_id, GST_COURSE),groupid=group_id)
        create_gattribute(course_node._id, at_course_type, u"General")
        
        # adding thumbnail 
        f = request.FILES.get("doc", "")
        # print "\nf is ",f

        if f:

            # if existing logo image is found
            if logo_img_node:
                # print "\nlogo_img_node--",logo_img_node
                # check whether it appears in any other node's grelation
                rel_obj = None
                rel_obj = triple_collection.find({"_type": "GRelation", 'subject': {'$ne': ObjectId(course_node._id)}, 'right_subject': logo_img_node._id})
                file_cur = node_collection.find({'_type':"File",'fs_file_ids':logo_img_node.fs_file_ids,'_id': {'$ne': logo_img_node._id}})
                # print "\nrel_obj--",rel_obj.count()
                # print "\nfile_cur.count()--",file_cur.count()
                if rel_obj.count() > 0 or file_cur.count() > 0:
                    # if found elsewhere too, delete it from current node's grelation ONLY
                    # print "\n Image exists for others"
                    if grel_id:
                        del_status, del_status_msg = delete_grelation(
                            node_id=ObjectId(grel_id),
                            deletion_type=1
                        )
                        # print del_status, "--", del_status_msg
                else:
                    # else delete the logo file
                    # print "\n delete node"
                    del_status, del_status_msg = delete_node(
                        node_id=logo_img_node._id,
                        deletion_type=1
                    )
                    # print del_status, "--", del_status_msg

            fileobj,fs = save_file(f,f.name,request.user.id,group_id, "", "", username=unicode(request.user.username), access_policy="PUBLIC", count=0, first_object="", oid=True)
            if fileobj:
                rt_has_logo = node_collection.one({'_type': "RelationType", 'name': "has_logo"})
                # print "\n creating GRelation has_logo\n"
                create_grelation(course_node._id, rt_has_logo, ObjectId(fileobj))
        return HttpResponseRedirect(reverse('course', kwargs={'group_id': group_id}))
    else:
        if node_id:
            context_variables['node'] = course_node
            context_variables['groupid'] = group_id
            context_variables['group_id'] = group_id
            context_variables['app_id'] = app._id
            context_variables['logo_img_node'] = logo_img_node
        context_variables['nodes_list'] = json.dumps(nodes_list)
        return render_to_response("ndf/course_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )


# @login_required
@get_execution_time
def course_detail(request, group_id, _id):
    # ins_objectid = ObjectId()
    # if ins_objectid.is_valid(group_id) is False:
    #     group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else:
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth:
    #             group_id = str(auth._id)
    # else:
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    course_structure_exists = False
    enrolled_status = False
    check_enroll_status = False
    title = GST_COURSE.name

    course_node = node_collection.one({"_id": ObjectId(_id)})
    if course_node:
        if course_node.collection_set:
            course_structure_exists = True

    gs_name = course_node.member_of_names_list[0]
    context_variables = {'groupid': group_id,
                        'group_id': group_id,
                        'app_id': app._id,
                        'title': title,
                        'node': course_node,
                        'node_type': gs_name
    }
    if gs_name == "Course":
        context_variables["course_structure_exists"] = course_structure_exists
        if course_node.relation_set:
            for rel in course_node.relation_set:
                if "announced_as" in rel:
                    cnode = node_collection.one({'_id': ObjectId(rel["announced_as"][0])},{'_id':1})
                    context_variables["acnode"] = str(cnode['_id'])
                    check_enroll_status = True
                    break

    else:
        if course_node.relation_set:
            for rel in course_node.relation_set:
                if "announced_for" in rel:
                    cnode = node_collection.one({'_id': ObjectId(rel["announced_for"][0])})
                    context_variables["cnode"] = cnode
                    check_enroll_status = True
                    break
    if request.user.id:
        if check_enroll_status:
            usr_id = int(request.user.id)
            auth_node = node_collection.one({'_type': "Author", 'created_by': usr_id})


            course_enrollment_status = {}

            if auth_node.attribute_set:
                for each in auth_node.attribute_set:
                    if each and "course_enrollment_status" in each:
                        course_enrollment_status = each["course_enrollment_status"]

            if "acnode" in context_variables:
                str_course_id = str(context_variables["acnode"])
            else:
                str_course_id = str(course_node._id)

            if course_enrollment_status:
                if str_course_id in course_enrollment_status:
                    enrolled_status = True
            context_variables['enrolled_status'] = enrolled_status
    return render_to_response("ndf/course_detail.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
        )


@login_required
@get_execution_time
def course_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    Creates/Modifies document of given sub-types of Course(s).
    """
    auth = None
    tiss_site = False
    # if ObjectId.is_valid(group_id) is False:
    #     group_ins = node_collection.one({'_type': "Group", "name": group_id})
    #     auth = node_collection.one({
    #         '_type': 'Author', 'name': unicode(request.user.username)
    #     })

    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else:
    #         auth = node_collection.one({
    #             '_type': 'Author', 'name': unicode(request.user.username)
    #         })
    #         if auth:
    #             group_id = str(auth._id)
    # else:
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    if GSTUDIO_SITE_NAME is "TISS":
        tiss_site = True

    app = None
    if app_id is None:
        app = node_collection.one({'_type': "GSystemType", 'name': app_name})
        if app:
            app_id = str(app._id)
    else:
        app = node_collection.one({'_id': ObjectId(app_id)})
    # app_set = ""
    app_collection_set = []
    title = ""

    course_gst = None
    course_gs = None
    hide_mis_meta_content = True
    mis_admin = None

    property_order_list = []

    template = ""
    template_prefix = "mis"

    if request.user:
        if auth is None:
            auth = node_collection.one({
                '_type': 'Author', 'name': unicode(request.user.username)
            })

        agency_type = auth.agency_type
        agency_type_node = node_collection.one({
            '_type': "GSystemType", 'name': agency_type
        }, {
            'collection_set': 1
        })
        if agency_type_node:
            for eachset in agency_type_node.collection_set:
                app_collection_set.append(
                    node_collection.one({
                        "_id": eachset
                    }, {
                        '_id': 1, 'name': 1, 'type_of': 1
                    })
                )
    if app_set_id:
        course_gst = node_collection.one({
            '_type': "GSystemType", '_id': ObjectId(app_set_id)
        }, {
            'name': 1, 'type_of': 1
        })

        template = "ndf/" + course_gst.name.strip().lower().replace(' ', '_') \
            + "_create_edit.html"
        title = course_gst.name

    if app_set_instance_id:
        course_gs = node_collection.one({
            '_type': "GSystem", '_id': ObjectId(app_set_instance_id)
        })
    else:
        course_gs = node_collection.collection.GSystem()
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
            colg_list_cur = node_collection.find({
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
                ac_node = node_collection.one({
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
                    course_node = node_collection.one({
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
                        course_node = node_collection.find_one({
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
                    cnode_for_content = node_collection.one({'_id': ObjectId(nc_id)})
                    nc_course_code = ac_nc_code[2]
                    if not course_gs:
                        # Create new Announced Course GSystem
                        course_gs = node_collection.collection.GSystem()
                        course_gs.member_of.append(course_gst._id)

                    if tiss_site:
                        # Prepare name for Announced Course GSystem
                        c_name = unicode(
                            nc_course_code + " - " + college_enrollment_code + " - "
                            + start_time.strftime("%b %Y") + " - "
                            + end_time.strftime("%b %Y")
                        )
                    else:
                        # Prepare name for Announced Course GSystem
                        c_name = unicode(
                            nc_course_code + " - "+ start_time.strftime("%b %Y") + " - "
                            + end_time.strftime("%b %Y")
                        )

                    request.POST["name"] = c_name

                    is_changed = get_node_common_fields(
                        request, course_gs, group_id, course_gst
                    )
                    if is_changed:
                        # Remove this when publish button is setup on interface
                        course_gs.status = u"PUBLISHED"

                    course_gs.content_org = cnode_for_content.content_org
                    course_gs.content = cnode_for_content.html_content

                    course_gs.save(is_changed=is_changed,groupid=group_id)
		            # [B] Store AT and/or RT field(s) of given course-node
                    for tab_details in property_order_list:
                        for field_set in tab_details[1]:
                            # Fetch only Attribute field(s) / Relation field(s)
                            if '_id' in field_set:
                                field_instance = node_collection.one({
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

                                        course_gs_triple_instance = create_gattribute(course_gs._id, node_collection.collection.AttributeType(field_instance), field_value)

                                    else:
                                        # i.e if field_instance_type == RelationType
                                        if field_instance["name"] == "announced_for":
                                            field_value = ObjectId(nc_id)
                                            # Pass ObjectId of selected Course

                                        elif field_instance["name"] == "acourse_for_college":
                                            field_value = college_node._id
                                            # Pass ObjectId of selected College

                                        course_gs_triple_instance = create_grelation(course_gs._id, node_collection.collection.RelationType(field_instance), field_value)

                    ann_course_id_list.append(course_gs._id)

            #commented email notifications to all registered user after announcement
            # if not tiss_site:

            #     site = Site.objects.get(pk=1)
            #     site = site.name.__str__()
            #     ann_course_url_link = "http://" + site + "/home/course/course_detail/" + \
            #         str(course_gs._id)
            #     user_obj = User.objects.all()
            #     # Sending email to all registered users on site NROER
            #     render_label = render_to_string(
            #         "notification/label.html",
            #         {"sender": "NROER eCourses",
            #           "activity": "Course Announcement",
            #           "conjunction": "-"
            #         })
            #     if user_obj:
            #         notification.create_notice_type(render_label," New eCourse '"\
            #             + str(course_gs.name) +"' has been announced."\
            #             +" Visit this link to enroll into this ecourse : " \
            #             + ann_course_url_link, "notification")
            #         notification.send(user_obj, render_label, {"from_user": "NROER eCourses"})

        else:
            is_changed = get_node_common_fields(request, course_gs, group_id, course_gst)

            if is_changed:
                # Remove this when publish button is setup on interface
                course_gs.status = u"PUBLISHED"

            course_gs.save(is_changed=is_changed,groupid=group_id)
            # [B] Store AT and/or RT field(s) of given course-node
            for tab_details in property_order_list:
                for field_set in tab_details[1]:
                    # Fetch only Attribute field(s) / Relation field(s)
                    if '_id' in field_set:
                        field_instance = node_collection.one({'_id': field_set['_id']})
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
                                    node_collection.collection.AttributeType(field_instance),
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
                                    node_collection.collection.RelationType(field_instance),
                                    field_value
                                )
        if tiss_site:
            return HttpResponseRedirect(
                reverse(
                    app_name.lower() + ":" + template_prefix + '_app_detail',
                    kwargs={
                        'group_id': group_id, "app_id": app_id,
                        "app_set_id": app_set_id
                    }
                )
            )
        else:
            return HttpResponseRedirect(
                reverse(
                    "course",
                    kwargs={
                        'group_id': group_id
                    }
                )
            )

    univ = node_collection.one({
        '_type': "GSystemType", 'name': "University"
    }, {
        '_id': 1
    })
    university_cur = None

    if not mis_admin:
        mis_admin = node_collection.one(
            {'_type': "Group", 'name': "MIS_admin"},
            {'_id': 1, 'name': 1, 'group_admin': 1}
        )

    if tiss_site:
        hide_mis_meta_content = False
    if univ and mis_admin:
        university_cur = node_collection.find(
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
        'hide_mis_meta_content':hide_mis_meta_content,
        'tiss_site': tiss_site,

        'university_cur': university_cur,
        'property_order_list': property_order_list
    }

    if app_set_instance_id:
        course_gs.get_neighbourhood(course_gs.member_of)
        context_variables['node'] = course_gs

        if "Announced Course" in course_gs.member_of_names_list:
            for attr in course_gs.attribute_set:
                if attr:
                    for eachk, eachv in attr.items():
                        context_variables[eachk] = eachv

            for rel in course_gs.relation_set:
                if rel:
                    for eachk, eachv in rel.items():
                        if eachv:
                            get_node_name = node_collection.one({'_id': eachv[0]})
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
@get_execution_time
def mis_course_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  Detail view of NUSSD Course/ Announced Course
  """
  # print "\n Found course_detail n gone inn this...\n\n"

  auth = None
  # if ObjectId.is_valid(group_id) is False:
  #   group_ins = node_collection.one({'_type': "Group", "name": group_id})
  #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #   if group_ins:
  #     group_id = str(group_ins._id)
  #   else:
  #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
  #     if auth:
  #       group_id = str(auth._id)
  # else:
  #   pass
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)

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

  course_gst = None
  course_gs = None

  node = None
  property_order_list = []
  property_order_list_ac = []
  is_link_needed = True         # This is required to show Link button on interface that link's Student's/VoluntaryTeacher's node with it's corresponding Author node

  template_prefix = "mis"
  response_dict = {'success': False}
  context_variables = {}

  #Course structure collection _dict
  course_collection_dict = {}
  course_collection_list = []
  course_structure_exists = False

  if request.user:
    if auth is None:
      auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username)})

    if auth:
      agency_type = auth.agency_type
      agency_type_node = node_collection.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
      if agency_type_node:
        for eachset in agency_type_node.collection_set:
          app_collection_set.append(node_collection.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))

  if app_set_id:
    course_gst = node_collection.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    title = course_gst.name
    template = "ndf/course_list.html"
    query = {}
    college = {}
    course = {}
    ac_data_set = []
    records_list = []
    if course_gst.name == "Announced Course":
        query = {
            "member_of": course_gst._id,
            "group_set": ObjectId(group_id),
            "status": "PUBLISHED",
            "attribute_set.ann_course_closure": u"Open",
        }

        res = node_collection.collection.aggregate([
            {
                '$match': query
            }, {
                '$project': {
                    '_id': 0,
                    'ac_id': "$_id",
                    'name': '$name',
                    'course': '$relation_set.announced_for',
                    'college': '$relation_set.acourse_for_college',
                    'nussd_course_type': '$attribute_set.nussd_course_type',
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
                if each["college"]:
                    colg_id = each["college"][0][0]
                    if colg_id not in college:
                        c = node_collection.one({"_id": colg_id}, {"name": 1, "relation_set.college_affiliated_to": 1})
                        each["college"] = c.name
                        each["college_id"] = c._id
                        college[colg_id] = {}
                        college[colg_id]["name"] = each["college"]
                        for rel in c.relation_set:
                            if rel and "college_affiliated_to" in rel:
                                univ_id = rel["college_affiliated_to"][0]
                                u = node_collection.one({"_id": univ_id}, {"name": 1})
                                each.update({"university": u.name})
                                college[colg_id]["university"] = each["university"]
                                college[colg_id]["university_id"] = u._id
                                each["university_id"] = u._id
                    else:
                        each["college"] = college[colg_id]["name"]
                        each["college_id"] = colg_id
                        each.update({"university": college[colg_id]["university"]})
                        each.update({"university_id": college[colg_id]["university_id"]})

                if each["course"]:
                    course_id = each["course"][0][0]
                    if course_id not in course:
                        each["course"] = node_collection.one({"_id": course_id}).name
                        course[course_id] = each["course"]
                    else:
                        each["course"] = course[course_id]

                ac_data_set.append(each)

        column_headers = [
                    ("name", "Announced Course Name"),
                    ("course", "Course Name"),
                    ("nussd_course_type", "Course Type"),
                    ("college", "College"),
                    ("university", "University")
        ]

    else:
        query = {
            "member_of": course_gst._id,
            "group_set": ObjectId(group_id),
        }

        res = node_collection.collection.aggregate([
            {
                '$match': query
            }, {
                '$project': {
                    '_id': 0,
                    'ac_id': "$_id",
                    'name': '$name',
                    'nussd_course_type': '$attribute_set.nussd_course_type',
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
                ac_data_set.append(each)

        column_headers = [
                    ("ac_id", "Edit"),
                    ("name", "Course Name"),
                    ("nussd_course_type", "Course Type"),
        ]


    response_dict["column_headers"] = column_headers
    response_dict["success"] = True
    response_dict["students_data_set"] = ac_data_set
    response_dict["groupid"] = group_id
    response_dict["app_id"] = app_id
    response_dict["app_set_id"] = app_set_id

  if app_set_instance_id:
    template = "ndf/course_details.html"

    node = node_collection.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    property_order_list = get_property_order_with_value(node)
    node.get_neighbourhood(node.member_of)
    if title == u"Announced Course":
        property_order_list_ac = node.attribute_set

    # Course structure as list of dicts
    if node.collection_set:
      course_structure_exists = True


  context_variables = { 'groupid': group_id, 'group_id': group_id,
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'course_gst_name': course_gst.name,
                        'title': title,
                        'course_structure_exists': course_structure_exists,
                        'node': node,
                        'property_order_list': property_order_list,
                        'property_order_list_ac': property_order_list_ac,
                        'is_link_needed': is_link_needed,
                        'response_dict':json.dumps(response_dict, cls=NodeJSONEncoder)
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
    error_message = "\n CourseDetailListViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n CourseDetailListViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)



# Ajax views for setting up Course Structure 

@login_required
@get_execution_time
def create_course_struct(request, group_id, node_id):
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

    # ins_objectid = ObjectId()
    # if ins_objectid.is_valid(group_id) is False:
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else:
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth:
    #             group_id = str(auth._id)
    # else:
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    group_obj = node_collection.one({'_id': ObjectId(group_id)})
    app_id = None
    app_set_id = None
    tiss_site = False

    property_order_list_cs = []
    property_order_list_css = []
    course_structure_exists = False
    title = "Course Authoring"
    if "CourseEventGroup" in group_obj.member_of_names_list:
        title = "CourseEvent Authoring"

    if GSTUDIO_SITE_NAME is "TISS":
        tiss_site = True

    course_node = node_collection.one({"_id": ObjectId(node_id)})

    cs_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSection"})
    cs_gs = node_collection.collection.GSystem()
    cs_gs.member_of.append(cs_gst._id)
    property_order_list_cs = get_property_order_with_value(cs_gs)

    css_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSubSection"})
    css_gs = node_collection.collection.GSystem()
    css_gs.member_of.append(css_gst._id)
    property_order_list_css = get_property_order_with_value(css_gs)

    course_collection_list = course_node.collection_set
    if course_collection_list:
        course_structure_exists = True

    # for attr in course_node.attribute_set:
    #   if attr.has_key("evaluation_type"):
    #     eval_type = attr["evaluation_type"]

    #If evaluation_type flag is True, it is Final. If False, it is Continous
    # if(eval_type==u"Final"):
    #     eval_type_flag = True
    # else:
    #     eval_type_flag = False

    if request.method == "GET":
      app_id = request.GET.get("app_id", "")
      app_set_id = request.GET.get("app_set_id", "")
    return render_to_response("ndf/create_course_structure.html",
                                  {'cnode': course_node,
                                    'groupid': group_id,
                                    'group_id': group_id,
                                    'title': title,
                                    'tiss_site':tiss_site,
                                    'app_id': app_id, 'app_set_id': app_set_id,
                                    'property_order_list': property_order_list_cs,
                                    'property_order_list_css': property_order_list_css
                                  },
                                  context_instance=RequestContext(request)
        )


@login_required
def save_course_section(request, group_id):
    '''
    Accepts:
     * NUSSD Course/Course node _id
     * CourseSection name

    Actions:
     * Creates CourseSection GSystem with name received.
     * Appends this new CourseSection node id into
      NUSSD Course/Course collection_set

    Returns:
     * success (i.e True/False)
     * ObjectId of CourseSection node
    '''
    response_dict = {"success": False}
    if request.is_ajax() and request.method == "POST":
        try:
            group_id = ObjectId(group_id)
        except:
            group_name, group_id = get_group_name_id(group_id)
        group_obj = node_collection.one({'_id': ObjectId(group_id)})

        if "CourseEventGroup" in group_obj.member_of_names_list:
            cs_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSectionEvent"})
        else:
            cs_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSection"})
        cs_node_name = request.POST.get("cs_name", '')
        course_node_id = request.POST.get("course_node_id", '')
        cs_new = node_collection.collection.GSystem()
        cs_new.member_of.append(cs_gst._id)
        cs_new.name = cs_node_name
        cs_new.modified_by = int(request.user.id)
        cs_new.status = u"PUBLISHED"
        cs_new.created_by = int(request.user.id)
        cs_new.contributors.append(int(request.user.id))
        course_node = node_collection.one({"_id": ObjectId(course_node_id)})
        cs_new.prior_node.append(ObjectId(course_node._id))
        cs_new.save(groupid=group_id)
        node_collection.collection.update({'_id': course_node._id}, {'$push': {'collection_set': cs_new._id }}, upsert=False, multi=False)
        response_dict["success"] = True
        response_dict["cs_new_id"] = str(cs_new._id)
        return HttpResponse(json.dumps(response_dict))


@login_required
def save_course_sub_section(request, group_id):
    '''
    Accepts:
     * CourseSection node _id
     * CourseSubSection name

    Actions:
     * Creates CourseSubSection GSystem with name received.
     * Appends this new CourseSubSection node id into
      CourseSection collection_set

    Returns:
     * success (i.e True/False)
     * ObjectId of CourseSubSection node

    '''

    response_dict = {"success": False}
    if request.is_ajax() and request.method == "POST":
        try:
            group_id = ObjectId(group_id)
        except:
            group_name, group_id = get_group_name_id(group_id)
        group_obj = node_collection.one({'_id': ObjectId(group_id)})

        if "CourseEventGroup" in group_obj.member_of_names_list:
            css_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSubSectionEvent"})
        else:
            css_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSubSection"})

        css_node_name = request.POST.get("css_name", '')
        cs_node_id = request.POST.get("cs_node_id", '')
        css_new = node_collection.collection.GSystem()
        css_new.member_of.append(css_gst._id)
        # set name
        css_new.name = css_node_name
        css_new.modified_by = int(request.user.id)
        css_new.status = u"PUBLISHED"
        css_new.created_by = int(request.user.id)
        css_new.contributors.append(int(request.user.id))

        cs_node = node_collection.one({"_id": ObjectId(cs_node_id)})
        css_new.prior_node.append(cs_node._id)
        css_new.save(groupid=group_id)
        node_collection.collection.update({'_id': cs_node._id}, {'$push': {'collection_set': css_new._id }}, upsert=False, multi=False)
        response_dict["success"] = True
        response_dict["css_new_id"] = str(css_new._id)
        return HttpResponse(json.dumps(response_dict))


@login_required
def change_node_name(request, group_id):
    '''
    Accepts:
     * CourseSection/ CourseSubSection node _id
     * New name for CourseSection node

    Actions:
     * Updates received node's name
    '''

    response_dict = {"success": False}
    if request.is_ajax() and request.method == "POST":
        node_id = request.POST.get("node_id", '')
        new_name = request.POST.get("new_name", '')
        node = node_collection.one({"_id": ObjectId(node_id)})
        node.name = new_name.strip()
        node.save(groupid=group_id)
        response_dict["success"] = True
        return HttpResponse(json.dumps(response_dict))


@login_required
def change_order(request, group_id):
    '''
    Accepts:
     * 2 node ids.
        Basically, either of CourseSection or CourseSubSection
     * Parent node id
        Either a NUSSD Course/Course or CourseSection

    Actions:
     * Swaps the 2 node ids in the collection set of received
        parent node
    '''

    response_dict = {"success": False}
    collection_set_list = []
    if request.is_ajax() and request.method == "POST":
        node_id_up = request.POST.get("node_id_up", '')
        node_id_down = request.POST.get("node_id_down", '')
        parent_node_id = request.POST.get("parent_node", '')

        parent_node = node_collection.one({"_id": ObjectId(parent_node_id)})
        collection_set_list = parent_node.collection_set
        a, b = collection_set_list.index(ObjectId(node_id_up)), collection_set_list.index(ObjectId(node_id_down))
        collection_set_list[b], collection_set_list[a] = collection_set_list[a], collection_set_list[b]
        node_collection.collection.update({'_id': parent_node._id}, {'$set': {'collection_set': collection_set_list }}, upsert=False, multi=False)
	
        parent_node.reload()
        response_dict["success"] = True
        return HttpResponse(json.dumps(response_dict))


@login_required
def course_sub_section_prop(request, group_id):
    '''
    Accepts:
     * CourseSubSection node _id
     * Properties dict

    Actions:
     * Creates GAttributes with the values of received dict
        for the respective CourseSubSection node

    Returns:
     * success (i.e True/False)
     * If request.method is POST, all GAttributes in a dict structure,
    '''
    response_dict = {"success": False}
    if request.is_ajax():
        if request.method == "POST":
            assessment_flag = False

            css_node_id = request.POST.get("css_node_id", '')
            prop_dict = request.POST.get("prop_dict", '')
            assessment_chk = json.loads(request.POST.get("assessment_chk", ''))

            prop_dict = json.loads(prop_dict)

            css_node = node_collection.one({"_id": ObjectId(css_node_id)})

            at_cs_hours = node_collection.one({'_type': 'AttributeType', 'name': 'course_structure_minutes'})
            at_cs_assessment = node_collection.one({'_type': 'AttributeType', 'name': 'course_structure_assessment'})
            at_cs_assignment = node_collection.one({'_type': 'AttributeType', 'name': 'course_structure_assignment'})
            at_cs_min_marks = node_collection.one({'_type': 'AttributeType', 'name': 'min_marks'})
            at_cs_max_marks = node_collection.one({'_type': 'AttributeType', 'name': 'max_marks'})

            if assessment_chk is True:
                create_gattribute(css_node._id, at_cs_assessment, True)
                assessment_flag = True

            for propk, propv in prop_dict.items():
                # add attributes to css gs
                if(propk == "course_structure_minutes"):
                    create_gattribute(css_node._id, at_cs_hours, int(propv))
                elif(propk == "course_structure_assignment"):
                    create_gattribute(css_node._id, at_cs_assignment, propv)
                if assessment_flag:
                    if(propk == "min_marks"):
                        create_gattribute(css_node._id, at_cs_min_marks, int(propv))
                    if(propk == "max_marks"):
                        create_gattribute(css_node._id, at_cs_max_marks, int(propv))
            css_node.reload()
            response_dict["success"] = True

        else:
            css_node_id = request.GET.get("css_node_id", '')
            css_node = node_collection.one({"_id": ObjectId(css_node_id)})

            if css_node.attribute_set:
                for each in css_node.attribute_set:
                    for k, v in each.items():
                        response_dict[k] = v
                response_dict["success"] = True
            else:
                response_dict["success"] = False

        return HttpResponse(json.dumps(response_dict))


@login_required
def add_units(request, group_id):
    '''
    Accepts:
     * CourseSubSection node _id
     * NUSSD Course/Course node _id

    Actions:
     * Redirects to course_units.html
    '''
    variable = None
    unit_node = None
    css_node_id = request.GET.get('css_node_id', '')
    unit_node_id = request.GET.get('unit_node_id', '')
    course_node_id = request.GET.get('course_node', '')
    app_id = request.GET.get('app_id', '')
    app_set_id = request.GET.get('app_set_id', '')
    css_node = node_collection.one({"_id": ObjectId(css_node_id)})
    course_node = node_collection.one({"_id": ObjectId(course_node_id)})
    title = "Course Units"
    try:
        unit_node = node_collection.one({"_id": ObjectId(unit_node_id)})
    except:
        unit_node = None
    page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
    page_instances = node_collection.find({"type_of": page_gst._id})
    page_ins_list = [i for i in page_instances]

    variable = RequestContext(request, {
        'group_id': group_id, 'groupid': group_id,
        'css_node': css_node,
        'title': title,
        'app_set_id': app_set_id,
        'app_id': app_id,
        'unit_node': unit_node,
        'course_node': course_node,
        'page_instance': page_ins_list
    })

    template = "ndf/course_units.html"
    return render_to_response(template, variable)


@login_required
def get_resources(request, group_id):
    '''
    Accepts:
     * Name of GSystemType (Page, File, etc.)
     * CourseSubSection node _id
     * widget_for

    Actions:
     * Fetches all GSystems of selected GSystemType as resources

    Returns:
     * Returns Drawer with resources
    '''
    response_dict = {'success': False, 'message': ""}
    try:
        if request.is_ajax() and request.method == "POST":
            css_node_id = request.POST.get('css_node_id', "")
            unit_node_id = request.POST.get('unit_node_id', "")
            widget_for = request.POST.get('widget_for', "")
            resource_type = request.POST.get('resource_type', "")
            resource_type = resource_type.strip()
            list_resources = []
            css_node = node_collection.one({"_id": ObjectId(css_node_id)})
            units_res = []
            try:
                unit_node = node_collection.one({"_id": ObjectId(unit_node_id)})
                units_res = [ObjectId(each_res_of_unit) for each_res_of_unit in unit_node.collection_set]
                units_res_nodes = node_collection.find({'_id': {'$in': units_res}})
                for each_res_node in units_res_nodes:
                    # print "\n\n each_res_node.relation_set----",each_res_node.relation_set
                    grel_dict = get_relation_value(each_res_node._id,"clone_of")
                    is_cursor = grel_dict.get("cursor",False)
                    if not is_cursor:
                        clone_of_obj = grel_dict.get("grel_node", None)
                        grel_id = grel_dict.get("grel_id")

                    # clone_of_obj,grel_node = get_relation_value(each_res_node._id,"clone_of")
                    if clone_of_obj:
                        units_res.append(clone_of_obj._id)
            except:
                unit_node = None

            if resource_type:
                if resource_type == "Pandora":
                    resource_type = "Pandora_video"
                if resource_type == "Quiz":
                    resource_type = "QuizItem"
                resource_gst = node_collection.one({'_type': "GSystemType", 'name': resource_type})
                res = node_collection.find(
                    {
                        'member_of': resource_gst._id,
                        'status': u"PUBLISHED",
                        '$or':[{'created_by': request.user.id},{'group_set': ObjectId(group_id)}],
                        '_id':{ '$nin': units_res }
                    }
                )
                for each in res:
                    if each not in list_resources:
                        list_resources.append(each)

                drawer_template_context = edit_drawer_widget("CourseUnits", group_id, unit_node, None, checked="collection_set", left_drawer_content=list_resources)
                drawer_template_context["widget_for"] = widget_for
                drawer_widget = render_to_string(
                    'ndf/drawer_widget.html',
                    drawer_template_context,
                    context_instance=RequestContext(request)
                )

            return HttpResponse(drawer_widget)
        else:
            error_message = "Resource Drawer: Either not an ajax call or not a POST request!!!"
            response_dict["message"] = error_message
            return HttpResponse(json.dumps(response_dict))

    except Exception as e:
        error_message = "Resource Drawer: " + str(e) + "!!!"
        response_dict["message"] = error_message
        return HttpResponse(json.dumps(response_dict))


@login_required
def save_resources(request, group_id):
    '''
    Accepts:
     * List of resources (i.e GSystem of Page, File, etc.)
     * CourseSubSection node _id

    Actions:
     * Sets the received resources in respective node's collection_set
    '''
    response_dict = {"success": False,"create_new_unit": True}
    if request.is_ajax() and request.method == "POST":
        try:
            group_id = ObjectId(group_id)
        except:
            group_name, group_id = get_group_name_id(group_id)

        list_of_res = json.loads(request.POST.get('list_of_res', ""))
        css_node_id = request.POST.get('css_node', "")
        unit_name = request.POST.get('unit_name', "")
        unit_name = unit_name.strip()
        unit_node_id = request.POST.get('unit_node_id', "")
        css_node = node_collection.one({"_id": ObjectId(css_node_id)})
        list_of_res_ids = [ObjectId(each_res) for each_res in list_of_res]

        try:
            cu_new = node_collection.one({'_id': ObjectId(unit_node_id)})
        except:
            cu_new = None
        if not cu_new:
            cu_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnit"})
            cu_new = node_collection.collection.GSystem()
            cu_new.member_of.append(cu_gst._id)
            # set name
            cu_new.name = unit_name.strip()
            cu_new.modified_by = int(request.user.id)
            cu_new.status = u"PUBLISHED"
            cu_new.created_by = int(request.user.id)
            cu_new.contributors.append(int(request.user.id))
            cu_new.group_set.append(group_id)
            cu_new.prior_node.append(css_node._id)
            cu_new.save(groupid=group_id)
            response_dict["create_new_unit"] = True
        node_collection.collection.update({'_id': cu_new._id}, {'$set': {'name': unit_name }}, upsert=False, multi=False)
	if cu_new._id not in css_node.collection_set:
            node_collection.collection.update({'_id': css_node._id}, {'$push': {'collection_set': cu_new._id }}, upsert=False, multi=False)
        # print "\n\n member_of_names_list----", cu_new.member_of_names_list, "list_of_res_ids", list_of_res_ids
        new_res_set = []
        if "CourseUnitEvent" in cu_new.member_of_names_list:
            list_of_res_nodes = node_collection.find({'_id': {'$in': list_of_res_ids}})

            for each_res_node in list_of_res_nodes:
                if each_res_node._id not in cu_new.collection_set:
                    new_gs = replicate_resource(request, each_res_node, group_id)
                    # if "QuizItem" in each_res_node.member_of_names_list:
                    #     node_collection.collection.update({'_id': cu_new._id}, {'$push': {'post_node':new_gs._id}},upsert=False,multi=False)
                    # else:
                    if new_gs:
                        new_res_set.append(new_gs._id)
                        node_collection.collection.update({'_id': new_gs._id}, {'$push': {'prior_node':cu_new._id}},upsert=False,multi=False)
        else:
            for each_res_node_course in list_of_res_ids:
                if each_res_node_course not in cu_new.collection_set:
                    new_res_set.append(each_res_node_course)

        for each_res_in_unit in new_res_set:
            if each_res_in_unit not in cu_new.collection_set:
                cu_new.collection_set.append(each_res_in_unit)
                cu_new.save()
        response_dict["success"] = True
        response_dict["cu_new_id"] = str(cu_new._id)

        return HttpResponse(json.dumps(response_dict))


@login_required
def create_edit_unit(request, group_id):
    '''
    Accepts:
     * ObjectId of unit node if exists
     * ObjectId of CourseSubSection node

    Actions:
     * Creates/Updates Unit node

    Returns:
     * success (i.e True/False)
    '''
    response_dict = {"success": False}
    if request.is_ajax() and request.method == "POST":
        try:
            group_id = ObjectId(group_id)
        except:
            group_name, group_id = get_group_name_id(group_id)
        group_obj = node_collection.one({'_id': ObjectId(group_id)})

        if "CourseEventGroup" in group_obj.member_of_names_list:
            cu_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnitEvent"})
        else:
            cu_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnit"})

        css_node_id = request.POST.get("css_node_id", '')
        unit_node_id = request.POST.get("unit_node_id", '')
        unit_name = request.POST.get("unit_name", '')
        css_node = node_collection.one({"_id": ObjectId(css_node_id)})
        try:
            cu_node = node_collection.one({'_id': ObjectId(unit_node_id)})
        except:
            cu_node = None
        if cu_node is None:
            cu_node = node_collection.collection.GSystem()
            cu_node.member_of.append(cu_gst._id)
            # set name
            cu_node.name = unit_name.strip()
            cu_node.modified_by = int(request.user.id)
            cu_node.created_by = int(request.user.id)
            cu_node.status = u"PUBLISHED"
            cu_node.contributors.append(int(request.user.id))
            cu_node.prior_node.append(css_node._id)
            cu_node.save(groupid=group_id)
            response_dict["unit_node_id"] = str(cu_node._id)
        node_collection.collection.update({'_id': cu_node._id}, {'$set': {'name': unit_name}}, upsert=False, multi=False)

        if cu_node._id not in css_node.collection_set:
            node_collection.collection.update({'_id': css_node._id}, {'$push': {'collection_set': cu_node._id}}, upsert=False, multi=False)
	    return HttpResponse(json.dumps(response_dict))



@login_required
def delete_course(request, group_id, node_id):
    del_stat = delete_item(node_id, "CourseUnit")
    if del_stat:
        return HttpResponseRedirect(reverse('course', kwargs={'group_id': ObjectId(group_id)}))


@login_required
def delete_from_course_structure(request, group_id):
    '''
    Accepts:
     * ObjectId of node that is to be deleted.
        It can be CourseSection/CourseSubSection/CourseUnit

    Actions:
     * Deletes the received node

    Returns:
     * success (i.e True/False)
    '''
    response_dict = {"success": False}
    del_stat = False
    if request.is_ajax() and request.method == "POST":
        try:
            group_id = ObjectId(group_id)
        except:
            group_name, group_id = get_group_name_id(group_id)
        group_obj = node_collection.one({'_id': ObjectId(group_id)})

        if "CourseEventGroup" in group_obj.member_of_names_list:
            ce = True
        else:
            ce = False
        oid = request.POST.get("oid", '')
        del_stat = delete_item(oid, ce)

        if del_stat:
            response_dict["success"] = True

        return HttpResponse(json.dumps(response_dict))


def delete_item(item, ce_flag):
    node_item = node_collection.one({'_id': ObjectId(item)})
    if ce_flag:
        cu_name = u"CourseUnit"
    else:
        cu_name = u"CourseUnitEvent"

    if cu_name not in node_item.member_of_names_list and node_item.collection_set:
        for each in node_item.collection_set:
            d_st = delete_item(each)

    del_status, del_status_msg = delete_node(
        node_id=node_item._id,
        deletion_type=0
    )

    return del_status


@login_required
def enroll_generic(request, group_id):
    response_dict = {"success": False}
    if request.is_ajax() and request.method == "POST":
        course_enrollment_status_at = node_collection.one({
            "_type": "AttributeType", "name": "course_enrollment_status"
        })
        node_id = request.POST.get('node_id', '')
        usr_id = request.POST.get('usr_id', '')
        usr_id = int(usr_id)
        auth_node = node_collection.one({'_type': "Author", 'created_by': usr_id})
        course_node = node_collection.one({'_id': ObjectId(node_id)})

        course_enrollment_status = {}

        if auth_node.attribute_set:
            for each in auth_node.attribute_set:
                if each and "course_enrollment_status" in each:
                    course_enrollment_status = each["course_enrollment_status"]

        str_course_id = str(course_node._id)
        if course_enrollment_status is not None:
            if str_course_id not in course_enrollment_status:
                course_enrollment_status.update({str_course_id: u"Approved"})

            at_node = create_gattribute(auth_node["_id"], course_enrollment_status_at, course_enrollment_status)
            response_dict['success'] = True
        return HttpResponse(json.dumps(response_dict))
    else:
        return HttpResponse(json.dumps(response_dict))


@login_required
def remove_resource_from_unit(request, group_id):
    '''
    Accepts:
     * ObjectId of node to be removed from collection_set.
     * ObjectId of unit_node.

    Actions:
     * Removed res_id from unit_node's collection_set

    Returns:
     * success (i.e True/False)
    '''
    response_dict = {"success": False}
    if request.is_ajax() and request.method == "POST":
        unit_node_id = request.POST.get("unit_node_id", '')
        res_id = request.POST.get("res_id", '')

        unit_node = node_collection.one({'_id': ObjectId(unit_node_id)})

        if unit_node.collection_set and res_id:
              node_collection.collection.update({'_id': unit_node._id}, {'$pull': {'collection_set': ObjectId(res_id)}}, upsert=False, multi=False)
	    
        response_dict["success"] = True
        return HttpResponse(json.dumps(response_dict))



@get_execution_time
def add_course_file(request, group_id):
    # this is context node getting from the url get request
    context_node_id = request.GET.get('context_node', '')

    context_node = node_collection.one({'_id': ObjectId(context_node_id)})
    if request.method == "POST":

        context_name = request.POST.get("context_name", "")
        css_node_id = request.POST.get("css_node_id", "")
        course_node = request.POST.get("course_node", "")
        unit_name = request.POST.get("unit_name_file", "")
        app_id = request.POST.get("app_id", "")
        app_set_id = request.POST.get("app_set_id", "")

        # i.e  if context_name is "Course"
        url_name = "/" + group_id + "/course/add_units/?css_node_id=" + \
            css_node_id + "&unit_node_id=" + context_node_id + "&course_node="+ course_node
        if app_id and app_set_id:
            url_name += "&app_id=" + app_id + "&app_set_id=" + app_set_id + ""
        if context_node_id:
            # set the unit node name
            node_collection.collection.update({'_id': ObjectId(context_node_id)}, {'$set': {'name': unit_name }}, upsert=False, multi=False)

        new_list = []
        file_uploaded = request.FILES.get("doc", "")
        # For checking the node is already available in gridfs or not
        if file_uploaded:
            fileobj,fs = save_file(file_uploaded,file_uploaded.name,request.user.id,group_id, "", "", username=unicode(request.user.username), access_policy="PUBLIC", count=0, first_object="", oid=True)
            file_node = node_collection.find_one({'_id': ObjectId(fileobj)})
            file_node.prior_node.append(context_node._id)
            file_node.status = u"PUBLISHED"
            file_node.save()
            context_node.collection_set.append(file_node._id)
            file_node.prior_node.append(context_node._id)
            file_node.save()
    
    return HttpResponseRedirect(url_name)


@login_required
def enroll_to_course(request, group_id):
    '''
    Accepts:
     * ObjectId of group.
     * Django user obj

    Actions:
     * Adds user to group

    Returns:
     * success (i.e True/False)
    '''
    response_dict = {"success": False}
    if request.is_ajax() and request.method == "POST":
        user_id = request.user.id
        group_obj = node_collection.one({'_id': ObjectId(group_id)})
        if user_id not in group_obj.author_set:
            group_obj.author_set.append(user_id)
        group_obj.save()
        response_dict["success"] = True
        return HttpResponse(json.dumps(response_dict))

def set_release_date_css(request, group_id):
	response_dict = {"success": False}
	try:
		if request.is_ajax() and request.method == "POST":
			css_date_dict = request.POST.get("css_date_dict", "")
			if css_date_dict:
				css_date_dict = json.loads(css_date_dict)
			# print "\n\ncss_date_dict",css_date_dict,"type--",type(css_date_dict)
			start_date_AT = node_collection.one({'_type': "AttributeType", 'name': "start_time"})
			for each_css in css_date_dict:
				if each_css['start_time']:
					start_date_val = datetime.datetime.strptime(each_css['start_time'], "%d/%m/%Y")
					create_gattribute(ObjectId(each_css['id']), start_date_AT, start_date_val)
			response_dict["success"] = True
			response_dict["message"] = "Release dates have been set successfully!"
	except Exception as e:
		response_dict["success"] = False
		response_dict["message"] = "Something went wrong! Please try after some time"
	return HttpResponse(json.dumps(response_dict))


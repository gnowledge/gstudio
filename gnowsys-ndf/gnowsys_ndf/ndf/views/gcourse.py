''' -- imports from python libraries -- '''
# from datetime import datetime
import datetime
import json
import ast
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
from django.core.cache import cache
from mongokit import IS
from mongokit import paginator
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT, GSTUDIO_TASK_TYPES
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.settings import GSTUDIO_SITE_NAME
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.group import *
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.templatetags.ndf_tags import edit_drawer_widget, get_disc_replies, get_all_replies,user_access_policy, get_relation_value, check_is_gstaff, get_attribute_value
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data, get_execution_time, delete_node, get_filter_querydict, update_notes_or_files_visited
from gnowsys_ndf.ndf.views.notify import set_notif_val
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value, get_group_name_id, get_course_completetion_status, replicate_resource
from gnowsys_ndf.ndf.views.ajax_views import *
from gnowsys_ndf.ndf.views.analytics_methods import *
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, create_task, delete_grelation, node_thread_access, get_group_join_status, delete_node, auto_enroll, add_to_author_set
from gnowsys_ndf.notification import models as notification
from gnowsys_ndf.settings import GSTUDIO_NOTE_CREATE_POINTS, GSTUDIO_QUIZ_CORRECT_POINTS, GSTUDIO_COMMENT_POINTS, GSTUDIO_FILE_UPLOAD_POINTS
from gnowsys_ndf.ndf.views.trash import trash_resource 
from gnowsys_ndf.ndf.views.translation import get_lang_node,get_trans_node_list,get_course_content_hierarchy, get_unit_hierarchy
from gnowsys_ndf.ndf.views.assessment_analytics import user_assessment_results


GST_COURSE = node_collection.one({'_type': "GSystemType", 'name': "Course"})
course_gst_name, course_gst_id = GSystemType.get_gst_name_id("Course")

# GST_ACOURSE = node_collection.one({'_type': "GSystemType", 'name': "Announced Course"})
# ann_course_gst_name, ann_course_gst_id = GSystemType.get_gst_name_id("Announced Course")

# gst_file = node_collection.one({'_type': "GSystemType", 'name': u"File"})
file_gst_name, file_gst_id = GSystemType.get_gst_name_id("File")

# gst_page = node_collection.one({'_type': "GSystemType", 'name': u"Page"})
page_gst_name, page_gst_id = GSystemType.get_gst_name_id("Page")
blog_page_gst_name, blog_page_gst_id = GSystemType.get_gst_name_id('Blog page')

has_banner_pic_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_banner_pic') })

app = GST_COURSE

@get_execution_time
def course(request, group_id, course_id=None):
    """
    * Renders a list of all 'courses' available within the database.
    """

    if request.user.is_anonymous():
        return HttpResponseRedirect(reverse('explore_courses', kwargs={}))

    group_obj = get_group_name_id(group_id, get_obj=True)
    group_id  = group_obj._id

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

    # course_ins = node_collection.find_one({'_type': "GSystemType", "name": "Course"})
    # if course_ins:
    #     course_id = str(course_ins._id)

    group_obj_post_node_list = group_obj.post_node
    # app_set = node_collection.one({'_type': "GSystemType", 'name': "Announced Course"})
    # app_set_id = app_set._id
    app_set_name, app_set_id = GSystemType.get_gst_name_id("Announced Course")

    # ce_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseEventGroup"})
    ce_gst_name, ce_gst_id = GSystemType.get_gst_name_id("CourseEventGroup")

    # Course search view
    # title = GST_COURSE.name
    # if GST_COURSE.name == "Course":
    title = "eCourses"

    query = {'member_of': ce_gst_id,'_id':{'$in': group_obj_post_node_list}}
    gstaff_access = False
    if request.user.id:
        # if user is admin then show all ce
        gstaff_access = check_is_gstaff(group_id,request.user)
        if not gstaff_access:
            query.update({'author_set':{'$ne':int(request.user.id)}})

        course_coll = node_collection.find({'member_of': course_gst_id,'group_set': ObjectId(group_id),'status':u"DRAFT"}).sort('last_update', -1)
        enr_ce_coll = node_collection.find({'member_of': ce_gst_id,'author_set': int(request.user.id),'_id':{'$in': group_obj_post_node_list}}).sort('last_update', -1)

        user_access =  user_access_policy(group_id ,request.user)
        if user_access == "allow":
            # show PRIVATE CourseEvent
            query.update({'group_type': {'$in':[u"PRIVATE",u"PUBLIC"]}})

    ce_coll = node_collection.find(query).sort('last_update', -1)
    # print "\n\n ce_coll",ce_coll.count()
    return render_to_response("ndf/gcourse.html",
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
    """Creates/Modifies details of base course group.
    """

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    logo_img_node = grel_id = fileobj = None
    # at_course_type = node_collection.one({'_type': 'AttributeType', 'name': 'nussd_course_type'})
    context_variables = {
                    'title': GST_COURSE.name,
                    'group_id': group_id,
                    'groupid': group_id
                }

    course_node = None
    if node_id:
        course_node = node_collection.one({'_id': ObjectId(node_id)})
        grel_dict = get_relation_value(node_id,'has_logo')
        is_cursor = grel_dict.get("cursor", False)
        if not is_cursor:
            logo_img_node = grel_dict.get("grel_node")
            grel_id = grel_dict.get("grel_id")

        # logo_img_node_grel_id = get_relation_value(node_id,'has_logo')
        # if logo_img_node_grel_id:
        #     logo_img_node = logo_img_node_grel_id[0]
        #     grel_id = logo_img_node_grel_id[1]

    # else:
    #     course_node = node_collection.collection.GSystem()

    available_nodes = node_collection.find({
            '_type': u'GSystem', 'member_of': ObjectId(course_gst_id),
            'group_set': ObjectId(group_id), 'status': {"$in": [u"DRAFT", u"PUBLISHED"]}
            },
            {'_id': 0, 'name': 1}
        )

    # for each in available_nodes:
    #     nodes_list.append(str((each.name).strip().lower()))
    nodes_list = [str((each.name).strip().lower()) for each in available_nodes]

    if request.method == "POST":
        # get_node_common_fields(request, course_node, group_id, GST_COURSE)
        group_access_type = request.POST.get('login-mode','PUBLIC')
        if isinstance(group_access_type, list):
            group_access_type = unicode(group_access_type[0])
        else:
            group_access_type = unicode(group_access_type)

        basecoursegroup_gst = node_collection.one({'_type': "GSystemType", 'name': u"BaseCourseGroup"})
        if not course_node:
            from gnowsys_ndf.ndf.views.group import CreateGroup

            base_course_group_name = request.POST.get('name','')
            group = CreateGroup(request)
            result = group.create_group(base_course_group_name)
            if result[0]:
                course_node = result[1]
                course_node.member_of = [basecoursegroup_gst._id]
                course_node.save()
                # course_node.save(is_changed=get_node_common_fields(request, course_node, group_id, GST_COURSE),groupid=group_id)
                # create_gattribute(course_node._id, at_course_type, u"General")
                # print "\n course_node ---- ", course_node
        if course_node:

            course_node.save(is_changed=get_node_common_fields(request, course_node, group_id, basecoursegroup_gst),groupid=group_id)
            course_node.group_type = group_access_type
            course_node.status = u'PUBLISHED'
            course_node.save()

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

        return HttpResponseRedirect(reverse('groupchange', kwargs={'group_id': course_node._id}))
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
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    course_structure_exists = False
    enrolled_status = False
    check_enroll_status = False
    title = GST_COURSE.name

    course_node = node_collection.one({"_id": ObjectId(_id)})

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
    return render_to_response("ndf/gcourse_detail.html",
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
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    if GSTUDIO_SITE_NAME is "TISS":
        tiss_site = True

    app = None
    if app_id is None:
        # app = node_collection.one({'_type': "GSystemType", 'name': app_name})
        app_gst_name, app_gst_id = GSystemType.get_gst_name_id(app_name)

        if app:
            app_id = str(app_gst_id)
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

    # univ = node_collection.one({'_type': "GSystemType", 'name': "University"}, {'_id': 1 })
    university_gst_name, university_gst_id = GSystemType.get_gst_name_id('University')
    university_cur = None

    if not mis_admin:
        mis_admin = node_collection.one(
            {'_type': "Group", 'name': "MIS_admin"},
            {'_id': 1, 'name': 1, 'group_admin': 1}
        )

    if tiss_site:
        hide_mis_meta_content = False
    if university_gst_id and mis_admin:
        university_cur = node_collection.find(
            {'member_of': university_gst_id, 'group_set': mis_admin._id},
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
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)

  app = None
  if app_id is None:
    # app = node_collection.one({'_type': "GSystemType", 'name': app_name})
    app_gst_name, app_gst_id = GSystemType.get_gst_name_id(app_name)

    if app_gst_id:
      app_id = str(app_gst_id)
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

    # cs_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSection"})
    cs_gst_name, cs_gst_id = GSystemType.get_gst_name_id('CourseSection')
    cs_gs = node_collection.collection.GSystem()
    cs_gs.member_of.append(cs_gst_id)
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
@get_execution_time
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
            # cs_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSectionEvent"})
            cs_gst_name, cs_gst_id = GSystemType.get_gst_name_id('CourseSectionEvent')

        else:
            # cs_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSection"})
            cs_gst_name, cs_gst_id = GSystemType.get_gst_name_id('CourseSection')

        cs_node_name = request.POST.get("cs_name", '')
        course_node_id = request.POST.get("course_node_id", '')
        cs_new = node_collection.collection.GSystem()
        cs_new.member_of.append(cs_gst_id)
        cs_new.name = cs_node_name
        cs_new.modified_by = int(request.user.id)
        cs_new.group_set.append(group_id)
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
@get_execution_time
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
            # css_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSubSectionEvent"})
            css_gst_name, css_gst_id = GSystemType.get_gst_name_id('CourseSubSectionEvent')
        else:
            # css_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSubSection"})
            css_gst_name, css_gst_id = GSystemType.get_gst_name_id('CourseSubSection')

        css_node_name = request.POST.get("css_name", '')
        cs_node_id = request.POST.get("cs_node_id", '')
        css_new = node_collection.collection.GSystem()
        css_new.member_of.append(css_gst_id)
        # set name
        css_new.name = css_node_name
        css_new.group_set.append(group_id)
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
@get_execution_time
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
@get_execution_time
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
        node_collection.collection.update({'_id': parent_node._id},
                {'$set': {'collection_set': collection_set_list }}, upsert=False, multi=False)
        parent_node.reload()
        response_dict["success"] = True
        return HttpResponse(json.dumps(response_dict))


@login_required
@get_execution_time
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
@get_execution_time
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
    # page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
    # page_gst_name, page_gst_id = GSystemType.get_gst_name_id('page')
    page_instances = node_collection.find({"type_of": page_gst_id})
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

    template = "ndf/gcourse_units.html"
    return render_to_response(template, variable)


@login_required
@get_execution_time
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
            try:
                unit_node = node_collection.one({"_id": ObjectId(unit_node_id)})
            except:
                unit_node = None
            if resource_type:
                if "Pandora" in resource_type :
                    resource_type = "Pandora_video"
                elif "Quiz" in resource_type:
                    resource_type = ["QuizItem", "QuizItemEvent"]
                    resource_gst_id = [GSystemType.get_gst_name_id(each_gst)[1] for each_gst in resource_type]
                elif "File" in resource_type:
                    resource_type = ["File", "Jsmol", "PoliceSquad", "OpenStoryTool", "TurtleBlocks", "BioMechanics"]
                    resource_gst_id = [GSystemType.get_gst_name_id(each_gst)[1] for each_gst in resource_type]
                else:
                    resource_gst_name, resource_gst_id = GSystemType.get_gst_name_id(resource_type)
                    # resource_gst = node_collection.one({'_type': "GSystemType", 'name': resource_type})
                    resource_gst_id = [resource_gst_id]
                res = node_collection.find(
                    {
                        'member_of': {'$in': resource_gst_id},
                        'status': u"PUBLISHED",
                        '$or':[{'group_set': ObjectId(group_id)},{'contributors': request.user.id}]
                    }
                ).sort('created_at', 1)
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
@get_execution_time
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
            # cu_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnit"})
            cu_gst_name, cu_gst_id = GSystemType.get_gst_name_id('CourseUnit')
            cu_new = node_collection.collection.GSystem()
            cu_new.member_of.append(cu_gst_id)
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
            for each_res in list_of_res_nodes:
                if group_id not in each_res.group_set:
                    new_gs = replicate_resource(request, each_res, group_id)
                    new_res_set.append(new_gs._id)
                else:
                    new_res_set.append(each_res._id)
        else:
            for each_res_node_course in list_of_res_ids:
                if each_res_node_course not in cu_new.collection_set:
                    new_res_set.append(each_res_node_course)

        for each_res_in_unit in new_res_set:
            if each_res_in_unit not in cu_new.collection_set:
                cu_new.collection_set.append(each_res_in_unit)
                cu_new.save()

        '''
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
        '''
        response_dict["success"] = True
        response_dict["cu_new_id"] = str(cu_new._id)
        return HttpResponse(json.dumps(response_dict))


@login_required
@get_execution_time
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
            # cu_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnitEvent"})
            cu_gst_name, cu_gst_id = GSystemType.get_gst_name_id('CourseUnitEvent')
        else:
            # cu_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnit"})
            cu_gst_name, cu_gst_id = GSystemType.get_gst_name_id('CourseUnit')

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
            cu_node.member_of.append(cu_gst_id)
            # set name
            cu_node.name = unit_name.strip()
            cu_node.modified_by = int(request.user.id)
            cu_node.created_by = int(request.user.id)
            cu_node.status = u"PUBLISHED"
            cu_node.contributors.append(int(request.user.id))
            cu_node.group_set.append(group_id)
            cu_node.prior_node.append(css_node._id)
            cu_node.save(groupid=group_id)
            response_dict["unit_node_id"] = str(cu_node._id)
        node_collection.collection.update({'_id': cu_node._id}, {'$set': {'name': unit_name}}, upsert=False, multi=False)

        if cu_node._id not in css_node.collection_set:
            node_collection.collection.update({'_id': css_node._id}, {'$push': {'collection_set': cu_node._id}}, upsert=False, multi=False)

        return HttpResponse(json.dumps(response_dict))


@login_required
@get_execution_time
def delete_course(request, group_id, node_id):
    del_stat = delete_item(node_id)
    if del_stat:
        return HttpResponseRedirect(reverse('course', kwargs={'group_id': ObjectId(group_id)}))


@login_required
@get_execution_time
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

@get_execution_time
def delete_item(item, ce_flag=False):
    node_item = node_collection.one({'_id': ObjectId(item)})
    if ce_flag:
        cu_name = u"CourseUnitEvent"
    else:
        cu_name = u"CourseUnit"
    if cu_name not in node_item.member_of_names_list and node_item.collection_set:
        for each in node_item.collection_set:
            d_st = delete_item(each)

    del_status, del_status_msg = delete_node(
        node_id=node_item._id,
        deletion_type=0
    )

    return del_status

@login_required
@get_execution_time
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
@get_execution_time
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



@login_required
@get_execution_time
def add_course_file(request, group_id):
    # this is context node getting from the url get request
    context_node_id = request.GET.get('context_node', '')

    context_node = node_collection.one({'_id': ObjectId(context_node_id)})
    if request.method == "POST":
        title = request.POST.get('context_name','')
        usrid = request.user.id
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
        from gnowsys_ndf.ndf.views.filehive import write_files

        fileobj_list = write_files(request, group_id)
        # fileobj_id = fileobj_list[0]['_id']
        # file_node = node_collection.one({'_id': ObjectId(fileobj_id) })

        for each_gs_file in fileobj_list:
            each_gs_file.status = u"PUBLISHED"
            each_gs_file.tags.append(u'raw@material')
            each_gs_file.prior_node.append(context_node._id)
            context_node.collection_set.append(each_gs_file._id)
            each_gs_file.save()
        context_node.save()

        # if file_uploaded:
        #     fileobj,fs = save_file(file_uploaded,file_uploaded.name,request.user.id,group_id, "", "", username=unicode(request.user.username), access_policy="PUBLIC", count=0, first_object="", oid=True)
        #     file_node = node_collection.find_one({'_id': ObjectId(fileobj)})
        #     file_node.prior_node.append(context_node._id)
        #     file_node.status = u"PUBLISHED"
        #     file_node.save()
        #     context_node.collection_set.append(file_node._id)
        #     file_node.save()
        # context_node.save()
    return HttpResponseRedirect(url_name)


@login_required
@get_execution_time
def unsubscribe_from_group(request, group_id):
    '''
    Accepts:
     * ObjectId of group.
     * Django user obj

    Actions:
     * Removes user from group

    Returns:
     * success (i.e True/False)
    '''
    response_dict = {"success": False}
    if request.is_ajax() and request.method == "POST":
        user_id = request.POST.get("user_id", "")
        remove_admin = eval(request.POST.get("asAdmin", 'False'))
        if not user_id:
            user_id = request.user.id
        user_id = int(user_id)
        group_obj = node_collection.one({'_id': ObjectId(group_id)})
        if remove_admin:
            if user_id in group_obj.group_admin:
                group_obj.group_admin.remove(user_id)
        else:
            if user_id in group_obj.author_set:
                group_obj.author_set.remove(user_id)
        group_obj.save()
        response_dict["success"] = True
        response_dict["member_count"] = len(group_obj.author_set)
        try:
            activ = "Subscription with " + group_obj.name +"."
            mail_content = "'This is to inform you that "+ \
            "you have been unsubscribed from group: '" + group_obj.name+ "'"
            user_obj = User.objects.get(id=user_id)
            set_notif_val(request, group_obj._id, mail_content, activ, user_obj)
        except Exception as e:
            print "\n Unable to send notifications ",e
        return HttpResponse(json.dumps(response_dict))

@login_required
@get_execution_time
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
    def _send_notif(userid, group_obj):
        activ = "Subscription with " + group_obj.name +"."
        mail_content = "'This is to inform you that "+ \
        "you have been subscribed to group: '" + group_obj.name+ "'"
        user_obj = User.objects.get(id=userid)
        set_notif_val(request, group_obj._id, mail_content, activ, user_obj)

    response_dict = {"success": False}
    if request.is_ajax() and request.method == "POST":
        try:
            user_id = request.POST.get("user_id", "")
            enroll_group_id = request.POST.get("enroll_group_id", None)
            add_admin = eval(request.POST.get("asAdmin", 'False'))
            is_module_enroll = eval(request.POST.get("module_enrollment", 'False'))
            if not user_id:
                user_id = request.user.id
            else:
                user_id = ast.literal_eval(user_id)
            if isinstance(user_id, list):
                user_id = map(int, user_id)
            else:
                user_id = int(user_id)
            if enroll_group_id:
                group_id = enroll_group_id

            if is_module_enroll:
                module_obj = Node.get_node_by_id(group_id)
                # print "\n Module: ", module_obj.name, " -- ", module_obj.member_of_names_list
                for each_group_id in module_obj.collection_set:
                    group_obj = add_to_author_set(each_group_id, user_id, add_admin)
            else:
                group_obj = add_to_author_set(group_id, user_id, add_admin)
                response_dict["member_count"] = len(group_obj.author_set)

            try:
                if isinstance(user_id, list):
                    for each_user_id in user_id:
                        _send_notif(each_user_id, group_obj)
                else:
                    _send_notif(user_id, group_obj)
            except Exception as e:
                print "\n Unable to send notifications ", e

        except Exception as er:
            print "\n ERROR Occurred in Enrollment!! ", er
            pass
        return HttpResponse(json.dumps(response_dict))

@login_required
@get_execution_time
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

@login_required
@get_execution_time
def course_summary(request, group_id):

    group_obj = get_group_name_id(group_id, get_obj=True)
    group_name = group_obj.name

    course_collection_data = get_collection(request, group_obj._id, group_obj._id)
    course_collection_data = json.loads(course_collection_data.content)

    variable = RequestContext(request, {
        'group_id': group_id, 'groupid': group_id, 'group_name': group_name,
        'course_collection_data': course_collection_data
    })

    template = "ndf/course_summary.html"
    return render_to_response(template, variable)

@get_execution_time
def course_resource_detail(request, group_id, course_sub_section, course_unit, resource_id):

    group_name, group_id = get_group_name_id(group_id)

    unit_node = node_collection.one({'_id': ObjectId(course_unit)})
    node_obj = node_collection.one({'_id': ObjectId(resource_id)})
    unit_obj_collection_set = unit_node.collection_set

    # all metadata reg position and next prev of resource

    resource_index = resource_next_id = resource_prev_id = None
    resource_count = len(unit_obj_collection_set)
    unit_resources_list_of_dict = node_collection.find({
                                    '_id': {'$in': unit_obj_collection_set}},
                                    {'name': 1, 'altnames': 1})

    resource_index = unit_obj_collection_set.index(node_obj._id)

    if (resource_index + 1) < resource_count:
        resource_next_id = unit_node.collection_set[resource_index + 1]

    if resource_index > 0:
        resource_prev_id = unit_node.collection_set[resource_index - 1]

    # --- END of all metadata reg position and next prev of resource ---

    node_obj.get_neighbourhood(node_obj.member_of)

    thread_node = allow_to_comment = None
    thread_node, allow_to_comment = node_thread_access(group_id, node_obj)

    variable = RequestContext(request, {
        'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
        'course_sub_section': course_sub_section, 'course_unit': course_unit,
        'allow_to_comment': allow_to_comment,
        'node': node_obj, 'unit_node': unit_node, 'resource_id': resource_id,
        'resource_index': resource_index, 'resource_next_id': resource_next_id,
        'resource_prev_id': resource_prev_id, 'resource_count': resource_count,
        'unit_resources_list_of_dict': unit_resources_list_of_dict
    })

    template = "ndf/unit_player.html"

    return render_to_response(template, variable)

@auto_enroll
@get_execution_time
def activity_player_detail(request, group_id, lesson_id, activity_id):

    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name

    parent_node_id = activity_id
    node_obj = node_collection.one({'_id': ObjectId(activity_id)})
    trans_node = get_lang_node(node_obj._id,request.LANGUAGE_CODE)
    if not trans_node:
        trans_node = node_obj
    lesson_node = node_collection.one({'_id': ObjectId(lesson_id)})
    lesson_obj_collection_set = lesson_node.collection_set
    group_obj_collection_set = group_obj.collection_set
    trans_lesson_node = get_lang_node(lesson_node._id,request.LANGUAGE_CODE)
    if trans_lesson_node:
        lesson_name = trans_lesson_node.name
    else:
        lesson_name  = lesson_node.name 
    # all metadata reg position and next prev of resource
    translation_obj = node_obj.get_relation('translation_of')

    resource_index = resource_next_id = resource_prev_id = None
    lesson_index = lesson_next_id = lesson_prev_id = None
    resource_count = len(lesson_obj_collection_set)
    lesson_count = len(group_obj.collection_set)
    unit_resources_list_of_dict = node_collection.find({
                                    '_id': {'$in': lesson_obj_collection_set}},
                                    {'name': 1, 'altnames': 1,'_id':1})
    act_list = []
    trans_act_list = get_trans_node_list(lesson_node.collection_set,request.LANGUAGE_CODE)
    
    lesson_index = group_obj_collection_set.index(lesson_node._id) 

    resource_index = lesson_obj_collection_set.index(node_obj._id)
 
    if (resource_index + 1) < resource_count:
        resource_next_id = lesson_node.collection_set[resource_index + 1]

    if resource_index > 0:
        resource_prev_id = lesson_node.collection_set[resource_index - 1]

    if (lesson_index + 1) < lesson_count:
        lesson_next_id = group_obj.collection_set[lesson_index + 1]

    if lesson_index > 0:
        lesson_prev_id = group_obj.collection_set[lesson_index - 1]

    # --- END of all metadata reg position and next prev of resource ---
    prev_lesson_obj = next_lesson_obj  = None
    if lesson_next_id:
        next_lesson_obj = Node.get_node_by_id(lesson_next_id)
    if lesson_prev_id:
        prev_lesson_obj = Node.get_node_by_id(lesson_prev_id)
    node_obj.get_neighbourhood(node_obj.member_of)

    thread_node = allow_to_comment = None
    thread_node, allow_to_comment = node_thread_access(group_id, node_obj)

    context_variables = {
        'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
        'allow_to_comment': True,
        'node': node_obj, 'lesson_node': lesson_node, 'activityid': ObjectId(activity_id),
        'resource_index': resource_index, 'resource_next_id': resource_next_id,
        'resource_prev_id': resource_prev_id, 'resource_count': resource_count,

        'lesson_index': lesson_index,'lesson_count': lesson_count,
        'translation': translation_obj, 'unit_resources_list_of_dict': unit_resources_list_of_dict,
        'trans_node':trans_node,
        'act_list':trans_act_list,
        'trans_lesson_name':lesson_name,
        'no_footer': True
    }
    
    
    if prev_lesson_obj and prev_lesson_obj.collection_set:
        context_variables.update({ 'lesson_act_prev_id': prev_lesson_obj.collection_set[0],'prev_lesson_id':prev_lesson_obj._id })
    if next_lesson_obj and next_lesson_obj.collection_set:
        context_variables.update({ 'next_lesson_id':next_lesson_obj._id,'lesson_next_act_id': next_lesson_obj.collection_set[0] })
    
    
    if request.user.is_authenticated():
        active_user_ids_list = [request.user.id]
        if GSTUDIO_BUDDY_LOGIN:
            active_user_ids_list += Buddy.get_buddy_userids_list_within_datetime(request.user.id, datetime.datetime.now())
        # removing redundancy of user ids:
        active_user_ids_list = dict.fromkeys(active_user_ids_list).keys()
        counter_objs_cur = Counter.get_counter_objs_cur(active_user_ids_list, group_id)
        for each_counter_obj in counter_objs_cur:
            # print "\n OLD updated counter_obj: ", each_counter_obj['visited_nodes']
            if str(activity_id) in each_counter_obj['visited_nodes']:
                each_counter_obj['visited_nodes'][str(activity_id)] = each_counter_obj['visited_nodes'][str(activity_id)] + 1
            else:
                each_counter_obj['visited_nodes'].update({str(activity_id): 1})

            each_counter_obj.last_update = datetime.datetime.now()
            each_counter_obj.save()
            # print "\n updated counter_obj: ", each_counter_obj['visited_nodes']
        # if 'tab_name' in group_obj.project_config and group_obj.project_config['tab_name'].lower() == "questions":
    template = "ndf/activity_player.html"
    return render_to_response(template,
                                context_variables,
                                context_instance = RequestContext(request)
    )

# Following View Not in Use
@get_execution_time
def course_dashboard(request, group_id):

    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name

    allow_to_join = get_group_join_status(group_obj)
    result_status = course_complete_percentage = None
    total_count = completed_count = None
    if request.user.is_authenticated():
        result_status = get_course_completetion_status(group_obj, request.user.id)
        if result_status:
            if "course_complete_percentage" in result_status:
                course_complete_percentage = result_status['course_complete_percentage']
            if "total_count" in result_status:
                total_count = result_status['total_count']
            if "completed_count" in result_status:
                completed_count = result_status['completed_count']

    template = 'ndf/gcourse_event_group.html'
    if 'BaseCourseGroup' in group_obj.member_of_names_list:
        template = 'ndf/basecourse_group.html'


    context_variables = RequestContext(request, {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            'group_obj': group_obj, 'title': 'dashboard', 'allow_to_join': allow_to_join,
            "course_complete_percentage": course_complete_percentage,
            "total_count":total_count, "completed_count":completed_count,
        })
    return render_to_response(template, context_variables)

@get_execution_time
def _get_current_and_old_display_pics(group_obj):
    banner_pic_obj = None
    old_profile_pics = []
    for each in group_obj.relation_set:
        if "has_banner_pic" in each:
            banner_pic_obj = node_collection.one(
                {'_type': {'$in': ["GSystem", "File"]}, '_id': each["has_banner_pic"]}
            )
            break

    all_old_prof_pics = triple_collection.find({'_type': "GRelation", "subject": group_obj._id, 'relation_type': has_banner_pic_rt._id, 'status': u"DELETED"})
    if all_old_prof_pics:
        for each_grel in all_old_prof_pics:
            n = node_collection.one({'_id': ObjectId(each_grel.right_subject)})
            if n not in old_profile_pics:
                old_profile_pics.append(n)

    return banner_pic_obj, old_profile_pics

# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::COURSE-PLAYER VIEWS::::::::::::::::::::::
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# :::::::::::::::::::::::::::::::::TAB VIEWS BEGINS::::::::::::::::::::::
@get_execution_time
def course_content(request, group_id):

    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name
    allow_to_join = get_group_join_status(group_obj)
    template = 'ndf/gcourse_event_group.html'
    unit_structure =  get_course_content_hierarchy(group_obj,request.LANGUAGE_CODE)
    visited_nodes = []
    if 'BaseCourseGroup' in group_obj.member_of_names_list:
        template = 'ndf/basecourse_group.html'
    if 'base_unit' in group_obj.member_of_names_list:
        template = 'ndf/lms.html'
    if 'announced_unit' in group_obj.member_of_names_list or 'Group' in group_obj.member_of_names_list or 'Author' in group_obj.member_of_names_list and 'base_unit' not in group_obj.member_of_names_list:
        template = 'ndf/lms.html'
    banner_pic_obj,old_profile_pics = _get_current_and_old_display_pics(group_obj)
    if request.user.is_authenticated():
        counter_obj = Counter.get_counter_obj(request.user.id, ObjectId(group_id))
        if counter_obj:
            # visited_nodes = map(str,counter_obj['visited_nodes'].keys())
            visited_nodes = counter_obj['visited_nodes']
    context_variables = RequestContext(request, {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            'group_obj': group_obj,'node': group_obj, 'title': 'course content',
            'allow_to_join': allow_to_join,
            'old_profile_pics':old_profile_pics, "prof_pic_obj": banner_pic_obj,
            'unit_structure': json.dumps(unit_structure,cls=NodeJSONEncoder),
            'visited_nodes': json.dumps(visited_nodes)
            })
    return render_to_response(template, context_variables)

@get_execution_time
def course_notebook(request, group_id, node_id=None, tab="my-notes"):
    group_obj = get_group_name_id(group_id, get_obj=True)
    group_id = group_obj._id
    group_name = group_obj.name

    all_blogs = blog_pages = user_blogs = user_id = None
    allow_to_comment = notebook_obj = None
    create_flag = eval(request.GET.get('create', 'False'))

    template = 'ndf/gcourse_event_group.html'
    # if 'base_unit' in group_obj.member_of_names_list:
    #     template = 'ndf/gevent_base.html'

    if 'announced_unit' in group_obj.member_of_names_list or 'Group' in group_obj.member_of_names_list or 'base_unit'  in group_obj.member_of_names_list or 'Author' in group_obj.member_of_names_list:
        template = 'ndf/lms.html'

    # page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
    # blogpage_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"})
    # blog_page_gst_name, blog_page_gst_id = GSystemType.get_gst_name_id('Blog page')

    thread_node = None
    banner_pic_obj,old_profile_pics = _get_current_and_old_display_pics(group_obj)
    '''
    banner_pic_obj = None
    old_profile_pics = []
    if not banner_pic_obj:
        for each in group_obj.relation_set:
            if "has_banner_pic" in each:
                banner_pic_obj = node_collection.one(
                    {'_type': {'$in': [u"GSystem", u"File"]}, '_id': each["has_banner_pic"][0]}
                )
                break

    has_banner_pic_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_banner_pic') })
    all_old_prof_pics = triple_collection.find({'_type': "GRelation", "subject": group_obj._id, 'relation_type': has_banner_pic_rt._id, 'status': u"DELETED"})
    if all_old_prof_pics:
        for each_grel in all_old_prof_pics:
            n = node_collection.one({'_id': ObjectId(each_grel.right_subject)})
            if n not in old_profile_pics:
                old_profile_pics.append(n)
    '''
    allow_to_join = get_group_join_status(group_obj)
    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            'group_obj': group_obj, 'title': 'notebook', 'allow_to_join': allow_to_join,
            'old_profile_pics':old_profile_pics, "prof_pic_obj": banner_pic_obj,
            'create_flag': create_flag
            }

    if request.user.is_authenticated():
        user_id = request.user.id

    blog_pages = node_collection.find({'member_of':page_gst_id, 'type_of': blog_page_gst_id,
     'group_set': group_obj._id, 'created_by': {'$ne': user_id}}).sort('created_at', -1)
    # print "\n -- blog --",blog_pages.count()

    if user_id:
        user_blogs = node_collection.find({'member_of':page_gst_id, 'type_of': blog_page_gst_id,
         'group_set': group_obj._id, 'created_by': user_id }).sort('created_at', -1)
        # print "\n -- user --",user_blogs.count()
    tab = 'all-notes'
    if node_id:
        notebook_obj = node_collection.one({'_id': ObjectId(node_id)})
        thread_node, allow_to_comment = node_thread_access(group_id, notebook_obj)
        if user_id:
            if user_id == notebook_obj.created_by:
                tab = 'my-notes'
            if user_id != notebook_obj.created_by:
                tab = 'all-notes'
            #updating counters collection
            # update_notes_or_files_visited(request.user.id, ObjectId(group_id),ObjectId(node_id),False,True)
            if request.user.is_authenticated():
                Counter.add_visit_count(resource_obj_or_id=notebook_obj._id.__str__(),
                                        current_group_id=group_id.__str__(),
                                        loggedin_userid=request.user.id)


    else:
        if user_blogs and user_blogs.count():
            notebook_obj = user_blogs[0]
            tab = 'my-notes'
            thread_node, allow_to_comment = node_thread_access(group_id, notebook_obj)
        elif blog_pages and blog_pages.count():
            notebook_obj = blog_pages[0]
            tab = 'all-notes'
            thread_node, allow_to_comment = node_thread_access(group_id, notebook_obj)
        else:
            tab = 'all-notes'

        if notebook_obj and not create_flag:
            # return HttpResponseRedirect(reverse('course_notebook_tab_note', 
                # kwargs={'group_id': group_id, "node_id": notebook_obj.pk, 'tab': tab}))
            return HttpResponseRedirect(reverse('course_notebook_note', 
                kwargs={'group_id': group_id, "node_id": notebook_obj.pk}))

    context_variables.update({'allow_to_comment': allow_to_comment})
    context_variables.update({'blog_pages': blog_pages})
    context_variables.update({'user_blogs': user_blogs})
    context_variables.update({'tab': tab})
    context_variables.update({'node': notebook_obj})
    return render_to_response(template,
                                context_variables,
                                context_instance = RequestContext(request)
    )

@get_execution_time
def course_raw_material(request, group_id, node_id=None,page_no=1):
    from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP

    coll_file_cur = []
    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    allow_to_upload = False
    group_name  = group_obj.name
    gstaff_users = []
    all_superusers = User.objects.filter(is_superuser=True)
    all_superusers_ids = all_superusers.values_list('id',flat=True)
    gstaff_users.extend(group_obj.group_admin)
    gstaff_users.append(group_obj.created_by)
    gstaff_users.extend(all_superusers_ids)
    allow_to_join = None
    files_cur = None
    allow_to_join = get_group_join_status(group_obj)
    banner_pic_obj,old_profile_pics = _get_current_and_old_display_pics(group_obj)
    '''
    banner_pic_obj = None
    old_profile_pics = []
    if not banner_pic_obj:
        for each in group_obj.relation_set:
            if "has_banner_pic" in each:
                banner_pic_obj = node_collection.one(
                    {'_type': {'$in': ["GSystem", "File"]}, '_id': each["has_banner_pic"][0]}
                )
                break

    has_banner_pic_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_banner_pic') })
    all_old_prof_pics = triple_collection.find({'_type': "GRelation", "subject": group_obj._id, 'relation_type': has_banner_pic_rt._id, 'status': u"DELETED"})
    if all_old_prof_pics:
        for each_grel in all_old_prof_pics:
            n = node_collection.one({'_id': ObjectId(each_grel.right_subject)})
            if n not in old_profile_pics:
                old_profile_pics.append(n)
    '''
    asset_gst_name, asset_gst_id = GSystemType.get_gst_name_id("Asset")
    asset_nodes = node_collection.find({'member_of': {'$in': [asset_gst_id]},
            'group_set': {'$all': [ObjectId(group_id)]},'tags': "raw@material"}).sort('last_update', -1)
    
    # from collections import defaultdict
    # asset_thumbnail = defaultdict(list)
    
    # data_list = []
    # for each in asset_nodes:
    #     grel_asstcontent = get_relation_value (each.pk, 'has_assetcontent')
    #     if grel_asstcontent['grel_id']:
    #         for each_rel in grel_asstcontent['grel_node']:
    #             if each_rel['if_file']['original']['relurl']:
    #                 asset_thumbnail[each._id].append(each_rel['if_file']['original']['relurl'])
    #             data_list.append(asset_thumbnail)
    

    for each in asset_nodes:
        each.get_neighbourhood(each.member_of)

    asset_nodes.rewind()
    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            'group_obj': group_obj, 'title': 'raw material',
            'old_profile_pics':old_profile_pics, "prof_pic_obj": banner_pic_obj,
            'asset_nodes':asset_nodes,
        }
    if node_id:
        file_obj = node_collection.one({'_id': ObjectId(node_id)})
        thread_node = None
        allow_to_comment = None
        thread_node, allow_to_comment = node_thread_access(group_id, file_obj)
        context_variables.update({'file_obj': file_obj, 'allow_to_comment':allow_to_comment})
        #updating counters collection
        # update_notes_or_files_visited(request.user.id, ObjectId(group_id),ObjectId(node_id),True,False)
        if request.user.is_authenticated():
            Counter.add_visit_count(resource_obj_or_id=file_obj._id.__str__(),
                                    current_group_id=group_id.__str__(),
                                    loggedin_userid=request.user.id)

    else:
        type_of_files = file_gst_id
        if "announced_unit" in group_obj.member_of_names_list:
            asset_gst_name, asset_gst_id = GSystemType.get_gst_name_id("Asset")
            type_of_files = asset_gst_id

        files_cur = node_collection.find({
                                        '_type': {'$in': ["File", "GSystem"]},
                                        '$or': [
                                                {'member_of': type_of_files},
                                                {
                                                    'collection_set': {'$exists': "true",'$not': {'$size': 0} },
                                                    'member_of': page_gst_id,
                                                }
                                            ],
                                        'group_set': {'$all': [ObjectId(group_id)]},
                                        'tags': "raw@material"
                        },
                        {
                            'name': 1,
                            'collection_set':1,
                            '_id': 1,
                            'member_of': 1,
                            'if_file':1
                        }).sort("last_update", -1)

    raw_material_page_info = paginator.Paginator(files_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)
    # context_variables.update({'coll_file_cur':files_cur})

    # print "\n\n\n\n **course_raw_page_info",course_raw_page_info
    gstaff_access = check_is_gstaff(group_id,request.user)

    # if request.user.id in gstaff_users:
    #     allow_to_upload = True
    if gstaff_access:
        allow_to_upload = True
    template = 'ndf/gcourse_event_group.html'
    
    if "announced_unit" in group_obj.member_of_names_list or "Group" in group_obj.member_of_names_list or "base_unit" in group_obj.member_of_names_list or 'Author' in group_obj.member_of_names_list :
        template = 'ndf/lms.html'
        # assets_page_info = paginator.Paginator(asset_nodes, page_no, GSTUDIO_NO_OF_OBJS_PP)
        # context_variables.update({'assets_page_info':assets_page_info})
    if 'BaseCourseGroup' in group_obj.member_of_names_list:
        template = 'ndf/basecourse_group.html'
    
    

    context_variables.update({'title':'raw material' ,'files_cur': files_cur,'raw_material_page_info':raw_material_page_info ,'allow_to_upload': allow_to_upload,'allow_to_join': allow_to_join})
    return render_to_response(template,
                                context_variables,
                                context_instance = RequestContext(request)
    )

@get_execution_time
def course_gallery(request, group_id,node_id=None,page_no=1):
    from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP

    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name
    gstaff_users = []
    query = {}
    allow_to_upload = True
    allow_to_join = query_dict = None
    allow_to_join = get_group_join_status(group_obj)
    banner_pic_obj,old_profile_pics = _get_current_and_old_display_pics(group_obj)

    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            'group_obj': group_obj, 'title': 'gallery', 'allow_to_upload':allow_to_upload,
            'allow_to_join':allow_to_join,
            'old_profile_pics':old_profile_pics, "prof_pic_obj": banner_pic_obj
        }

    if node_id:
        file_obj = node_collection.one({'_id': ObjectId(node_id)})
        thread_node = None
        allow_to_comment = None
        thread_node, allow_to_comment = node_thread_access(group_id, file_obj)
        context_variables.update({'file_obj': file_obj, 'allow_to_comment':allow_to_comment})
        # updating counters collection:
        # update_notes_or_files_visited(request.user.id, ObjectId(group_id),ObjectId(node_id),True,False)
        if request.user.is_authenticated():
            Counter.add_visit_count(resource_obj_or_id=file_obj._id.__str__(),
                                    current_group_id=group_id.__str__(),
                                    loggedin_userid=request.user.id)

    else:
        all_superusers = User.objects.filter(is_superuser=True)
        all_superusers_ids = all_superusers.values_list('id',flat=True)
        gstaff_users.extend(group_obj.group_admin)
        gstaff_users.append(group_obj.created_by)
        gstaff_users.extend(all_superusers_ids)

        files_cur = node_collection.find({
                                        'created_by': {'$nin': gstaff_users},
                                        '_type': {'$in':["File","GSystem"]},
                                        'group_set': {'$all': [ObjectId(group_id)]},
                                        'relation_set.clone_of': {'$exists': False},
                                        '$or': [
                                                {'member_of': file_gst_id},
                                                {
                                                    'collection_set': {'$exists': True,'$not': {'$size': 0} },
                                                    'member_of': page_gst_id,
                                                },
                                            ],
                                            },
                                        {
                                            'name': 1,
                                            'collection_set':1,
                                            '_id': 1,
                                            'member_of': 1,
                                            'if_file':1,
                                        }).sort("last_update", -1)
        context_variables.update({'files_cur': files_cur})
        gallery_page_info = paginator.Paginator(files_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)
        context_variables.update({'gallery_page_info':gallery_page_info,'coll_cur':files_cur})
    
    asset_gst_name, asset_gst_id = GSystemType.get_gst_name_id("Asset")
    
    asset_nodes = node_collection.find({'member_of': {'$in': [asset_gst_id]},
            'group_set': {'$all': [ObjectId(group_id)]},'tags': "asset@gallery"}).sort('last_update', -1)
    
    template = 'ndf/gcourse_event_group.html'
    
    if "announced_unit" in group_obj.member_of_names_list or "Group" in group_obj.member_of_names_list or 'Author' in group_obj.member_of_names_list or 'base_unit' in group_obj.member_of_names_list:
        template = 'ndf/lms.html'
        # assets_page_info = paginator.Paginator(asset_nodes, page_no, GSTUDIO_NO_OF_OBJS_PP)
        # context_variables.update({'assets_page_info':assets_page_info})
    
    context_variables.update({'asset_nodes': asset_nodes})

    return render_to_response(template,
                                context_variables,
                                context_instance = RequestContext(request)
    )

@get_execution_time
def course_about(request, group_id):
    group_obj   = Group.get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name

    weeks_count = 0
    curr_date_time = datetime.datetime.now().date()
    start_date = get_attribute_value(group_obj._id,"start_time")
    last_date = get_attribute_value(group_obj._id,"end_time")

    allow_to_join = get_group_join_status(group_obj)

    if start_date and last_date:
      start_date = start_date.date()
      last_date = last_date.date()
      from datetime import  timedelta
      start_day = (start_date - timedelta(days=start_date.weekday()))
      end_day = (last_date - timedelta(days=last_date.weekday()))

      # print 'Weeks:', (end_day - start_day).days / 7
      weeks_count = (end_day - start_day).days / 7
    
    show_analytics_notifications = True
    template = 'ndf/gcourse_event_group.html'
    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            'group_obj': group_obj, 'title': 'about', 'allow_to_join': allow_to_join,
            'weeks_count': weeks_count
        }
    if 'BaseCourseGroup' in group_obj.member_of_names_list:
        template = 'ndf/basecourse_group.html'
        show_analytics_notifications = False
    if 'base_unit' in group_obj.member_of_names_list :
        # template = 'ndf/gevent_base.html'
        template = 'ndf/lms.html'
        show_analytics_notifications = False
        educationalsubject = get_attribute_value(group_obj._id,"educationalsubject")
        educationallevel = get_attribute_value(group_obj._id,"educationallevel")
        context_variables.update({'educationalsubject_val': educationalsubject,
            "educationallevel_val": educationallevel})
    
    if 'announced_unit' in group_obj.member_of_names_list or 'Group' in group_obj.member_of_names_list or 'Author' in group_obj.member_of_names_list and 'base_unit' not in group_obj.member_of_names_list:
        template = 'ndf/lms.html'
    
    banner_pic_obj,old_profile_pics = _get_current_and_old_display_pics(group_obj)
    context_variables.update({'old_profile_pics':old_profile_pics,
                        "prof_pic_obj": banner_pic_obj,
                        'show_analytics_notifications':show_analytics_notifications})
    return render_to_response(template, context_variables,
            context_instance=RequestContext(request))

# :::::::::::::::::::::::::::::::::TAB VIEWS ENDS::::::::::::::::::::::

@get_execution_time
def course_gallerymodal(request, group_id, node_id):
    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name
    # node_id = request.GET.get("node_id", "")
    node_obj = node_collection.one({'_id': ObjectId(node_id)})
    # print "\n\n node_obj == ", node_obj.name
    thread_node = None
    allow_to_comment = None
    thread_node, allow_to_comment = node_thread_access(group_id, node_obj)
    allow_to_join = get_group_join_status(group_obj)

    template = 'ndf/ggallerymodal.html'

    context_variables = RequestContext(request, {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            'node': node_obj, 'title': 'course_gallerymodall',
            'allow_to_comment': allow_to_comment,
            'thread_node': thread_node,
            'allow_to_join': allow_to_join

        })
    return render_to_response(template, context_variables)

@get_execution_time
def course_note_page(request, group_id):

    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name

    node_id = request.GET.get("node_id", "")
    node_obj = node_collection.one({'_id': ObjectId(node_id)})

    thread_node = None
    allow_to_comment = None
    allow_to_join = get_group_join_status(group_obj)

    thread_node, allow_to_comment = node_thread_access(group_id, node_obj)
    template = 'ndf/note_page.html'

    context_variables = RequestContext(request, {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            'node': node_obj, 'title': 'course_gallerymodall',
            'allow_to_comment': allow_to_comment,
            'thread_node': thread_node, 'allow_to_join': allow_to_join,

        })
    return render_to_response(template, context_variables)

@login_required
@get_execution_time
def inline_edit_res(request, group_id):
    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name
    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            }
    template = None
    if request.method == "POST":
        node_id = request.POST.get("node_id", "")
        node_obj = node_collection.one({'_id': ObjectId(node_id)})
        type_of_req = request.POST.get("type", "")
        if type_of_req == "edit":
            node_content = request.POST.get("node_content", node_obj.content)
            template = 'ndf/html_editor.html'
            context_variables['var_name'] = "content_org"
            context_variables['var_value'] = node_content
            context_variables['node_id'] = node_obj._id
            context_variables['ckeditor_toolbar'] ="GeneralToolbar"
            context_variables['node'] = node_obj
        elif type_of_req == "save":
            content_val = request.POST.get("content_val", "")
            custom_redirect = request.POST.get("custom_redirect", "")
            node_obj.content = content_val
            node_obj.save()
            template = 'ndf/node_ajax_content.html'
            context_variables['no_discussion'] = True
            context_variables['node'] = node_obj
    return render_to_response(template, context_variables, context_instance = RequestContext(request))

@get_execution_time
def course_filters(request, group_id):

    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name

    gstaff_users = []
    all_superusers = User.objects.filter(is_superuser=True)
    all_superusers_ids = all_superusers.values_list('id',flat=True)
    gstaff_users.extend(group_obj.group_admin)
    gstaff_users.append(group_obj.created_by)
    gstaff_users.extend(all_superusers_ids)

    notebook_filter = False
    no_url_flag = True
    detail_urlname = None

    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
        }

    filter_applied = request.GET.get("filter_applied", "")
    filter_dict = request.GET.get("filter_dict", "")
    title = request.GET.get("title", "")
    if filter_applied:
        filter_applied = eval(filter_applied)
    # query = {'group_set': group_id, 'relation_set.clone_of':{'$exists': False}}
    # Exclude files that are part of course content.
    # Earlier 'has_clone' RT was used to identify such resources,
    # which was updated as per PR#1496 https://github.com/gnowledge/gstudio/pull/1496
    query = {'group_set': group_id, 'origin.fork_of':{'$exists': False}}

    template = 'ndf/file_list_tab.html'

    if title.lower() == "gallery" or title.lower() == "raw material":
        # file_gst = node_collection.one({'_type': 'GSystemType', 'name': u'File'})
        # query.update({'_type': "File"})
        query.update({'member_of': gst_file_id})

    elif title.lower() == "notebook":
        # page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
        # blogpage_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"})
        query.update({'member_of':page_gst_id, 'type_of': blog_page_gst_id})
        notebook_filter = True
        no_url_flag = False
        # detail_urlname = "course_notebook_tab_note"
        detail_urlname = "course_notebook_note"
    elif title.lower() == "notebook_lms":
        # page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
        # blogpage_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"})
        query.update({'member_of':page_gst_id, 'type_of': blog_page_gst_id})
        notebook_filter = True
        no_url_flag = False
        # detail_urlname = "course_notebook_tab_note"
        detail_urlname = "course_notebook_note"
        template = "ndf/widget_card_list.html"
    if title.lower() == "gallery":
        query.update({'created_by': {'$nin': gstaff_users}})
        no_url_flag = False
        detail_urlname = "course_gallery_detail"
    elif title.lower() == "raw material":
        query.update({'created_by': {'$in': gstaff_users}})
        no_url_flag = False
        detail_urlname = "course_raw_material_detail"
    elif title.lower() == "raw_material_lms":
        asset_gst_name, asset_gst_id = GSystemType.get_gst_name_id("Asset")
        query.update({'member_of':asset_gst_id,'tags':'raw@material' })
        no_url_flag = False
        detail_urlname = "asset_detail"
        template = "ndf/widget_card_list.html"
    elif title.lower() == "gallery_lms":
        asset_gst_name, asset_gst_id = GSystemType.get_gst_name_id("Asset")
        query.update({'member_of':asset_gst_id,'tags':'asset@gallery' })
        no_url_flag = False
        detail_urlname = "asset_detail"
        template = "ndf/widget_card_list.html"
    elif title.lower() == "assets_lms":
        asset_gst_name, asset_gst_id = GSystemType.get_gst_name_id("Asset")
        query.update({'member_of':asset_gst_id,'tags':'asset@asset' })
        no_url_flag = False
        detail_urlname = "asset_detail"
        template = "ndf/widget_card_list.html"
    if filter_applied:
        filter_dict = json.loads(filter_dict)
        query_dict = get_filter_querydict(filter_dict)
        if query_dict:
            for each_dict in query_dict:
                query.update(each_dict)
        elif title.lower() == "notebook":
            return HttpResponse("reload")

    # print "\n\n query === ", title, "\n\n---  \n",query
    files_cur = node_collection.find(query).sort('created_at', -1)
    # print "\n\n Total files: ", files_cur.count()
    context_variables.update({'files_cur': files_cur,"resource_type": files_cur,
                              "no_footer":True, "no_description":True, "no_url":no_url_flag,
                              "notebook_filter": notebook_filter, "detail_urlname": detail_urlname})
    return render_to_response(template,
                                context_variables,
                                context_instance = RequestContext(request)
    )


# :::::::::::::::::::::::::::::::::REPORT VIEWS BEGINS::::::::::::::::::::::

# @login_required # commented on-purpose for generating user-csvs
@get_execution_time
def course_analytics(request, group_id, user_id, render_template=False, get_result_dict=False, **kwargs):
    # set get_result_dict=True to get only raw data in dict format,
    # without being redirected to template. So that this method can
    # use to get dict result data in shell or for any command.
    # this will omit data from request.
    # if request and not get_result_dict:
    #     cache_key = u'course_analytics' + unicode(group_id) + "_" + unicode(user_id)
    #     cache_result = cache.get(cache_key)
    #     if cache_result:
    #         return render_to_response("ndf/user_course_analytics.html",
    #                                 cache_result,
    #                                 context_instance = RequestContext(request)
    #                             )

    # possible kwargs keys:
    # 
    # `get_counter_obj_in_result`  # flag named such to avoid confusion with builtin Counter method
    # - default value is False (i.e: get_counter_obj_in_result=False)
    # - By setting this to True, result dict will have counter object as a value for key, `counter_obj`
    # 
    # `assessment_and_quiz_data`
    analytics_data = {'user_id': user_id}
    analytics_data.update({
                'correct_attempted_quizitems' : 0,
                'unattempted_quizitems': 0,
                'visited_quizitems': 0,
                'notapplicable_quizitems': 0,
                'incorrect_attempted_quizitems': 0,
                'attempted_quizitems': 0,
                'admin_view': False
            })
    data_points_dict = {}
    assessment_and_quiz_data = kwargs.get('assessment_and_quiz_data', False)
    
    try:
        # user_obj = User.objects.get(pk=int(user_id))
        author_obj = node_collection.one({ '_type': u'Author', 'created_by': int(user_id) })
    except Exception, e:
        return analytics_data

    template = "ndf/lms.html"
    if request:
        ajax_request = request.GET.get("ajax_request",'')
    else:
        ajax_request = None
    if request:
        # let's keep all get calls from request in this block.
        # so that we can use this method for api calls
        if not get_result_dict:
            data_points_dict = request.GET.get('data_points_dict', {})

        unit_id = request.GET.get("data_unit_id",'')
        if unit_id:
            # This marks request from My-Desk
            group_id = ObjectId(unit_id)
            template = "ndf/user_course_analytics.html"

        gstaff_access = check_is_gstaff(group_id, request.user)
        if gstaff_access:
            template = "ndf/user_course_analytics.html"

    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name
    group_obj_member_of_names_list = group_obj.member_of_names_list
    # if "CourseEventGroup" in group_obj_member_of_names_list:
    #     template = "ndf/gcourse_event_group.html"

    if data_points_dict and not isinstance(data_points_dict, dict):
        data_points_dict = json.loads(data_points_dict)
        analytics_data['correct_attempted_quizitems'] = (data_points_dict['quiz_points'] / GSTUDIO_QUIZ_CORRECT_POINTS)
        analytics_data['user_notes'] = (data_points_dict['notes_points'] / GSTUDIO_NOTE_CREATE_POINTS)
        analytics_data['user_files'] = (data_points_dict['files_points'] / GSTUDIO_FILE_UPLOAD_POINTS)
        analytics_data['total_cmnts_by_user'] = (data_points_dict['interactions_points'] / GSTUDIO_COMMENT_POINTS)
        analytics_data['users_points'] = data_points_dict['users_points']

    counter_obj = Counter.get_counter_obj(user_id, ObjectId(group_id))
    analytics_instance = AnalyticsMethods(author_obj.created_by, author_obj.name, group_id)

    analytics_data['total_quizitems'] = 0

    if "CourseEventGroup" in group_obj_member_of_names_list and not ajax_request:
        template = "ndf/gcourse_event_group.html"
        # Modules Section
        all_modules= analytics_instance.get_total_modules_count()
        # TO IMPROVE
        completed_modules = analytics_instance.get_completed_modules_count()
        # Units Section
        all_units = analytics_instance.get_total_units_count()
        # print "\n Total Units =  ", all_units, "\n\n"
        completed_units = analytics_instance.get_completed_units_count()
        # print "\n Completed Units =  ", completed_units, "\n\n"
        analytics_data['level1_lbl'] = "Module Completion"
        analytics_data['level2_lbl'] = "Unit Completion"
        analytics_data['level1_progress_stmt'] = str(completed_modules) + " out of " + str(all_modules) + " Modules completed"
        analytics_data['level2_progress_stmt'] = str(completed_units) + " out of " + str(all_units) + " Units completed"
        if completed_modules and all_modules:
            analytics_data['level1_progress_meter'] = (completed_modules/float(all_modules))*100
        else:
            analytics_data['level1_progress_meter'] = 0

        if completed_units and all_units:
            analytics_data['level2_progress_meter'] = (completed_units/float(all_units))*100
        else:
            analytics_data['level2_progress_meter'] = 0

        # Depricated on 27Apr2017 - katkamrachana
        analytics_data['total_quizitems'] = analytics_instance.get_total_quizitems_count()
        # New implementation of using AT: 'total_assessment_items'
        # print "\n Total QuizItemEvents === ", analytics_data['total_quizitems'], "\n\n"
        # analytics_data['attempted_quizitems'] = counter_obj.no_questions_attempted
        analytics_data['attempted_quizitems'] = counter_obj['quiz']['attempted']
        # print "\n Attempted QuizItemEvents === ", analytics_data['attempted_quizitems'], "\n\n"
        if 'correct_attempted_quizitems' not in analytics_data:
            # analytics_data['correct_attempted_quizitems'] = counter_obj.no_correct_answers
            analytics_data['correct_attempted_quizitems'] = counter_obj['quiz']['correct']
        # print "\n Correct Attempted QuizItemEvents === ", analytics_data['correct_attempted_quizitems'], "\n\n"
        # analytics_data['incorrect_attempted_quizitems'] = counter_obj.no_incorrect_answers
        analytics_data['incorrect_attempted_quizitems'] = counter_obj['quiz']['incorrect']
        # print "\n InCorrect Attempted QuizItemEvents === ", analytics_data['incorrect_attempted_quizitems'], "\n\n"

    # Resources Section
    # analytics_data['total_res'] = analytics_instance.get_total_resources_count()
    # print "\n Total Resources === ", total_res, "\n\n"
    # analytics_data['completed_res'] = analytics_instance.get_completed_resources_count()
    # print "\n Completed Resources === ", completed_res, "\n\n"

    analytics_data['username'] = author_obj.name
    # QuizItem Section

    if "announced_unit" in group_obj_member_of_names_list:
        visited_nodes = []
        if counter_obj:
            visited_nodes = counter_obj['visited_nodes'].keys()
        unit_structure = get_unit_hierarchy(group_obj)
        all_lessons = len(unit_structure)
        all_activities = 0
        completed_activities = 0
        completed_lessons = 0
        for each_lesson_dict in unit_structure:
            lesson_act_ids = []
            for each_lesson_key, each_lesson_val in each_lesson_dict.iteritems():
                if each_lesson_key == 'id':
                    lesson_id = each_lesson_dict[each_lesson_key]
                    
                if each_lesson_key == 'activities':
                    all_activities = all_activities + len(each_lesson_dict[each_lesson_key])
                    for each_act_dict in each_lesson_dict[each_lesson_key]:
                        for each_act_key, each_act_val in each_act_dict.iteritems():
                            if each_act_key == 'id':
                                act_id = each_act_dict[each_act_key]
                                lesson_act_ids.append(act_id)
                                if act_id in visited_nodes:
                                    completed_activities = completed_activities + 1
            if all(each_act_id in visited_nodes for each_act_id in lesson_act_ids):
                completed_lessons = completed_lessons + 1
        analytics_data['level1_lbl'] = "Lesson Visited"
        analytics_data['level2_lbl'] = "Activity Visited"

        analytics_data['level1_progress_stmt'] = str(completed_lessons) + " out of " + str(all_lessons) + " Lessons Visited"
        analytics_data['level2_progress_stmt'] = str(completed_activities) + " out of " + str(all_activities) + " Activities Visited"
        if completed_lessons and all_lessons:
            analytics_data['level1_progress_meter'] = (completed_lessons/float(all_lessons))*100
        else:
            analytics_data['level1_progress_meter'] = 0
        if completed_activities and all_activities:
            analytics_data['level2_progress_meter'] = (completed_activities/float(all_activities))*100
        else:
            analytics_data['level2_progress_meter'] = 0
        # print "\n an: ", analytics_data
        # Resources Section
        # analytics_data['total_res'] = analytics_instance.get_total_resources_count()
        # print "\n Total Resources === ", total_res, "\n\n"
        # analytics_data['completed_res'] = analytics_instance.get_completed_resources_count()
        # print "\n Completed Resources === ", completed_res, "\n\n"

        # following code will override (gstudio quiz) counters:
        if assessment_and_quiz_data:
            analytics_data.update({
                'correct_attempted_assessments': 0,
                'unattempted_assessments': 0,
                'visited_assessments': 0,
                'notapplicable_assessments': 0,
                'incorrect_attempted_assessments': 0,
                'attempted_assessments': 0,
                'total_assessment_items': 0
                })

        items_count_cur = group_obj.get_attribute("total_assessment_items")
        if items_count_cur.count():
            items_count_cur_0_object_value = 0 if (items_count_cur[0].object_value == 'None') else items_count_cur[0].object_value
            if assessment_and_quiz_data:
                analytics_data['total_assessment_items'] = items_count_cur_0_object_value
            else:
                analytics_data['total_quizitems'] = items_count_cur_0_object_value

        # total_quiz_points = 0  # not used anywhere
        # assessment_list_cur = group_obj.get_attribute("assessment_list")
        # if assessment_list_cur.count():
        #     assessment_list_cur = assessment_list_cur[0]
        '''
        analytics_data['correct_attempted_quizitems'] = 0
        analytics_data['unattempted_quizitems'] = 0
        analytics_data['visited_quizitems'] = 0
        analytics_data['notapplicable_quizitems'] = 0
        analytics_data['incorrect_quizitems'] = 0
        analytics_data['attempted_quizitems'] = 0
        '''
        try:
            assessment_data_list = counter_obj['assessment']
            for each_dict in assessment_data_list:
                if assessment_and_quiz_data:
                    analytics_data['correct_attempted_assessments'] += each_dict['correct']
                    # analytics_data['unattempted_assessments'] += each_dict['unattempted']
                    # analytics_data['visited_assessments'] += each_dict['visited']
                    analytics_data['notapplicable_assessments'] += each_dict['notapplicable']
                    analytics_data['incorrect_attempted_assessments'] += each_dict['incorrect']
                    analytics_data['attempted_assessments'] += each_dict['attempted']
                else:
                    analytics_data['correct_attempted_quizitems'] += each_dict['correct']
                    # analytics_data['unattempted_quizitems'] += each_dict['unattempted']
                    # analytics_data['visited_quizitems'] += each_dict['visited']
                    analytics_data['notapplicable_quizitems'] += each_dict['notapplicable']
                    analytics_data['incorrect_attempted_quizitems'] += each_dict['incorrect']
                    analytics_data['attempted_quizitems'] += each_dict['attempted']
            if assessment_and_quiz_data:
                analytics_data['unattempted_assessments'] = analytics_data['total_assessment_items'] - analytics_data['attempted_assessments']
            else:
                analytics_data['unattempted_quizitems'] = analytics_data['total_quizitems'] - analytics_data['attempted_quizitems']
        except Exception as assessment_analytics_err:
            print "\nIn User analytics. Ignore if KeyError. Error: {0}".format(assessment_analytics_err)
            pass

    # Notes Section
    # analytics_data['total_notes'] = analytics_instance.get_total_notes_count()
    # print "\n Total Notes === ", total_notes, "\n\n"
    if 'user_notes' not in analytics_data:
        # analytics_data['user_notes'] = counter_obj.no_notes_written
        analytics_data['user_notes'] = counter_obj['page']['blog']['created']
    # print "\n User Notes === ", user_notes, "\n\n"

    # Files Section
    # analytics_data['total_files'] = analytics_instance.get_total_files_count()
    # print "\n Total Files === ", total_files, "\n\n"
    if 'user_files' not in analytics_data:
        # analytics_data['user_files'] = counter_obj.no_files_created
        analytics_data['user_files'] = counter_obj['file']['created']
    # print "\n User's Files === ", user_files, "\n\n"

    # Comments
    if 'total_cmnts_by_user' not in analytics_data:
        # analytics_data['total_cmnts_by_user'] = counter_obj.no_comments_by_user
        analytics_data['total_cmnts_by_user'] = counter_obj['total_comments_by_user']
    # print "\n Total Comments By User === ", total_cmnts_by_user, "\n\n"

    # Comments on Notes Section
    # analytics_data['cmts_on_user_notes'] = counter_obj.no_comments_received_on_notes
    analytics_data['cmts_on_user_notes'] = counter_obj['page']['blog']['comments_gained']
    # print "\n Total Comments On User Notes === ", cmts_on_user_notes, "\n\n"
    # analytics_data['unique_users_commented_on_user_notes'] = len(counter_obj.comments_by_others_on_notes.keys())
    # print "\n Total Unique Users - Commented on User Notes === ", unique_users_commented_on_user_notes, "\n\n"


    # Comments on Files Section
    # analytics_data['cmts_on_user_files'] = counter_obj.no_comments_received_on_files
    analytics_data['cmts_on_user_files'] = counter_obj['file']['comments_gained']
    # print "\n Total Comments User Files === ", cmts_on_user_files, "\n\n"
    # analytics_data['unique_users_commented_on_user_files'] = len(counter_obj.comments_by_others_on_files.keys())

    analytics_data['unique_users_commented_on_user_files'] = len(counter_obj['file']['comments_by_others_on_res'].keys())

    # print "\n Total Unique Users Commented on User Files === ", unique_users_commented_on_user_files, "\n\n"

    # BY User
    # TO IMPROVE
    # analytics_data['total_notes_read_by_user'] = counter_obj.no_others_notes_visited
    analytics_data['total_notes_read_by_user'] = counter_obj['page']['blog']['visits_on_others_res']
    # print "\n Total Notes read by User === ", total_notes_read_by_user, "\n\n"

    # TO IMPROVE
    # analytics_data['total_files_viewed_by_user'] = counter_obj.no_others_files_visited
    analytics_data['total_files_viewed_by_user'] = counter_obj['file']['visits_on_others_res']
    # print "\n Total Files viewed by User === ", total_files_viewed_by_user, "\n\n"

    # TO IMPROVE
    # analytics_data['other_viewing_my_files'] = counter_obj.no_visits_gained_on_files
    analytics_data['other_viewing_my_files'] = counter_obj['file']['visits_gained']
    # print "\n Total Users viewing My FILES === ", other_viewing_my_files, "\n\n"

    # TO IMPROVE
    # analytics_data['others_reading_my_notes'] = counter_obj.no_views_gained_on_notes
    analytics_data['others_reading_my_notes'] = counter_obj['page']['blog']['visits_gained']
    # print "\n Total Users reading My NOTES === ", others_reading_my_notes, "\n\n"

    # analytics_data['commented_on_others_notes'] = counter_obj.no_comments_on_others_notes
    analytics_data['commented_on_others_notes'] = counter_obj['page']['blog']['commented_on_others_res']
    # print "\n Total Notes on which User Commented === ", commented_on_others_notes, "\n\n"

    # analytics_data['commented_on_others_files'] = counter_obj.no_comments_on_others_files
    analytics_data['commented_on_others_files'] = counter_obj['file']['commented_on_others_res']
    # print "\n Total Notes on which User Commented === ", commented_on_others_notes, "\n\n"

    # all_cmts = analytics_instance.get_avg_rating_on_my_comments()
    # analytics_data['total_rating_rcvd_on_notes'] = counter_obj.avg_rating_received_on_notes
    analytics_data['total_rating_rcvd_on_notes'] = counter_obj['page']['blog']['avg_rating_gained']
    # print "\n\n analytics_data['total_rating_rcvd_on_notes'] === ",analytics_data['total_rating_rcvd_on_notes']
    # analytics_data['total_rating_rcvd_on_files'] = counter_obj.avg_rating_received_on_files
    analytics_data['total_rating_rcvd_on_files'] = counter_obj['file']['avg_rating_gained']
    # print "\n\n analytics_data['total_rating_rcvd_on_files'] === ",analytics_data['total_rating_rcvd_on_files']
    # cmts_on_user_notes = counter_obj.no_comments_received_on_notes
    cmts_on_user_notes = counter_obj['page']['blog']['comments_gained']
    # cmts_on_user_files = counter_obj.no_comments_received_on_files
    cmts_on_user_files = counter_obj['file']['comments_gained']
    analytics_data['cmnts_rcvd_by_user'] = 0
    if 'cmts_on_user_notes' in analytics_data and 'cmts_on_user_files' in analytics_data:
        analytics_data['cmnts_rcvd_by_user'] = analytics_data['cmts_on_user_notes'] + analytics_data['cmts_on_user_files']

    if "users_points" not in analytics_data:
        # analytics_data['users_points'] = counter_obj.course_score
        analytics_data['users_points'] = counter_obj['group_points']

    # analytics_data['users_points_breakup'] = analytics_instance.get_users_points(True)
    analytics_data['users_points_breakup'] = counter_obj.get_all_user_points_dict()
    analytics_data['group_obj'] = group_obj
    if kwargs.get('get_counter_obj_in_result', False):
        analytics_data['counter_obj'] = counter_obj
    del analytics_instance
    # print analytics_data

    if get_result_dict:
        return analytics_data

    # cache.set(cache_key, analytics_data, 60*10)
    analytics_data['group_member_of'] = group_obj.member_of_names_list
    analytics_data['group_name'] = group_obj.name
    analytics_data['group_id'] = group_obj._id
    analytics_data['groupid'] = group_obj._id
    analytics_data['title'] = "course_analytics"
    return render_to_response(template,
                                analytics_data,
                                context_instance = RequestContext(request)
    )

    # return HttpResponse(json.dumps(analytics_data))

@login_required
@get_execution_time
def course_analytics_admin(request, group_id):

    cache_key = u'course_analytics_admin' + unicode(slugify(group_id))
    cache_result = cache.get(cache_key)
    # if cache_result:
    #     return HttpResponse(cache_result)

    # from gnowsys_ndf.ndf.views.analytics_methods import AnalyticsMethods
    # from gnowsys_ndf.settings import GSTUDIO_FILE_UPLOAD_POINTS, GSTUDIO_COMMENT_POINTS, GSTUDIO_NOTE_CREATE_POINTS, GSTUDIO_QUIZ_CORRECT_POINTS
    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name
    thread_node = None
    banner_pic_obj,old_profile_pics = _get_current_and_old_display_pics(group_obj)
    template = "ndf/lms.html"

    if "CourseEventGroup" in group_obj.member_of_names_list:
        template = "ndf/gcourse_event_group.html"

    allow_to_join = get_group_join_status(group_obj)
    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            'group_obj': group_obj, 'title': 'course_analytics', 'allow_to_join': allow_to_join,
            'old_profile_pics':old_profile_pics, "prof_pic_obj": banner_pic_obj, "admin_analytics":  True,
            'admin_view': True
            }


    group_obj = get_group_name_id(group_id, get_obj=True)
    admin_analytics_data_list = []
    admin_analytics_data_append = admin_analytics_data_list.append
    FILES_MAX_POINT_VAL = NOTES_MAX_POINT_VAL = QUIZ_MAX_POINT_VAL = INTERACTIONS_MAX_POINT_VAL = 0

    all_group_authors = node_collection.find({'_type': u'Author', 'created_by': {'$in': group_obj.author_set}})
    # print group_obj.author_set

    auth_counters = counter_collection.find({'user_id': {'$in': group_obj.author_set}, 'group_id': ObjectId(group_id) })

    for each_author_obj in all_group_authors:
        admin_analytics_data = {}

        try:
            user_counter_obj = Counter(auth_counters.clone().where('this.user_id == '+str(each_author_obj.created_by)+' && this.group_id ==  "'+str(group_id)+'"')[0])
        except Exception, e:
            user_counter_obj = Counter.get_counter_obj(each_author_obj.created_by, ObjectId(group_id))
            print e

        # try:
        #     user_obj = User.objects.get(pk=int(each_author_obj))
        # except Exception, e:
        #     continue

        # analytics_instance = AnalyticsMethods(request, user_obj.id,user_obj.username, group_id)
        # username = user_obj.username
        # user_id = user_obj.id
        # users_points = analytics_instance.get_users_points()
        admin_analytics_data['username']    = each_author_obj.name
        admin_analytics_data['user_id']     = each_author_obj.created_by
        admin_analytics_data['users_points']= user_counter_obj['group_points']

        # admin_analytics_data["files_points"] = user_counter_obj['file']['created'] * GSTUDIO_FILE_UPLOAD_POINTS
        admin_analytics_data["files_points"] = user_counter_obj.get_file_points()
        if FILES_MAX_POINT_VAL < admin_analytics_data["files_points"]:
            FILES_MAX_POINT_VAL = admin_analytics_data["files_points"]

        # admin_analytics_data['notes_points'] = user_counter_obj['page']['blog']['created'] * GSTUDIO_NOTE_CREATE_POINTS
        admin_analytics_data['notes_points'] = user_counter_obj.get_page_points(page_type='blog')
        if NOTES_MAX_POINT_VAL < admin_analytics_data['notes_points']:
            NOTES_MAX_POINT_VAL = admin_analytics_data['notes_points']


        if "announced_unit" in group_obj.member_of_names_list:
            admin_analytics_data['quiz_points'] = user_counter_obj.get_assessment_points()
            if QUIZ_MAX_POINT_VAL < admin_analytics_data['quiz_points']:
                QUIZ_MAX_POINT_VAL = admin_analytics_data['quiz_points']
        else:
            # admin_analytics_data['quiz_points'] = user_counter_obj['quiz']['correct'] * GSTUDIO_QUIZ_CORRECT_POINTS
            admin_analytics_data['quiz_points'] = user_counter_obj.get_quiz_points()
            if QUIZ_MAX_POINT_VAL < admin_analytics_data['quiz_points']:
                QUIZ_MAX_POINT_VAL = admin_analytics_data['quiz_points']

        # admin_analytics_data['interactions_points'] = user_counter_obj['total_comments_by_user'] * GSTUDIO_COMMENT_POINTS
        admin_analytics_data['interactions_points'] = user_counter_obj.get_interaction_points()
        if INTERACTIONS_MAX_POINT_VAL < admin_analytics_data['interactions_points']:
            INTERACTIONS_MAX_POINT_VAL = admin_analytics_data['interactions_points']

        # del analytics_instance
        admin_analytics_data_append(admin_analytics_data)

    max_points_dict = {'file_max_points': FILES_MAX_POINT_VAL,'notes_max_points': NOTES_MAX_POINT_VAL,
    'quiz_max_points': QUIZ_MAX_POINT_VAL, 'interactions_max_points': INTERACTIONS_MAX_POINT_VAL}

    column_headers = [
        ("username", "Name"),
        # ("user_id", "user_id"),
        ("users_points", "Total Points"),
        ("files_points", "Files"),
        ("notes_points", "Notes"),
        ("quiz_points", "Assessments"),
        ("interactions_points", "Interactions"),
    ]
    response_dict = {}
    response_dict["column_headers"] = column_headers
    response_dict["success"] = True
    response_dict["students_data_set"] = admin_analytics_data_list
    response_dict['max_points_dict'] = max_points_dict
    context_variables["response_dict"] = json.dumps(response_dict)
    cache.set(cache_key, response_dict, 60*10)
    # print "\n admin_analytics_data_list === ",admin_analytics_data_list
    return render_to_response(template,
                                context_variables,
                                context_instance = RequestContext(request)
    )


@login_required
@get_execution_time
def build_progress_bar(request, group_id, node_id):
    cache_key = u'build_progress_bar_' + unicode(slugify(group_id)) + "_" + unicode(node_id) + "_" + unicode(request.user.id)
    cache_result = cache.get(cache_key)
    if cache_result:
        return HttpResponse(cache_result)
    result_status = {}
    try:
        group_obj   = get_group_name_id(group_id, get_obj=True)
        course_complete_percentage = total_count = completed_count = None
        if request.user.is_authenticated():
            result_status = get_course_completetion_status(group_obj, request.user.id)
    except Exception as e:
        # print "\n\n Error while fetching ---", e
        pass
    cache.set(cache_key, json.dumps(result_status), 60*15)
    return HttpResponse(json.dumps(result_status))

@get_execution_time
def get_resource_completion_status(request, group_id):
    result_dict = {'COMPLETED':[]}
    cr_ids = request.GET.get("cr_ids", "")
    if cr_ids:
        cr_ids = json.loads(cr_ids)
        for each_cr in cr_ids:
            b = benchmark_collection.find({'name': "course_resource_detail",
                'calling_url': {'$regex': '/'+unicode(each_cr)+'/$'},
                'user': request.user.username
                })
            if b.count():
                # print "\n\nb.count()",b.count()
                result_dict['COMPLETED'].append(each_cr)
    return HttpResponse(json.dumps(result_dict))

# :::::::::::::::::::::::::::::::::REPORT VIEWS ENDS::::::::::::::::::::::

@get_execution_time
@login_required
def manage_users(request, group_id):
    group_obj   = get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name
    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
        }
    template = 'ndf/users_mgmt.html'

    return render_to_response(template,
                                context_variables,
                                context_instance = RequestContext(request)
    )

@get_execution_time
def assets(request, group_id, asset_id=None,page_no=1):
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    group_obj = get_group_name_id(group_id, get_obj=True)
    asset_gst_name, asset_gst_id = GSystemType.get_gst_name_id("Asset")
    from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP
    #template = 'ndf/gevent_base.html'
    template = 'ndf/lms.html'
    if asset_id:
        asset_obj = node_collection.one({'_id': ObjectId(asset_id)})
        asset_content_list = get_relation_value(ObjectId(asset_obj._id),'has_assetcontent')
        # topic_gst_name, topic_gst_id = GSystemType.get_gst_name_id("Topic")
        
        asset_nodes = node_collection.find({'member_of': {'$in': [asset_gst_id]},
            'group_set': {'$all': [ObjectId(group_id)]}}).sort('last_update', -1)
        # topic_nodes = node_collection.find({'member_of': {'$in': [topic_gst_id]}})
        # assetcontent_page_info = paginator.Paginator(asset_content_list['grel_node'], page_no, GSTUDIO_NO_OF_OBJS_PP)
        context_variables = {
            'group_id': group_id, 'groupid': group_id,
            'title':'asset_detail','asset_obj':asset_obj,
            'asset_nodes':asset_nodes,'asset_content_list':asset_content_list,
            'group_obj':group_obj, 'group_name':group_obj.name
        }
        if 'announced_unit' in group_obj.member_of_names_list or 'Group' in group_obj.member_of_names_list and 'base_unit' not in group_obj.member_of_names_list :
                 
            if 'raw@material' in asset_obj.tags:
                context_variables.update({'title':'raw_material_detail'})
                template = 'ndf/lms.html'
            elif 'asset@gallery' in asset_obj.tags:
                context_variables.update({'title':'asset_gallery_detail'})
                template = 'ndf/lms.html'
                        
            else:
                #template = 'ndf/gevent_base.html'
                template = 'ndf/lms.html'
        return render_to_response(template,
                                    context_variables,
                                    context_instance = RequestContext(request)
        )

    asset_nodes = node_collection.find({'member_of': {'$in': [asset_gst_id]},
        'group_set': {'$all': [ObjectId(group_id)]}}).sort('last_update', -1)
    assets_page_info = paginator.Paginator(asset_nodes, page_no, GSTUDIO_NO_OF_OBJS_PP)
    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_obj.name, 
            'asset_nodes': asset_nodes,'title':'asset_list',
            'group_obj':group_obj,'assets_page_info':assets_page_info
        }
    
    return render_to_response(template,
                                context_variables,
                                context_instance = RequestContext(request)
    )

@get_execution_time
def assetcontent_detail(request, group_id, asset_id,asst_content_id,page_no=1):
    from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP
    assetcontent_obj = node_collection.one({'_id': ObjectId(asst_content_id)})
    asset_obj = node_collection.one({'_id': ObjectId(asset_id)})
    group_obj = get_group_name_id(group_id, get_obj=True)
    # print group_id,asset_id,asst_content_id
    asset_content_list = get_relation_value(ObjectId(asset_obj._id),'has_assetcontent')
    template = 'ndf/lms.html'
    assetcontent_page_info = paginator.Paginator(asset_content_list['grel_node'], page_no, GSTUDIO_NO_OF_OBJS_PP)
    context_variables = {
            'asset_content_list':asset_content_list,'group_id':group_obj._id,'group_name':group_obj.name,
            'groupid':group_obj._id,'node':assetcontent_obj,'asset_obj':asset_obj,
            'title':"asset_content_detail",'group_obj':group_obj,'assetcontent_page_info':assetcontent_page_info
        }
    if request.user.is_authenticated():
        # Counter.add_visit_count.delay(resource_obj_or_id=file_obj._id.__str__(),
        Counter.add_visit_count(resource_obj_or_id=assetcontent_obj._id.__str__(),
                                current_group_id=group_obj._id.__str__(),
                                loggedin_userid=request.user.id)

    if ("announced_unit" in group_obj.member_of_names_list or "Group" in group_obj.member_of_names_list) and  ("raw@material" in asset_obj.tags or "asset@gallery" in asset_obj.tags) :
        template = 'ndf/lms.html'
        if "raw@material" in asset_obj.tags:
            context_variables.update( {'title':"raw_material_detail"})
        if "asset@gallery" in asset_obj.tags:
            context_variables.update( {'title':"asset_gallery_detail"})
            
    return render_to_response(template,
                                context_variables,
                                context_instance = RequestContext(request)
    )

@get_execution_time
def create_edit_course_page(request, group_id, page_id=None,page_type=None):
    group_obj = get_group_name_id(group_id, get_obj=True)
    group_id = group_obj._id
    group_name = group_obj.name
    #template = 'ndf/gevent_base.html'
    template = 'ndf/lms.html'
    # templates_gst = node_collection.one({"_type":"GSystemType","name":"Template"})
    # if templates_gst._id:
    #   # templates_cur = node_collection.find({"member_of":ObjectId(GST_PAGE._id),"type_of":ObjectId(templates_gst._id)})
    #   templates_cur = node_collection.find({"type_of":ObjectId(templates_gst._id)})

    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,'page_type':page_type,
            'group_obj': group_obj, 'title': 'create_course_pages',
            'activity_node': None, #'templates_cur': templates_cur,
            'cancel_activity_url': reverse('course_pages',
                                        kwargs={
                                        'group_id': group_id
                                        })}

    if page_id:
        node_obj = node_collection.one({'_id': ObjectId(page_id)})
        context_variables.update({'activity_node': node_obj, 'hide_breadcrumbs': True,
            'cancel_activity_url': reverse('view_course_page',
                                        kwargs={
                                        'group_id': group_id,
                                        'page_id': node_obj._id
                                        })})


    return render_to_response(template,
                                context_variables,
                                context_instance = RequestContext(request)
    )

@get_execution_time
def course_pages(request, group_id, page_id=None,page_no=1):
    from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP
    group_obj = get_group_name_id(group_id, get_obj=True)
    group_id = group_obj._id
    group_name = group_obj.name
    #template = 'ndf/gevent_base.html'
    template = 'ndf/lms.html'
    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            'group_obj': group_obj, 'title': 'course_pages',
            'editor_view': True, 'activity_node': None, 'all_pages': None}

    if page_id:
        node_obj = node_collection.one({'_id': ObjectId(page_id)})
        
        rt_translation_of = Node.get_name_id_from_type('translation_of', 'RelationType', get_obj=True)

        other_translations_grels = triple_collection.find({
                            '_type': u'GRelation',
                            'subject': ObjectId(page_id),
                            'relation_type': rt_translation_of._id,
                            'right_subject': {'$nin': [node_obj._id]}
                        })
        other_translations = node_collection.find({'_id': {'$in': [r.right_subject for r in other_translations_grels]} })
        
        context_variables.update({'activity_node': node_obj, 'hide_breadcrumbs': True,'other_translations':other_translations})
        context_variables.update({'editor_view': False})


    else:
        activity_gst_name, activity_gst_id = GSystemType.get_gst_name_id("activity")
        all_pages = node_collection.find({'member_of':
                    {'$in': [page_gst_id, activity_gst_id] }, 'group_set': group_id,
                    'type_of': {'$ne': [blog_page_gst_id]}
                    # 'content': {'$regex': 'clix-activity-styles.css', '$options': 'i'}
                    }).sort('last_update',-1)
        course_pages_info = paginator.Paginator(all_pages, page_no, GSTUDIO_NO_OF_OBJS_PP)
        context_variables.update({'editor_view': False, 'all_pages': all_pages,'course_pages_info':course_pages_info})
    return render_to_response(template,
                                context_variables,
                                context_instance = RequestContext(request)
    )

@login_required
def save_course_page(request, group_id):
    group_obj = get_group_name_id(group_id, get_obj=True)
    group_id = group_obj._id
    group_name = group_obj.name
    tags = request.POST.get("tags",[])
    if tags:
        tags = json.loads(tags)
    else:
        tags = []    
    #template = 'ndf/gevent_base.html'
    template = 'ndf/lms.html'
    page_gst_name, page_gst_id = GSystemType.get_gst_name_id("Page")
    page_obj = None
    activity_lang =  request.POST.get("lan", '')
    if request.method == "POST":
        name = request.POST.get("name", "")
        alt_name = request.POST.get("alt_name", "")
        content = request.POST.get("content_org", None)
        node_id = request.POST.get("node_id", "")
        if node_id:
            page_obj = node_collection.one({'_id': ObjectId(node_id)})
            if page_obj.altnames != alt_name:
                page_obj.altnames = unicode(alt_name)
        else:
            is_info_page = request.POST.get("page_type", "")
            page_obj = node_collection.collection.GSystem()
            page_obj.fill_gstystem_values(request=request)
            page_obj.member_of = [page_gst_id]
            page_obj.group_set = [group_id]
            page_obj.altnames = unicode(alt_name)
            if is_info_page == "Info":
                info_page_gst_name, info_page_gst_id = GSystemType.get_gst_name_id('Info page')
                page_obj.type_of = [info_page_gst_id]
        
        if activity_lang:
            language = get_language_tuple(activity_lang)
            page_obj.language = language
        if 'admin_info_page' in request.POST:
            admin_info_page = request.POST['admin_info_page']
            if admin_info_page:
                admin_info_page = json.loads(admin_info_page)
            if "None" not in admin_info_page:
                has_admin_rt = node_collection.one({'_type': "RelationType", 'name': "has_admin_page"})
                admin_info_page = map(ObjectId, admin_info_page)
                create_grelation(page_obj._id, has_admin_rt,admin_info_page)
                page_obj.reload()
            return HttpResponseRedirect(reverse("view_course_page",
             kwargs={'group_id': group_id, 'page_id': page_obj._id}))

        if 'help_info_page' in request.POST:
            help_info_page = request.POST['help_info_page']
            if help_info_page:
                help_info_page = json.loads(help_info_page)
            if "None" not in help_info_page:
                has_help_rt = node_collection.one({'_type': "RelationType", 'name': "has_help"})
                help_info_page = map(ObjectId, help_info_page)
                create_grelation(page_obj._id, has_help_rt,help_info_page)
                page_obj.reload()
            return HttpResponseRedirect(reverse("view_course_page",
             kwargs={'group_id': group_id, 'page_id': page_obj._id}))
        page_obj.fill_gstystem_values(tags=tags)
        page_obj.name = unicode(name)
        page_obj.content = unicode(content)
        page_obj.created_by = request.user.id
        page_obj.save(groupid=group_id)
        return HttpResponseRedirect(reverse("view_course_page",
         kwargs={'group_id': group_id, 'page_id': page_obj._id}))

@get_execution_time
def load_content_data(request, group_id):
    node_id = request.GET.get("node_id", "")
    node = node_collection.one({'_id': ObjectId(node_id)})
    template = 'ndf/node_ajax_content.html'
    return render_to_response(template,
    {
      "group_id":group_id,"groupid":group_id, "node": node,
      "hide_breadcrumbs": True, 'expand_content':True
    },context_instance=RequestContext(request))

@get_execution_time
def delete_activity_page(request, group_id):
    activity_id_list = request.POST.getlist('delete_files_list[]', '')
    activity_id = request.POST.get('activity_id', '')
    if activity_id_list:
        for each_activity in activity_id_list:
            activity_page_node = node_collection.one({'_id':ObjectId(each_activity)})
            if activity_page_node:
                trash_resource(request,ObjectId(group_id),ObjectId(activity_page_node._id))
                del_status  = delete_node(node_id=activity_page_node._id, deletion_type=0)
                return HttpResponse('success')
    if activity_id:
        activity_page_node = node_collection.one({'_id':ObjectId(activity_id)})
        if activity_page_node:
            trash_resource(request,ObjectId(group_id),ObjectId(activity_page_node._id))
            del_status  = delete_node(node_id=activity_page_node._id, deletion_type=0)
            return HttpResponse('success')
    return HttpResponse('fail')

@get_execution_time
def _get_unit_hierarchy(unit_group_obj,lang="en"):
    '''
    ARGS: unit_group_obj
    Result will be of following form:
    {
        name: 'Lesson1',
        type: 'lesson',
        id: 'l1',
        activities: [
            {
                name: 'Activity 1',
                type: 'activity',
                id: 'a1'
            },
            {
                name: 'Activity 1',
                type: 'activity',
                id: 'a2'
            }
        ]
    }, {
        name: 'Lesson2',
        type: 'lesson',
        id: 'l2',
        activities: [
            {
                name: 'Activity 1',
                type: 'activity',
                id: 'a1'
            }
        ]
    }
    '''
    # n = node_collection.one({'_id': ObjectId('593043c64a82533fc27b78f8')})
    # trans_act_list = get_lang_node(n._id,request.LANGUAGE_CODE)
    # for each in trans_act_list:
    #     for k,v in trans_act_list.iteritems():
    #         lesson_dict = {}
    #         lesson

    unit_structure = []
    for each in unit_group_obj.collection_set:
        lesson_dict ={}
        lesson = Node.get_node_by_id(each)
        if lesson:
            trans_lesson = get_lang_node(lesson._id,lang)
            if trans_lesson:
                lesson_dict['label'] = trans_lesson.name
            else:
                lesson_dict['label'] = lesson.name
            lesson_dict['id'] = lesson._id
            lesson_dict['type'] = 'unit-name'
            lesson_dict['children'] = []
            if lesson.collection_set:
                for each_act in lesson.collection_set:
                    activity_dict ={}
                    activity = Node.get_node_by_id(each_act)
                    if activity:
                        trans_act_name = get_lang_node(each_act,lang)
                        if trans_act_name:
                            activity_dict['label'] = trans_act_name.altnames or trans_act_name.name
                            # activity_dict['label'] = trans_act_name.name
                        else:
                            # activity_dict['label'] = activity.name
                            activity_dict['label'] = activity.altnames or activity.name
                        activity_dict['type'] = 'activity-group'
                        activity_dict['id'] = str(activity._id)
                        lesson_dict['children'].append(activity_dict)
            unit_structure.append(lesson_dict)
    return unit_structure

@get_execution_time
def widget_page_create_edit(request, group_id, node_id=None):
    node_id = request.GET.get('node_id', None)
    detail_url = request.GET.get('detail_url',)
    editor_type = request.GET.get('editor_type', 'GeneralToolbar')

    template = 'ndf/widget_node_form.html'
    if node_id:
        # existing note.
        url_name = 'node_edit'
        url_kwargs={'group_id': group_id, 'node_id': node_id, 'detail_url_name': detail_url }
        node_obj = Node.get_node_by_id(node_id)

    else:
        # new note
        url_name = 'node_create'
        url_kwargs={'group_id': group_id, 'member_of': 'Page', 'detail_url_name': detail_url}
    blog_type_gst_name, blog_type_gst_id = GSystemType.get_gst_name_id("Blog page")

    additional_form_fields = {
        'fields': {
            '': {
                'name' :'type_of',
                'widget': 'input',
                'widget_attr': 'hidden',
                'value': str(blog_type_gst_id)
            }
        }
    }

    req_context = RequestContext(request, {
                                'node_obj': Node.get_node_by_id(node_id),
                                'group_id': group_id, 'groupid': group_id,
                                'additional_form_fields': additional_form_fields,
                                'editor_type': editor_type,
                                'post_url': reverse(url_name, kwargs=url_kwargs),
                                'cancel_url': reverse('course_notebook', kwargs={'group_id': group_id}),
                                'title': 'notebook',
                                'no_altnames':True
                            })
    return render_to_response(template, req_context)

@login_required
def load_assessment_analytics(request, group_id):
    domain = request.GET.get('domain')
    result_set = {'correct_attempted_quizitems': 0, 'visited_quizitems': 0, 
    'unattempted_quizitems': 0, 'attempted_quizitems': 0, 
    'incorrect_attempted_quizitems': 0, 'notapplicable_quizitems': 0}
    user_id = request.GET.get('user_id')
    group_obj = get_group_name_id(group_id, get_obj=True)
    group_id = group_obj._id
    group_name = group_obj.name
    # Variable Decalarations
    correctAttemptCount = unattemptedCount = 0
    notapplicableCount = incorrectCount = attemptedCount = 0
    count_dict = {'correctAttemptCount': correctAttemptCount, 
        'unattemptedCount': unattemptedCount, 'notapplicableCount': notapplicableCount,
        'incorrectCount': incorrectCount, 'attemptedCount': attemptedCount}
    total_items = 0
    offeredId_list = []
    try:
        assessment_list_cur = group_obj.get_attribute("assessment_list")
        total_assessment_items_cur = group_obj.get_attribute("total_assessment_items")
        if total_assessment_items_cur.count():
            total_items = total_assessment_items_cur[0].object_value

        active_user_ids_list = [request.user.id]
        if GSTUDIO_BUDDY_LOGIN:
            active_user_ids_list += Buddy.get_buddy_userids_list_within_datetime(request.user.id, datetime.datetime.now())
        if assessment_list_cur.count():
            assessment_list = assessment_list_cur[0].object_value
            for each_sublist in assessment_list:
                # each_sublist[0] -- bankID & each_sublist[1] -- OfferedId
                try:
                    user_data_set = user_assessment_results("https://" + domain, int(user_id),
                     each_sublist[0], each_sublist[1])
                    if user_data_set:
                        try:
                            for buser_id in active_user_ids_list:
                                counter_obj = Counter.get_counter_obj(buser_id, group_id)
                                #create
                                if not counter_obj['assessment']:
                                    assessment_dict = {'id': each_sublist[1], 'correct': user_data_set['Correct'],
                                    'notapplicable': user_data_set['NotApplicable'], 'attempted': user_data_set['Attempted'], 
                                    'incorrect': user_data_set['Incorrect']}
                                    counter_obj['assessment'].append(assessment_dict)
                                    counter_obj['group_points'] += (user_data_set['Correct'] * GSTUDIO_QUIZ_CORRECT_POINTS)
                                else:
                                    #edit
                                    reattempt = False
                                    for each_dict in counter_obj['assessment']:
                                        # check if AssessmentOffered Id exists in the values list
                                        if each_sublist[1] in each_dict.values():
                                            counter_obj['group_points'] -= (each_dict['correct'] * GSTUDIO_QUIZ_CORRECT_POINTS)
                                            counter_obj['group_points'] += (user_data_set['Correct'] * GSTUDIO_QUIZ_CORRECT_POINTS)
                                            each_dict.update({'correct': user_data_set['Correct'],
                                             'notapplicable': user_data_set['NotApplicable'],
                                             'attempted': user_data_set['Attempted'],
                                             'incorrect': user_data_set['Incorrect']})
                                            reattempt = True
                                            break
                                    if not reattempt:
                                        assessment_dict = {'id': each_sublist[1], 'correct': user_data_set['Correct'],
                                        'notapplicable': user_data_set['NotApplicable'], 'attempted': user_data_set['Attempted'],
                                        'incorrect': user_data_set['Incorrect']}
                                        counter_obj['assessment'].append(assessment_dict)
                                        counter_obj['group_points'] += (user_data_set['Correct'] * GSTUDIO_QUIZ_CORRECT_POINTS)
                                counter_obj.last_update = datetime.datetime.now()
                                counter_obj.save()
                        except Exception as update_asmnt_anlytcs_for_buddies_err:
                            pass
                            succes_update = False
                            print "\nError occurred in update_assessment_analytics_for_buddies(). ", update_asmnt_anlytcs_for_buddies_err
                except Exception as no_result_found_err:
                    print "Unable to fetch Results for Assessment: {0} attempted by \
                    User: {1}. \n Error: {2}".format(each_sublist[1], str(user_id), no_result_found_err)
                    pass
            counter_obj = Counter.get_counter_obj(int(user_id), group_id)
            assessment_data_list = counter_obj['assessment']

            for each_dict in assessment_data_list:
                try:
                    result_set['correct_attempted_quizitems'] += each_dict['correct']
                    # result_set['visited_quizitems'] += each_dict['visited']
                    # result_set['unattempted_quizitems'] += each_dict['unattempted']
                    result_set['incorrect_attempted_quizitems'] += each_dict['incorrect']
                    # result_set['notapplicable_quizitems'] += each_dict['notapplicable']
                    result_set['attempted_quizitems'] += each_dict['attempted']
                except Exception as key_err:
                    print "\nIn load_assessment_analytics() Ignore if KeyError. Error: {0}".format(key_err)
            result_set['unattempted_quizitems'] = total_items - result_set['attempted_quizitems']
            result_set['users_points'] = counter_obj['group_points']
    except Exception as e:
        print "\nError: ",e
    # print "\nRS: ", result_set
    return HttpResponse(json.dumps(result_set))

@get_execution_time
def update_assessment_analytics_for_buddies(offeredId, user_ids, logged_in_user_id, user_data_set):
    succes_update = True
    try:
        for user_id in user_ids:
            counter_obj = Counter.get_counter_obj(user_id, group_id)
            #create
            if not counter_obj['assessment']:
                assessment_dict = {'id': offeredId, 'correct': user_data_set['Correct'],
                'notapplicable': user_data_set['NotApplicable'], 'attempted': user_data_set['Attempted'], 
                'incorrect': user_data_set['Incorrect']}
                counter_obj['assessment'].append(assessment_dict)
                counter_obj['group_points'] += (user_data_set['Correct'] * GSTUDIO_QUIZ_CORRECT_POINTS)
            else:
                #edit
                reattempt = False
                for each_dict in counter_obj['assessment']:
                    # check if AssessmentOffered Id exists in the values list
                    if offeredId in each_dict.values():
                        counter_obj['group_points'] -= (each_dict['correct'] * GSTUDIO_QUIZ_CORRECT_POINTS)
                        counter_obj['group_points'] += (user_data_set['Correct'] * GSTUDIO_QUIZ_CORRECT_POINTS)
                        each_dict.update({'correct': user_data_set['Correct'],
                         'notapplicable': user_data_set['NotApplicable'],
                         'attempted': user_data_set['Attempted'],
                         'incorrect': user_data_set['Incorrect']})
                        reattempt = True
                        break
                if not reattempt:
                    assessment_dict = {'id': offeredId, 'correct': user_data_set['Correct'],
                    'notapplicable': user_data_set['NotApplicable'], 'attempted': user_data_set['Attempted'],
                    'incorrect': user_data_set['Incorrect']}
                    counter_obj['assessment'].append(assessment_dict)
                    counter_obj['group_points'] += (user_data_set['Correct'] * GSTUDIO_QUIZ_CORRECT_POINTS)
            counter_obj.last_update = datetime.datetime.now()
            counter_obj.save()
    except Exception as update_asmnt_anlytcs_for_buddies_err:
        pass
        succes_update = False
        print "\nError occurred in update_assessment_analytics_for_buddies(). ", update_asmnt_anlytcs_for_buddies_err
    return succes_update

@get_execution_time
def course_quiz_data(request, group_id, all_data=False):
    '''
        all_data = True, will return checked and subimitted data
        all_data = false, will return only subimitted data

    '''

    def _merged_to_from(min_list, max_list, na_index):
        # max list contains more num of list
        # min list contains less num of list
        partly_max_list = max_list[:len(min_list)]
        exception_list = max_list[len(min_list):]
        for min_list_ele,mod_max_list_ele in zip(min_list, partly_max_list):
            for ind in na_index:
                partly_max_list_ele[ind] = min_list_ele[ind]
        return partly_max_list + exception_list
    group_obj   = Group.get_group_name_id(group_id, get_obj=True)
    group_id    = group_obj._id
    group_name  = group_obj.name
    gstaff_access = check_is_gstaff(group_id, request.user)
    if not gstaff_access:
        return HttpResponseRedirect(reverse('course_content', kwargs={'group_id': ObjectId(group_id)}))

    allow_to_join = get_group_join_status(group_obj)
    template = 'ndf/gcourse_event_group.html'
    context_variables = {
            'group_id': group_id, 'groupid': group_id, 'group_name':group_name,
            'group_obj': group_obj, 'title': 'course_quiz_data', 'allow_to_join': allow_to_join
        }

    admin_analytics_data_list = []
    admin_analytics_data_append = admin_analytics_data_list.append
    qip_gst = node_collection.one({ '_type': 'GSystemType', 'name': 'QuizItemPost'})

    query = {'member_of': qip_gst._id, 'group_set': group_id}

    record_set = node_collection.collection.aggregate([
        {
            '$match': query
        }, {
            '$project': {
                '_id': 0,
                'name': '$name',
                'check': '$attribute_set.quizitempost_user_checked_ans',
                'submit': '$attribute_set.quizitempost_user_submitted_ans',
                'user_id': '$created_by',
                'thread_node': '$prior_node'
            }
        },
        {
            '$sort': {'created_at': 1}
        }
    ])

    l = []
    # print "rec['result']", rec['result']
    for each_record in record_set['result']:
        for record_key,record_val in each_record.items():
            if record_key == "user_id":
                # To prevent in error in case where 
                # User object does not exist, return user-id
                user_obj = User.objects.get(pk=int(record_val))
                if user_obj:
                    username = user_obj.username
                else:
                    username = record_val                    
                each_record['user_id'] = username

            if record_key == "thread_node" and record_val:
                # QuizItemPost's prior_node list contains ObjectId
                # of its Thread node and QuizItemEvent node
                qie_node = node_collection.find_one({'_id': {'$in': record_val}, 
                    'name': {'$regex': '^(?!Thread of).*'}})
                each_record['name'] = qie_node.content

            if record_key == "submit" and record_val:
                for submitted_ans_dict in record_val[0]:
                    for k,v in submitted_ans_dict.items():
                        l1 = []
                        l1.append(each_record['name'])
                        l1.append(each_record['user_id'])
                        l1.append(k)
                        l1.append(','.join(v))
                        l.append(l1)

            if all_data:
                if record_key == "check" and record_val:
                    for checked_ans_dict in record_val[0]:
                        for k,v in checked_ans_dict.items():
                            l2 = []
                            l2.append(each_record['name'])
                            l2.append(each_record['user_id'])
                            l2.append(k)
                            l2.append(','.join(v))
                            l2.append("--")
                            l2.append("--")
                            l.append(l2)

    # print "\nadmin_analytics_data: ", l
    user_dict_list = []
    user_dict = {}
    for e in l:
        # print "\n this is e: ", e, any(e[1] not in euu for euu in user_dict_list)
        if any(e[1] in euu.keys() for euu in user_dict_list):
            for en in user_dict_list:
                if e[1] in en.keys():
                    user_dict = en
        else:
            user_dict = {e[1]: {'submit': []}}
            # user_dict = {e[1]: {'check': [], 'submit': []}}
            user_dict_list.append(user_dict)
        if all_data:
            if e.index('--') in [2,3]:
                user_dict[e[1]]['submit'].append(e)
            elif e.index('--') in [4,5]:
                user_dict[e[1]]['check'].append(e)
        else:
            user_dict[e[1]]['submit'].append(e)

    return_list = []
    for each_user_dict in user_dict_list:
        for ked, ved in each_user_dict.items():
            if all_data:
                if len(ved['check'])< len(ved['submit']):
                    return_list.extend(_merged_to_from(ved['check'],ved['submit'], na_index=[2,3]))
                elif len(ved['submit'])< len(ved['check']):
                    return_list.extend(_merged_to_from(ved['submit'],ved['check'], na_index=[4,5]))
            else:
                return_list.extend(ved['submit'])

    banner_pic_obj,old_profile_pics = _get_current_and_old_display_pics(group_obj)
    context_variables.update({'old_profile_pics':old_profile_pics,
                        "prof_pic_obj": banner_pic_obj, 'data': json.dumps(return_list)})
    return render_to_response(template, context_variables,
            context_instance=RequestContext(request))

@get_execution_time
def finish_lesson(request, group_id, node_id):
    response_dict = {'success': False}
    try:
        if request.method == "POST":
            user_id = request.POST.get('user_id', None)
            lesson_node = Node.get_node_by_id(node_id)
            if lesson_node and user_id:
                user_id = int(user_id)
                if user_id not in lesson_node.author_set:
                    lesson_node.author_set.append(user_id)
                    lesson_node.save(groupid=group_id)
                    response_dict.update({'success': True})
    except Exception as complete_node_err:
      print "\nError occurred in complete_node(). ", complete_node_err 
      pass
    return HttpResponse(json.dumps(response_dict))

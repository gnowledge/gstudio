''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json

''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
from django.http import Http404

import ast
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
# Commented below imports from settings file, because of the wild-import from models
# from gnowsys_ndf.settings import META_TYPE, GAPPS, GSTUDIO_SITE_DEFAULT_LANGUAGE, GSTUDIO_SITE_NAME, GSTUDIO_USER_GAPPS_LIST
# from gnowsys_ndf.settings import GSTUDIO_RESOURCES_CREATION_RATING, GSTUDIO_RESOURCES_REGISTRATION_RATING, GSTUDIO_RESOURCES_REPLY_RATING
from mongokit import paginator

# from gnowsys_ndf.ndf.models import *
# from gnowsys_ndf.ndf.models import node_collection, triple_collection, gridfs_collection
from gnowsys_ndf.ndf.models import *
from django.contrib.auth.models import User

from gnowsys_ndf.ndf.views.methods import get_drawers, get_execution_time, get_group_name_id,get_language_tuple
from gnowsys_ndf.ndf.views.methods import create_grelation, create_gattribute
from gnowsys_ndf.ndf.views.methods import get_user_group, get_user_task, get_user_notification, get_user_activity,get_execution_time
from gnowsys_ndf.ndf.views.analytics_methods import *
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.views.forum import *
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
from gnowsys_ndf.ndf.views.filehive import write_files
from gnowsys_ndf.notification import models as notification
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_all_user_groups, get_user_course_groups

#######################################################################################################################################

gapp_mt = node_collection.one({'_type': "MetaType", 'name': META_TYPE[0]})
GST_IMAGE = node_collection.one({'member_of': gapp_mt._id, 'name': GAPPS[3]})
at_user_pref = node_collection.one({'_type': 'AttributeType', 'name': 'user_preference_off'})
ins_objectid  = ObjectId()
ce_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseEventGroup"})
announced_unit_gst = node_collection.one({'_type': "GSystemType", 'name': "announced_unit"})
gst_acourse = node_collection.one({'_type': "GSystemType", 'name': "Announced Course"})
gst_group = node_collection.one({'_type': "GSystemType", 'name': "Group"})
group_id = node_collection.one({'_type': "Group", 'name': "home"})._id
gst_module_name, gst_module_id = GSystemType.get_gst_name_id('Module')
gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')
gst_author_name, gst_author_id = GSystemType.get_gst_name_id('Author')


#######################################################################################################################################
#                                                                     V I E W S   D E F I N E D   F O R   U S E R   D A S H B O A R D
#######################################################################################################################################
@get_execution_time
def userpref(request, group_id):
    usrid = int(group_id)
    auth = node_collection.one({'_type': "Author", 'created_by': usrid})
    # auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    lan_dict={}
    pref=request.POST["pref"]
    fall_back=request.POST["fallback"]
    if pref:
        lan_dict['primary']=pref
        lan_dict['secondary']=fall_back
        lan_dict['default']=GSTUDIO_SITE_DEFAULT_LANGUAGE
        auth.preferred_languages=lan_dict
        auth.modified_by=request.user.id
        auth.save(groupid=group_id)
    return HttpResponse("Success")

@get_execution_time
def uDashboard(request, group_id):

    try:
        usrid = int(group_id)
        auth = node_collection.one({'_type': "Author", 'created_by': usrid})
    except:
        auth = get_group_name_id(group_id, get_obj=True)
        usrid = auth.created_by

    group_id = auth._id
    # Fetching user group of current user & then reassigning group_id with it's corresponding ObjectId value

    group_name = auth.name
    usrname = auth.name
    date_of_join = auth['created_at']
    # current_user = request.user.pk
    current_user = usrid

    has_profile_pic = None
    profile_pic_image = None
    current_user_obj = None
    usr_fname = None
    usr_lname = None
    success_state = True
    old_profile_pics = []

    is_already_selected = None

    task_gst = node_collection.one(
        {'_type': "GSystemType", 'name': "Task"}
    )

    if current_user:
        exclued_from_public = ""
        if int(current_user) == int(usrid):
          Access_policy=["PUBLIC","PRIVATE"]
        if int(current_user) != int(usrid):
          Access_policy=["PUBLIC"]
    else:
          Access_policy=["PUBLIC"]
          exclued_from_public =  ObjectId(task_gst._id)

    dashboard_count = {}
    group_list = []
    user_activity = []

    page_gst = node_collection.one({'_type': "GSystemType", 'name': 'Page'})
    page_cur = node_collection.find({'member_of': {'$all': [page_gst._id]},
                            'created_by': int(usrid), "status": {"$nin": ["HIDDEN"]}})
    file_cur = node_collection.find({'_type': u"File", 'created_by': int(usrid),
                                     "status": {"$nin": ["HIDDEN"]}})
    forum_gst = node_collection.one({"_type": "GSystemType", "name": "Forum"})
    forum_count = node_collection.find({"_type": "GSystem",
                            "member_of": forum_gst._id, 'created_by': int(usrid),
                            "status": {"$nin": ["HIDDEN"]}})
    quiz_gst = node_collection.one({"_type": "GSystemType", "name": "Quiz"})
    quiz_count = node_collection.find({"_type": "GSystem",
                            "member_of": quiz_gst._id, 'created_by': int(usrid),
                            "status": {"$nin": ["HIDDEN"]}})
    thread_gst = node_collection.one({"_type": "GSystemType", "name": "Twist"})
    thread_count =node_collection.find({"_type": "GSystem",
                            "member_of": thread_gst._id, 'created_by': int(usrid),
                            "status": {"$nin": ["HIDDEN"]}})
    reply_gst = node_collection.one({"_type": "GSystemType", "name": "Reply"})
    reply_count = node_collection.find({"_type": "GSystem",
                            "member_of": reply_gst._id, 'created_by': int(usrid),
                            "status": {"$nin": ["HIDDEN"]}})

    task_cur = ""
    if current_user:
        if int(current_user) == int(usrid):
                   task_cur = node_collection.find(
            {'member_of': task_gst._id, 'attribute_set.Status': {'$in': ["New", "In Progress"]}, 'attribute_set.Assignee':usrid}
        ).sort('last_update', -1).limit(10)
                   dashboard_count.update({'Task': task_cur.count()})

        current_user_obj = User.objects.get(id=current_user)
        usr_fname = current_user_obj.first_name
        usr_lname = current_user_obj.last_name

    group_cur = node_collection.find(
        {'_type': "Group", 'name': {'$nin': ["home", auth.name]},"access_policy":{"$in":Access_policy},
        '$or': [{'group_admin': int(usrid)}, {'author_set': int(usrid)}]}).sort('last_update', -1).limit(10)

    dashboard_count.update({'group':group_cur.count()})

    # user activity gives all the activities of the users

    activity = ""
    activity_user = node_collection.find(
        {'$and': [{'$or': [{'_type': 'GSystem'}, {'_type': 'group'},
        {'_type': 'File'}]}, {"access_policy": {"$in": Access_policy}},{'status':{'$in':[u"DRAFT",u"PUBLISHED"]}},
        {'member_of': {'$nin': [exclued_from_public]}},
        {'$or': [{'created_by': int(usrid)}, {'modified_by': int(usrid)}]}]
    }).sort('last_update', -1).limit(10)

    a_user = []
    dashboard_count.update({'activity': activity_user.count()})

    #for i in activity_user:
    #    if i._type != 'Batch' or i._type != 'Course' or i._type != 'Module':
    #        a_user.append(i)
    #loop replaced by a list comprehension
    a_user=[i for i in activity_user if (i._type != 'Batch' or i._type != 'Course' or i._type != 'Module')]
    #a temp. variable which stores the lookup for append method
    user_activity_append_temp=user_activity.append
    for each in a_user:
        if each.created_by == each.modified_by:
            if each.last_update == each.created_at:
                activity = 'created'
            else:
                activity = 'modified'
        else:
            activity = 'created'

        if each._type == 'Group':
            user_activity_append_temp(each)
        else:
            member_of = node_collection.find_one({"_id": each.member_of[0]})
            user_activity_append_temp(each)

    '''
        notification_list=[]
        notification_object = notification.NoticeSetting.objects.filter(user_id=int(ID))
        for each in notification_object:
            ntid = each.notice_type_id
            ntype = notification.NoticeType.objects.get(id=ntid)
            label = ntype.label.split("-")[0]
            notification_list.append(label)
        Retrieving Tasks Assigned for User (Only "New" and "In Progress")
        user_assigned = []
        attributetype_assignee = node_collection.find_one({"_type":'AttributeType', 'name':'Assignee'})
        attr_assignee = triple_collection.find(
            {"_type": "GAttribute", "attribute_type": attributetype_assignee._id, "object_value": request.user.id}
        ).sort('last_update', -1).limit(10)
        dashboard_count.update({'Task':attr_assignee.count()})
        for attr in attr_assignee :
            task_node = node_collection.one({'_id':attr.subject})
            if task_node:
                user_assigned.append(task_node)
        task_cur gives the task asigned to users
    '''

    obj = node_collection.find(
        {'_type': {'$in': [u"GSystem", u"File"]}, 'contributors': int(usrid),
         'group_set': {'$all': [ObjectId(group_id)]}}
    )
    collab_drawer = []
    #a temp. variable which stores the lookup for append method
    collab_drawer_append_temp=collab_drawer.append
    """
    To populate collaborators according
    to their latest modification of particular resource:
    """
    for each in obj.sort('last_update', -1):
        for val in each.contributors:
            user_obj = User.objects.filter(pk=val)
            if user_obj:
                collab_drawer_append_temp({'usrname': user_obj[0].username, 'Id': val,
                                  'resource': each.name})

    shelves = []
    datavisual = []
    shelf_list = {}
    show_only_pie = True

    has_profile_pic_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_profile_pic') })
    all_old_prof_pics = triple_collection.find({'_type': "GRelation", "subject": auth._id, 'relation_type': has_profile_pic_rt._id, 'status': u"DELETED"})
    get_prof_relation = triple_collection.find({'_type': "GRelation", "subject": auth._id, 'relation_type': has_profile_pic_rt._id, 'status': u"PUBLISHED"})
    if not profile_pic_image and get_prof_relation.count() != 0:
        if auth:
            for each in auth.relation_set:
                if "has_profile_pic" in each:
                    profile_pic_image = node_collection.one(
                        {'_type': "GSystem", '_id': each["has_profile_pic"][0]}
                    )
                    break
#     has_profile_pic_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_profile_pic') })
#     all_old_prof_pics = triple_collection.find({'_type': "GRelation", "subject": auth._id, 'relation_type': has_profile_pic_rt._id, 'status': u"DELETED"})
    if all_old_prof_pics:
        for each_grel in all_old_prof_pics:
            n = node_collection.one({'_id': ObjectId(each_grel.right_subject)})
            if n not in old_profile_pics:
                old_profile_pics.append(n)

    forum_create_rate = forum_count.count() * GSTUDIO_RESOURCES_CREATION_RATING
    file_create_rate = file_cur.count() * GSTUDIO_RESOURCES_CREATION_RATING
    page_create_rate = page_cur.count() * GSTUDIO_RESOURCES_CREATION_RATING
    quiz_create_rate = quiz_count.count() * GSTUDIO_RESOURCES_CREATION_RATING
    reply_create_rate = reply_count.count() * GSTUDIO_RESOURCES_REPLY_RATING
    thread_create_rate = thread_count.count() * GSTUDIO_RESOURCES_CREATION_RATING

    datavisual.append({"name": "Forum", "count": forum_create_rate})
    datavisual.append({"name": "File", "count": file_create_rate})
    datavisual.append({"name": "Page", "count": page_create_rate})
    datavisual.append({"name": "Quiz", "count": quiz_create_rate})
    datavisual.append({"name": "Reply", "count": reply_create_rate})
    datavisual.append({"name": "Thread", "count": thread_create_rate})
    datavisual.append({"name": "Registration", "count": GSTUDIO_RESOURCES_REGISTRATION_RATING})

    total_activity_rating = GSTUDIO_RESOURCES_REGISTRATION_RATING + (page_cur.count()  + file_cur.count()  + forum_count.count()  + quiz_count.count()) * GSTUDIO_RESOURCES_CREATION_RATING + (thread_count.count()  + reply_count.count()) * GSTUDIO_RESOURCES_REPLY_RATING

    all_user_gapps = node_collection.find({'_type': u'GSystemType', 'name': {'$in': GSTUDIO_USER_GAPPS_LIST}})

    return render_to_response(
        "ndf/uDashboard.html",
        {
            'usr': current_user, 'username': usrname, 'user_id': usrid,
            'success': success_state, 'all_user_gapps': all_user_gapps,
            'usr_fname':usr_fname, 'usr_lname':usr_lname,
            'DOJ': date_of_join, 'author': auth, 'group_id': group_id,
            'groupid': group_id, 'group_name': group_name,
            'current_user_obj':current_user_obj,
            'already_set': is_already_selected, 'user_groups': group_cur,
            'prof_pic_obj': profile_pic_image, 'user_task': task_cur,
            'group_count': group_cur.count(), 'page_count': page_cur.count(),
            'file_count': file_cur.count(), 'user_activity': user_activity,
            'dashboard_count': dashboard_count, 'show_only_pie': show_only_pie,
            'datavisual': json.dumps(datavisual),
            'total_activity_rating': total_activity_rating,
            'old_profile_pics':old_profile_pics,
            'site_name': GSTUDIO_SITE_NAME,
         },
        context_instance=RequestContext(request)
    )

@get_execution_time
def user_preferences(request, group_id, auth_id):
    try:
        grp = node_collection.one({'_id': ObjectId(auth_id)})
        if request.method == "POST":
            lst = []
            pref_to_set = request.POST['pref_to_set']
            pref_list=pref_to_set.split(",")
            if pref_list:
                for each in pref_list:
                    if each:
                        obj = node_collection.one({'_id':ObjectId(each)})
                        lst.append(obj);
                if lst:
                    ga_node = create_gattribute(grp._id, at_user_pref, lst)
                # gattribute = triple_collection.one({'$and':[{'_type':'GAttribute'},{'attribute_type':at_user_pref._id},{'subject':grp._id}]})
                # if gattribute:
                #     gattribute.delete()
                # if lst:
                #     create_attribute=collection.GAttribute()
                #     create_attribute.attribute_type=at_user_pref
                #     create_attribute.subject=grp._id
                #     create_attribute.object_value=lst
                #     create_attribute.save()
            return HttpResponse("Success")


        else:
            list_at_pref=[]
            user_id=request.user.id
            if not at_user_pref:
                return HttpResponse("Failure")
            poss_attrs=grp.get_possible_attributes(at_user_pref._id)
            if poss_attrs:
                list_at_pref=poss_attrs['user_preference_off']['object_value']
            all_user_groups=[]
            for each in get_all_user_groups():
                all_user_groups.append(each.name)
            st = node_collection.find({'$and':[{'_type':'Group'},{'author_set':{'$in':[user_id]}},{'name':{'$nin':all_user_groups}}]})
            data_list=set_drawer_widget(st,list_at_pref)
            return HttpResponse(json.dumps(data_list))
    except Exception as e:
        print "Exception in userpreference view "+str(e)
        return HttpResponse("Failure")

@get_execution_time
def user_template_view(request, group_id):
    auth_group = None
    group_list=[]
    group_cur = node_collection.find({'_type': "Group", 'name': {'$nin': ["home", request.user.username]}}).limit(4)
    for i in group_cur:
        group_list.append(i)

    blank_list = []
    attributetype_assignee = node_collection.find_one({"_type": 'AttributeType', 'name':'Assignee'})
    attr_assignee = triple_collection.find({"_type": "GAttribute", "attribute_type":attributetype_assignee._id, "object_value":request.user.username})
    for attr in attr_assignee :
     task_node = node_collection.find_one({'_id': attr.subject})
     blank_list.append(task_node)

    notification_object = notification.NoticeSetting.objects.filter(user_id=request.user.id)
    for each in notification_object:
      ntid = each.notice_type_id
      ntype = notification.NoticeType.objects.get(id=ntid)
      label = ntype.label.split("-")[0]
      blank_list.append({'label':label, 'display': ntype.display})
    blank_list.reverse()

    blank_list = []
    activity = ""
    activity_user = node_collection.find({'$and':[{'$or':[{'_type':'GSystem'},{'_type':'Group'},{'_type':'File'}]},
                                                 {'$or':[{'created_by':request.user.id}, {'modified_by':request.user.id}]}] }).sort('last_update', -1).limit(4)
    for each in activity_user:
      if each.created_by == each.modified_by :
        if each.last_update == each.created_at:
          activity =  'created'
        else :
          activity =  'modified'
      else :
        activity =  'created'
      if each._type == 'Group':
        blank_list.append(each)
      else :
        member_of = node_collection.find_one({"_id": each.member_of[0]})
        blank_list.append(each)
    print blank_list

    template = "ndf/task_card_view.html"
    #variable = RequestContext(request, {'TASK_inst': self_task,'group_name':group_name,'group_id': group_id, 'groupid': group_id,'send':send})
    variable = RequestContext(request, {'TASK_inst':blank_list,'group_name':group_id,'group_id': group_id, 'groupid': group_id})
    return render_to_response(template, variable)

@login_required
@get_execution_time
def user_activity(request, group_id):
    activity_user = node_collection.find({'$and':[{'$or':[{'_type':'GSystem'},{'_type':'group'},{'_type':'File'}]},

                                                 {'$or':[{'created_by':request.user.id}, {'modified_by':request.user.id}]}]

                                                 }).sort('last_update', -1)
    blank_list=[]
    for each in activity_user:
      if each.created_by == each.modified_by :
        if each.last_update == each.created_at:
          activity =  'created'
        else :
          activity =  'modified'
      else :
        activity =  'created'
      if each._type == 'Group':
        blank_list.append(each)
      else :
        member_of = node_collection.find_one({"_id":each.member_of[0]})
        blank_list.append(each)
    template = "ndf/User_Activity.html"
    #variable = RequestContext(request, {'TASK_inst': self_task,'group_name':group_name,'group_id': group_id, 'groupid': group_id,'send':send})
    variable = RequestContext(request, {'user_activity':blank_list,'group_name':group_id,'group_id': group_id, 'groupid': group_id})
    return render_to_response(template, variable)

@get_execution_time
def group_dashboard(request, group_id):
    """
    This view returns data required for group's dashboard.
    """
    has_profile_pic = None
    profile_pic_image = None
    old_profile_pics = []
    has_profile_pic_str = ""
    is_already_selected = None

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    group_obj = node_collection.one({"_id": ObjectId(group_id)})
    has_profile_pic_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_profile_pic') })

    all_old_prof_pics = triple_collection.find({'_type': "GRelation", "subject": group_obj._id, 'relation_type': has_profile_pic_rt._id, 'status': u"DELETED"})
    if all_old_prof_pics:
        for each_grel in all_old_prof_pics:
            n = node_collection.one({'_id': ObjectId(each_grel.right_subject)})
            old_profile_pics.append(n)
    banner_pic=""

    for each in group_obj.relation_set:
                if "has_profile_pic" in each:
                    if each["has_profile_pic"]:
                        profile_pic_image = node_collection.one(
                            {'_type': {"$in": ["GSystem", "File"]}, '_id': each["has_profile_pic"][0]}
                        )
                if "has_banner_pic" in each:
                    if each["has_banner_pic"]:
                        banner_pic = node_collection.one(
                            {'_type': {"$in": ["GSystem", "File"]}, '_id': each["has_banner_pic"][0]}
                        )
                if ("has_thumbnail" in each) and each["has_thumbnail"]:
                        banner_pic = node_collection.one(
                            {'_type': {"$in": ["GSystem", "File"]}, '_id': each["has_thumbnail"][0]}
                        )

    # Approve StudentCourseEnrollment view
    approval = False
    enrollment_details = []
    enrollment_columns = []

    sce_gst = node_collection.one({'_type': "GSystemType", 'name': "StudentCourseEnrollment"})
    if sce_gst:
        # Get StudentCourseEnrollment nodes which are there for approval
        sce_cur = node_collection.find({
            'member_of': sce_gst._id, 'group_set': ObjectId(group_id),
            # "attribute_set.enrollment_status": {"$nin": [u"OPEN"]},
            "attribute_set.enrollment_status": {"$in": [u"PENDING", "APPROVAL"]},
            'status': u"PUBLISHED"
        }, {
            'member_of': 1
        })

        if sce_cur.count():
            approval = True
            enrollment_columns = ["College", "Course", "Status", "Enrolled", "Remaining", "Approved", "Rejected"]
            for sce_gs in sce_cur:
                sce_gs.get_neighbourhood(sce_gs.member_of)
                data = {}

                # approve_task = sce_gs.has_corresponding_task[0]
                approve_task = sce_gs.has_current_approval_task[0]
                approve_task.get_neighbourhood(approve_task.member_of)
                data["Status"] = approve_task.Status
                # Check for corresponding task's status
                # Continue with next if status is found as "Closed"
                # As we listing only 'In Progress'/'New' task(s)
                if data["Status"] == "Closed":
                    continue

                data["_id"] = str(sce_gs._id)
                data["College"] = sce_gs.for_college[0].name
                if len(sce_gs.for_acourse) > 1:
                    # It means it's a Foundation Course's (FC) enrollment
                    start_enroll = None
                    end_enroll = None
                    for each in sce_gs.for_acourse[0].attribute_set:
                        if not each:
                            pass
                        elif "start_time" in each:
                            start_time = each["start_time"]
                        elif "end_time" in each:
                            end_time = each["end_time"]

                    data["Course"] = "Foundation_Course" + "_" + start_time.strftime("%d-%b-%Y") + "_" + end_time.strftime("%d-%b-%Y")

                else:
                    # Courses other than FC
                    data["Course"] = sce_gs.for_acourse[0].name
                # data["Completed On"] = sce_gs.completed_on.strftime("%d/%m/%Y")

                remaining_count = None
                enrolled_list = []
                approved_list = []
                rejected_list = []
                if sce_gs.has_key("has_enrolled"):
                    if sce_gs["has_enrolled"]:
                        enrolled_list = sce_gs["has_enrolled"]

                if sce_gs.has_key("has_approved"):
                    if sce_gs["has_approved"]:
                        approved_list = sce_gs["has_approved"]

                if sce_gs.has_key("has_rejected"):
                    if sce_gs["has_rejected"]:
                        rejected_list = sce_gs["has_rejected"]

                data["Enrolled"] = len(enrolled_list)
                data["Approved"] = len(approved_list)
                data["Rejected"] = len(rejected_list)
                remaining_count = len(enrolled_list) - (len(approved_list) + len(rejected_list))
                data["Remaining"] = remaining_count

                enrollment_details.append(data)

    page = '1'
    return render_to_response (
        "ndf/group_dashboard.html",
        {
            'group_id': group_id, 'groupid': group_id,'old_profile_pics':old_profile_pics,
            'approval': approval, 'enrollment_columns': enrollment_columns, 'enrollment_details': enrollment_details,'prof_pic_obj': profile_pic_image,'banner_pic':banner_pic,'page':page
        },
        context_instance=RequestContext(request)
    )

@get_execution_time
@login_required
def user_profile(request, group_id):
    from django.contrib.auth.models import User

    auth_node = get_group_name_id(group_id, get_obj=True)

    user_dict={}
    user_details = User.objects.get(id=request.user.id)
    user_dict['fname'] = user_details.first_name
    user_dict['lname']  = user_details.last_name

    if request.method == "POST":
        user = User.objects.get(id=request.user.id)
        user_data = request.POST.getlist('forminputs[]','')
        user_select_data = request.POST.getlist('formselects[]','')
        apps_to_set = request.POST.getlist('selected_apps_list[]', [])
        apps_to_set = [ObjectId(app_id) for app_id in apps_to_set if app_id ]

        apps_list = []
        apps_list_append = apps_list.append
        for each in apps_to_set:
            apps_list_append(
                node_collection.find_one({
                    "_id": each
                })
            )

        at_apps_list = node_collection.one({'_type': 'AttributeType', 'name': 'apps_list'})
        ga_node = create_gattribute(auth_node._id, at_apps_list, apps_list)

        for i in user_data:
			a=ast.literal_eval(i)
			if  a.get('first_name',None) != None:
			  	user.first_name = a['first_name']
			  	user_dict['fname'] = user.first_name
			if a.get('last_name',None) != None:
				user.last_name = a['last_name']
			  	user_dict['lname'] = user.last_name
        user.save()
        for i in user_select_data:
			a=ast.literal_eval(i)
			if  a.get('language_proficiency',None) != None:
				auth_node['language_proficiency'] = []
				for k in a.get('language_proficiency',''):
					language = get_language_tuple(k)
					auth_node['language_proficiency'].append(language)
			if  a.get('subject_proficiency',None) != None:
				auth_node['subject_proficiency'] =  list(a.get('subject_proficiency',''))
        auth_node.save()
        user_dict['node'] = auth_node
        user_dict['success'] = True
        return HttpResponse(json.dumps(user_dict,cls=NodeJSONEncoder))
    else:
		user_dict['node'] = auth_node
		return render_to_response(  "ndf/user_profile_form.html",
				{'group_id':group_id,'node':auth_node,'user':json.dumps(user_dict,cls=NodeJSONEncoder)},
				context_instance=RequestContext(request)
		)

@get_execution_time
@login_required
def user_data_profile(request, group_id):
	user = {}
	auth_node = node_collection.one({"_id":ObjectId(group_id)})
	user_details = User.objects.get(id=request.user.id)
	user['first_name'] = user_details.first_name
	user['last_name']  = user_details.last_name
	user['node'] = auth_node
	return HttpResponse(json.dumps(user,cls=NodeJSONEncoder))

@get_execution_time
def upload_prof_pic(request, group_id):
    if request.method == "POST" :
        user = request.POST.get('user','')
        if_module = request.POST.get('if_module','')
        if if_module == "True":
            group_id_for_module = request.POST.get('group_id_for_module','')
        url_name = request.POST.get('url_name','') # used for reverse
        # print "\n\n url_name", url_name
        group_obj = node_collection.one({'_id': ObjectId(group_id)})
        file_uploaded = request.FILES.get("filehive", "")
        pic_rt = request.POST.get("pic_rt", "")
        node_id = request.POST.get("node_id", "")
        # print "\n\n pic_rt === ", pic_rt
        has_profile_or_banner_rt = None
        if pic_rt == "is_banner":
            has_profile_or_banner_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_banner_pic') })
        elif pic_rt == "is_profile":
            has_profile_or_banner_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_profile_pic') })

        if pic_rt == "is_thumbnail":
            # print "================================"
            has_profile_or_banner_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_thumbnail') })
        choose_from_existing_pic = request.POST.get("old_pic_ele","")

        warehouse_grp_obj = node_collection.one({'_type': "Group", 'name': "warehouse"})
        if file_uploaded:
            fileobj = write_files(request,group_id)
            gs_obj_id = fileobj[0]['_id']
            # print "\n\n\nfileobj",gs_obj_id
            if fileobj:
                profile_pic_image = node_collection.one({'_id': ObjectId(gs_obj_id)})
                # The 'if' below is required in case file node is deleted but exists in grid_fs
                if profile_pic_image and not node_id:
                    gr_node = create_grelation(group_obj._id, has_profile_or_banner_rt, profile_pic_image._id)
                    # Move fileobj to "Warehouse" group
                    node_collection.collection.update({'_id': profile_pic_image._id}, {'$set': {'group_set': [warehouse_grp_obj._id] }}, upsert=False, multi=False)
                elif node_id:
                    # print "-----------------------------------------------------------------",node_id
                    gr_node = create_grelation(ObjectId(node_id), has_profile_or_banner_rt, profile_pic_image._id)
                    # Move fileobj to "Warehouse" group
                    node_collection.collection.update({'_id': profile_pic_image._id}, {'$set': {'group_set': [warehouse_grp_obj._id] }}, upsert=False, multi=False)
                else:
                    success_state = False
        elif choose_from_existing_pic:
            # update status of old GRelation
            profile_pic_image = node_collection.one({'_id': ObjectId(choose_from_existing_pic)})
            gr_node = create_grelation(group_obj._id,has_profile_or_banner_rt,profile_pic_image._id)
            # Move fileobj to "Warehouse" group
            if warehouse_grp_obj._id not in profile_pic_image.group_set:
                node_collection.collection.update({'_id': profile_pic_image._id}, {'$set': {'group_set': [warehouse_grp_obj._id] }}, upsert=False, multi=False)
            group_obj.reload()

        if user:
            group_id = user
        if if_module == "True":
            return HttpResponseRedirect(reverse(str(url_name), kwargs={'group_id': ObjectId(group_id_for_module),'node_id':group_obj._id }))
        else:
            return HttpResponseRedirect(reverse(str(url_name), kwargs={'group_id': group_id}))

@get_execution_time
@login_required
def my_courses(request, group_id):

    if str(request.user) == 'AnonymousUser':
        raise Http404("You don't have an authority for this page!")

    try:
        auth_obj = get_group_name_id(group_id, get_obj=True)
        user_id = auth_obj.created_by

    except:
        user_id = eval(group_id)
        auth_obj = node_collection.one({'_type': "Author", 'created_by': user_id})

    auth_id = auth_obj._id
    title = 'My Courses'
    my_course_objs = get_user_course_groups(user_id)
    # print my_course_objs

    return render_to_response('ndf/my-courses.html',
                {
                    'group_id': auth_id, 'groupid': auth_id,
                    'node': auth_obj, 'title': title,
                    'my_course_objs': my_course_objs
                },
                context_instance=RequestContext(request)
        )

@get_execution_time
@login_required
def my_desk(request, group_id):
    from gnowsys_ndf.settings import GSTUDIO_WORKSPACE_INSTANCE

    if str(request.user) == 'AnonymousUser':
        raise Http404("You don't have an authority for this page!")

    try:
        auth_obj = get_group_name_id(group_id, get_obj=True)
        user_id = auth_obj.created_by

    except:
        user_id = eval(group_id)
        auth_obj = node_collection.one({'_type': "Author", 'created_by': user_id})

    auth_id = auth_obj._id
    title = 'my desk'
    
    # modules_cur = node_collection.find({'member_of': gst_module_id  }).sort('last_update', -1)

    # my_course_objs = get_user_course_groups(user_id)
    # module_unit_ids = [val for each_module in modules_cur for val in each_module.collection_set ]

    # modules_cur.rewind()
        # print my_course_objs
    # base_unit_cur = node_collection.find({'member_of': {'$in': [ce_gst._id, announced_unit_gst._id]},
    #                                       'author_set': request.user.id,
    #                                     }).sort('last_update', -1)
    # my_list_unit = []
    # for each in base_unit_cur:
    #     my_list_unit.append(each._id)

    # base_unit_cur.rewind()
    # my_modules_cur = node_collection.find({'member_of': gst_module_id ,'collection_set':{'$in':my_list_unit } }).sort('last_update', -1)
    
    # my_modules = []
    # for each in my_modules_cur:
    #     my_modules.append(each._id)

    list_of_attr = ['first_name', 'last_name', 'enrollment_code', 'organization_name', 'educationallevel']
    auth_attr = auth_obj.get_attributes_from_names_list(list_of_attr)
    auth_profile_exists = all(v not in ['', None] for v in auth_attr.values())
    my_units = node_collection.find(
                {'member_of':
                    {'$in': [ce_gst._id, announced_unit_gst._id, gst_group._id]
                },
                'name': {'$nin': GSTUDIO_DEFAULT_GROUPS_LIST },
                'agency_type': {'$ne': unicode("School")},
                'author_set': request.user.id}).sort('last_update', -1)
    
    query =  {'name': {'$nin': GSTUDIO_DEFAULT_GROUPS_LIST } }
    
    
    if auth_obj.agency_type == "Teacher":
        query.update({'member_of': { '$in' :  [gst_author_id,gst_group._id]},
                     '$or': [
                        {'agency_type': {'$eq': unicode("School")}}, 
                        {'_type': unicode ("Author"),
                         'created_by' : request.user.id,
                        } 
                    ],    
                })
    else:
        query.update({'agency_type': {'$eq': unicode("School")}})
    my_workspaces = node_collection.find(query).sort('last_update', -1)
    
        
    # my_modules_cur.rewind()
    return render_to_response('ndf/lms_dashboard.html',
                {
                    'group_id': auth_id, 'groupid': auth_id,
                    'node': auth_obj, 'title': title,
                    # 'my_course_objs': my_course_objs,
                    'units_cur':my_units,
                    'auth_attr': auth_attr, 'auth_profile_exists': auth_profile_exists,
                    # 'modules_cur': my_modules_cur
                    'workspaces_cur' : my_workspaces,
                },
                context_instance=RequestContext(request)
        )

@get_execution_time
@login_required
def my_groups(request, group_id,page_no=1):

    from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP
    # if request.user == 'AnonymousUser':
        # raise 404

    try:
        auth = get_group_name_id(group_id, get_obj=True)

    except:
        user_id = eval(group_id)
        auth = node_collection.one({'_type': "Author", 'created_by': user_id})
    usrid = auth.created_by
    current_user = usrid
    if current_user:
        exclued_from_public = ""
        if int(current_user) == int(usrid):
          Access_policy=["PUBLIC","PRIVATE"]
        if int(current_user) != int(usrid):
          Access_policy=["PUBLIC"]
    else:
          Access_policy=["PUBLIC"]
          exclued_from_public =  ObjectId(task_gst._id)

    group_cur = node_collection.find(
        {'_type': "Group", 'name': {'$nin': ["home", auth.name]},"access_policy":{"$in":Access_policy}, 'status': u'PUBLISHED',
        '$or': [{'group_admin': int(usrid)}, {'author_set': int(usrid)}]}).sort('last_update', -1)
    group_page_cur = paginator.Paginator(group_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)

    auth_id = auth._id
    title = 'My Groups'

    return render_to_response('ndf/my-groups.html',
                {
                    'group_id': group_id, 'groupid': group_id,
                    'node': auth,
                    'title': title,'group_cur':group_cur,'group_page_cur':group_page_cur
                },
                context_instance=RequestContext(request)
        )

@get_execution_time
@login_required
def my_dashboard(request, group_id):

    user_id = eval(group_id)
    user_obj = User.objects.get(pk=int(user_id))
    auth_obj = node_collection.one({'_type': "Author", 'created_by': user_id})
    auth_id = auth_obj._id
    title = 'My Dashboard'

    cmnts_rcvd_by_user = 0
    analytics_instance = AnalyticsMethods(user_id, user_obj.username, auth_id)

    users_points = analytics_instance.get_users_points()

    # total_cmnts_by_user = analytics_instance.get_total_comments_by_user(site_wide=True)
    total_cmnts_by_user = Author.get_total_comments_by_user(user_id, site_wide=True)

    cmts_on_user_notes = analytics_instance.get_comments_counts_on_users_notes(False, site_wide=True)
    cmts_on_user_files = analytics_instance.get_comments_counts_on_users_files(False, site_wide=True)

    if cmts_on_user_notes or cmts_on_user_files:
        cmnts_rcvd_by_user = cmts_on_user_notes + cmts_on_user_files

    groups_cur = analytics_instance.get_user_joined_groups()
    my_course_objs = get_user_course_groups(user_id)

    del analytics_instance

    return render_to_response('ndf/my_dashboard.html',
                {
                    'group_id': auth_id, 'groupid': auth_id,
                    'node': auth_obj,'user_obj': user_obj,
                    'title': title,'users_points':users_points,
                    'total_cmnts_by_user':total_cmnts_by_user,
                    'cmnts_rcvd_by_user':cmnts_rcvd_by_user,
                    'groups_cur':groups_cur,
                    'my_course_objs': my_course_objs
                },
                context_instance=RequestContext(request)
        )

@get_execution_time
@login_required
def my_performance(request, group_id):
    from gnowsys_ndf.settings import GSTUDIO_WORKSPACE_INSTANCE

    if str(request.user) == 'AnonymousUser':
        raise Http404("You don't have an authority for this page!")

    try:
        auth_obj = get_group_name_id(group_id, get_obj=True)
        user_id = auth_obj.created_by

    except:
        user_id = eval(group_id)
        auth_obj = node_collection.one({'_type': "Author", 'created_by': user_id})

    auth_id = auth_obj._id
    title = 'my performance'
    list_of_attr = ['first_name', 'last_name', 'enrollment_code', 'organization_name', 'educationallevel']
    auth_attr = auth_obj.get_attributes_from_names_list(list_of_attr)
    auth_profile_exists = all(v not in ['', None] for v in auth_attr.values())

    my_units = node_collection.find(
                {'member_of':
                    {'$in': [ce_gst._id, announced_unit_gst._id, gst_group._id]
                },
                'name': {'$nin': GSTUDIO_DEFAULT_GROUPS_LIST },
                'author_set': request.user.id}).sort('last_update', -1)
    return render_to_response('ndf/lms_dashboard.html',
                {
                    'group_id': auth_id, 'groupid': auth_id,
                    'node': auth_obj, 'title': title,
                    # 'my_course_objs': my_course_objs,
                    'units_cur':my_units,
                    'auth_attr': auth_attr, 'auth_profile_exists': auth_profile_exists
                    # 'modules_cur': my_modules_cur
                },
                context_instance=RequestContext(request)
        )

@get_execution_time
@login_required
def save_profile(request, user_id):
    from django.contrib.auth.models import User

    user_dict = {'success': True, 'message': 'Profile updated successfully.'}
    request_variables = {}
    auth_attr = None
    auth_obj = Author.get_author_by_userid(int(user_id))
    try:
        auth_id = auth_obj._id
        if request.method == "POST":

            first_name = request.POST.get('first_name', None)
            last_name = request.POST.get('last_name', None)
            educationallevel = request.POST.get('educationallevel', None)
            organization_name = request.POST.get('organization_name', None)
            enrollment_code = request.POST.get('enrollment_code', None)
            request_variables.update({'first_name': first_name, 'last_name': last_name,
                'educationallevel': educationallevel, 'organization_name': organization_name,
                'enrollment_code': enrollment_code})

            for at_name, ga_val in request_variables.items():
                if ga_val:
                    create_gattribute(auth_id, at_name, ga_val)

            auth_attr = request_variables

    except AttributeError as no_auth:
        # user_dict.update({'success': False, 'message': 'Something went wrong. Please try again later.'})
        pass
    except Exception as no_auth:
        # user_dict.update({'success': False, 'message': 'Something went wrong. Please try again later.'})
        pass
    # return HttpResponse(json.dumps(user_dict))


    return render_to_response('ndf/widget_user_profile.html',
                {
                    'auth_attr': auth_attr, #'user_dict': json.dumps(user_dict)
                },
                context_instance=RequestContext(request)
        )


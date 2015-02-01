''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
from gnowsys_ndf.settings import LANGUAGES
from gnowsys_ndf.notification import models as notification
from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_drawers,get_all_gapps,create_grelation
from gnowsys_ndf.ndf.views.methods import get_user_group, get_user_task, get_user_notification, get_user_activity
from gnowsys_ndf.ndf.views.file import * 
from gnowsys_ndf.settings import META_TYPE,GAPPS,GSTUDIO_SITE_DEFAULT_LANGUAGE
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_all_user_groups

#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
collection_tr = db[Triple.collection_name]
gapp_mt = collection.Node.one({'_type': "MetaType", 'name': META_TYPE[0]})
GST_IMAGE = collection.Node.one({'member_of': gapp_mt._id, 'name': GAPPS[3]})
at_user_pref=collection.Node.one({'$and':[{'_type':'AttributeType'},{'name':'user_preference_off'}]})
ins_objectid  = ObjectId()


#######################################################################################################################################
#                                                                     V I E W S   D E F I N E D   F O R   U S E R   D A S H B O A R D
#######################################################################################################################################


def userpref(request,group_id):
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
    lan_dict={}
    pref=request.POST["pref"]
    fall_back=request.POST["fallback"]
    if pref:
        lan_dict['primary']=pref
        lan_dict['secondary']=fall_back
        lan_dict['default']=GSTUDIO_SITE_DEFAULT_LANGUAGE
        auth.preferred_languages=lan_dict
        auth.modified_by=request.user.id
        auth.save()
    return HttpResponse("Success")
    

@login_required
def uDashboard(request, group_id):
    usrid = group_id

    ID = int(usrid)
    # Fetching user group of current user & then reassigning group_id with it's corresponding ObjectId value
    auth = collection.Node.one({'_type': "Author", 'created_by': ID}, {'name': 1, 'relation_set': 1})
    group_id = auth._id

    group_name = auth.name
    usrname = auth.name

    date_of_join = request.user.date_joined
    current_user = request.user.pk

    has_profile_pic = None
    profile_pic_image = None
    is_already_selected = None

    if request.method == "POST" :
        """
        This will take the image uploaded by user and it searches if its already availale in gridfs 
        using its md5 
        """
        has_profile_pic_str = "has_profile_pic"
        gridfs = get_database()['fs.files']
        pp = None
        
        if has_profile_pic_str in request.FILES:
            pp = request.FILES[has_profile_pic_str]
            has_profile_pic = collection.Node.one({'_type': "RelationType", 'name': has_profile_pic_str})
    
            # Find md5
            pp_md5 = hashlib.md5(pp.read()).hexdigest()

            # Check whether this md5 exists in file collection
            gridfs_node = gridfs.one({'md5': pp_md5})
            if gridfs_node:
                # md5 exists
                right_subject = gridfs_node["docid"]
                
                # Check whether already selected
                is_already_selected = collection.Triple.one(
                    {'subject': auth._id, 'right_subject': right_subject, 'status': u"PUBLISHED"}
                )

                if is_already_selected:
                    # Already selected found
                    # Signify already selected
                    is_already_selected = gridfs_node["filename"]
                
                else:
                    # Already uploaded found
                    # Reset already uploaded as to be selected
                    profile_pic_image = create_grelation(auth._id, has_profile_pic, right_subject)

                profile_pic_image = collection.Node.one({'_type': "File", '_id': right_subject})
            
            else:
                # Otherwise (md5 doesn't exists)
                # Upload image
                # submitDoc(request, group_id)
                field_value = save_file(pp, pp, request.user.id, group_id, "", "", oid=True)[0]
                profile_pic_image = collection.Node.one({'_type': "File", 'name': unicode(pp)})

                # Create new grelation and append it to that along with given user
                gr_node = create_grelation(auth._id, has_profile_pic, profile_pic_image._id)

    dashboard_count={}  
    group_list=[]
    user_activity=[]
    group_cur = collection.Node.find(
        {'_type': "Group", 'name': {'$nin': ["home", request.user.username]}, 
        '$or': [{'group_admin': request.user.id}, {'author_set': request.user.id}],
    }).sort('last_update', -1).limit(10)

    dashboard_count.update({'group':group_cur.count()})  

    GST_PAGE = collection.Node.one({'_type': "GSystemType", 'name': 'Page'})
    page_cur = collection.GSystem.find({'member_of': {'$all': [GST_PAGE._id]}, 'created_by':int(ID)})
    file_cur = collection.Node.find({'_type':  u"File", 'created_by': int(ID) })

    for i in group_cur:
        group_list.append(i)

    # user_task = get_user_task(userObject)
    #user_notification = get_user_notification(userObject)
    #user_activity = get_user_activity(userObject)
    activity = ""
    activity_user = collection.Node.find(
        {'$and':[{'$or':[{'_type':'GSystem'},{'_type':'group'},{'_type':'File'}]},
        {'$or':[{'created_by':request.user.id}, {'modified_by':request.user.id}]}] 
    }).sort('last_update', -1).limit(10)

    a_user = []
    dashboard_count.update({'activity':activity_user.count()})
    
    for i in activity_user:
        if i._type != 'Batch' or i._type != 'Course' or i._type !='Module':
            a_user.append(i)
    
    for each in a_user:
        if each.created_by == each.modified_by :
            if each.last_update == each.created_at:
                activity =  'created'
            else:
                activity =  'modified'
        else:
            activity =  'created'
        
        if each._type == 'Group':
            user_activity.append(each)
        else:
            member_of = collection.Node.find_one({"_id":each.member_of[0]})
            user_activity.append(each)
    
    notification_list=[]    
    notification_object = notification.NoticeSetting.objects.filter(user_id=request.user.id)
    for each in notification_object:
        ntid = each.notice_type_id
        ntype = notification.NoticeType.objects.get(id=ntid)
        label = ntype.label.split("-")[0]
        notification_list.append(label)

    # Retrieving Tasks Assigned for User (Only "New" and "In Progress")
    user_assigned = []
    # attributetype_assignee = collection.Node.find_one({"_type":'AttributeType', 'name':'Assignee'})
    # attr_assignee = collection.Node.find(
    #     {"_type": "GAttribute", "attribute_type.$id": attributetype_assignee._id, "object_value": request.user.id}
    # ).sort('last_update', -1).limit(10)
    
    # dashboard_count.update({'Task':attr_assignee.count()})
    # for attr in attr_assignee :
    #     task_node = collection.Node.one({'_id':attr.subject})
    #     if task_node:   
    #         user_assigned.append(task_node) 
    task_gst = collection.Node.one(
        {'_type': "GSystemType", 'name': "Task"}
    )
    task_cur = collection.Node.find(
        {'member_of': task_gst._id, 'attribute_set.Status': {'$in': ["New", "In Progress"]}, 'attribute_set.Assignee': request.user.id}
    ).sort('last_update', -1).limit(10)

    dashboard_count.update({'Task': task_cur.count()})

    for task_node in task_cur:
        user_assigned.append(task_node)

    obj = collection.Node.find(
        {'_type': {'$in' : [u"GSystem", u"File"]}, 'contributors': int(ID) ,'group_set': {'$all': [ObjectId(group_id)]}}
    )
    collab_drawer = []  
    for each in obj.sort('last_update', -1):    # To populate collaborators according to their latest modification of particular resource:
        for val in each.contributors:
            name = User.objects.get(pk=val).username    
            collab_drawer.append({'usrname':name, 'Id': val,'resource': each.name})   

    shelves = []
    shelf_list = {}

    if not profile_pic_image:
        if auth:
            for each in auth.relation_set:
                if "has_profile_pic" in each:
                    profile_pic_image = collection.Node.one(
                        {'_type': "File", '_id': each["has_profile_pic"][0]}
                    )

                    break

    return render_to_response(
        "ndf/uDashboard.html",
        {
            'usr': current_user, 'username': usrname, 'user_id': ID, 'DOJ': date_of_join, 'author':auth,
            'group_id':group_id, 'groupid':group_id, 'group_name':group_name,
            'already_set': is_already_selected, 'prof_pic_obj': profile_pic_image,
            'group_count':group_cur.count(), 'page_count':page_cur.count(), 'file_count':file_cur.count(),
            'user_groups':group_list, 'user_task': user_assigned, 'user_activity':user_activity,
            'user_notification':notification_list,
            'dashboard_count':dashboard_count
        },
        context_instance=RequestContext(request)
    )

def user_preferences(request,group_id,auth_id):
    try:
        grp=collection.Node.one({'_id':ObjectId(auth_id)})
        if request.method == "POST":
            lst = []
            pref_to_set = request.POST['pref_to_set']
            pref_list=pref_to_set.split(",")
            if pref_list:
                for each in pref_list:
                    if each:
                        obj=collection.Node.one({'_id':ObjectId(each)})
                        lst.append(obj);
                gattribute=collection.Node.one({'$and':[{'_type':'GAttribute'},{'attribute_type.$id':at_user_pref._id},{'subject':grp._id}]})
                if gattribute:
                    gattribute.delete()
                if lst:
                    create_attribute=collection.GAttribute()
                    create_attribute.attribute_type=at_user_pref
                    create_attribute.subject=grp._id
                    create_attribute.object_value=lst
                    create_attribute.save()            
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
            st = collection.Node.find({'$and':[{'_type':'Group'},{'author_set':{'$in':[user_id]}},{'name':{'$nin':all_user_groups}}]})
            data_list=set_drawer_widget(st,list_at_pref)
            return HttpResponse(json.dumps(data_list))
    except Exception as e:
        print "Exception in userpreference view "+str(e)
        return HttpResponse("Failure")

def user_template_view(request,group_id):
    auth_group = None
    group_list=[]
    group_cur = collection.Node.find({'_type': "Group", 'name': {'$nin': ["home", request.user.username]}}).limit(4)
    for i in group_cur:
        group_list.append(i)

    blank_list = []
    attributetype_assignee = collection.Node.find_one({"_type":'AttributeType', 'name':'Assignee'})
    attr_assignee = collection.Node.find({"_type":"GAttribute", "attribute_type.$id":attributetype_assignee._id, "object_value":request.user.username})
    for attr in attr_assignee :
     task_node = collection.Node.find_one({'_id':attr.subject})
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
    activity_user = collection.Node.find({'$and':[{'$or':[{'_type':'GSystem'},{'_type':'Group'},{'_type':'File'}]}, 
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
        member_of = collection.Node.find_one({"_id":each.member_of[0]})
        blank_list.append(each)
    
    
    template = "ndf/task_card_view.html"
    #variable = RequestContext(request, {'TASK_inst': self_task,'group_name':group_name,'group_id': group_id, 'groupid': group_id,'send':send})
    variable = RequestContext(request, {'TASK_inst':blank_list,'group_name':group_id,'group_id': group_id, 'groupid': group_id})
    return render_to_response(template, variable)

@login_required
def user_activity(request, group_id):
    activity_user = collection.Node.find({'$and':[{'$or':[{'_type':'GSystem'},{'_type':'group'},{'_type':'File'}]},
                                                 
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
        member_of = collection.Node.find_one({"_id":each.member_of[0]})
        blank_list.append(each)
    template = "ndf/User_Activity.html"
    #variable = RequestContext(request, {'TASK_inst': self_task,'group_name':group_name,'group_id': group_id, 'groupid': group_id,'send':send})
    variable = RequestContext(request, {'user_activity':blank_list,'group_name':group_id,'group_id': group_id, 'groupid': group_id})
    return render_to_response(template, variable)

def group_dashboard(request, group_id):
    """
    This view returns data required for group's dashboard.
    """
    gridfs = get_database()['fs.files']
    profile_pic_image = None
    has_profile_pic_str = ""
    
    if ObjectId.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        group_ins = collection.Node.find_one({'_type': "Group","_id": ObjectId(group_id)})
        if group_ins:
            group_id = group_ins._id
    
    if request.method == "POST" :
        """
        This will take the image uploaded by user and it searches if its already availale in gridfs 
        using its md5 
        """
        if (request.POST.get('type','')=='banner_pic'):
          has_profile_pic_str = "has_Banner_pic"
        if (request.POST.get('type','')=='profile_pic'):
          has_profile_pic_str="has_profile_pic"  
        
        gridfs = get_database()['fs.files']
        pp = None
        profile_pic_image=""
        if has_profile_pic_str in request.FILES:
            pp = request.FILES[has_profile_pic_str]
            has_profile_pic = collection.Node.one({'_type': "RelationType", 'name': has_profile_pic_str})
            # Find md5
            pp_md5 = hashlib.md5(pp.read()).hexdigest()
            # Check whether this md5 exists in file collection
            gridfs_node = gridfs.one({'md5': pp_md5})
            if gridfs_node:
                # md5 exists
                right_subject = gridfs_node["docid"]
                
                # Check whether already selected
                is_already_selected = collection.Triple.one(
                    {'subject': group_id, 'right_subject': right_subject, 'status': u"PUBLISHED"}
                )

                if is_already_selected:
                    # Already selected found
                    # Signify already selected
                    is_already_selected = gridfs_node["filename"]
                
                else:
                    # Already uploaded found
                    # Reset already uploaded as to be selected
                    profile_pic_image = create_grelation(ObjectId(group_id), has_profile_pic, right_subject)

                profile_pic_image = collection.Node.one({'_type': "File", '_id': right_subject})
            else:
                # Otherwise (md5 doesn't exists)
                # Upload image
                # submitDoc(request, group_id)
                field_value = save_file(pp, pp, request.user.id, group_id, "", "", oid=True)[0]
                profile_pic_image = collection.Node.one({'_type': "File", 'name': unicode(pp)})
                # Create new grelation and append it to that along with given user
                if profile_pic_image:
                    gr_node = create_grelation(group_id, has_profile_pic, profile_pic_image._id)

    banner_pic=""
    group=collection.Node.one({"_id":ObjectId(group_id)})
    for each in group.relation_set:
                if "has_profile_pic" in each:
                    if each["has_profile_pic"]:
                        profile_pic_image = collection.Node.one(
                            {'_type': "File", '_id': each["has_profile_pic"][0]}
                        )
                if "has_Banner_pic" in each:
                    if each["has_Banner_pic"]:
                        banner_pic = collection.Node.one(
                            {'_type': "File", '_id': each["has_Banner_pic"][0]}
                        )

    # Approve StudentCourseEnrollment view
    approval = False
    enrollment_details = []
    enrollment_columns = []

    sce_gst = collection.Node.one({'_type': "GSystemType", 'name': "StudentCourseEnrollment"})
    if sce_gst:
        # Get StudentCourseEnrollment nodes which are there for approval
        sce_cur = collection.Node.find({
            'member_of': sce_gst._id, 'group_set': ObjectId(group_id),
            "attribute_set.enrollment_status": {"$nin": [u"OPEN"]},
            'status': u"PUBLISHED"
        }, {
            'member_of': 1
        })

        if sce_cur.count():
            approval = True
            enrollment_columns = ["College", "Course", "Completed On", "Status", "Enrolled", "Remaining", "Approved", "Rejected"]
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
            'group_id': group_id, 'groupid': group_id,
            'approval': approval, 'enrollment_columns': enrollment_columns, 'enrollment_details': enrollment_details,'prof_pic_obj': profile_pic_image,'banner_pic':banner_pic,'page':page
        },
        context_instance=RequestContext(request)
    )


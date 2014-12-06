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
from gnowsys_ndf.ndf.views.methods import get_drawers,get_all_gapps
from gnowsys_ndf.ndf.views.methods import get_user_group, get_user_task, get_user_notification, get_user_activity
from gnowsys_ndf.ndf.views.file import * 
from gnowsys_ndf.settings import GAPPS,GSTUDIO_SITE_DEFAULT_LANGUAGE
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_all_user_groups

#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
collection_tr = db[Triple.collection_name]
GST_IMAGE = collection.GSystemType.one({'name': GAPPS[3]})
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
    

# def dashboard(request, group_id, usrid):  
#     ins_objectid  = ObjectId()
#     if ins_objectid.is_valid(group_id) is False :
#         group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
#         auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
#         if group_ins:
#             group_id = str(group_ins._id)
#         else :
#             auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
#             if auth :
#                 group_id = str(auth._id)
#     else :
#         group_ins = collection.Node.find_one({'_type': "Group","_id": ObjectId(group_id)})
#         pass

#     ID = int(usrid)
#     usrname = User.objects.get(pk=ID).username
#     date_of_join = request.user.date_joined
#     current_user = request.user.pk

#     auth = collection.Node.one({'_type': 'Author', 'name': unicode(usrname) })
#     prof_pic = collection.Node.one({'_type': u'RelationType', 'name': u'has_profile_pic'})
#     uploaded = "None"

#     if request.method == "POST" :
#       """
#       This will take the image uploaded by user and it searches if its already available in gridfs 
#       using its md5 
#       """     
#       for index, each in enumerate(request.FILES.getlist("has_profile_pic", "")):
#           fcol = db[File.collection_name]
#       fileobj = fcol.File()
#       filemd5 = hashlib.md5(each.read()).hexdigest()
#       if fileobj.fs.files.exists({"md5":filemd5}):
#         coll = get_database()['fs.files']
#         a = coll.find_one({"md5":filemd5})
#         # prof_image takes the already available document of uploaded image from its md5 
#         prof_image = collection.Node.one({'_type': 'File', '_id': ObjectId(a['docid']) })

#       else:
#         # If uploaded image is not found in gridfs stores this new image 
#             submitDoc(request, group_id)
#             # prof_image takes the already available document of uploaded image from its name
#             prof_image = collection.Node.one({'_type': 'File', 'name': unicode(each) })

#       # prof_img takes already available relation of user with its profile image
#       prof_img = collection.GRelation.one({'subject': ObjectId(auth._id), 'right_subject': ObjectId(prof_image._id) })
#       # If prof_img not found then it creates the relation of new uploaded image with its user
#       if not prof_img:
#         prof_img = collection.GRelation()
#         prof_img.subject = ObjectId(auth._id) 
#         prof_img.relation_type = prof_pic
#         prof_img.right_subject = ObjectId(prof_image._id)
#         prof_img.save()
#       else:
#         obj_img = collection.Node.one({'_id': ObjectId(prof_img.right_subject) })
#         uploaded = obj_img.name

#     page_drawer = get_drawers(group_id,None,None,"Page")
#     image_drawer = get_drawers(group_id,None,None,"Image")
#     video_drawer = get_drawers(group_id,None,None,"Video")
#     file_drawer = get_drawers(group_id,None,None,"File")
#     quiz_drawer = get_drawers(group_id,None,None,"OnlyQuiz")
#     group_drawer = get_drawers(None,None,None,"Group")
#     forum_drawer = get_drawers(group_id,None,None,"Forum")
    
#     obj = collection.Node.find({'_type': {'$in' : [u"GSystem", u"File"]}, 'contributors': int(ID) ,'group_set': {'$all': [ObjectId(group_id)]}})
    
#     collab_drawer = []    
#     for each in obj.sort('last_update', -1):    # To populate collaborators according to their latest modification of particular resource:
#       for val in each.contributors:
#         name = User.objects.get(pk=val).username    
#         collab_drawer.append({'usrname':name, 'Id': val,'resource': each.name})   

#     shelves = []
#     shelf_list = {}
#     if auth:
#       dbref_profile_pic = prof_pic.get_dbref()
#       prof_pic_rel = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_profile_pic })        

#       # prof_pic_rel will get the cursor object of relation of user with its profile picture 
#       if prof_pic_rel.count() :
#         index = prof_pic_rel.count() - 1
#         Index = prof_pic_rel[index].right_subject
#         # img_obj = collection.Node.one({'_type': 'File', '_id': ObjectId(prof_pic_rel['right_subject']) })      
#         img_obj = collection.Node.one({'_type': 'File', '_id': ObjectId(Index) })      
#       else:
#         img_obj = "" 


#       has_shelf_RT = collection.Node.one({'_type': 'RelationType', 'name': u'has_shelf' })
#       dbref_has_shelf = has_shelf_RT.get_dbref()

#       shelf = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_has_shelf })        

#       if shelf:
#         for each in shelf:
#           shelf_name = collection.Node.one({'_id': ObjectId(each.right_subject)})           
#           shelves.append(shelf_name)

#           shelf_list[shelf_name.name] = []         
#           for ID in shelf_name.collection_set:
#             shelf_item = collection.Node.one({'_id': ObjectId(ID) })
#             shelf_list[shelf_name.name].append(shelf_item.name)

#       else:
#         shelves = []

#     return render_to_response("ndf/userDashboard.html",
#                               {'username': usrname, 'user_id': ID, 'DOJ': date_of_join, 
#                                'prof_pic_obj': img_obj,'group': group_ins,
#                                'group_id':group_id, 'usr': current_user,             
#                                'author':auth,
#                                'already_uploaded': uploaded,
#                                'shelf_list': shelf_list,'shelves': shelves,
#                                'page_drawer':page_drawer,'image_drawer': image_drawer,
#                                'video_drawer':video_drawer,'file_drawer': file_drawer,
#                                'quiz_drawer':quiz_drawer,'group_drawer': group_drawer,
#                                'forum_drawer':forum_drawer,'collab_drawer': collab_drawer,
#                                'groupid':group_id
#                               },
#                               context_instance=RequestContext(request)
#     )

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
      print "notification details"
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

    # Approve StudentCourseEnrollment view
    approval = False
    enrollment_details = []
    enrollment_columns = []

    sce_gst = collection.Node.one({'_type': "GSystemType", 'name': "StudentCourseEnrollment"})
    if sce_gst:
        sce_cur = collection.Node.find(
            {'member_of': sce_gst._id, 'group_set': ObjectId(group_id), 'status': u"PUBLISHED"},
            {'member_of': 1}
        )

        if sce_cur.count():
            approval = True
            enrollment_columns = ["College", "Course", "Completed On", "Status", "Enrolled", "Remaining", "Approved", "Rejected"]
            for sce_gs in sce_cur:
                sce_gs.get_neighbourhood(sce_gs.member_of)
                data = {}

                approve_task = sce_gs.has_corresponding_task[0]
                approve_task.get_neighbourhood(approve_task.member_of)
                data["Status"] = approve_task.Status
                # Check for corresponding task's status
                # Continue with next if status is found as "Closed"
                # As we listing only 'In Progress'/'New' task(s)
                if data["Status"] == "Closed":
                    continue

                data["_id"] = str(sce_gs._id)
                data["College"] = sce_gs.for_college[0].name
                data["Course"] = sce_gs.for_acourse[0].name
                data["Completed On"] =  sce_gs.completed_on.strftime("%d/%m/%Y")
                
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

    return render_to_response (
        "ndf/group_dashboard.html",
        {
            'group_id': group_id, 'groupid': group_id,
            'approval': approval, 'enrollment_columns': enrollment_columns, 'enrollment_details': enrollment_details
        },
        context_instance=RequestContext(request)
    )


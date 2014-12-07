from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from gnowsys_ndf.ndf.models import get_database
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget_for_users
from gnowsys_ndf.notification import models as notification
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_all_user_groups

import json

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


db = get_database()
col_Group = db[Node.collection_name]
sitename=Site.objects.all()[0]
def get_userobject(user_id):
    bx=User.objects.filter(id=user_id)
    if bx:
        bx=User.objects.get(id=user_id)
        return bx
    else:
        return 0

def get_user(username):
    bx=User.objects.filter(username=username)
    if bx:
        bx=User.objects.get(username=username)
        return bx
    else:
        return 0


# A general function used to send all kinds of notifications
def set_notif_val(request,group_id,msg,activ,bx):
    try:
        group_obj=col_Group.Group.one({'_id':ObjectId(group_id)})
        site=sitename.name.__str__()
        objurl="http://test"
        render = render_to_string("notification/label.html",{'sender':request.user.username,'activity':activ,'conjunction':'-','object':group_obj,'site':site,'link':objurl})
        notification.create_notice_type(render, msg, "notification")
        notification.send([bx], render, {"from_user": request.user})
        return True
    except Exception as e:
        print "Error in sending notification- "+str(e)
        return False

# Send invitation to any user to join or unsubscribe
def send_invitation(request,group_id):
    try:
        colg=col_Group.Group.one({'_id':ObjectId(group_id)})
        groupname=colg.name
        list_of_invities=request.POST.get("users","") 
        sender=request.user
        sending_user=User.objects.get(id=sender.id)
        list_of_users=list_of_invities.split(",")
        activ="invitation to join in group"

        msg="'This is to inform you that " +sending_user.username+ " has subscribed you to the group " +groupname+"'"

        ret=""
        for each in list_of_users:
            bx=User.objects.get(id=each)
            ret = set_notif_val(request,group_id,msg,activ,bx)
            if bx.id not in colg.author_set:
                colg.author_set.append(bx.id)
                colg.save()
        if ret :
            return HttpResponse("success")
        else:
            return HttpResponse("failure")
    except Exception as e:
        print str(e)
        return HttpResponse(str(e))


def notifyuser(request,group_id):
#    usobj=User.objects.filter(username=usern)
    colg=col_Group.Group.one({'_id':ObjectId(group_id)})
    groupname=colg.name
    activ="joined in group"
    msg="You have successfully joined in the group '"+ groupname +"'"
    bx=get_user(request.user)
    ret = set_notif_val(request,group_id,msg,activ,bx)
    if not ((bx.id in colg.author_set) or (bx.id==colg.created_by)):
        colg.author_set.append(bx.id)
        colg.modified_by = int(request.user.id)
        colg.save()
    if ret :
        return HttpResponse("success")
    else:
        return HttpResponse("failure")


def notify_remove_user(request,group_id):
    colg=col_Group.Group.one({'_id':ObjectId(group_id)})
    groupname=colg.name
    msg="You have been removed from the group '"+ groupname +"'"
    activ="removed from group"
    bx=get_user(request.user)
    ret = set_notif_val(request,group_id,msg,activ,bx)
    colg.author_set.remove(bx.id)
    colg.modified_by = int(request.user.id)
    colg.save()
    if ret:
        return HttpResponse("success")
    else:
        return HttpResponse("failure")

def invite_users(request,group_id):
    try:
        sending_user=request.user
        node=col_Group.Node.one({'_id':ObjectId(group_id)})
        if request.method == "POST":
            exst_users=[]
            new_users=[]
            users=[]
            deleted_users=node.author_set
            groupname=node.name
            users_to_invite = request.POST['users']
            not_status=request.POST['notif_status']
            new_users_list=users_to_invite.split(",")
            for each in new_users_list:
                if each :
                    users.append(int(each))
            if users:
                for each in users:
                    if each in node.author_set:
                        exst_users.append(each)
                    else:
                        if each not in node.author_set:
                            new_users.append(each)
                            node.author_set.append(each);
                node.save()
                
                # Send invitations according to not_status variable
                activ="invitation to join in group"
                if not_status == "ON":
                    for each in exst_users:
                        bx=User.objects.get(id=each)
                        msg="'This is to inform you that " +sending_user.username+ " has subscribed you to the group " +groupname+"'"
                        set_notif_val(request,group_id,msg,activ,bx)
                for each in new_users:
                    bx=User.objects.get(id=each)
                    msg="'This is to inform you that " +sending_user.username+ " has subscribed you to the group " +groupname+"'"
                    set_notif_val(request,group_id,msg,activ,bx)
            deleted_users=set(deleted_users)-set(users)
            activ="Unsubscribed from group"
            if deleted_users:
                for each in deleted_users:
                    bx=User.objects.get(id=each)
                    node.author_set.remove(each)
                    msg="'This is to inform you that " +sending_user.username+ " has unsubscribed you from the group " +groupname+"'"
                    set_notif_val(request,group_id,msg,activ,bx)
                node.save()
            return HttpResponse("Success")
        else:
            coll_obj_list = []
            lstusers=[]
            owner=node.created_by
            users=User.objects.all().order_by("email")
            user_names=[]
            st=[]
            for each in users:
                if each.id != owner and each.id not in node.author_set:
                   st.append(each)
                else:
                    if each.id !=owner:
                        coll_obj_list.append(each)

            data_list=set_drawer_widget_for_users(st,coll_obj_list)
            return HttpResponse(json.dumps(data_list))
   
    except Exception as e:
        print "Exception in invite_users "+str(e)
        return HttpResponse("Failure")

def invite_admins(request,group_id):
    try:
        sending_user=request.user
        node=col_Group.Node.one({'_id':ObjectId(group_id)})
        if request.method == "POST":
            exst_users=[]
            new_users=[]
            users=[]
            deleted_users=node.group_admin
            groupname=node.name
            users_to_invite = request.POST['users']
            not_status=request.POST['notif_status']
            new_users_list=users_to_invite.split(",")
            for each in new_users_list:
                if each :
                    users.append(int(each))
            if users:
                for each in users:
                    if each in node.group_admin:
                        exst_users.append(each)
                    else:
                        if each not in node.group_admin:
                            new_users.append(each)
                            node.group_admin.append(each);
                node.save()
                
                # Send invitations according to not_status variable
                activ="invitation to join in group"
                if not_status == "ON":
                    for each in exst_users:
                        bx=User.objects.get(id=each)
                        msg="'This is to inform you that " +sending_user.username+ " has subscribed you to the group " +groupname+" as admin'"
                        set_notif_val(request,group_id,msg,activ,bx)
                for each in new_users:
                    bx=User.objects.get(id=each)
                    msg="'This is to inform you that " +sending_user.username+ " has subscribed you to the group " +groupname+" as admin'"
                    set_notif_val(request,group_id,msg,activ,bx)
            deleted_users=set(deleted_users)-set(users)
            activ="Unsubscribed from group"
            if deleted_users:
                for each in deleted_users:
                    bx=User.objects.get(id=each)
                    node.group_admin.remove(each)
                    msg="'This is to inform you that " +sending_user.username+ " has unsubscribed you from the group " +groupname+" as admin'"
                    set_notif_val(request,group_id,msg,activ,bx)
                node.save()
            return HttpResponse("Success")
        else:
            coll_obj_list = []
            lstusers=[]
            owner=node.created_by
            users=User.objects.all().order_by("email")
            user_names=[]
            st=[]
            user_grps=get_all_user_groups()
            usergrps=[]
            for each in user_grps:
                usergrps.append(each.created_by)
            for each in users:
                if each.id != owner and each.id not in node.group_admin and each.id in usergrps:
                   st.append(each)
                else:
                    if each.id !=owner and each.id in usergrps:
                        coll_obj_list.append(each)

            data_list=set_drawer_widget_for_users(st,coll_obj_list)
            return HttpResponse(json.dumps(data_list))
   
    except Exception as e:
        print "Exception in invite_admins in notify view "+str(e)
        return HttpResponse("Failure")

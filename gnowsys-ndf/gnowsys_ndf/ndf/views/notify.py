from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from gnowsys_ndf.ndf.models import get_database
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.notification import models as notification
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


db = get_database()
col_Group = db[Group.collection_name]
sitename=Site.objects.all()[0]
def get_user(username):
    bx=User.objects.filter(username=username)
    if bx:
        bx=User.objects.get(username=username)
        return bx
    else:
        return 0


# A general function used to send all kind of notifications
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
        print "Error in sending notification-",e
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

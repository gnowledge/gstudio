from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from gnowsys_ndf.ndf.models import get_database
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.notification import models as notification
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

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



def set_notif_val(request,group_name,msg,activ,bx):
    try:
        obj=group_name
        site=sitename.name.__str__()
        objurl="http://test"
        render = render_to_string("notification/label.html",{'sender':username,'activity':activ,'conjunction':'-','object':obj,'site':site,'link':objurl})
        notification.create_notice_type(render, msg, "notification")
        notification.send([bx], render, {"from_user": request.user})
        return True
    except:
        return False

# Send invitation to any user
def send_invitation(request,group_name):
    try:
        list_of_invities=request.POST.get("users","") 
        sender=request.user
        sending_user=User.objects.get(id=sender.id)
        list_of_users=list_of_invities.split(",")
        activ="invitation to join in group"
        msg="'This is to inform you that " +str(sending_user.username)+ " has subscribed you to the group " +str(group_name)+"'"

        colg = col_Group.Group.one({'name':group_name})
        ret=""
        for each in list_of_users:
            bx=User.objects.get(id=each)
            ret = set_notif_val(request,group_name,msg,activ,bx)
            colg.author_set.append(bx.id)
            colg.save()
        if ret :
            return HttpResponse("success")
        else:
            return HttpResponse("failure")
    except Exception as e:
        return HttpResponse(str(e))

def notifyuser(request,group_name):
#    usobj=User.objects.filter(username=usern)
    activ="joined in group"
    msg="You have successfully joined in the group '"+str(group_name)+"'"
    bx=get_user(request.user)
    ret = set_notif_val(request,group_name,msg,activ,bx)
    colg = col_Group.Group.one({'name':group_name})
    if not ((bx.id in colg.author_set) or (bx.id==colg.created_by)):
        colg.author_set.append(bx.id)
        colg.save()
    if ret :
        return HttpResponse("success")
    else:
        return HttpResponse("failure")


def notify_remove_user(request,group_name):
    msg="You have been removed from the group '"+str(group_name)+"'"
    activ="removed from group"
    bx=get_user(request.user)
    ret = set_notif_val(request,group_name,msg,activ,bx)
    col_Group = db[Group.collection_name]
    colg = col_Group.Group.one({'name':group_name})
    colg.author_set.remove(bx.id)
    colg.save()
    if ret:
        return HttpResponse("success")
    else:
        return HttpResponse("failure")

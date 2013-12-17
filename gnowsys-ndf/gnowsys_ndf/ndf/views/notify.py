from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from gnowsys_ndf.ndf.models import get_database
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.notification import models as notification
from django.contrib.auth.models import User
from django.template.loader import render_to_string

db = get_database()
col_Group = db[Group.collection_name]

def get_user(username):
    bx=User.objects.filter(username=username)
    if bx:
        bx=User.objects.get(username=username)
        return bx
    else:
        return 0



def set_notif_val(request,group_name,msg,activ,bx):
    try:
        username=request.user
        obj=group_name
        site="sample"
        objurl="sample"
        render = render_to_string("notification/label.html",{'sender':username,'activity':activ,'conjunction':'-','object':obj,'site':site,'oburl':objurl})
        notification.create_notice_type(render, msg, "notification")
        notification.send([bx], render, {"from_user": request.user})
        return True
    except:
        return False

def notifyuser(request,group_name):
#    usobj=User.objects.filter(username=usern)
    activ="joined in group"
    msg="You have successfully joined in the group '"+str(group_name)+"'"
    bx=get_user(request.user)
    ret = set_notif_val(request,group_name,msg,activ,bx)
    colg = col_Group.Group.one({'name':group_name})
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

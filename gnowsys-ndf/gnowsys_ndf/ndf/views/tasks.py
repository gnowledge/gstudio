from celery import task
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from gnowsys_ndf.notification import models as notification
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.models import node_collection, triple_collection
import json

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

sitename = Site.objects.all()[0]

@task
def task_set_notify_val(request_user_id, group_id, msg, activ, to_user):
    '''
        Attach notification mail to celery task
    '''
    request_user = User.objects.get(id=request_user_id)
    to_send_user = User.objects.get(id=to_user)
    try:
        group_obj = node_collection.one({'_id': ObjectId(group_id)})
        site = sitename.name.__str__()
        objurl = "http://test"
        render = render_to_string(
            "notification/label.html",
            {
                'sender': request_user.username,
                'activity': activ,
                'conjunction': '-',
                'object': group_obj,
                'site': site,
                'link': objurl
            }
        )
        notification.create_notice_type(render, msg, "notification")
        notification.send([to_send_user], render, {"from_user": request_user})
        return True
    except Exception as e:
        print "Error in sending notification- "+str(e)
        return False


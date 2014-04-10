import datetime
import json
import pickle
from django.contrib.auth.models import User
from gnowsys_ndf.notification import models as notification
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

def migrate():
   """ test """
   fp=open("cube_users","r")
   usernames=[]
   userids=[]
   for each in User.objects.all():
      usernames.append(each.username)
      userids.append(each.id)
   line = pickle.loads(fp.read())
   userobj=User.objects.all()[0]
   msg1="Your user account with username '"
   msg2="' has been migrated from cube.metastudio.org to www.metastudio.org"
   msg3="\nIncase you forgot your password, please use 'change password' option to change it.\nFrom now on, please use the site www.metastudio.org . All the resources from beta.metastudio.org will be migrated to this site."
   name=userobj.username
   activ="migrating users"
   site=Site.objects.all()[0]
   sender=name
   for each in line:
      b=each
      a=User()
      if not each['username'] in usernames:
         if each['id'] in userids:
            b['id']=max(userids)+1
         a.__dict__=b
         a.save()
         bx=User.objects.get(username=each['username'])
         msg=msg1+bx.username+msg2+msg3
         render = render_to_string("notification/label.html",{'sender':name,'activity':activ,'conjunction':'-','object':'','site':site,'lin#k':''})
         notification.create_notice_type(render, msg, "notification")
#         notification.send([bx], render, {"from_user": sender})
   fp.close()




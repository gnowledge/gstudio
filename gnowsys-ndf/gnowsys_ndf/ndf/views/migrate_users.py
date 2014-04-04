""" test """
import datetime
import json
import pickle
from django.contrib.auth.models import User
def migrate():
   """ test """
   fp=open("nroer_user_data","r")   
   usernames=[]
   userids=[]
   for each in User.objects.all():
      usernames.append(each.username)
      userids.append(each.id)
   line = pickle.loads(fp.read())
   for each in line:
      b=each
      a=User()
      if not each['username'] in usernames:
         if each['id'] in userids:
            b['id']=max(userids)+1
         a.__dict__=b
         a.save()   
   fp.close()   




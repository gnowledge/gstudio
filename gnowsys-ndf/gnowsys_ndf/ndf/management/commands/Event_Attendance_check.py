from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.models import GSystem
from gnowsys_ndf.ndf.views.methods import  create_gattribute
from datetime import date,time,timedelta
from gnowsys_ndf.ndf.views.notify import set_notif_val
from gnowsys_ndf.notification import models as notification
collection = get_database()[Node.collection_name]

Event =collection.Node.find({"name":{'$in':["Classroom Session","Exam"]}})

yesterday = date.today() - timedelta(1)
day_before_yesterday=date.today() - timedelta(2)
date1=datetime.date.today()
ti=time(0,0)
Today=datetime.datetime.combine(date1,ti)
yesterday=datetime.datetime.combine(yesterday,ti)
day_before_yesterday=datetime.datetime.combine(day_before_yesterday,ti)
no_of_days=0

#get the Mis Admin
Mis_admin=collection.Node.one({"_type":"Group","name":"MIS_admin"})
Mis_admin_name=""
if  Mis_admin:
    Mis_admin_list=Mis_admin.group_admin
    Mis_admin_list.append(Mis_admin.created_by)
    user_obj = User.objects.get(id=Mis_admin.created_by)
    Mis_admin_name=user_obj.username
try:
    Attendance_Event=collection.Node.find({"member_of":{'$in':[ObjectId(Event[0]._id),ObjectId(Event[1]._id)]},"attribute_set.end_time":    {'$gte':day_before_yesterday}})

    Attendance_marked_event=collection.Node.find({"member_of":{'$in':[ObjectId(Event[0]._id),ObjectId(Event[1]._id)]},"relation_set.has_attended":{"$exists":False},"attribute_set.start_time":{'$gte':yesterday,'lt':Today}})

    reschedule_attendance=collection.Node.one({"name":"reschedule_attendance"})
    
    for i in Attendance_Event:
      create_gattribute(ObjectId(i._id),reschedule_attendance,False)

    for i in Attendance_marked_event:
      for j in i.attribute_set:
        if unicode("start_time") in j.keys():
             if (j["start_time"] >= day_before_yesterday and j["start_time"] <  yesterday):
                no_of_days=2
             if (j["start_time"] >=  yesterday and j["start_time"] < Today):
                no_of_days=1
              
      to_user_list=[]
      node=collection.Node.one({"_id":{'$in':i.group_set}})
      for j in node.group_admin:
        user_obj = User.objects.get(id=j)
        if user_obj not in to_user_list:
                to_user_list.append(user_obj)
        render_label = render_to_string(
              "notification/label.html",
              {
                  "sender": Mis_admin_name,
                  "activity": "Attendance not marked",
                  "conjunction": "-"
              })
        notification.create_notice_type(render_label,"Attendance is not marked"+ i.name +"\n Please enter marks in \n Attendance would be blocked after"+ no_of_days+"days" , "notification")
        notification.send(to_user_list, render_label, {"from_user": Mis_admin_name})
except Exception as e:
    error_message = "\n Event Error: " + str(e) + " !!!\n"
    raise Exception(error_message)
    
  
  


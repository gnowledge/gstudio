from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.models import GSystem
from gnowsys_ndf.ndf.views.methods import  create_gattribute
from datetime import date,time,timedelta
from gnowsys_ndf.ndf.views.notify import set_notif_val
from django.template.loader import render_to_string
from gnowsys_ndf.notification import models as notification
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = " This script will Close Attendance Capabilities of Any Event Which is Two days old" 
    "it will also send email to the from the day the event is held and the next day of it"  
    "as a reminder to enter the marks"
    "the email would go PO of the Group and the voluntry teacher of the event"

    

    def handle(self, *args, **options):

          collection = get_database()[Node.collection_name]

          Event = collection.Node.find({"_type":"GSystemType","name":{'$in':["Classroom Session","Exam"]}})

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
          
          
              
           
          Attendance_Event = collection.Node.find({"member_of":{'$in':[ObjectId(Event[0]._id),ObjectId(Event[1]._id)]},"attribute_set.start_time":{'$gte':day_before_yesterday,'$lt':Today}})

          rescheduled_Attendance_events=collection.Node.find({"member_of":{'$in':[ObjectId(Event[0]._id),ObjectId(Event[1]._id)]},"attribute_set.reschedule_attendance.reschedule_till":{'$gt':yesterday}})
          
          rescheduled_events = collection.Node.find({"member_of":{'$in':[ObjectId(Event[0]._id),ObjectId(Event[1]._id)]},"attribute_set.event_edit_reschedule.reschedule_till":{'$gt':yesterday}}) 
          
          Attendance_marked_event = collection.Node.find({"member_of":{'$in':[ObjectId(Event[0]._id),ObjectId(Event[1]._id)]},"relation_set.has_attended":{"$exists":False},"attribute_set.start_time":{'$gte':yesterday,'lt':Today}})

          reschedule_attendance = collection.Node.one({"_type":"AttributeType","name":"reschedule_attendance"})
          
          reschedule_event=collection.Node.one({"_type":"AttributeType","name":"event_edit_reschedule"})
          
          reschedule_dates = {}
          for i in Attendance_Event:
             for j in i.attribute_set:
               if unicode('reschedule_attendance') in j.keys():
                  reschedule_dates = j['reschedule_attendance']
             reschedule_dates["reschedule_allow"] = False
             create_gattribute(ObjectId(i._id),reschedule_attendance,reschedule_dates)
              
          reschedule_dates={}
          for i in rescheduled_events:
              for j in i.attribute_set:
                       if unicode('event_edit_reschedule') in j.keys():
                         reschedule_dates = j['event_edit_reschedule']
              reschedule_dates['reschedule_allow'] = False
              create_gattribute(ObjectId(i._id),reschedule_event,reschedule_dates)
              
          reschedule_dates={}
          for i in rescheduled_Attendance_events:
             for j in i.attribute_set:
               if unicode('reschedule_attendance') in j .keys():
                  reschedule_dates = j['reschedule_attendance']
               reschedule_dates["reschedule_allow"] = False
             create_gattribute(ObjectId(i._id),reschedule_attendance,reschedule_dates)

          
          for i in Attendance_marked_event:
            event_status = collection.Node.one({"_type":"AttributeType","name":"event_status"})
            create_gattribute(ObjectId(i._id),event_status,unicode('Incomplete'))
            
            for j in i.attribute_set:
              if unicode("start_time") in j.keys():
                   if (j["start_time"] >= day_before_yesterday and j["start_time"] <  yesterday):
                      no_of_days = 2
                   if (j["start_time"] >=  yesterday and j["start_time"] < Today):
                      no_of_days = 1
                    
            to_user_list=[]
            #node is the node of the college Group
            node = collection.Node.one({"_type":"Group","_id":{'$in':i.group_set}})
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
              notification.create_notice_type(render_label,"Attendance is not marked for "+ i.name +" Event \n Attendance would be blocked after" + str(no_of_days) + "days" , "notification")
              notification.send(to_user_list, render_label, {"from_user": Mis_admin_name})
       
              
            
            


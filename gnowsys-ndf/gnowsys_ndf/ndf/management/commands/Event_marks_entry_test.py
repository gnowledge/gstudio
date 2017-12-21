from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.models import GSystem
from gnowsys_ndf.ndf.views.methods import  create_gattribute
from datetime import date,time,timedelta
from django.template.loader import render_to_string
from gnowsys_ndf.ndf.views.notify import set_notif_val
from gnowsys_ndf.notification import models as notification
from django.template import RequestContext
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

collection = get_database()[Node.collection_name]

class Command(BaseCommand):

    help = " This script will send Email All the Events whos marks are not entered"
    

    def handle(self, *args, **options):
            Event = collection.Node.find({"_type":"GSystemType","name":{'$in':["Classroom Session","Exam"]}})

            marks_enter = collection.Node.find({"member_of":{'$in':[ObjectId(Event[0]._id),ObjectId(Event[1]._id)]},"attribute_set.marks_entered":True})
            Mis_admin = collection.Node.one({"_type":"Group","name":"MIS_admin"})
            Mis_admin_name=""
            if  Mis_admin:
                Mis_admin_list = Mis_admin.group_admin
                Mis_admin_list.append(Mis_admin.created_by)
                user_obj = User.objects.get(id=Mis_admin.created_by)
                Mis_admin_name = user_obj.username

            for i in marks_enter:
              to_user_list = []
              event_status = collection.Node.one({"_type":"AttributeType","name":"event_status"})
              create_gattribute(ObjectId(i._id),event_status,unicode('Incomplete'))
              node = collection.Node.one({"_id":{'$in':i.group_set}})
              for j in node.group_admin:
                 user_obj = User.objects.get(id = j)
                 if user_obj not in to_user_list:
                   to_user_list.append(user_obj)
                   render_label = render_to_string(
                          "notification/label.html",
                          {
                              "sender": Mis_admin_name,
                              "activity": "Marks not entered",
                              "conjunction": "-"
                          })
                 notification.create_notice_type(render_label," Marks is not entered for Event" + i.name +"\n Please enter marks soon"   , "notification")
                 notification.send(to_user_list, render_label, {"from_user": Mis_admin_name})



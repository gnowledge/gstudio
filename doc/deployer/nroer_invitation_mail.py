from django.template.loader import render_to_string
from django.contrib.auth.models import User
from gnowsys_ndf.notification import models as notification
from gnowsys_ndf.ndf.models import *

def send_notifications():
	'''
	Send an email notification to users of the platform
	'''
	try:
		list_of_users_ids = []
		# list_of_users_ids will hold django ids of all old site nroer imported users

		user_objs = []
		# user_objs will hold django user objects of list_of_users_ids
		# sorted in ascending order on id

		target_users = []
		# target_users will hold specific number of django user objects of user_objs

		# target_users and user_objs is kept separate with 
		# a purpose to select a range of users(target_users) from all user_objs 

		with open('success_log.csv') as f:
			for indexval,eachrow in enumerate(f):
				if indexval>9 : # and not len(list_of_users_ids) > 100:
					list_of_items = eachrow.split(",")
					list_of_users_ids.append(str(list_of_items[1]))

		user_objs = User.objects.filter(id__in=list_of_users_ids).order_by('id')
		# order_by ensures user objects to be fetched in same sequence always
		target_users = user_objs[:100] # 21-12-2015  -- Mail Sending to Top '5' Users
		print "\n Preparing to send Mail to Top 100 users"
		site_var = "nroer.gov.in"
		render_label = render_to_string("notification/label.html",{"sender": site_var,"activity": "NROER WC","conjunction": "-",'site':site_var,'link':site_var})

		notification_msg = "As curators and developers of the National Repository of Open Educational " \
			+ "Resources (NROER) we have great pleasure in announcing the readiness of a new platform for " \
			+ "NROER. Please visit http://nroer.gov.in  to explore the many new features and benefit from " \
			+ "the multiple ways resources have been curated.\n\nYou have received this mail because you are " \
			+ "a registered user of NROER. Your login details have not changed. "\
			+ "Your login email is the same as the one on which you have received this mail." \
			+ "\n\nIf you have forgotten your password, please access " \
			+ "http://nroer.gov.in/accounts/password/reset/ to reset it. " \
			+ "\n\nOnce logged in, update your profile by visiting your dashboard which can be accessed " \
			+ "by clicking on your name in the menu bar. " \
			+ "\n\nIf you need any assistance, please contact us at nroer.support@gnowledge.org." \
			+ "\n\nWe look forward to hearing from you. You can add your feedback at " \
			+ "http://nroer.gov.in/home/page/5665aa9681fccb03424ffcda"

		for eachuser_obj in target_users:
			notification.create_notice_type(render_label,"\nDear "+str(eachuser_obj.username)+",\n\t " + notification_msg + "\n\nWith best regards,\nNROER Team", "notification")
			notification.send([eachuser_obj], render_label, {"from_user": "NROER Team"})
		print "\n Successfully sent Mail to Top 100 users"
	except Exception as e:
		return "Error occurred while sending NROER Welcome notification  " + str(e)

send_notifications()
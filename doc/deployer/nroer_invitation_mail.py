from django.template.loader import render_to_string
from django.contrib.auth.models import User
from gnowsys_ndf.notification import models as notification
from gnowsys_ndf.ndf.models import *


def send_notifications():
	'''
	Fetch all django user objects
	order_by is applied in order to ensure user_objs seq remain same always
	'''
	try:
		# Update the following comment whenever this script is run
		# Notifications sent to -- '0' No. of Users -- 17-12-2015
		user_objs = User.objects.order_by('id')
		target_users = user_objs[:2]
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

		for each_user in target_users:
			if each_user:
				notification.create_notice_type(render_label,"\nDear "+str(each_user.username)+",\n\t " + notification_msg + "\n\nWith best regards,\nNROER Team", "notification")
				notification.send([each_user], render_label, {"from_user": "NROER Team"})
	except ValueError as ve:
		return "Please enter proper values"
	except Exception as e:
		return "Error occurred while sending NROER Welcome notification  " + str(e)

send_notifications()
from django.contrib.auth.models import User
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id
from report_error import error_message

def authenticate_user(mail,group_name):
	id = -1
	try:
		id = User.objects.get(email=mail).id
	except:
		return id,False,error_message["User does not exist"]
	
	# Extracting lists of all groups
	gst_group = node_collection.find({'_type':u'Group'})
	group_list = []
	
	for each in gst_group:
		group_list.append(each.name)

	if(group_name in group_list):
		gst_home = get_group_name_id(group_name,get_obj=True)
		if(id in gst_home.author_set):
			return id,True,error_message["User authenticated"]
		else:	
			return id,False,error_message["User not a member of this group"]
	else:
		return id,False,error_message["Group does not exist"]
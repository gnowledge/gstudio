from django.contrib.auth.models import User
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id

def authenticate_user(user,group_name):
	id = -1
	try:
		id = User.objects.get(username=user).id
		print user
	except:
		print 'User with this username does not exists'
		return id,False
	
	# Extracting lists of all groups
	gst_group = node_collection.find({'_type':u'Group'})
	group_list = []
	
	for each in gst_group:
		group_list.append(each.name)

	if(group_name in group_list):
		gst_home = get_group_name_id(group_name,get_obj=True)
		if(id in gst_home.author_set):
			return id,True
		else:	
			print 'User not a member of this group'
			return id,False
	else:
		#create that group
		print 'Group name does not exist, Please create the group'
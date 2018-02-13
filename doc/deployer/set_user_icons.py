import os
import io
import time
from django.http import HttpRequest
from django.contrib.auth.models import User
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH
from gnowsys_ndf.ndf.views.filehive import *
from gnowsys_ndf.ndf.views.methods import create_grelation

warehouse_grp = node_collection.one({'_type': "Group", 'name': "warehouse"})
file_gst = node_collection.one({'_type': "GSystemType", 'name': "File"})
has_profile_pic_rt = node_collection.one({'_type': 'RelationType', 'name': unicode('has_profile_pic') })


if not os.path.exists(GSTUDIO_LOGS_DIR_PATH):
	os.makedirs(GSTUDIO_LOGS_DIR_PATH)

log_file_name = 'set_user_icons.log'
log_file_path = os.path.join(GSTUDIO_LOGS_DIR_PATH, log_file_name)
log_file = open(log_file_path, 'a+')
script_start_str = "######### Script ran on : " + time.strftime("%c") + " #########\n----------------\n"
log_file.write(str(script_start_str))

path = '/home/docker/code/display-pics/'
if not os.path.exists(path):
	path = str(raw_input("Enter path of directory containing icons : "))

# path = "/tmp/User_icons/final-student-teacher-icon-set-and-usernames/color-student-usernames"
try:
	if os.path.exists(path):
		print "\n Path exists"
		for each_img_name in os.listdir(path):
			each_img_name_wo_ext = each_img_name.split('.')[0]
			user_id_list = User.objects.filter(username__contains=str(each_img_name_wo_ext)).values_list('id', flat=True)
			user_id_list = list(user_id_list)
			# print type(user_id_list)
			auth_nodes = node_collection.find({'_type': "Author", 'created_by': {'$in': user_id_list}})
			# print auth_nodes.count()
			if user_id_list and auth_nodes.count():
				file_obj_in_str = open(path+'/'+each_img_name,'r+')
				img_file = io.BytesIO(file_obj_in_str.read())
				img_file.seek(0)
				fh_obj = filehive_collection.collection.Filehive()
				filehive_obj_exists = fh_obj.check_if_file_exists(img_file)
				file_gs_obj = None
				if not filehive_obj_exists:
					file_gs_obj = node_collection.collection.GSystem()

					file_gs_obj.fill_gstystem_values(
													request=HttpRequest(),
													name=unicode(each_img_name_wo_ext),
													group_set=[warehouse_grp._id],
													# language=language,
													uploaded_file=img_file,
													created_by=1,
													member_of=file_gst._id,
													origin={'user-icon-list-path':str(path)},
													unique_gs_per_file=True
											)

					file_gs_obj.save(groupid=warehouse_grp._id)
				else:
					file_gs_obj = node_collection.one({'_type':"GSystem", '$or': [
								{'if_file.original.id':filehive_obj_exists._id},
								{'if_file.mid.id':filehive_obj_exists._id},
								{'if_file.thumbnail.id':filehive_obj_exists._id}]})


				# create GRelation 'has_profile_pic' with respective Author nodes
				if file_gs_obj:
					for each_auth in auth_nodes:
						gr_node = create_grelation(each_auth._id, has_profile_pic_rt, file_gs_obj._id)
						print "\n File : ", file_gs_obj.name , " -- linked -- ", each_auth.name
						log_file.write("\n File : " + str(file_gs_obj.name) + " -- linked -- "+ str(each_auth.name))

			else:
				print "\n Either Users or Authors with file name : ", str(each_img_name_wo_ext), "does NOT exist."
	else:
		print "\n No such path exists."


except Exception as user_icon_err:
	print "\n Error occurred!!!" + str(user_icon_err)
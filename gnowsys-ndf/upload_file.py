import os
import io
import time
from django.http import HttpRequest
from django.contrib.auth.models import User
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GSTUDIO_LOGS_DIR_PATH
from gnowsys_ndf.ndf.views.filehive import *
from gnowsys_ndf.ndf.views.methods import create_grelation

home_grp = node_collection.one({'_type': "Group", 'name':u'home'})
file_gst = node_collection.one({'_type': "GSystemType", 'name': u'File'})

each_img_name = 'abcd.png'
each_img_name_wo_ext = each_img_name.split('.')[0]
path = '.'

if not os.path.exists(path):
	print os.listdir('.')
	print "directory doesn't exist"
	#path = str(raw_input("Enter path of directory containing icons : "))

try:
	file_obj_in_str = open(path+'/'+each_img_name,'r+')
except:
	print "can't open"

img_file = io.BytesIO(file_obj_in_str.read())
img_file.seek(0)
fh_obj = filehive_collection.collection.Filehive()
filehive_obj_exists = fh_obj.check_if_file_exists(img_file)
file_gs_obj = None

if not filehive_obj_exists:
	file_gs_obj = node_collection.collection.GSystem()

	file_gs_obj.fill_gstystem_values(
									request=None,
									name=unicode(each_img_name_wo_ext),
									group_set=[home_grp._id],
									# language=language,
									uploaded_file=img_file,
									created_by=1156051,
									member_of=[file_gst._id],
									origin={'user-icon-list-path':str(path)},
									unique_gs_per_file=True
									)
	print "\n\nGS obj id "+str(file_gs_obj._id)+"\n\n"
	try:
		# file_gs_obj.save(groupid=home_grp._id)
		file_gs_obj.save(groupid=home_grp._id)
	except Exception as e:
		print 'exception while saving', e

	try:
		print file_gs_obj
	except:
		print "can't show object"
else:
	print "file exists"
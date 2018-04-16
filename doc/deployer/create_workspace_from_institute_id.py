from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID ,GSTUDIO_INSTITUTE_NAME

workspace_name = GSTUDIO_INSTITUTE_ID+"-"+GSTUDIO_INSTITUTE_NAME
gst_group_id = node_collection.one({'_type': 'GSystemType', 'name': 'Group'})._id
group_obj = node_collection.one({'_type': 'Group', 'name': unicode(GSTUDIO_INSTITUTE_ID)})
if GSTUDIO_INSTITUTE_ID and GSTUDIO_INSTITUTE_NAME: 
	if not group_obj:
		group_obj = node_collection.collection.Group()
		group_obj.name = unicode(GSTUDIO_INSTITUTE_ID.strip())
		group_obj.altnames = unicode(workspace_name.strip())
		group_obj.content = unicode("Welcome to CLIx workspace!\n Here all students and teachers in your school can collaboratively work to create interesting learning content.\nYou can create activity pages and lessons, write e-Notes, upload and share files such as images, audios, videos, Turtle projects, GeoGebra projects, PhET simulations, CLIx Apps. You can take help from other CLIx modules under Explore section.\n\n Unleash the fun of learning by creation :)\n")
		group_obj.access_policy = u"PUBLIC"
		group_obj.subscription_policy=u"OPEN"
		group_obj.group_type = u"PUBLIC"
		group_obj.created_by = 1
		group_obj.modified_by = 1
		group_obj.contributors = [1]
		group_obj.author_set = [1]
		group_obj.encryption_policy = u"NOT_ENCRYPTED"
		group_obj.disclosure_policy = u"DISCLOSED_TO_MEM"
		group_obj.edit_policy = u"EDITABLE_NON_MODERATED"
		group_obj.status = u"PUBLISHED"
		group_obj.visibility_policy = u"ANNOUNCED"
		group_obj.member_of = [gst_group_id]
		group_obj.agency_type = u"School"
		group_obj.origin.append({'source': 'create_workspace_from_institute_id'})

		group_obj.save()
		print "workspace created:",group_obj.altnames
	else:
		print "\n Already exists Group: ", workspace_name
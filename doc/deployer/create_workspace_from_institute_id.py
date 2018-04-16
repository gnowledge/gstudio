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

		group_obj.save()
		print "workspace created:",group_obj.altnames
	else:
		print "\n Already exists Group: ", workspace_name
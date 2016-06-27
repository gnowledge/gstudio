from gnowsys_ndf.ndf.models import *
from report_error import error_message
import send_page

def create_page(**kwargs): 
	p = node_collection.collection.GSystem()

	if kwargs.has_key('group_name'):
		group_name = kwargs.get('group_name','home')
	else:
		group_name = 'home'
	group_name = unicode(group_name)

	if kwargs.has_key('name'):
		name = kwargs.get('name','')
	else:
		return error_message["Page Content required"]
	name = unicode(name)

	if kwargs.has_key('content'):
		content = kwargs.get('content','')
	else:
		return error_message["Page name required"]
	content = unicode(content)

	if kwargs.has_key('created_by'):
		created_by = kwargs.get('created_by','')
	else:
		return error_message["User details required"]

	if kwargs.has_key('sendMailTo'):
		sendMailTo = kwargs.get('sendMailTo','')
	else:
		sendMailTo = 'ps.mio.bits@gmail.com'

	gst_page = node_collection.one({'_type':u'GSystemType','name':u'Page'})
	gst_group = node_collection.one({'_type':u'Group','name':group_name})

	available_nodes = node_collection.find({'_type': u'GSystem', 'member_of': ObjectId(gst_page._id),
		'group_set': ObjectId(gst_group._id)})

	nodes_list = []
	for each in available_nodes:
		nodes_list.append(str((each.name).strip().lower()))

	if name in nodes_list:
		return error_message["already exists"]
	else:
		p.fill_gstystem_values(name = name,member_of=[gst_page._id],created_by = created_by,
			content = content,group_set=[gst_group._id])
		
		send_page.send_page(to_user=sendMailTo,page_name=name,
				page_content=content)

		p.save()
		return 0;



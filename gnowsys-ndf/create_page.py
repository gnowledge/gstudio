from gnowsys_ndf.ndf.models import *

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
		print "Page name required"
	name = unicode(name)

	if kwargs.has_key('content'):
		content = kwargs.get('content','')
	else:
		print "Page Content required"
	content = unicode(content)

	if kwargs.has_key('created_by'):
		created_by = kwargs.get('created_by','')
	else:
		print "User details required"


	gst_page = node_collection.one({'_type':u'GSystemType','name':u'Page'})
	gst_group = node_collection.one({'_type':u'Group','name':group_name})

	available_nodes = node_collection.find({'_type': u'GSystem', 'member_of': ObjectId(gst_page._id),
		'group_set': ObjectId(gst_group._id)})

	nodes_list = []
	for each in available_nodes:
		nodes_list.append(str((each.name).strip().lower()))

	if name in nodes_list:
		print "Page with same name already exists in this group"
	else:
		p.fill_gsystem_values(name = name,member_of=[gst_page._id],created_by = created_by,
			content = content,group_set=[gst_group._id])
		p.save()
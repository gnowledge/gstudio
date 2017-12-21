from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import create_gattribute
try:
	page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
	blogpage_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"})
	blog_pages = node_collection.find({'member_of':page_gst._id, 'type_of': blogpage_gst._id}).sort('created_at', -1)
	twist_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Twist'})
	rel_resp_at = node_collection.one({'_type': 'AttributeType', 'name': 'release_response'})
	print "\n Total blog pages found: ",blog_pages.count()

	for each_blog_page in blog_pages:
		if each_blog_page.relation_set:
			for each_rel in each_blog_page.relation_set:
				if each_rel and "has_thread" in each_rel:
					thread_node_obj = node_collection.one({'_id': ObjectId(each_rel['has_thread'][0])})
					if thread_node_obj:
						if thread_node_obj.attribute_set:
							create_gattribute(thread_node_obj._id, rel_resp_at, True)
except Exception as e:
	print "\n Exception occurred : ", str(e), " !!!"
	pass


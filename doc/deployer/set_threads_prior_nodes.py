from gnowsys_ndf.ndf.models import *

has_thread_RT = node_collection.one({'_type': 'RelationType', 'name': 'has_thread'})
has_thread_grelations = triple_collection.find({'_type': 'GRelation', 'relation_type': has_thread_RT._id})

for each_has_thread_grelations in has_thread_grelations:
	thread_node_id = each_has_thread_grelations.right_subject
	node_id = each_has_thread_grelations.subject
	thread_node = node_collection.one({'_id': ObjectId(thread_node_id)})
	node_obj = node_collection.one({'_id': ObjectId(node_id)})
	# Update prior_node field of thread node
	if (not thread_node.prior_node) or (node_id not in thread_node.prior_node):
		thread_node.prior_node.append(node_id)
		thread_node.save()
	if (not node_obj.post_node) or (thread_node_id not in node_obj.post_node):
		node_obj.post_node.append(node_id)
		node_obj.save()
	print ".",
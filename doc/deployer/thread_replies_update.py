from gnowsys_ndf.ndf.models import *
twist_gst = node_collection.one({'_type': "GSystemType", 'name': "Twist"})
reply_gst = node_collection.one({'_type': "GSystemType", 'name': "Reply"})
qip_gst = node_collection.one({ '_type': 'GSystemType', 'name': 'QuizItemPost'})
twist_cur = node_collection.find({'member_of': twist_gst._id})

print "\n Total threads found: ", twist_cur.count()
print "\n Latest script ======================"
def get_replies(node_id, list_of_user_ids,thread_id, nested=False):
	reply_cur = node_collection.find({'member_of': {'$in': [reply_gst._id, qip_gst._id]}, 'prior_node': ObjectId(node_id)})
	# if not list_of_user_ids and reply_cur.count():
	# 	print "\n First level comments -- ", reply_cur.count()
	# if nested:
	# 	print "\n Nested-- ", reply_cur.count()
	for each_reply in reply_cur:
		thread_id_val = None
		thread_pnid_val = thread_prior_node_id_val = None
		thread_pn_node_id_exists = thread_id_exists = False
		each_reply_origin = each_reply.origin

		thread_obj = node_collection.one({'_id': ObjectId(thread_id)})

		if thread_obj.prior_node:
			thread_prior_node_id_val = thread_obj.prior_node[0]

		if each_reply.created_by:
			list_of_user_ids.append(each_reply.created_by)

		for each_val in each_reply_origin:
			if type(each_val) == dict:
				if 'thread_id' in each_val:
					# thread_id_val = each_val['thread_id']
					thread_id_exists = True
				if 'prior_node_id_of_thread' in each_val:
					# thread_pnid_val = each_val['prior_node_id_of_thread']
					thread_pn_node_id_exists = True
		print "\n\n thread_id_exists ",thread_id_exists
		print "\n\n thread_pn_node_id_exists ",thread_pn_node_id_exists

		if not thread_id_exists or not each_reply.origin:
			each_reply_origin.append({'thread_id': ObjectId(thread_id)})
		if thread_prior_node_id_val:
			if not thread_pn_node_id_exists or not each_reply.origin:
				each_reply_origin.append({'prior_node_id_of_thread': thread_prior_node_id_val})
		print "\n each_reply.origin",each_reply.origin
		print "\n each_reply_origin",each_reply_origin
		if each_reply_origin:
			each_reply.origin = each_reply_origin
			each_reply.save()
		# Update origin field of each_reply with {'thread_id': ObjectId(thread_id)}
		get_replies(each_reply._id, list_of_user_ids, thread_id, nested=True)
	# print "\n\n Total list_of_user_ids length ", len(list_of_user_ids)
	return list_of_user_ids



list_of_replies = []
for each_twist in twist_cur:
	user_ids = []
	list_of_ids = get_replies(each_twist._id, user_ids, each_twist._id)
	if list_of_ids:
		print "\n length of list_of_ids ", len(list_of_ids), " --- \n", each_twist._id, "\n"
		distinct_list_of_ids = list(set(list_of_ids))
		print "\n Distinct -- length of list_of_ids ", len(distinct_list_of_ids), " --- \n", each_twist._id, "\n"
		# print "\n length of list_of_ids ", len(list_of_ids), " --- \n", list_of_ids, "\n"
		# Update thread instance's author_set field with list_of_ids
		if distinct_list_of_ids:
			each_twist.author_set = distinct_list_of_ids
		each_twist.save()
	else:
		print "\n No comments found"

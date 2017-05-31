from gnowsys_ndf.ndf.models import *
twist_gst = node_collection.one({'_type': "GSystemType", 'name': "Twist"})
has_thread_rt = node_collection.one({'_type': 'RelationType', 'name': 'has_thread'})
reply_gst = node_collection.one({'_type': "GSystemType", 'name': "Reply"})
# get all has_thread grel having status deleted
del_has_thread_grel = triple_collection.find({'relation_type': has_thread_rt._id, 'status': 'DELETED'})

# for ref.
node_and_del_thread = {each_thread.right_subject:each_thread.subject for each_thread in del_has_thread_grel}
del_has_thread_grel.rewind()
# find all its right_subj i.e thread nodes
del_thread_node_ids = [each_thr.right_subject for each_thr in del_has_thread_grel]
# fetch thread only if it has any comments attached to it
del_thread_cur = node_collection.find({'_id': {'$in': del_thread_node_ids}, 'author_set': {'$ne': []}})
print "\ndel_thread_cur: ", del_thread_cur.count()

# if yes find related/newly created thread obj ('PUBLISHED')
# attach the comments to the newly created thread obj
for each_th_obj in del_thread_cur:
	# print "\neach_th_obj.author_set: ", each_th_obj.author_set, " -- ", each_th_obj._id
	subj_id = node_and_del_thread[each_th_obj._id]
	pub_has_thread_grel = triple_collection.find_one({'relation_type': has_thread_rt._id, 
		'subject': subj_id, 'status': 'PUBLISHED'})
	# print "\n ObjectId(pub_has_thread_grel.right_subject): ", ObjectId(pub_has_thread_grel.right_subject)

	triples_of_del_th = triple_collection.find({'subject': each_th_obj._id, '_type': 'GAttribute'})
	triple_collection.collection.update({'subject': each_th_obj._id, '_type': 'GAttribute'},
	{'$set': {'subject': ObjectId(pub_has_thread_grel.right_subject)}},upsert=False, multi=True)
	pub_thread_res = node_collection.collection.update({
		'_id': ObjectId(pub_has_thread_grel.right_subject)},
		{'$addToSet': {'author_set': {'$each': each_th_obj.author_set}}},
		upsert=False, multi=False)
	print "\npub_thread_res: ", pub_thread_res
	del_thread_replies = node_collection.collection.update({
		'prior_node': each_th_obj._id, 'member_of': reply_gst._id},
		{'$set': {'prior_node': [ObjectId(pub_has_thread_grel.right_subject)],
		'origin': [{u'thread_id': ObjectId(pub_has_thread_grel.right_subject)}]}},
		upsert=False, multi=True)
	print "\ndel_thread_replies: ", del_thread_replies
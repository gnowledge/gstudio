from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import create_gattribute
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
print "\nTotal Old Threads holding comments references: ", del_thread_cur.count()

# if yes find related/newly created thread obj ('PUBLISHED')
# attach the comments to the newly created thread obj
for each_th_obj in del_thread_cur:
	# print "\neach_th_obj.author_set: ", each_th_obj.author_set, " -- ", each_th_obj._id
	subj_id = node_and_del_thread[each_th_obj._id]
	pub_has_thread_grel = triple_collection.find_one({'relation_type': has_thread_rt._id, 
		'subject': subj_id, 'status': 'PUBLISHED'})
	# print "\n ObjectId(pub_has_thread_grel.right_subject): ", ObjectId(pub_has_thread_grel.right_subject)

	triples_of_del_th = triple_collection.find({'subject': each_th_obj._id, '_type': 'GAttribute'})
	print create_gattribute(ObjectId(pub_has_thread_grel.right_subject), 'release_response', True)
	# triple_collection.collection.update({'subject': each_th_obj._id, '_type': 'GAttribute'},
	# {'$set': {'subject': ObjectId(pub_has_thread_grel.right_subject)}},upsert=False, multi=True)
	pub_thread_res = node_collection.collection.update({
		'_id': ObjectId(pub_has_thread_grel.right_subject)},
		{'$addToSet': {'author_set': {'$each': each_th_obj.author_set}}},
		upsert=False, multi=False)
	print "\nPublished Thread updates result: ", pub_thread_res
	del_thread_replies = node_collection.collection.update({
		'prior_node': each_th_obj._id, 'member_of': reply_gst._id},
		{'$set': {'prior_node': [ObjectId(pub_has_thread_grel.right_subject)],
		'origin': [{u'thread_id': ObjectId(pub_has_thread_grel.right_subject)}]}},
		upsert=False, multi=True)
	print "\nDeleted Thread updates result: ", del_thread_replies

th = node_collection.find({'member_of': twist_gst._id})
print "\n Total threads: ", th.count()
th_ids = [e._id for e in th]
rel_resp_at = node_collection.one({'_type': 'AttributeType', 'name': 'release_response'}) 
tr = triple_collection.find({'attribute_type': rel_resp_at._id, 'subject': {'$in': th_ids}})
th_with_rel_resp = [e.subject for e in tr ] 
print "\n Threads having release_response set: ", len(th_with_rel_resp)
th_ids_with_no_rel_resp = set(th_ids) - set(th_with_rel_resp)
print "\n Threads NOT having release_response set: ", len(th_ids_with_no_rel_resp)
th_ids_with_no_rel_resp = list(th_ids_with_no_rel_resp)
for each_th_with_no_rel_resp in th_ids_with_no_rel_resp:
	create_gattribute(ObjectId(each_th_with_no_rel_resp), 'release_response', True)
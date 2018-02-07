from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import create_grelation


twist_gst = node_collection.one({'_type':"GSystemType", 'name': "Twist"})
twist_cur = node_collection.find({'member_of': twist_gst._id, 'relation_set.thread_of':{'$exists': False}})
print "\n Total threads found without thread_of -- ", twist_cur.count()
has_thread_rt = node_collection.one({"_type": "RelationType", "name": u"has_thread"})

for eachtw in twist_cur:
	if eachtw.prior_node:
		for eachprior_node_id in eachtw.prior_node:
			prior_node_id = eachprior_node_id
			prior_node_obj = node_collection.one({'_id': ObjectId(prior_node_id)})
			if "Forum" in prior_node_obj.member_of_names_list:
				gr = create_grelation(prior_node_obj._id, has_thread_rt, eachtw._id)
				break

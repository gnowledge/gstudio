from gnowsys_ndf.ndf.models import *

def set_prior_nodes_from_collection_set(node_obj):
	print "\n Name : ", node_obj.name, " -- ", node_obj.member_of_names_list , " --- ", node_obj._id
	if node_obj.collection_set:
		for each in node_obj.collection_set:
			each_obj = node_collection.one({'_id': ObjectId(each)})
			# if "Page" in each_obj.member_of_names_list:
			# 	print "\n\n Page -- ", each_obj.prior_node
			if node_obj._id not in each_obj.prior_node:
				each_obj.prior_node.append(node_obj._id)
				each_obj.save()
			set_prior_nodes_from_collection_set(each_obj)

ce_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseEventGroup"})
course_event_grps = node_collection.find({'member_of': ce_gst._id})

for eachce in course_event_grps:
	set_prior_nodes_from_collection_set(eachce)


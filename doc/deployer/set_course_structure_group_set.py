from gnowsys_ndf.ndf.models import *

'''
Fetch all CourseEvent Groups.
Updated all nested nodes' (CourseSectionEvent,
 CourseSubSectionEvent, CourseUnitEvent) group_set
 with the corresponding CourseEventGroup ObjectId
'''
try:
	ce_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseEventGroup"})
	all_ceg = node_collection.find({'member_of': ce_gst._id })
	print "\n Total CourseEventGroups found = ", all_ceg.count()

	for each_ceg in all_ceg:
		if each_ceg.collection_set:
			for each_cs in each_ceg.collection_set:
				cs_node = node_collection.one({'_id': ObjectId(each_cs)})
				if cs_node and 'group_set' in cs_node:
					if each_ceg._id in cs_node.group_set:
						pass
					else:
						cs_node.group_set.append(each_ceg._id)
						cs_node.save()
					if cs_node.collection_set:
						for each_css in cs_node.collection_set:
							css_node = node_collection.one({'_id': ObjectId(each_css)})
							if css_node and 'group_set' in css_node:
								if each_ceg._id in css_node.group_set:
									pass
								else:
									css_node.group_set.append(each_ceg._id)
									css_node.save()
								if css_node.collection_set:
									for each_cu in css_node.collection_set:
										cu_node = node_collection.one({'_id': ObjectId(each_cu)})
										if cu_node and 'group_set' in cu_node:
											if each_ceg._id in cu_node.group_set:
												pass
											else:
												cu_node.group_set.append(each_ceg._id)
												cu_node.save()
											if cu_node.collection_set:
												for each_res in cu_node.collection_set:
													res_node = node_collection.one({'_id': ObjectId(each_res)})
													if res_node and 'group_set' in res_node:
														if each_ceg._id in res_node.group_set:
															pass
														else:
															res_node.group_set.append(each_ceg._id)
															res_node.save()

	print "\n ********* Update Complete Successfully********* \n"
except Exception as group_set_update_exception:
	print "\n ********* Update Failed ********* \n"
	print "\n Error : ", group_set_update_exception
	

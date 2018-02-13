from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import delete_node 

video_js_test_named_files = node_collection.find({'name': {'$regex': 'video-js-test', '$options': 'i'}, '_type': 'GSystem'})

asset_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Asset'})
asset_cur = node_collection.find({'member_of': asset_gst._id})

for e in asset_cur:
	d,dd = delete_node(node_id=e._id, deletion_type=1)
	print d

for e in video_js_test_named_files:
	d,dd = delete_node(node_id=e._id, deletion_type=1)
	print d

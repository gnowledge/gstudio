from gnowsys_ndf.ndf.models import node_collection, GSystemType
from gnowsys_ndf.ndf.views.methods import get_all_iframes_of_unit
# domain = raw_input("Enter domain name/IP: ")
domain = "https://localhost"
# domain = "https://staging-clix.tiss.edu"
gst_announced_unit_name, gst_announced_unit_id = GSystemType.get_gst_name_id("announced_unit")
announced_unit_cur = node_collection.find({'member_of': gst_announced_unit_id})
for each_ann_unit in announced_unit_cur:
	get_all_iframes_of_unit(each_ann_unit, domain)
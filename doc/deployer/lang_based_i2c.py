state_lang_map = {
	'mz': 'en',
	'rj': 'hi',
	'cg': 'hi',
	'tg': 'te',
}
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID

ce_gst_name, ce_gst_id = GSystemType.get_gst_name_id("CourseEventGroup")

# group_type
# access_policy
lang_val = [value for key, value in state_lang_map.items() if key in GSTUDIO_INSTITUTE_ID]
lang_tuple = get_language_tuple(lang_val[0])
ce_to_be_displayed_cur = node_collection.find({'member_of': ce_gst_id, 
	'group_type': u'PRIVATE', 'access_policy': u'PRIVATE', 'language': lang_tuple
})
ce_to_be_hidden_cur = node_collection.find({'member_of': ce_gst_id, 
	'group_type': u'PUBLIC', 'access_policy': u'PUBLIC',
	'language': {'$ne': lang_tuple}
})

print "\n Released ", ce_to_be_displayed_cur.count(), " course(s) for ", lang_val[0]
for each_show_ce in ce_to_be_displayed_cur:
	each_show_ce.access_policy = u"PUBLIC"
	each_show_ce.group_type = u"PUBLIC"
	each_show_ce.save()

print "\n Hiding ", ce_to_be_hidden_cur.count(), " course(s) for NON ", lang_val[0]
for each_hide_ce in ce_to_be_hidden_cur:
	each_hide_ce.access_policy = u"PRIVATE"
	each_hide_ce.group_type = u"PRIVATE"
	each_hide_ce.save()
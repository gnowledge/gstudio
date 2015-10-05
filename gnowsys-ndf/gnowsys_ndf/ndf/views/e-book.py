import json

''' -- imports from installed packages -- ''' 
from django.shortcuts import render_to_response
from django.template import RequestContext
# from django.core.urlresolvers import reverse
from mongokit import paginator


try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
# from gnowsys_ndf.ndf.models import Node, GRelation, GSystemType, File, Triple
from gnowsys_ndf.ndf.models import node_collection
# from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id, cast_to_data_type, get_execution_time
from gnowsys_ndf.ndf.views.methods import get_filter_querydict


# GST_IMAGE = node_collection.one({'_type':'GSystemType', 'name': u"Image"})
ebook_gst = node_collection.one({'_type':'GSystemType', 'name': u"E-Book"})
GST_FILE = node_collection.one({'_type':'GSystemType', 'name': u"File"})
GST_PAGE = node_collection.one({'_type':'GSystemType', 'name': u'Page'})

@get_execution_time
def ebook_listing(request, group_id, page_no=1):
	from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP
	import urllib

	try:
		group_id = ObjectId(group_id) 
	except: 
		group_name, group_id = get_group_name_id(group_id)

	selfilters = urllib.unquote(request.GET.get('selfilters', ''))
	# print "===\n", selfilters, "===\n"
	query_dict = [{}]
	if selfilters:
		selfilters = json.loads(selfilters)
		query_dict = get_filter_querydict(selfilters)
	# else:
	# 	query_dict.append({'collection_set': {'$exists': "true", '$not': {'$size': 0} }})
        
	# print "\n----\n", query_dict
	# all_ebooks = node_collection.find({
	# 		# "_type": "File",
	# 		# "attribute_set.educationaluse": "eBooks",
	# 		'$and': query_dict,
	# 		'collection_set': {'$exists': "true", '$not': {'$size': 0} }
	# 	})

	all_ebooks = node_collection.find({												
								'member_of': {'$in': [GST_FILE._id, GST_PAGE._id]},
								# '_type': 'File',
								# 'fs_file_ids': {'$ne': []}, 
								'group_set': {'$in': [ObjectId(group_id)]},
								'attribute_set.educationaluse': 'eBooks',
								'$and': query_dict,
								'$or': [
										{ 'access_policy': u"PUBLIC" },
										{ '$and': [
													{'access_policy': u"PRIVATE"}, 
													{'created_by': request.user.id}
												]
										}
									],
								'collection_set': {'$exists': "true", '$not': {'$size': 0} }
								}).sort("last_update", -1)

	ebooks_page_info = paginator.Paginator(all_ebooks, page_no, GSTUDIO_NO_OF_OBJS_PP)

	return render_to_response("ndf/ebook.html", {
								"all_ebooks": all_ebooks, "ebook_gst": ebook_gst,
								"page_info": ebooks_page_info, "title": "eBooks",
								"group_id": group_id, "groupid": group_id
								}, context_instance = RequestContext(request))

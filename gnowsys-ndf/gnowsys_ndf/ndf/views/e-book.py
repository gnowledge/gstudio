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
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import Node, GRelation,GSystemType,File,Triple
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id, cast_to_data_type,get_execution_time


GST_FILE = node_collection.one({'_type':'GSystemType', 'name': "File"})
ebook_gst = node_collection.one({'_type':'GSystemType', 'name': "E-Book"})
GST_IMAGE = node_collection.one({'_type':'GSystemType', 'name': GAPPS[3]})
GST_VIDEO = node_collection.one({'_type':'GSystemType', 'name': GAPPS[4]})
e_library_GST = node_collection.one({'_type':'GSystemType', 'name': 'E-Library'})
pandora_video_st = node_collection.one({'_type':'GSystemType', 'name': 'Pandora_video'})
app = node_collection.one({'_type':'GSystemType', 'name': 'E-Library'})

@get_execution_time
def ebook_listing(request, group_id, page_no=1):

	group_name, group_id = get_group_name_id(group_id)

	all_ebooks = node_collection.find({"_type": "File", "attribute_set.educationaluse": "eBooks"})
	# all_ebook = node_collection.find({"_type": "File", "member_of": {"$in":[gst_ebook._id]} })


	# return render_to_response("ndf/page_list.html",
 #                                {'title': "E-Book", 
 #                                 'appId':app._id,
 								# 	'shelf_list': shelf_list,'shelves': shelves,
 #                                 'searching': True, 'query': search_field,
 #                                 'page_nodes': all_ebook, 'groupid':group_id, 'group_id':group_id
 #                                }, 
 #                                context_instance=RequestContext(request) )

	return render_to_response("ndf/ebook.html",
								{"all_ebooks": all_ebooks, "group_id": group_id, "groupid": group_id},
								context_instance = RequestContext(request))

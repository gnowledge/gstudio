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
from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP
# from gnowsys_ndf.ndf.models import Node, GRelation, GSystemType, File, Triple
from gnowsys_ndf.ndf.models import node_collection
# from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.views.methods import get_group_name_id, cast_to_data_type,get_execution_time


# GST_IMAGE = node_collection.one({'_type':'GSystemType', 'name': u"Image"})
ebook_gst = node_collection.one({'_type':'GSystemType', 'name': u"E-Book"})


@get_execution_time
def ebook_listing(request, group_id, page_no=1):

	try:
		group_id = ObjectId(group_id) 
	except: 
		group_name, group_id = get_group_name_id(group_id)
        
	all_ebooks = node_collection.find({"_type": "File", "attribute_set.educationaluse": "eBooks", 'collection_set': {'$exists': "true", '$not': {'$size': 0} }})

	ebooks_page_info = paginator.Paginator(all_ebooks, page_no, GSTUDIO_NO_OF_OBJS_PP)

	return render_to_response("ndf/ebook.html", {
								"all_ebooks": all_ebooks, "ebook_gst": ebook_gst,
								"page_info": ebooks_page_info, "title": "eBooks",
								"group_id": group_id, "groupid": group_id
								}, context_instance = RequestContext(request))

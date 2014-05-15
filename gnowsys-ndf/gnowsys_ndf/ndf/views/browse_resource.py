''' -- imports from installed packages -- ''' 
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django_mongokit import get_database
from gnowsys_ndf.ndf.org2any import org2html

try:
	from bson import ObjectId
except ImportError:  # old pymongo
	from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import Node, GRelation,GSystemType,File,Triple
from gnowsys_ndf.ndf.views.file import *

#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
collection_tr = db[Triple.collection_name]
GST_browse_resource = collection.GSystemType.one({'_type':'GSystemType', 'name': 'Browse Resource'})

#######################################################################################################################################

def resource_list(request,group_id,app_id=None):

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
		group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		if group_ins:
		    group_id = str(group_ins._id)
		else :
		    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		    if auth :
		        group_id = str(auth._id)
	else :
	    pass
	if app_id is None:
	    app_ins = collection.Node.find_one({'_type':'GSystemType', 'name': 'Browse Resource'})
	    if app_ins:
	        app_id = str(app_ins._id)


	# if GST_browse_resource._id == ObjectId(app_id):

	"""
	* Renders a list of all 'Resources(XCR)' available within the database.
	"""
	title = GST_browse_resource.name

	file_id = GST_FILE._id
	files = collection.Node.find({'member_of': {'$all': [ObjectId(file_id)]}, '_type': 'File', 'fs_file_ids':{'$ne': []}, 'group_set': {'$all': [ObjectId(group_id)]}}).sort("last_update", -1)
	docCollection = collection.Node.find({'member_of': {'$nin': [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id)]}, '_type': 'File','fs_file_ids': {'$ne': []}, 'group_set': {'$all': [ObjectId(group_id)]}}).sort("last_update", -1)
	imageCollection = collection.Node.find({'member_of': {'$all': [ObjectId(GST_IMAGE._id)]}, '_type': 'File','fs_file_ids': {'$ne': []}, 'group_set': {'$all': [ObjectId(group_id)]}}).sort("last_update", -1)
	videoCollection = collection.Node.find({'member_of': {'$all': [ObjectId(GST_VIDEO._id)]}, '_type': 'File','fs_file_ids': {'$ne': []}, 'group_set': {'$all': [ObjectId(group_id)]}}).sort("last_update", -1)
	already_uploaded = request.GET.getlist('var', "")

	pandora_video_st=collection.Node.one({'$and':[{'name':'Pandora_video'},{'_type':'GSystemType'}]})
	source_id_at=collection.Node.one({'$and':[{'name':'source_id'},{'_type':'AttributeType'}]})

	pandora_video_id=[]
	source_id_set=[]
	get_member_set=collection.Node.find({'$and':[{'member_of': {'$all': [ObjectId(pandora_video_st._id)]}},{'_type':'File'}]})


	return render_to_response("ndf/resource_list.html", 
	    	{'title': title, 
	    	'files': files,
	    	'sourceid':source_id_set,
	    	'wetube_videos':get_member_set,
	    	'docCollection': docCollection,
	    	'imageCollection': imageCollection,
	    	'videoCollection': videoCollection,
	    	'already_uploaded': already_uploaded,
	    	'groupid': group_id,
	    	'group_id':group_id
	    	}, context_instance = RequestContext(request))


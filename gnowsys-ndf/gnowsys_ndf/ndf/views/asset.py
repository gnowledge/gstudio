import datetime
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from django.http import HttpRequest

from gnowsys_ndf.ndf.models import Node, GSystemType, Buddy, Counter
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import get_group_name_id, get_language_tuple, create_grelation, get_execution_time, auto_enroll
from gnowsys_ndf.settings import GSTUDIO_BUDDY_LOGIN, GSTUDIO_DEFAULT_LANGUAGE, GSTUDIO_FILE_UPLOAD_POINTS

# gst_asset = node_collection.one({'_type': u'GSystemType', 'name': u'Asset'})
gst_asset_name, gst_asset_id = GSystemType.get_gst_name_id(u'Asset')
gst_page_name, gst_page_id = GSystemType.get_gst_name_id(u'Page')
gst_file_name, gst_file_id = GSystemType.get_gst_name_id(u'File')

@auto_enroll
@get_execution_time
def create_asset(name,
				group_id,
				created_by,
				node_id=None,
				content=None,
				request=HttpRequest(),
				**kwargs):
	'''
	This method is equivalent to write_files() but
	also (about to) incorporate page creation.

	So plan is to not to change write_files() which is working smoothly at various places.
	But to create another equivalent function and in future, replace this for write_files()
	'''
	if not name:
		name = request.POST.get('name') if request else None

	if not created_by:
		created_by = request.user.id if request else None

	group_name, group_id = get_group_name_id(group_id)

	# compulsory values, if not found raise error.
	# if not all([name, created_by, group_id, uploaded_files]):
	if not all([name, created_by, group_id]):
		raise ValueError('"name", "created_by", "group" are mandatory args."')

	author_obj     = node_collection.one({'_type': u'Author', 'created_by': created_by})
	author_obj_id  = author_obj._id

	group_set = [ObjectId(group_id), ObjectId(author_obj_id)]
	kwargs.update({'name': unicode(name)})
	kwargs.update({'created_by': created_by})
	kwargs.update({'member_of': gst_asset_id})
	kwargs.update({'group_set': group_set})
	kwargs.update({'content': content})

	if node_id:
		asset_gs_obj = node_collection.one({'_id': ObjectId(node_id)})
	else:
		asset_gs_obj = node_collection.collection.GSystem()
	asset_gs_obj.fill_gstystem_values(request=request,
									**kwargs)
	asset_gs_obj.fill_node_values(**kwargs)
	asset_gs_obj.save(group_id=group_id)
	return asset_gs_obj

@auto_enroll
@get_execution_time
def create_assetcontent(asset_id,
						name,
						group_name_or_id,
						created_by,
						node_id=None,
						content=None,
						files=[None],
						resource_type='Page',
						request=HttpRequest(),
						**kwargs):

	# Mandatory arg: 'asset_id'. AssetContent should fall under Asset.
	# And if no Asset exists with supplied arg, can't proceeed.
	asset_obj = Node.get_node_by_id(asset_id)
	if not asset_obj:
		raise ValueError('No Asset exists with supplied asset_id.')

	if not name:
		name = request.POST.get('name') if request else None
	if not created_by:
		created_by = request.user.id if request else None

	group_name, group_id = get_group_name_id(group_name_or_id)
	group_id = ObjectId(group_id)
	if group_id not in asset_obj['group_set']:
		# AssetContent should fall under Asset. If 'group_id' arg is
		# supplied, it should fall under asset's group id.
		raise Exception('Supplied group_id and group_id of Asset does not match.')

	test_content = True if (content or files) else False

	# compulsory values, if not found raise error.
	# if not all([name, created_by, group_id, uploaded_files]):

	if not all([name, created_by, group_id, test_content]):
		raise ValueError('"asset_id", "name", "created_by", "group" and ("content" or "files") are mandatory args.')

	author_obj     = node_collection.one({'_type': u'Author', 'created_by': created_by})
	author_obj_id  = author_obj._id

	group_set = [ObjectId(group_id), ObjectId(author_obj_id)]
	gst_name_id_dict = {
		'Page': gst_page_id, 'page': gst_page_id,
		'File': gst_file_id, 'file': gst_file_id
	}

	try:
		member_of_gst_id = gst_name_id_dict[resource_type]
	except Exception, e:
		print "resource_type arg is not supplied."
		# handle condition based on files.
		member_of_gst_id = gst_file_id if files[0] else gst_page_id
	kwargs.update({'name': unicode(name)})
	kwargs.update({'created_by': created_by})
	kwargs.update({'member_of': member_of_gst_id})
	kwargs.update({'group_set': group_set})
	kwargs.update({'unique_gs_per_file': False})
	if content:
		kwargs.update({'content': content})

	asset_content_obj = None
	if node_id:
		asset_content_obj = node_collection.one({'_id': ObjectId(node_id)})
	else:
		asset_content_obj = node_collection.collection.GSystem()
	asset_content_obj.fill_gstystem_values(request=request,
											uploaded_file=files[0],
											**kwargs)
	asset_content_obj.fill_node_values(**kwargs)
	asset_content_obj.save(groupid=group_id)
	asset_contents_list = [asset_content_obj._id]
	rt_has_asset_content = node_collection.one({'_type': 'RelationType',
		'name': 'has_assetcontent'})
	asset_grels = triple_collection.find({'_type': 'GRelation', \
		'relation_type': rt_has_asset_content._id,'subject': asset_obj._id},
		{'_id': 0, 'right_subject': 1})
	for each_asset in asset_grels:
		asset_contents_list.append(each_asset['right_subject'])
	
	create_grelation(asset_obj._id, rt_has_asset_content, asset_contents_list)
	active_user_ids_list = [request.user.id]
	if GSTUDIO_BUDDY_LOGIN:
		active_user_ids_list += Buddy.get_buddy_userids_list_within_datetime(request.user.id, datetime.datetime.now())
		# removing redundancy of user ids:
		active_user_ids_list = dict.fromkeys(active_user_ids_list).keys()

	counter_objs_cur = Counter.get_counter_objs_cur(active_user_ids_list, group_id)
	# counter_obj = Counter.get_counter_obj(request.user.id, group_id)
	for each_counter_obj in counter_objs_cur:
		each_counter_obj['file']['created'] += 1
		each_counter_obj['group_points'] += GSTUDIO_FILE_UPLOAD_POINTS
		each_counter_obj.last_update = datetime.datetime.now()
		each_counter_obj.save()
	return asset_content_obj

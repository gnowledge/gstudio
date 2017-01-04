try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from django.http import HttpRequest

from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_group_name_id, get_language_tuple
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_LANGUAGE

gst_asset = node_collection.one({'_type': u'GSystemType', 'name': u'Asset'})

def create_asset(request=HttpRequest(),
				name=None,
				group_id=None,
				created_by=None,
				content=None,
				files=[],
				language=None,
				unique_gs_per_file=True):
	'''
	This method is equivalent to write_files() but
	also (about to) incorporate page creation.

	So plan is to not to change write_files() which is working smoothly at various places.
	But to create another equivalent function and in future, replace this for write_files()
	'''

	if not name:
		name = request.POST.get('name') if request else None

	if not created_by:
		created_by = created_by | request.user.id if request else None

	group_name, group_id = get_group_name_id(group_id)

	# compulsory values, if not found raise error.
	# if not all([name, created_by, group_id, uploaded_files]):
	if not all([name, created_by, group_id]):
		raise ValueError('"name", "created_by", "group", "file | page" are mandetory args."')

	author_obj     = node_collection.one({'_type': u'Author', 'created_by': created_by})
	author_obj_id  = author_obj._id

	if request and not language:
		language = request.POST.get('language', GSTUDIO_DEFAULT_LANGUAGE)

	language = get_language_tuple(language)
	group_set = [ObjectId(group_id), ObjectId(author_obj_id)]

	asset_gs_obj = node_collection.collection.GSystem()

	asset_gs_obj.fill_gstystem_values(request=request,
									name=name,
									member_of=gst_asset._id,
									group_set=group_set,
									created_by=created_by,
									content=content,
									language=language)

	# print asset_gs_obj

	# for each_resource in uploaded_files:

	# 	gs_obj = node_collection.collection.GSystem()

	# 	if name and not first_obj and (name != 'untitled'):
	# 		file_name = name
	# 	else:
	# 		file_name = each_resource.name if hasattr(each_resource, 'name') else name

	# 	existing_file_gs = gs_obj.fill_gstystem_values(request=request,
	# 								name=file_name,
	# 								group_set=group_set,
	# 								language=language,
	# 								uploaded_file=each_file,
	# 								unique_gs_per_file=unique_gs_per_file)
	# 	# print "existing_file_gs",existing_file_gs
	# 	if (gs_obj.get('_id', None) or existing_file_gs.get('_id', None)) and \
	# 	   (existing_file_gs.get('_id', None) == gs_obj.get('_id', None)):
	# 		if gst_file_id not in gs_obj.member_of:
	# 			gs_obj.member_of.append(gst_file_id)

	# 		gs_obj.save(groupid=group_id,validate=False)

	# 		if 'video' in gs_obj.if_file.mime_type:
	# 			convertVideo.delay(created_by, str(gs_obj._id), file_name)
	# 		if not first_obj:
	# 			first_obj = gs_obj
	# 		else:
	# 			collection_set.append(gs_obj._id)

	# 		gs_obj_list.append(gs_obj)
	# 	elif existing_file_gs:
	# 			gs_obj_list.append(existing_file_gs)

	# if make_collection and collection_set:
	# 	first_obj.collection_set = collection_set
	# 	first_obj.save()

	# return gs_obj_list

	# # return render_to_response('ndf/filehive.html', {
	# # 	'group_id': group_id, 'groupid': group_id,
	# # 	}, context_instance=RequestContext(request))

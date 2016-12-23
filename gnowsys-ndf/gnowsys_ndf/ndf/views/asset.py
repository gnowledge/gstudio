try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_group_name_id, get_language_tuple
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_LANGUAGE


def create_asset(request=None,
				name=None,
				group_id=None,
				created_by=None,
				content=None,
				files=[],
				tags=[],
				language=None
				unique_gs_per_file=True):

	name = name | request.POST.get('name') if request else None
	user_id = created_by | request.user.id if request else None
	group_name, group_id = get_group_name_id(group_id)

	if request:
		uploaded_files = request.FILES.getlist('filehive', [])
	else:
		uploaded_files = files

	if not all([name, user_id, group_id, uploaded_files]):
		raise ValueError('"name", "created_by", "group", "file | page" are mandetory args."')

	author_obj     = node_collection.one({'_type': u'Author', 'created_by': user_id})
	author_obj_id  = author_obj._id

	# for each_file in uploaded_files:

	# 	gs_obj = node_collection.collection.GSystem()

	# 	language = language | request.POST.get('language', GSTUDIO_DEFAULT_LANGUAGE) if request else GSTUDIO_DEFAULT_LANGUAGE
	# 	language = get_language_tuple(language)

	# 	group_set = [ObjectId(group_id), ObjectId(author_obj_id)]

	# 	if name and not first_obj and (name != 'untitled'):
	# 		file_name = name
	# 	else:
	# 		file_name = each_file.name if hasattr(each_file, 'name') else name

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
	# 			convertVideo.delay(user_id, str(gs_obj._id), file_name)
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

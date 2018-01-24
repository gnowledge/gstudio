# from StringIO import StringIO
# import hashlib
import os
# import shutil
import mimetypes
import magic

from hashfs import HashFS

from django.shortcuts import render_to_response
from django.template import RequestContext

from gnowsys_ndf.settings import MEDIA_ROOT, GSTUDIO_SITE_DEFAULT_LANGUAGE
from gnowsys_ndf.ndf.models import node_collection, filehive_collection, gfs
from gnowsys_ndf.ndf.models import GSystem, Author
from gnowsys_ndf.ndf.views.methods import get_language_tuple, get_group_name_id
from gnowsys_ndf.ndf.views.tasks import convertVideo

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

gst_file = node_collection.one({'_type': u'GSystemType', 'name': u'File'})
gst_file_id = gst_file._id

def upload_form(request, group_id):
	if request.method == 'GET':
		return render_to_response('ndf/filehive.html', {
			'group_id': group_id, 'groupid': group_id,
			}, context_instance=RequestContext(request))


def write_files(request, group_id, make_collection=False, unique_gs_per_file=True, **kwargs):

	user_id = request.user.id
	try:
		user_id = Author.extract_userid(request, **kwargs)
	except Exception as e:
		pass
	# print "user_id: ", user_id

	# author_obj = node_collection.one({'_type': u'Author', 'created_by': int(user_id)})
	author_obj = Author.get_author_obj_from_name_or_id(user_id)
	author_obj_id = author_obj._id
	kwargs['created_by'] = user_id

	group_name, group_id = get_group_name_id(group_id)

	first_obj      = None
	collection_set = []
	uploaded_files = request.FILES.getlist('filehive', [])
	name           = request.POST.get('name')

	gs_obj_list    = []
	for each_file in uploaded_files:

		gs_obj = node_collection.collection.GSystem()

		language = request.POST.get('language', GSTUDIO_SITE_DEFAULT_LANGUAGE)
		language = get_language_tuple(language)

		group_set = [ObjectId(group_id), ObjectId(author_obj_id)]

		if name and not first_obj and (name != 'untitled'):
			file_name = name
		else:
			file_name = each_file.name if hasattr(each_file, 'name') else name

		existing_file_gs = gs_obj.fill_gstystem_values(request=request,
									name=file_name,
									group_set=group_set,
									language=language,
									uploaded_file=each_file,
									unique_gs_per_file=unique_gs_per_file,
									**kwargs)
		# print "existing_file_gs",existing_file_gs
		if (gs_obj.get('_id', None) or existing_file_gs.get('_id', None)) and \
		   (existing_file_gs.get('_id', None) == gs_obj.get('_id', None)):
			if gst_file_id not in gs_obj.member_of:
				gs_obj.member_of.append(gst_file_id)

			gs_obj.save(groupid=group_id,validate=False)

			if 'video' in gs_obj.if_file.mime_type:
				convertVideo.delay(user_id, str(gs_obj._id), file_name)
			if not first_obj:
				first_obj = gs_obj
			else:
				collection_set.append(gs_obj._id)

			gs_obj_list.append(gs_obj)
		elif existing_file_gs:
				gs_obj_list.append(existing_file_gs)

	if make_collection and collection_set:
		first_obj.collection_set = collection_set
		first_obj.save()

	return gs_obj_list

	# return render_to_response('ndf/filehive.html', {
	# 	'group_id': group_id, 'groupid': group_id,
	# 	}, context_instance=RequestContext(request))


def read_file(request, group_id):

	all_fgs = node_collection.find({'_type': 'GSystem', 'member_of': gst_file._id})
	return render_to_response('ndf/filehive_listing.html', {
		'group_id': group_id, 'groupid': group_id,
		'all_filehives': all_fgs
		}, context_instance=RequestContext(request))

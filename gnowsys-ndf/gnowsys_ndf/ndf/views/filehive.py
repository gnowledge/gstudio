# from StringIO import StringIO
# import hashlib
# import os
# import shutil
import mimetypes
import magic

from hashfs import HashFS

from django.shortcuts import render_to_response
from django.template import RequestContext

from gnowsys_ndf.settings import MEDIA_ROOT, GSTUDIO_SITE_DEFAULT_LANGUAGE
from gnowsys_ndf.ndf.models import node_collection, filehive_collection, gfs
from gnowsys_ndf.ndf.models import GSystem
from gnowsys_ndf.ndf.views.methods import get_language_tuple

gst_file = node_collection.one({'_type': u'GSystemType', 'name': u'File'})
gst_file_id = gst_file._id

def write_file(request, group_id):
	if request.method == 'GET':
		return render_to_response('ndf/filehive.html', {
			'group_id': group_id, 'groupid': group_id,

			}, context_instance=RequestContext(request))

	if request.method == 'POST':
		uploaded_files = request.FILES.getlist('files', [])
		first_obj = None
		collection_set = []
		for each_file in uploaded_files:
			gs_obj = node_collection.collection.GSystem()
			language = request.POST.get('language', GSTUDIO_SITE_DEFAULT_LANGUAGE)
			language = get_language_tuple(language)
			gs_obj.fill_gstystem_values(request=request,
										language=language,
										uploaded_file=each_file)
			print "\n=========in view============\n"
			print each_file
			gs_obj.member_of.append(gst_file_id)
			gs_obj.save()

			if not first_obj:
				first_obj = gs_obj
			else:
				collection_set.append(gs_obj._id)

		if collection_set:
			first_obj.collection_set = collection_set
			first_obj.save()

		return render_to_response('ndf/filehive.html', {
			'group_id': group_id, 'groupid': group_id,
			}, context_instance=RequestContext(request))


def read_file(request, group_id):

	all_fgs = node_collection.find({'_type': 'GSystem', 'member_of': gst_file._id})
	return render_to_response('ndf/filehive_listing.html', {
		'group_id': group_id, 'groupid': group_id,
		'all_filehives': all_fgs
		}, context_instance=RequestContext(request))

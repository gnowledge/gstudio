''' -- imports from installed packages -- '''
#from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from gnowsys_ndf.ndf.models import File

db = get_database()
collection = db[File.collection_name]
def videoDashboard(request, group_name, video_id):
    imgcol = collection.File.find({'mime_type': {'$regex': 'video'}})
    print imgcol,"dsfsda"
    template = "ndf/videoDashboard.html"
    url = request.get_full_path()
    variable = RequestContext(request, {'videoCollection':imgcol, 'pageUrl':url, 'stId':video_id})
    return render_to_response(template, variable)

def getvideoThumbnail(request, group_name, _id):
    imgobj = collection.File.one({"_id": ObjectId(_id)})
    if (imgobj.fs.files.exists(imgobj.fs_file_ids[1])):
        f = imgobj.fs.files.get(ObjectId(imgobj.fs_file_ids[1]))
        return HttpResponse(f.read())
        
    
def getFullvideo(request, group_name, _id):
    imgobj = collection.File.one({"_id": ObjectId(_id)})
    if (imgobj.fs.files.exists(imgobj.fs_file_ids[0])):
        f = imgobj.fs.files.get(ObjectId(imgobj.fs_file_ids[0]))
        return HttpResponse(f.read(), content_type=f.content_type)

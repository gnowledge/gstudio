''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from gnowsys_ndf.ndf.models import *

db = get_database()
collection=db[File.collection_name]
def imageDashboard(request,image_id):
    imgcol=collection.File.find({'mime_type': {'$regex': 'image'}})
    template="ndf/ImageDashboard.html"
    url=request.get_full_path()
    variable=RequestContext(request,{'imageCollection':imgcol,'pageUrl':url,'stId':image_id})
    return render_to_response(template,variable)

def getImageThumbnail(request,_id):
        imgobj=collection.File.one({"_id": ObjectId(_id)})
        if (imgobj.fs.files.exists(imgobj.fs_file_ids[1])):
            fl=imgobj.fs.files.get(ObjectId(imgobj.fs_file_ids[1]))
            return HttpResponse(fl.read())
                
    
def getFullImage(request,_id):
    imgobj=collection.File.one({"_id": ObjectId(_id)})
    if (imgobj.fs.files.exists(imgobj.fs_file_ids[0])):
        fl=imgobj.fs.files.get(ObjectId(imgobj.fs_file_ids[0]))
        return HttpResponse(fl.read(),content_type=fl.content_type)

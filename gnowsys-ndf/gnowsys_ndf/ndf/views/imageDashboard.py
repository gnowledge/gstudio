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
def imageDashboard(request, group_name, image_id):
    imgcol = collection.File.find({'mime_type': {'$regex': 'image'}})
    template = "ndf/ImageDashboard.html"
    already_uploaded=request.GET.get("already_uploaded","")
    variable = RequestContext(request, {'imageCollection':imgcol,'already_uploaded':already_uploaded })
    return render_to_response(template, variable)

def getImageThumbnail(request, group_name, _id):
    imgobj = collection.File.one({"_id": ObjectId(_id)})
    if (imgobj.fs.files.exists(imgobj.fs_file_ids[1])):
        f = imgobj.fs.files.get(ObjectId(imgobj.fs_file_ids[1]))
        return HttpResponse(f.read())
        
    
def getFullImage(request, group_name, _id):
    imgobj = collection.File.one({"_id": ObjectId(_id)})
    if (imgobj.fs.files.exists(imgobj.fs_file_ids[0])):
        f = imgobj.fs.files.get(ObjectId(imgobj.fs_file_ids[0]))
        return HttpResponse(f.read(), content_type=f.content_type)

def image_search(request,group_name):
    imgcol=collection.File.find({'mime_type':{'$regex': 'image'}})
    if request.method=="GET":
        keyword=request.GET.get("search","")
        img_search=collection.File.find({'$and':[{'mime_type':{'$regex': 'image'}},{'$or':[{'name':{'$regex':keyword}},{'tags':{'$regex':keyword}}]}]})
        template="ndf/file_search.html"
        variable=RequestContext(request,{'file_collection':img_search,'view_name':'image_search'})
        return render_to_response(template,variable)

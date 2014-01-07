''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from gnowsys_ndf.ndf.models import File

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.views.methods import get_node_common_fields

db = get_database()
collection = db[File.collection_name]
GST_IMAGE = collection.GSystemType.one({'name': GAPPS[3]})

def imageDashboard(request, group_name, image_id):
    img_col= collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(image_id)]},'_type':'File', 'group_set': {'$all': [group_name]}})
    template = "ndf/ImageDashboard.html"
    already_uploaded=request.GET.getlist('var',"")
    variable = RequestContext(request, {'imageCollection': img_col,'already_uploaded':already_uploaded })
    return render_to_response(template, variable)

def getImageThumbnail(request, group_name, _id):
    imgobj = collection.File.one({"_type": u"File", "_id": ObjectId(_id)})
    if imgobj is not None:
        if (imgobj.fs.files.exists(imgobj.fs_file_ids[1])):
            f = imgobj.fs.files.get(ObjectId(imgobj.fs_file_ids[1]))
            return HttpResponse(f.read())
    else:
        return HttpResponse("")
        
    
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

def image_detail(request, group_name, _id):
    img_node = collection.File.one({"_id": ObjectId(_id)})
    return render_to_response("ndf/image_detail.html",
                                  { 'node': img_node,
                                    'group_name': group_name
                                  },
                                  context_instance = RequestContext(request)
        )
def image_edit(request,group_name,_id):
    img_node = collection.File.one({"_id": ObjectId(_id)})
    if request.method == "POST":
        get_node_common_fields(request, img_node, group_name, GST_IMAGE)
        img_node.save()
        return HttpResponseRedirect(reverse('image_detail', kwargs={'group_name': group_name, '_id': img_node._id}))
        
    else:
        return render_to_response("ndf/image_edit.html",
                                  { 'node': img_node,
                                    'group_name': group_name
                                },
                                  context_instance=RequestContext(request)
                              )

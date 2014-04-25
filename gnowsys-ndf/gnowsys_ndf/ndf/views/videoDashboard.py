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
GST_VIDEO = collection.GSystemType.one({'name': GAPPS[4]})

def videoDashboard(request, group_id, video_id):
    vid_col = collection.GSystem.find({'member_of': {'$all': [ObjectId(video_id)]},'_type':'File', 'group_set': {'$all': [group_id]}})
    template = "ndf/videoDashboard.html"
    already_uploaded=request.GET.getlist('var',"")
    variable = RequestContext(request, {'videoCollection':vid_col, 'already_uploaded':already_uploaded, 'newgroup':group_id})
    return render_to_response(template, variable)

def getvideoThumbnail(request, group_id, _id):
    videoobj = collection.File.one({"_id": ObjectId(_id)})
    if (videoobj.fs.files.exists(videoobj.fs_file_ids[1])):
        f = videoobj.fs.files.get(ObjectId(videoobj.fs_file_ids[1]))
        return HttpResponse(f.read())
        
    
def getFullvideo(request, group_id, _id):
    videoobj = collection.File.one({"_id": ObjectId(_id)})
    if len(videoobj.fs_file_ids) > 2:
    	if (videoobj.fs.files.exists(videoobj.fs_file_ids[2])):
            f = videoobj.fs.files.get(ObjectId(videoobj.fs_file_ids[2]))
            return HttpResponse(f.read(), content_type=f.content_type)
    else : 
        if (videoobj.fs.files.exists(videoobj.fs_file_ids[0])):
            f = videoobj.fs.files.get(ObjectId(videoobj.fs_file_ids[0]))
            return HttpResponse(f.read(), content_type=f.content_type)
       
        
def video_search(request,group_id):
    vidcol=collection.File.find({'mime_type':{'$regex': 'video'}})
    if request.method=="GET":
        keyword=request.GET.get("search","")
        vid_search=collection.File.find({'$and':[{'mime_type':{'$regex': 'video'}},{'$or':[{'name':{'$regex':keyword}},{'tags':{'$regex':keyword}}]}]})
        template="ndf/file_search.html"
        variable=RequestContext(request,{'file_collection':vid_search,'view_name':'video_search','newgroup':group_id})
        return render_to_response(template,variable)        


def video_detail(request, group_id, _id):
    vid_node = collection.File.one({"_id": ObjectId(_id)})
    video_obj=request.GET.get("vid_id","")
    return render_to_response("ndf/video_detail.html",
                                  { 'node': vid_node,
                                    'group_id': group_id,
                                    'groupid':group_id,
                                    'video_obj':video_obj
                                  },
                                  context_instance = RequestContext(request)
        )
def video_edit(request,group_id,_id):
    vid_node = collection.File.one({"_id": ObjectId(_id)})
    video_obj=request.GET.get("vid_id","")
    if request.method == "POST":
        get_node_common_fields(request, vid_node, group_id, GST_VIDEO)
        vid_node.save()
        return HttpResponseRedirect(reverse('video_detail', kwargs={'group_id': group_id, '_id': vid_node._id}))
        
    else:
        return render_to_response("ndf/video_edit.html",
                                  { 'node': vid_node,
                                    'group_id': group_id,
                                    'groupid':group_id,
                                    'video_obj':video_obj
                                },
                                  context_instance=RequestContext(request)
                              )

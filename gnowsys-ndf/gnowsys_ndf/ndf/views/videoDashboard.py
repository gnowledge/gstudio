''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from gnowsys_ndf.ndf.models import File
''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.views.methods import get_node_common_fields,create_grelation_list,get_execution_time
from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute
from gnowsys_ndf.ndf.views.methods import get_node_metadata, create_gattribute, create_grelation
from gnowsys_ndf.ndf.models import node_collection, triple_collection


GST_VIDEO = node_collection.one({"_type": "GSystemType", 'name': GAPPS[4]})

@get_execution_time
def videoDashboard(request, group_id, video_id):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    if video_id is None:
        video_ins = node_collection.find_one({'_type':"GSystemType", "name":"Video"})
        if video_ins:
            video_id = str(video_ins._id)
    vid_col = node_collection.find({'member_of': {'$all': [ObjectId(video_id)]},'_type':'File', 'group_set': {'$all': [group_id]}})
    template = "ndf/videoDashboard.html"
    already_uploaded=request.GET.getlist('var',"")
    variable = RequestContext(request, {'videoCollection':vid_col, 'already_uploaded':already_uploaded, 'newgroup':group_id})
    return render_to_response(template, variable)
@get_execution_time
def getvideoThumbnail(request, group_id, _id):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    videoobj = node_collection.one({"_id": ObjectId(_id)})
    if videoobj:
        if (videoobj.fs.files.exists(videoobj.fs_file_ids[0])):
            f = videoobj.fs.files.get(ObjectId(videoobj.fs_file_ids[0]))
            return HttpResponse(f.read())
        
@get_execution_time    
def getFullvideo(request, group_id, _id):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    videoobj = node_collection.one({"_id": ObjectId(_id)})
    if len(videoobj.fs_file_ids) > 2:
    	if (videoobj.fs.files.exists(videoobj.fs_file_ids[2])):
            f = videoobj.fs.files.get(ObjectId(videoobj.fs_file_ids[2]))
            return HttpResponse(f.read(), content_type=f.content_type)
    else : 
        if (videoobj.fs.files.exists(videoobj.fs_file_ids[0])):
            f = videoobj.fs.files.get(ObjectId(videoobj.fs_file_ids[0]))
            return HttpResponse(f.read(), content_type=f.content_type)
       
@get_execution_time        
def video_search(request,group_id):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    vidcol = node_collection.find({'mime_type':{'$regex': 'video'}})
    if request.method=="GET":
        keyword=request.GET.get("search","")
        vid_search = node_collection.find({'$and':[{'mime_type':{'$regex': 'video'}},{'$or':[{'name':{'$regex':keyword}},{'tags':{'$regex':keyword}}]}]})
        template="ndf/file_search.html"
        variable=RequestContext(request,{'file_collection':vid_search,'view_name':'video_search','newgroup':group_id})
        return render_to_response(template,variable)        

@get_execution_time
def video_detail(request, group_id, _id):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    vid_node = node_collection.one({"_id": ObjectId(_id)})
    if vid_node._type == "GSystemType":
	return videoDashboard(request, group_id, _id)
    video_obj=request.GET.get("vid_id","")
    return render_to_response("ndf/video_detail.html",
                                  { 'node': vid_node,
                                    'group_id': group_id,
                                    'groupid':group_id,
                                    'video_obj':video_obj
                                  },
                                  context_instance = RequestContext(request)
        )
@get_execution_time        
def video_edit(request,group_id,_id):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    vid_node = node_collection.one({"_id": ObjectId(_id)})
    title = GST_VIDEO.name
    video_obj=request.GET.get("vid_id","")
    if request.method == "POST":

        # get_node_common_fields(request, vid_node, group_id, GST_VIDEO)
        vid_node.save(is_changed=get_node_common_fields(request, vid_node, group_id, GST_VIDEO))
	get_node_metadata(request,vid_node)
	teaches_list = request.POST.get('teaches_list','') # get the teaches list
        assesses_list = request.POST.get('assesses_list','') # get the teaches list 
	if teaches_list !='':
			teaches_list=teaches_list.split(",")
	create_grelation_list(vid_node._id,"teaches",teaches_list)
	
	if assesses_list !='':
		assesses_list=assesses_list.split(",")
					
	create_grelation_list(vid_node._id,"assesses",assesses_list)


        return HttpResponseRedirect(reverse('video_detail', kwargs={'group_id': group_id, '_id': vid_node._id}))
    vid_col = node_collection.find({'member_of': GST_VIDEO._id,'group_set': ObjectId(group_id)})
    nodes_list = []
    for each in vid_col:
      nodes_list.append(str((each.name).strip().lower()))
        
    else:
        return render_to_response("ndf/video_edit.html",
                                  { 'node': vid_node, 'title': title,
                                    'group_id': group_id,
                                    'groupid':group_id,
                                    'video_obj':video_obj,
                                    'nodes_list':nodes_list
                                },
                                  context_instance=RequestContext(request)
                              )

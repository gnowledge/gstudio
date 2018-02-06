''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response  # , render
from django.template import RequestContext
import json 
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
# from gnowsys_ndf.ndf.models import File

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import META_TYPE, GAPPS  # , MEDIA_ROOT
from gnowsys_ndf.ndf.models import node_collection  # , triple_collection
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, get_node_metadata, create_thread_for_node
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, delete_grelation
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_relation_value
from gnowsys_ndf.ndf.views.methods import get_execution_time, create_grelation_list, node_thread_access, get_group_name_id
gapp_mt = node_collection.one({'_type': "MetaType", 'name': META_TYPE[0]})
GST_VIDEO = node_collection.one({'member_of': gapp_mt._id, 'name': GAPPS[4]})
file_gst = node_collection.find_one( { "_type" : "GSystemType","name":"File" } )

@get_execution_time
def videoDashboard(request, group_id):
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    files_cur = node_collection.find({
                                        '_type': {'$in': ["GSystem"]},
                                        'member_of': file_gst._id,
                                        'group_set': {'$all': [ObjectId(group_id)]},
                                        'if_file.mime_type': {'$regex': 'video'},
                                        'status' : { '$ne': u"DELETED" }

                                        # 'created_by': {'$in': gstaff_users},
                            # '$or': [
                                    # {
                                    # },
                                    # {
                                    #     '$or': [
                                    #             {'access_policy': u"PUBLIC"},
                                    #             {
                                    #                 '$and': [
                                    #                         {'access_policy': u"PRIVATE"},
                                    #                         {'created_by': request.user.id}
                                    #                     ]
                                    #             }
                                    #         ],
                                    # }
                                    # {    'collection_set': {'$exists': "true", '$not': {'$size': 0} }}
                                # ]
                        },
                        {
                            'name': 1,
                            '_id': 1,
                            'fs_file_ids': 1,
                            'member_of': 1,
                            'mime_type': 1,
                            'if_file':1
                        }).sort("last_update", -1)
    template = "ndf/videoDashboard.html"
    variable = RequestContext(request, {'group_id':group_id,'groupid':group_id,'files_cur':files_cur})
    return render_to_response(template, variable)
@get_execution_time
def getvideoThumbnail(request, group_id, _id):
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    videoobj = node_collection.one({"_id": ObjectId(_id)})        
    if videoobj:
        if hasattr(videoobj, 'if_file'):
            f = videoobj.get_file(videoobj.if_file.mid.relurl)
            return HttpResponse(f, content_type=videoobj.if_file.mime_type)

        else:
            f = videoobj.fs.files.get(ObjectId(videoobj.fs_file_ids[0]))
            return HttpResponse(f.read(), content_type=f.content_type)
@get_execution_time    
def getFullvideo(request, group_id, _id):
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

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
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    vidcol = node_collection.find({'mime_type':{'$regex': 'video'}})
    if request.method=="GET":
        keyword=request.GET.get("search","")
        vid_search = node_collection.find({'$and':[{'mime_type':{'$regex': 'video'}},{'$or':[{'name':{'$regex':keyword}},{'tags':{'$regex':keyword}}]}]})
        template="ndf/file_search.html"
        variable=RequestContext(request,{'file_collection':vid_search,'view_name':'video_search','newgroup':group_id})
        return render_to_response(template,variable)        

@get_execution_time
def video_detail(request, group_id, _id):
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    vid_node = node_collection.one({"_id": ObjectId(_id)})
    vid_node.get_neighbourhood(vid_node.member_of)
    thread_node = None
    allow_to_comment = None
    thread_node, allow_to_comment = node_thread_access(group_id, vid_node)

    # First get the navigation list till topic from theme map
    nav_l=request.GET.get('nav_li','')
    breadcrumbs_list = []
    nav_li = ""

    if nav_l:
      nav_li = nav_l

    if vid_node._type == "GSystemType":
        return videoDashboard(request, group_id, _id)
    video_obj=request.GET.get("vid_id","")
    return render_to_response("ndf/video_detail.html",
                                  { 'node': vid_node,
                                    'node_has_thread': thread_node,
                                    'allow_to_comment':allow_to_comment,
                                    'group_id': group_id,
                                    'groupid':group_id, 'nav_list':nav_li,
                                    'video_obj':video_obj
                                  },
                                  context_instance = RequestContext(request)
        )
@get_execution_time        
def video_edit(request,group_id,_id):
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
        
    vid_node = node_collection.one({"_id": ObjectId(_id)})
    title = GST_VIDEO.name
    video_obj=request.GET.get("vid_id","")
    group_obj = node_collection.one({'_id': ObjectId(group_id)})
    ce_id = request.GET.get('course_event_id')
    course_tab_title = request.POST.get("course_tab_title",'')
    res = request.GET.get('res')

    if request.method == "POST":

        # get_node_common_fields(request, vid_node, group_id, GST_VIDEO)
        vid_node.save(is_changed=get_node_common_fields(request, vid_node, group_id, GST_VIDEO),groupid=group_id)
        thread_create_val = request.POST.get("thread_create",'')
        course_tab_title = request.POST.get("course_tab_title",'')
        # help_info_page = request.POST.getlist('help_info_page','')
        help_info_page = request.POST['help_info_page']
        if help_info_page:
            help_info_page = json.loads(help_info_page)
        
        discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
        if thread_create_val == "Yes":
            create_gattribute(vid_node._id, discussion_enable_at, True)
            return_status = create_thread_for_node(request,group_id, vid_node)
        else:
            create_gattribute(vid_node._id, discussion_enable_at, False)

        # print "\n\n help_info_page ================ ",help_info_page
        if help_info_page and u"None" not in help_info_page:
            has_help_rt = node_collection.one({'_type': "RelationType", 'name': "has_help"})
            try:
                help_info_page = map(ObjectId, help_info_page)
                create_grelation(vid_node._id, has_help_rt,help_info_page)
            except Exception as invalidobjectid:
                # print "\n\n ERROR -------- ",invalidobjectid
                pass
        else:

            # Check if node had has_help RT
            grel_dict = get_relation_value(vid_node._id,"has_help")
            # print "\n\n grel_dict ==== ", grel_dict
            if grel_dict:
                grel_id = grel_dict.get("grel_id","")
                if grel_id:
                    for each_grel_id in grel_id:
                        del_status, del_status_msg = delete_grelation(
                            subject_id=vid_node._id,
                            node_id=each_grel_id,
                            deletion_type=0
                        )
                        # print "\n\n del_status == ",del_status
                        # print "\n\n del_status_msg == ",del_status_msg
        if "CourseEventGroup" not in group_obj.member_of_names_list:
            get_node_metadata(request,vid_node)
            teaches_list = request.POST.get('teaches_list', '')  # get the teaches list
            assesses_list = request.POST.get('assesses_list', '')  # get the teaches list
            if teaches_list !='':
                teaches_list=teaches_list.split(",")
            create_grelation_list(vid_node._id,"teaches",teaches_list)
            if assesses_list !='':
                assesses_list=assesses_list.split(",")
            create_grelation_list(vid_node._id,"assesses",assesses_list)
            return HttpResponseRedirect(reverse('video_detail', kwargs={'group_id': group_id, '_id': vid_node._id}))
        else:
            vid_node.status = u"PUBLISHED"
            vid_node.save()
            if course_tab_title:
                if course_tab_title == "raw material":
                    course_tab_title = "raw_material"
                return HttpResponseRedirect(reverse('course_'+course_tab_title + '_detail', kwargs={'group_id': group_id, 'node_id': str(vid_node._id)}))
            return HttpResponseRedirect(reverse('course_about', kwargs={'group_id': group_id}))
            # url = "/"+ str(group_id) +"/?selected="+str(vid_node._id)+"#view_page"
            # return HttpResponseRedirect(url)

    else:
        vid_col = node_collection.find({'member_of': GST_VIDEO._id,'group_set': ObjectId(group_id)})
        nodes_list = []
        for each in vid_col:
          nodes_list.append(str((each.name).strip().lower()))

        return render_to_response("ndf/video_edit.html",
                                  { 'node': vid_node, 'title': title,
                                    'group_id': group_id,
                                    'groupid':group_id,
                                    'video_obj':video_obj,
                                    'nodes_list':nodes_list,
                                    'ce_id': ce_id,
                                    'res': res, 'course_tab_title':course_tab_title
                                },
                                  context_instance=RequestContext(request)
                              )

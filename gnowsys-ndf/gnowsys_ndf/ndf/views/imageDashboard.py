''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from mongokit import paginator
import json

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
# from gnowsys_ndf.ndf.models import File

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import META_TYPE, GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_node_common_fields,create_grelation_list,get_execution_time, delete_grelation, create_grelation
from gnowsys_ndf.ndf.views.methods import get_node_metadata, node_thread_access, create_thread_for_node
from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_relation_value,get_file_obj
from gnowsys_ndf.ndf.views.methods import get_node_metadata, get_node_common_fields, create_gattribute, get_page, get_execution_time,set_all_urls,get_group_name_id
gapp_mt = node_collection.one({'_type': "MetaType", 'name': META_TYPE[0]})
GST_IMAGE = node_collection.one({'member_of': gapp_mt._id, 'name': GAPPS[3]})
image_ins = node_collection.find_one({'_type': "GSystemType", "name": "Image"})
file_gst = node_collection.find_one( { "_type" : "GSystemType","name":"File" } )

@get_execution_time
def imageDashboard(request, group_id, image_id=None,page_no=1):
    from gnowsys_ndf.settings import GSTUDIO_NO_OF_OBJS_PP
    '''
    fetching image acording to group name
    '''
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
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

    if image_id is None:
        image_ins = node_collection.find_one({'_type': "GSystemType", "name": "Image"})
        if image_ins:
            image_id = str(image_ins._id)

    # img_col = node_collection.find({'_type': 'File', 'member_of': {'$all': [ObjectId(image_id)]}, 'group_set': ObjectId(group_id)}).sort("last_update", -1)
    files_cur = node_collection.find({
                                        '_type': {'$in': ["GSystem"]},
                                        'member_of': file_gst._id,
                                        'group_set': {'$all': [ObjectId(group_id)]},
                                        'if_file.mime_type': {'$regex': 'image'},
                                        'status' : { '$ne': u"DELETED" },
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
    # print "file count\n\n\n",files_cur.count()

    # image_page_info = paginator.Paginator(files_cur, page_no, GSTUDIO_NO_OF_OBJS_PP)
    template = "ndf/ImageDashboard.html"
    already_uploaded=request.GET.getlist('var',"")
    variable = RequestContext(request, {'imageCollection': files_cur,'already_uploaded':already_uploaded,'groupid':group_id,'group_id':group_id })
    return render_to_response(template, variable)

@get_execution_time
def getImageThumbnail(request, group_id, _id):
    '''
    this funciton can be called to get thumbnail of image throw url
    '''
    # ins_objectid = ObjectId()
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

    img_obj = node_collection.one({"_type": u"File", "_id": ObjectId(_id)})

    if (img_obj is not None) and (len(img_obj.fs_file_ids) >= 2):
        # getting latest uploaded pic's _id
        img_fs = img_obj.fs_file_ids[1]

        if (img_obj.fs.files.exists(img_fs)):
            f = img_obj.fs.files.get(ObjectId(img_fs))
            return HttpResponse(f.read(),content_type=f.content_type)
    else:
        return HttpResponse("")

@get_execution_time
def getFullImage(request, group_id, _id, file_name = ""):
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
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

    img_obj = node_collection.one({"_id": ObjectId(_id)})
    if img_obj is not None:
        if (img_obj.fs.files.exists(img_obj.fs_file_ids[0])):
            f = img_obj.fs.files.get(ObjectId(img_obj.fs_file_ids[0]))
            return HttpResponse(f.read(), content_type=f.content_type)
        else:
            return HttpResponse("")
    else:
        return HttpResponse("")

@get_execution_time
def get_mid_size_img(request, group_id, _id):
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

    img_obj = node_collection.one({"_id": ObjectId(_id)})

    try:
        if hasattr(img_obj, 'if_file'):
            f = img_obj.get_file(img_obj.if_file.mid.relurl)
            return HttpResponse(f, content_type=img_obj.if_file.mime_type)

        else:
            f = img_obj.fs.files.get(ObjectId(img_obj.fs_file_ids[2]))
            return HttpResponse(f.read(), content_type=f.content_type)

    except IndexError:

        if hasattr(img_obj, 'if_file'):
            f = img_obj.get_file(img_obj.if_file.original.relurl)
            return HttpResponse(f, content_type=img_obj.if_file.mime_type)
        else:
            f = img_obj.fs.files.get(ObjectId(img_obj.fs_file_ids[0]))
            return HttpResponse(f.read(), content_type=f.content_type)

@get_execution_time
def image_search(request,group_id):
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

    imgcol = node_collection.find({"_type": "File", 'mime_type': {'$regex': 'image'}})
    if request.method=="GET":
        keyword=request.GET.get("search","")
        img_search=node_collection.find({'$and':[{'mime_type':{'$regex': 'image'}},{'$or':[{'name':{'$regex':keyword}},{'tags':{'$regex':keyword}}]}]})
        template="ndf/file_search.html"
        variable=RequestContext(request,{'file_collection':img_search,'view_name':'image_search','groupid':group_id,'group_id':group_id})
        return render_to_response(template,variable)

@get_execution_time
def image_detail(request, group_id, _id):
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

    img_node = node_collection.one({"_id": ObjectId(_id)})

    # First get the navigation list till topic from theme map
    nav_l=request.GET.get('nav_li','')
    breadcrumbs_list = []
    nav_li = ""

    if nav_l:
      nav_li = nav_l

    if img_node._type == "GSystemType":
    	return imageDashboard(request, group_id, _id)
    img_node.get_neighbourhood(img_node.member_of)
    thread_node = None
    allow_to_comment = None
    thread_node, allow_to_comment = node_thread_access(group_id, img_node)

    imageCollection = node_collection.find({'member_of': {'$all': [ObjectId(GST_IMAGE._id)]},
                                              '_type': 'File','fs_file_ids': {'$ne': []},
                                              'group_set': {'$all': [ObjectId(group_id)]},
                                              '$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [
                                                  {'access_policy': u"PRIVATE"},
                                                  {'created_by': request.user.id}
                                                  ]
                                                }
                                              ]
                                            }).sort("last_update", -1)

    return render_to_response("ndf/image_detail.html",
                                  { 'node': img_node,
                                    'group_id': group_id, 'nav_list':nav_li,
                                    'node_has_thread': thread_node,
                                    'allow_to_comment':allow_to_comment,
                                    'groupid':group_id, 'imageCollection': imageCollection
                                  },
                                  context_instance = RequestContext(request)
        )

@get_execution_time
def image_edit(request,group_id,_id):
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

    group_obj = node_collection.one({'_id': ObjectId(group_id)})
    img_node = node_collection.one({"_id": ObjectId(_id)})
    ce_id = request.GET.get('course_event_id')
    res = request.GET.get('res')
    course_tab_title = request.GET.get('course_tab_title','')

    title = GST_IMAGE.name
    if request.method == "POST":
        # get_node_common_fields(request, img_node, group_id, GST_IMAGE)
        img_node.save(is_changed=get_node_common_fields(request, img_node, group_id, GST_IMAGE),groupid=group_id)
        thread_create_val = request.POST.get("thread_create",'')
        course_tab_title = request.POST.get("course_tab_title",'')
        # help_info_page = request.POST.getlist('help_info_page','')
        help_info_page = request.POST['help_info_page']
        if help_info_page:
            help_info_page = json.loads(help_info_page)

        discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
        if thread_create_val == "Yes":
            create_gattribute(img_node._id, discussion_enable_at, True)
            return_status = create_thread_for_node(request,group_id, img_node)
        else:
            create_gattribute(img_node._id, discussion_enable_at, False)

        # print "\n\n help_info_page ================ ",help_info_page
        if help_info_page and u"None" not in help_info_page:
          has_help_rt = node_collection.one({'_type': "RelationType", 'name': "has_help"})
          try:
            help_info_page = map(ObjectId, help_info_page)
            create_grelation(img_node._id, has_help_rt,help_info_page)
          except Exception as invalidobjectid:
            # print "\n\n ERROR -------- ",invalidobjectid
            pass
        else:

          # Check if node had has_help RT
          grel_dict = get_relation_value(img_node._id,"has_help")
          # print "\n\n grel_dict ==== ", grel_dict
          if grel_dict:
            grel_id = grel_dict.get("grel_id","")
            if grel_id:
              for each_grel_id in grel_id:
                del_status, del_status_msg = delete_grelation(
                    subject_id=img_node._id,
                    node_id=each_grel_id,
                    deletion_type=0
                )
                # print "\n\n del_status == ",del_status
                # print "\n\n del_status_msg == ",del_status_msg

        if "CourseEventGroup" not in group_obj.member_of_names_list:
            get_node_metadata(request,img_node)
            teaches_list = request.POST.get('teaches_list','') # get the teaches list
            if teaches_list !='':
                teaches_list=teaches_list.split(",")
            create_grelation_list(img_node._id,"teaches",teaches_list)
            assesses_list = request.POST.get('assesses_list','')
            if assesses_list !='':
                assesses_list=assesses_list.split(",")

            create_grelation_list(img_node._id,"assesses",assesses_list)

            return HttpResponseRedirect(reverse('image_detail', kwargs={'group_id': group_id, '_id': img_node._id}))
        else:
            img_node.status = u"PUBLISHED"
            img_node.save()
            if course_tab_title:
                if course_tab_title == "raw material":
                    course_tab_title = "raw_material"
                return HttpResponseRedirect(reverse('course_'+course_tab_title + '_detail', kwargs={'group_id': group_id, 'node_id': str(img_node._id)}))
            return HttpResponseRedirect(reverse('course_about', kwargs={'group_id': group_id}))
            # url = "/"+ str(group_id) +"/?selected="+str(img_node._id)+"#view_page"
            # return HttpResponseRedirect(url)
    else:
        img_node.get_neighbourhood(img_node.member_of)
        return render_to_response("ndf/image_edit.html",
                                  {'node': img_node, 'title': title,
                                    'group_id': group_id,
                                    'groupid': group_id,
                                    'ce_id':ce_id,
                                    'res': res, 'course_tab_title':course_tab_title
                                },
                                  context_instance=RequestContext(request)
                              )

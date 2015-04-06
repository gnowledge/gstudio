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
from gnowsys_ndf.settings import META_TYPE, GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_node_common_fields,create_grelation_list,get_execution_time
from gnowsys_ndf.ndf.views.methods import get_node_metadata
from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute
gapp_mt = node_collection.one({'_type': "MetaType", 'name': META_TYPE[0]})
GST_IMAGE = node_collection.one({'member_of': gapp_mt._id, 'name': GAPPS[3]})


@get_execution_time
def imageDashboard(request, group_id, image_id=None):
    '''
    fetching image acording to group name
    '''
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    if image_id is None:
        image_ins = node_collection.find_one({'_type': "GSystemType", "name": "Image"})
        if image_ins:
            image_id = str(image_ins._id)
    img_col = node_collection.find({'_type': 'File', 'member_of': {'$all': [ObjectId(image_id)]}, 'group_set': {'$all': [ObjectId(group_id)]}})
    template = "ndf/ImageDashboard.html"
    already_uploaded=request.GET.getlist('var',"")
    variable = RequestContext(request, {'imageCollection': img_col,'already_uploaded':already_uploaded,'groupid':group_id,'group_id':group_id })
    return render_to_response(template, variable)

@get_execution_time
def getImageThumbnail(request, group_id, _id):
    '''
    this funciton can be called to get thumbnail of image throw url
    '''
    ins_objectid = ObjectId()
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
    img_obj = node_collection.one({"_type": u"File", "_id": ObjectId(_id)})

    if img_obj is not None:
        # getting latest uploaded pic's _id
        img_fs = img_obj.fs_file_ids[2]

        if (img_obj.fs.files.exists(img_fs)):
            f = img_obj.fs.files.get(ObjectId(img_fs))
            return HttpResponse(f.read(),content_type=f.content_type)
    else:
        return HttpResponse("")
        
@get_execution_time    
def getFullImage(request, group_id, _id, file_name = ""):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
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
    img_obj = node_collection.one({"_id": ObjectId(_id)})
    try:
        f = img_obj.fs.files.get(ObjectId(img_obj.fs_file_ids[2]))
        return HttpResponse(f.read(), content_type=f.content_type)
    except IndexError:
        f = img_obj.fs.files.get(ObjectId(img_obj.fs_file_ids[0]))
        return HttpResponse(f.read(), content_type=f.content_type)
        
@get_execution_time
def image_search(request,group_id):
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
    imgcol = node_collection.find({"_type": "File", 'mime_type': {'$regex': 'image'}})
    if request.method=="GET":
        keyword=request.GET.get("search","")
        img_search=node_collection.find({'$and':[{'mime_type':{'$regex': 'image'}},{'$or':[{'name':{'$regex':keyword}},{'tags':{'$regex':keyword}}]}]})
        template="ndf/file_search.html"
        variable=RequestContext(request,{'file_collection':img_search,'view_name':'image_search','groupid':group_id,'group_id':group_id})
        return render_to_response(template,variable)

@get_execution_time
def image_detail(request, group_id, _id):
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
                                    'groupid':group_id, 'imageCollection': imageCollection
                                  },
                                  context_instance = RequestContext(request)
        )

@get_execution_time
def image_edit(request,group_id,_id):
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
    img_node = node_collection.one({"_id": ObjectId(_id)})
    title = GST_IMAGE.name
    if request.method == "POST":

        # get_node_common_fields(request, img_node, group_id, GST_IMAGE)
        img_node.save(is_changed=get_node_common_fields(request, img_node, group_id, GST_IMAGE))
        
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
	img_node.get_neighbourhood(img_node.member_of)
        return render_to_response("ndf/image_edit.html",
                                  { 'node': img_node,'title': title,
                                    'group_id': group_id,
                                    'groupid':group_id
                                },
                                  context_instance=RequestContext(request)
                              )

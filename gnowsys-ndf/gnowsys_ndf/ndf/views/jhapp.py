import json
from django.http import HttpResponseRedirect
from django.http import HttpResponse
''' -- imports from installed packages -- ''' 
from django.shortcuts import render_to_response
from django.template import RequestContext
from gnowsys_ndf.ndf.views.methods import *
try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId
''' -- imports from application folders/files -- '''
# from gnowsys_ndf.ndf.models import Node, GRelation, GSystemType, File, Triple
from django.core.urlresolvers import reverse
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.templatetags.ndf_tags import check_is_gstaff
from gnowsys_ndf.settings import *

GST_JSMOL = node_collection.one({"_type":"GSystemType","name":"Jsmol"})
GST_POLICESQUAD = node_collection.one({"_type":"GSystemType","name":"PoliceSquad"})
@login_required
@get_execution_time
def jhapp(request, group_id):
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)
  jhapp_list = []
  for each in GSTUDIO_SUPPORTED_JHAPPS:
    each_node = node_collection.one({'name':unicode(each)})
    if each_node:
      jhapp_list.append(ObjectId(each_node._id))
  jhapp_res = node_collection.find({'member_of': {'$in': jhapp_list}})
  # print "*************",jhapp_res

  return render_to_response("ndf/jhapp.html",RequestContext(request, {"groupid":group_id, "group_id":group_id,'jhapp_res':jhapp_res}))

@login_required
@get_execution_time
def uploadjhapp(request, group_id):

  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)
  return render_to_response("ndf/uploadjhapp.html",RequestContext(request, {"groupid":group_id, "group_id":group_id,'gstudio_supported_jhapps':GSTUDIO_SUPPORTED_JHAPPS}))

@login_required
@get_execution_time
def savejhapp(request,group_id):
  from gnowsys_ndf.ndf.views.file import save_file
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)
  jhapp_type = request.POST.getlist("jhapp-type", "")
  jhapp_type_trim = jhapp_type[0].replace(" ", "")
  group_obj = node_collection.one({'_id': ObjectId(group_id)})
  title = request.POST.get('context_name','')
  usrid = request.user.id
  # jsmol_gst  = node_collection.one({"_type":"GSystemType","name":"Jsmol" })
  sel_jhapp_gst  = node_collection.one({"_type":"GSystemType","name":unicode(jhapp_type_trim) })
  
  import zipfile
  from gnowsys_ndf.ndf.views.filehive import write_files
  is_user_gstaff = check_is_gstaff(group_obj._id, request.user)
  
  fileobj_list = write_files(request, group_id)
  fileobj_id = fileobj_list[0]['_id']
  file_node = node_collection.one({'_id': ObjectId(fileobj_id) })
  
  if sel_jhapp_gst._id:
    file_node.member_of = [ObjectId(sel_jhapp_gst._id)]
  
  uploaded_files = request.FILES.getlist('filehive', [])
  zip_path = file_node.if_file.original['relurl']
  zip_split_path = zip_path.split('.')
  un_zip_path = zip_path.split('/')
  file_name = str(uploaded_files[0]).split(".")
  un_zip_split_path = "/data/media/"+un_zip_path[0] + "/" + un_zip_path[1] + "/" +un_zip_path[2] + "/"

  with zipfile.ZipFile("/data/media/"+ file_node.if_file.original['relurl'], "r") as z:
    z.extractall(un_zip_split_path)
  
  relurl_path = str("/" + un_zip_path[0] + "/" + un_zip_path[1] + "/" +un_zip_path[2] + "/" + file_name[0] + "/" + "index" + ".html" )
  # print "_______________________________",relurl_path
  discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
  for each_gs_file in fileobj_list:
      #set interaction-settings
      each_gs_file.status = u"PUBLISHED"
      if usrid not in each_gs_file.contributors:
          each_gs_file.contributors.append(usrid)

      group_object = node_collection.one({'_id': ObjectId(group_id)})
      if (group_object.edit_policy == "EDITABLE_MODERATED") and (group_object.moderation_level > 0):
          from gnowsys_ndf.ndf.views.moderation import get_moderator_group_set
          # print "\n\n\n\ninside editable moderated block"
          each_gs_file.group_set = get_moderator_group_set(each_gs_file.group_set, group_object._id)
          # print "\n\n\npage_node._id",page_node._id
          each_gs_file.status = u'MODERATION'
          # print "\n\n\n page_node.status",page_node.status
      each_gs_file.save()
      create_gattribute(each_gs_file._id, discussion_enable_at, True)
      return_status = create_thread_for_node(request,group_obj._id, each_gs_file)
  file_node.url = "/data/media/"+ file_node.if_file.original['relurl']
  file_node.if_file.original.relurl =  relurl_path
  file_node.if_file.mime_type = u"text/html"
  file_node.save()
  return HttpResponseRedirect( reverse('file_detail', kwargs={"group_id": group_id,'_id':fileobj_id}))
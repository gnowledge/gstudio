''' -- imports from installed packages -- '''
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response  # , render
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.cache import cache

from mongokit import paginator
import mongokit
import json

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import META_TYPE, GSTUDIO_NROER_GAPPS
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_GAPPS_LIST, GSTUDIO_WORKING_GAPPS, BENCHMARK
from gnowsys_ndf.ndf.models import db, node_collection, triple_collection
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.mobwrite.models import TextObj
from gnowsys_ndf.ndf.models import HistoryManager, Benchmark
from gnowsys_ndf.ndf.views.methods import get_execution_time, get_group_name_id
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.notification import models as notification
from gnowsys_ndf.ndf.views.moderation import create_moderator_task
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_thread_node, get_relation_value
from gnowsys_ndf.ndf.views.methods import create_thread_for_node

''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import datetime
import time
from sys import getsizeof, exc_info
import subprocess
import re
import ast
import string
import json
import locale
import multiprocessing as mp 
from datetime import datetime, timedelta, date
# import csv
# from collections import Counter
from collections import OrderedDict
col = db[Benchmark.collection_name]

# history_manager = HistoryManager()
# theme_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Theme'})
# theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item'})
# topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})

# C O M M O N   M E T H O D S   D E F I N E D   F O R   V I E W S

# grp_st = node_collection.one({'$and': [{'_type': 'GSystemType'}, {'name': 'Group'}]})
# ins_objectid = ObjectId()
reply_st = node_collection.one({ '_type':'GSystemType', 'name':'Reply'})

@login_required
@get_execution_time
def create_discussion(request, group_id, node_id):
  '''
  Method to create discussion thread for File and Page.
  '''

  try:
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    twist_st = node_collection.one({'_type':'GSystemType', 'name':'Twist'})

    node = node_collection.one({'_id': ObjectId(node_id)})
    thread = None

    if "Twist" in node.member_of_names_list:
        thread = node

    if not thread:
        thread_id = get_thread_node(node_id)
        if thread_id:
            thread = node_collection.one({'_id': ObjectId(thread_id)})
    # group = node_collection.one({'_id':ObjectId(group_id)})
    # thread = node_collection.one({"member_of": ObjectId(twist_st._id),"relation_set.thread_of.0": ObjectId(node._id)})
    # print "\n thread is ---", thread
    # thread = node_collection.one({ "_type": "GSystem", "name": node.name, "member_of": ObjectId(twist_st._id), "prior_node": ObjectId(node_id) })
    
    # the following code will never be executed
    # not commenting it for now.
    if not thread:
      # print "\n\n Creating Thread"
      thread_obj = create_thread_for_node(request, group_id, node)
      # print "\n thread_obj===",thread_obj
      # retriving RelationType
      # relation_type = node_collection.one({ "_type": "RelationType", "name": u"has_thread", "inverse_name": u"thread_of" })
      
      # Creating thread with the name of node
      # thread_obj = node_collection.collection.GSystem()

      # thread_obj.name = unicode(node.name)
      # thread_obj.status = u"PUBLISHED"

      # thread_obj.created_by = int(request.user.id)
      # thread_obj.modified_by = int(request.user.id)
      # thread_obj.contributors.append(int(request.user.id))

      # thread_obj.member_of.append(ObjectId(twist_st._id))
      # thread_obj.prior_node.append(ObjectId(node_id))
      # thread_obj.group_set.append(ObjectId(group_id))
      
      # thread_obj.save()
      # print "\n\n Thread id ", thread_obj._id
      # creating GRelation
      # create_grelation(node_id, relation_type, twist_st)
      if thread_obj:
          response_data = [ "thread-created", str(thread_obj._id) ]

      return HttpResponse(json.dumps(response_data))

    else:
      # print "\n\n Thread id Thread-exist ", thread._id
      response_data =  [ "Thread-exist", str(thread._id) ]

      return HttpResponse(json.dumps(response_data))
  
  except Exception as e:
    
    error_message = "\n DiscussionThreadCreateError: " + str(e) + "\n"
    raise Exception(error_message)
    # return HttpResponse("server-error")


# to add discussion replie
@get_execution_time
def discussion_reply(request, group_id, node_id):

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    try:
        group_object = node_collection.one({'_id': ObjectId(group_id)})
        prior_node = request.POST.get("prior_node_id", "")
        content_org = request.POST.get("reply_text_content", "") # reply content
        node = node_collection.one({"_id": ObjectId(node_id)})
        # gs_type_node_id = get_relation_value(node_id,'thread_of')
        gs_type_node_id = None
        if node and node.relation_set:
            for each_rel in node.relation_set:
                if each_rel and "thread_of" in each_rel:
                    gs_type_node_id = each_rel['thread_of'][0]
                    break
        # grel_dict = get_relation_value(node_id,'thread_of')
        # is_cursor = grel_dict.get("cursor",False)
        # if not is_cursor:
        #     gs_type_node_id = grel_dict.get("grel_node")
        #     # grel_id = grel_dict.get("grel_id")

        # print "\n\n node.name === ", node.member_of_names_list, node._id, node.name

        # process and save node if it reply has content  
        if content_org:
      
            user_id = int(request.user.id)
            user_name = unicode(request.user.username)

            # auth = node_collection.one({'_type': 'Author', 'name': user_name })
            
            # creating empty GST and saving it
            reply_obj = node_collection.collection.GSystem()

            reply_obj.name = unicode("Reply of:" + str(prior_node))
            reply_obj.status = u"PUBLISHED"

            reply_obj.created_by = user_id
            reply_obj.modified_by = user_id
            reply_obj.contributors.append(user_id)

            reply_obj.member_of.append(ObjectId(reply_st._id))
            reply_obj.prior_node.append(ObjectId(prior_node))
            reply_obj.group_set.append(ObjectId(group_id))
        
            reply_obj.content_org = unicode(content_org)
            filename = slugify(unicode("Reply of:" + str(prior_node))) + "-" + user_name + "-"
            # reply_obj.content = org2html(content_org, file_prefix=filename)
            reply_obj.content = content_org
            if gs_type_node_id:
                reply_obj.origin.append({'prior_node_id_of_thread': ObjectId(gs_type_node_id)})
            if node_id:
                reply_obj.origin.append({'thread_id': ObjectId(node_id)})

            # ==============================
            # try:

            upload_files_count=int(request.POST.get("upload_cnt",0))
            # print "upfiles=",upload_files_count
            lst=[]
            lstobj_collection=[]
            usrid = int(request.user.id)
            if upload_files_count > 0:
                # print "uploaded items",request.FILES.items()
                try:
                    thread_obj = node_collection.one({'_id': ObjectId(prior_node)})
                    # print "thread_obj : ", thread_obj
                    if thread_obj.access_policy:
                        access_policy = thread_obj.access_policy
                    else:
                        access_policy = u'PUBLIC'
                        
                except:
                    access_policy = u'PUBLIC'

                for key,value in request.FILES.items():
                    fname=unicode(value.__dict__['_name'])
                    # print "key=",key,"value=",value,"fname=",fname
                    
                    fileobj,fs=save_file(value,fname,usrid,group_id, "", "", username=unicode(request.user.username), access_policy=access_policy, count=0, first_object="", oid=True)


                    if type(fileobj) == list:
                        obid = str(list(fileobj)[1])
                    else:
                        obid=str(fileobj)

                    try:
                        file_obj=node_collection.find_one({'_id': ObjectId(obid)})
                        lstobj_collection.append(file_obj._id) 
                    except:
                        pass
                    if "CourseEventGroup" not in group_object.member_of_names_list:
                        if group_object.edit_policy == 'EDITABLE_MODERATED':
                            t = create_moderator_task(request, file_obj.group_set[0], file_obj._id,on_upload=True)
                # print "::: lstobj_collection: ", lstobj_collection
            # except:
                # lstobj_collection = []
            # ==============================
            reply_obj.collection_set = lstobj_collection
            # print "=== lstobj_collection: ", lstobj_collection
        
            # saving the reply obj
            reply_obj.save()
            formated_time = reply_obj.created_at.strftime("%B %d, %Y, %I:%M %p")

            files = []
            for each_coll_item in reply_obj.collection_set:
                temp_list = []
                temp = node_collection.one({'_id': ObjectId(each_coll_item)}, {'mime_type': 1, 'name': 1})
                temp_list.append(str(temp['_id']))
                temp_list.append(str(temp['mime_type']))
                temp_list.append(str(temp['name']))
                
                files.append(temp_list)

            # print files

            # ["status_info", "reply_id", "prior_node", "html_content", "org_content", "user_id", "user_name", "created_at" ]
            reply = json.dumps( [ "reply_saved", str(reply_obj._id), str(reply_obj.prior_node[0]), reply_obj.content, reply_obj.content_org, user_id, user_name, formated_time, files], cls=DjangoJSONEncoder )

            # print "===========", reply

            # ---------- mail/notification sending -------
            try:
                node_creator_user_obj = User.objects.get(id=node.created_by)
                node_creator_user_name = node_creator_user_obj.username
                if int(request.user.id) not in node.author_set:
                    node.author_set.append(int(request.user.id))
                    node.save()
                site = Site.objects.get(pk=1)
                site = site.name.__str__()
                
                from_user = user_name

                to_user_list = [node_creator_user_obj]

                msg = "\n\nDear " + node_creator_user_name + ",\n\n" + \
                      "A reply has been added in discussion under the " + \
                      node.member_of_names_list[0] + " named: '" + \
                      node.name + "' by '" + user_name + "'."

                activity = "Discussion Reply"
                render_label = render_to_string(
                    "notification/label.html",
                    {
                        # "sender": from_user,
                        "activity": activity,
                        "conjunction": "-",
                        "link": "url_link"
                    }
                )
                notification.create_notice_type(render_label, msg, "notification")
                notification.send(to_user_list, render_label, {"from_user": from_user})
            except Exception as notification_err:
                print "\n Unable to send notification", notification_err
            # ---------- END of mail/notification sending ---------
            return HttpResponse( reply )

        else: # no reply content

            return HttpResponse(json.dumps(["no_content"]))      

    except Exception as e:
      
        error_message = "\n DiscussionReplyCreateError: " + str(e) + "\n"
        raise Exception(error_message)

        return HttpResponse(json.dumps(["Server Error"]))


@get_execution_time
def discussion_delete_reply(request, group_id, node_id):

    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    nodes_to_delete = json.loads(request.POST.get("nodes_to_delete", "[]"))
    
    deleted_replies = []
    node_obj = node_collection.one({'_id': ObjectId(node_id)})
    # print "\n\nnode_obj.name", node_obj.name, node_obj.member_of_names_list,node_obj._id

    for each_reply in nodes_to_delete:
        temp_reply = node_collection.one({"_id": ObjectId(each_reply)})
        
        if temp_reply:
            deleted_replies.append(temp_reply._id.__str__())
            temp_reply.delete()

    replies_cur = node_collection.find({'origin.thread_id': ObjectId(node_id)})
    # print "\n replies_cur",replies_cur.count()
    if not replies_cur.count():
        author_set_ids = node_obj.author_set
        author_set_ids.remove(int(request.user.id))
        node_obj.author_set = author_set_ids
        node_obj.save()
    return HttpResponse(json.dumps(deleted_replies))


@login_required
@get_execution_time
def edit_comment(request, group_id, node_id=None,call_from_discussion=None):
    
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    if request.GET:
        node_id = request.GET.get('sourceObjDataId');
    content_val = None
    if request.POST:
        content_val = request.POST.get("content_val", "")
        node_id = request.POST.get('sourceObjDataId')
    if node_id:
        node_id = node_id.strip()
        node_obj = node_collection.one({'_id': ObjectId(node_id)})
        if content_val:
            node_obj.content = content_val
            node_obj.save()

    context_variables = {
            'group_id': group_id, 'groupid': group_id,'node': node_obj,'node_id':node_id
            }

    template = 'ndf/html_editor.html'
    context_variables['var_name'] = "content_org",
    context_variables['var_value'] = node_obj.content
    context_variables['node_id'] = node_obj._id
    context_variables['ckeditor_toolbar'] ="BasicToolbar" 

    return render_to_response(template, context_variables, context_instance = RequestContext(request))

@get_execution_time
def get_thread_comments_count(request, group_id, thread_node_id):
  return HttpResponse(node_collection.find({'member_of': reply_st._id, 'origin.thread_id':ObjectId(thread_node_id)}).count())
  # return HttpResponse(json.dumps(result_set))
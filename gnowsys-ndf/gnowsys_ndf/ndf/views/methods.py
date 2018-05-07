''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import datetime
import time
import subprocess
import re
import ast
import string
import json
import locale
import pymongo
import multiprocessing as mp
import mongokit
import json
# import csv

from sys import getsizeof, exc_info
from bson import BSON
from bson import json_util
# from datetime import datetime, timedelta, date
from collections import OrderedDict
from mongokit import paginator
# from collections import Counter

''' -- imports from installed packages -- '''
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.shortcuts import render_to_response  # , render
from django.http import HttpResponse, HttpRequest
from django.core.serializers.json import DjangoJSONEncoder
from django.core.cache import cache
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
# to display error template if non existent pub is given in settings.py
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import PermissionDenied

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import META_TYPE, GSTUDIO_NROER_GAPPS, GSTUDIO_IMPLICIT_ENROLL
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_GAPPS_LIST, GSTUDIO_WORKING_GAPPS, BENCHMARK, GSTUDIO_DEFAULT_LANGUAGE
from gnowsys_ndf.settings import LANGUAGES, OTHER_COMMON_LANGUAGES, GSTUDIO_BUDDY_LOGIN, DEFAULT_DISCUSSION_LABEL
# from gnowsys_ndf.ndf.models import db, node_collection, triple_collection, counter_collection
from gnowsys_ndf.ndf.models import *
# from gnowsys_ndf.ndf.org2any import org2html
# from gnowsys_ndf.mobwrite.models import TextObj
from gnowsys_ndf.ndf.models import HistoryManager, Benchmark
from gnowsys_ndf.notification import models as notification
# get pub of gpg key with which to sign syncdata attachments
from gnowsys_ndf.settings import SYNCDATA_KEY_PUB, GSTUDIO_MAIL_DIR_PATH
from gnowsys_ndf.ndf.views.tasks import record_in_benchmark
from datetime import datetime, timedelta, date
from gnowsys_ndf.ndf.views.utils import get_dict_from_list_of_dicts

history_manager = HistoryManager()
theme_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Theme'})
theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item'})
topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
grp_st = node_collection.one({'$and': [{'_type': 'GSystemType'}, {'name': 'Group'}]})
ins_objectid = ObjectId()
player_disc_enable_at_name, player_disc_enable_at_id = Node.get_name_id_from_type('player_discussion_enable', 'AttributeType')

# C O M M O N   M E T H O D S   D E F I N E D   F O R   V I E W S

def staff_required(func):
    """
    Decorator for CRUD views of Group and Event to check whether a user
    is allowed and is active.
    Currently, ONLY SuperUsers will be allowed.
    """
    def wrapper(*args, **kwargs):
        for arg in args:
            if arg.user.is_superuser and arg.user.is_active:
                return func(*args, **kwargs)
            raise PermissionDenied
    return wrapper


def get_execution_time(f):
    def wrap(*args,**kwargs):

        time1 = time.time()
        ret = f(*args,**kwargs)
        time2 = time.time()

        post_bool = get_bool = False,
        sessionid = user_name = path = '',

        req = args[0] if len(args) else None
        locale = 'en'

        if isinstance(req, WSGIRequest):
            # try :
            post_bool = bool(args[0].POST)
            get_bool = bool(args[0].GET)
            locale = req.LANGUAGE_CODE
            # except :
            #     pass

            try :
                sessionid = unicode(args[0].COOKIES['sessionid'])
            except :
                pass

            try :
                user_name = unicode(args[0].user.username)
            except :
                pass

            # try :
            path = unicode(args[0].path)
            # except :
            #     pass

        record_in_benchmark(kwargs_len=len(kwargs),
                            # total_param_size=sum([getsizeof(each_kwarg) for each_kwarg in kwargs.values()]),
                            total_param_size=None,
                            post_bool=post_bool,
                            get_bool=get_bool,
                            sessionid=sessionid,
                            user_name=user_name,
                            path=path,
                            funct_name=f.func_name,
                            time_taken=unicode(str(time2 - time1)),
                            locale=locale

                        )
        return ret
    return wrap


import json
import bson
import shutil
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage

def server_sync(func):
    def wrap(*args, **kwargs):
        ret = func(*args, **kwargs)


        #do a regex check on SYNCDATA_KEY_PUB, if it contains anything other than letters and nos DONOT run the subprocess.call()
        # function as this can be a potential security LOOPHOLE
        #if pub is found to be invalid changes WILL NOT be captured
        searchObj = re.search( r'[^A-Za-z0-9]', SYNCDATA_KEY_PUB, re.M|re.I)
        if searchObj:
            print "Invalid character found in SYNCDATA_KEY_PUB. Please ensure valid existing PUB has been added to local_settings.py", searchObj.group()
            return

        check_command = 'gpg --list-keys | grep -o "'+SYNCDATA_KEY_PUB+'"'
        std_out= subprocess.call([check_command],shell=True)
        #code to check if SYNCDATA_KEY_PUB in local settings.py is a pub which is present in the gpg database of the system
        #if not, change WILL NOT be captured
        #std_out will have shell command return code =0 (success) 1 (failure)
        if str(std_out) == '1':
            error_obj =  "Given pub = %s is not in gpg database of your system. Failed to capture changes for syncdata" % SYNCDATA_KEY_PUB
            print '**'*30
            print '\n'*3
            print error_obj
            print '\n'*3
            print '**'*30
            return

        ''' Get current date and time to timestamp json and the document being captured by this function.
         This done so that files in syncdata folder will have unique name'''
        #timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S').replace(" ","_").replace("/","_") + "_" + str(datetime.now().microsecond)
        timestamp = kwargs['time']

        ''' To fetch the data about the node '''
        # the actual file
        file_data = kwargs['file_data']
        # the node file
        node = kwargs['file_object']
        # content-type of the file
        content_type = kwargs['content_type']

        ''' path where the json file that contains the information about node is located '''
        settings_dir1 = os.path.dirname(__file__)
        settings_dir2 = os.path.dirname(settings_dir1)
        settings_dir3 = os.path.dirname(settings_dir2)
        gen_path = os.path.abspath(os.path.dirname(settings_dir3))

        print '+' * 20
        print gen_path

        file_path = ""
        file_name_filtered = ""
        if file_data:
            file_name_filtered = file_data.name
            special_char = ['!','?','$','%','$','#','&','*','(',')','   ','|',';','\"','<','>','~','`','[',']','{','}',' ']
            for i in special_char:
                file_name_filtered = file_name_filtered.replace(i,'')
            file_path = gen_path + '/' + str(file_name_filtered)

        node_data_path = gen_path + '/node_data.json'
        # subject += str(node._id)

        print '+' * 20
        print node_data_path

        if 'image' in content_type or 'video' in content_type:
            # To make the fs_file_ids filed set empty
            if file_data:
                node.fs_file_ids = []
                # pass the image data as attachment
                file_data.seek(0)
                # path = default_storage.save(file_path, ContentFile(file_data.read()))
                with open(file_path,'wb+') as outfile:
                    outfile.write(file_data.read())


        else:
            #the other documents which need only the json data to be sent
            if file_data:
                node.fs_file_ids = []
                file_data.seek(0)
                file_path = gen_path + '/' + str(file_name_filtered)
                # path = default_storage.save(file_path, ContentFile(file_data.read()))
                with open(file_path,'wb+') as outfile:
                    outfile.write(file_data.read())

        ''' Code to sign the document file, prefix timestamp to document file name and move it to syncdata folder '''
        path1 = os.path.dirname(__file__)
        path2 = os.path.dirname(path1)

        settings_dir = os.path.dirname(__file__)
        PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
        # path_MailClient = os.path.join(PROJECT_ROOT, 'MailClient/')
        path_MailClient = GSTUDIO_MAIL_DIR_PATH

        if not os.path.exists(path_MailClient):
            os.makedirs(path_MailClient)

        p1 = path_MailClient + '/syncdata/'

        if not os.path.exists(p1):
            os.makedirs(p1)

        p1 = path_MailClient + '/sent_syncdata_files/'

        if not os.path.exists(p1):
            os.makedirs(p1)

        dst = str(path2) + "/MailClient/syncdata"

        print '+' * 20
        print dst

        if not os.path.exists(dst):
            os.makedirs(dst)
        path_for_this_capture = dst + '/' + timestamp +"_"+ str(node["_id"])

        print '+' * 20
        print path_for_this_capture

        if not os.path.exists(path_for_this_capture):
            os.makedirs(path_for_this_capture)

        if file_data:

            # '.gpg' in output file name is later used to split the filename and obtain original file name in received attachments in
            # 'server_sync()' function of mailclient.py views file

            #make filename.extension --> filename_extension since finally the name should be filename_extension.gpg
            op_file_name = file_path.split(file_name_filtered)[0]+ timestamp + '_' + file_name_filtered + '_sig'
            print ':' * 20
            print op_file_name
            print ':' * 20
            print file_path
            command = 'gpg -u ' + SYNCDATA_KEY_PUB + ' --output ' + op_file_name + ' --sign ' + file_path
            subprocess.call([command],shell=True)
            src = op_file_name

            print '+' * 20

            shutil.move(src,path_for_this_capture)
            # mail.attach_file(file_path)

        print 'JSON'
        node_json = bson.json_util.dumps(node)
        print "creating the file",node['_id']
        with open(node_data_path,'w') as outfile:
            json.dump(node_json, outfile)
        ''' Run command to sign the json file, rename and move to syncdata folder'''
        #add _sig otherwise django_mailbox scrambles file name
        json_op_file_name = node_data_path.split('node_data.json')[0]+ timestamp + '_' + 'node_data.json' + '_sig'
        print os.path.exists(node_data_path)
        command = 'gpg --batch --yes -u ' + SYNCDATA_KEY_PUB + ' --output ' + json_op_file_name + ' --sign ' + node_data_path
        subprocess.call([command],shell=True)
        src = json_op_file_name
        shutil.move(src,path_for_this_capture)
        # mail.attach_file(json_op_file_name)

        # mail.attach_file(node_data_path)
        # mail.subject = subject + str(node._id)
        #mail.send()
        if os.path.exists(node_data_path):
            os.remove(node_data_path)
        # os.remove(json_op_file_name)
        if file_data:
            os.remove(file_path)
            # os.remove(op_file_name)
        return ret
        print "opertation finish"
    return wrap

@get_execution_time
@server_sync
def capture_data(file_object=None, file_data=None, content_type=None,time=None):
    '''
    Serves as an itermediate function to capture the node details and allow
    the decorator to send the created/updated node through E-Mail
    '''
    pass

@get_execution_time
def get_group_name_id(group_name_or_id, get_obj=False):
    '''
      - This method takes possible group name/id as an argument and returns (group-name and id) or group object.

      - If no second argument is passed, as method name suggests, returned result is "group_name" first and "group_id" second.

      - When we need the entire group object, just pass second argument as (boolian) True. In the case group object will be returned.

      Example 1: res_group_name, res_group_id = get_group_name_id(group_name_or_id)
      - "res_group_name" will contain name of the group.
      - "res_group_id" will contain _id/ObjectId of the group.

      Example 2: res_group_obj = get_group_name_id(group_name_or_id, get_obj=True)
      - "res_group_obj" will contain entire object.

      Optimization Tip: before calling this method, try to cast group_id to ObjectId as follows (or copy paste following snippet at start of function or wherever there is a need):
      try:
          group_id = ObjectId(group_id)
      except:
          group_name, group_id = get_group_name_id(group_id)

    '''
    # if cached result exists return it
    if not get_obj:
        slug = slugify(group_name_or_id)
        # for unicode strings like hindi-text slugify doesn't works
        cache_key = 'get_group_name_id_' + str(slug) if slug else str(abs(hash(group_name_or_id)))
        cache_result = cache.get(cache_key)

        if cache_result:
            return (cache_result[0], ObjectId(cache_result[1]))
    # ---------------------------------

    # case-1: argument - "group_name_or_id" is ObjectId
    if ObjectId.is_valid(group_name_or_id):

        group_obj = node_collection.one({"_id": ObjectId(group_name_or_id)})

        # checking if group_obj is valid
        if group_obj:
            # if (group_name_or_id == group_obj._id):
            group_id = group_name_or_id
            group_name = group_obj.name

            if get_obj:
                return group_obj
            else:
                # setting cache with both ObjectId and group_name
                cache.set(cache_key, (group_name, group_id), 60 * 60)
                cache_key = u'get_group_name_id_' + slugify(group_name)
                cache.set(cache_key, (group_name, group_id), 60 * 60)
                return group_name, group_id

    # case-2: argument - "group_name_or_id" is group name
    else:
        group_obj = node_collection.one(
            {"_type": {"$in": ["Group", "Author"]}, "name": unicode(group_name_or_id)})

        # checking if group_obj is valid
        if group_obj:
            # if (group_name_or_id == group_obj.name):
            group_name = group_name_or_id
            group_id = group_obj._id

            if get_obj:
                return group_obj
            else:
                # setting cache with both ObjectId and group_name
                cache.set(cache_key, (group_name, group_id), 60*60)
                cache_key = u'get_group_name_id_' + slugify(group_name)
                cache.set(cache_key, (group_name, group_id), 60*60)
                return group_name, group_id

    if get_obj:
        return None
    else:
        return None, None


@login_required
def update_notes_or_files_visited(user_id, group_id,node_id,if_file,if_note) :
    # counter_obj = Counter.get_counter_obj(user_id, group_id)
    # if if_file:
    #     file_node_obj = node_collection.one({'_id': node_id})
    #     file_creator_id = file_node_obj.created_by
    #     if file_creator_id != user_id :
    #         # counter_obj.no_others_files_visited += 1
    #         counter_obj['file']['visits_on_others_res'] += 1
    #         counter_obj_creator = Counter.get_counter_obj(file_creator_id, group_id)
    #         # counter_obj_creator.no_visits_gained_on_files += 1
    #         counter_obj_creator['file']['visits_gained'] += 1
    #         counter_obj_creator.last_update = datetime.now()
    #         counter_obj_creator.save()

    # elif if_note:
    #     note_node_obj = node_collection.one({'_id':node_id})
    #     note_creator_id = note_node_obj.created_by
    #     if note_creator_id != user_id :
    #         # counter_obj.no_others_notes_visited += 1
    #         counter_obj['page']['blog']['visits_on_others_res'] += 1
    #         counter_obj_creator = Counter.get_counter_obj(note_creator_id, group_id)
    #         # counter_obj_creator.no_views_gained_on_notes += 1
    #         counter_obj_creator['page']['blog']['visits_gained'] += 1
    #         counter_obj_creator.last_update = datetime.now()
    #         counter_obj_creator.save()

    # counter_obj.last_update = datetime.now()
    # counter_obj.save()

    active_user_ids_list = [user_id]
    if GSTUDIO_BUDDY_LOGIN:
        active_user_ids_list += Buddy.get_buddy_userids_list_within_datetime(user_id, datetime.now())
        # removing redundancy of user ids:
        active_user_ids_list = dict.fromkeys(active_user_ids_list).keys()

    counter_objs_cur = Counter.get_counter_objs_cur(active_user_ids_list, group_id)

    for each_counter_obj in counter_objs_cur:
        if if_file:
            file_node_obj = node_collection.one({'_id': node_id})
            file_creator_id = file_node_obj.created_by
            if file_creator_id != user_id:
                # each_counter_obj.no_others_files_visited += 1
                each_counter_obj['file']['visits_on_others_res'] += 1
                counter_obj_creator = Counter.get_counter_obj(file_creator_id, group_id)
                # counter_obj_creator.no_visits_gained_on_files += 1
                counter_obj_creator['file']['visits_gained'] += 1
                counter_obj_creator.last_update = datetime.now()
                counter_obj_creator.save()

        elif if_note:
            note_node_obj = node_collection.one({'_id':node_id})
            note_creator_id = note_node_obj.created_by
            if note_creator_id != user_id :
                # each_counter_obj.no_others_notes_visited += 1
                each_counter_obj['page']['blog']['visits_on_others_res'] += 1
                counter_obj_creator = Counter.get_counter_obj(note_creator_id, group_id)
                # counter_obj_creator.no_views_gained_on_notes += 1
                counter_obj_creator['page']['blog']['visits_gained'] += 1
                counter_obj_creator.last_update = datetime.now()
                counter_obj_creator.save()

        each_counter_obj.last_update = datetime.now()
        each_counter_obj.save()


@get_execution_time
def create_task(request,group_id,task_dict,set_notif_val,attribute_list):
   '''
        creates a task for assignee
   '''
   try:
           usr=request.user.id
           task_node = collection.GSystem()
           GST_TASK = collection.Node.one({'_type': "GSystemType", 'name': 'Task'})
           grp=collection.Node.one({'_id':ObjectId(group_id)})
           if not grp:
                   return
           else:
                   group_name=grp.name
           if request.method == "POST": # create
                   task_node.name = unicode(task_dict['name'])
                   task_node.content_org = unicode(task_dict['content_org'])
                   task_node.created_by=usr
                   if GST_TASK._id not in task_node.member_of:
                           task_node.member_of.append(GST_TASK._id)
                   if usr not in task_node.contributors:
                           task_node.contributors.append(request.user.id)
                   if group_id not in task_node.group_set:
                           task_node.group_set.append(grp._id)
                   task_node.status=u'DRAFT'
                   task_node.url= u'task'
                   task_node.language = ('en', 'English')
                   contr=[]
                   contr.append(usr)
                   task_node.contributors=contr
                   parent = task_dict['parent']
                   Status = task_dict['Status']
                   Start_date = task_dict['start_time']
                   Priority = task_dict['Priority']
                   Due_date = task_dict['end_time']
                   Estimated_time = task_dict['Estimated_time']
                   watchers = task_dict['watchers']
                   if watchers:
                           for each_watchers in watchers.split(','):
                                   bx=User.objects.get(username=each_watchers)
                                   task_node.author_set.append(bx.id)
                   task_node.save()
                   # filename = task_node.name
                   # task_node.content = org2html(task_dict['content_org'], file_prefix=filename)
                   # task_node.save()
                   if parent: # prior node saving
                           task_node.prior_node = [ObjectId(parent)]
                           parent_object = collection.Node.find_one({'_id':ObjectId(parent)})
                           parent_object.post_node = [task_node._id]
                           parent_object.save()
                           task_node.save()
                   for each in attribute_list:
                           if task_dict.has_key(str(each)) :
                                   if not task_dict[each] == "":
                                           attributetype_key = collection.Node.find_one({"_type":'AttributeType', 'name':each})
                                           newattribute = collection.GAttribute()
                                           newattribute.subject = task_node._id
                                           newattribute.attribute_type = attributetype_key
                                           if type(task_dict[each]) == date_time.datetime :
                                                   newattribute.name= task_dict['name']+"--"+str(each)+"--"+str(task_dict[str(each)])

                                           else:
                                                   if each == 'Assignee':
                                                           usr_ob=User.objects.get(id=task_dict['Assignee'])
                                                           if usr_ob:
                                                                   newattribute.name= task_dict['name']+"--"+str(each)+"--"+usr_ob.username
                                                   else:
                                                           newattribute.name= task_dict['name']+"--"+str(each)+"--"+unicode(task_dict[str(each)])
                                           if each == 'start_time' or each == 'end_time':
                                                   newattribute.object_value=task_dict[str(each)]
                                           else:
                                                   if each == 'Assignee':
                                                           usr_ob=User.objects.get(id=task_dict['Assignee'])
                                                           if usr_ob:
                                                                   newattribute.object_value = unicode(usr_ob.username)
                                                   else:
                                                           newattribute.object_value = unicode(task_dict[str(each)])
                                           newattribute.save()
                   if task_dict['Assignee'] :
                            activ="task reported"
                            msg="Task -"+task_node.name+"- has been reported by "+"\n     - Status: "+task_dict['Status']+"\n     -  Url: http://"+sitename.name+"/"+group_name.replace(" ","%20").encode('utf8')+"/task/"+str(task_node._id)+"/"
                            bx=User.objects.get(id=task_dict['Assignee'])
                            site=sitename.name.__str__()
                            objurl="http://test"
                            render = render_to_string("notification/label.html",{'sender':request.user.username,'activity':activ,'conjunction':'-','object':group_id,'site':site,'link':objurl})
                            notification.create_notice_type(render, msg, "notification")
                            notification.send([bx], render, {"from_user": request.user})

           return task_node
   except Exception as e:
           print "Exception in create_task "+ str(e)

def create_task_for_activity(request,group_id,activity_dict,get_assignee_list,set_notif_val):
    """Creates a task for an activity and notify assignee.
    """
    try:
        ins_objectid  = ObjectId()
        if ins_objectid.is_valid(group_id) is False :
            group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
            if group_ins:
                group_id = str(group_ins._id)
            else:
                auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
                if auth:
                    group_id=str(auth._id)
        elif ins_objectid.is_valid(group_id) is True :
            group_ins = collection.Node.find_one({'_type': "Group","_id": ObjectId(group_id)})
            if group_ins:
                group_id = str(group_ins._id)
        grp=collection.Node.one({'_id':ObjectId(group_id)})
        group_name=grp.name
        at_list = ["Status", "start_time", "Priority", "end_time", "Assignee"]
        task_dict=activity_dict
        assignee=grp.created_by
        task_dict['Assignee']=assignee
        main_task=create_task(request,group_id,task_dict,set_notif_val,at_list)
        if not main_task:
                return
        if not get_assignee_list:
                return
        if len(get_assignee_list) == 1 : #Single assignee
                #IF IT'S SINGLE ASSIGNEE CREATE A SINGLE TASK ON ASSIGNEE
                assignee=get_assignee_list[0]
                task_dict['Assignee']=assignee
                one_task=create_task(request,group_id,task_dict,set_notif_val,at_list)
                return
        else:
                task_collection_list=[]
                if len(get_assignee_list) > 1 : #task collection
                        #CREATE A GROUP TASK (TASK_COLLECTION)
                        for each in get_assignee_list:
                                if not each == grp.created_by and not request.user.id == each: # check if uploaded user is not moderator or creator
                                        task_dict['Assignee']=each
                                        task=create_task(request,group_id,task_dict,set_notif_val,at_list)
                                        if task:
                                                task_collection_list.append(task._id)
                        if task_collection_list:
                                op = collection.update({'_id': ObjectId(main_task._id)}, {'$set': {'collection_set': task_collection_list}})
        return
    except Exception as e:
        print "Exception in create_task_for_activity "+str(e)


def get_all_subscribed_users(group_id):
  grp=node_collection.one({'_id':ObjectId(group_id)})
  ins_objectid  = ObjectId()
  all_users=[]
  if ins_objectid.is_valid(group_id) :
    if grp.author_set:
      all_users=grp.author_set
    if grp.created_by in all_users:
      all_users.remove(grp.created_by)
  return all_users

def get_all_admins(group_id):
  grp=node_collection.one({'_id':ObjectId(group_id)})
  return grp.group_admin


def check_if_moderated_group(group_id):
  grp=node_collection.one({'_id':ObjectId(group_id)})
  ins_objectid  = ObjectId()
  # print "edtpol",grp.edit_policy
  if ins_objectid.is_valid(group_id) :
    if grp.edit_policy == "EDITABLE_MODERATED":
      return True
    else:
      return False
  else:
    return False


def check_delete(main):
    try:

        def check(*args, **kwargs):
            relns = ""
            node_id = kwargs['node_id']
            ins_objectid = ObjectId()
            if ins_objectid.is_valid(node_id):
                node = node_collection.one({'_id': ObjectId(node_id)})
                relns = node.get_possible_relations(node.member_of)
                attrbts = node.get_possible_attributes(node.member_of)
                return main(*args, **kwargs)
            else:
                print "Not a valid id"
        return check
    except Exception as e:
        print "Error in check_delete " + str(e)


@get_execution_time
def get_all_resources_for_group(group_id):
    if ins_objectid.is_valid(group_id):
        obj_resources = node_collection.find({'$and': [{'$or': [{'_type': 'GSystem'}, {'_type': 'File'}]}, {
                                             'group_set': {'$all': [ObjectId(group_id)]}}, {'member_of': {'$nin': [grp_st._id]}}]})
        return obj_resources


@get_execution_time
def get_gapps(default_gapp_listing=False, already_selected_gapps=[]):
    """Returns list of GApps.

    Arguments:
    default_gapp_listing -- (Optional argument)
        - This is to decide which list should be considered for listing GAPPs;
        that is, in menu-bar and GAPPs selection menu for a given group
        - True: DEFAULT_GAPPS (menu-bar)
            - At present used in listing GAPPS whenever a new group is created
        - False: GSTUDIO_WORKING_GAPPS (selection-menu)
            - At present used in listing GAPPS for setting-up GAPPS for a group

    already_selected_gapps -- (Optional argument)
        - List of GApps already set for a given group in form of
        dictionary variable
        - If specified, then these listed GApps are excluded from
        the list of GApps returned by this function

    Returns:
        - List of GApps where each GApp is in form of node/dictionary
    """
    gapps_list = []

    global GSTUDIO_DEFAULT_GAPPS_LIST
    gapps_list = GSTUDIO_DEFAULT_GAPPS_LIST

    if not gapps_list or not default_gapp_listing:
                # If GSTUDIO_DEFAULT_GAPPS_LIST not set (i.e. empty)
                # Or we need to setup list for selection purpose of GAPPS
                # for a group
        gapps_list = GSTUDIO_WORKING_GAPPS

        # If already_selected_gapps is non-empty,
        # Then append their names in list of GApps to be excluded
        if already_selected_gapps:
            gapps_list_remove = gapps_list.remove
            #Function used by Processes implemented below
            def multi_(lst):
              for each_gapp in lst:
                gapp_name = each_gapp["name"]

                if gapp_name in gapps_list:
                    gapps_list_remove(gapp_name)
            #this empty list will have the Process objects as its elements
            processes=[]
            n1=len(already_selected_gapps)
            lst1=already_selected_gapps
            #returns no of cores in the cpu
            x=mp.cpu_count()
            #divides the list into those many parts
            n2=n1/x
            #Process object is created.The list after being partioned is also given as an argument.
            for i in range(x):
              processes.append(mp.Process(target=multi_,args=(lst1[i*n2:(i+1)*n2],)))
            for i in range(x):
              processes[i].start() #each Process started
            for i in range(x):
              processes[i].join() #each Process converges
    # Find all GAPPs
    meta_type = node_collection.one({
        "_type": "MetaType", "name": META_TYPE[0]
    })
    gapps_cur = None
    gapps_cur = node_collection.find({
        "_type": "GSystemType", "member_of": meta_type._id,
        "name": {"$in": gapps_list}
    }).sort("created_at")

    return list(gapps_cur)


@get_execution_time
def forum_notification_status(group_id, user_id):
    """Checks forum notification turn off for an author object
    """
    try:
        grp_obj = node_collection.one({'_id': ObjectId(group_id)})
        auth_obj = node_collection.one({'_id': ObjectId(user_id)})
        at_user_pref = node_collection.one(
            {'$and': [{'_type': 'AttributeType'}, {'name': 'user_preference_off'}]})
        list_at_pref = []
        if at_user_pref:
            poss_attrs = auth_obj.get_possible_attributes(at_user_pref._id)
            if poss_attrs:
                if 'user_preference_off' in poss_attrs:
                    list_at_pref = poss_attrs[
                        'user_preference_off']['object_value']
                if grp_obj in list_at_pref:
                    return False
                else:
                    return True
        return True
    except Exception as e:
        print "Exception in forum notification status check " + str(e)


@get_execution_time
def get_forum_repl_type(forrep_id):
    forum_st = node_collection.one(
        {'$and': [{'_type': 'GSystemType'}, {'name': GAPPS[5]}]})
    obj = node_collection.one({'_id': ObjectId(forrep_id)})
    if obj:
        if forum_st._id in obj.member_of:
            return "Forum"
        else:
            return "Reply"
    else:
        return "None"


@get_execution_time
def check_existing_group(group_name):
    if type(group_name) == 'unicode':
        colg = node_collection.find({'_type': u'Group', "name": group_name})
        if colg.count() > 0:
            return True
        if ins_objectid.is_valid(group_name):  # if group_name holds group_id
            colg = node_collection.find(
                {'_type': u'Group', "_id": ObjectId(group_name)})
        if colg.count() > 0:
            return True
        else:
            colg = node_collection.find(
                {'_type': {'$in': ['Group', 'Author']}, "_id": ObjectId(group_name)})
            if colg.count() > 0:
                return True
    else:
        if ins_objectid.is_valid(group_name):  # if group_name holds group_id
            colg = node_collection.find(
                {'_type': u'Group', "_id": ObjectId(group_name)})
            if colg.count() > 0:
                return True
            colg = node_collection.find(
                {'_type': {'$in': ['Group', 'Author']}, "_id": ObjectId(group_name)})
            if colg.count() > 0:
                return True
        else:
            colg = node_collection.find(
                {'_type': {'$in': ['Group', 'Author']}, "_id": group_name._id})
    if colg.count() >= 1:
        return True
    else:
        return False


@get_execution_time
def filter_drawer_nodes(nid, group_id=None):
    page_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Page'})
    file_gst = node_collection.one({'_type': 'GSystemType', 'name': 'File'})
    Pandora_video_gst = node_collection.one(
        {'_type': 'GSystemType', 'name': 'Pandora_video'})
    quiz_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Quiz'})
    quizItem_gst = node_collection.one(
        {'_type': "GSystemType", 'name': "QuizItem"})
    query = None

    if group_id:
        query = {'_type': {'$in': ['GSystem', 'File']}, 'group_set': ObjectId(group_id),
                 'collection_set': {'$exists': True, '$not': {'$size': 0}, '$in': [ObjectId(nid)]},
                 'member_of': {'$in': [page_gst._id, file_gst._id, Pandora_video_gst._id, quiz_gst._id, quizItem_gst._id]}
                 }

    else:
        query = {'_type': {'$in': ['GSystem', 'File']}, 'collection_set': {'$exists': True, '$not': {'$size': 0}, '$in': [ObjectId(nid)]},
                 'member_of': {'$in': [page_gst._id, file_gst._id, Pandora_video_gst._id, quiz_gst._id, quizItem_gst._id]}
                 }

    nodes = node_collection.find(query)

    # Remove parent nodes in which current node exists

    def filter_nodes(parents, group_id=None):
        length = []
        if parents:
            length.extend(parents)

            inner_parents = []
            for each in parents:
                if group_id:
                    query = {'_type': {'$in': ['GSystem', 'File']}, 'group_set': ObjectId(group_id),
                             'collection_set': {'$exists': True, '$not': {'$size': 0}, '$in': [ObjectId(each)]},
                             'member_of': {'$in': [page_gst._id, file_gst._id, Pandora_video_gst._id, quiz_gst._id, quizItem_gst._id]}
                             }
                else:
                    query = {'_type': {'$in': ['GSystem', 'File']},
                             'collection_set': {'$exists': True, '$not': {'$size': 0}, '$in': [ObjectId(each)]},
                             'member_of': {'$in': [page_gst._id, file_gst._id, Pandora_video_gst._id, quiz_gst._id, quizItem_gst._id]}
                             }

                nodes = node_collection.find(query)
                if nodes.count() > 0:
                    for k in nodes:
                        inner_parents.append(k._id)

            for each in inner_parents:
                if each not in parents:
                    parents.append(each)

            if set(length) != set(parents):
                parents = filter_nodes(parents, group_id)
                return parents
            else:
                return parents

    parents_list = []
    if nodes.count() > 0:
        for each in nodes:
            parents_list.append(each._id)

        parents = filter_nodes(parents_list, group_id)
        return parents
    else:
        return parents_list


@get_execution_time
def get_drawers(group_id, nid=None, nlist=[], page_no=1, checked=None, **kwargs):
    """Get both drawers-list.
    """
    dict_drawer = {}
    dict1 = {}
    # Changed from dictionary to list so that it's content are reflected in a
    # sequential-order
    dict2 = []
    filtering = []

    drawer = None
    if checked:
        if nid:
            filtering = filter_drawer_nodes(nid, group_id)

        if checked == "Page":
            gst_page_id = node_collection.one(
                {'_type': "GSystemType", 'name': "Page"})._id
            drawer = node_collection.find({'_type': u"GSystem", '_id': {'$nin': filtering}, 'member_of': {
                                          '$all': [gst_page_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "File":
            drawer = node_collection.find({'_type': u"File", '_id': {
                                          '$nin': filtering}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "Image":
            gst_image_id = node_collection.one(
                {'_type': "GSystemType", 'name': "Image"})._id
            drawer = node_collection.find({'_type': u"File", '_id': {'$nin': filtering}, 'member_of': {
                                          '$in': [gst_image_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "Video":
            gst_video_id = node_collection.one(
                {'_type': "GSystemType", 'name': "Video"})._id
            drawer = node_collection.find({'_type': u"File", '_id': {'$nin': filtering}, 'member_of': {
                                          '$in': [gst_video_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "Quiz":
            # For prior-node-list
            drawer = node_collection.find({'_type': {'$in': [u"GSystem", u"File"]}, '_id': {
                                          '$nin': filtering}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "QuizObj" or checked == "assesses":
            # For collection-list
            gst_quiz_id = node_collection.one(
                {'_type': "GSystemType", 'name': "Quiz"})._id
            gst_quiz_item_id = node_collection.one(
                {'_type': "GSystemType", 'name': "QuizItem"})._id
            drawer = node_collection.find({'_type': u"GSystem", '_id': {'$nin': filtering}, 'member_of': {
                                          '$in': [gst_quiz_id, gst_quiz_item_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "OnlyQuiz":
            gst_quiz_id = node_collection.one(
                {'_type': "GSystemType", 'name': "Quiz"})._id
            drawer = node_collection.find({'_type': u"GSystem", '_id': {'$nin': filtering}, 'member_of': {
                                          '$all': [gst_quiz_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "QuizItem":
            gst_quiz_item_id = node_collection.one(
                {'_type': "GSystemType", 'name': "QuizItem"})._id
            drawer = node_collection.find({'_type': u"GSystem", '_id': {'$nin': filtering}, 'member_of': {
                                          '$all': [gst_quiz_item_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "Group":
            drawer = node_collection.find(
                {'_type': u"Group", '_id': {'$nin': filtering}})

        elif checked == "Users":
            drawer = node_collection.find(
                {'_type': u"Author", '_id': {'$nin': filtering}})

        elif checked == "Forum":
            gst_forum_id = node_collection.one(
                {'_type': "GSystemType", 'name': "Forum"})._id
            drawer = node_collection.find({'_type': u"GSystem", '_id': {'$nin': filtering}, 'member_of': {
                                          '$all': [gst_forum_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "Module":
            gst_module_id = node_collection.one(
                {'_type': "GSystemType", 'name': "Module"})._id
            drawer = node_collection.find({'_type': u"GSystem", '_id': {'$nin': filtering}, 'member_of': {
                                          '$all': [gst_module_id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "Pandora Video":
            gst_pandora_video_id = node_collection.one(
                {'_type': "GSystemType", 'name': "Pandora_video"})._id
            drawer = node_collection.find({'_type': u"File", '_id': {'$nin': filtering}, 'member_of': {
                                          '$all': [gst_pandora_video_id]}, 'group_set': {'$all': [ObjectId(group_id)]}}).limit(50)

        elif checked == "Theme":
            drawer = node_collection.find({'_type': u"GSystem", '_id': {'$nin': filtering}, 'member_of': {
                                          '$in': [theme_GST._id, topic_GST._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "theme_item":
            drawer = node_collection.find({'_type': u"GSystem", '_id': {'$nin': filtering}, 'member_of': {
                                          '$in': [theme_item_GST._id, topic_GST._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "Topic":
            drawer = node_collection.find({'_type': {'$in': [u"GSystem", u"File"]}, '_id': {'$nin': filtering}, 'member_of': {
                                          '$nin': [theme_GST._id, theme_item_GST._id, topic_GST._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})

        elif checked == "RelationType" or checked == "CourseUnits":
            # Special case used while dealing with RelationType widget
            if kwargs.has_key("left_drawer_content"):
                drawer = kwargs["left_drawer_content"]
    else:
        # For heterogeneous collection
        if checked == "RelationType" or checked == "CourseUnits":
            # Special case used while dealing with RelationType widget
            drawer = checked

        else:
            filtering = filter_drawer_nodes(nid, group_id)
            Page = node_collection.one(
                {'_type': 'GSystemType', 'name': 'Page'})
            File = node_collection.one(
                {'_type': 'GSystemType', 'name': 'File'})
            Quiz = node_collection.one(
                {'_type': "GSystemType", 'name': "Quiz"})
            drawer = node_collection.find({'_type': {'$in': [u"GSystem", u"File"]},
                                           '_id': {'$nin': filtering}, 'group_set': {'$all': [ObjectId(group_id)]},
                                           'member_of': {'$in': [Page._id, File._id, Quiz._id]}
                                           })
    if checked != "RelationType" and checked != "CourseUnits":
        paged_resources = paginator.Paginator(drawer, page_no, 10)
        drawer.rewind()

    if (nid is None) and (not nlist):
        for each in drawer:
            dict_drawer[each._id] = each

    elif (nid is None) and (nlist):

        for each in drawer:
            if each._id not in nlist:
                dict1[each._id] = each

        dict2 = [node_collection.one({'_id': oid}) for oid in nlist]

        for oid in nlist:
            obj = node_collection.one({'_id': oid})
            dict2.append(obj)
        dict_drawer['1'] = dict1
        dict_drawer['2'] = list(set(dict2))

    else:
        for each in drawer:
            if each._id != nid:
                if each._id not in nlist:
                    dict1[each._id] = each

        dict2 = [node_collection.one({'_id': oid})  for oid in nlist]

        for oid in nlist:
            obj = node_collection.one({'_id': oid})
            dict2.append(obj)
        dict_drawer['1'] = dict1
        dict_drawer['2'] = list(set(dict2))

    if checked == "RelationType" or checked == "CourseUnits":
        return dict_drawer

    else:
        return dict_drawer, paged_resources


# get type of resourc
@get_execution_time
def get_resource_type(request, node_id):
    get_resource_type = node_collection.one({'_id': ObjectId(node_id)})
    get_type = get_resource_type._type
    return get_type


@get_execution_time
def get_translate_common_fields(request, get_type, node, group_id, node_type, node_id):
  """ retrive & update the common fields required for translation of the node """

  usrid = int(request.user.id)
  content_org = request.POST.get('content_org')
  tags = request.POST.get('tags')
  name = request.POST.get('name')
  tags = request.POST.get('tags')
  access_policy = request.POST.get('access_policy')
  usrid = int(request.user.id)
  language= request.POST.get('lan')
  if get_type == "File":
    get_parent_node = node_collection.one({'_id': ObjectId(node_id)})
    get_mime_type=get_parent_node.mime_type
    get_fs_file_ids=get_parent_node.fs_file_ids
    node.mime_type=get_mime_type
    node.fs_file_ids=get_fs_file_ids

  if not ('_id' in node):
    node.created_by = usrid
    if get_type == "File":
        get_node_type = node_collection.one({"_type": "GSystemType", 'name': get_type})
        node.member_of.append(get_node_type._id)
        if 'image' in get_mime_type:
          get_image_type = node_collection.one({"_type": "GSystemType", 'name': 'Image'})
          node.member_of.append(get_image_type._id)
        if 'video' in get_mime_type:
          get_video_type = node_collection.one({"_type": "GSystemType", 'name': 'Video'})
          node.member_of.append(get_video_type._id)

    else:
      node.member_of.append(node_type._id)

  node.name = unicode(name)
  node.language = get_language_tuple(language)

  node.modified_by = usrid
  if access_policy:
    node.access_policy = access_policy

  if usrid not in node.contributors:
    node.contributors.append(usrid)

  group_obj = node_collection.one({'_id': ObjectId(group_id)})
  if group_obj._id not in node.group_set:
    node.group_set.append(group_obj._id)
  if tags:
    node.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]

  if tags:
    node.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]

  if content_org:
    node.content_org = unicode(content_org)
    node.name=unicode(name)
    # Required to link temporary files with the current user who is modifying this document
    usrname = request.user.username
    # filename = slugify(name) + "-" + usrname + "-" + ObjectId().__str__()
    # node.content = org2html(content_org, file_prefix=filename)
    node.content = unicode(content_org)

@get_execution_time
def get_node_common_fields(request, node, group_id, node_type, coll_set=None):
    """Updates the retrieved values of common fields from request
    into the given node.
    """

    group_obj = node_collection.one({'_id': ObjectId(group_id)})
    # theme_item_GST = node_collection.one({'_type': 'GSystemType', 'name': 'theme_item'})
    # topic_GST = node_collection.one({'_type': 'GSystemType', 'name': 'Topic'})
    # collection = None

    if coll_set:
        if "Theme" in coll_set.member_of_names_list:
            node_type = theme_GST
        if "theme_item" in coll_set.member_of_names_list:
            node_type = theme_item_GST
        if "Topic" in coll_set.member_of_names_list:
            node_type = topic_GST

        name = request.POST.get('name_' + str(coll_set._id), "")
        content_org = request.POST.get(str(coll_set._id), "")
        tags = request.POST.get('tags' + str(coll_set._id), "")

    else:
        name = request.POST.get('name', '').strip()
        content_org = request.POST.get('content_org')
        # print "\n\n\n content_org",content_org
        tags = request.POST.get('tags',[])
        if tags:
            tags = json.loads(tags)

    language = request.POST.get('lan')
    copyright = request.POST.get('copyright')
    sub_theme_name = request.POST.get("sub_theme_name", '')
    add_topic_name = request.POST.get("add_topic_name", '')
    is_changed = False
    sub_theme_name = unicode(request.POST.get("sub_theme_name", ''))
    add_topic_name = unicode(request.POST.get("add_topic_name", ''))
    usrid = int(request.user.id)
    usrname = unicode(request.user.username)
    access_policy = request.POST.get("login-mode", '')
    right_drawer_list = []
    checked = request.POST.get("checked", '')
    check_collection = request.POST.get("check_collection", '')
    if check_collection:
        if check_collection == "collection":
            right_drawer_list = request.POST.get('collection_list', '')
        elif check_collection == "prior_node":
            right_drawer_list = request.POST.get('prior_node_list', '')
        elif check_collection == "teaches":
            right_drawer_list = request.POST.get('teaches_list', '')
        elif check_collection == "assesses":
            right_drawer_list = request.POST.get('assesses_list', '')
        elif check_collection == "module":
            right_drawer_list = request.POST.get('module_list', '')

    map_geojson_data = request.POST.get('map-geojson-data')
    user_last_visited_location = request.POST.get('last_visited_location')
    altnames = request.POST.get('altnames', '')
    # featured = request.POST.get('featured', '')

    if map_geojson_data:
        map_geojson_data = map_geojson_data + ","
        map_geojson_data = list(ast.literal_eval(map_geojson_data))
    else:
        map_geojson_data = []

    # For create only ---------------------------------------------------------
    if not ("_id" in node):
        node.created_by = usrid

        if node_type._id not in node.member_of:
            node.member_of.append(node_type._id)
            if node_type.name == "Term":
                node.member_of.append(topic_GST._id)

        if group_obj._id not in node.group_set:
            node.group_set.append(group_obj._id)

        if access_policy == "PUBLIC":
            node.access_policy = unicode(access_policy)
        else:
            node.access_policy = unicode(access_policy)

        node.status = "PUBLISHED"
        is_changed = True

        # End of if
        specific_url = set_all_urls(node.member_of)
        node.url = specific_url

    if name:
        if node.name != name:
            node.name = name
            is_changed = True

    if altnames or "altnames" in request.POST:
        if node.altnames != altnames:
            node.altnames = altnames
            is_changed = True

    # if featured or (not featured):
    #     if node.featured != featured:
    #         node.featured = featured
    #         is_changed = True

    if sub_theme_name:
        if node.name != sub_theme_name:
            node.name = sub_theme_name
            is_changed = True

    if add_topic_name:
        if node.name != add_topic_name:
            node.name = add_topic_name
            is_changed = True

    #  language
    if language:
        node.language = get_language_tuple(language)
        # print "=========node.language-==========\n", node.language
        is_changed = True
    else:
        node.language = get_language_tuple(u"en")
        # node.language = ("en","English")
        is_changed = True

    #  access_policy
    if access_policy:
        # Policy will be changed only by the creator of the resource
        # via access_policy(public/private) option on the template which
        # is visible only to the creator
        if access_policy == "PUBLIC" and node.access_policy != access_policy:
            node.access_policy = u"PUBLIC"
            # print "\n Changed: access_policy (pu 2 pr)"
            is_changed = True
        elif access_policy == "PRIVATE" and node.access_policy != access_policy:
            node.access_policy = u"PRIVATE"
            # print "\n Changed: access_policy (pr 2 pu)"
            is_changed = True
    else:
        node.access_policy = u"PUBLIC"

    # For displaying nodes in home group as well as in creator group.
    user_group_obj = node_collection.one({
        '_type': ObjectId(group_id), 'name': usrname
    })

    if group_obj._id not in node.group_set:
        node.group_set.append(group_obj._id)
    else:
        if user_group_obj:
            if user_group_obj._id not in node.group_set:
                node.group_set.append(user_group_obj._id)

    # tags
    # if tags:

    # tags_list = []
    if tags != node.tags:
        # for tag in tags.split(","):
        #     tag = unicode(tag.strip())

        #     if tag:
        #         tags_list.append(tag)

        # if set(node.tags) != set(tags_list):
            # node.tags = tags_list
        if set(node.tags) != tags:
            node.tags = tags
            is_changed = True

    #  Build collection, prior node, teaches and assesses lists
    if check_collection:
        changed = build_collection(
            node, check_collection, right_drawer_list, checked)
        if changed:
            is_changed = True
    #  org-content
    # type_of_val = request.POST.get('type_of','')
    type_of_val = request.POST.getlist("type_of",'')

    wiki_page_gst = node_collection.one({'_type':'GSystemType', 'name': "Wiki page"},{'_id':1})

    '''
    Exceptional case for "Wiki pages".
    As org-editor is used ONLY for Wiki pages
    and rest everywhere ckeditor is used
    '''
    if type_of_val:
        node.type_of = [ObjectId(type_of_val[0])]
        is_changed = True

    # if type_of_val == str(wiki_page_gst._id):
    #     if node.content_org != content_org:
    #         node.content_org = unicode(content_org)

    #         # Required to link temporary files with the current user who is
    #         # modifying this document
    #         usrname = request.user.username
    #         filename = slugify(name) + "-" + slugify(usrname) + "-" + ObjectId().__str__()
    #         node.content = unicode(org2html(content_org, file_prefix=filename))
    #         is_changed = True
    if node.content != content_org:
        node.content = unicode(content_org)
        is_changed = True

    '''
    if node.content_org != content_org:
        node.content_org = unicode(content_org)

        # Required to link temporary files with the current user who is
        # modifying this document
        usrname = request.user.username
        filename = slugify(name) + "-" + slugify(usrname) + "-" + ObjectId().__str__()

        node_page_type_list = []
        if node.get("_id",None):
            get_node = node_collection.one({'_id': ObjectId(node._id)})
            node_type_of = get_node.type_of
            if node_type_of:
              for each_node_type_of in node_type_of:
                node_type_of_name = node_collection.one({'_id': each_node_type_of})
                node_page_type_list.append(node_type_of_name.name)

        # org editor for wiki page and ckeditor for blog and info pages
        if node_page_type_list:
          if "Wiki page" in node_page_type_list:
            # node.content = unicode(org2html(content_org, file_prefix=filename))
            node.content = unicode(content_org)
            pass
          else:
            node.content = unicode(content_org)
        else:
          # node.content = unicode(org2html(content_org, file_prefix=filename))
            node.content = unicode(content_org)
        is_changed = True
    '''

    # visited_location in author class
    if node.location != map_geojson_data:
        node.location = map_geojson_data  # Storing location data
        is_changed = True

    if node.legal['copyright'] != copyright:
        node.legal['copyright'] = copyright
        is_changed = True

    if user_last_visited_location:
        user_last_visited_location = list(
            ast.literal_eval(user_last_visited_location))

        author = node_collection.one(
            {'_type': "GSystemType", 'name': "Author"})
        user_group_location = node_collection.one({
            '_type': "Author", 'member_of': author._id, 'created_by': usrid,
            'name': usrname
        })

        if user_group_location:
            if node._type == "Author" and user_group_location._id == node._id:
                if node['visited_location'] != user_last_visited_location:
                    node['visited_location'] = user_last_visited_location
                    is_changed = True

            else:
                user_group_location['visited_location'] = user_last_visited_location
                user_group_location.save(groupid=group_id)

    if is_changed:
        node.status = unicode("DRAFT")

        node.modified_by = usrid

        if usrid not in node.contributors:
            node.contributors.append(usrid)

    return is_changed
# ============= END of def get_node_common_fields() ==============


@get_execution_time
def build_collection(node, check_collection, right_drawer_list, checked):
  is_changed = False

  if check_collection == "prior_node":
    if right_drawer_list != '':
      # prior_node_list = [ObjectId(each.strip()) for each in prior_node_list.split(",")]
      right_drawer_list = [ObjectId(each.strip()) for each in right_drawer_list.split(",")]

      if node.prior_node != right_drawer_list:
        i = 0
        node.prior_node=[]
        node_prior_node_append_temp=node.prior_node.append #a temp. variable which stores the lookup for append method
        while (i < len(right_drawer_list)):
          node_id = ObjectId(right_drawer_list[i])
          node_obj = node_collection.one({"_id": node_id})
          if node_obj:
            node_prior_node_append_temp(node_id)

          i = i+1
        # print "\n Changed: prior_node"
        is_changed = True
    else:
      node.prior_node = []
      is_changed = True

  elif check_collection == "collection":
    #  collection
    if right_drawer_list != '':
      right_drawer_list = [ObjectId(each.strip()) for each in right_drawer_list.split(",")]

      nlist = node.collection_set

      # if set(node.collection_set) != set(right_drawer_list):
      if node.collection_set != right_drawer_list:
        i = 0
        node.collection_set = []
        # checking if each _id in collection_list is valid or not
        nlist_append_temp=nlist.append #a temp. variable which stores the lookup for append method
        node_collection_set_append_temp=node.collection_set.append #a temp. variable which stores the lookup for append method
        while (i < len(right_drawer_list)):
          node_id = ObjectId(right_drawer_list[i])
          node_obj = node_collection.one({"_id": node_id})
          if node_obj:
            if node_id not in nlist:
              nlist_append_temp(node_id)
            else:
              node_collection_set_append_temp(node_id)
              # After adding it to collection_set also make the 'node' as prior node for added collection element
              node_collection.collection.update({'_id': ObjectId(node_id), 'prior_node': {'$nin':[node._id]} },{'$push': {'prior_node': ObjectId(node._id)}})

          i = i+1

        for each in nlist:
          if each not in node.collection_set:
            node_collection_set_append_temp(each)
            node.status = u"PUBLISHED"
            node.save()
            # After adding it to collection_set also make the 'node' as prior node for added collection element
            node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {'$nin':[node._id]} },{'$push': {'prior_node': ObjectId(node._id)}})

        # For removing collection elements from heterogeneous collection drawer only
        if not checked:
          if nlist:
            for each in nlist:
              if each not in right_drawer_list and each in node.collection_set:
                node.collection_set.remove(each)
                # Also for removing prior node element after removing collection element
                node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {'$in':[node._id]} },{'$pull': {'prior_node': ObjectId(node._id)}})
    is_changed = False

  if check_collection == "prior_node":
      if right_drawer_list != '':
          # prior_node_list = [ObjectId(each.strip()) for each in prior_node_list.split(",")]
          right_drawer_list = [ObjectId(each.strip())
                               for each in right_drawer_list.split(",")]

          if node.prior_node != right_drawer_list:
              i = 0
              node.prior_node = []
              while (i < len(right_drawer_list)):
                  node_id = ObjectId(right_drawer_list[i])
                  node_obj = node_collection.one({"_id": node_id})
                  if node_obj:
                      node.prior_node.append(node_id)

                  i = i + 1
              # print "\n Changed: prior_node"
              is_changed = True
      else:
          node.prior_node = []
          is_changed = True

  elif check_collection == "collection":
      #  collection

      if right_drawer_list != '':
          if isinstance(right_drawer_list, list):
              right_drawer_list = [ObjectId(each)
                                   for each in right_drawer_list]
          else:
              right_drawer_list = [ObjectId(each.strip())
                                   for each in right_drawer_list.split(",")]

          nlist = node.collection_set

          # if set(node.collection_set) != set(right_drawer_list):
          if node.collection_set != right_drawer_list:
              i = 0
              node.collection_set = []
              # checking if each _id in collection_list is valid or not
              while (i < len(right_drawer_list)):
                  node_id = ObjectId(right_drawer_list[i])
                  node_obj = node_collection.one({"_id": node_id})
                  if node_obj:
                      if node_id not in nlist:
                          nlist.append(node_id)
                      else:
                          node.collection_set.append(node_id)
                          # After adding it to collection_set also make the
                          # 'node' as prior node for added collection element
                          node_collection.collection.update({'_id': ObjectId(node_id), 'prior_node': {
                                                            '$nin': [node._id]}}, {'$push': {'prior_node': ObjectId(node._id)}})

                  i = i + 1

              for each in nlist:
                  if each not in node.collection_set:
                      node.collection_set.append(each)
                      # After adding it to collection_set also make the
                      # 'node' as prior node for added collection element
                      node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {
                                                        '$nin': [node._id]}}, {'$push': {'prior_node': ObjectId(node._id)}})

              # For removing collection elements from heterogeneous
              # collection drawer only
              if not checked:
                  if nlist:
                      for each in nlist:
                          if each not in right_drawer_list:
                              node.collection_set.remove(each)
                              # Also for removing prior node element after
                              # removing collection element
                              node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {
                                                                '$in': [node._id]}}, {'$pull': {'prior_node': ObjectId(node._id)}})

              else:
                  if nlist and checked:
                      if checked == "QuizObj":
                          quiz = node_collection.one(
                              {'_type': 'GSystemType', 'name': "Quiz"})
                          quizitem = node_collection.one(
                              {'_type': 'GSystemType', 'name': "QuizItem"})
                          for each in nlist:
                              obj = node_collection.one(
                                  {'_id': ObjectId(each)})
                              if quiz._id in obj.member_of or quizitem._id in obj.member_of:
                                  if obj._id not in right_drawer_list:
                                      node.collection_set.remove(obj._id)
                                      # Also for removing prior node element
                                      # after removing collection element
                                      node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {
                                                                        '$in': [node._id]}}, {'$pull': {'prior_node': ObjectId(node._id)}})

                      elif checked == "Pandora Video":
                          check = node_collection.one(
                              {'_type': 'GSystemType', 'name': 'Pandora_video'})
                          for each in nlist:
                              obj = node_collection.one(
                                  {'_id': ObjectId(each)})
                              if check._id == obj.member_of[0]:
                                  if obj._id not in right_drawer_list:
                                      node.collection_set.remove(obj._id)
                                      node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {
                                                                        '$in': [node._id]}}, {'$pull': {'prior_node': ObjectId(node._id)}})
                      else:
                          check = node_collection.one(
                              {'_type': 'GSystemType', 'name': unicode(checked)})
                          for each in nlist:
                              obj = node_collection.one(
                                  {'_id': ObjectId(each)})
                              if len(obj.member_of) < 2:
                                  if check._id == obj.member_of[0]:
                                      if obj._id not in right_drawer_list:
                                          node.collection_set.remove(obj._id)
                                          node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {
                                                                            '$in': [node._id]}}, {'$pull': {'prior_node': ObjectId(node._id)}})
                              else:
                                  if check._id == obj.member_of[1]:
                                      if obj._id not in right_drawer_list:
                                          node.collection_set.remove(obj._id)
                                          node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {
                                                                            '$in': [node._id]}}, {'$pull': {'prior_node': ObjectId(node._id)}})

              is_changed = True

      else:
          if node.collection_set and checked:
              if checked == "QuizObj":
                  quiz = node_collection.one(
                      {'_type': 'GSystemType', 'name': "Quiz"})
                  quizitem = node_collection.one(
                      {'_type': 'GSystemType', 'name': "QuizItem"})
                  for each in node.collection_set:
                      obj = node_collection.one({'_id': ObjectId(each)})
                      if quiz._id in obj.member_of or quizitem._id in obj.member_of:
                          node.collection_set.remove(obj._id)
                          node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {
                                                            '$in': [node._id]}}, {'$pull': {'prior_node': ObjectId(node._id)}})
              elif checked == "Pandora Video":
                  check = node_collection.one(
                      {'_type': 'GSystemType', 'name': 'Pandora_video'})
                  for each in node.collection_set:
                      obj = node_collection.one({'_id': ObjectId(each)})
                      if check._id == obj.member_of[0]:
                          node.collection_set.remove(obj._id)
                          node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {
                                                            '$in': [node._id]}}, {'$pull': {'prior_node': ObjectId(node._id)}})
              else:
                  check = node_collection.one(
                      {'_type': 'GSystemType', 'name': unicode(checked)})
                  for each in node.collection_set:
                      obj = node_collection.one({'_id': ObjectId(each)})
                      if len(obj.member_of) < 2:
                          if check._id == obj.member_of[0]:
                              node.collection_set.remove(obj._id)
                              node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {
                                                                '$in': [node._id]}}, {'$pull': {'prior_node': ObjectId(node._id)}})
                      else:
                          if check._id == obj.member_of[1]:
                              node.collection_set.remove(obj._id)
                              node_collection.collection.update({'_id': ObjectId(each), 'prior_node': {
                                                                '$in': [node._id]}}, {'$pull': {'prior_node': ObjectId(node._id)}})

          else:
              node.collection_set = []

          is_changed = True

  elif check_collection == "teaches":
      # Teaches
      if right_drawer_list != '':

          right_drawer_list = [ObjectId(each.strip())
                               for each in right_drawer_list.split(",")]

          relationtype = node_collection.one(
              {"_type": "RelationType", "name": "teaches"})
          list_grelations = triple_collection.find(
              {"_type": "GRelation", "subject": node._id, "relation_type": relationtype._id})
          for relation in list_grelations:
              # nlist.append(ObjectId(relation.right_subject))
              relation.delete()

          if right_drawer_list:
              list_grelations.rewind()
              i = 0

              while (i < len(right_drawer_list)):
                  node_id = ObjectId(right_drawer_list[i])
                  node_obj = node_collection.one({"_id": node_id})
                  if node_obj:
                      create_grelation(node._id, relationtype, node_id)
                  i = i + 1

              # print "\n Changed: teaches_list"
              is_changed = True
      else:
          relationtype = node_collection.one(
              {"_type": "RelationType", "name": "teaches"})
          list_grelations = triple_collection.find(
              {"_type": "GRelation", "subject": node._id, "relation_type": relationtype._id})
          for relation in list_grelations:
              relation.delete()

          is_changed = True

  elif check_collection == "assesses":
      # Assesses
      if right_drawer_list != '':
          right_drawer_list = [ObjectId(each.strip())
                               for each in right_drawer_list.split(",")]

          relationtype = node_collection.one(
              {"_type": "RelationType", "name": "assesses"})
          list_grelations = triple_collection.find(
              {"_type": "GRelation", "subject": node._id, "relation_type": relationtype._id})
          for relation in list_grelations:
              relation.delete()

          if right_drawer_list:
              list_grelations.rewind()
              i = 0

              while (i < len(right_drawer_list)):
                  node_id = ObjectId(right_drawer_list[i])
                  node_obj = node_collection.one({"_id": node_id})
                  if node_obj:
                      create_grelation(node._id, relationtype, node_id)
                  i = i + 1

              # print "\n Changed: teaches_list"
              is_changed = True
      else:
          relationtype = node_collection.one(
              {"_type": "RelationType", "name": "assesses"})
          list_grelations = triple_collection.find(
              {"_type": "GRelation", "subject": node._id, "relation_type": relationtype._id})
          for relation in list_grelations:
              relation.delete()

          is_changed = True

  # elif check_collection == "module":
      #  Module
      # if right_drawer_list != '':
      #   right_drawer_list = [ObjectId(each.strip()) for each in right_drawer_list.split(",")]

      #   if set(node.collection_set) != set(right_drawer_list):
      #     i = 0
      #     while (i < len(right_drawer_list)):
      #       node_id = ObjectId(right_drawer_list[i])
      #       node_obj = node_collection.one({"_id": node_id})
      #       if node_obj:
      #         if node_id not in node.collection_set:
      #           node.collection_set.append(node_id)

      #       i = i+1
          # print "\n Changed: module_list"
          # is_changed = True
      # else:
          # node.module_set = []
          # is_changed = True
  if is_changed == True:
      return True
  else:
      return False


@get_execution_time
def get_versioned_page(node):
    rcs = RCS()
    fp = history_manager.get_file_path(node)
    cmd = 'rlog  %s' % \
        (fp)
    rev_no = ""
    proc1 = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE)
    for line in iter(proc1.stdout.readline, b''):
        if line.find('revision') != -1 and line.find('selected') == -1:
            rev_no = string.split(line, 'revision')
            rev_no = rev_no[1].strip('\t\n\r')
            rev_no = rev_no.split()[0]
        if line.find('status') != -1:
            up_ind = line.find('status')
            if line.find(('PUBLISHED'), up_ind) != -1:
                rev_no = rev_no.split()[0]
                node = history_manager.get_version_document(node, rev_no)
                proc1.kill()
                return (node, rev_no)
        if rev_no == '1.1':
            node = history_manager.get_version_document(node, '1.1')
            proc1.kill()
            return(node, '1.1')

@get_execution_time
def get_user_page(request, node):
    ''' function gives the last docment submited by the currently logged in user either it
        can be drafted or published
    '''

    rcs = RCS()
    fp = history_manager.get_file_path(node)
    cmd = 'rlog  %s' % \
        (fp)
    rev_no = ""
    proc1 = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE)
    for line in iter(proc1.stdout.readline, b''):

        if line.find('revision') != -1 and line.find('selected') == -1:

            rev_no = string.split(line, 'revision')
            rev_no = rev_no[1].strip('\t\n\r')
            rev_no = rev_no.strip(' ')
        if line.find('updated') != -1:
            up_ind = line.find('updated')
            if line.find(str(request.user), up_ind) != -1:
                rev_no = rev_no.strip(' ')
                node = history_manager.get_version_document(node, rev_no)
                proc1.kill()
                return (node, rev_no)
        if rev_no == '1.1':
            node = history_manager.get_version_document(node, '1.1')
            proc1.kill()
            return(node, '1.1')


@get_execution_time
def get_page(request, node):
    '''
    function to filter between the page to be displyed to user
    i.e which page to be shown to the user drafted or the published page
    if a user have some drafted content then he would be shown his own drafted contents
    and if he has published his contents then he would be shown the current published contents
    '''
    username = request.user
    node1, ver1 = get_versioned_page(node)
    node2, ver2 = get_user_page(request, node)

    if ver2 != '1.1':
        if node2 is not None:
            if node2.status == 'PUBLISHED':

                if float(ver2) > float(ver1):
                    return (node2, ver2)
                elif float(ver2) < float(ver1):
                    return (node1, ver1)
                elif float(ver2) == float(ver1):
                    return(node1, ver1)
            elif node2.status == 'DRAFT':
                   #========== conditions for Group===============#

                if node._type == "Group":

                    count = check_page_first_creation(request, node2)
                    if count == 1:
                        return (node1, ver1)
                    elif count == 2:
                        return (node2, ver2)

                return (node2, ver2)
        else:

            return(node1, ver1)

    else:

                # if node._type == "GSystem" and node1.status == "DRAFT":
                #     if node1.created_by ==request.user.id:
                #           return (node2,ver2)
                #      else:
                #      return (node2,ver2)
        return (node1, ver1)

@get_execution_time
def get_page(request,node):
  '''
  function to filter between the page to be displyed to user
  i.e which page to be shown to the user drafted or the published page
  if a user have some drafted content then he would be shown his own drafted contents
  and if he has published his contents then he would be shown the current published contents
  '''
  username =request.user
  node1,ver1=get_versioned_page(node)
  node2,ver2=get_user_page(request,node)

  if  ver2 != '1.1':
            if node2 is not None:
                if node2.status == 'PUBLISHED':

                        if float(ver2) > float(ver1):
                                return (node2,ver2)
                        elif float(ver2) < float(ver1):
                                return (node1,ver1)
                        elif float(ver2) == float(ver1):
                                return(node1,ver1)
                elif node2.status == 'DRAFT':
                       #========== conditions for Group===============#

                        if   node._type == "Group":

                            count=check_page_first_creation(request,node2)
                            if count == 1:
                                return (node1,ver1)
                            elif count == 2:
                                return (node2,ver2)

                        return (node2,ver2)
            else:

                        return(node1,ver1)

  else:
        # if node._type == "GSystem" and node1.status == "DRAFT":
        #     if node1.created_by ==request.user.id:
        #           return (node2,ver2)
        #      else:
        #          return (node2,ver2)
        return (node1,ver1)

@get_execution_time
def check_page_first_creation(request, node):
    ''' function to check wheather the editing is performed by the user very first time '''
    rcs = RCS()
    fp = history_manager.get_file_path(node)
    cmd = 'rlog  %s' % \
        (fp)
    rev_no = ""
    count = 0
    proc1 = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE)
    for line in iter(proc1.stdout.readline, b''):
        if line.find('updated') != -1 or line.find('created') != -1:
            if line.find(str(request.user)) != -1:
                count = count + 1
                if count == 2:
                    proc1.kill()
                    return (count)
    proc1.kill()
    if count == 1:
        return(count)


@get_execution_time
def tag_info(request, group_id, tagname=None):
    '''
    Function to get all the resources related to tag
    '''
    group_name, group_id = get_group_name_id(group_id)
    group_id = ObjectId(group_id)
    cur = None
    total = None
    total_length = None
    yesterdays_result = []
    week_ago_result = []
    search_result = []
    group_cur_list = []  # for AutheticatedUser
    today = date.today()
    yesterdays_search = {date.today() - timedelta(days=1)}
    week_ago_search = {date.today() - timedelta(days=7)}
    locale.setlocale(locale.LC_ALL, '')
    userid = request.user.id
    # collection = get_database()[Node.collection_name]
    tag_str = request.GET.get("search", "")
    tag_search = tag_str.lower()
    # if coming from search, set tagname value to search value
    if tag_search:
        tagname = tag_search

    if request.user.is_superuser:  # Superuser can see private an public files
        if tagname:
            cur = node_collection.find({'tags': {'$regex': tagname, '$options': "i"},
                                        'group_set':ObjectId(group_id)
                  })
            #loop replaced by a list comprehension
            search_result=[every for every in cur]

    # Autheticate user can see all public files
    elif request.user.is_authenticated():
        # group_cur = node_collection.find({'_type': 'Group',
        #                                   '$or': [
        #                                       {'created_by': userid},
        #                                       {'group_admin': userid},
        #                                       {'author_set': userid},
        #                                       {'group_type': u'PUBLIC'},
        #                                     ]
        #                                   })
        # for each in group_cur:
        #     group_cur_list.append(each._id)
        if tagname:  # and (group_id in group_cur_list):
            cur = node_collection.find({'tags': {'$regex': tagname, '$options': "i"},
                                        'group_set': ObjectId(group_id),
                                        '$or': [
                {'status': u'PUBLISHED'},
                                            {'created_by': userid},
                                          ]
                                      })
            #loop replaced by a list comprehension
            search_result=[every for every in cur]

    else:  # Unauthenticated user can see all public files.
        group_node = node_collection.one({'_id': ObjectId(group_id)})
        if group_node.group_type == u"PUBLIC":
            if tagname:
                cur = node_collection.find({'tags': {'$regex': tagname, '$options': "i"},
                                            'group_set': group_id,
                                            'status': u'PUBLISHED'
                                            }
                                     )
                #loop replaced by a list comprehension
                search_result=[every for every in cur]

    if search_result:
        total = len(search_result)
        total = locale.format("%d", total, grouping=True)
        if len(search_result) == 0:
            total_length = len(search_result)
    context_variable = {'group_id': group_id, 'groupid': group_id,
                        'search_result': search_result,
                        'tagname': tagname, 'total': total,
                        'total_length': total_length}
    return render_to_response(
        "ndf/tag_browser.html",
        context_variable,
        context_instance=RequestContext(request)
    )


# code for merging two text Documents
import difflib


@get_execution_time
def diff_string(original, revised):

        # build a list of sentences for each input string
    original_text = _split_with_maintain(original)
    new_text = _split_with_maintain(revised)
    a = original_text + new_text
    strings = '\n'.join(a)
    #f=(strings.replace("*", ">").replace("-","="))
    #f=(f.replace("> 1 >",">").replace("= 1 =","="))

    return strings


STANDARD_REGEX = '[.!?]'


def _split_with_maintain(value, treat_trailing_spaces_as_sentence=True, split_char_regex=STANDARD_REGEX):
    result = []
    check = value

    # compile regex
    rx = re.compile(split_char_regex)

    # traverse the string
    while len(check) > 0:
        found = rx.search(str(check))
        if found == None:
            result.append(check)
            break

        idx = found.start()
        result.append(str(check[:idx]))            # append the string
        # append the puncutation so changing ? to . doesn't invalidate the
        # whole sentence
        result.append(str(check[idx:idx + 1]))
        check = check[idx + 1:]

        # group the trailing spaces if requested
        if treat_trailing_spaces_as_sentence:
            space_idx = 0
            while True:
                if space_idx >= len(check):
                    break
                if check[space_idx] != " ":
                    break
                space_idx += 1

            if space_idx != 0:
                result.append(check[0:space_idx])

            check = check[space_idx:]

    return result

'''
@get_execution_time
def update_mobwrite_content_org(node_system):
          # on revert or merge of nodes,a content_org is synced to mobwrite object
          # input :
          #         node
    system = node_system
    filename = TextObj.safe_name(str(system._id))
    textobj = TextObj.objects.filter(filename=filename)
    content_org = system.content_org
    if textobj:
        textobj = TextObj.objects.get(filename=filename)
        textobj.text = content_org
        textobj.save()
    else:
        textobj = TextObj(filename=filename, text=content_org)
        textobj.save()
    return textobj
'''

@get_execution_time
def cast_to_data_type(value, data_type):
    # print "\n\n\ninitial value and datatype",value,data_type
    '''
    This method will cast first argument: "value" to second argument: "data_type" and returns catsed value.
    '''
    # print "\n\t\tin method: ", value, " == ", data_type

    if data_type != "list":
      value = value.strip()
    casted_value = value
    if data_type == "unicode":
        casted_value = unicode(value)

    elif data_type == "basestring":
        casted_value = unicode(value)

    elif (data_type == "int") and str(value):
        casted_value = int(value) if (str.isdigit(str(value))) else value

    elif (data_type == "float") and str(value):
        casted_value = float(value) if (str.isdigit(str(value))) else value

    elif (data_type == "long") and str(value):
        casted_value = long(value) if (str.isdigit(str(value))) else value

    # converting unicode to int and then to bool
    elif data_type == "bool" and str(value):
        if (str.isdigit(str(value))):
            casted_value = bool(int(value))
        elif unicode(value) in [u"True", u"False"]:
            if (unicode(value) == u"True"):
                casted_value = True
            elif (unicode(value) == u"False"):
                casted_value = False

    elif (data_type == "list") and (not isinstance(value, list)):
        # print "coming here",value
        value = value.replace("\n", "").split(",")

        # check for complex list type like: [int] or [unicode]
        if isinstance(data_type, list) and len(data_type) and isinstance(data_type[0], type):
            # print "before",value
            casted_value = [data_type[0](i.strip()) for i in value if i]
            # print "casted_value",casted_value
        else:  # otherwise normal list
            # print "before",value
            casted_value = [i.strip() for i in value if i]
            # print "casted_value",casted_value

    elif data_type == "datetime.datetime":
        # "value" should be in following example format
        # In [10]: datetime.strptime( "11/12/2014", "%d/%m/%Y")
        # Out[10]: datetime(2014, 12, 11, 0, 0)
        casted_value = datetime.strptime(value, "%d/%m/%Y")

    return casted_value


@get_execution_time
def get_node_metadata(request, node, **kwargs):
    '''
    Getting list of updated GSystems with kwargs arguments.
    Pass is_changed=True as last/third argument while calling this/get_node_metadata method.
    Example:
      updated_ga_nodes = get_node_metadata(request, node_obj, GST_FILE_OBJ, is_changed=True)

    '''
    attribute_type_list = ["age_range", "audience", "timerequired",
                           "interactivitytype", "basedonurl", "educationaluse",
                           "textcomplexity", "readinglevel", "educationalsubject",
                           "educationallevel", "curricular", "educationalalignment",
                           "adaptation_of", "other_contributors", "creator", "source"
                           ]

    if "is_changed" in kwargs:
        updated_ga_nodes = []

    if('_id' in node):

        for atname in attribute_type_list:

            field_value = request.POST.get(atname, "")
            # print atname,field_value

            at = node_collection.one(
                {"_type": "AttributeType", "name": atname})

            if at:
                # print "\n\nfirst field_value datatype",at.data_type
                if at.data_type == "list":
                  field_value = request.POST.getlist(atname, "")
                  # print "\n\nlist field value",field_value
                else:
                  field_value = request.POST.get(atname, "")
                  # print "\n\nnon list field value",field_value
                field_value = cast_to_data_type(field_value, at["data_type"])
                # print at["data_type"], "\n\nfield_value: ",field_value, ", type: ",type(field_value)
                if "is_changed" in kwargs:
                    # print "field value"
                    temp_res = create_gattribute(node._id, at, field_value, is_changed=True)
                    if temp_res["is_changed"]:  # if value is true
                        updated_ga_nodes.append(temp_res)

                else:

                    create_gattribute(node._id, at, unicode(field_value))

    if "is_changed" in kwargs:
        return updated_ga_nodes


@get_execution_time
def create_grelation_list(subject_id, relation_type_name, right_subject_id_list):
    # function to create grelations for new ones and delete old ones.
    relationtype = node_collection.one(
        {"_type": "RelationType", "name": unicode(relation_type_name)})
    # list_current_grelations = triple_collection.find({"_type":"GRelation","subject":subject_id,"relation_type":relationtype})
    # removes all existing relations given subject and relation type and then
    # creates again.
    triple_collection.collection.remove(
        {"_type": "GRelation", "subject": subject_id, "relation_type": relationtype._id})

    for relation_id in right_subject_id_list:
        create_grelation(
            ObjectId(subject_id), relationtype, ObjectId(relation_id))
        # gr_node = triple_collection.collection.GRelation()
        # gr_node.subject = ObjectId(subject_id)
        # gr_node.relation_type = relationtype
        # gr_node.right_subject = ObjectId(relation_id)
        # gr_node.status = u"PUBLISHED"
        # gr_node.save()

        for relation_id in right_subject_id_list:

            gr_node = collection.GRelation()
            gr_node.subject = ObjectId(subject_id)
            gr_node.relation_type = relationtype._id
            gr_node.right_subject = ObjectId(relation_id)
            gr_node.status = u"PUBLISHED"
            gr_node.save()
            # gr_node.save(triple_node=relationtype, triple_id=relationtype._id)


@get_execution_time
def get_widget_built_up_data(at_rt_objectid_or_attr_name_list, node, type_of_set=[]):
    """
    Returns data in list of dictionary format which is required for building html widget.
    This data is used by html_widget template-tag.
    """
    if not isinstance(at_rt_objectid_or_attr_name_list, list):
        at_rt_objectid_or_attr_name_list = [at_rt_objectid_or_attr_name_list]
    # a temp. variable which stores the lookup for append method
    type_of_set_append_temp = type_of_set.append
    if not type_of_set:
        node["property_order"] = []
        # a temp. variable which stores the lookup for append method
        node_property_order_append_temp = node["property_order"].append
        gst_nodes = node_collection.find({'_type': "GSystemType", '_id': {
                                         '$in': node["member_of"]}}, {'type_of': 1, 'property_order': 1})
        for gst in gst_nodes:
            for type_of in gst["type_of"]:
                if type_of not in type_of_set:
                    type_of_set_append_temp(type_of)

            for po in gst["property_order"]:
                if po not in node["property_order"]:
                    node_property_order_append_temp(po)

    BASE_FIELD_METADATA = {
        'name': {'name': "name", '_type': "BaseField", 'altnames': "Name", 'required': True},
        'content_org': {'name': "content_org", '_type': "BaseField", 'altnames': "Describe", 'required': False},
        # 'featured': {'name': "featured", '_type': "BaseField", 'altnames': "Featured"},
        'location': {'name': "location", '_type': "BaseField", 'altnames': "Location", 'required': False},
        'status': {'name': "status", '_type': "BaseField", 'altnames': "Status", 'required': False},
        'tags': {'name': "tags", '_type': "BaseField", 'altnames': "Tags", 'required': False}
    }

    widget_data_list = []
    # a temp. variable which stores the lookup for append method
    widget_data_list_append_temp = widget_data_list.append
    for at_rt_objectid_or_attr_name in at_rt_objectid_or_attr_name_list:
        # ObjectId.is_valid(at_rt_objectid_or_attr_name):
        if type(at_rt_objectid_or_attr_name) == ObjectId:
            # For attribute-field(s) and/or relation-field(s)

            field = node_collection.one({'_id': ObjectId(at_rt_objectid_or_attr_name)}, {
                                        '_type': 1, 'subject_type': 1, 'object_type': 1, 'name': 1, 'altnames': 1, 'inverse_name': 1})


            altnames = u""
            value = None
            data_type = None
            if field._type == RelationType or field._type == "RelationType":
                # For RelationTypes
                if set(node["member_of"]).issubset(field.subject_type):
                    # It means we are dealing with normal relation &
                    data_type = node.structure[field.name]
                    value = node[field.name]
                    if field.altnames:
                        if ";" in field.altnames:
                            altnames = field.altnames.split(";")[0]
                        else:
                            altnames = field.altnames
                elif set(node["member_of"]).issubset(field.object_type):
                    # It means we are dealing with inverse relation
                    data_type = node.structure[field.inverse_name]
                    value = node[field.inverse_name]
                    if field.altnames:
                        if ";" in field.altnames:
                            altnames = field.altnames.split(";")[1]

                else:
                    member_of_node = node_collection.one({'_id': node.member_of[0]})
                    if set(member_of_node["type_of"]).issubset(field.subject_type):
                        data_type = node.structure[field.name]
                        value = node[field.name]
                        if field.altnames:
                            if ";" in field.altnames:
                                altnames = field.altnames.split(";")[0]
                            else:
                                altnames = field.altnames
            else:
                # For AttributeTypes
                altnames = field.altnames
                data_type = node.structure[field.name]
                value = node[field.name]

            widget_data_list_append_temp({'_type': field._type,  # It's only use on details-view template; overridden in ndf_tags html_widget()
                              '_id': field._id,
                              'data_type': data_type,
                              'name': field.name, 'altnames': altnames,
                              'value': value
                              })


        else:
            # For node's base-field(s)
            # widget_data_list.append([node['member_of'], BASE_FIELD_METADATA[at_rt_objectid_or_attr_name], node[at_rt_objectid_or_attr_name]])
            widget_data_list_append_temp({'_type': BASE_FIELD_METADATA[at_rt_objectid_or_attr_name]['_type'],
                              'data_type': node.structure[at_rt_objectid_or_attr_name],
                              'name': at_rt_objectid_or_attr_name, 'altnames': BASE_FIELD_METADATA[at_rt_objectid_or_attr_name]['altnames'],
                              'value': node[at_rt_objectid_or_attr_name],
                              'required': BASE_FIELD_METADATA[at_rt_objectid_or_attr_name]['required']
                              })

    return widget_data_list

@get_execution_time
def get_property_order_with_value(node):
    new_property_order = []
    demo = None

    if '_id' in node:
        demo = node_collection.one({'_id': node._id})

    else:
        demo = eval("node_collection.collection" + "." + node['_type'])()
        demo["member_of"] = node["member_of"]

    if demo["_type"] not in ["MetaType", "GSystemType", "AttributeType", "RelationType"]:
        # If GSystems found, then only perform following statements

        demo["property_order"] = []
        type_of_set = []
        # temp. variables which stores the lookup for append method
        type_of_set_append_temp = type_of_set.append
        demo_prop_append_temp = demo["property_order"].append
        gst_nodes = node_collection.find({'_type': "GSystemType", '_id': {
                                         '$in': demo["member_of"]}}, {'type_of': 1, 'property_order': 1})
        for gst in gst_nodes:
            for type_of in gst["type_of"]:
                if type_of not in type_of_set:
                    type_of_set_append_temp(type_of)

            for po in gst["property_order"]:
                if po not in demo["property_order"]:
                    demo_prop_append_temp(po)

        demo.get_neighbourhood(node["member_of"])
        # a temp. variable which stores the lookup for append method
        new_property_order_append_temp = new_property_order.append
        for tab_name, list_field_id_or_name in demo['property_order']:
            list_field_set = get_widget_built_up_data(
                list_field_id_or_name, demo, type_of_set)
            new_property_order_append_temp([tab_name, list_field_set])

        demo["property_order"] = new_property_order

    else:
        # Otherwise (if GSystemType found) depending upon whether type_of
        # exists or not returns property_order.
        if not demo["property_order"] and demo.has_key("_id"):
            type_of_nodes = node_collection.find(
                {'_type': "GSystemType", '_id': {'$in': demo["type_of"]}}, {'property_order': 1})

            if type_of_nodes.count():
                demo["property_order"] = []
                for to in type_of_nodes:
                    for po in to["property_order"]:
                        demo["property_order"].append(po)

            node_collection.collection.update({'_id': demo._id}, {
                                              '$set': {'property_order': demo["property_order"]}}, upsert=False, multi=False)

    new_property_order = demo['property_order']

    if demo.has_key('_id'):
        node = node_collection.one({'_id': demo._id})

    else:
        node = eval("node_collection.collection" + "." + demo['_type'])()
        node["member_of"] = demo["member_of"]

    node['property_order'] = new_property_order

    return node['property_order']


@get_execution_time
def parse_template_data(field_data_type, field_value, **kwargs):
    """
    Parses the value fetched from request (GET/POST) object based on the data-type of the given field.

    Arguments:
    field_data_type -- data-type of the field
    field_value -- value of the field retrieved from GET/POST object

    Returns:
    Parsed value based on the data-type of the field
    """

    '''
  kwargs_keys_list = [
                    "date_format_string",     # date-format in string representation
                    "field_instance"          # dict-object reperesenting AT/RT node
                  ]
  '''
    DATA_TYPE_STR_CHOICES = [
        "unicode", "basestring",
        "int", "float", "long",
        "list", "dict",
        "datetime",
        "bool",
        "ObjectId"
    ]
    try:
        if type(field_data_type) == type:
            field_data_type = field_data_type.__name__

            if not field_value:
                if field_data_type == "dict":
                    return {}

                elif field_data_type == "list":
                    return []

                else:
                    return None

            if field_data_type == "unicode":
                field_value = unicode(field_value)

            elif field_data_type == "basestring":
                field_value = field_value

            elif field_data_type == "int":
                field_value = int(field_value)

            elif field_data_type == "float":
                field_value = float(field_value)

            elif field_data_type == "long":
                field_value = long(field_value)

            elif field_data_type == "list":
                if ("[" in field_value) and ("]" in field_value):
                    field_value = json.loads(field_value)

                else:
                    lr = field_value.replace(" ,", ",")
                    rr = lr.replace(", ", ",")
                    field_value = rr.split(",")

            elif field_data_type == "dict":
                field_value = "???"

            elif field_data_type == "datetime":
                field_value = datetime.strptime(
                    field_value, kwargs["date_format_string"])

            elif field_data_type == "bool":
                if field_value == "Yes" or field_value == "yes" or field_value == "1":
                    if field_value == "1":
                        field_value = bool(int(field_value))
                    else:
                        field_value = True

                elif field_value == "No" or field_value == "no" or field_value == "0":
                    if field_value == "0":
                        field_value = bool(int(field_value))
                    else:
                        field_value = False

            elif field_data_type == "ObjectId":
                field_value = ObjectId(field_value)

            else:
                error_message = "Unknown data-type (" + \
                    field_data_type + ") found"
                raise Exception(error_message)

        elif type(field_data_type) == list:

            if "field_instance" in kwargs:
                if kwargs["field_instance"]["_type"] == RelationType or kwargs["field_instance"]["_type"] == "RelationType":
                    # Write RT related code
                    if not field_value:
                        return None
                    if field_value:
                        field_value = ObjectId(field_value)

                    else:
                        error_message = "This ObjectId(" + \
                            field_type + ") doesn't exists"
                        raise Exception(error_message)

            else:
                if not field_value:
                    return []

                if ("[" in field_value) and ("]" in field_value):
                    field_value = json.loads(field_value)

                else:
                    lr = field_value.replace(" ,", ",")
                    rr = lr.replace(", ", ",")
                    field_value = rr.split(",")

                return field_value

        elif type(field_data_type) == dict:
            # Write code...
            if not field_value:
                return {}

        elif type(field_data_type) == mongokit.operators.IS:
            # Write code...
            if not field_value:
                return None

            field_value = unicode(field_value) if type(
                field_value) != unicode else field_value

        elif type(field_data_type) == mongokit.document.R:
            # Write code...
            if kwargs["field_instance"]["_type"] == AttributeType or kwargs["field_instance"]["_type"] == "AttributeType":
                # Write AT related code
                if not field_value:
                    if field_data_type == "dict":
                        return {}
                    elif field_data_type == "list":
                        return []

                    else:
                        return None

            else:
                error_message = "Neither AttributeType nor RelationType found"
                raise Exception(error_message)

        else:
            error_message = "Unknown data-type found"
            raise Exception(error_message)

        return field_value

    except Exception as e:
        error_message = "\n TemplateDataParsingError: " + str(e) + " !!!\n"
        raise Exception(error_message)



def validate_scope_values(rt_at_type_node, req_triple_scope):
    # check if req_scope_values keys are present
    # in rt_at_type_node scope list
    # req_triple_scope:
    #   {
    #     'relation_type_scope' : {'alt_format': 'mp4', 'alt_size': '720p', 'alt_language': 'hi'},
    #     'attribute_type_scope' : {'alt_format': 'mp4', 'alt_size': '720p', 'alt_language': 'hi'},
    #     'object_scope' : unicode,
    #     'subject_scope' : unicode
    #   }
    validated_scope_val = {}
    for each_scope_dict_key,each_scope_dict_val in req_triple_scope.items():
        # type(each_scope_dict_val): dict
        if each_scope_dict_key == "relation_type_scope":
            if isinstance(each_scope_dict_val, dict):
                for each_scope_alt_key, each_scope_alt_val in each_scope_dict_val.items():
                    if each_scope_alt_key in rt_at_type_node['relation_type_scope']:
                        if 'relation_type_scope' in validated_scope_val:
                            old_rt_scope_val = validated_scope_val['relation_type_scope']
                        else:
                            old_rt_scope_val = {}
                        old_rt_scope_val.update({each_scope_alt_key: each_scope_alt_val})
                        validated_scope_val.update({each_scope_dict_key: old_rt_scope_val})
        if each_scope_dict_key == "attribute_type_scope":
            if isinstance(each_scope_dict_val, dict):
                for each_scope_alt_key, each_scope_alt_val in each_scope_dict_val.items():
                    if each_scope_alt_key in rt_at_type_node['attribute_type_scope']:
                        if 'attribute_type_scope' in validated_scope_val:
                            old_at_scope_val = validated_scope_val['attribute_type_scope']
                        else:
                            old_at_scope_val = {}
                        old_at_scope_val.update({each_scope_alt_key: each_scope_alt_val})
                        validated_scope_val.update({each_scope_dict_key: old_at_scope_val})
        if each_scope_dict_key == "object_scope":
            if unicode(each_scope_dict_val.strip()) in rt_at_type_node['object_scope']:
                validated_scope_val.update({each_scope_dict_key: unicode(each_scope_dict_val)})
        if each_scope_dict_key == "subject_scope":
            if unicode(each_scope_dict_val.strip()) in rt_at_type_node['subject_scope']:
                validated_scope_val.update({each_scope_dict_key: unicode(each_scope_dict_val)})
    return validated_scope_val


def update_scope_of_triple(triple_node, rt_at_type_node, req_scope_values, is_grel=True):
    if req_scope_values:
        validated_scope_values = validate_scope_values(rt_at_type_node, req_scope_values)
        if 'object_scope' in validated_scope_values:
            triple_node.object_scope = validated_scope_values['object_scope']
        if 'subject_scope' in validated_scope_values:
            triple_node.subject_scope = validated_scope_values['subject_scope']
        if is_grel and 'relation_type_scope' in validated_scope_values:
            triple_node.relation_type_scope = validated_scope_values['relation_type_scope']
        elif 'attribute_type_scope' in validated_scope_values:
            triple_node.attribute_type_scope = validated_scope_values['attribute_type_scope']
        triple_node.save()
        # triple_node.save(triple_node=rt_at_type_node, triple_id=rt_at_type_node._id)
        return triple_node

@get_execution_time
def create_gattribute(subject_id, attribute_type_node, object_value=None, **kwargs):

    def _update_attr_set(attr_set_list_of_dicts, attr_key, attr_value):
        temp_attr_dict = get_dict_from_list_of_dicts(attr_set_list_of_dicts)
        temp_attr_dict.update({unicode(attr_key): attr_value})
        return [{k:v} for k, v in temp_attr_dict.iteritems()]

    ga_node = None
    info_message = ""
    old_object_value = None
    triple_scope_val = kwargs.get('triple_scope', None)
    try:
        attribute_type_node = Node.get_node_obj_from_id_or_obj(attribute_type_node, AttributeType)
    except Exception:
        attribute_type_node = Node.get_name_id_from_type(attribute_type_node, 'AttributeType', get_obj=True)
    # print "\nattribute_type_node: ", attribute_type_node.name
    ga_node = triple_collection.one(
        {'_type': "GAttribute", 'subject': subject_id, 'attribute_type': attribute_type_node._id})

    '''
    Example:
    triple_scope:
      {
        attribute_type_scope : {'alt_format': 'mp4', 'alt_size': '720p', 'alt_language': 'hi'},
        object_scope : unicode,
        subject_scope : unicode
      }

    '''

    if ga_node is None:
        # Code for creation
        try:
            ga_node = triple_collection.collection.GAttribute()

            ga_node.subject = subject_id
            ga_node.attribute_type = attribute_type_node._id

            if (not object_value) and type(object_value) != bool:
                # this is when value of attribute is cleared/empty
                # in this case attribute will be created with status deleted
                object_value = u"None"
                ga_node.status = u"DELETED"

            else:
                ga_node.status = u"PUBLISHED"

            ga_node.object_value = object_value
            # ga_node.save(triple_node=attribute_type_node, triple_id=attribute_type_node._id)
            ga_node.save()
            if triple_scope_val:
                ga_node = update_scope_of_triple(ga_node,attribute_type_node, triple_scope_val, is_grel=False)

            if ga_node.status == u"DELETED":
                info_message = " GAttribute (" + ga_node.name + \
                    ") created successfully with status as 'DELETED'!\n"

            else:
                info_message = " GAttribute (" + \
                    ga_node.name + ") created successfully.\n"

                # Fetch corresponding document & append into it's attribute_set
                node_collection.collection.update({'_id': subject_id},
                                                  {'$addToSet': {
                                                      'attribute_set': {attribute_type_node.name: object_value}}},
                                                  upsert=False, multi=False
                                                  )

            is_ga_node_changed = True

        except Exception as e:
            error_message = "\n GAttributeCreateError: " + str(e) + "\n"
            raise Exception(error_message)

    else:
        # Code for updating existing gattribute
        is_ga_node_changed = False
        try:
            if (not object_value) and type(object_value) != bool:
                # this is when value of attribute is cleared/empty
                # in this case attribute will be set with status deleted
                old_object_value = ga_node.object_value

                ga_node.status = u"DELETED"
                ga_node.save()
                # ga_node.save(triple_node=attribute_type_node, triple_id=attribute_type_node._id)
                if triple_scope_val:
                    ga_node = update_scope_of_triple(ga_node,attribute_type_node, triple_scope_val, is_grel=False)

                info_message = " GAttribute (" + ga_node.name + \
                    ") status updated from 'PUBLISHED' to 'DELETED' successfully.\n"

                # Fetch corresponding document & update it's attribute_set with
                # proper value
                node_collection.collection.update({'_id': subject_id, 'attribute_set.' + attribute_type_node.name: old_object_value}, {'$pull': {'attribute_set': {attribute_type_node.name: old_object_value}}}, upsert=False, multi=False)

            else:
                if type(ga_node.object_value) == list:
                    if type(ga_node.object_value[0]) == dict:
                        old_object_value = ga_node.object_value

                        if len(old_object_value) != len(object_value):
                            ga_node.object_value = object_value
                            is_ga_node_changed = True

                        else:
                            pairs = zip(old_object_value, object_value)
                            if any(x != y for x, y in pairs):
                                ga_node.object_value = object_value
                                is_ga_node_changed = True

                    elif type(ga_node.object_value[0]) == list:
                        if ga_node.object_value != object_value:
                            old_object_value = ga_node.object_value
                            ga_node.object_value = object_value
                            is_ga_node_changed = True

                    else:
                        if set(ga_node.object_value) != set(object_value):
                            old_object_value = ga_node.object_value
                            ga_node.object_value = object_value
                            is_ga_node_changed = True

                elif type(ga_node.object_value) == dict:
                    if cmp(ga_node.object_value, object_value) != 0:
                        old_object_value = ga_node.object_value
                        ga_node.object_value = object_value
                        is_ga_node_changed = True

                else:
                    if ga_node.object_value != object_value:
                        old_object_value = ga_node.object_value
                        ga_node.object_value = object_value
                        is_ga_node_changed = True

                if is_ga_node_changed or ga_node.status == u"DELETED":
                    if ga_node.status == u"DELETED":
                        ga_node.status = u"PUBLISHED"
                        ga_node.save()
                        # ga_node.save(triple_node=attribute_type_node, triple_id=attribute_type_node._id)
                        if triple_scope_val:
                            ga_node = update_scope_of_triple(ga_node,attribute_type_node, triple_scope_val, is_grel=False)


                        info_message = " GAttribute (" + ga_node.name + \
                            ") status updated from 'DELETED' to 'PUBLISHED' successfully.\n"

                        # Fetch corresponding document & append into it's
                        # attribute_set
                        # node_collection.collection.update({'_id': subject_id},
                        #                                   {'$addToSet': {
                        #                                       'attribute_set': {attribute_type_node.name: object_value}}},
                        #                                   upsert=False, multi=False)
                        subject_node_obj = node_collection.one({'_id': ObjectId(subject_id)})
                        subject_node_obj.attribute_set = _update_attr_set(
                                                            subject_node_obj.attribute_set,
                                                            attribute_type_node.name,
                                                            object_value
                                                        )
                        subject_node_obj.save()


                    else:
                        ga_node.status = u"PUBLISHED"
                        ga_node.save()
                        # ga_node.save(triple_node=attribute_type_node, triple_id=attribute_type_node._id)
                        if triple_scope_val:
                            ga_node = update_scope_of_triple(ga_node,attribute_type_node, triple_scope_val, is_grel=False)

                        info_message = " GAttribute (" + \
                            ga_node.name + ") updated successfully.\n"

                        # Fetch corresponding document & update it's
                        # attribute_set with proper value
                        # node_collection.collection.update({'_id': subject_id, 'attribute_set.' + attribute_type_node.name: {"$exists": True}},
                        #                               {'$set': {
                        #                                   'attribute_set.$.' + attribute_type_node.name: ga_node.object_value}},
                        #                               upsert=False, multi=False)
                        subject_node_obj = node_collection.one({'_id': ObjectId(subject_id)})
                        subject_node_obj.attribute_set = _update_attr_set(
                                                            subject_node_obj.attribute_set,
                                                            attribute_type_node.name,
                                                            ga_node.object_value
                                                        )
                        subject_node_obj.save()
                else:
                    info_message = " GAttribute (" + ga_node.name + \
                        ") already exists (Nothing updated) !\n"

        except Exception as e:
            error_message = "\n GAttributeUpdateError: " + str(e) + "\n"
            raise Exception(error_message)

    # print "\n\t is_ga_node_changed: ", is_ga_node_changed

    # cache_key = str(subject_id) + 'attribute_value' + str(attribute_type_node.name)
    # cache.set(cache_key, object_value, 60 * 60)

    if "is_changed" in kwargs:
        ga_dict = {}
        ga_dict["is_changed"] = is_ga_node_changed
        ga_dict["node"] = ga_node
        ga_dict["before_obj_value"] = old_object_value
        return ga_dict
    else:
        return ga_node


# @get_execution_time
def create_grelation(subject_id, relation_type_node, right_subject_id_or_list, **kwargs):
    """Creates single or multiple GRelation documents (instances) based on given
    RelationType's cardinality (one-to-one / one-to-many).

    Arguments:
    subject_id -- ObjectId of the subject-node
    relation_type_node -- Document of the RelationType node (Embedded document)
    right_subject_id_or_list --
      - When one to one relationship: Single ObjectId of the right_subject node
      - When one to many relationship: List of ObjectId(s) of the right_subject node(s)

    Returns:
    - When one to one relationship: Created/Updated/Existed document.
    - When one to many relationship: Created/Updated/Existed list of documents.

    kwargs -- can hold the scope value
    """
    gr_node = None
    multi_relations = False
    triple_scope_val = kwargs.get('triple_scope', None)
    language = get_language_tuple(kwargs.get('language', None))
    '''
    Example:
    triple_scope:
      {
        relation_type_scope : {'alt_format': 'mp4', 'alt_size': '720p', 'alt_language': 'hi'},
        object_scope : unicode,
        subject_scope : unicode
      }

    In next phase, validate the scope values by adding:
        GSTUDIO_FORMAT_SCOPE_VALUES
        GSTUDIO_SIZE_SCOPE_VALUES
        GSTUDIO_LANGUAGE_SCOPE_VALUES
        in settings.py
        - katkamrachana, 23-12-2016
    '''
    try:
        subject_id = ObjectId(subject_id)

        def _create_grelation_node(subject_id, relation_type_node, right_subject_id_or_list, relation_type_text, triple_scope_val=None):
            # Code for creating GRelation node
            gr_node = triple_collection.collection.GRelation()

            gr_node.subject = subject_id
            gr_node.relation_type = relation_type_node._id
            gr_node.right_subject = right_subject_id_or_list
            # gr_node.relation_type_scope = relation_type_scope
            gr_node.language = language
            gr_node.status = u"PUBLISHED"
            gr_node.save()
            # gr_node.save(triple_node=relation_type_node, triple_id=relation_type_node._id)

            gr_node_name = gr_node.name
            info_message = "%(relation_type_text)s: GRelation (%(gr_node_name)s) " % locals() \
                + "created successfully.\n"

            relation_type_node_name = relation_type_node.name
            relation_type_node_inverse_name = relation_type_node.inverse_name

            left_subject = node_collection.one({
                "_id": subject_id,
                "relation_set." + relation_type_node_name: {"$exists": True}
            })
            if triple_scope_val:
                gr_node = update_scope_of_triple(gr_node,relation_type_node, triple_scope_val, is_grel=True)

            if left_subject:
                                # Update value of grelation in existing as key-value pair value in
                                # given node's "relation_set" field
                node_collection.collection.update({
                    "_id": subject_id,
                    "relation_set." + relation_type_node_name: {'$exists': True}
                }, {
                    "$addToSet": {"relation_set.$." + relation_type_node_name: right_subject_id_or_list}
                },
                    upsert=False, multi=False
                )

            else:
                # Add grelation as new key-value pair value in given node's
                # relation_set field
                node_collection.collection.update({
                    "_id": subject_id
                }, {
                    "$addToSet": {"relation_set": {relation_type_node_name: [right_subject_id_or_list]}}
                },
                    upsert=False, multi=False
                )

            right_subject = node_collection.one({
                '_id': right_subject_id_or_list,
                "relation_set." + relation_type_node_inverse_name: {"$exists": True}
            }, {
                'relation_set': 1
            })

            if right_subject:
                # Update value of grelation in existing as key-value pair value in
                # given node's "relation_set" field
                node_collection.collection.update({
                    "_id": right_subject_id_or_list, "relation_set." + relation_type_node_inverse_name: {'$exists': True}
                }, {
                    "$addToSet": {"relation_set.$." + relation_type_node_inverse_name: subject_id}
                },
                    upsert=False, multi=False
                )

            else:
                # Add grelation as new key-value pair value in given node's
                # relation_set field
                node_collection.collection.update({
                    "_id": right_subject_id_or_list
                }, {
                    "$addToSet": {"relation_set": {relation_type_node_inverse_name: [subject_id]}}
                },
                    upsert=False, multi=False
                )

            return gr_node

        def _update_deleted_to_published(gr_node, relation_type_node, relation_type_text, triple_scope_val=None):
            gr_node.status = u"PUBLISHED"
            # gr_node.language = language
            gr_node.save()
            # gr_node.save(triple_node=relation_type_node, triple_id=relation_type_node._id)

            gr_node_name = gr_node.name
            relation_type_node_name = relation_type_node.name
            relation_type_node_inverse_name = relation_type_node.inverse_name

            subject_id = gr_node.subject
            right_subject = gr_node.right_subject

            info_message = " %(relation_type_text)s: GRelation (%(gr_node_name)s) " % locals() \
                + \
                "status updated from 'DELETED' to 'PUBLISHED' successfully.\n"

            node_collection.collection.update({
                "_id": subject_id, "relation_set." + relation_type_node_name: {'$exists': True}
            }, {
                "$addToSet": {"relation_set.$." + relation_type_node_name: right_subject}
            },
                upsert=False, multi=False
            )

            node_collection.collection.update({
                "_id": right_subject, "relation_set." + relation_type_node_inverse_name: {'$exists': True}
            }, {
                "$addToSet": {'relation_set.$.' + relation_type_node_inverse_name: subject_id}
            },
                upsert=False, multi=False
            )

            return gr_node


        if relation_type_node["object_cardinality"]:
            # If object_cardinality value exists and greater than 1 (or eaqual to 100)
            # Then it signifies it's a one to many type of relationship
            # assign multi_relations = True
            type_of_relationship = relation_type_node.member_of_names_list
            if relation_type_node["object_cardinality"] > 1:
                multi_relations = True

                if META_TYPE[3] in type_of_relationship:
                    # If Binary relationship found

                    # Check whether right_subject_id_or_list is list or not
                    # If not convert it to list
                    if not isinstance(right_subject_id_or_list, list):
                        right_subject_id_or_list = [right_subject_id_or_list]

                    # Check whether all values of a list are of ObjectId data-type or not
                    # If not convert them to ObjectId
                    for i, each in enumerate(right_subject_id_or_list):
                        right_subject_id_or_list[i] = ObjectId(each)

                else:
                    # Relationship Other than Binary one found; e.g, Triadic
                    if right_subject_id_or_list:
                        if not isinstance(right_subject_id_or_list[0], list):
                            right_subject_id_or_list = [
                                right_subject_id_or_list]

                        # right_subject_id_or_list: [[id, id, ...], [id, id,
                        # ...], ...]
                        for i, each_list in enumerate(right_subject_id_or_list):
                            # each_list: [id, id, ...]
                            for j, each in enumerate(each_list):
                                right_subject_id_or_list[i][j] = ObjectId(each)

            else:
                if META_TYPE[3] in type_of_relationship:
                    # If Binary relationship found
                    if isinstance(right_subject_id_or_list, list):
                        right_subject_id_or_list = ObjectId(
                            right_subject_id_or_list[0])

                    else:
                        right_subject_id_or_list = ObjectId(
                            right_subject_id_or_list)
                else:
                    # Relationship Other than Binary one found; e.g, Triadic
                    # right_subject_id_or_list: [[id, id, ...], [id, id, ...],
                    # ...]
                    if isinstance(right_subject_id_or_list, ObjectId):
                        right_subject_id_or_list = [right_subject_id_or_list]
                    if right_subject_id_or_list:
                        if isinstance(right_subject_id_or_list[0], list):
                            # Reduce it to [id, id, id, ...]
                            right_subject_id_or_list = right_subject_id_or_list[
                                0]

                        for i, each_id in enumerate(right_subject_id_or_list):
                            right_subject_id_or_list[i] = ObjectId(each_id)

        if multi_relations:
            # For dealing with multiple relations (one to many)

            # Iterate and find all relationships (including DELETED ones' also)
            nodes = triple_collection.find({
                '_type': "GRelation", 'subject': subject_id,
                'relation_type': relation_type_node._id
            })

            gr_node_list = []

            for n in nodes:
                if n.right_subject in right_subject_id_or_list:
                    if n.status != u"DELETED":
                        # If match found with existing one's, then only remove that ObjectId from the given list of ObjectIds
                        # Just to remove already existing entries (whose status
                        # is PUBLISHED)
                        right_subject_id_or_list.remove(n.right_subject)
                        gr_node_list.append(n)
                        # if triple_scope_val:
                        #     n = update_scope_of_triple(n, relation_type_node, triple_scope_val, is_grel=True)

                        node_collection.collection.update(
                            {'_id': subject_id, 'relation_set.' +
                                relation_type_node.name: {'$exists': True}},
                            {'$addToSet': {
                                'relation_set.$.' + relation_type_node.name: n.right_subject}},
                            upsert=False, multi=False
                        )

                        node_collection.collection.update(
                            {'_id': n.right_subject, 'relation_set.' +
                                relation_type_node.inverse_name: {'$exists': True}},
                            {'$addToSet': {
                                'relation_set.$.' + relation_type_node.inverse_name: subject_id}},
                            upsert=False, multi=False
                        )
                        n.reload()

                else:
                    # Case: When already existing entry doesn't exists in newly come list of right_subject(s)
                    # So change their status from PUBLISHED to DELETED
                    n.status = u"DELETED"
                    n.save()
                    # n.save(triple_node=relation_type_node, triple_id=relation_type_node._id)

                    info_message = " MultipleGRelation: GRelation (" + n.name + \
                        ") status updated from 'PUBLISHED' to 'DELETED' successfully.\n"

                    node_collection.collection.update({
                        '_id': subject_id, 'relation_set.' + relation_type_node.name: {'$exists': True}
                    }, {
                        '$pull': {'relation_set.$.' + relation_type_node.name: n.right_subject}
                    },
                        upsert=False, multi=False
                    )

                    res = node_collection.collection.update({
                        '_id': n.right_subject, 'relation_set.' + relation_type_node.inverse_name: {'$exists': True}
                    }, {
                        '$pull': {'relation_set.$.' + relation_type_node.inverse_name: subject_id}
                    },
                        upsert=False, multi=False
                    )

            if right_subject_id_or_list:
                # If still ObjectId list persists, it means either they are new ones'
                # or from deleted ones'
                # For deleted one's, find them and modify their status to PUBLISHED
                # For newer one's, create them as new document
                for nid in right_subject_id_or_list:
                    gr_node = triple_collection.one({
                        '_type': "GRelation", 'subject': subject_id,
                        'relation_type': relation_type_node._id, 'right_subject': nid
                    })

                    if gr_node is None:
                        # New one found so create it
                        # check for relation_type_scope variable in kwargs and pass
                        gr_node = _create_grelation_node(
                            subject_id, relation_type_node, nid, "MultipleGRelation", triple_scope_val)
                        gr_node_list.append(gr_node)

                    else:
                        # Deleted one found so change it's status back to
                        # Published
                        if gr_node.status == u'DELETED':
                            gr_node = _update_deleted_to_published(
                                gr_node, relation_type_node, "MultipleGRelation")
                            gr_node_list.append(gr_node)

                        else:
                            error_message = " MultipleGRelation: Corrupt value found - GRelation (" + \
                                gr_node.name + ")!!!\n"
                            # raise Exception(error_message)

            return gr_node_list

        else:
            # For dealing with single relation (one to one)
            gr_node = None

            relation_type_node_id = relation_type_node._id
            relation_type_node_name = relation_type_node.name
            relation_type_node_inverse_name = relation_type_node.inverse_name

            gr_node_cur = triple_collection.find({
                "_type": "GRelation", "subject": subject_id,
                "relation_type": relation_type_node_id
            })
            for node in gr_node_cur:
                node_name = node.name
                node_status = node.status
                node_right_subject = node.right_subject

                if node_right_subject == right_subject_id_or_list:
                    # If match found, it means it could be either DELETED one
                    # or PUBLISHED one

                    if node_status == u"DELETED":
                        # If deleted, change it's status back to Published from
                        # Deleted
                        node = _update_deleted_to_published(
                            node, relation_type_node, "SingleGRelation", triple_scope_val)

                    elif node_status == u"PUBLISHED":
                        if triple_scope_val:
                            node = update_scope_of_triple(node, relation_type_node, triple_scope_val, is_grel=True)

                        node_collection.collection.update({
                            "_id": subject_id, "relation_set." + relation_type_node_name: {'$exists': True}
                        }, {
                            "$addToSet": {"relation_set.$." + relation_type_node_name: node_right_subject}
                        },
                            upsert=False, multi=False
                        )

                        node_collection.collection.update({
                            "_id": node_right_subject, "relation_set." + relation_type_node_inverse_name: {'$exists': True}
                        }, {
                            "$addToSet": {"relation_set.$." + relation_type_node_inverse_name: subject_id}
                        },
                            upsert=False, multi=False
                        )
                        info_message = " SingleGRelation: GRelation (%(node_name)s) already exists !\n" % locals(
                        )

                    # Set gr_node value as matched value, so that no need to
                    # create new one
                    node.reload()
                    gr_node = node

                else:
                    # If match not found and if it's PUBLISHED one, modify it
                    # to DELETED
                    if node.status == u'PUBLISHED':
                        node.status = u"DELETED"
                        node.save()
                        # node.save(triple_node=relation_type_node, triple_id=relation_type_node._id)

                        node_collection.collection.update({
                            '_id': subject_id, 'relation_set.' + relation_type_node_name: {'$exists': True}
                        }, {
                            '$pull': {'relation_set.$.' + relation_type_node_name: node_right_subject}
                        },
                            upsert=False, multi=False
                        )

                        node_collection.collection.update({
                            '_id': node_right_subject, 'relation_set.' + relation_type_node_inverse_name: {'$exists': True}
                        }, {
                            '$pull': {'relation_set.$.' + relation_type_node_inverse_name: subject_id}
                        },
                            upsert=False, multi=False
                        )
                        info_message = " SingleGRelation: GRelation (%(node_name)s) status " % locals() \
                            + \
                            "updated from 'PUBLISHED' to 'DELETED' successfully.\n"

            if gr_node is None:
                # Code for creation
                gr_node = _create_grelation_node(
                    subject_id, relation_type_node, right_subject_id_or_list, "SingleGRelation", triple_scope_val)

            return gr_node

    except Exception as e:
        error_message = "\n GRelationError (line #" + \
            str(exc_info()[-1].tb_lineno) + "): " + str(e) + "\n"
        raise Exception(error_message)


###############################################      #####################
@get_execution_time
def set_all_urls(member_of):
    Gapp_obj = node_collection.one({"_type": "MetaType", "name": "GAPP"})
    factory_obj = node_collection.one(
        {"_type": "MetaType", "name": "factory_types"})

    url = ""
    gsType = member_of[0]
    gsType_obj = node_collection.one({"_id": ObjectId(gsType)})

    if Gapp_obj._id in gsType_obj.member_of:
        if gsType_obj.name == u"Quiz":
            url = u"quiz/details"
        else:
            url = gsType_obj.name.lower()
    elif factory_obj._id in gsType_obj.member_of:
        if gsType_obj.name == u"QuizItem":
            url = u"quiz/details"
        elif gsType_obj.name == u"Twist":
            url = u"forum/thread"
        else:
            url = gsType_obj.name.lower()
    else:
        url = u"None"
    return url
############################################### ##########################


@login_required
@get_execution_time
def create_discussion(request, group_id, node_id):
    '''
    Method to create discussion thread for File and Page.
    '''

    try:

        twist_st = node_collection.one(
            {'_type': 'GSystemType', 'name': 'Twist'})

        node = node_collection.one({'_id': ObjectId(node_id)})

        # group = node_collection.one({'_id':ObjectId(group_id)})

        thread = node_collection.one({"_type": "GSystem", "name": node.name, "member_of": ObjectId(
            twist_st._id), "prior_node": ObjectId(node_id)})

        if not thread:

            # retriving RelationType
            # relation_type = node_collection.one({ "_type": "RelationType", "name": u"has_thread", "inverse_name": u"thread_of" })

            # Creating thread with the name of node
            thread_obj = node_collection.collection.GSystem()

            thread_obj.name = unicode(node.name)
            thread_obj.status = u"PUBLISHED"

            thread_obj.created_by = int(request.user.id)
            thread_obj.modified_by = int(request.user.id)
            thread_obj.contributors.append(int(request.user.id))

            thread_obj.member_of.append(ObjectId(twist_st._id))
            thread_obj.prior_node.append(ObjectId(node_id))
            thread_obj.group_set.append(ObjectId(group_id))

            thread_obj.save()

            # creating GRelation
            # create_grelation(node_id, relation_type, twist_st)
            response_data = ["thread-created", str(thread_obj._id)]

            return HttpResponse(json.dumps(response_data))

        else:
            response_data = ["Thread-exist", str(thread._id)]
            return HttpResponse(json.dumps(response_data))

    except Exception as e:

        error_message = "\n DiscussionThreadCreateError: " + str(e) + "\n"
        raise Exception(error_message)
        # return HttpResponse("server-error")


# to add discussion replie
@get_execution_time
def discussion_reply(request, group_id, node_id):
    try:

        prior_node = request.POST.get("prior_node_id", "")
        content_org = request.POST.get(
            "reply_text_content", "")  # reply content

        # process and save node if it reply has content
        if content_org:

            user_id = int(request.user.id)
            user_name = unicode(request.user.username)

            # auth = node_collection.one({'_type': 'Author', 'name': user_name })
            reply_st = node_collection.one(
                {'_type': 'GSystemType', 'name': 'Reply'})

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
            reply_obj.content = unicode(content_org)
            # filename = slugify(
            #     unicode("Reply of:" + str(prior_node))) + "-" + user_name + "-"
            # reply_obj.content = org2html(content_org, file_prefix=filename)

            # saving the reply obj
            reply_obj.save()

            formated_time = reply_obj.created_at.strftime(
                "%B %d, %Y, %I:%M %p")

            # ["status_info", "reply_id", "prior_node", "html_content", "org_content", "user_id", "user_name", "created_at" ]
            reply = json.dumps(["reply_saved", str(reply_obj._id), str(reply_obj.prior_node[
                               0]), reply_obj.content, reply_obj.content_org, user_id, user_name, formated_time], cls=DjangoJSONEncoder)

            # ---------- mail/notification sending -------
            node = node_collection.one({"_id": ObjectId(node_id)})
            node_creator_user_obj = User.objects.get(id=node.created_by)
            node_creator_user_name = node_creator_user_obj.username

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
            notification.send(
                to_user_list, render_label, {"from_user": from_user})

            # ---------- END of mail/notification sending ---------

            return HttpResponse(reply)

        else:  # no reply content

            return HttpResponse(json.dumps(["no_content"]))

    except Exception as e:

        error_message = "\n DiscussionReplyCreateError: " + str(e) + "\n"
        raise Exception(error_message)

        return HttpResponse(json.dumps(["Server Error"]))


@get_execution_time
def discussion_delete_reply(request, group_id):

    nodes_to_delete = json.loads(request.POST.get("nodes_to_delete", "[]"))

    reply_st = node_collection.one({'_type': 'GSystemType', 'name': 'Reply'})

    deleted_replies = []

    for each_reply in nodes_to_delete:
        temp_reply = node_collection.one({"_id": ObjectId(each_reply)})

        if temp_reply:
            deleted_replies.append(temp_reply._id.__str__())
            temp_reply.delete()
    return HttpResponse(json.dumps(deleted_replies))

@get_execution_time
def get_user_group(userObject):
    '''
    methods for getting user's belongs to group.
    input (userObject) is user object
    output list of dict, dict contain groupname, access, group_type, created_at and created_by
    '''
    blank_list = []
    cur_groups_user = node_collection.find({'_type': "Group",
                                            '$or': [
                                                {'created_by': userObject.id},
                                                {'group_admin': userObject.id},
                                                {'author_set': userObject.id},
                                            ]
                                            }).sort('last_update', -1)
    for eachgroup in cur_groups_user:
        access = ""
        if eachgroup.created_by == userObject.id:
            access = "owner"
        elif userObject.id in eachgroup.group_admin:
            access = "admin"
        elif userObject.id in eachgroup.author_set:
            access = "member"
        else:
            access = "member"
        user = User.objects.get(id=eachgroup.created_by)
        blank_list.append({'id': str(eachgroup._id), 'name': eachgroup.name, 'access': access,
                           'group_type': eachgroup.group_type, 'created_at': eachgroup.created_at, 'created_by': user.username})
    return blank_list


@get_execution_time
def get_user_task(userObject):
    '''
    methods for getting user's assigned task.
    input (userObject) is user object
    output list of dict, dict contain taskname, status, due_time, created_at and created_by, group_name
    '''
    blank_list = []
    attributetype_assignee = node_collection.find_one(
        {"_type": 'AttributeType', 'name': 'Assignee'})
    attributetype_status = node_collection.find_one(
        {"_type": 'AttributeType', 'name': 'Status'})
    attributetype_end_time = node_collection.find_one(
        {"_type": 'AttributeType', 'name': 'end_time'})
    attr_assignee = triple_collection.find(
        {"_type": "GAttribute", "attribute_type": attributetype_assignee._id, "object_value": userObject.username})
    for attr in attr_assignee:
        blankdict = {}
        task_node = node_collection.find_one({'_id': attr.subject})
        attr_status = triple_collection.find_one(
            {"_type": "GAttribute", "attribute_type": attributetype_status._id, "subject": task_node._id})
        attr_end_time = triple_collection.find_one(
            {"_type": "GAttribute", "attribute_type": attributetype_end_time._id, "subject": task_node._id})
        if attr_status.object_value is not "closed":
            group = node_collection.find_one({"_id": task_node.group_set[0]})
            user = User.objects.get(id=task_node.created_by)
            blankdict.update({'name': task_node.name, 'created_at': task_node.created_at,
                              'created_by': user.username, 'group_name': group.name, 'id': str(task_node._id)})
            if attr_status:
                blankdict.update({'status': attr_status.object_value})
            if attr_end_time:
                blankdict.update({'due_time': attr_end_time.object_value})
            blank_list.append(blankdict)
    return blank_list


@get_execution_time
def get_user_notification(userObject):
    '''
    methods for getting user's notification.
    input (userObject) is user object
    output list of dict, dict contain notice label, notice display
    '''
    blank_list = []
    notification_object = notification.NoticeSetting.objects.filter(
        user_id=userObject.id)
    for each in notification_object.reverse():
        ntid = each.notice_type_id
        ntype = notification.NoticeType.objects.get(id=ntid)
        label = ntype.label.split("-")[0]
        blank_list.append({'label': label, 'display': ntype.display})
    blank_list.reverse()
    return blank_list


@get_execution_time
def get_user_activity(userObject):
    '''
    methods for getting user's activity.
    input (userObject) is user object
    output list of dict, dict
    '''
    blank_list = []
    activity = ""
    activity_user = node_collection.find({'$and': [{'$or': [{'_type': 'GSystem'}, {'_type': 'Group'}, {'_type': 'File'}]},
                                                   {'$or': [{'created_by': userObject.id}, {'modified_by': userObject.id}]}]}).sort('last_update', -1).limit(10)
    for each in activity_user:
        if each.created_by == each.modified_by:
            if each.last_update == each.created_at:
                activity = 'created'
            else:
                activity = 'modified'
        else:
            activity = 'created'
        if each._type == 'Group':
            blank_list.append({'id': str(each._id), 'name': each.name, 'date':
                               each.last_update, 'activity': activity, 'type': each._type})
        else:
            member_of = node_collection.find_one({"_id": each.member_of[0]})
            blank_list.append({'id': str(each._id), 'name': each.name, 'date': each.last_update, 'activity':
                               activity, 'type': each._type, 'group_id': str(each.group_set[0]), 'member_of': member_of.name.lower()})
    return blank_list


@get_execution_time
def get_file_node(file_name=""):
    # if cached result exists return it
    cache_key = u'get_file_node' + slugify(unicode(file_name))
    cache_result = cache.get(cache_key)

    if cache_result:
        return cache_result
    # ---------------------------------

    file_list = []
    new = []
    a = str(file_name).split(',')
    for i in a:
        k = str(i.strip('   [](\'u\'   '))
        new.append(k)
        ins_objectid = ObjectId()
    for i in new:
        if ins_objectid.is_valid(i) is False:
            filedoc = node_collection.find(
                {'_type': 'File', 'name': unicode(i)})
        else:
            filedoc = node_collection.find(
                {'_type': 'File', '_id': ObjectId(i)})
        if filedoc:
            for i in filedoc:
                file_list.append(i.name)
    cache.set(cache_key, file_list, 60 * 15)
    return file_list


@get_execution_time
def create_task(task_dict, task_type_creation="single"):
    """Creates task with required attribute(s) and relation(s).

    task_dict
    - Required keys: _id[optional], name, group_set, created_by, modified_by, contributors, content_org,
        created_by_name, Status, Priority, start_time, end_time, Assignee, has_type

    task_type_creation
    - Valid input values: "single", "multiple", "group"
    """
    # Fetch Task GSystemType document
    task_gst = node_collection.one(
        {'_type': "GSystemType", 'name': "Task"}
    )

    # List of keys of "task_dict" dictionary
    task_dict_keys = task_dict.keys()

    if "_id" in task_dict:
        task_node = node_collection.one({'_id': task_dict["_id"]})
        task_dict["name"] = task_node.name
    else:
        task_node = node_collection.find_one({"member_of": task_gst._id, "name": task_dict[
                                             "name"], "attribute_set.Status": {"$nin": ["Closed"]}})

        if task_node is None:
            task_node = node_collection.collection.GSystem()
            task_node["member_of"] = [task_gst._id]

    # Store built in variables of task node
    # Iterate task_node using it's keys
    for key in task_node:
        if key in ["Status", "Priority", "start_time", "end_time", "Assignee", "has_type"]:
            # Required because these values might come as key in node's
            # document
            continue

        if key in task_dict_keys:
            if key == "content_org":
                #  org-content
                task_node[key] = task_dict[key]

                # Required to link temporary files with the current user who is
                # modifying this document
                filename = slugify(
                    task_dict["name"]) + "-" + task_dict["created_by_name"] + "-" + ObjectId().__str__()
                task_dict_keys.remove("created_by_name")
                # task_node.content = org2html(task_dict[key], file_prefix=filename)
                task_node.content = unicode(task_dict[key])

            else:
                task_node[key] = task_dict[key]

            task_dict_keys.remove(key)

    # Save task_node with built-in variables as required for creating
    # GAttribute(s)/GRelation(s)
    task_node.status = u"PUBLISHED"
    task_node.save()

    # Create GAttribute(s)/GRelation(s)
    for attr_or_rel_name in task_dict_keys:
        attr_or_rel_node = node_collection.one(
            {'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': unicode(
                attr_or_rel_name)}
        )

        if attr_or_rel_node:
            if attr_or_rel_node._type == "AttributeType":
                ga_node = create_gattribute(
                    task_node._id, attr_or_rel_node, task_dict[attr_or_rel_name])

            elif attr_or_rel_node._type == "RelationType":
                gr_node = create_grelation(
                    task_node._id, attr_or_rel_node, task_dict[attr_or_rel_name])

            task_node.reload()

        else:
            raise Exception(
                "\n No AttributeType/RelationType exists with given name(" + attr_or_rel_name + ") !!!")

    # If given task is a group task (create a task for each Assignee from the list)
    # Iterate Assignee list & create separate tasks for each Assignee
    # with same set of attribute(s)/relation(s)
    if task_type_creation == "group":
        mutiple_assignee = task_dict["Assignee"]
        collection_set = []
        for each in mutiple_assignee:
            task_dict["Assignee"] = [each]
            task_sub_node = create_task(task_dict)
            collection_set.append(task_sub_node._id)

        node_collection.collection.update({'_id': task_node._id}, {
                                          '$set': {'collection_set': collection_set}}, upsert=False, multi=False)

    else:
        # Send notification for each each Assignee of the task
        # Only be done in case when task_type_creation is not group,
        # i.e. either single or multiple
        if not task_dict.has_key("_id"):
          site = Site.objects.get(pk=1)
          # site = site.name.__str__()
          site = site.domain.__str__()

          from_user = task_node.user_details_dict["created_by"]  # creator of task

          group_name = node_collection.one(
              {'_type': {'$in': ["Group", "Author"]}, '_id': task_node.group_set[0]},
              {'name': 1}
          ).name

          url_link = "http://" + site + "/" + group_name.replace(" ","%20").encode('utf8') + "/task/" + str(task_node._id)

          to_user_list = []
          for index, user_id in enumerate(task_dict["Assignee"]):
              user_obj = User.objects.get(id=user_id)
              task_dict["Assignee"][index] = user_obj.username
              if user_obj not in to_user_list:
                  to_user_list.append(user_obj)

          msg = "Task '" + task_node.name + "' has been reported by " + from_user + \
              "\n     - Status: " + task_dict["Status"] + \
              "\n     - Priority: " + task_dict["Priority"] + \
              "\n     - Assignee: " + ", ".join(task_dict["Assignee"]) +  \
              "\n     - For more details, please click here: " + url_link

          activity = "reported task"
          render_label = render_to_string(
              "notification/label.html",
              {
                  "sender": from_user,
                  "activity": activity,
                  "conjunction": "-",
                  "link": url_link
              }
          )
          notification.create_notice_type(render_label, msg, "notification")
          notification.send(to_user_list, render_label, {"from_user": from_user})

    return task_node


@get_execution_time
def get_student_enrollment_code(college_id, node_id_to_ignore, registration_date, college_group_id=None):
    """Returns new student's enrollment code

    Enrollment Code is combination of following values:
    Code: (MH/SNG/15/xxxx)
    - 2-letters state code
    - 3-letters college code
    - 2-digits year of registration
    - 4-digits Auto-generated No.

    Arguments:
    college_id: ObjectId of college's node
    node_id_to_ignore: ObjectId of the student node for which this function generates enrollment_code
    registration_date: Date of registration of student node for which this function generates enrollment_code
    college_group_id [Optional]: ObjectId of college's group node

    Returns:
    Newly created enrollment code for student node
    """

    new_student_enrollment_code = u""
    last_enrollment_code = u""
    enrollment_code_except_num = u""
    college_id = ObjectId(college_id)
    if college_group_id:
        college_group_id = ObjectId(college_group_id)
    college_name = u""
    college_code = u""
    state_code = u""
    two_digit_year_code = u""
    student_count = 0
    four_digit_num = u""

    # If registering very first student, then create enrollment code
    # Else fetch enrollment code from last registered student node

    # Fetch college enrollemnt code
    college_node = node_collection.collection.aggregate([{
        "$match": {
            "_id": college_id
        }
    }, {
        "$project": {
            "college_name": "$name",
            "college_code": "$attribute_set.enrollment_code",
            "college_group_id": "$relation_set.has_group",
            "state_id": "$relation_set.organization_belongs_to_state"
        }
    }])

    college_node = college_node["result"]
    if college_node:
        college_node = college_node[0]
        colg_group_id = college_node["college_group_id"]
        if colg_group_id:
            colg_group_id = ObjectId(colg_group_id[0][0])
            if colg_group_id != college_group_id:
                # Reset college_group_id as passed is not given
                # college node's group id
                college_group_id = colg_group_id

        college_name = college_node["college_name"]

        # Set College enrollment code
        college_code = college_node["college_code"]
        if college_code:
            college_code = college_code[0]

        if not college_name or not college_code:
            raise Exception(
                "Either name or enrollment code is not set for given college's ObjectId(" + str(college_id) + ") !!!")

        # Set Last two digits of current year
        # current_year = str(datetime.today().year)
        current_year = str(registration_date.year)
        two_digit_year_code = current_year[-2:]

        # Fetch total no. of students registered for current year
        # Along with enrollment code of last registered student
        date_gte = datetime.strptime("1/1/" + current_year, "%d/%m/%Y")
        date_lte = datetime.strptime("31/12/" + current_year, "%d/%m/%Y")
        student_gst = node_collection.one({
            "_type": "GSystemType",
            "name": "Student"
        })
        res = node_collection.collection.aggregate([{
            "$match": {
                "_id": {"$nin": [ObjectId(node_id_to_ignore)]},
                "member_of": student_gst._id,
                "group_set": college_group_id,
                "relation_set.student_belongs_to_college": college_id,
                "attribute_set.registration_date": {'$gte': date_gte, '$lte': date_lte},
                "status": u"PUBLISHED"
            }
        }, {
            "$sort": {
                "created_at": 1
            }
        }, {
            "$group": {
                "_id": {
                    "college": college_name,
                    "registration_year": current_year
                },
                "count": {
                    "$sum": 1
                },
                "last_enrollment_code": {
                    "$last": "$attribute_set.enrollment_code"
                }
            }
        }])

        student_data_result = res["result"]

        if student_data_result:
            student_count = student_data_result[0]["count"]
            last_enrollment_code = student_data_result[
                0]["last_enrollment_code"]
            if last_enrollment_code:
                last_enrollment_code = last_enrollment_code[0]

            if last_enrollment_code and student_count:
                # Fetch student enrollment code of last registered student node
                enrollment_code_except_num, four_digit_num = last_enrollment_code.rsplit(
                    "/", 1)
                four_digit_num = int(last_enrollment_code[-4:])

                if four_digit_num == student_count:
                    # 4. Four digit number of student's count (new) set
                    four_digit_num = "%04d" % (student_count + 1)
                    new_student_enrollment_code = u"%(enrollment_code_except_num)s/%(four_digit_num)s" % locals(
                    )

                else:
                    raise Exception(
                        "Inconsistent Data Found (Student count & last enrollment code's number doesn't match) !!!")
            else:
                raise Exception(
                    "Invalid Data Found (Student count & no last enrollment code) !!!")
        else:
            # Registering very first student node
            # Create enrollment code, hence fetch state node's state-code
            state_id = college_node["state_id"]
            if state_id:
                state_id = ObjectId(state_id[0][0])

                # Fetch state code
                state_node = node_collection.collection.aggregate([{
                    "$match": {
                        "_id": state_id
                    }
                }, {
                    "$project": {
                        "state_name": "$name",
                        "state_code": "$attribute_set.state_code"
                    }
                }])

                # 2. State code set
                state_node = state_node["result"]
                if state_node:
                    state_node = state_node[0]
                    state_name = state_node["state_name"]
                    state_code = state_node["state_code"]
                    if state_code:
                        state_code = state_code[0]
                    else:
                        raise Exception(
                            "No state code found for given state(" + state_name + ")")

                # 4. Four digit number of student's count (new) set
                four_digit_num = "%04d" % (student_count + 1)

                new_student_enrollment_code = u"%(state_code)s/%(college_code)s/%(two_digit_year_code)s/%(four_digit_num)s" % locals(
                )
            else:
                raise Exception(
                    "Either state not set or inconsistent state value found for given college(" + college_name + ") !!!")

        return new_student_enrollment_code
    else:
        raise Exception(
            "No college node exists with given college's ObjectId(" + str(college_id) + ") !!!")


@get_execution_time
def create_college_group_and_setup_data(college_node):
    """
    Creates private group for given college; establishes relationship
    between them via "has_group" RelationType.

    Also populating data into it needed for registrations.

    Arguments:
    college_node -- College node (or document)

    Returns:
    College group node
    GRelation node
    """

    gfc = None
    gr_gfc = None

    # [A] Creating group
    group_gst = node_collection.one(
        {'_type': "GSystemType", 'name': "Group"},
        {'_id': 1}
    )
    creator_and_modifier = college_node.created_by

    gfc = node_collection.one(
        {'_type': "Group", 'name': college_node.name},
        {'_id': 1, 'name': 1, 'group_type': 1}
    )

    if not gfc:
        gfc = node_collection.collection.Group()
        gfc._type = u"Group"
        gfc.name = college_node.name
        gfc.altnames = college_node.name
        gfc.member_of = [group_gst._id]
        gfc.group_type = u"PRIVATE"
        gfc.created_by = creator_and_modifier
        gfc.modified_by = creator_and_modifier
        gfc.contributors = [creator_and_modifier]
        gfc.status = u"PUBLISHED"
        gfc.save()


    if "_id" in gfc:
        has_group_rt = node_collection.one(
            {'_type': "RelationType", 'name': "has_group"}
        )
        gr_gfc = create_grelation(college_node._id, has_group_rt, gfc._id)

        # [B] Setting up data into college group
        if gr_gfc:
            # List of Types (names) whose data needs to be populated
            # in college group
            gst_list = [
                "Country", "State", "District", "University",
                "College", "Caste", "NUSSD Course"
            ]

            gst_cur = node_collection.find(
                {'_type': "GSystemType", 'name': {'$in': gst_list}}
            )

            # List of Types (ObjectIds)
            gst_list = []
            for each in gst_cur:
                gst_list.append(each._id)

            mis_admin = node_collection.one(
                {
                    '_type': "Group",
                    '$or': [
                        {'name': {'$regex': u"MIS_admin", '$options': 'i'}},
                        {'altnames': {'$regex': u"MIS_admin", '$options': 'i'}}
                    ],
                    'group_type': "PRIVATE"
                },
                {'_id': 1}
            )

            # Update GSystem node(s) of GSystemType(s) specified in gst_list
            # Append newly created college group's ObjectId in group_set field
            node_collection.collection.update(
                {
                    '_type': "GSystem", 'member_of': {'$in': gst_list},
                    'group_set': mis_admin._id
                },
                {'$addToSet': {'group_set': gfc._id}},
                upsert=False, multi=True
            )

    return gfc, gr_gfc


def get_published_version_list(request, document_object):
    """Returns the list of revision numbers of published nodes.
    """
    published_node_version = []
    rcs = RCS()
    fp = history_manager.get_file_path(document_object)
    cmd = 'rlog  %s' % \
        (fp)
    rev_no = ""
    proc1 = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE)
    for line in iter(proc1.stdout.readline, b''):
        if line.find('revision') != -1 and line.find('selected') == -1:
            rev_no = string.split(line, 'revision')
            rev_no = rev_no[1].strip('\t\n\r')
            rev_no = rev_no.strip(' ')
        if line.find('PUBLISHED') != -1:
            published_node_version.append(rev_no)
    return published_node_version


def parse_data(doc):
  '''Section to parse node '''
  user_idlist = ['modified_by','created_by','author_set','contributors']
  date_typelist = ['last_update','created_at']
  objecttypelist = ['member_of','group_set', 'collection_set','prior_node']
  languagelist = ['language']
  content = ['content']
  keys_by_dict = ['attribute_set', 'relation_set']
  keys_by_filesize = ['file_size']

  for i in doc:

          if i in content:
             doc[i] = str(doc[i])
          if i in user_idlist:
             if type(doc[i]) == list :
                      temp =   ""
                      for userid in doc[i]:
                      		  if User.objects.filter(id = userid).exists():
	                              user = User.objects.get(id = userid)
	                              if user:
	                                if temp:
	                                        temp =temp  + "," + (str(user.get_username()) )
	                                else:
	                                        temp = str(user.get_username())
	              doc[i] = temp
             else:

                      		  if User.objects.filter(id = doc[i]).exists():
	                              user = User.objects.get(id = doc[i])
	                              if user:
	                                doc[i] = str(user.get_username())
          elif i in date_typelist:
              doc[i] = datetime.strftime(doc[i],"%d %B %Y %H:%M")
          elif i in objecttypelist:
               for j in doc[i]:
                   node = node_collection.one({"_id":ObjectId(j)})
                   doc[i] = node.name
          if i in keys_by_dict:
              att_dic = {}
              if "None" not in doc[i]:
                      if type(doc[i]) != str and i == "attribute_set":
                              str1 =""
                              for att in doc[i]:
                                      for k1, v1 in att.items():
                                        if type(v1) == list:
                                                str1 = ""
                                                if type(v1[0]) in [OrderedDict, dict]:
                                                    for each in v1:
                                                        str1 += str(each["name"]) + ", "
                                                else:
                                                    str1 = ",".join(str(v1))
                                                att_dic[k1] = str1
                                        else:
                                                att_dic[k1] = str(v1)
                              for att,value in att_dic.items():
                                  str1 =  str1 + att + " : " + value + "  "+"\n"
                              doc[i] = str1
                      if i == "relation_set":
                              str1 =""
                              for each in doc[i]:
                                      for k1, v1 in each.items():
                                              for rel in v1:
                                                      if isinstance(rel, ObjectId):
                                                              rel = node_collection.one({'_id':ObjectId(rel)})
                                                              att_dic[k1] = rel.name
                                                      elif '$oid' in rel:
                                                              rel = rel['$oid']
                                                              rel = node_collection.one({'_id':ObjectId(rel)})
                                                              att_dic[k1] = rel.name
                                                      #print "\n\n\nrel", rel
                                                      rel = node_collection.one({'_id':ObjectId(rel._id)})
                                                      att_dic[k1] = rel.name
                              for att,value in att_dic.items():
                                  str1 =  str1 + att + " : " + value + "  "+"\n"
                              doc[i] = str1

          elif i == "rating":
             new_str = ""
             if doc[i]:
               for k in doc[i]:
                  userid = k['user_id']
                  score = k['score']
                  if User.objects.filter(id = userid).exists():
	                                user = User.objects.get(id = userid)
	                                if user:
	                                   new_str = new_str + "User" +":" + str(user.get_username()) + "  " + "Score" + str (score) + "\n"
	     if not doc[i]:
	              doc[i] = ""
	     else:
	              doc[i] = new_str
          elif i == "location":
              coordinates = []
              parsed_string = ""
              for j in doc[i]:
                 coordinates = j['geometry']['coordinates']
              if  coordinates:
                   for j in coordinates:
                      if parsed_string:
                        parsed_string =   str(parsed_string)  + "," + str(j)
                      else:
                        parsed_string =   str(j)
              if not doc[i]:
                   doc[i] = ""
              else:
                   doc[i] = parsed_string

          elif not doc[i]:
             doc[i] = ""


def delete_gattribute(subject_id=None, deletion_type=0, **kwargs):
    """This function deletes GAttribute node(s) of Triples collection.

    Keyword arguments:
    subject_id -- (Optional argument)
        - Specify this argument if you need to delete/purge GAttribute(s)
        related to given node belonging to Nodes collection
        - ObjectId of the node whose GAttribute node(s) need(s) to be deleted,
        accepted in either format String or ObjectId
        - Default value is set to None

    kwargs["node_id"] -- (Optional argument)
        - Specify this argument if you need to delete/purge only a given
        GAttribute node
        - ObjectId of the GAttribute node to be deleted/purged, accepted in
        either format String or ObjectId
        - If this argument is specified, subject_id will work as an optional
        argument and even query variable would be overridden by node_id's
        query variable

    deletion_type -- (Optional argument)
        - Specify this to signify which type of deletion you need to perform
        - Accepts only either of the following values:
        (a) 0 (zero, i.e.  Normal delete)
            - Process in which node exists in database; only status field's
            value is set to "DELETED"
        (b) 1 (one, i.e. Purge)
            - Process in which node is deleted from the database
        - Default value is set to 0 (zero)

    Returns:
    A tuple with following values:
        First-element: Boolean value
        Second-element: Message

    If deletion is successful, then (True, "Success message.")
    Otherwise, (False, "Error message !")

    Examples:
    del_status, del_status_msg = delete_attribute(
        subject_id=ObjectId("...")
        [, deletion_type=0[/1]]
    )

    del_status, del_status_msg = delete_attribute(
        node_id=ObjectId("...")
        [, deletion_type=0[/1]]
    )
    """
    node_id = None
    str_node_id = ""
    str_subject_id = ""
    str_deletion_type = "deleted"  # As default value of deletion_type is 0

    # Below variable holds list of ObjectId (string format)
    # of GAttribute node(s) which is/are going to be deleted
    gattribute_deleted_id = []

    # Below variable holds list of ObjectId (string format)
    # of GAttribute node(s) whose object_value field is/are going to be updated
    gattribute_updated_id = []

    query = OrderedDict()

    try:
        # print "\n 1 >> Begin..."
        if deletion_type not in [0, 1]:
            delete_status_message = "Must pass \"deletion_type\" agrument's " \
                + "value as either 0 (Normal delete) or 1 (Purge)"
            raise Exception(delete_status_message)

        # print "\n 2 >> looking for node_id..."
        if "node_id" in kwargs:
            # Typecast node_id from string into ObjectId,
            # if found in string format
            node_id = kwargs["node_id"]

            # print "\t 2a >> convert node_id..."
            if node_id:
                if type(node_id) == ObjectId:
                    str_node_id = str(node_id)
                    # print "\t 2b >> node_id -- O to s: ",
                    # type(str_subject_id), " -- ", str_subject_id
                else:
                    str_node_id = node_id
                    if ObjectId.is_valid(node_id):
                        node_id = ObjectId(node_id)
                        # print "\t 2c >> node_id -- s to O: ",
                        # type(str_subject_id), " -- ", str_subject_id
                    else:
                        delete_status_message = "Invalid value found for node_id " \
                            + "(%(str_node_id)s)... [Expected value in" % locals() \
                            + " ObjectId format] !!!"
                        raise Exception(delete_status_message)

                # Forming query to delete a specific GAtribute node
                query = {"_id": node_id}
                # print "\t 2d >> query... ", query

        # print "\n 3 >> looking for subject_id..."
        if not node_id:
            # Perform check for subject_id
            # print "\t 3 >> found subject_id..."
            if not subject_id:
                delete_status_message = "Either specify subject_id " \
                    + "or node_id [Expected value in ObjectId format] !!!"
                raise Exception(delete_status_message)

            # print "\t 3a >> convert subject_id..."
            if subject_id:
                # Typecast subject_id from string into ObjectId,
                # if found in string format
                if type(subject_id) == ObjectId:
                    str_subject_id = str(subject_id)
                    # print "\t 3b >> subject_id -- O to s: ",
                    # type(str_subject_id), " -- ", str_subject_id
                else:
                    str_subject_id = subject_id
                    if ObjectId.is_valid(subject_id):
                        subject_id = ObjectId(subject_id)
                        # print "\t 3c >> subject_id -- s to O: ",
                        # type(str_subject_id), " -- ", str_subject_id
                    else:
                        if not node_id:
                            delete_status_message = "Invalid value found for subject_id " \
                                + "(%(str_subject_id)s)... [Expected value in" % locals() \
                                + " ObjectId format] !!!"
                            raise Exception(delete_status_message)

                # Check first whether request is
                # for single GAttribute node delete or not
                # print "\t 3d >> Override query... ???"
                if not node_id:
                    # Form this query only when you need to
                    # delete GAttribute(s) related to a given node
                    query = {"_type": "GAttribute", "subject": subject_id}
                    # print "\t 3e >> query (YES)... ", query

        # Based on what you need to perform (query)
        # Delete single GAttribute node, or
        # Delete GAttribute node(s) related to a given node (subject_id)
        # Find the required GAttribute node(s)
        gattributes = triple_collection.find(query)
        # print "\n 4 >> gattributes.count()... ", gattributes.count()

        # Perform normal delete operation (i.e. deletion_type == 0)
        if deletion_type == 1:
            for each_ga in gattributes:
                gattribute_deleted_id.append(each_ga._id.__str__())

                if each_ga.status != u"DELETED":
                    create_gattribute(each_ga.subject, each_ga.attribute_type)
                    # print "\t 4 >> each_ga (0) ... ", each_ga._id

        # print "\n 5 >> gattribute_deleted_id... " + ",
        # ".join(gattribute_deleted_id)

        # Perform purge operation
        if deletion_type == 1:
            # Remove from database
            str_deletion_type = "purged"
            single_gattribute_to_be_purged = triple_collection.find_one(query)
            if single_gattribute_to_be_purged:
                # deleting related RCS file
                HistoryManager.delete_json_file(single_gattribute_to_be_purged, type(single_gattribute_to_be_purged))
                triple_collection.collection.remove(query)

            # print "\n 6 >> purged also... " + ",
            # ".join(gattribute_deleted_id)

        # Formulate delete-status-message
        if gattribute_deleted_id:
            delete_status_message = "\tFollowing are the list of ObjectId(s) of " \
                + "%(str_deletion_type)s GAttribute node(s):- \n\t" % locals() \
                + ", ".join(gattribute_deleted_id)
        else:
            delete_status_message = "\tNo GAttribute nodes have been " \
                + "%(str_deletion_type)s !!!" % locals()

        # print "\n 7 >> special use-case... "
        # Special use-case
        if subject_id:
            # Find GAttribute node(s) whose object_value field (i.e. a list)
            # has subject_id as one of it's value
            gattributes = None
            gattributes = triple_collection.find({
                "_type": "GAttribute", "object_value": subject_id
            })
            # print "\n 8 >> gattributes.count()... ", gattributes.count()
            for each_ga in gattributes:
                # (a) Update GAttribute node's object_value field
                # Remove subject_id from object_value
                # (b) Update subject node's attribute_set field
                # Remove subject_id from the value corresponding to
                # subject node's "attribute-name" key referenced
                # in attribute_set field

                # Expecting object_value as list of ObjectIds
                obj_val = []
                # print "\n 8a >> each_ga... ", each_ga._id
                if type(each_ga.object_value) == list:
                    obj_val = each_ga.object_value

                    # Declaration required to avoid list-copy by reference
                    prev_obj_val = []
                    prev_obj_val.extend(obj_val)

                    if subject_id in obj_val:
                        obj_val.remove(subject_id)

                    # print "\t 8b >> obj_val... ", obj_val
                    # print "\t 8c >> prev_obj_val... ", prev_obj_val

                    if prev_obj_val != obj_val:
                        # Update only when there is any change found
                        # Below call will perform (a) & (b) collectively
                        create_gattribute(
                            each_ga.subject, each_ga.attribute_type, obj_val
                        )

                        gattribute_updated_id.append(each_ga._id.__str__())
                        # print "\t 8d >> updated..."

            if gattribute_updated_id:
                delete_status_message += "\tFollowing are the list of ObjectId(s) of " \
                    + "GAttribute node(s) whose object_value field is updated:- \n\t" \
                    + ", ".join(gattribute_updated_id)

        # Return output of the function
        # print "\n 9 >> ", delete_status_message
        return (True, delete_status_message)
    except Exception as e:
        delete_status_message = "DeleteGAttributeError: " + str(e)
        return (False, delete_status_message)


def delete_grelation(subject_id=None, deletion_type=0, **kwargs):
    """This function deletes GRelation node(s) of Triples collection.

    Keyword arguments:
    subject_id -- (Optional argument)
        - Specify this argument if you need to delete/purge GRelation(s)
        related to given node belonging to Nodes collection
        - ObjectId of the node whose GRelation node(s) need(s) to be deleted,
        accepted in either format String or ObjectId
        - Default value is set to None

    kwargs["node_id"] -- (Optional argument)
        - Specify this argument if you need to delete/purge only a given
        GRelation node
        - ObjectId of the GRelation node to be deleted/purged, accepted in
        either format String or ObjectId
        - If this argument is specified, subject_id will work as an optional
        argument and even query variable would be overridden by node_id's
        query variable

    deletion_type -- (Optional argument)
        - Specify this to signify which type of deletion you need to perform
        - Accepts only either of the following values:
        (a) 0 (zero, i.e.  Normal delete)
            - Process in which node exists in database; only status field's
            value is set to "DELETED"
        (b) 1 (one, i.e. Purge)
            - Process in which node is deleted from the database
        - Default value is set to 0 (zero)

    Returns:
    A tuple with following values:
        First-element: Boolean value
        Second-element: Message

    If deletion is successful, then (True, "Success message.")
    Otherwise, (False, "Error message !")

    Examples:
    del_status, del_status_msg = delete_grelation(
        subject_id=ObjectId("...")
        [, deletion_type=0[/1]]
    )

    del_status, del_status_msg = delete_grelation(
        node_id=ObjectId("...")
        [, deletion_type=0[/1]]
    )
    """
    node_id = None
    str_node_id = ""
    str_subject_id = ""
    str_deletion_type = "deleted"  # As default value of deletion_type is 0

    # Below variable holds list of ObjectId (string format)
    # of GRelation node(s) which is/are going to be deleted
    grelation_deleted_id = []

    # Below variable holds list of ObjectId (string format)
    # of GRelation node(s) [inverse-relation] which is/are going to be deleted
    inverse_grelation_deleted_id = []

    query_by_id = {}  # Search by _id field
    query_for_relation = OrderedDict()  # Search by subject field
    query_for_inverse_relation = OrderedDict()  # Search by right_subject field

    def _perform_delete_updates_on_node(gr_node):
        rt_node = node_collection.one({'_id': ObjectId(gr_node.relation_type)})
        rel_name = rt_node.name
        inv_rel_name = rt_node.inverse_name
        subj = gr_node.subject
        right_subj = gr_node.right_subject

        # Remove right-subject-node's ObjectId from the value
        # corresponding to subject-node's "relation-name" key
        # referenced in relation_set field
        res = node_collection.collection.update({
            '_id': subj,
            'relation_set.' + rel_name: {'$exists': True}
        }, {
            '$pull': {'relation_set.$.' + rel_name: right_subj}
        },
            upsert=False, multi=False
        )
        # print "\n 5 -- subject node's (", subj, ") relation-name key (",
        # rel_name, ") referenced in relation_set field updated -- \n", res

        # Remove subject-node's ObjectId from the value corresponding
        # to right-subject-node's "inverse-relation-name" key
        # referenced in relation_set field
        res = node_collection.collection.update({
            '_id': right_subj,
            'relation_set.' + inv_rel_name: {'$exists': True}
        }, {
            '$pull': {'relation_set.$.' + inv_rel_name: subj}
        },
            upsert=False, multi=False
        )
        # print " 5 -- right_subject node's (", right_subj, ")
        # inverse-relation-name key (", inv_rel_name, ") referenced in
        # relation_set field updated -- \n", res

        gr_node.status = u"DELETED"
        gr_node.save()
        # gr_node.save(triple_node=rt_node, triple_id=rt_node._id)


    try:
        # print "\n 1 >> Begin..."
        if deletion_type not in [0, 1]:
            delete_status_message = "Must pass \"deletion_type\" agrument's " \
                + "value as either 0 (Normal delete) or 1 (Purge) !!!"
            raise Exception(delete_status_message)

        # print "\n 2 >> looking for node_id..."
        if "node_id" in kwargs:
            # Typecast node_id from string into ObjectId,
            # if found in string format
            node_id = kwargs["node_id"]

            # print "\t 2a >> convert node_id..."
            if node_id:
                if type(node_id) == ObjectId:
                    str_node_id = str(node_id)
                    # print "\t 2b >> node_id -- O to s: ",
                    # type(str_subject_id), " -- ", str_subject_id
                else:
                    str_node_id = node_id
                    if ObjectId.is_valid(node_id):
                        node_id = ObjectId(node_id)
                        # print "\t 2c >> node_id -- s to O: ",
                        # type(str_subject_id), " -- ", str_subject_id
                    else:
                        delete_status_message = "Invalid value found for node_id " \
                            + "(%(str_node_id)s)... [Expected value in" % locals() \
                            + " ObjectId format] !!!"
                        raise Exception(delete_status_message)

                # Forming query to delete a specific GRelation node
                query_by_id = {"_id": node_id}
                # print "\t 2d >> query... ", query_by_id

        # print "\n 3 >> looking for subject_id..."
        if not node_id:
            # Perform check for subject_id
            # print "\t 3 >> found subject_id..."
            if not subject_id:
                delete_status_message = "Either specify subject_id " \
                    + "or node_id [Expected value in ObjectId format] !!!"
                raise Exception(delete_status_message)

            # print "\t 3a >> convert subject_id..."
            if subject_id:
                # Typecast subject_id from string into ObjectId,
                # if found in string format
                if type(subject_id) == ObjectId:
                    str_subject_id = str(subject_id)
                    # print "\t 3b >> subject_id -- O to s: ",
                    # type(str_subject_id), " -- ", str_subject_id
                else:
                    str_subject_id = subject_id
                    if ObjectId.is_valid(subject_id):
                        subject_id = ObjectId(subject_id)
                        # print "\t 3c >> subject_id -- s to O: ",
                        # type(str_subject_id), " -- ", str_subject_id
                    else:
                        if not node_id:
                            delete_status_message = "Invalid value found for subject_id " \
                                + "(%(str_subject_id)s)... [Expected value in" % locals() \
                                + " ObjectId format] !!!"
                            raise Exception(delete_status_message)

                # Check first whether request is
                # for single GRelation node delete or not
                # print "\t 3d >> Override query... ???"
                if not node_id:
                    # Form this query only when you need to
                    # delete/purge GRelation(s) related to a given node
                    query_for_relation = {
                        "_type": "GRelation", "subject": subject_id}
                    query_for_inverse_relation = {
                        "_type": "GRelation", "right_subject": subject_id}
                    # print "\t 3e >> query (YES)... \n\t", query_for_relation,
                    # "\n\t", query_for_inverse_relation

        # Based on what you need to perform
        # Delete single GRelation node (query_by_id), or
        # Delete GRelation node(s) related to a given node (subject_id)
        # (i.e, query_for_relation and query_for_inverse_relation)
        # Find the required GRelation node(s) & perform required operation(s)
        if query_by_id:
            # print "\n delete single GRelation node"
            grelations = triple_collection.find(query_by_id)
            for each_rel in grelations:
                if each_rel.status != u"DELETED":
                    _perform_delete_updates_on_node(each_rel)
                grelation_deleted_id.append(each_rel._id.__str__())

            # print "\n 5 >> grelation_deleted_id... " + ",
            # ".join(grelation_deleted_id)

            # Perform purge operation
            if deletion_type == 1:
                # Remove from database
                str_deletion_type = "purged"
                single_grelation_to_be_purged = triple_collection.find_one(query_by_id)
                HistoryManager.delete_json_file(single_grelation_to_be_purged, type(single_grelation_to_be_purged))
                triple_collection.collection.remove(query_by_id)



                # print "\n 6 >> purged (relation) also... " + ",
                # ".join(grelation_deleted_id)
        else:
            # print "\n handle query_for_relation, query_for_inverse_relation"
            grelations = None
            inv_grelations = None

            # (1) Find relation(s) of given node (subject_id)
            # i.e, GRelation node where given node's ObjectId resides
            # in subject field
            grelations = triple_collection.find(query_for_relation)
            for each_rel in grelations:
                if each_rel.status != u"DELETED":
                    _perform_delete_updates_on_node(each_rel)
                grelation_deleted_id.append(each_rel._id.__str__())

            # (2) Find inverse-relation(s) of given node (subject_id)
            # i.e, GRelation node where given node's ObjectId resides
            # in right_subject field
            inv_grelations = triple_collection.find(query_for_inverse_relation)
            for each_inv_rel in inv_grelations:
                if each_inv_rel.status != u"DELETED":
                    _perform_delete_updates_on_node(each_inv_rel)
                inverse_grelation_deleted_id.append(each_inv_rel._id.__str__())

            # print "\n 5 >> grelation_deleted_id... " + ", ".join(grelation_deleted_id)
            # print "\n 5 >> inverse_grelation_deleted_id... " + ",
            # ".join(inverse_grelation_deleted_id)

            # Perform purge operation
            if deletion_type == 1:
                # Remove from database
                str_deletion_type = "purged"
                grelations_to_be_purged = triple_collection.find(query_for_relation)
                for each_grelations_to_be_purged in grelations_to_be_purged:
                    # deleting related RCS file
                    HistoryManager.delete_json_file(each_grelations_to_be_purged, type(each_grelations_to_be_purged))
                triple_collection.collection.remove(query_for_relation)
                triple_collection.collection.remove(query_for_inverse_relation)
                # print "\n 6 >> purged (relation) also... " + ", ".join(grelation_deleted_id)
                # print "\n 6 >> purged (inverse-relation) also... " + ",
                # ".join(inverse_grelation_deleted_id)


        # Formulate delete-status-message
        if grelation_deleted_id:
            delete_status_message = "\tFollowing are the list of ObjectId(s) of " \
                + "%(str_deletion_type)s GRelation [Normal relation] node(s):- \n\t" % locals() \
                + ", ".join(grelation_deleted_id)
        else:
            delete_status_message = "\tNo GRelation [Normal relation] nodes have been " \
                + "%(str_deletion_type)s !!!" % locals()

        if inverse_grelation_deleted_id:
            delete_status_message += "\n\n\tFollowing are the list of ObjectId(s) of " \
                + "%(str_deletion_type)s GRelation [Inverse relation] node(s):- \n\t" % locals() \
                + ", ".join(inverse_grelation_deleted_id)
        else:
            delete_status_message += "\n\n\tNo GRelation [Inverse relation] nodes have been " \
                + "%(str_deletion_type)s !!!" % locals()

        # Return output of the function
        # print "\n 9 >> ", delete_status_message
        return (True, delete_status_message)
    except Exception as e:
        delete_status_message = "DeleteGRelationError: " + str(e)
        return (False, delete_status_message)


def delete_node(
        node_id=None, collection_name=node_collection.collection_name,
        deletion_type=0, **kwargs):
    """This function deletes node belonging to either Nodes collection or
    Triples collection.

    Keyword Arguments:
    node_id -- (Optional argument)
        - Specify this argument if you need to delete/purge only a given
        node from Nodes/Triples collection
        - ObjectId of the node to be deleted/purged, accepted in
        either format String or ObjectId
        - If this argument is specified, then subject_id parameter will be
        ignored (if specified) in case of deleting node from Triples collection
        - If this argument is ignored, then you must specify subject_id as a
        parameter (mandatory in case of deleting node from Triples collection).
        - Default value is set to None

    collection_name -- (Optional argument)
        - Specify this to signify from which collection you need to delete node
        i.e. helpful in setting-up the collection-variable
        - Name of the collection you need to refer for performing deletion
        - Accepts only either of the following values:
        (a) node_collection.collection_name/"Nodes"
        (b) triple_collection.collection_name/"Triples"
        - Default set to node_collection.collection_name (i.e. "Nodes")

    deletion_type -- (Optional argument)
        - Specify this to signify which type of deletion you need to perform
        - Accepts only either of the following values:
        (a) 0 (zero, i.e.  Normal delete)
            - Process in which node exists in database; only status field's
            value is set to "DELETED"
        (b) 1 (one, i.e. Purge)
            - Process in which node is deleted from the database
        - Default value is set to 0 (zero)

    kwargs["subject_id"] -- (Optional argument)
        - Specify this argument if you need to delete/purge GRelation(s) and/or
        GAttribute(s) related to given node belonging to Nodes collection
        - ObjectId of the node whose GAttribute(s) and/or GRelation node(s)
        need(s) to be deleted, accepted in either format String or ObjectId
        - Default value is set to None

    kwargs["_type"] -- (Optional argument)
        - Specify this argument if you need to delete/purge specifically either
        only GAttribute node(s) or GRelation node(s)
        - If ignored, then by default node(s) belonging to both types
        (GAttribute and GRelation) will be considered for deleting/purging
        - Can also be specified in case of delete/purge Nodes collection node

    Returns:
    A tuple with following values:
        First-element: Boolean value
        Second-element: Message

    If deletion is successful, then (True, "Success message.")
    Otherwise, (False, "Error message !")

    If you need to delete node of Nodes collection, then you only need to
    specify node_id, collection_name, and deletion_type as parameters.
        Examples:
        del_status, del_status_msg = delete_node(
            node_id=ObjectId("...")
            [, collection_name=node_collection.collection_name]
            [, deletion_type=0[/1]]
        )

    If you need to delete node(s) of Triples collection, then you need to
    specify node_id/subject_id [depending on whether you need to delete single
    node or multiple nodes which are related to given node of Nodes collection]
    , collection_name, _type, and deletion_type as parameters.
        Examples:
        del_status, del_status_msg = delete_node(
            subject_id=ObjectId("..."),
            collection_name=triple_collection.collection_name
            [, _type="GAttribute"[/"GRelation"]]
            [, deletion_type=0[/1]]
        )
        del_status, del_status_msg = delete_node(
            node_id=ObjectId("..."),
            collection_name=triple_collection.collection_name
            [, _type="GAttribute"[/"GRelation"]]
            [, deletion_type=0[/1]]
        )
    """

    try:
        # print "\n 1 >> Entered in delete_node() function..."
        # Convert into string format if value of some other data-type is passed
        collection_name = collection_name.__str__()

        # Check from which collection you need to delete node from
        if collection_name == node_collection.collection_name:
            # Perform deletion operation on Nodes collection
            str_node_id = ""
            query = {}
            node_to_be_deleted = None
            node_name = ""
            # As default value of deletion_type is 0
            str_deletion_type = "deleted"
            delete_status_message = ""

            # print "\n 2 >> Nodes collection..."
            if deletion_type not in [0, 1]:
                delete_status_message = "Must pass \"deletion_type\" agrument's " \
                    + "value as either 0 (Normal delete) or 1 (Purge) !!!"
                raise Exception(delete_status_message)

            # print "\t 3 >> found node_id..."
            if not node_id:
                delete_status_message = "No value found for node_id" \
                    + "... [Expected value in ObjectId format] !!!"
                raise Exception(delete_status_message)

            # print "\t 3a >> convert node_id..."
            # Typecast node_id from string into ObjectId,
            # if found in string format
            if type(node_id) == ObjectId:
                str_node_id = str(node_id)
                # print "\t 3b >> node_id -- O to s: ", type(str_node_id), " --
                # ", str_node_id
            else:
                str_node_id = node_id
                if ObjectId.is_valid(node_id):
                    node_id = ObjectId(node_id)
                    # print "\t 3c >> node_id -- s to O: ", type(str_node_id),
                    # " -- ", str_node_id
                else:
                    delete_status_message = "Invalid value found for node_id " \
                        + "(%(str_node_id)s)... [Expected value in" % locals() \
                        + " ObjectId format] !!!"
                    raise Exception(delete_status_message)

            # Forming query to delete a specific node from Nodes collection
            query = {"_id": node_id}
            # print "\t 3d >> query... ", query

            # Fetch the deleting-node from given node_id
            node_to_be_deleted = node_collection.find_one(query)

            if not node_to_be_deleted:
                delete_status_message = "Node with given ObjectId " \
                    + "(%(str_node_id)s) doesn't exists " % locals() \
                    + "in Nodes collection !!!"
                raise Exception(delete_status_message)

            node_name = node_to_be_deleted.name

            if node_to_be_deleted.status == u"DELETED" and deletion_type == 0:
                delete_status_message = "%(node_name)s (%(str_node_id)s) has " % locals() \
                    + "already been deleted (using normal delete)." \
                    + "\n\nIf required, you can still purge this node !"
                return (True, delete_status_message)

            # print "\n 4 >> node to be deleted fetched successfully... ",
            # node_to_be_deleted.name
            if ((node_to_be_deleted.status == u"DELETED" and
                 deletion_type == 1) or
                    (node_to_be_deleted.status != u"DELETED")):
                # Perform delete/purge operation for
                # deleting-node's GAttribute(s)
                # print "\n\n 5 >> node's (", node_to_be_deleted.name,")
                # GAttribute... "
                del_status, del_status_msg = delete_gattribute(
                    subject_id=node_to_be_deleted._id,
                    deletion_type=deletion_type
                )
                if not del_status:
                    raise Exception(del_status_msg)
                delete_status_message = del_status_msg
                # print "\n 5* >> delete_status_message... \n",
                # delete_status_message

                # Required as below this node is getting saved and
                # in above delete_gattribute() function, it's getting updated
                node_to_be_deleted.reload()

                # Perform delete/purge operation
                # for deleting-node's GRelation(s)
                # print "\n\n 6 >> node's (", node_to_be_deleted.name,")
                # GRelation... "
                del_status, del_status_msg = delete_grelation(
                    subject_id=node_to_be_deleted._id,
                    deletion_type=deletion_type
                )
                if not del_status:
                    raise Exception(del_status_msg)
                delete_status_message += "\n\n" + del_status_msg
                # print "\n 6* >> delete_status_message... \n",
                # delete_status_message

                # Required as below this node is getting saved and
                # in above delete_gattribute() function, it's getting updated
                node_to_be_deleted.reload()

                # Search deleting-node's ObjectId in collection_set field and
                # remove from it, if found any
                res = node_collection.collection.update({
                    "_type": {'$in': ['GSystem', 'Group']},
                    "collection_set": node_to_be_deleted._id
                }, {
                    "$pull": {"collection_set": node_to_be_deleted._id}
                },
                    upsert=False, multi=True
                )
                # print "\n 7 >> collection_set : \n", res

                # Search deleting-node's ObjectId in prior_node field and
                # remove from it, if found any
                res = node_collection.collection.update({
                    "_type": "GSystem", "prior_node": node_to_be_deleted._id
                }, {
                    "$pull": {"prior_node": node_to_be_deleted._id}
                },
                    upsert=False, multi=True
                )
                # print "\n 8 >> prior_node : \n", res

                # Search deleting-node's ObjectId in post_node field and
                # remove from it, if found any
                res = node_collection.collection.update({
                    "_type": "GSystem", "post_node": node_to_be_deleted._id
                }, {
                    "$pull": {"post_node": node_to_be_deleted._id}
                },
                    upsert=False, multi=True
                )
                # print "\n 9 >> post_node : \n", res

                # Perform normal delete on deleting-node
                # Only changes the status of given node to DELETED
                node_to_be_deleted.status = u"DELETED"
                node_to_be_deleted.save()


            # Perform Purge operation on deleting-node
            if deletion_type == 1:
                # Remove from database
                str_deletion_type = "purged"

                # If given node is of member-of File GApp
                # Then remove it's references from GridFS as well
                # Consider File GApp's ObjectId is there in member_of field
                # print "\n node_to_be_deleted.member_of_names_list: ",
                # node_to_be_deleted.member_of_names_list
                if "File" in node_to_be_deleted.member_of_names_list:
                    # print "\n 10 >> node found as File; nodes in GridFS : ",
                    # len(node_to_be_deleted.fs_file_ids)
                    if hasattr(node_to_be_deleted, 'fs_file_ids') and node_to_be_deleted.fs_file_ids:
                        for each in node_to_be_deleted.fs_file_ids:
                            if node_to_be_deleted.fs.files.exists(each) and node_collection.find({'fs_file_ids': {'$in': [each]} }).count() == 1:
                                # print "\tdeleting node in GridFS : ", each
                                node_to_be_deleted.fs.files.delete(each)
                    elif hasattr(node_to_be_deleted, 'if_file'):
                        fh_original_id = node_to_be_deleted.if_file.original.id
                        if node_collection.find({'_type': 'GSystem', 'if_file.original.id': ObjectId(fh_original_id) }).count() == 1:
                            for each_file in ['original', 'mid', 'thumbnail']:
                                fh_id = node_to_be_deleted.if_file[each_file]['id']
                                fh_relurl = node_to_be_deleted.if_file[each_file]['relurl']
                                if fh_id or fh_relurl:
                                    Filehive.delete_file_from_filehive(fh_id, fh_relurl)

                # deleting related RCS file
                HistoryManager.delete_json_file(node_to_be_deleted, type(node_to_be_deleted))

                # Finally delete the node
                node_to_be_deleted.delete()

            delete_status_message += "\n\n %(node_name)s (%(str_node_id)s) " % locals() \
                + "%(str_deletion_type)s successfully." % locals()
            # print delete_status_message
            return (True, delete_status_message)

        elif collection_name == triple_collection.collection_name:
            # Perform deletion operation on Triples collection
            subject_id = None
            underscore_type = ""
            str_node_id = ""
            query = {}
            delete_status_message = ""

            # print "\n 3 >> Triples collection..."
            if deletion_type not in [0, 1]:
                delete_status_message = "Must pass \"deletion_type\" agrument's " \
                    + "value as either 0 (Normal delete) or 1 (Purge) !!!"
                raise Exception(delete_status_message)

            # print "\n 4 >> look out for subject_id..."
            if "subject_id" in kwargs:
                subject_id = kwargs["subject_id"]
                # print "\t4a >> found subject_id...", subject_id

            if (not node_id) and (not subject_id):
                delete_status_message = "Value not found for neither node_id nor " \
                    + "subject_id... [Expected value(s) in ObjectId format]"
                raise Exception(delete_status_message)

            # print "\n 5 >> look out for _type..."
            if "_type" in kwargs:
                underscore_type = kwargs["_type"].__str__()
                # print "\t5a >> found _type...", underscore_type
                if underscore_type not in ["GAttribute", "GRelation"]:
                    delete_status_message = "Invalid value found for _type parameter " \
                        + "%(underscore_type)s... " % locals() \
                        + "Please pass either GAttribute or GRelation"
                    raise Exception(delete_status_message)

            # print "\n 5b >> convert node_id..."
            if node_id:
                if type(node_id) == ObjectId:
                    str_node_id = str(node_id)
                    # print "\t 5ba >> node_id -- O to s: ", type(str_node_id),
                    # " -- ", str_node_id
                else:
                    str_node_id = node_id
                    if ObjectId.is_valid(node_id):
                        node_id = ObjectId(node_id)
                        # print "\t 5bb >> node_id -- s to O: ",
                        # type(str_node_id), " -- ", str_node_id
                    else:
                        delete_status_message = "Invalid value found for node_id " \
                            + "(%(str_node_id)s)... [Expected value in" % locals() \
                            + " ObjectId format] !!!"
                        raise Exception(delete_status_message)

                # Forming query to delete a specific node from Triples
                # collection
                query = {"_id": node_id}
                # print "\t 5bc >> query... ", query

                # Fetch the deleting-node from given node_id
                node_to_be_deleted = triple_collection.find_one(query)

                if not node_to_be_deleted:
                    delete_status_message = "Node with given ObjectId " \
                        + \
                        "(%(str_node_id)s) doesn't exists in Triples collection" % locals(
                        )
                    raise Exception(delete_status_message)
                # print "\t 5bd >> node_to_be_deleted... ",
                # node_to_be_deleted.name, " -- ", node_to_be_deleted._type

                # Resetting underscore_type
                # To rectify, if by mistake wrong value is set
                # That is, consider _type is set as "GAttribute" (by mistake)
                # but node (with node_id) represents "GRelation"
                # To avoid this kind of case(s), resetting underscore_type
                underscore_type = node_to_be_deleted._type
                # print "\t 5be >> underscore_type set to node_to_be_deleted's
                # _type... ", underscore_type

            if underscore_type == "GAttribute":
                # Delete/Purge only GAttribute node(s)

                # print "\n 6 >> Delete/Purge only GAttribute node(s)..."
                del_status, del_status_msg = delete_gattribute(
                    node_id=node_id, subject_id=subject_id,
                    deletion_type=deletion_type
                )
                if not del_status:
                    raise Exception(del_status_msg)
                delete_status_message = del_status_msg
                # print "\n 6* >> delete_status_message... \n",
                # delete_status_message
            elif underscore_type == "GRelation":
                # Delete/Purge only GRelation node(s)

                # print "\n 7 >> Delete/Purge only GRelation node(s)..."
                del_status, del_status_msg = delete_grelation(
                    node_id=node_id, subject_id=subject_id,
                    deletion_type=deletion_type
                )
                if not del_status:
                    raise Exception(del_status_msg)
                delete_status_message = del_status_msg
                # print "\n 7* >> delete_status_message... \n",
                # delete_status_message
            else:
                # Delete/Purge both GAttribute & GRelation node(s)

                # print "\n 8 >> Delete/Purge both GAttribute & GRelation node(s)..."
                # Delete/Purge GAttribute node(s)
                del_status, del_status_msg = delete_gattribute(
                    node_id=node_id, subject_id=subject_id,
                    deletion_type=deletion_type
                )
                if not del_status:
                    raise Exception(del_status_msg)
                delete_status_message = del_status_msg
                # print "\n 8* >> delete_status_message... \n",
                # delete_status_message

                # Delete/Purge GRelation node(s)
                del_status, del_status_msg = delete_grelation(
                    node_id=node_id, subject_id=subject_id,
                    deletion_type=deletion_type
                )
                if not del_status:
                    raise Exception(del_status_msg)
                delete_status_message += "\n\n" + del_status_msg
                # print "\n 8* >> delete_status_message... \n",
                # delete_status_message

            # Return output of the function
            # print delete_status_message
            return (True, delete_status_message)

        else:
            delete_status_message = " Invalid value (%(collection_name)s) " % locals() \
                + "found for collection_name field. Please refer function " \
                + "details for correct value !!!"
            raise Exception(delete_status_message)
    except Exception as e:
        delete_status_message = "Error (from delete_node) :-\n" + str(e)
        return (False, delete_status_message)


def repository(request, group_id):
    '''
    It's an NROER repository. Which will hold the list of apps.
    '''

    gapp_metatype = node_collection.one({"_type": "MetaType", "name": "GAPP"})

    gapps_list = [i.values()[0] for i in GSTUDIO_NROER_GAPPS]
    gapps_list.insert(gapps_list.index('program'), 'event')
    gapps_list.pop(gapps_list.index('program'))
    # print gapps_list

    gapps_obj_list = []

    for each_gapp in gapps_list:
        gapp_obj = node_collection.one({'_type': 'GSystemType',
                                        'name': {"$regex": each_gapp, "$options": "i"},
                                        "member_of": {"$in": [gapp_metatype._id]}
                                        })
        gapps_obj_list.append(gapp_obj)

    return render_to_response("ndf/repository.html",
                              {"gapps_obj_list": gapps_obj_list,
                               "gapps_dict": GSTUDIO_NROER_GAPPS,
                               'group_id': group_id, 'groupid': group_id
                               },
                              context_instance=RequestContext(request)
                              )

def create_thread(group_id, node, user_id, release_response_val, interaction_type_val, start_time, end_time):
    user_id = node.created_by
    thread_node = None
    from gnowsys_ndf.ndf.templatetags.ndf_tags import get_relation_value, get_attribute_value
    has_thread_rt = node_collection.one({"_type": "RelationType", 
        "name": u"has_thread"})
    has_thread_triple_of_node = triple_collection.find_one({'subject': node._id, 
        'relation_type': has_thread_rt._id, 'status': u'PUBLISHED'})
    if has_thread_triple_of_node:
        thread_node_id = has_thread_triple_of_node.right_subject
        thread_node = node_collection.one({'_id': ObjectId(thread_node_id)})

    if not thread_node:

        twist_gst = node_collection.one({'_type': 'GSystemType',
                     'name': 'Twist'})
        thread_node = node_collection.collection.GSystem()
        thread_node.name = u"Thread of " + unicode(node.name)
        thread_node.status = u"PUBLISHED"
        thread_node.created_by = user_id
        thread_node.modified_by = user_id
        thread_node.contributors = [user_id]
        thread_node.prior_node = [node._id]
        thread_node.member_of = [ObjectId(twist_gst._id)]
        thread_node.group_set = [ObjectId(group_id)]
        thread_node.save()
        has_thread_gr = create_grelation(node._id, has_thread_rt, thread_node._id)

    # attributes for thread_node
    if start_time:
        start_time = datetime.strptime(start_time, "%d/%m/%Y")
    if end_time:
        end_time = datetime.strptime(end_time, "%d/%m/%Y")
    if release_response_val:
        release_response_val = eval(release_response_val)
        create_gattribute(thread_node._id, 'release_response', release_response_val)
    if not interaction_type_val:
        interaction_type_val = unicode(DEFAULT_DISCUSSION_LABEL)
        create_gattribute(thread_node._id, 'thread_interaction_type', interaction_type_val)
    else:
        create_gattribute(thread_node._id, 'thread_interaction_type', interaction_type_val)

    if start_time and end_time:
        create_gattribute(thread_node._id, 'start_time', start_time)
        create_gattribute(thread_node._id, 'end_time', end_time)
    thread_node.reload()
    print "\n\n thread_obj", thread_node.attribute_set, "\n---\n"
    return thread_node


def create_thread_for_node(request, group_id, node):
    """
      Accepts:
       * ObjectId of group.
       * node - Page/File GSystem

      Actions:
       * Finds the thread_node associated with passed node.
       * Creates ATs release_response and thread_interaction_type for thread_node
       * If dates set for thread, created ATs start_time and end_time for thread_node
       * Creates RT has_thread between node and thread_node

      Returns:
        * Success - True/False
    """
    try:
        if request.method == "POST":
            release_response_val = unicode(request.POST.get("release_resp_sel",'True'))
            interaction_type_val = unicode(request.POST.get("interaction_type_sel", None))
            start_time = request.POST.get("thread_start_date", None)
            end_time = request.POST.get("thread_close_date", None)
            thread_node = create_thread(group_id, node, node.created_by, release_response_val, interaction_type_val, start_time, end_time)
            return thread_node
    except Exception as e:
        print "Something went wrong while creating thread node. ",e

def node_thread_access(group_id, node):
    """
      Accepts:
       * ObjectId of group.
       * node - Page/File GSystem

      Actions:
       * Finds the thread_node associated with passed node.
       * Validation for discussion based on start_time and end_time, if exists

      Returns:
       * thread_node - used in discussion.html
       * success (i.e True/False)
    """

    from gnowsys_ndf.ndf.templatetags.ndf_tags import get_relation_value, get_attribute_value

    has_thread_node = None
    discussion_enable_val = get_attribute_value(node._id,"discussion_enable")

    if not discussion_enable_val:
        return has_thread_node, discussion_enable_val

    thread_start_time = None
    thread_end_time = None
    allow_to_comment = True  # default set to True to allow commenting if no date is set for thread
    # has_thread_node_thread_grel = get_relation_value(node._id,"has_thread")
    grel_dict = get_relation_value(node._id,"has_thread", True)
    is_cursor = grel_dict.get("cursor",False)
    if not is_cursor:
        has_thread_node = grel_dict.get("grel_node")

    # if "has_thread" in node:
    #     if node['has_thread']:
    #             has_thread_node = node['has_thread'][0]
    if has_thread_node:
        has_thread_node = grel_dict['grel_node']
        thread_start_time = get_attribute_value(has_thread_node._id,"start_time")
        thread_end_time = get_attribute_value(has_thread_node._id,"end_time")
        # if has_thread_node_thread_grel[0].attribute_set:
        # if get_attribute_value(has_thread_node_thread_grel[0]._id,"start_time")
            # for each_attr in has_thread_node_thread_grel[0].attribute_set:
            #     if each_attr and 'start_time' in each_attr:
            #         thread_start_time = each_attr['start_time']
            #     if each_attr and 'end_time' in each_attr:
            #         thread_end_time = each_attr['end_time']
    else:
        allow_to_comment = False
    if thread_start_time and thread_end_time:
        curr_date_time = datetime.now()
        if curr_date_time.date() < thread_start_time.date() or curr_date_time.date() > thread_end_time.date():
            allow_to_comment = False
    return has_thread_node,allow_to_comment

def get_prior_node_hierarchy(oid):
    """pass the node's ObjectId and get list of objects in hierarchy

    Args:
        oid (TYPE): mongo ObjectId

    Returns:
        list: List of objects starts from passed node till top node
    """
    hierarchy_list = []
    prev_obj_id = ObjectId(oid)

    while prev_obj_id:
        try:
            prev_obj = node_collection.one({'_id': prev_obj_id})
            prev_obj_id = prev_obj.prior_node[0]
            # print prev_obj.name

        except:
            # print "===", prev_obj.name
            prev_obj_id = None

        finally:
            hierarchy_list.append(prev_obj)

    return hierarchy_list


def get_language_tuple(lang):
    """
    from input argument of language code of language name
    get the std matching tuple from settings.

    Returns:
        tuple: (<language code>, <language name>)

    Args:
        lang (str or unicode): it is the one of item from tuple.
        It may either language-code or language-name.
    """
    if not lang:
        return ('en', 'English')

    all_languages = list(LANGUAGES) + OTHER_COMMON_LANGUAGES

    # check if lang argument itself is a complete, valid tuple that exists in all_languages.
    if (lang in all_languages) or (tuple(lang) in all_languages):
        return lang

    all_languages_concanated = reduce(lambda x, y: x+y, all_languages)

    # iterating over each document in the cursor:
    # - Secondly, replacing invalid language values to valid tuple from settings
    if lang in all_languages_concanated:
        for each_lang in all_languages:
            if lang in each_lang:
                return each_lang

    # as a default return: ('en', 'English')
    return ('en', 'English')

def get_filter_querydict(filters):
    """
    After getting the filters from request,
    this method converts it into mongo query-able.
    suitable form. Which can be passed to '$and'.

    Args:
        filter (JSON): It's a nested list of '$or' dicts.
        e.g:
        [{"$or":[{"selFieldValue":"educationallevel","selFieldValueAltnames":"Level","selFieldGstudioType":"attribute","selFieldText":"Upper Primary","selFieldPrimaryType":"list"},{"selFieldValue":"educationallevel","selFieldValueAltnames":"Level","selFieldGstudioType":"attribute","selFieldText":"Primary","selFieldPrimaryType":"list"}]},{"$or":[{"selFieldValue":"interactivitytype","selFieldValueAltnames":"interactivitytype","selFieldGstudioType":"attribute","selFieldText":"Expositive","selFieldPrimaryType":"basestring"}]}]



    Returns:
        JSON: JSON format which can be directly feed to query.
        e.g:
        [{}, {'$or': [{u'attribute_set.educationallevel': {'$in': [u'Upper Primary']}}, {u'attribute_set.educationallevel': {'$in': [u'Primary']}}, {u'attribute_set.interactivitytype': u'Expositive'}]}, {'$or': [{u'attribute_set.educationallevel': {'$in': [u'Upper Primary']}}, {u'attribute_set.educationallevel': {'$in': [u'Primary']}}, {u'attribute_set.interactivitytype': u'Expositive'}]}]
    """
    query_dict = []
    for each in filters:
          temp_list = []
          filter_grp = each["or"]
          for each_filter in filter_grp:
            temp_dict = {}
            each_filter["selFieldText"] = cast_to_data_type(each_filter["selFieldText"], each_filter["selFieldPrimaryType"])

            if each_filter["selFieldPrimaryType"] == unicode("list"):
              each_filter["selFieldText"] = {"$in": each_filter["selFieldText"]}

            if each_filter["selFieldGstudioType"] == "attribute":

              temp_dict["attribute_set." + each_filter["selFieldValue"]] = each_filter["selFieldText"]
              temp_list.append(temp_dict)
              # print "\n===temp_list : ", temp_list, "\===n"
            elif each_filter["selFieldGstudioType"] == "field":
              if each_filter["selFieldValue"] == 'Language':
                each_filter["selFieldValue"] = u'language'
                # print 'each_filter["selFieldText"]', each_filter["selFieldValue"]
                each_filter["selFieldText"] = get_language_tuple(each_filter["selFieldText"])
              if each_filter["selFieldValue"] == 'created_by':
                filter_username = each_filter["selFieldText"]
                filter_user_id = User.objects.get(username=filter_username).id
                each_filter["selFieldText"] = filter_user_id
              temp_dict[each_filter["selFieldValue"]] = each_filter["selFieldText"]
              temp_list.append(temp_dict)

          # print " ::: ",temp_list
          if temp_list:
            query_dict.append({ "$or": temp_list})

    return query_dict

def get_course_units_tree(data,list_ele):
    # print data
    if type(data) == list:
        for each_dict in data:
            # print type(each_dict)
            if type(each_dict) == dict:
                # print "each_dict",each_dict
                if each_dict['node_type']=="CourseSubSectionEvent":
                    if 'children' in each_dict:
                        list_ele.extend(each_dict['children'])
                else:
                    # print "\n each_dict---",each_dict
                    if "children" in each_dict:
                        get_course_units_tree(each_dict['children'],list_ele)

def create_clone(user_id, node, group_id, mem_of_node_id=None):
    try:
        cloned_copy = node.copy()
        cloned_copy['_id'] = ObjectId()
        cloned_copy['group_set'] = [group_id]
        cloned_copy['status'] = u"PUBLISHED"
        cloned_copy['modified_by'] = int(user_id)
        cloned_copy['created_by'] = int(user_id)
        # cloned_copy['prior_node'] = node.prior_node
        cloned_copy['contributors'] = [int(user_id)]
        cloned_copy['post_node'] = []
        cloned_copy['collection_set'] = []
        cloned_copy['prior_node'] = []
        cloned_copy['relation_set'] = []
        # Avoid resetting attribbute_set.
        # cloned_copy['attribute_set'] = []
        cloned_copy['origin'] = [{'fork_of': node._id}]
        if mem_of_node_id:
            cloned_copy['member_of'] = [ObjectId(mem_of_node_id)]
        if "QuizItem" in node.member_of_names_list:
            quiz_item_event_gst = node_collection.one({'_type': "GSystemType", 'name': "QuizItemEvent"})
            cloned_copy['member_of'] = [quiz_item_event_gst._id]
        cloned_obj_id = node_collection.collection.insert(cloned_copy)
        cloned_obj = node_collection.one({'_id': ObjectId(cloned_obj_id)})
        cloned_obj.save(groupid=group_id, validate=False)
        return cloned_obj

    except Exception as re_clone_err:
        print re_clone_err
        print "Failed cloning resource"
        return None

@get_execution_time
def clone_triple(node_obj, triple_obj, group_id, user_id, override_AT_with=None, grelation=False):
    try:
        cloned_copy = triple_obj.copy()
        cloned_copy['_id'] = ObjectId()
        cloned_copy['subject'] = node_obj._id
        if grelation:
            if isinstance(triple_obj.right_subject, ObjectId):
                right_subj_node = node_collection.one({'_id': ObjectId(triple_obj.right_subject)})
                right_sub_new_node = create_clone(user_id, right_subj_node, group_id)
                pull_triples(source_node=right_subj_node, target_node=right_sub_new_node, 
                                group_id=group_id, user_id=user_id)
                cloned_copy['right_subject'] = right_sub_new_node._id

            if isinstance(triple_obj.right_subject, list):
                cloned_rs_ids = []
                for rs_id in triple_obj.right_subject:
                    right_subj_node = node_collection.one({'_id': ObjectId(rs_id)})
                    right_sub_new_node = create_clone(user_id, right_subj_node, group_id)
                    pull_triples(source_node=right_subj_node, target_node=right_sub_new_node, 
                                group_id=group_id, user_id=user_id)
                    cloned_rs_ids.append(right_sub_new_node._id)
                if cloned_rs_ids:
                    cloned_copy['right_subject'] = cloned_rs_ids
        else:
            if override_AT_with:
                cloned_copy['attribute_type'] = node_collection.one({
                    '_type': 'AttributeType', 'name': override_AT_with})._id
        cloned_obj_id = triple_collection.collection.insert(cloned_copy)
        cloned_obj = triple_collection.one({'_id': ObjectId(cloned_obj_id)})
        cloned_obj.save(groupid=group_id, validate=False)
    except Exception as clone_triple_err:
        # print "\n!!!Error while cloning Triple instance.!!! ", clone_triple_err 
        pass

@get_execution_time
def pull_triples(source_node, target_node, group_id, user_id):
    # - katkamrachana , 18May2017.
    # Fetching triples irrespective of status, 
    # since we will create a clone of triple object.
    # GAttributes
    # print "\n Pulling Triples---------"
    node_gattr_cur = triple_collection.find({'_type': 'GAttribute', 'subject': source_node._id})
    # print "\n GA: ", node_gattr_cur.count()
    for each_gattr in node_gattr_cur:
        override_AT_with = None
        if each_gattr.attribute_type == player_disc_enable_at_id:
            override_AT_with = "discussion_enable" 
        cloned_gattr = clone_triple(node_obj=target_node, triple_obj=each_gattr,
                            group_id=group_id, user_id=user_id, override_AT_with=override_AT_with)

    # GRelations
    node_grel_cur = triple_collection.find({'_type': 'GRelation', 'subject': source_node._id})
    # print "\n GR: ", node_grel_cur.count()
    for each_grel in node_grel_cur:
        cloned_grel = clone_triple(node_obj=target_node, triple_obj=each_grel,
                            group_id=group_id, user_id=user_id, grelation=True)

@get_execution_time
def replicate_resource(request, node, group_id, mem_of_node_id=None):
    try:
        create_thread_for_node_flag = True
        if request:
            user_id = request.user.id
        else:
            user_id = 1
        new_gsystem = create_clone(user_id, node, group_id, mem_of_node_id=mem_of_node_id)

        if new_gsystem:
            # FORKING TRIPLES

            ##### TRIPLES GATTRIBUTES
            pull_triples(source_node=node, target_node=new_gsystem, 
                            group_id=group_id, user_id=user_id)
        if "QuizItem" in node.member_of_names_list or "QuizItemEvent" in node.member_of_names_list:
            from gnowsys_ndf.ndf.templatetags.ndf_tags import get_thread_node
            thread_obj = get_thread_node(new_gsystem._id)
            if not thread_obj:
                thread_obj = create_thread_for_node(request,group_id, new_gsystem)
        return new_gsystem
    except Exception as replicate_resource_err:
        print replicate_resource_err
        print "Failed replicating resource"
        return None

@get_execution_time
def dig_nodes_field(parent_node, field_name="collection_set", 
    only_leaf_nodes=False, member_of=None, list_of_node_ids = []):
  '''
  This function fetches list of ObjectIds by
  digging into the node's field_name and
  the result's field_name recursively.

  'field_name' can be collection_set/prior_node/post_node etc.
  'member_of' is a list of GST names e.g ['Page', 'File']

  If 'only_leaf_nodes' is True, the leaf nodes will be fetched,
  i.e the nodes not having any value in their said field_name

  To invoke this function:
    result = dig_nodes_field(node_obj)/
    result = dig_nodes_field(node_obj,'collection_set')/
    result = dig_nodes_field(node_obj,'collection_set',True)/
    empty_list = []
    result = dig_nodes_field(node_obj,'collection_set',True,empty_list)/
    result = dig_nodes_field(node_obj,'collection_set',True,test_list,['Page'])/
    result = dig_nodes_field(node_obj,'collection_set',True,test_list,['Page','File])
  '''
  # print "\n\n Node name -- ", parent_node.name, "-- ",parent_node[field_name]

  for each_id in parent_node[field_name]:
    if each_id not in list_of_node_ids:
      each_obj = node_collection.one({'_id': ObjectId(each_id)})
      # print "each_obj--",each_obj._id, " -- ", each_obj.name, " - - ", each_obj.member_of_names_list, "=== ", member_of
      member_of_match = True
      if member_of:
        member_of_match = False
        member_of_match = [each_ele for each_ele in member_of if each_ele in each_obj.member_of_names_list]
        # print "member_of_match",member_of_match
      if member_of_match and each_id not in list_of_node_ids:
        # print "File Found", len(each_obj[field_name])
        if only_leaf_nodes:
          if not each_obj[field_name]:
            list_of_node_ids.append(each_id)
          else:
            dig_nodes_field(each_obj, field_name,only_leaf_nodes, member_of, list_of_node_ids)
        else:
            list_of_node_ids.append(each_id)


  # print "\n len(list_of_node_ids) -- ",len(list_of_node_ids)
  return list_of_node_ids

def sublistExists(parent_list, child_list):
    # print "\n parent_list == ",parent_list
    # print "\n child_list == ",child_list
    if parent_list and child_list:
      exists = all(each_item in parent_list for each_item in child_list)
      return exists
    return False

def get_course_completed_ids(list_of_all_ids,children_ids,return_completed_list,return_incompleted_list):
    completed = return_completed_list
    incompleted = return_incompleted_list
    # children_ids_list = children_ids
    children_ids_list = []
    all_nodes = node_collection.find({'_id': {'$in': list_of_all_ids}},
      {'name':1, 'collection_set':1, '_id': 1, 'member_of': 1,'created_at':1}).sort('created_at',-1)

    for eachnode in all_nodes:
      # print "\n eachnode.name --- ",eachnode.name , eachnode.member_of_names_list
      if sublistExists(children_ids, eachnode.collection_set):
        completed.append(eachnode._id)
        children_ids_list.append(eachnode._id)
        if eachnode._id in incompleted:
          incompleted.remove(eachnode._id)
      else:
        incompleted.append(eachnode._id)
    # print "\n\n completed_ids_list 1--- ", completed
    # print "\n\n incompleted_ids_list1 --- ", incompleted
    if children_ids_list:
      get_course_completed_ids(list_of_all_ids,children_ids_list,completed,incompleted)

    return completed, incompleted

@get_execution_time
def get_group_join_status(group_obj):
    from gnowsys_ndf.ndf.templatetags.ndf_tags import get_attribute_value
    allow_to_join = None
    start_enrollment_date = get_attribute_value(group_obj._id,"start_enroll")
    last_enrollment_date = get_attribute_value(group_obj._id,"end_enroll")
    curr_date_time = datetime.now().date()

    if start_enrollment_date and last_enrollment_date:
      start_enrollment_date = start_enrollment_date.date()
      last_enrollment_date = last_enrollment_date.date()
      if start_enrollment_date <= curr_date_time and last_enrollment_date >= curr_date_time:
          allow_to_join = "Open"
      else:
          allow_to_join = "Closed"
    return allow_to_join

@get_execution_time
def get_course_completetion_status(group_obj, user_id,ids_list=False):
    result_dict = {'success': False}
    try:
      user_obj = User.objects.get(pk=int(user_id))
      '''
      for cs in group_obj.collection_set:
        cs_node = node_collection.one({'_id': ObjectId(cs)})
        all_node_ids.append(cs_node._id)
        if cs_node:
          all_cs_count = all_cs_count + 1
          for css in cs_node.collection_set:
            css_node = node_collection.one({'_id': ObjectId(css)})
            all_node_ids.append(css_node._id)
            if css_node:
              for cu in css_node.collection_set:
                cu_node = node_collection.one({'_id': ObjectId(cu)})
                all_node_ids.append(cu_node._id)
                if cu_node:
                  for res in cu_node.collection_set:
                    all_node_ids.append(res)
                    # res_node = node_collection.one({'_id': ObjectId(res)})
                    b = benchmark_collection.find({'name': "course_resource_detail",
                        'calling_url': {'$regex': '/'+unicode(res)+'/$'},
                        'user': user_obj.username
                        })
                    if b.count():
                      completed_cs_count = completed_cs_count + 1
                      res_completed_ids.append(res)
                      completed_ids.append(res)
                    # else:
                    #   incompleted_ids.append(res)
                  if all(each_item in completed_ids for each_item in cu_node.collection_set):
                    completed_ids.append(cu_node._id)
                  else:
                    partially_exists = any(each_id in completed_ids for each_id in cu_node.collection_set)
                    if partially_exists:
                      incompleted_ids.append(cu_node._id)

              if all(each_item in completed_ids for each_item in css_node.collection_set):
                completed_ids.append(css_node._id)
              else:
                partially_exists = any(each_id in completed_ids for each_id in css_node.collection_set)
                if partially_exists or all(each_item in incompleted_ids for each_item in css_node.collection_set):
                  incompleted_ids.append(css_node._id)

          if all(each_item in completed_ids for each_item in cs_node.collection_set):
            completed_ids.append(cs_node._id)
          else:
            partially_exists = any(each_id in completed_ids for each_id in cs_node.collection_set)
            if partially_exists or all(each_item in incompleted_ids for each_item in cs_node.collection_set):
              incompleted_ids.append(cs_node._id)
      '''


      all_res = set()
      regex_res_ids = ''
      completed_unit_ids = []
      unit_event_gst = node_collection.one({'_type':"GSystemType", 'name':"CourseUnitEvent"})
      cs_event_gst = node_collection.one({'_type':"GSystemType", 'name':"CourseSectionEvent"})
      css_event_gst = node_collection.one({'_type':"GSystemType", 'name':"CourseSubSectionEvent"})

      all_units_of_grp = node_collection.find({'member_of': unit_event_gst._id,'group_set': group_obj._id})
      all_sessions_of_grp = node_collection.find({'member_of': css_event_gst._id,'group_set': group_obj._id})
      all_modules_of_grp = node_collection.find({'member_of': cs_event_gst._id,'group_set': group_obj._id})

      unit_info_before_query = {}
      for each in all_units_of_grp:
        all_res.update(each.collection_set)
        unit_info_before_query.update({unicode(each._id): set(map(unicode,each.collection_set))})

      for each_res in all_res:
        regex_res_ids += '/'+each_res.__str__()+'/$|'
      regex_res_ids = regex_res_ids[:-1]
      benchmark_res = benchmark_collection.find({'name':"course_resource_detail", 'calling_url': {'$regex': regex_res_ids}, 'user': user_obj.username, 'group': unicode(group_obj._id)},{'_id':0,'calling_url':1})

      unit_info_after_query = {}
      for each_benchmark in benchmark_res:
        calling_url_split = each_benchmark['calling_url'].split('/')
        if len(calling_url_split) > 5:
          if calling_url_split[5] in unit_info_after_query.keys():
            val = unit_info_after_query[unicode(calling_url_split[5])]
          else:
            val = set()
          val.add(calling_url_split[6])
          unit_info_after_query.update({unicode(calling_url_split[5]):val})

      for each_unit in unit_info_after_query:
        if each_unit in unit_info_before_query:
          if unit_info_after_query[each_unit] == unit_info_before_query[each_unit]:
            completed_unit_ids.append(ObjectId(each_unit))
      completed_sessions_ids_final = []
      completed_units_cur = node_collection.find({'_id': {'$in': completed_unit_ids}},{'_id':0, 'prior_node':1})
      completed_sessions_ids = [each_completed_unit_node.prior_node[0] for each_completed_unit_node in completed_units_cur]
      completed_sessions_cur = node_collection.find({'_id': {'$in': completed_sessions_ids},'member_of': css_event_gst._id})

      for each_session in completed_sessions_cur:
        if all(each_u_id in completed_unit_ids for each_u_id in each_session.collection_set):
          completed_sessions_ids_final.append(each_session._id)

      completed_sessions_cur_final = node_collection.find({'_id': {'$in': completed_sessions_ids_final},'member_of': css_event_gst._id})
      completed_modules_ids = [each_completed_session_node.prior_node[0] for each_completed_session_node in completed_sessions_cur_final]
      completed_modules_cur = node_collection.find({'_id': {'$in': completed_modules_ids},'member_of': cs_event_gst._id})
      completed_modules = []
      for each_module in completed_modules_cur:
        if all(each_m_id in completed_sessions_ids_final for each_m_id in each_module.collection_set):
          completed_modules.append(each_module._id)


      # print "\nTotal modules : ", all_modules_of_grp.count()
      # print "\nCompleted modules : ", len(completed_modules_ids)

      # print "\nTotal Units : ", all_units_of_grp.count()
      # print "\nCompleted Units : ", len(completed_unit_ids)

      return_perc = (len(completed_modules_ids)/float(all_modules_of_grp.count()))*100

      # print "\n\n return_perc==== ",return_perc
      result_dict['course_complete_percentage'] = return_perc
      result_dict['modules_completed_count'] = completed_modules_cur.count()
      result_dict['modules_total_count'] = all_modules_of_grp.count()
      result_dict['units_completed_count'] = completed_units_cur.count()
      result_dict['units_total_count'] = all_units_of_grp.count()


      result_dict.update({'success': False})
      # print "\n\nresult_dict == ",result_dict
      return result_dict
    except Exception as error_in_get_course_completion_status:
      # print "\n ERROR in get_course_completetion_status", error_in_get_course_completion_status
      return result_dict

def get_all_iframes_of_unit(group_obj, domain):
    # tuple : [[assessment.Bank<id>, assessment.Offered<id>],
    # [assessment.Bank<id>, assessment.Offered<id>]]
    # ref: https://docs.python.org/2.7/library/urlparse.html#urlparse.parse_qsl
    from bs4 import BeautifulSoup
    result_set = []
    assessment_str = "assessment.Bank"
    group_id  = group_obj._id
    try:
        gst_page_name, gst_page_id = GSystemType.get_gst_name_id("Page")
        gst_wiki_page_name, gst_wiki_page_id = GSystemType.get_gst_name_id("Wiki page")

        # Fech all pages having assessments embedded into it
        pages_holding_assessments_cur = node_collection.find({
                    'group_set': ObjectId(group_id),
                    'member_of': gst_page_id,
                    'type_of': {'$ne': gst_wiki_page_id},
                    'content': {'$regex': assessment_str, '$options': "i"}
            })


        # From each page's content collect the assessment iframe
        for each_node in pages_holding_assessments_cur:
            all_iframes = BeautifulSoup(
                each_node.content, 'html.parser').find_all(
                'iframe',src=re.compile(assessment_str)
            )
            for each_iframe in all_iframes:
                try:
                    bank_offered_id = parse_assessment_url(each_iframe["src"])
                    if bank_offered_id not in result_set:
                        result_set.append(bank_offered_id)
                except Exception as iframe_update_err:
                    print "\nError Occurred in calling parse_assessment_url() {0}".format(
                        iframe_update_err)
                    pass
        '''
        AT: "assessment_list" will hold `result_set = [[a,b], [x,y]]`
            where 'a' and 'x' represent bank id &
            where 'b' and 'y' represent assessment_offered_id
        '''
        if result_set:
            create_gattribute(group_id, "assessment_list", result_set)
            group_obj.reload()
            # print "\nresult_set: ", result_set
            update_total_assessment_items(group_id, result_set, domain)
            group_obj.reload()
    except Exception as get_all_iframes_of_unit_err:
        print "\nError Occurred in get_all_iframes_of_unit() {0}".format(
            get_all_iframes_of_unit_err)
        pass

    return group_obj

def parse_assessment_url(url_as_str):
    import urlparse
    bank_offered_id = [None,None]
    try:
        parsed_src = urlparse.urlparse(url_as_str)
        get_params = urlparse.parse_qsl(parsed_src.query)
        # print "\nget_params: ", get_params
        for param in get_params:
            if 'bank' in param[0]:
                bank_offered_id[0] = param[1]
            if 'assessment_offered_id' in param[0]:
                bank_offered_id[1] = param[1]
        return bank_offered_id
    except Exception as iframe_update_err:
        print "\nError Occurred in parse_assessment_url() {0}".format(
            iframe_update_err)
        return bank_offered_id

def update_total_assessment_items(group_id, assessment_list, domain):
    from gnowsys_ndf.ndf.views.assessment_analytics import items_count_from_asessment_offered
    import urllib
    questionCount_val = 0
    try:
        for each_assessment_list in assessment_list:
            items_count = items_count_from_asessment_offered(domain,each_assessment_list[0],each_assessment_list[1])
            questionCount_val = questionCount_val + items_count
            print "\nquestionCount_val: ", questionCount_val

        '''
        AT: "total_assessment_items" will hold `questionCount_val = x`
            where 'x' represent count of questions
        '''

        print "\nAC: ", questionCount_val
        create_gattribute(group_id, "total_assessment_items", questionCount_val)
        return questionCount_val
    except Exception as update_total_assessment_items_err:
        print "\nError Occurred in update_total_assessment_items() {0}".format(
            update_total_assessment_items_err)
        return questionCount_val

@get_execution_time
def update_unit_in_modules(module_val, unit_id):
    gst_module_name, gst_module_id = GSystemType.get_gst_name_id('Module')
    # get all modules which are parent's of this unit/group
    parent_modules = node_collection.find({
            '_type': 'GSystem',
            'member_of': gst_module_id,
            'collection_set': {'$in': [unit_id]}
        })
    # check for any mismatch in parent_modules and module_val
    if parent_modules or module_val:
        # import ipdb; ipdb.set_trace()
        module_oid_list = [ObjectId(m) for m in module_val if m]
        parent_modules_oid_list = [o._id for o in parent_modules]

        # summing all ids to iterate over
        oids_set = set(module_oid_list + parent_modules_oid_list)

        for each_oid in oids_set:
            if each_oid not in module_oid_list:
                # it is an old module existed with curent unit.
                # remove current node's id from it's collection_set
                # existing deletion
                each_node_obj = Node.get_node_by_id(each_oid)
                each_node_obj_cs = each_node_obj.collection_set
                each_node_obj_cs.pop(each_node_obj_cs.index(unit_id))
                each_node_obj.collection_set = each_node_obj_cs
                each_node_obj.save(group_id=unit_id)
            elif each_oid not in parent_modules_oid_list:
                # if this id does not exists with existing parent's id list
                # then add current node_id in collection_set of each_oid.
                # new addition
                each_node_obj = Node.get_node_by_id(each_oid)
                if unit_id not in each_node_obj.collection_set:
                    each_node_obj.collection_set.append(unit_id)
                    each_node_obj.save(group_id=unit_id)

@get_execution_time
def add_to_author_set(group_id, user_id, add_admin=False):
    def _update_user_counter(userid, group_id):
        counter_obj = Counter.get_counter_obj(userid, ObjectId(group_id))
        counter_obj['is_group_member'] = True
        counter_obj.save()

    group_obj = get_group_name_id(group_id, get_obj=True)
    if group_obj:
        try:
            if add_admin:
                if isinstance(user_id, list):
                    non_admin_user_ids = [each_userid for each_userid in user_id if each_userid not in group_obj.group_admin ]
                    if non_admin_user_ids:
                        group_obj.group_admin.extend(non_admin_user_ids)
                        group_obj.group_admin = list(set(group_obj.group_admin))
                else:
                    if user_id not in group_obj.group_admin:
                        group_obj.group_admin.append(user_id)
            else:
                if isinstance(user_id, list):
                    non_member_user_ids = [each_userid for each_userid in user_id if each_userid not in group_obj.author_set ]
                    if non_member_user_ids:
                        group_obj.author_set.extend(non_member_user_ids)
                        group_obj.author_set = list(set(group_obj.author_set))
                else:
                    if user_id not in group_obj.author_set:
                        group_obj.author_set.append(user_id)
            group_obj.save()

            if 'Group' not in group_obj.member_of_names_list:
                # get new/existing counter document for a user for a given course for the purpose of analytics
                if isinstance(user_id, list):
                    for each_user_id in user_id:
                        _update_user_counter(each_user_id, group_obj._id)
                else:
                    _update_user_counter(user_id, group_obj._id)
            # print "\n Added to author_set"
        except Exception as e:
            pass
        return group_obj
    pass

@get_execution_time
def auto_enroll(f):
    def wrap(*args,**kwargs):

        ret = f(*args,**kwargs)
        if GSTUDIO_IMPLICIT_ENROLL:
            group_id = kwargs.get("group_id", None)
            user_id = None
            request = args[0] if len(args) else None
            if request and isinstance(request, WSGIRequest):
                user_id = [request.user.id]
                if GSTUDIO_BUDDY_LOGIN:
                    user_id += Buddy.get_buddy_userids_list_within_datetime(request.user.id,
                                         datetime.now())
            else:
                user_id = kwargs.get("user_id", None)
                if not user_id:
                    user_id = kwargs.get("created_by", None)

            if user_id and group_id:
                add_to_author_set(group_id=group_id, user_id=user_id)
        return ret
    return wrap

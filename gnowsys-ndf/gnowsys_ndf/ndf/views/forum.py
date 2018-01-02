''' -- imports from installed packages -- '''
import json
import datetime

''' -- imports from django -- '''
from django.shortcuts import render_to_response, render
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from django.template import RequestContext
from django.template import Context
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required

''' -- imports from django_mongokit -- '''

''' -- imports from gstudio -- '''
from gnowsys_ndf.ndf.models import GSystemType, GSystem,Node
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import get_forum_repl_type, forum_notification_status
from gnowsys_ndf.ndf.views.methods import set_all_urls,check_delete,get_execution_time
from gnowsys_ndf.ndf.views.methods import create_grelation
from gnowsys_ndf.ndf.views.methods import get_group_name_id, capture_data
from gnowsys_ndf.ndf.views.notify import set_notif_val,get_userobject
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_forum_twists,get_all_replies
from gnowsys_ndf.settings import GAPPS
import StringIO
import sys
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

# ##########################################################################

forum_gst = node_collection.one({ '_type': 'GSystemType', 'name': u"Forum" })
reply_gst = node_collection.one({ '_type':'GSystemType' , 'name': u'Reply' })
twist_gst = node_collection.one({ '_type':'GSystemType', 'name': u'Twist' })

start_time = node_collection.one({'$and':[{'_type':'AttributeType'},{'name':'start_time'}]})
end_time = node_collection.one({'$and':[{'_type':'AttributeType'},{'name':'end_time'}]})
sitename = Site.objects.all()[0].name.__str__()

app = forum_gst


@get_execution_time
def forum(request, group_id, node_id=None):
    '''
    Method to list all the available forums and to return forum-search-query result.
    '''
    # print "\n\n\n inside forum"
    # getting group id and group name
    group_name, group_id = get_group_name_id(group_id)

    # getting Forum GSystem's ObjectId
    node_id = str(forum_gst._id)

    if request.method == "POST":
        # Forum search view
        title = forum_gst.name

        search_field = request.POST['search_field']
        existing_forums = node_collection.find({'member_of': {'$all': [ObjectId(forum_gst._id)]},
                                         '$or': [{'name': {'$regex': search_field, '$options': 'i'}},
                                                 {'tags': {'$regex':search_field, '$options': 'i'}}],
                                         'group_set': {'$all': [ObjectId(group_id)]},
                                     'status':{'$nin':['HIDDEN']}
                                     }).sort('last_update', -1)

        return render_to_response("ndf/forum.html",
                                {'title': title,
                                 'searching': True, 'query': search_field,
                                 'existing_forums': existing_forums, 'groupid':group_id, 'group_id':group_id
                                },
                                context_instance=RequestContext(request)
        )

    elif forum_gst._id == ObjectId(node_id):
        # Forum list view

        existing_forums = node_collection.find({
                                            'member_of': {'$all': [ObjectId(node_id)]},
                                            'group_set': {'$all': [ObjectId(group_id)]},
                                            'status':{'$nin':['HIDDEN']}
                                            }).sort('last_update', -1)
        forum_detail_list = []
        '''
        for each in existing_forums:

            temp_forum = {}
            temp_forum['name'] = each.name
            temp_forum['created_at'] = each.created_at
            temp_forum['created_by'] = each.created_by
            temp_forum['tags'] = each.tags
            temp_forum['member_of_names_list'] = each.member_of_names_list
            temp_forum['user_details_dict'] = each.user_details_dict
            temp_forum['html_content'] = each.html_content
            temp_forum['contributors'] = each.contributors
            temp_forum['id'] = each._id
            temp_forum['threads'] = node_collection.find({
                                                        '$and':[
                                                                {'_type': 'GSystem'},
                                                                {'prior_node': ObjectId(each._id)}
                                                                ],
                                                        'status': {'$nin': ['HIDDEN']}
                                                        }).count()

            forum_detail_list.append(temp_forum)
        print "\n\n\n forum detail list",forum_detail_list'''
        variables = RequestContext(request, {'existing_forums':existing_forums ,'groupid': group_id, 'group_id': group_id})

        return render_to_response("ndf/forum.html",variables)


@login_required
@get_execution_time
def create_forum(request, group_id):
    '''
    Method to create forum and Retrieve all the forums
    '''

    # getting group id and group name
    group_name, group_id = get_group_name_id(group_id)

    # getting all the values from submitted form
    if request.method == "POST":

        colg = node_collection.one({'_id':ObjectId(group_id)}) # getting group ObjectId

        colf = node_collection.collection.GSystem() # creating new/empty GSystem object

        name = unicode(request.POST.get('forum_name',"")).strip() # forum name
        colf.name = name

        content_org = request.POST.get('content_org',"") # forum content
        if content_org:
            colf.content_org = unicode(content_org)
            usrname = request.user.username
            filename = slugify(name) + "-" + usrname + "-"
            colf.content = content_org

        usrid = int(request.user.id)
        usrname = unicode(request.user.username)

        colf.created_by=usrid
        colf.modified_by = usrid

        if usrid not in colf.contributors:
            colf.contributors.append(usrid)

        colf.group_set.append(colg._id)

        # appending user group's ObjectId in group_set
        user_group_obj = node_collection.one({'$and':[{'_type':u'Group'},{'name':usrname}]})
        if user_group_obj:
            if user_group_obj._id not in colf.group_set:
                colf.group_set.append(user_group_obj._id)

        colf.member_of.append(forum_gst._id)
        ################# ADDED 14th July.Its done!
        colf.access_policy = u"PUBLIC"
        colf.url = set_all_urls(colf.member_of)

        ### currently timed forum feature is not in use ###
        # sdate=request.POST.get('sdate',"")
        # shrs= request.POST.get('shrs',"")
        # smts= request.POST.get('smts',"")

        # edate= request.POST.get('edate',"")
        # ehrs= request.POST.get('ehrs',"")
        # emts=request.POST.get('emts',"")

        # start_dt={}
        # end_dt={}

        # if not shrs:
        #     shrs=0
        # if not smts:
        #     smts=0
        # if sdate:
        #     sdate1=sdate.split("/")
        #     st_date = datetime.datetime(int(sdate1[2]),int(sdate1[0]),int(sdate1[1]),int(shrs),int(smts))
        #     start_dt[start_time.name]=st_date

        # if not ehrs:
        #     ehrs=0
        # if not emts:
        #     emts=0
        # if edate:
        #     edate1=edate.split("/")
        #     en_date= datetime.datetime(int(edate1[2]),int(edate1[0]),int(edate1[1]),int(ehrs),int(emts))
        #     end_dt[end_time.name]=en_date
       # colf.attribute_set.append(start_dt)
       # colf.attribute_set.append(end_dt)
        colf.save(groupid=group_id)

        '''Code to send notification to all members of the group except those whose notification preference is turned OFF'''
        try:
            link="http://"+sitename+"/"+str(colg._id)+"/forum/"+str(colf._id)
            for each in colg.author_set:
                bx=User.objects.filter(id=each)
                if bx:
                    bx=User.objects.get(id=each)
                else:
                    continue
                activity="Added forum"
                msg=usrname+" has added a forum in the group -'"+colg.name+"'\n"+"Please visit "+link+" to see the forum."
                if bx:
                    auth = node_collection.one({'_type': 'Author', 'name': unicode(bx.username) })
                    if colg._id and auth:
                        no_check=forum_notification_status(colg._id,auth._id)
                    else:
                        no_check=True
                    if no_check:
                        ret = set_notif_val(request,colg._id,msg,activity,bx)
        except Exception as e:
            print e

        # returning response to ndf/forumdetails.html
        return HttpResponseRedirect(reverse('show', kwargs={'group_id':group_id,'forum_id': colf._id }))

        # variables=RequestContext(request,{'forum':colf})
        # return render_to_response("ndf/forumdetails.html",variables)

    # getting all the GSystem of forum to provide autocomplete/intellisence of forum names
    available_nodes = node_collection.find({'_type': u'GSystem', 'member_of': ObjectId(forum_gst._id),'group_set': ObjectId(group_id) })

    nodes_list = []
    for each in available_nodes:
      nodes_list.append(str((each.name).strip().lower()))

    return render_to_response("ndf/create_forum.html",{'group_id':group_id,'groupid':group_id, 'nodes_list': nodes_list},RequestContext(request))


@login_required
@get_execution_time
def edit_forum(request,group_id,forum_id):
    '''
    Method to create forum and Retrieve all the forums
    '''
    forum = node_collection.one({ '_id': ObjectId(forum_id) })

    # # method to convert group_id to ObjectId if it is groupname
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

    group_name, group_id = get_group_name_id(group_id)

    # getting all the values from submitted form
    if request.method == "POST":

        colg = node_collection.one({'_id':ObjectId(group_id)}) # getting group ObjectId

        colf = node_collection.one({'_id':ObjectId(forum_id)}) # creating new/empty GSystem object

        name = unicode(request.POST.get('forum_name',"")).strip() # forum name
        colf.name = name

        content_org = request.POST.get('content_org',"") # forum content
        if content_org:
            colf.content_org = unicode(content_org)
            usrname = request.user.username
            filename = slugify(name) + "-" + usrname + "-"
            colf.content = content_org

        usrid = int(request.user.id)
        usrname = unicode(request.user.username)

        colf.modified_by = usrid

        if usrid not in colf.contributors:
            colf.contributors.append(usrid)


        ################# ADDED 14th July.Its done!
        colf.access_policy = u"PUBLIC"
        colf.url = set_all_urls(colf.member_of)

        ### currently timed forum feature is not in use ###
        # sdate=request.POST.get('sdate',"")
        # shrs= request.POST.get('shrs',"")
        # smts= request.POST.get('smts',"")

        # edate= request.POST.get('edate',"")
        # ehrs= request.POST.get('ehrs',"")
        # emts=request.POST.get('emts',"")

        # start_dt={}
        # end_dt={}

        # if not shrs:
        #     shrs=0
        # if not smts:
        #     smts=0
        # if sdate:
        #     sdate1=sdate.split("/")
        #     st_date = datetime.datetime(int(sdate1[2]),int(sdate1[0]),int(sdate1[1]),int(shrs),int(smts))
        #     start_dt[start_time.name]=st_date

        # if not ehrs:
        #     ehrs=0
        # if not emts:
        #     emts=0
        # if edate:
        #     edate1=edate.split("/")
        #     en_date= datetime.datetime(int(edate1[2]),int(edate1[0]),int(edate1[1]),int(ehrs),int(emts))
        #     end_dt[end_time.name]=en_date
       # colf.attribute_set.append(start_dt)
       # colf.attribute_set.append(end_dt)
        colf.save(groupid=group_id)
        '''Code to send notification to all members of the group except those whose notification preference is turned OFF'''
        try:
            link="http://"+sitename+"/"+str(colg._id)+"/forum/"+str(colf._id)
            for each in colg.author_set:
                bx=User.objects.get(id=each)
                activity="Edited forum"
                msg=usrname+" has edited forum -" +colf.name+" in the group -'"+colg.name+"'\n"+"Please visit "+link+" to see the forum."
                if bx:
                    auth = node_collection.one({'_type': 'Author', 'name': unicode(bx.username) })
                    if colg._id and auth:
                        no_check=forum_notification_status(colg._id,auth._id)
                    else:
                        no_check=True
                    if no_check:
                        ret = set_notif_val(request,colg._id,msg,activity,bx)

        except Exception as e:
            print e
        # returning response to ndf/forumdetails.html
        return HttpResponseRedirect(reverse('show', kwargs={'group_id':group_id,'forum_id': colf._id }))

        # variables=RequestContext(request,{'forum':colf})
        # return render_to_response("ndf/forumdetails.html",variables)

    # getting all the GSystem of forum to provide autocomplete/intellisence of forum names
    available_nodes = node_collection.find({'_type': u'GSystem', 'member_of': ObjectId(forum_gst._id),'group_set': ObjectId(group_id) })

    nodes_list = []
    for each in available_nodes:
      nodes_list.append(str((each.name).strip().lower()))

    return render_to_response("ndf/edit_forum.html",{'group_id':group_id,'groupid':group_id, 'nodes_list': nodes_list,'forum':forum},RequestContext(request))



@get_execution_time
def display_forum(request,group_id,forum_id):
    hide_create_thread_btn = True
    other_forums_list = None
    other_forums = node_collection.find({'member_of': forum_gst._id,'group_set': ObjectId(group_id),
                                        '_id':{'$nin':[ObjectId(forum_id)]}})
    if other_forums.count():
        other_forums_list = [[str(d._id), d.name] for d in other_forums]

    forum = node_collection.one({'_id': ObjectId(forum_id)})

    usrname = User.objects.get(id=forum.created_by).username

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

    forum_object = node_collection.one({'_id': ObjectId(forum_id)})
    if forum_object._type == "GSystemType":
       return forum(request, group_id, forum_id)
    th_all=get_forum_twists(forum)
    if th_all:
        th_count=len(list(th_all))
    else:
        th_count=0
    variables = RequestContext(request,{
                                        'forum':forum,
                                        'hide_create_thread_btn': hide_create_thread_btn,
                                        'groupid':group_id,'group_id':group_id,
                                        'forum_created_by':usrname,
                                        'other_forums': other_forums_list,
                                        'thread_count':th_count,
                                        })

    return render_to_response("ndf/forumdetails.html",variables)



@get_execution_time
def display_thread(request,group_id, thread_id, forum_id=None):
    '''
    Method to display thread and it's content
    '''
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     # auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
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

    try:
        other_threads_list = None
        thread = node_collection.one({'_id': ObjectId(thread_id)})
        other_threads = node_collection.find({'member_of': twist_gst._id, 'prior_node': thread.prior_node,
                                            '_id': {'$nin': [ObjectId(thread._id)]}})
        if other_threads.count():
            other_threads_list = [[str(d._id), d.name] for d in other_threads]
        rep_lst=get_all_replies(thread)
        lst_rep=list(rep_lst)
        if lst_rep:
            reply_count=len(lst_rep)
        else:
            reply_count=0
        forum = ""

        for each in thread.prior_node:
            forum=node_collection.one({'$and':[{'member_of': {'$all': [forum_gst._id]}},{'_id':ObjectId(each)}]})
            if forum:
                usrname = User.objects.get(id=forum.created_by).username
                variables = RequestContext(request,
                                            {   'forum':forum,
                                                'thread':thread,
                                                'groupid':group_id,
                                                'other_threads_list':other_threads_list,
                                                'group_id':group_id,
                                                'eachrep':thread,
                                                'user':request.user,
                                                'reply_count':reply_count,
                                                'forum_created_by':usrname
                                            })
                return render_to_response("ndf/thread_details.html",variables)
        usrname = User.objects.get(id=thread.created_by).username
        variables= RequestContext(request,
                                            {   'forum':thread,
                                                'thread':None,
                                                'groupid':group_id,
                                                'group_id':group_id,
                                                'other_threads_list':other_threads_list,
                                                'eachrep':thread,
                                                'user':request.user,
                                                'reply_count':reply_count,
                                                'forum_created_by':usrname
                                            })
        return render_to_response("ndf/thread_details.html",variables)
    except Exception as e:
        print "Exception in thread_details "+str(e)
        pass


@login_required
@get_execution_time
def create_thread(request, group_id, forum_id):
    '''
    Method to create thread
    '''

    forum = node_collection.one({'_id': ObjectId(forum_id)})

    # forum_data = {
    #                 'name':forum.name,
    #                 'content':forum.content,
    #                 'created_by':User.objects.get(id=forum.created_by).username
    #             }
    # print forum_data

    forum_threads = []
    exstng_reply = node_collection.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(forum._id)}],'status':{'$nin':['HIDDEN']}})
    exstng_reply.sort('created_at')
    for each in exstng_reply:
        forum_threads.append((each.name).strip().lower())

    if request.method == "POST":

        colg = node_collection.one({'_id':ObjectId(group_id)})

        name = unicode(request.POST.get('thread_name',""))
        content_org = request.POST.get('content_org',"")

        # -------------------
        colrep = node_collection.collection.GSystem()
        colrep.member_of.append(twist_gst._id)
        # ADDED ON 14th July
        colrep.access_policy = u"PUBLIC"
        colrep.url = set_all_urls(colrep.member_of)
        colrep.prior_node.append(forum._id)
        colrep.name = name
        if content_org:
            colrep.content_org = unicode(content_org)
            # Required to link temporary files with the current user who is modifying this document
            usrname = request.user.username
            filename = slugify(name) + "-" + usrname + "-"
            colrep.content = content_org

        usrid = int(request.user.id)
        colrep.created_by = usrid
        colrep.modified_by = usrid

        if usrid not in colrep.contributors:
            colrep.contributors.append(usrid)

        colrep.group_set.append(colg._id)
        colrep.save(groupid=group_id)
        has_thread_rt = node_collection.one({"_type": "RelationType", "name": u"has_thread"})
        gr = create_grelation(forum._id, has_thread_rt, [colrep._id])

        try:
            '''Code to send notification to all members of the group except those whose notification preference is turned OFF'''
            link="http://"+sitename+"/"+str(colg._id)+"/forum/thread/"+str(colrep._id)
            for each in colg.author_set:
                bx=User.objects.filter(id=each)
                if bx:
                    bx=User.objects.get(id=each)
                else:
                    continue
                activity="Added thread"
                msg=request.user.username+" has added a thread in the forum " + forum.name + " in the group -'" + colg.name+"'\n"+"Please visit "+link+" to see the thread."
                if bx:
                    auth = node_collection.one({'_type': 'Author', 'name': unicode(bx.username) })
                    if colg._id and auth:
                        no_check=forum_notification_status(colg._id,auth._id)
                    else:
                        no_check=True
                    if no_check:
                        ret = set_notif_val(request,colg._id,msg,activity,bx)
        except Exception, e:
            print e


        url_name = "/" + group_id + "/forum/thread/" + str(colrep._id)
        return HttpResponseRedirect(url_name)
        # variables = RequestContext(request,
        #                              {  'forum':forum,
        #                                 'thread':colrep,
        #                                 'eachrep':colrep,
        #                                 'groupid':group_id,
        #                                 'group_id':group_id,
        #                                 'user': request.user,
        #                                 'reply_count':0,
        #                                 'forum_threads': json.dumps(forum_threads),
        #                                 'forum_created_by':User.objects.get(id=forum.created_by).username
        #                             })
        # print "\n\n renedering to thread_details"
        # return render_to_response("ndf/thread_details.html",variables)

    else:
        return render_to_response("ndf/create_thread.html",
                                    {   'group_id':group_id,
                                        'groupid':group_id,
                                        'forum': forum,
                                        'forum_threads': json.dumps(forum_threads),
                                        'forum_created_by':User.objects.get(id=forum.created_by).username
                                    },
                              RequestContext(request))



@login_required
@get_execution_time
def add_node(request, group_id):

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
    group_name, group_id = get_group_name_id(group_id)

    try:
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        content_org = request.POST.get("reply","")
        node = request.POST.get("node","")
        thread = request.POST.get("thread","") # getting thread _id
        forumid = request.POST.get("forumid","") # getting forum _id
        sup_id = request.POST.get("supnode","") #getting _id of it's parent node
        tw_name = request.POST.get("twistname","")
        upload_files_count=int(request.POST.get("upload_cnt",0))
        #print "upfiles=",upload_files_count
        lst=[]
        lstobj_collection=[]
        usrid = int(request.user.id)
        if upload_files_count > 0:
            #print "uploaded items",request.FILES.items()
            try:
                thread_obj = node_collection.one({'_id': ObjectId(thread)})
                access_policy = thread_obj.access_policy
            except:
                access_policy = u'PUBLIC'

            for key,value in request.FILES.items():
                fname=unicode(value.__dict__['_name'])
                #print "key=",key,"value=",value,"fname=",fname

                fileobj,fs=save_file(value,fname,usrid,group_id, "", "", username=unicode(request.user.username), access_policy=access_policy, count=0, first_object="")

                if type(fileobj) == list:
                    obid = str(list(fileobj)[1])
                else:
                    obid=str(fileobj)
                file_obj=node_collection.find_one({'_id': ObjectId(obid)})
                lstobj_collection.append(file_obj._id)
        forumobj = ""
        groupobj = ""
        colg = node_collection.one({'_id':ObjectId(group_id)})
        if forumid:
            forumobj = node_collection.one({"_id": ObjectId(forumid)})

        sup = node_collection.one({"_id": ObjectId(sup_id)})

        if not sup :
            return HttpResponse("failure")

        colrep = node_collection.collection.GSystem()

        if node == "Twist":
            name = tw_name
            colrep.member_of.append(twist_gst._id)
        elif node == "Reply":
            name = unicode("Reply of:"+str(sup._id))
            colrep.member_of.append(reply_gst._id)
        #Adding uploaded files id's in collection set of reply
        if upload_files_count > 0:
            colrep.collection_set = lstobj_collection

        colrep.prior_node.append(sup._id)
        colrep.name = name

        if content_org:
            colrep.content_org = unicode(content_org)
            # Required to link temporary files with the current user who is modifying this document
            usrname = request.user.username
            filename = slugify(name) + "-" + usrname + "-"
            colrep.content = content_org


        colrep.created_by = usrid
        colrep.modified_by = usrid

        if usrid not in colrep.contributors:
            colrep.contributors.append(usrid)
        colrep.prior_node.append(sup._id)
        colrep.name = name

        if content_org:
            colrep.content_org = unicode(content_org)
            # Required to link temporary files with the current user who is modifying this document
            usrname = request.user.username
            filename = slugify(name) + "-" + usrname + "-"
            colrep.content = content_org

        usrid=int(request.user.id)
        colrep.created_by=usrid
        colrep.modified_by = usrid

        if usrid not in colrep.contributors:
            colrep.contributors.append(usrid)

        colrep.group_set.append(colg._id)

        colrep.save(groupid=group_id)

        # print "----------", colrep._id
        groupname = colg.name

        if node == "Twist" :
            url="http://"+sitename+"/"+str(group_id)+"/forum/thread/"+str(colrep._id)
            activity=request.user.username+" -added a thread '"
            prefix="' on the forum '"+forumobj.name+"'"
            nodename=name

        if node == "Reply":
            threadobj=node_collection.one({"_id": ObjectId(thread)})
            url="http://"+sitename+"/"+str(group_id)+"/forum/thread/"+str(threadobj._id)
            activity=request.user.username+" -added a reply "
            prefix=" on the thread '"+threadobj.name+"' on the forum '"+forumobj.name+"'"
            nodename=""

        link = url

        for each in colg.author_set:
            if each != colg.created_by:
                bx=User.objects.get(id=each)
                msg=activity+"-"+nodename+prefix+" in the group '"+ groupname +"'\n"+"Please visit "+link+" to see the updated page"
                if bx:
                    no_check=forum_notification_status(group_id,auth._id)
                    if no_check:
                        ret = set_notif_val(request,group_id,msg,activity,bx)

        bx=User.objects.get(id=colg.created_by)
        msg=activity+"-"+nodename+prefix+" in the group '"+groupname+"' created by you"+"\n"+"Please visit "+link+" to see the updated page"

        if bx:
            no_check=forum_notification_status(group_id,auth._id)
            if no_check:
                ret = set_notif_val(request,group_id,msg,activity,bx)
        if node == "Reply":
            # if exstng_reply:
            #     exstng_reply.prior_node =[]
            #     exstng_reply.prior_node.append(colrep._id)
            #     exstng_reply.save()

            threadobj=node_collection.one({"_id": ObjectId(thread)})
            variables=RequestContext(request,{'thread':threadobj,'user':request.user,'forum':forumobj,'groupid':group_id,'group_id':group_id})
            return render_to_response("ndf/refreshtwist.html",variables)
        else:
            templ=get_template('ndf/refreshthread.html')
            html = templ.render(Context({'forum':forumobj,'user':request.user,'groupid':group_id,'group_id':group_id}))
            return HttpResponse(html)

    except Exception as e:
        return HttpResponse(""+str(e))
    return HttpResponse("success")


@get_execution_time
def get_profile_pic(username):

    auth = node_collection.one({'_type': 'Author', 'name': unicode(username) })
    prof_pic = node_collection.one({'_type': u'RelationType', 'name': u'has_profile_pic'})
    # dbref_profile_pic = prof_pic.get_dbref()
    collection_tr = db[Triple.collection_name]
    prof_pic_rel = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': prof_pic._id })

    # prof_pic_rel will get the cursor object of relation of user with its profile picture
    if prof_pic_rel.count() :
        index = prof_pic_rel[prof_pic_rel.count() - 1].right_subject
        img_obj = node_collection.one({'_type': 'File', '_id': ObjectId(index) })
    else:
        img_obj = ""

    return img_obj


@login_required
@check_delete
@get_execution_time
def delete_forum(request,group_id,node_id,relns=None):
    """ Changing status of forum to HIDDEN
    """
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

    op = node_collection.collection.update({'_id': ObjectId(node_id)}, {'$set': {'status': u"HIDDEN"}})

    node=node_collection.one({'_id':ObjectId(node_id)})

    #send notifications to all group members
    colg=node_collection.one({'_id':ObjectId(group_id)})
    for each in colg.author_set:
        if each != colg.created_by:
            bx=get_userobject(each)
            if bx:
                activity=request.user.username+" -deleted forum "
                msg=activity+"-"+node.name+"- in the group '"+ colg.name
#                no_check=forum_notification_status(group_id,auth._id)
#                if no_check:
                ret = set_notif_val(request,group_id,msg,activity,bx)
    activity=request.user.username+" -deleted forum "
    bx=get_userobject(colg.created_by)
    if bx:
        msg=activity+"-"+node.name+"- in the group '"+colg.name+"' created by you"
#        no_check=forum_notification_status(group_id,auth._id)
#        if no_check:
        ret = set_notif_val(request,group_id,msg,activity,bx)
    return HttpResponseRedirect(reverse('forum', kwargs={'group_id': group_id}))


@login_required
@get_execution_time
def delete_thread(request,group_id,forum_id,node_id):
    """ Changing status of thread to HIDDEN
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(node_id) :
        thread=node_collection.one({'_id':ObjectId(node_id)})
    else:
        return
    forum = node_collection.one({'_id': ObjectId(forum_id)})
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
    op = node_collection.collection.update({'_id': ObjectId(node_id)}, {'$set': {'status': u"HIDDEN"}})

    node=node_collection.one({'_id':ObjectId(node_id)})
    forum_threads = []
    exstng_reply = node_collection.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(forum._id)}],'status':{'$nin':['HIDDEN']}})
    exstng_reply.sort('created_at')
    forum_node=node_collection.one({'_id':ObjectId(forum_id)})
    for each in exstng_reply:
        forum_threads.append(each.name)
    #send notifications to all group members
    colg=node_collection.one({'_id':ObjectId(group_id)})
    for each in colg.author_set:
        if each != colg.created_by:
            bx=get_userobject(each)
            if bx:
                activity=request.user.username+" -deleted thread "
                prefix=" in the forum "+forum_node.name
                link="http://"+sitename+"/"+str(colg._id)+"/forum/"+str(forum_node._id)
                msg=activity+"-"+node.name+prefix+"- in the group '"+colg.name+"' created by you."+"'\n"+"Please visit "+link+" to see the forum."
#                no_check=forum_notification_status(group_id,auth._id)
#                if no_check:
                ret = set_notif_val(request,group_id,msg,activity,bx)
    activity=request.user.username+" -deleted thread "
    prefix=" in the forum "+forum_node.name
    bx=get_userobject(colg.created_by)
    if bx:
        link="http://"+sitename+"/"+str(colg._id)+"/forum/"+str(forum_node._id)
        msg=activity+"-"+node.name+prefix+"- in the group '"+colg.name+"' created by you."+"'\n"+"Please visit "+link+" to see the forum."
#        no_check=forum_notification_status(group_id,auth._id)
#        if no_check:
        ret = set_notif_val(request,group_id,msg,activity,bx)
    #send notification code ends here
    variables = RequestContext(request,{
                                        'forum':forum,
                                        'groupid':group_id,'group_id':group_id,
                                        'forum_created_by':User.objects.get(id=forum.created_by).username
                                        })

    return render_to_response("ndf/forumdetails.html",variables)

@login_required
@get_execution_time
def edit_thread(request,group_id,forum_id,thread_id):
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

    forum=node_collection.one({'_id':ObjectId(forum_id)})
    thread=node_collection.one({'_id':ObjectId(thread_id)})
    exstng_reply = node_collection.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(forum._id)}]})
    nodes=[]
    exstng_reply.sort('created_at')
    for each in exstng_reply:
        nodes.append(each.name)
    request.session['nodes']=json.dumps(nodes)
    colg=node_collection.one({'_id':ObjectId(group_id)})
    if request.method == 'POST':
        name = unicode(request.POST.get('thread_name',"")) # thread name
        thread.name = name

        content_org = request.POST.get('content_org',"") # thread content
        # print "content=",content_org
        if content_org:
            thread.content_org = unicode(content_org)
            usrname = request.user.username
            filename = slugify(name) + "-" + usrname + "-"
            thread.content = content_org

        thread.save(groupid=group_id)

        link="http://"+sitename+"/"+str(colg._id)+"/forum/thread/"+str(thread._id)
        for each in colg.author_set:
            if each != colg.created_by:
                bx=get_userobject(each)
                if bx:
                    msg=request.user.username+" has edited thread- "+thread.name+"- in the forum " + forum.name + " in the group -'" + colg.name+"'\n"+"Please visit "+link+" to see the thread."
                    activity="Edited thread"
                    #auth = node_collection.one({'_type': 'Author', 'name': unicode(bx.username) })
                    #if colg._id and auth:
                        #no_check=forum_notification_status(colg._id,auth._id)
#                    else:
#                        no_check=True
#                    if no_check:
                    ret = set_notif_val(request,colg._id,msg,activity,bx)
        activity=request.user.username+" edited thread -"
        bx=get_userobject(colg.created_by)
        prefix="-in the forum -"+forum.name
        if bx:
            msg=activity+"-"+thread.name+prefix+" in the group '"+colg.name+"' created by you"+"\n"+"Please visit "+link+" to see the thread"
#            no_check=forum_notification_status(group_id,auth._id)
#            if no_check:
            ret = set_notif_val(request,group_id,msg,activity,bx)


        variables = RequestContext(request,{'group_id':group_id,'thread_id': thread._id,'nodes':json.dumps(nodes)})
        return HttpResponseRedirect(reverse('thread', kwargs={'group_id':group_id,'thread_id': thread._id }))
    else:
        return render_to_response("ndf/edit_thread.html",
                                    {   'group_id':group_id,
                                        'groupid':group_id,
                                        'forum': forum,
                                        'thread':thread,
                                        'forum_created_by':User.objects.get(id=forum.created_by).username
                                    },
                              RequestContext(request))

@login_required
@get_execution_time
def delete_reply(request,group_id,forum_id,thread_id,node_id):

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

    #group_name, group_id = get_group_name_id(group_id)
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    activity = ""

    op = node_collection.collection.update({'_id': ObjectId(node_id)}, {'$set': {'status': u"HIDDEN"}})

    # ??? CHECK
    replyobj=node_collection.one({'_id':ObjectId(node_id)})

    forumobj=node_collection.one({"_id": ObjectId(forum_id)})
    threadobj=node_collection.one({"_id": ObjectId(thread_id)})
    # notifications to all group members
    colg=node_collection.one({'_id':ObjectId(group_id)})
    link="http://"+sitename+"/"+str(colg._id)+"/forum/thread/"+str(threadobj._id)
    for each in colg.author_set:
        if each != colg.created_by:
            bx=get_userobject(each)
            if bx:
                msg=request.user.username+" has deleted reply- "+replyobj.content_org+"- in the thread " + threadobj.name + " in the group -'" + colg.name+"'\n"+"Please visit "+link+" to see the thread."
                activity="Deleted reply"
                #auth = node_collection.one({'_type': 'Author', 'name': unicode(bx.username) })
                #if colg._id and auth:
                     #no_check=forum_notification_status(colg._id,auth._id)
#               else:
#                    no_check=True
#                    if no_check:
                ret = set_notif_val(request,colg._id,msg,activity,bx)
        prefix="-in the forum -"+forumobj.name
        msg=request.user.username+" has deleted reply- "+replyobj.content_org+"- in the thread " + threadobj.name +prefix+ " in the group -'" + colg.name+"' created by you"+"\n Please visit "+link+" to see the thread."
        bx=get_userobject(colg.created_by)
        if bx:
#            no_check=forum_notification_status(group_id,auth._id)
#            if no_check:
            ret = set_notif_val(request,group_id,msg,activity,bx)


    variables=RequestContext(request,{'thread':threadobj,'user':request.user,'forum':forumobj,'groupid':group_id,'group_id':group_id})
    return HttpResponseRedirect(reverse('thread', kwargs={'group_id':group_id,'thread_id': threadobj._id }))
#    return render_to_response("ndf/replytwistrep.html",variables)

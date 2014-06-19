''' -- imports from installed packages -- '''
import json

from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template import Context
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.contrib.sites.models import Site



from django_mongokit import get_database
from gnowsys_ndf.ndf.views.methods import get_forum_repl_type,forum_notification_status
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem,Node
from gnowsys_ndf.ndf.views.notify import set_notif_val
import datetime
from gnowsys_ndf.ndf.org2any import org2html
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId



###########################################################################

collection = get_database()[Node.collection_name]
forum_st = collection.Node.one({'$and':[{'_type':'GSystemType'},{'name':GAPPS[5]}]})
start_time = collection.Node.one({'$and':[{'_type':'AttributeType'},{'name':'start_time'}]})
end_time = collection.Node.one({'$and':[{'_type':'AttributeType'},{'name':'end_time'}]})
reply_st = collection.Node.one({'$and':[{'_type':'GSystemType'},{'name':'Reply'}]})
twist_st = collection.Node.one({'$and':[{'_type':'GSystemType'},{'name':'Twist'}]})


def forum(request, group_id, node_id=None):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    if node_id is None:
        node_ins = collection.Node.find_one({'_type':"GSystemType", "name":"Forum"})
        if node_ins:
            node_id = str(node_ins._id)
    
    if request.method == "POST":
      # Forum search view
      title = forum_st.name
      
      search_field = request.POST['search_field']
      existing_forums = collection.Node.find({'member_of': {'$all': [ObjectId(forum_st._id)]},
                                         '$or': [{'name': {'$regex': search_field, '$options': 'i'}}, 
                                                 {'tags': {'$regex':search_field, '$options': 'i'}}], 
                                         'group_set': {'$all': [ObjectId(group_id)]}
                                     }).sort('last_update', -1)

      return render_to_response("ndf/forum.html",
                                {'title': title, 
                                 'searching': True, 'query': search_field,
                                 'existing_forums': existing_forums, 'groupid':group_id, 'group_id':group_id
                                }, 
                                context_instance=RequestContext(request)
      )

    elif forum_st._id == ObjectId(node_id):
      
      # Forum list view

      existing_forums = collection.Node.find({'member_of': {'$all': [ObjectId(node_id)]}, 'group_set': {'$all': [ObjectId(group_id)]}}).sort('last_update', -1)
      forum_detail_list = []

      for each in existing_forums:
        
        temp_forum = {}
        temp_forum['name'] = each.name
        temp_forum['created_at'] = each.created_at
        temp_forum['tags'] = each.tags
        temp_forum['member_of_names_list'] = each.member_of_names_list
        temp_forum['user_details_dict'] = each.user_details_dict
        temp_forum['html_content'] = each.html_content
        temp_forum['contributors'] = each.contributors
        temp_forum['id'] = each._id
        temp_forum['threads'] = collection.GSystem.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(each._id)}]}).count()
        
        forum_detail_list.append(temp_forum)

      variables=RequestContext(request,{'existing_forums': forum_detail_list, 'groupid': group_id, 'group_id': group_id})
      return render_to_response("ndf/forum.html",variables)

def create_forum(request,group_id):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    if request.method == "POST":

        colg = collection.Group.one({'_id':ObjectId(group_id)})

        colf = collection.GSystem()

        name = unicode(request.POST.get('forum_name',""))
        colf.name = name
        
        content_org = request.POST.get('content_org',"")
        if content_org:
            colf.content_org = unicode(content_org)
            usrname = request.user.username
            filename = slugify(name) + "-" + usrname + "-"
            colf.content = org2html(content_org, file_prefix=filename)
        
        usrid=int(request.user.id)
        usrname = unicode(request.user.username)
        
        colf.created_by=usrid
        colf.modified_by = usrid
        if usrid not in colf.contributors:
            colf.contributors.append(usrid)
        
        colf.group_set.append(colg._id)

        user_group_obj = collection.Group.one({'$and':[{'_type':u'Group'},{'name':usrname}]})
        if user_group_obj:
            if user_group_obj._id not in colf.group_set:
                colf.group_set.append(user_group_obj._id)     

        colf.member_of.append(forum_st._id)

        sdate=request.POST.get('sdate',"")
        shrs= request.POST.get('shrs',"") 
        smts= request.POST.get('smts',"")
        
        edate= request.POST.get('edate',"")
        ehrs= request.POST.get('ehrs',"")
        emts=request.POST.get('emts',"")
        
        start_dt={}
        end_dt={}
        
        if not shrs:
            shrs=0
        if not smts:
            smts=0
        if sdate:
            sdate1=sdate.split("/") 
            st_date = datetime.datetime(int(sdate1[2]),int(sdate1[0]),int(sdate1[1]),int(shrs),int(smts))
            start_dt[start_time.name]=st_date
        
        if not ehrs:
            ehrs=0
        if not emts:
            emts=0
        if edate:
            edate1=edate.split("/")
            en_date= datetime.datetime(int(edate1[2]),int(edate1[0]),int(edate1[1]),int(ehrs),int(emts))
            end_dt[end_time.name]=en_date
       # colf.attribute_set.append(start_dt)
       # colf.attribute_set.append(end_dt)
        colf.save()
        return HttpResponseRedirect(reverse('show', kwargs={'group_id':group_id,'forum_id': colf._id }))
        # variables=RequestContext(request,{'forum':colf})
        # return render_to_response("ndf/forumdetails.html",variables)


    available_nodes = collection.Node.find({'_type': u'GSystem', 'member_of': ObjectId(forum_st._id) })

    nodes_list = []
    for each in available_nodes:
      nodes_list.append(each.name)

    return render_to_response("ndf/create_forum.html",{'group_id':group_id,'groupid':group_id, 'nodes_list': nodes_list},RequestContext(request))

def display_forum(request,group_id,forum_id):
    
    forum = collection.Node.one({'_id': ObjectId(forum_id)})

    usrname = User.objects.get(id=forum.created_by).username

    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    forum_object = collection.Node.one({'_id': ObjectId(forum_id)})
    if forum_object._type == "GSystemType":
       return forum(request, group_id, forum_id)

    variables = RequestContext(request,{
                                        'forum':forum,
                                        'groupid':group_id,'group_id':group_id,
                                        'forum_created_by':usrname
                                        })

    return render_to_response("ndf/forumdetails.html",variables)

def display_thread(request,group_id, thread_id, forum_id=None):
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    try:
        thread = collection.Node.one({'_id': ObjectId(thread_id)})
        forum=""
        for each in thread.prior_node:
            forum=collection.GSystem.one({'$and':[{'member_of': {'$all': [forum_st._id]}},{'_id':ObjectId(each)}]})
            if forum:
                usrname = User.objects.get(id=forum.created_by).username
                variables = RequestContext(request,
                                            {   'forum':forum,
                                                'thread':thread,
                                                'groupid':group_id,
                                                'group_id':group_id,
                                                'eachrep':thread,
                                                'user':request.user,
                                                'forum_created_by':usrname
                                            })
                return render_to_response("ndf/thread_details.html",variables)
    except:
        pass



def create_thread(request, group_id, forum_id):

    forum = collection.Node.one({'_id': ObjectId(forum_id)})
    forum_data = {  
                    'name':forum.name,
                    'content':forum.content,
                    'created_by':User.objects.get(id=forum.created_by).username
                }
    # print forum_data
    forum_threads = []
    exstng_reply = collection.GSystem.find({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(forum._id)}]})
    exstng_reply.sort('created_at')
    
    for each in exstng_reply:
        forum_threads.append(each.name)
    
    if request.method == "POST":

        colg = collection.Group.one({'_id':ObjectId(group_id)})

        name = unicode(request.POST.get('thread_name',""))
        
        content_org = request.POST.get('content_org',"")

        # -------------------
        colrep = collection.GSystem()
    
        colrep.member_of.append(twist_st._id)
        
        colrep.prior_node.append(forum._id)
        colrep.name = name

        if content_org:
            colrep.content_org = unicode(content_org)
            # Required to link temporary files with the current user who is modifying this document
            usrname = request.user.username
            filename = slugify(name) + "-" + usrname + "-"
            colrep.content = org2html(content_org, file_prefix=filename)

        usrid=int(request.user.id)
        colrep.created_by=usrid
        colrep.modified_by = usrid

        if usrid not in colrep.contributors:
            colrep.contributors.append(usrid)
        
        colrep.group_set.append(colg._id)
        colrep.save()

        variables = RequestContext(request,
                                    {   'forum':forum,
                                        'thread':colrep,
                                        'eachrep':colrep,
                                        'groupid':group_id,
                                        'group_id':group_id,
                                        'user':request.user,
                                        'forum_threads': json.dumps(forum_threads),
                                        'forum_created_by':User.objects.get(id=forum.created_by).username
                                    })

        return render_to_response("ndf/thread_details.html",variables)

    else:
        return render_to_response("ndf/create_thread.html",
                                    {   'group_id':group_id,
                                        'groupid':group_id,
                                        'forum': forum,
                                        'forum_threads': json.dumps(forum_threads),
                                        'forum_created_by':User.objects.get(id=forum.created_by).username
                                    },
                              RequestContext(request))



def add_node(request,group_id):

    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass

    try:
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        sitename=Site.objects.all()[0].name.__str__()
        content_org=request.POST.get("reply","")
        node=request.POST.get("node","")
        thread=request.POST.get("thread","")
        forumid=request.POST.get("forumid","")
        sup_id=request.POST.get("supnode","")
        tw_name=request.POST.get("twistname","")
        forumobj=""
        groupobj=""
    
        colg = collection.Group.one({'_id':ObjectId(group_id)})

        if forumid:
            forumobj=collection.GSystem.one({"_id": ObjectId(forumid)})
    
        sup=collection.GSystem.one({"_id": ObjectId(sup_id)})
    
        if not sup :        
            return HttpResponse("failure")
    
        colrep=collection.GSystem()
    
        if node == "Twist":
            name=tw_name
            colrep.member_of.append(twist_st._id)
        elif node == "Reply":
            name=unicode("Reply of:"+str(sup._id))
            colrep.member_of.append(reply_st._id)
    
        colrep.prior_node.append(sup._id)
        colrep.name=name

        if content_org:
            colrep.content_org = unicode(content_org)
            # Required to link temporary files with the current user who is modifying this document
            usrname = request.user.username
            filename = slugify(name) + "-" + usrname + "-"
            colrep.content = org2html(content_org, file_prefix=filename)

        usrid=int(request.user.id)
        colrep.created_by=usrid
        colrep.modified_by = usrid

        if usrid not in colrep.contributors:
            colrep.contributors.append(usrid)
        
        colrep.group_set.append(colg._id)
        colrep.save()
        groupname=colg.name
        
        if node == "Twist" :  
            url="http://"+sitename+"/"+str(group_id)+"/forum/thread/"+str(colrep._id)
            activity=str(request.user.username)+" -added a thread '"
            prefix="' on the forum '"+forumobj.name+"'"
            nodename=name
        
        if node == "Reply":
            threadobj=collection.GSystem.one({"_id": ObjectId(thread)})
            url="http://"+sitename+"/"+str(group_id)+"/forum/thread/"+str(threadobj._id)
            activity=str(request.user.username)+" -added a reply "
            prefix=" on the thread '"+threadobj.name+"' on the forum '"+forumobj.name+"'"
            nodename=""
        
        link=url
        
        for each in colg.author_set:
            bx=User.objects.get(id=each)
            msg=activity+"-"+nodename+prefix+" in the group '"+str(groupname)+"'\n"+"Please visit "+link+" to see the updated page"
            if bx:
                no_check=forum_notification_status(group_id,auth._id)
                if no_check:
                    ret = set_notif_val(request,group_id,msg,activity,bx)
        
        bx=User.objects.get(id=colg.created_by)
        msg=activity+"-"+nodename+prefix+" in the group '"+str(groupname)+"' created by you"+"\n"+"Please visit "+link+" to see the updated page"   
        
        if bx:
            no_check=forum_notification_status(group_id,auth._id)
            if no_check:
                ret = set_notif_val(request,group_id,msg,activity,bx)
        
        if node == "Reply":
            # if exstng_reply:
            #     exstng_reply.prior_node =[]
            #     exstng_reply.prior_node.append(colrep._id)
            #     exstng_reply.save()

            threadobj=collection.GSystem.one({"_id": ObjectId(thread)})
            variables=RequestContext(request,{'thread':threadobj,'user':request.user,'forum':forumobj,'groupid':group_id,'group_id':group_id})
            return render_to_response("ndf/refreshtwist.html",variables)
        else:
            templ=get_template('ndf/refreshthread.html')
            html = templ.render(Context({'forum':forumobj,'user':request.user,'groupid':group_id,'group_id':group_id}))
            return HttpResponse(html)


    except Exception as e:
        return HttpResponse(""+str(e))
    return HttpResponse("success")


def get_profile_pic(username):
    
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(username) })
    prof_pic = collection.Node.one({'_type': u'RelationType', 'name': u'has_profile_pic'})
    dbref_profile_pic = prof_pic.get_dbref()
    collection_tr = db[Triple.collection_name]
    prof_pic_rel = collection_tr.Triple.find({'_type': 'GRelation', 'subject': ObjectId(auth._id), 'relation_type': dbref_profile_pic })

    # prof_pic_rel will get the cursor object of relation of user with its profile picture 
    if prof_pic_rel.count() :
        index = prof_pic_rel[prof_pic_rel.count() - 1].right_subject
        img_obj = collection.Node.one({'_type': 'File', '_id': ObjectId(index) })        
    else:
        img_obj = "" 

    return img_obj
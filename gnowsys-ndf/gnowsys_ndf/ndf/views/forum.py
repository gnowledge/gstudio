''' -- imports from installed packages -- '''

from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template import Context
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.loader import get_template



from django_mongokit import get_database
from gnowsys_ndf.ndf.views.methods import get_forum_repl_type
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem,Node

import datetime
from gnowsys_ndf.ndf.org2any import org2html
try:
    from bson import ObjectId
except ImportError:  # old pymongo                                                                                                           
    from pymongo.objectid import ObjectId



###########################################################################

db = get_database()
gs_collection = db[Node.collection_name]
forum_st = gs_collection.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':GAPPS[5]}]})
start_time=gs_collection.AttributeType.one({'$and':[{'_type':'AttributeType'},{'name':'start_time'}]})
end_time=gs_collection.AttributeType.one({'$and':[{'_type':'AttributeType'},{'name':'end_time'}]})
reply_st=gs_collection.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':'Reply'}]})
twist_st=gs_collection.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':'Twist'}]})



def forum(request,group_name,node_id):
    existing_forums=gs_collection.GSystem.find({'$and':[{'_type':u'GSystem'},{'member_of':'Forum'}]})
    existing_forums.sort('name')
    variables=RequestContext(request,{'existing_forums':existing_forums})
    return render_to_response("ndf/forum.html",variables)

def create_forum(request,group_name):
    if request.method == "POST":
        colf=gs_collection.GSystem()
        name=unicode(request.POST.get('forum_name',""))
        colf.name=name
        content_org = "\n"+request.POST.get('content_org')
        filename = slugify(name) + "-" + request.user.username + "-"
        colf.content = unicode(org2html(content_org, file_prefix=filename))
        colf.content_org = unicode(content_org.encode('utf8'))
        usrid=int(request.user.id)
        colf.created_by=usrid
        colf.member_of.append(forum_st.name)
        colf.gsystem_type.append(forum_st._id)
        sdate=request.POST.get('sdate',"")
        shrs= request.POST.get('shrs',"") 
        smts= request.POST.get('smts',"")
        edate= request.POST.get('edate',"")
        ehrs= request.POST.get('ehrs',"")
        emts=request.POST.get('emts',"")
        start_dt={}
        end_dt={}
        if sdate:
            sdate1=sdate.split("/") 
            st_date = datetime.datetime(int(sdate1[2]),int(sdate1[0]),int(sdate1[1]),int(shrs),int(smts))
            start_dt[start_time.name]=st_date
        if edate:
            edate1=edate.split("/")
            en_date= datetime.datetime(int(edate1[2]),int(edate1[0]),int(edate1[1]),int(ehrs),int(emts))
            end_dt[end_time.name]=en_date
        colf.attribute_set.append(start_dt)
        colf.attribute_set.append(end_dt)
        colf.save()
        return HttpResponseRedirect(reverse('show', kwargs={'group_name': group_name, 'forum_id': colf._id}))
        # variables=RequestContext(request,{'forum':colf})
        # return render_to_response("ndf/forumdetails.html",variables)
    return render_to_response("ndf/create_forum.html",RequestContext(request))

def display_forum(request,group_name,forum_id):
    forum = gs_collection.GSystemType.one({'_id': ObjectId(forum_id)})
    variables=RequestContext(request,{'forum':forum})
    return render_to_response("ndf/forumdetails.html",variables)

def add_node(request,group_name):
    try:
        content_org="\n"+request.POST["reply"]
        node=request.POST["node"]
        sup_id=request.POST["supnode"]
        tw_name=request.POST["twistname"]
        sup=gs_collection.GSystem.one({"_id": ObjectId(sup_id)})
        if not sup :        
            return HttpResponse("failure")
        colrep=gs_collection.GSystem()
        if node == "Twist":
            name=slugify(tw_name)
            colrep.name=unicode(name)
            colrep.member_of.append(twist_st.name)
            colrep.gsystem_type.append(twist_st._id)
        elif node == "Reply_Twist":
            name="Reply of Twist:"+str(sup._id)
            colrep.name=unicode(name)
            colrep.member_of.append(reply_st.name)
            colrep.gsystem_type.append(reply_st._id)
        elif node == "Reply":
            name="Reply of:"+str(sup._id)
            colrep.name=unicode(name)
            colrep.member_of.append(reply_st.name)
            colrep.gsystem_type.append(reply_st._id)
        colrep.prior_node.append(sup._id)
        filename = slugify(name) + "-" + request.user.username + "-"
        colrep.content = unicode(org2html(content_org, file_prefix=filename))
        colrep.content_org = unicode(content_org.encode('utf8'))
        usrid=int(request.user.id)
        colrep.created_by=usrid
        colrep.save()
        if node == "Reply":
            exstng_reply=gs_collection.GSystem.one({'$and':[{'_type':'GSystem'},{'prior_node':ObjectId(sup._id)}]})
            if exstng_reply:
                exstng_reply.prior_node =[]
                exstng_reply.prior_node.append(colrep._id)
                exstng_reply.save()
        if node == "Twist":
            forum=sup
            templ=get_template('ndf/refreshtwist.html')
            html = templ.render(Context({'forum':forum,'user':request.user}))
            return HttpResponse(html)
        else:
             return HttpResponse("success")

    except Exception as e:
        return HttpResponse("")
    return HttpResponse("success")

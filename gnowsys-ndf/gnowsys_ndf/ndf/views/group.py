''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django_mongokit import get_database
from django.contrib.auth.models import User

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.ndf.views.ajax_views import set_drawer_widget
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_existing_groups
from gnowsys_ndf.ndf.views.methods import *

#######################################################################################################################################

from django.contrib.auth.models import User
db = get_database()
gst_collection = db[GSystemType.collection_name]
gst_group = gst_collection.GSystemType.one({'name': GAPPS[2]})
gs_collection = db[GSystem.collection_name]
collection = db[Node.collection_name]

#######################################################################################################################################
#      V I E W S   D E F I N E D   F O R   G A P P -- ' G R O U P '
#######################################################################################################################################


def group(request, group_id,app_id):
    """Renders a list of all 'Group-type-GSystems' available within the database.
    """
    group_nodes = []
    excl_gr_nodes=[]
    col_Group = db[Group.collection_name]
    user_list=[]
    users=User.objects.all()
    for each in users:
        user_list.append(each.username)
    colg = col_Group.Group.find({'_type': u'Group'})
    colg.sort('name')
    gr = list(colg)
    for items in gr:
            group_nodes.append(items)
    group_nodes_count = len(group_nodes)
    colg = col_Group.Group.find({'$and':[{'_type': u'Group'},{'name':{'$nin':user_list}}]})
    colg.sort('name')
    gr = list(colg)
    for items in gr:
            excl_gr_nodes.append(items)
    return render_to_response("ndf/group.html", {'group_nodes': group_nodes, 'group_nodes_excluding_users':excl_gr_nodes,'group_nodes_count': group_nodes_count,'groupid': group_id,'group_id': group_id}, context_instance=RequestContext(request))
    



def create_group(request,group_id):
    if request.method == "POST":
        col_Group = db[Group.collection_name]
        colg = col_Group.Group()
        Mod_colg=col_Group.Group()

        cname=request.POST.get('groupname', "")
        colg.altnames=cname
        colg.name = unicode(cname)
        colg.member_of.append(gst_group._id)
        usrid = int(request.user.id)
        colg.created_by = usrid
        colg.modified_by = usrid
        
        if usrid not in colg.contributors:
            colg.contributors.append(usrid)

        colg.group_type = request.POST.get('group_type', "")        
        colg.edit_policy = request.POST.get('edit_policy', "")
        colg.subscription_policy = request.POST.get('subscription', "")
        colg.visibility_policy = request.POST.get('existance', "")
        colg.disclosure_policy = request.POST.get('member', "")
        colg.encryption_policy = request.POST.get('encryption', "")
        colg.save()
        
        if colg.edit_policy == "EDITABLE_MODERATED":
            Mod_colg.altnames = cname + "Mod" 
            Mod_colg.name = cname + "Mod"     
            Mod_colg.group_type = "PRIVATE"
            Mod_colg.created_by = usrid
            Mod_colg.modified_by = usrid
            if usrid not in Mod_colg.contributors:
                Mod_colg.contributors.append(usrid)
            Mod_colg.prior_node.append(colg._id)
            Mod_colg.save() 
            colg.post_node.append(Mod_colg._id)
            colg.save()

        return render_to_response("ndf/groupdashboard.html",{'groupobj':colg,'node':colg,'user':request.user,'groupid':group_id,'group_id':group_id},context_instance=RequestContext(request))

    return render_to_response("ndf/create_group.html", {'groupid':group_id,'group_id':group_id},RequestContext(request))
    
# def home_dashboard(request):
#     try:
#         groupobj=gs_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
#     except Exception as e:
#         groupobj=""
#         pass
#     print "frhome--",groupobj
#     return render_to_response("ndf/groupdashboard.html",{'groupobj':groupobj,'user':request.user,'curgroup':groupobj},context_instance=RequestContext(request))



def group_dashboard(request,group_id=None):
    try:
        groupobj="" 
        grpid=""
        if group_id == None:
            groupobj=gs_collection.Node.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
            grpid=groupobj['_id']
        else:
            groupobj=gs_collection.Group.one({'_id':ObjectId(group_id)})
            grpid=groupobj['_id']
    except Exception as e:
        groupobj=gs_collection.Node.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
        grpid=groupobj['_id']
        pass
    return render_to_response("ndf/groupdashboard.html",{'node': groupobj, 'groupid':grpid, 'group_id':grpid, 'user':request.user},context_instance=RequestContext(request))

@login_required
def edit_group(request,group_id):
    page_node = gs_collection.GSystem.one({"_id": ObjectId(group_id)})
    
    if request.method == "POST":
            get_node_common_fields(request, page_node, group_id, gst_group)
            if page_node.access_policy == "PUBLIC":
                page_node.group_type = "PUBLIC"
            if page_node.access_policy == "PRIVATE":
                page_node.group_type = "PRIVATE"
            page_node.save()
            group_id=page_node._id
            return HttpResponseRedirect(reverse('groupchange', kwargs={'group_id':group_id}))
    return render_to_response("ndf/edit_group.html",
                                      { 'node': page_node,
                                        'groupid':group_id,
                                        'group_id':group_id
                                        },
                                      context_instance=RequestContext(request)
                                      )


def switch_group(request,group_id,node_id):
    try:
        node=collection.Node.one({"_id":ObjectId(node_id)})
        print "method=",request.method
        if request.method == "POST":
            new_groups=request.POST.get('new_grps',"")
            print "newgrps",new_groups
            for each in new_groups:
                print "each id",each
                if ObjectId(each) not in node.group_set:
                    node.group_set.append(ObjectId(each));
            node.save()
            return HttpResponse("Success")
        else:
            coll_obj_list = []
            st = collection.Node.find({"_type":"Group"})

            for each in node.group_set:
                coll_obj_list.append(collection.Node.one({'_id':each}))
            data_list=set_drawer_widget(st,coll_obj_list)
            return HttpResponse(json.dumps(data_list))
     
    except Exception as e:
        print "Exception in switch_group"+str(e)
        return HttpResponse("Failure")

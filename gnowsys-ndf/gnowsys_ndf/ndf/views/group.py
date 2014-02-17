''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem
from gnowsys_ndf.ndf.models import Group

from gnowsys_ndf.ndf.templatetags.ndf_tags import get_existing_groups
from gnowsys_ndf.ndf.views.methods import *

#######################################################################################################################################

db = get_database()
gst_collection = db[GSystemType.collection_name]
gst_group = gst_collection.GSystemType.one({'name': GAPPS[2]})
gs_collection = db[GSystem.collection_name]

#######################################################################################################################################
#      V I E W S   D E F I N E D   F O R   G A P P -- ' G R O U P '
#######################################################################################################################################


def group(request, group_id,app_id):
    """Renders a list of all 'Group-type-GSystems' available within the database.
    """
    group_nodes = []
    col_Group = db[Group.collection_name]
    colg = col_Group.Group.find({'_type': u'Group'})
    colg.sort('name')
    gr = list(colg)
    for items in gr:
            group_nodes.append(items)
    group_nodes_count = len(group_nodes)
    return render_to_response("ndf/group.html", {'group_nodes': group_nodes, 'group_nodes_count': group_nodes_count,'newgroup':group_id}, context_instance=RequestContext(request))
    


def create_group(request,group_id):
    if request.method == "POST":
        col_Group = db[Group.collection_name]
        colg = col_Group.Group()
        cname=request.POST.get('groupname', "")
        colg.altnames=cname
        colg.name = unicode(cname)
        colg.member_of.append(u"Group")
        usrid = int(request.user.id)
        colg.created_by=usrid
        colg.group_type = request.POST.get('group_type', "")
        colg.edit_policy = request.POST.get('edit_policy', "")
        colg.subscription_policy = request.POST.get('subscription', "")
        colg.visibility_policy = request.POST.get('existance', "")
        colg.disclosure_policy = request.POST.get('member', "")
        colg.encryption_policy = request.POST.get('encryption', "")
        print "sub Pol",colg.subscription_policy
        colg.save()
        return render_to_response("ndf/groupdashboard.html",{'groupobj':colg,'node':colg,'user':request.user,'newgroup':group_id},context_instance=RequestContext(request))
    return render_to_response("ndf/create_group.html", RequestContext(request))
    
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
        print "insidegrpdash",group_id
        if group_id == None:
            print "home"
            groupobj=gs_collection.one({'$and':[{'_type':u'Group'},{'name':u'home'}]})
        else:
            print "other grps"    
            groupobj=gs_collection.Group.one({'_id':ObjectId(group_id)})
    except Exception as e:
        groupobj=""
        pass
    print "grpdash-",groupobj
    return render_to_response("ndf/groupdashboard.html",{'newgroup':groupobj,'curgroup':groupobj,'user':request.user},context_instance=RequestContext(request))

def edit_group(request,group_id):
    page_node = gs_collection.GSystem.one({"_id": ObjectId(group_id)})
    if request.method == "POST":
            get_node_common_fields(request, page_node, group_name, gst_group)
            page_node.save()
            group_name=page_node.name
            return HttpResponseRedirect(reverse('groupchange', kwargs={'group_name': group_name,'newgroup':group_id}))
    return render_to_response("ndf/edit_group.html",
                                      { 'node': page_node,
                                        'newgroup':group_id,
                                        'group_name': group_id
                                        },
                                      context_instance=RequestContext(request)
                                      )




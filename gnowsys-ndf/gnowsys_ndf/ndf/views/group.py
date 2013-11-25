''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

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
###########################################################################

db = get_database()
gst_collection = db[GSystemType.collection_name]
gst_group = gst_collection.GSystemType.one({'name': GAPPS[2]})

def group(request, group_id):
    """
    * Renders a list of all 'Group-type-GSystems' available within the database.

    """
    group_nodes=get_existing_groups()
    group_nodes_count = len(group_nodes)
    return render_to_response("ndf/group.html", {'group_nodes': group_nodes, 'group_nodes_count': group_nodes_count}, context_instance=RequestContext(request))
    


def create_group(request):
    if request.method == "POST":
        col_Group = db[Group.collection_name]
        colg = col_Group.Group()
        colg.name = request.POST.get('groupname', "")
        colg.member_of.append(u"Ggroup")
        colg.gtype = request.POST.get('group_type', "")
        colg.edit_policy = request.POST.get('edit_policy', "")
        colg.sub_policy = request.POST.get('subscription', "")
        colg.ex_policy = request.POST.get('existance', "")
        colg.list_member_policy = request.POST.get('member', "")
        colg.encr_policy = request.POST.get('encryption', "")
        colg.save()
    return render_to_response("ndf/create_group.html", RequestContext(request))
    

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
from gnowsys_ndf.ndf.models import Group

###########################################################################

DB = get_database()

def create_group(request):
    if request.method == "POST":
        col_Group = DB[Group.collection_name]
        colg = col_Group.Group()
        colg.name = request.POST.get('groupname', "")
        colg.member_of = u"test"
        colg.gtype = request.POST.get('group_type', "")
        colg.edit_policy = request.POST.get('edit_policy', "")
        colg.sub_policy = request.POST.get('subscription', "")
        colg.ex_policy = request.POST.get('existance', "")
        colg.list_member_policy = request.POST.get('member', "")
        colg.encr_policy = request.POST.get('encryption', "")
        colg.save()
    return render_to_response("ndf/creategroup.html",RequestContext(request))
    

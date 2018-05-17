from gnowsys_ndf.ndf.gstudio_es.node import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from gnowsys_ndf.ndf.views.methods import *



def get_analytics(request,group_id="home"):
	group_name, group_id = get_group_name_id('home')
	# print group_id
	# print request.user
	# print request.path
	return render_to_response("ndf/analytics.html",{ "group_id":group_id,"groupid":group_id },context_instance=RequestContext(request))


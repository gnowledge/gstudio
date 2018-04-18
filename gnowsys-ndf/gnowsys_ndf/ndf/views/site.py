''' -- imports from python libraries -- '''
# import os -- Keep such imports here

''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.views.generic import RedirectView
from gnowsys_ndf.ndf.views.methods import get_execution_time
from gnowsys_ndf.ndf.views.analytics import *

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

@get_execution_time
def site_about(request):
    # page_obj = Node.get_node_by_id(page_id)
    return render_to_response(
                                        "ndf/site_about.html",
                                        {
                                            'title': 'About',
                                        },
                                        context_instance=RequestContext(request)
                                    )
@get_execution_time
def site_credits(request):
    # page_obj = Node.get_node_by_id(page_id)
    return render_to_response(
                                        "ndf/site_credits.html",
                                        {
                                            'title': 'Credits',
                                        },
                                        context_instance=RequestContext(request)
                                    )

@get_execution_time
def site_contact(request):
    # page_obj = Node.get_node_by_id(page_id)
    return render_to_response(
                                        "ndf/site_contact.html",
                                        {
                                            'title': 'Contact',
                                        },
                                        context_instance=RequestContext(request)
                                    )

@get_execution_time
def site_termsofuse(request):
    # page_obj = Node.get_node_by_id(page_id)
    return render_to_response(
                                        "ndf/site_termsofuse.html",
                                        {
                                            'title': 'Terms Of Use',
                                        },
                                        context_instance=RequestContext(request)
                                    )
@get_execution_time
def site_privacypolicy(request):
    # page_obj = Node.get_node_by_id(page_id)
    return render_to_response(
                                        "ndf/site_privacypolicy.html",
                                        {
                                            'title': 'Privacy Policy',
                                        },
                                        context_instance=RequestContext(request)
                                    )
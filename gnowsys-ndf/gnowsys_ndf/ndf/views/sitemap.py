# from django.contrib.sitemaps import Sitemap
from gnowsys_ndf.ndf.models import *
from django.shortcuts import render_to_response  # , render  uncomment when to use
from django.template import RequestContext
import datetime

def sitemap(request):
    print "******************* Inseide sitemap"

    return render_to_response("ndf/sitemap.html",
                                {"name":"name"},
                                context_instance = RequestContext(request)
    )
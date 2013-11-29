''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import GSystemType

#######################################################################################################################################

db = get_database()
gst_collection = db[GSystemType.collection_name]

#######################################################################################################################################
#                                                                                           V I E W S   D E F I N E D   F O R   H O M E
#######################################################################################################################################


def homepage(request):
    gst_collection = db[GSystemType.collection_name]
    gst_cur = gst_collection.GSystemType.find()
    
    gapps = {}
    for app in gst_cur:
        gapps[app._id] = app.name.lower()

    return render_to_response("ndf/base.html", {'gapps': gapps}, context_instance=RequestContext(request))

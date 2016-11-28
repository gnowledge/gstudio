import json
from django.http import HttpResponseRedirect
from django.http import HttpResponse
''' -- imports from installed packages -- ''' 
from django.shortcuts import render_to_response
from django.template import RequestContext
from gnowsys_ndf.ndf.views.methods import get_group_name_id
try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
# from gnowsys_ndf.ndf.models import Node, GRelation, GSystemType, File, Triple
from gnowsys_ndf.ndf.models import node_collection

ebook_gst = node_collection.one({'_type':'GSystemType', 'name': u"E-Book"})
GST_FILE = node_collection.one({'_type':'GSystemType', 'name': u"File"})
GST_PAGE = node_collection.one({'_type':'GSystemType', 'name': u'Page'})


def jhapp(request, group_id):
  try:
      group_id = ObjectId(group_id)
  except:
      group_name, group_id = get_group_name_id(group_id)

  return render_to_response("ndf/jhapp.html",RequestContext(request, {"groupid":group_id, "group_id":group_id}))
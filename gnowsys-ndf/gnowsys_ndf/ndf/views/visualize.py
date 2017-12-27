''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json, ast
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''

from gnowsys_ndf.settings import GAPPS
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.views.file import *
from gnowsys_ndf.ndf.rcslib import RCS
# from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.templatetags.ndf_tags import group_type_info

#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
@get_execution_time
def graphs(request,group_id):
		# HttpResponseRedirect("ndf/visualize.html",
		# 					 	{
		# 					 		'groupid':group_id, 'group_id':group_id,
		# 					 	},
		# 					 	# context_instance=RequestContext(request)
		# 					 )
	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
	    group_ins = node_collection.find_one({'_type': "Group","name": group_id})
	    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	    if group_ins:
	        group_id = str(group_ins._id)
	    else :
	        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
	        if auth :
	            group_id = str(auth._id)

	return render_to_response("ndf/visualize.html", {'group_id': group_id, 'groupid': group_id }, context_instance=RequestContext(request))

# def graph_display(request, group_id):
# 	ns_objectid  = ObjectId()
# 	if ins_objectid.is_valid(group_id) is False :
# 	    group_ins = node_collection.find_one({'_type': "Group","name": group_id})
# 	    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
# 	    if group_ins:
# 	        group_id = str(group_ins._id)
# 	    else :
# 	        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
# 	        if auth :
# 	            group_id = str(auth._id)

# 	return render(request, 'ndf/graph_display.html', {"groupid":group_id})

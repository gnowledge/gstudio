''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from django_mongokit import get_database
from mongokit import paginator

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''

from gnowsys_ndf.ndf.models import Node, Triple
from gnowsys_ndf.ndf.views.methods import get_node_common_fields
#######################################################################################################################################
db = get_database()
collection = db[Node.collection_name]

def term(request, group_id):

	ins_objectid  = ObjectId()
	if ins_objectid.is_valid(group_id) is False :
		group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
		auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
		if group_ins:
			group_id = str(group_ins._id)
		else :
			auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
			if auth :
				group_id = str(auth._id)
	else :
		pass


  	

 	return render_to_response("ndf/terms_list.html",
                               {'group_id': group_id,'groupid': group_id},
                              context_instance = RequestContext(request)
    )
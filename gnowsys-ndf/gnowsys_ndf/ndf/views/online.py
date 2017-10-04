'''


''' -- imports from installed packages -- '''
import json

from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template import Context
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from datetime import datetime

from django_mongokit import get_database
from gnowsys_ndf.ndf.views.methods import get_forum_repl_type,forum_notification_status
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem,Node
from gnowsys_ndf.ndf.views.notify import set_notif_val
import datetime
# from gnowsys_ndf.ndf.org2any import org2html
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

##################
collection = get_database()[Node.collection_name]
##################

def tests(request, group_id):
    """Renders a list of all 'Page-type-GSystems' available within the database.
    """
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

    #print "\n inside meeting \n"
    #print "\ngroup_id: ", group_id,"\n"

    return render_to_response("ndf/online.html",{'groupid': group_id},context_instance=RequestContext(request))
'''

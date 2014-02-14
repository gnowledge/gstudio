#from django.http import HttpResponseRedirect
#from django.http import HttpResponse
from django.shortcuts import render_to_response #render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
#from django.contrib.auth.decorators import login_required
from django_mongokit import get_database


try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import GSystemType, Node 


db = get_database()
collection = db[Node.collection_name]
GST_COLLECTION = db[GSystemType.collection_name]
GST_MODULE = GST_COLLECTION.GSystemType.one({'name': GAPPS[8]})

def module(request, group_name, module_id):
    """
   * Renders a list of all 'modules' available within the database.
    """
    if GST_MODULE._id == ObjectId(module_id):
        title = GST_MODULE.name
        module_coll = collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(module_id)]}, 'group_set': {'$all': [group_name]}})
        template = "ndf/module.html"
        variable = RequestContext(request, {'module_coll': module_coll })
        return render_to_response(template, variable)

    

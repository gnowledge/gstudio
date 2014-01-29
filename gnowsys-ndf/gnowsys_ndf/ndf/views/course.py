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
GST_COURSE = GST_COLLECTION.GSystemType.one({'name': GAPPS[7]})

def course(request, group_name, course_id):
    """
   * Renders a list of all 'courses' available within the database.
    """
    if GST_COURSE._id == ObjectId(course_id):
        title = GST_COURSE.name
        course_coll = collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(course_id)]}, 'group_set': {'$all': [group_name]}})
        template = "ndf/course.html"
        variable = RequestContext(request, {'course_coll': course_coll })
        return render_to_response(template, variable)

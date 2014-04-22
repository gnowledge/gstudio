from django.http import HttpResponseRedirect
#from django.http import HttpResponse
from django.shortcuts import render_to_response #render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
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

def module(request, group_id, module_id):
    """
   * Renders a list of all 'modules' available within the database.
    """
    if GST_MODULE._id == ObjectId(module_id):
        title = GST_MODULE.name
        module_coll = collection.GSystem.find({'member_of': {'$all': [ObjectId(module_id)]}, 'group_set': {'$all': [ObjectId(group_id)]}})
        template = "ndf/module.html"
        variable = RequestContext(request, {'module_coll': module_coll,'group_id':group_id,'groupid':group_id })
        return render_to_response(template, variable)


def module_detail(request, group_id, _id):
    course_node = collection.Node.one({"_id": ObjectId(_id)})
    return render_to_response("ndf/module_detail.html",
                                  { 'node': course_node,
                                    'groupid': group_id,
                                    'group_id':group_id
                                  },
                                  context_instance = RequestContext(request)
        )

    
@login_required    
def delete_module(request, group_id, _id):
    """This method will delete module object and its Attribute and Relation
    """
    pageurl = request.GET.get("next", "")
    try:
        node = collection.Node.one({'_id':ObjectId(_id)})
        if node:
            attributes = collection.Triple.find({'_type':'GAttribute','subject':node._id})
            relations = collection.Triple.find({'_type':'GRelation','subject':node._id})
            if attributes.count() > 0:
                for each in attributes:
                    collection.Triple.one({'_id':each['_id']}).delete()
                    
            if relations.count() > 0:
                for each in relations:
                    collection.Triple.one({'_id':each['_id']}).delete()
            node.delete()
    except Exception as e:
        print "Exception:", e
    return HttpResponseRedirect(pageurl) 

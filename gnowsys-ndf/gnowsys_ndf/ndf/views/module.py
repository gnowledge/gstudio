from django.http import HttpResponseRedirect
#from django.http import HttpResponse
from django.shortcuts import render_to_response #render  uncomment when to use
from django.template import RequestContext
# from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


from gnowsys_ndf.settings import GAPPS  # , MEDIA_ROOT
from gnowsys_ndf.ndf.models import GSystemType, Node
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import get_execution_time
GST_MODULE = node_collection.one({'_type': "GSystemType", 'name': GAPPS[8]})
app = GST_MODULE

@get_execution_time
def module(request, group_id, module_id=None):
    """
    * Renders a list of all 'modules' available within the database.
    """
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #   group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #   auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #   if group_ins:
    #     group_id = str(group_ins._id)
    #   else :
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if auth :
    #       group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    
    if module_id is None:
      module_ins = node_collection.find_one({'_type':"GSystemType", "name":"Module"})
      if module_ins:
        module_id = str(module_ins._id)
    
    if request.method == "POST":
      # Module search view
      title = GST_MODULE.name
      
      search_field = request.POST['search_field']
      module_coll = node_collection.find({'member_of': {'$all': [ObjectId(GST_MODULE._id)]},
                                         '$or': [{'name': {'$regex': search_field, '$options': 'i'}}, 
                                                 {'tags': {'$regex':search_field, '$options': 'i'}}], 
                                         'group_set': {'$all': [ObjectId(group_id)]}
                                     }).sort('last_update', -1)

      # module_nodes_count = course_coll.count()

      return render_to_response("ndf/module.html",
                                {'title': title,
                                 'appId':app._id,
                                 'searching': True, 'query': search_field,
                                 'module_coll': module_coll, 'groupid':group_id, 'group_id':group_id
                                }, 
                                context_instance=RequestContext(request)
                                )

    elif GST_MODULE._id == ObjectId(module_id):
      # Module list view
      title = GST_MODULE.name
      module_coll = node_collection.find({'member_of': {'$all': [ObjectId(module_id)]}, 'group_set': {'$all': [ObjectId(group_id)]}})
      template = "ndf/module.html"
      variable = RequestContext(request, {'title': title, 'appId':app._id, 'module_coll': module_coll, 'group_id': group_id, 'groupid': group_id})
      return render_to_response(template, variable)

@get_execution_time
def module_detail(request, group_id, _id):
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group","name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    course_node = node_collection.one({"_id": ObjectId(_id)})
    if course_node._type == "GSystemType":
	return module(request, group_id, _id)
    return render_to_response("ndf/module_detail.html",
                                  { 'node': course_node,
                                    'appId':app._id,
                                    'groupid': group_id,
                                    'group_id':group_id
                                  },
                                  context_instance = RequestContext(request)
        )


    
@login_required
@get_execution_time    
def delete_module(request, group_id, _id):
    """This method will delete module object and its Attribute and Relation
    """
    # ins_objectid  = ObjectId()
    # if ins_objectid.is_valid(group_id) is False :
    #     group_ins = node_collection.find_one({'_type': "Group", "name": group_id})
    #     auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #     if group_ins:
    #         group_id = str(group_ins._id)
    #     else :
    #         auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    #         if auth :
    #             group_id = str(auth._id)
    # else :
    #     pass
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
        
    pageurl = request.GET.get("next", "")
    try:
        node = node_collection.one({'_id': ObjectId(_id)})
        if node:
            attributes = triple_collection.find({'_type': 'GAttribute', 'subject': node._id})
            relations = triple_collection.find({'_type': 'GRelation', 'subject': node._id})
            if attributes.count() > 0:
                for each in attributes:
                    triple_collection.one({'_id': each['_id']}).delete()
                    
            if relations.count() > 0:
                for each in relations:
                    triple_collection.one({'_id': each['_id']}).delete()
            node.delete()
    except Exception as e:
        print "Exception:", e
    return HttpResponseRedirect(pageurl)

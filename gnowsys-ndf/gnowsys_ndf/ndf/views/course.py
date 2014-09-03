from django.http import HttpResponseRedirect
from django.http import HttpResponse
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
from gnowsys_ndf.ndf.views.methods import get_node_common_fields

collection = get_database()[Node.collection_name]
GST_COURSE = collection.Node.one({'_type': "GSystemType", 'name': GAPPS[7]})
app = collection.Node.one({'_type': "GSystemType", 'name': GAPPS[7]})

def course(request, group_id, course_id=None):
    """
    * Renders a list of all 'courses' available within the database.
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
    
    if course_id is None:
      course_ins = collection.Node.find_one({'_type':"GSystemType", "name":"Course"})
      if course_ins:
        course_id = str(course_ins._id)

    if request.method == "POST":
      # Course search view
      title = GST_COURSE.name
      
      search_field = request.POST['search_field']
      course_coll = collection.Node.find({'member_of': {'$all': [ObjectId(GST_COURSE._id)]},
                                         '$or': [
                                            {'$and': [
                                              {'name': {'$regex': search_field, '$options': 'i'}}, 
                                              {'$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                ]
                                              }
                                              ]
                                            },
                                            {'$and': [
                                              {'tags': {'$regex':search_field, '$options': 'i'}},
                                              {'$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                ]
                                              }
                                              ]
                                            }
                                          ],
                                         'group_set': {'$all': [ObjectId(group_id)]}
                                     }).sort('last_update', -1)

      # course_nodes_count = course_coll.count()

      return render_to_response("ndf/course.html",
                                {'title': title,
                                 'appId':app._id,
                                 'searching': True, 'query': search_field,
                                 'course_coll': course_coll, 'groupid':group_id, 'group_id':group_id
                                }, 
                                context_instance=RequestContext(request)
                                )

    elif GST_COURSE._id == ObjectId(course_id):
      # Course list view
      title = GST_COURSE.name
      course_coll = collection.GSystem.find({'member_of': {'$all': [ObjectId(course_id)]}, 
                                             'group_set': {'$all': [ObjectId(group_id)]},
                                             '$or': [
                                              {'access_policy': u"PUBLIC"},
                                              {'$and': [
                                                {'access_policy': u"PRIVATE"}, 
                                                {'created_by': request.user.id}
                                                ]
                                              }
                                             ]
                                            })
      template = "ndf/course.html"
      variable = RequestContext(request, {'title': title, 'course_nodes_count': course_coll.count(), 'course_coll': course_coll, 'groupid':group_id, 'appId':app._id, 'group_id':group_id})
      return render_to_response(template, variable)

@login_required
def create_edit(request, group_id, node_id = None):
    """Creates/Modifies details about the given quiz-item.
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
    context_variables = { 'title': GST_COURSE.name,
                          'group_id': group_id,
                          'groupid':group_id
                      }

    if node_id:
        course_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
    else:
        course_node = collection.GSystem()

    if request.method == "POST":
        # get_node_common_fields(request, course_node, group_id, GST_COURSE)
        course_node.save(is_changed=get_node_common_fields(request, course_node, group_id, GST_COURSE))
        return HttpResponseRedirect(reverse('course', kwargs={'appId':app._id,'group_id': group_id}))
        
    else:
        if node_id:
            context_variables['node'] = course_node
            context_variables['groupid']=group_id
            context_variables['group_id']=group_id
            context_variables['appId']=app._id
        return render_to_response("ndf/course_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )

def course_detail(request, group_id, _id):
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
    course_node = collection.Node.one({"_id": ObjectId(_id)})
    if course_node._type == "GSystemType":
	return course(request, group_id, _id)
    return render_to_response("ndf/course_detail.html",
                                  { 'node': course_node,
                                    'groupid': group_id,
                                    'group_id':group_id,
                                    'appId':app._id
                                  },
                                  context_instance = RequestContext(request)
        )

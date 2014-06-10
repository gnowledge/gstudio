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
GST_BATCH = collection.GSystemType.one({'name': GAPPS[9]})

def batch(request, group_id):
    """
   * Renders a list of all 'modules' available within the database.
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
    batch_coll = collection.GSystem.find({'member_of': {'$all': [GST_BATCH._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
    users_in_group = collection.Node.one({'_id':ObjectId(group_id)}).author_set
    template = "ndf/batch.html"
    variable = RequestContext(request, {'batch_coll': batch_coll,'group_id':group_id, 'groupid':group_id,'title':GST_BATCH.name,'st_batch_id':GST_BATCH._id,'users_in_group':users_in_group})
    return render_to_response(template, variable)

def create_and_edit(request, group_id, _id = None):
        fc_courses = []
        batch = ""
        batch_count = ""
        course_name = ""
        if request.method == 'POST':
            batch_count = request.POST.get('batch_count','')
        group = collection.Node.one({"_id":ObjectId(group_id)})
        fc_st = collection.Node.one({'_type':'GSystemType','name':'Foundation Course'})
        rt_has_course = collection.Node.one({'_type':'RelationType', 'name':'has_course'})
        if _id:
            batch = collection.Node.one({'_id':ObjectId(_id)})
        if fc_st:
            fc_courses = collection.Node.find({'member_of': {'$all': [fc_st._id]}})
            
        if rt_has_course and _id:
            course = collection.Triple.one({'relation_type.$id':rt_has_course._id,'right_subject':ObjectId(_id)})
            if course:
                course_name = collection.Node.one({'_id':ObjectId(course.subject)}).name

        template = "ndf/create_batch.html"
        variable = RequestContext(request, {'group_id':group_id, 'groupid':group_id,'title':GST_BATCH.name,'batch_count':batch_count,'st_batch_id':GST_BATCH._id,'fc_courses':fc_courses,'batch':batch,'course_name':course_name,'batch_count':1})
        return render_to_response(template, variable)
    
def save_and_update(request, group_id):
    if request.method == 'POST':
        users = request.POST.get('collection_set_list', '')
        user_list = users.split(',')
        batch_name = request.POST.get('batch_name', '')
        batch_count = request.POST.get('batch_count', '')
        course_id = request.POST.get('courses', '')
        node_id = request.POST.get('node_id', '')
        if node_id:
            new_batch = collection.Node.one({'_id':ObjectId(node_id)})
            new_batch.author_set = []
        else:
            new_batch = collection.GSystem()
        new_batch.name = batch_name
        for each in user_list:
            new_batch.author_set.append(int(each))
        new_batch.member_of.append(GST_BATCH._id)
        new_batch.created_by = int(request.user.id)
        new_batch.group_set.append(ObjectId(group_id))
        new_batch.contributors.append(int(request.user.id))
        new_batch.modified_by = int(request.user.id)
        new_batch.save()
        if course_id:
            save_course(course_id, new_batch._id)
        batch_count = int(batch_count) - 1
        fc_st = collection.Node.one({'_type':'GSystemType','name':'Foundation Course'})
        if fc_st:
            fc_courses = collection.Node.find({'member_of': {'$all': [fc_st._id]}})
        if batch_count == 0:
            return HttpResponseRedirect('/'+group_id+'/'+'batch')
        else:
            template = "ndf/create_batch.html"
            variable = RequestContext(request, {'group_id':group_id, 'groupid':group_id,'title':GST_BATCH.name, 'batch_count':batch_count,'st_batch_id':GST_BATCH._id,'fc_courses':fc_courses})
        return render_to_response(template, variable)


def save_course(course_id, right_subject_id):
    rt_has_course = collection.Node.one({'_type':'RelationType', 'name':'has_course'})
    if rt_has_course and course_id and right_subject_id:
        course = collection.Triple.one({'relation_type.$id':rt_has_course._id,'right_subject':ObjectId(right_subject_id)})
        if course:
            relation = collection.Node.one({'_id':ObjectId(course.subject)})
        else:
            relation = collection.GRelation()                         #instance of GRelation class
        relation.relation_type = rt_has_course
        relation.right_subject = right_subject_id
        relation.subject = ObjectId(course_id)
        relation.save()

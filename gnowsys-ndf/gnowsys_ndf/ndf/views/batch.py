from django.http import HttpResponseRedirect
#from django.http import HttpResponse
from django.shortcuts import render_to_response #render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django_mongokit import get_database
import json  

from mongokit import IS
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import GSystemType, Node
from gnowsys_ndf.ndf.views.methods import create_grelation

db = get_database()
collection = db[Node.collection_name]
GST_BATCH = collection.GSystemType.one({'name': GAPPS[9]})
app = collection.GSystemType.one({'name': GAPPS[9]})

def batch(request, group_id):
    """
   * Renders a list of all 'batches' available within the database.
    """
    ins_objectid  = ObjectId()
    st_student = collection.Node.one({'_type':'GSystemType','name':'Student'})
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
    st_student = collection.Node.one({'_type':'GSystemType','name':'Student'})
    student_coll = collection.GSystem.find({'member_of': {'$all': [st_student._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
    #users_in_group = collection.Node.one({'_id':ObjectId(group_id)}).author_set
    template = "ndf/batch.html"
    variable = RequestContext(request, {'batch_coll': batch_coll,'appId':app._id, 'group_id':group_id, 'groupid':group_id,'title':GST_BATCH.name,'st_batch_id':GST_BATCH._id,'student_count':student_coll.count()})
    return render_to_response(template, variable)


def new_create_and_edit(request, group_id, _id = None):
    node = ""
    count = ""
    batch_count = 1
    batch = ""
    if request.method == 'POST':
        batch_count = int(request.POST.get('batch_count',''))
    st_student = collection.Node.one({'_type':'GSystemType','name':'Student'})
    student_coll = collection.GSystem.find({'member_of': {'$all': [st_student._id]}, 'group_set': {'$all': [ObjectId(group_id)]}})
    if _id:
        batch = collection.Node.one({'_id':ObjectId(_id)})
        variable = RequestContext(request, {'group_id':group_id, 'appId':app._id,'groupid':group_id,'title':GST_BATCH.name,'st_batch_id':GST_BATCH._id,'student_count':student_coll.count(), 'node':batch})
    else:
        fetch_ATs = ["nussd_course_type"]
        req_ATs = []

        for each in fetch_ATs:
            each = collection.Node.one({'_type': "AttributeType", 'name': each}, {'_type': 1, '_id': 1, 'data_type': 1, 'complex_data_type': 1, 'name': 1, 'altnames': 1})

            if each["data_type"] == "IS()":
                dt = "IS("
                for v in each.complex_data_type:
                    dt = dt + "u'" + v + "'" + ", " 
                dt = dt[:(dt.rfind(", "))] + ")"
                each["data_type"] = dt

            each["data_type"] = eval(each["data_type"])
            each["value"] = None
            req_ATs.append(each)
        variable = RequestContext(request, {'group_id':group_id, 'appId':app._id,'ATs': req_ATs, 'groupid':group_id,'title':GST_BATCH.name,'batch_count':xrange(batch_count),'st_batch_id':GST_BATCH._id,'student_count':student_coll.count(),'count':batch_count, 'node':batch})
    
    template = "ndf/new_create_batch.html"
    return render_to_response(template, variable)

        
def save_students_for_batches(request, group_id):
    '''
    This save method creates new  and update existing the batches
    '''
    print "in views"
    if request.method == 'POST':
        batch_user_list_v = request.POST.get('batch_user_list_dict', '')
        print "\nbefore",batch_user_list_v
        batch_user_list_v = json.loads(batch_user_list_v)
        print "\nafter",batch_user_list_v
        ac_id = request.POST.get('ac_id', '')
        print "batch_user_list_v",batch_user_list_v
        for k,v in batch_user_list_v.items():
            save_batch(k,v, group_id, request, ac_id, None)
        return HttpResponseRedirect(reverse('batch',kwargs={'group_id':group_id}))


def save_batch(batch_name, user_list, group_id, request, ac_id, node_id):
    print "batch_name",batch_name,"\n\nuser list",user_list
    new_batch = collection.GSystem()
    new_batch.member_of.append(GST_BATCH._id)

    new_batch.created_by = int(request.user.id)
    new_batch.group_set.append(ObjectId(group_id))
    new_batch.name = batch_name
    new_batch.contributors.append(int(request.user.id))
    new_batch.modified_by = int(request.user.id)
    new_batch.save()
    all_batches_in_grp=[]

    rt_has_batch_member = collection.Node.one({'_type':'RelationType', 'name':'has_batch_member'})
    rt_group_has_batch = collection.Node.one({'_type':'RelationType', 'name':'group_has_batch'})
    rt_has_course = collection.Node.one({'_type':'RelationType', 'name':'has_course'})
    relation_coll = collection.Triple.find({'_type':'GRelation','relation_type.$id':rt_group_has_batch._id,'subject':ObjectId(group_id)})
    
    for each in relation_coll:
        all_batches_in_grp.append(each.right_subject)
        #to get all batches of the group
    
    create_grelation(new_batch._id,rt_has_batch_member,user_list)

    create_grelation(new_batch._id,rt_has_course,ObjectId(ac_id))
    all_batches_in_grp.append(new_batch._id)

    create_grelation(ObjectId(group_id),rt_group_has_batch,all_batches_in_grp)
    return new_batch._id


def detail(request, group_id, _id):
    student_coll = []
    node = collection.Node.one({'_id':ObjectId(_id)})
    rt_has_batch_member = collection.Node.one({'_type':'RelationType','name':'has_batch_member'})
    relation_coll = collection.Triple.find({'_type':'GRelation','relation_type.$id':rt_has_batch_member._id,'subject':node._id})
    
    for each in relation_coll:
        n = collection.Node.one({'_id':ObjectId(each.right_subject)})
        student_coll.append(n)
    template = "ndf/batch_detail.html"
    variable = RequestContext(request, {'node':node, 'appId':app._id, 'groupid':group_id, 'group_id': group_id,'title':GST_BATCH.name, 'student_coll':student_coll})
    return render_to_response(template, variable)

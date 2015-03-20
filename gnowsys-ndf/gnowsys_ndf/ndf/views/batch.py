from django.http import HttpResponseRedirect
#from django.http import HttpResponse
from django.shortcuts import render_to_response #render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
import json

from mongokit import IS
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import GSystemType, Node
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import create_grelation,get_execution_time

GST_BATCH = node_collection.one({"_type": "GSystemType", 'name': "Batch"})
app = GST_BATCH


@get_execution_time
def batch(request, group_id):
    """
   * Renders a list of all 'batches' available within the database.
    """
    ins_objectid  = ObjectId()
    st_student = node_collection.one({'_type':'GSystemType','name':'Student'})
    if ins_objectid.is_valid(group_id) is False :
        group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    nussd_course_type_name = ""
    announced_course_name = ""
    print group_id

    if request.method == "POST":
      announced_course_name = request.POST.get("announced_course_name", "")
      nussd_course_type_name = request.POST.get("nussd_course_name","")
      colg_gst = node_collection.one({'_type': "GSystemType", 'name': 'College'})
      req_colg_id = node_collection.one({'member_of':colg_gst._id,'relation_set.has_group':ObjectId(group_id)})
      batch_coll = node_collection.find({'member_of':GST_BATCH._id,'relation_set.has_course':ObjectId(announced_course_name)})
      # for each_batch in batch_coll:
      #   each_batch['batch_name_human_readble'] = (each_batch.name).replace('_',' ')
    else:
      batch_coll = node_collection.find({'member_of': GST_BATCH._id,'relation_set.batch_in_group':ObjectId(group_id)})
    fetch_ATs = ["nussd_course_type"]
    req_ATs = []
    for each in fetch_ATs:
      each = node_collection.one({'_type': "AttributeType", 'name': each}, {'_type': 1, '_id': 1, 'data_type': 1, 'complex_data_type': 1, 'name': 1, 'altnames': 1})

      if each["data_type"] == "IS()":
          dt = "IS("
          for v in each.complex_data_type:
              dt = dt + "u'" + v + "'" + ", " 
          dt = dt[:(dt.rfind(", "))] + ")"
          each["data_type"] = dt

      each["data_type"] = eval(each["data_type"])
      each["value"] = None
      req_ATs.append(each)

    #users_in_group = node_collection.one({'_id':ObjectId(group_id)}).author_set
    template = "ndf/batch.html"
    variable = RequestContext(request, {'batch_coll': batch_coll,'appId':app._id,'nussd_course_name_var':nussd_course_type_name,'announced_course_name_var':announced_course_name, 'ATs': req_ATs,'group_id':group_id, 'groupid':group_id,'title':GST_BATCH.name,'st_batch_id':GST_BATCH._id})
    return render_to_response(template, variable)


@get_execution_time
def new_create_and_edit(request, group_id, _id=None):
    node = ""
    count = ""
    batch = ""
    batch_count = 1
    ac = None
    nussd_course_name = ""

    if request.method == 'POST':
        batch_count = int(request.POST.get('batch_count', ''))

    st_student = node_collection.one({'_type':'GSystemType','name':'Student'})
    student_coll = node_collection.find(
        {'member_of': st_student._id, 'group_set': ObjectId(group_id)}
    )

    if _id:
        batch = node_collection.one(
            {'_id':ObjectId(_id)}, 
            {'relation_set.has_course': 1, 'name': 1}
        )

        for each in batch.relation_set:
            if "has_course" in each.keys():
                ac_id_of_batch = each["has_course"][0]

        ac = node_collection.one(
            {'_id': ObjectId(ac_id_of_batch), 'attribute_set.nussd_course_type': {'$exists': True}},
            {'attribute_set.nussd_course_type': 1}
        )

        if ac:
            for attr in ac.attribute_set:
                if attr and attr.has_key("nussd_course_type"):
                    nussd_course_name = attr["nussd_course_type"]
                    break

    fetch_ATs = ["nussd_course_type"]
    req_ATs = []
    for each in fetch_ATs:
        each = node_collection.one({'_type': "AttributeType", 'name': each}, {'_type': 1, '_id': 1, 'data_type': 1, 'complex_data_type': 1, 'name': 1, 'altnames': 1})

        if each["data_type"] == "IS()":
            dt = "IS("
            for v in each.complex_data_type:
                dt = dt + "u'" + v + "'" + ", " 
            dt = dt[:(dt.rfind(", "))] + ")"
            each["data_type"] = dt

        each["data_type"] = eval(each["data_type"])
        each["value"] = None
        req_ATs.append(each)
    
    variable = RequestContext(request, {
        'group_id': group_id, 'groupid': group_id, 
        'appId': app._id, 'title': GST_BATCH.name, 'ATs': req_ATs,
        'count':batch_count, 'batch_count': xrange(batch_count), 'st_batch_id': GST_BATCH._id, 
        'ac_node': ac, 
        'student_count': student_coll.count(), 
        'nussd_course_name': nussd_course_name, 
        'node': batch
    })
    
    template = "ndf/new_create_batch.html"
    return render_to_response(template, variable)

@get_execution_time        
def save_students_for_batches(request, group_id):
    '''
    This save method creates new  and update existing the batches
    '''
    edit_batch = []
    if request.method == 'POST':
        batch_user_list = request.POST.get('batch_user_list_dict', '')
        batch_user_list = json.loads(batch_user_list)
        ac_id = request.POST.get('ac_id', '')

        for k,v in batch_user_list.items():
            save_batch(k,v, group_id, request, ac_id)
        return HttpResponseRedirect(reverse('batch',kwargs={'group_id':group_id}))

@get_execution_time
def save_batch(batch_name, user_list, group_id, request, ac_id):

    rt_has_batch_member = node_collection.one({'_type':'RelationType', 'name':'has_batch_member'})
    all_batches_in_grp=[]
    b_node = node_collection.one({'member_of':GST_BATCH._id,'name':unicode(batch_name)})
    if not b_node:
        b_node = node_collection.collection.GSystem()
        b_node.member_of.append(GST_BATCH._id)
        b_node.created_by = int(request.user.id)
        b_node.group_set.append(ObjectId(group_id))
        b_node.name = batch_name
        b_node.name = batch_name
        b_node['altnames'] = batch_name.replace('_',' ')

        b_node.contributors.append(int(request.user.id))
        b_node.modified_by = int(request.user.id)
        b_node.save()
        all_batches_in_grp.append(b_node._id)

    rt_group_has_batch = node_collection.one({'_type':'RelationType', 'name':'group_has_batch'})
    rt_has_course = node_collection.one({'_type':'RelationType', 'name':'has_course'})
    
    relation_coll = triple_collection.find({'_type':'GRelation','relation_type.$id':rt_group_has_batch._id,'subject':ObjectId(group_id)})
    
    for each in relation_coll:
        all_batches_in_grp.append(each.right_subject)
        #to get all batches of the group
    
    create_grelation(b_node._id,rt_has_batch_member,user_list)

    create_grelation(b_node._id,rt_has_course,ObjectId(ac_id))
   
    create_grelation(ObjectId(group_id),rt_group_has_batch,all_batches_in_grp)

@get_execution_time
def detail(request, group_id, _id):
    student_coll = []
    node = node_collection.one({'_id':ObjectId(_id)})
    rt_has_batch_member = node_collection.one({'_type':'RelationType','name':'has_batch_member'})
    relation_coll = triple_collection.find({'_type':'GRelation','relation_type.$id':rt_has_batch_member._id,'subject':node._id,'status':u'PUBLISHED'})
    
    for each in relation_coll:
        n = node_collection.one({'_id':ObjectId(each.right_subject)})
        student_coll.append(n)
    template = "ndf/batch_detail.html"
    variable = RequestContext(request, {'node':node,'node_name_human_readable':(node.name).replace('_',' '), 'appId':app._id, 'groupid':group_id, 'group_id': group_id,'title':GST_BATCH.name, 'student_coll':student_coll})
    return render_to_response(template, variable)


@login_required
@get_execution_time
def delete_batch(request,group_id,_id):
    if ObjectId.is_valid(group_id) is False :
        group_ins = node_collection.find_one({'_type': "Group","name": group_id})
        auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass

    node = node_collection.one({ '_id': ObjectId(_id)})
    left_relations = triple_collection.find({"_type":"GRelation", "subject":node._id})
    right_relations = triple_collection.find({"_type":"GRelation", "right_subject":node._id})
    attributes = triple_collection.find({"_type":"GAttribute", "subject":node._id})

    for eachobject in right_relations:
        # If given node is used in relationship with any other node (as right_subject)
        # Then this node's ObjectId must be removed from relation_set field of other node
        node_collection.collection.update(
            {'_id': eachobject.subject, 'relation_set.'+eachobject.relation_type.name: {'$exists': True}}, 
            {'$pull': {'relation_set.$.'+eachobject.relation_type.name: node._id}}, 
            upsert=False, multi=False
        )
        eachobject.delete()

    all_associates = list(left_relations)+list(attributes)
    # Deleting GAttributes and GRelations where given node is used as left subject
    for eachobject in all_associates:
        eachobject.delete()

    # Finally deleting given node
    node.delete()
    return HttpResponseRedirect(reverse('batch', kwargs={'group_id': group_id}))

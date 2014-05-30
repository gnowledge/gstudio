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

def create(request, group_id):
    if request.method == 'POST':
        batch_count = request.POST.get('batch_count','')
        group = collection.Node.one({"_id":ObjectId(group_id)})
        template = "ndf/create_batch.html"
        variable = RequestContext(request, {'group_id':group_id, 'groupid':group_id,'title':GST_BATCH.name,'batch_count':batch_count,'st_batch_id':GST_BATCH._id})
        return render_to_response(template, variable)
    
def save(request, group_id):
    if request.method == 'POST':
        users = request.POST.get('collection_set_list','')
        user_list = users.split(',')
        batch_name = request.POST.get('batch_name','')
        batch_count = request.POST.get('batch_count','')
        print request.user.id
        #course

        new_batch = collection.GSystem()
        new_batch.name = batch_name
        for each in user_list:
            new_batch.author_set.append(int(each))
        new_batch.member_of.append(GST_BATCH._id)
        new_batch.created_by = request.user.id
        new_batch.group_set.append(ObjectId(group_id))
        new_batch.save()
        batch_count = int(batch_count) - 1
        if batch_count == 0:
            return HttpResponseRedirect('/'+group_id+'/'+'batch')
        else:
            template = "ndf/create_batch.html"
            variable = RequestContext(request, {'group_id':group_id, 'groupid':group_id,'title':GST_BATCH.name, 'batch_count':batch_count,'st_batch_id':GST_BATCH._id})
        return render_to_response(template, variable)

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
from gnowsys_ndf.ndf.models import File

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import META_TYPE, GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_node_common_fields,create_grelation_list,get_execution_time
from gnowsys_ndf.ndf.views.methods import get_node_metadata, node_thread_access, create_thread_for_node
from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute
from gnowsys_ndf.ndf.views.methods import get_node_metadata, get_node_common_fields, create_gattribute, get_page, get_execution_time,set_all_urls,get_group_name_id 
gapp_mt = node_collection.one({'_type': "MetaType", 'name': META_TYPE[0]})
GST_AUDIO = node_collection.one({'member_of': gapp_mt._id, 'name': GAPPS[3]})

@get_execution_time
def audioDashboard(request, group_id, audio_id=None):

    '''
    fetching audio files acording to group name
    '''
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    if audio_id is None:
        audio_ins = node_collection.find_one({'_type': "GSystemType", "name": "Audio"})
        print "audio_ins",audio_ins
        if audio_ins:
            audio_id = str(audio_ins._id)
    audio_col = node_collection.find({'_type': 'File', 'member_of': {'$all': [ObjectId(audio_id)]}, 'group_set': {'$all': [ObjectId(group_id)]}})
    # print "***********audio_col",audio_col
    template = "ndf/audioDashboard.html"
    already_uploaded=request.GET.getlist('var',"")
    variable = RequestContext(request, {'audioCollection': audio_col,'already_uploaded':already_uploaded,'groupid':group_id,'group_id':group_id })
    return render_to_response(template, variable)

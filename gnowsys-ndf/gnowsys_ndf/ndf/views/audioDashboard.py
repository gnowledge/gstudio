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
# from gnowsys_ndf.ndf.models import File

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import META_TYPE, GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_node_common_fields,create_grelation_list,get_execution_time
from gnowsys_ndf.ndf.views.methods import get_node_metadata, node_thread_access, create_thread_for_node
from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute
from gnowsys_ndf.ndf.views.methods import get_node_metadata, get_node_common_fields, create_gattribute, get_page, get_execution_time,set_all_urls,get_group_name_id 
gapp_mt = node_collection.one({'_type': "MetaType", 'name': META_TYPE[0]})
GST_AUDIO = node_collection.one({'member_of': gapp_mt._id, 'name': GAPPS[3]})
file_gst = node_collection.find_one( { "_type" : "GSystemType","name":"File" } )


@get_execution_time
def audioDashboard(request, group_id, audio_id=None):

    '''
    fetching audio files acording to group name
    '''
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)
    files_cur = node_collection.find({

                                    '_type': {'$in': ["GSystem"]},
                                    'member_of': file_gst._id,
                                    'group_set': {'$all': [ObjectId(group_id)]},
                                    'if_file.mime_type': {'$regex': 'audio'},
                                    'status' : { '$ne': u"DELETED" } 

                                    # 'created_by': {'$in': gstaff_users},
                        # '$or': [
                                # {
                                # },
                                # {
                                #     '$or': [
                                #             {'access_policy': u"PUBLIC"},
                                #             {
                                #                 '$and': [
                                #                         {'access_policy': u"PRIVATE"},
                                #                         {'created_by': request.user.id}
                                #                     ]
                                #             }
                                #         ],
                                # }
                                # {    'collection_set': {'$exists': "true", '$not': {'$size': 0} }}
                            # ]
                    },
                    {
                        'name': 1,
                        '_id': 1,
                        'fs_file_ids': 1,
                        'member_of': 1,
                        'mime_type': 1,
                        'if_file':1
                    }).sort("last_update", -1)
    # print "files_cur length++++++++++",files_cur.count()
    template = "ndf/audioDashboard.html"
    variable = RequestContext(request, {'audioCollection': files_cur,'groupid':group_id,'group_id':group_id })
    return render_to_response(template, variable)

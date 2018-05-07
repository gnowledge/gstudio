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
from gnowsys_ndf.ndf.views.methods import get_node_metadata, get_node_common_fields, create_gattribute, get_page, get_execution_time,set_all_urls,get_group_name_id,get_filter_querydict 
gapp_mt = node_collection.one({'_type': "MetaType", 'name': META_TYPE[0]})
GST_AUDIO = node_collection.one({'member_of': gapp_mt._id, 'name': GAPPS[3]})
file_gst = node_collection.find_one( { "_type" : "GSystemType","name":"File" } )
from gnowsys_ndf.ndf.models import GSystemType
announced_unit_gst = node_collection.one({'_type': "GSystemType", 'name': "announced_unit"})
gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')
import urllib
from gnowsys_ndf.ndf.gstudio_es.es import *
if GSTUDIO_ELASTIC_SEARCH:
    q = Q('match',name=dict(query='File',type='phrase'))
    file_gst = Search(using=es, index="nodes",doc_type="gsystemtype").query(q).execute()

    q = Q('match',name=dict(query='announced_unit',type='phrase'))
    announced_unit = Search(using=es, index="nodes",doc_type="gsystemtype").query(q).execute()

    q = Q('match',name=dict(query='base_unit',type='phrase'))
    base_unit = Search(using=es, index="nodes",doc_type="gsystemtype").query(q).execute()

@get_execution_time
def audioDashboard(request, group_id, audio_id=None):

    '''
    fetching audio files acording to group name
    '''
    try:
        group_id = ObjectId(group_id)
    except:
        group_name, group_id = get_group_name_id(group_id)

    selfilters = urllib.unquote(request.POST.get('filters', ''))
    filter_query_dict = []
    if selfilters:
        selfilters = json.loads(selfilters)
        filter_query_dict = get_filter_querydict(selfilters)

    search_workspace = request.POST.get("search_workspace",None)
    search_text = request.POST.get("search_text",None)
    template = "ndf/audioDashboard.html"
    if search_workspace != "default" and search_workspace != None and search_text:
        group_name, group_id = get_group_name_id(search_workspace)
    if GSTUDIO_ELASTIC_SEARCH:
        if filter_query_dict:
            filter_query_dict = esearch.es_filters(filter_query_dict)

        q = Q('bool',must=[Q('match',type='group'),~Q('match',name='trash'),~Q('match',name='warehouse')],should=[~Q('match',member_of=announced_unit.hits[0].id),~Q('match',member_of=base_unit.hits[0].id),Q('match',author_set=request.user.id),Q('match',group_admin=request.user.id)],minimum_should_match=2)
        all_workspaces=Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)
        all_workspaces_count = all_workspaces.count()
        strconcat1 = ""
        for value in filter_query_dict:
            strconcat1 = strconcat1+'eval(str("'+ value +'")),'

        if search_text:
            q = eval("Q('bool', must=[Q('match', type='gsystem'),~Q('match', status='deleted'),Q('match', member_of=file_gst.hits[0].id),Q('match', if_file__mime_type='audio'),Q('match', group_set=str(group_id)), Q('multi_match', query=search_text, fields=['content','name','tags']),"+strconcat1[:-1]+"])")
        else:
            q = eval("Q('bool', must=[Q('match', type='gsystem'),~Q('match', status='deleted'),Q('match', member_of=file_gst.hits[0].id),Q('match', if_file__mime_type='audio'),Q('match', group_set=str(group_id)),"+strconcat1[:-1]+"])")
        files_cur =Search(using=es, index="nodes",doc_type="gsystemtype,gsystem,metatype,relationtype,attribute_type,group,author").query(q)
        files_cur_count = files_cur.count()
        variable = RequestContext(request, {'GSTUDIO_ELASTIC_SEARCH':GSTUDIO_ELASTIC_SEARCH,'all_workspaces_count':all_workspaces_count,'all_workspaces':all_workspaces[0:all_workspaces_count],'audioCollection': files_cur[0:files_cur_count],'groupid':group_id,'group_id':group_id })        
    else:
        all_workspaces = node_collection.find(
                    {'_type':'Group','member_of':
                        {'$nin': [ announced_unit_gst._id,gst_base_unit_id]
                    }
                    }).sort('last_update', -1)
        all_workspaces_count = all_workspaces.count()
        if filter_query_dict:
            if search_text:
                filter_query_dict.append({'group_set': {'$all': [ObjectId(group_id)]}})
                filter_query_dict.append({'$or':[{'content':{'$regex' : search_text, '$options' : 'i'}},{'name':{'$regex' : search_text, '$options' : 'i'}},{'altnames':{'$regex' : search_text, '$options' : 'i'}},{'tags':{'$regex' : search_text, '$options' : 'i'}}] })
            else:
                filter_query_dict.append({'group_set': {'$all': [ObjectId(group_id)]}})

        else:
            if search_text:
                filter_query_dict.append({'group_set': {'$all': [ObjectId(group_id)]}})
                filter_query_dict.append({'$or':[{'content':{'$regex' : search_text, '$options' : 'i'}},{'name':{'$regex' : search_text, '$options' : 'i'}},{'altnames':{'$regex' : search_text, '$options' : 'i'}},{'tags':{'$regex' : search_text, '$options' : 'i'}}] })
            else:
                filter_query_dict = [{'group_set': {'$all': [ObjectId(group_id)]}}]
        files_cur = node_collection.find({
                                    '$and':filter_query_dict,
                                    '_type': {'$in': ["GSystem"]},
                                    'member_of': file_gst._id,
                                    # 'group_set': {'$all': [ObjectId(group_id)]},
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
    #print "files_cur length++++++++++",files_cur.count()
        template = "ndf/audioDashboard.html"
        variable = RequestContext(request, {'all_workspaces_count':all_workspaces_count,'all_workspaces':all_workspaces,'audioCollection': files_cur,'groupid':group_id,'group_id':group_id })
    return render_to_response(template, variable)

import json

# ''' -- imports from installed packages -- '''
# from django.http import HttpResponseRedirect
from django.http import HttpResponse
# from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response  #, render
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.ndf.models import Buddy
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_execution_time

# ''' -- imports from application folders/files -- '''
# from gnowsys_ndf.settings import META_TYPE, GAPPS, MEDIA_ROOT
# from gnowsys_ndf.ndf.models import node_collection
# from gnowsys_ndf.ndf.views.methods import get_node_common_fields,create_grelation_list,get_execution_time
# from gnowsys_ndf.ndf.views.methods import get_node_metadata, node_thread_access, create_thread_for_node
# from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute
# from gnowsys_ndf.ndf.views.methods import get_node_metadata, get_node_common_fields, create_gattribute, get_page, get_execution_time,set_all_urls,get_group_name_id
# gapp_mt = node_collection.one({'_type': "MetaType", 'name': META_TYPE[0]})
# GST_AUDIO = node_collection.one({'member_of': gapp_mt._id, 'name': GAPPS[3]})
from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID

def list_buddy(request, group_id):

    '''
    fetching all buddies.
    '''
    # try:
    #     group_id = ObjectId(group_id)
    # except:
    #     group_name, group_id = get_group_name_id(group_id)

    all_inst_users = User.objects.filter(username__iendswith=GSTUDIO_INSTITUTE_ID)
    all_inst_authors = node_collection.find({ '_type': u'Author', 'name': {'$regex': GSTUDIO_INSTITUTE_ID + '$'} })
    # print all_inst_authors.count()
    buddies_authid_name_dict= request.session.get('buddies_authid_name_dict', {})
    buddies_authid_list     = request.session.get('buddies_authid_list', [])


    template = 'ndf/buddy_list.html'

    variable = RequestContext(request, {
                                    "group_id": group_id, 'all_inst_users': all_inst_authors,
                                    'buddies_id_name_dict': buddies_authid_name_dict,
                                    'buddies_id_list': buddies_authid_list
                                })

    return render_to_response(template, variable)


@login_required
@get_execution_time
def update_buddies(request, group_id):

    selected_buddies_list = eval(request.POST.get('selected_buddies_list', '[]'))

    updated_buddies_authid_name_dict = []

    buddies_authid_list = request.session.get('buddies_authid_list', [])

    if selected_buddies_list or buddies_authid_list:

        # update_buddies method signature:
        # def update_buddies(self, loggedin_userid, session_key, buddy_auth_ids_list=[]):
        active_buddy_auth_list = Buddy.update_buddies(request.user.id, request.session.session_key, selected_buddies_list)
        # print "\n\nactive_buddy_auth_list : ", active_buddy_auth_list

        updated_buddies_cur = node_collection.find({
                                                    '_id': {
                                                        '$in': [ObjectId(ab) for ab in active_buddy_auth_list]
                                                    }
                                                },
                                                {'name': 1})

        updated_buddies_authid_name_dict = { b['_id'].__str__(): b['name'] for b in updated_buddies_cur}
        # print "\n\nupdated_buddies : ", updated_buddies_authid_name_dict

        request.session['buddies_userid_list']      = [ b['created_by'] for b in updated_buddies_cur]
        request.session['buddies_authid_list']      = active_buddy_auth_list
        request.session['buddies_authid_name_dict'] = updated_buddies_authid_name_dict

    return HttpResponse(json.dumps(updated_buddies_authid_name_dict))

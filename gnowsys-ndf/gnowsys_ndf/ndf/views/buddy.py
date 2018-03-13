import json
from bson import json_util

# ''' -- imports from installed packages -- '''
from django.http import HttpResponse
from django.shortcuts import render_to_response  #, render
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.ndf.models import Buddy, Author #, DjangoActiveUsersGroup
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_execution_time
from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID


@login_required
def list_buddy(request, group_id='home'):

    '''
    fetching all buddies.
    '''

    buddies_authid_name_dict= request.session.get('buddies_authid_name_dict', {})
    buddies_authid_list     = request.session.get('buddies_authid_list', [])
    # to load all user's at page load time (performance penalty, kept for ref):
    #
    # filter_authors = [ObjectId(auth_oid)for auth_oid in buddies_authid_list]
    # all_inst_users = User.objects.filter(username__iendswith=GSTUDIO_INSTITUTE_ID)
    # all_inst_authors = node_collection.find({
    #                                         '_type': u'Author',
    #                                         # '_id': {'$nin': filter_authors},
    #                                         'name': {
    #                                             '$regex': GSTUDIO_INSTITUTE_ID + '$'
    #                                             },
    #                                         'created_by': {'$ne': request.user.id}
    #                                         })

    selected_buddies_obj_list = node_collection.find({
                                            '_id': {'$in': [ObjectId(b) for b in buddies_authid_list]}
                                            })

    template = 'ndf/buddy_list.html'

    variable = RequestContext(request, {
                                    "group_id": group_id, 'all_inst_users': selected_buddies_obj_list,
                                    'buddies_id_name_dict': buddies_authid_name_dict,
                                    'buddies_id_list': buddies_authid_list
                                })

    return render_to_response(template, variable)


@login_required
@get_execution_time
def update_buddies(request, group_id):

    selected_buddies_list = eval(request.POST.get('selected_buddies_list', '[]'))
    # print "=== selected_buddies_list : ", selected_buddies_list
    selected_buddies_userids_list = Author.get_user_id_list_from_author_oid_list(selected_buddies_list)
    selected_buddies_userids_set = set(selected_buddies_userids_list)

    updated_buddies_authid_name_dict = {}
    already_active_userid_name_dict = {}

    buddies_authid_list = request.session.get('buddies_authid_list', [])
    existing_buddies_userid_list = Author.get_user_id_list_from_author_oid_list(buddies_authid_list)
    # print "=== buddies_authid_list : ", buddies_authid_list
    # print "=== existing_buddies_userid_list : ", existing_buddies_userid_list
    intersection_buddy_userids = selected_buddies_userids_set.intersection(set(existing_buddies_userid_list))
    # print "=======", intersection_buddy_userids

    if selected_buddies_list:

        # sitewide_active_userids_list = DjangoActiveUsersGroup.get_all_user_set_ids_list()
        sitewide_active_userids_list = Buddy.get_active_buddies_user_ids_list()
        sitewide_active_userids_set  = set(sitewide_active_userids_list)

        already_active_user_ids = list(selected_buddies_userids_set.intersection(sitewide_active_userids_set) - set(intersection_buddy_userids))

        if already_active_user_ids:
            auth_cur = node_collection.find({'_type': u'Author', 'created_by': {'$in': already_active_user_ids} }, {'_id': 0, 'name': 1, 'created_by': 1} )
                        # { b['_id'].__str__(): b['name'] for b in updated_buddies_cur}
            if auth_cur:
                already_active_userid_name_dict = {a['created_by']: a['name'] for a in auth_cur}
            # print "==== already_active_userid_name_dict : ", already_active_userid_name_dict

        selected_buddies_list = list(selected_buddies_userids_set - sitewide_active_userids_set) + list(intersection_buddy_userids)
        # print "== sitewide_active_userids_set: ", sitewide_active_userids_set
        # print "selected_buddies_list : ", selected_buddies_list
        # print "== selected_buddies_userids_set: ", selected_buddies_userids_set

        selected_buddies_list = Author.get_author_oid_list_from_user_id_list(user_ids_list=selected_buddies_list, list_of_str_oids=True)

    if selected_buddies_list or buddies_authid_list:

        # update_buddies method signature:
        # def update_buddies(self, loggedin_userid, session_key, buddy_auth_ids_list=[]):
        active_buddy_auth_list = Buddy.update_buddies(request.user.id, request.session.session_key, selected_buddies_list)
        # print "\n\nactive_buddy_auth_list : ", active_buddy_auth_list

        # ab: active buddy
        updated_buddies_cur = node_collection.find({
                                                    '_id': {
                                                        '$in': [ObjectId(ab) for ab in active_buddy_auth_list]
                                                    }
                                                },
                                                {'name': 1, 'created_by': 1}).sort('name', 1)

        updated_buddies_authid_name_dict = { str(b['_id']): b['name'] for b in updated_buddies_cur}
        updated_buddies_cur.rewind()
        buddies_username_id_dict = { str(b['name']): b['created_by'] for b in updated_buddies_cur}
        updated_buddies_cur.rewind()

        request.session['buddies_userid_list']      = [ b['created_by'] for b in updated_buddies_cur]
        request.session['buddies_authid_list']      = active_buddy_auth_list
        request.session['buddies_authid_name_dict'] = json.dumps(updated_buddies_authid_name_dict)
        request.session['buddies_username_id_dict'] = json.dumps(buddies_username_id_dict)
        # print "\n\nrequest.session['buddies_authid_name_dict'] : ", request.session['buddies_authid_name_dict']

    result_dict = {
                'buddies': updated_buddies_authid_name_dict,
                'already_active': already_active_userid_name_dict
            }
    # print "=== result_dict : ", result_dict

    return HttpResponse(json.dumps(result_dict))


# @get_execution_time
# @login_required
def search_authors(request, group_id):
    selected_ids = request.GET.get('selected_ids', '')
    selected_ids = selected_ids.split(',')
    selected_ids = [ObjectId(auth) for auth in selected_ids if auth]
    return HttpResponse(
            json_util.dumps(
                node_collection.find({
                        '_id': {'$nin': selected_ids},
                        '_type': 'Author',
                        'name': {'$regex': unicode(request.GET.get('search_text', u'')), '$options': "i"}
                    },
                    {'name': 1, 'content': 1})
                )
            )


def get_buddy_auth_id_from_name(request, group_id, username=None):
    response_dict ={'success': False}
    username = request.GET.get('selected_buddy_username')
    sitewide_active_userids_list = Buddy.get_active_buddies_user_ids_list()
    auth_node = Author.get_name_id_from_type(username, 'Author', get_obj=True)
    if auth_node and (auth_node.created_by not in sitewide_active_userids_list):
        response_dict.update({'auth_id': str(auth_node._id)})
        response_dict.update({'success': True})
        
    return HttpResponse(json.dumps(response_dict))
''' -- imports from python libraries -- '''
import json

''' -- imports from installed packages -- '''
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId
import datetime

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from gnowsys_ndf.settings import GSTUDIO_BUDDY_LOGIN, GSTUDIO_NOTE_CREATE_POINTS

''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import GSystemType, Group, Node, GSystem, Buddy, Counter  #, Triple
from gnowsys_ndf.ndf.models import node_collection

from gnowsys_ndf.ndf.views.methods import get_execution_time, staff_required, auto_enroll
from gnowsys_ndf.ndf.views.methods import get_language_tuple, create_gattribute, create_thread_for_node

''' -- common db queries -- '''

@login_required
@auto_enroll
@get_execution_time
def node_create_edit(request,
                    group_id=None,
                    member_of=None,
                    detail_url_name=None,
                    node_type='GSystem',
                    node_id=None):
    '''
    creation as well as edit of node
    '''
    # check for POST method to node update operation
    if request.method == "POST":

        # put validations
        if node_type not in node_collection.db.connection._registered_documents.keys():
            raise ValueError('Improper node_type passed')

        kwargs={}
        group_name, group_id = Group.get_group_name_id(group_id)
        member_of_name, member_of_id = GSystemType.get_gst_name_id(member_of)

        if node_id: # existing node object
            node_obj = Node.get_node_by_id(node_id)

        else: # create new
            kwargs={
                    'group_set': group_id,
                    'member_of': member_of_id
                    }
            node_obj = node_collection.collection[node_type]()

        language = get_language_tuple(request.POST.get('language', None))
        node_obj.fill_gstystem_values(request=request,
                                    language=language,
                                            **kwargs)
        node_obj.save(group_id=group_id)
        node_id = node_obj['_id']

        # Consider for Blog page creation
        if member_of_name == "Page":
            blog_page_gst_name, blog_page_gst_id = GSystemType.get_gst_name_id("Blog page")
            if blog_page_gst_id in node_obj.type_of:
                discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
                create_gattribute(node_obj._id, discussion_enable_at, True)
                return_status = create_thread_for_node(request,group_id, node_obj)

                active_user_ids_list = [request.user.id]
                if GSTUDIO_BUDDY_LOGIN:
                    active_user_ids_list += Buddy.get_buddy_userids_list_within_datetime(request.user.id, datetime.datetime.now())
                # removing redundancy of user ids:
                active_user_ids_list = dict.fromkeys(active_user_ids_list).keys()
                counter_objs_cur = Counter.get_counter_objs_cur(active_user_ids_list, group_id)
                for each_counter_obj in counter_objs_cur:
                    each_counter_obj['page']['blog']['created'] += 1
                    each_counter_obj['group_points'] += GSTUDIO_NOTE_CREATE_POINTS
                    each_counter_obj.last_update = datetime.datetime.now()
                    each_counter_obj.save()

        post_req = request.POST
        attrs_to_create_update = [f for f in post_req.keys() if ('attribute' in f)]
        attrs_to_create_update = [a.split('_')[1] for a in attrs_to_create_update]

        for each_attr_name in attrs_to_create_update:
            each_attr_name_obj = Node.get_name_id_from_type(each_attr_name, 'AttributeType', get_obj=True)
            post_req_attr_key = 'attribute_'+each_attr_name
            post_method = 'getlist' if (each_attr_name_obj.data_type in [list, 'list']) else 'get'
            create_gattribute(node_id,
                            each_attr_name_obj,
                            object_value=getattr(post_req, post_method)(post_req_attr_key))


        return HttpResponseRedirect(reverse(detail_url_name, kwargs={'group_id': group_id, 'node_id': node_id}))

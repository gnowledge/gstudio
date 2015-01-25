''' -- imports from python libraries -- '''
# from datetime import datetime
import datetime
import json

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect #, HttpResponse uncomment when to use
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response #, render  uncomment when to use
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site

from mongokit import IS

from django_mongokit import get_database

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT, GSTUDIO_TASK_TYPES
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data
from gnowsys_ndf.ndf.views.notify import set_notif_val
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation, create_task

collection = get_database()[Node.collection_name]
app = collection.Node.one({'_type': "GSystemType", 'name': GAPPS[7]})


@login_required
def enrollment_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
    """
    Creates/Modifies document of given sub-types of Course(s).
    """

    auth = None
    if ObjectId.is_valid(group_id) is False:
        group_ins = collection.Node.one({'_type': "Group", "name": group_id})
        auth = collection.Node.one(
            {'_type': 'Author', 'name': unicode(request.user.username)}
        )
        if group_ins:
            group_id = str(group_ins._id)
        else:
            auth = collection.Node.one(
                {'_type': 'Author', 'name': unicode(request.user.username)}
            )
            if auth:
                group_id = str(auth._id)

    app = None
    if app_id is None:
        app = collection.Node.one({'_type': "GSystemType", 'name': app_name})
        if app:
            app_id = str(app._id)
    else:
        app = collection.Node.one({'_id': ObjectId(app_id)})

    app_name = app.name

    app_set = ""
    app_collection_set = []
    title = ""

    enrollment_gst = None
    enrollment_gs = None
    mis_admin = None

    property_order_list = []

    template = ""
    template_prefix = "mis"

    if request.user:
        if auth is None:
            auth = collection.Node.one(
                {'_type': 'Author', 'name': unicode(request.user.username)}
            )
        agency_type = auth.agency_type
        agency_type_node = collection.Node.one(
            {'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1}
        )
        if agency_type_node:
            for eachset in agency_type_node.collection_set:
                app_collection_set.append(
                    collection.Node.one(
                        {"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}
                    )
                )

    if app_set_id:
        enrollment_gst = collection.Node.one(
            {'_type': "GSystemType", '_id': ObjectId(app_set_id)},
            {'name': 1, 'type_of': 1}
        )
        template = "ndf/" \
            + enrollment_gst.name.strip().lower().replace(' ', '_') \
            + "_create_edit.html"

        title = enrollment_gst.name
        enrollment_gs = collection.GSystem()
        enrollment_gs.member_of.append(enrollment_gst._id)

    if app_set_instance_id:
        enrollment_gs = collection.Node.one(
            {'_type': "GSystem", '_id': ObjectId(app_set_instance_id)}
        )

    property_order_list = get_property_order_with_value(enrollment_gs)

    if request.method == "POST":
        print("\n coming in POST...\n")

    default_template = "ndf/enrollment_create_edit.html"
    context_variables = {
        'groupid': group_id, 'group_id': group_id,
        'app_id': app_id, 'app_name': app_name,
        'app_collection_set': app_collection_set,
        'app_set_id': app_set_id,
        'title': title,
        'property_order_list': property_order_list
    }

    if app_set_instance_id:
        enrollment_gs.get_neighbourhood(enrollment_gs.member_of)
        context_variables['node'] = enrollment_gs
        for each_in in enrollment_gs.attribute_set:
            for eachk, eachv in each_in.items():
                context_variables[eachk] = eachv

        for each_in in enrollment_gs.relation_set:
            for eachk, eachv in each_in.items():
                get_node_name = collection.Node.one({'_id': eachv[0]})
                context_variables[eachk] = get_node_name.name

    try:
        return render_to_response(
            [template, default_template],
            context_variables,
            context_instance=RequestContext(request)
        )

    except TemplateDoesNotExist as tde:
        error_message = "\n EnrollmentCreateEditViewError: This html template (" \
            + str(tde) + ") does not exists !!!\n"
        raise Http404(error_message)

    except Exception as e:
        error_message = "\n EnrollmentCreateEditViewError: " + str(e) + " !!!\n"
        raise Exception(error_message)

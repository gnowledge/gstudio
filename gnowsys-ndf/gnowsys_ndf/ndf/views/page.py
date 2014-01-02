''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.methods import get_drawers
from gnowsys_ndf.ndf.views.methods import get_node_common_fields


#######################################################################################################################################

db = get_database()
gst_collection = db[GSystemType.collection_name]
gst_page = gst_collection.GSystemType.one({'name': GAPPS[0]})
gs_collection = db[GSystem.collection_name]
history_manager = HistoryManager()
rcs = RCS()

#######################################################################################################################################
#                                                                            V I E W S   D E F I N E D   F O R   G A P P -- ' P A G E '
#######################################################################################################################################

def page(request, group_name, app_id):
    """Renders a list of all 'Page-type-GSystems' available within the database.
    """
    if gst_page._id == ObjectId(app_id):
        title = gst_page.name
        
        page_nodes = gs_collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(app_id)]}, 'group_set': {'$all': [group_name]}})
        page_nodes.sort('last_update', -1)
        page_nodes_count = page_nodes.count()

        return render_to_response("ndf/page_list.html",
                                  {'title': title, 
                                   'page_nodes': page_nodes, 'page_nodes_count': page_nodes_count
                                  }, 
                                  context_instance=RequestContext(request)
        )

    else:
        page_node = gs_collection.GSystem.one({"_id": ObjectId(app_id)})
        prior_node_obj_dict = {}
        prior_node_list = page_node.prior_node
        
        for each_id in prior_node_list:
            if each_id != page_node._id:
                node_collection_object = gs_collection.GSystem.one({"_id": ObjectId(each_id)})
                dict_key = node_collection_object._id
                dict_value = node_collection_object
                
                prior_node_obj_dict[dict_key] = dict_value

        collection_obj_dict = {}
        collection_list = page_node.collection_set
        
        for each_id in collection_list:
            if each_id != page_node._id:
                node_collection_object = gs_collection.GSystem.one({"_id": ObjectId(each_id)})
                dict_key = node_collection_object._id
                dict_value = node_collection_object
                
                collection_obj_dict[dict_key] = dict_value

        # Version dictionary required to display number of versions created
        version_dict = {}
        version_dict = history_manager.get_version_dict(page_node)
        
        return render_to_response("ndf/node_details_base.html", 
                                  { 'node': page_node, 'user_details': user_details,
                                    'version_dict': version_dict,
                                    'prior_node_obj_dict': prior_node_obj_dict,
                                    'collection_obj_dict': collection_obj_dict,
                                   'group_name': group_name
                                  },
                                  context_instance = RequestContext(request)
        )        
        
    
def create_page(request, group_name):
    """Creates a new page.
    """
    if request.user.is_authenticated():
        page_node = gs_collection.GSystem()

        if request.method == "POST":
            get_node_common_fields(request, page_node, group_name, gst_page)
            page_node.save()
            return HttpResponseRedirect(reverse('page', kwargs={'group_name': group_name, 'app_id': gst_page._id}))

        else:
            return render_to_response("ndf/page_create.html",
                                      { 'title': gst_page.name,
                                        'group_name': group_name
                                      },
                                      context_instance=RequestContext(request)
            )



def edit_page(request, group_name, node_id):
    """Displays/Modifies details about the given page.
    """
    if request.user.is_authenticated():
        page_node = gs_collection.GSystem.one({"_id": ObjectId(node_id)})

        if request.method == "POST":
            get_node_common_fields(request, page_node, group_name, gst_page)
            page_node.save()
            return HttpResponseRedirect(reverse('page_details', kwargs={'group_name': group_name, 'app_id': page_node._id}))

        else:
            return render_to_response("ndf/page_edit.html",
                                      { 'node': page_node,
                                        'group_name': group_name
                                      },
                                      context_instance=RequestContext(request)
            )


def version_node(request, group_name, node_id, version_no):
    """Renders either a single or compared version-view based on request.

    In single version-view, all information of the node for the given version-number 
    is provided.

    In compared version-view, comparitive information in tabular form about the node 
    for the given version-numbers is provided.
    """
    view = ""          # either single or compare
    selected_versions = {}
    node = gs_collection.GSystem.one({"_id": ObjectId(node_id)})

    fp = history_manager.get_file_path(node)

    if request.method == "POST":
        print "\n if -- version page\n"
        view = "compare"

        version_1 = request.POST["version_1"]
        version_2 = request.POST["version_2"]

        diff = get_html_diff(fp, version_1, version_2)

        selected_versions = {"1": version_1, "2": version_2}
        content = diff

    else:
        print "\n else -- version page\n"
        view = "single"

        # Retrieve rcs-file for a given version-number
        rcs.checkout((fp, version_no))

        # Copy content from rcs-version-file
        data = None
        with open(fp, 'r') as sf:
            data = sf.read()

        # Used json.loads(x) -- to covert string to dictionary object
        # If want to use key from this converted dictionay, use array notation because dot notation doesn't works!
        data = json.loads(data)

        # Remove retrieved rcs-file belonging to the given version-number
        rcs.checkin(fp)

        selected_versions = {"1": version_no, "2": ""}
        content = data

    return render_to_response("ndf/version_page.html",
                              {'view': view,
                               'node': node,
                               'selected_versions': selected_versions,
                               'content': content
                              },
                              context_instance = RequestContext(request)
    )        



#######################################################################################################################################
#                                                                                                     H E L P E R  -  F U N C T I O N S
#######################################################################################################################################

def get_html_diff(versionfile, fromfile="", tofile=""):
    if versionfile != "":
        if fromfile == "":
            fromfile = rcs.head(versionfile)

        if tofile == "":
            tofile = rcs.head(versionfile)

        # fromfile ----------------------------------------------------------

        # Retrieve rcs-file for a given version-number (here, version-number <--> fromfile)
        rcs.checkout((versionfile, fromfile))

        # Copy content from rcs-version-file
        fromlines = None
        with open(versionfile, 'r') as ff:
            fromlines = ff.readlines()

        # Remove retrieved rcs-file belonging to the given version-number
        rcs.checkin(versionfile)

        # tofile ------------------------------------------------------------

        # Retrieve rcs-file for a given version-number (here, version-number <--> tofile)
        rcs.checkout((versionfile, tofile))

        # Copy content from rcs-version-file
        tolines = None
        with open(versionfile, 'r') as tf:
            tolines = tf.readlines()

        # Remove retrieved rcs-file belonging to the given version-number
        rcs.checkin(versionfile)

        fromfile = "Version #" + fromfile
        tofile = "Version #" + tofile

        return HtmlDiff(wrapcolumn=60).make_file(fromlines, tolines, fromfile, tofile)

    else:
        print "\n Please pass a valid rcs-version-file!!!\n"
        #TODO: Throw an error indicating the above message!
        return ""

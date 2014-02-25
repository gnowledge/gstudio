''' -- imports from python libraries -- '''
# import os -- Keep such imports here
import json
from difflib import HtmlDiff

''' -- imports from installed packages -- '''
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.template.defaultfilters import slugify

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import Node, GSystem
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.views.methods import get_node_common_fields


#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
gst_page = collection.Node.one({'_type': 'GSystemType', 'name': GAPPS[0]})
history_manager = HistoryManager()
rcs = RCS()

#######################################################################################################################################
#                                                                            V I E W S   D E F I N E D   F O R   G A P P -- ' P A G E '
#######################################################################################################################################

def page(request, group_id, app_id=None):
    """Renders a list of all 'Page-type-GSystems' available within the database.
    """
    if request.method == "POST":
        # Written for implementing search-functionality
        title = gst_page.name
        
        search_field = request.POST['search_field']

        page_nodes = collection.Node.find({'member_of': {'$all': [ObjectId(app_id)]},
                                           '$or': [{'name': {'$regex': search_field, '$options': 'i'}}, 
                                                   {'tags': {'$regex':search_field, '$options': 'i'}}], 
                                           'group_set': {'$all': [group_id]}
                                       })
        page_nodes.sort('last_update', -1)
        page_nodes_count = page_nodes.count()

        return render_to_response("ndf/page_list.html",
                                  {'title': title, 
                                   'searching': True, 'query': search_field,
                                   'page_nodes': page_nodes, 'newgroup':group_id,'page_nodes_count': page_nodes_count
                                  }, 
                                  context_instance=RequestContext(request)
        )

    elif gst_page._id == ObjectId(app_id):
        title = gst_page.name
        # collection.Node.reload()
        page_nodes = collection.Node.find({'member_of': {'$all': [ObjectId(app_id)]}, 
                                           'group_set': {'$all': [group_name]},                                           
                                           'status': {'$nin': ['HIDDEN']}
                                       })        

        page_nodes.sort('last_update', -1)
        page_nodes_count = page_nodes.count()        

        return render_to_response("ndf/page_list.html",
                                  {'title': title, 
                                   'page_nodes': page_nodes,'newgroup':group_id,'page_nodes_count': page_nodes_count
                                  }, 
                                  context_instance=RequestContext(request)
        )

    else:
        page_node = collection.Node.one({"_id": ObjectId(app_id)})

        return render_to_response('ndf/page_details.html', 
                                  { 'node': page_node,
                                    'group_id': group_id,
                                    'newgroup':group_id,
                                    'graphData': graphData
                                  },
                                  context_instance = RequestContext(request)
        )        



@login_required
def create_edit_page(request, group_id, node_id=None):
    """Creates/Modifies details about the given quiz-item.
    """

    context_variables = { 'title': gst_page.name,
                          'group_id': group_id
                      }

    if node_id:
        page_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
    else:
        page_node = collection.GSystem()

    if request.method == "POST":
        get_node_common_fields(request, page_node, group_id, gst_page)
        page_node.save()
        
        return HttpResponseRedirect(reverse('page_details', kwargs={'group_id': group_id, 'newgroup':group_id, 'app_id': page_node._id}))
        
    else:
        if node_id:
            context_variables['node'] = page_node
            context_variables['newgroup']=group_id
            
        return render_to_response("ndf/page_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )

@login_required    
def delete_page(request, group_name, node_id):
    """Change the status to Hidden.
    
    Just hide the page from users!
    """

    print "\n node: ", type(node_id), "\n"
    op = collection.update({'_id': ObjectId(node_id)}, {'$set': {'status': u"HIDDEN"}})
    print " op: ", op, "\n"
    
    return HttpResponseRedirect(reverse('page', kwargs={'group_name': group_name, 'app_id': gst_page._id}))


def version_node(request, group_id, node_id, version_no):
    """Renders either a single or compared version-view based on request.

    In single version-view, all information of the node for the given version-number 
    is provided.

    In compared version-view, comparitive information in tabular form about the node 
    for the given version-numbers is provided.
    """
    view = ""          # either single or compare
    selected_versions = {}
    node = collection.Node.one({"_id": ObjectId(node_id)})

    fp = history_manager.get_file_path(node)

    if request.method == "POST":
        view = "compare"

        version_1 = request.POST["version_1"]
        version_2 = request.POST["version_2"]

        diff = get_html_diff(fp, version_1, version_2)

        selected_versions = {"1": version_1, "2": version_2}
        content = diff

    else:
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
                               'newgroup':group_id,
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

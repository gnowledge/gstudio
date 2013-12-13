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

def page(request, group_name,app_id):
    """Renders a list of all 'Page-type-GSystems' available within the database.
    """
    if gst_page._id == ObjectId(app_id):
        title = gst_page.name
        
        page_nodes = gs_collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(app_id)]}})
        page_nodes.sort('last_update', -1)
        page_nodes_count = page_nodes.count()

        return render_to_response("ndf/page.html", 
                                  {'title': title, 
                                   'page_nodes': page_nodes, 'page_nodes_count': page_nodes_count
                                  }, 
                                  context_instance=RequestContext(request)
        )

    
def create_page(request,group_name):
    """Creates a new page.
    """
    if request.user.is_authenticated():

        page_node = gs_collection.GSystem()

        collection = None
        private = None

        if request.method == "POST":
            
            name = request.POST.get('page_name')
            page_node.name = unicode(name)

            page_node.member_of.append(gst_page.name)

            page_node.gsystem_type.append(gst_page._id)

            usrid = int(request.user.id)
            page_node.created_by = usrid          # Confirm the data-type for this field in models.py file is changed from ObjectId (Prev-{Author, django_mongokit}) to int (Curr-{User, django})

            if usrid not in page_node.modified_by:
                page_node.modified_by.append(usrid)

            tags = request.POST.get('page_tags')
            page_node.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]

            prior_node_list = request.POST['prior-node-list']
            if prior_node_list != '':
                prior_node_list = prior_node_list.split(",")

            i = 0                    
            while (i < len(prior_node_list)):                    
                pn_name = str(prior_node_list[i])
                pn_name = pn_name.replace("'", "")
                page_node.prior_node.append(gs_collection.GSystem.one({'name': unicode(pn_name)})._id)
                i = i+1


            private = request.POST.get("private", '')
            if private:
                private = True
            else:
                private = False

            collection = request.POST.get("collection", '')
            if collection:
                collection_list = request.POST['collection-list']
                if collection_list != '':
                    collection_list = collection_list.split(",")

                i = 0                    
                while (i < len(collection_list)):                    
                    c_name = str(collection_list[i])
                    c_name = c_name.replace("'", "")
                    objs = gs_collection.GSystem.one({'name': unicode(c_name)})
                    page_node.collection_set.append(objs._id)
                    i = i+1

            content_org = request.POST.get('content_org')
            usrname = request.user.username
            # Required to link temporary files with the current user who is modifying this document
            filename = slugify(name) + "-" + usrname + "-"

            page_node.content = unicode(org2html(content_org, file_prefix=filename))

            page_node.content_org = unicode(content_org.encode('utf8'))

            page_node.save()

            return HttpResponseRedirect(reverse('page', kwargs={'group_name': group_name, 'app_id': gst_page._id}))
        else:
            # if request.method is not "POST"!!!

            drawer1 = get_drawers()
            return render_to_response("ndf/create_page.html", 
                                      { 'pn_drawer1': drawer1,
                                        'c_drawer1': drawer1,
                                        'group_name':group_name
                                      }, 
                                      context_instance=RequestContext(request)
            )


def edit_page(request, group_name, node_id):
    """Displays/Modifies details about the given page.
    """
    page_node = gs_collection.GSystem.one({"_id": ObjectId(node_id)})

    if request.user.is_authenticated():

        if request.method == "POST":

            name = request.POST.get('name')
            page_node.name = unicode(name)

            usrid = int(request.user.id)
            if usrid not in page_node.modified_by:
                page_node.modified_by.append(int(request.user.id))

            tags = request.POST.get('tags')
            page_node.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]

            prior_node_list = request.POST['prior-node-list']
            page_node.prior_node = []

            if prior_node_list != '':
                prior_node_list = prior_node_list.split(",")

            i = 0
            while (i < len(prior_node_list)):
                pn_name = str(prior_node_list[i])
                pn_name = pn_name.replace("'", "")
                page_node.prior_node.append(gs_collection.GSystem.one({'name': unicode(pn_name)})._id)
                i = i+1


            collection_list = request.POST['collection-list']
            page_node.collection_set = []

            if collection_list != '':
                collection_list = collection_list.split(",")

            i = 0
            while (i < len(collection_list)):
                c_name = str(collection_list[i])
                c_name = c_name.replace("'", "")
                #objs = gs_collection.GSystem.one({'name': unicode(c_name)})
                page_node.collection_set.append(gs_collection.GSystem.one({'name': unicode(c_name)})._id)
                i = i+1

            content_org = request.POST.get('content_org')
            page_node.content_org = unicode(content_org.encode('utf8'))

            usrname = request.user.username
            # Required to link temporary files with the current user who is modifying this document
            filename = slugify(name) + "-" + usrname + "-"
            page_node.content = unicode(org2html(content_org, file_prefix=filename))

            page_node.save()
            
            return HttpResponseRedirect(reverse('edit_page', kwargs={'group_name': group_name, 'node_id': page_node._id}))

        else:

            # Retrieving names of created-by & modified-by users, and appending to 'user_details' dict-variable
            user_details = {}
            user_details['created_by'] = User.objects.get(pk=page_node.created_by).username

            modified_by_usernames = []
            for each_pk in page_node.modified_by:
                modified_by_usernames.append(User.objects.get(pk=each_pk).username)
            user_details['modified_by'] = modified_by_usernames

            # Based on prior-nodes, constructing drawers & prior-node-dictionary-variable  
            pn_drawers = get_drawers(page_node._id, page_node.prior_node)
            pn_drawer1 = pn_drawers['1']
            pn_drawer2 = pn_drawers['2']

            prior_node_obj_dict = {}
            prior_node_list = page_node.prior_node
        
            for each_id in prior_node_list:
                if each_id != page_node._id:
                    node_collection_object = gs_collection.GSystem.one({"_id": ObjectId(each_id)})
                    dict_key = node_collection_object._id
                    dict_value = node_collection_object
                
                    prior_node_obj_dict[dict_key] = dict_value

            # Based on collection-elements, constructing drawers & collection-dictionary-variable  
            c_drawers = get_drawers(page_node._id, page_node.collection_set)
            c_drawer1 = c_drawers['1']
            c_drawer2 = c_drawers['2']

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

            return render_to_response("ndf/edit_page.html", 
                                      { 'node': page_node, 'user_details': user_details,
                                        'version_dict': version_dict,
                                        'pn_drawer1': pn_drawer1, 'pn_drawer2': pn_drawer2, 'prior_node_obj_dict': prior_node_obj_dict,
                                        'c_drawer1': c_drawer1, 'c_drawer2': c_drawer2, 'collection_obj_dict': collection_obj_dict,
                                        'group_name': group_name
                                      }, 
                                      context_instance = RequestContext(request)
            )

    else:

        return render_to_response("ndf/edit_page.html", 
                                  { 'node': page_node, 'group_name':group_name
                                  }, 
                                  context_instance = RequestContext(request)
        )

def version_page(request, group_name, node_id, version_no):

    view = ""          # either single or compare

    if request.method == "POST":
        print "\n if -- version page\n"
        view = "compare"

    else:
        print "\n else -- version page\n"
        view = "single"

        page_node = gs_collection.GSystem.one({"_id": ObjectId(node_id)})
        fp = history_manager.get_file_path(page_node)

        diff = get_html_diff(fp, version_no)

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

    return render_to_response("ndf/version_page.html",
                              {'view': "compare",
                               'node': diff
                              },
                              context_instance = RequestContext(request)
    )        

#######################################################################################################################################
#                                                                                                     H E L P E R  -  F U N C T I O N S
#######################################################################################################################################

def get_drawers(nid=None, nlist=[]):
    """Get both drawers-list.
    """

    dict_drawer={}
    dict1={}
    dict2={}

    drawer = gs_collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(gst_page._id)]}})

    if (nid is None) and (not nlist):
      for each in drawer:
        dict_drawer[each._id] = str(each.name)

    else:
      for each in drawer:
        if each._id != nid:
          if each._id not in nlist:
            dict1[each._id]=str(each.name)
          
          else:
            dict2[each._id]=str(each.name)
      
      dict_drawer['1'] = dict1
      dict_drawer['2'] = dict2

    return dict_drawer

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

        return HtmlDiff(wrapcolumn=60).make_file(fromlines, tolines, fromfile, tofile)

    else:
        print "\n Please pass a valid rcs-version-file!!!\n"
        #TODO: Throw an error indicating the above message!
        return ""

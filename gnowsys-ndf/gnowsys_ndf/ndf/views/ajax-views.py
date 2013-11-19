''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' -- imports from application folders/files -- '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.org2any import org2html

###########################################################################

db = get_database()

###########################################################################

def edit_collection(request):

    if request.method == "POST":
        collection_list = request.POST['collection-list']
        obj_id = request.POST['node_id']

        # Creating Collection-objects
        col_GSystem = db[GSystem.collection_name]
        node = col_GSystem.GSystem.one({'_id': ObjectId(obj_id)})

        node.collection_set = []

        if collection_list != '':
            collection_list = collection_list.split(",")

            i = 0
            while i<len(collection_list):                    
                c_name = str(collection_list[i])
                c_name = c_name.replace("'", "")
                objs = col_GSystem.GSystem.one({'name': unicode(c_name)})
                node.collection_set.append(objs._id)
                i=i+1

            # Saving the current document's instance into database
            node.save()

        collection_list = node.collection_set
        collection_obj_dict = {}

        if collection_list: 
            for each_id in collection_list:
                node_collection_object = col_GSystem.GSystem.one({"_id": ObjectId(each_id)})
            
                dict_key = node_collection_object._id
                dict_value = node_collection_object
            
                collection_obj_dict[dict_key] = dict_value

        return render_to_response('ndf/display_page.html', {'node': node, 'collection_obj_dict': collection_obj_dict}, context_instance=RequestContext(request))
    else:
        return render_to_response("ndf/display_page.html", context_instance=RequestContext(request))   



def edit_content(request):

    if request.is_ajax() and request.method == "POST":
        #if request.POST.has_key('client_org_content'):
        # Retrieving data from request object
        obj_id = ""
        usrname = ""

        org_content = request.POST['client_org_content']
        obj_id = ObjectId(request.POST['client_object_id'])
        usrname = request.POST['client_username']

        # Fetching the document's instance from database
        col_GSystem = db[GSystem.collection_name]
        node = col_GSystem.GSystem.one({'_id': obj_id})

        filename = slugify(node_name) + "-" + usrname + "-"
        node.content = unicode(org2html(org_content, file_prefix=filename))
        node.content_org = unicode(org_content.encode('utf8'))

        # Updating the above instance with modified data
        node.save()

        # Must fetch from database again, otherwise you won't get the updated data
        node = col_GSystem.GSystem.one({'_id': obj_id})

        return render_to_response('ndf/display_content.html', {'node': node}, context_instance=RequestContext(request))

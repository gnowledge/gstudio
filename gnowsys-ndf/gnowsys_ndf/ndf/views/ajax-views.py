''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.http import HttpResponse
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

DB = get_database()
history_manager = HistoryManager()
rcs_obj = RCS()
unicode_wikipage = unicode("Wikipage")

def edit_content(request):

    obj_id = ""
    usrname = ""
    
    #if request.is_ajax() and request.method =="POST":
    if request.POST.has_key('client_org_content'):
        # Retrieving data from request object
        org_content = request.POST['client_org_content']
        obj_id = ObjectId(request.POST['client_object_id'])
        usrname = request.POST['client_username']

        # Fetching the document's instance from database
        col_GSystem = DB[GSystem.collection_name]
        node = col_GSystem.GSystem.one({'_id': obj_id})
        node_name = node.name

        filename = slugify(node_name) + "-" + usrname + "-"
        content = unicode(org2html(org_content, file_prefix=filename))
        content_org = unicode(org_content.encode('utf8') + "\n\n")

        # Updating the above instance with modified data
        col_GSystem.update({'_id': obj_id}, {'$set': {'content_org': content_org, 'content': content}}, upsert=False)

        # Must fetch from database again, otherwise you won't get the updated data
        node = col_GSystem.GSystem.one({'_id': obj_id})

        # Storing histroy in rcs-version-file
        fp = history_manager.get_file_path(node)
        rcs_obj.checkout(fp)

        if history_manager.create_or_replace_json_file(node):
            rcs_obj.checkin(fp, 1, "Document " + node_name + " modified by " + usrname)

        return render_to_response('ndf/display_content.html', {'node': node})
    else:
        return render_to_response('ndf/edit_content.html', context_instance=RequestContext(request, {'user': usrname, 'node': node}))

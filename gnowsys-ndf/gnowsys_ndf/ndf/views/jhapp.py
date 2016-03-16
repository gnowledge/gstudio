import os
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
from gnowsys_ndf.ndf.models import File

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import META_TYPE, GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_node_common_fields,create_grelation_list,get_execution_time
from gnowsys_ndf.ndf.views.methods import get_node_metadata, node_thread_access, create_thread_for_node
from gnowsys_ndf.ndf.management.commands.data_entry import create_gattribute
from gnowsys_ndf.ndf.views.methods import get_node_metadata, get_node_common_fields, create_gattribute, get_page, get_execution_time,set_all_urls,get_group_name_id 

@get_execution_time
def get_jhapp_apps(request, group_id):
    app_name_dict = ['']
    app_name_dict = get_subdirectories('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/static/ndf/JHApp/TurnJS')
    print "path",os.path()
    for root, directories, filenames in os.walk('/home/docker/code/gstudio/gnowsys-ndf/gnowsys_ndf/ndf/static/ndf/JHApp'):
      for directory in directories: 
        print "directory",directory 

    return render_to_response('ndf/jhapp.html',            
            {
                'group_id': group_id, 'groupid': group_id,
                'app_name_dict': app_name_dict

            },
            context_instance=RequestContext(request))

def get_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]
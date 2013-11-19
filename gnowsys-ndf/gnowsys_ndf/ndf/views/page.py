''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
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

from gnowsys_ndf.ndf.models import GSystemType, GSystem
from gnowsys_ndf.ndf.org2any import org2html

###########################################################################

db = get_database()
gst_collection = db[GSystemType.collection_name]
gst_page = gst_collection.GSystemType.one({'name': GAPPS[0]})

def page(request, page_id):
    """
    * Renders a list of all 'Page-type-GSystems' available within the database.

    """

    if gst_page._id == ObjectId(page_id):
        title = gst_page.name
        
        gs_collection = db[GSystem.collection_name]
        page_nodes = gs_collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(page_id)]}})
        page_nodes.sort('creationtime', -1)
        page_nodes_count = page_nodes.count()

        return render_to_response("ndf/page.html", {'title': title, 'page_nodes': page_nodes, 'page_nodes_count': page_nodes_count}, context_instance=RequestContext(request))

    return HttpResponseRedirect(reverse('homepage'))

    
def create_page(request):
    """
    * Creates a new page.

    """
    if request.user.is_authenticated():

        ###
        collection = None
        private = None
        pageId = ""
        test1 = get_pdrawer()
        get_page_drawer = get_pg_drawer()

        ###

        if request.method == "POST":
            # Creating Collection-objects
            gst_collection = db[GSystemType.collection_name]
            gs_collection = db[GSystem.collection_name]
            
            # Retrieving values from request object
            name = request.POST.get('page_name')
            tags = request.POST.get('page_tags')
            tags_list = []
            tags_list.append(tags)     # Necessary to extend retrieved tags as list
            tags = [unicode(t) for t in tags_list]
            content_org = request.POST.get('content_org')
            usrid = int(request.POST.get('usrid'))
            usrname = request.POST.get('usrname')
            collection_list = request.POST['collection-list']

            ### checkbox inputs for collection & private
            collection = request.POST.get("collection", '')
            private = request.POST.get("private", '')
            
            boolean = False
            boolean = collection

            collection_list = collection_list.split(",")
            i = 0                    

            if private:
                private = True
            else:
                private = False

            if collection:
                collection = True
            else:
                collection = False

            ###
            
            # Instantiating & Initializing GSystem object
            page_node = gs_collection.GSystem()
            page_node.name = unicode(name)
            page_node.tags.extend(tags)
            page_node.member_of.append(gst_page.name)
            page_node.gsystem_type.append(gst_page._id)
            page_node.created_by = usrid          # Confirm the data-type for this field in models.py file is changed from ObjectId (Prev-{Author, django_mongokit}) to int (Curr-{User, django})
            
            # Required to link temporary files with there user
            filename = slugify(name) + "-" + usrname + "-"
            page_node.content = unicode(org2html(content_org, file_prefix=filename))

            page_node.content_org = unicode(content_org.encode('utf8'))

            ###
            if boolean:
                while i<len(collection_list):                    
                    c_name = str(collection_list[i])
                    c_name = c_name.replace("'","")                    
                    objs = gs_collection.GSystem.one({'name': unicode(c_name)})
                    page_node.collection_set.append(objs._id)
                    i = i+1

            ###

            page_node.save()

            return HttpResponseRedirect(reverse('page', kwargs={'page_id': gst_page._id}))
        else:
            # if request.method is not "POST"!!!
            return render_to_response("ndf/create_page.html", {'test1': test1,'get_page_drawer': get_page_drawer}, context_instance=RequestContext(request))
    else:
        # if user is not authenticated!!!
        return HttpResponseRedirect(reverse('page'))


###
def get_pdrawer():
    pagedrawer = []
    dict1={}
    
    col_GSystem = db[GSystem.collection_name]    
    drawer = col_GSystem.GSystem.find({'gsystem_type': {'$all': [ObjectId(gst_page._id)]}}) 
            
    for each in drawer:
	pagedrawer.append(str(each.name))
	dict1[each._id]=str(each.name)
        
    return dict1

def get_pg_drawer():
    pagedrawer = []
    col_GSystem = db[GSystem.collection_name]
    drawer = col_GSystem.GSystem.find({'gsystem_type': {'$all': [ObjectId(gst_page._id)]}}) 

    for each in drawer:
	pagedrawer.append(str(each.name))

    return pagedrawer
###


def display_page(request, node_id):
    """Display details of the given page.

    Arguments:-
    request: Request object
    node_id: ObjectId of the given page

    Return: Response rendered to display_page.html along with the given 
    page's object
    """

    gs_collection = db[GSystem.collection_name]
    node = gs_collection.GSystem.one({"_id": ObjectId(node_id)})

    collection_obj_dict = {}
    collection_list = node.collection_set
    
    for each_id in collection_list:
        if each_id != node._id:
    
            node_collection_object = gs_collection.GSystem.one({"_id": ObjectId(each_id)})
            dict_key = node_collection_object._id
            dict_value = node_collection_object

            collection_obj_dict[dict_key] = dict_value        
   
    return render_to_response("ndf/display_page.html", \
                               { 'node': node, \
                                 'collection_obj_dict': collection_obj_dict, \
                               }, \
                               context_instance=RequestContext(request) \
                             )   

"""
def delete_node(request, _id):
    col_GSystem = DB[GSystem.collection_name]
    node = col_GSystem.GSystem.one({"_id": ObjectId(_id)})
    node.delete()
    return HttpResponseRedirect(reverse("wikipage"))
"""







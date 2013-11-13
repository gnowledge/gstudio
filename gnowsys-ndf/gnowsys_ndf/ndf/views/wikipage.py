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
from gnowsys_ndf.ndf.models import GSystemType, GSystem
from gnowsys_ndf.ndf.models import HistoryManager
from gnowsys_ndf.ndf.rcslib import RCS
from gnowsys_ndf.ndf.org2any import org2html

###########################################################################

DB = get_database()
history_manager = HistoryManager()
rcs_obj = RCS()
unicode_wikipage = unicode("Wikipage")

def wikipage(request):
    col_GSystem = DB[GSystem.collection_name]
    nodes = col_GSystem.GSystem.find({'member_of': unicode_wikipage})
    nodes.sort('creationtime', -1)
    nodes_count = nodes.count()

    #if member_id is not None:
    return render_to_response("ndf/wiki.html", {'nodes': nodes, 'nodes_count': nodes_count}, context_instance=RequestContext(request))    

    
def create_wiki(request):

    if request.user.is_authenticated():

        if request.method == "POST":
            # Creating Collection-objects
            col_GSystemType = DB[GSystemType.collection_name]
            col_GSystem = DB[GSystem.collection_name]
            
            # Retrieving values from request object
            wiki_name = request.POST.get('wiki_name')
            wiki_tags = request.POST.get('tags')
            wiki_content_org = request.POST.get('content_org')
            wiki_member_of = unicode_wikipage
            id_wiki_gsystem_type = col_GSystemType.GSystemType.one({'name': unicode_wikipage})._id

            usrid = int(request.POST.get('usrid'))
            usrname = request.POST.get('usrname')
            
            # Instantiating & Initializing GSystem object
            doc_page = col_GSystem.GSystem()
            doc_page.name = unicode(wiki_name)
            doc_page.tags.append(unicode(wiki_tags))
            doc_page.member_of = wiki_member_of
            doc_page.gsystem_type.append(id_wiki_gsystem_type)
            doc_page.created_by = usrid          # Confirm the data-type for this field in models.py file is changed from ObjectId (Prev-{Author, django_mongokit}) to int (Curr-{User, django})
            
            # Required to link temporary files with there user
            filename = slugify(wiki_name) + "-" + usrname + "-"
            doc_page.content = unicode(org2html(wiki_content_org, file_prefix=filename))

            doc_page.content_org = unicode(wiki_content_org.encode('utf8') + "\n\n")

            # Saving the current document's instance into database
            doc_page.save()

            ''' -- Storing history of this current document's instance -- '''
            if history_manager.create_or_replace_json_file(doc_page):
                fp = history_manager.get_file_path(doc_page)
                rcs_obj.checkin(fp, 0, "This document("+str(doc_page.name)+") is of GSystem(" + doc_page.member_of  +").", "-i")

            #create_wikipage(wiki_name, usrid, wiki_org_content, usrname, collection=False, list=[], private=False)

            return HttpResponseRedirect(reverse('wikipage'))
        
        else:
            return render_to_response("ndf/create_wiki.html",context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('wikipage'))


def display_page(request, page_id):
    """Display details of the given wikipage.

    Arguments:-
    request: Request object
    page_id: ObjectId of the given page

    Return: Response rendered to display_page.html along with the given 
    wikipage's object
    """

    col_GSystem = DB[GSystem.collection_name]
    node = col_GSystem.GSystem.one({"_id": ObjectId(page_id)})

    return render_to_response("ndf/display_page.html", \
                                  {'node': node}, \
                                  context_instance=RequestContext(request) \
                                  )

    #return HttpResponseRedirect(reverse("wikipage"))

		
def delete_node(request, _id):
    col_GSystem = DB[GSystem.collection_name]
    node = col_GSystem.GSystem.one({"_id": ObjectId(_id)})
    node.delete()
    return HttpResponseRedirect(reverse("wikipage"))







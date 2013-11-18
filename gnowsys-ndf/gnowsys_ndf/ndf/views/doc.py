''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

import magic  #for this install python-magic example:pip install python-magic

#from string import maketrans 


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem
from gnowsys_ndf.ndf.models import File

###########################################################################

db = get_database()
gst_collection = db[GSystemType.collection_name]
gst_doc = gst_collection.GSystemType.one({'name': GAPPS[1]})

def doc(request, doc_id):
    """
    * Renders a list of all 'Group-type-GSystems' available within the database.

    """

    if gst_doc._id == ObjectId(doc_id):
        title = gst_doc.name
        
        gs_collection = db[GSystem.collection_name]
        doc_nodes = gs_collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(doc_id)]}})
        doc_nodes.sort('creationtime', -1)
        doc_nodes_count = doc_nodes.count()

        return render_to_response("ndf/doc.html", {'title': title, 'doc_nodes': doc_nodes, 'doc_nodes_count': doc_nodes_count}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('homepage'))


def submitDoc(request):
    db=get_database()[File.collection_name]
    fileobj=db.File()
    if request.method=="POST":
        title = request.POST.get("docTitle","")
        user = request.POST.get("user","")
        memberOf = request.POST.get("memberOf","")
        files=request.FILES.get("doc","")
        #this code is for creating file document and saving
        fileobj.name = unicode(title)
        fileobj.user = unicode(user)
        fileobj.member_of.append(unicode(memberOf))
        fileobj.save()
        filetype=magic.from_buffer(files.read()) #Gusing filetype by python-magic
        print "test",title,user,memberOf	
        #this code is for storing Document in gridfs
        files.seek(0) #moving files cursor to start
        objectid=fileobj.fs.files.put(files.read(),filename=title,content_type=filetype)
        #files.seek(0)		
        #print "fileread:",files.read()
        #print "objectid:",objectid
    return HttpResponseRedirect("/ndf/documentList/")

def GetDoc(request):
    filecollection=get_database()[File.collection_name]
    files=filecollection.File.find()
    template="ndf/DocumentList.html"
    variable=RequestContext(request,{'filecollection':files})
    return render_to_response(template,variable)

def readDoc(request,_id):
    filecollection=get_database()[File.collection_name]
    fileobj=filecollection.File.one({"_id": ObjectId(_id)})  
    fl=fileobj.fs.files.get_last_version(fileobj.name)
    return HttpResponse(fl.read(),content_type=fl.content_type)

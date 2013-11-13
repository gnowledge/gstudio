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
from gnowsys_ndf.ndf.models import File

###########################################################################

def submitDoc(request):
    db=get_database()[File.collection_name]
    fileobj=db.File()
    if request.method=="POST":
        title = request.POST.get("docTitle","")
        user = request.POST.get("user","")
        memberOf = request.POST.get("memberOf","")
        files=request.FILES.get("doc","")
        #this code is for creating file document and saving
        fileobj.name=unicode(title)
        fileobj.user=unicode(user)
        fileobj.member_of=unicode(memberOf)
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

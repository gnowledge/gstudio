''' -- imports from python libraries -- '''
import hashlib # for calculating md5
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
from PIL import Image #install PIL example:pip install PIL
from StringIO import StringIO


#from string import maketrans 


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem
from gnowsys_ndf.ndf.models import File

#######################################################################################################################################

db = get_database()
gst_collection = db[GSystemType.collection_name]
gst_file = gst_collection.GSystemType.one({'name': GAPPS[1]})

#######################################################################################################################################
#                                                                            V I E W S   D E F I N E D   F O R   G A P P -- ' P A G E '
#######################################################################################################################################


def file(request, file_id):
    """
    * Renders a list of all 'Group-type-GSystems' available within the database.

    """
    if gst_file._id == ObjectId(file_id):
        title = gst_file.name
        
        gs_collection = db[GSystem.collection_name]
        file_nodes = gs_collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(file_id)]}})
        file_nodes.sort('last_update', -1)
        file_nodes_count = file_nodes.count()

        return render_to_response("ndf/file.html", {'title': title, 'file_nodes': file_nodes, 'file_nodes_count': file_nodes_count}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('homepage'))


def uploadDoc(request):
    stId,mainPageUrl="",""
    if request.method=="POST":
        stId=request.POST.get("stId","")
        mainPageUrl=request.POST.get("pageUrl","")
    template="ndf/UploadDoc.html"
    if stId and mainPageUrl:
        variable=RequestContext(request,{'stId':stId,'mainPageUrl':mainPageUrl})
    else:
        print "else"
        variable=RequestContext(request,{})
    return render_to_response(template,variable)
      
    

def submitDoc(request):
    if request.method=="POST":
        title = request.POST.get("docTitle","")
        userid = request.POST.get("user","")
	stId = request.POST.get("stId","")
        mainPageUrl = request.POST.get("mainPageUrl","")
        memberOf = request.POST.get("memberOf","")
	for each in request.FILES.getlist("doc[]",""):
		checkmd5=save_file(each,title,userid,memberOf,stId)
                if (checkmd5=="True"):
                    return HttpResponse("File already uploaded")
        if mainPageUrl:
            return HttpResponseRedirect(mainPageUrl)
        else:
            return HttpResponseRedirect("/ndf/documentList/")

def save_file(files,title,userid,memberOf,stId):
        fcol=db[File.collection_name]
        print "stid",stId
	fileobj=fcol.File()
        #gst=gst_collection.GSystemType.one({"_id":ObjectId(stId)})
	filemd5= hashlib.md5(files.read()).hexdigest()
        files.seek(0)
        filetype=magic.from_buffer(files.read())               #Gusing filetype by python-magic
	if fileobj.fs.files.exists({"md5":filemd5}):
		return "True"
	else:
		fileobj.name=unicode(title)
        	fileobj.created_by=int(userid)
        	#fileobj.member_of=unicode(memberOf)           #shuold be group 
                fileobj.mime_type=filetype
                if stId:
                    fileobj.gsystem_type.append(ObjectId(stId))
        	fileobj.save()
                files.seek(0)                                  #moving files cursor to start
		filename=files.name
		#this code is for storing Document in gridfs
		objectid=fileobj.fs.files.put(files.read(),filename=filename,content_type=filetype)
		fileobj.fs_file_ids.append(objectid)
                #storing thumbnail of image in saved object
                if 'image' in filetype:
                    thumbnailimg=convert_image_thumbnail(files)
                    tobjectid=fileobj.fs.files.put(thumbnailimg,filename=filename+"-thumbnail",content_type=filetype)
                    fileobj.fs_file_ids.append(tobjectid)
		fileobj.save()
                print "filetype:",filetype
                return "False"


def convert_image_thumbnail(files):
    files.seek(0)
    thumb_io=StringIO()
    size=128,128
    img=Image.open(StringIO(files.read()))
    img.thumbnail(size,Image.ANTIALIAS)
    img.save(thumb_io,"JPEG")
    thumb_io.seek(0)
    return thumb_io
		

	
def GetDoc(request):
    filecollection=get_database()[File.collection_name]
    files=filecollection.File.find()
    template="ndf/DocumentList.html"
    variable=RequestContext(request,{'filecollection':files})
    return render_to_response(template,variable)

def readDoc(request,_id):
    filecollection=get_database()[File.collection_name]
    fileobj=filecollection.File.one({"_id": ObjectId(_id)})  
    fl=fileobj.fs.files.get(ObjectId(fileobj.fs_file_ids[0]))
    if 'image' in fl.content_type:
        fl=fileobj.fs.files.get(ObjectId(fileobj.fs_file_ids[1]))
    return HttpResponse(fl.read(),content_type=fl.content_type)

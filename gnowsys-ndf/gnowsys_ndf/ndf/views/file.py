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
import os

#from string import maketrans 


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS

from gnowsys_ndf.ndf.models import GSystemType, GSystem
from gnowsys_ndf.ndf.models import File

###########################################################################

db = get_database()
gst_collection = db[GSystemType.collection_name]
gst_doc = gst_collection.GSystemType.one({'name': GAPPS[1]})

# def file(request, file_id):
#     """
#     * Renders a list of all 'Group-type-GSystems' available within the database.

#     """
#     if gst_doc._id == ObjectId(file_id):
#         title = gst_doc.name
        
#         gs_collection = db[GSystem.collection_name]
#         file_nodes = gs_collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(file_id)]}})
#         file_nodes.sort('creationtime', -1)
#         file_nodes_count = file_nodes.count()

#         return render_to_response("ndf/file.html", {'title': title, 'file_nodes': file_nodes, 'file_nodes_count': file_nodes_count}, context_instance=RequestContext(request))
#     else:
#         return HttpResponseRedirect(reverse('homepage'))

def file(request,file_id):
#     lstImg,lstVid,lstPdf,lstHtml,lstAudio,lstSpreadsheet,lstPresentation=[]
#     if gst_doc._id==ObjectId(file_id):
    # if gst_doc._id == ObjectId(file_id):
    #     title = gst_doc.name
        
    #     gs_collection = db[GSystem.collection_name]
    #     file_nodes = gs_collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(file_id)]}})
    #     file_nodes.sort('creationtime', -1)
    #     file_nodes_count = file_nodes.count()
    #     return render_to_response("ndf/file.html", {'title': title, 'file_nodes': file_nodes, 'file_nodes_count': file_nodes_count}, context_instance=RequestContext(request))
    # else:
    #     return HttpResponseRedirect(reverse('homepage'))
    variable=RequestContext(request,{})
    template="ndf/file.html"
    return render_to_response(template,variable)

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
    alreadyUploadedFiles=[]
    if request.method=="POST":
        title = request.POST.get("docTitle","")
        userid = request.POST.get("user","")
	stId = request.POST.get("stId","")
        mainPageUrl = request.POST.get("mainPageUrl","")
        print "url",mainPageUrl
        memberOf = request.POST.get("memberOf","")
	for each in request.FILES.getlist("doc[]",""):
            f=save_file(each,title,userid,memberOf,stId)
            if f:
                alreadyUploadedFiles.append(f)
        if 'image' in mainPageUrl:
            collection=db[File.collection_name]
            imgcol=collection.File.find({'mime_type': {'$regex': 'image'}})
            variable=RequestContext(request,{'alreadyUploadedFiles':alreadyUploadedFiles,'imageCollection':imgcol})
            template="ndf/ImageDashboard.html"
            return render_to_response(template,variable)
        else:
            filecollection=get_database()[File.collection_name]
            files=filecollection.File.find()
            variable=RequestContext(request,{'alreadyUploadedFiles':alreadyUploadedFiles,'filecollection':files})
            template='ndf/DocumentList.html'
            return render_to_response(template,variable)

def save_file(files,title,userid,memberOf,stId):
    fcol=db[File.collection_name]
    print "stid",stId
    fileobj=fcol.File()
    #gst=gst_collection.GSystemType.one({"_id":ObjectId(stId)})
    filemd5= hashlib.md5(files.read()).hexdigest()
    files.seek(0)
    size,ext=getFileSize(files)
    if fileobj.fs.files.exists({"md5":filemd5}):
            return files.name
    else:
        try:
            files.seek(0)
            filetype=magic.from_buffer(files.read(100000),mime='true')               #Gusing filetype by python-magic
            print "filetype:",filetype
            filename=files.name
            fileobj.name=unicode(title)
            fileobj.created_by=int(userid)
            #fileobj.member_of=unicode(memberOf)           #shuold be group 
            fileobj.mime_type=filetype
            if stId:
                fileobj.gsystem_type.append(ObjectId(stId))
            fileobj.save()
            files.seek(0)   #moving files cursor to start
            #this code is for storing Document in gridfs
            objectid=fileobj.fs.files.put(files.read(),filename=filename,content_type=filetype)
            print "file uploaded:",objectid
            fileobj.fs_file_ids.append(objectid)
            fileobj.save()
            #storing thumbnail of image in saved object
            print "test filetype:",filetype
            if 'image' in filetype:
                thumbnailimg=convert_image_thumbnail(files)
                tobjectid=fileobj.fs.files.put(thumbnailimg,filename=filename+"-thumbnail",content_type=filetype)
                fileobj.fs_file_ids.append(tobjectid)
                fileobj.save()
                print "thumbnail uploaded",tobjectid
        except Exception as e:
            print "Not Uploaded files:",files.name,"Execption:",e

def getFileSize(File):
        File.seek(0,os.SEEK_END)
        num=File.tell() 
        for x in ['bytes','KB','MB','GB','TB']:
                if num < 1024.0:
                        return  (num, x)
                num /= 1024.0


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
    #return files
    template="ndf/DocumentList.html"
    variable=RequestContext(request,{'filecollection':files})
    return render_to_response(template,variable)

def readDoc(request,_id):
    filecollection=get_database()[File.collection_name]
    fileobj=filecollection.File.one({"_id": ObjectId(_id)})  
    fl=fileobj.fs.files.get(ObjectId(fileobj.fs_file_ids[0]))
    return HttpResponse(fl.read(),content_type=fl.content_type)

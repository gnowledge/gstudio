''' -- imports from python libraries -- '''
from django.template.defaultfilters import slugify
import hashlib # for calculating md5
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response #, render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django_mongokit import get_database
from gnowsys_ndf.ndf.org2any import org2html

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

import magic  #for this install python-magic example:pip install python-magic
import mimetypes
from PIL import Image, ImageDraw, ImageFile #install PIL example:pip install PIL
from StringIO import StringIO
import os
import subprocess
import ox
#from string import maketrans 


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT

from gnowsys_ndf.ndf.models import GSystemType#, GSystem uncomment when to use
from gnowsys_ndf.ndf.models import File

#######################################################################################################################################

db = get_database()
GST_COLLECTION = db[GSystemType.collection_name]
GST_FILE = GST_COLLECTION.GSystemType.one({'name': GAPPS[1]})
GST_IMAGE = GST_COLLECTION.GSystemType.one({'name': GAPPS[3]})
GST_VIDEO = GST_COLLECTION.GSystemType.one({'name': GAPPS[4]})


####################################################################################################################################                                             V I E W S   D E F I N E D   F O R   G A P P -- ' F I L E '
###################################################################################################################################

def file(request, group_name, file_id):
    """
   * Renders a list of all 'Files' available within the database.
    """
    if GST_FILE._id == ObjectId(file_id):
        title = GST_FILE.name
        collection = db[File.collection_name]
        files = collection.GSystem.find({'gsystem_type': {'$all': [ObjectId(file_id)]},'_type':'File', 'group_set': {'$all': [group_name]}})
        already_uploaded = request.GET.getlist('var', "")
        return render_to_response("ndf/file.html", {'title': title, 'files':files, 'already_uploaded':already_uploaded}, context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('homepage'))
        
@login_required    
def uploadDoc(request, group_name):
    if request.method == "GET":
        page_url = request.GET.get("next", "")
        template = "ndf/UploadDoc.html"
    if  page_url:
        variable = RequestContext(request, {'page_url': page_url})
    else:
        variable = RequestContext(request, {})
    return render_to_response(template, variable)
      
    

@login_required
def submitDoc(request, group_name):
    """
    submit files for saving into gridfs and creating object
    """
    alreadyUploadedFiles = []
    str1 = ''
    if request.method == "POST":
        mtitle = request.POST.get("docTitle", "")
        userid = request.POST.get("user", "")
        usrname = request.user.username
        page_url = request.POST.get("page_url", "")
        content_org = request.POST.get('content_org', '')
        print "content:", content_org
        tags = request.POST.get('tags')
        #memberOf = request.POST.get("memberOf", "")
        i = 1
	for index, each in enumerate(request.FILES.getlist("doc[]", "")):
            if mtitle:
                if index == 0:
                    f = save_file(each, mtitle, userid, group_name, GST_FILE._id.__str__(), content_org, tags, usrname)
                else:
                    title = mtitle + "_" + str(i) #increament title        
                    f = save_file(each, title, userid, group_name, GST_FILE._id.__str__(), content_org, tags, usrname)
                    i = i + 1
            else:
                title = each.name
                f = save_file(each, title, userid, group_name, GST_FILE._id.__str__(), content_org, tags, usrname)
            if f:
                alreadyUploadedFiles.append(f)
                title = mtitle
        for each in alreadyUploadedFiles:
            str1 = str1 + 'var=' + each + '&'
        return HttpResponseRedirect(page_url+'?'+str1)
    else:
        return HttpResponseRedirect(reverse('homepage'))
            
def save_file(files, title, userid, group_name, st_id, content_org, tags, usrname):
    """
    this will create file object and save files in gridfs collection
    """
    fcol = db[File.collection_name]
    fileobj = fcol.File()
    filemd5 = hashlib.md5(files.read()).hexdigest()
    files.seek(0)
    size, unit = getFileSize(files)
    size = {'size':round(size, 2), 'unit':unicode(unit)}
    if fileobj.fs.files.exists({"md5":filemd5}):
        return files.name                                                                #return already exist file
    else:
        try:
            files.seek(0)
            filetype = magic.from_buffer(files.read(100000), mime = 'true')               #Gusing filetype by python-magic
            filetype1 = mimetypes.guess_type(files.name)[0]
            if filetype1:
                filetype1 = filetype1
            else :
                filetype1 = ""
            filename = files.name
            fileobj.name = unicode(title)
            fileobj.created_by = int(userid)
            fileobj.file_size = size
            fileobj.group_set.append(unicode(group_name))        #group name stored in group_set field
            fileobj.gsystem_type.append(GST_FILE._id)
            fileobj.mime_type = filetype
            if content_org:
                fileobj.content_org = unicode(content_org)
                # Required to link temporary files with the current user who is modifying this document
                filename = slugify(title) + "-" + usrname + "-"
                fileobj.content = org2html(content_org, file_prefix=filename)
            fileobj.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]
            fileobj.save()
            files.seek(0)                                                                  #moving files cursor to start
            objectid = fileobj.fs.files.put(files.read(), filename=filename, content_type=filetype) #store files into gridfs
            fileobj.fs_file_ids.append(objectid)
            fileobj.save()

            """ 
            code for converting video into webm and converted video assigning to varible files
            """
            if 'video' in filetype or 'video' in filetype1 or filename.endswith('.webm') == True:
            	fileobj.mime_type = "video"
                fileobj.gsystem_type.append(GST_VIDEO._id)
       	        fileobj.save()
            	webmfiles, filetype, thumbnailvideo = convertVideo(files, userid, fileobj._id)
	       
                '''storing thumbnail of video with duration in saved object'''
                tobjectid = fileobj.fs.files.put(thumbnailvideo.read(), filename=filename+"-thumbnail", content_type="thumbnail-image") 
       	        fileobj.fs_file_ids.append(tobjectid)                                      #saving thumbnail's id into file object
       	        fileobj.save()
       	        if filename.endswith('.webm') == False:
                    tobjectid = fileobj.fs.files.put(webmfiles.read(), filename=filename+".webm", content_type=filetype)
                    fileobj.fs_file_ids.append(tobjectid) # saving webm video id into file object
                    fileobj.save()

            '''storing thumbnail of image in saved object'''
            if 'image' in filetype:
                fileobj.gsystem_type.append(GST_IMAGE._id)
                thumbnailimg = convert_image_thumbnail(files)
                tobjectid = fileobj.fs.files.put(thumbnailimg, filename=filename+"-thumbnail", content_type=filetype)
                fileobj.fs_file_ids.append(tobjectid)
                fileobj.save()
                files.seek(0)
                mid_size_img = convert_mid_size_image(files)
                mid_img_id = fileobj.fs.files.put(mid_size_img, filename=filename+"-mid_size_img", content_type=filetype)
                fileobj.fs_file_ids.append(mid_img_id)
                fileobj.save()

        except Exception as e:
            print "Some Exception:", files.name, "Execption:", e

def getFileSize(File):
    """
    obtain file size if provided file object
    """
    try:
        File.seek(0,os.SEEK_END)
        num=int(File.tell())
        for x in ['bytes','KB','MB','GB','TB']:
            if num < 1024.0:
                return  (num, x)
            num /= 1024.0
    except Exception as e:
        print "Unabe to calucalate size",e
        return 0,'bytes'
                     
def convert_image_thumbnail(files):
    """
    convert image file into thumbnail
    """
    files.seek(0)
    thumb_io = StringIO()
    size = 128, 128
    img = Image.open(StringIO(files.read()))
    img.thumbnail(size, Image.ANTIALIAS)
    img.save(thumb_io, "JPEG")
    thumb_io.seek(0)
    return thumb_io

def convert_mid_size_image(files):
    '''
    convert image into 1000 pixel size userd for image gallery
    '''
    mid_size_img = StringIO()
    img = Image.open(StringIO(files.read()))
    width , height = img.size
    diff = width - height
    if (diff > 0):
        diviser = width / 1000
    else:
        diviser = height / 1000
    size = int(width / diviser),int(height / diviser)
    img.resize(size,Image.ANTIALIAS)
    img.save(mid_size_img, "JPEG")
    mid_size_img.seek(0)
    return mid_size_img
    
    
    
def convertVideo(files, userid, objid):
    """
    converting video into webm format, if video already in webm format ,then pass to create thumbnails
    """
    fileVideoName = str(objid)
    initialFileName = str(objid)
    os.system("mkdir -p "+ "/tmp"+"/"+str(userid)+"/"+fileVideoName+"/")
    fd = open('%s/%s/%s/%s' % (str("/tmp"), str(userid),str(fileVideoName), str(fileVideoName)), 'wb')
    for chunk in files.chunks():
        fd.write(chunk)
    fd.close()
    if files._get_name().endswith('.webm') == False:
        proc = subprocess.Popen(['ffmpeg', '-y', '-i', str("/tmp/"+userid+"/"+fileVideoName+"/"+fileVideoName), str("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+".webm")])
        proc.wait()
        files = open("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+".webm")
    else : 
        files = open("/tmp/"+userid+"/"+fileVideoName+"/"+fileVideoName)
    filetype = "video"
    oxData = ox.avinfo("/tmp/"+userid+"/"+fileVideoName+"/"+fileVideoName)
    duration = oxData['duration'] # fetching duration of video by python ox
    duration = int(duration)
    secs, mins, hrs = 00, 00, 00
    if duration > 60 :
        secs  = duration % 60
        mins = duration / 60
        if mins > 60 :
            hrs = mins / 60
            mins = mins % 60 
    else:
        secs = duration
    videoDuration = ""
    durationTime = str(str(hrs)+":"+str(mins)+":"+str(secs)) # calculating Time duration of video in hrs,mins,secs

    if duration > 30 :
	videoDuration = "00:00:30"
    else :
    	videoDuration = "00:00:00"    	
    proc = subprocess.Popen(['ffmpeg', '-i', str("/tmp/"+userid+"/"+fileVideoName+"/"+fileVideoName), '-ss', videoDuration, "-s", "170*128", "-vframes", "1", str("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+".png")]) # creating thumbnail of video using ffmpeg
    proc.wait()
    background = Image.open("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+".png")
    fore = Image.open(MEDIA_ROOT+"ndf/images/poster.jpg")
    background.paste(fore, (120, 100))
    draw = ImageDraw.Draw(background)
    draw.text((120, 100), durationTime, (255, 255, 255)) # drawing duration time on thumbnail image
    background.save("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+"Time.png")
    thumbnailvideo = open("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+"Time.png")
    return files, filetype, thumbnailvideo

	
def GetDoc(request, group_name):
    filecollection = get_database()[File.collection_name]
    files = filecollection.File.find({'_type': u'File'})
    #return files
    template = "ndf/DocumentList.html"
    variable = RequestContext(request, {'filecollection':files})
    return render_to_response(template, variable)

def readDoc(request, _id, group_name):
    filecollection = get_database()[File.collection_name]
    fileobj = filecollection.File.one({"_id": ObjectId(_id)})  
    grid_fs_obj = fileobj.fs.files.get(ObjectId(fileobj.fs_file_ids[0]))
    return HttpResponse(grid_fs_obj.read(), content_type = grid_fs_obj.content_type)

def file_search(request, group_name):
    if request.method == "GET":
        keyword = request.GET.get("search", "")
        files = db[File.collection_name]
        file_search = files.File.find({'$or':[{'name':{'$regex': keyword}}, {'tags':{'$regex':keyword}}]}) #search result from file
        template = "ndf/file_search.html"
        variable = RequestContext(request, {'file_collection':file_search, 'view_name':'file_search'})
        return render_to_response(template, variable)

@login_required    
def delete_file(request, group_name, _id):
  """Delete file and its data
  """
  file_collection = db[File.collection_name]
  pageurl = request.GET.get("next", "")
  try:
    cur = file_collection.File.one({'_id':ObjectId(_id)})
    if cur.fs_file_ids:
        for each in cur.fs_file_ids:
            cur.fs.files.delete(each)
    cur.delete()
  except Exception as e:
    print "Exception:", e
  return HttpResponseRedirect(pageurl) 

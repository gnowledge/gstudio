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
import threading
from django.http import Http404
#from string import maketrans 


''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT

from gnowsys_ndf.ndf.models import Node, GRelation
from gnowsys_ndf.ndf.models import GSystemType#, GSystem uncomment when to use
from gnowsys_ndf.ndf.models import File
from gnowsys_ndf.ndf.views.methods import get_node_common_fields

#######################################################################################################################################

db = get_database()
collection = db[Node.collection_name]
GST_FILE = collection.GSystemType.one({'name': GAPPS[1], '_type':'GSystemType'})
GST_IMAGE = collection.GSystemType.one({'name': GAPPS[3], '_type':'GSystemType'})
GST_VIDEO = collection.GSystemType.one({'name': GAPPS[4], '_type':'GSystemType'})

####################################################################################################################################                                             V I E W S   D E F I N E D   F O R   G A P P -- ' F I L E '
###################################################################################################################################
lock=threading.Lock()
count = 0    
def file(request, group_id, file_id):
    """
   * Renders a list of all 'Files' available within the database.
    """
    if GST_FILE._id == ObjectId(file_id):
        title = GST_FILE.name
       
        files = collection.Node.find({'member_of': {'$all': [ObjectId(file_id)]}, '_type': 'File', 'fs_file_ids':{'$ne': []}, 'group_set': {'$all': [ObjectId(group_id)]}}).sort("last_update", -1)
        docCollection = collection.Node.find({'member_of': {'$nin': [ObjectId(GST_IMAGE._id), ObjectId(GST_VIDEO._id)]}, '_type': 'File','fs_file_ids': {'$ne': []}, 'group_set': {'$all': [ObjectId(group_id)]}}).sort("last_update", -1)
        imageCollection = collection.Node.find({'member_of': {'$all': [ObjectId(GST_IMAGE._id)]}, '_type': 'File','fs_file_ids': {'$ne': []}, 'group_set': {'$all': [ObjectId(group_id)]}}).sort("last_update", -1)
        videoCollection = collection.Node.find({'member_of': {'$all': [ObjectId(GST_VIDEO._id)]}, '_type': 'File','fs_file_ids': {'$ne': []}, 'group_set': {'$all': [ObjectId(group_id)]}}).sort("last_update", -1)
        already_uploaded = request.GET.getlist('var', "")
    
        '''                                                                                                                                 saving wetube.gnowledge.org videos data in GSystem, with locking                                                            
        '''
        lock.acquire()
        try:
                api=ox.api.API("http://wetube.gnowledge.org/api")
                #countVideo = api.find({"query":{"operator":"&","conditions":[{"operator":"==","key":"project","value":"NROER"}]}})
                #totalVideoNo=countVideo['data']['items']
                allVideo = api.find({"keys":["id","title","director","id","posterRatio","year","user"],"query":{"conditions":[{"oper\
ator":"==","key":"project","value":"NROER"}],"operator":"&"},"sort":[{"operator":"+","key":"title"}]})

                allVideosData=allVideo['data']['items']

                pandora_video_st=collection.Node.one({'$and':[{'name':'Pandora_video'},{'_type':'GSystemType'}]}) 
                source_id_at=collection.Node.one({'$and':[{'name':'source_id'},{'_type':'AttributeType'}]}) 
                pandora_video_id=[] 
                source_id_set=[]
                for each in allVideosData[:50]: 
                    gattribute=collection.Node.one({'$and':[{'object_value':each['id']},{'_type':'GAttribute'},{'attribute_type.$id':source_id_at._id}]}) 
                    if gattribute is None: 
                        #gs=collection.GSystem() 
                        gs=collection.File()
                        gs.mime_type="video"
                        gs.member_of=[pandora_video_st._id] 
                        gs.name=each['title'].lower()
                        gs.created_by=1
                        gs.modified_by = 1
                        if 1 not in gs.contributors:
                            gs.contributors.append(1)
                        gs.save() 

                        at=collection.GAttribute() 
                        at.attribute_type=source_id_at 
                        at.object_value=each['id'] 
                        at.subject=gs._id 
                        at.save() 
                get_member_set=collection.Node.find({'$and':[{'member_of': {'$all': [ObjectId(pandora_video_st._id)]}},{'_type':'Fil\
e'}]})
      
                for each in get_member_set:
                    pandora_video_id.append(each['_id'])
                for each in pandora_video_id:
                    att_set=collection.Node.one({'$and':[{'subject':each},{'_type':'GAttribute'},{'attribute_type.$id':source_id_at._id}]})
                    if att_set:
                        object1=collection.Node.one({'_id':each})
                        obj_set={}
                        obj_set['id']=att_set.object_value
                        obj_set['object']=object1
                        source_id_set.append(obj_set)

                # for each in pandora_video_id:
                #     get_video = collection.GSystem.find({'member_of': {'$all': [ObjectId(file_id)]}, '_type': 'File', 'group_set': {'$all': [ObjectId(group_id)]}})
        
                
        finally:
            lock.release()

        return render_to_response("ndf/file.html", 
                                  {'title': title, 
                                   'files': files,
                                   'sourceid':source_id_set,
                                   'docCollection': docCollection,
                                   'imageCollection': imageCollection,
                                   'videoCollection': videoCollection,
                                   'already_uploaded': already_uploaded,
                                   'groupid': group_id,
                                   'group_id':group_id
                                  }, 
                                  context_instance = RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('homepage',kwargs={'group_id': group_id, 'groupid':group_id}))
        
@login_required    
def uploadDoc(request, group_id):
    if request.method == "GET":
        page_url = request.GET.get("next", "")
        template = "ndf/UploadDoc.html"
    if  page_url:
        variable = RequestContext(request, {'page_url': page_url,'groupid':group_id,'group_id':group_id})
    else:
        variable = RequestContext(request, {'groupid':group_id,'group_id':group_id})
    return render_to_response(template, variable)
      
    

@login_required
def submitDoc(request, group_id):
    """
    submit files for saving into gridfs and creating object
    """
    alreadyUploadedFiles = []
    str1 = ''
    img_type=""
    obj_id_instance = ObjectId()
    if request.method == "POST":
        mtitle = request.POST.get("docTitle", "")
        userid = request.POST.get("user", "")
        language = request.POST.get("lan", "")
        img_type = request.POST.get("type", "")
        usrname = request.user.username
        page_url = request.POST.get("page_url", "")
        content_org = request.POST.get('content_org', '')
        access_policy = request.POST.get("login-mode", '') # To add access policy(public or private) to file object
        tags = request.POST.get('tags')

        i = 1
	for index, each in enumerate(request.FILES.getlist("doc[]", "")):
            if mtitle:
                if index == 0:

                    f = save_file(each, mtitle, userid, group_id, content_org, tags, img_type, language, usrname, access_policy)
                else:
                    title = mtitle + "_" + str(i) #increament title        
                    f = save_file(each, title, userid, group_id, content_org, tags, img_type, language, usrname, access_policy)
                    i = i + 1
            else:
                title = each.name
                f = save_file(each,title,userid,group_id, content_org, tags, img_type, language, usrname, access_policy)
            if not obj_id_instance.is_valid(f):
                alreadyUploadedFiles.append(f)
                title = mtitle
        for each in alreadyUploadedFiles:
            str1 = str1 + 'var=' + each + '&'

        if img_type != "": 
            
            return HttpResponseRedirect(reverse('userDashboard', kwargs={'group_id': group_id }))

        else:
            return HttpResponseRedirect(page_url+'?'+str1)

    else:
        return HttpResponseRedirect(reverse('homepage',kwargs={'group_id': group_id, 'groupid':group_id}))


    
first_object = ''
def save_file(files,title, userid, group_id, content_org, tags, img_type = None, language = None, usrname = None, access_policy=None):
    """
    this will create file object and save files in gridfs collection
    """
    global count,first_object
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
            if language:
                fileobj.language= unicode(language)
            fileobj.created_by = int(userid)
            fileobj.modified_by = int(userid)
            if int(userid) not in fileobj.contributors:
                fileobj.contributors.append(int(userid))
            
            if access_policy:
                fileobj.access_policy = unicode(access_policy) # For giving privacy to file objects   
            
            fileobj.file_size = size
            group_object=fcol.Group.one({'_id':ObjectId(group_id)})
            
            if group_object._id not in fileobj.group_set:
                fileobj.group_set.append(group_object._id)        #group id stored in group_set field
            if usrname:
                user_group_object=fcol.Group.one({'$and':[{'_type':u'Group'},{'name':usrname}]})
                if user_group_object:
                    if user_group_object._id not in fileobj.group_set:                 # File creator_group_id stored in group_set field
                        fileobj.group_set.append(user_group_object._id)

            fileobj.member_of.append(GST_FILE._id)
            fileobj.mime_type = filetype
            if img_type == None:
                if content_org:
                    fileobj.content_org = unicode(content_org)
                    # Required to link temporary files with the current user who is modifying this document
                    filename_content = slugify(title) + "-" + usrname + "-"
                    fileobj.content = org2html(content_org, file_prefix = filename_content)
                fileobj.tags = [unicode(t.strip()) for t in tags.split(",") if t != ""]
            
            fileobj.save()
            files.seek(0)                                                                  #moving files cursor to start
            objectid = fileobj.fs.files.put(files.read(), filename=filename, content_type=filetype) #store files into gridfs
            collection.File.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':objectid}})
            
            # For making collection if uploaded file more than one
            if count == 0:
                first_object = fileobj
            else:
                collection.File.find_and_modify({'_id':first_object._id},{'$push':{'collection_set':fileobj._id}})
                
                
            """ 
            code for converting video into webm and converted video assigning to varible files
            """
            if 'video' in filetype or 'video' in filetype1 or filename.endswith('.webm') == True:
                collection.File.find_and_modify({'_id':fileobj._id},{'$push':{'member_of':GST_VIDEO._id}})
                collection.File.find_and_modify({'_id':fileobj._id},{'$set':{'mime_type':'video'}})
            	webmfiles, filetype, thumbnailvideo = convertVideo(files, userid, fileobj._id)
	       
                '''storing thumbnail of video with duration in saved object'''
                tobjectid = fileobj.fs.files.put(thumbnailvideo.read(), filename=filename+"-thumbnail", content_type="thumbnail-image") 
       	        
                collection.File.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':tobjectid}})
                
       	        if filename.endswith('.webm') == False:
                    tobjectid = fileobj.fs.files.put(webmfiles.read(), filename=filename+".webm", content_type=filetype)
                    # saving webm video id into file object
                    collection.File.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':tobjectid}})

            '''storing thumbnail of image in saved object'''
            if 'image' in filetype:
                collection.File.find_and_modify({'_id':fileobj._id},{'$push':{'member_of':GST_IMAGE._id}})
                thumbnailimg = convert_image_thumbnail(files)
                tobjectid = fileobj.fs.files.put(thumbnailimg, filename=filename+"-thumbnail", content_type=filetype)
                collection.File.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':tobjectid}})
                
                files.seek(0)
                mid_size_img = convert_mid_size_image(files)
                if mid_size_img:
                    mid_img_id = fileobj.fs.files.put(mid_size_img, filename=filename+"-mid_size_img", content_type=filetype)
                    collection.File.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':mid_img_id}})
            count = count + 1
            return fileobj._id
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
    proc = subprocess.Popen(['ffmpeg', '-i', str("/tmp/"+userid+"/"+fileVideoName+"/"+fileVideoName), '-ss', videoDuration, "-s", "170*128", "-vframes", "1", str("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+".png")]) # GScreating thumbnail of video using ffmpeg
    proc.wait()
    background = Image.open("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+".png")
    fore = Image.open(MEDIA_ROOT+"ndf/images/poster.jpg")
    background.paste(fore, (120, 100))
    draw = ImageDraw.Draw(background)
    draw.text((120, 100), durationTime, (255, 255, 255)) # drawing duration time on thumbnail image
    background.save("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+"Time.png")
    thumbnailvideo = open("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+"Time.png")
    return files, filetype, thumbnailvideo

	
def GetDoc(request, group_id):
    filecollection = get_database()[File.collection_name]
    files = filecollection.File.find({'_type': u'File'})
    #return files
    template = "ndf/DocumentList.html"
    variable = RequestContext(request, {'filecollection':files,'groupid':group_id,'group_id':group_id})
    return render_to_response(template, variable)


def file_search(request, group_id):
    if request.method == "GET":
        keyword = request.GET.get("search", "")
        files = db[File.collection_name]
        file_search = files.File.find({'$or':[{'name':{'$regex': keyword}}, {'tags':{'$regex':keyword}}]}) #search result from file
        template = "ndf/file_search.html"
        variable = RequestContext(request, {'file_collection':file_search, 'view_name':'file_search','groupid':group_id,'group_id':group_id})
        return render_to_response(template, variable)

@login_required    
def delete_file(request, group_id, _id):
  """Delete file and its data
  """
  file_collection = db[File.collection_name]
  auth = collection.Node.one({'_type': u'Group', 'name': unicode(request.user.username) })
  pageurl = request.GET.get("next", "")
  try:
    cur = file_collection.File.one({'_id':ObjectId(_id)})
    rel_obj = collection.GRelation.one({'subject': ObjectId(auth._id), 'right_subject': ObjectId(_id) })
    if rel_obj :
        rel_obj.delete()
    if cur.fs_file_ids:
        for each in cur.fs_file_ids:
            cur.fs.files.delete(each)
    cur.delete()
  except Exception as e:
    print "Exception:", e
  return HttpResponseRedirect(pageurl) 


def file_detail(request, group_id, _id):
    """Depending upon mime-type of the node, this view returns respective display-view.
    """
    file_node = collection.File.one({"_id": ObjectId(_id)})

    file_template = ""
    if file_node.mime_type:
        if file_node.mime_type == 'video':      
            file_template = "ndf/video_detail.html"
        elif 'image' in file_node.mime_type:
            file_template = "ndf/image_detail.html"
        else:
            file_template = "ndf/document_detail.html"
        #grid_fs_obj = file_node.fs.files.get(ObjectId(file_node.fs_file_ids[0]))
        #return HttpResponse(grid_fs_obj.read(), content_type = grid_fs_obj.content_type)
    else:
         raise Http404 

    breadcrumbs_list = []
    breadcrumbs_list.append(( str(file_node._id), file_node.name ))
    return render_to_response(file_template,
                              { 'node': file_node,
                                'group_id': group_id,
                                'groupid':group_id,
                                'breadcrumbs_list': breadcrumbs_list
                              },
                              context_instance = RequestContext(request)
                             )

def getFileThumbnail(request, group_id, _id):
    """Returns thumbnail of respective file
    """
    file_node = collection.File.one({"_id": ObjectId(_id)})

    if file_node is not None:
        if file_node.fs_file_ids:
            if (file_node.fs.files.exists(file_node.fs_file_ids[1])):
                f = file_node.fs.files.get(ObjectId(file_node.fs_file_ids[1]))
                return HttpResponse(f.read(), content_type=f.content_type)
            else:
                return HttpResponse("")
        else:
            return HttpResponse("")
    else:
        return HttpResponse("")

def readDoc(request, _id, group_id, file_name = ""):
    '''Return Files 
    '''
    print "inside read doc",group_id,file_name,_id
    file_node = collection.File.one({"_id": ObjectId(_id)})
    if file_node is not None:
        if file_node.fs_file_ids:
            if (file_node.fs.files.exists(file_node.fs_file_ids[0])):
                grid_fs_obj = file_node.fs.files.get(ObjectId(file_node.fs_file_ids[0]))
                return HttpResponse(grid_fs_obj.read(), content_type = grid_fs_obj.content_type)
            else:
                return HttpResponse("")
        else:
            print "else in fs_file_ids"
            return HttpResponse("")
    else:
        return HttpResponse("")

def file_edit(request,group_id,_id):
    file_node = collection.File.one({"_id": ObjectId(_id)})
    if request.method == "POST":
        get_node_common_fields(request, file_node, group_id, GST_FILE)
        file_node.save()
        return HttpResponseRedirect(reverse('file_detail', kwargs={'group_id': group_id, '_id': file_node._id}))
        
    else:
        return render_to_response("ndf/document_edit.html",
                                  { 'node': file_node,
                                    'group_id': group_id,
                                    'groupid':group_id
                                },
                                  context_instance=RequestContext(request)
                              )

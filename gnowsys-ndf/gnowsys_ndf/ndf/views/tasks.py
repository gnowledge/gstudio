from celery import task
import ox
import os
import magic
import subprocess
import mimetypes
import pandora_client
from PIL import Image, ImageDraw
from StringIO import StringIO
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.settings import MEDIA_ROOT 

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

@task    
def convertVideo(userid, file_id, filename):
    """
    converting video into webm format, if video already in webm format ,then pass to create thumbnails
    """
    
    fileobj = node_collection.one({'_id':ObjectId(file_id)})
    
    objid = fileobj._id
    fileVideoName = str(objid)
    initialFileName = str(objid)

    files =  fileobj.fs.files.get(ObjectId(fileobj.fs_file_ids[0]))
    
    # -- create tmp directory
    os.system("mkdir -p "+ "/tmp"+"/"+str(userid)+"/"+fileVideoName+"/")
    # -- create tmp file
    fd = open('%s/%s/%s/%s' % (str("/tmp"), str(userid),str(fileVideoName), str(fileVideoName)), 'wb')

    # -- writing uploaded files chunk to tmp file
    for line in files:
        fd.write(line)
    fd.close()
    # -- convert tmp_file tmp_webm file in local disk
    if files.filename.endswith('.webm') == False:
        input_filename = str("/tmp/"+userid+"/"+fileVideoName+"/"+fileVideoName)
        output_filename = str("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+".webm")
        proc = subprocess.Popen(['ffmpeg', '-y', '-i', input_filename,output_filename])
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
    fore = Image.open(MEDIA_ROOT + "ndf/images/poster.jpg")
    background.paste(fore, (120, 100))
    draw = ImageDraw.Draw(background)
    draw.text((120, 100), durationTime, (255, 255, 255)) # drawing duration time on thumbnail image
    background.save("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+"Time.png")
    thumbnailvideo = open("/tmp/"+userid+"/"+fileVideoName+"/"+initialFileName+"Time.png")
    
    webmfiles = files
    '''storing thumbnail of video with duration in saved object'''
    tobjectid = fileobj.fs.files.put(thumbnailvideo.read(), filename=filename+"-thumbnail", content_type="thumbnail-image") 
    
    node_collection.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':tobjectid}})
    if filename.endswith('.webm') == False:
        tobjectid = fileobj.fs.files.put(webmfiles.read(), filename=filename+".webm", content_type=filetype)

        # --saving webm video id into file object
        node_collection.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':tobjectid}})


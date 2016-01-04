from celery import task

from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from gnowsys_ndf.notification import models as notification
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.models import node_collection, triple_collection
import json

import ox
import os
import magic
import subprocess
import mimetypes
import pandora_client
from PIL import Image, ImageDraw
from StringIO import StringIO

from gnowsys_ndf.settings import MEDIA_ROOT 


try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


# sitename = Site.objects.all()[0]
site = Site.objects.get(pk=1)
site_domain = site.domain
# print "=== site_domain: ", site_domain
sitename = unicode(site.name.__str__())

@task
def task_set_notify_val(request_user_id, group_id, msg, activ, to_user):
    '''
        Attach notification mail to celery task
    '''
    request_user = User.objects.get(id=request_user_id)
    to_send_user = User.objects.get(id=to_user)
    try:
        group_obj = node_collection.one({'_id': ObjectId(group_id)})
        # site = sitename.name.__str__()
        objurl = "http://test"
        render = render_to_string(
            "notification/label.html",
            {
                'sender': request_user.username,
                'activity': activ,
                'conjunction': '-',
                'object': group_obj,
                'site': sitename,
                'link': objurl
            }
        )
        notification.create_notice_type(render, msg, "notification")
        notification.send([to_send_user], render, {"from_user": request_user})
        return True
    except Exception as e:
        print "Error in sending notification- "+str(e)
        return False


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
        input_filename = str("/tmp/"+str(userid)+"/"+fileVideoName+"/"+fileVideoName)
        output_filename = str("/tmp/"+str(userid)+"/"+fileVideoName+"/"+initialFileName+".webm")
        proc = subprocess.Popen(['ffmpeg', '-y', '-i', input_filename,output_filename])
        proc.wait()
        files = open("/tmp/"+str(userid)+"/"+fileVideoName+"/"+initialFileName+".webm")
    else : 
        files = open("/tmp/"+str(userid)+"/"+fileVideoName+"/"+fileVideoName)
    
    filetype = "video"
    oxData = ox.avinfo("/tmp/"+str(userid)+"/"+fileVideoName+"/"+fileVideoName)
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
    proc = subprocess.Popen(['ffmpeg', '-i', str("/tmp/"+str(userid)+"/"+fileVideoName+"/"+fileVideoName), '-ss', videoDuration, "-s", "170*128", "-vframes", "1", str("/tmp/"+str(userid)+"/"+fileVideoName+"/"+initialFileName+".png")]) # GScreating thumbnail of video using ffmpeg
    proc.wait()
    background = Image.open("/tmp/"+str(userid)+"/"+fileVideoName+"/"+initialFileName+".png")
    fore = Image.open(MEDIA_ROOT + "ndf/images/poster.jpg")
    background.paste(fore, (120, 100))
    draw = ImageDraw.Draw(background)
    draw.text((120, 100), durationTime, (255, 255, 255)) # drawing duration time on thumbnail image
    background.save("/tmp/"+str(userid)+"/"+fileVideoName+"/"+initialFileName+"Time.png")
    thumbnailvideo = open("/tmp/"+str(userid)+"/"+fileVideoName+"/"+initialFileName+"Time.png")
    
    webmfiles = files
    '''storing thumbnail of video with duration in saved object'''
    th_gridfs_id = fileobj.fs.files.put(thumbnailvideo.read(), filename=filename+"-thumbnail", content_type="image/png") 

    # node_collection.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':th_gridfs_id}})

    # print "fileobj.fs_file_ids: ", fileobj.fs_file_ids
    node_fs_file_ids = fileobj.fs_file_ids

    if len(node_fs_file_ids) == 1:
        node_fs_file_ids.append(ObjectId(th_gridfs_id))
    elif len(node_fs_file_ids) > 1:
        node_fs_file_ids[1] = ObjectId(th_gridfs_id)

    # print "node_fs_file_ids: ", node_fs_file_ids

    node_collection.collection.update(
                                        {'_id': ObjectId(fileobj._id)},
                                        {'$set': {'fs_file_ids': node_fs_file_ids}}
                                    )

    
    if filename.endswith('.webm') == False:


        vid_gridfs_id = fileobj.fs.files.put(webmfiles.read(), filename=filename+".webm", content_type=filetype)

        fileobj.reload()
        # print "fileobj.fs_file_ids: ", fileobj.fs_file_ids
        node_fs_file_ids = fileobj.fs_file_ids

        if len(node_fs_file_ids) == 2:
            node_fs_file_ids.append(ObjectId(vid_gridfs_id))
        elif len(node_fs_file_ids) > 2:
            node_fs_file_ids[2] = ObjectId(vid_gridfs_id)

        # print "node_fs_file_ids: ", node_fs_file_ids

        node_collection.collection.update(
                                            {'_id': ObjectId(fileobj._id)},
                                            {'$set': {'fs_file_ids': node_fs_file_ids}}
                                        )

        # --saving webm video id into file object
        # node_collection.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':vid_gridfs_id}})


import json
import ox
import os
import magic
import subprocess
import mimetypes
# import pandora_client
import datetime

from PIL import Image, ImageDraw
from StringIO import StringIO
from celery import task
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

from gnowsys_ndf.notification import models as notification
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.models import node_collection, triple_collection, filehive_collection, benchmark_collection
from gnowsys_ndf.settings import MEDIA_ROOT

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

@task
def task_set_notify_val(request_user_id, group_id, msg, activ, to_user):
    '''
    Attach notification mail to celery task
    '''

    # sitename = Site.objects.all()[0]
    site = Site.objects.get(pk=1)
    site_domain = site.domain
    # print "=== site_domain: ", site_domain
    sitename = unicode(site.name.__str__())

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

    if hasattr(fileobj, 'fs_file_ids'):
        files =  fileobj.fs.files.get(ObjectId(fileobj.fs_file_ids[0]))
    elif hasattr(fileobj, 'if_file'):
        files = fileobj.get_file(fileobj.if_file['original']['relurl'])

    # -- create tmp directory
    os.system("mkdir -p "+ "/tmp"+"/"+str(userid)+"/"+fileVideoName+"/")
    # -- create tmp file
    fd = open('%s/%s/%s/%s' % (str("/tmp"), str(userid),str(fileVideoName), str(fileVideoName)), 'wb')

    # -- writing uploaded files chunk to tmp file
    for line in files:
        fd.write(line)
    fd.close()
    # -- convert tmp_file tmp_webm file in local disk

    if (hasattr(files, 'name') and (files.name.endswith('.webm') == False)) or \
        (hasattr(files, 'filename') and (files.filename.endswith('.webm') == False)):
        input_filename = str("/tmp/"+str(userid)+"/"+fileVideoName+"/"+fileVideoName)
        output_filename = str("/tmp/"+str(userid)+"/"+fileVideoName+"/"+initialFileName+".webm")
        proc = subprocess.Popen(['ffmpeg', '-y', '-i', input_filename,output_filename])
        proc.wait()
        files = open("/tmp/"+str(userid)+"/"+fileVideoName+"/"+initialFileName+".webm")
    else :
        files = open("/tmp/"+str(userid)+"/"+fileVideoName+"/"+fileVideoName)

    filetype = "video"
    filepath = "/tmp/"+str(userid)+"/"+fileVideoName+"/"+fileVideoName
    # print "filepath: ", filepath
    # print "======== ", os.path.isfile(filepath)
    oxData = ox.avinfo(filepath)
    # print "============ oxData: ", oxData
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
    fore = Image.open("gnowsys_ndf/ndf/static/ndf/images/poster.jpg")
    background.paste(fore, (120, 100))
    draw = ImageDraw.Draw(background)
    draw.text((120, 100), durationTime, (255, 255, 255)) # drawing duration time on thumbnail image
    background.save("/tmp/"+str(userid)+"/"+fileVideoName+"/"+initialFileName+"Time.png")
    thumbnailvideo = open("/tmp/"+str(userid)+"/"+fileVideoName+"/"+initialFileName+"Time.png")

    webmfiles = files
    '''storing thumbnail of video with duration in saved object'''

    # th_gridfs_id = fileobj.fs.files.put(thumbnailvideo.read(), filename=filename+"-thumbnail", content_type="image/png")

    if hasattr(fileobj, 'fs_file_ids'):
        th_gridfs_id = fileobj.fs.files.put(thumbnailvideo.read(), filename=filename+"-thumbnail", content_type="image/png")
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
        # node_collection.find_and_modify({'_id':fileobj._id},{'$push':{'fs_file_ids':th_gridfs_id}})

        # print "fileobj.fs_file_ids: ", fileobj.fs_file_ids

    elif hasattr(fileobj, 'if_file'):
        thumbnail_filehive_obj = filehive_collection.collection.Filehive()
        thumbnail_file = thumbnailvideo

        mime_type = 'image/png'
        file_name = unicode( filename + '-thumbnail' )
        thumbnail_file_extension = '.png'

        thumbnail_filehive_id_url_dict = thumbnail_filehive_obj.save_file_in_filehive(
            file_blob=thumbnail_file,
            file_name=file_name,
            first_uploader=userid,
            first_parent=fileobj._id,
            mime_type=mime_type,
            file_extension=thumbnail_file_extension,
            if_image_size_name='thumbnail'
            )

        # print "==== ", thumbnail_filehive_id_url_dict

        node_collection.collection.update(
                                            {'_id': ObjectId(fileobj._id)},
                                            {'$set': {'if_file.thumbnail': thumbnail_filehive_id_url_dict}}
                                        )

    if filename.endswith('.webm') == False:

        if hasattr(fileobj, 'fs_file_ids'):
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

        elif hasattr(fileobj, 'if_file'):
            webm_filehive_obj = filehive_collection.collection.Filehive()
            fileobj.reload()
            midsize_file = webmfiles

            mime_type = webm_filehive_obj.get_file_mimetype(midsize_file)
            file_name = unicode( filename + '.webm' )
            mid_file_extension = '.webm'

            mid_filehive_id_url_dict = webm_filehive_obj.save_file_in_filehive(
                file_blob=midsize_file,
                file_name=file_name,
                first_uploader=userid,
                first_parent=fileobj._id,
                mime_type=mime_type,
                file_extension=mid_file_extension,
                if_image_size_name='mid'
                )

            # print "==== ",  mid_filehive_id_url_dict

            node_collection.collection.update(
                                                {'_id': ObjectId(fileobj._id)},
                                                {'$set': {'if_file.mid': mid_filehive_id_url_dict}}
                                            )

            # print fileobj





# TODO: following task too need to manage/work/run from same file.
#       currently, its present in gnowsys_ndf.tasks

# from gnowsys_ndf.settings import SYNCDATA_DURATION
# from celery.decorators import periodic_task
# from gnowsys_ndf.celery import app
# from datetime import timedelta
# # @task
# @periodic_task(run_every=timedelta(seconds=SYNCDATA_DURATION))
# def run_syncdata_script():
#     #check if last scan file is update
#     #if not skip the execution the script might be running
#     #or stuck
#     #manage directory path

#     data_fetch_script_name = 'fetch_data'
#     command = "python manage.py " + data_fetch_script_name
#     subprocess.call([command],shell=True)
#     print data_fetch_script_name + ' executed.'

#     syncdata_sending_script_name = 'send_syncdata'
#     command1 = "python manage.py " + syncdata_sending_script_name
#     subprocess.call([command1],shell=True)
#     print syncdata_sending_script_name + ' executed.'

#     syncdata_fetching_script_name = 'fetch_syncdata'
#     command2 = "python manage.py " + syncdata_fetching_script_name
#     subprocess.call([command2],shell=True)
#     print syncdata_fetching_script_name + ' executed.'

#     return 'Both scripts executed'


@task
def record_in_benchmark(kwargs_len, total_param_size, post_bool, get_bool, sessionid, user_name, path, funct_name, time_taken, locale):
    benchmark_node = benchmark_collection.Benchmark()
    benchmark_node.time_taken   = time_taken
    benchmark_node.name         = unicode(funct_name)
    benchmark_node.has_data     = { "POST" : 0, "GET" : 0}
    benchmark_node.has_data["POST"] = bool(post_bool)
    benchmark_node.has_data["GET"]  = bool(get_bool)
    benchmark_node.session_key  = unicode(sessionid)
    benchmark_node.user = unicode(user_name)
    benchmark_node.parameters = unicode(kwargs_len)
    benchmark_node.locale = locale
    benchmark_node.size_of_parameters = unicode(total_param_size)
    benchmark_node.last_update = datetime.datetime.now()
    try:
        benchmark_node.calling_url = unicode(path)
        url = path.split("/")

        if url[1] != '' :
            group = url[1]
            group_name, group_id = get_group_name_id(group)
            benchmark_node.group = str(group_id)
        else :
            pass

        if url[2] == "" :
            benchmark_node.action = None
        else :
            benchmark_node.action = url[2]
            if url[3] != '' :
                benchmark_node.action +=  str('/'+url[3])
            else :
                pass
        if "node_id" in get_data and "collection_nav" in funct_name:
            benchmark_node.calling_url += "?selected="+req.GET['node_id']
            # modify calling_url if collection_nav is called i.e collection-player
    except :
        pass
    benchmark_node.save()

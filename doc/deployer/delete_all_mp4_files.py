import os
from gnowsys_ndf.ndf.models import *
#This Script will delete all mp4 files if it has webm and will replace mp4 objects with webm objects
video_files = node_collection.find({'if_file.mime_type': {'$regex': str('video'), '$options': "i"}})

if video_files:
    print "\n All Video files count: ",video_files.count()
for each in video_files:
    if 'mp4' in each.if_file.original.relurl:
        if each.if_file.mid.relurl:
            if os.path.isfile('/data/media/'+ each.if_file.original.relurl):
                if os.path.isfile('/data/media/'+ each.if_file.mid.relurl):
                    os.remove('/data/media/'+each.if_file.original.relurl)
                    each.if_file.original.relurl = each.if_file.mid.relurl
                    each.if_file.original.id = each.if_file.mid.id 
                    print each._id
                    each.save()


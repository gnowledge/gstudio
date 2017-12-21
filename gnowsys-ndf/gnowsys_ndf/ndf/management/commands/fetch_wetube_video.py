''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database
from django.contrib.auth.models import User

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.views.methods import create_gattribute
import ox

####################################################################################################################

collection = get_database()[Node.collection_name]

class Command(BaseCommand):
    """This script save wetube.gnowledge.org videos data in GSystem                                                            
     """

    help = "\tThis script save wetube.gnowledge.org videos data in GSystem "

    def handle(self, *args, **options):
        
        api = ox.api.API("http://wetube.gnowledge.org/api")

        countVideo = api.find({"query":{"operator":"&","conditions":[{"operator":"==","key":"project","value":"NROER"}]}})
        totalVideoNo = countVideo['data']['items']
        
        allVideo = api.find({"keys":["id","title","director","id","posterRatio","year","user"],"query":{"conditions":[{"oper\
    ator":"==","key":"project","value":"NROER"}],"operator":"&"},"range":[0,totalVideoNo],"sort":[{"operator":"+","key":"title"}]})

        allVideosData = allVideo['data']['items']
        
        pandora_video_st = collection.Node.one({'$and':[{'name':'Pandora_video'},{'_type':'GSystemType'}]})
        file_gst = collection.Node.one({'$and':[{'name':'File'},{'_type':'GSystemType'}]})
        source_id_AT = collection.Node.one({'$and':[{'name':'source_id'},{'_type':'AttributeType'}]})
        grp = collection.Node.one({'_type': 'Group', 'name':'home' })
        auth_id = User.objects.get(username='nroer_team').pk

        if auth_id:
            for each in allVideosData:
                
                pandora_video = collection.Node.one({'_type': 'File', 'member_of': {'$in': [pandora_video_st._id]}, 'name': unicode(each['title']).lower(), 'created_by': auth_id })
                
                if pandora_video is None:
                    
                    gs = collection.File()
                    gs.name = unicode(each['title']).lower()
                    gs.mime_type = "video"
                    gs.access_policy = u"PRIVATE"
                    gs.member_of = [file_gst._id, pandora_video_st._id]
                    gs.created_by = auth_id
                    gs.modified_by = auth_id
                    gs.group_set.append(grp._id)
                    gs.contributors.append(auth_id)
                    gs.save()

                    gs.reload()

                    create_gattribute(gs._id, source_id_AT, each['id'])
                    print "\n Document created for pandora video '",gs.name,"' sucessfully !! \n"

                else:
                    print "\n Document Pandora Video '",pandora_video.name,"' already created !! \n"

        else:
            print "\n Sorry .. Need to create user as 'nroer_team' for running this script \n"

        # get_member_set=collection.Node.find({'$and':[{'member_of': {'$all': [ObjectId(pandora_video_st._id)]}},{'_type':'File'}]})



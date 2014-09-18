''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node
import ox
db =get_database()
collection = db['Nodes']


####################################################################################################################

class Command(BaseCommand):
    """This script save wetube.gnowledge.org videos data in GSystem                                                            
     """


    help = "\tThis script save wetube.gnowledge.org videos data in GSystem "

    def handle(self, *args, **options):
        main()
        
        # --- End of handle() ---


def main():
    api=ox.api.API("http://wetube.gnowledge.org/api")
    countVideo = api.find({"query":{"operator":"&","conditions":[{"operator":"==","key":"project","value":"NROER"}]}})
    totalVideoNo=countVideo['data']['items']
    allVideo = api.find({"keys":["id","title","director","id","posterRatio","year","user"],"query":{"conditions":[{"oper\
ator":"==","key":"project","value":"NROER"}],"operator":"&"},"range":[0,totalVideoNo],"sort":[{"operator":"+","key":"title"}]})
    allVideosData=allVideo['data']['items']
    pandora_video_st=collection.Node.one({'$and':[{'name':'Pandora_video'},{'_type':'GSystemType'}]})
    source_id_at=collection.Node.one({'$and':[{'name':'source_id'},{'_type':'AttributeType'}]})
    grp = collection.Node.one({'_type': 'Group', 'name':'home' })

    pandora_video_id=[]
    
    source_id_set=[]
    for each in allVideosData[:10]:
        gattribute=collection.Node.one({'$and':[{'object_value':each['id']},{'_type':'GAttribute'},{'attribute_type.$id':source_id_at._id}]})
        if gattribute is None:
            #gs=collection.GSystem()                                                                                     
            gs=collection.File()
            gs.mime_type="video"
            gs.member_of=[pandora_video_st._id]
            gs.name=each['title'].lower()
            gs.created_by=1
            gs.modified_by = 1
            gs.group_set.append(grp._id)
            if 1 not in gs.contributors:
                gs.contributors.append(1)
                gs.save()

                at=collection.GAttribute()
                at.attribute_type=source_id_at
                at.object_value=each['id']
                at.subject=gs._id
                at.save()
                

    get_member_set=collection.Node.find({'$and':[{'member_of': {'$all': [ObjectId(pandora_video_st._id)]}},{'_type':'File'}]})



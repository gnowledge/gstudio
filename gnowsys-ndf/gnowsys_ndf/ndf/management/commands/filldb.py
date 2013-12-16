''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import GSystemType
from gnowsys_ndf.ndf.models import GSystem
from gnowsys_ndf.ndf.models import Group

from gnowsys_ndf.settings import GAPPS

####################################################################################################################

class Command(BaseCommand):
    help = "Based on GAPPS list, inserts few documents (consisting of dummy values) into the following collections:\n\n" \
           "\tGSystemType, GSystemType"

    def handle(self, *args, **options):
        db = get_database()

        db.drop_collection(GSystem.collection_name)
        db.drop_collection(GSystemType.collection_name)
        db.drop_collection(Group.collection_name)
        
        gst_collection = db[GSystemType.collection_name]
        gst_node = []
        user_id = 1 
        for i in range(0, len(GAPPS)):
            gst_node.append(gst_collection.GSystemType())
            
            gst_node[i].name = unicode(GAPPS[i])
            gst_node[i].created_by = user_id
            gst_node[i].modified_by.append(user_id)
            gst_node[i].save()
        gs_collection = db[Group.collection_name]
        gs_node = gs_collection.Group()
        gs_node.name = u'home'
        gs_node.created_by = user_id
        gs_node.member_of.append(u"Group")
        gs_node.save()
        # --- End of handle() ---

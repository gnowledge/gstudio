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

from gnowsys_ndf.settings import GAPPS

####################################################################################################################

class Command(BaseCommand):
    help = "Based on GAPPS list, inserts few documents (consisting of dummy values) into the following collections:\n\n" \
           "\tGSystemType, GSystemType"

    def handle(self, *args, **options):
        db = get_database()

        db.drop_collection(GSystem.collection_name)
        db.drop_collection(GSystemType.collection_name)
        
        gst_collection = db[GSystemType.collection_name]
        gst_node = []

        gs_collection = db[GSystem.collection_name]

        for i in range(0, len(GAPPS)):
            gst_node.append(gst_collection.GSystemType())
            
            gst_node[i].name = unicode(GAPPS[i])
            gst_node[i].save()

            gs_node = []
            for j in range(0, 2):
                gs_node.append(gs_collection.GSystem())
                
                gs_node[j].name = unicode(GAPPS[i]) + unicode(j + 1)
                gs_node[j].gsystem_type.append(gst_node[i]._id)
                gs_node[j].member_of.append(gst_node[i].name)
                gs_node[j].save()

        # --- End of handle() ---

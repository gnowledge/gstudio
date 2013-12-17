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
        collection = db[GSystemType.collection_name]
        #gst_collection=collection.find({'_type':'GSystemType'})
        #gst_node = []
        user_id = 1 
        a=""
        for each in GAPPS:
            a=collection.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':each}]})
            if (a == None or each!=a['name']):
                    gst_node=collection.GSystemType()
                    gst_node.name = unicode(each)
                    gst_node.created_by = user_id
                    gst_node.modified_by.append(user_id)
                    gst_node.save()

            # --- End of handle() ---

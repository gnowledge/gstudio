''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from mongokit import IS

from django_mongokit import get_database
from django.contrib.auth.models import User

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node,GSystem

####################################################################################################################

class Command(BaseCommand):

    help = " This script will replace the unicode of 'type_of' field of Node with ObjectId ."

    def handle(self, *args, **options):
        db=get_database()
        collection = db[Node.collection_name]
        
        cur=collection.Node.find({'type_of':{'$exists':True}})
        for n in cur:
            gst = n.type_of
            if gst == 'profile_pic':
            	type_obj=collection.Node.one({'name': gst})
            	if type_obj:
                	n.type_of = ObjectId(type_obj._id)
                
                	n.save()


            
            
       
          

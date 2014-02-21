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
from gnowsys_ndf.ndf.models import Node

####################################################################################################################

class Command(BaseCommand):

    help = " This script will add the access_policy field to all created documents in your database."

    def handle(self, *args, **options):

      collection = get_database()[Node.collection_name]
      cur = collection.Node.find({'_type': {'$in': ['GSystem', 'File', 'Group']}})
        
      for n in cur:
        usrname = User.objects.get(pk=n.created_by).username
          
        u = collection.Node.one({'_type': 'Group', 'name': usrname})
          
        if u:
          n.group_set.append(u.name)
          n.save()
            
       
          
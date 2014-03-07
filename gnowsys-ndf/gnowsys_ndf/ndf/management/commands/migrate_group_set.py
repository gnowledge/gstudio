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

    help = " This script will replace the [unicode] (i.e. group_name) of 'group_set' field of GSystem with [ObjectId] (i.e. group_id)."

    def handle(self, *args, **options):
        db=get_database()
        collection = db[Node.collection_name]
        """
        cur=collection.Node.find({'group_set':{'$exists':True}})
        for each in cur:
            gps = collection.Node.find({'_type':u'Group'})
            for eachgps in gps:
                grpname = unicode(eachgps.name)
                if grpname.strip() in each.group_set:
                    each.group_set.remove(grpname)
                    each.group_set.append(eachgps._id)
            for each_group_set_item in each.group_set:
                if type(each_group_set_item)==unicode:
                    each.group_set.remove(each_group_set_item)
            each.save()
        """

        cur=collection.Node.find({'group_set':{'$exists':True}})
        for n in cur:
            gs = n.group_set
            n.group_set = []
            for group in gs:
                if type(group) == unicode:
                    group_obj=collection.Node.one({'name': group})
                    if group_obj:
                        n.group_set.append(group_obj._id)
                else:
                    n.group_set.append(group)
            n.save()


            
            
       
          

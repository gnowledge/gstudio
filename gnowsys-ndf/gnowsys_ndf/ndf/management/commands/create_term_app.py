''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node
###################################################################################################################################################################################
collection = get_database()[Node.collection_name]
gapp_GST = collection.Node.one({'_type': 'MetaType', 'name': 'GAPP'})    

class Command(BaseCommand):

    help = "This script will create a Term app"

    def handle(self, *args, **options):
        
        term = collection.Node.one({'_type': 'GSystemType', 'name': 'Term', 'member_of': ObjectId(gapp_GST._id) })
        if not term:
            term = collection.GSystemType()
            term.name = u"Term"
            term.altnames = u"Topic"
            term.access_policy = u"PUBLIC"
            term.contributors.append(1)
            term.created_by = int(1)
            term.modified_by = int(1)
            term.status = u"PUBLISHED"
            term.member_of.append(gapp_GST._id)
            term.meta_type_set.append(gapp_GST)
            term.save()
            print "'Term' app successfully created ! !"
        else:
            print "'Term' app already available"
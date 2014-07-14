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
	rep=collection.Node.one({'name':"Reply",'_type':'GSystemType'})
	
	twi=collection.Node.one({'name':"Twist",'_type':'GSystemType'})
        obj= collection.Node.one({'name':"mm_id",'_type':'AttributeType'})
	if obj is None:
		a=collection.AttributeType()
		a.name=u"mm_id"
		a.created_by=1
		a.altnames=u"MM_ID"
		a.subject_type.append(rep._id)
		a.subject_type.append(twi._id)
		a.data_type="basestring"
		a.modified_by=1
		a.save()
		rep.attribute_type_set.append(obj)
		rep.save()
		twi.attribute_type_set.append(obj)
		twi.save()


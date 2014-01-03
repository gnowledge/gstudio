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
                    gst_node.member_of.append(u"GAPP")
                    gst_node.modified_by.append(user_id)
                    gst_node.save()
        #Create default group 'home'
        a=collection.GSystemType.find({'$and':[{'_type':'Group'},{'name':'home'}]})
        if a.count() < 1:
            gs_node = collection.Group()
            gs_node.name = u'home'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"Group")
            gs_node.save()
        a=collection.GSystemType.find({'$and':[{'_type':'AttributeType'},{'name':'start_time'}]})
        forumtype=collection.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':'Forum'}]})
        if a.count() < 1:
            gs_node = collection.AttributeType()
            gs_node.name = u'start_time'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"AT")
            gs_node.data_type="DateTime"
            gs_node.subject_type.append(forumtype._id)
            gs_node.save()
        a=collection.GSystemType.find({'$and':[{'_type':'AttributeType'},{'name':'end_time'}]})
        if a.count() < 1:
            gs_node = collection.AttributeType()
            gs_node.name = u'end_time'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"AT")
            gs_node.data_type="DateTime"
            gs_node.subject_type.append(forumtype._id)
            gs_node.save()
        replytype=collection.GSystemType.find({'$and':[{'_type':'GSystemType'},{'name':'Twist'}]})
        if replytype.count() < 1:
            gs_node = collection.GSystemType()
            gs_node.name = u'Twist'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"ST")
            gs_node.meta_type_set.append(forumtype._id)
            gs_node.save()
        replytype=collection.GSystemType.find({'$and':[{'_type':'GSystemType'},{'name':'Reply'}]})
        if replytype.count() < 1:
            gs_node = collection.GSystemType()
            gs_node.name = u'Reply'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"ST")
            gs_node.meta_type_set.append(forumtype._id)
            gs_node.save()


            # --- End of handle() ---


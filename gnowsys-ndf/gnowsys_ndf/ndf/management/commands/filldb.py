''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError
from django_mongokit import get_database
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node
from gnowsys_ndf.ndf.models import GSystemType
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.settings import GAPPS

####################################################################################################################

class Command(BaseCommand):
    help = "Based on GAPPS list, inserts few documents (consisting of dummy values) into the following collections:\n\n" \
           "\tGSystemType, AttributeType"

    def handle(self, *args, **options):
        db = get_database()
        #collection = db[GSystemType.collection_name]
        collection = db[Node.collection_name]

        user_id = 1 

        a= None
        for each in GAPPS:
            node_doc =collection.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':each}]})
            if (a == None or each != a['name']):
                gst_node=collection.GSystemType()
                gst_node.name = unicode(each)
                gst_node.created_by = user_id
                gst_node.member_of.append(u'GAPP')
                gst_node.modified_by.append(user_id)
                gst_node.save()
            elif('ST' not in a.member_of): # it will append 'ST' to already created GSystemType's member_of field
                a.member_of.append(u'GAPP')
                a.save()
                   
        #Create default group 'home'
        node_doc =collection.GSystemType.one({'$and':[{'_type': u'Group'},{'name': u'home'}]})
        if node_doc is None:
            gs_node = collection.Group()
            gs_node.name = u'home'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"Group")
            gs_node.save()

        forum_type = collection.GSystemType.one({'$and':[{'_type': u'GSystemType'},{'name': u'Forum'}]})


        reply_type = collection.GSystemType.one({'$and':[{'_type': u'GSystemType'},{'name': u'Twist'}]})
        if reply_type is None:
            gs_node = collection.GSystemType()
            gs_node.name = u'Twist'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"ST")
            gs_node.meta_type_set.append(forum_type._id)
            gs_node.save()

        reply_type = collection.GSystemType.one({'$and':[{'_type': u'GSystemType'},{'name': u'Reply'}]})
        if reply_type is None:
            gs_node = collection.GSystemType()
            gs_node.name = u'Reply'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"ST")
            gs_node.meta_type_set.append(forum_type._id)
            gs_node.save()

        # Retrieve 'Quiz' GSystemType's id -- in order to append it to 'meta_type_set' for 'QuizItem' GSystemType
        quiz_type_id = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Quiz'})._id

        # Create 'QuizItem' GSystemType, if didn't exists 
        quiz_item_type = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'QuizItem'})
        if quiz_item_type is None:
            gs_node = collection.GSystemType()
            gs_node.name = u'QuizItem'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"ST")
            gs_node.meta_type_set.append(quiz_type_id)
            gs_node.save()

        node_doc = collection.GSystemType.one({'$and':[{'_type': u'AttributeType'},{'name': u'start_time'}]})
        if node_doc is None:
            gs_node = collection.AttributeType()
            gs_node.name = u'start_time'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"AT")
            #gs_node.data_type="DateTime"
            gs_node.data_type = "datetime.datetime"
            gs_node.subject_type.append(forum_type._id)
            gs_node.subject_type.append(quiz_type_id)
            gs_node.save()

        node_doc = collection.GSystemType.one({'$and':[{'_type': u'AttributeType'},{'name': u'end_time'}]})
        if node_doc is None:
            gs_node = collection.AttributeType()
            gs_node.name = u'end_time'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"AT")
            #gs_node.data_type="DateTime"
            gs_node.data_type = "datetime.datetime"
            gs_node.subject_type.append(forum_type._id)
            gs_node.subject_type.append(quiz_type_id)
            gs_node.save()


        # --- End of handle() ---


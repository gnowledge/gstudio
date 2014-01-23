''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from mongokit import IS

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node, GSystemType
from gnowsys_ndf.ndf.models import Group
from gnowsys_ndf.ndf.models import DATA_TYPE_CHOICES, QUIZ_TYPE_CHOICES_TU
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

        node_doc = None
        for each in GAPPS:
            node_doc = collection.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':each}]})
            if (node_doc == None or each != node_doc['name']):
                gst_node=collection.GSystemType()
                gst_node.name = unicode(each)
                gst_node.created_by = user_id
                gst_node.member_of.append(u'GAPP')
                gst_node.modified_by.append(user_id)
                gst_node.save()
            elif('ST' not in node_doc.member_of): # it will append 'ST' to already created GSystemType's member_of field
                node_doc.member_of.append(u'GAPP')
                node_doc.save()
                   
        #Create default group 'home'
        node_doc =collection.GSystemType.one({'$and':[{'_type': u'Group'},{'name': u'home'}]})
        if node_doc is None:
            gs_node = collection.Group()
            gs_node.name = u'home'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"Group")
            gs_node.disclosure_policy=u'DISCLOSED_TO_MEM'
            gs_node.subscription_policy=u'OPEN'
            gs_node.visibility_policy=u'ANNOUNCED'
            gs_node.encryption_policy=u'NOT_ENCRYPTED'
            gs_node.group_type=u'PRIVATE'
            gs_node.edit_policy =u'NON_EDITABLE'
            gs_node.save()

        forum_type = collection.GSystemType.one({'$and':[{'_type': u'GSystemType'},{'name': u'Forum'}]})

        reply_type = collection.GSystemType.one({'$and':[{'_type': u'GSystemType'},{'name': u'Twist'}]})
        if reply_type is None:
            gs_node = collection.GSystemType()
            gs_node.name = u'Twist'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"ST")
            # gs_node.meta_type_set.append(forum_type._id)
            # gs_node.meta_type_set.append(forum_type)
            gs_node.save()

        reply_type = collection.GSystemType.one({'$and':[{'_type': u'GSystemType'},{'name': u'Reply'}]})
        if reply_type is None:
            gs_node = collection.GSystemType()
            gs_node.name = u'Reply'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"ST")
            # gs_node.meta_type_set.append(forum_type._id)
            gs_node.save()

        # Retrieve 'Quiz' GSystemType's id -- in order to append it to 'meta_type_set' for 'QuizItem' GSystemType
        quiz_type_id = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Quiz'})._id

        # Create 'QuizItem' GSystemType, if didn't exists 
        quiz_item_type = collection.Node.one({'_type': u'GSystemType', 'name': u'QuizItem'})
        if quiz_item_type is None:
            gs_node = collection.GSystemType()
            gs_node.name = u'QuizItem'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"ST")
            # gs_node.meta_type_set.append(quiz_type_id)
            gs_node.save()

        quiz_item_type = collection.Node.one({'_type': u'GSystemType', 'name': u'QuizItem'})

        # Create 'quiz_type' AttributeType, if didn't exists 
        node_doc = collection.Node.one({'_type': u'AttributeType', 'name': u'quiz_type'})
        if node_doc is None:
            gs_node = collection.AttributeType()
            gs_node.name = u'quiz_type'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"AT")
            gs_node.data_type = str(QUIZ_TYPE_CHOICES_TU)  # One of them from the given values
            gs_node.subject_type.append(quiz_item_type._id)
            gs_node.save()

        # Create 'options' AttributeType, if didn't exists 
        node_doc = collection.Node.one({'_type': u'AttributeType', 'name': u'options'})
        if node_doc is None:
            gs_node = collection.AttributeType()
            gs_node.name = u'options'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"AT")
            gs_node.data_type = "[" + DATA_TYPE_CHOICES[6] + "]"  # list of unicodes
            gs_node.subject_type.append(quiz_item_type._id)
            gs_node.save()

        # Create 'correct_answer' AttributeType, if didn't exists 
        node_doc = collection.Node.one({'_type': u'AttributeType', 'name': u'correct_answer'})
        if node_doc is None:
            gs_node = collection.AttributeType()
            gs_node.name = u'correct_answer'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"AT")
            gs_node.data_type = "[" + DATA_TYPE_CHOICES[6] + "]"  # list of unicodes
            gs_node.subject_type.append(quiz_item_type._id)
            gs_node.save()

        # Append quiz_type, options & correct_answer to attribute_type_set of 'QuizItem'
        quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'quiz_type'}))
        quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'options'}))
        quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'correct_answer'}))
        quiz_item_type.save()

        node_doc = collection.GSystemType.one({'$and':[{'_type': u'AttributeType'},{'name': u'start_time'}]})
        if node_doc is None:
            gs_node = collection.AttributeType()
            gs_node.name = u'start_time'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"AT")
            # gs_node.data_type="DateTime"
            # gs_node.data_type = "datetime.datetime"
            gs_node.data_type = DATA_TYPE_CHOICES[9]   # datetime.datetime
            gs_node.subject_type.append(forum_type._id)
            gs_node.subject_type.append(quiz_type_id)
            gs_node.save()

        node_doc = collection.GSystemType.one({'$and':[{'_type': u'AttributeType'},{'name': u'end_time'}]})
        if node_doc is None:
            gs_node = collection.AttributeType()
            gs_node.name = u'end_time'
            gs_node.created_by = user_id
            gs_node.member_of.append(u"AT")
            # gs_node.data_type="DateTime"
            # gs_node.data_type = "datetime.datetime"
            gs_node.data_type = DATA_TYPE_CHOICES[9]   # datetime.datetime
            gs_node.subject_type.append(forum_type._id)
            gs_node.subject_type.append(quiz_type_id)
            gs_node.save()


        # --- End of handle() ---


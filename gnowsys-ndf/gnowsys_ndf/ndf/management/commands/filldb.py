>>''' imports from installed packages '''
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
from gnowsys_ndf.settings import META_TYPE


####################################################################################################################
#global variables
db = get_database()
collection = db[Node.collection_name]

#append gsystem_type name to create factory GSystemType
factory_system_types = ['Twist', 'Reply', 'Author', 'Shelf', 'QuizItem']

#fill attribute name,data_type,gsystem_type name in bellow dict to create factory Attribute Type
factory_attribute_type = [{'quiz_type':{'gsystem_names_list':['QuizItem'], 'data_type':'str(QUIZ_TYPE_CHOICES_TU)'}},{'options':{'gsystem_names_list':['QuizItem'], 'data_type':'"[" + DATA_TYPE_CHOICES[6] + "]"'}}, {'correct_answer':{'gsystem_names_list':['QuizItem'], 'data_type':'"[" + DATA_TYPE_CHOICES[6] + "]"'}}, {'start_time':{'gsystem_names_list':['QuizItem','Forum'], 'data_type':'DATA_TYPE_CHOICES[9]'}}, {'end_time':{'gsystem_names_list':['QuizItem','Forum'], 'data_type':'DATA_TYPE_CHOICES[9]'}}, {'module_set_md5':{'gsystem_names_list':['Module'], 'data_type':'u""'}}]

#fill relation_type_name,inverse_name,subject,right_subject in bellow dict to create factory Relation Type
factory_relation_type = [{'has_shelf':{'subject':['Author'],'right_subject':['Shelf'], 'inverse_name':'shelf_of'}}, {'translation_of':{'subject':['Page'],'right_subject':['Page'], 'inverse_name':'translation_of'}}]

class Command(BaseCommand):
    help = "Based on GAPPS list, inserts few documents (consisting of dummy values) into the following collections:\n\n" \
           "\tGSystemType, AttributeType"

    def handle(self, *args, **options):
        user_id = 1 
        node_doc = None
        meta_type_name = META_TYPE[0]
        meta_type = collection.GSystemType.one({'$and':[{'_type':'MetaType'},{'name':meta_type_name}]}) # getting MetaType Object
        if meta_type == None:
            meta_type = create_meta_type(user_id) #creating MetaType
        
        for each in GAPPS:
            node_doc = collection.GSystemType.one({'$and':[{'_type':'GSystemType'},{'name':each}]})
            if (node_doc == None or each != node_doc['name']):
                gst_node=collection.GSystemType()
                gst_node.name = unicode(each)
                gst_node.created_by = user_id
                gst_node.member_of.append(meta_type._id) # appending metatype to the GSystemType
                gst_node.modified_by.append(user_id)
                gst_node.save()
            elif(meta_type._id not in node_doc.member_of):
                 node_doc.member_of.append(meta_type._id)
                 node_doc.save()
                   
        #Create default group 'home'
        node_doc =collection.GSystemType.one({'$and':[{'_type': u'Group'},{'name': u'home'}]})
        if node_doc is None:
            gs_node = collection.Group()
            gs_node.name = u'home'
            gs_node.created_by = user_id
            gs_node.member_of.append(collection.Node.one({'name': "Group"})._id)
            gs_node.disclosure_policy=u'DISCLOSED_TO_MEM'
            gs_node.subscription_policy=u'OPEN'
            gs_node.visibility_policy=u'ANNOUNCED'
            gs_node.encryption_policy=u'NOT_ENCRYPTED'
            gs_node.group_type= u'PUBLIC'
            gs_node.edit_policy =u'NON_EDITABLE'
            gs_node.save()
        
        #creating factory GSystemType's 
        for each in factory_gsystem_types:
            create_gsystem_type(each, user_id)

        #creating factory AttributeType's
        for each in factory_attribute_type:
            gsystem_id_list = []
            for key,value in each.items():
                at_name = key
                data_type = value['data_type']
                for e in value['gsystem_names_list']:
                    node = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name': e}]})
                    gsystem_id_list.append(node._id)
            create_attribute_type(at_name, user_id, data_type, gsystem_id_list)
        
        #creating factory RelationType's --under construction
        for each in factory_attribute_type:
            subject_id_list = []
            right_subject_id_list = []
            for key,value in each.items():
                at_name = key
                data_type = value['data_type']
                for s in value['subject']:
                    node = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name': s}]})
                    subject_id_list.append(node._id)
                for rs in value['right_subject']:
                    node = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name': rs}]})
                    right_subject_id_list.append(node._id)
            create_attribute_type(at_name, user_id, data_type, gsystem_id_list)
        


        # forum_type = collection.GSystemType.one({'$and':[{'_type': u'GSystemType'},{'name': u'Forum'}]})

        # reply_type = collection.GSystemType.one({'$and':[{'_type': u'GSystemType'},{'name': u'Twist'}]})
        # if reply_type is None:
        #     gs_node = collection.GSystemType()
        #     gs_node.name = u'Twist'
        #     gs_node.created_by = user_id
        #     # gs_node.member_of.append(u"ST")
        #     # gs_node.meta_type_set.append(forum_type._id)
        #     # gs_node.meta_type_set.append(forum_type)
        #     gs_node.save()

        # reply_type = collection.GSystemType.one({'$and':[{'_type': u'GSystemType'},{'name': u'Reply'}]})
        # if reply_type is None:
        #     gs_node = collection.GSystemType()
        #     gs_node.name = u'Reply'
        #     gs_node.created_by = user_id
        #     # gs_node.member_of.append(u"ST")
        #     # gs_node.meta_type_set.append(forum_type._id)
        #     gs_node.save()

        # # Create 'Author' GSystemType, if it didn't exists
        # auth = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Author'}) 
        # if auth is None:
        #     auth = collection.GSystemType()
        #     auth.name = u"Author"
        #     auth.created_by = user_id
        #     # auth.member_of.append(u"ST")
        #     auth.save()

        # auth = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Author'}) 

        # # Create 'shelf' GSystemType, if it didn't exists
        # shelf = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Shelf'}) 
        # if shelf is None:
        #     gst_node = collection.GSystemType()
        #     gst_node.name = u"Shelf"
        #     gst_node.created_by = user_id
        #     # gst_node.member_of.append(u"ST")
        #     gst_node.save()

        # shelf = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Shelf'})    

        # Create 'has_shelf' RelationType, if it didn't exists    
        has_shelf_RT = collection.RelationType.one({'_type': u'RelationType', 'name': u'has_shelf'}) 
        if has_shelf_RT is None:
            rt_node = collection.RelationType()
            rt_node.name = u"has_shelf"
            rt_node.inverse_name = u"shelf_of"
            rt_node.subject_type.append(auth._id)
            rt_node.object_type.append(shelf._id)
            rt_node.created_by = user_id
            # rt_node.member_of.append(u"RT")
            rt_node.save()            

        page = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Page'})    

        # Create 'translation_of' RelationType, if it didn't exists    
        translation_of_RT = collection.RelationType.one({'_type': u'RelationType', 'name': u'translation_of'}) 
        if translation_of_RT is None:
            rt = collection.RelationType()
            rt.name = u"translation_of"
            rt.inverse_name = u"translation_of"
            rt.subject_type.append(page._id)
            rt.object_type.append(page._id)
            rt.created_by = user_id
            rt.save()            

        # Create 'Pandora_video' GsystemType, if it didn't exists    
        pandora_video = collection.GSystemType.one({'$and':[{'_type': u'GSystemType'},{'name': u'Pandora_video'}]})
        if pandora_video is None:
            st = collection.GSystemType()
            st.name = u'Pandora_video'
            st.created_by = user_id
            st.save()

      	pandora_video = collection.GSystemType.one({'$and':[{'_type': u'GSystemType'},{'name': u'Pandora_video'}]})

        # Create 'source_id' AttributeType, if didn't exists 
        source_id = collection.Node.one({'$and':[{'_type': 'AttributeType'},{'name': u'source_id'}]})
        if source_id is None:
            at = collection.AttributeType()
            at.name = u'source_id'
            at.created_by = user_id
            at.data_type = u''                #unicode data type
            at.subject_type.append(pandora_video._id)
            at.save()


        # # Retrieve 'Quiz' GSystemType's id -- in order to append it to 'meta_type_set' for 'QuizItem' GSystemType
        # quiz_type = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Quiz'})

        # # Create 'QuizItem' GSystemType, if didn't exists 
        # quiz_item_type = collection.Node.one({'_type': u'GSystemType', 'name': u'QuizItem'})
        # if quiz_item_type is None:
        #     gst_node = collection.GSystemType()
        #     gst_node.name = u'QuizItem'
        #     gst_node.created_by = user_id
        #     # gst_node.member_of.append(u"ST")
        #     # gst_node.meta_type_set.append(quiz_type._id)
        #     gst_node.save()

        # quiz_item_type = collection.Node.one({'_type': u'GSystemType', 'name': u'QuizItem'})

        # # Create 'quiz_type' AttributeType, if didn't exists 
        # node_doc = collection.Node.one({'_type': u'AttributeType', 'name': u'quiz_type'})
        # if node_doc is None:
        #     at_node = collection.AttributeType()
        #     at_node.name = u'quiz_type'
        #     at_node.created_by = user_id
        #     # at_node.member_of.append(u"AT")
        #     at_node.data_type = str(QUIZ_TYPE_CHOICES_TU)  # One of them from the given values
        #     at_node.subject_type.append(quiz_item_type._id)
        #     at_node.save()

        # # Create 'options' AttributeType, if didn't exists 
        # node_doc = collection.Node.one({'_type': u'AttributeType', 'name': u'options'})
        # if node_doc is None:
        #     at_node = collection.AttributeType()
        #     at_node.name = u'options'
        #     at_node.created_by = user_id
        #     # at_node.member_of.append(u"AT")
        #     at_node.data_type = "[" + DATA_TYPE_CHOICES[6] + "]"  # list of unicodes
        #     at_node.subject_type.append(quiz_item_type._id)
        #     at_node.save()

        # # Create 'correct_answer' AttributeType, if didn't exists 
        # node_doc = collection.Node.one({'_type': u'AttributeType', 'name': u'correct_answer'})
        # if node_doc is None:
        #     at_node = collection.AttributeType()
        #     at_node.name = u'correct_answer'
        #     at_node.created_by = user_id
        #     # at_node.member_of.append(u"AT")
        #     at_node.data_type = "[" + DATA_TYPE_CHOICES[6] + "]"  # list of unicodes
        #     at_node.subject_type.append(quiz_item_type._id)
        #     at_node.save()

        # # Create 'module_set_md5' AttributeType, if didn't exists 
        # node = collection.Node.one({'$and':[{'_type': 'AttributeType'},{'name': 'module_set_md5'}]})
        # GST_MODULE = collection.Node.one({'$and':[{'_type':'GSystemType'},{'name':'Module'}]})
        # if node is None:
        #     at = collection.AttributeType()
        #     at.name = u'module_set_md5'
        #     at.created_by = user_id
        #     at.data_type = u''                #unicode data type
        #     at.subject_type.append(GST_MODULE._id)
        #     at.save()

        # Append quiz_type, options & correct_answer to attribute_type_set of 'QuizItem'
        if not quiz_item_type.attribute_type_set:
            quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'quiz_type'}))
            quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'options'}))
            quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'correct_answer'}))
            quiz_item_type.save()

        # node_doc = collection.GSystemType.one({'$and':[{'_type': u'AttributeType'},{'name': u'start_time'}]})
        # if node_doc is None:
        #     at_node = collection.AttributeType()
        #     at_node.name = u'start_time'
        #     at_node.created_by = user_id
        #     # at_node.member_of.append(u"AT")
        #     # at_node.data_type="DateTime"
        #     # at_node.data_type = "datetime.datetime"
        #     at_node.data_type = DATA_TYPE_CHOICES[9]   # datetime.datetime
        #     at_node.subject_type.append(forum_type._id)
        #     at_node.subject_type.append(quiz_type._id)
        #     at_node.save()

        # node_doc = collection.GSystemType.one({'$and':[{'_type': u'AttributeType'},{'name': u'end_time'}]})
        # if node_doc is None:
        #     at_node = collection.AttributeType()
        #     at_node.name = u'end_time'
        #     at_node.created_by = user_id
        #     # at_node.member_of.append(u"AT")
        #     # at_node.data_type="DateTime"
        #     # at_node.data_type = "datetime.datetime"
        #     at_node.data_type = DATA_TYPE_CHOICES[9]   # datetime.datetime
        #     at_node.subject_type.append(forum_type._id)
        #     at_node.subject_type.append(quiz_type._id)
        #     at_node.save()

        # Append start_time & end_time to attribute_type_set of 'Quiz'
        if not quiz_type.attribute_type_set:
            quiz_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'start_time'}))
            quiz_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'end_time'}))
            quiz_type.save()


        # --- End of handle() ---

def create_meta_type(user_id):
    '''
    creating meta_type in database
    '''
    meta = collection.MetaType()
    meta.name = META_TYPE[0]
    meta.created_by = user_id # default hardcode
    meta.save()
    return meta

def create_gsystem_type(st_name,user_id):
    '''
    creating factory GSystemType's 
    '''
    node = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name':st_name}]})
    if node is None:
        try:
            gs_node = collection.GSystemType()
            gs_node.name = unicode(st_name)
            gs_node.created_by = user_id
            gs_node.save()
        except Exception as e:
            print 'GsystemType',st_name,'fails to create because:',e

def create_attribute_type(at_name, user_id, data_type, system_type_id_list):
    '''
    creating factory AttributeType's
    '''
    node = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name':st_name}]})
    if node is None:
        try:
            at = collection.AttributeType()
            at.name = unicode(at_name)
            at.created_by = user_id
            at.data_type = data_type              
            for each in system_type_id_list:
                at.subject.append(system_type_id)
            at.save()
        except Exception as e:
            print 'AttributeType',at_name,'fails to create because:',e

#-- under construction
def create_attribute_type(rt_name, inverse_name, subject, right_subject, user_id):
     '''
    creating factory RelationType's
    '''
     has_shelf_RT = collection.RelationType.one({'_type': u'RelationType', 'name': u'has_shelf'}) 
     if has_shelf_RT is None:
         rt_node = collection.RelationType()
         rt_node.name = u"has_shelf"
         rt_node.inverse_name = u"shelf_of"
         rt_node.subject_type.append(auth._id)
         rt_node.object_type.append(shelf._id)
         rt_node.created_by = user_id
         # rt_node.member_of.append(u"RT")
         rt_node.save()            

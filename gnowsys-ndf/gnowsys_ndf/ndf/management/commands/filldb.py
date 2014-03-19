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
from gnowsys_ndf.settings import META_TYPE


####################################################################################################################
#global variables
db = get_database()
collection = db[Node.collection_name]

#append gsystem_type name to create factory GSystemType
factory_gsystem_types = ['Twist', 'Reply', 'Author', 'Shelf', 'QuizItem', 'Pandora_video', 'profile_pic']

#fill attribute name,data_type,gsystem_type name in bellow dict to create factory Attribute Type
factory_attribute_types = [{'quiz_type':{'gsystem_names_list':['QuizItem'], 'data_type':'str(QUIZ_TYPE_CHOICES_TU)'}},{'options':{'gsystem_names_list':['QuizItem'], 'data_type':'"[" + DATA_TYPE_CHOICES[6] + "]"'}}, {'correct_answer':{'gsystem_names_list':['QuizItem'], 'data_type':'"[" + DATA_TYPE_CHOICES[6] + "]"'}}, {'start_time':{'gsystem_names_list':['QuizItem','Forum'], 'data_type':'DATA_TYPE_CHOICES[9]'}}, {'end_time':{'gsystem_names_list':['QuizItem','Forum'], 'data_type':'DATA_TYPE_CHOICES[9]'}}, {'module_set_md5':{'gsystem_names_list':['Module'], 'data_type':'u""'}},{'source_id':{'gsystem_names_list':['Pandora_video'], 'data_type':'u""'}} ]

#fill relation_type_name,inverse_name,subject_type,object_type in bellow dict to create factory Relation Type
factory_relation_types = [{'has_shelf':{'subject_type':['Author'],'object_type':['Shelf'], 'inverse_name':'shelf_of'}}, {'translation_of':{'subject_type':['Page'],'object_type':['Page'], 'inverse_name':'translation_of'}}, {'has_module':{'subject_type':['Page'],'object_type':['Module'], 'inverse_name':'generated_from'}}]

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
        for each in factory_attribute_types:
            gsystem_id_list = []
            for key,value in each.items():
                at_name = key
                data_type = value['data_type']
                for e in value['gsystem_names_list']:
                    node = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name': e}]})
                    if node is not None:
                        gsystem_id_list.append(node._id)
                    else:
                        print e,"as GSystemType not present in database"
            create_attribute_type(at_name, user_id, data_type, gsystem_id_list)
        
        #creating factory RelationType's 
        for each in factory_relation_types:
            subject_type_id_list = []
            object_type_id_list = []
            for key,value in each.items():
                at_name = key
                inverse_name = value['inverse_name']
                for s in value['subject_type']:
                    node_s = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name': s}]})
                    subject_type_id_list.append(node_s._id)
                for rs in value['object_type']:
                    node_rs = collection.Node.one({'$and':[{'_type': u'GSystemType'},{'name': rs}]})
                    object_type_id_list.append(node_rs._id)
            create_relation_type(at_name, inverse_name, user_id, subject_type_id_list, object_type_id_list)
        
        # # Retrieve 'Quiz' GSystemType's id -- in order to append it to 'meta_type_set' for 'QuizItem' GSystemType
        quiz_type = collection.GSystemType.one({'_type': u'GSystemType', 'name': u'Quiz'})

        quiz_item_type = collection.Node.one({'_type': u'GSystemType', 'name': u'QuizItem'})

        
        # Append quiz_type, options & correct_answer to attribute_type_set of 'QuizItem'
        if not quiz_item_type.attribute_type_set:
            quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'quiz_type'}))
            quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'options'}))
            quiz_item_type.attribute_type_set.append(collection.Node.one({'_type': u'AttributeType', 'name': u'correct_answer'}))
            quiz_item_type.save()

        
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

def create_gsystem_type(st_name, user_id):
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
    else:
        print 'GSystemType',st_name,'already created'

def create_attribute_type(at_name, user_id, data_type, system_type_id_list):
    '''
    creating factory AttributeType's
    '''
    node = collection.Node.one({'$and':[{'_type': u'AttributeType'},{'name':at_name}]})
    if node is None:
        try:
            at = collection.AttributeType()
            at.name = unicode(at_name)
            at.created_by = user_id
            at.data_type = data_type              
            for each in system_type_id_list:
                at.subject_type.append(each)
            at.save()
        except Exception as e:
            print 'AttributeType',at_name,'fails to create because:',e
    else:
        print 'AttributeType',at_name,'already created'


def create_relation_type(rt_name, inverse_name, user_id, subject_type_id_list, object_type_id_list):
    '''
    creating factory RelationType's
    '''
    rt_node = collection.RelationType.one({'_type': u'RelationType', 'name': rt_name}) 
    if rt_node is None:
        try:
            rt_node = collection.RelationType()
            rt_node.name = unicode(rt_name)
            rt_node.inverse_name = unicode(inverse_name)
            for st_id in subject_type_id_list:
                rt_node.subject_type.append(st_id)
            for ot_id in object_type_id_list:
                rt_node.object_type.append(ot_id)
            rt_node.created_by = user_id
            rt_node.save()
        except Exception as e:
            print 'RelationType',rt_name,'fails to create because:',e
    else:
        print 'RelationType',rt_node.name,'already created'

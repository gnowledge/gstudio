# imports from python libraries 
import os
import hashlib
import datetime
import json
#from random import random
#from random import choice


# imports from installed packages 
#from django.conf import settings
from django.contrib.auth.models import User
#from django.contrib.auth.models import check_password
#from django.core.validators import RegexValidator
from django.db import models

from django_mongokit import connection
from django_mongokit import get_database
from django_mongokit.document import DjangoDocument

#from mongokit import CustomType
from mongokit import IS
#from mongokit import OR

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


# imports from application folders/files 
from gnowsys_ndf.settings import RCS_REPO_DIR
from gnowsys_ndf.settings import RCS_REPO_DIR_HASH_LEVEL
from gnowsys_ndf.settings import MARKUP_LANGUAGE
from gnowsys_ndf.settings import MARKDOWN_EXTENSIONS
from gnowsys_ndf.settings import GROUP_AGENCY_TYPES,AUTHOR_AGENCY_TYPES
from gnowsys_ndf.ndf.rcslib import RCS
from django.dispatch import receiver
from registration.signals import user_registered


NODE_TYPE_CHOICES = (
    ('Nodes'),
    ('Attribute Types'),
    ('Attributes'),
    ('Relation Types'),
    ('Relations'),
    ('GSystem Types'),
    ('GSystems'),
    ('Node Specification'),
    ('Attribute Specification'),
    ('Relation Specification'),
    ('Intersection'),
    ('Complement'),
    ('Union'),
    ('Process Types'),
    ('Process')
)

TYPES_OF_GROUP = (
    ('ANONYMOUS'),
    ('PUBLIC'),
    ('PRIVATE')
)

EDIT_POLICY = (
    ('NON_EDITABLE'),
    ('EDITABLE_MODERATED'),
    ('EDITABLE_NON_MODERATED')
)

SUBSCRIPTION_POLICY = (
    ('OPEN'),
    ('BY_REQUEST'),
    ('BY_INVITATION'),
)

EXISTANCE_POLICY = (
    ('ANNOUNCED'),
    ('NOT_ANNOUNCED')
)

LIST_MEMBER_POLICY = (
    ('DISCLOSED_TO_MEM'),
    ('NOT_DISCLOSED_TO_MEM')
)

ENCRYPTION_POLICY=(
    ('ENCRYPTED'),
    ('NOT_ENCRYPTED')
)

DATA_TYPE_CHOICES = (
    "None",
    "bool",
    "basestring",
    "unicode",
    "int",
    "float",
    "long",
    "datetime.datetime",
    "list",
    "dict",
    "ObjectId",
    "IS()"
)

    

my_doc_requirement = u'storing_orignal_doc'
reduced_doc_requirement = u'storing_reduced_doc'
to_reduce_doc_requirement = u'storing_to_be_reduced_doc'
indexed_word_list_requirement = u'storing_indexed_words'



# CUSTOM DATA-TYPE DEFINITIONS


STATUS_CHOICES_TU = IS(u'DRAFT', u'HIDDEN', u'PUBLISHED', u'DELETED')
STATUS_CHOICES = tuple(str(qtc) for qtc in STATUS_CHOICES_TU)

QUIZ_TYPE_CHOICES_TU = IS(u'Short-Response', u'Single-Choice', u'Multiple-Choice')
QUIZ_TYPE_CHOICES = tuple(str(qtc) for qtc in QUIZ_TYPE_CHOICES_TU)


# FRAME CLASS DEFINITIONS


@receiver(user_registered)
def user_registered_handler(sender, user, request, **kwargs):
    collection = get_database()[Node.collection_name]
    tmp_hold=collection.node_holder()
    dict_to_hold={}
    dict_to_hold['node_type']='Author'
    dict_to_hold['userid']=user.id
    agency_type = request.POST.get("agency_type", "")
    if agency_type:
        dict_to_hold['agency_type']=agency_type
    else:
        # Set default value for agency_type as "Other"
        dict_to_hold['agency_type']="Other"
    dict_to_hold['group_affiliation']=request.POST.get("group_affiliation", "")
    tmp_hold.details_to_hold=dict_to_hold 
    tmp_hold.save()
    return
    


@connection.register
class Node(DjangoDocument):
    '''Everything is a Node.  Other classes should inherit this Node class.  

    According to the specification of GNOWSYS, all nodes, including
    types, metatypes and members of types, edges of nodes, should all
    be Nodes.
    
    Member of this class must belong to one of the NODE_TYPE_CHOICES. 

    Some in-built Edge names (Relation types) are defined in this
    class: type_of, member_of, prior_node, post_node, collection_set,
    group_set.  

    type_of is used to express generalization of Node. And member_of
    to express its type. This type_of should not be confused with
    _type.  The latter expresses the Python classes defined in this
    program that the object inherits.  The former (type_of) is about
    the data the application represents.

    _type is useful in seggregating the nodes from the mongodb
    collection, where all nodes are stored.

    prior_node is to express that the current node depends in some way
    to another node/s.  post_node is seldom used.  Currently we use it
    to define sub-Group, and to set replies to a post in the Forum App.

    Nodes are publisehed in one group or another, or in more than one
    group. The groups in which a node is publisehed is expressed in
    group_set.

    '''
    objects = models.Manager()

    collection_name = 'Nodes'
    structure = {
        '_type': unicode, # check required: required field, Possible
                          # values are to be taken only from the list
                          # NODE_TYPE_CHOICES
        'name': unicode,
        'altnames': unicode,
        'plural': unicode,
        'prior_node': [ObjectId], 
        'post_node': [ObjectId],
        
        'language': unicode,

        'type_of': [ObjectId], # check required: only ObjectIDs of GSystemType 
        'member_of': [ObjectId], # check required: only ObjectIDs of
                                 # GSystemType for GSystems, or only
                                 # ObjectIDs of MetaTypes for
                                 # GSystemTypes
        'access_policy': unicode, # check required: only possible
                                  # values are Public or Private.  Why
                                  # is this unicode?
        
      	'created_at': datetime.datetime,
        'created_by': int, # test required: only ids of Users

        'last_update': datetime.datetime,
        'modified_by': int, # test required: only ids of Users

        'contributors': [int], # test required: set of all ids of
                               # Users of created_by and modified_by
                               # fields
        'location': [dict], # check required: this dict should be a
                            # valid GeoJason format
        'content': unicode, 
        'content_org': unicode, 

        'group_set': [ObjectId], # check required: should not be
                                 # empty. For type nodes it should be
                                 # set to a Factory Group called
                                 # Administration
        'collection_set': [ObjectId],  # check required: to exclude
                                       # parent nodes as children, use
                                       # MPTT logic
        'property_order': [],  # Determines the order & grouping in
                               # which attribute(s)/relation(s) are
                               # displayed in the form

        'start_publication': datetime.datetime,
        'tags': [unicode],
        'featured': bool,
        'url': unicode,
        'comment_enabled': bool,
      	'login_required': bool,
      	# 'password': basestring,

        'status': STATUS_CHOICES_TU,
        'rating':[{'score':int,
                  'user_id':int,
                  'ip_address':basestring}]
    }
    
    required_fields = ['name', '_type'] # 'group_set' to be included
                                        # here after the default
                                        # 'Administration' group is
                                        # ready.
    default_values = {'created_at': datetime.datetime.utcnow, 'status': u'DRAFT'}
    use_dot_notation = True

    ########## Setter(@x.setter) & Getter(@property) ##########

    @property
    def user_details_dict(self):
        """Retrieves names of created-by & modified-by users from the given
        node, and appends those to 'user_details' dict-variable

        """
        user_details = {}
        if self.created_by:
            user_details['created_by'] = User.objects.get(pk=self.created_by).username

        contributor_names = []
        for each_pk in self.contributors:
            contributor_names.append(User.objects.get(pk=each_pk).username)
        # user_details['modified_by'] = contributor_names
        user_details['contributors'] = contributor_names

        if self.modified_by:
            user_details['modified_by'] = User.objects.get(pk=self.modified_by).username

        return user_details

    @property
    def member_of_names_list(self):
        """Returns a list having names of each member (GSystemType, i.e Page,
        File, etc.), built from 'member_of' field (list of ObjectIds)

        """
        member_of_names = []

        collection = get_database()[Node.collection_name]
        if self.member_of:
            for each_member_id in self.member_of:
                if type(each_member_id) == ObjectId:
                    _id = each_member_id
                else:
                    _id = each_member_id['$oid']
                if _id:
                    mem=collection.Node.one({'_id': ObjectId(_id)})
                    if mem:
                        member_of_names.append(mem.name)
        else:
            if self.has_key("gsystem_type"):
                for each_member_id in self.gsystem_type:
                    if type(each_member_id) == ObjectId:
                        _id = each_member_id
                    else:
                        _id = each_member_id['$oid']
                    if _id:
                        mem=collection.Node.one({'_id': ObjectId(_id)})
                        if mem:
                            member_of_names.append(mem.name)
        return member_of_names

    @property        
    def prior_node_dict(self):
        """Returns a dictionary consisting of key-value pair as
        ObjectId-Document pair respectively for prior_node objects of
        the given node.

        """
        
        collection = get_database()[Node.collection_name]
        
        obj_dict = {}

        i = 0
        for each_id in self.prior_node:
            i = i + 1

            if each_id != self._id:
                node_collection_object = collection.Node.one({"_id": ObjectId(each_id)})
                dict_key = i
                dict_value = node_collection_object
                
                obj_dict[dict_key] = dict_value

        return obj_dict

    @property
    def collection_dict(self):
        """Returns a dictionary consisting of key-value pair as
        ObjectId-Document pair respectively for collection_set objects
        of the given node.

        """

        collection = get_database()[Node.collection_name]
        
        obj_dict = {}

        i = 0;
        for each_id in self.collection_set:
            i = i + 1

            if each_id != self._id:
                node_collection_object = collection.Node.one({"_id": ObjectId(each_id)})
                dict_key = i
                dict_value = node_collection_object
                
                obj_dict[dict_key] = dict_value

        return obj_dict

    @property
    def html_content(self):
        """Returns the content in proper html-format.

        """
        if MARKUP_LANGUAGE == 'markdown':
            return markdown(self.content, MARKDOWN_EXTENSIONS)
        elif MARKUP_LANGUAGE == 'textile':
            return textile(self.content)
        elif MARKUP_LANGUAGE == 'restructuredtext':
            return restructuredtext(self.content)
        return self.content
        
    @property
    def current_version(self):
        history_manager= HistoryManager()
        return history_manager.get_current_version(self)    

    @property
    def version_dict(self):
        """Returns a dictionary containing list of revision numbers of the
        given node.
        
        Example:
        {
         "1": "1.1",
         "2": "1.2",
         "3": "1.3",
        }

        """
        history_manager = HistoryManager()
        return history_manager.get_version_dict(self)


    ########## Built-in Functions (Overridden) ##########
    
    def __unicode__(self):
        return self._id
    
    def identity(self):
        return self.__unicode__()
    
    def save(self, *args, **kwargs):
        if kwargs.has_key("is_changed"):
          if not kwargs["is_changed"]:
            #print "\n ", self.name, "(", self._id, ") -- Nothing has changed !\n\n"
            return
    
        is_new = False

        if not self.has_key('_id'):
            is_new = True               # It's a new document, hence yet no ID!"

            # On save, set "created_at" to current date
            self.created_at = datetime.datetime.today()

        self.last_update = datetime.datetime.today()

        # Check the fields which are not present in the class
        # structure, whether do they exists in their GSystemType's
        # "attribute_type_set"; If exists, add them to the document
        # Otherwise, throw an error -- " Illegal access: Invalid field
        # found!!! "
        collection = get_database()[Node.collection_name]
        for key, value in self.iteritems():
            if key == '_id':
                continue

            if not self.structure.has_key(key):
                field_found = False
                for gst_id in self.member_of:
                    attribute_set_list = collection.Node.one({'_id': gst_id}).attribute_type_set
                    
                    for attribute in attribute_set_list:
                        if key == attribute['name']:
                            field_found = True

                            # TODO: Check whether type of "value"
                            # matches with that of
                            # "attribute['data_type']" Don't continue
                            # searching from list of remaining
                            # attributes
                            break

                    if field_found:
                        # Don't continue searching from list of
                        # remaining gsystem-types
                        break

                if not field_found:
                    print "\n Invalid field(", key, ") found!!!\n"
                    # Throw an error: " Illegal access: Invalid field
                    # found!!! "
        
        super(Node, self).save(*args, **kwargs)
        
    	#This is the save method of the node class.It is still not
    	#known on which objects is this save method applicable We
    	#still do not know if this save method is called for the
    	#classes which extend the Node Class or for every class There
    	#is a very high probability that it is called for classes
    	#which extend the Node Class only The classes which we have
    	#i.e. the MyReduce() and ToReduce() class do not extend from
    	#the node class Hence calling the save method on those objects
    	#should not create a recursive function
    	
    	#If it is a new document then Make a new object of ToReduce
    	#class and the id of this document to that object else Check
    	#whether there is already an object of ToReduce() with the id
    	#of this object.  If there is an object present pass else add
    	#that object I have not applied the above algorithm
   	
   	#Instead what I have done is that I have searched the
   	#ToReduce() collection class and searched whether the ID of
   	#this document is present or not.  If the id is not present
   	#then add that id.If it is present then do not add that id
   		
   	old_doc = collection.ToReduceDocs.find_one({'required_for':to_reduce_doc_requirement,'doc_id':self._id})
        
    		#print "~~~~~~~~~~~~~~~~~~~~It is not present in the ToReduce() class collection.Message Coming from save() method ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",self._id
    	if  not old_doc:


    		z = collection.ToReduceDocs()
    		z.doc_id = self._id
    		z.required_for = to_reduce_doc_requirement
    		z.save()

    	#If you create/edit anything then this code shall add it in the URL

        history_manager = HistoryManager()
        rcs_obj = RCS()
	if is_new:
            # Create history-version-file
            try:
                if history_manager.create_or_replace_json_file(self):
                    fp = history_manager.get_file_path(self)
                    user = User.objects.get(pk=self.created_by).username
                    message = "This document (" + self.name + ") is created by " + user + " on " + self.created_at.strftime("%d %B %Y")
                    rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")
            except Exception as err:
                print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be created!!!\n"
                collection.remove({'_id': self._id})
                raise RuntimeError(err)

        else:
            # Update history-version-file
            fp = history_manager.get_file_path(self)

            try:
                rcs_obj.checkout(fp)
            except Exception as err:
                try:
                    if history_manager.create_or_replace_json_file(self):
                        fp = history_manager.get_file_path(self)
                        user = User.objects.get(pk=self.created_by).username
                        message = "This document (" + self.name + ") is re-created by " + user + " on " + self.created_at.strftime("%d %B %Y")
                        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

                except Exception as err:
                    print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be re-created!!!\n"
                    collection.remove({'_id': self._id})
                    raise RuntimeError(err)

            try:
                if history_manager.create_or_replace_json_file(self):
                    user = User.objects.get(pk=self.modified_by).username
                    message = "This document (" + self.name + ") is lastly updated by " + user + " status:" + self.status + " on " + self.last_update.strftime("%d %B %Y")
                    rcs_obj.checkin(fp, 1, message.encode('utf-8'))

            except Exception as err:
                print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be updated!!!\n"
                raise RuntimeError(err)
    

                

    ##########  User-Defined Functions ##########

    def get_possible_attributes(self, gsystem_type_id_or_list):
        """Returns user-defined attribute(s) of given node which belongs to
        either given single/list of GType(s).

        Keyword arguments: gsystem_type_id_or_list -- Single/List of
        ObjectId(s) of GSystemTypes' to which the given node (self)
        belongs
  
        If node (self) has '_id' -- Node is created; indicating
        possible attributes needs to be searched under GAttribute
        collection & return value of those attributes (previously
        existing) as part of the list along with attribute-data_type

        Else -- Node needs to be created; indicating possible
        attributes needs to be searched under AttributeType collection
        & return default value 'None' of those attributes as part of
        the list along with attribute-data_type
  
        Returns: Dictionary that holds follwoing details:- Key -- Name
        of the attribute Value, which inturn is a dictionary that
        holds key and values as shown below: 

        { 'attribute-type-name': { 'altnames': Value of AttributeType
        node's altnames field, 'data_type': Value of AttributeType
        node's data_type field, 'object_value': Value of GAttribute
        node's object_value field } }

        """

        gsystem_type_list = []
        possible_attributes = {}

        # Converts to list, if passed parameter is only single ObjectId
        if not isinstance(gsystem_type_id_or_list, list):
            gsystem_type_list = [gsystem_type_id_or_list]
        else:
            gsystem_type_list = gsystem_type_id_or_list

        # Code for finding out attributes associated with each gsystem_type_id in the list
        collection = get_database()[Node.collection_name]
        for gsystem_type_id in gsystem_type_list:

            # Converts string representaion of ObjectId to it's corresponding ObjectId type, if found
            if not isinstance(gsystem_type_id, ObjectId):
                if ObjectId.is_valid(gsystem_type_id):
                    gsystem_type_id = ObjectId(gsystem_type_id)
                else:
                    error_message = "\n ObjectIdError: Invalid ObjectId (" + gsystem_type_id + ") found while finding attributes !!!\n"
                    raise Exception(error_message)
            
            # Case [A]: While editing GSystem
            # Checking in Gattribute collection - to collect user-defined attributes' values, if already set!
            if self.has_key("_id"):
                # If - node has key '_id'
                attributes = collection.Triple.find({'_type': "GAttribute", 'subject': self._id})
                for attr_obj in attributes:
                    # attr_obj is of type - GAttribute [subject (node._id), attribute_type (AttributeType), object_value (value of attribute)]
                    # Must convert attr_obj.attribute_type [dictionary] to collection.Node(attr_obj.attribute_type) [document-object]
                    AttributeType.append_attribute(collection.AttributeType(attr_obj.attribute_type), possible_attributes, attr_obj.object_value)

            # Case [B]: While creating GSystem / if new attributes get added
            # Again checking in AttributeType collection - because to collect newly added user-defined attributes, if any!
            attributes = collection.Node.find({'_type': 'AttributeType', 'subject_type': gsystem_type_id})
            for attr_type in attributes:
                # Here attr_type is of type -- AttributeType
                AttributeType.append_attribute(attr_type, possible_attributes)

            # type_of check for current GSystemType to which the node belongs to
            gsystem_type_node = collection.Node.one({'_id': gsystem_type_id}, {'name': 1, 'type_of': 1})
            if gsystem_type_node.type_of:
                attributes = collection.Node.find({'_type': 'AttributeType', 'subject_type': {'$in': gsystem_type_node.type_of}})
                for attr_type in attributes:
                    # Here attr_type is of type -- AttributeType
                    AttributeType.append_attribute(attr_type, possible_attributes)

        return possible_attributes


    def get_possible_relations(self, gsystem_type_id_or_list):
        """Returns relation(s) of given node which belongs to either given
        single/list of GType(s).

        Keyword arguments: gsystem_type_id_or_list -- Single/List of
        ObjectId(s) of GTypes' to which the given node (self) belongs
  
        If node (self) has '_id' -- Node is created; indicating
        possible relations need to be searched under GRelation
        collection & return value of those relations (previously
        existing) as part of the dict along with relation-type details
        ('object_type' and 'inverse_name')

        Else -- Node needs to be created; indicating possible
        relations need to be searched under RelationType collection &
        return default value 'None' for those relations as part of the
        dict along with relation-type details ('object_type' and
        'inverse_name')
  
        Returns: Dictionary that holds details as follows:- Key --
        Name of the relation Value -- It's again a dictionary that
        holds key and values as shown below: 

        { // If inverse_relation - False 'relation-type-name': {
        'altnames': Value of RelationType node's altnames field [0th
        index-element], 'subject_or_object_type': Value of
        RelationType node's object_type field, 'inverse_name': Value
        of RelationType node's inverse_name field,
        'subject_or_right_subject_list': List of Value(s) of GRelation
        node's right_subject field }
          
          // If inverse_relation - True 'relation-type-name': {
          'altnames': Value of RelationType node's altnames field [1st
          index-element], 'subject_or_object_type': Value of
          RelationType node's subject_type field, 'inverse_name':
          Value of RelationType node's name field,
          'subject_or_right_subject_list': List of Value(s) of
          GRelation node's subject field } }

        """
        gsystem_type_list = []
        possible_relations = {}

        # Converts to list, if passed parameter is only single ObjectId
        if not isinstance(gsystem_type_id_or_list, list):
            gsystem_type_list = [gsystem_type_id_or_list]
        else:
            gsystem_type_list = gsystem_type_id_or_list

        # Code for finding out relations associated with each gsystem_type_id in the list
        collection = get_database()[Node.collection_name]
        for gsystem_type_id in gsystem_type_list:

            # Converts string representaion of ObjectId to it's corresponding ObjectId type, if found
            if not isinstance(gsystem_type_id, ObjectId):
                if ObjectId.is_valid(gsystem_type_id):
                    gsystem_type_id = ObjectId(gsystem_type_id)
                else:
                    error_message = "\n ObjectIdError: Invalid ObjectId (" + gsystem_type_id + ") found while finding relations !!!\n"
                    raise Exception(error_message)
            
            # Relation 
            inverse_relation = False
            # Case - While editing GSystem Checking in GRelation
            # collection - to collect relations' values, if already
            # set!
            if self.has_key("_id"):
                # If - node has key '_id'
                relations = collection.Triple.find({'_type': "GRelation", 'subject': self._id, 'status': u"PUBLISHED"})
                for rel_obj in relations:
                    # rel_obj is of type - GRelation
                    # [subject(node._id), relation_type(RelationType),
                    # right_subject(value of related object)] Must
                    # convert rel_obj.relation_type [dictionary] to
                    # collection.Node(rel_obj.relation_type)
                    # [document-object]
                    RelationType.append_relation(collection.RelationType(rel_obj.relation_type), 
                                                  possible_relations, inverse_relation, rel_obj.right_subject)

            # Case - While creating GSystem / if new relations get
            # added Checking in RelationType collection - because to
            # collect newly added user-defined relations, if any!
            relations = collection.Node.find({'_type': 'RelationType', 'subject_type': gsystem_type_id})
            for rel_type in relations:
                # Here rel_type is of type -- RelationType
                RelationType.append_relation(rel_type, possible_relations, inverse_relation)

            # type_of check for current GSystemType to which the node
            # belongs to
            gsystem_type_node = collection.Node.one({'_id': gsystem_type_id}, {'name': 1, 'type_of': 1})
            if gsystem_type_node.type_of:
                relations = collection.Node.find({'_type': 'RelationType', 'subject_type': {'$in': gsystem_type_node.type_of}})
                for rel_type in relations:
                    # Here rel_type is of type -- RelationType
                    RelationType.append_relation(rel_type, possible_relations, inverse_relation)

            # Inverse-Relation 
            inverse_relation = True
            # Case - While editing GSystem Checking in GRelation
            # collection - to collect inverse-relations' values, if
            # already set!
            if self.has_key("_id"):
                # If - node has key '_id'
                relations = collection.Triple.find({'_type': "GRelation", 'right_subject': self._id, 'status': u"PUBLISHED"})
                for rel_obj in relations:
                    # rel_obj is of type - GRelation
                    # [subject(node._id), relation_type(RelationType),
                    # right_subject(value of related object)] Must
                    # convert rel_obj.relation_type [dictionary] to
                    # collection.Node(rel_obj.relation_type)
                    # [document-object]
                    RelationType.append_relation(collection.RelationType(rel_obj.relation_type), 
                                                                          possible_relations, inverse_relation, rel_obj.subject)

            # Case - While creating GSystem / if new relations get
            # added Checking in RelationType collection - because to
            # collect newly added user-defined relations, if any!
            relations = collection.Node.find({'_type': 'RelationType', 'object_type': gsystem_type_id})
            for rel_type in relations:
                # Here rel_type is of type -- RelationType
                RelationType.append_relation(rel_type, possible_relations, inverse_relation)

            # type_of check for current GSystemType to which the node
            # belongs to
            gsystem_type_node = collection.Node.one({'_id': gsystem_type_id}, {'name': 1, 'type_of': 1})
            if gsystem_type_node.type_of:
                relations = collection.Node.find({'_type': 'RelationType', 'object_type': {'$in': gsystem_type_node.type_of}})
                for rel_type in relations:
                    # Here rel_type is of type -- RelationType
                    RelationType.append_relation(rel_type, possible_relations, inverse_relation)

        return possible_relations

    def get_neighbourhood(self, member_of):
        """Attaches attributes and relations of the node to itself;
        i.e. key's types to it's structure and key's values to itself 
        """

        attributes = self.get_possible_attributes(member_of)
        for key, value in attributes.iteritems():
            self.structure[key] = value['data_type']
            self[key] = value['object_value']

        relations = self.get_possible_relations(member_of)
        for key, value in relations.iteritems():
            self.structure[key] = value['subject_or_object_type']
            self[key] = value['subject_or_right_subject_list']


@connection.register
class MetaType(Node):
    """MetaType class: Its members are any of GSystemType, AttributeType,
    RelationType, ProcessType.  

    It is used to express the NodeTypes that are part of an
    Application developed using GNOWSYS-Studio. E.g, a GSystemType
    'Page' or 'File' become applications by expressing them as members
    of a MetaType, 'GAPP'.

    """

    structure = {
        'description': basestring,		# Description (name)
        'parent': ObjectId                      # Foreign key to self 
    }
    use_dot_notation = True


@connection.register
class AttributeType(Node):
    '''To define reusable properties that can be set as possible
    attributes to a GSystemType. A set of possible properties defines
    a GSystemType.  

    '''

    structure = {
	'data_type': basestring, # check required: only of the DATA_TYPE_CHOICES
        'complex_data_type': [unicode], # can be a list or a dictionary 
        'subject_type': [ObjectId], # check required: only one of Type
                                    # Nodes. GSystems cannot be set as
                                    # subject_types
	'applicable_node_type': [basestring],	# can be one or more
                                                # than one of
                                                # NODE_TYPE_CHOICES
		
	'verbose_name': basestring,
	'null': bool, 
	'blank': bool, 
	'help_text': unicode,
	'max_digits': int, # applicable if the datatype is a number
	'decimal_places': int, # applicable if the datatype is a float
	'auto_now': bool,
	'auto_now_add': bool,
	'upload_to': unicode,
	'path': unicode,
	'verify_exist': bool,
	'min_length': int, 
	'required': bool,
	'label': unicode,
	'unique': bool,
	'validators': list,
	'default': unicode,
	'editable': bool
    }

    required_fields = ['data_type', 'subject_type']
    use_dot_notation = True

    ##########  User-Defined Functions ##########

    @staticmethod
    def append_attribute(attr_id_or_node, attr_dict, attr_value=None, inner_attr_dict=None):
        collection = get_database()[Node.collection_name]

        if isinstance(attr_id_or_node, unicode):
            # Convert unicode representation of ObjectId into it's
            # corresponding ObjectId type Then fetch
            # attribute-type-node from AttributeType collection of
            # respective ObjectId
            if ObjectId.is_valid(attr_id_or_node):
                attr_id_or_node = collection.Node.one({'_type': 'AttributeType', '_id': ObjectId(attr_id_or_node)})
            else:
                print "\n Invalid ObjectId: ", attr_id_or_node, " is not a valid ObjectId!!!\n"
                # Throw indicating the same
        
        if not attr_id_or_node.complex_data_type:
            # Code for simple data-type Simple data-types: int, float,
            # ObjectId, list, dict, basestring, unicode
            if inner_attr_dict is not None:
                # If inner_attr_dict exists It means node should ne
                # added to this inner_attr_dict and not to attr_dict
                if not inner_attr_dict.has_key(attr_id_or_node.name):
                    # If inner_attr_dict[attr_id_or_node.name] key
                    # doesn't exists, then only add it!
                    if attr_value is None:
                        inner_attr_dict[attr_id_or_node.name] = {'altnames': attr_id_or_node.altnames,
                                                                 '_id': attr_id_or_node._id,
                                                                 'data_type': eval(attr_id_or_node.data_type), 
                                                                 'object_value': attr_value
                                                                }
                    else:
                        inner_attr_dict[attr_id_or_node.name] = {'altnames': attr_id_or_node.altnames,
                                                                 '_id': attr_id_or_node._id,
                                                                 'data_type': eval(attr_id_or_node.data_type), 
                                                                 'object_value': attr_value[attr_id_or_node.name]
                                                                }
                
                if attr_dict.has_key(attr_id_or_node.name):
                    # If this attribute-node exists in outer
                    # attr_dict, then remove it
                    del attr_dict[attr_id_or_node.name]

            else:
                # If inner_attr_dict is None
                if not attr_dict.has_key(attr_id_or_node.name):
                    # If attr_dict[attr_id_or_node.name] key doesn't
                    # exists, then only add it!
                    attr_dict[attr_id_or_node.name] = {'altnames': attr_id_or_node.altnames,
                                                       '_id': attr_id_or_node._id,
                                                       'data_type': eval(attr_id_or_node.data_type), 
                                                       'object_value': attr_value
                                                      }

        else:
            # Code for complex data-type 
            # Complex data-types: [...], {...}
            if attr_id_or_node.data_type == "dict":
                if not attr_dict.has_key(attr_id_or_node.name):
                    inner_attr_dict = {}

                    for c_attr_id in attr_id_or_node.complex_data_type:
                        # NOTE: Here c_attr_id is in unicode format
                        # Hence, this function first converts attr_id 
                        # to ObjectId format if unicode found
                        AttributeType.append_attribute(c_attr_id, attr_dict, attr_value, inner_attr_dict)

                    attr_dict[attr_id_or_node.name] = inner_attr_dict

                else:
                    for remove_attr_name in attr_dict[attr_id_or_node.name].iterkeys():
                        if attr_dict.has_key(remove_attr_name):
                            # If this attribute-node exists in outer
                            # attr_dict, then remove it
                            del attr_dict[remove_attr_name]
                    

            elif attr_id_or_node.data_type == "list":
                if len(attr_id_or_node.complex_data_type) == 1:
                    # Represents list of simple data-types
                    # Ex: [int], [ObjectId], etc.
                    dt = unicode("[" + attr_id_or_node.complex_data_type[0] + "]")
                    if not attr_dict.has_key(attr_id_or_node.name):
                        # If attr_dict[attr_id_or_node.name] key
                        # doesn't exists, then only add it!
                        attr_dict[attr_id_or_node.name] = {'altnames': attr_id_or_node.altnames,
                                                           '_id': attr_id_or_node._id,
                                                           'data_type': eval(dt), 
                                                           'object_value': attr_value
                                                          }
                    
                else:
                    # Represents list of complex data-types Ex:
                    # [{...}]
                    for c_attr_id in attr_id_or_node.complex_data_type:
                        if not ObjectId.is_valid(c_attr_id):
                            # If basic data-type values are found,
                            # pass the iteration
                            continue
           
                        # If unicode representation of ObjectId is
                        # found
                        AttributeType.append_attribute(c_attr_id, attr_dict, attr_value)

            elif attr_id_or_node.data_type == "IS()":
                # Below code does little formatting, for example:
                # data_type: "IS()" complex_value: [u"ab", u"cd"] dt:
                # "IS(u'ab', u'cd')"
                dt = "IS("
                for v in attr_id_or_node.complex_data_type:
                    dt = dt + "u'" + v + "'" + ", " 
                dt = dt[:(dt.rfind(", "))] + ")"

                if not attr_dict.has_key(attr_id_or_node.name):
                    # If attr_dict[attr_id_or_node.name] key doesn't
                    # exists, then only add it!
                    attr_dict[attr_id_or_node.name] = {'altnames': attr_id_or_node.altnames,
                                                       '_id': attr_id_or_node._id,
                                                       'data_type': eval(dt), 
                                                       'object_value': attr_value
                                                      }


@connection.register
class RelationType(Node):

    structure = {
        'inverse_name': unicode,
        'subject_type': [ObjectId],	       # ObjectId's of Any Class
        'object_type': [ObjectId],	       # ObjectId's of Any Class
        'subject_cardinality': int,				
	'object_cardinality': int,
	'subject_applicable_nodetype': basestring,		# NODE_TYPE_CHOICES [default (GST)]
	'object_applicable_nodetype': basestring,
        'slug': basestring,
        'is_symmetric': bool,
        'is_reflexive': bool,
        'is_transitive': bool        
    }

    required_fields = ['inverse_name', 'subject_type', 'object_type']
    use_dot_notation = True

    ##########  User-Defined Functions ##########

    @staticmethod
    def append_relation(rel_type_node, rel_dict, inverse_relation, left_or_right_subject=None):
        """Appends details of a relation in format described below.
        
        Keyword arguments: rel_type_node -- Document of RelationType
        node rel_dict -- Dictionary to which relation-details are
        appended inverse_relation -- Boolean variable that indicates
        whether appending an relation or inverse-relation
        left_or_right_subject -- Actual value of related-subjects
        (only if provided, otherwise by default it's None)
        
        Returns: Dictionary that holds details as follows: Key -- Name
        of the relation Value -- It's again a dictionary that holds
        key and values as shown below: { // If inverse_relation -
        False 'relation-type-name': { 'altnames': Value of
        RelationType node's altnames field [0th index-element],
        'subject_or_object_type': Value of RelationType node's
        object_type field, 'inverse_name': Value of RelationType
        node's inverse_name field, 'subject_or_right_subject_list':
        List of Value(s) of GRelation node's right_subject field }
          
          // If inverse_relation - True 'relation-type-name': {
          'altnames': Value of RelationType node's altnames field [1st
          index-element], 'subject_or_object_type': Value of
          RelationType node's subject_type field, 'inverse_name':
          Value of RelationType node's name field,
          'subject_or_right_subject_list': List of Value(s) of
          GRelation node's subject field } }

        """

        collection = get_database()[Node.collection_name]

        left_or_right_subject_node = None

        if left_or_right_subject:
            left_or_right_subject_node = collection.Node.one({'_id': left_or_right_subject})

            if not left_or_right_subject_node:
                error_message = "\n AppendRelationError: Right subject with this ObjectId("+str(left_or_right_subject)+") doesn't exists !!!"
                raise Exception(error_message)

        rel_name = ""
        opp_rel_name = ""
        alt_names = ""
        subject_or_object_type = None

        if inverse_relation:
          # inverse_relation = True
          # Means looking from object type
          # relation-type's name & inverse-name will be swapped
          rel_name = rel_type_node.inverse_name
          opp_rel_name = rel_type_node.name
          if rel_type_node.altnames:
          	if ";" in rel_type_node.altnames:
          		alt_names = rel_type_node.altnames.split(";")[1]
          else:
          	alt_names = u""
          subject_or_object_type = rel_type_node.subject_type
          
        else:
          # inverse_relation = False
          # Means looking from subject type
          # relation-type's name & inverse-name will be as it is
          rel_name = rel_type_node.name
          opp_rel_name = rel_type_node.inverse_name
          if rel_type_node.altnames:
          	if ";" in rel_type_node.altnames:
          		alt_names = rel_type_node.altnames.split(";")[0]
          else:
          	alt_names = u""
          subject_or_object_type = rel_type_node.object_type

        if not rel_dict.has_key(rel_name):
            subject_or_right_subject_list = [left_or_right_subject_node] if left_or_right_subject_node else []

            rel_dict[rel_name] = {
                'altnames': alt_names,
                'subject_or_object_type': subject_or_object_type,
                'inverse_name': opp_rel_name,
                'subject_or_right_subject_list': subject_or_right_subject_list
            }

        else:
            subject_or_right_subject_list = rel_dict[rel_name]["subject_or_right_subject_list"] if rel_dict[rel_name]["subject_or_right_subject_list"] else []
            if left_or_right_subject_node:
                if not (left_or_right_subject_node in subject_or_right_subject_list):
                    subject_or_right_subject_list.append(left_or_right_subject_node)
                    rel_dict[rel_name]["subject_or_right_subject_list"] = subject_or_right_subject_list

        rel_dict[rel_name]["_id"] = rel_type_node._id
        return rel_dict


class ProcessType(Node):
    """A kind of nodetype for defining processes or events or temporal
    objects involving change.

    """  

    structure = { 
        'changing_attributetype_set': [AttributeType],  # List of Attribute Types
        'changing_relationtype_set': [RelationType]    # List of Relation Types
    }
    use_dot_notation = True

# user should have a list of groups attributeType added should
# automatically be added to the attribute_type_set of GSystemType
 
@connection.register
class GSystemType(Node):
    """Class to generalize GSystems
    """

    structure = {
        'meta_type_set': [MetaType],            # List of Metatypes
        'attribute_type_set': [AttributeType],	# Embed list of Attribute Type Class as Documents
        'relation_type_set': [RelationType],    # Holds list of Relation Types
        'process_type_set': [ProcessType],      # List of Process Types

        'property_order': []                    # List of user-defined attributes in template-view order
    }
    
    use_dot_notation = True
    use_autorefs = True                         # To support Embedding of Documents

    
@connection.register
class GSystem(Node):
    """GSystemType instance
    """
    use_schemaless = True

    structure = {        
        'attribute_set': [dict],		# ObjectIds of GAttributes
        'relation_set': [dict],		            # ObjectIds of GRelations
        'module_set': [dict],                   # Holds the ObjectId & SnapshotID (version_number) of collection elements 
                                                # along with their sub-collection elemnts too 
        'author_set': [int],                     # List of Authors

        'annotations' : [dict],      # List of json files for annotations on the page
        'license': basestring       # contains license/s in string format
    }
    
    use_dot_notation = True

        


@connection.register
class File(GSystem):
    """File class to hold any resource 
    """

    structure = {
        'mime_type': basestring,             # Holds the type of file
        'fs_file_ids': [ObjectId],           # Holds the List of  ids of file stored in gridfs 
        'file_size': {
            'size': float,
            'unit': unicode
        }  #dict used to hold file size in int and unit palace in term of KB,MB,GB
    }

    gridfs = {
        'containers' : ['files']
    }

    use_dot_notation = True

    
@connection.register
class Group(GSystem):
    """Group class to create collection (group) of members
    """

    structure = {
        'group_type': basestring,            # Types of groups - Anonymous, public or private
        'edit_policy': basestring,           # Editing policy of the group - non editable,editable moderated or editable non-moderated
        'subscription_policy': basestring,   # Subscription policy to this group - open, by invitation, by request
        'visibility_policy': basestring,     # Existance of the group - announced or not announced
        'disclosure_policy': basestring,     # Members of this group - disclosed or not 
        'encryption_policy': basestring,     # Encryption - yes or no
        'agency_type': basestring,           # A choice field such as Pratner,Govt.Agency, NGO etc.

        'group_admin': [int],		     # ObjectId of Author class
        'partner':bool                       # Shows partners exists for a group or not     
    }

    use_dot_notation = True

    validators = {
        'group_type':lambda x: x in TYPES_OF_GROUP,
        'edit_policy':lambda x: x in EDIT_POLICY,
        'subscription_policy':lambda x: x in SUBSCRIPTION_POLICY,
        'visibility_policy':lambda x: x in EXISTANCE_POLICY,
        'disclosure_policy':lambda x: x in LIST_MEMBER_POLICY,
        'encryption_policy':lambda x: x in ENCRYPTION_POLICY,
        'agency_type':lambda x: x in GROUP_AGENCY_TYPES
    } 

    def is_gstaff(self, user):
      """
      Checks whether given user belongs to GStaff.
      GStaff includes only the following users of a group:
        1) Super-user (Django's superuser)
        2) Creator of the group (created_by field)
        3) Admin-user of the group (group_admin field)
      Other memebrs (author_set field) doesn't belongs to GStaff.

      Arguments:
      self -- Node of the currently selected group
      user -- User object taken from request object

      Returns:
      True -- If user is one of them, from the above specified list of categories.
      False -- If above criteria is not met (doesn't belongs to any of the category, mentioned above)!
      """

      if (user.is_superuser) or (user.id == self.created_by) or (user.id in self.group_admin):
        return True

      else:
        return False




@connection.register
class Author(Group):
    """Author class to store django user instances
    """
    structure = {                
        'email': unicode,       
        'password': unicode,
        'visited_location': [],
        'preferred_languages':dict,          # preferred languages for users like preferred lang. , fall back lang. etc.
        'group_affiliation':basestring
    }

    use_dot_notation = True

    validators = {
        'agency_type':lambda x: x in AUTHOR_AGENCY_TYPES         # agency_type inherited from Group class
    }

    required_fields = ['name', 'password']
    
    def __init__(self, *args, **kwargs):
        super(Author, self).__init__(*args, **kwargs)
        

    def __eq__(self, other_user):
        # found that otherwise millisecond differences in created_at is compared
        try:
            other_id = other_user['_id']
        except (AttributeError, TypeError):
            return False

        return self['_id'] == other_id


    @property

    def id(self):

        return self.name

    

    def password_crypt(self, password):

        password_salt = str(len(password))

        crypt = hashlib.sha1(password[::-1].upper() + password_salt).hexdigest()

        PASSWORD = unicode(crypt, 'utf-8')

        return PASSWORD  

    

    def is_anonymous(self):

        return False

    

    def is_authenticated(self):

        return True


#  HELPER -- CLASS DEFINITIONS


class HistoryManager():
    """Handles history management for documents of a collection 
    using Revision Control System (RCS).
    """

    objects = models.Manager()

    __RCS_REPO_DIR = RCS_REPO_DIR

    def __init__(self):
        pass

    def check_dir_path(self, dir_path):
        """Checks whether path exists; and if not it creates that path.

        Arguments:
        (1) dir_path -- a string value representing an absolute path 

        Returns: Nothing
        """
        dir_exists = os.path.isdir(dir_path)
    	
    	if not dir_exists:
            os.makedirs(dir_path)

    def get_current_version(self, document_object):
        """Returns the current version/revision number of the given document instance.
        """
        fp = self.get_file_path(document_object)
        rcs = RCS()
        return rcs.head(fp)

    def get_version_dict(self, document_object):
        """Returns a dictionary containing list of revision numbers.
        
        Example:
        {
         "1": "1.1",
         "2": "1.2",
         "3": "1.3",
        }
        """
        fp = self.get_file_path(document_object)

        rcs = RCS()
        current_rev = rcs.head(fp)          # Say, 1.4
        total_no_of_rev = int(rcs.info(fp)["total revisions"])         # Say, 4
        
        version_dict = {}
        for i, j in zip(range(total_no_of_rev), reversed(range(total_no_of_rev))):
            version_dict[(j+1)] = rcs.calculateVersionNumber(fp, (i))

        return version_dict

    def get_file_path(self, document_object):
        """Returns absolute filesystem path for a json-file.

        This path is combination of :-
        (a) collection_directory_path: path to the collection-directory
        to which the given instance belongs
        (b) hashed_directory_structure: path built from object id based 
        on the set hashed-directory-level
        (c) file_name: '.json' extension concatenated with object id of
        the given instance

        Arguments:
        (1) document_object -- an instance of a collection

        Returns: a string representing json-file's path
        """
        file_name = (document_object._id.__str__() + '.json')

        collection_dir = \
            (os.path.join(self.__RCS_REPO_DIR, \
                              document_object.collection_name)) 

        # Example: 
        # if -- file_name := "523f59685a409213818e3ec6.json"
        # then -- collection_hash_dirs := "6/c/3/8/ 
        # -- from last (2^0)pos/(2^1)pos/(2^2)pos/(2^3)pos/../(2^n)pos"
        # here n := hash_level_num
        collection_hash_dirs = ""
        for pos in range(0, RCS_REPO_DIR_HASH_LEVEL):
            collection_hash_dirs += \
                (document_object._id.__str__()[-2**pos] + "/")

        file_path = \
            os.path.join(collection_dir, \
                             (collection_hash_dirs + file_name))

        return file_path

    def create_rcs_repo_collections(self, *versioning_collections):
        """Creates Revision Control System (RCS) repository.

        After creating rcs-repo, it also creates sub-directories 
        for each collection inside it.

        Arguments:
        (1) versioning_collections -- a list representing collection-names

        Returns: Nothing
        """
        try:
            self.check_dir_path(self.__RCS_REPO_DIR)
        except OSError as ose:
            print("\n\n RCS repository not created!!!\n {0}: {1}\n"\
                      .format(ose.errno, ose.strerror))
        else:
            print("\n\n RCS repository created @ following path:\n {0}\n"\
                      .format(self.__RCS_REPO_DIR))

        # for collection in versioning_collections:
        #     rcs_repo_collection = os.path.join(self.__RCS_REPO_DIR, \
        #                                            collection)
        #     try:
        #         os.makedirs(rcs_repo_collection)
        #     except OSError as ose:
        #         print(" {0} collection-directory under RCS repository "\
        #                   "not created!!!\n Error #{1}: {2}\n"\
        #                   .format(collection, ose.errno, ose.strerror))
        #     else:
        #         print(" {0} collection-directory under RCS repository "\
        #                   "created @ following path:\n {1}\n"\
        #                   .format(collection, rcs_repo_collection))
               
    def create_or_replace_json_file(self, document_object=None):
        """Creates/Overwrites a json-file for passed document object in 
        its respective hashed-directory structure.

        Arguments:
        (1) document_object -- an instance of document of a collection

        Returns: A boolean value indicating whether created successfully
        (a) True - if created
        (b) False - Otherwise
        """

        collection_tuple = (MetaType, GSystemType, GSystem, AttributeType, GAttribute, RelationType, GRelation)
        file_res = False    # True, if no error/exception occurred

        if document_object is not None and \
                isinstance(document_object, collection_tuple):

            file_path = self.get_file_path(document_object)

            json_data = document_object.to_json_type()
            #------------------------------------------------------------------
            # Creating/Overwriting data into json-file and rcs-file
            #------------------------------------------------------------------

            # file_mode as w:-
            #    Opens a file for writing only.
            #    Overwrites the file if the file exists.
            #    If the file does not exist, creates a new file for writing.
            file_mode = 'w'	
            rcs_file = None
            
            try:
                self.check_dir_path(os.path.dirname(file_path))

                rcs_file = open(file_path, file_mode)
            except OSError as ose:
                print("\n\n Json-File not created: Hashed directory "\
                          "structure doesn't exists!!!")
                print("\n {0}: {1}\n".format(ose.errno, ose.strerror))
            except IOError as ioe:
                print(" " + str(ioe))
                print("\n\n Please refer following command from "\
                          "\"Get Started\" file:\n"\
                          "\tpython manage.py initrcsrepo\n")
            except Exception as e:
                print(" Unexpected error : " + str(e))
            else:
                rcs_file.write(json.dumps(json_data,
                                          sort_keys=True,
                                          indent=4,
                                          separators=(',', ': '),
                                          cls=NodeJSONEncoder
                                          )
                               )
                
                # TODO: Commit modifications done to the file into 
                # it's rcs-version-file

                file_res = True
            finally:
                if rcs_file is not None:
                    rcs_file.close()

        else:
            # TODO: Throw/raise error having following message!
            # if document_object is None or
            # !isinstance(document_object, collection_tuple)

            msg = " Following instance is either invalid or " \
            + "not matching given instances-type list " + str(collection_tuple) + ":-" \
            + "\n\tObjectId: " + document_object._id.__str__() \
            + "\n\t    Type: " + document_object._type \
            + "\n\t    Name: " + document_object.name
            raise RuntimeError(msg)

        return file_res
      
    def get_version_document(self, document_object, version_no=""):
        """Returns an object representing mongodb document instance of a given version number.
        """
        if version_no == "":
            version_no = self.get_current_version(document_object)

        fp = self.get_file_path(document_object)
        rcs = RCS()
        rcs.checkout((fp, version_no))

        json_data = ""
        with open(fp, 'r') as version_file:
            json_data = version_file.read()

        collection = get_database()[Node.collection_name]
	
	# assigning None value to key, which is not present in json_data compare to Node class keys
	null = 0
	import json
	json_dict = json.loads(json_data)
	json_node_keys = document_object.keys()
	json_dict_keys = json_dict.keys()
	diff_keys = list(set(json_node_keys)-set(json_dict_keys))
	if diff_keys:
		for each in diff_keys:
			json_dict[each]=None
	json_data = json.dumps(json_dict)

        # Converts the json-formatted data into python-specific format
        doc_obj = collection.Node.from_json(json_data)

        rcs.checkin(fp)
        
        # Below Code temporary resolves the problem of '$oid' This
        # problem occurs when we convert mongodb's document into
        # json-format using mongokit's to_json_type() function - It
        # converts ObjectId() type into corresponding format
        # "{u'$oid': u'24-digit-hexstring'}" But actual problem comes
        # into picture when we have a field whose data-type is "list
        # of ObjectIds" In case of '_id' field (automatically created
        # by mongodb), mongokit handles this conversion and does so
        # But not in case of "list of ObjectIds", it still remains in
        # above given format and causes problem

        for k, v in doc_obj.iteritems():
            oid_list_str = ""
            oid_ObjectId_list = []
            if v and type(v) == list:
                oid_list_str = v.__str__()
                try:
                    if '$oid' in oid_list_str: #v.__str__():

                        for oid_dict in v:
                            oid_ObjectId = ObjectId(oid_dict['$oid'])
                            oid_ObjectId_list.append(oid_ObjectId)

                        doc_obj[k] = oid_ObjectId_list

                except Exception as e:
                    print "\n Exception for document's ("+doc_obj.name+") key ("+k+") -- ", str(e), "\n"

        return doc_obj

class NodeJSONEncoder(json.JSONEncoder):
  def default(self, o):
    if isinstance(o, ObjectId):
      return str(o)

    if isinstance(o, datetime.datetime):
      return o.strftime("%d/%m/%Y %H:%M:%S")

    return json.JSONEncoder.default(self, o)



#  TRIPLE CLASS DEFINITIONS


@connection.register
class Triple(DjangoDocument):

  objects = models.Manager()

  collection_name = 'Nodes'
  structure = {
    '_type': unicode,
    'name': unicode,
    'subject_scope': basestring,
    'subject': ObjectId,	          # ObjectId's of GSystem Class
    'lang': basestring,               # Put validation for standard language codes
    'status': STATUS_CHOICES_TU
  }
  
  required_fields = ['name', 'subject']
  use_dot_notation = True
  use_autorefs = True
  ########## Built-in Functions (Overridden) ##########
  
  def __unicode__(self):
    return self._id
  
  def identity(self):
    return self.__unicode__()

  def save(self, *args, **kwargs):
    is_new = False
    
    if not self.has_key('_id'):
      is_new = True               # It's a new document, hence yet no ID!"

    collection = get_database()[Node.collection_name]
    
    """
    Check for correct GSystemType match in AttributeType and GAttribute, similarly for RelationType and GRelation
    """
    #it's me
    subject_name = collection.Node.one({'_id': self.subject}).name
    subject_system_flag = False
    subject_id = self.subject
    subject_document = collection.Node.one({"_id":self.subject})
    # print subject_document

    subject_type_list = []
    subject_member_of_list = []
    name_value = u""

    if self._type == "GAttribute":
      self.name = subject_name + " -- " + self.attribute_type['name'] + " -- " + unicode(self.object_value)
      name_value = self.name

      subject_type_list = self.attribute_type['subject_type']
      subject_member_of_list = subject_document.member_of

      intersection = set(subject_member_of_list) & set(subject_type_list)
      if intersection:
        subject_system_flag = True

      else:
        # If instersection is not found with member_of fields' ObjectIds, 
        # then check for type_of field of each one of the member_of node
        for gst_id in subject_member_of_list:
          gst_node = collection.Node.one({'_id': gst_id}, {'type_of': 1})
          if set(gst_node.type_of) & set(subject_type_list):
            subject_system_flag = True
            break

    elif self._type == "GRelation":
      right_subject_document = collection.Node.one({'_id': self.right_subject})
      right_subject_name = collection.Node.one({'_id': self.right_subject}).name
      self.name = subject_name + " -- " + self.relation_type['name'] + " -- " + right_subject_name
      name_value = self.name

      subject_type_list = self.relation_type['subject_type']
      object_type_list= self.relation_type['object_type']

      left_subject_member_of_list = subject_document.member_of
      right_subject_member_of_list = right_subject_document.member_of

      left_intersection = set(subject_type_list) & set(left_subject_member_of_list)
      right_intersection = set(object_type_list) & set(right_subject_member_of_list)
      if left_intersection and right_intersection:
        subject_system_flag = True

      else:
        left_subject_system_flag = False
        if left_intersection:
          left_subject_system_flag = True

        else:
          for gst_id in left_subject_member_of_list:
            gst_node = collection.Node.one({'_id': gst_id}, {'type_of': 1})
            if set(gst_node.type_of) & set(subject_type_list):
              left_subject_system_flag = True
              break


        right_subject_system_flag = False
        if right_intersection:
          right_subject_system_flag = True

        else:
          for gst_id in right_subject_member_of_list:
            gst_node = collection.Node.one({'_id': gst_id}, {'type_of': 1})
            if set(gst_node.type_of) & set(object_type_list):
              right_subject_system_flag = True
              break

        if left_subject_system_flag and right_subject_system_flag:
          subject_system_flag = True

    if self._type =="GRelation" and subject_system_flag == False:
      print "The 2 lists do not have any common element"
      raise Exception("\n Cannot create the GRelation ("+name_value+") as the subject/object that you have mentioned is not a member of a GSytemType for which this RelationType is defined!!!\n")

    if self._type =="GAttribute" and subject_system_flag == False:
      print "\n The 2 lists do not have any common element\n"
      error_message = "\n "+name_value+ " -- subject_type_list ("+str(subject_type_list)+") -- subject_member_of_list ("+str(subject_member_of_list)+") \n"
      raise Exception(error_message + "Cannot create the GAttribute ("+name_value+") as the subject that you have mentioned is not a member of a GSystemType which this AttributeType is defined")

    #it's me
    #check for data_type in GAttribute case. Object value of the GAttribute must have the same type as that of the type specified in AttributeType
    """if self._type == "GAttribute": data_type_in_attribute_type =
    self.attribute_type['data_type'] data_type_of_object_value =
    type(self.object_value) print "Attribute:: " +
    str(data_type_in_attribute_type) print "Value:: " +
    str(data_type_of_object_value) if data_type_in_attribute_type !=
    data_type_of_object_value: raise Exception("The DataType of the
    value you have entered for this attribute is not correct. Pls ener
    a value with type ---> " + str(data_type_in_attribute_type))

    """
    #end of data_type_check

    super(Triple, self).save(*args, **kwargs)
        
    history_manager = HistoryManager()
    rcs_obj = RCS()
    if is_new:
      # Create history-version-file
      if history_manager.create_or_replace_json_file(self):
        fp = history_manager.get_file_path(self)
        message = "This document (" + self.name + ") is created on " + datetime.datetime.now().strftime("%d %B %Y")
        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")
    
    else:
      # Update history-version-file
      fp = history_manager.get_file_path(self)
      rcs_obj.checkout(fp)

      if history_manager.create_or_replace_json_file(self):
        message = "This document (" + self.name + ") is lastly updated on " + datetime.datetime.now().strftime("%d %B %Y")
        rcs_obj.checkin(fp, 1, message.encode('utf-8'))


@connection.register
class GAttribute(Triple):

    structure = {
        'attribute_type_scope': basestring,
        'attribute_type': AttributeType,  # DBRef of AttributeType Class
        'object_value_scope': basestring,
        'object_value': None		  # value -- it's data-type, is determined by attribute_type field
    }
    
    required_fields = ['attribute_type', 'object_value']
    use_dot_notation = True
    use_autorefs = True                   # To support Embedding of Documents


  

@connection.register
class GRelation(Triple):

    structure = {
        'relation_type_scope': basestring,
        'relation_type': RelationType,    # DBRef of RelationType Class
        'right_subject_scope': basestring,
        'right_subject': ObjectId,	  # ObjectId's of GSystems Class
    }
    
    required_fields = ['relation_type', 'right_subject']
    use_dot_notation = True
    use_autorefs = True                   # To support Embedding of Documents



####################################### Added on 19th June 2014 for SEARCH ##############################


@connection.register
class ReducedDocs(DjangoDocument):
	structure={
            '_type': unicode,
            'content':dict,  #This contains the content in the dictionary format
            'orignal_id':ObjectId, #The object ID of the orignal document
            'required_for':unicode,
            'is_indexed':bool, #This will be true if the map reduced document has been indexed. If it is not then it will be false
	}
	use_dot_notation = True

@connection.register
class ToReduceDocs(DjangoDocument):
	structure={
    '_type': unicode,
		'doc_id':ObjectId,
		'required_for':unicode,
	}
	use_dot_notation = True

@connection.register
class IndexedWordList(DjangoDocument):
	structure={
    '_type': unicode,
		'word_start_id':float,
		'words':dict,
		'required_for':unicode,
	}
	use_dot_notation = True
	#word_start_id = 0 --- a ,1---b,2---c .... 25---z,26--misc.

# This is like a temperory holder, where you can hold any node temporarily and later permenently save in database 
@connection.register
class node_holder(DjangoDocument):
        objects = models.Manager()
        structure={
            '_type': unicode,
            'details_to_hold':dict
        }    
        required_fields = ['details_to_hold']
        use_dot_notation = True

"""
@connection.register
class allLinks(DjangoDocument):
    structure = {
	'member_of':ObjectId,
	'link':unicode,
	'required_for':unicode,
    }
    # required_fields = ['member_of', 'link']
    use_dot_notation = True
"""

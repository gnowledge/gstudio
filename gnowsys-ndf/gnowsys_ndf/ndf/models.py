# imports from python libraries #######################################################################################################
import os
import hashlib
import datetime
import json

from random import random
from random import choice

# imports from installed packages #####################################################################################################
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import check_password
from django.core.validators import RegexValidator
from django.db import models



from django_mongokit import connection
from django_mongokit import get_database
from django_mongokit.document import DjangoDocument

from mongokit import CustomType
from mongokit import IS
from mongokit import OR

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId


# imports from application folders/files ##############################################################################################
from gnowsys_ndf.settings import RCS_REPO_DIR
from gnowsys_ndf.settings import RCS_REPO_DIR_HASH_LEVEL
from gnowsys_ndf.settings import MARKUP_LANGUAGE
from gnowsys_ndf.settings import MARKDOWN_EXTENSIONS

from gnowsys_ndf.ndf.rcslib import RCS



#######################################################################################################################################

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

#######################################################################################################################################
# CUSTOM DATA-TYPE DEFINITIONS
#######################################################################################################################################

STATUS_CHOICES_TU = IS(u'DRAFT', u'HIDDEN', u'PUBLISHED')
STATUS_CHOICES = tuple(str(qtc) for qtc in STATUS_CHOICES_TU)

QUIZ_TYPE_CHOICES_TU = IS(u'Short-Response', u'Single-Choice', u'Multiple-Choice')
QUIZ_TYPE_CHOICES = tuple(str(qtc) for qtc in QUIZ_TYPE_CHOICES_TU)




#######################################################################################################################################
# FRAME CLASS DEFINITIONS
#######################################################################################################################################



@connection.register
class Node(DjangoDocument):
    objects = models.Manager()

    collection_name = 'Nodes'
    structure = {
        '_type': unicode,
        'name': unicode,
        'altnames': unicode,
        'plural': unicode,
        'prior_node': [ObjectId],
        'post_node': [ObjectId],
        
        'language': unicode,

        'type_of': [ObjectId],                  # To define type_of GSystemType for particular node              
        'member_of': [ObjectId],
        'access_policy': unicode,               # To Create Public or Private node

      	'created_at': datetime.datetime,
        'created_by': int,			            # Primary Key of User(django's) Class who created the document

        'last_update': datetime.datetime,
        'modified_by': int,		                # Primary Key of User(django's) Class who lastly modified the document

        'contributors': [int],		            # List of Primary Keys of User(django's) Class

        'location': [dict],

        'content': unicode,
        'content_org': unicode,

        'group_set': [ObjectId],                # List of ObjectId's of Groups to which this document belongs
        'collection_set': [ObjectId],		    # List of ObjectId's of different GTypes/GSystems
        'property_order': [],                   # Determines the order & grouping in which attribute(s)/relation(s) displayed on form

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
    
    required_fields = ['name']
    default_values = {'created_at': datetime.datetime.utcnow, 'status': u'DRAFT'}
    use_dot_notation = True

    ########## Setter(@x.setter) & Getter(@property) ##########

    @property
    def user_details_dict(self):
      """Retrieves names of created-by & modified-by users from the given node, 
      and appends those to 'user_details' dict-variable
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
      """Returns a list having names of each member (GSystemType, i.e Page, File, etc.), 
      built from 'member_of' field (list of ObjectIds)
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
      """Returns a dictionary consisting of key-value pair as ObjectId-Document 
      pair respectively for prior_node objects of the given node.
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
      """Returns a dictionary consisting of key-value pair as ObjectId-Document 
      pair respectively for collection_set objects of the given node.
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
      """Returns a dictionary containing list of revision numbers of
      the given node.
      
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
            print "\n ", self.name, "(", self._id, ") -- Nothing has changed !\n\n"
            return

        is_new = False

        if not self.has_key('_id'):
            is_new = True               # It's a new document, hence yet no ID!"

            # On save, set "created_at" to current date
            self.created_at = datetime.datetime.today()

        self.last_update = datetime.datetime.today()

        # Check the fields which are not present in the class structure, 
        # whether do they exists in their GSystemType's "attribute_type_set";
        #    If exists, add them to the document
        #    Otherwise, throw an error -- " Illegal access: Invalid field found!!! "
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

                            # TODO: Check whether type of "value" matches with that of "attribute['data_type']"
                            # Don't continue searching from list of remaining attributes 
                            break

                    if field_found:
                        # Don't continue searching from list of remaining gsystem-types 
                        break

                if not field_found:
                    print "\n Invalid field(", key, ") found!!!\n"
                    # Throw an error: " Illegal access: Invalid field found!!! "
        
        super(Node, self).save(*args, **kwargs)
        
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
            rcs_obj.checkout(fp)

            try:
                # print "\n Updating...", self._id, " -- ", self.name
                if history_manager.create_or_replace_json_file(self):
                    user = User.objects.get(pk=self.modified_by).username
                    message = "This document (" + self.name + ") is lastly updated by " + user + " status:" + self.status + " on " + self.last_update.strftime("%d %B %Y")
                    rcs_obj.checkin(fp, 1, message.encode('utf-8'))
            except Exception as err:
                print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be updated!!!\n"
                raise RuntimeError(err)
                

    ##########  User-Defined Functions ##########

    def get_possible_attributes(self, gsystem_type_id_or_list):
        """Returns user-defined attribute(s) of given node which belongs to either given single/list of GType(s).

        Keyword arguments:
        gsystem_type_id_or_list -- Single/List of ObjectId(s) of GSystemTypes' to which the given node (self) belongs
  
        If node (self) has '_id' -- Node is created; indicating possible attributes needs to be searched under GAttribute collection & return 
        value of those attributes (previously existing) as part of the list along with attribute-data_type

        Else -- Node needs to be created; indicating possible attributes needs to be searched under AttributeType collection & return default 
        value 'None' of those attributes as part of the list along with attribute-data_type
  
        Returns: 
        Dictionary that holds follwoing details:-
        Key -- Name of the attribute
        Value -- It's again a dictionary that holds key and values as shown below:
        {
          'attribute-type-name': {
              'altnames': Value of AttributeType node's altnames field,
              'data_type': Value of AttributeType node's data_type field,
              'object_value': Value of GAttribute node's object_value field
          }
        }
        
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
        """Returns relation(s) of given node which belongs to either given single/list of GType(s).

        Keyword arguments:
        gsystem_type_id_or_list -- Single/List of ObjectId(s) of GTypes' to which the given node (self) belongs
  
        If node (self) has '_id' -- Node is created; indicating possible relations need to be searched under GRelation collection & return 
        value of those relations (previously existing) as part of the dict along with relation-type details ('object_type' and 'inverse_name')

        Else -- Node needs to be created; indicating possible relations need to be searched under RelationType collection & return default 
        value 'None' for those relations as part of the dict along with relation-type details ('object_type' and 'inverse_name')
  
        Returns: 
        Dictionary that holds details as follows:-
        Key -- Name of the relation
        Value -- It's again a dictionary that holds key and values as shown below:
        {
          // If inverse_relation - False
          'relation-type-name': {
              'altnames': Value of RelationType node's altnames field [0th index-element],
              'subject_or_object_type': Value of RelationType node's object_type field,
              'inverse_name': Value of RelationType node's inverse_name field,
              'subject_or_right_subject_list': List of Value(s) of GRelation node's right_subject field
          }
          
          // If inverse_relation - True
          'relation-type-name': {
              'altnames': Value of RelationType node's altnames field [1st index-element],
              'subject_or_object_type': Value of RelationType node's subject_type field,
              'inverse_name': Value of RelationType node's name field,
              'subject_or_right_subject_list': List of Value(s) of GRelation node's subject field
          }
        }
        
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
            
            # Relation ===================================================================================================================
            inverse_relation = False
            # Case - While editing GSystem
            # Checking in GRelation collection - to collect relations' values, if already set!
            if self.has_key("_id"):
                # If - node has key '_id'
                relations = collection.Triple.find({'_type': "GRelation", 'subject': self._id})
                for rel_obj in relations:
                    # rel_obj is of type - GRelation [subject(node._id), relation_type(RelationType), right_subject(value of related object)]
                    # Must convert rel_obj.relation_type [dictionary] to collection.Node(rel_obj.relation_type) [document-object]
                    RelationType.append_relation(collection.RelationType(rel_obj.relation_type), 
                                                  possible_relations, inverse_relation, rel_obj.right_subject)

            # Case - While creating GSystem / if new relations get added
            # Checking in RelationType collection - because to collect newly added user-defined relations, if any!
            relations = collection.Node.find({'_type': 'RelationType', 'subject_type': gsystem_type_id})
            for rel_type in relations:
                # Here rel_type is of type -- RelationType
                RelationType.append_relation(rel_type, possible_relations, inverse_relation)

            # type_of check for current GSystemType to which the node belongs to
            gsystem_type_node = collection.Node.one({'_id': gsystem_type_id}, {'name': 1, 'type_of': 1})
            if gsystem_type_node.type_of:
                relations = collection.Node.find({'_type': 'RelationType', 'subject_type': {'$in': gsystem_type_node.type_of}})
                for rel_type in relations:
                    # Here rel_type is of type -- RelationType
                    RelationType.append_relation(rel_type, possible_relations, inverse_relation)

            # Inverse-Relation ==============================================================================================================
            inverse_relation = True
            # Case - While editing GSystem
            # Checking in GRelation collection - to collect inverse-relations' values, if already set!
            if self.has_key("_id"):
                # If - node has key '_id'
                relations = collection.Triple.find({'_type': "GRelation", 'right_subject': self._id})
                for rel_obj in relations:
                    # rel_obj is of type - GRelation [subject(node._id), relation_type(RelationType), right_subject(value of related object)]
                    # Must convert rel_obj.relation_type [dictionary] to collection.Node(rel_obj.relation_type) [document-object]
                    RelationType.append_relation(collection.RelationType(rel_obj.relation_type), 
                                                                          possible_relations, inverse_relation, rel_obj.subject)

            # Case - While creating GSystem / if new relations get added
            # Checking in RelationType collection - because to collect newly added user-defined relations, if any!
            relations = collection.Node.find({'_type': 'RelationType', 'object_type': gsystem_type_id})
            for rel_type in relations:
                # Here rel_type is of type -- RelationType
                RelationType.append_relation(rel_type, possible_relations, inverse_relation)

            # type_of check for current GSystemType to which the node belongs to
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
    """MetaType class - A collection of Types 
    """

    structure = {
        'description': basestring,		# Description (name)
        'parent': ObjectId                      # Foreign key to self 
    }
    use_dot_notation = True


@connection.register
class AttributeType(Node):

    structure = {
	'data_type': basestring,
        'complex_data_type': [unicode],
        'subject_type': [ObjectId],
	'applicable_node_type': [basestring],	# NODE_TYPE_CHOICES
		
	'verbose_name': basestring,
	'null': bool,
	'blank': bool,
	'help_text': unicode,
	'max_digits': int,
	'decimal_places': int,
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
            # Convert unicode representation of ObjectId into it's corresponding ObjectId type
            # Then fetch attribute-type-node from AttributeType collection of respective ObjectId
            if ObjectId.is_valid(attr_id_or_node):
                attr_id_or_node = collection.Node.one({'_type': 'AttributeType', '_id': ObjectId(attr_id_or_node)})
            else:
                print "\n Invalid ObjectId: ", attr_id_or_node, " is not a valid ObjectId!!!\n"
                # Throw indicating the same
        
        if not attr_id_or_node.complex_data_type:
            # Code for simple data-type 
            # Simple data-types: int, float, ObjectId, list, dict, basestring, unicode
            if inner_attr_dict is not None:
                # If inner_attr_dict exists
                # It means node should ne added to this inner_attr_dict and not to attr_dict
                if not inner_attr_dict.has_key(attr_id_or_node.name):
                    # If inner_attr_dict[attr_id_or_node.name] key doesn't exists, then only add it!
                    if attr_value is None:
                        inner_attr_dict[attr_id_or_node.name] = {'altnames': attr_id_or_node.altnames,
                                                                 'data_type': eval(attr_id_or_node.data_type), 
                                                                 'object_value': attr_value
                                                                }
                    else:
                        inner_attr_dict[attr_id_or_node.name] = {'altnames': attr_id_or_node.altnames,
                                                                 'data_type': eval(attr_id_or_node.data_type), 
                                                                 'object_value': attr_value[attr_id_or_node.name]
                                                                }
                
                if attr_dict.has_key(attr_id_or_node.name):
                    # If this attribute-node exists in outer attr_dict, then remove it
                    del attr_dict[attr_id_or_node.name]

            else:
                # If inner_attr_dict is None
                if not attr_dict.has_key(attr_id_or_node.name):
                    # If attr_dict[attr_id_or_node.name] key doesn't exists, then only add it!
                    attr_dict[attr_id_or_node.name] = {'altnames': attr_id_or_node.altnames,
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
                            # If this attribute-node exists in outer attr_dict, then remove it
                            del attr_dict[remove_attr_name]
                    

            elif attr_id_or_node.data_type == "list":
                if len(attr_id_or_node.complex_data_type) == 1:
                    # Represents list of simple data-types
                    # Ex: [int], [ObjectId], etc.
                    dt = unicode("[" + attr_id_or_node.complex_data_type[0] + "]")
                    if not attr_dict.has_key(attr_id_or_node.name):
                        # If attr_dict[attr_id_or_node.name] key doesn't exists, then only add it!
                        attr_dict[attr_id_or_node.name] = {'altnames': attr_id_or_node.altnames,
                                                           'data_type': eval(dt), 
                                                           'object_value': attr_value
                                                          }
                    
                else:
                    # Represents list of complex data-types
                    # Ex: [{...}]
                    for c_attr_id in attr_id_or_node.complex_data_type:
                        if not ObjectId.is_valid(c_attr_id):
                            # If basic data-type values are found, pass the iteration
                            continue
           
                        # If unicode representation of ObjectId is found
                        AttributeType.append_attribute(c_attr_id, attr_dict, attr_value)

            elif attr_id_or_node.data_type == "IS()":
                # Below code does little formatting, for example:
                # data_type: "IS()"
                # complex_value: [u"ab", u"cd"]
                # dt: "IS(u'ab', u'cd')"
                dt = "IS("
                for v in attr_id_or_node.complex_data_type:
                    dt = dt + "u'" + v + "'" + ", " 
                dt = dt[:(dt.rfind(", "))] + ")"

                if not attr_dict.has_key(attr_id_or_node.name):
                    # If attr_dict[attr_id_or_node.name] key doesn't exists, then only add it!
                    attr_dict[attr_id_or_node.name] = {'altnames': attr_id_or_node.altnames,
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
        
        Keyword arguments:
        rel_type_node -- Document of RelationType node
        rel_dict -- Dictionary to which relation-details are appended
        inverse_relation -- Boolean variable that indicates whether appending an relation or inverse-relation
        left_or_right_subject -- Actual value of related-subjects (only if provided, otherwise by default it's None)
        
        Returns: Dictionary that holds details as follows:
        Key -- Name of the relation
        Value -- It's again a dictionary that holds key and values as shown below:
        {
          // If inverse_relation - False
          'relation-type-name': {
              'altnames': Value of RelationType node's altnames field [0th index-element],
              'subject_or_object_type': Value of RelationType node's object_type field,
              'inverse_name': Value of RelationType node's inverse_name field,
              'subject_or_right_subject_list': List of Value(s) of GRelation node's right_subject field
          }
          
          // If inverse_relation - True
          'relation-type-name': {
              'altnames': Value of RelationType node's altnames field [1st index-element],
              'subject_or_object_type': Value of RelationType node's subject_type field,
              'inverse_name': Value of RelationType node's name field,
              'subject_or_right_subject_list': List of Value(s) of GRelation node's subject field
          }
        }
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


@connection.register
class GSystemType(Node):
    """Class to organize Systems
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
        # 'attribute_set': [ObjectId],		# ObjectIds of GAttributes
        # 'relation_set': [ObjectId],		# ObjectIds of GRelations
        'module_set': [dict],                   # Holds the ObjectId & SnapshotID (version_number) of collection elements 
                                                # along with their sub-collection elemnts too 
        'author_set': [int],                     # List of Authors

        'annotations' : [dict]      # List of json files for annotations on the page
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
        'disclosure_policy': basestring,    # Members of this group - disclosed or not 
        'encryption_policy': basestring,            # Encryption - yes or no

        'group_admin': [int]				# ObjectId of Author class
    }

    use_dot_notation = True

    validators = {
        'group_type':lambda x: x in TYPES_OF_GROUP,
        'edit_policy':lambda x: x in EDIT_POLICY,
        'subscription_policy':lambda x: x in SUBSCRIPTION_POLICY,
        'visibility_policy':lambda x: x in EXISTANCE_POLICY,
        'disclosure_policy':lambda x: x in LIST_MEMBER_POLICY,
        'encryption_policy':lambda x: x in ENCRYPTION_POLICY
    } 


@connection.register
class Author(Group):
    """Author class to store django user instances
    """
    structure = {                
        'email': unicode,       
        'password': unicode,
        'visited_location': []
    }

    use_dot_notation = True

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



#######################################################################################################################################
#  HELPER -- CLASS DEFINITIONS
#######################################################################################################################################

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
                                          separators=(',', ': ')
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
	json_dict = eval(json_data)
	json_node_keys = collection.Node.keys()
	json_dict_keys = json_dict.keys()
	diff_keys = list(set(json_node_keys)-set(json_dict_keys))
	if diff_keys:
		for each in diff_keys:
			json_dict[each]=None
	json_data = json.dumps(json_dict)

        # Converts the json-formatted data into python-specific format
        doc_obj = collection.Node.from_json(json_data)

        rcs.checkin(fp)
        
        # Below Code temporary resolves the problem of '$oid'
        # This problem occurs when we convert mongodb's document into json-format using mongokit's to_json_type() function
        # - It converts ObjectId() type into corresponding format "{u'$oid': u'24-digit-hexstring'}"
        # But actual problem comes into picture when we have a field whose data-type is "list of ObjectIds"
        # In case of '_id' field (automatically created by mongodb), mongokit handles this conversion and does so
        # But not in case of "list of ObjectIds", it still remains in above given format and causes problem

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


#######################################################################################################################################
#  TRIPLE CLASS DEFINITIONS
#######################################################################################################################################

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
        subject_name = collection.Node.one({'_id': self.subject}).name
        
        if self._type == "GAttribute":
            self.name = subject_name + " -- " + self.attribute_type['name'] + " -- " + unicode(self.object_value)

        elif self._type == "GRelation":
            right_subject_name = collection.Node.one({'_id': self.right_subject}).name
            self.name = subject_name + " -- " + self.relation_type['name'] + " -- " + right_subject_name

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


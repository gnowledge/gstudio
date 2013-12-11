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

from djangoratings.fields import RatingField

from django_mongokit import connection
from django_mongokit import get_database
from django_mongokit.document import DjangoDocument

from mongokit import CustomType

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

STATUS_CHOICES = (
    ('DRAFT'),
    ('HIDDEN'),
    ('PUBLISHED')
)

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

#######################################################################################################################################
#                                                                            C U S T O M    D A T A    T Y P E    D E F I N I T I O N S
#######################################################################################################################################

class RatingField(CustomType):
    mongo_type = unicode
    python_type = int
    def to_bson(self, value):
        """convert type to a mongodb type"""
        return unicode(value)

    def to_python(self, value):
        """convert type to a python object"""
        if value is not None:
            return value
        # else:
        #     return "value must be between 0 and 5"

#######################################################################################################################################
#                                                                                                    C L A S S    D E F I N I T I O N S
#######################################################################################################################################

@connection.register
class Author(DjangoDocument):
    """
    Author class modified for storing in mongokit
    """
    
    objects = models.Manager()
    
    collection_name = 'Authors'
    structure = {
        'username': unicode,
        'password': unicode,
        'email': unicode,
        'first_name': unicode,
        'last_name': unicode,
        'address': unicode,
        'phone': long,
        'is_active': bool,
        'is_staff': bool,
        'is_superuser': bool,        
        'created_at': datetime.datetime,
        'last_login': datetime.datetime,
    }
    
    use_dot_notation = True
    required_fields = ['username', 'password']
    default_values = {'created_at': datetime.datetime.now}
    #validators={
    #'phone': lambda x: x > 0 and x < 10 }
    indexes = [
        {
            'fields': 'username',
            'unique': True
        }
    ]
    
    def __init__(self, *args, **kwargs):
        super(Author, self).__init__(*args, **kwargs)
        
    def __eq__(self, other_user):
        # found that otherwise millisecond differences in created_at is compared
        try:
            other_id = other_user['_id']
        except (AttributeError, TypeError):
            return False
            return self['_id'] == other_id
    
    # play ball with Django
    @property
    def id(self):
        return self.username
    
    def password_crypt(self, password):
        password_salt = str(len(password))
        crypt = hashlib.sha1(password[::-1].upper() + password_salt).hexdigest()
        PASSWORD = unicode(crypt, 'utf-8')
        return PASSWORD  
    
    def is_anonymous(self):
        return False
    
    def is_authenticated(self):
        return True
    
    def get_full_name(self):
        "Returns the first_name plus the last_name, with a space in between."
        full_name = u'%s %s' % (self.first_name, 
                                self.last_name)
        return full_name.strip()
    
    def __unicode__(self):
        return self._id


@connection.register
class Node(DjangoDocument):

    objects = models.Manager()

    collection_name = 'Nodes'
    structure = {
        'name': unicode,
        'altnames': unicode,
        'plural': unicode,
        'prior_node': [ObjectId],
        
        'type_of': unicode,
      	'member_of': [unicode], 		 

      	'created_at': datetime.datetime,
        'last_update': datetime.datetime,
        #'rating': RatingField(),
        'created_by': int,			# Primary Key of User(django's) Class
        'modified_by': [int],		# list of Primary Keys of User(django's) Class

        'start_publication': datetime.datetime,

        'content': unicode,
        'content_org': unicode,
        #'image': 

        'tags': [unicode],
        'featured': bool,

        'comment_enabled': bool,
      	'login_required': bool,
      	#'password': basestring,

        'status': STATUS_CHOICES
    }
    
    required_fields = ['name']
    default_values = {'created_at': datetime.datetime.utcnow}
    use_dot_notation = True

    ########## Setter(@x.setter) & Getter(@property) ##########

    @property
    def html_content(self):
        """Return the content correctly formatted"""
        if MARKUP_LANGUAGE == 'markdown':
            return markdown(self.content, MARKDOWN_EXTENSIONS)
        elif MARKUP_LANGUAGE == 'textile':
            return textile(self.content)
        elif MARKUP_LANGUAGE == 'restructuredtext':
            return restructuredtext(self.content)
        return str(self.content)

    ########## Built-in Functions (Defined/Overridden) ##########
    
    def __unicode__(self):
        return self._id
    
    def identity(self):
        return self.__unicode__()
    
    def save(self, *args, **kwargs):
        is_new = False

        if not self.has_key('_id'):
            is_new = True               # It's a new document, hence yet no ID!"

            ''' on save, set created_at to current date'''
            self.created_at = datetime.datetime.today()

        self.last_update = datetime.datetime.today()

        history_manager = HistoryManager()
        rcs_obj = RCS()
        
        super(Node, self).save(*args, **kwargs)
        
        if is_new:
            # Create history-version-file
            if history_manager.create_or_replace_json_file(self):
                fp = history_manager.get_file_path(self)
                user = User.objects.get(pk=self.created_by).username
                message = "This document ("+str(self.name)+") is created by " + user + " on " + self.created_at.strftime("%d %B %Y")
                rcs_obj.checkin(fp, 1, message, "-i")
        else:
            # Update history-version-file
            fp = history_manager.get_file_path(self)
            rcs_obj.checkout(fp)

            if history_manager.create_or_replace_json_file(self):
                message = "This document ("+str(self.name)+") is lastly updated on " + self.last_update.strftime("%d %B %Y")
                rcs_obj.checkin(fp, 1, message)


@connection.register
class MetaType(Node):
    """
    MetaType class - A collection of Types 
    """

    collection_name = 'MetaTypes'
    structure = {
        'description': basestring,		# Description (name)
        'parent': ObjectId                      # Foreign key to self 
    }
    use_dot_notation = True


@connection.register
class AttributeType(Node):
    collection_name = 'AttributeTypes'
    structure = {
	'data_type': basestring,		# NoneType in mongokit
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


'''
# **********************************************************************
#  This is an Aggregation class, hence we are not keeping history of it.
# **********************************************************************
@connection.register
class Attribute(Node):
    collection_name = 'Attributes'
    structure = {
        'attribute_type': ObjectId,		# ObjectId's of AttributeType Class
        'attribute_value': None                 # To store values of created attribute type		
    }
    
    use_dot_notation = True 
'''
 
@connection.register
class RelationType(Node):
    collection_name = 'RelationTypes'
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
	
'''
# **********************************************************************
#  This is an Aggregation class, hence we are not keeping history of it.
# **********************************************************************

@connection.register
class Relation(Node):
    collection_name = 'Relations'
    structure = {
        'subject_type_value': ObjectId,		# ObjectId's of GSystemType Class
        'relation_type_value': ObjectId,	# ObjectId's of RelationType Class
        'object_type_value': ObjectId,		# ObjectId's of GSystemType Class
	}

    use_dot_notation = True
'''

class ProcessType(Node):
    """
    A kind of nodetype for defining processes or events or temporal                                                                             objects involving change.
    """  
    collection_name = 'ProcessTypes'
    structure = { 
        'changing_attributetype_set': [AttributeType],  # List of Attribute Types
        'changing_relationtype_set': [RelationType]    # List of Relation Types
    }
    use_dot_notation = True


@connection.register
class GSystemType(Node):
    """                                                                                                                                         Class to organize Systems                                                                                                            
    """
    collection_name = 'GSystemTypes'
    structure = {
        'meta_type_set': [MetaType],            # List of Metatypes
        'attribute_type_set': [AttributeType],	# Embed list of Attribute Type Class as Documents
        'relation_type_set': [RelationType],    # Holds list of Relation Types
        'process_type_set': [ProcessType]       # List of Process Types 
    }
    
    use_dot_notation = True
    
    
@connection.register
class GSystem(Node):
    """
    GSystemType instance
    """

    collection_name = 'GSystems'
    structure = {
        'gsystem_type': [ObjectId],		# ObjectId's of GSystemType Class  
        'attribute_set': [dict],		# dict that holds AT name & its values
        'relation_set': [dict],			# dict that holds RT name & its related_object value
        'collection_set': [ObjectId],		# list of ObjectId's of GSystem Class
        'author_set':[Author]                   # List of Authors
    }
    
    use_dot_notation = True


@connection.register
class File(GSystem):
    """
    File class to hold any resource 
    """

    collection_name = 'Files'
    structure = {
        'mime_type' : basestring,           # Holds the type of file
        'fs_file_ids' : [ObjectId],           # Holds the List of  ids of file stored in gridfs 
        'file_size'   :{'size':float,'unit':unicode} #dict used to hold file size in int and unit palace in term of KB,MB,GB
    }

    gridfs = {
        'containers' : ['files']
    }

    use_dot_notation = True

    
@connection.register
class Group(GSystem):
    """
    Group class to create collection (group) of members
    """

    collection_name='Groups'
    structure = {
        'gtype': basestring,                 # Types of groups - Anonymous,public or private
        'edit_policy': basestring,           # Editing policy of the group- non editable, moderately editable, editable
        'sub_policy': basestring,            # Subscription policy to this group- open, by invitation, by request
        'ex_policy': basestring,             # Existance of the group -announced or not announced
        'list_member_policy': basestring,    # Members of this group - disclosed or not 
        'encr_policy': basestring            # Encryption - yes or no
    }

    use_dot_notation = True

    validators = {
        'gtype':lambda x: x in TYPES_OF_GROUP,
        'edit_policy':lambda x: x in EDIT_POLICY,
        'sub_policy':lambda x: x in SUBSCRIPTION_POLICY,
        'ex_policy':lambda x: x in EXISTANCE_POLICY,
        'list_member_policy':lambda x: x in LIST_MEMBER_POLICY,
        'encr_policy':lambda x: x in ENCRYPTION_POLICY
    } 

#######################################################################################################################################
#                                                                                  H E L P E R  --   C L A S S    D E F I N I T I O N S
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
        '''Checks whether path exists; and if not it creates that path.

        Arguments:
          dir_path -- a string value representing an absolute path 

        Returns: Nothing
        '''
        dir_exists = os.path.isdir(dir_path)
    	
    	if not dir_exists:
            os.makedirs(dir_path)

    def get_file_path(self, document_object):
        '''Returns absolute filesystem path for a json-file.

        This path is combination of :-
        (a) collection_directory_path: path to the collection-directory
        to which the given instance belongs
        (b) hashed_directory_structure: path built from object id based 
        on the set hashed-directory-level
        (c) file_name: '.json' extension concatenated with object id of
        the given instance

        Arguments:
          document_object -- an instance of a collection

        Returns: a string representing json-file's path
          
        '''
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
        '''Creates Revision Control System (RCS) repository.

        After creating rcs-repo, it also creates sub-directories 
        for each collection inside it.

        Arguments:
          versioning_collections -- a list representing collection-names

        Returns: Nothing
        '''
        try:
            self.check_dir_path(self.__RCS_REPO_DIR)
        except OSError as ose:
            print("\n\n RCS repository not created!!!\n {0}: {1}\n"\
                      .format(ose.errno, ose.strerror))
        else:
            print("\n\n RCS repository created @ following path:\n {0}\n"\
                      .format(self.__RCS_REPO_DIR))

        for collection in versioning_collections:
            rcs_repo_collection = os.path.join(self.__RCS_REPO_DIR, \
                                                   collection)
            try:
                os.makedirs(rcs_repo_collection)
            except OSError as ose:
                print(" {0} collection-directory under RCS repository "\
                          "not created!!!\n Error #{1}: {2}\n"\
                          .format(collection, ose.errno, ose.strerror))
            else:
                print(" {0} collection-directory under RCS repository "\
                          "created @ following path:\n {1}\n"\
                          .format(collection, rcs_repo_collection))
               
    def create_or_replace_json_file(self, document_object=None):
        '''Creates/Overwrites a json-file for passed document object in 
        its respective hashed-directory structure.

        Arguments:
          document_object -- an instance of document of a collection

        Returns: A boolean value indicating whether created successfully
          True - if created
          False - Otherwise
        '''

        collection_tuple = (AttributeType, RelationType, GSystemType, GSystem)
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

            print("\n Error: Either invalid instance or "\
                      "not matching given instances list!!!")

        return file_res

      

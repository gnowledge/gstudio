''' imports from python libraries '''
import hashlib
import os
import datetime
import json
from random import random
from random import choice

''' imports from installed packages '''
from django.conf import settings
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.models import check_password
from django.db import models

from django_mongokit import connection
from django_mongokit import get_database
from django_mongokit.document import DjangoDocument

from mongokit import OR

from bson import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.settings import RCS_REPO_DIR
from gnowsys_ndf.settings import RCS_REPO_DIR_HASH_LEVEL

############################################################################

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

#############################################################################


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
    
    indexes = [
        {'fields': 'username',
         'unique': True}
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
      	'member_of': unicode, 			# 
      	'created_at': datetime.datetime,
        'created_by': ObjectId,			# ObjectId's of Author Class
        #'rating': 
        'start_publication': datetime.datetime,
        'content': unicode,
        'content_org': unicode,
        #'image': 
        'tags': [unicode],
        'featured': bool,
        'last_update': datetime.datetime,
        'modified_by': [ObjectId],		# list of ObjectId's of Author Class
        'comment_enabled': bool,
      	'login_required': bool
      	#'password': basestring,
        }
    
    required_fields = ['name', 'member_of']
    default_values = {'created_at':datetime.datetime.utcnow}
    use_dot_notation = True
    
    def __unicode__(self):
        return self._id
    
    def identity(self):
        return self.__unicode__()
    
    def save(self, *args, **kwargs):
        ''' on save, set created_at to current date'''
        self.created_at = datetime.datetime.today()
        
        super(Node, self).save(*args, **kwargs)
        
        ''' on save, store history file(in json-format) for 
        corresponding document and commit to it'srepository
        '''
        
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
		
	'verbose_name': basestring,
	'null': bool,
	'blank': bool,
	'help_text': unicode,
	'max_digits': int,
	'decimal_places': int,
	'auto_now': bool,
	'auto_now_at': bool,
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

    required_fields = ['data_type']
    use_dot_notation = True


"""This is an Aggregation class, hence we are not keeping history of it.
"""
@connection.register
class Attribute(Node):
    collection_name = 'Attributes'
    structure = {
        'attribute_type': ObjectId,		# ObjectId's of AttributeType Class
        'attribute_value': None                 # To store values of created attribute type		
	}
    
    use_dot_notation = True 
    
    
@connection.register
class RelationType(Node):
    collection_name = 'RelationTypes'
    structure = {
        'inverse_name': unicode,
        'subject_type': [ObjectId],	       # ObjectId's of GSystemType Class
        'object_type': [ObjectId],	       # ObjectId's of GSystemType Class
        'slug': basestring,
        'is_symmetric': bool,
        'is_reflexive': bool,
        'is_transitive': bool        
	}

    required_fields = ['inverse_name']
    use_dot_notation = True
	

"""This is an Aggregation class, hence we are not keeping history of it.
"""
@connection.register
class Relation(Node):
    collection_name = 'Relations'
    structure = {
        'subject_type_value': ObjectId,		# ObjectId's of GSystemType Class
        'relation_type_value': ObjectId,	# ObjectId's of RelationType Class
        'object_type_value': ObjectId,		# ObjectId's of GSystemType Class
	}

    use_dot_notation = True

class ProcessType(Node):
    """
    A kind of nodetype for defining processes or events or temporal                                                                             objects involving change.
    """  
    collection_name = 'ProcessTypes'
    structure = { 
        'changing_attributetype_set':[AttributeType],  # List of Attribute Types
        'changing_relationtype_set':[RelationType]    # List of Relation Types
        }
    use_dot_notation = True


@connection.register
class GSystemType(Node):
    """                                                                                                                                         class to organize Systems                                                                                                                
    """
    collection_name = 'GSystemTypes'
    structure = {
        'meta_type_set': [MetaType],            #List of Metatypes
        'attribute_type_set': [AttributeType],	# Embed list of Attribute Type Class as Documents
        'relation_type_set':[RelationType],      # Holds list of Relation Types
        'process_type_set':[ProcessType],        # List of Process Types 
        'author_set':[Author]                   # List of Authors
         
	}
    
    use_dot_notation = True
    
    
@connection.register
class GSystem(Node):
    """
    GSystemType instance
    """

    collection_name = 'GSystems'
    structure = {
        'gsystem_type': [GSystemType],		# ObjectId's of GSystemType Class  
        'attribute_set': [dict],		# dict that holds AT name & its values
        'relation_set': [dict],			# dict that holds RT name & its related_object value
        'collection_set': [ObjectId]		# list of ObjectId's of GSystem Class
        }
    
    use_dot_notation = True
    

######################################################################################################





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
        #print("\n file_name      : {0}".format(file_name))

        collection_dir = \
            (os.path.join(self.__RCS_REPO_DIR, \
                              document_object.collection_name)) 
        #print("\n collection_dir : {0}".format(collection_dir))

        # Example: 
        # if -- file_name := "523f59685a409213818e3ec6.json"
        # then -- collection_hash_dirs := "6/c/3/8/ 
        # -- from last (2^0)pos/(2^1)pos/(2^2)pos/(2^3)pos/../(2^n)pos"
        # here n := hash_level_num
        collection_hash_dirs = ""
        for pos in range(0, RCS_REPO_DIR_HASH_LEVEL):
            collection_hash_dirs += \
                (document_object._id.__str__()[-2**pos] + "/")
        #print("\n collection_hash_dirs : {0}".format(collection_hash_dirs))

        file_path = \
            os.path.join(collection_dir, \
                             (collection_hash_dirs + file_name))
        #print("\n file_path      : {0}".format(file_path))

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

        collection_tuple = (Author, AttributeType, RelationType, GSystemType, GSystem)
        file_res = False    # True, if no error/exception occurred

        if document_object is not None and \
                isinstance(document_object, collection_tuple):

            file_path = self.get_file_path(document_object)

            json_data = document_object.to_json_type()
            #print("\n json_data      : {0}".format(self.__json_data))

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

      

''' imports from python libraries '''
import os
import datetime
import json

''' imports from installed packages '''
from django.db import models

from django_mongokit import connection
from django_mongokit.document import DjangoDocument

from mongokit import OR

from bson import ObjectId

from git import Repo
from git.exc import GitCommandError
from git.exc import InvalidGitRepositoryError
from git.exc import NoSuchPathError
from git.repo.fun import is_git_dir

''' imports from application folders/files '''
from gnowsys_ndf.settings import GIT_REPO_DIR
from gnowsys_ndf.settings import GIT_REPO_DIR_HASH_LEVEL

####################################################################################################

@connection.register
class Author(DjangoDocument):
    objects = models.Manager()
    collection_name = 'Authors'
    structure = {
        'name': unicode,
        'created_at': datetime.datetime
    }

    required_fields = ['name']
    default_values = {'created_at':datetime.datetime.utcnow}

    use_dot_notation = True

    def __unicode__(self):
        return self.name

    def identity(self):
        return self.__unicode__()

    def my_func(self, *args, **kwargs):
        return (" my_func working...\n")


@connection.register
class Node(DjangoDocument):
    objects = models.Manager()
    collection_name = 'Nodes'
    structure = {
        'name': unicode,
        'altnames': unicode,
        'plural': unicode,
      	'member_of': unicode,			# 
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
        historyManager = HistoryManager(self)
        historyManager.store_doc_history_as_json_and_commit()
       

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
        'slug': basestring,
        'is_symmetric': bool,
        'is_reflexive': bool,
        'is_transitive': bool
	}

    use_dot_notation = True
	

"""This is an Aggregation class, hence we are not keeping history of it.
"""
@connection.register
class Relation(Node):
    collection_name = 'Relations'
    structure = {
        'subject_object': ObjectId,		# ObjectId's of RelationType Class
        'relation_type': ObjectId,		# ObjectId's of RelationType Class
        'related_object': ObjectId		# ObjectId's of Any type of Class
	}

    use_dot_notation = True


@connection.register
class GSystemType(Node):
    collection_name = 'GSystemTypes'
    structure = {
        'attribute_type_set': [AttributeType]	# Embed list of AttributeType Class as Documents
	}

    use_dot_notation = True
	

@connection.register
class GSystem(Node):
    collection_name = 'GSystems'
    structure = {
        'gsystem_type': ObjectId,		# ObjectId's of GSystemType Class  
        'attribute_set': dict,			# dict that holds keys (with their associated --
                                                # -- values) belonging to it's 'gsystem_type'
        'relation_set': dict,			# list of Relation Class
        'collection_set': [ObjectId]		# list of ObjectId's of GSystem Class
	}

    use_dot_notation = True

####################################################################################################

class HistoryManager():
    """Handles history management for documents of each collection using git.

      Creates/Initializes a git repository for each collection.

      While maintaing history for each document, follows following steps:
        (1) Creates json-format file for each newly created and/or modified 
            document.
        (2) Stores newly created file in it's corresponding collection's git
            repository by creating required level of recursive hash 
            directories.
        (3) Overwrites file, if already exists.
        (4) Adds the modified file to the git using `git add <file-name>`
        (5) Commits the modified file to the git using `git commit -m <msg>`
    """

    objects = models.Manager()


    """ Absolute path to the directory that consists of all
    collection repositories
    """
    __GIT_REPO_DIR = GIT_REPO_DIR
    __collection_hash_dirs = ""

    def __init__(self, document_object=None):
        self.__collection_dir = (os.path.join(self.__GIT_REPO_DIR,\
                                                  document_object.collection_name))\
                                                  if document_object is not None\
                                                  else document_object

        self.__file_name = (document_object._id.__str__() + '.json')\
            if document_object is not None else document_object

        if document_object is not None:
            # Example: self.__collection_hash_dirs = 5/2/3/f/
            for pos in range(0, GIT_REPO_DIR_HASH_LEVEL):
                self.__collection_hash_dirs += \
                    (document_object._id.__str__()[pos] + "/")

        self.__file_path = (self.__collection_dir + '/' + \
                                self.__collection_hash_dirs + self.__file_name)\
                                if document_object is not None else document_object

        self.__collection_git_repo = self.get_repo()\
            if document_object is not None else document_object

        self.__json_data = document_object.to_json_type()\
            if document_object is not None else document_object


    def check_dir_path(self, dir_path):
        dir_exists = os.path.isdir(dir_path)
    	
    	if not dir_exists:
            os.makedirs(dir_path)


    def create_repos(self, *versioning_collections):
        """Creates/Initiates git repositories for each collection

          Arguments:
          versioning_collections -- a list representing number of collections

          Returns: Nothing
        """
        self.check_dir_path(self.__GIT_REPO_DIR)

        for collection in versioning_collections:
            collection_git_repo = \
                Repo.init(os.path.join(self.__GIT_REPO_DIR, collection), True)


    def get_repo(self):
        """Returns git repository object representing current collection 
        based on path corresponding to the document that is passed as an 
        argument to the HistoryManager class's constructor

          Arguments: Empty

          Returns: Repo object
        """
        try:
            return Repo(self.__collection_dir)
        except InvalidGitRepositoryError as igre:
            print("\n {0}_get_repo : {1}".format(InvalidGitRepositoryError.__name__, igre.message))
            return None


    def store_doc_history_as_json_and_commit(self):
        """On save, creates/overwrites a history file in json-format for 
        the document in the corresponding collection's git repository.

        TODO: 
        (1) Reduce HASH-DIR LEVEL by 1, if the current-dir size is full
        """
        
        # file_mode as w
        # Opens a file for writing only. 
        # Overwrites the file if the file exists. 
        # If the file does not exist, creates a new file for writing.
        file_mode = 'w'	 

        file_git = None
        
        try:
            self.check_dir_path(os.path.dirname(self.__file_path))

            file_git = open(self.__file_path, file_mode)
	except IOError as ioe:
            print(" " + str( ioe ) + "\n\n")
            print(" Please refer following command from \"Get Started\"" \
                       "file:\n\tpython manage.py initgitrepos\n")
        except Exception as e:
            print(" Unexpected error : " + str(e))
        else:
            file_git.write(json.dumps(self.__json_data,
                                        sort_keys=True,
                                        indent=4,
                                        separators=(',', ': ')
                                      )
                           )

            # Commit modifications done to the file to it's git repository
            self.add_n_commit()
        finally:
            if file_git is not None:
                file_git.close()

    def add_n_commit(self):
        """Adds and committs list of files to staging area. 
        """

        collection_git_index = None
        file_list            = []

        # creates index (stage area)
        collection_git_index = self.__collection_git_repo.index
        
        # prepares a list of files to be committed and adds them
        file_list.append((self.__collection_hash_dirs + self.__file_name))
        collection_git_index.add(file_list)

        # commits to git repository 
        collection_git_index.commit(" " + (self.__collection_hash_dirs + self.__file_name) + " added/modofied.")


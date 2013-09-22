''' imports from python libraries '''
<<<<<<< HEAD
import os
import datetime
import json

''' imports from installed packages '''
from django.db import models
=======
import os, sys
import datetime
import json
>>>>>>> 50041433bee53a620ba79bdc145a23e7beea01df

''' imports from installed packages '''
from django_mongokit import connection
from django_mongokit.document import DjangoDocument

from mongokit import OR

from bson import ObjectId

<<<<<<< HEAD
from git import Repo
from git.exc import GitCommandError
from git.exc import InvalidGitRepositoryError
from git.exc import NoSuchPathError
from git.repo.fun import is_git_dir

''' imports from application folders/files '''
from gnowsys_ndf.settings import GIT_REPO_DIR
from gnowsys_ndf.settings import GIT_REPO_DIR_HASH_LEVEL

####################################################################################################
=======
''' imports from application folders/files '''
from gnowsys_ndf import settings

####################################################################################################################
>>>>>>> 50041433bee53a620ba79bdc145a23e7beea01df

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
<<<<<<< HEAD
        'modified_by': [ObjectId],		# list of ObjectId's of Author Class
=======
        'modified_by': [ObjectId],					# list of ObjectId's of Author Class
      	#'history': [ObjectId],						# list of ObjectId's of Any Type of Class (Previous)
>>>>>>> 50041433bee53a620ba79bdc145a23e7beea01df
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
        ''' on save insert created_at '''
        self.created_at = datetime.datetime.today()
        
        super(Node, self).save(*args, **kwargs)
		
<<<<<<< HEAD
        historyManager = HistoryManager(self)
=======
		super(Node, self).save(*args, **kwargs)
		
		''' 
			On save, create a history file for the document 
		    in the corresponding collection's git repository 
		'''
		collection_path = os.path.join( settings.GIT_REPO_PATH, 
										self.collection_name )
		file_name = self._id.__str__() + '.json'
		file_path = collection_path + '/' +  file_name
		file_mode = 'w'	# Opens a file for writing only. Overwrites the file if the file exists. If the file does not exist, creates a new file for writing.
		file_git = None
		
		# Checks whether collection_path with two-level hash exists:
		#	If exists: Proceed further...
		#	Else	 : Create that path first, then proceed!
		
		try:
			file_git = open( file_path, file_mode )
			
			file_git.write( json.dumps( self.to_json_type(), 
										sort_keys=True, 
										indent=4, 
										separators=(',', ': ')
									  )
						  )
		except IOError as ioe:
			print( " " + str( ioe ) + "\n\n" )
			print( " Please refer following command from \"Get Started\" file:\n\tpython manage.py initgitrepos\n" )
		except:
			print( "Unexpected error : " + sys.exc_info()[0] )
		else:
			print( " File opened successfully...\n" )
		finally:
			if (file_git != None):
				file_git.close()

>>>>>>> 50041433bee53a620ba79bdc145a23e7beea01df

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


"""
	This is an Aggregation class, hence we are not keeping history of it.
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
	

"""
This is an Aggregation class, hence we are not keeping history of it.
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
        (6)
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
        print("\n __collection_dir : {0}".format(self.__collection_dir))

        self.__file_name = (document_object._id.__str__() + '.json')\
            if document_object is not None else document_object
        print("\n __collection_dir : {0}".format(self.__collection_dir))

        if document_object is not None:
            # Example: self.__collection_hash_dirs = 5/2/3/f/
            for pos in range(0, GIT_REPO_DIR_HASH_LEVEL):
                self.__collection_hash_dirs += \
                    (document_object._id.__str__()[pos] + "/")
        print("\n __collection_hash_dirs : {0}".format(self.__collection_hash_dirs))

        self.__file_path = (self.__collection_dir + '/' + \
                                self.__collection_hash_dirs + self.__file_name)\
                                if document_object is not None else document_object
        print("\n __file_path : {0}".format(self.__file_path))

        self.__collection_git_repo = self.get_repo()\
            if document_object is not None else document_object
        print("\n __collection_git_repo : {0}".format(self.__collection_git_repo))


    def create_repos(self, *versioning_collections):
        """Creates/Initiates git repositories for each collection

         Arguments:
         versioning_collections -- a list representing number of collections

         Returns: Nothing
        """
        dir_exists = os.path.isdir(self.__GIT_REPO_DIR)
    	
    	if not dir_exists:
            os.makedirs(self.__GIT_REPO_DIR)
            print(" Following path for git repository created " \
                      "successfully :- \n  " + self.__GIT_REPO_DIR + "\n")

        for collection in versioning_collections:
            collection_git_repo = \
                Repo.init(os.path.join(self.__GIT_REPO_DIR, collection), True)
            print(" Git repository for {0} created successfully --\n {1}"\
                      .format(collection, collection_git_repo))
    	print("\n")


    def get_repo(self):
        """Returns git repository object representing current collection 
        based on path corresponding to the document that is passed as an 
        argument to the HistoryManager class's constructor
        """
        try:
            return Repo(self.__collection_dir)
        except InvalidGitRepositoryError as igre:
            print("\n {0} : {1}".format(InvalidGitRepositoryError.__name__, igre.message))
            return None

    def store_doc_history_as_json(self):
        """On save, creates/overwrites a history file in json-format for 
        the document in the corresponding collection's git repository.
        """
        
        # file_mode as w
        # Opens a file for writing only. 
        # Overwrites the file if the file exists. 
        # If the file does not exist, creates a new file for writing.
        file_mode = 'w'	 

        file_git = None
        
        try:
            file_git = open(self.__file_path, file_mode)
	except IOError as ioe:
            print( " " + str( ioe ) + "\n\n" )
            print( " Please refer following command from \"Get Started\"" \
                       "file:\n\tpython manage.py initgitrepos\n" )
        except Exception as e:
            print( "Unexpected error : " + str(e) )
        else:
            file_git.write(json.dumps(self.to_json_type(),		
                                        sort_keys=True, 
                                        indent=4, 
                                        separators=(',', ': ')
                                      )
                           )
            #self.add_n_commit()
        finally:
            if file_git is not None:
                file_git.close()

    def add_n_commit(self):
        """Adds and committs list of files to staging area. 
        """

        collection_git_index = None
        file_list            = None

        # creates index (stage area)
        collection_git_index = self.__collection_git_repo.index
        
        # prepares a list of files to be committed and adds them
        file_list.append(self.__file_name)
        collection_git_index.add(file_list)

        # commits to git repository 
        collection_git_index.commit( " " + self.__file_name + " added." )


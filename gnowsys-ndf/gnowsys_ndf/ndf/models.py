''' imports from python libraries '''
import hashlib,os
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


from git import Repo
from git.exc import GitCommandError
from git.exc import InvalidGitRepositoryError
from git.exc import NoSuchPathError
from git.repo.fun import is_git_dir

''' imports from application folders/files '''


###############################################################################

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


@connection.register
class Author(DjangoDocument):
    """
    author class modified for storing in mongokit
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
        #historyManager = HistoryManager(self)
        #historyManager.store_doc_history_as_json_and_commit()
        
        
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
        'subject_type': [ObjectId],	       # ObjectId's of GSystemType Class
        'object_type': [ObjectId],	       # ObjectId's of GSystemType Class        
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
        'object_type_value': ObjectId		# ObjectId's of GSystemType Class
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
        'attribute_set': [dict],		# dict that holds AT name & its values
        'relation_set': [dict],			# dict that holds RT name & its related_object value
        'collection_set': [ObjectId]		# list of ObjectId's of GSystem Class
        }
    
    use_dot_notation = True
 

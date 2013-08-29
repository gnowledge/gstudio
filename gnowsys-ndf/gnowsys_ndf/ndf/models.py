import datetime
from django_mongokit import connection
from django_mongokit.document import DjangoDocument
from bson import ObjectId

from django.contrib.auth.models import User

@connection.register
class Author(DjangoDocument):
    collection_name = 'authors'
    structure = {
        'name': unicode,
        'created_at': datetime.datetime
    }

    required_fields = ['name']
    default_values = {'created_at':datetime.datetime.utcnow}

    use_dot_notation = True

    def __unicode__(self):
		return self._id

    def identity(self):
        return self.__unicode__()


@connection.register
class Node(DjangoDocument):
    collection_name = 'nodes'
    structure = {
        'name': unicode,
        'altnames': unicode,
        'plural': unicode,
      	'node_type': unicode,						# Node_Type_Choices
      	'created_at': datetime.datetime,
        'created_by': ObjectId,						# Author Class
        #'rating': 
        'start_publication': datetime.datetime,
        'content': unicode,
        'content_org': unicode,
        #'image': 
        'tags': [unicode],
        'featured': bool,
        'last_update': datetime.datetime,
        'modified_by': [ObjectId],					# list of Author Class
      	'history': [ObjectId],						# list of Any Type of Class (Previous)
        'comment_enabled': bool,
      	'login_required': bool
      	#'password': basestring,
    }

    required_fields = ['name', 'node_type']
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


@connection.register
class AttributeType(Node):
	collection_name = 'attributeTypes'
	structure = {
		'dataType': basestring,						# Field_Type_Choices
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
		#'validators': list
		'default': unicode,
		'editable': bool
	}

	#required_fields = ['dataType']
	use_dot_notation = True
	

@connection.register
class Attribute(Node):
	collection_name = 'attributes'
	structure = {
		'attribute_type': ObjectId,					# AttributeType
		'attribute_value': None						# To store values of created attribute type		
	}
	
	use_dot_notation = True 
	

@connection.register
class RelationType(Node):
	collection_name = 'relationTypes'
	structure = {
		'inverse_name': unicode,
		'slug': basestring,
		'is_symmetric': bool,
		'is_reflexive': bool,
		'is_transitive': bool
	}

	use_dot_notation = True
	

@connection.register
class Relation(Node):
	collection_name = 'relations'
	structure = {
		'relation_type': ObjectId,					# RelationType Class
		'related_object': ObjectId					# Node Class
	}

	use_dot_notation = True

@connection.register
class GSystemType(Node):
	collection_name = 'gsystemTypes'
	structure = {
		'attribute_type_set': [ObjectId]			# list of Attribute Class
	}

	use_dot_notation = True
	
@connection.register
class GSystem(Node):
	collection_name = 'gsystems'
	structure = {
		'gsystem_type': ObjectId,					# GSystemType Class
		'attribute_set': [ObjectId],				# list of Attribute Class
		'relation_set': [ObjectId],					# list of Relation Class
		'collection_set': [ObjectId]				# list of GSystem Class
	}

	use_dot_notation = True
	
	

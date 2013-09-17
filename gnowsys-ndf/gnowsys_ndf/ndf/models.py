import datetime

from django_mongokit import connection
from django_mongokit.document import DjangoDocument

from mongokit import OR

from bson import ObjectId


@connection.register
class Author(DjangoDocument):
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
    collection_name = 'Nodes'
    structure = {
        'name': unicode,
        'altnames': unicode,
        'plural': unicode,
      	'member_of': unicode,						# 
      	'created_at': datetime.datetime,
        'created_by': ObjectId,						# ObjectId's of Author Class
        #'rating': 
        'start_publication': datetime.datetime,
        'content': unicode,
        'content_org': unicode,
        #'image': 
        'tags': [unicode],
        'featured': bool,
        'last_update': datetime.datetime,
        'modified_by': [ObjectId],					# list of ObjectId's of Author Class
      	"""'history': [ObjectId],"""				# list of ObjectId's of Any Type of Class (Previous)
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


@connection.register
class AttributeType(Node):
	collection_name = 'AttributeTypes'
	structure = {
		'data_type': basestring,						# NoneType in mongokit
		
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
		'attribute_type': ObjectId,					# ObjectId's of AttributeType Class
		'attribute_value': None						# To store values of created attribute type		
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
		'subject_object': ObjectId,					# ObjectId's of RelationType Class
		'relation_type': ObjectId,					# ObjectId's of RelationType Class
		'related_object': ObjectId					# ObjectId's of Any type of Class
	}

	use_dot_notation = True


@connection.register
class GSystemType(Node):
	collection_name = 'GSystemTypes'
	structure = {
		'attribute_type_set': [AttributeType]		# Embed list of AttributeType Class as Documents
	}

	use_dot_notation = True
	

@connection.register
class GSystem(Node):
	collection_name = 'GSystems'
	structure = {
		'gsystem_type': ObjectId,					# ObjectId's of GSystemType Class  
		'attribute_set': dict,						# dictionary that holds keys (with their associated values) belonging to it's 'gsystem_type'
		'relation_set': dict,						# list of Relation Class
		'collection_set': [ObjectId]				# list of ObjectId's of GSystem Class
	}

	use_dot_notation = True


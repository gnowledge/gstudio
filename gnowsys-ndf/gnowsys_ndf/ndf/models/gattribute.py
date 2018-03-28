from base_imports import *
from triple import *

@connection.register
class GAttribute(Triple):
    structure = {
        'attribute_type_scope': dict,
        # 'attribute_type': AttributeType,  # Embedded document of AttributeType Class
        'attribute_type': ObjectId,  # ObjectId of AttributeType node
        # 'object_value_scope': basestring,
        'object_value': None  # value -- it's data-type, is determined by attribute_type field
    }

    indexes = [
        {
            # 1: Compound index
            'fields': [
                ('_type', INDEX_ASCENDING), ('subject', INDEX_ASCENDING), \
                ('attribute_type', INDEX_ASCENDING), ('status', INDEX_ASCENDING)
            ],
            'check': False  # Required because $id is not explicitly specified in the structure
        }
    ]

    required_fields = ['attribute_type', 'object_value']
    use_dot_notation = True
    use_autorefs = True                   # To support Embedding of Documents
    default_values = {
                        'attribute_type_scope': {}
                    }


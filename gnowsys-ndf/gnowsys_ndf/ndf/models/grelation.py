from base_imports import *
from triple import *

@connection.register
class GRelation(Triple):
    structure = {
        'relation_type_scope': dict,
        # 'relation_type': RelationType,  # DBRef of RelationType Class
        'relation_type': ObjectId,  # ObjectId of RelationType node
        # 'right_subject_scope': basestring,
        # ObjectId's of GSystems Class / List of list of ObjectId's of GSystem Class
        'right_subject': OR(ObjectId, list)
    }
    default_values = {
                        'relation_type_scope': {}
                    }

    indexes = [{
        # 1: Compound index
        'fields': [
            ('_type', INDEX_ASCENDING), ('subject', INDEX_ASCENDING), \
            ('relation_type'), ('status', INDEX_ASCENDING), \
            ('right_subject', INDEX_ASCENDING)
        ],
        'check': False  # Required because $id is not explicitly specified in the structure
    }, {
        # 2: Compound index
        'fields': [
            ('_type', INDEX_ASCENDING), ('right_subject', INDEX_ASCENDING), \
            ('relation_type'), ('status', INDEX_ASCENDING)
        ],
        'check': False  # Required because $id is not explicitly specified in the structure
    }]

    required_fields = ['relation_type', 'right_subject']
    use_dot_notation = True
    use_autorefs = True  # To support Embedding of Documents


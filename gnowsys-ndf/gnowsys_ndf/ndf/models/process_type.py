from base_imports import *
from attribute_type import *
from relation_type import *


class ProcessType(Node):
    """A kind of nodetype for defining processes or events or temporal
    objects involving change.
    """
    structure = {
        'changing_attributetype_set': [AttributeType],  # List of Attribute Types
        'changing_relationtype_set': [RelationType]    # List of Relation Types
    }
    use_dot_notation = True




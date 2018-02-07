from base_imports import *
from node import *

@connection.register
class AttributeType(Node):
    '''To define reusable properties that can be set as possible
    attributes to a GSystemType. A set of possible properties defines
    a GSystemType.

    '''

    structure = {
    'data_type': basestring, # check required: only of the DATA_TYPE_CHOICES
    'complex_data_type': [unicode], # can be a list or a dictionary
    'subject_type': [ObjectId], # check required: only one of Type
                                    # Nodes. GSystems cannot be set as
                                    # subject_types
    'subject_scope': list,
    'object_scope': list,
    'attribute_type_scope': list,
    'applicable_node_type': [basestring],	# can be one or more
                                                # than one of
                                                # NODE_TYPE_CHOICES
    'verbose_name': basestring,
    'null': bool,
    'blank': bool,
    'help_text': unicode,
    'max_digits': int, # applicable if the datatype is a number
    'decimal_places': int, # applicable if the datatype is a float
    'auto_now': bool,
    'auto_now_add': bool,
    'upload_to': unicode,
    'path': unicode,
    'verify_exist': bool,

    #   raise issue y used
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
    default_values = {
                        'subject_scope': [],
                        'object_scope': [],
                        'attribute_type_scope': [],
                    }

    # validators={
    # 'data_type':x in DATA_TYPE_CHOICES
    # 'data_type':lambda x: x in DATA_TYPE_CHOICES
    # }

    ##########  User-Defined Functions ##########

    @staticmethod
    def append_attribute(attr_id_or_node, attr_dict, attr_value=None, inner_attr_dict=None):

        from bson.dbref import DBRef
        if isinstance(attr_id_or_node, DBRef):
            attr_id_or_node = AttributeType(db.dereference(attr_id_or_node))

        elif isinstance(attr_id_or_node, (unicode, ObjectId)):
            # Convert unicode representation of ObjectId into it's
            # corresponding ObjectId type Then fetch
            # attribute-type-node from AttributeType collection of
            # respective ObjectId
            if ObjectId.is_valid(attr_id_or_node):
                attr_id_or_node = node_collection.one({'_type': 'AttributeType', '_id': ObjectId(attr_id_or_node)})
            else:
                print "\n Invalid ObjectId: ", attr_id_or_node, " is not a valid ObjectId!!!\n"
                # Throw indicating the same

        if not attr_id_or_node.complex_data_type:
            # Code for simple data-type Simple data-types: int, float,
            # ObjectId, list, dict, basestring, unicode
            if inner_attr_dict is not None:
                # If inner_attr_dict exists It means node should ne
                # added to this inner_attr_dict and not to attr_dict
                if not (attr_id_or_node.name in inner_attr_dict):
                    # If inner_attr_dict[attr_id_or_node.name] key
                    # doesn't exists, then only add it!
                    if attr_value is None:
                        inner_attr_dict[attr_id_or_node.name] = {
                            'altnames': attr_id_or_node.altnames, '_id': attr_id_or_node._id,
                            'data_type': eval(attr_id_or_node.data_type),
                            'object_value': attr_value
                        }
                    else:
                        inner_attr_dict[attr_id_or_node.name] = {
                            'altnames': attr_id_or_node.altnames, '_id': attr_id_or_node._id,
                            'data_type': eval(attr_id_or_node.data_type),
                            'object_value': attr_value[attr_id_or_node.name]
                        }

                if attr_id_or_node.name in attr_dict:
                    # If this attribute-node exists in outer
                    # attr_dict, then remove it
                    del attr_dict[attr_id_or_node.name]

            else:
                # If inner_attr_dict is None
                if not (attr_id_or_node.name in attr_dict):
                    # If attr_dict[attr_id_or_node.name] key doesn't
                    # exists, then only add it!
                    attr_dict[attr_id_or_node.name] = {
                        'altnames': attr_id_or_node.altnames, '_id': attr_id_or_node._id,
                        'data_type': eval(attr_id_or_node.data_type),
                        'object_value': attr_value
                    }

        else:
            # Code for complex data-type
            # Complex data-types: [...], {...}
            if attr_id_or_node.data_type == "dict":
                if not (attr_id_or_node.name in attr_dict):
                    inner_attr_dict = {}

                    for c_attr_id in attr_id_or_node.complex_data_type:
                        # NOTE: Here c_attr_id is in unicode format
                        # Hence, this function first converts attr_id
                        # to ObjectId format if unicode found
                        AttributeType.append_attribute(c_attr_id, attr_dict, attr_value, inner_attr_dict)

                    attr_dict[attr_id_or_node.name] = inner_attr_dict

                else:
                    for remove_attr_name in attr_dict[attr_id_or_node.name].iterkeys():
                        if remove_attr_name in attr_dict:
                            # If this attribute-node exists in outer
                            # attr_dict, then remove it
                            del attr_dict[remove_attr_name]

            elif attr_id_or_node.data_type == "list":
                if len(attr_id_or_node.complex_data_type) == 1:
                    # Represents list of simple data-types
                    # Ex: [int], [ObjectId], etc.
                    dt = unicode("[" + attr_id_or_node.complex_data_type[0] + "]")
                    if not (attr_id_or_node.name in attr_dict):
                        # If attr_dict[attr_id_or_node.name] key
                        # doesn't exists, then only add it!
                        attr_dict[attr_id_or_node.name] = {
                            'altnames': attr_id_or_node.altnames, '_id': attr_id_or_node._id,
                            'data_type': eval(dt),
                            'object_value': attr_value
                        }

                else:
                    # Represents list of complex data-types Ex:
                    # [{...}]
                    for c_attr_id in attr_id_or_node.complex_data_type:
                        if not ObjectId.is_valid(c_attr_id):
                            # If basic data-type values are found,
                            # pass the iteration
                            continue

                        # If unicode representation of ObjectId is
                        # found
                        AttributeType.append_attribute(c_attr_id, attr_dict, attr_value)

            elif attr_id_or_node.data_type == "IS()":
                # Below code does little formatting, for example:
                # data_type: "IS()" complex_value: [u"ab", u"cd"] dt:
                # "IS(u'ab', u'cd')"
                dt = "IS("
                for v in attr_id_or_node.complex_data_type:
                    dt = dt + "u'" + v + "'" + ", "
                dt = dt[:(dt.rfind(", "))] + ")"

                if not (attr_id_or_node.name in attr_dict):
                    # If attr_dict[attr_id_or_node.name] key doesn't
                    # exists, then only add it!
                    attr_dict[attr_id_or_node.name] = {
                        'altnames': attr_id_or_node.altnames, '_id': attr_id_or_node._id,
                        'data_type': eval(dt),
                        'object_value': attr_value
                    }

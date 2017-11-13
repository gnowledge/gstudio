from base_imports import *
from node import *

@connection.register
class RelationType(Node):
    structure = {
        'inverse_name': unicode,
        'subject_type': [ObjectId],  # ObjectId's of Any Class
        'object_type': [OR(ObjectId, list)],  # ObjectId's of Any Class
        'subject_scope': list,
        'object_scope': list,
        'relation_type_scope': list,
        'subject_cardinality': int,
        'object_cardinality': int,
        'subject_applicable_nodetype': basestring,  # NODE_TYPE_CHOICES [default (GST)]
        'object_applicable_nodetype': basestring,
        'slug': basestring,
        'is_symmetric': bool,
        'is_reflexive': bool,
        'is_transitive': bool
    }

    required_fields = ['inverse_name', 'subject_type', 'object_type']
    use_dot_notation = True
    default_values = {
                        'subject_scope': [],
                        'object_scope': [],
                        'relation_type_scope': [],
                    }

    # User-Defined Functions ##########
    @staticmethod
    def append_relation(
        rel_type_node, rel_dict, inverse_relation, left_or_right_subject=None
    ):
        """Appends details of a relation in format described below.

        Keyword arguments:
        rel_type_node -- Document of RelationType
        node rel_dict -- Dictionary to which relation-details are
        appended inverse_relation -- Boolean variable that indicates
        whether appending an relation or inverse-relation
        left_or_right_subject -- Actual value of related-subjects
        (only if provided, otherwise by default it's None)

        Returns: Dictionary that holds details as follows: Key -- Name
        of the relation Value -- It's again a dictionary that holds
        key and values as shown below: { // If inverse_relation -
        False 'relation-type-name': { 'altnames': Value of
        RelationType node's altnames field [0th index-element],
        'subject_or_object_type': Value of RelationType node's
        object_type field, 'inverse_name': Value of RelationType
        node's inverse_name field, 'subject_or_right_subject_list':
        List of Value(s) of GRelation node's right_subject field }

          // If inverse_relation - True 'relation-type-name': {
          'altnames': Value of RelationType node's altnames field [1st
          index-element], 'subject_or_object_type': Value of
          RelationType node's subject_type field, 'inverse_name':
          Value of RelationType node's name field,
          'subject_or_right_subject_list': List of Value(s) of
          GRelation node's subject field } }
        """
        if isinstance(rel_type_node, (unicode, ObjectId)):
            # Convert unicode representation of ObjectId into it's
            # corresponding ObjectId type Then fetch
            # attribute-type-node from AttributeType collection of
            # respective ObjectId
            if ObjectId.is_valid(rel_type_node):
                rel_type_node = node_collection.one({'_type': 'RelationType', '_id': ObjectId(rel_type_node)})
            else:
                print "\n Invalid ObjectId: ", rel_type_node, " is not a valid ObjectId!!!\n"
                # Throw indicating the same

        left_or_right_subject_node = None

        if left_or_right_subject:
            if META_TYPE[3] in rel_type_node.member_of_names_list:
                # If Binary relationship found
                left_or_right_subject_node = node_collection.one({
                    '_id': left_or_right_subject
                })
            else:
                left_or_right_subject_node = []
                if isinstance(left_or_right_subject, ObjectId):
                    left_or_right_subject = [left_or_right_subject]
                for each in left_or_right_subject:
                    each_node = node_collection.one({
                        '_id': each
                    })
                    left_or_right_subject_node.append(each_node)

            if not left_or_right_subject_node:
                error_message = "\n AppendRelationError: Right subject with " \
                    + "this ObjectId(" + str(left_or_right_subject) + ") " \
                    + "doesn't exists !!!"
                raise Exception(error_message)

        rel_name = ""
        opp_rel_name = ""
        alt_names = ""
        subject_or_object_type = None

        if inverse_relation:
            # inverse_relation = True
            # Means looking from object type
            # relation-type's name & inverse-name will be swapped
            rel_name = rel_type_node.inverse_name
            opp_rel_name = rel_type_node.name

            if rel_type_node.altnames:
                if ";" in rel_type_node.altnames:
                    alt_names = rel_type_node.altnames.split(";")[1]
            else:
                alt_names = u""

            subject_or_object_type = rel_type_node.subject_type

        else:
            # inverse_relation = False
            # Means looking from subject type
            # relation-type's name & inverse-name will be as it is
            rel_name = rel_type_node.name
            opp_rel_name = rel_type_node.inverse_name
            if rel_type_node.altnames:
                if ";" in rel_type_node.altnames:
                    alt_names = rel_type_node.altnames.split(";")[0]
            else:
                alt_names = u""

            subject_or_object_type = rel_type_node.object_type

        if not (rel_name in rel_dict):
            subject_or_right_subject_list = [left_or_right_subject_node] if left_or_right_subject_node else []

            rel_dict[rel_name] = {
                'altnames': alt_names,
                'subject_or_object_type': subject_or_object_type,
                'inverse_name': opp_rel_name,
                'subject_or_right_subject_list': subject_or_right_subject_list
            }

        else:
            subject_or_right_subject_list = rel_dict[rel_name]["subject_or_right_subject_list"] if rel_dict[rel_name]["subject_or_right_subject_list"] else []
            if left_or_right_subject_node:
                if not (left_or_right_subject_node in subject_or_right_subject_list):
                    subject_or_right_subject_list.append(left_or_right_subject_node)
                    rel_dict[rel_name]["subject_or_right_subject_list"] = subject_or_right_subject_list

        rel_dict[rel_name]["_id"] = rel_type_node._id
        return rel_dict

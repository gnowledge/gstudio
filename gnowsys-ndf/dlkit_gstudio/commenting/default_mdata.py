"""GStudio osid metadata configurations for commenting service."""

from .. import types
from ..primitives import Type
DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data("DEFAULT"))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data("DEFAULT"))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data("DEFAULT"))
DEFAULT_GENUS_TYPE = Type(**types.Genus().get_type_data("DEFAULT"))



def get_comment_mdata():
    """Return default mdata map for Comment"""
    return {
        'text': {
            'element_label': 'text',
            'instructions': 'enter no more than 256 characters.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_string_values': [{
                'text': '',
                'languageTypeId': str(DEFAULT_LANGUAGE_TYPE),
                'scriptTypeId': str(DEFAULT_SCRIPT_TYPE),
                'formatTypeId': str(DEFAULT_FORMAT_TYPE),
                }],
            'syntax': 'STRING',
            'minimum_string_length': 0,
            'maximum_string_length': 256,
            'string_set': [],
        },
        'reference': {
            'element_label': 'reference',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'rating': {
            'element_label': 'rating',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
    }


def get_book_mdata():
    """Return default mdata map for Book"""
    return {
    }

"""Type default metadata elements"""

from .. import types
from ..primitives import Type
DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data('DEFAULT'))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data('DEFAULT'))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data('DEFAULT'))
DEFAULT_GENUS_TYPE = Type(**types.Genus().get_type_data('DEFAULT'))

MDATA = {
    'display_name': {
        'element_label': 'Display Name',
        'instructions': 'Required, 255 character maximum',
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
        'string_set': []
        }
    
    'display_label': {
        'element_label': 'Display Label',
        'instructions': 'Optional',
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
        'maximum_string_length': 1024, 
        'string_set': []
        }

    'description': {
        'element_label': 'Description',
        'instructions': 'Optional',
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
        'maximum_string_length': 1024, 
        'string_set': []
        }
    
    'domain': {
        'element_label': 'Domain',
        'instructions': 'Optional',
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
        'maximum_string_length': 1024, 
        'string_set': []
        }
    }
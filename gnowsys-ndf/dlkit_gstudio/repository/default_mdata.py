"""GStudio osid metadata configurations for repository service."""

from .. import types
from ..primitives import Type
DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data("DEFAULT"))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data("DEFAULT"))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data("DEFAULT"))
DEFAULT_GENUS_TYPE = Type(**types.Genus().get_type_data("DEFAULT"))
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_LICENSE


def get_asset_mdata():
    """Return default mdata map for Asset"""
    return {
        'copyright_registration': {
            'element_label': 'copyright registration',
            'instructions': 'enter no more than 256 characters.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_string_values': [''],
            'syntax': 'STRING',
            'minimum_string_length': 0,
            'maximum_string_length': 256,
            'string_set': [],
        },
        'copyright': {
            'element_label': 'copyright',
            'instructions': 'enter no more than 256 characters.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_string_values': [{
                'text': GSTUDIO_DEFAULT_LICENSE,
                'languageTypeId': str(DEFAULT_LANGUAGE_TYPE),
                'scriptTypeId': str(DEFAULT_SCRIPT_TYPE),
                'formatTypeId': str(DEFAULT_FORMAT_TYPE),
                }],
            'syntax': 'STRING',
            'minimum_string_length': 0,
            'maximum_string_length': 256,
            'string_set': [],
        },
        'title': {
            'element_label': 'title',
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
        'distribute_verbatim': {
            'element_label': 'distribute verbatim',
            'instructions': 'enter either true or false.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_boolean_values': [None],
            'syntax': 'BOOLEAN',
        },
        'created_date': {
            'element_label': 'created date',
            'instructions': 'enter a valid datetime object.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_date_time_values': [None],
            'syntax': 'DATETIME',
            'date_time_set': [],
        },
        'distribute_alterations': {
            'element_label': 'distribute alterations',
            'instructions': 'enter either true or false.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_boolean_values': [None],
            'syntax': 'BOOLEAN',
        },
        'principal_credit_string': {
            'element_label': 'principal credit string',
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
        'published_date': {
            'element_label': 'published date',
            'instructions': 'enter a valid datetime object.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_date_time_values': [None],
            'syntax': 'DATETIME',
            'date_time_set': [],
        },
        'source': {
            'element_label': 'source',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'provider_links': {
            'element_label': 'provider links',
            'instructions': 'accepts an osid.id.Id[] object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': True,
            'default_id_values': [],
            'syntax': 'ID',
            'id_set': [],
        },
        'public_domain': {
            'element_label': 'public domain',
            'instructions': 'enter either true or false.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_boolean_values': [None],
            'syntax': 'BOOLEAN',
        },
        'distribute_compositions': {
            'element_label': 'distribute compositions',
            'instructions': 'enter either true or false.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_boolean_values': [None],
            'syntax': 'BOOLEAN',
        },
        'composition': {
            'element_label': 'composition',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'published': {
            'element_label': 'published',
            'instructions': 'enter either true or false.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_boolean_values': [None],
            'syntax': 'BOOLEAN',
        },
    }


def get_asset_content_mdata():
    """Return default mdata map for AssetContent"""
    return {
        'url': {
            'element_label': 'url',
            'instructions': 'enter no more than 256 characters.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_string_values': [''],
            'syntax': 'STRING',
            'minimum_string_length': 0,
            'maximum_string_length': 256,
            'string_set': [],
        },
        'data': {
            'element_label': 'data',
            'instructions': 'accepts a valid data input stream.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_object_values': [''],
            'syntax': 'OBJECT',
            'object_types': [],
            'object_set': [],
        },
        'accessibility_type': {
            'element_label': 'accessibility type',
            'instructions': 'accepts an osid.type.Type object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_type_values': ['NoneType%3ANONE%40dlkit.mit.edu'],
            'syntax': 'TYPE',
            'type_set': [],
        },
        'asset': {
            'element_label': 'asset',
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


def get_composition_mdata():
    """Return default mdata map for Composition"""
    return {
        'children': {
            'element_label': 'children',
            'instructions': 'accepts an osid.id.Id[] object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': True,
            'default_id_values': [],
            'syntax': 'ID',
            'id_set': [],
        },
    }


def get_repository_mdata():
    """Return default mdata map for Repository"""
    return {
    }

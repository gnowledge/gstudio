"""GStudio osid metadata configurations for learning service."""

from .. import types
from ..primitives import Type
DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data("DEFAULT"))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data("DEFAULT"))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data("DEFAULT"))
DEFAULT_GENUS_TYPE = Type(**types.Genus().get_type_data("DEFAULT"))



def get_objective_mdata():
    """Return default mdata map for Objective"""
    return {
        'cognitive_process': {
            'element_label': 'cognitive process',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'assessment': {
            'element_label': 'assessment',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'knowledge_category': {
            'element_label': 'knowledge category',
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


def get_activity_mdata():
    """Return default mdata map for Activity"""
    return {
        'courses': {
            'element_label': 'courses',
            'instructions': 'accepts an osid.id.Id[] object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': True,
            'default_id_values': [],
            'syntax': 'ID',
            'id_set': [],
        },
        'assessments': {
            'element_label': 'assessments',
            'instructions': 'accepts an osid.id.Id[] object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': True,
            'default_id_values': [],
            'syntax': 'ID',
            'id_set': [],
        },
        'objective': {
            'element_label': 'objective',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'assets': {
            'element_label': 'assets',
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


def get_proficiency_mdata():
    """Return default mdata map for Proficiency"""
    return {
        'completion': {
            'element_label': 'completion',
            'instructions': 'enter a decimal value.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_decimal_values': [None],
            'syntax': 'DECIMAL',
            'decimal_scale': None,
            'minimum_decimal': None,
            'maximum_decimal': None,
            'decimal_set': [],
        },
        'objective': {
            'element_label': 'objective',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'resource': {
            'element_label': 'resource',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'level': {
            'element_label': 'level',
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


def get_objective_bank_mdata():
    """Return default mdata map for ObjectiveBank"""
    return {
    }

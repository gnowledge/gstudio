"""GStudio osid metadata configurations for assessment.authoring service."""

from .. import types
from ..primitives import Type
DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data("DEFAULT"))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data("DEFAULT"))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data("DEFAULT"))
DEFAULT_GENUS_TYPE = Type(**types.Genus().get_type_data("DEFAULT"))



def get_assessment_part_mdata():
    """Return default mdata map for AssessmentPart"""
    return {
        'assessment_part': {
            'element_label': 'assessment part',
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
        'weight': {
            'element_label': 'weight',
            'instructions': 'enter an integer value',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_integer_values': [None],
            'syntax': 'INTEGER',
            'minimum_integer': None,
            'maximum_integer': None,
            'integer_set': []
        },
        'allocated_time': {
            'element_label': 'allocated time',
            'instructions': 'enter a valid duration object.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_duration_values': [None],
            'syntax': 'DURATION',
            'date_time_set': [],
        },
    }


def get_sequence_rule_mdata():
    """Return default mdata map for SequenceRule"""
    return {
        'next_assessment_part': {
            'element_label': 'next assessment part',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'cumulative': {
            'element_label': 'cumulative',
            'instructions': 'enter either true or false.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_boolean_values': [None],
            'syntax': 'BOOLEAN',
        },
        'assessment_part': {
            'element_label': 'assessment part',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'minimum_score': {
            'element_label': 'minimum score',
            'instructions': 'enter an integer value',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_integer_values': [None],
            'syntax': 'INTEGER',
            'minimum_integer': None,
            'maximum_integer': None,
            'integer_set': []
        },
        'maximum_score': {
            'element_label': 'maximum score',
            'instructions': 'enter an integer value',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_integer_values': [None],
            'syntax': 'INTEGER',
            'minimum_integer': None,
            'maximum_integer': None,
            'integer_set': []
        },
    }

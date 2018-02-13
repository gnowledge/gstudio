"""GStudio osid metadata configurations for grading service."""

from .. import types
from ..primitives import Type
DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data("DEFAULT"))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data("DEFAULT"))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data("DEFAULT"))
DEFAULT_GENUS_TYPE = Type(**types.Genus().get_type_data("DEFAULT"))



def get_grade_mdata():
    """Return default mdata map for Grade"""
    return {
        'output_score': {
            'element_label': 'output score',
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
        'grade_system': {
            'element_label': 'grade system',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'input_score_end_range': {
            'element_label': 'input score end range',
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
        'input_score_start_range': {
            'element_label': 'input score start range',
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
    }


def get_grade_system_mdata():
    """Return default mdata map for GradeSystem"""
    return {
        'numeric_score_increment': {
            'element_label': 'numeric score increment',
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
        'lowest_numeric_score': {
            'element_label': 'lowest numeric score',
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
        'based_on_grades': {
            'element_label': 'based on grades',
            'instructions': 'enter either true or false.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_boolean_values': [None],
            'syntax': 'BOOLEAN',
        },
        'highest_numeric_score': {
            'element_label': 'highest numeric score',
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
    }


def get_grade_entry_mdata():
    """Return default mdata map for GradeEntry"""
    return {
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
        'grade': {
            'element_label': 'grade',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'ignored_for_calculations': {
            'element_label': 'ignored for calculations',
            'instructions': 'enter either true or false.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_boolean_values': [None],
            'syntax': 'BOOLEAN',
        },
        'score': {
            'element_label': 'score',
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
        'gradebook_column': {
            'element_label': 'gradebook column',
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


def get_gradebook_column_mdata():
    """Return default mdata map for GradebookColumn"""
    return {
        'grade_system': {
            'element_label': 'grade system',
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


def get_gradebook_column_summary_mdata():
    """Return default mdata map for GradebookColumnSummary"""
    return {
        'gradebook_column': {
            'element_label': 'gradebook column',
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


def get_gradebook_mdata():
    """Return default mdata map for Gradebook"""
    return {
    }

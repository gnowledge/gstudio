"""GStudio osid metadata configurations for assessment service."""

from .. import types
from ..primitives import Type
DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data("DEFAULT"))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data("DEFAULT"))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data("DEFAULT"))
DEFAULT_GENUS_TYPE = Type(**types.Genus().get_type_data("DEFAULT"))



def get_question_mdata():
    """Return default mdata map for Question"""
    return {
        'item': {
            'element_label': 'item',
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


def get_answer_mdata():
    """Return default mdata map for Answer"""
    return {
        'item': {
            'element_label': 'item',
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


def get_item_mdata():
    """Return default mdata map for Item"""
    return {
        'learning_objectives': {
            'element_label': 'learning objectives',
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


def get_assessment_mdata():
    """Return default mdata map for Assessment"""
    return {
        'rubric': {
            'element_label': 'rubric',
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


def get_assessment_offered_mdata():
    """Return default mdata map for AssessmentOffered"""
    return {
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
        'start_time': {
            'element_label': 'start time',
            'instructions': 'enter a valid datetime object.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_date_time_values': [None],
            'syntax': 'DATETIME',
            'date_time_set': [],
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
        'items_shuffled': {
            'element_label': 'items shuffled',
            'instructions': 'enter either true or false.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_boolean_values': [None],
            'syntax': 'BOOLEAN',
        },
        'score_system': {
            'element_label': 'score system',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'deadline': {
            'element_label': 'deadline',
            'instructions': 'enter a valid datetime object.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_date_time_values': [None],
            'syntax': 'DATETIME',
            'date_time_set': [],
        },
        'duration': {
            'element_label': 'duration',
            'instructions': 'enter a valid duration object.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_duration_values': [None],
            'syntax': 'DURATION',
            'date_time_set': [],
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
        'items_sequential': {
            'element_label': 'items sequential',
            'instructions': 'enter either true or false.',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_boolean_values': [None],
            'syntax': 'BOOLEAN',
        },
    }


def get_assessment_taken_mdata():
    """Return default mdata map for AssessmentTaken"""
    return {
        'assessment_offered': {
            'element_label': 'assessment offered',
            'instructions': 'accepts an osid.id.Id object',
            'required': False,
            'read_only': False,
            'linked': False,
            'array': False,
            'default_id_values': [''],
            'syntax': 'ID',
            'id_set': [],
        },
        'taker': {
            'element_label': 'taker',
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


def get_assessment_section_mdata():
    """Return default mdata map for AssessmentSection"""
    return {
        'assessment_taken': {
            'element_label': 'assessment taken',
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


def get_bank_mdata():
    """Return default mdata map for Bank"""
    return {
    }

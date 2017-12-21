"""Default type enumerators"""
# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods,no-self-use
#    NEED TO RE-IMPLEMENT IN NEW STYLE

from dlkit.abstract_osid.osid.errors import NotFound
from .profile import LANGUAGETYPE, SCRIPTTYPE, FORMATTYPE

class NoneType(object):
    """Enumerator for None or Null Types"""

    none_types = {
        'NONE': 'None',
        'NULL': 'Null',
        }

    def __init__(self):
        self.type_set = {
            'None': self.none_types
        }

    def get_type_data(self, name):
        """Return dictionary representation of type."""
        try:
            return {
                'authority': 'DLKIT.MIT.EDU',
                'namespace': 'NoneType',
                'identifier': name,
                'domain': 'Generic Types',
                'display_name': self.none_types[name] + ' Type',
                'display_label': self.none_types[name],
                'description': ('The ' + self.none_types[name] +
                                ' Type. This type indicates that no type is specified.')
            }
        except IndexError:
            raise NotFound('NoneType: ' + name)

class Genus(object):
    """Enumerator for Genus Types"""

    generic_types = {
        'DEFAULT': 'Default',
        'UNKNOWN': 'Unkown'
        }

    def __init__(self):
        self.type_set = {
            'Gen': self.generic_types
        }

    def get_type_data(self, name):
        """Return dictionary representation of type."""
        try:
            return {
                'authority': 'DLKIT.MIT.EDU',
                'namespace': 'GenusType',
                'identifier': name,
                'domain': 'Generic Types',
                'display_name': self.generic_types[name] + ' Generic Type',
                'display_label': self.generic_types[name],
                'description': ('The ' + self.generic_types[name] +
                                ' Type. This type has no symantic meaning.')
            }
        except IndexError:
            raise NotFound('GenusType: ' + name)

class Language(object):
    """Gets default Language Types"""

    def get_type_data(self, name):
        """Return dictionary representation of type."""
        if name == 'DEFAULT':
            return LANGUAGETYPE
        else:
            raise NotFound('DEFAULT Language Type')

class Script(object):
    """Gets default Script Types"""

    def get_type_data(self, name):
        """Return dictionary representation of type."""
        if name == 'DEFAULT':
            return SCRIPTTYPE
        else:
            raise NotFound('DEFAULT Script Type')


class Format(object):
    """Gets default Format Types"""

    def get_type_data(self, name):
        """Return dictionary representation of type."""
        if name == 'DEFAULT':
            return FORMATTYPE
        else:
            raise NotFound('DEFAULT Format Type')


class Relationship(object):
    """Enumerator for Relationship Types"""

    def __init__(self):
        pass

    def get_type_data(self, name):
        """Return dictionary representation of type."""
        try:
            return {
                'authority': 'DLKIT',
                'namespace': 'relationship.Relationship',
                'identifier': name.lower(),
                'domain': 'Generic Types',
                'display_name': name.title() + ' Type',
                'display_label': name.title(),
                'description': ('The ' + name.title() + ' Type.')
            }
        except IndexError:
            raise NotFound('RelationshipType: ' + name.title())

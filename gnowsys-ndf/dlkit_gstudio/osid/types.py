"""Generic type enumerators - IS THIS USED???"""
# -*- coding: utf-8 -*-
# pylint: disable=too-few-public-methods
#    needs to be converted to new-style type enumerators, or discarded

class Generic(object):
    """Enumerator for None or Null Types"""

    generic_types = {
        'DEFAULT': 'Default',
        'UNKNOWN': 'Unkown'
        }

    def __init__(self):
        type_set = {
            'GT': self.generic_types
            }

    def get_type_data(self, name):
        """Return dictionary representation of type."""
        return {
            'authority': 'birdland.mit.edu',
            'namespace': 'Genus Types',
            'identifier': name,
            'domain': 'Generic Types',
            'display_name': self.generic_types[name] + ' Generic Type',
            'display_label': self.generic_types[name],
            'description': ('The ' +  self.generic_types[name] +
                            ' Type. This type has no symantic meaning.')
            }

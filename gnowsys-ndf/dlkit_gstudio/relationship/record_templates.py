"""GStudio implementations of relationship records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.relationship import records as abc_relationship_records
from ..osid import records as osid_records




class RelationshipRecord(abc_relationship_records.RelationshipRecord, osid_records.OsidRecord):
    """A record for a ``Relationship``.

    The methods specified by the record type are available through the
    underlying object.

    """




class RelationshipQueryRecord(abc_relationship_records.RelationshipQueryRecord, osid_records.OsidRecord):
    """A record for a ``RelationshipQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class RelationshipFormRecord(abc_relationship_records.RelationshipFormRecord, osid_records.OsidRecord):
    """A record for a ``RelationshipForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class RelationshipSearchRecord(abc_relationship_records.RelationshipSearchRecord, osid_records.OsidRecord):
    """A record for a ``RelationshipSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class FamilyRecord(abc_relationship_records.FamilyRecord, osid_records.OsidRecord):
    """A record for a ``Family``.

    The methods specified by the record type are available through the
    underlying object.

    """




class FamilyQueryRecord(abc_relationship_records.FamilyQueryRecord, osid_records.OsidRecord):
    """A record for a ``FamilyQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class FamilyFormRecord(abc_relationship_records.FamilyFormRecord, osid_records.OsidRecord):
    """A record for a ``FamilyForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class FamilySearchRecord(abc_relationship_records.FamilySearchRecord, osid_records.OsidRecord):
    """A record for a ``FamilySearch``.

    The methods specified by the record type are available through the
    underlying object.

    """





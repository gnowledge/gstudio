"""GStudio implementations of learning records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.learning import records as abc_learning_records
from ..osid import records as osid_records




class ObjectiveRecord(abc_learning_records.ObjectiveRecord, osid_records.OsidRecord):
    """A record for an ``Objective``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ObjectiveQueryRecord(abc_learning_records.ObjectiveQueryRecord, osid_records.OsidRecord):
    """A record for an ``ObjectiveQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ObjectiveFormRecord(abc_learning_records.ObjectiveFormRecord, osid_records.OsidRecord):
    """A record for an ``ObjectiveForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ObjectiveSearchRecord(abc_learning_records.ObjectiveSearchRecord, osid_records.OsidRecord):
    """A record for an ``ObjectiveSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ActivityRecord(abc_learning_records.ActivityRecord, osid_records.OsidRecord):
    """A record for a ``Activity``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ActivityQueryRecord(abc_learning_records.ActivityQueryRecord, osid_records.OsidRecord):
    """A record for an ``ActivityQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ActivityFormRecord(abc_learning_records.ActivityFormRecord, osid_records.OsidRecord):
    """A record for a ``ActivityForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ActivitySearchRecord(abc_learning_records.ActivitySearchRecord, osid_records.OsidRecord):
    """A record for an ``ActivitySearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ProficiencyRecord(abc_learning_records.ProficiencyRecord, osid_records.OsidRecord):
    """A record for a ``Proficiency``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ProficiencyQueryRecord(abc_learning_records.ProficiencyQueryRecord, osid_records.OsidRecord):
    """A record for a ``ProficiencyQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ProficiencyFormRecord(abc_learning_records.ProficiencyFormRecord, osid_records.OsidRecord):
    """A record for a ``ProficiencyForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ProficiencySearchRecord(abc_learning_records.ProficiencySearchRecord, osid_records.OsidRecord):
    """A record for a ``ProficiencySearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ObjectiveBankRecord(abc_learning_records.ObjectiveBankRecord, osid_records.OsidRecord):
    """A record for a ``ObjectiveBank``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ObjectiveBankQueryRecord(abc_learning_records.ObjectiveBankQueryRecord, osid_records.OsidRecord):
    """A record for an ``ObjectiveBankQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ObjectiveBankFormRecord(abc_learning_records.ObjectiveBankFormRecord, osid_records.OsidRecord):
    """A record for a ``ObjectiveBankForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ObjectiveBankSearchRecord(abc_learning_records.ObjectiveBankSearchRecord, osid_records.OsidRecord):
    """A record for a ``ObjectiveBankSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """





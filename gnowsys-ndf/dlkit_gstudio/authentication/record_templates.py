"""GStudio implementations of authentication records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.authentication import records as abc_authentication_records
from ..osid import records as osid_records




class AgentRecord(abc_authentication_records.AgentRecord, osid_records.OsidRecord):
    """A record for an ``Agent``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AgentQueryRecord(abc_authentication_records.AgentQueryRecord, osid_records.OsidRecord):
    """A record for an ``AgentQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AgentFormRecord(abc_authentication_records.AgentFormRecord, osid_records.OsidRecord):
    """A record for an ``AgentForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AgentSearchRecord(abc_authentication_records.AgentSearchRecord, osid_records.OsidRecord):
    """A record for an ``AgentSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """





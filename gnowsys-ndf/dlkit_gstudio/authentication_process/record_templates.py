"""GStudio implementations of authentication.process records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.authentication_process import records as abc_authentication_process_records
from ..osid import records as osid_records




class AuthenticationRecord(abc_authentication_process_records.AuthenticationRecord, osid_records.OsidRecord):
    """A record for an ``Authentication``.

    The methods specified by the record type are available through the
    underlying object.

    """





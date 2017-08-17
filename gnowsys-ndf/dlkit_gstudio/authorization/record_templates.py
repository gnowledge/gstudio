"""GStudio implementations of authorization records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.authorization import records as abc_authorization_records
from ..osid import records as osid_records




class AuthorizationRecord(abc_authorization_records.AuthorizationRecord, osid_records.OsidRecord):
    """A record for an ``Authorization`` The methods specified by the record type are available through the underlying object."""




class AuthorizationQueryRecord(abc_authorization_records.AuthorizationQueryRecord, osid_records.OsidRecord):
    """A record for an ``AuthorizationQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AuthorizationFormRecord(abc_authorization_records.AuthorizationFormRecord, osid_records.OsidRecord):
    """A record for an ``AuthorizationForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AuthorizationSearchRecord(abc_authorization_records.AuthorizationSearchRecord, osid_records.OsidRecord):
    """A record for an ``AuthorizationSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class VaultRecord(abc_authorization_records.VaultRecord, osid_records.OsidRecord):
    """A record for a ``Vault``.

    The methods specified by the record type are available through the
    underlying object.

    """




class VaultQueryRecord(abc_authorization_records.VaultQueryRecord, osid_records.OsidRecord):
    """A record for a ``VaultQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class VaultFormRecord(abc_authorization_records.VaultFormRecord, osid_records.OsidRecord):
    """A record for a ``VaultForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class VaultSearchRecord(abc_authorization_records.VaultSearchRecord, osid_records.OsidRecord):
    """A record for a ``VaultSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """





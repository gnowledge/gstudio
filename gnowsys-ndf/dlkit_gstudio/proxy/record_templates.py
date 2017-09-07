"""GStudio implementations of proxy records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.proxy import records as abc_proxy_records
from ..osid import records as osid_records




class ProxyRecord(abc_proxy_records.ProxyRecord, osid_records.OsidRecord):
    """A record for a ``Proxy``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ProxyConditionRecord(abc_proxy_records.ProxyConditionRecord, osid_records.OsidRecord):
    """A record for a ``ProxyCondition``.

    The methods specified by the record type are available through the
    underlying object.

    """





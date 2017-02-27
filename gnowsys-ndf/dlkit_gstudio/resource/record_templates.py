"""GStudio implementations of resource records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.resource import records as abc_resource_records
from ..osid import records as osid_records




class ResourceRecord(abc_resource_records.ResourceRecord, osid_records.OsidRecord):
    """A record for a ``Resource``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ResourceQueryRecord(abc_resource_records.ResourceQueryRecord, osid_records.OsidRecord):
    """A record for a ``ResourceQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ResourceFormRecord(abc_resource_records.ResourceFormRecord, osid_records.OsidRecord):
    """A record for a ``ResourceForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ResourceSearchRecord(abc_resource_records.ResourceSearchRecord, osid_records.OsidRecord):
    """A record for a ``ResourceSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BinRecord(abc_resource_records.BinRecord, osid_records.OsidRecord):
    """A record for a ``Bin``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BinQueryRecord(abc_resource_records.BinQueryRecord, osid_records.OsidRecord):
    """A record for a ``BinQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BinFormRecord(abc_resource_records.BinFormRecord, osid_records.OsidRecord):
    """A record for a ``BinForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BinSearchRecord(abc_resource_records.BinSearchRecord, osid_records.OsidRecord):
    """A record for a ``BinSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """





"""GStudio implementations of repository records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.repository import records as abc_repository_records
from ..osid import records as osid_records




class AssetRecord(abc_repository_records.AssetRecord, osid_records.OsidRecord):
    """A record for an ``Asset``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssetQueryRecord(abc_repository_records.AssetQueryRecord, osid_records.OsidRecord):
    """A record for an ``AssetQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssetFormRecord(abc_repository_records.AssetFormRecord, osid_records.OsidRecord):
    """A record for an ``AssetForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssetSearchRecord(abc_repository_records.AssetSearchRecord, osid_records.OsidRecord):
    """A record for an ``AssetSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssetContentRecord(abc_repository_records.AssetContentRecord, osid_records.OsidRecord):
    """A record for an ``AssetContent``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssetContentQueryRecord(abc_repository_records.AssetContentQueryRecord, osid_records.OsidRecord):
    """A record for an ``AssetContentQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssetContentFormRecord(abc_repository_records.AssetContentFormRecord, osid_records.OsidRecord):
    """A record for an ``AssetForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class CompositionRecord(abc_repository_records.CompositionRecord, osid_records.OsidRecord):
    """A record for a ``Composition``.

    The methods specified by the record type are available through the
    underlying object.

    """




class CompositionQueryRecord(abc_repository_records.CompositionQueryRecord, osid_records.OsidRecord):
    """A record for a ``CompositionQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class CompositionFormRecord(abc_repository_records.CompositionFormRecord, osid_records.OsidRecord):
    """A record for a ``CompositionForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class CompositionSearchRecord(abc_repository_records.CompositionSearchRecord, osid_records.OsidRecord):
    """A record for a ``CompositionSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class RepositoryRecord(abc_repository_records.RepositoryRecord, osid_records.OsidRecord):
    """A record for a ``Repository``.

    The methods specified by the record type are available through the
    underlying object.

    """




class RepositoryQueryRecord(abc_repository_records.RepositoryQueryRecord, osid_records.OsidRecord):
    """A record for a ``RepositoryQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class RepositoryFormRecord(abc_repository_records.RepositoryFormRecord, osid_records.OsidRecord):
    """A record for a ``RepositoryForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class RepositorySearchRecord(abc_repository_records.RepositorySearchRecord, osid_records.OsidRecord):
    """A record for a ``RepositorySearch``.

    The methods specified by the record type are available through the
    underlying object.

    """





"""GStudio implementations of commenting records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.commenting import records as abc_commenting_records
from ..osid import records as osid_records




class CommentRecord(abc_commenting_records.CommentRecord, osid_records.OsidRecord):
    """A record for a ``Comment``.

    The methods specified by the record type are available through the
    underlying object.

    """




class CommentQueryRecord(abc_commenting_records.CommentQueryRecord, osid_records.OsidRecord):
    """A record for a ``CommentQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class CommentFormRecord(abc_commenting_records.CommentFormRecord, osid_records.OsidRecord):
    """A record for a ``CommentForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class CommentSearchRecord(abc_commenting_records.CommentSearchRecord, osid_records.OsidRecord):
    """A record for a ``CommentSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BookRecord(abc_commenting_records.BookRecord, osid_records.OsidRecord):
    """A record for a ``Book``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BookQueryRecord(abc_commenting_records.BookQueryRecord, osid_records.OsidRecord):
    """A record for a ``BookQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BookFormRecord(abc_commenting_records.BookFormRecord, osid_records.OsidRecord):
    """A record for a ``BookForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BookSearchRecord(abc_commenting_records.BookSearchRecord, osid_records.OsidRecord):
    """A record for a ``BookSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """





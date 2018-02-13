"""GStudio implementations of grading records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.grading import records as abc_grading_records
from ..osid import records as osid_records




class GradeRecord(abc_grading_records.GradeRecord, osid_records.OsidRecord):
    """A record for a ``Grade``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradeQueryRecord(abc_grading_records.GradeQueryRecord, osid_records.OsidRecord):
    """A record for a ``GradeQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradeFormRecord(abc_grading_records.GradeFormRecord, osid_records.OsidRecord):
    """A record for a ``GradeForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradeSystemRecord(abc_grading_records.GradeSystemRecord, osid_records.OsidRecord):
    """A record for a ``GradeSystem``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradeSystemQueryRecord(abc_grading_records.GradeSystemQueryRecord, osid_records.OsidRecord):
    """A record for a ``GradeSystemQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradeSystemFormRecord(abc_grading_records.GradeSystemFormRecord, osid_records.OsidRecord):
    """A record for a ``GradeSystemForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradeSystemSearchRecord(abc_grading_records.GradeSystemSearchRecord, osid_records.OsidRecord):
    """A record for a ``GradeSystemSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradeEntryRecord(abc_grading_records.GradeEntryRecord, osid_records.OsidRecord):
    """A record for a ``GradeEntry``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradeEntryQueryRecord(abc_grading_records.GradeEntryQueryRecord, osid_records.OsidRecord):
    """A record for a ``GradeEntryQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradeEntryFormRecord(abc_grading_records.GradeEntryFormRecord, osid_records.OsidRecord):
    """A record for a ``GradeEntryForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradeEntrySearchRecord(abc_grading_records.GradeEntrySearchRecord, osid_records.OsidRecord):
    """A record for a ``GradeEntrySearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradebookColumnRecord(abc_grading_records.GradebookColumnRecord, osid_records.OsidRecord):
    """A record for a ``GradebookColumn``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradebookColumnQueryRecord(abc_grading_records.GradebookColumnQueryRecord, osid_records.OsidRecord):
    """A record for a ``GradebookColumnQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradebookColumnFormRecord(abc_grading_records.GradebookColumnFormRecord, osid_records.OsidRecord):
    """A record for a ``GradebookColumnForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradebookColumnSearchRecord(abc_grading_records.GradebookColumnSearchRecord, osid_records.OsidRecord):
    """A record for a ``GradebookColumnSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradebookColumnSummaryRecord(abc_grading_records.GradebookColumnSummaryRecord, osid_records.OsidRecord):
    """A record for a ``GradebookColumnSummary``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradebookColumnSummaryQueryRecord(abc_grading_records.GradebookColumnSummaryQueryRecord, osid_records.OsidRecord):
    """A record for a ``GradebookColumnSummaryQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradebookRecord(abc_grading_records.GradebookRecord, osid_records.OsidRecord):
    """A record for a ``Gradebook``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradebookQueryRecord(abc_grading_records.GradebookQueryRecord, osid_records.OsidRecord):
    """A record for a ``GradebookQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradebookFormRecord(abc_grading_records.GradebookFormRecord, osid_records.OsidRecord):
    """A record for a ``GradebookForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class GradebookSearchRecord(abc_grading_records.GradebookSearchRecord, osid_records.OsidRecord):
    """A record for a ``GradebookSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """





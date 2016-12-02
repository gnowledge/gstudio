"""GStudio implementations of assessment records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.assessment import records as abc_assessment_records
from ..osid import records as osid_records




class QuestionRecord(abc_assessment_records.QuestionRecord, osid_records.OsidRecord):
    """A record for a ``Question``.

    The methods specified by the record type are available through the
    underlying object.

    """




class QuestionQueryRecord(abc_assessment_records.QuestionQueryRecord, osid_records.OsidRecord):
    """A record for a ``QuestionQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class QuestionFormRecord(abc_assessment_records.QuestionFormRecord, osid_records.OsidRecord):
    """A record for a ``QuestionForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AnswerRecord(abc_assessment_records.AnswerRecord, osid_records.OsidRecord):
    """A record for an ``Answer``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AnswerQueryRecord(abc_assessment_records.AnswerQueryRecord, osid_records.OsidRecord):
    """A record for an ``AnswerQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AnswerFormRecord(abc_assessment_records.AnswerFormRecord, osid_records.OsidRecord):
    """A record for an ``AnswerForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ItemRecord(abc_assessment_records.ItemRecord, osid_records.OsidRecord):
    """A record for an ``Item``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ItemQueryRecord(abc_assessment_records.ItemQueryRecord, osid_records.OsidRecord):
    """A record for an ``ItemQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ItemFormRecord(abc_assessment_records.ItemFormRecord, osid_records.OsidRecord):
    """A record for an ``ItemForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ItemSearchRecord(abc_assessment_records.ItemSearchRecord, osid_records.OsidRecord):
    """A record for an ``ItemSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentRecord(abc_assessment_records.AssessmentRecord, osid_records.OsidRecord):
    """A record for an ``Assessment``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentQueryRecord(abc_assessment_records.AssessmentQueryRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentFormRecord(abc_assessment_records.AssessmentFormRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentSearchRecord(abc_assessment_records.AssessmentSearchRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentOfferedRecord(abc_assessment_records.AssessmentOfferedRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentOffered``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentOfferedQueryRecord(abc_assessment_records.AssessmentOfferedQueryRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentOfferedQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentOfferedFormRecord(abc_assessment_records.AssessmentOfferedFormRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentOfferedForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentOfferedSearchRecord(abc_assessment_records.AssessmentOfferedSearchRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentOfferedSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentTakenRecord(abc_assessment_records.AssessmentTakenRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentTaken``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentTakenQueryRecord(abc_assessment_records.AssessmentTakenQueryRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentTakenQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentTakenFormRecord(abc_assessment_records.AssessmentTakenFormRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentTakenForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentTakenSearchRecord(abc_assessment_records.AssessmentTakenSearchRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentTakenSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentSectionRecord(abc_assessment_records.AssessmentSectionRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentSection``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BankRecord(abc_assessment_records.BankRecord, osid_records.OsidRecord):
    """A record for a ``Bank``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BankQueryRecord(abc_assessment_records.BankQueryRecord, osid_records.OsidRecord):
    """A record for a ``BankQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BankFormRecord(abc_assessment_records.BankFormRecord, osid_records.OsidRecord):
    """A record for a ``BankForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class BankSearchRecord(abc_assessment_records.BankSearchRecord, osid_records.OsidRecord):
    """A record for a ``BankSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class ResponseRecord(abc_assessment_records.ResponseRecord, osid_records.OsidRecord):
    """A record for a ``Response``.

    The methods specified by the record type are available through the
    underlying object.

    """





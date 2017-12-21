"""GStudio implementations of assessment.authoring records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.assessment_authoring import records as abc_assessment_authoring_records
from ..osid import records as osid_records




class AssessmentPartRecord(abc_assessment_authoring_records.AssessmentPartRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentPart``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentPartQueryRecord(abc_assessment_authoring_records.AssessmentPartQueryRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentPartQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentPartFormRecord(abc_assessment_authoring_records.AssessmentPartFormRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentPartForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class AssessmentPartSearchRecord(abc_assessment_authoring_records.AssessmentPartSearchRecord, osid_records.OsidRecord):
    """A record for an ``AssessmentPartSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """




class SequenceRuleRecord(abc_assessment_authoring_records.SequenceRuleRecord, osid_records.OsidRecord):
    """A record for a ``SequenceRule``.

    The methods specified by the record type are available through the
    underlying object.

    """




class SequenceRuleQueryRecord(abc_assessment_authoring_records.SequenceRuleQueryRecord, osid_records.OsidRecord):
    """A record for a ``SequenceRuleQuery``.

    The methods specified by the record type are available through the
    underlying object.

    """




class SequenceRuleFormRecord(abc_assessment_authoring_records.SequenceRuleFormRecord, osid_records.OsidRecord):
    """A record for a ``SequenceRuleForm``.

    The methods specified by the record type are available through the
    underlying object.

    """




class SequenceRuleSearchRecord(abc_assessment_authoring_records.SequenceRuleSearchRecord, osid_records.OsidRecord):
    """A record for a ``SequenceRuleSearch``.

    The methods specified by the record type are available through the
    underlying object.

    """





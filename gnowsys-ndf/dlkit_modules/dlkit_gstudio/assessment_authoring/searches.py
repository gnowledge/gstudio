"""GStudio implementations of assessment.authoring searches."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.assessment_authoring import searches as abc_assessment_authoring_searches
from ..osid import searches as osid_searches




class AssessmentPartSearch(abc_assessment_authoring_searches.AssessmentPartSearch, osid_searches.OsidSearch):
    """The search interface for governing assessment part searches."""

    @utilities.arguments_not_none
    def search_among_assessment_parts(self, bank_ids):
        """Execute this search among the given list of assessment parts.

        arg:    bank_ids (osid.id.IdList): list of assessment parts
        raise:  NullArgument - ``bank_ids`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_assessment_part_results(self, assessment_part_search_order):
        """Specify an ordering to the search results.

        arg:    assessment_part_search_order
                (osid.assessment.authoring.AssessmentPartSearchOrder):
                assessment part search order
        raise:  NullArgument - ``assessment_part_search_order`` is
                ``null``
        raise:  Unsupported - ``assessment_part_search_order`` is not of
                this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assessment_part_search_record(self, assessment_part_search_record_type):
        """Gets the assessment part search record corresponding to the given assessment part search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    assessment_part_search_record_type (osid.type.Type): an
                assessment part search record type
        return:
                (osid.assessment.authoring.records.AssessmentPartSearchR
                ecord) - the assessment part search record
        raise:  NullArgument - ``assessment_part_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_part_search_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentPartSearchResults(abc_assessment_authoring_searches.AssessmentPartSearchResults, osid_searches.OsidSearchResults):
    """This interface provides a means to capture results of a search."""

    def get_assessment_parts(self):
        """Gets the ``AssessmentPartList`` resulting from a search.

        return: (osid.assessment.authoring.AssessmentPartList) - the
                assessment part list
        raise:  IllegalState - list has already been retrieved
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_parts = property(fget=get_assessment_parts)

    def get_assessment_part_query_inspector(self):
        """Gets the inspector for the query to examine the terms used in the search.

        return: (osid.assessment.authoring.AssessmentPartQueryInspector)
                - the assessment part query inspector
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_part_query_inspector = property(fget=get_assessment_part_query_inspector)

    @utilities.arguments_not_none
    def get_assessment_part_search_results_record(self, assessment_part_search_record_type):
        """Gets the assessment part search results record corresponding to the given assessment part search record ``Type``.

        This method must be used to retrieve an object implementing the
        requested record.

        arg:    assessment_part_search_record_type (osid.type.Type): an
                assessment part search record type
        return: (osid.assessment.authoring.records.AssessmentPartSearchR
                esultsRecord) - the assessment part search results
                record
        raise:  NullArgument - ``assessment_part_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unsupported -
                ``has_record_type(assessment_part_search_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class SequenceRuleSearch(abc_assessment_authoring_searches.SequenceRuleSearch, osid_searches.OsidSearch):
    """The search interface for governing sequence rule searches."""

    @utilities.arguments_not_none
    def search_among_sequence_rules(self, bank_ids):
        """Execute this search among the given list of sequence rules.

        arg:    bank_ids (osid.id.IdList): list of sequence rules
        raise:  NullArgument - ``bank_ids`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_sequence_rule_results(self, sequence_rule_search_order):
        """Specify an ordering to the search results.

        arg:    sequence_rule_search_order
                (osid.assessment.authoring.SequenceRuleSearchOrder):
                sequence rule search order
        raise:  NullArgument - ``sequence_rule_search_order`` is
                ``null``
        raise:  Unsupported - ``sequence_rule_search_order`` is not of
                this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_sequence_rule_search_record(self, sequence_rule_search_record_type):
        """Gets the sequence rule search record corresponding to the given sequence rule search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    sequence_rule_search_record_type (osid.type.Type): a
                sequence rule search record type
        return:
                (osid.assessment.authoring.records.SequenceRuleSearchRec
                ord) - the sequence rule search record
        raise:  NullArgument - ``sequence_rule_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(sequence_rule_search_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class SequenceRuleSearchResults(abc_assessment_authoring_searches.SequenceRuleSearchResults, osid_searches.OsidSearchResults):
    """This interface provides a means to capture results of a search."""

    def get_sequence_rules(self):
        """Gets the ``SequenceRuleList`` resulting from a search.

        return: (osid.assessment.authoring.SequenceRuleList) - the
                sequence rule list
        raise:  IllegalState - list has already been retrieved
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    sequence_rules = property(fget=get_sequence_rules)

    def get_sequence_rule_query_inspector(self):
        """Gets the inspector for the query to examine the terms used in the search.

        return: (osid.assessment.authoring.SequenceRuleQueryInspector) -
                the sequence rule query inspector
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    sequence_rule_query_inspector = property(fget=get_sequence_rule_query_inspector)

    @utilities.arguments_not_none
    def get_sequence_rule_search_results_record(self, sequence_rule_search_record_type):
        """Gets the sequence rule search results record corresponding to the given sequence rule search record ``Type``.

        This method must be used to retrieve an object implementing the
        requested record.

        arg:    sequence_rule_search_record_type (osid.type.Type): a
                sequence rule search record type
        return: (osid.assessment.authoring.records.SequenceRuleSearchRes
                ultsRecord) - the sequence rule search results record
        raise:  NullArgument - ``sequence_rule_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unsupported -
                ``has_record_type(sequence_rule_search_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



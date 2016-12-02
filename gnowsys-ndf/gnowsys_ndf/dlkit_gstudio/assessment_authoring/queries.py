"""GStudio implementations of assessment.authoring queries."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.assessment_authoring import queries as abc_assessment_authoring_queries
from ..osid import queries as osid_queries
from ..primitives import Id
from ..utilities import get_registry
from dlkit.abstract_osid.osid import errors




class AssessmentPartQuery(abc_assessment_authoring_queries.AssessmentPartQuery, osid_queries.OsidObjectQuery, osid_queries.OsidContainableQuery, osid_queries.OsidOperableQuery):
    """This is the query for searching assessment parts.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'assessment_authoring.AssessmentPart'
        self._runtime = runtime
        record_type_data_sets = get_registry('ASSESSMENT_PART_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def match_assessment_id(self, assessment_id, match):
        """Sets the assessment ``Id`` for this query.

        arg:    assessment_id (osid.id.Id): an assessment ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_id_terms(self):
        """Clears all assessment ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_id_terms = property(fdel=clear_assessment_id_terms)

    def supports_assessment_query(self):
        """Tests if an ``AssessmentQuery`` is available.

        return: (boolean) - ``true`` if an assessment query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_assessment_query(self):
        """Gets the query for an assessment.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.AssessmentQuery) - the assessment query
        raise:  Unimplemented - ``supports_assessment_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    assessment_query = property(fget=get_assessment_query)

    def clear_assessment_terms(self):
        """Clears all assessment terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_terms = property(fdel=clear_assessment_terms)

    @utilities.arguments_not_none
    def match_parent_assessment_part_id(self, assessment_part_id, match):
        """Sets the assessment part ``Id`` for this query.

        arg:    assessment_part_id (osid.id.Id): an assessment part
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_part_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_parent_assessment_part_id_terms(self):
        """Clears all assessment part ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    parent_assessment_part_id_terms = property(fdel=clear_parent_assessment_part_id_terms)

    def supports_parent_assessment_part_query(self):
        """Tests if an ``AssessmentPartQuery`` is available.

        return: (boolean) - ``true`` if an assessment part query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_parent_assessment_part_query(self):
        """Gets the query for an assessment part.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.authoring.AssessmentPartQuery) - the
                assessment part query
        raise:  Unimplemented -
                ``supports_parent_assessment_part_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_parent_assessment_part_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    parent_assessment_part_query = property(fget=get_parent_assessment_part_query)

    @utilities.arguments_not_none
    def match_any_parent_assessment_part(self, match):
        """Matches assessment parts with any parent assessment part.

        arg:    match (boolean): ``true`` to match assessment parts with
                any parent, ``false`` to match assessment parts with no
                parents
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_parent_assessment_part_terms(self):
        """Clears all assessment part terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    parent_assessment_part_terms = property(fdel=clear_parent_assessment_part_terms)

    @utilities.arguments_not_none
    def match_section(self, match):
        """Matches assessment parts that are also used as sections.

        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_section_terms(self):
        """Clears all section terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    section_terms = property(fdel=clear_section_terms)

    @utilities.arguments_not_none
    def match_weight(self, low, high, match):
        """Matches assessment parts that fall in between the given weights inclusive.

        arg:    low (cardinal): low end of range
        arg:    high (cardinal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``high`` is less than ``low``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_weight(self, match):
        """Matches assessment parts with any weight assigned.

        arg:    match (boolean): ``true`` to match assessment parts with
                any wieght, ``false`` to match assessment parts with no
                weight
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_weight_terms(self):
        """Clears all weight terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    weight_terms = property(fdel=clear_weight_terms)

    @utilities.arguments_not_none
    def match_allocated_time(self, low, high, match):
        """Matches assessment parts hose allocated time falls in between the given times inclusive.

        arg:    low (osid.calendaring.Duration): low end of range
        arg:    high (osid.calendaring.Duration): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``high`` is less than ``low``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_allocated_time(self, match):
        """Matches assessment parts with any time assigned.

        arg:    match (boolean): ``true`` to match assessment parts with
                any alloocated time, ``false`` to match assessment parts
                with no allocated time
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_allocated_time_terms(self):
        """Clears all allocated time terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    allocated_time_terms = property(fdel=clear_allocated_time_terms)

    @utilities.arguments_not_none
    def match_child_assessment_part_id(self, assessment_part_id, match):
        """Sets the assessment part ``Id`` for this query.

        arg:    assessment_part_id (osid.id.Id): an assessment part
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_part_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_child_assessment_part_id_terms(self):
        """Clears all assessment part ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    child_assessment_part_id_terms = property(fdel=clear_child_assessment_part_id_terms)

    def supports_child_assessment_part_query(self):
        """Tests if an ``AssessmentPartQuery`` is available.

        return: (boolean) - ``true`` if an assessment part query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_child_assessment_part_query(self):
        """Gets the query for an assessment part.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.authoring.AssessmentPartQuery) - the
                assessment part query
        raise:  Unimplemented -
                ``supports_child_assessment_part_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_child_assessment_part_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    child_assessment_part_query = property(fget=get_child_assessment_part_query)

    @utilities.arguments_not_none
    def match_any_child_assessment_part(self, match):
        """Matches assessment parts with any child assessment part.

        arg:    match (boolean): ``true`` to match assessment parts with
                any children, ``false`` to match assessment parts with
                no children
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_child_assessment_part_terms(self):
        """Clears all assessment part terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    child_assessment_part_terms = property(fdel=clear_child_assessment_part_terms)

    @utilities.arguments_not_none
    def match_bank_id(self, bank_id, match):
        """Matches constrainers mapped to the bank.

        arg:    bank_id (osid.id.Id): the bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_bank_id_terms(self):
        """Clears the bank ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id_terms = property(fdel=clear_bank_id_terms)

    def supports_bank_query(self):
        """Tests if an ``BankQuery`` is available.

        return: (boolean) - ``true`` if a bank query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_bank_query(self):
        """Gets the query for a bank.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.BankQuery) - the bank query
        raise:  Unimplemented - ``supports_bank_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    bank_query = property(fget=get_bank_query)

    def clear_bank_terms(self):
        """Clears the bank query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_terms = property(fdel=clear_bank_terms)

    @utilities.arguments_not_none
    def get_assessment_part_query_record(self, assessment_part_record_type):
        """Gets the assessment part query record corresponding to the given ``AssessmentPart`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    assessment_part_record_type (osid.type.Type): an
                assessment part record type
        return:
                (osid.assessment.authoring.records.AssessmentPartQueryRe
                cord) - the assessment part query record
        raise:  NullArgument - ``assessment_part_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_part_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class SequenceRuleQuery(abc_assessment_authoring_queries.SequenceRuleQuery, osid_queries.OsidRuleQuery):
    """This is the query for searching sequence rules.

    Each method match specifies a ``AND`` term while multiple
    invocations of the same method produce a nested ``OR``.

    """

    @utilities.arguments_not_none
    def match_assessment_part_id(self, assessment_part_id, match):
        """Sets the assessment part ``Id`` for this query.

        arg:    assessment_part_id (osid.id.Id): an assessment part
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_part_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_part_id_terms(self):
        """Clears all assessment part ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_part_id_terms = property(fdel=clear_assessment_part_id_terms)

    def supports_assessment_part_query(self):
        """Tests if an ``AssessmentPartQuery`` is available.

        return: (boolean) - ``true`` if an assessment part query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_assessment_part_query(self):
        """Gets the query for an assessment part.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.authoring.AssessmentPartQuery) - the
                assessment part query
        raise:  Unimplemented - ``supports_assessment_part_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_part_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    assessment_part_query = property(fget=get_assessment_part_query)

    def clear_assessment_part_terms(self):
        """Clears all assessment part terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_part_terms = property(fdel=clear_assessment_part_terms)

    @utilities.arguments_not_none
    def match_next_assessment_part_id(self, assessment_part_id, match):
        """Sets the assessment part ``Id`` for this query.

        arg:    assessment_part_id (osid.id.Id): an assessment part
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_part_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_next_assessment_part_id_terms(self):
        """Clears all assessment part ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    next_assessment_part_id_terms = property(fdel=clear_next_assessment_part_id_terms)

    def supports_next_assessment_part_query(self):
        """Tests if an ``AssessmentPartQuery`` is available.

        return: (boolean) - ``true`` if an assessment part query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_next_assessment_part_query(self):
        """Gets the query for an assessment part.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.authoring.AssessmentPartQuery) - the
                assessment part query
        raise:  Unimplemented -
                ``supports_next_assessment_part_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_next_assessment_part_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    next_assessment_part_query = property(fget=get_next_assessment_part_query)

    def clear_next_assessment_part_terms(self):
        """Clears all assessment part terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    next_assessment_part_terms = property(fdel=clear_next_assessment_part_terms)

    @utilities.arguments_not_none
    def match_minimum_score(self, low, high, match):
        """Matches minimum scores that fall in between the given scores inclusive.

        arg:    low (cardinal): low end of range
        arg:    high (cardinal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``high`` is less than ``low``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_minimum_score(self, match):
        """Matches assessment parts with any minimum score assigned.

        arg:    match (boolean): ``true`` to match assessment parts with
                any minimum score, ``false`` to match assessment parts
                with no minimum score
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_minimum_score_terms(self):
        """Clears all minimum score terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    minimum_score_terms = property(fdel=clear_minimum_score_terms)

    @utilities.arguments_not_none
    def match_maximum_score(self, low, high, match):
        """Matches maximum scores that fall in between the given scores inclusive.

        arg:    low (cardinal): low end of range
        arg:    high (cardinal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``high`` is less than ``low``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_maximum_score(self, match):
        """Matches assessment parts with any maximum score assigned.

        arg:    match (boolean): ``true`` to match assessment parts with
                any maximum score, ``false`` to match assessment parts
                with no maximum score
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_maximum_score_terms(self):
        """Clears all maximum score terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    maximum_score_terms = property(fdel=clear_maximum_score_terms)

    @utilities.arguments_not_none
    def match_cumulative(self, match):
        """Matches cumulative rules.

        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_cumulative_terms(self):
        """Clears all cumulative terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cumulative_terms = property(fdel=clear_cumulative_terms)

    @utilities.arguments_not_none
    def match_applied_assessment_part_id(self, assessment_part_id, match):
        """Sets the assessment part ``Id`` for this query.

        arg:    assessment_part_id (osid.id.Id): an assessment part
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_part_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_applied_assessment_part_id_terms(self):
        """Clears all assessment part ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    applied_assessment_part_id_terms = property(fdel=clear_applied_assessment_part_id_terms)

    def supports_applied_assessment_part_query(self):
        """Tests if an ``AssessmentPartQuery`` is available.

        return: (boolean) - ``true`` if an assessment part query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_applied_assessment_part_query(self):
        """Gets the query for an assessment part.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.authoring.AssessmentPartQuery) - the
                assessment part query
        raise:  Unimplemented -
                ``supports_applied_assessment_part_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_applied_assessment_part_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    applied_assessment_part_query = property(fget=get_applied_assessment_part_query)

    @utilities.arguments_not_none
    def match_any_applied_assessment_part(self, match):
        """Matches assessment parts with any applied assessment part.

        arg:    match (boolean): ``true`` to match assessment parts with
                any applied assessment part, ``false`` to match
                assessment parts with no applied assessment parts
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_applied_assessment_part_terms(self):
        """Clears all assessment part terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    applied_assessment_part_terms = property(fdel=clear_applied_assessment_part_terms)

    @utilities.arguments_not_none
    def match_bank_id(self, bank_id, match):
        """Matches constrainers mapped to the bank.

        arg:    bank_id (osid.id.Id): the bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_bank_id_terms(self):
        """Clears the bank ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id_terms = property(fdel=clear_bank_id_terms)

    def supports_bank_query(self):
        """Tests if an ``BankQuery`` is available.

        return: (boolean) - ``true`` if a bank query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_bank_query(self):
        """Gets the query for a bank.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.BankQuery) - the bank query
        raise:  Unimplemented - ``supports_bank_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    bank_query = property(fget=get_bank_query)

    def clear_bank_terms(self):
        """Clears the bank query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_terms = property(fdel=clear_bank_terms)

    @utilities.arguments_not_none
    def get_sequence_rule_query_record(self, sequence_rule_record_type):
        """Gets the sequence rule query record corresponding to the given ``SequenceRule`` record ``Type``.

        Multiple record retrievals produce a nested ``OR`` term.

        arg:    sequence_rule_record_type (osid.type.Type): a sequence
                rule record type
        return:
                (osid.assessment.authoring.records.SequenceRuleQueryReco
                rd) - the sequence rule query record
        raise:  NullArgument - ``sequence_rule_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(sequence_rule_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



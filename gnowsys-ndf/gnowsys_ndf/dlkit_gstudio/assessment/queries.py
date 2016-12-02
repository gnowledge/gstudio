"""GStudio implementations of assessment queries."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.assessment import queries as abc_assessment_queries
from ..id.objects import IdList
from ..osid import queries as osid_queries
from ..primitives import Id
from ..utilities import get_registry
from dlkit.abstract_osid.osid import errors




class QuestionQuery(abc_assessment_queries.QuestionQuery, osid_queries.OsidObjectQuery):
    """This is the query for searching questions.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'assessment.Question'
        self._runtime = runtime
        record_type_data_sets = get_registry('QUESTION_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def get_question_query_record(self, question_record_type):
        """Gets the question record query corresponding to the given ``Item`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    question_record_type (osid.type.Type): a question record
                type
        return: (osid.assessment.records.QuestionQueryRecord) - the
                question query record
        raise:  NullArgument - ``question_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(question_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AnswerQuery(abc_assessment_queries.AnswerQuery, osid_queries.OsidObjectQuery):
    """This is the query for searching answers.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'assessment.Answer'
        self._runtime = runtime
        record_type_data_sets = get_registry('ANSWER_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def get_answer_query_record(self, answer_record_type):
        """Gets the answer record query corresponding to the given ``Answer`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    answer_record_type (osid.type.Type): an answer record
                type
        return: (osid.assessment.records.AnswerQueryRecord) - the answer
                query record
        raise:  NullArgument - ``answer_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(answer_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ItemQuery(abc_assessment_queries.ItemQuery, osid_queries.OsidObjectQuery, osid_queries.OsidAggregateableQuery):
    """This is the query for searching items.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'assessment.Item'
        self._runtime = runtime
        record_type_data_sets = get_registry('ITEM_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def match_learning_objective_id(self, objective_id, match):
        """Sets the learning objective ``Id`` for this query.

        arg:    objective_id (osid.id.Id): a learning objective ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  NullArgument - ``objective_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_learning_objective_id_terms(self):
        """Clears all learning objective ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    learning_objective_id_terms = property(fdel=clear_learning_objective_id_terms)

    def supports_learning_objective_query(self):
        """Tests if an ``ObjectiveQuery`` is available.

        return: (boolean) - ``true`` if a learning objective query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_learning_objective_query(self):
        """Gets the query for a learning objective.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveQuery) - the learning objective
                query
        raise:  Unimplemented - ``supports_learning_objective_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_learning_objective_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    learning_objective_query = property(fget=get_learning_objective_query)

    @utilities.arguments_not_none
    def match_any_learning_objective(self, match):
        """Matches an item with any objective.

        arg:    match (boolean): ``true`` to match items with any
                learning objective, ``false`` to match items with no
                learning objectives
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_learning_objective_terms(self):
        """Clears all learning objective terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    learning_objective_terms = property(fdel=clear_learning_objective_terms)

    @utilities.arguments_not_none
    def match_question_id(self, question_id, match):
        """Sets the question ``Id`` for this query.

        arg:    question_id (osid.id.Id): a question ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``question_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_question_id_terms(self):
        """Clears all question ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    question_id_terms = property(fdel=clear_question_id_terms)

    def supports_question_query(self):
        """Tests if a ``QuestionQuery`` is available.

        return: (boolean) - ``true`` if a question query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_question_query(self):
        """Gets the query for a question.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.QuestionQuery) - the question query
        raise:  Unimplemented - ``supports_question_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_learning_objective_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    question_query = property(fget=get_question_query)

    @utilities.arguments_not_none
    def match_any_question(self, match):
        """Matches an item with any question.

        arg:    match (boolean): ``true`` to match items with any
                question, ``false`` to match items with no questions
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_question_terms(self):
        """Clears all question terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    question_terms = property(fdel=clear_question_terms)

    @utilities.arguments_not_none
    def match_answer_id(self, answer_id, match):
        """Sets the answer ``Id`` for this query.

        arg:    answer_id (osid.id.Id): an answer ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``answer_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_answer_id_terms(self):
        """Clears all answer ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    answer_id_terms = property(fdel=clear_answer_id_terms)

    def supports_answer_query(self):
        """Tests if an ``AnswerQuery`` is available.

        return: (boolean) - ``true`` if an answer query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_answer_query(self):
        """Gets the query for an answer.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.AnswerQuery) - the answer query
        raise:  Unimplemented - ``supports_answer_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_learning_objective_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    answer_query = property(fget=get_answer_query)

    @utilities.arguments_not_none
    def match_any_answer(self, match):
        """Matches an item with any answer.

        arg:    match (boolean): ``true`` to match items with any
                answer, ``false`` to match items with no answers
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_answer_terms(self):
        """Clears all answer terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    answer_terms = property(fdel=clear_answer_terms)

    @utilities.arguments_not_none
    def match_assessment_id(self, assessment_id, match):
        """Sets the assessment ``Id`` for this query.

        arg:    assessment_id (osid.id.Id): an assessment ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
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

    @utilities.arguments_not_none
    def match_any_assessment(self, match):
        """Matches an item with any assessment.

        arg:    match (boolean): ``true`` to match items with any
                assessment, ``false`` to match items with no assessments
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_terms(self):
        """Clears all assessment terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_terms = property(fdel=clear_assessment_terms)

    @utilities.arguments_not_none
    def match_bank_id(self, bank_id, match):
        """Sets the bank ``Id`` for this query.

        arg:    bank_id (osid.id.Id): a bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  NullArgument - ``bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_bank_id_terms(self):
        """Clears all bank ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id_terms = property(fdel=clear_bank_id_terms)

    def supports_bank_query(self):
        """Tests if a ``BankQuery`` is available.

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
        """Clears all bank terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_terms = property(fdel=clear_bank_terms)

    @utilities.arguments_not_none
    def get_item_query_record(self, item_record_type):
        """Gets the item record query corresponding to the given ``Item`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    item_record_type (osid.type.Type): an item record type
        return: (osid.assessment.records.ItemQueryRecord) - the item
                query record
        raise:  NullArgument - ``item_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(item_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentQuery(abc_assessment_queries.AssessmentQuery, osid_queries.OsidObjectQuery):
    """This is the query for searching assessments.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'assessment.Assessment'
        self._runtime = runtime
        record_type_data_sets = get_registry('ASSESSMENT_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def match_level_id(self, grade_id, match):
        """Sets the level grade ``Id`` for this query.

        arg:    grade_id (osid.id.Id): a grade ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_level_id_terms(self):
        """Clears all level ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    level_id_terms = property(fdel=clear_level_id_terms)

    def supports_level_query(self):
        """Tests if a ``GradeQuery`` is available.

        return: (boolean) - ``true`` if a grade query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_level_query(self):
        """Gets the query for a grade.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeQuery) - the grade query
        raise:  Unimplemented - ``supports_level_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_level_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    level_query = property(fget=get_level_query)

    @utilities.arguments_not_none
    def match_any_level(self, match):
        """Matches an assessment that has any level assigned.

        arg:    match (boolean): ``true`` to match assessments with any
                level, ``false`` to match assessments with no level
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_level_terms(self):
        """Clears all level terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    level_terms = property(fdel=clear_level_terms)

    @utilities.arguments_not_none
    def match_rubric_id(self, assessment_id, match):
        """Sets the rubric assessment ``Id`` for this query.

        arg:    assessment_id (osid.id.Id): an assessment ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_rubric_id_terms(self):
        """Clears all rubric assessment ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric_id_terms = property(fdel=clear_rubric_id_terms)

    def supports_rubric_query(self):
        """Tests if an ``AssessmentQuery`` is available.

        return: (boolean) - ``true`` if a rubric assessment query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_rubric_query(self):
        """Gets the query for a rubric assessment.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.AssessmentQuery) - the assessment query
        raise:  Unimplemented - ``supports_rubric_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_rubric_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    rubric_query = property(fget=get_rubric_query)

    @utilities.arguments_not_none
    def match_any_rubric(self, match):
        """Matches an assessment that has any rubric assessment assigned.

        arg:    match (boolean): ``true`` to match assessments with any
                rubric, ``false`` to match assessments with no rubric
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_rubric_terms(self):
        """Clears all rubric assessment terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric_terms = property(fdel=clear_rubric_terms)

    @utilities.arguments_not_none
    def match_item_id(self, item_id, match):
        """Sets the item ``Id`` for this query.

        arg:    item_id (osid.id.Id): an item ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``item_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_item_id_terms(self):
        """Clears all item ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    item_id_terms = property(fdel=clear_item_id_terms)

    def supports_item_query(self):
        """Tests if an ``ItemQuery`` is available.

        return: (boolean) - ``true`` if an item query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_item_query(self):
        """Gets the query for an item.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.ItemQuery) - the item query
        raise:  Unimplemented - ``supports_item_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    item_query = property(fget=get_item_query)

    @utilities.arguments_not_none
    def match_any_item(self, match):
        """Matches an assessment that has any item.

        arg:    match (boolean): ``true`` to match assessments with any
                item, ``false`` to match assessments with no items
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_item_terms(self):
        """Clears all item terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    item_terms = property(fdel=clear_item_terms)

    @utilities.arguments_not_none
    def match_assessment_offered_id(self, assessment_offered_id, match):
        """Sets the assessment offered ``Id`` for this query.

        arg:    assessment_offered_id (osid.id.Id): an assessment
                offered ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_offered_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_offered_id_terms(self):
        """Clears all assessment offered ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_offered_id_terms = property(fdel=clear_assessment_offered_id_terms)

    def supports_assessment_offered_query(self):
        """Tests if an ``AssessmentOfferedQuery`` is available.

        return: (boolean) - ``true`` if an assessment offered query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_assessment_offered_query(self):
        """Gets the query for an assessment offered.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.AssessmentOfferedQuery) - the
                assessment offered query
        raise:  Unimplemented - ``supports_assessment_offered_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    assessment_offered_query = property(fget=get_assessment_offered_query)

    @utilities.arguments_not_none
    def match_any_assessment_offered(self, match):
        """Matches an assessment that has any offering.

        arg:    match (boolean): ``true`` to match assessments with any
                offering, ``false`` to match assessments with no
                offerings
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_offered_terms(self):
        """Clears all assessment offered terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_offered_terms = property(fdel=clear_assessment_offered_terms)

    @utilities.arguments_not_none
    def match_assessment_taken_id(self, assessment_taken_id, match):
        """Sets the assessment taken ``Id`` for this query.

        arg:    assessment_taken_id (osid.id.Id): an assessment taken
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_taken_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_taken_id_terms(self):
        """Clears all assessment taken ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_taken_id_terms = property(fdel=clear_assessment_taken_id_terms)

    def supports_assessment_taken_query(self):
        """Tests if an ``AssessmentTakenQuery`` is available.

        return: (boolean) - ``true`` if an assessment taken query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_assessment_taken_query(self):
        """Gets the query for an assessment taken.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.AssessmentTakenQuery) - the assessment
                taken query
        raise:  Unimplemented - ``supports_assessment_taken_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    assessment_taken_query = property(fget=get_assessment_taken_query)

    @utilities.arguments_not_none
    def match_any_assessment_taken(self, match):
        """Matches an assessment that has any taken version.

        arg:    match (boolean): ``true`` to match assessments with any
                taken assessments, ``false`` to match assessments with
                no taken assessments
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_taken_terms(self):
        """Clears all assessment taken terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_taken_terms = property(fdel=clear_assessment_taken_terms)

    @utilities.arguments_not_none
    def match_bank_id(self, bank_id, match):
        """Sets the bank ``Id`` for this query.

        arg:    bank_id (osid.id.Id): a bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_bank_id_terms(self):
        """Clears all bank ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id_terms = property(fdel=clear_bank_id_terms)

    def supports_bank_query(self):
        """Tests if a ``BankQuery`` is available.

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
        """Clears all bank terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_terms = property(fdel=clear_bank_terms)

    @utilities.arguments_not_none
    def get_assessment_query_record(self, assessment_record_type):
        """Gets the assessment query record corresponding to the given ``Assessment`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    assessment_record_type (osid.type.Type): an assessment
                record type
        return: (osid.assessment.records.AssessmentQueryRecord) - the
                assessment query record
        raise:  NullArgument - ``assessment_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_record_type)`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentOfferedQuery(abc_assessment_queries.AssessmentOfferedQuery, osid_queries.OsidObjectQuery, osid_queries.OsidSubjugateableQuery):
    """This is the query for searching assessments.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'assessment.AssessmentOffered'
        self._runtime = runtime
        record_type_data_sets = get_registry('ASSESSMENT_OFFERED_RECORD_TYPES', runtime)
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
    def match_level_id(self, grade_id, match):
        """Sets the level grade ``Id`` for this query.

        arg:    grade_id (osid.id.Id): a grade ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_level_id_terms(self):
        """Clears all level ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    level_id_terms = property(fdel=clear_level_id_terms)

    def supports_level_query(self):
        """Tests if a ``GradeQuery`` is available.

        return: (boolean) - ``true`` if a grade query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_level_query(self):
        """Gets the query for a grade.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeQuery) - the grade query
        raise:  Unimplemented - ``supports_level_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_level_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    level_query = property(fget=get_level_query)

    @utilities.arguments_not_none
    def match_any_level(self, match):
        """Matches an assessment offered that has any level assigned.

        arg:    match (boolean): ``true`` to match offerings with any
                level, ``false`` to match offerings with no levsls
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_level_terms(self):
        """Clears all level terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    level_terms = property(fdel=clear_level_terms)

    @utilities.arguments_not_none
    def match_items_sequential(self, match):
        """Match sequential assessments.

        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_items_sequential_terms(self):
        """Clears all sequential terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    items_sequential_terms = property(fdel=clear_items_sequential_terms)

    @utilities.arguments_not_none
    def match_items_shuffled(self, match):
        """Match shuffled item assessments.

        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_items_shuffled_terms(self):
        """Clears all shuffled terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    items_shuffled_terms = property(fdel=clear_items_shuffled_terms)

    @utilities.arguments_not_none
    def match_start_time(self, start, end, match):
        """Matches assessments whose start time falls between the specified range inclusive.

        arg:    start (osid.calendaring.DateTime): start of range
        arg:    end (osid.calendaring.DateTime): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``end`` is less than ``start``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_start_time(self, match):
        """Matches offerings that has any start time assigned.

        arg:    match (boolean): ``true`` to match offerings with any
                start time, ``false`` to match offerings with no start
                time
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_start_time_terms(self):
        """Clears all scheduled terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    start_time_terms = property(fdel=clear_start_time_terms)

    @utilities.arguments_not_none
    def match_deadline(self, start, end, match):
        """Matches assessments whose end time falls between the specified range inclusive.

        arg:    start (osid.calendaring.DateTime): start of range
        arg:    end (osid.calendaring.DateTime): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``end`` is less than ``start``
        raise:  NullArgument - ``start`` or ``end`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_deadline(self, match):
        """Matches offerings that have any deadline assigned.

        arg:    match (boolean): ``true`` to match offerings with any
                deadline, ``false`` to match offerings with no deadline
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_deadline_terms(self):
        """Clears all deadline terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    deadline_terms = property(fdel=clear_deadline_terms)

    @utilities.arguments_not_none
    def match_duration(self, low, high, match):
        """Matches assessments whose duration falls between the specified range inclusive.

        arg:    low (osid.calendaring.Duration): start range of duration
        arg:    high (osid.calendaring.Duration): end range of duration
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``end`` is less than ``start``
        raise:  NullArgument - ``start`` or ``end`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_duration(self, match):
        """Matches offerings that have any duration assigned.

        arg:    match (boolean): ``true`` to match offerings with any
                duration, ``false`` to match offerings with no duration
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_duration_terms(self):
        """Clears all duration terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    duration_terms = property(fdel=clear_duration_terms)

    @utilities.arguments_not_none
    def match_score_system_id(self, grade_system_id, match):
        """Sets the grade system ``Id`` for this query.

        arg:    grade_system_id (osid.id.Id): a grade system ``Id``
        arg:    match (boolean): ``true for a positive match, false for
                a negative match``
        raise:  NullArgument - ``grade_system_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_score_system_id_terms(self):
        """Clears all grade system ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score_system_id_terms = property(fdel=clear_score_system_id_terms)

    def supports_score_system_query(self):
        """Tests if a ``GradeSystemQuery`` is available.

        return: (boolean) - ``true`` if a grade system query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_score_system_query(self):
        """Gets the query for a grade system.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeSystemQuery) - the grade system query
        raise:  Unimplemented - ``supports_score_system_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_score_system_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    score_system_query = property(fget=get_score_system_query)

    @utilities.arguments_not_none
    def match_any_score_system(self, match):
        """Matches taken assessments that have any grade system assigned.

        arg:    match (boolean): ``true`` to match assessments with any
                grade system, ``false`` to match assessments with no
                grade system
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_score_system_terms(self):
        """Clears all grade system terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score_system_terms = property(fdel=clear_score_system_terms)

    @utilities.arguments_not_none
    def match_grade_system_id(self, grade_system_id, match):
        """Sets the grade system ``Id`` for this query.

        arg:    grade_system_id (osid.id.Id): a grade system ``Id``
        arg:    match (boolean): ``true for a positive match, false for
                a negative match``
        raise:  NullArgument - ``grade_system_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_system_id_terms(self):
        """Clears all grade system ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system_id_terms = property(fdel=clear_grade_system_id_terms)

    def supports_grade_system_query(self):
        """Tests if a ``GradeSystemQuery`` is available.

        return: (boolean) - ``true`` if a grade system query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grade_system_query(self):
        """Gets the query for a grade system.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeSystemQuery) - the grade system query
        raise:  Unimplemented - ``supports_score_system_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_score_system_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    grade_system_query = property(fget=get_grade_system_query)

    @utilities.arguments_not_none
    def match_any_grade_system(self, match):
        """Matches taken assessments that have any grade system assigned.

        arg:    match (boolean): ``true`` to match assessments with any
                grade system, ``false`` to match assessments with no
                grade system
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_system_terms(self):
        """Clears all grade system terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system_terms = property(fdel=clear_grade_system_terms)

    @utilities.arguments_not_none
    def match_rubric_id(self, assessment_offered_id, match):
        """Sets the rubric assessment offered ``Id`` for this query.

        arg:    assessment_offered_id (osid.id.Id): an assessment
                offered ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_offered_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_rubric_id_terms(self):
        """Clears all rubric assessment offered ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric_id_terms = property(fdel=clear_rubric_id_terms)

    def supports_rubric_query(self):
        """Tests if an ``AssessmentOfferedQuery`` is available.

        return: (boolean) - ``true`` if a rubric assessment offered
                query is available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_rubric_query(self):
        """Gets the query for a rubric assessment.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.AssessmentOfferedQuery) - the
                assessment offered query
        raise:  Unimplemented - ``supports_rubric_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_rubric_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    rubric_query = property(fget=get_rubric_query)

    @utilities.arguments_not_none
    def match_any_rubric(self, match):
        """Matches an assessment offered that has any rubric assessment assigned.

        arg:    match (boolean): ``true`` to match assessments offered
                with any rubric, ``false`` to match assessments offered
                with no rubric
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_rubric_terms(self):
        """Clears all rubric assessment terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric_terms = property(fdel=clear_rubric_terms)

    @utilities.arguments_not_none
    def match_assessment_taken_id(self, assessment_taken_id, match):
        """Sets the assessment taken ``Id`` for this query.

        arg:    assessment_taken_id (osid.id.Id): an assessment taken
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_taken_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_taken_id_terms(self):
        """Clears all assessment taken ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_taken_id_terms = property(fdel=clear_assessment_taken_id_terms)

    def supports_assessment_taken_query(self):
        """Tests if an ``AssessmentTakenQuery`` is available.

        return: (boolean) - ``true`` if an assessment taken query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_assessment_taken_query(self):
        """Gets the query for an assessment taken.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.AssessmentTakenQuery) - the assessment
                taken query
        raise:  Unimplemented - ``supports_assessment_taken_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    assessment_taken_query = property(fget=get_assessment_taken_query)

    @utilities.arguments_not_none
    def match_any_assessment_taken(self, match):
        """Matches offerings that have any taken assessment version.

        arg:    match (boolean): ``true`` to match offerings with any
                taken assessment, ``false`` to match offerings with no
                assessmen taken
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_taken_terms(self):
        """Clears all assessment taken terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_taken_terms = property(fdel=clear_assessment_taken_terms)

    @utilities.arguments_not_none
    def match_bank_id(self, bank_id, match):
        """Sets the bank ``Id`` for this query.

        arg:    bank_id (osid.id.Id): a bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_bank_id_terms(self):
        """Clears all bank ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id_terms = property(fdel=clear_bank_id_terms)

    def supports_bank_query(self):
        """Tests if a ``BankQuery`` is available.

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
        """Clears all bank terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_terms = property(fdel=clear_bank_terms)

    @utilities.arguments_not_none
    def get_assessment_offered_query_record(self, assessment_offered_record_type):
        """Gets the assessment offered query record corresponding to the given ``AssessmentOffered`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    assessment_offered_record_type (osid.type.Type): an
                assessment offered record type
        return: (osid.assessment.records.AssessmentOfferedQueryRecord) -
                the assessment offered query record
        raise:  NullArgument - ``assessment_offered_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_offered_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentTakenQuery(abc_assessment_queries.AssessmentTakenQuery, osid_queries.OsidObjectQuery):
    """This is the query for searching assessments.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'assessment.AssessmentTaken'
        self._runtime = runtime
        record_type_data_sets = get_registry('ASSESSMENT_TAKEN_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def match_assessment_offered_id(self, assessment_offered_id, match):
        """Sets the assessment offered ``Id`` for this query.

        arg:    assessment_offered_id (osid.id.Id): an assessment ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_offered_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_offered_id_terms(self):
        """Clears all assessment offered ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_offered_id_terms = property(fdel=clear_assessment_offered_id_terms)

    def supports_assessment_offered_query(self):
        """Tests if an ``AssessmentOfferedQuery`` is available.

        return: (boolean) - ``true`` if an assessment offered query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_assessment_offered_query(self):
        """Gets the query for an assessment.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.AssessmentOfferedQuery) - the
                assessment offered query
        raise:  Unimplemented - ``supports_assessment_offered_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    assessment_offered_query = property(fget=get_assessment_offered_query)

    def clear_assessment_offered_terms(self):
        """Clears all assessment offered terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_offered_terms = property(fdel=clear_assessment_offered_terms)

    @utilities.arguments_not_none
    def match_taker_id(self, resource_id, match):
        """Sets the resource ``Id`` for this query.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``resource_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_taker_id_terms(self):
        """Clears all resource ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    taker_id_terms = property(fdel=clear_taker_id_terms)

    def supports_taker_query(self):
        """Tests if a ``ResourceQuery`` is available.

        return: (boolean) - ``true`` if a resource query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_taker_query(self):
        """Gets the query for a resource.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.resource.ResourceQuery) - the resource query
        raise:  Unimplemented - ``supports_taker_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_taker_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    taker_query = property(fget=get_taker_query)

    def clear_taker_terms(self):
        """Clears all resource terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    taker_terms = property(fdel=clear_taker_terms)

    @utilities.arguments_not_none
    def match_taking_agent_id(self, agent_id, match):
        """Sets the agent ``Id`` for this query.

        arg:    agent_id (osid.id.Id): an agent ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``agent_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_taking_agent_id_terms(self):
        """Clears all agent ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    taking_agent_id_terms = property(fdel=clear_taking_agent_id_terms)

    def supports_taking_agent_query(self):
        """Tests if an ``AgentQuery`` is available.

        return: (boolean) - ``true`` if an agent query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_taking_agent_query(self):
        """Gets the query for an agent.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.authentication.AgentQuery) - the agent query
        raise:  Unimplemented - ``supports_taking_agent_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_taking_agent_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    taking_agent_query = property(fget=get_taking_agent_query)

    def clear_taking_agent_terms(self):
        """Clears all taking agent terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    taking_agent_terms = property(fdel=clear_taking_agent_terms)

    @utilities.arguments_not_none
    def match_actual_start_time(self, start, end, match):
        """Matches assessments whose start time falls between the specified range inclusive.

        arg:    start (osid.calendaring.DateTime): start of range
        arg:    end (osid.calendaring.DateTime): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``end`` is less than ``start``
        raise:  NullArgument - ``start`` or ``end`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_actual_start_time(self, match):
        """Matches taken assessments taken that have begun.

        arg:    match (boolean): ``true`` to match assessments taken
                started, ``false`` to match assessments taken that have
                not begun
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_actual_start_time_terms(self):
        """Clears all start time terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    actual_start_time_terms = property(fdel=clear_actual_start_time_terms)

    @utilities.arguments_not_none
    def match_completion_time(self, start, end, match):
        """Matches assessments whose completion time falls between the specified range inclusive.

        arg:    start (osid.calendaring.DateTime): start of range
        arg:    end (osid.calendaring.DateTime): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``end`` is less than ``start``
        raise:  NullArgument - ``start`` or ``end`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_completion_time(self, match):
        """Matches taken assessments taken that have completed.

        arg:    match (boolean): ``true`` to match assessments taken
                completed, ``false`` to match assessments taken that are
                incomplete
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_completion_time_terms(self):
        """Clears all in completion time terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    completion_time_terms = property(fdel=clear_completion_time_terms)

    @utilities.arguments_not_none
    def match_time_spent(self, low, high, match):
        """Matches assessments where the time spent falls between the specified range inclusive.

        arg:    low (osid.calendaring.Duration): start of duration range
        arg:    high (osid.calendaring.Duration): end of duration range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``high`` is less than ``low``
        raise:  NullArgument - ``low`` or ``high`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_time_spent_terms(self):
        """Clears all in time spent terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    time_spent_terms = property(fdel=clear_time_spent_terms)

    @utilities.arguments_not_none
    def match_score_system_id(self, grade_system_id, match):
        """Sets the grade system ``Id`` for this query.

        arg:    grade_system_id (osid.id.Id): a grade system ``Id``
        arg:    match (boolean): ``true for a positive match, false for
                a negative match``
        raise:  NullArgument - ``grade_system_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_score_system_id_terms(self):
        """Clears all grade system ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score_system_id_terms = property(fdel=clear_score_system_id_terms)

    def supports_score_system_query(self):
        """Tests if a ``GradeSystemQuery`` is available.

        return: (boolean) - ``true`` if a grade system query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_score_system_query(self):
        """Gets the query for a grade system.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeSystemQuery) - the grade system query
        raise:  Unimplemented - ``supports_score_system_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_score_system_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    score_system_query = property(fget=get_score_system_query)

    @utilities.arguments_not_none
    def match_any_score_system(self, match):
        """Matches taken assessments that have any grade system assigned.

        arg:    match (boolean): ``true`` to match assessments with any
                grade system, ``false`` to match assessments with no
                grade system
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_score_system_terms(self):
        """Clears all grade system terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score_system_terms = property(fdel=clear_score_system_terms)

    @utilities.arguments_not_none
    def match_score(self, low, high, match):
        """Matches assessments whose score falls between the specified range inclusive.

        arg:    low (decimal): start of range
        arg:    high (decimal): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  InvalidArgument - ``high`` is less than ``low``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_score(self, match):
        """Matches taken assessments that have any score assigned.

        arg:    match (boolean): ``true`` to match assessments with any
                score, ``false`` to match assessments with no score
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_score_terms(self):
        """Clears all score terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score_terms = property(fdel=clear_score_terms)

    @utilities.arguments_not_none
    def match_grade_id(self, grade_id, match):
        """Sets the grade ``Id`` for this query.

        arg:    grade_id (osid.id.Id): a grade ``Id``
        arg:    match (boolean): ``true for a positive match, false for
                a negative match``
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_id_terms(self):
        """Clears all grade ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_id_terms = property(fdel=clear_grade_id_terms)

    def supports_grade_query(self):
        """Tests if a ``GradeQuery`` is available.

        return: (boolean) - ``true`` if a grade query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grade_query(self):
        """Gets the query for a grade.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeQuery) - the grade query
        raise:  Unimplemented - ``supports_grade_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_grade_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    grade_query = property(fget=get_grade_query)

    @utilities.arguments_not_none
    def match_any_grade(self, match):
        """Matches taken assessments that have any grade assigned.

        arg:    match (boolean): ``true`` to match assessments with any
                grade, ``false`` to match assessments with no grade
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_terms(self):
        """Clears all grade terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_terms = property(fdel=clear_grade_terms)

    @utilities.arguments_not_none
    def match_feedback(self, comments, string_match_type, match):
        """Sets the comment string for this query.

        arg:    comments (string): comment string
        arg:    string_match_type (osid.type.Type): the string match
                type
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  InvalidArgument - ``comments is`` not of
                ``string_match_type``
        raise:  NullArgument - ``comments`` or ``string_match_type`` is
                ``null``
        raise:  Unsupported -
                ``supports_string_match_type(string_match_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_feedback(self, match):
        """Matches taken assessments that have any comments.

        arg:    match (boolean): ``true`` to match assessments with any
                comments, ``false`` to match assessments with no
                comments
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_feedback_terms(self):
        """Clears all comment terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    feedback_terms = property(fdel=clear_feedback_terms)

    @utilities.arguments_not_none
    def match_rubric_id(self, assessment_taken_id, match):
        """Sets the rubric assessment taken ``Id`` for this query.

        arg:    assessment_taken_id (osid.id.Id): an assessment taken
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_taken_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_rubric_id_terms(self):
        """Clears all rubric assessment taken ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric_id_terms = property(fdel=clear_rubric_id_terms)

    def supports_rubric_query(self):
        """Tests if an ``AssessmentTakenQuery`` is available.

        return: (boolean) - ``true`` if a rubric assessment taken query
                is available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_rubric_query(self):
        """Gets the query for a rubric assessment.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.AssessmentTakenQuery) - the assessment
                taken query
        raise:  Unimplemented - ``supports_rubric_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_rubric_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    rubric_query = property(fget=get_rubric_query)

    @utilities.arguments_not_none
    def match_any_rubric(self, match):
        """Matches an assessment taken that has any rubric assessment assigned.

        arg:    match (boolean): ``true`` to match assessments taken
                with any rubric, ``false`` to match assessments taken
                with no rubric
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_rubric_terms(self):
        """Clears all rubric assessment taken terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rubric_terms = property(fdel=clear_rubric_terms)

    @utilities.arguments_not_none
    def match_bank_id(self, bank_id, match):
        """Sets the bank ``Id`` for this query.

        arg:    bank_id (osid.id.Id): a bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_bank_id_terms(self):
        """Clears all bank ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id_terms = property(fdel=clear_bank_id_terms)

    def supports_bank_query(self):
        """Tests if a ``BankQuery`` is available.

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
        """Clears all bank terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_terms = property(fdel=clear_bank_terms)

    @utilities.arguments_not_none
    def get_assessment_taken_query_record(self, assessment_taken_record_type):
        """Gets the assessment taken query record corresponding to the given ``AssessmentTaken`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    assessment_taken_record_type (osid.type.Type): an
                assessment taken record type
        return: (osid.assessment.records.AssessmentTakenQueryRecord) -
                the assessment taken query record
        raise:  NullArgument - ``assessment_taken_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(assessment_taken_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class BankQuery(abc_assessment_queries.BankQuery, osid_queries.OsidCatalogQuery):
    """This is the query for searching banks Each method specifies an ``AND`` term while multiple invocations of the same method produce a nested ``OR``."""

    def __init__(self, runtime):
        self._runtime = runtime


    @utilities.arguments_not_none
    def match_item_id(self, item_id, match):
        """Sets the item ``Id`` for this query.

        arg:    item_id (osid.id.Id): an item ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``item_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_item_id_terms(self):
        """Clears all item ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('itemId')

    item_id_terms = property(fdel=clear_item_id_terms)

    def supports_item_query(self):
        """Tests if a ``ItemQuery`` is available.

        return: (boolean) - ``true`` if an item query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_item_query(self):
        """Gets the query for an item.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.ItemQuery) - the item query
        raise:  Unimplemented - ``supports_item_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    item_query = property(fget=get_item_query)

    @utilities.arguments_not_none
    def match_any_item(self, match):
        """Matches assessment banks that have any item assigned.

        arg:    match (boolean): ``true`` to match banks with any item,
                ``false`` to match assessments with no item
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_item_terms(self):
        """Clears all item terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('item')

    item_terms = property(fdel=clear_item_terms)

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
        self._clear_terms('assessmentId')

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

    @utilities.arguments_not_none
    def match_any_assessment(self, match):
        """Matches assessment banks that have any assessment assigned.

        arg:    match (boolean): ``true`` to match banks with any
                assessment, ``false`` to match banks with no assessment
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_terms(self):
        """Clears all assessment terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('assessment')

    assessment_terms = property(fdel=clear_assessment_terms)

    @utilities.arguments_not_none
    def match_assessment_offered_id(self, assessment_offered_id, match):
        """Sets the assessment offered ``Id`` for this query.

        arg:    assessment_offered_id (osid.id.Id): an assessment ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``assessment_offered_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_offered_id_terms(self):
        """Clears all assessment offered ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('assessmentOfferedId')

    assessment_offered_id_terms = property(fdel=clear_assessment_offered_id_terms)

    def supports_assessment_offered_query(self):
        """Tests if an ``AssessmentOfferedQuery`` is available.

        return: (boolean) - ``true`` if an assessment offered query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_assessment_offered_query(self):
        """Gets the query for an assessment offered.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.AssessmentOfferedQuery) - the
                assessment offered query
        raise:  Unimplemented - ``supports_assessment_offered_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    assessment_offered_query = property(fget=get_assessment_offered_query)

    @utilities.arguments_not_none
    def match_any_assessment_offered(self, match):
        """Matches assessment banks that have any assessment offering assigned.

        arg:    match (boolean): ``true`` to match banks with any
                assessment offering, ``false`` to match banks with no
                offering
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_offered_terms(self):
        """Clears all assessment offered terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('assessmentOffered')

    assessment_offered_terms = property(fdel=clear_assessment_offered_terms)

    @utilities.arguments_not_none
    def match_ancestor_bank_id(self, bank_id, match):
        """Sets the bank ``Id`` for to match banks in which the specified bank is an acestor.

        arg:    bank_id (osid.id.Id): a bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ancestor_bank_id_terms(self):
        """Clears all ancestor bank ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('ancestorBankId')

    ancestor_bank_id_terms = property(fdel=clear_ancestor_bank_id_terms)

    def supports_ancestor_bank_query(self):
        """Tests if a ``BankQuery`` is available.

        return: (boolean) - ``true`` if a bank query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_ancestor_bank_query(self):
        """Gets the query for an ancestor bank.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.BankQuery) - the bank query
        raise:  Unimplemented - ``supports_ancestor_bank_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_ancestor_bank_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    ancestor_bank_query = property(fget=get_ancestor_bank_query)

    @utilities.arguments_not_none
    def match_any_ancestor_bank(self, match):
        """Matches a bank that has any ancestor.

        arg:    match (boolean): ``true`` to match banks with any
                ancestor banks, ``false`` to match root banks
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ancestor_bank_terms(self):
        """Clears all ancestor bank terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('ancestorBank')

    ancestor_bank_terms = property(fdel=clear_ancestor_bank_terms)

    @utilities.arguments_not_none
    def match_descendant_bank_id(self, bank_id, match):
        """Sets the bank ``Id`` for to match banks in which the specified bank is a descendant.

        arg:    bank_id (osid.id.Id): a bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_descendant_bank_id_terms(self):
        """Clears all descendant bank ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('descendantBankId')

    descendant_bank_id_terms = property(fdel=clear_descendant_bank_id_terms)

    def supports_descendant_bank_query(self):
        """Tests if a ``BankQuery`` is available.

        return: (boolean) - ``true`` if a bank query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_descendant_bank_query(self):
        """Gets the query for a descendant bank.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.assessment.BankQuery) - the bank query
        raise:  Unimplemented - ``supports_descendant_bank_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_descendant_bank_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    descendant_bank_query = property(fget=get_descendant_bank_query)

    @utilities.arguments_not_none
    def match_any_descendant_bank(self, match):
        """Matches a bank that has any descendant.

        arg:    match (boolean): ``true`` to match banks with any
                descendant banks, ``false`` to match leaf banks
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_descendant_bank_terms(self):
        """Clears all descendant bank terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('descendantBank')

    descendant_bank_terms = property(fdel=clear_descendant_bank_terms)

    @utilities.arguments_not_none
    def get_bank_query_record(self, bank_record_type):
        """Gets the bank query record corresponding to the given ``Bank`` record ``Type``.

        Multiple record retrievals produce a nested ``OR`` term.

        arg:    bank_record_type (osid.type.Type): a bank record type
        return: (osid.assessment.records.BankQueryRecord) - the bank
                query record
        raise:  NullArgument - ``bank_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(bank_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



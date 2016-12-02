"""GStudio implementations of learning queries."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.learning import queries as abc_learning_queries
from ..id.objects import IdList
from ..osid import queries as osid_queries
from ..primitives import Id
from ..utilities import get_registry
from dlkit.abstract_osid.osid import errors




class ObjectiveQuery(abc_learning_queries.ObjectiveQuery, osid_queries.OsidObjectQuery, osid_queries.OsidFederateableQuery):
    """This is the query for searching objectives.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'learning.Objective'
        self._runtime = runtime
        record_type_data_sets = get_registry('OBJECTIVE_RECORD_TYPES', runtime)
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
        """Clears the assessment ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_id_terms = property(fdel=clear_assessment_id_terms)

    def supports_assessment_query(self):
        """Tests if an ``AssessmentQuery`` is available for querying activities.

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
        """Matches an objective that has any assessment assigned.

        arg:    match (boolean): ``true`` to match objectives with any
                assessment, ``false`` to match objectives with no
                assessment
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_terms(self):
        """Clears the assessment terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_terms = property(fdel=clear_assessment_terms)

    @utilities.arguments_not_none
    def match_knowledge_category_id(self, grade_id, match):
        """Sets the knowledge category ``Id`` for this query.

        arg:    grade_id (osid.id.Id): a grade ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_knowledge_category_id_terms(self):
        """Clears the knowledge category ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    knowledge_category_id_terms = property(fdel=clear_knowledge_category_id_terms)

    def supports_knowledge_category_query(self):
        """Tests if a ``GradeQuery`` is available for querying knowledge categories.

        return: (boolean) - ``true`` if a grade query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_knowledge_category_query(self):
        """Gets the query for a knowledge category.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeQuery) - the grade query
        raise:  Unimplemented - ``supports_knowledge_category_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_knowledge_category_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    knowledge_category_query = property(fget=get_knowledge_category_query)

    @utilities.arguments_not_none
    def match_any_knowledge_category(self, match):
        """Matches an objective that has any knowledge category.

        arg:    match (boolean): ``true`` to match objectives with any
                knowledge category, ``false`` to match objectives with
                no knowledge category
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_knowledge_category_terms(self):
        """Clears the knowledge category terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    knowledge_category_terms = property(fdel=clear_knowledge_category_terms)

    @utilities.arguments_not_none
    def match_cognitive_process_id(self, grade_id, match):
        """Sets the cognitive process ``Id`` for this query.

        arg:    grade_id (osid.id.Id): a grade ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_cognitive_process_id_terms(self):
        """Clears the cognitive process ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cognitive_process_id_terms = property(fdel=clear_cognitive_process_id_terms)

    def supports_cognitive_process_query(self):
        """Tests if a ``GradeQuery`` is available for querying cognitive processes.

        return: (boolean) - ``true`` if a grade query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_cognitive_process_query(self):
        """Gets the query for a cognitive process.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeQuery) - the grade query
        raise:  Unimplemented - ``supports_cognitive_process_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_cognitive_process_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    cognitive_process_query = property(fget=get_cognitive_process_query)

    @utilities.arguments_not_none
    def match_any_cognitive_process(self, match):
        """Matches an objective that has any cognitive process.

        arg:    match (boolean): ``true`` to match objectives with any
                cognitive process, ``false`` to match objectives with no
                cognitive process
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_cognitive_process_terms(self):
        """Clears the cognitive process terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    cognitive_process_terms = property(fdel=clear_cognitive_process_terms)

    @utilities.arguments_not_none
    def match_activity_id(self, activity_id, match):
        """Sets the activity ``Id`` for this query.

        arg:    activity_id (osid.id.Id): an activity ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``activity_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_activity_id_terms(self):
        """Clears the activity ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    activity_id_terms = property(fdel=clear_activity_id_terms)

    def supports_activity_query(self):
        """Tests if an ``ActivityQuery`` is available for querying activities.

        return: (boolean) - ``true`` if an activity query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_activity_query(self):
        """Gets the query for an activity.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ActivityQuery) - the activity query
        raise:  Unimplemented - ``supports_activity_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_activity_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    activity_query = property(fget=get_activity_query)

    @utilities.arguments_not_none
    def match_any_activity(self, match):
        """Matches an objective that has any related activity.

        arg:    match (boolean): ``true`` to match objectives with any
                activity, ``false`` to match objectives with no activity
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_activity_terms(self):
        """Clears the activity terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    activity_terms = property(fdel=clear_activity_terms)

    @utilities.arguments_not_none
    def match_requisite_objective_id(self, requisite_objective_id, match):
        """Sets the requisite objective ``Id`` for this query.

        arg:    requisite_objective_id (osid.id.Id): a requisite
                objective ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``requisite_objective_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_requisite_objective_id_terms(self):
        """Clears the requisite objective ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    requisite_objective_id_terms = property(fdel=clear_requisite_objective_id_terms)

    def supports_requisite_objective_query(self):
        """Tests if an ``ObjectiveQuery`` is available for querying requisite objectives.

        return: (boolean) - ``true`` if an objective query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_requisite_objective_query(self):
        """Gets the query for a requisite objective.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveQuery) - the objective query
        raise:  Unimplemented - ``supports_requisite_objective_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_requisite_objective_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    requisite_objective_query = property(fget=get_requisite_objective_query)

    @utilities.arguments_not_none
    def match_any_requisite_objective(self, match):
        """Matches an objective that has any related requisite.

        arg:    match (boolean): ``true`` to match objectives with any
                requisite, ``false`` to match objectives with no
                requisite
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_requisite_objective_terms(self):
        """Clears the requisite objective terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    requisite_objective_terms = property(fdel=clear_requisite_objective_terms)

    @utilities.arguments_not_none
    def match_dependent_objective_id(self, dependent_objective_id, match):
        """Sets the dependent objective ``Id`` to query objectives dependent on the given objective.

        arg:    dependent_objective_id (osid.id.Id): a dependent
                objective ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``dependent_objective_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_dependent_objective_id_terms(self):
        """Clears the dependent objective ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    dependent_objective_id_terms = property(fdel=clear_dependent_objective_id_terms)

    def supports_depndent_objective_query(self):
        """Tests if an ``ObjectiveQuery`` is available for querying dependent objectives.

        return: (boolean) - ``true`` if an objective query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_dependent_objective_query(self):
        """Gets the query for a dependent objective.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveQuery) - the objective query
        raise:  Unimplemented - ``supports_dependent_objective_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_dependent_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    dependent_objective_query = property(fget=get_dependent_objective_query)

    @utilities.arguments_not_none
    def match_any_dependent_objective(self, match):
        """Matches an objective that has any related dependents.

        arg:    match (boolean): ``true`` to match objectives with any
                dependent, ``false`` to match objectives with no
                dependents
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_dependent_objective_terms(self):
        """Clears the dependent objective terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    dependent_objective_terms = property(fdel=clear_dependent_objective_terms)

    @utilities.arguments_not_none
    def match_equivalent_objective_id(self, equivalent_objective_id, match):
        """Sets the equivalent objective ``Id`` to query equivalents.

        arg:    equivalent_objective_id (osid.id.Id): an equivalent
                objective ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``equivalent_objective_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_equivalent_objective_id_terms(self):
        """Clears the equivalent objective ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    equivalent_objective_id_terms = property(fdel=clear_equivalent_objective_id_terms)

    def supports_equivalent_objective_query(self):
        """Tests if an ``ObjectiveQuery`` is available for querying equivalent objectives.

        return: (boolean) - ``true`` if an objective query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_equivalent_objective_query(self):
        """Gets the query for an equivalent objective.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveQuery) - the objective query
        raise:  Unimplemented -
                ``supports_equivalent_objective_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_equivalent_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    equivalent_objective_query = property(fget=get_equivalent_objective_query)

    @utilities.arguments_not_none
    def match_any_equivalent_objective(self, match):
        """Matches an objective that has any related equivalents.

        arg:    match (boolean): ``true`` to match objectives with any
                equivalent, ``false`` to match objectives with no
                equivalents
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_equivalent_objective_terms(self):
        """Clears the equivalent objective terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    equivalent_objective_terms = property(fdel=clear_equivalent_objective_terms)

    @utilities.arguments_not_none
    def match_ancestor_objective_id(self, objective_id, match):
        """Sets the objective ``Id`` for this query to match objectives that have the specified objective as an ancestor.

        arg:    objective_id (osid.id.Id): an objective ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``objective_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ancestor_objective_id_terms(self):
        """Clears the ancestor objective ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    ancestor_objective_id_terms = property(fdel=clear_ancestor_objective_id_terms)

    def supports_ancestor_objective_query(self):
        """Tests if an ``ObjectiveQuery`` is available.

        return: (boolean) - ``true`` if an objective query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_ancestor_objective_query(self):
        """Gets the query for an objective.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveQuery) - the objective query
        raise:  Unimplemented - ``supports_ancestor_objective_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_ancestor_objective_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    ancestor_objective_query = property(fget=get_ancestor_objective_query)

    @utilities.arguments_not_none
    def match_any_ancestor_objective(self, match):
        """Matches objectives that have any ancestor.

        arg:    match (boolean): ``true`` to match objective with any
                ancestor, ``false`` to match root objectives
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ancestor_objective_terms(self):
        """Clears the ancestor objective query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    ancestor_objective_terms = property(fdel=clear_ancestor_objective_terms)

    @utilities.arguments_not_none
    def match_descendant_objective_id(self, objective_id, match):
        """Sets the objective ``Id`` for this query to match objectives that have the specified objective as a descendant.

        arg:    objective_id (osid.id.Id): an objective ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``objective_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_descendant_objective_id_terms(self):
        """Clears the descendant objective ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    descendant_objective_id_terms = property(fdel=clear_descendant_objective_id_terms)

    def supports_descendant_objective_query(self):
        """Tests if an ``ObjectiveQuery`` is available.

        return: (boolean) - ``true`` if an objective query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_descendant_objective_query(self):
        """Gets the query for an objective.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveQuery) - the objective query
        raise:  Unimplemented -
                ``supports_descendant_objective_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_descendant_objective_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    descendant_objective_query = property(fget=get_descendant_objective_query)

    @utilities.arguments_not_none
    def match_any_descendant_objective(self, match):
        """Matches objectives that have any ancestor.

        arg:    match (boolean): ``true`` to match objectives with any
                ancestor, ``false`` to match leaf objectives
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_descendant_objective_terms(self):
        """Clears the descendant objective query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    descendant_objective_terms = property(fdel=clear_descendant_objective_terms)

    @utilities.arguments_not_none
    def match_objective_bank_id(self, objective_bank_id, match):
        """Sets the objective bank ``Id`` for this query.

        arg:    objective_bank_id (osid.id.Id): an objective bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``objective_bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_objective_bank_id_terms(self):
        """Clears the objective bank ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_bank_id_terms = property(fdel=clear_objective_bank_id_terms)

    def supports_objective_bank_query(self):
        """Tests if a ``ObjectiveBankQuery`` is available for querying objective banks.

        return: (boolean) - ``true`` if an objective bank query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_objective_bank_query(self):
        """Gets the query for an objective bank.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveBankQuery) - the objective bank
                query
        raise:  Unimplemented - ``supports_objective_bank_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_objective_bank_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    objective_bank_query = property(fget=get_objective_bank_query)

    def clear_objective_bank_terms(self):
        """Clears the objective bank terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_bank_terms = property(fdel=clear_objective_bank_terms)

    @utilities.arguments_not_none
    def get_objective_query_record(self, objective_record_type):
        """Gets the objective query record corresponding to the given ``Objective`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    objective_record_type (osid.type.Type): an objective
                query record type
        return: (osid.learning.records.ObjectiveQueryRecord) - the
                objective query record
        raise:  NullArgument - ``objective_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(objective_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ActivityQuery(abc_learning_queries.ActivityQuery, osid_queries.OsidObjectQuery, osid_queries.OsidSubjugateableQuery):
    """This is the query for searching activities.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'learning.Activity'
        self._runtime = runtime
        record_type_data_sets = get_registry('ACTIVITY_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def match_objective_id(self, objective_id, match):
        """Sets the objective ``Id`` for this query.

        arg:    objective_id (osid.id.Id): an objective ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``objective_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_objective_id_terms(self):
        """Clears the objective ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_id_terms = property(fdel=clear_objective_id_terms)

    def supports_objective_query(self):
        """Tests if an ``ObjectiveQuery`` is available for querying objectives.

        return: (boolean) - ``true`` if an objective query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_objective_query(self):
        """Gets the query for an objective.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveQuery) - the objective query
        raise:  Unimplemented - ``supports_objective_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_objective_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    objective_query = property(fget=get_objective_query)

    def clear_objective_terms(self):
        """Clears the objective terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_terms = property(fdel=clear_objective_terms)

    @utilities.arguments_not_none
    def match_asset_id(self, asset_id, match):
        """Sets the asset ``Id`` for this query.

        arg:    asset_id (osid.id.Id): an asset ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``asset_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_asset_id_terms(self):
        """Clears the asset ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    asset_id_terms = property(fdel=clear_asset_id_terms)

    def supports_asset_query(self):
        """Tests if an ``AssetQuery`` is available for querying objectives.

        return: (boolean) - ``true`` if an robjective query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_asset_query(self):
        """Gets the query for an asset.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.repository.AssetQuery) - the asset query
        raise:  Unimplemented - ``supports_asset_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_objective_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    asset_query = property(fget=get_asset_query)

    @utilities.arguments_not_none
    def match_any_asset(self, match):
        """Matches an activity that has any objective assigned.

        arg:    match (boolean): ``true`` to match activities with any
                asset, ``false`` to match activities with no asset
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_asset_terms(self):
        """Clears the asset terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    asset_terms = property(fdel=clear_asset_terms)

    @utilities.arguments_not_none
    def match_course_id(self, course_id, match):
        """Sets the course ``Id`` for this query.

        arg:    course_id (osid.id.Id): a course ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``course_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_course_id_terms(self):
        """Clears the course ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    course_id_terms = property(fdel=clear_course_id_terms)

    def supports_course_query(self):
        """Tests if a ``CourseQuery`` is available for querying courses.

        return: (boolean) - ``true`` if a course query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_course_query(self):
        """Gets the query for a course.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.course.CourseQuery) - the course query
        raise:  Unimplemented - ``supports_course_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_course_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    course_query = property(fget=get_course_query)

    @utilities.arguments_not_none
    def match_any_course(self, match):
        """Matches an activity that has any course assigned.

        arg:    match (boolean): ``true`` to match activities with any
                courses, ``false`` to match activities with no courses
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_course_terms(self):
        """Clears the course terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    course_terms = property(fdel=clear_course_terms)

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
        """Clears the assessment ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_id_terms = property(fdel=clear_assessment_id_terms)

    def supports_assessment_query(self):
        """Tests if an ``AssessmentQuery`` is available for querying assessments.

        return: (boolean) - ``true`` if an assessment query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_assessment_query(self):
        """Gets the query for a assessment.

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
        """Matches an activity that has any assessment assigned.

        arg:    match (boolean): ``true`` to match activities with any
                assessments, ``false`` to match activities with no
                assessments
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_assessment_terms(self):
        """Clears the assessment terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_terms = property(fdel=clear_assessment_terms)

    @utilities.arguments_not_none
    def match_objective_bank_id(self, objective_bank_id, match):
        """Sets the objective bank ``Id`` for this query.

        arg:    objective_bank_id (osid.id.Id): an objective bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``objective_bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_objective_bank_id_terms(self):
        """Clears the objective bank ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_bank_id_terms = property(fdel=clear_objective_bank_id_terms)

    def supports_objective_bank_query(self):
        """Tests if a ``ObjectiveBankQuery`` is available for querying resources.

        return: (boolean) - ``true`` if an objective bank query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_objective_bank_query(self):
        """Gets the query for an objective bank.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveBankQuery) - the objective bank
                query
        raise:  Unimplemented - ``supports_objective_bank_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_objective_bank_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    objective_bank_query = property(fget=get_objective_bank_query)

    def clear_objective_bank_terms(self):
        """Clears the objective bank terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_bank_terms = property(fdel=clear_objective_bank_terms)

    @utilities.arguments_not_none
    def get_activity_query_record(self, activity_record_type):
        """Gets the activity query record corresponding to the given ``Activity`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    activity_record_type (osid.type.Type): an activity query
                record type
        return: (osid.learning.records.ActivityQueryRecord) - the
                activity query record
        raise:  NullArgument - ``activity_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(activity_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ProficiencyQuery(abc_learning_queries.ProficiencyQuery, osid_queries.OsidRelationshipQuery):
    """This is the query for searching proficiencies.

    Each method match specifies an ``AND`` term while multiple
    invocations of the same method produce a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'learning.Proficiency'
        self._runtime = runtime
        record_type_data_sets = get_registry('PROFICIENCY_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def match_resource_id(self, resource_id, match):
        """Sets the resource ``Id`` for this query.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        raise:  NullArgument - ``resource_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_resource_id_terms(self):
        """Clears the resource ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    resource_id_terms = property(fdel=clear_resource_id_terms)

    def supports_resource_query(self):
        """Tests if a ``ResourceQuery`` is available.

        return: (boolean) - ``true`` if a resource query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_resource_query(self):
        """Gets the query for a resource.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.resource.ResourceQuery) - the resource query
        raise:  Unimplemented - ``supports_resource_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_resource_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    resource_query = property(fget=get_resource_query)

    def clear_resource_terms(self):
        """Clears the resource terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    resource_terms = property(fdel=clear_resource_terms)

    @utilities.arguments_not_none
    def match_objective_id(self, objective_id, match):
        """Sets the objective ``Id`` for this query.

        arg:    objective_id (osid.id.Id): an objective ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``objective_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_objective_id_terms(self):
        """Clears the objective ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_id_terms = property(fdel=clear_objective_id_terms)

    def supports_objective_query(self):
        """Tests if an ``ObjectiveQuery`` is available for querying objectives.

        return: (boolean) - ``true`` if an robjective query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_objective_query(self):
        """Gets the query for an objective.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveQuery) - the objective query
        raise:  Unimplemented - ``supports_objective_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_objective_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    objective_query = property(fget=get_objective_query)

    @utilities.arguments_not_none
    def match_any_objective(self, match):
        """Matches an activity that has any objective assigned.

        arg:    match (boolean): ``true`` to match activities with any
                objective, ``false`` to match activities with no
                objective
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_objective_terms(self):
        """Clears the objective terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_terms = property(fdel=clear_objective_terms)

    @utilities.arguments_not_none
    def match_completion(self, start, end, match):
        """Sets the completion for this query to match completion percentages between the given range inclusive.

        arg:    start (decimal): start of range
        arg:    end (decimal): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``end`` is less than ``start``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_completion_terms(self):
        """Clears the completion terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    completion_terms = property(fdel=clear_completion_terms)

    @utilities.arguments_not_none
    def match_minimum_completion(self, completion, match):
        """Sets the minimum completion for this query.

        arg:    completion (decimal): completion percentage
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_minimum_completion_terms(self):
        """Clears the minimum completion terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    minimum_completion_terms = property(fdel=clear_minimum_completion_terms)

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
    def match_objective_bank_id(self, objective_bank_id, match):
        """Sets the objective bank ``Id`` for this query.

        arg:    objective_bank_id (osid.id.Id): an objective bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``objective_bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_objective_bank_id_terms(self):
        """Clears the objective bank ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_bank_id_terms = property(fdel=clear_objective_bank_id_terms)

    def supports_objective_bank_query(self):
        """Tests if a ``ObjectiveBankQuery`` is available for querying resources.

        return: (boolean) - ``true`` if an objective bank query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_objective_bank_query(self):
        """Gets the query for an objective bank.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveBankQuery) - the objective bank
                query
        raise:  Unimplemented - ``supports_objective_bank_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_objective_bank_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    objective_bank_query = property(fget=get_objective_bank_query)

    def clear_objective_bank_terms(self):
        """Clears the objective bank terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_bank_terms = property(fdel=clear_objective_bank_terms)

    @utilities.arguments_not_none
    def get_proficiency_query_record(self, proficiency_record_type):
        """Gets the proficiency query record corresponding to the given ``Proficiency`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    proficiency_record_type (osid.type.Type): a proficiency
                offered record type
        return: (osid.learning.records.ProficiencyQueryRecord) - the
                proficiency offered query record
        raise:  NullArgument - ``proficiency_offered_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(proficiency_offered_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ObjectiveBankQuery(abc_learning_queries.ObjectiveBankQuery, osid_queries.OsidCatalogQuery):
    """This is the query for searching objective banks.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """

    def __init__(self, runtime):
        self._runtime = runtime


    @utilities.arguments_not_none
    def match_objective_id(self, objective_id, match):
        """Sets the objective ``Id`` for this query.

        arg:    objective_id (osid.id.Id): an objective ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``objective_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_objective_id_terms(self):
        """Clears the objective ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('objectiveId')

    objective_id_terms = property(fdel=clear_objective_id_terms)

    def supports_objective_query(self):
        """Tests if an ``ObjectiveQuery`` is available.

        return: (boolean) - ``true`` if an objective query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_objective_query(self):
        """Gets the query for an objective.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveQuery) - the objective query
        raise:  Unimplemented - ``supports_objective_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_objective_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    objective_query = property(fget=get_objective_query)

    @utilities.arguments_not_none
    def match_any_objective(self, match):
        """Matches an objective bank that has any objective assigned.

        arg:    match (boolean): ``true`` to match objective banks with
                any objective, ``false`` to match objective banks with
                no objectives
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_objective_terms(self):
        """Clears the objective terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('objective')

    objective_terms = property(fdel=clear_objective_terms)

    @utilities.arguments_not_none
    def match_activity_id(self, activity_id, match):
        """Sets the activity ``Id`` for this query.

        arg:    activity_id (osid.id.Id): an activity ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``activity_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_activity_id_terms(self):
        """Clears the activity ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('activityId')

    activity_id_terms = property(fdel=clear_activity_id_terms)

    def supports_activity_query(self):
        """Tests if a ``ActivityQuery`` is available for querying activities.

        return: (boolean) - ``true`` if an activity query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_activity_query(self):
        """Gets the query for an activity.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ActivityQuery) - the activity query
        raise:  Unimplemented - ``supports_activity_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_activity_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    activity_query = property(fget=get_activity_query)

    @utilities.arguments_not_none
    def match_any_activity(self, match):
        """Matches an objective bank that has any activity assigned.

        arg:    match (boolean): ``true`` to match objective banks with
                any activity, ``false`` to match objective banks with no
                activities
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_activity_terms(self):
        """Clears the activity terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('activity')

    activity_terms = property(fdel=clear_activity_terms)

    @utilities.arguments_not_none
    def match_ancestor_objective_bank_id(self, objective_bank_id, match):
        """Sets the objective bank ``Id`` for this query to match objective banks that have the specified objective bank as an ancestor.

        arg:    objective_bank_id (osid.id.Id): an objective bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``objective_bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ancestor_objective_bank_id_terms(self):
        """Clears the ancestor objective bank ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('ancestorObjectiveBankId')

    ancestor_objective_bank_id_terms = property(fdel=clear_ancestor_objective_bank_id_terms)

    def supports_ancestor_objective_bank_query(self):
        """Tests if a ``ObjectiveBankQuery`` is available for querying ancestor objective banks.

        return: (boolean) - ``true`` if an objective bank query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_ancestor_objective_bank_query(self):
        """Gets the query for an objective bank.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveBankQuery) - the objective bank
                query
        raise:  Unimplemented -
                ``supports_ancestor_objective_bank_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_ancestor_calndar_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    ancestor_objective_bank_query = property(fget=get_ancestor_objective_bank_query)

    @utilities.arguments_not_none
    def match_any_ancestor_objective_bank(self, match):
        """Matches an objective bank that has any ancestor.

        arg:    match (boolean): ``true`` to match objective banks with
                any ancestor, ``false`` to match root objective banks
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ancestor_objective_bank_terms(self):
        """Clears the ancestor objective bank terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('ancestorObjectiveBank')

    ancestor_objective_bank_terms = property(fdel=clear_ancestor_objective_bank_terms)

    @utilities.arguments_not_none
    def match_descendant_objective_bank_id(self, objective_bank_id, match):
        """Sets the objective bank ``Id`` for this query to match objective banks that have the specified objective bank as a descendant.

        arg:    objective_bank_id (osid.id.Id): an objective bank ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``objective_bank_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_descendant_objective_bank_id_terms(self):
        """Clears the descendant objective bank ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('descendantObjectiveBankId')

    descendant_objective_bank_id_terms = property(fdel=clear_descendant_objective_bank_id_terms)

    def supports_descendant_objective_bank_query(self):
        """Tests if a ``ObjectiveBankQuery`` is available for querying descendant objective banks.

        return: (boolean) - ``true`` if an objective bank query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_descendant_objective_bank_query(self):
        """Gets the query for an objective bank.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.learning.ObjectiveBankQuery) - the objective bank
                query
        raise:  Unimplemented -
                ``supports_descendant_objective_bank_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_descendant_calndar_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    descendant_objective_bank_query = property(fget=get_descendant_objective_bank_query)

    @utilities.arguments_not_none
    def match_any_descendant_objective_bank(self, match):
        """Matches an objective bank that has any descendant.

        arg:    match (boolean): ``true`` to match objective banks with
                any descendant, ``false`` to match leaf objective banks
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_descendant_objective_bank_terms(self):
        """Clears the descendant objective bank terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('descendantObjectiveBank')

    descendant_objective_bank_terms = property(fdel=clear_descendant_objective_bank_terms)

    @utilities.arguments_not_none
    def get_objective_bank_query_record(self, objective_bank_record_type):
        """Gets the objective bank query record corresponding to the given ``ObjectiveBank`` record ``Type``.

        Multiple record retrievals produce a nested ``OR`` term.

        arg:    objective_bank_record_type (osid.type.Type): an
                objective bank record type
        return: (osid.learning.records.ObjectiveBankQueryRecord) - the
                objective bank query record
        raise:  NullArgument - ``objective_bank_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(objective_bank_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



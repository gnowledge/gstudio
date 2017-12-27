"""GStudio implementations of grading queries."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.grading import queries as abc_grading_queries
from ..id.objects import IdList
from ..osid import queries as osid_queries
from ..primitives import Id
from ..utilities import get_registry
from dlkit.abstract_osid.osid import errors




class GradeQuery(abc_grading_queries.GradeQuery, osid_queries.OsidObjectQuery, osid_queries.OsidSubjugateableQuery):
    """This is the query for searching gradings.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'grading.Grade'
        self._runtime = runtime
        record_type_data_sets = get_registry('GRADE_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def match_grade_system_id(self, grade_system_id, match):
        """Sets the grade system ``Id`` for this query.

        arg:    grade_system_id (osid.id.Id): a grade system ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  NullArgument - ``grade_system_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_system_id_terms(self):
        """Clears the grade system ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system_id_terms = property(fdel=clear_grade_system_id_terms)

    def supports_grade_system_query(self):
        """Tests if a ``GradeSystemQuery`` is available for querying grade systems.

        return: (boolean) - ``true`` if a grade system query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grade_system_query(self):
        """Gets the query for a grade system.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeSystemQuery) - the grade system query
        raise:  Unimplemented - ``supports_grade_system_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_grade_system_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    grade_system_query = property(fget=get_grade_system_query)

    def clear_grade_system_terms(self):
        """Clears the grade system terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system_terms = property(fdel=clear_grade_system_terms)

    @utilities.arguments_not_none
    def match_input_score_start_range(self, start, end, match):
        """Matches grades with the start input score inclusive.

        arg:    start (decimal): start of range
        arg:    end (decimal): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  InvalidArgument - ``start`` is greater than ``end``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_input_score_start_range_terms(self):
        """Clears the nput score start range terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    input_score_start_range_terms = property(fdel=clear_input_score_start_range_terms)

    @utilities.arguments_not_none
    def match_input_score_end_range(self, start, end, match):
        """Matches grades with the end input score inclusive.

        arg:    start (decimal): start of range
        arg:    end (decimal): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  InvalidArgument - ``start`` is greater than ``end``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_input_score_end_range_terms(self):
        """Clears the nput score start range terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    input_score_end_range_terms = property(fdel=clear_input_score_end_range_terms)

    @utilities.arguments_not_none
    def match_input_score(self, start, end, match):
        """Matches grades with the input score range contained within the given range inclusive.

        arg:    start (decimal): start of range
        arg:    end (decimal): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  InvalidArgument - ``start`` is greater than ``end``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_input_score_terms(self):
        """Clears the input score start range terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    input_score_terms = property(fdel=clear_input_score_terms)

    @utilities.arguments_not_none
    def match_output_score(self, start, end, match):
        """Matches grades with the output score contained within the given range inclusive.

        arg:    start (decimal): start of range
        arg:    end (decimal): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  InvalidArgument - ``start`` is greater than ``end``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_output_score_terms(self):
        """Clears the output score terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    output_score_terms = property(fdel=clear_output_score_terms)

    @utilities.arguments_not_none
    def match_grade_entry_id(self, grade_entry_id, match):
        """Sets the grade entry ``Id`` for this query.

        arg:    grade_entry_id (osid.id.Id): a grade entry ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  NullArgument - ``grade_entry_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_entry_id_terms(self):
        """Clears the grade entry ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_entry_id_terms = property(fdel=clear_grade_entry_id_terms)

    def supports_grade_entry_query(self):
        """Tests if a ``GradeEntryQuery`` is available for querying grade entries.

        return: (boolean) - ``true`` if a grade entry query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grade_entry_query(self):
        """Gets the query for a grade entry.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeEntryQuery) - the grade entry query
        raise:  Unimplemented - ``supports_grade_entry_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_grade_entry_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    grade_entry_query = property(fget=get_grade_entry_query)

    @utilities.arguments_not_none
    def match_any_grade_entry(self, match):
        """Matches grades that are assigned to any grade entry.

        arg:    match (boolean): ``true`` to match grades used in any
                grade entry, ``false`` to match grades that are not used
                in any grade entries
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_entry_terms(self):
        """Clears the grade entry terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_entry_terms = property(fdel=clear_grade_entry_terms)

    @utilities.arguments_not_none
    def match_gradebook_id(self, gradebook_id, match):
        """Sets the gradebook ``Id`` for this query.

        arg:    gradebook_id (osid.id.Id): a gradebook ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  NullArgument - ``gradebook_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_gradebook_id_terms(self):
        """Clears the gradebook ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_id_terms = property(fdel=clear_gradebook_id_terms)

    def supports_gradebook_query(self):
        """Tests if a ``GradebookQuery`` is available.

        return: (boolean) - ``true`` if a gradebook query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_gradebook_query(self):
        """Gets the query for a gradebook.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookQuery) - the gradebook query
        raise:  Unimplemented - ``supports_gradebook_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_gradebook_column_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    gradebook_query = property(fget=get_gradebook_query)

    def clear_gradebook_terms(self):
        """Clears the gradebook terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_terms = property(fdel=clear_gradebook_terms)

    @utilities.arguments_not_none
    def get_grade_query_record(self, grade_record_type):
        """Gets the grade query record corresponding to the given ``Grade`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    grade_record_type (osid.type.Type): a grade record type
        return: (osid.grading.records.GradeQueryRecord) - the grade
                query record
        raise:  NullArgument - ``grade_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(grade_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradeSystemQuery(abc_grading_queries.GradeSystemQuery, osid_queries.OsidObjectQuery, osid_queries.OsidAggregateableQuery):
    """This is the query for searching grade systems.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'grading.GradeSystem'
        self._runtime = runtime
        record_type_data_sets = get_registry('GRADE_SYSTEM_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def match_based_on_grades(self, match):
        """Matches grade systems based on grades.

        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_based_on_grades_terms(self):
        """Clears the grade ``based`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    based_on_grades_terms = property(fdel=clear_based_on_grades_terms)

    @utilities.arguments_not_none
    def match_grade_id(self, grade_id, match):
        """Sets the grade ``Id`` for this query.

        arg:    grade_id (osid.id.Id): a grade ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_id_terms(self):
        """Clears the grade ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_id_terms = property(fdel=clear_grade_id_terms)

    def supports_grade_query(self):
        """Tests if a ``GradeQuery`` is available for querying grades.

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
        """Matches grade systems with any grade.

        arg:    match (boolean): ``true`` to match grade systems with
                any grade, ``false`` to match systems with no grade
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_terms(self):
        """Clears the grade terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_terms = property(fdel=clear_grade_terms)

    @utilities.arguments_not_none
    def match_lowest_numeric_score(self, start, end, match):
        """Matches grade systems whose low end score falls in the specified range inclusive.

        arg:    start (decimal): low end of range
        arg:    end (decimal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  InvalidArgument - ``end`` is less than ``start``
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_lowest_numeric_score_terms(self):
        """Clears the lowest numeric score terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    lowest_numeric_score_terms = property(fdel=clear_lowest_numeric_score_terms)

    @utilities.arguments_not_none
    def match_numeric_score_increment(self, start, end, match):
        """Matches grade systems numeric score increment is between the specified range inclusive.

        arg:    start (decimal): low end of range
        arg:    end (decimal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  InvalidArgument - ``end`` is less than ``start``
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_numeric_score_increment_terms(self):
        """Clears the numeric score increment terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    numeric_score_increment_terms = property(fdel=clear_numeric_score_increment_terms)

    @utilities.arguments_not_none
    def match_highest_numeric_score(self, start, end, match):
        """Matches grade systems whose high end score falls in the specified range inclusive.

        arg:    start (decimal): low end of range
        arg:    end (decimal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  InvalidArgument - ``end`` is less than ``start``
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_highest_numeric_score_terms(self):
        """Clears the highest numeric score terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    highest_numeric_score_terms = property(fdel=clear_highest_numeric_score_terms)

    @utilities.arguments_not_none
    def match_gradebook_column_id(self, gradebook_column_id, match):
        """Sets the gradebook column ``Id`` for this query.

        arg:    gradebook_column_id (osid.id.Id): a gradebook column
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  NullArgument - ``gradebook_column_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_gradebook_column_id_terms(self):
        """Clears the gradebook column ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_column_id_terms = property(fdel=clear_gradebook_column_id_terms)

    def supports_gradebook_column_query(self):
        """Tests if a ``GradebookColumnQuery`` is available.

        return: (boolean) - ``true`` if a gradebook column query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_gradebook_column_query(self):
        """Gets the query for a gradebook column.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookColumnQuery) - the gradebook
                column query
        raise:  Unimplemented - ``supports_gradebook_column_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_gradebook_column_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    gradebook_column_query = property(fget=get_gradebook_column_query)

    @utilities.arguments_not_none
    def match_any_gradebook_column(self, match):
        """Matches grade systems assigned to any gradebook column.

        arg:    match (boolean): ``true`` to match grade systems mapped
                to any column, ``false`` to match systems mapped to no
                columns
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_gradebook_column_terms(self):
        """Clears the gradebook column terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_column_terms = property(fdel=clear_gradebook_column_terms)

    @utilities.arguments_not_none
    def match_gradebook_id(self, gradebook_id, match):
        """Sets the gradebook ``Id`` for this query.

        arg:    gradebook_id (osid.id.Id): a gradebook ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  NullArgument - ``gradebook_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_gradebook_id_terms(self):
        """Clears the gradebook ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_id_terms = property(fdel=clear_gradebook_id_terms)

    def supports_gradebook_query(self):
        """Tests if a ``GradebookQuery`` is available.

        return: (boolean) - ``true`` if a gradebook query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_gradebook_query(self):
        """Gets the query for a gradebook.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookQuery) - the gradebook query
        raise:  Unimplemented - ``supports_gradebook_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_gradebook_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    gradebook_query = property(fget=get_gradebook_query)

    def clear_gradebook_terms(self):
        """Clears the gradebook terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_terms = property(fdel=clear_gradebook_terms)

    @utilities.arguments_not_none
    def get_grade_system_query_record(self, grade_system_record_type):
        """Gets the grade system query record corresponding to the given ``GradeSystem`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    grade_system_record_type (osid.type.Type): a grade
                system record type
        return: (osid.grading.records.GradeSystemQueryRecord) - the
                grade system query record
        raise:  NullArgument - ``grade_system_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(grade_system_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradeEntryQuery(abc_grading_queries.GradeEntryQuery, osid_queries.OsidRelationshipQuery):
    """This is the query for searching grade entries.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'grading.GradeEntry'
        self._runtime = runtime
        record_type_data_sets = get_registry('GRADE_ENTRY_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def match_gradebook_column_id(self, gradebook_column_id, match):
        """Sets the gradebook column ``Id`` for this query.

        arg:    gradebook_column_id (osid.id.Id): a gradebook column
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``gradebook_column_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._add_match('gradebookColumnId',
                        gradebook_column_id,
                        match)
    

    def clear_gradebook_column_id_terms(self):
        """Clears the gradebook column ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_column_id_terms = property(fdel=clear_gradebook_column_id_terms)

    def supports_gradebook_column_query(self):
        """Tests if a ``GradebookColumnQuery`` is available for querying creators.

        return: (boolean) - ``true`` if a gradebook column query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_gradebook_column_query(self):
        """Gets the query for a gradebook column.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookColumnQuery) - the gradebook
                column query
        raise:  Unimplemented - ``supports_gradebook_column_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_gradebook_column_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    gradebook_column_query = property(fget=get_gradebook_column_query)

    def clear_gradebook_column_terms(self):
        """Clears the gradebook column terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_column_terms = property(fdel=clear_gradebook_column_terms)

    @utilities.arguments_not_none
    def match_key_resource_id(self, resource_id, match):
        """Sets the key resource ``Id`` for this query.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``resource_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_key_resource_id_terms(self):
        """Clears the key resource ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    key_resource_id_terms = property(fdel=clear_key_resource_id_terms)

    def supports_key_resource_query(self):
        """Tests if a ``ResourceQUery`` is available for querying key resources.

        return: (boolean) - ``true`` if a resource query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_key_resource_query(self):
        """Gets the query for a key resource.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.resource.ResourceQuery) - the resource query
        raise:  Unimplemented - ``supports_key_resource_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_key_resource_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    key_resource_query = property(fget=get_key_resource_query)

    @utilities.arguments_not_none
    def match_any_key_resource(self, match):
        """Matches grade entries with any key resource.

        arg:    match (boolean): ``true`` to match grade entries with
                any key resource, ``false`` to match entries with no key
                resource
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_key_resource_terms(self):
        """Clears the key resource terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    key_resource_terms = property(fdel=clear_key_resource_terms)

    @utilities.arguments_not_none
    def match_derived(self, match):
        """Matches derived grade entries.

        arg:    match (boolean): ``true`` to match derived grade entries
                , ``false`` to match manual entries
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_derived_terms(self):
        """Clears the derived terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    derived_terms = property(fdel=clear_derived_terms)

    @utilities.arguments_not_none
    def match_overridden_grade_entry_id(self, grade_entry_id, match):
        """Sets the grade entry ``Id`` for an overridden calculated grade entry.

        arg:    grade_entry_id (osid.id.Id): a grade entry ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``grade_entry_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_overridden_grade_entry_id_terms(self):
        """Clears the overridden grade entry ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    overridden_grade_entry_id_terms = property(fdel=clear_overridden_grade_entry_id_terms)

    def supports_overridden_grade_entry_query(self):
        """Tests if a ``GradeEntry`` is available for querying overridden calculated grade entries.

        return: (boolean) - ``true`` if a grade entry query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_overridden_grade_entry_query(self):
        """Gets the query for an overridden derived grade entry.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeEntryQuery) - the grade entry query
        raise:  Unimplemented -
                ``supports_overridden_grade_entry_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_overridden_grade_entry_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    overridden_grade_entry_query = property(fget=get_overridden_grade_entry_query)

    @utilities.arguments_not_none
    def match_any_overridden_grade_entry(self, match):
        """Matches grade entries overriding any calculated grade entry.

        arg:    match (boolean): ``true`` to match grade entries
                overriding any grade entry, ``false`` to match entries
                not overriding any entry
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_overridden_grade_entry_terms(self):
        """Clears the overridden grade entry terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    overridden_grade_entry_terms = property(fdel=clear_overridden_grade_entry_terms)

    @utilities.arguments_not_none
    def match_ignored_for_calculations(self, match):
        """Matches grade entries ignored for calculations.

        arg:    match (boolean): ``true`` to match grade entries ignored
                for calculations, ``false`` to match entries used in
                calculations
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ignored_for_calculations_terms(self):
        """Clears the ignored for calculation entries terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    ignored_for_calculations_terms = property(fdel=clear_ignored_for_calculations_terms)

    @utilities.arguments_not_none
    def match_grade_id(self, grade_id, match):
        """Sets the grade ``Id`` for this query.

        arg:    grade_id (osid.id.Id): a grade ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``grade_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_id_terms(self):
        """Clears the grade ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_id_terms = property(fdel=clear_grade_id_terms)

    def supports_grade_query(self):
        """Tests if a ``GradeQuery`` is available for querying grades.

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
        """Matches grade entries with any grade.

        arg:    match (boolean): ``true`` to match grade entries with
                any grade, ``false`` to match entries with no grade
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_terms(self):
        """Clears the grade terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_terms = property(fdel=clear_grade_terms)

    @utilities.arguments_not_none
    def match_score(self, start, end, match):
        """Matches grade entries which score is between the specified score inclusive.

        arg:    start (decimal): start of range
        arg:    end (decimal): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``end`` is less than ``start``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_score(self, match):
        """Matches grade entries with any score.

        arg:    match (boolean): ``true`` to match grade entries with
                any score, ``false`` to match entries with no score
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_score_terms(self):
        """Clears the score terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    score_terms = property(fdel=clear_score_terms)

    @utilities.arguments_not_none
    def match_time_graded(self, start, end, match):
        """Matches grade entries which graded time is between the specified times inclusive.

        arg:    start (osid.calendaring.DateTime): start of range
        arg:    end (osid.calendaring.DateTime): end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``end`` is less than ``start``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_time_graded_terms(self):
        """Clears the time graded terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    time_graded_terms = property(fdel=clear_time_graded_terms)

    @utilities.arguments_not_none
    def match_grader_id(self, resource_id, match):
        """Sets the agent ``Id`` for this query.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``resource_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grader_id_terms(self):
        """Clears the grader ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grader_id_terms = property(fdel=clear_grader_id_terms)

    def supports_grader_query(self):
        """Tests if a ``ResourceQuery`` is available for querying graders.

        return: (boolean) - ``true`` if a resource query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grader_query(self):
        """Gets the query for an agent.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.resource.ResourceQuery) - the resource query
        raise:  Unimplemented - ``supports_resource_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_resource_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    grader_query = property(fget=get_grader_query)

    @utilities.arguments_not_none
    def match_any_grader(self, match):
        """Matches grade entries with any grader.

        arg:    match (boolean): ``true`` to match grade entries with
                any grader, ``false`` to match entries with no grader
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grader_terms(self):
        """Clears the grader terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grader_terms = property(fdel=clear_grader_terms)

    @utilities.arguments_not_none
    def match_grading_agent_id(self, agent_id, match):
        """Sets the grading agent ``Id`` for this query.

        arg:    agent_id (osid.id.Id): an agent ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``agent_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grading_agent_id_terms(self):
        """Clears the grader ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grading_agent_id_terms = property(fdel=clear_grading_agent_id_terms)

    def supports_grading_agent_query(self):
        """Tests if an ``AgentQuery`` is available for querying grading agents.

        return: (boolean) - ``true`` if an agent query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grading_agent_query(self):
        """Gets the query for an agent.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.authentication.AgentQuery) - the agent query
        raise:  Unimplemented - ``supports_grading_agent_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_grading_agent_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    grading_agent_query = property(fget=get_grading_agent_query)

    @utilities.arguments_not_none
    def match_any_grading_agent(self, match):
        """Matches grade entries with any grading agent.

        arg:    match (boolean): ``true`` to match grade entries with
                any grading agent, ``false`` to match entries with no
                grading agent
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grading_agent_terms(self):
        """Clears the grading agent terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grading_agent_terms = property(fdel=clear_grading_agent_terms)

    @utilities.arguments_not_none
    def match_gradebook_id(self, gradebook_id, match):
        """Sets the gradebook ``Id`` for this query.

        arg:    gradebook_id (osid.id.Id): a gradebook ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``gradebook_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_gradebook_id_terms(self):
        """Clears the gradebook ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_id_terms = property(fdel=clear_gradebook_id_terms)

    def supports_gradebook_query(self):
        """Tests if a ``GradebookQuery`` is available for querying resources.

        return: (boolean) - ``true`` if a gradebook query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_gradebook_query(self):
        """Gets the query for a gradebook.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookQuery) - the gradebook query
        raise:  Unimplemented - ``supports_gradebook_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_gradebook_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    gradebook_query = property(fget=get_gradebook_query)

    def clear_gradebook_terms(self):
        """Clears the gradebook terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_terms = property(fdel=clear_gradebook_terms)

    @utilities.arguments_not_none
    def get_grade_entry_query_record(self, grade_entry_record_type):
        """Gets the grade entry query record corresponding to the given ``GradeEntry`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    grade_entry_record_type (osid.type.Type): a grade entry
                record type
        return: (osid.grading.records.GradeEntryQueryRecord) - the grade
                entry query record
        raise:  NullArgument - ``grade_entry_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(grade_entry_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradebookColumnQuery(abc_grading_queries.GradebookColumnQuery, osid_queries.OsidObjectQuery):
    """This is the query for searching gradings.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    def __init__(self, runtime):
        self._namespace = 'grading.GradebookColumn'
        self._runtime = runtime
        record_type_data_sets = get_registry('GRADEBOOK_COLUMN_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def match_grade_system_id(self, grade_system_id, match):
        """Sets the grade system ``Id`` for this query.

        arg:    grade_system_id (osid.id.Id): a grade system ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``grade_system_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._add_match('gradeSystemId', str(grade_system_id), bool(match))
    

    def clear_grade_system_id_terms(self):
        """Clears the grade system ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system_id_terms = property(fdel=clear_grade_system_id_terms)

    def supports_grade_system_query(self):
        """Tests if a ``GradeSystemQuery`` is available for querying grade systems.

        return: (boolean) - ``true`` if a grade system query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grade_system_query(self):
        """Gets the query for a grade system.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeSystemQuery) - the grade system query
        raise:  Unimplemented - ``supports_grade_system_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_grade_system_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    grade_system_query = property(fget=get_grade_system_query)

    @utilities.arguments_not_none
    def match_any_grade_system(self, match):
        """Matches gradebook columns with any grade system assigned.

        arg:    match (boolean): ``true`` to match columns with any
                grade system, ``false`` to match columns with no grade
                system
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_system_terms(self):
        """Clears the grade system terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_system_terms = property(fdel=clear_grade_system_terms)

    @utilities.arguments_not_none
    def match_grade_entry_id(self, grade_entry_id, match):
        """Sets the grade entry ``Id`` for this query.

        arg:    grade_entry_id (osid.id.Id): a grade entry ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``grade_entry_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_entry_id_terms(self):
        """Clears the grade entry ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_entry_id_terms = property(fdel=clear_grade_entry_id_terms)

    def supports_grade_entry_query(self):
        """Tests if a ``GradeEntryQuery`` is available for querying grade entries.

        return: (boolean) - ``true`` if a grade entry query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grade_entry_query(self):
        """Gets the query for a grade entry.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeEntryQuery) - the grade entry query
        raise:  Unimplemented - ``supports_grade_entry_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_grade_entry_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    grade_entry_query = property(fget=get_grade_entry_query)

    @utilities.arguments_not_none
    def match_any_grade_entry(self, match):
        """Matches gradebook columns with any grade entry assigned.

        arg:    match (boolean): ``true`` to match columns with any
                grade entry, ``false`` to match columns with no grade
                entries
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_entry_terms(self):
        """Clears the grade entry terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    grade_entry_terms = property(fdel=clear_grade_entry_terms)

    def supports_gradebook_column_summary_query(self):
        """Tests if a ``GradebookColumnSummaryQuery`` is available for querying grade systems.

        return: (boolean) - ``true`` if a gradebook column summary query
                interface is available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_gradebook_column_summary_query(self):
        """Gets the query interface for a gradebook column summary.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookColumnSummaryQuery) - the
                gradebook column summary query
        raise:  Unimplemented -
                ``supports_gradebook_column_summary_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_gradebook_column_summary_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    gradebook_column_summary_query = property(fget=get_gradebook_column_summary_query)

    def clear_gradebook_column_summary_terms(self):
        """Clears the gradebook column summary terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_column_summary_terms = property(fdel=clear_gradebook_column_summary_terms)

    @utilities.arguments_not_none
    def match_gradebook_id(self, gradebook_id, match):
        """Sets the gradebook ``Id`` for this query.

        arg:    gradebook_id (osid.id.Id): a gradebook ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``gradebook_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_gradebook_id_terms(self):
        """Clears the gradebook ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_id_terms = property(fdel=clear_gradebook_id_terms)

    def supports_gradebook_query(self):
        """Tests if a ``GradebookQuery`` is available for querying grade systems.

        return: (boolean) - ``true`` if a gradebook query interface is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_gradebook_query(self):
        """Gets the query interface for a gradebook.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookQuery) - the gradebook query
        raise:  Unimplemented - ``supports_gradebook_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_gradebook_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    gradebook_query = property(fget=get_gradebook_query)

    def clear_gradebook_terms(self):
        """Clears the gradebook terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_terms = property(fdel=clear_gradebook_terms)

    @utilities.arguments_not_none
    def get_gradebook_column_query_record(self, gradebook_column_record_type):
        """Gets the gradebook column query record corresponding to the given ``GradebookColumn`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    gradebook_column_record_type (osid.type.Type): a
                gradebook column record type
        return: (osid.grading.records.GradebookColumnQueryRecord) - the
                gradebook column query record
        raise:  NullArgument - ``gradebook_column_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(gradebook_column_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradebookColumnSummaryQuery(abc_grading_queries.GradebookColumnSummaryQuery, osid_queries.OsidRuleQuery):
    """This is the query for searching gradebook column summaries.

    Each method match request produces an ``AND`` term while multiple
    invocations of a method produces a nested ``OR``.

    """

    @utilities.arguments_not_none
    def match_gradebook_column_id(self, gradebook_column_id, match):
        """Sets the gradebook column ``Id`` for this query.

        arg:    gradebook_column_id (osid.id.Id): a gradeboo column
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``gradebook_column_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_gradebook_column_id_terms(self):
        """Clears the gradebook column ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_column_id_terms = property(fdel=clear_gradebook_column_id_terms)

    def supports_gradebook_column_query(self):
        """Tests if a ``GradebookColumnQuery`` is available for querying gradebook column.

        return: (boolean) - ``true`` if a gradebook column query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_gradebook_column_query(self):
        """Gets the query for a gradebook column.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookColumnQuery) - the gradebook
                column query
        raise:  Unimplemented - ``supports_gradebook_column_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_gradebook_column_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    gradebook_column_query = property(fget=get_gradebook_column_query)

    @utilities.arguments_not_none
    def match_any_gradebook_column(self, match):
        """Matches gradebook column derivations with any gradebookc olumn.

        arg:    match (boolean): ``true`` to match gradebook column
                derivations with any gradebook column, ``false`` to
                match gradebook column derivations with no gradebook
                columns
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_gradebook_column_terms(self):
        """Clears the source grade system terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_column_terms = property(fdel=clear_gradebook_column_terms)

    @utilities.arguments_not_none
    def match_mean(self, low, high, match):
        """Matches a mean between the given values inclusive.

        arg:    low (decimal): low end of range
        arg:    high (decimal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``low`` is greater than ``high``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_mean_terms(self):
        """Clears the mean terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    mean_terms = property(fdel=clear_mean_terms)

    @utilities.arguments_not_none
    def match_minimum_mean(self, value, match):
        """Matches a mean greater than or equal to the given value.

        arg:    value (decimal): minimum value
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_minimum_mean_terms(self):
        """Clears the minimum mean terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    minimum_mean_terms = property(fdel=clear_minimum_mean_terms)

    @utilities.arguments_not_none
    def match_median(self, low, high, match):
        """Matches a median between the given values inclusive.

        arg:    low (decimal): low end of range
        arg:    high (decimal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``low`` is greater than ``high``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_median_terms(self):
        """Clears the median terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    median_terms = property(fdel=clear_median_terms)

    @utilities.arguments_not_none
    def match_minimum_median(self, value, match):
        """Matches a median greater than or equal to the given value.

        arg:    value (decimal): minimum value
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_minimum_median_terms(self):
        """Clears the minimum median terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    minimum_median_terms = property(fdel=clear_minimum_median_terms)

    @utilities.arguments_not_none
    def match_mode(self, low, high, match):
        """Matches a mode between the given values inclusive.

        arg:    low (decimal): low end of range
        arg:    high (decimal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``low`` is greater than ``high``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_mode_terms(self):
        """Clears the mode terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    mode_terms = property(fdel=clear_mode_terms)

    @utilities.arguments_not_none
    def match_minimum_mode(self, value, match):
        """Matches a mode greater than or equal to the given value.

        arg:    value (decimal): minimum value
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_minimum_mode_terms(self):
        """Clears the minimum mode terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    minimum_mode_terms = property(fdel=clear_minimum_mode_terms)

    @utilities.arguments_not_none
    def match_rms(self, low, high, match):
        """Matches a root mean square between the given values inclusive.

        arg:    low (decimal): low end of range
        arg:    high (decimal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``low`` is greater than ``high``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_rms_terms(self):
        """Clears the root mean square terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    rms_terms = property(fdel=clear_rms_terms)

    @utilities.arguments_not_none
    def match_minimum_rms(self, value, match):
        """Matches a root mean square greater than or equal to the given value.

        arg:    value (decimal): minimum value
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_minimum_rms_terms(self):
        """Clears the minimum RMS terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    minimum_rms_terms = property(fdel=clear_minimum_rms_terms)

    @utilities.arguments_not_none
    def match_standard_deviation(self, low, high, match):
        """Matches a standard deviation mean square between the given values inclusive.

        arg:    low (decimal): low end of range
        arg:    high (decimal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``low`` is greater than ``high``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_standard_deviation_terms(self):
        """Clears the standard deviation terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    standard_deviation_terms = property(fdel=clear_standard_deviation_terms)

    @utilities.arguments_not_none
    def match_minimum_standard_deviation(self, value, match):
        """Matches a standard deviation greater than or equal to the given value.

        arg:    value (decimal): minimum value
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_minimum_standard_deviation_terms(self):
        """Clears the minimum standard deviation terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    minimum_standard_deviation_terms = property(fdel=clear_minimum_standard_deviation_terms)

    @utilities.arguments_not_none
    def match_sum(self, low, high, match):
        """Matches a sum mean square between the given values inclusive.

        arg:    low (decimal): low end of range
        arg:    high (decimal): high end of range
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  InvalidArgument - ``low`` is greater than ``high``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_sum_terms(self):
        """Clears the sum terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    sum_terms = property(fdel=clear_sum_terms)

    @utilities.arguments_not_none
    def match_minimum_sum(self, value, match):
        """Matches a sum greater than or equal to the given value.

        arg:    value (decimal): minimum value
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_minimum_sum_terms(self):
        """Clears the minimum sum terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    minimum_sum_terms = property(fdel=clear_minimum_sum_terms)

    @utilities.arguments_not_none
    def match_gradebook_id(self, gradebook_id, match):
        """Sets the gradebook ``Id`` for this query.

        arg:    gradebook_id (osid.id.Id): a gradebook ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``gradebook_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_gradebook_id_terms(self):
        """Clears the gradebook ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_id_terms = property(fdel=clear_gradebook_id_terms)

    def supports_gradebook_query(self):
        """Tests if a ``GradebookQuery`` is available.

        return: (boolean) - ``true`` if a gradebook query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_gradebook_query(self):
        """Gets the query for a gradebook.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookQuery) - the gradebook query
        raise:  Unimplemented - ``supports_gradebook_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_gradebook_column_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    gradebook_query = property(fget=get_gradebook_query)

    def clear_gradebook_terms(self):
        """Clears the gradebook terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    gradebook_terms = property(fdel=clear_gradebook_terms)

    @utilities.arguments_not_none
    def get_gradebook_column_summary_query_record(self, gradebook_column_summary_record_type):
        """Gets the gradebook column summary query record corresponding to the given ``GradebookColumnSummary`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    gradebook_column_summary_record_type (osid.type.Type): a
                gradebook column summary record type
        return: (osid.grading.records.GradebookColumnSummaryQueryRecord)
                - the gradebook column summary query record
        raise:  NullArgument - ``gradebook_column_summary_record_type``
                is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(gradebook_column_summary_record_type)`
                ` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class GradebookQuery(abc_grading_queries.GradebookQuery, osid_queries.OsidCatalogQuery):
    """This is the query for searching gradebooks.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """

    def __init__(self, runtime):
        self._runtime = runtime


    @utilities.arguments_not_none
    def match_grade_system_id(self, grade_system_id, match):
        """Sets the grade system ``Id`` for this query.

        arg:    grade_system_id (osid.id.Id): a grade system ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``grade_system_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_system_id_terms(self):
        """Clears the grade system ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('gradeSystemId')

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
        raise:  Unimplemented - ``supports_grade_system_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_grade_system_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    grade_system_query = property(fget=get_grade_system_query)

    @utilities.arguments_not_none
    def match_any_grade_system(self, match):
        """Matches gradebooks that have any grade system.

        arg:    match (boolean): ``true`` to match gradebooks with any
                grade system, ``false`` to match gradebooks with no
                grade system
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_system_terms(self):
        """Clears the grade system terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('gradeSystem')

    grade_system_terms = property(fdel=clear_grade_system_terms)

    @utilities.arguments_not_none
    def match_grade_entry_id(self, grade_entry_id, match):
        """Sets the grade entry ``Id`` for this query.

        arg:    grade_entry_id (osid.id.Id): a grade entry ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``grade_entry_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_entry_id_terms(self):
        """Clears the grade entry ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('gradeEntryId')

    grade_entry_id_terms = property(fdel=clear_grade_entry_id_terms)

    def supports_grade_entry_query(self):
        """Tests if a ``GradeEntryQuery`` is available.

        return: (boolean) - ``true`` if a grade entry query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_grade_entry_query(self):
        """Gets the query for a grade entry.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradeEntryQuery) - the grade entry query
        raise:  Unimplemented - ``supports_grade_entry_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_grade_entry_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    grade_entry_query = property(fget=get_grade_entry_query)

    @utilities.arguments_not_none
    def match_any_grade_entry(self, match):
        """Matches gradebooks that have any grade entry.

        arg:    match (boolean): ``true`` to match gradebooks with any
                grade entry, ``false`` to match gradebooks with no grade
                entry
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_grade_entry_terms(self):
        """Clears the grade entry terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('gradeEntry')

    grade_entry_terms = property(fdel=clear_grade_entry_terms)

    @utilities.arguments_not_none
    def match_gradebook_column_id(self, gradebook_column_id, match):
        """Sets the gradebook column ``Id`` for this query.

        arg:    gradebook_column_id (osid.id.Id): a gradebook column
                ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``gradebook_column_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_gradebook_column_id_terms(self):
        """Clears the gradebook column ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('gradebookColumnId')

    gradebook_column_id_terms = property(fdel=clear_gradebook_column_id_terms)

    def supports_gradebook_column_query(self):
        """Tests if a ``GradebookColumnQuery`` is available.

        return: (boolean) - ``true`` if a gradebook column query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_gradebook_column_query(self):
        """Gets the query for a gradebook column.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookColumnQuery) - the gradebook
                column query
        raise:  Unimplemented - ``supports_gradebook_column_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_gradebook_column_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    gradebook_column_query = property(fget=get_gradebook_column_query)

    @utilities.arguments_not_none
    def match_any_gradebook_column(self, match):
        """Matches gradebooks that have any column.

        arg:    match (boolean): ``true`` to match gradebooks with any
                column, ``false`` to match gradebooks with no column
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_gradebook_column_terms(self):
        """Clears the gradebook column terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('gradebookColumn')

    gradebook_column_terms = property(fdel=clear_gradebook_column_terms)

    @utilities.arguments_not_none
    def match_ancestor_gradebook_id(self, gradebook_id, match):
        """Sets the gradebook ``Id`` for this query to match gradebooks that have the specified gradebook as an ancestor.

        arg:    gradebook_id (osid.id.Id): a gradebook ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``gradebook_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ancestor_gradebook_id_terms(self):
        """Clears the ancestor gradebook ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('ancestorGradebookId')

    ancestor_gradebook_id_terms = property(fdel=clear_ancestor_gradebook_id_terms)

    def supports_ancestor_gradebook_query(self):
        """Tests if a ``GradebookQuery`` is available.

        return: (boolean) - ``true`` if a gradebook query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_ancestor_gradebook_query(self):
        """Gets the query for a gradebook.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookQuery) - the gradebook query
        raise:  Unimplemented - ``supports_ancestor_gradebook_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_ancestor_gradebook_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    ancestor_gradebook_query = property(fget=get_ancestor_gradebook_query)

    @utilities.arguments_not_none
    def match_any_ancestor_gradebook(self, match):
        """Matches gradebook with any ancestor.

        arg:    match (boolean): ``true`` to match gradebooks with any
                ancestor, ``false`` to match root gradebooks
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ancestor_gradebook_terms(self):
        """Clears the ancestor gradebook terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('ancestorGradebook')

    ancestor_gradebook_terms = property(fdel=clear_ancestor_gradebook_terms)

    @utilities.arguments_not_none
    def match_descendant_gradebook_id(self, gradebook_id, match):
        """Sets the gradebook ``Id`` for this query to match gradebooks that have the specified gradebook as a descendant.

        arg:    gradebook_id (osid.id.Id): a gradebook ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``gradebook_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_descendant_gradebook_id_terms(self):
        """Clears the descendant gradebook ``Id`` terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('descendantGradebookId')

    descendant_gradebook_id_terms = property(fdel=clear_descendant_gradebook_id_terms)

    def supports_descendant_gradebook_query(self):
        """Tests if a ``GradebookQuery`` is available.

        return: (boolean) - ``true`` if a gradebook query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_descendant_gradebook_query(self):
        """Gets the query for a gradebook.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.grading.GradebookQuery) - the gradebook query
        raise:  Unimplemented -
                ``supports_descendant_gradebook_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_descendant_gradebook_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    descendant_gradebook_query = property(fget=get_descendant_gradebook_query)

    @utilities.arguments_not_none
    def match_any_descendant_gradebook(self, match):
        """Matches gradebook with any descendant.

        arg:    match (boolean): ``true`` to match gradebooks with any
                descendant, ``false`` to match leaf gradebooks
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_descendant_gradebook_terms(self):
        """Clears the descendant gradebook terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('descendantGradebook')

    descendant_gradebook_terms = property(fdel=clear_descendant_gradebook_terms)

    @utilities.arguments_not_none
    def get_gradebook_query_record(self, gradebook_record_type):
        """Gets the gradebook query record corresponding to the given ``Gradebook`` record ``Type``.

        Multiple record retrievals produce a nested ``OR`` term.

        arg:    gradebook_record_type (osid.type.Type): a gradebook
                record type
        return: (osid.grading.records.GradebookQueryRecord) - the
                gradebook query record
        raise:  NullArgument - ``gradebook_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(gradebook_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



"""GStudio implementations of learning searches."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.learning import searches as abc_learning_searches
from ..osid import searches as osid_searches




class ObjectiveSearch(abc_learning_searches.ObjectiveSearch, osid_searches.OsidSearch):
    """``ObjectiveSearch`` defines the interface for specifying objective search options."""

    @utilities.arguments_not_none
    def search_among_objectives(self, objective_ids):
        """Execute this search among the given list of objectives.

        arg:    objective_ids (osid.id.IdList): list of objectives
        raise:  NullArgument - ``objective_ids`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_objective_results(self, objective_search_order):
        """Specify an ordering to the search results.

        arg:    objective_search_order
                (osid.learning.ObjectiveSearchOrder): objective search
                order
        raise:  NullArgument - ``objective_search_order`` is ``null``
        raise:  Unsupported - ``objective_search_order`` is not of this
                service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_objective_search_record(self, objective_search_record_type):
        """Gets the objective search record corresponding to the given objective search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    objective_search_record_type (osid.type.Type): an
                objective search record type
        return: (osid.learning.records.ObjectiveSearchRecord) - the
                objective search record
        raise:  NullArgument - ``objective_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_search_record_type(objective_search_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ObjectiveSearchResults(abc_learning_searches.ObjectiveSearchResults, osid_searches.OsidSearchResults):
    """This interface provides a means to capture results of a search."""

    def get_objectives(self):
        """Gets the objective list resulting from the search.

        return: (osid.learning.ObjectiveList) - the objective list
        raise:  IllegalState - list already retrieved
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objectives = property(fget=get_objectives)

    def get_objective_query_inspector(self):
        """Gets the inspector for the query to examine the terms used in the search.

        return: (osid.learning.ObjectiveQueryInspector) - the query
                inspector
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_query_inspector = property(fget=get_objective_query_inspector)

    @utilities.arguments_not_none
    def get_objective_search_results_record(self, objective_search_record_type):
        """Gets the objective search results record corresponding to the given objective search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    objective_search_record_type (osid.type.Type): an
                objective search record type
        return: (osid.learning.records.ObjectiveSearchResultsRecord) -
                the objective search results record
        raise:  NullArgument - ``objective_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_search_record_type(objective_search_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ActivitySearch(abc_learning_searches.ActivitySearch, osid_searches.OsidSearch):
    """``ActivitySearch`` defines the interface for specifying activity search options."""

    @utilities.arguments_not_none
    def search_among_activities(self, activity_ids):
        """Execute this search among the given list of activities.

        arg:    activity_ids (osid.id.IdList): list of activities
        raise:  NullArgument - ``activity_ids`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_activity_results(self, activitiesearch_order):
        """Specify an ordering to the search results.

        arg:    activitiesearch_order
                (osid.learning.ActivitySearchOrder): activity search
                order
        raise:  NullArgument - ``activitiesearch_order`` is ``null``
        raise:  Unsupported - ``activitiesearch_order`` is not of this
                service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_activity_search_record(self, activitiesearch_record_type):
        """Gets the activity record corresponding to the given activity search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    activitiesearch_record_type (osid.type.Type): an
                activity search record type
        return: (osid.learning.records.ActivitySearchRecord) - the
                activity search record
        raise:  NullArgument - ``activitiesearch_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_search_record_type(activitiesearch_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ActivitySearchResults(abc_learning_searches.ActivitySearchResults, osid_searches.OsidSearchResults):
    """This interface provides a means to capture results of a search."""

    def get_activities(self):
        """Gets the activity list resulting from the search.

        return: (osid.learning.ActivityList) - the activity list
        raise:  IllegalState - list already retrieved
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    activities = property(fget=get_activities)

    def get_activity_query_inspector(self):
        """Gets the inspector for the query to examine the terms used in the search.

        return: (osid.learning.ActivityQueryInspector) - the query
                inspector
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    activity_query_inspector = property(fget=get_activity_query_inspector)

    @utilities.arguments_not_none
    def get_activity_search_results_record(self, activitiesearch_record_type):
        """Gets the activity search results record corresponding to the given activity search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    activitiesearch_record_type (osid.type.Type): an
                activity search record type
        return: (osid.learning.records.ActivitySearchResultsRecord) -
                the activity search results record
        raise:  NullArgument - ``activitiesearch_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_search_record_type(activitiesearch_record_type)``
                is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ProficiencySearch(abc_learning_searches.ProficiencySearch, osid_searches.OsidSearch):
    """The search interface for governing proficiency searches."""

    @utilities.arguments_not_none
    def search_among_proficiencies(self, proficiency_ids):
        """Execute this search among the given list of proficiencies.

        arg:    proficiency_ids (osid.id.IdList): list of proficiencies
        raise:  NullArgument - ``proficiency_ids`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_proficiency_results(self, proficiency_search_order):
        """Specify an ordering to the search results.

        arg:    proficiency_search_order
                (osid.learning.ProficiencySearchOrder): proficiency
                search order
        raise:  NullArgument - ``proficiency_search_order`` is ``null``
        raise:  Unsupported - ``proficiency_search_order`` is not of
                this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_proficiency_search_record(self, proficiency_search_record_type):
        """Gets the proficiency search record corresponding to the given proficiency search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    proficiency_search_record_type (osid.type.Type): a
                proficiency search record type
        return: (osid.learning.records.ProficiencySearchRecord) - the
                proficiency search record
        raise:  NullArgument - ``proficiency_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(proficiency_search_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ProficiencySearchResults(abc_learning_searches.ProficiencySearchResults, osid_searches.OsidSearchResults):
    """This interface provides a means to capture results of a search."""

    def get_proficiencies(self):
        """Gets the proficiency list resulting from a search.

        return: (osid.learning.ProficiencyList) - the proficiency list
        raise:  IllegalState - list already retrieved
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    proficiencies = property(fget=get_proficiencies)

    def get_proficiency_query_inspector(self):
        """Gets the inspector for the query to examine the terms used in the search.

        return: (osid.learning.ProficiencyQueryInspector) - the
                proficiency query inspector
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    proficiency_query_inspector = property(fget=get_proficiency_query_inspector)

    @utilities.arguments_not_none
    def get_proficiency_search_results_record(self, proficiency_search_record_type):
        """Gets the proficiency search results record corresponding to the given proficiency search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    proficiency_search_record_type (osid.type.Type): a
                proficiency search record type
        return: (osid.learning.records.ProficiencySearchResultsRecord) -
                the proficiency search results record
        raise:  NullArgument - ``proficiency_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(proficiency_search_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ObjectiveBankSearch(abc_learning_searches.ObjectiveBankSearch, osid_searches.OsidSearch):
    """The interface for governing objective bank searches."""

    @utilities.arguments_not_none
    def search_among_objective_banks(self, objective_bank_ids):
        """Execute this search among the given list of objective banks.

        arg:    objective_bank_ids (osid.id.IdList): list of objective
                banks
        raise:  NullArgument - ``objective bank_ids`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_objective_bank_results(self, objective_bank_search_order):
        """Specify an ordering to the search results.

        arg:    objective_bank_search_order
                (osid.learning.ObjectiveBankSearchOrder): objective bank
                search order
        raise:  NullArgument - ``objective_bank_search_order`` is
                ``null``
        raise:  Unsupported - ``objective_bank_search_order`` is not of
                this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_objective_bank_search_record(self, objective_bank_search_record_type):
        """Gets the objective bank search record corresponding to the given objective bank search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    objective_bank_search_record_type (osid.type.Type): an
                objective bank search record type
        return: (osid.learning.records.ObjectiveBankSearchRecord) - the
                objective bank search record
        raise:  NullArgument - ``objective_bank_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_search_record_type(objective
                bank_search_record_type)`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ObjectiveBankSearchResults(abc_learning_searches.ObjectiveBankSearchResults, osid_searches.OsidSearchResults):
    """This interface provides a means to capture results of a search."""

    def get_objective_banks(self):
        """Gets the objective bank list resulting from the search.

        return: (osid.learning.ObjectiveBankList) - the objective bank
                list
        raise:  IllegalState - list already retrieved
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_banks = property(fget=get_objective_banks)

    def get_objective_bank_query_inspector(self):
        """Gets the inspector for the query to examine the terms used in the search.

        return: (osid.learning.ObjectiveBankQueryInspector) - the query
                inspector
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    objective_bank_query_inspector = property(fget=get_objective_bank_query_inspector)

    @utilities.arguments_not_none
    def get_objective_bank_search_results_record(self, objective_bank_search_record_type):
        """Gets the objective bank search results record corresponding to the given objective bank search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    objective_bank_search_record_type (osid.type.Type): an
                objective bank search record type
        return: (osid.learning.records.ObjectiveBankSearchResultsRecord)
                - the objective bank search results record
        raise:  NullArgument - ``objective_bank_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_search_record_type(objective
                bank_search_record_type)`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



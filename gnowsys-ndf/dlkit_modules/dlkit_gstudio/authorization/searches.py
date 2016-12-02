"""GStudio implementations of authorization searches."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.authorization import searches as abc_authorization_searches
from ..osid import searches as osid_searches




class AuthorizationSearch(abc_authorization_searches.AuthorizationSearch, osid_searches.OsidSearch):
    """``AuthorizationSearch`` defines the interface for specifying authorization search options."""

    @utilities.arguments_not_none
    def search_among_authorizations(self, authorization_ids):
        """Execute this search among the given list of authorizations.

        arg:    authorization_ids (osid.id.IdList): list of
                authorizations
        raise:  NullArgument - ``authorization_ids`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_authorization_results(self, authorization_search_order):
        """Specify an ordering to the search results.

        arg:    authorization_search_order
                (osid.authorization.AuthorizationSearchOrder):
                authorization search order
        raise:  NullArgument - ``authorization_search_order`` is
                ``null``
        raise:  Unsupported - ``authorization_search_order`` is not of
                this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorization_search_record(self, authorization_search_record_type):
        """Gets the authorization search record corresponding to the given authorization search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    authorization_search_record_type (osid.type.Type): an
                authorization search record type
        return: (osid.authorization.records.AuthorizationSearchRecord) -
                the authorization search record
        raise:  NullArgument - ``authorization_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(authorization_search_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AuthorizationSearchResults(abc_authorization_searches.AuthorizationSearchResults, osid_searches.OsidSearchResults):
    """This interface provides a means to capture results of a search."""

    def get_authorizations(self):
        """Gets the authorization list resulting from the search.

        return: (osid.authorization.AuthorizationList) - the
                authorization list
        raise:  IllegalState - list has already been retrieved
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    authorizations = property(fget=get_authorizations)

    def get_authorization_query_inspector(self):
        """Gets the inspector for the query to examine the terms used in the search.

        return: (osid.authorization.AuthorizationQueryInspector) - the
                query inspector
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    authorization_query_inspector = property(fget=get_authorization_query_inspector)

    @utilities.arguments_not_none
    def get_authorization_search_results_record(self, authorization_search_record_type):
        """Gets the authorization search results record corresponding to the given authorization search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    authorization_search_record_type (osid.type.Type): an
                authorization search record type
        return:
                (osid.authorization.records.AuthorizationSearchResultsRe
                cord) - the authorization search results record
        raise:  NullArgument - ``authorization_search_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(authorization_search_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class VaultSearch(abc_authorization_searches.VaultSearch, osid_searches.OsidSearch):
    """The interface for governing vault searches."""

    @utilities.arguments_not_none
    def search_among_vaults(self, vault_ids):
        """Execute this search among the given list of vaults.

        arg:    vault_ids (osid.id.IdList): list of vaults
        raise:  NullArgument - ``vault_ids`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_vault_results(self, vault_search_order):
        """Specify an ordering to the search results.

        arg:    vault_search_order
                (osid.authorization.VaultSearchOrder): vault search
                order
        raise:  NullArgument - ``vault_search_order`` is ``null``
        raise:  Unsupported - ``vault_search_order`` is not of this
                service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_vault_search_record(self, vault_search_record_type):
        """Gets the vault search record corresponding to the given vault search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    vault_search_record_type (osid.type.Type): a vault
                search record type
        return: (osid.authorization.records.VaultSearchRecord) - the
                vault search record
        raise:  NullArgument - ``vault_search_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(vault_search_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class VaultSearchResults(abc_authorization_searches.VaultSearchResults, osid_searches.OsidSearchResults):
    """This interface provides a means to capture results of a search."""

    def get_vaults(self):
        """Gets the vault list resulting from the search.

        return: (osid.authorization.VaultList) - the vault list
        raise:  IllegalState - list has already been retrieved
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vaults = property(fget=get_vaults)

    def get_vault_query_inspector(self):
        """Gets the inspector for the query to examine the terms used in the search.

        return: (osid.authorization.VaultQueryInspector) - the vault
                query inspector
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault_query_inspector = property(fget=get_vault_query_inspector)

    @utilities.arguments_not_none
    def get_vault_search_results_record(self, vault_search_record_type):
        """Gets the vault search results record corresponding to the given vault search record ``Type``.

        This method is used to retrieve an object implementing the
        requested record.

        arg:    vault_search_record_type (osid.type.Type): a vault
                search record type
        return: (osid.authorization.records.VaultSearchResultsRecord) -
                the vault search results record
        raise:  NullArgument - ``vault_search_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(vault_search_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



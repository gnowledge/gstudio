"""GStudio implementations of authorization queries."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.authorization import queries as abc_authorization_queries
from ..id.objects import IdList
from ..osid import queries as osid_queries
from ..primitives import Id
from ..utilities import get_registry
from dlkit.abstract_osid.osid import errors




class AuthorizationQuery(abc_authorization_queries.AuthorizationQuery, osid_queries.OsidRelationshipQuery):
    """The query for authorizations."""

    def __init__(self, runtime):
        self._namespace = 'authorization.Authorization'
        self._runtime = runtime
        record_type_data_sets = get_registry('AUTHORIZATION_RECORD_TYPES', runtime)
        self._all_supported_record_type_data_sets = record_type_data_sets
        self._all_supported_record_type_ids = []
        for data_set in record_type_data_sets:
            self._all_supported_record_type_ids.append(str(Id(**record_type_data_sets[data_set])))
        osid_queries.OsidObjectQuery.__init__(self, runtime)


    @utilities.arguments_not_none
    def match_explicit_authorizations(self, match):
        """Matches explciit authorizations.

        arg:    match (boolean): ``true`` to match explicit
                authorizations, ``false`` to match implciit
                authorizations
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_explicit_authorizations_terms(self):
        """Clears the explicit authorization query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    explicit_authorizations_terms = property(fdel=clear_explicit_authorizations_terms)

    @utilities.arguments_not_none
    def match_related_authorization_id(self, id_, match):
        """Adds an ``Id`` to match explicit or implicitly related authorizations depending on ``matchExplicitAuthorizations()``.

        Multiple ``Ids`` can be added to perform a boolean ``OR`` among
        them.

        arg:    id (osid.id.Id): ``Id`` to match
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_related_authorization_id_terms(self):
        """Clears the related authorization ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    related_authorization_id_terms = property(fdel=clear_related_authorization_id_terms)

    def supports_related_authorization_query(self):
        """Tests if an ``AuthorizationQuery`` is available.

        return: (boolean) - ``true`` if an authorization query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_related_authorization_query(self, match):
        """Gets the authorization query.

        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        return: (osid.authorization.AuthorizationQuery) - the
                ``AuthorizationQuery``
        raise:  Unimplemented -
                ``supports_related_authorization_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_related_authorization_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def clear_related_authorization_terms(self):
        """Clears the related authorization query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    related_authorization_terms = property(fdel=clear_related_authorization_terms)

    @utilities.arguments_not_none
    def match_resource_id(self, resource_id, match):
        """Matches the resource identified by the given ``Id``.

        arg:    resource_id (osid.id.Id): the ``Id`` of the ``Resource``
        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        raise:  NullArgument - ``resource_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_resource_id_terms(self):
        """Clears the resource ``Id`` query terms.

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

    @utilities.arguments_not_none
    def get_resource_query(self, match):
        """Gets the resource query.

        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        return: (osid.resource.ResourceQuery) - the ``ResourceQuery``
        raise:  Unimplemented - ``supports_resource_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_resource_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_resource(self, match):
        """Matches authorizations that have any resource.

        arg:    match (boolean): ``true`` to match authorizations with
                any resource, ``false`` to match authorizations with no
                resource
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_resource_terms(self):
        """Clears the resource query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    resource_terms = property(fdel=clear_resource_terms)

    @utilities.arguments_not_none
    def match_trust_id(self, trust_id, match):
        """Matches the trust identified by the given ``Id``.

        arg:    trust_id (osid.id.Id): the ``Id`` of the ``Trust``
        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        raise:  NullArgument - ``trust_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_trust_id(self, match):
        """Matches authorizations that have any trust defined.

        arg:    match (boolean): ``true`` to match authorizations with
                any trust, ``false`` to match authorizations with no
                trusts
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_trust_id_terms(self):
        """Clears the trust ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    trust_id_terms = property(fdel=clear_trust_id_terms)

    @utilities.arguments_not_none
    def match_agent_id(self, agent_id, match):
        """Matches the agent identified by the given ``Id``.

        arg:    agent_id (osid.id.Id): the Id of the ``Agent``
        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        raise:  NullArgument - ``agent_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_agent_id_terms(self):
        """Clears the agent ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    agent_id_terms = property(fdel=clear_agent_id_terms)

    def supports_agent_query(self):
        """Tests if an ``AgentQuery`` is available.

        return: (boolean) - ``true`` if an agent query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_agent_query(self, match):
        """Gets the agent query.

        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        return: (osid.authentication.AgentQuery) - the ``AgentQuery``
        raise:  Unimplemented - ``supports_agent_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def match_any_agent(self, match):
        """Matches authorizations that have any agent.

        arg:    match (boolean): ``true`` to match authorizations with
                any agent, ``false`` to match authorizations with no
                agent
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_agent_terms(self):
        """Clears the agent query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    agent_terms = property(fdel=clear_agent_terms)

    @utilities.arguments_not_none
    def match_function_id(self, function_id, match):
        """Matches the function identified by the given ``Id``.

        arg:    function_id (osid.id.Id): the Id of the ``Function``
        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        raise:  NullArgument - ``function_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_function_id_terms(self):
        """Clears the function ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    function_id_terms = property(fdel=clear_function_id_terms)

    def supports_function_query(self):
        """Tests if a ``FunctionQuery`` is available.

        return: (boolean) - ``true`` if a function query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_function_query(self, match):
        """Gets the function query.

        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        return: (osid.authorization.FunctionQuery) - the
                ``FunctinQuery``
        raise:  Unimplemented - ``supports_function_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_function_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def clear_function_terms(self):
        """Clears the function query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    function_terms = property(fdel=clear_function_terms)

    @utilities.arguments_not_none
    def match_qualifier_id(self, qualifier_id, match):
        """Matches the qualifier identified by the given ``Id``.

        arg:    qualifier_id (osid.id.Id): the Id of the ``Qualifier``
        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        raise:  NullArgument - ``qualifier_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_qualifier_id_terms(self):
        """Clears the qualifier ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    qualifier_id_terms = property(fdel=clear_qualifier_id_terms)

    def supports_qualifier_query(self):
        """Tests if a ``QualifierQuery`` is available.

        return: (boolean) - ``true`` if a qualifier query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_qualifier_query(self, match):
        """Gets the qualiier query.

        arg:    match (boolean): ``true`` if a positive match, ``false``
                for a negative match
        return: (osid.authorization.QualifierQuery) - the
                ``QualifierQuery``
        raise:  Unimplemented - ``supports_qualifier_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_qualifier_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def clear_qualifier_terms(self):
        """Clears the qualifier query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    qualifier_terms = property(fdel=clear_qualifier_terms)

    @utilities.arguments_not_none
    def match_vault_id(self, vault_id, match):
        """Sets the vault ``Id`` for this query.

        arg:    vault_id (osid.id.Id): a vault ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``vault_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_vault_id_terms(self):
        """Clears the vault ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault_id_terms = property(fdel=clear_vault_id_terms)

    def supports_vault_query(self):
        """Tests if a ``VaultQuery`` is available.

        return: (boolean) - ``true`` if a vault query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_vault_query(self):
        """Gets the query for a vault.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.authorization.VaultQuery) - the vault query
        raise:  Unimplemented - ``supports_vault_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_vault_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    vault_query = property(fget=get_vault_query)

    def clear_vault_terms(self):
        """Clears the vault query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault_terms = property(fdel=clear_vault_terms)

    @utilities.arguments_not_none
    def get_authorization_query_record(self, authorization_record_type):
        """Gets the authorization query record corresponding to the given ``Authorization`` record ``Type``.

        Multiple retrievals produce a nested ``OR`` term.

        arg:    authorization_record_type (osid.type.Type): an
                authorization record type
        return: (osid.authorization.records.AuthorizationQueryRecord) -
                the authorization query record
        raise:  NullArgument - ``authorization_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(authorization_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class VaultQuery(abc_authorization_queries.VaultQuery, osid_queries.OsidCatalogQuery):
    """This is the query for searching vaults.

    Each method specifies an ``AND`` term while multiple invocations of
    the same method produce a nested ``OR``.

    """

    def __init__(self, runtime):
        self._runtime = runtime


    @utilities.arguments_not_none
    def match_function_id(self, function_id, match):
        """Sets the function ``Id`` for this query.

        arg:    function_id (osid.id.Id): a function ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``function_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_function_id_terms(self):
        """Clears the function ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('functionId')

    function_id_terms = property(fdel=clear_function_id_terms)

    def supports_function_query(self):
        """Tests if a ``FunctionQuery`` is available.

        return: (boolean) - ``true`` if a function query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_function_query(self):
        """Gets the query for a function.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.authorization.FunctionQuery) - the function query
        raise:  Unimplemented - ``supports_function_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_function_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    function_query = property(fget=get_function_query)

    @utilities.arguments_not_none
    def match_any_function(self, match):
        """Matches vaults that have any function.

        arg:    match (boolean): ``true`` to match vaults with any
                function mapping, ``false`` to match vaults with no
                function mapping
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_function_terms(self):
        """Clears the function query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('function')

    function_terms = property(fdel=clear_function_terms)

    @utilities.arguments_not_none
    def match_qualifier_id(self, qualifier_id, match):
        """Sets the qualifier ``Id`` for this query.

        arg:    qualifier_id (osid.id.Id): a qualifier ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``qualifier_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_qualifier_id_terms(self):
        """Clears the qualifier ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('qualifierId')

    qualifier_id_terms = property(fdel=clear_qualifier_id_terms)

    def supports_qualifier_query(self):
        """Tests if a ``QualifierQuery`` is available.

        return: (boolean) - ``true`` if a qualifier query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_qualifier_query(self):
        """Gets the query for a qualifier.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.authorization.QualifierQuery) - the qualifier
                query
        raise:  Unimplemented - ``supports_qualifier_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_qualifier_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    qualifier_query = property(fget=get_qualifier_query)

    @utilities.arguments_not_none
    def match_any_qualifier(self, match):
        """Matches vaults that have any qualifier.

        arg:    match (boolean): ``true`` to match vaults with any
                qualifier mapping, ``false`` to match vaults with no
                qualifier mapping
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_qualifier_terms(self):
        """Clears the qualifier query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('qualifier')

    qualifier_terms = property(fdel=clear_qualifier_terms)

    @utilities.arguments_not_none
    def match_authorization_id(self, authorization_id, match):
        """Sets the authorization ``Id`` for this query.

        arg:    authorization_id (osid.id.Id): an authorization ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``authorization_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_authorization_id_terms(self):
        """Clears the authorization ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('authorizationId')

    authorization_id_terms = property(fdel=clear_authorization_id_terms)

    def supports_authorization_query(self):
        """Tests if an ``AuthorizationQuery`` is available.

        return: (boolean) - ``true`` if an authorization query is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_authorization_query(self):
        """Gets the query for an authorization.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.authorization.AuthorizationQuery) - the
                authorization query
        raise:  Unimplemented - ``supports_authorization_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_authorization_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    authorization_query = property(fget=get_authorization_query)

    @utilities.arguments_not_none
    def match_any_authorization(self, match):
        """Matches vaults that have any authorization.

        arg:    match (boolean): ``true`` to match vaults with any
                authorization mapping, ``false`` to match vaults with no
                authorization mapping
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_authorization_terms(self):
        """Clears the authorization query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('authorization')

    authorization_terms = property(fdel=clear_authorization_terms)

    @utilities.arguments_not_none
    def match_ancestor_vault_id(self, vault_id, match):
        """Sets the vault ``Id`` for this query to match vaults that have the specified vault as an ancestor.

        arg:    vault_id (osid.id.Id): a vault ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for a negative match
        raise:  NullArgument - ``vault_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ancestor_vault_id_terms(self):
        """Clears the ancestor vault ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('ancestorVaultId')

    ancestor_vault_id_terms = property(fdel=clear_ancestor_vault_id_terms)

    def supports_ancestor_vault_query(self):
        """Tests if a ``VaultQuery`` is available.

        return: (boolean) - ``true`` if a vault query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_ancestor_vault_query(self):
        """Gets the query for a vault.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.authorization.VaultQuery) - the vault query
        raise:  Unimplemented - ``supports_ancestor_vault_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_ancestor_vault_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    ancestor_vault_query = property(fget=get_ancestor_vault_query)

    @utilities.arguments_not_none
    def match_any_ancestor_vault(self, match):
        """Matches vaults that have any ancestor.

        arg:    match (boolean): ``true`` to match vaults with any
                ancestor, ``false`` to match root vaults
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_ancestor_vault_terms(self):
        """Clears the ancestor vault query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('ancestorVault')

    ancestor_vault_terms = property(fdel=clear_ancestor_vault_terms)

    @utilities.arguments_not_none
    def match_descendant_vault_id(self, vault_id, match):
        """Sets the vault ``Id`` for this query to match vaults that have the specified vault as a descendant.

        arg:    vault_id (osid.id.Id): a vault ``Id``
        arg:    match (boolean): ``true`` for a positive match,
                ``false`` for negative match
        raise:  NullArgument - ``vault_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_descendant_vault_id_terms(self):
        """Clears the descendant vault ``Id`` query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('descendantVaultId')

    descendant_vault_id_terms = property(fdel=clear_descendant_vault_id_terms)

    def supports_descendant_vault_query(self):
        """Tests if a ``VaultQuery`` is available.

        return: (boolean) - ``true`` if a vault query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_descendant_vault_query(self):
        """Gets the query for a vault.

        Multiple retrievals produce a nested ``OR`` term.

        return: (osid.authorization.VaultQuery) - the vault query
        raise:  Unimplemented - ``supports_descendant_vault_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_descendant_vault_query()`` is ``true``.*

        """
        raise errors.Unimplemented()

    descendant_vault_query = property(fget=get_descendant_vault_query)

    @utilities.arguments_not_none
    def match_any_descendant_vault(self, match):
        """Matches vaults that have any descendant.

        arg:    match (boolean): ``true`` to match vaults with any
                Ddscendant, ``false`` to match leaf vaults
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_descendant_vault_terms(self):
        """Clears the descendant vault query terms.

        *compliance: mandatory -- This method must be implemented.*

        """
        self._clear_terms('descendantVault')

    descendant_vault_terms = property(fdel=clear_descendant_vault_terms)

    @utilities.arguments_not_none
    def get_vault_query_record(self, vault_record_type):
        """Gets the vault query record corresponding to the given ``Vault`` record ``Type``.

        Multiple record retrievals produce a nested ``OR`` term.

        arg:    vault_record_type (osid.type.Type): a vault record type
        return: (osid.authorization.records.VaultQueryRecord) - the
                vault query record
        raise:  NullArgument - ``vault_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(vault_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



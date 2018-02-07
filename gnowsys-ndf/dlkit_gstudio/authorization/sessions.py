"""GStudio implementations of authorization sessions."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification


from . import objects
from .. import utilities
from dlkit.abstract_osid.authorization import sessions as abc_authorization_sessions
from ..osid import sessions as osid_sessions
from ..osid.sessions import OsidSession
from dlkit.abstract_osid.osid import errors



from gnowsys_ndf.ndf.models import Group, Author


class AuthorizationSession(abc_authorization_sessions.AuthorizationSession, osid_sessions.OsidSession):
    """This is the basic session for verifying authorizations."""

    def __init__(self, catalog_id=None, proxy=None, runtime=None, **kwargs):
        self._catalog_class = objects.Vault
        self._session_name = 'AuthorizationSession'
        self._catalog_name = 'Vault'
        OsidSession._init_object(
            self,
            catalog_id,
            proxy,
            runtime,
            db_name='authorization',
            cat_name='Vault',
            cat_class=objects.Vault)
        self._kwargs = kwargs

    def get_vault_id(self):
        """Gets the ``Vault``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Vault Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault_id = property(fget=get_vault_id)

    def get_vault(self):
        """Gets the ``Vault`` associated with this session.

        return: (osid.authorization.Vault) - the ``Vault`` associated
                with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault = property(fget=get_vault)

    def can_access_authorizations(self):
        """Tests if this user can perform authorization checks.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer lookup
        operations to unauthorized users.

        return: (boolean) - ``false`` if authorization methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def is_authorized(self, agent_id, function_id=None, qualifier_id=None):
        """Determines if the given agent is authorized.

        An agent is authorized if an active authorization exists whose
        ``Agent,`` ``Function`` and ``Qualifier`` matches the supplied
        parameters. Authorizations may be defined using groupings or
        hieratchical structures for both the ``Agent`` and the
        ``Qualifier`` but are queried in the de-nornmalized form.

        The ``Agent`` is generally determined through the use of an
        Authentication OSID. The ``Function`` and ``Qualifier`` are
        already known as they map to the desired authorization to
        validate.

        arg:    agent_id (osid.id.Id): the ``Id`` of an ``Agent``
        arg:    function_id (osid.id.Id): the ``Id`` of a ``Function``
        arg:    qualifier_id (osid.id.Id): the ``Id`` of a ``Qualifier``
        return: (boolean) - ``true`` if the user is authorized,
                ``false`` othersise
        raise:  NotFound - ``function_id`` is not found
        raise:  NullArgument - ``agent_id`` , ``function_id`` or
                ``qualifier_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure making request
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: Authorizations may be stored in a
        normalized form with respect to various Resources and created
        using specific nodes in a ``Function`` or ``Qualifer``
        hierarchy. The provider needs to maintain a de-normalized
        implicit authorization store or expand the applicable
        hierarchies on the fly to honor this query.  Querying the
        authorization service may in itself require a separate
        authorization. A ``PermissionDenied`` is a result of this
        authorization failure. If no explicit or implicit authorization
        exists for the queried tuple, this method should return
        ``false``.

        """
        # function_id.namespace gives <service_name>.<type>
        # function_id.identifier gives function name [E.g 'lookup']
        # qualifier_id.identifier gives Group ObjectId
        # agent_id.identifier gives user id [Needs check]
        # Check agent is member/admin of catalog(qualifier object)
        # try:
        #     # agent_id should be django user_id
        #     print "\n agent_id -- ", agent_id
        #     return Group.can_access(int(agent_id.identifier), qualifier_id)
        # except Exception:
        #     return Author.can_access(agent_id, qualifier_id)

        # agent_id_dict = utilities.split_osid_id(str(agent_id))
        # return bool(Group.get_group_name_id(unicode(agent_id_dict['identifier']), get_obj=True))

        return bool(Group.get_group_name_id(unicode(agent_id.identifier), get_obj=True))


    @utilities.arguments_not_none
    def get_authorization_condition(self, function_id):
        """Gets the ``AuthorizationCondition`` for making conditional authorization checks.

        arg:    function_id (osid.id.Id): the ``Id`` of a ``Function``
        return: (osid.authorization.AuthorizationCondition) - an
                authorization condition
        raise:  NotFound - ``function_id`` is not found
        raise:  NullArgument - ``function_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure making request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def is_authorized_on_condition(self, agent_id, function_id, qualifier_id, condition):
        """Determines if the given agent is authorized.

        An agent is authorized if an active authorization exists whose
        ``Agent,`` ``Function`` and ``Qualifier`` matches the supplied
        parameters. Authorizations may be defined using groupings or
        hieratchical structures for both the ``Agent`` and the
        ``Qualifier`` but are queried in the de-nornmalized form.

        The ``Agent`` is generally determined through the use of an
        Authentication OSID. The ``Function`` and ``Qualifier`` are
        already known as they map to the desired authorization to
        validate.

        arg:    agent_id (osid.id.Id): the ``Id`` of an ``Agent``
        arg:    function_id (osid.id.Id): the ``Id`` of a ``Function``
        arg:    qualifier_id (osid.id.Id): the ``Id`` of a ``Qualifier``
        arg:    condition (osid.authorization.AuthorizationCondition):
                an authorization condition
        return: (boolean) - ``true`` if the user is authorized,
                ``false`` othersise
        raise:  NotFound - ``function_id`` is not found
        raise:  NullArgument - ``agent_id`` , ``function_id,
                qualifier_id`` , or ``condition`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure making request
        raise:  Unsupported - ``condition`` is not of this service
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: Authorizations may be stored in a
        normalized form with respect to various Resources and created
        using specific nodes in a ``Function`` or ``Qualifer``
        hierarchy. The provider needs to maintain a de-normalized
        implicit authorization store or expand the applicable
        hierarchies on the fly to honor this query.  Querying the
        authorization service may in itself require a separate
        authorization. A ``PermissionDenied`` is a result of this
        authorization failure. If no explicit or implicit authorization
        exists for the queried tuple, this method should return
        ``false``.

        """
        raise errors.Unimplemented()


class AuthorizationLookupSession(abc_authorization_sessions.AuthorizationLookupSession, osid_sessions.OsidSession):
    """This session defines methods to search and retrieve ``Authorization`` mappings."""

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_vault_id(self):
        """Gets the ``Vault``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Vault Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault_id = property(fget=get_vault_id)

    def get_vault(self):
        """Gets the ``Vault`` associated with this session.

        return: (osid.authorization.Vault) - the ``Vault`` associated
                with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault = property(fget=get_vault)

    def can_lookup_authorizations(self):
        """Tests if this user can perform authorization lookups.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer lookup
        operations to unauthorized users.

        return: (boolean) - ``false`` if lookup methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_comparative_authorization_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_authorization_view(self):
        """A complete view of the ``Authorization`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_federated_vault_view(self):
        """Federates the view for methods in this session.

        A federated view will include authorizations in vaults which are
        children of this vault in the vault hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_isolated_vault_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts lookups to this vault only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_effective_authorization_view(self):
        """Only authorizations whose effective dates are current are returned by methods in this session.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_any_effective_authorization_view(self):
        """All authorizations of any effective dates are returned by all methods in this session.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_implicit_authorization_view(self):
        """Sets the view for methods in this session to implicit authorizations.

        An implicit view will include authorizations derived from other
        authorizations as a result of the ``Qualifier,`` ``Function`` or
        ``Resource`` hierarchies. This method is the opposite of
        ``explicitAuthorizationView()``.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_explicit_authorization_view(self):
        """Sets the view for methods in this session to explicit authorizations.

        An explicit view includes only those authorizations that were
        explicitly defined and not implied. This method is the opposite
        of ``implicitAuthorizationView()``.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorization(self, authorization_id):
        """Gets the ``Authorization`` specified by its ``Id``.

        In plenary mode, the exact ``Id`` is found or a ``NotFound``
        results. Otherwise, the returned ``Authorization`` may have a
        different ``Id`` than requested, such as the case where a
        duplicate ``Id`` was assigned to an ``Authorization`` and
        retained for compatibility.

        arg:    authorization_id (osid.id.Id): the ``Id`` of the
                ``Authorization`` to retrieve
        return: (osid.authorization.Authorization) - the returned
                ``Authorization``
        raise:  NotFound - no ``Authorization`` found with the given
                ``Id``
        raise:  NullArgument - ``authorization_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_by_ids(self, authorization_ids):
        """Gets an ``AuthorizationList`` corresponding to the given ``IdList``.

        In plenary mode, the returned list contains all of the
        authorizations specified in the ``Id`` list, in the order of the
        list, including duplicates, or an error results if an ``Id`` in
        the supplied list is not found or inaccessible. Otherwise,
        inaccessible ``Authorizations`` may be omitted from the list and
        may present the elements in any order including returning a
        unique set.

        arg:    authorization_ids (osid.id.IdList): the list of ``Ids``
                to retrieve
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization list``
        raise:  NotFound - an ``Id was`` not found
        raise:  NullArgument - ``authorization_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_by_genus_type(self, authorization_genus_type):
        """Gets an ``AuthorizationList`` corresponding to the given authorization genus ``Type`` which does not include authorizations of genus types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known
        authorizations or an error results. Otherwise, the returned list
        may contain only those authorizations that are accessible
        through this session.

        arg:    authorization_genus_type (osid.type.Type): an
                authorization genus type
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization`` list
        raise:  NullArgument - ``authorization_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_by_parent_genus_type(self, authorization_genus_type):
        """Gets an ``AuthorizationList`` corresponding to the given authorization genus ``Type`` and include authorizations of genus types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known
        authorizations or an error results. Otherwise, the returned list
        may contain only those authorizations that are accessible
        through this session.

        arg:    authorization_genus_type (osid.type.Type): an
                authorization genus type
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization`` list
        raise:  NullArgument - ``authorization_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_by_record_type(self, authorization_record_type):
        """Gets an ``AuthorizationList`` containing the given authorization record ``Type``.

        In plenary mode, the returned list contains all known
        authorizations or an error results. Otherwise, the returned list
        may contain only those authorizations that are accessible
        through this session.

        arg:    authorization_record_type (osid.type.Type): an
                authorization record type
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization`` list
        raise:  NullArgument - ``authorization_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_on_date(self, from_, to):
        """Gets an ``AuthorizationList`` effective during the entire given date range inclusive but not confined to the date range.

        arg:    from (osid.calendaring.DateTime): starting date
        arg:    to (osid.calendaring.DateTime): ending date
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization`` list
        raise:  InvalidArgument - ``from`` is greater than ``to``
        raise:  NullArgument - ``from`` or ``to`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_for_resource(self, resource_id):
        """Gets a list of ``Authorizations`` associated with a given resource.

        Authorizations related to the given resource, including those
        related through an ``Agent,`` are returned. In plenary mode, the
        returned list contains all known authorizations or an error
        results. Otherwise, the returned list may contain only those
        authorizations that are accessible through this session.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization list``
        raise:  NullArgument - ``resource_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_for_resource_on_date(self, resource_id, from_, to):
        """Gets an ``AuthorizationList`` effective during the entire given date range inclusive but not confined to the date range.

        Authorizations related to the given resource, including those
        related through an ``Agent,`` are returned.

        In plenary mode, the returned list contains all known
        authorizations or an error results. Otherwise, the returned list
        may contain only those authorizations that are accessible
        through this session.

        In effective mode, authorizations are returned that are
        currently effective. In any effective mode, active
        authorizations and those currently expired are returned.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        arg:    from (osid.calendaring.DateTime): starting date
        arg:    to (osid.calendaring.DateTime): ending date
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization`` list
        raise:  InvalidArgument - ``from`` is greater than ``to``
        raise:  NullArgument - ``resource_id, from`` or ``to`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_for_agent(self, agent_id):
        """Gets a list of ``Authorizations`` associated with a given agent.

        In plenary mode, the returned list contains all known
        authorizations or an error results. Otherwise, the returned list
        may contain only those authorizations that are accessible
        through this session.

        arg:    agent_id (osid.id.Id): an agent ``Id``
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization list``
        raise:  NullArgument - ``agent_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_for_agent_on_date(self, agent_id, from_, to):
        """Gets an ``AuthorizationList`` for the given agent and effective during the entire given date range inclusive but not confined to the date range.

        arg:    agent_id (osid.id.Id): an agent ``Id``
        arg:    from (osid.calendaring.DateTime): starting date
        arg:    to (osid.calendaring.DateTime): ending date
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization`` list
        raise:  InvalidArgument - ``from`` is greater than ``to``
        raise:  NullArgument - ``agent_id, from`` or ``to`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_for_function(self, function_id):
        """Gets a list of ``Authorizations`` associated with a given function.

        In plenary mode, the returned list contains all known
        authorizations or an error results. Otherwise, the returned list
        may contain only those authorizations that are accessible
        through this session.

        arg:    function_id (osid.id.Id): a function ``Id``
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization list``
        raise:  NullArgument - ``function_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_for_function_on_date(self, function_id, from_, to):
        """Gets an ``AuthorizationList`` for the given function and effective during the entire given date range inclusive but not confined to the date range.

        arg:    function_id (osid.id.Id): a function ``Id``
        arg:    from (osid.calendaring.DateTime): starting date
        arg:    to (osid.calendaring.DateTime): ending date
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization`` list
        raise:  InvalidArgument - ``from`` is greater than ``to``
        raise:  NullArgument - ``function_id, from`` or ``to`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_for_resource_and_function(self, resource_id, function_id):
        """Gets a list of ``Authorizations`` associated with a given resource.

        Authorizations related to the given resource, including those
        related through an ``Agent,`` are returned. In plenary mode, the
        returned list contains all known authorizations or an error
        results. Otherwise, the returned list may contain only those
        authorizations that are accessible through this session.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        arg:    function_id (osid.id.Id): a function ``Id``
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization list``
        raise:  NullArgument - ``resource_id`` or ``function_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_for_resource_and_function_on_date(self, resource_id, function_id, from_, to):
        """Gets an ``AuthorizationList`` effective during the entire given date range inclusive but not confined to the date range.

        Authorizations related to the given resource, including those
        related through an ``Agent,`` are returned.

        In plenary mode, the returned list contains all known
        authorizations or an error results. Otherwise, the returned list
        may contain only those authorizations that are accessible
        through this session.

        In effective mode, authorizations are returned that are
        currently effective. In any effective mode, active
        authorizations and those currently expired are returned.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        arg:    function_id (osid.id.Id): a function ``Id``
        arg:    from (osid.calendaring.DateTime): starting date
        arg:    to (osid.calendaring.DateTime): ending date
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization`` list
        raise:  InvalidArgument - ``from`` is greater than ``to``
        raise:  NullArgument - ``resource_id, function_id, from`` or
                ``to`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_for_agent_and_function(self, agent_id, function_id):
        """Gets a list of ``Authorizations`` associated with a given agent.

        Authorizations related to the given resource, including those
        related through an ``Agent,`` are returned. In plenary mode, the
        returned list contains all known authorizations or an error
        results. Otherwise, the returned list may contain only those
        authorizations that are accessible through this session.

        arg:    agent_id (osid.id.Id): an agent ``Id``
        arg:    function_id (osid.id.Id): a function ``Id``
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization list``
        raise:  NullArgument - ``agent_id`` or ``function_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_for_agent_and_function_on_date(self, agent_id, function_id, from_, to):
        """Gets an ``AuthorizationList`` for the given agent and effective during the entire given date range inclusive but not confined to the date range.

        arg:    agent_id (osid.id.Id): an agent ``Id``
        arg:    function_id (osid.id.Id): a function ``Id``
        arg:    from (osid.calendaring.DateTime): starting date
        arg:    to (osid.calendaring.DateTime): ending date
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization`` list
        raise:  InvalidArgument - ``from`` is greater than ``to``
        raise:  NullArgument - ``agent_id, function_id, from`` or ``to``
                is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorizations_by_qualifier(self, qualifier_id):
        """Gets a list of ``Authorizations`` associated with a given qualifier.

        In plenary mode, the returned list contains all known
        authorizations or an error results. Otherwise, the returned list
        may contain only those authorizations that are accessible
        through this session.

        arg:    qualifier_id (osid.id.Id): a qualifier ``Id``
        return: (osid.authorization.AuthorizationList) - the returned
                ``Authorization list``
        raise:  NullArgument - ``qualifier_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_explicit_authorization(self, authorization_id):
        """Gets the explicit ``Authorization`` that generated the given implicit authorization.

        If the given ``Authorization`` is explicit, then the same
        ``Authorization`` is returned.

        arg:    authorization_id (osid.id.Id): an authorization
        return: (osid.authorization.Authorization) - the explicit
                ``Authorization``
        raise:  NotFound - ``authorization_id`` is not found
        raise:  NullArgument - ``authorization_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_authorizations(self):
        """Geta all ``Authorizations``.

        In plenary mode, the returned list contains all known
        authorizations or an error results. Otherwise, the returned list
        may contain only those authorizations that are accessible
        through this session.

        return: (osid.authorization.AuthorizationList) - a list of
                ``Authorizations``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    authorizations = property(fget=get_authorizations)


class AuthorizationQuerySession(abc_authorization_sessions.AuthorizationQuerySession, osid_sessions.OsidSession):
    """This session provides methods for searching ``Authorization`` objects.

    The search query is constructed using the ``AuthorizationQuery``.

    This session defines views that offer differing behaviors for
    searching.

      * federated view: searches include authorizations in ``Vaults`` of
        which this vault is a ancestor in the vault hierarchy
      * isolated view: searches are restricted to authorizations in this
        ``Vault``
      * implicit authorization view: authorizations include implicit
        authorizations
      * explicit authorization view: only explicit authorizations are
        returned


    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_vault_id(self):
        """Gets the ``Vault``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Vault Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault_id = property(fget=get_vault_id)

    def get_vault(self):
        """Gets the ``Vault`` associated with this session.

        return: (osid.authorization.Vault) - the ``Vault`` associated
                with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault = property(fget=get_vault)

    def can_search_authorizations(self):
        """Tests if this user can perform authorization searches.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer search
        operations to unauthorized users.

        return: (boolean) - ``false`` if search methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_federated_vault_view(self):
        """Federates the view for methods in this session.

        A federated view will include authorizations in vaults which are
        children of this vault in the vault hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_isolated_vault_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts searches to this vault only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_implicit_authorization_view(self):
        """Sets the view for methods in this session to implicit authorizations.

        An implicit view will include authorizations derived from other
        authorizations as a result of the ``Qualifier,`` ``Function`` or
        ``Resource`` hierarchies. This method is the opposite of
        ``explicit_aut``

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_explicit_authorization_view(self):
        """Sets the view for methods in this session to explicit authorizations.

        An explicit view includes only those authorizations that were
        explicitly defined and not implied. This method is the opposite
        of ``implicitAuthorizationView()``.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def get_authorization_query(self):
        """Gets an authorization query.

        return: (osid.authorization.AuthorizationQuery) - the
                authorization query
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    authorization_query = property(fget=get_authorization_query)

    @utilities.arguments_not_none
    def get_authorizations_by_query(self, authorization_query):
        """Gets a list of ``Authorizations`` matching the given query.

        arg:    authorization_query
                (osid.authorization.AuthorizationQuery): the
                authorization query
        return: (osid.authorization.AuthorizationList) - the returned
                ``AuthorizationList``
        raise:  NullArgument - ``authorization_query`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``authorization_query`` is not of this
                service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AuthorizationAdminSession(abc_authorization_sessions.AuthorizationAdminSession, osid_sessions.OsidSession):
    """This session creates, updates, and deletes ``Authorizations``.

    The data for create and update is provided by the consumer via the
    form object. ``OsidForms`` are requested for each create or update
    and may not be reused.

    Create and update operations differ in their usage. To create an
    ``Authorization,`` an ``AuthorizationForm`` is requested using
    ``get_authorization_form_for_create()`` specifying the desired
    relationship peers and record ``Types`` or none if no record
    ``Types`` are needed. The returned ``AuthorizationForm`` will
    indicate that it is to be used with a create operation and can be
    used to examine metdata or validate data prior to creation. Once the
    ``AuthorizationForm`` is submiited to a create operation, it cannot
    be reused with another create operation unless the first operation
    was unsuccessful. Each ``AuthorizationForm`` corresponds to an
    attempted transaction.

    For updates, ``AuthorizationForms`` are requested to the
    ``Authorization``  ``Id`` that is to be updated using
    ``getAuthorizationFormForUpdate()``. Similarly, the
    ``AuthorizationForm`` has metadata about the data that can be
    updated and it can perform validation before submitting the update.
    The ``AuthorizationForm`` can only be used once for a successful
    update and cannot be reused.

    The delete operations delete ``Authorizations``. To unmap an
    ``Authorization`` from the current ``Vault,`` the
    ``AuthorizationVaultAssignmentSession`` should be used. These delete
    operations attempt to remove the ``Authorization`` itself thus
    removing it from all known ``Vault`` catalogs.

    This session includes an ``Id`` aliasing mechanism to assign an
    external ``Id`` to an internally assigned Id.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_vault_id(self):
        """Gets the ``Vault``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Vault Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault_id = property(fget=get_vault_id)

    def get_vault(self):
        """Gets the ``Vault`` associated with this session.

        return: (osid.authorization.Vault) - the ``Vault`` associated
                with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault = property(fget=get_vault)

    def can_create_authorizations(self):
        """Tests if this user can create ``Authorizations``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer create
        operations to unauthorized users.

        return: (boolean) - ``false`` if ``Authorization`` creation is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_create_authorization_with_record_types(self, authorization_record_types):
        """Tests if this user can create a single ``Authorization`` using the desired record types.

        While ``AuthorizationManager.getAuthorizationRecordTypes()`` can
        be used to examine which records are supported, this method
        tests which record(s) are required for creating a specific
        ``Authorization``. Providing an empty array tests if an
        ``Authorization`` can be created with no records.

        arg:    authorization_record_types (osid.type.Type[]): array of
                authorization record types
        return: (boolean) - ``true`` if ``Authorization`` creation using
                the specified ``Types`` is supported, ``false``
                otherwise
        raise:  NullArgument - ``authorization_record_types`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_authorization_form_for_create_for_agent(self, agent_id, function_id, qualifier_id, authorization_record_types):
        """Gets the authorization form for creating new authorizations.

        A new form should be requested for each create transaction.

        arg:    agent_id (osid.id.Id): the agent ``Id``
        arg:    function_id (osid.id.Id): the function ``Id``
        arg:    qualifier_id (osid.id.Id): the qualifier ``Id``
        arg:    authorization_record_types (osid.type.Type[]): array of
                authorization record types
        return: (osid.authorization.AuthorizationForm) - the
                authorization form
        raise:  NotFound - ``agent_id, function_id`` or ``qualifier_id``
                is not found
        raise:  NullArgument - ``agent_id, function_id, qualifier_id``
                or ``authorization_record_types`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - unable to get form with requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorization_form_for_create_for_resource(self, resource_id, function_id, qualifier_id, authorization_record_types):
        """Gets the authorization form for creating new authorizations.

        A new form should be requested for each create transaction.

        arg:    resource_id (osid.id.Id): the resource ``Id``
        arg:    function_id (osid.id.Id): the function ``Id``
        arg:    qualifier_id (osid.id.Id): the qualifier ``Id``
        arg:    authorization_record_types (osid.type.Type[]): array of
                authorization record types
        return: (osid.authorization.AuthorizationForm) - the
                authorization form
        raise:  NotFound - ``resource_id, function_id`` or
                ``qualifier_id`` is not found
        raise:  NullArgument - ``resource_id, function_id,
                qualifier_id,`` or ``authorization_record_types`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - unable to get form with requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_authorization_form_for_create_for_resource_and_trust(self, resource_id, trust_id, function_id, qualifier_id, authorization_record_types):
        """Gets the authorization form for creating new authorizations.

        A new form should be requested for each create transaction.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        arg:    trust_id (osid.id.Id): an ``Id`` for a circle of trust
        arg:    function_id (osid.id.Id): a function ``Id``
        arg:    qualifier_id (osid.id.Id): the qualifier ``Id``
        arg:    authorization_record_types (osid.type.Type[]): array of
                authorization record types
        return: (osid.authorization.AuthorizationForm) - the
                authorization form
        raise:  NotFound - ``resource_id, trust_id, function_id`` , or
                ``qualifierid`` is not found
        raise:  NullArgument - ``resource_id, trust_id`` ,
                ``resource_id, qualifier_id`` or
                ``authorization_record_types`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - unable to get form with requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def create_authorization(self, authorization_form):
        """Creates a new explicit ``Authorization``.

        arg:    authorization_form
                (osid.authorization.AuthorizationForm): the
                authorization form
        return: (osid.authorization.Authorization) - ``t`` he new
                ``Authorization``
        raise:  IllegalState - ``authorization_form`` already used in a
                create transaction
        raise:  InvalidArgument - one or more of the form elements is
                invalid
        raise:  NullArgument - ``authorization_form`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``authorization_form`` did not originate
                from this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_update_authorizations(self):
        """Tests if this user can update ``Authorizations``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known updating an
        ``Authorization`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        update operations to an unauthorized user.

        return: (boolean) - ``false`` if authorization modification is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_authorization_form_for_update(self, authorization_id):
        """Gets the authorization form for updating an existing authorization.

        A new authorization form should be requested for each update
        transaction.

        arg:    authorization_id (osid.id.Id): the ``Id`` of the
                ``Authorization``
        return: (osid.authorization.AuthorizationForm) - the
                authorization form
        raise:  NotFound - ``authorization_id`` is not found
        raise:  NullArgument - ``authorization_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def update_authorization(self, authorization_form):
        """Updates an existing authorization.

        arg:    authorization_form
                (osid.authorization.AuthorizationForm): the
                authorization ``Id``
        raise:  IllegalState - ``authorization_form`` already used in an
                update transaction
        raise:  InvalidArgument - one or more of the form elements is
                invalid
        raise:  NullArgument - ``authorization_form`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``authorization_form`` did not originate
                from ``get_authorization_form_for_update()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_delete_authorizations(self):
        """Tests if this user can delete ``Authorizations``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known deleting an
        ``Authorization`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        delete operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Authorization`` deletion is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def delete_authorization(self, authorization_id):
        """Deletes the ``Authorization`` identified by the given ``Id``.

        arg:    authorization_id (osid.id.Id): the ``Id`` of the
                ``Authorization`` to delete
        raise:  NotFound - an ``Authorization`` was not found identified
                by the given ``Id``
        raise:  NullArgument - ``authorization_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_manage_authorization_aliases(self):
        """Tests if this user can manage ``Id`` aliases for ``Authorizations``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known changing an alias
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer alias
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Authorization`` aliasing is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def alias_authorization(self, authorization_id, alias_id):
        """Adds an ``Id`` to an ``Authorization`` for the purpose of creating compatibility.

        The primary ``Id`` of the ``Authorization`` is determined by the
        provider. The new ``Id`` performs as an alias to the primary
        ``Id``. If the alias is a pointer to another authorization. it
        is reassigned to the given authorization ``Id``.

        arg:    authorization_id (osid.id.Id): the ``Id`` of an
                ``Authorization``
        arg:    alias_id (osid.id.Id): the alias ``Id``
        raise:  AlreadyExists - ``alias_id`` is already assigned
        raise:  NotFound - ``authorization_id`` not found
        raise:  NullArgument - ``authorization_id`` or ``alias_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class VaultLookupSession(abc_authorization_sessions.VaultLookupSession, osid_sessions.OsidSession):
    """This session provides methods for retrieving ``Vault`` objects.

    The ``Vault`` represents a collection of ``Functions`` and
    ``Authorizations``.

    This session defines views that offer differing behaviors when
    retrieving multiple objects.

      * comparative view: elements may be silently omitted or re-ordered
      * plenary view: provides a complete set or is an error condition


    Generally, the comparative view should be used for most applications
    as it permits operation even if there is data that cannot be
    accessed. For example, a browsing application may only need to
    examine the ``Vaults`` it can access, without breaking execution.
    However, an administrative application may require all ``Vault``
    elements to be available.

    Vaults may have an additional records indicated by their respective
    record types. The record may not be accessed through a cast of the
    ``Vault``.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def can_lookup_vaults(self):
        """Tests if this user can perform ``Vault`` lookups.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer lookup
        operations to unauthorized users.

        return: (boolean) - ``false`` if lookup methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_comparative_vault_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_vault_view(self):
        """A complete view of the ``Vault`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_vault(self, vault_id):
        """Gets the ``Vault`` specified by its ``Id``.

        In plenary mode, the exact ``Id`` is found or a ``NotFound``
        results. Otherwise, the returned ``Vault`` may have a different
        ``Id`` than requested, such as the case where a duplicate ``Id``
        was assigned to a ``Vault`` and retained for compatibility.

        arg:    vault_id (osid.id.Id): ``Id`` of the ``Vault``
        return: (osid.authorization.Vault) - the vault
        raise:  NotFound - ``vault_id`` not found
        raise:  NullArgument - ``vault_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_vaults_by_ids(self, vault_ids):
        """Gets a ``VaultList`` corresponding to the given ``IdList``.

        In plenary mode, the returned list contains all of the vaults
        specified in the ``Id`` list, in the order of the list,
        including duplicates, or an error results if an ``Id`` in the
        supplied list is not found or inaccessible. Otherwise,
        inaccessible ``Vault`` objects may be omitted from the list and
        may present the elements in any order including returning a
        unique set.

        arg:    vault_ids (osid.id.IdList): the list of ``Ids`` to
                retrieve
        return: (osid.authorization.VaultList) - the returned ``Vault``
                list
        raise:  NotFound - an ``Id was`` not found
        raise:  NullArgument - ``vault_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_vaults_by_genus_type(self, vault_genus_type):
        """Gets a ``VaultList`` corresponding to the given vault genus ``Type`` which does not include vaults of types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known vaults or
        an error results. Otherwise, the returned list may contain only
        those vaults that are accessible through this session.

        arg:    vault_genus_type (osid.type.Type): a vault genus type
        return: (osid.authorization.VaultList) - the returned ``Vault``
                list
        raise:  NullArgument - ``vault_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_vaults_by_parent_genus_type(self, vault_genus_type):
        """Gets a ``VaultList`` corresponding to the given vault genus ``Type`` and include any additional vaults with genus types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known vaults or
        an error results. Otherwise, the returned list may contain only
        those vaults that are accessible through this session.

        arg:    vault_genus_type (osid.type.Type): a vault genus type
        return: (osid.authorization.VaultList) - the returned ``Vault``
                list
        raise:  NullArgument - ``vault_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_vaults_by_record_type(self, vault_record_type):
        """Gets a ``VaultList`` containing the given vault record ``Type``.

        In plenary mode, the returned list contains all known vaults or
        an error results. Otherwise, the returned list may contain only
        those vaults that are accessible through this session.

        arg:    vault_record_type (osid.type.Type): a vault record type
        return: (osid.authorization.VaultList) - the returned ``Vault``
                list
        raise:  NullArgument - ``vault_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_vaults_by_provider(self, resource_id):
        """Gets a ``VaultList`` from the given provider ````.

        In plenary mode, the returned list contains all known vaults or
        an error results. Otherwise, the returned list may contain only
        those vaults that are accessible through this session.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        return: (osid.authorization.VaultList) - the returned ``Vault``
                list
        raise:  NullArgument - ``resource_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_vaults(self):
        """Gets all ``Vaults``.

        In plenary mode, the returned list contains all known vaults or
        an error results. Otherwise, the returned list may contain only
        those vaults that are accessible through this session.

        return: (osid.authorization.VaultList) - a ``VaultList``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vaults = property(fget=get_vaults)


class VaultQuerySession(abc_authorization_sessions.VaultQuerySession, osid_sessions.OsidSession):
    """This session provides methods for searching among ``Vault`` objects.

    The search query is constructed using the ``VaultQuery``.

    Vaults may have a query record indicated by their respective record
    types. The query record is accessed via the ``VaultQuery``.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def can_search_vaults(self):
        """Tests if this user can perform ``Vault`` searches.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer search
        operations to unauthorized users.

        return: (boolean) - ``false`` if search methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def get_vault_query(self):
        """Gets a vault query.

        return: (osid.authorization.VaultQuery) - a vault query
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault_query = property(fget=get_vault_query)

    @utilities.arguments_not_none
    def get_vaults_by_query(self, vault_query):
        """Gets a list of ``Vault`` objects matching the given search.

        arg:    vault_query (osid.authorization.VaultQuery): the vault
                query
        return: (osid.authorization.VaultList) - the returned
                ``VaultList``
        raise:  NullArgument - ``vault_query`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``vault_query`` is not of this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class VaultAdminSession(abc_authorization_sessions.VaultAdminSession, osid_sessions.OsidSession):
    """This session creates, updates, and deletes ``Vaults``.

    The data for create and update is provided by the consumer via the
    form object. ``OsidForms`` are requested for each create or update
    and may not be reused.

    Create and update operations differ in their usage. To create a
    ``Vault,`` a ``VaultForm`` is requested using
    ``get_vault_form_for_create()`` specifying the desired record
    ``Types`` or none if no record ``Types`` are needed. The returned
    ``VaultForm`` will indicate that it is to be used with a create
    operation and can be used to examine metdata or validate data prior
    to creation. Once the ``VaultForm`` is submiited to a create
    operation, it cannot be reused with another create operation unless
    the first operation was unsuccessful. Each ``VaultForm`` corresponds
    to an attempted transaction.

    For updates, ``VaultForms`` are requested to the ``Vault``  ``Id``
    that is to be updated using ``getVaultFormForUpdate()``. Similarly,
    the ``VaultForm`` has metadata about the data that can be updated
    and it can perform validation before submitting the update. The
    ``VaultForm`` can only be used once for a successful update and
    cannot be reused.

    The delete operations delete ``Vaults``. It is safer to remove all
    mappings to the ``Vault`` catalogs before deletion.

    This session includes an ``Id`` aliasing mechanism to assign an
    external ``Id`` to an internally assigned Id.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def can_create_vaults(self):
        """Tests if this user can create ``Vaults``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known creating a ``Vault``
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may not wish to offer create
        operations to unauthorized users.

        return: (boolean) - ``false`` if ``Vault`` creation is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_create_vault_with_record_types(self, vault_record_types):
        """Tests if this user can create a single ``Vault`` using the desired record types.

        While ``AuthorizationManager.getVaultRecordTypes()`` can be used
        to examine which records are supported, this method tests which
        record(s) are required for creating a specific ``Vault``.
        Providing an empty array tests if a ``Vault`` can be created
        with no records.

        arg:    vault_record_types (osid.type.Type[]): array of vault
                record types
        return: (boolean) - ``true`` if ``Vault`` creation using the
                specified ``Types`` is supported, ``false`` otherwise
        raise:  NullArgument - ``vault_record_types`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_vault_form_for_create(self, vault_record_types):
        """Gets the vault form for creating new vaults.

        A new form should be requested for each create transaction.

        arg:    vault_record_types (osid.type.Type[]): array of vault
                record types
        return: (osid.authorization.VaultForm) - the vault form
        raise:  NullArgument - ``vault_record_types`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - unable to get form qith requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def create_vault(self, vault_form):
        """Creates a new ``Vault``.

        arg:    vault_form (osid.authorization.VaultForm): the form for
                this ``Vault``
        return: (osid.authorization.Vault) - the new ``Vault``
        raise:  IllegalState - ``vault_form`` already used in a create
                transaction
        raise:  InvalidArgument - one or more of the form elements is
                invalid
        raise:  NullArgument - ``vault_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``vault_form`` did not originate from
                ``get_vault_form_for_create()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_update_vaults(self):
        """Tests if this user can update ``Vaults``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known updating a ``Vault``
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may not wish to offer update
        operations to unauthorized users.

        return: (boolean) - ``false`` if ``Vault`` modification is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_vault_form_for_update(self, vault_id):
        """Gets the vault form for updating an existing vault.

        A new vault form should be requested for each update
        transaction.

        arg:    vault_id (osid.id.Id): the ``Id`` of the ``Vault``
        return: (osid.authorization.VaultForm) - the vault form
        raise:  NotFound - ``vault_id`` is not found
        raise:  NullArgument - ``vault_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def update_vault(self, vault_form):
        """Updates an existing vault.

        arg:    vault_form (osid.authorization.VaultForm): the form
                containing the elements to be updated
        raise:  IllegalState - ``vault_form`` already used in an update
                transaction
        raise:  InvalidArgument - the form contains an invalid value
        raise:  NullArgument - ``vault_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``vault_form`` did not originate from
                ``get_vault_form_for_update()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_delete_vaults(self):
        """Tests if this user can delete vaults.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known deleting a ``Vault``
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may not wish to offer delete
        operations to unauthorized users.

        return: (boolean) - ``false`` if ``Vault`` deletion is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def delete_vault(self, vault_id):
        """Deletes a ``Vault``.

        arg:    vault_id (osid.id.Id): the ``Id`` of the ``Vault`` to
                remove
        raise:  NotFound - ``vault_id`` not found
        raise:  NullArgument - ``vault_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_manage_vault_aliases(self):
        """Tests if this user can manage ``Id`` aliases for ``Vaults``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known changing an alias
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer alias
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Vault`` aliasing is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def alias_vault(self, vault_id, alias_id):
        """Adds an ``Id`` to a ``Vault`` for the purpose of creating compatibility.

        The primary ``Id`` of the ``Vault`` is determined by the
        provider. The new ``Id`` performs as an alias to the primary
        ``Id``. If the alias is a pointer to another vault it is
        reassigned to the given vault ``Id``.

        arg:    vault_id (osid.id.Id): the ``Id`` of a ``Vault``
        arg:    alias_id (osid.id.Id): the alias ``Id``
        raise:  AlreadyExists - ``alias_id`` is already assigned
        raise:  NotFound - ``vault_id`` not found
        raise:  NullArgument - ``vault_id`` or ``alias_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



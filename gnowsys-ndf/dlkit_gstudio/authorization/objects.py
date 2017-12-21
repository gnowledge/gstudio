"""GStudio implementations of authorization objects."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification

#from ..id.objects import IdList
#import importlib
#from ..osid.objects import OsidForm
#from ..osid.objects import OsidObjectForm
#from ..utilities import get_registry


import importlib


from . import default_mdata
from .. import utilities
from dlkit.abstract_osid.authorization import objects as abc_authorization_objects
from ..osid import objects as osid_objects
from ..osid.metadata import Metadata
from ..primitives import Id
from ..utilities import get_registry
from ..utilities import update_display_text_defaults
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.id.primitives import Id




class Authorization(abc_authorization_objects.Authorization, osid_objects.OsidRelationship):
    """An Authorization is a mapping among an actor, a ``Function`` and a ``Qualifier``.

    This interface is not required for performing authorization checks
    but is used for examining and managing authorizations.

    The actor of an authorization may be specified in a variety of
    forms.

      * ``Agent``
      * ``Resource:`` the authorization provider uses all the ``Agents``
        associated with a ``Resource`` for matching authorizations
      * ``Resource`` and ``Trust:`` the authorization provider uses the
        associated ``Agents`` within a cicle of ``Trust``


    An explicit ``Authorization`` represents the mappings as they are
    specified in the authorization provdier. Implicit authorizations may
    be retrieved which are authorizations inferred through the
    ``Function`` or ``Qualifier`` hierarchies. An implicit
    ``Authorization`` is one where ``is_implicit()`` is true and should
    not be used for modification as it is only available for auditing
    purposes.

    An ``Authorization`` containing a ``Resource`` may also provide the
    associated Agent in a request for implicit authorizations or for all
    the authorizations, both explicit and implicit, for a given
    ``Agent``.

    """

    _namespace = 'authorization.Authorization'

    def __init__(self, **kwargs):
        osid_objects.OsidObject.__init__(self, object_name='AUTHORIZATION', **kwargs)
        self._catalog_name = 'vault'


    def is_implicit(self):
        """Tests if this authorization is implicit.

        return: (boolean) - ``true`` if this authorization is implicit,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def has_resource(self):
        """Tests if this authorization has a ``Resource``.

        return: (boolean) - ``true`` if this authorization has a
                ``Resource,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_resource_id(self):
        """Gets the ``resource _id`` for this authorization.

        return: (osid.id.Id) - the ``Resource Id``
        raise:  IllegalState - ``has_resource()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    resource_id = property(fget=get_resource_id)

    def get_resource(self):
        """Gets the ``Resource`` for this authorization.

        return: (osid.resource.Resource) - the ``Resource``
        raise:  IllegalState - ``has_resource()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    resource = property(fget=get_resource)

    def has_trust(self):
        """Tests if this authorization has a ``Trust``.

        return: (boolean) - ``true`` if this authorization has a
                ``Trust,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_trust_id(self):
        """Gets the ``Trust``  ``Id`` for this authorization.

        return: (osid.id.Id) - the trust ``Id``
        raise:  IllegalState - ``has_trust()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    trust_id = property(fget=get_trust_id)

    def get_trust(self):
        """Gets the ``Trust`` for this authorization.

        return: (osid.authentication.process.Trust) - the ``Trust``
        raise:  IllegalState - ``has_trust()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    trust = property(fget=get_trust)

    def has_agent(self):
        """Tests if this authorization has an ``Agent``.

        An implied authorization may have an ``Agent`` in addition to a
        specified ``Resource``.

        return: (boolean) - ``true`` if this authorization has an
                ``Agent,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_agent_id(self):
        """Gets the ``Agent Id`` for this authorization.

        return: (osid.id.Id) - the ``Agent Id``
        raise:  IllegalState - ``has_agent()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    agent_id = property(fget=get_agent_id)

    def get_agent(self):
        """Gets the ``Agent`` for this authorization.

        return: (osid.authentication.Agent) - the ``Agent``
        raise:  IllegalState - ``has_agent()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    agent = property(fget=get_agent)

    def get_function_id(self):
        """Gets the ``Function Id`` for this authorization.

        return: (osid.id.Id) - the function ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    function_id = property(fget=get_function_id)

    def get_function(self):
        """Gets the ``Function`` for this authorization.

        return: (osid.authorization.Function) - the function
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    function = property(fget=get_function)

    def get_qualifier_id(self):
        """Gets the ``Qualifier Id`` for this authorization.

        return: (osid.id.Id) - the qualifier ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    qualifier_id = property(fget=get_qualifier_id)

    def get_qualifier(self):
        """Gets the qualifier for this authorization.

        return: (osid.authorization.Qualifier) - the qualifier
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    qualifier = property(fget=get_qualifier)

    @utilities.arguments_not_none
    def get_authorization_record(self, authorization_record_type):
        """Gets the authorization record corresponding to the given ``Authorization`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``authorization_record_type`` may be the
        ``Type`` returned in ``get_record_types()`` or any of its
        parents in a ``Type`` hierarchy where
        ``has_record_type(authorization_record_type)`` is ``true`` .

        arg:    authorization_record_type (osid.type.Type): the type of
                the record to retrieve
        return: (osid.authorization.records.AuthorizationRecord) - the
                authorization record
        raise:  NullArgument - ``authorization_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(authorization_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AuthorizationForm(abc_authorization_objects.AuthorizationForm, osid_objects.OsidRelationshipForm):
    """This is the form for creating and updating ``Authorizations``.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``AuthorizationAdminSession``. For each data element that may be
    set, metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'authorization.Authorization'

    def __init__(self, **kwargs):
        osid_objects.OsidRelationshipForm.__init__(self, object_name='AUTHORIZATION', **kwargs)
        self._mdata = default_mdata.get_authorization_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    def _init_metadata(self, **kwargs):
        """Initialize form metadata"""
        osid_objects.OsidRelationshipForm._init_metadata(self, **kwargs)
        self._function_default = self._mdata['function']['default_id_values'][0]
        self._qualifier_default = self._mdata['qualifier']['default_id_values'][0]

    def _init_form(self, record_types=None, **kwargs):
        """Initialize form elements"""
        osid_objects.OsidRelationshipForm._init_form(self, record_types=record_types)
        # Initialize all form elements to default values here

    @utilities.arguments_not_none
    def get_authorization_form_record(self, authorization_record_type):
        """Gets the ``AuthorizationFormRecord`` corresponding to the given authorization record ``Type``.

        arg:    authorization_record_type (osid.type.Type): the
                authorization record type
        return: (osid.authorization.records.AuthorizationFormRecord) -
                the authorization form record
        raise:  NullArgument - ``authorization_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(authorization_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AuthorizationList(abc_authorization_objects.AuthorizationList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``AuthorizationList`` provides a means for accessing ``Authorization`` elements sequentially either one at a time or many at a time.

    Examples: while (al.hasNext()) { Authorization authorization =
    al.getNextAuthorization(); }

    or
      while (al.hasNext()) {
           Authorization[] authorizations = al.getNextAuthorizations(al.available());
      }



    """

    def get_next_authorization(self):
        """Gets the next ``Authorization`` in this list.

        return: (osid.authorization.Authorization) - the next
                ``Authorization`` in this list. The ``has_next()``
                method should be used to test that a next
                ``Authorization`` is available before calling this
                method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Authorization)

    next_authorization = property(fget=get_next_authorization)

    @utilities.arguments_not_none
    def get_next_authorizations(self, n):
        """Gets the next set of ``Authorization`` elements in this list which must be less than or equal to the number returned from ``available()``.

        arg:    n (cardinal): the number of ``Authorization`` elements
                requested which should be less than or equal to
                ``available()``
        return: (osid.authorization.Authorization) - an array of
                ``Authorization`` elements.The length of the array is
                less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class Vault(abc_authorization_objects.Vault, osid_objects.OsidCatalog):
    """A vault defines a collection of authorizations and functions."""

    _namespace = 'authorization.Vault'

    def __init__(self, **kwargs):
        # self._record_type_data_sets = get_registry('VAULT_RECORD_TYPES', runtime)
        osid_objects.OsidCatalog.__init__(self, object_name='VAULT', **kwargs)

    @utilities.arguments_not_none
    def get_vault_record(self, vault_record_type):
        """Gets the vault record corresponding to the given ``Vault`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``vault_record_type`` may be the ``Type``
        returned in ``get_record_types()`` or any of its parents in a
        ``Type`` hierarchy where ``has_record_type(vault_record_type)``
        is ``true`` .

        arg:    vault_record_type (osid.type.Type): a vault record type
        return: (osid.authorization.records.VaultRecord) - the vault
                record
        raise:  NullArgument - ``vault_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(vault_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class VaultForm(abc_authorization_objects.VaultForm, osid_objects.OsidCatalogForm):
    """This is the form for creating and updating vaults.

    Like all ``OsidForm`` objects, various data elements may be set here
    for use in the create and update methods in the
    ``VaultAdminSession``. For each data element that may be set,
    metadata may be examined to provide display hints or data
    constraints.

    """

    _namespace = 'authorization.Vault'

    def __init__(self, **kwargs):
        osid_objects.OsidCatalogForm.__init__(self, object_name='VAULT', **kwargs)
        self._mdata = default_mdata.get_vault_mdata()
        self._init_metadata(**kwargs)
        if not self.is_for_update():
            self._init_form(**kwargs)

    @utilities.arguments_not_none
    def get_vault_form_record(self, vault_record_type):
        """Gets the ``VaultFormRecord`` corresponding to the given vault record ``Type``.

        arg:    vault_record_type (osid.type.Type): a vault record type
        return: (osid.authorization.records.VaultFormRecord) - the vault
                form record
        raise:  NullArgument - ``vault_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(vault_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class VaultList(abc_authorization_objects.VaultList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``VaultList`` provides a means for accessing ``Vault`` elements sequentially either one at a time or many at a time.

    Examples: while (vl.hasNext()) { Vault vault = vl.getNextVault(); }

    or
      while (vl.hasNext()) {
           Vault[] vaults = vl.getNextVaults(vl.available());
      }



    """

    def get_next_vault(self):
        """Gets the next ``Vault`` in this list.

        return: (osid.authorization.Vault) - the next ``Vault`` in this
                list. The ``has_next()`` method should be used to test
                that a next ``Vault`` is available before calling this
                method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(Vault)

    next_vault = property(fget=get_next_vault)

    @utilities.arguments_not_none
    def get_next_vaults(self, n):
        """Gets the next set of ``Vault`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``Vault`` elements requested
                which must be less than or equal to ``available()``
        return: (osid.authorization.Vault) - an array of ``Vault``
                elements.The length of the array is less than or equal
                to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)


class VaultNode(abc_authorization_objects.VaultNode, osid_objects.OsidNode):
    """This interface is a container for a partial hierarchy retrieval.

    The number of hierarchy levels traversable through this interface
    depend on the number of levels requested in the
    ``VaultHierarchySession``.

    """

    def get_vault(self):
        """Gets the ``Vault`` at this node.

        return: (osid.authorization.Vault) - the vault represented by
                this node
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    vault = property(fget=get_vault)

    def get_parent_vault_nodes(self):
        """Gets the parents of this vault.

        return: (osid.authorization.VaultNodeList) - the parents of this
                vault
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    parent_vault_nodes = property(fget=get_parent_vault_nodes)

    def get_child_vault_nodes(self):
        """Gets the children of this vault.

        return: (osid.authorization.VaultNodeList) - the children of
                this vault
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    child_vault_nodes = property(fget=get_child_vault_nodes)


class VaultNodeList(abc_authorization_objects.VaultNodeList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``VaultNodeList`` provides a means for accessing ``VaultNode`` elements sequentially either one at a time or many at a time.

    Examples: while (vnl.hasNext()) { VaultNode node =
    vnl.getNextVaultNode(); }

    or
      while (vnl.hasNext()) {
           VaultNode[] nodes = vnl.getNextVaultNodes(vnl.available());
      }



    """

    def get_next_vault_node(self):
        """Gets the next ``VaultNode`` in this list.

        return: (osid.authorization.VaultNode) - the next ``VaultNode``
                in this list. The ``has_next()`` method should be used
                to test that a next ``VaultNode`` is available before
                calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resource
        return self.next()

    def next(self):
        return self._get_next_object(VaultNode)

    next_vault_node = property(fget=get_next_vault_node)

    @utilities.arguments_not_none
    def get_next_vault_nodes(self, n):
        """Gets the next set of ``VaultNode`` elements in this list which must be less than or equal to the return from ``available()``.

        arg:    n (cardinal): the number of ``VaultNode`` elements
                requested which must be less than or equal to
                ``available()``
        return: (osid.authorization.VaultNode) - an array of
                ``VaultNode`` elements.The length of the array is less
                than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)



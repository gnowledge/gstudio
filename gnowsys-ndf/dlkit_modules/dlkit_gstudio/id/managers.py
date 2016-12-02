"""GStudio implementations of id managers."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ..osid import managers as osid_managers
from dlkit.manager_impls.id import managers as id_managers




class IdProfile(osid_managers.OsidProfile, id_managers.IdProfile):
    """The ``IdProfile`` describes the interoperability among id services."""

    def supports_id_lookup(self):
        """Tests if ``Id`` lookup is supported.

        return: (boolean) - ``true`` if ``Id`` lookup is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def supports_id_issue(self):
        """Tests if an ``Id`` issue service is supported.

        return: (boolean) - ``true`` if ``Id`` issuing is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def supports_id_admin(self):
        """Tests if an ``Id`` administrative service is supported.

        return: (boolean) - ``true`` if ``Id`` administration is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def supports_id_batch(self):
        """Tests for the availability of an Id batch service.

        return: (boolean) - ``true`` if an Id batch service is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class IdManager(osid_managers.OsidManager, IdProfile, id_managers.IdManager):
    """This manager provides access to the available sessions of the Id service.

    ``Ids`` are created through the ``IdAdminSession`` which provides
    the means for creating a unique identifier.

    The ``IdLookupSession`` can be used for mapping one ``Id`` to
    another in addition to getting a list of the assigned identifiers.

    """

    def get_id_lookup_session(self):
        """Gets the session associated with the id lookup service.

        return: (osid.id.IdLookupSession) - an ``IdLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_id_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_id_lookup()`` is ``true``.*

        """
        raise errors.Unimplemented()

    id_lookup_session = property(fget=get_id_lookup_session)

    def get_id_issue_session(self):
        """Gets the session associated with the id issue service.

        return: (osid.id.IdIssueSession) - an ``IdIssueSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_id_issue()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_id_issue()`` is ``true``.*

        """
        raise errors.Unimplemented()

    id_issue_session = property(fget=get_id_issue_session)

    def get_id_admin_session(self):
        """Gets the session associated with the id admin service.

        return: (osid.id.IdAdminSession) - an ``IdAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_id_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_id_admin()`` is ``true``.*

        """
        raise errors.Unimplemented()

    id_admin_session = property(fget=get_id_admin_session)

    def get_id_batch_manager(self):
        """Gets an ``IdBatchManager``.

        return: (osid.id.batch.IdBatchManager) - an ``IdBatchManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_id_batch()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_id_batch()`` is ``true``.*

        """
        raise errors.Unimplemented()

    id_batch_manager = property(fget=get_id_batch_manager)


class IdProxyManager(osid_managers.OsidProxyManager, IdProfile, id_managers.IdProxyManager):
    """This manager provides access to the available sessions of the Id service.

    Methods in this manager support the passing of a ``Proxy`` object
    for the purpose of pasisng information from a server envrionment.

    ``Ids`` are created through the ``IdAdminSession`` which provides
    the means for creating a unique identifier. The ``IdBrowserSession``
    can be used for mapping one ``Id`` to another in addition to getting
    a list of the assigned identifiers.

    """

    @utilities.arguments_not_none
    def get_id_lookup_session(self, proxy):
        """Gets the session associated with the id lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.id.IdLookupSession) - an ``IdLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_id_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_id_lookup()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_id_issue_session(self, proxy):
        """Gets the session associated with the id issue service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.id.IdIssueSession) - an ``IdIssueSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_id_issue()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_id_issue()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_id_admin_session(self, proxy):
        """Gets the session associated with the id administrative service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.id.IdAdminSession) - an ``IdAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_id_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_id_admin()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def get_id_batch_proxy_manager(self):
        """Gets an ``IdnProxyManager``.

        return: (osid.id.batch.IdBatchProxyManager) - an
                ``IdBatchProxyManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_id_batch()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_id_batch()`` is ``true``.*

        """
        raise errors.Unimplemented()

    id_batch_proxy_manager = property(fget=get_id_batch_proxy_manager)



"""GStudio implementations of type managers."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ..osid import managers as osid_managers
from dlkit.abstract_osid.osid import errors
from dlkit.manager_impls.type import managers as type_managers




class TypeProfile(osid_managers.OsidProfile, type_managers.TypeProfile):
    """The ``TypeProfile`` describes the interoperability among type services."""

    def supports_type_lookup(self):
        """Tests if ``Type`` lookup is supported.

        return: (boolean) - ``true`` if ``Type`` lookup is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        from . import profile
        return 'supports_type_lookup' in profile.SUPPORTS

    def supports_type_admin(self):
        """Tests if a ``Type`` administrative service is supported.

        return: (boolean) - ``true`` if ``Type`` administration is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        from . import profile
        return 'supports_type_admin' in profile.SUPPORTS


class TypeManager(osid_managers.OsidManager, TypeProfile, type_managers.TypeManager):
    """This manager provides access to the available sessions of the type service.

    The ``TypeLookupSession`` is used for looking up ``Types`` and the
    ``TypeAdminSession`` is used for managing and registering new Types.

    """

    def get_type_lookup_session(self):
        """Gets the ``OsidSession`` associated with the type lookup service.

        return: (osid.type.TypeLookupSession) - a ``TypeLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_type_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_type_lookup()`` is ``true``.*

        """
        if not self.supports_type_lookup():
            raise errors.Unimplemented()
        try:
            from . import sessions
        except ImportError:
            raise errors.OperationFailed()
        try:
            session = sessions.TypeLookupSession()
        except AttributeError:
            raise errors.OperationFailed()
        return session

    type_lookup_session = property(fget=get_type_lookup_session)

    def get_type_admin_session(self):
        """Gets the ``OsidSession`` associated with the type admin service.

        return: (osid.type.TypeAdminSession) - a ``TypeAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_type_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_type_admin()`` is ``true``.*

        """
        if not self.supports_type_admin():
            raise errors.Unimplemented()
        try:
            from . import sessions
        except ImportError:
            raise errors.OperationFailed()
        try:
            session = sessions.TypeAdminSession()
        except AttributeError:
            raise errors.OperationFailed()
        return session

    type_admin_session = property(fget=get_type_admin_session)


class TypeProxyManager(osid_managers.OsidProxyManager, TypeProfile, type_managers.TypeProxyManager):
    """This manager provides access to the available sessions of the type service.

    Methods in this manager support the passing of a ``Proxy`` object
    for the purpose of passing information from a server environment.
    The ``TypeLookupSession`` is used for looking up ``Types`` and the
    ``TypeAdminSession`` is used for managing and registering new Types.

    """

    @utilities.arguments_not_none
    def get_type_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the type lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.type.TypeLookupSession) - a ``TypeLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_type_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_type_lookup()`` is ``true``.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_type_admin_session(self, proxy):
        """Gets the ``OsidSession`` associated with the ``TypeAdmin`` service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.type.TypeAdminSession) - the new
                ``TypeAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_type_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_type_admin()`` is ``true``.*

        """
        raise errors.Unimplemented()



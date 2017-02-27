"""GStudio implementations of osid managers."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from . import profile
from .. import utilities
from dlkit.abstract_osid.osid import managers as abc_osid_managers
from ..osid import markers as osid_markers
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.locale.primitives import DisplayText
from dlkit.primordium.id.primitives import Id
from dlkit.primordium.type.primitives import Type




class OsidProfile(abc_osid_managers.OsidProfile, osid_markers.Sourceable):
    """The ``OsidProfile`` defines the interoperability areas of an OSID.

    An ``OsidProfile`` is implemented by an ``OsidManager``. The top
    level ``OsidProfile`` tests for version compatibility. Each OSID
    extends this interface to include its own interoperability
    definitions within its managers.

    """

    
    def __init__(self):
        self._runtime = None
        self._configs = None

    def _initialize_manager(self, runtime):
        """Sets the runtime and saves configuration"""
        if self._runtime is not None:
            raise errors.IllegalState('this manager has already been initialized.')
        self._runtime = runtime
        self._config = runtime.get_configuration()
        # Do other things here, like do things with configurations

    def get_id(self):
        """Gets an identifier for this service implementation.

        The identifier is unique among services but multiple
        instantiations of the same service use the same ``Id``. This
        identifier is the same identifier used in managing OSID
        installations.

        return: (osid.id.Id) - the ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        return Id(**profile.ID)

    id_ = property(fget=get_id)

    ident = property(fget=get_id)

    def get_display_name(self):
        """Gets a display name for this service implementation.

        return: (osid.locale.DisplayText) - a display name
        *compliance: mandatory -- This method must be implemented.*

        """
        return DisplayText(
            text = profile.DISPLAYNAME,
            language_type=Type(**profile.LANGUAGETYPE),
            script_type=Type(**profile.SCRIPTTYPE),
            format_type=Type(**profile.FORMATTYPE))

    display_name = property(fget=get_display_name)

    def get_description(self):
        """Gets a description of this service implementation.

        return: (osid.locale.DisplayText) - a description
        *compliance: mandatory -- This method must be implemented.*

        """
        return DisplayText(
            text=profile.DESCRIPTION,
            language_type=Type(**profile.LANGUAGETYPE),
            script_type=Type(**profile.SCRIPTTYPE),
            format_type=Type(**profile.FORMATTYPE))

    description = property(fget=get_description)

    def get_version(self):
        """Gets the version of this service implementation.

        return: (osid.installation.Version) - the service implementation
                version
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    version = property(fget=get_version)

    def get_release_date(self):
        """Gets the date this service implementation was released.

        return: (osid.calendaring.DateTime) - the release date
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    release_date = property(fget=get_release_date)

    @utilities.arguments_not_none
    def supports_osid_version(self, version):
        """Test for support of an OSID specification version.

        arg:    version (osid.installation.Version): the specification
                version to test
        return: (boolean) - ``true`` if this manager supports the given
                OSID version, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: An implementation may support multiple
        versions of an OSID.

        """
        raise errors.Unimplemented()

    def get_locales(self):
        """Gets the locales supported in this service.

        return: (osid.locale.LocaleList) - list of locales supported
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    locales = property(fget=get_locales)

    def supports_journal_rollback(self):
        """Test for support of a journaling rollback service.

        return: (boolean) - ``true`` if this manager supports the
                journal rollback, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # Perhaps someday I will support journaling
        return False

    def supports_journal_branching(self):
        """Test for support of a journal branching service.

        return: (boolean) - ``true`` if this manager supports the
                journal branching, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # Perhaps someday I will support journaling
        return False

    def get_branch_id(self):
        """Gets the ``Branch Id`` representing this service branch.

        return: (osid.id.Id) - the branch ``Id``
        raise:  Unimplemented - ``supports_journal_branching()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    branch_id = property(fget=get_branch_id)

    def get_branch(self):
        """Gets this service branch.

        return: (osid.journaling.Branch) - the service branch
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_journal_branching()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    branch = property(fget=get_branch)

    def get_proxy_record_types(self):
        """Gets the proxy record ``Types`` supported in this service.

        If no proxy manager is available, an empty list is returned.

        return: (osid.type.TypeList) - list of proxy record types
                supported
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    proxy_record_types = property(fget=get_proxy_record_types)

    @utilities.arguments_not_none
    def supports_proxy_record_type(self, proxy_record_type):
        """Test for support of a proxy type.

        arg:    proxy_record_type (osid.type.Type): a proxy record type
        return: (boolean) - ``true`` if this service supports the given
                proxy record type, ``false`` otherwise
        raise:  NullArgument - ``proxy_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidManager(abc_osid_managers.OsidManager, OsidProfile):
    """The ``OsidManager`` is the top level interface for all OSID managers.

    An OSID manager is instantiated through the ``OsidRuntimeManager``
    and represents an instance of a service. An OSID manager is
    responsible for implementing a profile for a service and creating
    sessions that, in general, correspond to the profile. An application
    need only create a single ``OsidManager`` per service and
    implementors must ensure the ``OsidManager`` is thread-safe ````.
    The ``OsidSessions`` spawned from an OSID manager are dedicated to
    single processing threads. The ``OsidManager`` defines methods in
    common throughout all OSID managers which implement this interface.

    """

    def __init__(self):
        OsidProfile.__init__(self)

    @utilities.arguments_not_none
    def initialize(self, runtime):
        """Initializes this manager.

        A manager is initialized once at the time of creation.

        arg:    runtime (osid.OsidRuntimeManager): the runtime
                environment
        raise:  ConfigurationError - an error with implementation
                configuration
        raise:  IllegalState - this manager has already been initialized
                by the ``OsidRuntime``
        raise:  NullArgument - ``runtime`` is ``null``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: In addition to loading its runtime
        configuration an implementation may create shared resources such
        as connection pools to be shared among all sessions of this
        service and released when this manager is closed. Providers must
        thread-protect any data stored in the manager.  To maximize
        interoperability, providers should not honor a second call to
        ``initialize()`` and must set an ``IllegalState`` error.

        """
        OsidProfile._initialize_manager(self, runtime)

    @utilities.arguments_not_none
    def rollback_service(self, rollback_time):
        """Rolls back this service to a point in time.

        arg:    rollback_time (timestamp): the requested time
        return: (osid.journaling.JournalEntry) - the journal entry
                corresponding to the actual state of this service
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unimplemented - ``supports_journal_rollback()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def change_branch(self, branch_id):
        """Changes the service branch.

        arg:    branch_id (osid.id.Id): the new service branch
        raise:  NotFound - ``branch_id`` not found
        raise:  NullArgument - ``branch_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unimplemented - ``supports_journal_branching()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidProxyManager(abc_osid_managers.OsidProxyManager, OsidProfile):
    """The ``OsidProxyManager`` is the top level interface for all OSID proxy managers.

    A proxy manager accepts parameters to pass through end-user
    authentication credentials and other necessary request parameters in
    a server environment. Native applications should use an
    ``OsidManager`` to maintain a higher degree of interoperability by
    avoiding this coupling.

    An OSID proxy manager is instantiated through the
    ``OsidRuntimeManager`` and represents an instance of a service. An
    OSID manager is responsible for defining clusters of
    interoperability within a service and creating sessions that
    generally correspond to these clusters, An application need only
    create a single ``OsidProxyManager`` per service and implementors
    must ensure the ``OsidProxyManager`` is thread-safe ````. The
    ``OsidSessions`` spawned from an OSID manager are dedicated to
    single processing threads. The ``OsidProxyManager`` defines methods
    in common throughout all OSID managers which implement this
    interface.

    """

    def __init__(self):
        OsidProfile.__init__(self)

    @utilities.arguments_not_none
    def initialize(self, runtime):
        """Initializes this manager.

        A manager is initialized once at the time of creation.

        arg:    runtime (osid.OsidRuntimeManager): the runtime
                environment
        raise:  ConfigurationError - an error with implementation
                configuration
        raise:  IllegalState - this manager has already been initialized
                by the ``OsidRuntime``
        raise:  NullArgument - ``runtime`` is ``null``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: In addition to loading its runtime
        configuration an implementation may create shared resources such
        as connection pools to be shared among all sessions of this
        service and released when this manager is closed. Providers must
        thread-protect any data stored in the manager.  To maximize
        interoperability, providers should not honor a second call to
        ``initialize()`` and must set an ``IllegalState`` error.

        """
        OsidProfile._initialize_manager(self, runtime)

    @utilities.arguments_not_none
    def rollback_service(self, rollback_time, proxy):
        """Rolls back this service to a point in time.

        arg:    rollback_time (timestamp): the requested time
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.journaling.JournalEntry) - the journal entry
                corresponding to the actual state of this service
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unimplemented - ``supports_journal_rollback()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def change_branch(self, branch_id, proxy):
        """Changes the service branch.

        arg:    branch_id (osid.id.Id): the new service branch
        arg:    proxy (osid.proxy.Proxy): a proxy
        raise:  NotFound - ``branch_id`` not found
        raise:  NullArgument - ``branch_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unimplemented - ``supports_journal_branching()`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidRuntimeProfile(abc_osid_managers.OsidRuntimeProfile, OsidProfile):
    """The ``OsidRuntimeProfile`` defines the service aspects of the OSID runtime service."""

    def supports_configuration(self):
        """Tests if a configuration service is provided within this runtime environment.

        return: (boolean) - ``true`` if a configuration service is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidRuntimeManager(abc_osid_managers.OsidRuntimeManager, OsidManager, OsidRuntimeProfile):
    """The ``OsidRuntimeManager`` represents and OSID platform and contains the information required for running OSID implementations such as search paths and configurations."""

    def __init__(self, configuration_key = None):
        self._configuration_key = configuration_key

    @utilities.arguments_not_none
    def get_manager(self, osid, impl_class_name, version):
        """Finds, loads and instantiates providers of OSID managers.

        Providers must conform to an OsidManager interface. The
        interfaces are defined in the OSID enumeration. For all OSID
        requests, an instance of ``OsidManager`` that implements the
        ``OsidManager`` interface is returned. In bindings where
        permitted, this can be safely cast into the requested manager.

        arg:    osid (osid.OSID): represents the OSID
        arg:    impl_class_name (string): the name of the implementation
        arg:    version (osid.installation.Version): the minimum
                required OSID specification version
        return: (osid.OsidManager) - the manager of the service
        raise:  ConfigurationError - an error in configuring the
                implementation
        raise:  NotFound - the implementation class was not found
        raise:  NullArgument - ``impl_class_name`` or ``version`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``impl_class_name`` does not support the
                requested OSID
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: After finding and instantiating the
        requested ``OsidManager,`` providers must invoke
        ``OsidManager.initialize(OsidRuntimeManager)`` where the
        environment is an instance of the current environment that
        includes the configuration for the service being initialized.
        The ``OsidRuntimeManager`` passed may include information useful
        for the configuration such as the identity of the service being
        instantiated.

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_proxy_manager(self, osid, implementation, version):
        """Finds, loads and instantiates providers of OSID managers.

        Providers must conform to an ``OsidManager`` interface. The
        interfaces are defined in the OSID enumeration. For all OSID
        requests, an instance of ``OsidManager`` that implements the
        ``OsidManager`` interface is returned. In bindings where
        permitted, this can be safely cast into the requested manager.

        arg:    osid (osid.OSID): represents the OSID
        arg:    implementation (string): the name of the implementation
        arg:    version (osid.installation.Version): the minimum
                required OSID specification version
        return: (osid.OsidProxyManager) - the manager of the service
        raise:  ConfigurationError - an error in configuring the
                implementation
        raise:  NotFound - the implementation class was not found
        raise:  NullArgument - ``implementation`` or ``version`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``implementation`` does not support the
                requested OSID
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: After finding and instantiating the
        requested ``OsidManager,`` providers must invoke
        ``OsidManager.initialize(OsidRuntimeManager)`` where the
        environment is an instance of the current environment that
        includes the configuration for the service being initialized.
        The ``OsidRuntimeManager`` passed may include information useful
        for the configuration such as the identity of the service being
        instantiated.

        """
        raise errors.Unimplemented()

    def get_configuration(self):
        """Gets the current configuration in the runtime environment.

        return: (osid.configuration.ValueLookupSession) - a
                configuration
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - an authorization failure occured
        raise:  Unimplemented - a configuration service is not supported
        *compliance: optional -- This method must be implemented if
        ``supports_configuration()`` is ``true``.*

        """
        raise errors.Unimplemented()

    configuration = property(fget=get_configuration)



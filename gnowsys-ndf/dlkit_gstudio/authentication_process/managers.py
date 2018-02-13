"""GStudio implementations of authentication.process managers."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from . import sessions
from .. import utilities
from ..osid import managers as osid_managers
from ..primitives import Type
from ..type.objects import TypeList
from ..utilities import get_registry
from dlkit.abstract_osid.osid import errors
from dlkit.manager_impls.authentication_process import managers as authentication_process_managers




class AuthenticationProcessProfile(osid_managers.OsidProfile, authentication_process_managers.AuthenticationProcessProfile):
    """The ``AuthenticationProcessProfile`` describes the interoperability among authentication process services."""

    def supports_authentication_acquisition(self):
        """Tests if authentication acquisition is supported.

        Authentication acquisition is responsible for acquiring client
        side authentication credentials.

        return: (boolean) - ``true`` if authentication acquisiiton is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_authentication_validation(self):
        """Tests if authentication validation is supported.

        Authentication validation verifies given authentication
        credentials and maps to an agent identity.

        return: (boolean) - ``true`` if authentication validation is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_trust_lookup(self):
        """Tests if a trust look up session is supported.

        return: (boolean) - ``true`` if trust lookup is supported ``,``
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_circle_of_trust(self):
        """Tests if a session to examine agent and trust relationships is supported.

        return: (boolean) - ``true`` if a circle of trust is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_challenge(self):
        """Tests if this authentication service supports a challenge- response mechanism where credential validation service must implement a means to generate challenge data.

        return: (boolean) - ``true`` if this is a challenge-response
                system, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def get_authentication_record_types(self):
        """Gets the supported authentication record types.

        return: (osid.type.TypeList) - a list containing the supported
                authentication record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('AUTHENTICATION_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    authentication_record_types = property(fget=get_authentication_record_types)

    @utilities.arguments_not_none
    def supports_authentication_record_type(self, authentication_record_type):
        """Tests if the given authentication record type is supported.

        arg:    authentication_record_type (osid.type.Type): a ``Type``
                indicating an authentication record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``authentication_record_type`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('AUTHENTICATION_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (authentication_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    authentication_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    authentication_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_authentication_input_record_types(self):
        """Gets the supported authentication input record types.

        return: (osid.type.TypeList) - a list containing the supported
                authentication input record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('AUTHENTICATION_INPUT_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    authentication_input_record_types = property(fget=get_authentication_input_record_types)

    @utilities.arguments_not_none
    def supports_authentication_input_record_type(self, authentication_input_record_type):
        """Tests if the given authentication input record type is supported.

        arg:    authentication_input_record_type (osid.type.Type): a
                ``Type`` indicating an authentication input record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``authentication_input_record_type`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('AUTHENTICATION_INPUT_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (authentication_input_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    authentication_input_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    authentication_input_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_challenge_record_types(self):
        """Gets the supported challenge types.

        return: (osid.type.TypeList) - a list containing the supported
                challenge types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('CHALLENGE_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    challenge_record_types = property(fget=get_challenge_record_types)

    @utilities.arguments_not_none
    def supports_challenge_record_type(self, challenge_record_type):
        """Tests if the given challenge data type is supported.

        arg:    challenge_record_type (osid.type.Type): a ``Type``
                indicating a challenge record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``challenge_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('CHALLENGE_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (challenge_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    challenge_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    challenge_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def supports_credential_export(self):
        """Tests if ``Authentication`` objects can export serialzied credentials for transport.

        return: (boolean) - ``true`` if the given credentials export is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def get_credential_types(self):
        """Gets the supported credential types.

        return: (osid.type.TypeList) - a list containing the supported
                credential types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.repository.RepositoryProfile.get_coordinate_types
        return TypeList([])

    credential_types = property(fget=get_credential_types)

    @utilities.arguments_not_none
    def supports_credential_type(self, credential_type):
        """Tests if the given credential type is supported.

        arg:    credential_type (osid.type.Type): a ``Type`` indicating
                a credential type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``credential_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.repository.RepositoryProfile.supports_coordinate_type
        return False

    def get_trust_types(self):
        """Gets the supported trust types.

        return: (osid.type.TypeList) - a list containing the supported
                trust types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.repository.RepositoryProfile.get_coordinate_types
        return TypeList([])

    trust_types = property(fget=get_trust_types)

    @utilities.arguments_not_none
    def supports_trust_type(self, trust_type):
        """Tests if the given trust type is supported.

        arg:    trust_type (osid.type.Type): a ``Type`` indicating a
                trust type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``trust_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.repository.RepositoryProfile.supports_coordinate_type
        return False


class AuthenticationProcessManager(osid_managers.OsidManager, AuthenticationProcessProfile, authentication_process_managers.AuthenticationProcessManager):
    """The authentication process manager provides access to authentication sessions and provides interoperability tests for various aspects of this service.

    The sessions included in this manager are:

      * ``AuthenticationAcquisitionSession:`` a session to acquire
        credentials from a user and serialize them for transport to a
        remote peer for authentication
      * ``AuthenticationValidationSession: a`` session to receive and
        validate authentication credentials from a remote peer wishing
        to authenticate
      * ``TrustLookupSession:`` a session to look up authentication
        circles of trust
      * ``CircleOfTrustSession:`` a session to examine agent circles of
        trust


    """

    def __init__(self):
        osid_managers.OsidManager.__init__(self)

    def get_authentication_acquisition_session(self):
        """Gets an ``AuthenticationAcquisitionSession`` which is responsible for acquiring authentication credentials on behalf of a service client.

        return:
                (osid.authentication.process.AuthenticationAcquisitionSe
                ssion) - an acquisition session for this service
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_authentication_acquisition()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_acquisition()`` is ``true``.*

        """
        if not self.supports_authentication_acquisition():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AuthenticationAcquisitionSession(runtime=self._runtime)

    authentication_acquisition_session = property(fget=get_authentication_acquisition_session)

    def get_authentication_validation_session(self):
        """Gets the ``OsidSession`` associated with the ``AuthenticationValidation`` service.

        return:
                (osid.authentication.process.AuthenticationValidationSes
                sion) - an ``AuthenticationValidationSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_authentication_validation()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_validation()`` is ``true``.*

        """
        if not self.supports_authentication_validation():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AuthenticationValidationSession(runtime=self._runtime)

    authentication_validation_session = property(fget=get_authentication_validation_session)

    def get_trust_lookup_session(self):
        """Gets the ``OsidSession`` associated with the trust lookup service.

        return: (osid.authentication.process.TrustLookupSession) - a
                ``TrustLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_trust_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_trust_lookup()`` is ``true``.*

        """
        if not self.supports_trust_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.TrustLookupSession(runtime=self._runtime)

    trust_lookup_session = property(fget=get_trust_lookup_session)

    @utilities.arguments_not_none
    def get_trust_lookup_session_for_agency(self, agency_id):
        """Gets the ``OsidSession`` associated with the trust lookup service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        return: (osid.authentication.process.TrustLookupSession) - a
                ``TrustLookupSession``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_trust_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_trust_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_trust_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.TrustLookupSession(agency_id, self._runtime)

    def get_circle_of_trust_session(self):
        """Gets the ``OsidSession`` associated with the trust circle service.

        return: (osid.authentication.process.CircleOfTrustSession) - a
                ``CircleOfTrustSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_circle_of_trust()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_circle_of_trust()`` is ``true``.*

        """
        if not self.supports_circle_of_trust():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CircleOfTrustSession(runtime=self._runtime)

    circle_of_trust_session = property(fget=get_circle_of_trust_session)

    @utilities.arguments_not_none
    def get_circle_of_trust_session_for_agency(self, agency_id):
        """Gets the ``OsidSession`` associated with the trust circle service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        return: (osid.authentication.process.CircleOfTrustSession) - a
                ``CircleOfTrustSession``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_ciirle_of_trust()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_circle_of_trust()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_circle_of_trust():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CircleOfTrustSession(agency_id, self._runtime)


class AuthenticationProcessProxyManager(osid_managers.OsidProxyManager, AuthenticationProcessProfile, authentication_process_managers.AuthenticationProcessProxyManager):
    """The authentication process proxy manager provides access to authentication sessions and provides interoperability tests for various aspects of this service.

    Methods in this manager support the passing of a ``Proxy`` object.
    The sessions included in this manager are:

      * ``AuthenticationAcquisitionSession:`` session to acquire
        credentials from a user and serialize them for transport to a
        remote peer for authentication
      * ``AuthenticationValidationSession:`` session to receive and
        validate authentication credentials from a remote peer wishing
        to authenticate
      * ``TrustLookupSession:`` a session to look up authentication
        circles of trust
      * ``CircleOfTrustSession:`` a session to examine agent circles of
        trust


    """

    def __init__(self):
        osid_managers.OsidProxyManager.__init__(self)

    @utilities.arguments_not_none
    def get_authentication_acquisition_session(self, proxy):
        """Gets the ``OsidSession`` associated with the ``AuthenticationAcquisitionSession`` using the supplied ``Authentication``.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return:
                (osid.authentication.process.AuthenticationAcquisitionSe
                ssion) - an ``AuthenticationAcquisitionSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_authentication_acquisition()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_acquisition()`` is ``true``.*

        """
        if not self.supports_authentication_acquisition():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AuthenticationAcquisitionSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_authentication_validation_session(self, proxy):
        """Gets the ``OsidSession`` associated with the ``AuthenticationValidation`` service using the supplied ``Authentication``.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return:
                (osid.authentication.process.AuthenticationValidationSes
                sion) - an ``AuthenticationValidationSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_authentication_validation()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_validation()`` is ``true``.*

        """
        if not self.supports_authentication_validation():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AuthenticationValidationSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_trust_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the trust lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.process.TrustLookupSession) - a
                ``TrustLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_trust_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_trust_lookup()`` is ``true``.*

        """
        if not self.supports_trust_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.TrustLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_trust_lookup_session_for_agency(self, agency_id, proxy):
        """Gets the ``OsidSession`` associated with the trust lookup service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.process.TrustLookupSession) - a
                ``TrustLookupSession``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_trust_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_trust_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_trust_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.TrustLookupSession(agency_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_circle_of_trust_session(self, proxy):
        """Gets the ``OsidSession`` associated with the trust circle service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.process.CircleOfTrustSession) - a
                ``CircleOfTrustSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_circle_of_trust()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_circle_of_trust()`` is ``true``.*

        """
        if not self.supports_circle_of_trust():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CircleOfTrustSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_circle_of_trust_session_for_agency(self, agency_id, proxy):
        """Gets the ``OsidSession`` associated with the trust circle service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.process.CircleOfTrustSession) - a
                ``CircleOfTrustSession``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_ciirle_of_trust()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_circle_of_trust()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_circle_of_trust():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CircleOfTrustSession(agency_id, proxy, self._runtime)



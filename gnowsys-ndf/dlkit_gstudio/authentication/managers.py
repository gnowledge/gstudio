"""GStudio implementations of authentication managers."""

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
from dlkit.manager_impls.authentication import managers as authentication_managers




class AuthenticationProfile(osid_managers.OsidProfile, authentication_managers.AuthenticationProfile):
    """The ``AuthenticationProfile`` describes the interoperability among authentication services."""

    def supports_visible_federation(self):
        """Tests if federation is visible.

        return: (boolean) - ``true`` if visible federation is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_authentication_acquisition(self):
        """Tests is authentication acquisition is supported.

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

    def supports_agent_lookup(self):
        """Tests if an agent lookup service is supported.

        An agent lookup service defines methods to access agents.

        return: (boolean) - ``true`` if agent lookup is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agent_query(self):
        """Tests if an agent query service is supported.

        return: (boolean) - ``true`` if agent query is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agent_search(self):
        """Tests if an agent search service is supported.

        return: (boolean) - ``true`` if agent search is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agent_admin(self):
        """Tests if an agent administrative service is supported.

        return: (boolean) - ``true`` if agent admin is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agent_notification(self):
        """Tests if agent notification is supported.

        Messages may be sent when agents are created, modified, or
        deleted.

        return: (boolean) - ``true`` if agent notification is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agent_agency(self):
        """Tests if retrieving mappings of agents and agencies is supported.

        return: (boolean) - ``true`` if agent agency mapping retrieval
                is supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agent_agency_assignment(self):
        """Tests if managing mappings of agents and agencies is supported.

        return: (boolean) - ``true`` if agent agency assignment is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agent_smart_agency(self):
        """Tests if agent smart agency is available.

        return: (boolean) - ``true`` if agent smart agency is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agency_lookup(self):
        """Tests if an agency lookup service is supported.

        An agency lookup service defines methods to access agencies.

        return: (boolean) - ``true`` if agency lookup is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agency_query(self):
        """Tests if an agency query service is supported.

        return: (boolean) - ``true`` if agency query is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agency_search(self):
        """Tests if an agency search service is supported.

        return: (boolean) - ``true`` if agency search is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agency_admin(self):
        """Tests if an agency administrative service is supported.

        return: (boolean) - ``true`` if agency admin is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agency_notification(self):
        """Tests if agency notification is supported.

        Messages may be sent when agencies are created, modified, or
        deleted.

        return: (boolean) - ``true`` if agency notification is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agency_hierarchy(self):
        """Tests if an agency hierarchy traversal is supported.

        return: (boolean) - ``true`` if an agency hierarchy traversal is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_agency_hierarchy_design(self):
        """Tests if an agency hierarchy design is supported.

        return: (boolean) - ``true`` if an agency hierarchy design is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_authentication_keys(self):
        """Tests if an authentication key service is available.

        return: (boolean) - ``true`` if an authentication key service is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_authentication_process(self):
        """Tests if an authentication process service is available.

        return: (boolean) - ``true`` if an authentication process
                service is supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def get_agent_record_types(self):
        """Gets the supported ``Agent`` record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``Agent`` record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('AGENT_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    agent_record_types = property(fget=get_agent_record_types)

    @utilities.arguments_not_none
    def supports_agent_record_type(self, agent_record_type):
        """Tests if the given ``Agent`` record type is supported.

        arg:    agent_record_type (osid.type.Type): a ``Type``
                indicating an ``Agent`` record type
        return: (boolean) - ``true`` if the given record Type is
                supported, ``false`` otherwise
        raise:  NullArgument - ``agent_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('AGENT_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (agent_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    agent_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    agent_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_agent_search_record_types(self):
        """Gets the supported ``Agent`` search record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``Agent`` search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('AGENT_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    agent_search_record_types = property(fget=get_agent_search_record_types)

    @utilities.arguments_not_none
    def supports_agent_search_record_type(self, agent_search_record_type):
        """Tests if the given ``Agent`` search record type is supported.

        arg:    agent_search_record_type (osid.type.Type): a ``Type``
                indicating an ``Agent`` search record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``agent_search_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('AGENT_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (agent_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    agent_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    agent_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_agency_record_types(self):
        """Gets the supported ``Agency`` record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``Agency`` record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('AGENCY_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    agency_record_types = property(fget=get_agency_record_types)

    @utilities.arguments_not_none
    def supports_agency_record_type(self, agency_record_type):
        """Tests if the given ``Agency`` record type is supported.

        arg:    agency_record_type (osid.type.Type): a ``Type``
                indicating an ``Agency`` record type
        return: (boolean) - ``true`` if the given record Type is
                supported, ``false`` otherwise
        raise:  NullArgument - ``agency_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('AGENCY_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (agency_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    agency_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    agency_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_agency_search_record_types(self):
        """Gets the supported ``Agency`` search record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``Agency`` search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('AGENCY_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    agency_search_record_types = property(fget=get_agency_search_record_types)

    @utilities.arguments_not_none
    def supports_agency_search_record_type(self, agency_search_record_type):
        """Tests if the given ``Agency`` search record type is supported.

        arg:    agency_search_record_type (osid.type.Type): a ``Type``
                indicating an ``Agency`` search record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``agency_search_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('AGENCY_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (agency_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    agency_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    agency_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports


class AuthenticationManager(osid_managers.OsidManager, AuthenticationProfile, authentication_managers.AuthenticationManager):
    """The authentication manager provides access to authentication sessions and provides interoperability tests for various aspects of this service.

    The sessions included in this manager are:

      * ``AgentLookupSession:`` a session to look up ``Agents``
      * ``AgentQuerySession:`` a session to query ``Agents``
      * ``AgentSearchSession:`` a session to search ``Agents``
      * ``AgentAdminSession:`` a session to create, modify and delete
        ``Agents``
      * ``AgentNotificationSession: a`` session to receive messages
        pertaining to ``Agent`` changes

      * ``AgentAgencySession:`` a session to retrieve ``Agent`` to
        ``Agency`` mappings
      * ``AgentAgencyAssignmentSession:`` a session to manage ``Agent``
        to ``Agency`` mappings
      * ``AgentSmartAgencySession:`` a session to create dynamic
        agencies
      * ``AgencyLookupSession:`` a session to lookup agencies
      * ``AgencyQuerySession:`` a session to query agencies
      * ``AgencySearchSession`` : a session to search agencies
      * ``AgencyAdminSession`` : a session to create, modify and delete
        agencies
      * ``AgencyNotificationSession`` : a session to receive messages
        pertaining to ``Agency`` changes
      * ``AgencyHierarchySession`` : a session to traverse the
        ``Agency`` hierarchy
      * ``AgencyHierarchyDesignSession`` : a session to manage the
        ``Agency`` hierarchy


    """

    def __init__(self):
        osid_managers.OsidManager.__init__(self)

    def get_agent_lookup_session(self):
        """Gets the ``OsidSession`` associated with the agent lookup service.

        return: (osid.authentication.AgentLookupSession) - an
                ``AgentLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_lookup()`` is ``true``.*

        """
        if not self.supports_agent_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentLookupSession(runtime=self._runtime)

    agent_lookup_session = property(fget=get_agent_lookup_session)

    @utilities.arguments_not_none
    def get_agent_lookup_session_for_agency(self, agency_id):
        """Gets the ``OsidSession`` associated with the agent lookup service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        return: (osid.authentication.AgentLookupSession) - ``an
                _agent_lookup_session``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_agent_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_agent_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AgentLookupSession(agency_id, self._runtime)

    def get_agent_query_session(self):
        """Gets the ``OsidSession`` associated with the agent query service.

        return: (osid.authentication.AgentQuerySession) - an
                ``AgentQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_query()`` is ``true``.*

        """
        if not self.supports_agent_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentQuerySession(runtime=self._runtime)

    agent_query_session = property(fget=get_agent_query_session)

    @utilities.arguments_not_none
    def get_agent_query_session_for_agency(self, agency_id):
        """Gets the ``OsidSession`` associated with the agent query service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        return: (osid.authentication.AgentQuerySession) - ``an
                _agent_query_session``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_agent_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_query()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_agent_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AgentQuerySession(agency_id, self._runtime)

    def get_agent_search_session(self):
        """Gets the ``OsidSession`` associated with the agent search service.

        return: (osid.authentication.AgentSearchSession) - an
                ``AgentSearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_search()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_search()`` is ``true``.*

        """
        if not self.supports_agent_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentSearchSession(runtime=self._runtime)

    agent_search_session = property(fget=get_agent_search_session)

    @utilities.arguments_not_none
    def get_agent_search_session_for_agency(self, agency_id):
        """Gets the ``OsidSession`` associated with the agent search service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        return: (osid.authentication.AgentSearchSession) - ``an
                _agent_search_session``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_agent_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_agent_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AgentSearchSession(agency_id, self._runtime)

    def get_agent_admin_session(self):
        """Gets the ``OsidSession`` associated with the agent administration service.

        return: (osid.authentication.AgentAdminSession) - an
                ``AgentAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_admin()`` is ``true``.*

        """
        if not self.supports_agent_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentAdminSession(runtime=self._runtime)

    agent_admin_session = property(fget=get_agent_admin_session)

    @utilities.arguments_not_none
    def get_agent_admin_session_for_agency(self, agency_id):
        """Gets the ``OsidSession`` associated with the agent admin service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        return: (osid.authentication.AgentAdminSession) - ``an
                _agent_admin_session``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_agent_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_admin()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_agent_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AgentAdminSession(agency_id, self._runtime)

    @utilities.arguments_not_none
    def get_agent_notification_session(self, agent_receiver):
        """Gets the notification session for notifications pertaining to service changes.

        arg:    agent_receiver (osid.authentication.AgentReceiver): the
                agent receiver
        return: (osid.authentication.AgentNotificationSession) - an
                ``AgentNotificationSession``
        raise:  NullArgument - ``agent_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_notification()`` is ``true``.*

        """
        if not self.supports_agent_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentNotificationSession(runtime=self._runtime, receiver=agent_receiver)

    @utilities.arguments_not_none
    def get_agent_notification_session_for_agency(self, agent_receiver, agency_id):
        """Gets the ``OsidSession`` associated with the agent notification service for the given agency.

        arg:    agent_receiver (osid.authentication.AgentReceiver): the
                agent receiver
        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        return: (osid.authentication.AgentNotificationSession) - ``an
                _agent_notification_session``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agent_receiver`` or ``agency_id`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_agent_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_agent_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AgentNotificationSession(agency_id, runtime=self._runtime, receiver=agent_receiver)

    def get_agent_agency_session(self):
        """Gets the session for retrieving agent to agency mappings.

        return: (osid.authentication.AgentAgencySession) - an
                ``AgentAgencySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_agency()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_agency()`` is ``true``.*

        """
        if not self.supports_agent_agency():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentAgencySession(runtime=self._runtime)

    agent_agency_session = property(fget=get_agent_agency_session)

    def get_agent_agency_assignment_session(self):
        """Gets the session for assigning agent to agency mappings.

        return: (osid.authentication.AgentAgencyAssignmentSession) - a
                ``AgentAgencyAsignmentSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_agency_assignment()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_agency_assignment()`` is ``true``.*

        """
        if not self.supports_agent_agency_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentAgencyAssignmentSession(runtime=self._runtime)

    agent_agency_assignment_session = property(fget=get_agent_agency_assignment_session)

    @utilities.arguments_not_none
    def get_agent_smart_agency_session(self, agency_id):
        """Gets the ``OsidSession`` associated with the agent smart agency service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        return: (osid.authentication.AgentSmartAgencySession) - an
                ``AgentSmartAgencySession``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_smart_agency()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_smart_agency()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def get_agency_lookup_session(self):
        """Gets the ``OsidSession`` associated with the agency lookup service.

        return: (osid.authentication.AgencyLookupSession) - an
                ``AgencyLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_lookup()`` is ``true``.*

        """
        if not self.supports_agency_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencyLookupSession(runtime=self._runtime)

    agency_lookup_session = property(fget=get_agency_lookup_session)

    def get_agency_search_session(self):
        """Gets the ``OsidSession`` associated with the agency search service.

        return: (osid.authentication.AgencySearchSession) - an
                ``AgencySearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_search()`` is ``true``.*

        """
        if not self.supports_agency_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencySearchSession(runtime=self._runtime)

    agency_search_session = property(fget=get_agency_search_session)

    def get_agency_admin_session(self):
        """Gets the ``OsidSession`` associated with the agency administration service.

        return: (osid.authentication.AgencyAdminSession) - an
                ``AgencyAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_admin()`` is ``true``.*

        """
        if not self.supports_agency_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencyAdminSession(runtime=self._runtime)

    agency_admin_session = property(fget=get_agency_admin_session)

    @utilities.arguments_not_none
    def get_agency_notification_session(self, agency_receiver):
        """Gets the notification session for notifications pertaining to agency service changes.

        arg:    agency_receiver (osid.authentication.AgencyReceiver):
                the agency receiver
        return: (osid.authentication.AgencyNotificationSession) - an
                ``AgencyNotificationSession``
        raise:  NullArgument - ``agency_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_notification()`` is ``true``.*

        """
        if not self.supports_agency_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencyNotificationSession(runtime=self._runtime, receiver=agency_receiver)

    def get_agency_hierarchy_session(self):
        """Gets the session traversing agency hierarchies.

        return: (osid.authentication.AgencyHierarchySession) - an
                ``AgencyHierarchySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_hierarchy()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_hierarchy()`` is ``true``.*

        """
        if not self.supports_agency_hierarchy():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencyHierarchySession(runtime=self._runtime)

    agency_hierarchy_session = property(fget=get_agency_hierarchy_session)

    def get_agency_hierarchy_design_session(self):
        """Gets the session designing agency hierarchies.

        return: (osid.authentication.AgencyHierarchyDesignSession) - an
                ``AgencyHierarchyDesignSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_hierarchy_design()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_hierarchy_design()`` is ``true``.*

        """
        if not self.supports_agency_hierarchy_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencyHierarchyDesignSession(runtime=self._runtime)

    agency_hierarchy_design_session = property(fget=get_agency_hierarchy_design_session)

    def get_authentication_batch_manager(self):
        """Gets an ``AuthenticationBatchManager``.

        return: (osid.authentication.batch.AuthenticationBatchManager) -
                an ``AuthenticationBatchManager``.
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_authentication_batch()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_authentication_batch()`` is ``true``.*

        """
        raise errors.Unimplemented()

    authentication_batch_manager = property(fget=get_authentication_batch_manager)

    def get_authentication_keys_manager(self):
        """Gets an ``AuthenticationKeysManager``.

        return: (osid.authentication.keys.AuthenticationKeysManager) -
                an ``AuthenticationKeysManager``.
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_authentication_keys()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_authentication_keys()`` is ``true``.*

        """
        raise errors.Unimplemented()

    authentication_keys_manager = property(fget=get_authentication_keys_manager)

    def get_authentication_process_manager(self):
        """Gets an ``AuthenticationProcessManager``.

        return:
                (osid.authentication.process.AuthenticationProcessManage
                r) - an ``AuthenticationProcessManager``.
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_authentication_process()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_authentication_process()`` is ``true``.*

        """
        raise errors.Unimplemented()

    authentication_process_manager = property(fget=get_authentication_process_manager)


class AuthenticationProxyManager(osid_managers.OsidProxyManager, AuthenticationProfile, authentication_managers.AuthenticationProxyManager):
    """The authentication proxy manager provides access to authentication sessions and provides interoperability tests for various aspects of this service.

    Methods in this manager support the passing of a ``Proxy`` object.
    The sessions included in this manager are:

      * ``AgentLookupSession:`` session to look up ``Agents``
      * ``AgentQuerySession`` : a session to query ``Agents``
      * ``AgentSearchSession:`` session to search ``Agents``
      * ``AgentAdminSession:`` session to create, modify and delete
        ``Agents``
      * Agent ``NotificationSession:`` session to receive messages
        pertaining to ``Agent`` changes

      * ``AgentAgencySession:`` a session to retrieve ``Agent`` to
        ``Agency`` mappings
      * ``AgentAgencyAssignmentSession:`` a session to manage ``Agent``
        to ``Agency`` mappings
      * ``AgentSmartAgencySession:`` a session to create dynamic
        agencies
      * ``AgencyLookupSession:`` a session to lookup agencies
      * ``AgencyQuerySession:`` a session to query agencies
      * ``AgencySearchSession`` : a session to search agencies
      * ``AgencyAdminSession`` : a session to create, modify and delete
        agencies
      * ``AgencyNotificationSession`` : a session to receive messages
        pertaining to ``Agency`` changes
      * ``AgencyHierarchySession`` : a session to traverse the
        ``Agency`` hierarchy
      * ``AgencyHierarchyDesignSession`` : a session to manage the
        ``Agency`` hierarchy


    """

    def __init__(self):
        osid_managers.OsidProxyManager.__init__(self)

    @utilities.arguments_not_none
    def get_agent_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the agent lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentLookupSession) - an
                ``AgentLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_lookup()`` is ``true``.*

        """
        if not self.supports_agent_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_agent_lookup_session_for_agency(self, agency_id, proxy):
        """Gets the ``OsidSession`` associated with the agent lookup service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentLookupSession) - ``an
                _agent_lookup_session``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_agent_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_agent_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AgentLookupSession(agency_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_agent_query_session(self, proxy):
        """Gets the ``OsidSession`` associated with the agent query service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentQuerySession) - an
                ``AgentQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_query()`` is ``true``.*

        """
        if not self.supports_agent_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_agent_query_session_for_agency(self, agency_id, proxy):
        """Gets the ``OsidSession`` associated with the agent query service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentQuerySession) - an
                ``AgentQuerySession``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_agent_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_query()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_agent_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AgentQuerySession(agency_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_agent_search_session(self, proxy):
        """Gets the ``OsidSession`` associated with the agent search service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentSearchSession) - an
                ``AgentSearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_search()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_search()`` is ``true``.*

        """
        if not self.supports_agent_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentSearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_agent_search_session_for_agency(self, agency_id, proxy):
        """Gets the ``OsidSession`` associated with the agent search service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentSearchSession) - ``an
                _agent_search_session``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_agent_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_agent_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AgentSearchSession(agency_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_agent_admin_session(self, proxy):
        """Gets the ``OsidSession`` associated with the agent administration service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentAdminSession) - an
                ``AgentAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_admin()`` is ``true``.*

        """
        if not self.supports_agent_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_agent_admin_session_for_agency(self, agency_id, proxy):
        """Gets the ``OsidSession`` associated with the agent admin service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentAdminSession) - ``an
                _agent_admin_session``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_agent_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_admin()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_agent_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AgentAdminSession(agency_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_agent_notification_session(self, agent_receiver, proxy):
        """Gets the messaging receiver session for notifications pertaining to agent changes.

        arg:    agent_receiver (osid.authentication.AgentReceiver): the
                agent receiver
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentNotificationSession) - an
                ``AgentNotificationSession``
        raise:  NullArgument - ``proxy`` or ``agent_receiver`` is null
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_notification()`` is ``true``.*

        """
        if not self.supports_agent_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentNotificationSession(proxy=proxy, runtime=self._runtime, receiver=agent_receiver)

    @utilities.arguments_not_none
    def get_agent_notification_session_for_agency(self, agent_receiver, agency_id, proxy):
        """Gets the ``OsidSession`` associated with the agent notification service for the given agency.

        arg:    agent_receiver (osid.authentication.AgentReceiver): the
                agent receiver
        arg:    agency_id (osid.id.Id): the ``Id`` of the agency
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentNotificationSession) - ``an
                _agent_notification_session``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agent_receiver, agency_id`` or
                ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_agent_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_agent_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AgentNotificationSession(catalog_id=agency_id, proxy=proxy, runtime=self._runtime, receiver=agent_receiver)

    @utilities.arguments_not_none
    def get_agent_agency_session(self, proxy):
        """Gets the session for retrieving agent to agency mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentAgencySession) - an
                ``AgentAgencySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_agency()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_agency()`` is ``true``.*

        """
        if not self.supports_agent_agency():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentAgencySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_agent_agency_assignment_session(self, proxy):
        """Gets the session for assigning agent to agency mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentAgencyAssignmentSession) - an
                ``AgentAgencyAssignmentSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_agency_assignment()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_agency_assignment()`` is ``true``.*

        """
        if not self.supports_agent_agency_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentAgencyAssignmentSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_agent_smart_agency_session(self, agency_id, proxy):
        """Gets the ``OsidSession`` associated with the agent smart agency service for the given agency.

        arg:    agency_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgentSmartAgencySession) - an
                ``AgentSmartAgencySession``
        raise:  NotFound - ``agency_id`` not found
        raise:  NullArgument - ``agency_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agent_smart_agency()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agent_smart_agency()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        if not self.supports_agent_smart_agency():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgentSmartAgencySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_agency_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the agency lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgencyLookupSession) - an
                ``AgencyLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_lookup()`` is ``true``.*

        """
        if not self.supports_agency_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencyLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_agency_search_session(self, proxy):
        """Gets the ``OsidSession`` associated with the agency search service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgencySearchSession) - an
                ``AgencySearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_search()`` is ``true``.*

        """
        if not self.supports_agency_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencySearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_agency_admin_session(self, proxy):
        """Gets the ``OsidSession`` associated with the agency administration service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgencyAdminSession) - an
                ``AgencyAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_admin()`` is ``true``.*

        """
        if not self.supports_agency_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencyAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_agency_notification_session(self, agency_receiver, proxy):
        """Gets the messaging receiver session for notifications pertaining to agency changes.

        arg:    agency_receiver (osid.authentication.AgencyReceiver):
                the agency receiver
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgencyNotificationSession) - an
                ``AgencyNotificationSession``
        raise:  NullArgument - ``agency_receiver`` or ``proxy`` is null
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_notification()`` is ``true``.*

        """
        if not self.supports_agency_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencyNotificationSession(proxy=proxy, runtime=self._runtime, receiver=agency_receiver)

    @utilities.arguments_not_none
    def get_agency_hierarchy_session(self, proxy):
        """Gets the session traversing agency hierarchies.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgencyHierarchySession) - an
                ``AgencyHierarchySession``
        raise:  NullArgument - ``proxy`` is null
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_hierarchy()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_hierarchy()`` is ``true``.*

        """
        if not self.supports_agency_hierarchy():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencyHierarchySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_agency_hierarchy_design_session(self, proxy):
        """Gets the session designing agency hierarchies.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.authentication.AgencyHierarchyDesignSession) - an
                ``AgencyHierarchyDesignSession``
        raise:  NullArgument - ``proxy`` is null
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_agency_hierarchy_design()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_agency_hierarchy_design()`` is ``true``.*

        """
        if not self.supports_agency_hierarchy_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AgencyHierarchyDesignSession(proxy=proxy, runtime=self._runtime)

    def get_authentication_batch_proxy_manager(self):
        """Gets an ``AuthenticationBatchProxyManager``.

        return:
                (osid.authentication.batch.AuthenticationBatchProxyManag
                er) - an ``AuthenticationBatchProxyManager``.
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_authentication_batch()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_authentication_batch()`` is ``true``.*

        """
        raise errors.Unimplemented()

    authentication_batch_proxy_manager = property(fget=get_authentication_batch_proxy_manager)

    def get_authentication_keys_proxy_manager(self):
        """Gets an ``AuthenticationKeysProxyManager``.

        return:
                (osid.authentication.keys.AuthenticationKeysProxyManager
                ) - an ``AuthenticationKeysProxyManager``.
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_authentication_keys()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_authentication_keys()`` is ``true``.*

        """
        raise errors.Unimplemented()

    authentication_keys_proxy_manager = property(fget=get_authentication_keys_proxy_manager)

    def get_authentication_process_proxy_manager(self):
        """Gets an ``AuthenticationProcessProxyManager``.

        return:
                (osid.authentication.process.AuthenticationProcessProxyM
                anager) - an ``AuthenticationProcessproxyManager``.
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_authentication_process()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_authentication_process()`` is ``true``.*

        """
        raise errors.Unimplemented()

    authentication_process_proxy_manager = property(fget=get_authentication_process_proxy_manager)



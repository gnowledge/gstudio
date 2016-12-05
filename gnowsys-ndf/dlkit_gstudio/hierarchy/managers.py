"""GStudio implementations of hierarchy managers."""

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
from dlkit.manager_impls.hierarchy import managers as hierarchy_managers




class HierarchyProfile(osid_managers.OsidProfile, hierarchy_managers.HierarchyProfile):
    """The hierarchy profile describes the interoperability among hierarchy services."""

    def supports_visible_federation(self):
        """Tests if federation is visible.

        Visible federation allows for selecting among multiple
        hierarchies.

        return: (boolean) - ``true`` if visible federation is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_hierarchy_traversal(self):
        """Tests if hierarchy traversal is supported.

        return: (boolean) - ``true`` if hierarchy traversal is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_hierarchy_design(self):
        """Tests if hierarchy design is supported.

        return: (boolean) - ``true`` if hierarchy design is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_hierarchy_sequencing(self):
        """Tests if hierarchy sequencing is supported.

        return: (boolean) - ``true`` if hierarchy sequencing is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_hierarchy_structure_notification(self):
        """Tests if hierarchy structure notification is supported.

        return: (boolean) - ``true`` if hierarchy structure notification
                is supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_hierarchy_lookup(self):
        """Tests if a hierarchy lookup is supported.

        return: (boolean) - ``true`` if hierarchy lookup is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_hierarchy_query(self):
        """Tests if a hierarchy query is supported.

        return: (boolean) - ``true`` if hierarchy query is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_hierarchy_search(self):
        """Tests if a hierarchy search is supported.

        return: (boolean) - ``true`` if hierarchy search is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_hierarchy_admin(self):
        """Tests if a hierarchy administration is supported.

        return: (boolean) - ``true`` if hierarchy administration is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_hierarchy_notification(self):
        """Tests if hierarchy notification is supported.

        Messages may be sent when hierarchies are created, modified, or
        deleted.

        return: (boolean) - ``true`` if hierarchy notification is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def get_hierarchy_record_types(self):
        """Gets the supported ``Hierarchy`` types.

        return: (osid.type.TypeList) - a list containing the supported
                ``Hierarchy`` record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('HIERARCHY_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    hierarchy_record_types = property(fget=get_hierarchy_record_types)

    @utilities.arguments_not_none
    def supports_hierarchy_record_type(self, hierarchy_record_type):
        """Tests if the given ``Hierarchy`` record type is supported.

        arg:    hierarchy_record_type (osid.type.Type): a ``Type``
                indicating a ``Hierarchy`` record type
        return: (boolean) - ``true`` if the given record Type is
                supported, ``false`` otherwise
        raise:  NullArgument - ``hierarchy_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('HIERARCHY_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (hierarchy_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    hierarchy_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    hierarchy_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_hierarchy_search_record_types(self):
        """Gets the supported ``Hierarchy`` search record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``Hierarchy`` search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('HIERARCHY_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    hierarchy_search_record_types = property(fget=get_hierarchy_search_record_types)

    @utilities.arguments_not_none
    def supports_hierarchy_search_record_type(self, hierarchy_search_record_type):
        """Tests if the given ``Hierarchy`` search record type is supported.

        arg:    hierarchy_search_record_type (osid.type.Type): a
                ``Type`` indicating a ``Hierarchy`` search record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``hierarchy_search_record_type`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('HIERARCHY_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (hierarchy_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    hierarchy_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    hierarchy_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports


class HierarchyManager(osid_managers.OsidManager, HierarchyProfile, hierarchy_managers.HierarchyManager):
    """The hierarchy manager provides access sessions to traverse and manage hierrachies of ``Ids``.

    The sessions included in this manager are:

      * ``HierarchyTraversalSession:`` a basic session traversing a
        hierarchy
      * ``HierarchyDesignSession:`` a session to design a hierarchy
      * ``HierarchySequencingSession:`` a session to sequence nodes in a
        hierarchy
      * ``HierarchyStructureNotificationSession:`` a session for
        notififcations within a hierarchy structure
      * ``HierarchyLookupSession:`` a session looking up hiererachies
      * ``HierarchyQuerySession:`` a session querying hiererachies
      * ``HierarchySearchSession:`` a session for searching for
        hierarchies
      * ``HierarchyAdminSession:`` a session for creating and deleting
        hierarchies
      * ``HierarchyNotificationSession:`` a session for subscribing to
        changes in hierarchies


    """

    def __init__(self):
        osid_managers.OsidManager.__init__(self)

    def get_hierarchy_traversal_session(self):
        """Gets the ``OsidSession`` associated with the hierarchy traversal service.

        return: (osid.hierarchy.HierarchyTraversalSession) - a
                ``HierarchyTraversalSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_traversal()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_traversal()`` is ``true``.*

        """
        if not self.supports_hierarchy_traversal():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyTraversalSession(runtime=self._runtime)

    hierarchy_traversal_session = property(fget=get_hierarchy_traversal_session)

    @utilities.arguments_not_none
    def get_hierarchy_traversal_session_for_hierarchy(self, hierarchy_id):
        """Gets the ``OsidSession`` associated with the hierarchy traversal service for the given hierarchy.

        arg:    hierarchy_id (osid.id.Id): the ``Id`` of the hierarchy
        return: (osid.hierarchy.HierarchyTraversalSession) - the new
                ``HierarchyTraversalSession``
        raise:  NotFound - ``hierarchy_id`` not found
        raise:  NullArgument - ``hierarchyid`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_hierarchy_traversal()`` or
                ``supports_visible_fedaration()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_traversal()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_hierarchy_traversal():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.HierarchyTraversalSession(hierarchy_id, self._runtime)

    def get_hierarchy_design_session(self):
        """Gets the ``OsidSession`` associated with the hierarchy design service.

        return: (osid.hierarchy.HierarchyDesignSession) - a
                ``HierarchyDesignSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_design()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_design()`` is ``true``.*

        """
        if not self.supports_hierarchy_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyDesignSession(runtime=self._runtime)

    hierarchy_design_session = property(fget=get_hierarchy_design_session)

    @utilities.arguments_not_none
    def get_hierarchy_design_session_for_hierarchy(self, hierarchy_id):
        """Gets the ``OsidSession`` associated with the topology design service using for the given hierarchy.

        arg:    hierarchy_id (osid.id.Id): the ``Id`` of the graph
        return: (osid.hierarchy.HierarchyDesignSession) - a
                ``HierarchyDesignSession``
        raise:  NotFound - ``hierarchy_id`` is not found
        raise:  NullArgument - ``hierarchy_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_design()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_design()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_hierarchy_design():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.HierarchyDesignSession(hierarchy_id, self._runtime)

    def get_hierarchy_sequencing_session(self):
        """Gets the ``OsidSession`` associated with the hierarchy sequencing service.

        return: (osid.hierarchy.HierarchySequencingSession) - a
                ``HierarchySequencingSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_sequencing()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_sequencing()`` is ``true``.*

        """
        if not self.supports_hierarchy_sequencing():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchySequencingSession(runtime=self._runtime)

    hierarchy_sequencing_session = property(fget=get_hierarchy_sequencing_session)

    @utilities.arguments_not_none
    def get_hierarchy_sequencing_session_for_hierarchy(self, hierarchy_id):
        """Gets the ``OsidSession`` associated with the sequencing design service using for the given hierarchy.

        arg:    hierarchy_id (osid.id.Id): the ``Id`` of the graph
        return: (osid.hierarchy.HierarchySequencingSession) - a
                ``HierarchySequencingSession``
        raise:  NotFound - ``hierarchy_id`` is not found
        raise:  NullArgument - ``hierarchy_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_sequencing()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_sequencing()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_hierarchy_sequencing():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.HierarchySequencingSession(hierarchy_id, self._runtime)

    @utilities.arguments_not_none
    def get_hierarchy_structure_notification_session(self, hierarchy_structure_receiver):
        """Gets the session for subscribing to notifications of changes within a hierarchy structure.

        arg:    hierarchy_structure_receiver
                (osid.hierarchy.HierarchyStructureReceiver): a receiver
        return: (osid.hierarchy.HierarchyStructureNotificationSession) -
                a ``HierarchyStructureNotificationSession``
        raise:  NullArgument - ``hierarchy_structure_receiver`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_hierarchy_structure_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_structure_notification()`` is ``true``.*

        """
        if not self.supports_hierarchy_structure_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyStructureNotificationSession(runtime=self._runtime, receiver=hierarchy_structure_receiver)

    @utilities.arguments_not_none
    def get_hierarchy_structure_notification_session_for_hierarchy(self, hierarchy_structure_receiver, hierarchy_id):
        """Gets the session for subscribing to notifications of changes within a hierarchy structure for the given hierarchy.

        arg:    hierarchy_structure_receiver
                (osid.hierarchy.HierarchyStructureReceiver): a receiver
        arg:    hierarchy_id (osid.id.Id): the ``Id`` of the graph
        return: (osid.hierarchy.HierarchyStructureNotificationSession) -
                a ``HierarchyStructureNotificationSession``
        raise:  NotFound - ``hierarchy_id`` is not found
        raise:  NullArgument - ``hierarchy_structure_receiver`` or
                ``hierarchy_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_hierarchy_structure_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_structure_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_hierarchy_structure_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.HierarchyStructureNotificationSession(hierarchy_id, runtime=self._runtime, receiver=hierarchy_structure_receiver)

    def get_hierarchy_lookup_session(self):
        """Gets the ``OsidSession`` associated with the hierarchy lookup service.

        return: (osid.hierarchy.HierarchyLookupSession) - a
                ``HierarchyLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_lookup()`` is ``true``.*

        """
        if not self.supports_hierarchy_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyLookupSession(runtime=self._runtime)

    hierarchy_lookup_session = property(fget=get_hierarchy_lookup_session)

    def get_hierarchy_query_session(self):
        """Gets the ``OsidSession`` associated with the hierarchy query service.

        return: (osid.hierarchy.HierarchyQuerySession) - a
                ``HierarchyQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_query()`` is ``true``.*

        """
        if not self.supports_hierarchy_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyQuerySession(runtime=self._runtime)

    hierarchy_query_session = property(fget=get_hierarchy_query_session)

    def get_hierarchy_search_session(self):
        """Gets the ``OsidSession`` associated with the hierarchy search service.

        return: (osid.hierarchy.HierarchySearchSession) - a
                ``HierarchySearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_search()`` is ``true``.*

        """
        if not self.supports_hierarchy_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchySearchSession(runtime=self._runtime)

    hierarchy_search_session = property(fget=get_hierarchy_search_session)

    def get_hierarchy_admin_session(self):
        """Gets the hierarchy administrative session.

        return: (osid.hierarchy.HierarchyAdminSession) - a
                ``HierarchyAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_admin()`` is ``true``.*

        """
        if not self.supports_hierarchy_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyAdminSession(runtime=self._runtime)

    hierarchy_admin_session = property(fget=get_hierarchy_admin_session)

    @utilities.arguments_not_none
    def get_hierarchy_notification_session(self, hierarchy_receiver):
        """Gets a hierarchy notification session.

        arg:    hierarchy_receiver (osid.hierarchy.HierarchyReceiver):
                notification callback
        return: (osid.hierarchy.HierarchyNotificationSession) - a
                ``HierarchyNotificationSession``
        raise:  NullArgument - ``hierarchy_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_notification()`` is ``true``.*

        """
        if not self.supports_hierarchy_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyNotificationSession(runtime=self._runtime, receiver=hierarchy_receiver)


class HierarchyProxyManager(osid_managers.OsidProxyManager, HierarchyProfile, hierarchy_managers.HierarchyProxyManager):
    """The hierarchy manager provides access sessions to traverse and manage hierrachies of ``Ids``.

    Methods in this manager accept a ``Proxy`` to pass information from
    server environments. The sessions included in this manager are:

      * ``HierarchyTraversalSession:`` a basic session traversing a
        hierarchy
      * ``HierarchyDesignSession:`` a session to design a hierarchy
      * ``HierarchySequencingSession:`` a session to sequence nodes in a
        hierarchy
      * ``HierarchyStructureNotificationSession:`` a session for
        notififcations within a hierarchy structure
      * ``HierarchyLookupSession:`` a session looking up hiererachies
      * ``HierarchyQuerySession:`` a session querying hiererachies
      * ``HierarchySearchSession:`` a session for searching for
        hierarchies
      * ``HierarchyAdminSession:`` a session for creating and deleting
        hierarchies
      * ``HierarchyNotificationSession:`` a session for subscribing to
        changes in hierarchies


    """

    def __init__(self):
        osid_managers.OsidProxyManager.__init__(self)

    @utilities.arguments_not_none
    def get_hierarchy_traversal_session(self, proxy):
        """Gets the ``OsidSession`` associated with the hierarchy traversal service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchyTraversalSession) - a
                ``HierarchyTraversalSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_traversal()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_traversal()`` is ``true``.*

        """
        if not self.supports_hierarchy_traversal():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyTraversalSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_hierarchy_traversal_session_for_hierarchy(self, hierarchy_id, proxy):
        """Gets the ``OsidSession`` associated with the hierarchy traversal service for the given hierarchy.

        arg:    hierarchy_id (osid.id.Id): the ``Id`` of the hierarchy
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchyTraversalSession) - a
                ``HierarchyTraversalSession``
        raise:  NotFound - ``hierarchyid`` not found
        raise:  NullArgument - ``hierarchy_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_hierarchy_traversal()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_traversal()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_hierarchy_traversal():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.HierarchyTraversalSession(hierarchy_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_hierarchy_design_session(self, proxy):
        """Gets the ``OsidSession`` associated with the hierarchy design service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchyDesignSession) - a
                ``HierarchyDesignSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_design()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_design()`` is ``true``.*

        """
        if not self.supports_hierarchy_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyDesignSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_hierarchy_design_session_for_hierarchy(self, hierarchy_id, proxy):
        """Gets the ``OsidSession`` associated with the topology design service using for the given hierarchy.

        arg:    hierarchy_id (osid.id.Id): the ``Id`` of the hierarchy
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchyDesignSession) - a
                ``HierarchyDesignSession``
        raise:  NotFound - ``hierarchy_id`` is not found
        raise:  NullArgument - ``hierarchy_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_design()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_design()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_hierarchy_design():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.HierarchyDesignSession(hierarchy_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_hierarchy_sequencing_session(self, proxy):
        """Gets the ``OsidSession`` associated with the hierarchy sequencing service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchySequencingSession) - a
                ``HierarchySequencingSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_sequencing()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_sequencing()`` is ``true``.*

        """
        if not self.supports_hierarchy_sequencing():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchySequencingSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_hierarchy_sequencing_session_for_hierarchy(self, hierarchy_id, proxy):
        """Gets the ``OsidSession`` associated with the sequencing design service using for the given hierarchy.

        arg:    hierarchy_id (osid.id.Id): the ``Id`` of the graph
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchySequencingSession) - a
                ``HierarchySequencingSession``
        raise:  NotFound - ``hierarchy_id`` is not found
        raise:  NullArgument - ``hierarchy_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_sequencing()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_sequencing()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_hierarchy_sequencing():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.HierarchySequencingSession(hierarchy_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_hierarchy_structure_notification_session(self, hierarchy_structure_receiver, proxy):
        """Gets the session for subscribing to notifications of changes within a hierarchy structure.

        arg:    hierarchy_structure_receiver
                (osid.hierarchy.HierarchyStructureReceiver): a receiver
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchyStructureNotificationSession) -
                a ``HierarchyStructureNotificationSession``
        raise:  NullArgument - ``hierarchy_structure_receiver`` or
                ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_hierarchy_structure_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_structure_notification()`` is ``true``.*

        """
        if not self.supports_hierarchy_structure_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyStructureNotificationSession(proxy=proxy, runtime=self._runtime, receiver=hierarchy_structure_receiver)

    @utilities.arguments_not_none
    def get_hierarchy_structure_notification_session_for_hierarchy(self, hierarchy_structure_receiver, hierarchy_id, proxy):
        """Gets the session for subscribing to notifications of changes within a hierarchy structure for the given hierarchy.

        arg:    hierarchy_structure_receiver
                (osid.hierarchy.HierarchyStructureReceiver): a receiver
        arg:    hierarchy_id (osid.id.Id): the ``Id`` of the hierarchy
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchyStructureNotificationSession) -
                a ``HierarchyStructureNotificationSession``
        raise:  NotFound - ``hierarchy_id`` is not found
        raise:  NullArgument - ``hierarchy_structure_receiver,
                hierarchy_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_hierarchy_structure_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_structure_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_hierarchy_structure_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.HierarchyStructureNotificationSession(catalog_id=hierarchy_id, proxy=proxy, runtime=self._runtime, receiver=hierarchy_structure_receiver)

    @utilities.arguments_not_none
    def get_hierarchy_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the hierarchy lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchyLookupSession) - a
                ``HierarchyLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_lookup()`` is ``true``.*

        """
        if not self.supports_hierarchy_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_hierarchy_query_session(self, proxy):
        """Gets the ``OsidSession`` associated with the hierarchy query service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchyQuerySession) - a
                ``HierarchyQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_query()`` is ``true``.*

        """
        if not self.supports_hierarchy_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_hierarchy_search_session(self, proxy):
        """Gets the ``OsidSession`` associated with the hierarchy search service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchySearchSession) - a
                ``HierarchySearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_search()`` is ``true``.*

        """
        if not self.supports_hierarchy_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchySearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_hierarchy_admin_session(self, proxy):
        """Gets the hierarchy administrative session.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchyAdminSession) - a
                ``HierarchyAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_admin()`` is ``true``.*

        """
        if not self.supports_hierarchy_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_hierarchy_notification_session(self, hierarchy_receiver, proxy):
        """Gets the hierarchy notification session.

        arg:    hierarchy_receiver (osid.hierarchy.HierarchyReceiver):
                notification callback
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.hierarchy.HierarchyNotificationSession) - a
                ``HierarchyNotificationSession``
        raise:  NullArgument - ``hierarchy_receiver`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_hierarchy_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_hierarchy_notification()`` is ``true``.*

        """
        if not self.supports_hierarchy_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.HierarchyNotificationSession(proxy=proxy, runtime=self._runtime, receiver=hierarchy_receiver)



"""GStudio implementations of repository managers."""

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
from dlkit.manager_impls.repository import managers as repository_managers




class RepositoryProfile(osid_managers.OsidProfile, repository_managers.RepositoryProfile):
    """The repository profile describes interoperability among repository services."""

    def supports_visible_federation(self):
        """Tests if federation is visible.

        return: (boolean) - ``true`` if visible federation is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_asset_lookup(self):
        """Tests if asset lookup is supported.

        return: (boolean) - ``true`` if asset lookup is supported ``,``
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return True # Change to True when implemented.

    def supports_asset_query(self):
        """Tests if asset query is supported.

        return: (boolean) - ``true`` if asset query is supported ``,``
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return True # Change to True when implemented.

    def supports_asset_search(self):
        """Tests if asset search is supported.

        return: (boolean) - ``true`` if asset search is supported ``,``
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_asset_admin(self):
        """Tests if asset administration is supported.

        return: (boolean) - ``true`` if asset administration is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return True # Change to True when implemented.

    def supports_asset_notification(self):
        """Tests if asset notification is supported.

        A repository may send messages when assets are created,
        modified, or deleted.

        return: (boolean) - ``true`` if asset notification is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_asset_repository(self):
        """Tests if retrieving mappings of assets and repositories is supported.

        return: (boolean) - ``true`` if asset repository mapping
                retrieval is supported ``,`` ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_asset_repository_assignment(self):
        """Tests if managing mappings of assets and repositories is supported.

        return: (boolean) - ``true`` if asset repository assignment is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_asset_smart_repository(self):
        """Tests if asset smart repository is supported.

        return: (boolean) - ``true`` if asset smart repository is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_asset_temporal(self):
        """Tests if retrieving mappings of assets and time coverage is supported.

        return: (boolean) - ``true`` if asset temporal mapping retrieval
                is supported ``,`` ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_asset_temporal_assignment(self):
        """Tests if managing mappings of assets and time ocverage is supported.

        return: (boolean) - ``true`` if asset temporal assignment is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_asset_spatial(self):
        """Tests if retrieving mappings of assets and spatial coverage is supported.

        return: (boolean) - ``true`` if asset spatial mapping retrieval
                is supported ``,`` ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_asset_spatial_assignment(self):
        """Tests if managing mappings of assets and spatial ocverage is supported.

        return: (boolean) - ``true`` if asset spatial assignment is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_asset_composition(self):
        """Tests if assets are included in compositions.

        return: (boolean) - ``true`` if asset composition supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_asset_composition_design(self):
        """Tests if mapping assets to compositions is supported.

        return: (boolean) - ``true`` if designing asset compositions is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_composition_lookup(self):
        """Tests if composition lookup is supported.

        return: (boolean) - ``true`` if composition lookup is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_composition_query(self):
        """Tests if composition query is supported.

        return: (boolean) - ``true`` if composition query is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_composition_search(self):
        """Tests if composition search is supported.

        return: (boolean) - ``true`` if composition search is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_composition_admin(self):
        """Tests if composition administration is supported.

        return: (boolean) - ``true`` if composition administration is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_composition_notification(self):
        """Tests if composition notification is supported.

        return: (boolean) - ``true`` if composition notification is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_composition_repository(self):
        """Tests if retrieval of composition to repository mappings is supported.

        return: (boolean) - ``true`` if composition to repository
                mapping is supported ``,`` ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_composition_repository_assignment(self):
        """Tests if assigning composition to repository mappings is supported.

        return: (boolean) - ``true`` if composition to repository
                assignment is supported ``,`` ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_composition_smart_repository(self):
        """Tests if composition smart repository is supported.

        return: (boolean) - ``true`` if composition smart repository is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_repository_lookup(self):
        """Tests if repository lookup is supported.

        return: (boolean) - ``true`` if repository lookup is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return True # Change to True when implemented.

    def supports_repository_query(self):
        """Tests if repository query is supported.

        return: (boolean) - ``true`` if repository query is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_repository_search(self):
        """Tests if repository search is supported.

        return: (boolean) - ``true`` if repository search is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_repository_admin(self):
        """Tests if repository administration is supported.

        return: (boolean) - ``true`` if repository administration is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return True # Change to True when implemented.

    def supports_repository_notification(self):
        """Tests if repository notification is supported.

        Messages may be sent when ``Repository`` objects are created,
        deleted or updated. Notifications for assets within repositories
        are sent via the asset notification session.

        return: (boolean) - ``true`` if repository notification is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_repository_hierarchy(self):
        """Tests if a repository hierarchy traversal is supported.

        return: (boolean) - ``true`` if a repository hierarchy traversal
                is supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return True # Change to True when implemented.

    def supports_repository_hierarchy_design(self):
        """Tests if a repository hierarchy design is supported.

        return: (boolean) - ``true`` if a repository hierarchy design is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_repository_batch(self):
        """Tests if a repository batch service is supported.

        return: (boolean) - ``true`` if a repository batch service is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_repository_rules(self):
        """Tests if a repository rules service is supported.

        return: (boolean) - ``true`` if a repository rules service is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def get_asset_record_types(self):
        """Gets all the asset record types supported.

        return: (osid.type.TypeList) - the list of supported asset
                record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ASSET_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    asset_record_types = property(fget=get_asset_record_types)

    @utilities.arguments_not_none
    def supports_asset_record_type(self, asset_record_type):
        """Tests if a given asset type is supported.

        arg:    asset_record_type (osid.type.Type): the asset record
                type
        return: (boolean) - ``true`` if the asset record type is
                supported ``,``  ``false`` otherwise
        raise:  NullArgument - ``asset_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ASSET_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (asset_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    asset_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    asset_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_asset_search_record_types(self):
        """Gets all the asset search record types supported.

        return: (osid.type.TypeList) - the list of supported asset
                search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ASSET_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    asset_search_record_types = property(fget=get_asset_search_record_types)

    @utilities.arguments_not_none
    def supports_asset_search_record_type(self, asset_search_record_type):
        """Tests if a given asset search record type is supported.

        arg:    asset_search_record_type (osid.type.Type): the asset
                search record type
        return: (boolean) - ``true`` if the asset search record type is
                supported ``,``  ``false`` otherwise
        raise:  NullArgument - ``asset_search_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ASSET_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (asset_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    asset_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    asset_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_asset_content_record_types(self):
        """Gets all the asset content record types supported.

        return: (osid.type.TypeList) - the list of supported asset
                content record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ASSET_CONTENT_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    asset_content_record_types = property(fget=get_asset_content_record_types)

    @utilities.arguments_not_none
    def supports_asset_content_record_type(self, asset_content_record_type):
        """Tests if a given asset content record type is supported.

        arg:    asset_content_record_type (osid.type.Type): the asset
                content record type
        return: (boolean) - ``true`` if the asset content record type is
                supported ``,``  ``false`` otherwise
        raise:  NullArgument - ``asset_content_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ASSET_CONTENT_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (asset_content_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    asset_content_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    asset_content_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_composition_record_types(self):
        """Gets all the composition record types supported.

        return: (osid.type.TypeList) - the list of supported composition
                record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('COMPOSITION_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    composition_record_types = property(fget=get_composition_record_types)

    @utilities.arguments_not_none
    def supports_composition_record_type(self, composition_record_type):
        """Tests if a given composition record type is supported.

        arg:    composition_record_type (osid.type.Type): the
                composition record type
        return: (boolean) - ``true`` if the composition record type is
                supported ``,``  ``false`` otherwise
        raise:  NullArgument - ``composition_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('COMPOSITION_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (composition_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    composition_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    composition_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_composition_search_record_types(self):
        """Gets all the composition search record types supported.

        return: (osid.type.TypeList) - the list of supported composition
                search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('COMPOSITION_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    composition_search_record_types = property(fget=get_composition_search_record_types)

    @utilities.arguments_not_none
    def supports_composition_search_record_type(self, composition_search_record_type):
        """Tests if a given composition search record type is supported.

        arg:    composition_search_record_type (osid.type.Type): the
                composition serach type
        return: (boolean) - ``true`` if the composition search record
                type is supported ``,`` ``false`` otherwise
        raise:  NullArgument - ``composition_search_record_type`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('COMPOSITION_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (composition_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    composition_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    composition_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_repository_record_types(self):
        """Gets all the repository record types supported.

        return: (osid.type.TypeList) - the list of supported repository
                record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('REPOSITORY_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    repository_record_types = property(fget=get_repository_record_types)

    @utilities.arguments_not_none
    def supports_repository_record_type(self, repository_record_type):
        """Tests if a given repository record type is supported.

        arg:    repository_record_type (osid.type.Type): the repository
                record type
        return: (boolean) - ``true`` if the repository record type is
                supported ``,``  ``false`` otherwise
        raise:  NullArgument - ``repository_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('REPOSITORY_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (repository_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    repository_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    repository_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_repository_search_record_types(self):
        """Gets all the repository search record types supported.

        return: (osid.type.TypeList) - the list of supported repository
                search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('REPOSITORY_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    repository_search_record_types = property(fget=get_repository_search_record_types)

    @utilities.arguments_not_none
    def supports_repository_search_record_type(self, repository_search_record_type):
        """Tests if a given repository search record type is supported.

        arg:    repository_search_record_type (osid.type.Type): the
                repository search type
        return: (boolean) - ``true`` if the repository search record
                type is supported ``,`` ``false`` otherwise
        raise:  NullArgument - ``repository_search_record_type`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('REPOSITORY_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (repository_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    repository_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    repository_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_spatial_unit_record_types(self):
        """Gets all the spatial unit record types supported.

        return: (osid.type.TypeList) - the list of supported spatial
                unit record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('SPATIAL_UNIT_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    spatial_unit_record_types = property(fget=get_spatial_unit_record_types)

    @utilities.arguments_not_none
    def supports_spatial_unit_record_type(self, spatial_unit_record_type):
        """Tests if a given spatial unit record type is supported.

        arg:    spatial_unit_record_type (osid.type.Type): the spatial
                unit record type
        return: (boolean) - ``true`` if the spatial unit record type is
                supported ``,``  ``false`` otherwise
        raise:  NullArgument - ``spatial_unit_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('SPATIAL_UNIT_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (spatial_unit_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    spatial_unit_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    spatial_unit_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_coordinate_types(self):
        """Gets all the coordinate types supported.

        return: (osid.type.TypeList) - the list of supported coordinate
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.repository.RepositoryProfile.get_coordinate_types
        return TypeList([])

    coordinate_types = property(fget=get_coordinate_types)

    @utilities.arguments_not_none
    def supports_coordinate_type(self, coordinate_type):
        """Tests if a given coordinate type is supported.

        arg:    coordinate_type (osid.type.Type): the coordinate type
        return: (boolean) - ``true`` if the coordinate type is supported
                ``,``  ``false`` otherwise
        raise:  NullArgument - ``coordinate_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.repository.RepositoryProfile.supports_coordinate_type
        return False


class RepositoryManager(osid_managers.OsidManager, RepositoryProfile, repository_managers.RepositoryManager):
    """The repository manager provides access to asset lookup and creation session and provides interoperability tests for various aspects of this service.

    The sessions included in this manager are:

      * ``AssetLookupSession:`` a session to retrieve assets
      * ``AssetQuerySession:`` a session to query assets
      * ``AssetSearchSession:`` a session to search for assets
      * ``AssetAdminSession:`` a session to create and delete assets
      * ``AssetNotificationSession:`` a session to receive notifications
        pertaining to asset changes
      * ``AssetRepositorySession:`` a session to look up asset to
        repository mappings
      * ``AssetRepositoryAssignmentSession:`` a session to manage asset
        to repository mappings
      * ``AssetSmartRepositorySession:`` a session to manage dynamic
        repositories of assets
      * ``AssetTemporalSession:`` a session to access the temporal
        coverage of an asset
      * ``AssetTemporalAssignmentSession:`` a session to manage the
        temporal coverage of an asset
      * ``AssetSpatialSession:`` a session to access the spatial
        coverage of an asset
      * ``AssetSpatialAssignmentSession:`` a session to manage the
        spatial coverage of an asset
      * ``AssetCompositionSession:`` a session to look up asset
        composition mappings
      * ``AssetCompositionDesignSession:`` a session to map assets to
        compositions

      * ``CompositionLookupSession: a`` session to retrieve compositions
      * ``CompositionQuerySession:`` a session to query compositions
      * ``CompositionSearchSession:`` a session to search for
        compositions
      * ``CompositionAdminSession:`` a session to create, update and
        delete compositions
      * ``CompositionNotificationSession:`` a session to receive
        notifications pertaining to changes in compositions
      * ``CompositionRepositorySession:`` a session to retrieve
        composition repository mappings
      * ``CompositionRepositoryAssignmentSession:`` a session to manage
        composition repository mappings
      * ``CompositionSmartRepositorySession:`` a session to manage
        dynamic repositories of compositions

      * ``RepositoryLookupSession: a`` session to retrieve repositories
      * ``RepositoryQuerySession:`` a session to query repositories
      * ``RepositorySearchSession:`` a session to search for
        repositories
      * ``RepositoryAdminSession:`` a session to create, update and
        delete repositories
      * ``RepositoryNotificationSession:`` a session to receive
        notifications pertaining to changes in repositories
      * ``RepositoryHierarchySession:`` a session to traverse repository
        hierarchies
      * ``RepositoryHierarchyDesignSession:`` a session to manage
        repository hierarchies


    """

    def __init__(self):
        osid_managers.OsidManager.__init__(self)

    def get_asset_lookup_session(self):
        """Gets the ``OsidSession`` associated with the asset lookup service.

        return: (osid.repository.AssetLookupSession) - the new
                ``AssetLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_lookup()`` is ``true``.*

        """
        if not self.supports_asset_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetLookupSession(runtime=self._runtime)

    asset_lookup_session = property(fget=get_asset_lookup_session)

    @utilities.arguments_not_none
    def get_asset_lookup_session_for_repository(self, repository_id):
        """Gets the ``OsidSession`` associated with the asset lookup service for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.AssetLookupSession) - the new
                ``AssetLookupSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_asset_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetLookupSession(repository_id, self._runtime)

    def get_asset_query_session(self):
        """Gets an asset query session.

        return: (osid.repository.AssetQuerySession) - an
                ``AssetQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_query()`` is ``true``.*

        """
        if not self.supports_asset_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetQuerySession(runtime=self._runtime)

    asset_query_session = property(fget=get_asset_query_session)

    @utilities.arguments_not_none
    def get_asset_query_session_for_repository(self, repository_id):
        """Gets an asset query session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.AssetQuerySession) - an
                ``AssetQuerySession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_asset_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_query()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_asset_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetQuerySession(repository_id, self._runtime)

    def get_asset_search_session(self):
        """Gets an asset search session.

        return: (osid.repository.AssetSearchSession) - an
                ``AssetSearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_search()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_search()`` is ``true``.*

        """
        if not self.supports_asset_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetSearchSession(runtime=self._runtime)

    asset_search_session = property(fget=get_asset_search_session)

    @utilities.arguments_not_none
    def get_asset_search_session_for_repository(self, repository_id):
        """Gets an asset search session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.AssetSearchSession) - an
                ``AssetSearchSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_asset_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetSearchSession(repository_id, self._runtime)

    def get_asset_admin_session(self):
        """Gets an asset administration session for creating, updating and deleting assets.

        return: (osid.repository.AssetAdminSession) - an
                ``AssetAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_admin()`` is ``true``.*

        """
        if not self.supports_asset_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetAdminSession(runtime=self._runtime)

    asset_admin_session = property(fget=get_asset_admin_session)

    @utilities.arguments_not_none
    def get_asset_admin_session_for_repository(self, repository_id):
        """Gets an asset administration session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.AssetAdminSession) - an
                ``AssetAdminSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_admin()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_asset_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetAdminSession(repository_id, self._runtime)

    @utilities.arguments_not_none
    def get_asset_notification_session(self, asset_receiver):
        """Gets the notification session for notifications pertaining to asset changes.

        arg:    asset_receiver (osid.repository.AssetReceiver): the
                notification callback
        return: (osid.repository.AssetNotificationSession) - an
                ``AssetNotificationSession``
        raise:  NullArgument - ``asset_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_notification()`` is ``true``.*

        """
        if not self.supports_asset_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetNotificationSession(runtime=self._runtime, receiver=asset_receiver)

    @utilities.arguments_not_none
    def get_asset_notification_session_for_repository(self, asset_receiver, repository_id):
        """Gets the asset notification session for the given repository.

        arg:    asset_receiver (osid.repository.AssetReceiver): the
                notification callback
        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.AssetNotificationSession) - an
                ``AssetNotificationSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``asset_receiver`` or ``repository_id``
                is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_asset_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_notfication()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetNotificationSession(repository_id, runtime=self._runtime, receiver=asset_receiver)

    def get_asset_repository_session(self):
        """Gets the session for retrieving asset to repository mappings.

        return: (osid.repository.AssetRepositorySession) - an
                ``AssetRepositorySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_repository()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_repository()`` is ``true``.*

        """
        if not self.supports_asset_repository():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetRepositorySession(runtime=self._runtime)

    asset_repository_session = property(fget=get_asset_repository_session)

    def get_asset_repository_assignment_session(self):
        """Gets the session for assigning asset to repository mappings.

        return: (osid.repository.AssetRepositoryAssignmentSession) - an
                ``AssetRepositoryAsignmentSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_asset_repository_assignment()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_repository_assignment()`` is ``true``.*

        """
        if not self.supports_asset_repository_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetRepositoryAssignmentSession(runtime=self._runtime)

    asset_repository_assignment_session = property(fget=get_asset_repository_assignment_session)

    @utilities.arguments_not_none
    def get_asset_smart_repository_session(self, repository_id):
        """Gets an asset smart repository session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.AssetSmartRepositorySession) - an
                ``AssetSmartRepositorySession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_asset_smart_repository()``
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_smart_repository()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def get_asset_temporal_session(self):
        """Gets the session for retrieving temporal coverage of an asset.

        return: (osid.repository.AssetTemporalSession) - an
                ``AssetTemporalSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_temporal()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_temporal()`` is ``true``.*

        """
        if not self.supports_asset_temporal():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetTemporalSession(runtime=self._runtime)

    asset_temporal_session = property(fget=get_asset_temporal_session)

    @utilities.arguments_not_none
    def get_asset_temporal_session_for_repository(self, repository_id):
        """Gets the session for retrieving temporal coverage of an asset for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.AssetTemporalSession) - an
                ``AssetTemporalSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_temporal()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_temporal()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_temporal():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetTemporalSession(repository_id, self._runtime)

    def get_asset_temporal_assignment_session(self):
        """Gets the session for assigning temporal coverage to an asset.

        return: (osid.repository.AssetTemporalAssignmentSession) - an
                ``AssetTemporalAssignmentSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_temporal_assignment()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_temporal_assignment()`` is ``true``.*

        """
        if not self.supports_asset_temporal_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetTemporalAssignmentSession(runtime=self._runtime)

    asset_temporal_assignment_session = property(fget=get_asset_temporal_assignment_session)

    @utilities.arguments_not_none
    def get_asset_temporal_assignment_session_for_repository(self, repository_id):
        """Gets the session for assigning temporal coverage of an asset for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.AssetTemporalAssignmentSession) - an
                ``AssetTemporalAssignmentSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_temporal_assignment()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_temporal_assignment()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_temporal_assignment():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetTemporalAssignmentSession(repository_id, self._runtime)

    def get_asset_spatial_session(self):
        """Gets the session for retrieving spatial coverage of an asset.

        return: (osid.repository.AssetSpatialSession) - an
                ``AssetSpatialSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_spatial_assets()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_spatial_assets()`` is ``true``.*

        """
        if not self.supports_asset_spatial():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetSpatialSession(runtime=self._runtime)

    asset_spatial_session = property(fget=get_asset_spatial_session)

    @utilities.arguments_not_none
    def get_asset_spatial_session_for_repository(self, repository_id):
        """Gets the session for retrieving spatial coverage of an asset for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.AssetSpatialSession) - an
                ``AssetSpatialSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_spatial()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_spatial()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_spatial():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetSpatialSession(repository_id, self._runtime)

    def get_asset_spatial_assignment_session(self):
        """Gets the session for assigning spatial coverage to an asset.

        return: (osid.repository.AssetSpatialAssignmentSession) - an
                ``AssetSpatialAssignmentSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_spatial_assignment()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_spatial_assignment()`` is ``true``.*

        """
        if not self.supports_asset_spatial_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetSpatialAssignmentSession(runtime=self._runtime)

    asset_spatial_assignment_session = property(fget=get_asset_spatial_assignment_session)

    @utilities.arguments_not_none
    def get_asset_spatial_assignment_session_for_repository(self, repository_id):
        """Gets the session for assigning spatial coverage of an asset for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.AssetSpatialAssignmentSession) - an
                ``AssetSpatialAssignmentSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_spatial_assignment()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_spatial_assignment()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_spatial_assignment():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetSpatialAssignmentSession(repository_id, self._runtime)

    def get_asset_composition_session(self):
        """Gets the session for retrieving asset compositions.

        return: (osid.repository.AssetCompositionSession) - an
                ``AssetCompositionSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_composition()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_composition()`` is ``true``.*

        """
        if not self.supports_asset_composition():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetCompositionSession(runtime=self._runtime)

    asset_composition_session = property(fget=get_asset_composition_session)

    def get_asset_composition_design_session(self):
        """Gets the session for creating asset compositions.

        return: (osid.repository.AssetCompositionDesignSession) - an
                ``AssetCompositionDesignSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_composition_design()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_composition_design()`` is ``true``.*

        """
        if not self.supports_asset_composition_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetCompositionDesignSession(runtime=self._runtime)

    asset_composition_design_session = property(fget=get_asset_composition_design_session)

    def get_asset_content_lookup_session(self):
        # This impl is temporary until Tom adds missing methods to RepositoryProxyManager in spec
        if not self.supports_asset_lookup():  # should be asset_content_lookup
            raise errors.Unimplemented()
        return sessions.AssetContentLookupSession(runtime=self._runtime) # pylint: disable=no-member

    @utilities.arguments_not_none
    def get_asset_content_lookup_session_for_repository(self, repository_id):
        # This impl is temporary until Tom adds missing methods to RepositoryProxyManager in spec
        if not self.supports_asset_lookup():  # should be asset_content_lookup
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        return sessions.AssetContentLookupSession(repository_id, runtime=self._runtime) # pylint: disable=no-member

    def get_composition_lookup_session(self):
        """Gets the ``OsidSession`` associated with the composition lookup service.

        return: (osid.repository.CompositionLookupSession) - the new
                ``CompositionLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_lookup()`` is ``true``.*

        """
        if not self.supports_composition_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionLookupSession(runtime=self._runtime)

    composition_lookup_session = property(fget=get_composition_lookup_session)

    @utilities.arguments_not_none
    def get_composition_lookup_session_for_repository(self, repository_id):
        """Gets the ``OsidSession`` associated with the composition lookup service for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.CompositionLookupSession) - the new
                ``CompositionLookupSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_composition_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_composition_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CompositionLookupSession(repository_id, self._runtime)

    def get_composition_query_session(self):
        """Gets a composition query session.

        return: (osid.repository.CompositionQuerySession) - a
                ``CompositionQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_query()`` is ``true``.*

        """
        if not self.supports_composition_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionQuerySession(runtime=self._runtime)

    composition_query_session = property(fget=get_composition_query_session)

    @utilities.arguments_not_none
    def get_composition_query_session_for_repository(self, repository_id):
        """Gets a composition query session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.CompositionQuerySession) - a
                ``CompositionQuerySession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_composition_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_query()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_composition_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CompositionQuerySession(repository_id, self._runtime)

    def get_composition_search_session(self):
        """Gets a composition search session.

        return: (osid.repository.CompositionSearchSession) - a
                ``CompositionSearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_search()`` is ``true``.*

        """
        if not self.supports_composition_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionSearchSession(runtime=self._runtime)

    composition_search_session = property(fget=get_composition_search_session)

    @utilities.arguments_not_none
    def get_composition_search_session_for_repository(self, repository_id):
        """Gets a composition search session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.CompositionSearchSession) - a
                ``CompositionSearchSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_composition_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_composition_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CompositionSearchSession(repository_id, self._runtime)

    def get_composition_admin_session(self):
        """Gets a composition administration session for creating, updating and deleting compositions.

        return: (osid.repository.CompositionAdminSession) - a
                ``CompositionAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_admin()`` is ``true``.*

        """
        if not self.supports_composition_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionAdminSession(runtime=self._runtime)

    composition_admin_session = property(fget=get_composition_admin_session)

    @utilities.arguments_not_none
    def get_composition_admin_session_for_repository(self, repository_id):
        """Gets a composiiton administrative session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.CompositionAdminSession) - a
                ``CompositionAdminSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_admin()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_composition_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CompositionAdminSession(repository_id, self._runtime)

    @utilities.arguments_not_none
    def get_composition_notification_session(self, composition_receiver):
        """Gets the notification session for notifications pertaining to composition changes.

        arg:    composition_receiver
                (osid.repository.CompositionReceiver): the notification
                callback
        return: (osid.repository.CompositionNotificationSession) - a
                ``CompositionNotificationSession``
        raise:  NullArgument - ``composition_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_notification()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_notification()`` is ``true``.*

        """
        if not self.supports_composition_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionNotificationSession(runtime=self._runtime, receiver=composition_receiver)

    @utilities.arguments_not_none
    def get_composition_notification_session_for_repository(self, composition_receiver, repository_id):
        """Gets the composition notification session for the given repository.

        arg:    composition_receiver
                (osid.repository.CompositionReceiver): the notification
                callback
        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.CompositionNotificationSession) - a
                ``CompositionNotificationSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``composition_receiver`` or
                ``repository_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_composition_notification()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_notfication()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_composition_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CompositionNotificationSession(repository_id, runtime=self._runtime, receiver=composition_receiver)

    def get_composition_repository_session(self):
        """Gets the session for retrieving composition to repository mappings.

        return: (osid.repository.CompositionRepositorySession) - a
                ``CompositionRepositorySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_repository()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_repository()`` is ``true``.*

        """
        if not self.supports_composition_repository():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionRepositorySession(runtime=self._runtime)

    composition_repository_session = property(fget=get_composition_repository_session)

    def get_composition_repository_assignment_session(self):
        """Gets the session for assigning composition to repository mappings.

        return: (osid.repository.CompositionRepositoryAssignmentSession)
                - a ``CompositionRepositoryAssignmentSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_composition_repository_assignment()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_repository_assignment()`` is ``true``.*

        """
        if not self.supports_composition_repository_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionRepositoryAssignmentSession(runtime=self._runtime)

    composition_repository_assignment_session = property(fget=get_composition_repository_assignment_session)

    @utilities.arguments_not_none
    def get_composition_smart_repository_session(self, repository_id):
        """Gets a composition smart repository session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        return: (osid.repository.CompositionSmartRepositorySession) - a
                ``CompositionSmartRepositorySession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented -
                ``supports_composition_smart_repository()``  ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_smart_repository()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def get_repository_lookup_session(self):
        """Gets the repository lookup session.

        return: (osid.repository.RepositoryLookupSession) - a
                ``RepositoryLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_lookup()`` is ``true``.*

        """
        if not self.supports_repository_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryLookupSession(runtime=self._runtime)

    repository_lookup_session = property(fget=get_repository_lookup_session)

    def get_repository_query_session(self):
        """Gets the repository query session.

        return: (osid.repository.RepositoryQuerySession) - a
                ``RepositoryQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_query()`` is ``true``.*

        """
        if not self.supports_repository_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryQuerySession(runtime=self._runtime)

    repository_query_session = property(fget=get_repository_query_session)

    def get_repository_search_session(self):
        """Gets the repository search session.

        return: (osid.repository.RepositorySearchSession) - a
                ``RepositorySearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_search()`` is ``true``.*

        """
        if not self.supports_repository_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositorySearchSession(runtime=self._runtime)

    repository_search_session = property(fget=get_repository_search_session)

    def get_repository_admin_session(self):
        """Gets the repository administrative session for creating, updating and deleteing repositories.

        return: (osid.repository.RepositoryAdminSession) - a
                ``RepositoryAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_admin()`` is ``true``.*

        """
        if not self.supports_repository_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryAdminSession(runtime=self._runtime)

    repository_admin_session = property(fget=get_repository_admin_session)

    @utilities.arguments_not_none
    def get_repository_notification_session(self, repository_receiver):
        """Gets the notification session for subscribing to changes to a repository.

        arg:    repository_receiver
                (osid.repository.RepositoryReceiver): the notification
                callback
        return: (osid.repository.RepositoryNotificationSession) - a
                ``RepositoryNotificationSession``
        raise:  NullArgument - ``repository_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_notification()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_notification()`` is ``true``.*

        """
        if not self.supports_repository_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryNotificationSession(runtime=self._runtime, receiver=repository_receiver)

    def get_repository_hierarchy_session(self):
        """Gets the repository hierarchy traversal session.

        return: (osid.repository.RepositoryHierarchySession) - ``a
                RepositoryHierarchySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_hierarchy()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_hierarchy()`` is ``true``.*

        """
        if not self.supports_repository_hierarchy():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryHierarchySession(runtime=self._runtime)

    repository_hierarchy_session = property(fget=get_repository_hierarchy_session)

    def get_repository_hierarchy_design_session(self):
        """Gets the repository hierarchy design session.

        return: (osid.repository.RepositoryHierarchyDesignSession) - a
                ``RepostoryHierarchyDesignSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_repository_hierarchy_design()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_hierarchy_design()`` is ``true``.*

        """
        if not self.supports_repository_hierarchy_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryHierarchyDesignSession(runtime=self._runtime)

    repository_hierarchy_design_session = property(fget=get_repository_hierarchy_design_session)

    def get_repository_batch_manager(self):
        """Gets a ``RepositoryBatchManager``.

        return: (osid.repository.batch.RepositoryBatchManager) - a
                ``RepostoryBatchManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_batch()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_batch()`` is ``true``.*

        """
        raise errors.Unimplemented()

    repository_batch_manager = property(fget=get_repository_batch_manager)

    def get_repository_rules_manager(self):
        """Gets a ``RepositoryRulesManager``.

        return: (osid.repository.rules.RepositoryRulesManager) - a
                ``RepostoryRulesManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_rules()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_rules()`` is ``true``.*

        """
        raise errors.Unimplemented()

    repository_rules_manager = property(fget=get_repository_rules_manager)

    @utilities.arguments_not_none
    def get_asset_composition_session_for_repository(self, repository_id):
        # This impl is temporary until Tom adds missing methods to RepositoryProxyManager in spec
        if not self.supports_asset_composition():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        return sessions.AssetCompositionSession(repository_id, runtime=self._runtime) # pylint: disable=no-member

    @utilities.arguments_not_none
    def get_asset_composition_design_session_for_repository(self, repository_id):
        # This impl is temporary until Tom adds missing methods to RepositoryProxyManager in spec
        if not self.supports_asset_composition():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        return sessions.AssetCompositionDesignSession(repository_id, runtime=self._runtime) # pylint: disable=no-member


class RepositoryProxyManager(osid_managers.OsidProxyManager, RepositoryProfile, repository_managers.RepositoryProxyManager):
    """The repository manager provides access to asset lookup and creation session and provides interoperability tests for various aspects of this service.

    Methods in this manager support the passing of a ``Proxy`` for the
    purposes of passing information from a server environment. The
    sessions included in this manager are:

      * ``AssetLookupSession:`` a session to retrieve assets
      * ``AssetQuerySession:`` a session to query assets
      * ``AssetSearchSession:`` a session to search for assets
      * ``AssetAdminSession:`` a session to create and delete assets
      * ``AssetNotificationSession:`` a session to receive notifications
        pertaining to asset changes
      * ``AssetRepositorySession:`` a session to look up asset to
        repository mappings
      * ``AssetRepositoryAssignmentSession:`` a session to manage asset
        to repository mappings
      * ``AssetSmartRepositorySession:`` a session to manage dynamic
        repositories of assets
      * ``AssetTemporalSession:`` a session to access the temporal
        coverage of an asset
      * ``AssetTemporalAssignmentSession:`` a session to manage the
        temporal coverage of an asset
      * ``AssetSpatialSession:`` a session to access the spatial
        coverage of an asset
      * ``AssetSpatialAssignmentSession:`` a session to manage the
        spatial coverage of an asset
      * ``AssetCompositionSession:`` a session to look up asset
        composition mappings
      * ``AssetCompositionDesignSession:`` a session to map assets to
        compositions

      * ``CompositionLookupSession: a`` session to retrieve compositions
      * ``CompositionQuerySession:`` a session to query compositions
      * ``CompositionSearchSession:`` a session to search for
        compositions
      * ``CompositionAdminSession:`` a session to create, update and
        delete compositions
      * ``CompositionNotificationSession:`` a session to receive
        notifications pertaining to changes in compositions
      * ``CompositionRepositorySession:`` a session to retrieve
        composition repository mappings
      * ``CompositionRepositoryAssignmentSession:`` a session to manage
        composition repository mappings
      * ``CompositionSmartRepositorySession:`` a session to manage
        dynamic repositories of compositions

      * ``RepositoryLookupSession: a`` session to retrieve repositories
      * ``RepositoryQuerySession:`` a session to query repositories
      * ``RepositorySearchSession:`` a session to search for
        repositories
      * ``RepositoryAdminSession:`` a session to create, update and
        delete repositories
      * ``RepositoryNotificationSession:`` a session to receive
        notifications pertaining to changes in repositories
      * ``RepositoryHierarchySession:`` a session to traverse repository
        hierarchies
      * ``RepositoryHierarchyDesignSession:`` a session to manage
        repository hierarchies


    """

    def __init__(self):
        osid_managers.OsidProxyManager.__init__(self)

    @utilities.arguments_not_none
    def get_asset_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the asset lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetLookupSession) - an
                ``AssetLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_lookup()`` is ``true``.*

        """
        if not self.supports_asset_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_asset_lookup_session_for_repository(self, repository_id, proxy):
        """Gets the ``OsidSession`` associated with the asset lookup service for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetLookupSession) - an
                ``AssetLookupSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_asset_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetLookupSession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_asset_query_session(self, proxy):
        """Gets the ``OsidSession`` associated with the asset query service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetQuerySession) - an
                ``AssetQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_query()`` is ``true``.*

        """
        if not self.supports_asset_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_asset_query_session_for_repository(self, repository_id, proxy):
        """Gets the ``OsidSession`` associated with the asset query service for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetQuerySession) - an
                ``AssetQuerySession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_asset_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_query()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_asset_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetQuerySession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_asset_search_session(self, proxy):
        """Gets an asset search session.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetSearchSession) - an
                ``AssetSearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_search()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_search()`` is ``true``.*

        """
        if not self.supports_asset_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetSearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_asset_search_session_for_repository(self, repository_id, proxy):
        """Gets an asset search session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetSearchSession) - an
                ``AssetSearchSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_asset_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetSearchSession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_asset_admin_session(self, proxy):
        """Gets an asset administration session for creating, updating and deleting assets.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetAdminSession) - an
                ``AssetAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_admin()`` is ``true``.*

        """
        if not self.supports_asset_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_asset_admin_session_for_repository(self, repository_id, proxy):
        """Gets an asset administration session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetAdminSession) - an
                ``AssetAdminSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_admin()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_asset_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetAdminSession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_asset_notification_session(self, asset_receiver, proxy):
        """Gets the notification session for notifications pertaining to asset changes.

        arg:    asset_receiver (osid.repository.AssetReceiver): the
                notification callback
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetNotificationSession) - an
                ``AssetNotificationSession``
        raise:  NullArgument - ``asset_receiver`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_notification()`` is ``true``.*

        """
        if not self.supports_asset_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetNotificationSession(proxy=proxy, runtime=self._runtime, receiver=asset_receiver)

    @utilities.arguments_not_none
    def get_asset_notification_session_for_repository(self, asset_receiver, repository_id, proxy):
        """Gets the asset notification session for the given repository.

        arg:    asset_receiver (osid.repository.AssetReceiver): the
                notification callback
        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetNotificationSession) - an
                ``AssetNotificationSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``asset_receiver, repository_id`` or
                ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_asset_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_notfication()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetNotificationSession(catalog_id=repository_id, proxy=proxy, runtime=self._runtime, receiver=asset_receiver)

    @utilities.arguments_not_none
    def get_asset_repository_session(self, proxy):
        """Gets the session for retrieving asset to repository mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetRepositorySession) - an
                ``AssetRepositorySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_repository()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_repository()`` is ``true``.*

        """
        if not self.supports_asset_repository():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetRepositorySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_asset_repository_assignment_session(self, proxy):
        """Gets the session for assigning asset to repository mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetRepositoryAssignmentSession) - an
                ``AssetRepositoryAsignmentSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_asset_repository_assignment()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_repository_assignment()`` is ``true``.*

        """
        if not self.supports_asset_repository_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetRepositoryAssignmentSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_asset_smart_repository_session(self, repository_id, proxy):
        """Gets an asset smart repository session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetSmartRepositorySession) - an
                ``AssetSmartRepositorySession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_asset_smart_repository()``
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_smart_repository()`` is ``true``.*

        """
        if not self.supports_asset_smart_repository():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetSmartRepositorySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_asset_temporal_session(self, proxy):
        """Gets the session for retrieving temporal coverage of an asset.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetTemporalSession) - an
                ``AssetTemporalSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_temporal()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_temporal()`` is ``true``.*

        """
        if not self.supports_asset_temporal():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetTemporalSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_asset_temporal_session_for_repository(self, repository_id, proxy):
        """Gets the session for retrieving temporal coverage of an asset for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetTemporalSession) - an
                ``AssetTemporalSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_temporal()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_temporal()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_temporal():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetTemporalSession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_asset_temporal_assignment_session(self, proxy):
        """Gets the session for assigning temporal coverage to an asset.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetTemporalAssignmentSession) - an
                ``AssetTemporalAssignmentSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_temporal_assignment()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_temporal_assignment()`` is ``true``.*

        """
        if not self.supports_asset_temporal_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetTemporalAssignmentSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_asset_temporal_assignment_session_for_repository(self, repository_id, proxy):
        """Gets the session for assigning temporal coverage of an asset for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetTemporalAssignmentSession) - an
                ``AssetTemporalAssignmentSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_temporal_assignment()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_temporal_assignment()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_temporal_assignment():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetTemporalAssignmentSession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_asset_spatial_session(self, proxy):
        """Gets the session for retrieving spatial coverage of an asset.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetSpatialSession) - an
                ``AssetSpatialSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_spatial_assets()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_spatial_assets()`` is ``true``.*

        """
        if not self.supports_asset_spatial():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetSpatialSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_asset_spatial_session_for_repository(self, repository_id, proxy):
        """Gets the session for retrieving spatial coverage of an asset for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetSpatialSession) - an
                ``AssetSpatialSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_spatial()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_spatial()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_spatial():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetSpatialSession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_asset_spatial_assignment_session(self, proxy):
        """Gets the session for assigning spatial coverage to an asset.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetSpatialAssignmentSession) - an
                ``AssetSpatialAssignmentSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_spatial_assignment()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_spatial_assignment()`` is ``true``.*

        """
        if not self.supports_asset_spatial_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetSpatialAssignmentSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_asset_spatial_assignment_session_for_repository(self, repository_id, proxy):
        """Gets the session for assigning spatial coverage of an asset for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetSpatialAssignmentSession) - an
                ``AssetSpatialAssignmentSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_spatial_assignment()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_spatial_assignment()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_asset_spatial_assignment():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssetSpatialAssignmentSession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_asset_composition_session(self, proxy):
        """Gets the session for retrieving asset compositions.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetCompositionSession) - an
                ``AssetCompositionSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_composition()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_composition()`` is ``true``.*

        """
        if not self.supports_asset_composition():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetCompositionSession(proxy=proxy, runtime=self._runtime)

    def get_asset_content_lookup_session(self, proxy):
        # This impl is temporary until Tom adds missing methods to RepositoryProxyManager in spec
        if not self.supports_asset_lookup():  # should be asset_content_lookup
            raise errors.Unimplemented()
        return sessions.AssetContentLookupSession(proxy, runtime=self._runtime) # pylint: disable=no-member

    @utilities.arguments_not_none
    def get_asset_content_lookup_session_for_repository(self, repository_id, proxy):
        # This impl is temporary until Tom adds missing methods to RepositoryProxyManager in spec
        if not self.supports_asset_lookup():  # should be asset_content_lookup
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        return sessions.AssetContentLookupSession(repository_id, proxy, runtime=self._runtime) # pylint: disable=no-member



    @utilities.arguments_not_none
    def get_asset_composition_design_session(self, proxy):
        """Gets the session for creating asset compositions.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.AssetCompositionDesignSession) - an
                ``AssetCompositionDesignSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_asset_composition_design()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_asset_composition_design()`` is ``true``.*

        """
        if not self.supports_asset_composition_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssetCompositionDesignSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_composition_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the composition lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionLookupSession) - the new
                ``CompositionLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_lookup()`` is ``true``.*

        """
        if not self.supports_composition_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_composition_lookup_session_for_repository(self, repository_id, proxy):
        """Gets the ``OsidSession`` associated with the composition lookup service for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionLookupSession) - the new
                ``CompositionLookupSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_composition_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_composition_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CompositionLookupSession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_composition_query_session(self, proxy):
        """Gets a composition query session.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionSearchSession) - a
                ``CompositionQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_query()`` is ``true``.*

        """
        if not self.supports_composition_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_composition_query_session_for_repository(self, repository_id, proxy):
        """Gets a composition query session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionQuerySession) - a
                ``CompositionQuerySession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_composition_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_query()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_composition_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CompositionQuerySession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_composition_search_session(self, proxy):
        """Gets a composition search session.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionSearchSession) - a
                ``CompositionSearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_search()`` is ``true``.*

        """
        if not self.supports_composition_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionSearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_composition_search_session_for_repository(self, repository_id, proxy):
        """Gets a composition search session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionSearchSession) - a
                ``CompositionSearchSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_composition_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_composition_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CompositionSearchSession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_composition_admin_session(self, proxy):
        """Gets a composition administration session for creating, updating and deleting compositions.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionAdminSession) - a
                ``CompositionAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_admin()`` is ``true``.*

        """
        if not self.supports_composition_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_composition_admin_session_for_repository(self, repository_id, proxy):
        """Gets a composiiton administrative session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionAdminSession) - a
                ``CompositionAdminSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_admin()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_composition_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CompositionAdminSession(repository_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_composition_notification_session(self, composition_receiver, proxy):
        """Gets the notification session for notifications pertaining to composition changes.

        arg:    composition_receiver
                (osid.repository.CompositionReceiver): the notification
                callback
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionNotificationSession) - a
                ``CompositionNotificationSession``
        raise:  NullArgument - ``composition_receiver`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_notification()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_notification()`` is ``true``.*

        """
        if not self.supports_composition_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionNotificationSession(proxy=proxy, runtime=self._runtime, receiver=composition_receiver)

    @utilities.arguments_not_none
    def get_composition_notification_session_for_repository(self, composition_receiver, repository_id, proxy):
        """Gets the composition notification session for the given repository.

        arg:    composition_receiver
                (osid.repository.CompositionReceiver): the notification
                callback
        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionNotificationSession) - a
                ``CompositionNotificationSession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``composition_receiver, repository_id``
                or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_composition_notification()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_notfication()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_composition_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CompositionNotificationSession(catalog_id=repository_id, proxy=proxy, runtime=self._runtime, receiver=composition_receiver)

    @utilities.arguments_not_none
    def get_composition_repository_session(self, proxy):
        """Gets the session for retrieving composition to repository mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionRepositorySession) - a
                ``CompositionRepositorySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_composition_repository()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_repository()`` is ``true``.*

        """
        if not self.supports_composition_repository():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionRepositorySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_composition_repository_assignment_session(self, proxy):
        """Gets the session for assigning composition to repository mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionRepositoryAssignmentSession)
                - a ``CompositionRepositoryAssignmentSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_composition_repository_assignment()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_repository_assignment()`` is ``true``.*

        """
        if not self.supports_composition_repository_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionRepositoryAssignmentSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_composition_smart_repository_session(self, repository_id, proxy):
        """Gets a composition smart repository session for the given repository.

        arg:    repository_id (osid.id.Id): the ``Id`` of the repository
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.CompositionSmartRepositorySession) - a
                ``CompositionSmartRepositorySession``
        raise:  NotFound - ``repository_id`` not found
        raise:  NullArgument - ``repository_id`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented -
                ``supports_composition_smart_repository()``  ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_composition_smart_repository()`` is ``true``.*

        """
        if not self.supports_composition_smart_repository():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CompositionSmartRepositorySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_repository_lookup_session(self, proxy):
        """Gets the repository lookup session.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.RepositoryLookupSession) - a
                ``RepositoryLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_lookup()`` is ``true``.*

        """
        if not self.supports_repository_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_repository_query_session(self, proxy):
        """Gets the repository query session.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.RepositoryQuerySession) - a
                ``RepositoryQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_query()`` is ``true``.*

        """
        if not self.supports_repository_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_repository_search_session(self, proxy):
        """Gets the repository search session.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.RepositorySearchSession) - a
                ``RepositorySearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_search()`` is ``true``.*

        """
        if not self.supports_repository_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositorySearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_repository_admin_session(self, proxy):
        """Gets the repository administrative session for creating, updating and deleteing repositories.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.RepositoryAdminSession) - a
                ``RepositoryAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_admin()`` is ``true``.*

        """
        if not self.supports_repository_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_repository_notification_session(self, repository_receiver, proxy):
        """Gets the notification session for subscribing to changes to a repository.

        arg:    repository_receiver
                (osid.repository.RepositoryReceiver): the notification
                callback
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.RepositoryNotificationSession) - a
                ``RepositoryNotificationSession``
        raise:  NullArgument - ``repository_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_notification()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_notification()`` is ``true``.*

        """
        if not self.supports_repository_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryNotificationSession(proxy=proxy, runtime=self._runtime, receiver=repository_receiver)

    @utilities.arguments_not_none
    def get_repository_hierarchy_session(self, proxy):
        """Gets the repository hierarchy traversal session.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.RepositoryHierarchySession) - ``a
                RepositoryHierarchySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_hierarchy()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_hierarchy()`` is ``true``.*

        """
        if not self.supports_repository_hierarchy():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryHierarchySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_repository_hierarchy_design_session(self, proxy):
        """Gets the repository hierarchy design session.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.repository.RepositoryHierarchyDesignSession) - a
                ``RepostoryHierarchyDesignSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_repository_hierarchy_design()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_hierarchy_design()`` is ``true``.*

        """
        if not self.supports_repository_hierarchy_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RepositoryHierarchyDesignSession(proxy=proxy, runtime=self._runtime)

    def get_repository_batch_proxy_manager(self):
        """Gets a ``RepositoryBatchProxyManager``.

        return: (osid.repository.batch.RepositoryBatchProxyManager) - a
                ``RepostoryBatchProxyManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_batch()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_batch()`` is ``true``.*

        """
        raise errors.Unimplemented()

    repository_batch_proxy_manager = property(fget=get_repository_batch_proxy_manager)

    def get_repository_rules_proxy_manager(self):
        """Gets a ``RepositoryRulesProxyManager``.

        return: (osid.repository.rules.RepositoryRulesProxyManager) - a
                ``RepostoryRulesProxyManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_repository_rules()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_repository_rules()`` is ``true``.*

        """
        raise errors.Unimplemented()

    repository_rules_proxy_manager = property(fget=get_repository_rules_proxy_manager)

    @utilities.arguments_not_none
    def get_asset_composition_session_for_repository(self, repository_id, proxy):
        # This impl is temporary until Tom adds missing methods to RepositoryProxyManager in spec
        if not self.supports_asset_composition():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        return sessions.AssetCompositionSession(repository_id, proxy, runtime=self._runtime) # pylint: disable=no-member

    @utilities.arguments_not_none
    def get_asset_composition_design_session_for_repository(self, repository_id, proxy):
        # This impl is temporary until Tom adds missing methods to RepositoryProxyManager in spec
        if not self.supports_asset_composition():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        return sessions.AssetCompositionDesignSession(repository_id, proxy, runtime=self._runtime) # pylint: disable=no-member



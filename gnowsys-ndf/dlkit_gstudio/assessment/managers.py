"""GStudio implementations of assessment managers."""

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
from dlkit.manager_impls.assessment import managers as assessment_managers




class AssessmentProfile(osid_managers.OsidProfile, assessment_managers.AssessmentProfile):
    """The ``AssessmentProfile`` describes the interoperability among assessment services."""

    def supports_visible_federation(self):
        """Tests if federation is visible.

        return: (boolean) - ``true`` if visible federation is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_my_assessment_taken(self):
        """Tests if a session is available to lookup taken assessments for the authenticated agent.

        return: (boolean) - ``true`` if my assessment taken session is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment(self):
        """Tests for the availability of a assessment service which is the service for taking and examining assessments taken.

        return: (boolean) - ``true`` if assessment is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_results(self):
        """Tests for the availability of an assessment rsults service.

        return: (boolean) - ``true`` if assessment results is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_item_lookup(self):
        """Tests if an item lookup service is supported.

        return: (boolean) - true if item lookup is supported, false
                otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_item_query(self):
        """Tests if an item query service is supported.

        return: (boolean) - ``true`` if item query is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_item_search(self):
        """Tests if an item search service is supported.

        return: (boolean) - ``true`` if item search is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_item_admin(self):
        """Tests if an item administrative service is supported.

        return: (boolean) - ``true`` if item admin is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_item_notification(self):
        """Tests if item notification is supported.

        Messages may be sent when items are created, modified, or
        deleted.

        return: (boolean) - ``true`` if item notification is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_item_bank(self):
        """Tests if an item to bank lookup session is available.

        return: (boolean) - ``true`` if item bank lookup session is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_item_bank_assignment(self):
        """Tests if an item to bank assignment session is available.

        return: (boolean) - ``true`` if item bank assignment is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_item_smart_bank(self):
        """Tests if an item smart bank session is available.

        return: (boolean) - ``true`` if item smart bank session is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_lookup(self):
        """Tests if an assessment lookup service is supported.

        An assessment lookup service defines methods to access
        assessments.

        return: (boolean) - true if assessment lookup is supported,
                false otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_query(self):
        """Tests if an assessment query service is supported.

        return: (boolean) - ``true`` if assessment query is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_search(self):
        """Tests if an assessment search service is supported.

        return: (boolean) - ``true`` if assessment search is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_admin(self):
        """Tests if an assessment administrative service is supported.

        return: (boolean) - ``true`` if assessment admin is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_notification(self):
        """Tests if assessment notification is supported.

        Messages may be sent when assessments are created, modified, or
        deleted.

        return: (boolean) - ``true`` if assessment notification is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_bank(self):
        """Tests if an assessment to bank lookup session is available.

        return: (boolean) - ``true`` if assessment bank lookup session
                is supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_bank_assignment(self):
        """Tests if an assessment to bank assignment session is available.

        return: (boolean) - ``true`` if assessment bank assignment is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_smart_bank(self):
        """Tests if an assessment smart bank session is available.

        return: (boolean) - ``true`` if assessment smart bank session is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_basic_authoring(self):
        """Tests if an assessment basic authoring session is available.

        return: (boolean) - ``true`` if assessment basic authoring is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_offered_lookup(self):
        """Tests if an assessment offered lookup service is supported.

        return: (boolean) - true if assessment offered lookup is
                supported, false otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_offered_query(self):
        """Tests if an assessment offered query service is supported.

        return: (boolean) - ``true`` if assessment offered query is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_offered_search(self):
        """Tests if an assessment offered search service is supported.

        return: (boolean) - ``true`` if assessment offered search is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_offered_admin(self):
        """Tests if an assessment offered administrative service is supported.

        return: (boolean) - ``true`` if assessment offered admin is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_offered_notification(self):
        """Tests if assessment offered notification is supported.

        Messages may be sent when offered assessments are created,
        modified, or deleted.

        return: (boolean) - ``true`` if assessment offered notification
                is supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_offered_bank(self):
        """Tests if an assessment offered to bank lookup session is available.

        return: (boolean) - ``true`` if assessment offered bank lookup
                session is supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_offered_bank_assignment(self):
        """Tests if an assessment offered to bank assignment session is available.

        return: (boolean) - ``true`` if assessment offered bank
                assignment is supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_offered_smart_bank(self):
        """Tests if an assessment offered smart bank session is available.

        return: (boolean) - ``true`` if assessment offered smart bank
                session is supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_taken_lookup(self):
        """Tests if an assessment taken lookup service is supported.

        return: (boolean) - ``true`` if assessment taken lookup is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_taken_query(self):
        """Tests if an assessment taken query service is supported.

        return: (boolean) - ``true`` if assessment taken query is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_taken_search(self):
        """Tests if an assessment taken search service is supported.

        return: (boolean) - ``true`` if assessment taken search is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_taken_admin(self):
        """Tests if an assessment taken administrative service is supported which is used to instantiate an assessment offered.

        return: (boolean) - ``true`` if assessment taken admin is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_taken_notification(self):
        """Tests if assessment taken notification is supported.

        Messages may be sent when items are created, modified, or
        deleted.

        return: (boolean) - ``true`` if assessment taken notification is
                supported ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_taken_bank(self):
        """Tests if an assessment taken to bank lookup session is available.

        return: (boolean) - ``true`` if assessment taken bank lookup
                session is supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_taken_bank_assignment(self):
        """Tests if an assessment taken to bank assignment session is available.

        return: (boolean) - ``true`` if assessment taken bank assignment
                is supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_taken_smart_bank(self):
        """Tests if an assessment taken smart bank session is available.

        return: (boolean) - ``true`` if assessment taken smart bank
                session is supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_bank_lookup(self):
        """Tests if a bank lookup service is supported.

        A bank lookup service defines methods to access assessment
        banks.

        return: (boolean) - ``true`` if bank lookup is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_bank_query(self):
        """Tests if a bank query service is supported.

        return: (boolean) - ``true`` if bank query is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_bank_search(self):
        """Tests if a bank search service is supported.

        return: (boolean) - ``true`` if bank search is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_bank_admin(self):
        """Tests if a banlk administrative service is supported.

        return: (boolean) - ``true`` if bank admin is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_bank_notification(self):
        """Tests if bank notification is supported.

        Messages may be sent when items are created, modified, or
        deleted.

        return: (boolean) - ``true`` if bank notification is supported
                ``,``  ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_bank_hierarchy(self):
        """Tests if a bank hierarchy traversal is supported.

        return: (boolean) - ``true`` if a bank hierarchy traversal is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_bank_hierarchy_design(self):
        """Tests if bank hierarchy design is supported.

        return: (boolean) - ``true`` if a bank hierarchy design is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_authoring(self):
        """Tests if an assessment authoring service is supported.

        return: (boolean) - ``true`` if an assessment authoring is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_assessment_batch(self):
        """Tests if an assessment batch service is supported.

        return: (boolean) - ``true`` if an assessment batch service is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def get_item_record_types(self):
        """Gets the supported ``Item`` record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``Item`` record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ITEM_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    item_record_types = property(fget=get_item_record_types)

    @utilities.arguments_not_none
    def supports_item_record_type(self, item_record_type):
        """Tests if the given ``Item`` record type is supported.

        arg:    item_record_type (osid.type.Type): a ``Type`` indicating
                a ``Item`` record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``item_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ITEM_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (item_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    item_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    item_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_item_search_record_types(self):
        """Gets the supported ``Item`` search record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``Item`` search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ITEM_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    item_search_record_types = property(fget=get_item_search_record_types)

    @utilities.arguments_not_none
    def supports_item_search_record_type(self, item_search_record_type):
        """Tests if the given ``Item`` search record type is supported.

        arg:    item_search_record_type (osid.type.Type): a ``Type``
                indicating an ``Item`` search record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``item_search_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ITEM_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (item_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    item_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    item_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_assessment_record_types(self):
        """Gets the supported ``Assessment`` record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``Assessment`` record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ASSESSMENT_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    assessment_record_types = property(fget=get_assessment_record_types)

    @utilities.arguments_not_none
    def supports_assessment_record_type(self, assessment_record_type):
        """Tests if the given ``Assessment`` record type is supported.

        arg:    assessment_record_type (osid.type.Type): a ``Type``
                indicating an ``Assessment`` record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``assessment_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ASSESSMENT_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (assessment_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    assessment_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    assessment_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_assessment_search_record_types(self):
        """Gets the supported ``Assessment`` search record types.

        return: (osid.type.TypeList) - a list containing the supported
                assessment search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ASSESSMENT_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    assessment_search_record_types = property(fget=get_assessment_search_record_types)

    @utilities.arguments_not_none
    def supports_assessment_search_record_type(self, assessment_search_record_type):
        """Tests if the given assessment search record type is supported.

        arg:    assessment_search_record_type (osid.type.Type): a
                ``Type`` indicating an assessment search record type
        return: (boolean) - ``true`` if the given search record Type is
                supported, ``false`` otherwise
        raise:  NullArgument - ``assessment_search_record_type`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ASSESSMENT_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (assessment_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    assessment_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    assessment_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_assessment_offered_record_types(self):
        """Gets the supported ``AssessmentOffered`` record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``AssessmentOffered`` record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ASSESSMENT_OFFERED_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    assessment_offered_record_types = property(fget=get_assessment_offered_record_types)

    @utilities.arguments_not_none
    def supports_assessment_offered_record_type(self, assessment_offered_record_type):
        """Tests if the given ``AssessmentOffered`` record type is supported.

        arg:    assessment_offered_record_type (osid.type.Type): a
                ``Type`` indicating an ``AssessmentOffered`` record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``assessment_offered_record_type`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ASSESSMENT_OFFERED_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (assessment_offered_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    assessment_offered_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    assessment_offered_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_assessment_offered_search_record_types(self):
        """Gets the supported ``AssessmentOffered`` search record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``AssessmentOffered`` search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ASSESSMENT_OFFERED_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    assessment_offered_search_record_types = property(fget=get_assessment_offered_search_record_types)

    @utilities.arguments_not_none
    def supports_assessment_offered_search_record_type(self, assessment_offered_search_record_type):
        """Tests if the given ``AssessmentOffered`` search record type is supported.

        arg:    assessment_offered_search_record_type (osid.type.Type):
                a ``Type`` indicating an ``AssessmentOffered`` search
                record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``assessment_offered_search_record_type``
                is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ASSESSMENT_OFFERED_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (assessment_offered_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    assessment_offered_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    assessment_offered_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_assessment_taken_record_types(self):
        """Gets the supported ``AssessmentTaken`` record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``AssessmentTaken`` record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ASSESSMENT_TAKEN_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    assessment_taken_record_types = property(fget=get_assessment_taken_record_types)

    @utilities.arguments_not_none
    def supports_assessment_taken_record_type(self, assessment_taken_record_type):
        """Tests if the given ``AssessmentTaken`` record type is supported.

        arg:    assessment_taken_record_type (osid.type.Type): a
                ``Type`` indicating an ``AssessmentTaken`` record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``assessment_taken_record_type`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ASSESSMENT_TAKEN_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (assessment_taken_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    assessment_taken_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    assessment_taken_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_assessment_taken_search_record_types(self):
        """Gets the supported ``AssessmentTaken`` search record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``AssessmentTaken`` search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ASSESSMENT_TAKEN_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    assessment_taken_search_record_types = property(fget=get_assessment_taken_search_record_types)

    @utilities.arguments_not_none
    def supports_assessment_taken_search_record_type(self, assessment_taken_search_record_type):
        """Tests if the given ``AssessmentTaken`` search record type is supported.

        arg:    assessment_taken_search_record_type (osid.type.Type): a
                ``Type`` indicating an ``AssessmentTaken`` search record
                type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``assessment_taken_search_record_type``
                is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ASSESSMENT_TAKEN_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (assessment_taken_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    assessment_taken_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    assessment_taken_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_assessment_section_record_types(self):
        """Gets the supported ``AssessmentSection`` record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``AssessmentSection`` record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('ASSESSMENT_SECTION_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    assessment_section_record_types = property(fget=get_assessment_section_record_types)

    @utilities.arguments_not_none
    def supports_assessment_section_record_type(self, assessment_section_record_type):
        """Tests if the given ``AssessmentSection`` record type is supported.

        arg:    assessment_section_record_type (osid.type.Type): a
                ``Type`` indicating an ``AssessmentSection`` record type
        return: (boolean) - ``true`` if the given Type is supported,
                ``false`` otherwise
        raise:  NullArgument - ``assessment_section_record_type`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('ASSESSMENT_SECTION_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (assessment_section_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    assessment_section_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    assessment_section_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_bank_record_types(self):
        """Gets the supported ``Bank`` record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``Bank`` record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('BANK_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    bank_record_types = property(fget=get_bank_record_types)

    @utilities.arguments_not_none
    def supports_bank_record_type(self, bank_record_type):
        """Tests if the given ``Bank`` record type is supported.

        arg:    bank_record_type (osid.type.Type): a ``Type`` indicating
                a ``Bank`` type
        return: (boolean) - ``true`` if the given key record ``Type`` is
                supported, ``false`` otherwise
        raise:  NullArgument - ``bank_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('BANK_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (bank_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    bank_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    bank_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_bank_search_record_types(self):
        """Gets the supported bank search record types.

        return: (osid.type.TypeList) - a list containing the supported
                ``Bank`` search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('BANK_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    bank_search_record_types = property(fget=get_bank_search_record_types)

    @utilities.arguments_not_none
    def supports_bank_search_record_type(self, bank_search_record_type):
        """Tests if the given bank search record type is supported.

        arg:    bank_search_record_type (osid.type.Type): a ``Type``
                indicating a ``Bank`` search record type
        return: (boolean) - ``true`` if the given search record ``Type``
                is supported, ``false`` otherwise
        raise:  NullArgument - ``bank_search_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('BANK_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (bank_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    bank_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    bank_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports


class AssessmentManager(osid_managers.OsidManager, AssessmentProfile, assessment_managers.AssessmentManager):
    """The assessment manager provides access to assessment sessions and provides interoperability tests for various aspects of this service.

    The sessions included in this manager are:

      * ``MyAssessmentTakenSession:`` a session to get taken or in
        progress assessments for the current agent
      * ``AssessmentSession:`` a session to be assessed and examine
        assessments taken
      * ``AssessmentResultsSession:`` a session to retrieve assessment
        results

      * ``ItemLookupSession:`` a session to look up ``Items``
      * ``ItemQuerySession`` : a session to query ``Items``
      * ``ItemSearchSession:`` a session to search ``Items``
      * ``ItemAdminSession:`` a session to create, modify and delete
        ``Items``
      * ``ItemNotificationSession: a`` session to receive messages
        pertaining to ``Item`` changes
      * ``ItemBankSession:`` a session for looking up item and bank
        mappings
      * ``ItemBankAssignmentSession:`` a session for managing item and
        bank mappings
      * ``ItemSmartBankSession:`` a session for managing dynamic banks

      * ``AssessmentLookupSession:`` a session to look up
        ``Assessments``
      * ``AssessmentQuerySession:`` a session to query ``Assessments``
      * ``AssessmentSearchSession:`` a session to search ``Assessments``
      * ``AssessmentAdminSession:`` a session to create, modify and
        delete ``Assessments``
      * ``AssessmentNotificationSession: a`` session to receive messages
        pertaining to ``Assessment`` changes

      * ``AssessmentBankSession:`` a session for looking up assessment
        and bank mappings
      * ``AssessmentBankAssignmentSession:`` a session for managing
        assessment and bank mappings
      * ``AssessmentSmartBankSession:`` a session for managing dynamic
        banks
      * ``AssessmentBasicAuthoringSession:`` a session for making simple
        mappings of assessment items to assessments

      * ``AssessmentOfferedLookupSession:`` a session to look up
        ``AssessmentsOffered``
      * ``AssessmentOfferedQuerySession:`` a session to query
        ``AssessmentsOffered``
      * ``AssessmentOfferedSearchSession`` : a session to search
        ``AssessmentsOffered``
      * ``AssessmentOfferedAdminSession:`` a session to create, modify
        and delete ``AssessmentsOffered``
      * ``AssessmentOfferedNotificationSession: a`` session to receive
        messages pertaining to ``AssessmentOffered`` changes
      * ``AssessmentOfferedBankSession:`` a session for looking up
        assessments offered and bank mappings
      * ``AssessmentOfferedBankAssignmentSession:`` a session for
        managing assessments offered and bank mappings
      * ``AssessmentOfferedSmartBankSession`` : a session to manage
        dynamic banks of assessments offered

      * ``AssessmentTakenLookupSession:`` a session to look up
        ``Assessments``
      * ``AssessmentTakenQuerySession:`` a session to query
        ``Assessments``
      * ``AssessmentTakenSearchSession:`` a session to search
        Assessments
      * ``AssessmentTakenAdminSession:`` a session to create, modify and
        delete ``AssessmentsTaken``
      * ``AssessmentTakenNotificationSession: a`` session to receive
        messages pertaining to ``AssessmentTaken`` changes
      * ``AssessmentTakenBankSession:`` a session for looking up
        assessments taken and bank mappings
      * ``AssessmenttTakenBankAssignmentSession:`` a session for
        managing assessments taken and bank mappings
      * ``AssessmentTakenSmartBankSession:`` a session to manage dynamic
        banks of assessments taken

      * ``BankLookupSession:`` a session to lookup banks
      * ``BankQuerySession`` : a session to query banks
      * ``BankSearchSession:`` a session to search banks
      * ``BankAdminSession`` : a session to create, modify and delete
        banks
      * ``BankNotificationSession`` : a session to receive messages
        pertaining to ``Bank`` changes
      * ``BankHierarchySession`` : a session to traverse the ``Bank``
        hierarchy
      * ``BankHierarchyDesignSession`` : a session to manage the
        ``Bank`` hierarchy


    """

    def __init__(self):
        osid_managers.OsidManager.__init__(self)

    def get_my_assessment_taken_session(self):
        """Gets a ``MyAssessmentTakenSession`` to retrieve assessments taken for the current agent.

        return: (osid.assessment.MyAssessmentTakenSession) - a
                ``MyAssessmentTakenSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_my_assessment_taken()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_my_assessment_taken()`` is ``true``.*

        """
        if not self.supports_my_assessment_taken():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.MyAssessmentTakenSession(runtime=self._runtime)

    my_assessment_taken_session = property(fget=get_my_assessment_taken_session)

    @utilities.arguments_not_none
    def get_my_assessment_taken_session_for_bank(self, bank_id):
        """Gets a ``MyAssessmentTakenSession`` to retrieve assessments taken for the current agent for the given bank ``Id``.

        arg:    bank_id (osid.id.Id): the ``Id`` of a bank
        return: (osid.assessment.MyAssessmentTakenSession) - a
                ``MyAssessmentTakenSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_my_assessment_taken()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_my_assessment_taken()`` is ``true``.*

        """
        if not self.supports_my_assessment_taken():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.MyAssessmentTakenSession(bank_id, self._runtime)

    def get_assessment_session(self):
        """Gets an ``AssessmentSession`` which is responsible for taking assessments and examining responses from assessments taken.

        return: (osid.assessment.AssessmentSession) - an assessment
                session for this service
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment()`` is ``true``.*

        """
        if not self.supports_assessment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentSession(runtime=self._runtime)

    assessment_session = property(fget=get_assessment_session)

    @utilities.arguments_not_none
    def get_assessment_session_for_bank(self, bank_id):
        """Gets an ``AssessmentSession`` which is responsible for performing assessments for the given bank ``Id``.

        arg:    bank_id (osid.id.Id): the ``Id`` of a bank
        return: (osid.assessment.AssessmentSession) - an assessment
                session for this service
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment()`` is ``true``.*

        """
        if not self.supports_assessment():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentSession(bank_id, self._runtime)

    def get_assessment_results_session(self):
        """Gets an ``AssessmentResultsSession`` to retrieve assessment results.

        return: (osid.assessment.AssessmentResultsSession) - an
                assessment results session for this service
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_results()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_results()`` is ``true``.*

        """
        if not self.supports_assessment_results():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentResultsSession(runtime=self._runtime)

    assessment_results_session = property(fget=get_assessment_results_session)

    @utilities.arguments_not_none
    def get_assessment_results_session_for_bank(self, bank_id):
        """Gets an ``AssessmentResultsSession`` to retrieve assessment results for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the assessment taken
        return: (osid.assessment.AssessmentResultsSession) - an
                assessment results session for this service
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_results()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_results()`` is ``true``.*

        """
        if not self.supports_assessment_results():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentResultsSession(bank_id, self._runtime)

    def get_item_lookup_session(self):
        """Gets the ``OsidSession`` associated with the item lookup service.

        return: (osid.assessment.ItemLookupSession) - an
                ``ItemLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_lookup()`` is ``true``.*

        """
        if not self.supports_item_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemLookupSession(runtime=self._runtime)

    item_lookup_session = property(fget=get_item_lookup_session)

    @utilities.arguments_not_none
    def get_item_lookup_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the item lookup service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.ItemLookupSession) - ``an
                _item_lookup_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_item_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_lookup()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_item_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.ItemLookupSession(bank_id, self._runtime)

    def get_item_query_session(self):
        """Gets the ``OsidSession`` associated with the item query service.

        return: (osid.assessment.ItemQuerySession) - an
                ``ItemQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_query()`` is ``true``.*

        """
        if not self.supports_item_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemQuerySession(runtime=self._runtime)

    item_query_session = property(fget=get_item_query_session)

    @utilities.arguments_not_none
    def get_item_query_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the item query service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.ItemQuerySession) - ``an
                _item_query_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_item_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_query()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_item_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.ItemQuerySession(bank_id, self._runtime)

    def get_item_search_session(self):
        """Gets the ``OsidSession`` associated with the item search service.

        return: (osid.assessment.ItemSearchSession) - an
                ``ItemSearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_search()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_search()`` is ``true``.*

        """
        if not self.supports_item_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemSearchSession(runtime=self._runtime)

    item_search_session = property(fget=get_item_search_session)

    @utilities.arguments_not_none
    def get_item_search_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the item search service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.ItemSearchSession) - ``an
                _item_search_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_item_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_search()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_item_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.ItemSearchSession(bank_id, self._runtime)

    def get_item_admin_session(self):
        """Gets the ``OsidSession`` associated with the item administration service.

        return: (osid.assessment.ItemAdminSession) - an
                ``ItemAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_admin()`` is ``true``.*

        """
        if not self.supports_item_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemAdminSession(runtime=self._runtime)

    item_admin_session = property(fget=get_item_admin_session)

    @utilities.arguments_not_none
    def get_item_admin_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the item admin service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.ItemAdminSession) - ``an
                _item_admin_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_item_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_admin()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_item_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.ItemAdminSession(bank_id, self._runtime)

    @utilities.arguments_not_none
    def get_item_notification_session(self, item_receiver):
        """Gets the notification session for notifications pertaining to item changes.

        arg:    item_receiver (osid.assessment.ItemReceiver): the item
                receiver interface
        return: (osid.assessment.ItemNotificationSession) - an
                ``ItemNotificationSession``
        raise:  NullArgument - ``item_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_notification()`` is ``true``.*

        """
        if not self.supports_item_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemNotificationSession(runtime=self._runtime, receiver=item_receiver)

    @utilities.arguments_not_none
    def get_item_notification_session_for_bank(self, item_receiver, bank_id):
        """Gets the ``OsidSession`` associated with the item notification service for the given bank.

        arg:    item_receiver (osid.assessment.ItemReceiver): the item
                receiver interface
        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentNotificationSession) - ``an
                _item_notification_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``item_receiver`` or ``bank_id`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_item_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_item_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentNotificationSession(bank_id, runtime=self._runtime, receiver=item_receiver)

    def get_item_bank_session(self):
        """Gets the ``OsidSession`` associated with the item banking service.

        return: (osid.assessment.ItemBankSession) - an
                ``ItemBankSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_bank()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_bank()`` is ``true``.*

        """
        if not self.supports_item_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemBankSession(runtime=self._runtime)

    item_bank_session = property(fget=get_item_bank_session)

    def get_item_bank_assignment_session(self):
        """Gets the ``OsidSession`` associated with the item bank assignment service.

        return: (osid.assessment.ItemBankAssignmentSession) - an
                ``ItemBankAssignmentSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_bank_assignment()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_bank_assignment()`` is ``true``.*

        """
        if not self.supports_item_bank_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemBankAssignmentSession(runtime=self._runtime)

    item_bank_assignment_session = property(fget=get_item_bank_assignment_session)

    @utilities.arguments_not_none
    def get_item_smart_bank_session(self, bank_id):
        """Gets the ``OsidSession`` associated with the item smart banking service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.ItemSmartBankSession) - an
                ``ItemSmartBankSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_smart_bank()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_smart_bank()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def get_assessment_lookup_session(self):
        """Gets the ``OsidSession`` associated with the assessment lookup service.

        return: (osid.assessment.AssessmentLookupSession) - an
                ``AssessmentLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_lookup()`` is ``true``.*

        """
        if not self.supports_assessment_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentLookupSession(runtime=self._runtime)

    assessment_lookup_session = property(fget=get_assessment_lookup_session)

    @utilities.arguments_not_none
    def get_assessment_lookup_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment lookup service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentLookupSession) - ``an
                _assessment_lookup_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentLookupSession(bank_id, self._runtime)

    def get_assessment_query_session(self):
        """Gets the ``OsidSession`` associated with the assessment query service.

        return: (osid.assessment.AssessmentQuerySession) - an
                ``AssessmentQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_query()`` is ``true``.*

        """
        if not self.supports_assessment_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentQuerySession(runtime=self._runtime)

    assessment_query_session = property(fget=get_assessment_query_session)

    @utilities.arguments_not_none
    def get_assessment_query_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment query service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentQuerySession) - ``an
                _assessment_query_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_query()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentQuerySession(bank_id, self._runtime)

    def get_assessment_search_session(self):
        """Gets the ``OsidSession`` associated with the assessment search service.

        return: (osid.assessment.AssessmentSearchSession) - an
                ``AssessmentSearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_search()`` is ``true``.*

        """
        if not self.supports_assessment_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentSearchSession(runtime=self._runtime)

    assessment_search_session = property(fget=get_assessment_search_session)

    @utilities.arguments_not_none
    def get_assessment_search_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment search service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentSearchSession) - ``an
                _assessment_search_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentSearchSession(bank_id, self._runtime)

    def get_assessment_admin_session(self):
        """Gets the ``OsidSession`` associated with the assessment administration service.

        return: (osid.assessment.AssessmentAdminSession) - an
                ``AssessmentAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_admin()`` is ``true``.*

        """
        if not self.supports_assessment_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentAdminSession(runtime=self._runtime)

    assessment_admin_session = property(fget=get_assessment_admin_session)

    @utilities.arguments_not_none
    def get_assessment_admin_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment admin service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentAdminSession) - ``an
                _assessment_admin_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_admin()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentAdminSession(bank_id, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_notification_session(self, assessment_receiver):
        """Gets the notification session for notifications pertaining to assessment changes.

        arg:    assessment_receiver
                (osid.assessment.AssessmentReceiver): the assessment
                receiver interface
        return: (osid.assessment.AssessmentNotificationSession) - an
                ``AssessmentNotificationSession``
        raise:  NullArgument - ``assessment_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_notification()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_notification()`` is ``true``.*

        """
        if not self.supports_assessment_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentNotificationSession(runtime=self._runtime, receiver=assessment_receiver)

    @utilities.arguments_not_none
    def get_assessment_notification_session_for_bank(self, assessment_receiver, bank_id):
        """Gets the ``OsidSession`` associated with the assessment notification service for the given bank.

        arg:    assessment_receiver
                (osid.assessment.AssessmentReceiver): the assessment
                receiver interface
        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentNotificationSession) - ``an
                _assessment_notification_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``assessment_receiver`` or ``bank_id`` is
                ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_notification()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentNotificationSession(bank_id, runtime=self._runtime, receiver=assessment_receiver)

    def get_assessment_bank_session(self):
        """Gets the ``OsidSession`` associated with the assessment banking service.

        return: (osid.assessment.AssessmentBankSession) - an
                ``AssessmentBankSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_bank()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_bank()`` is ``true``.*

        """
        if not self.supports_assessment_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentBankSession(runtime=self._runtime)

    assessment_bank_session = property(fget=get_assessment_bank_session)

    def get_assessment_bank_assignment_session(self):
        """Gets the ``OsidSession`` associated with the assessment bank assignment service.

        return: (osid.assessment.AssessmentBankAssignmentSession) - an
                ``AssessmentBankAssignmentSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_bank_assignment()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_bank_assignment()`` is ``true``.*

        """
        if not self.supports_assessment_bank_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentBankAssignmentSession(runtime=self._runtime)

    assessment_bank_assignment_session = property(fget=get_assessment_bank_assignment_session)

    @utilities.arguments_not_none
    def get_assessment_smart_bank_session(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment smart banking service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentSmartBankSession) - an
                ``AssessmentSmartBankSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_smart_bank()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_smart_bank()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def get_assessment_basic_authoring_session(self):
        """Gets the ``OsidSession`` associated with the assessment authoring service.

        return: (osid.assessment.AssessmentBasicAuthoringSession) - an
                ``AssessmentBasicAuthoringSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_basic_authoring()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_basic_authoring()`` is ``true``.*

        """
        if not self.supports_assessment_basic_authoring():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentBasicAuthoringSession(runtime=self._runtime)

    assessment_basic_authoring_session = property(fget=get_assessment_basic_authoring_session)

    @utilities.arguments_not_none
    def get_assessment_basic_authoring_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment authoring service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of a bank
        return: (osid.assessment.AssessmentBasicAuthoringSession) - an
                ``AssessmentBasicAuthoringSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_basic_authoring()`` or
                ``supports_visibe_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_basic_authoring()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        if not self.supports_assessment_basic_authoring():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentBasicAuthoringSession(bank_id, self._runtime)

    def get_assessment_offered_lookup_session(self):
        """Gets the ``OsidSession`` associated with the assessment offered lookup service.

        return: (osid.assessment.AssessmentOfferedLookupSession) - an
                ``AssessmentOfferedLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_offered_lookup()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_lookup()`` is ``true``.*

        """
        if not self.supports_assessment_offered_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedLookupSession(runtime=self._runtime)

    assessment_offered_lookup_session = property(fget=get_assessment_offered_lookup_session)

    @utilities.arguments_not_none
    def get_assessment_offered_lookup_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment offered lookup service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentOfferedLookupSession) - an
                ``AssessmentOfferedLookupSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_offered_lookup()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_offered_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentOfferedLookupSession(bank_id, self._runtime)

    def get_assessment_offered_query_session(self):
        """Gets the ``OsidSession`` associated with the assessment offered query service.

        return: (osid.assessment.AssessmentOfferedQuerySession) - an
                ``AssessmentOfferedQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_offered_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_query()`` is ``true``.*

        """
        if not self.supports_assessment_offered_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedQuerySession(runtime=self._runtime)

    assessment_offered_query_session = property(fget=get_assessment_offered_query_session)

    @utilities.arguments_not_none
    def get_assessment_offered_query_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment offered query service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentOfferedQuerySession) - an
                ``AssessmentOfferedQuerySession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_offered_query()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_query()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_offered_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentOfferedQuerySession(bank_id, self._runtime)

    def get_assessment_offered_search_session(self):
        """Gets the ``OsidSession`` associated with the assessment offered search service.

        return: (osid.assessment.AssessmentOfferedSearchSession) - an
                ``AssessmentOfferedSearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_offered_search()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_search()`` is ``true``.*

        """
        if not self.supports_assessment_offered_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedSearchSession(runtime=self._runtime)

    assessment_offered_search_session = property(fget=get_assessment_offered_search_session)

    @utilities.arguments_not_none
    def get_assessment_offered_search_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment offered search service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentOfferedSearchSession) - an
                ``AssessmentOfferedSearchSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_offered_search()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_offered_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentOfferedSearchSession(bank_id, self._runtime)

    def get_assessment_offered_admin_session(self):
        """Gets the ``OsidSession`` associated with the assessment offered administration service.

        return: (osid.assessment.AssessmentOfferedAdminSession) - an
                ``AssessmentOfferedAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_offered_admin()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_admin()`` is ``true``.*

        """
        if not self.supports_assessment_offered_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedAdminSession(runtime=self._runtime)

    assessment_offered_admin_session = property(fget=get_assessment_offered_admin_session)

    @utilities.arguments_not_none
    def get_assessment_offered_admin_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment offered admin service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentOfferedAdminSession) - an
                ``AssessmentOfferedAdminSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_offered_admin()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_admin()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_offered_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentOfferedAdminSession(bank_id, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_notification_session(self, assessment_offered_receiver):
        """Gets the notification session for notifications pertaining to offered assessment changes.

        arg:    assessment_offered_receiver
                (osid.assessment.AssessmentOfferedReceiver): the
                assessment offered receiver interface
        return: (osid.assessment.AssessmentOfferedNotificationSession) -
                an ``AssessmentOfferedNotificationSession``
        raise:  NullArgument - ``assessment_offered_receiver`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_offered_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_notification()`` is ``true``.*

        """
        if not self.supports_assessment_offered_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedNotificationSession(runtime=self._runtime, receiver=assessment_offered_receiver)

    @utilities.arguments_not_none
    def get_assessment_offered_notification_session_for_bank(self, assessment_offered_receiver, bank_id):
        """Gets the ``OsidSession`` associated with the offered assessment notification service for the given bank.

        arg:    assessment_offered_receiver
                (osid.assessment.AssessmentOfferedReceiver): the
                assessment offered receiver interface
        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentOfferedNotificationSession) -
                a ``AssessmentOfferedNotificationSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``assessment_offered_receiver`` or
                ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented -
                ``supports_assessment_offered_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_offered_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentOfferedNotificationSession(bank_id, runtime=self._runtime, receiver=assessment_offered_receiver)

    def get_assessment_offered_bank_session(self):
        """Gets the session for retrieving offered assessments to bank mappings.

        return: (osid.assessment.AssessmentOfferedBankSession) - an
                ``AssessmentOfferedBankSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_offered_bank()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_bank()`` is ``true``.*

        """
        if not self.supports_assessment_offered_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedBankSession(runtime=self._runtime)

    assessment_offered_bank_session = property(fget=get_assessment_offered_bank_session)

    def get_assessment_offered_bank_assignment_session(self):
        """Gets the session for assigning offered assessments to bank mappings.

        return: (osid.assessment.AssessmentOfferedBankAssignmentSession)
                - an ``AssessmentOfferedBankAssignmentSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_offered_bank_assignment()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_bank_assignment()`` is ``true``.*

        """
        if not self.supports_assessment_offered_bank_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedBankAssignmentSession(runtime=self._runtime)

    assessment_offered_bank_assignment_session = property(fget=get_assessment_offered_bank_assignment_session)

    @utilities.arguments_not_none
    def get_assessment_offered_smart_bank_session(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment offered smart banking service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentOfferedSmartBankSession) - an
                ``AssessmentOfferedSmartBankSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_offered_smart_bank()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_smart_bank()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def get_assessment_taken_lookup_session(self):
        """Gets the ``OsidSession`` associated with the assessment taken lookup service.

        return: (osid.assessment.AssessmentTakenLookupSession) - an
                ``AssessmentTakenLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_taken_lookup()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_lookup()`` is ``true``.*

        """
        if not self.supports_assessment_taken_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenLookupSession(runtime=self._runtime)

    assessment_taken_lookup_session = property(fget=get_assessment_taken_lookup_session)

    @utilities.arguments_not_none
    def get_assessment_taken_lookup_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment taken lookup service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentTakenLookupSession) - an
                ``AssessmentTakenLookupSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_taken_lookup()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_taken_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentTakenLookupSession(bank_id, self._runtime)

    def get_assessment_taken_query_session(self):
        """Gets the ``OsidSession`` associated with the assessment taken query service.

        return: (osid.assessment.AssessmentTakenQuerySession) - an
                ``AssessmentTakenQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_taken_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_query()`` is ``true``.*

        """
        if not self.supports_assessment_taken_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenQuerySession(runtime=self._runtime)

    assessment_taken_query_session = property(fget=get_assessment_taken_query_session)

    @utilities.arguments_not_none
    def get_assessment_taken_query_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment taken query service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentTakenQuerySession) - an
                ``AssessmentTakenQuerySession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_taken_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_query()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_taken_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentTakenQuerySession(bank_id, self._runtime)

    def get_assessment_taken_search_session(self):
        """Gets the ``OsidSession`` associated with the assessment taken search service.

        return: (osid.assessment.AssessmentTakenSearchSession) - an
                ``AssessmentTakenSearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_taken_search()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_search()`` is ``true``.*

        """
        if not self.supports_assessment_taken_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenSearchSession(runtime=self._runtime)

    assessment_taken_search_session = property(fget=get_assessment_taken_search_session)

    @utilities.arguments_not_none
    def get_assessment_taken_search_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment taken search service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentTakenSearchSession) - an
                ``AssessmentTakenSearchSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_taken_search()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_taken_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentTakenSearchSession(bank_id, self._runtime)

    def get_assessment_taken_admin_session(self):
        """Gets the ``OsidSession`` associated with the assessment taken administration service.

        return: (osid.assessment.AssessmentTakenAdminSession) - an
                ``AssessmentTakenAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_taken_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_admin()`` is ``true``.*

        """
        if not self.supports_assessment_taken_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenAdminSession(runtime=self._runtime)

    assessment_taken_admin_session = property(fget=get_assessment_taken_admin_session)

    @utilities.arguments_not_none
    def get_assessment_taken_admin_session_for_bank(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment taken admin service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentTakenAdminSession) - an
                ``AssessmentTakenSearchSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_taken_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_admin()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_taken_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentTakenAdminSession(bank_id, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_notification_session(self, assessment_taken_receiver):
        """Gets the notification session for notifications pertaining to taken assessment changes.

        arg:    assessment_taken_receiver
                (osid.assessment.AssessmentTakenReceiver): the
                assessment taken receiver interface
        return: (osid.assessment.AssessmentTakenNotificationSession) -
                an ``AssessmentTakenNotificationSession``
        raise:  NullArgument - ``assessment_taken_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_taken_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_notification()`` is ``true``.*

        """
        if not self.supports_assessment_taken_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenNotificationSession(runtime=self._runtime, receiver=assessment_taken_receiver)

    @utilities.arguments_not_none
    def get_assessment_taken_notification_session_for_bank(self, assessment_taken_receiver, bank_id):
        """Gets the ``OsidSession`` associated with the taken assessment notification service for the given bank.

        arg:    assessment_taken_receiver
                (osid.assessment.AssessmentTakenReceiver): the
                assessment taken receiver interface
        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentTakenNotificationSession) -
                an ``AssessmentTakenNotificationSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``assessment_taken_receiver`` or
                ``bank_id`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented -
                ``supports_assessment_taken_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_taken_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentTakenNotificationSession(bank_id, runtime=self._runtime, receiver=assessment_taken_receiver)

    def get_assessment_taken_bank_session(self):
        """Gets the session for retrieving taken assessments to bank mappings.

        return: (osid.assessment.AssessmentTakenBankSession) - an
                ``AssessmentTakenBankSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_taken_bank()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_bank()`` is ``true``.*

        """
        if not self.supports_assessment_taken_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenBankSession(runtime=self._runtime)

    assessment_taken_bank_session = property(fget=get_assessment_taken_bank_session)

    def get_assessment_taken_bank_assignment_session(self):
        """Gets the session for assigning taken assessments to bank mappings.

        return: (osid.assessment.AssessmentTakenBankAssignmentSession) -
                an ``AssessmentTakenBankAssignmentSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_taken_bank_assignment()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_bank_assignment()`` is ``true``.*

        """
        if not self.supports_assessment_taken_bank_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenBankAssignmentSession(runtime=self._runtime)

    assessment_taken_bank_assignment_session = property(fget=get_assessment_taken_bank_assignment_session)

    @utilities.arguments_not_none
    def get_assessment_taken_smart_bank_session(self, bank_id):
        """Gets the ``OsidSession`` associated with the assessment taken smart banking service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        return: (osid.assessment.AssessmentTakenSmartBankSession) - an
                ``AssessmentTakenSmartBankSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_taken_smart_bank()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_smart_bank()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def get_bank_lookup_session(self):
        """Gets the OsidSession associated with the bank lookup service.

        return: (osid.assessment.BankLookupSession) - a
                ``BankLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_lookup() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_lookup()`` is true.*

        """
        if not self.supports_bank_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankLookupSession(runtime=self._runtime)

    bank_lookup_session = property(fget=get_bank_lookup_session)

    def get_bank_query_session(self):
        """Gets the OsidSession associated with the bank query service.

        return: (osid.assessment.BankQuerySession) - a
                ``BankQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_query() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_query()`` is true.*

        """
        if not self.supports_bank_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankQuerySession(runtime=self._runtime)

    bank_query_session = property(fget=get_bank_query_session)

    def get_bank_search_session(self):
        """Gets the OsidSession associated with the bank search service.

        return: (osid.assessment.BankSearchSession) - a
                ``BankSearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_search() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_search()`` is true.*

        """
        if not self.supports_bank_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankSearchSession(runtime=self._runtime)

    bank_search_session = property(fget=get_bank_search_session)

    def get_bank_admin_session(self):
        """Gets the OsidSession associated with the bank administration service.

        return: (osid.assessment.BankAdminSession) - a
                ``BankAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_admin() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_admin()`` is true.*

        """
        if not self.supports_bank_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankAdminSession(runtime=self._runtime)

    bank_admin_session = property(fget=get_bank_admin_session)

    @utilities.arguments_not_none
    def get_bank_notification_session(self, bankreceiver):
        """Gets the notification session for notifications pertaining to bank service changes.

        arg:    bankreceiver (osid.assessment.BankReceiver): the bank
                receiver interface
        return: (osid.assessment.BankNotificationSession) - a
                ``BankNotificationSession``
        raise:  NullArgument - ``bank_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_notification() is
                false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_notification()`` is true.*

        """
        if not self.supports_bank_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankNotificationSession(runtime=self._runtime, receiver=bankreceiver)

    def get_bank_hierarchy_session(self):
        """Gets the session traversing bank hierarchies.

        return: (osid.assessment.BankHierarchySession) - a
                ``BankHierarchySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_hierarchy() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_hierarchy()`` is true.*

        """
        if not self.supports_bank_hierarchy():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankHierarchySession(runtime=self._runtime)

    bank_hierarchy_session = property(fget=get_bank_hierarchy_session)

    def get_bank_hierarchy_design_session(self):
        """Gets the session designing bank hierarchies.

        return: (osid.assessment.BankHierarchyDesignSession) - a
                ``BankHierarchySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_hierarchy_design() is
                false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_hierarchy_design()`` is true.*

        """
        if not self.supports_bank_hierarchy_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankHierarchyDesignSession(runtime=self._runtime)

    bank_hierarchy_design_session = property(fget=get_bank_hierarchy_design_session)

    def get_assessment_authoring_manager(self):
        """Gets an ``AssessmentAuthoringManager``.

        return: (osid.assessment.authoring.AssessmentAuthoringManager) -
                an ``AssessmentAuthoringManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_authoring() is
                false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_authoring()`` is true.*

        """
        raise errors.Unimplemented()

    assessment_authoring_manager = property(fget=get_assessment_authoring_manager)

    def get_assessment_batch_manager(self):
        """Gets an ``AssessmentBatchManager``.

        return: (osid.assessment.batch.AssessmentBatchManager) - an
                ``AssessmentBatchManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_batch() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_batch()`` is true.*

        """
        raise errors.Unimplemented()

    assessment_batch_manager = property(fget=get_assessment_batch_manager)


class AssessmentProxyManager(osid_managers.OsidProxyManager, AssessmentProfile, assessment_managers.AssessmentProxyManager):
    """The assessment manager provides access to assessment sessions and provides interoperability tests for various aspects of this service.

    Methods in this manager support the passing of a ``Proxy`` object.
    The sessions included in this manager are:

      * ``MyAssessmentTakenSession:`` a session to get taken or in
        progress assessments for the current agent
      * ``AssessmentSession:`` a session to be assessed and examine
        assessments taken
      * ``AssessmentResultsSession:`` a session to retrieve assessment
        results

      * ``ItemLookupSession:`` a session to look up ``Items``
      * ``ItemQuerySession`` : a session to query ``Items``
      * ``ItemSearchSession:`` a session to search ``Items``
      * ``ItemAdminSession:`` a session to create, modify and delete
        ``Items``
      * ``ItemNotificationSession: a`` session to receive messages
        pertaining to ``Item`` changes
      * ``ItemBankSession:`` a session for looking up item and bank
        mappings
      * ``ItemBankAssignmentSession:`` a session for managing item and
        bank mappings
      * ``ItemSmartBankSession:`` a session for managing dynamic banks

      * ``AssessmentLookupSession:`` a session to look up
        ``Assessments``
      * ``AssessmentQuerySession:`` a session to query ``Assessments``
      * ``AssessmentSearchSession:`` a session to search ``Assessments``
      * ``AssessmentAdminSession:`` a session to create, modify and
        delete ``Assessments``
      * ``AssessmentNotificationSession: a`` session to receive messages
        pertaining to ``Assessment`` changes

      * ``AssessmentBankSession:`` a session for looking up assessment
        and bank mappings
      * ``AssessmentBankAssignmentSession:`` a session for managing
        assessment and bank mappings
      * ``AssessmentSmartBankSession:`` a session for managing dynamic
        banks
      * ``AssessmentBasicAuthoringSession:`` a session for making simple
        mappings of assessment items to assessments

      * ``AssessmentOfferedLookupSession:`` a session to look up
        ``Assessments``
      * ``AssessmentOfferedQuerySession:`` a session to query
        ``Assessments``
      * ``AssessmentOfferedSearchSession`` : a session to search
        ``Assessments``
      * ``AssessmentOfferedAdminSession:`` a session to create, modify
        and delete ``Assessments``
      * ``AssessmentOfferedNotificationSession: a`` session to receive
        messages pertaining to ``Assessment`` changes
      * ``AssessmentOfferedBankSession:`` a session for looking up
        assessment and bank mappings
      * ``AssessmentOfferedBankAssignmentSession:`` a session for
        managing assessment and bank mappings
      * ``AssessmentOfferedSmartBankSession`` : a session to manage
        dynamic banks

      * ``AssessmentTakenLookupSession:`` a session to look up
        ``Assessments``
      * ``AssessmentTakenQuerySession:`` a session to query
        ``Assessments``
      * ``AssessmentTakenSearchSession:`` a session to search
        Assessments
      * ``AssessmentTakenAdminSession:`` a session to create, modify and
        delete ``AssessmentsTaken``
      * ``AssessmentTakenNotificationSession: a`` session to receive
        messages pertaining to ``AssessmentTaken`` changes
      * ``AssessmentTakenBankSession:`` a session for looking up
        assessments taken and bank mappings
      * ``AssessmenttTakenBankAssignmentSession:`` a session for
        managing assessments taken and bank mappings
      * ``AssessmentTakenSmartBankSession:`` a session to manage dynamic
        banks of assessments taken

      * ``BankLookupSession:`` a session to lookup banks
      * ``BankQuerySession`` : a session to query banks
      * ``BankSearchSession:`` a session to search banks
      * ``BankAdminSession`` : a session to create, modify and delete
        banks
      * ``BankNotificationSession`` : a session to receive messages
        pertaining to ``Bank`` changes
      * ``BankHierarchySession`` : a session to traverse the ``Bank``
        hierarchy
      * ``BankHierarchyDesignSession`` : a session to manage the
        ``Bank`` hierarchy


    """

    def __init__(self):
        osid_managers.OsidProxyManager.__init__(self)

    @utilities.arguments_not_none
    def get_my_assessment_taken_session(self, proxy):
        """Gets a ``MyAssessmentTakenSession`` to retrieve assessments taken for the current agent.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.MyAssessmentTakenSession) - a
                ``MyAssessmentTakenSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_my_assessment_taken()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_my_assessment_taken()`` is ``true``.*

        """
        if not self.supports_my_assessment_taken():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.MyAssessmentTakenSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_my_assessment_taken_session_for_bank(self, bank_id, proxy):
        """Gets a ``MyAssessmentTakenSession`` to retrieve assessments taken for the current agent for the given bank ``Id``.

        arg:    bank_id (osid.id.Id): the ``Id`` of a bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.MyAssessmentTakenSession) - a
                ``MyAssessmentTakenSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_my_assessment_taken()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_my_assessment_taken()`` is ``true``.*

        """
        if not self.supports_my_assessment_taken():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.MyAssessmentTakenSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_session(self, proxy):
        """Gets an ``AssessmentSession`` which is responsible for taking assessments and examining responses from assessments taken.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentSession) - an assessment
                session for this service
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment()`` is ``true``.*

        """
        if not self.supports_assessment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_session_for_bank(self, bank_id, proxy):
        """Gets an ``AssessmentSession`` which is responsible for performing assessments for the given bank ``Id``.

        arg:    bank_id (osid.id.Id): the ``Id`` of a bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentSession) - an assessment
                session for this service
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment()`` is ``true``.*

        """
        if not self.supports_assessment():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_results_session(self, proxy):
        """Gets an ``AssessmentResultsSession`` to retrieve assessment results.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentResultsSession) - an
                assessment results session for this service
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_results()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_results()`` is ``true``.*

        """
        if not self.supports_assessment_results():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentResultsSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_results_session_for_bank(self, bank_id, proxy):
        """Gets an ``AssessmentResultsSession`` to retrieve assessment results for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the assessment taken
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentResultsSession) - an
                assessment results session for this service
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_results()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_results()`` is ``true``.*

        """
        if not self.supports_assessment_results():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentResultsSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_item_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the item lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemLookupSession) - an
                ``ItemLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_lookup()`` is ``true``.*

        """
        if not self.supports_item_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_item_lookup_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the item lookup service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemLookupSession) - ``an
                _item_lookup_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_item_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_lookup()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_item_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.ItemLookupSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_item_query_session(self, proxy):
        """Gets the ``OsidSession`` associated with the item query service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemQuerySession) - an
                ``ItemQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_query()`` is ``true``.*

        """
        if not self.supports_item_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_item_query_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the item query service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemQuerySession) - ``an
                _item_query_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_item_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_query()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_item_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.ItemQuerySession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_item_search_session(self, proxy):
        """Gets the ``OsidSession`` associated with the item search service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemSearchSession) - an
                ``ItemSearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_search()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_search()`` is ``true``.*

        """
        if not self.supports_item_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemSearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_item_search_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the item search service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemSearchSession) - ``an
                _item_search_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``porxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_item_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_search()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_item_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.ItemSearchSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_item_admin_session(self, proxy):
        """Gets the ``OsidSession`` associated with the item administration service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemAdminSession) - an
                ``ItemAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_admin()`` is ``true``.*

        """
        if not self.supports_item_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_item_admin_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the item admin service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemAdminSession) - ``an
                _item_admin_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_item_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_admin()`` and ``supports_visible_federation()``
        are ``true``.*

        """
        if not self.supports_item_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.ItemAdminSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_item_notification_session(self, item_receiver, proxy):
        """Gets the notification session for notifications pertaining to item changes.

        arg:    item_receiver (osid.assessment.ItemReceiver): the item
                receiver interface
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemNotificationSession) - an
                ``ItemNotificationSession``
        raise:  NullArgument - ``item_receiver`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_notification()`` is ``true``.*

        """
        if not self.supports_item_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemNotificationSession(proxy=proxy, runtime=self._runtime, receiver=item_receiver)

    @utilities.arguments_not_none
    def get_item_notification_session_for_bank(self, item_receiver, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the item notification service for the given bank.

        arg:    item_receiver (osid.assessment.ItemReceiver): the item
                receiver interface
        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentNotificationSession) - ``an
                _item_notification_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``item_receiver, bank_id`` or ``proxy``
                is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_item_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_item_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentNotificationSession(catalog_id=bank_id, proxy=proxy, runtime=self._runtime, receiver=item_receiver)

    @utilities.arguments_not_none
    def get_item_bank_session(self, proxy):
        """Gets the ``OsidSession`` associated with the item banking service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemBankSession) - an
                ``ItemBankSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_bank()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_bank()`` is ``true``.*

        """
        if not self.supports_item_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemBankSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_item_bank_assignment_session(self, proxy):
        """Gets the ``OsidSession`` associated with the item bank assignment service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemBankAssignmentSession) - an
                ``ItemBankAssignmentSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_bank_assignment()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_bank_assignment()`` is ``true``.*

        """
        if not self.supports_item_bank_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemBankAssignmentSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_item_smart_bank_session(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the item smart banking service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.ItemSmartBankSession) - an
                ``ItemSmartBankSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_item_smart_bank()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_item_smart_bank()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        if not self.supports_item_smart_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.ItemSmartBankSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentLookupSession) - an
                ``AssessmentLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_lookup()`` is ``true``.*

        """
        if not self.supports_assessment_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_lookup_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment lookup service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentLookupSession) - ``an
                _assessment_lookup_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentLookupSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_query_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment query service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentQuerySession) - an
                ``AssessmentQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_query()`` is ``true``.*

        """
        if not self.supports_assessment_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_query_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment query service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentQuerySession) - ``an
                _assessment_query_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_query()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentQuerySession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_search_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment search service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentSearchSession) - an
                ``AssessmentSearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_search()`` is ``true``.*

        """
        if not self.supports_assessment_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentSearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_search_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment search service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentSearchSession) - ``an
                _assessment_search_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentSearchSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_admin_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment administration service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentAdminSession) - an
                ``AssessmentAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_admin()`` is ``true``.*

        """
        if not self.supports_assessment_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_admin_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment admin service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentAdminSession) - ``an
                _assessment_admin_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_admin()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentAdminSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_notification_session(self, assessment_receiver, proxy):
        """Gets the notification session for notifications pertaining to assessment changes.

        arg:    assessment_receiver
                (osid.assessment.AssessmentReceiver): the assessment
                receiver interface
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentNotificationSession) - an
                ``AssessmentNotificationSession``
        raise:  NullArgument - ``assessment_receiver`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_notification()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_notification()`` is ``true``.*

        """
        if not self.supports_assessment_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentNotificationSession(proxy=proxy, runtime=self._runtime, receiver=assessment_receiver)

    @utilities.arguments_not_none
    def get_assessment_notification_session_for_bank(self, assessment_receiver, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment notification service for the given bank.

        arg:    assessment_receiver
                (osid.assessment.AssessmentReceiver): the assessment
                receiver interface
        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentNotificationSession) - ``an
                _assessment_notification_session``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``assessment_receiver, bank_id`` or
                ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_notification()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentNotificationSession(catalog_id=bank_id, proxy=proxy, runtime=self._runtime, receiver=assessment_receiver)

    @utilities.arguments_not_none
    def get_assessment_bank_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment banking service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentBankSession) - an
                ``AssessmentBankSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_bank()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_bank()`` is ``true``.*

        """
        if not self.supports_assessment_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentBankSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_bank_assignment_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment bank assignment service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentBankAssignmentSession) - an
                ``AssessmentBankAssignmentSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_bank_assignment()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_bank_assignment()`` is ``true``.*

        """
        if not self.supports_assessment_bank_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentBankAssignmentSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_smart_bank_session(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment smart banking service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentSmartBankSession) - an
                ``AssessmentSmartBankSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_smart_bank()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_smart_bank()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        if not self.supports_assessment_smart_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentSmartBankSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_basic_authoring_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment authoring service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentBasicAuthoringSession) - an
                ``AssessmentBasicAuthoringSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_basic_authoring()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_basic_authoring()`` is ``true``.*

        """
        if not self.supports_assessment_basic_authoring():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentBasicAuthoringSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_basic_authoring_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment authoring service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of a bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentBasicAuthoringSession) - an
                ``AssessmentBasicAuthoringSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_basic_authoring()`` or
                ``supports_visibe_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_basic_authoring()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        if not self.supports_assessment_basic_authoring():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentBasicAuthoringSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment offered lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedLookupSession) - an
                ``AssessmentOfferedLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_offered_lookup()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_lookup()`` is ``true``.*

        """
        if not self.supports_assessment_offered_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_lookup_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment offered lookup service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedLookupSession) - an
                ``AssessmentOfferedLookupSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_offered_lookup()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_offered_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentOfferedLookupSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_query_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment offered query service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedQuerySession) - an
                ``AssessmentOfferedQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_offered_query()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_query()`` is ``true``.*

        """
        if not self.supports_assessment_offered_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_query_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment offered query service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedQuerySession) - an
                ``AssessmentOfferedQuerySession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_offered_query()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_query()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_offered_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentOfferedQuerySession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_search_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment offered search service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedSearchSession) - an
                ``AssessmentOfferedSearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_offered_search()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_search()`` is ``true``.*

        """
        if not self.supports_assessment_offered_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedSearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_search_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment offered search service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedSearchSession) - an
                ``AssessmentOfferedSearchSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or proxy is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_offered_search()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_offered_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentOfferedSearchSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_admin_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment offered administration service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedAdminSession) - an
                ``AssessmentOfferedAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_offered_admin()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_admin()`` is ``true``.*

        """
        if not self.supports_assessment_offered_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_admin_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment offered admin service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedAdminSession) - an
                ``AssessmentOfferedAdminSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_offered_admin()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_admin()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_offered_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentOfferedAdminSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_notification_session(self, assessment_offered_receiver, proxy):
        """Gets the notification session for notifications pertaining to offered assessment changes.

        arg:    assessment_offered_receiver
                (osid.assessment.AssessmentOfferedReceiver): the
                assessment offered receiver interface
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedNotificationSession) -
                an ``AssessmentOfferedNotificationSession``
        raise:  NullArgument - ``assessment_offered_receiver`` or
                ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_offered_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_notification()`` is ``true``.*

        """
        if not self.supports_assessment_offered_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedNotificationSession(proxy=proxy, runtime=self._runtime, receiver=assessment_offered_receiver)

    @utilities.arguments_not_none
    def get_assessment_offered_notification_session_for_bank(self, assessment_offered_receiver, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the offered assessment notification service for the given bank.

        arg:    assessment_offered_receiver
                (osid.assessment.AssessmentOfferedReceiver): the
                assessment offered receiver interface
        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedNotificationSession) -
                a ``AssessmentOfferedNotificationSession``
        raise:  NotFound - ``bank_id`` or ``proxy`` not found
        raise:  NullArgument - ``assessment_offered_receiver, bank_id``
                or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented -
                ``supports_assessment_offered_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_offered_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentOfferedNotificationSession(catalog_id=bank_id, proxy=proxy, runtime=self._runtime, receiver=assessment_offered_receiver)

    @utilities.arguments_not_none
    def get_assessment_offered_bank_session(self, proxy):
        """Gets the session for retrieving offered assessments to bank mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedBankSession) - an
                ``AssessmentOfferedBankSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_offered_bank()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_bank()`` is ``true``.*

        """
        if not self.supports_assessment_offered_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedBankSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_bank_assignment_session(self, proxy):
        """Gets the session for assigning offered assessments to bank mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedBankAssignmentSession)
                - an ``AssessmentOfferedBankAssignmentSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_offered_bank_assignment()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_bank_assignment()`` is ``true``.*

        """
        if not self.supports_assessment_offered_bank_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedBankAssignmentSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_offered_smart_bank_session(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment offered smart banking service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentOfferedSmartBankSession) - an
                ``AssessmentOfferedSmartBankSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_offered_smart_bank()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_offered_smart_bank()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        if not self.supports_assessment_offered_smart_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentOfferedSmartBankSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment taken lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenLookupSession) - an
                ``AssessmentTakenLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_taken_lookup()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_lookup()`` is ``true``.*

        """
        if not self.supports_assessment_taken_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_lookup_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment taken lookup service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenLookupSession) - an
                ``AssessmentTakenLookupSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_taken_lookup()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_lookup()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_taken_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentTakenLookupSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_query_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment taken query service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenQuerySession) - an
                ``AssessmentTakenQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_taken_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_query()`` is ``true``.*

        """
        if not self.supports_assessment_taken_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_query_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment taken query service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenQuerySession) - an
                ``AssessmentTakenQuerySession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_taken_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_query()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_taken_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentTakenQuerySession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_search_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment taken search service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenSearchSession) - an
                ``AssessmentTakenSearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_taken_search()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_search()`` is ``true``.*

        """
        if not self.supports_assessment_taken_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenSearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_search_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment taken search service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenSearchSession) - an
                ``AssessmentTakenSearchSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_taken_search()``
                or ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_search()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_taken_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentTakenSearchSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_admin_session(self, proxy):
        """Gets the ``OsidSession`` associated with the assessment taken administration service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenAdminSession) - an
                ``AssessmentTakenAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_taken_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_admin()`` is ``true``.*

        """
        if not self.supports_assessment_taken_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_admin_session_for_bank(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment taken admin service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenAdminSession) - an
                ``AssessmentTakenSearchSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented - ``supports_assessment_taken_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_admin()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_taken_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentTakenAdminSession(bank_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_notification_session(self, assessment_taken_receiver, proxy):
        """Gets the notification session for notifications pertaining to taken assessment changes.

        arg:    assessment_taken_receiver
                (osid.assessment.AssessmentTakenReceiver): the
                assessment taken receiver interface
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenNotificationSession) -
                an ``AssessmentTakenNotificationSession``
        raise:  NullArgument - ``assessment_taken_receiver`` or
                ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_taken_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_notification()`` is ``true``.*

        """
        if not self.supports_assessment_taken_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenNotificationSession(proxy=proxy, runtime=self._runtime, receiver=assessment_taken_receiver)

    @utilities.arguments_not_none
    def get_assessment_taken_notification_session_for_bank(self, assessment_taken_receiver, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the taken assessment notification service for the given bank.

        arg:    assessment_taken_receiver
                (osid.assessment.AssessmentTakenReceiver): the
                assessment taken receiver interface
        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenNotificationSession) -
                an ``AssessmentTakenNotificationSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``assessment_taken_receiver, bank_id`` or
                ``proxy`` is ``null``
        raise:  OperationFailed - ``unable to complete request``
        raise:  Unimplemented -
                ``supports_assessment_taken_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_notification()`` and
        ``supports_visible_federation()`` are ``true``.*

        """
        if not self.supports_assessment_taken_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.AssessmentTakenNotificationSession(catalog_id=bank_id, proxy=proxy, runtime=self._runtime, receiver=assessment_taken_receiver)

    @utilities.arguments_not_none
    def get_assessment_taken_bank_session(self, proxy):
        """Gets the session for retrieving taken assessments to bank mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenBankSession) - an
                ``AssessmentTakenBankSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_taken_bank()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_bank()`` is ``true``.*

        """
        if not self.supports_assessment_taken_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenBankSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_bank_assignment_session(self, proxy):
        """Gets the session for assigning taken assessments to bank mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenBankAssignmentSession) -
                an ``AssessmentTakenBankAssignmentSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_taken_bank_assignment()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_bank_assignment()`` is ``true``.*

        """
        if not self.supports_assessment_taken_bank_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenBankAssignmentSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_assessment_taken_smart_bank_session(self, bank_id, proxy):
        """Gets the ``OsidSession`` associated with the assessment taken smart banking service for the given bank.

        arg:    bank_id (osid.id.Id): the ``Id`` of the bank
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.AssessmentTakenSmartBankSession) - an
                ``AssessmentTakenSmartBankSession``
        raise:  NotFound - ``bank_id`` not found
        raise:  NullArgument - ``bank_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented -
                ``supports_assessment_taken_smart_bank()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_taken_smart_bank()`` and
        ``supports_visibe_federation()`` is ``true``.*

        """
        if not self.supports_assessment_taken_smart_bank():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.AssessmentTakenSmartBankSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_bank_lookup_session(self, proxy):
        """Gets the OsidSession associated with the bank lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.BankLookupSession) - a
                ``BankLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_lookup() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_lookup()`` is true.*

        """
        if not self.supports_bank_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_bank_query_session(self, proxy):
        """Gets the OsidSession associated with the bank query service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.BankQuerySession) - a
                ``BankQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_query() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_query()`` is true.*

        """
        if not self.supports_bank_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_bank_search_session(self, proxy):
        """Gets the OsidSession associated with the bank search service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.BankSearchSession) - a
                ``BankSearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_search() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_search()`` is true.*

        """
        if not self.supports_bank_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankSearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_bank_admin_session(self, proxy):
        """Gets the OsidSession associated with the bank administration service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.BankAdminSession) - a
                ``BankAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_admin() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_admin()`` is true.*

        """
        if not self.supports_bank_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_bank_notification_session(self, bank_receiver, proxy):
        """Gets the notification session for notifications pertaining to bank service changes.

        arg:    bank_receiver (osid.assessment.BankReceiver): the bank
                receiver interface
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.BankNotificationSession) - a
                ``BankNotificationSession``
        raise:  NullArgument - ``bank_receiver`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_notification() is
                false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_notification()`` is true.*

        """
        if not self.supports_bank_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankNotificationSession(proxy=proxy, runtime=self._runtime, receiver=bank_receiver)

    @utilities.arguments_not_none
    def get_bank_hierarchy_session(self, proxy):
        """Gets the session traversing bank hierarchies.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.BankHierarchySession) - a
                ``BankHierarchySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_hierarchy() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_hierarchy()`` is true.*

        """
        if not self.supports_bank_hierarchy():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankHierarchySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_bank_hierarchy_design_session(self, proxy):
        """Gets the session designing bank hierarchies.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.assessment.BankHierarchyDesignSession) - a
                ``BankHierarchySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_bank_hierarchy_design() is
                false``
        *compliance: optional -- This method must be implemented if
        ``supports_bank_hierarchy_design()`` is true.*

        """
        if not self.supports_bank_hierarchy_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BankHierarchyDesignSession(proxy=proxy, runtime=self._runtime)

    def get_assessment_authoring_proxy_manager(self):
        """Gets an ``AssessmentAuthoringProxyManager``.

        return:
                (osid.assessment.authoring.AssessmentAuthoringProxyManag
                er) - an ``AssessmentAuthoringProxyManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_authoring() is
                false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_authoring()`` is true.*

        """
        raise errors.Unimplemented()

    assessment_authoring_proxy_manager = property(fget=get_assessment_authoring_proxy_manager)

    def get_assessment_batch_proxy_manager(self):
        """Gets an ``AssessmentBatchProxyManager``.

        return: (osid.assessment.batch.AssessmentBatchProxyManager) - an
                ``AssessmentBatchProxyManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_assessment_batch() is false``
        *compliance: optional -- This method must be implemented if
        ``supports_assessment_batch()`` is true.*

        """
        raise errors.Unimplemented()

    assessment_batch_proxy_manager = property(fget=get_assessment_batch_proxy_manager)



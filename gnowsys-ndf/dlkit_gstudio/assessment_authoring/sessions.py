"""GStudio implementations of assessment.authoring sessions."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.assessment_authoring import sessions as abc_assessment_authoring_sessions
from ..osid import sessions as osid_sessions
from ..osid.sessions import OsidSession
from dlkit.abstract_osid.osid import errors




class AssessmentPartLookupSession(abc_assessment_authoring_sessions.AssessmentPartLookupSession, osid_sessions.OsidSession):
    """This session defines methods for retrieving assessment parts."""

    def get_bank_id(self):
        """Gets the ``Bank``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Bank Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id = property(fget=get_bank_id)

    def get_bank(self):
        """Gets the ``Bank`` associated with this session.

        return: (osid.assessment.Bank) - the ``Bank`` associated with
                this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank = property(fget=get_bank)

    def can_lookup_assessment_parts(self):
        """Tests if this user can perform ``AssessmentPart`` lookups.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may not offer lookup operations
        to unauthorized users.

        return: (boolean) - ``false`` if lookup methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_comparative_assessment_part_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_assessment_part_view(self):
        """A complete view of the ``AssessmentPart`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_federated_bank_view(self):
        """Federates the view for methods in this session.

        A federated view will include assessment parts in catalogs which
        are children of this catalog in the bank hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_isolated_bank_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts retrievals to this bank only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_active_assessment_part_view(self):
        """Only active assessment parts are returned by methods in this session.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_any_status_assessment_part_view(self):
        """All active and inactive assessment parts are returned by methods in this session.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_sequestered_assessment_part_view(self):
        """The methods in this session omit sequestered assessment parts.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_unsequestered_assessment_part_view(self):
        """The methods in this session return all assessment parts, including sequestered assessment parts.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assessment_part(self, assessment_part_id):
        """Gets the ``AssessmentPart`` specified by its ``Id``.

        arg:    assessment_part_id (osid.id.Id): the ``Id`` of the
                ``AssessmentPart`` to retrieve
        return: (osid.assessment.authoring.AssessmentPart) - the
                returned ``AssessmentPart``
        raise:  NotFound - no ``AssessmentPart`` found with the given
                ``Id``
        raise:  NullArgument - ``assessment_part_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assessment_parts_by_ids(self, assessment_part_ids):
        """Gets an ``AssessmentPartList`` corresponding to the given ``IdList``.

        arg:    assessment_part_ids (osid.id.IdList): the list of
                ``Ids`` to retrieve
        return: (osid.assessment.authoring.AssessmentPartList) - the
                returned ``AssessmentPart`` list
        raise:  NotFound - an ``Id was`` not found
        raise:  NullArgument - ``assessment_part_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assessment_parts_by_genus_type(self, assessment_part_genus_type):
        """Gets an ``AssessmentPartList`` corresponding to the given assessment part genus ``Type`` which does not include assessment parts of types derived from the specified ``Type``.

        arg:    assessment_part_genus_type (osid.type.Type): an
                assessment part genus type
        return: (osid.assessment.authoring.AssessmentPartList) - the
                returned ``AssessmentPart`` list
        raise:  NullArgument - ``assessment_part_genus_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assessment_parts_by_parent_genus_type(self, assessment_genus_type):
        """Gets an ``AssessmentPartList`` corresponding to the given assessment part genus ``Type`` and include any additional assessment parts with genus types derived from the specified ``Type``.

        arg:    assessment_genus_type (osid.type.Type): an assessment
                part genus type
        return: (osid.assessment.authoring.AssessmentPartList) - the
                returned ``AssessmentPart`` list
        raise:  NullArgument - ``assessment_part_genus_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assessment_parts_by_record_type(self, assessment_part_record_type):
        """Gets an ``AssessmentPart`` containing the given assessment part record ``Type``.

        arg:    assessment_part_record_type (osid.type.Type): an
                assessment part record type
        return: (osid.assessment.authoring.AssessmentPartList) - the
                returned ``AssessmentPart`` list
        raise:  NullArgument - ``assessment_part_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assessment_parts_for_assessment(self, assessment_id):
        """Gets an ``AssessmentPart`` for the given assessment.

        arg:    assessment_id (osid.id.Id): an assessment ``Id``
        return: (osid.assessment.authoring.AssessmentPartList) - the
                returned ``AssessmentPart`` list
        raise:  NullArgument - ``assessment_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_assessment_parts(self):
        """Gets all ``AssessmentParts``.

        return: (osid.assessment.authoring.AssessmentPartList) - a list
                of ``AssessmentParts``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    assessment_parts = property(fget=get_assessment_parts)


class AssessmentPartAdminSession(abc_assessment_authoring_sessions.AssessmentPartAdminSession, osid_sessions.OsidSession):
    """This session creates, updates, and deletes ``AssessmentParts``.

    The data for create and update is provided by the consumer via the
    form object. ``OsidForms`` are requested for each create or update
    and may not be reused.

    Create and update operations differ in their usage. To create an
    ``AssessmentPart,`` an ``AssessmentPartForm`` is requested using
    ``get_assessment_part_form_for_create()`` specifying the desired
    record ``Types`` or none if no record ``Types`` are needed. The
    returned ``AssessmentPartForm`` will indicate that it is to be used
    with a create operation and can be used to examine metdata or
    validate data prior to creation. Once the ``AssessmentPartForm`` is
    submiited to a create operation, it cannot be reused with another
    create operation unless the first operation was unsuccessful. Each
    ``AssessmentPartForm`` corresponds to an attempted transaction.

    For updates, ``AssessmentPartForms`` are requested to the
    ``AssessmentPart``  ``Id`` that is to be updated using
    ``getAssessmentPartFormForUpdate()``. Similarly, the
    ``AssessmentPartForm`` has metadata about the data that can be
    updated and it can perform validation before submitting the update.
    The ``AssessmentPartForm`` can only be used once for a successful
    update and cannot be reused.

    The delete operations delete ``AssessmentParts``.

    This session includes an ``Id`` aliasing mechanism to assign an
    external ``Id`` to an internally assigned Id.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_bank_id(self):
        """Gets the ``Bank``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Bank Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id = property(fget=get_bank_id)

    def get_bank(self):
        """Gets the ``Bank`` associated with this session.

        return: (osid.assessment.Bank) - the ``Bank`` associated with
                this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank = property(fget=get_bank)

    def can_create_assessment_parts(self):
        """Tests if this user can create assessment parts.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known mapping methods in
        this session will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        create operations to unauthorized users.

        return: (boolean) - ``false`` if ``AssessmentPart`` creation is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_create_assessment_part_with_record_types(self, assessment_part_record_types):
        """Tests if this user can create a single ``AssessmentPart`` using the desired record types.

        While
        ``AssessmentAuthoringManager.getAssessmentPartRecordTypes()``
        can be used to examine which records are supported, this method
        tests which record(s) are required for creating a specific
        ``AssessmentPart``. Providing an empty array tests if an
        ``AssessmentPart`` can be created with no records.

        arg:    assessment_part_record_types (osid.type.Type[]): array
                of assessment part record types
        return: (boolean) - ``true`` if ``AssessmentPart`` creation
                using the specified record ``Types`` is supported,
                ``false`` otherwise
        raise:  NullArgument - ``assessment_part_record_types`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_assessment_part_form_for_create_for_assessment(self, assessment_id, assessment_part_record_types):
        """Gets the assessment part form for creating new assessment parts for an assessment.

        A new form should be requested for each create transaction.

        arg:    assessment_id (osid.id.Id): an assessment ``Id``
        arg:    assessment_part_record_types (osid.type.Type[]): array
                of assessment part record types to be included in the
                create operation or an empty list if none
        return: (osid.assessment.authoring.AssessmentPartForm) - the
                assessment part form
        raise:  NotFound - ``assessment_id`` is not found
        raise:  NullArgument - ``assessment_id`` or
                ``assessment_part_record_types`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unsupported - unable to get form for requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def create_assessment_part_for_assessment(self, assessment_part_form):
        """Creates a new assessment part.

        arg:    assessment_part_form
                (osid.assessment.authoring.AssessmentPartForm):
                assessment part form
        return: (osid.assessment.authoring.AssessmentPart) - the new
                part
        raise:  IllegalState - ``assessment_part_form`` already used in
                a create transaction
        raise:  InvalidArgument - ``assessment_part_form`` is invalid
        raise:  NullArgument - ``assessment_part_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unsupported - ``assessment_part_form`` did not originate
                from
                ``get_assessment_part_form_for_create_for_assessment()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assessment_part_form_for_create_for_assessment_part(self, assessment_part_id, assessment_part_record_types):
        """Gets the assessment part form for creating new assessment parts under another assessment part.

        A new form should be requested for each create transaction.

        arg:    assessment_part_id (osid.id.Id): an assessment part
                ``Id``
        arg:    assessment_part_record_types (osid.type.Type[]): array
                of assessment part record types to be included in the
                create operation or an empty list if none
        return: (osid.assessment.authoring.AssessmentPartForm) - the
                assessment part form
        raise:  NotFound - ``assessment_part_id`` is not found
        raise:  NullArgument - ``assessment_part_id`` or
                ``assessment_part_record_types`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unsupported - unable to get form for requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def create_assessment_part_for_assessment_part(self, assessment_part_form):
        """Creates a new assessment part.

        arg:    assessment_part_form
                (osid.assessment.authoring.AssessmentPartForm):
                assessment part form
        return: (osid.assessment.authoring.AssessmentPart) - the new
                part
        raise:  IllegalState - ``assessment_part_form`` already used in
                a create transaction
        raise:  InvalidArgument - ``assessment_part_form`` is invalid
        raise:  NullArgument - ``assessment_part_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unsupported - ``assessment_part_form`` did not originate
                from ``get_assessment_part_form_for_create_for_assessmen
                t_part()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_update_assessment_parts(self):
        """Tests if this user can update ``AssessmentParts``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known updating an
        ``AssessmentPart`` will result in a ``PermissionDenied``. This
        is intended as a hint to an application that may opt not to
        offer update operations to an unauthorized user.

        return: (boolean) - ``false`` if assessment part modification is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_assessment_part_form_for_update(self, assessment_part_id):
        """Gets the assessment part form for updating an existing assessment part.

        A new assessment part form should be requested for each update
        transaction.

        arg:    assessment_part_id (osid.id.Id): the ``Id`` of the
                ``AssessmentPart``
        return: (osid.assessment.authoring.AssessmentPartForm) - the
                assessment part form
        raise:  NotFound - ``assessment_part_id`` is not found
        raise:  NullArgument - ``assessment_part_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def update_assessment_part(self, assessment_part_id, assessment_part_form):
        """Updates an existing assessment part.

        arg:    assessment_part_id (osid.id.Id): the ``Id`` of the
                ``AssessmentPart``
        arg:    assessment_part_form
                (osid.assessment.authoring.AssessmentPartForm): part
                form
        raise:  NotFound - ``assessment_part_id`` not found
        raise:  NullArgument - ``assessment_part_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        raise:  Unsupported - ``assessment_part_form`` is not of this
                service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_delete_assessment_parts(self):
        """Tests if this user can delete ``AssessmentParts``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known deleting an
        ``AssessmentPart`` will result in a ``PermissionDenied``. This
        is intended as a hint to an application that may opt not to
        offer delete operations to an unauthorized user.

        return: (boolean) - ``false`` if ``AssessmentPart`` deletion is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def delete_assessment_part(self, assessment_part_id):
        """Removes an asessment part and all mapped items.

        arg:    assessment_part_id (osid.id.Id): the ``Id`` of the
                ``AssessmentPart``
        raise:  NotFound - ``assessment_part_id`` not found
        raise:  NullArgument - ``assessment_part_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure occurred
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_manage_assessment_part_aliases(self):
        """Tests if this user can manage ``Id`` aliases for ``AssessmentParts``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known changing an alias
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer alias
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``AssessmentPart`` aliasing is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def alias_assessment_part(self, assessment_part_id, alias_id):
        """Adds an ``Id`` to an ``AssessmentPart`` for the purpose of creating compatibility.

        The primary ``Id`` of the ``AssessmentPart`` is determined by
        the provider. The new ``Id`` is an alias to the primary ``Id``.
        If the alias is a pointer to another assessment part, it is
        reassigned to the given assessment part ``Id``.

        arg:    assessment_part_id (osid.id.Id): the ``Id`` of an
                ``AssessmentPart``
        arg:    alias_id (osid.id.Id): the alias ``Id``
        raise:  AlreadyExists - ``alias_id`` is in use as a primary
                ``Id``
        raise:  NotFound - ``assessment_part_id`` not found
        raise:  NullArgument - ``assessment_part_id`` or ``alias_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentPartItemSession(abc_assessment_authoring_sessions.AssessmentPartItemSession, osid_sessions.OsidSession):
    """This session defines methods for looking up ``Item`` to ``AssessmentPart`` mappings."""

    def get_bank_id(self):
        """Gets the ``Bank``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Bank Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id = property(fget=get_bank_id)

    def get_bank(self):
        """Gets the ``Bank`` associated with this session.

        return: (osid.assessment.Bank) - the ``Bank`` associated with
                this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank = property(fget=get_bank)

    def can_access_assessment_part_items(self):
        """Tests if this user can perform assessment part lookups.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer lookup
        operations to unauthorized users.

        return: (boolean) - ``false`` if lookup methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def use_comparative_asseessment_part_item_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_assessment_part_item_view(self):
        """A complete view of the returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_federated_bank_view(self):
        """Federates the view for methods in this session.

        A federated view will include assessment parts in catalogs which
        are children of this catalog in the bank hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_isolated_bank_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts retrievals to this bank only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assessment_part_items(self, assessment_part_id):
        """Gets the list of items mapped to the given ``AssessmentPart``.

        In plenary mode, the returned list contains all known items or
        an error results. Otherwise, the returned list may contain only
        those items that are accessible through this session.

        arg:    assessment_part_id (osid.id.Id): ``Id`` of the
                ``AssessmentPart``
        return: (osid.assessment.ItemList) - list of items
        raise:  NotFound - ``assessment_part_id`` not found
        raise:  NullArgument - ``assessment_part_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_assessment_parts_by_item(self, item_id):
        """Gets the assessment parts containing the given item.

        In plenary mode, the returned list contains all known assessment
        parts or an error results. Otherwise, the returned list may
        contain only those assessment parts that are accessible through
        this session.

        arg:    item_id (osid.id.Id): ``Id`` of the ``Item``
        return: (osid.assessment.authoring.AssessmentPartList) - the
                returned ``AssessmentPart list``
        raise:  NotFound - ``item_id`` is not found
        raise:  NullArgument - ``item_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class AssessmentPartItemDesignSession(abc_assessment_authoring_sessions.AssessmentPartItemDesignSession, osid_sessions.OsidSession):
    """This session provides the means for adding items to an assessment part.

    The item is identified inside an assesment part using its own Id. To
    add the same item to the assessment part, multiple assessment parts
    should be used and placed at the same level in the
    ``AssessmentPart`` hierarchy.

    """

    def get_bank_id(self):
        """Gets the ``Bank``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Bank Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id = property(fget=get_bank_id)

    def get_bank(self):
        """Gets the ``Bank`` associated with this session.

        return: (osid.assessment.Bank) - the ``Bank`` associated with
                this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank = property(fget=get_bank)

    def can_design_assessment_parts(self):
        """Tests if this user can manage mapping of ``Items`` to ``AssessmentParts``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as an application hint that may opt not to offer composition
        operations.

        return: (boolean) - ``false`` if assessment part composition is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def add_item(self, item_id, assessment_part_id):
        """Appends an item to an assessment part.

        arg:    item_id (osid.id.Id): ``Id`` of the ``Item``
        arg:    assessment_part_id (osid.id.Id): ``Id`` of the
                ``AssessmentPart``
        raise:  AlreadyExists - ``item_id`` already part of
                ``assessment_part_id``
        raise:  NotFound - ``item_id`` or ``assessment_part_id`` not
                found
        raise:  NullArgument - ``item_id`` or ``assessment_part_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization fauilure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def move_item_ahead(self, item_id, assessment_part_id, reference_id):
        """Reorders items in an assessment part by moving the specified item in front of a reference item.

        arg:    item_id (osid.id.Id): ``Id`` of the ``Item``
        arg:    assessment_part_id (osid.id.Id): ``Id`` of the
                ``AssessmentPartId``
        arg:    reference_id (osid.id.Id): ``Id`` of the reference
                ``Item``
        raise:  NotFound - ``item_id`` or ``reference_id``  ``not found
                in assessment_part_id``
        raise:  NullArgument - ``item_id, reference_id`` or
                ``assessment_part_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization fauilure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def move_item_behind(self, item_id, assessment_part_id, reference_id):
        """Reorders items in an assessment part by moving the specified item behind of a reference item.

        arg:    item_id (osid.id.Id): ``Id`` of the ``Item``
        arg:    assessment_part_id (osid.id.Id): ``Id of the
                AssessmentPartId``
        arg:    reference_id (osid.id.Id): ``Id`` of the reference
                ``Item``
        raise:  NotFound - ``item_id`` or ``reference_id``  ``not found
                in assessment_part_id``
        raise:  NullArgument - ``item_id, reference_id`` or
                ``assessment_part_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization fauilure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_items(self, item_ids, assessment_part_id):
        """Reorders a set of items in an assessment part.

        arg:    item_ids (osid.id.Id[]): ``Ids`` for a set of ``Items``
        arg:    assessment_part_id (osid.id.Id): ``Id`` of the
                ``AssessmentPartId``
        raise:  NotFound - ``assessment_part_id`` not found or, an
                ``item_id`` not related to ``assessment_part_id``
        raise:  NullArgument - ``item_ids`` or ``agenda_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def remove_item(self, item_id, assessment_part_id):
        """Removes an ``Item`` from an ``AssessmentPartId``.

        arg:    item_id (osid.id.Id): ``Id`` of the ``Item``
        arg:    assessment_part_id (osid.id.Id): ``Id`` of the
                ``AssessmentPartId``
        raise:  NotFound - ``item_id``  ``not found in
                assessment_part_id``
        raise:  NullArgument - ``item_id`` or ``assessment_part_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization fauilure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class SequenceRuleLookupSession(abc_assessment_authoring_sessions.SequenceRuleLookupSession, osid_sessions.OsidSession):
    """This session provides methods for retrieving ``SequenceRules``."""

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_bank_id(self):
        """Gets the ``Bank``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Bank Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id = property(fget=get_bank_id)

    def get_bank(self):
        """Gets the ``Bank`` associated with this session.

        return: (osid.assessment.Bank) - the bank
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank = property(fget=get_bank)

    def can_lookup_sequence_rules(self):
        """Tests if this user can perform ``SequenceRules`` lookups.

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

    def use_comparative_sequence_rule_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_sequence_rule_view(self):
        """A complete view of the ``SequenceRule`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_federated_bank_view(self):
        """Federates the view for methods in this session.

        A federated view will include sequence rule in banks which are
        children of this bank in the bank hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_isolated_bank_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts lookups to this bank only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_active_sequence_rule_view(self):
        """Only active sequence rules are returned by methods in this session.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_any_status_sequence_rule_view(self):
        """All active and inactive sequence rules are returned by methods in this session.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_sequence_rule(self, sequence_rule_id):
        """Gets the ``SequenceRule`` specified by its ``Id``.

        arg:    sequence_rule_id (osid.id.Id): ``Id`` of the
                ``SequenceRule``
        return: (osid.assessment.authoring.SequenceRule) - the sequence
                rule
        raise:  NotFound - ``sequence_rule_id`` not found
        raise:  NullArgument - ``sequence_rule_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_sequence_rules_by_ids(self, sequence_rule_ids):
        """Gets a ``SequenceRuleList`` corresponding to the given ``IdList``.

        arg:    sequence_rule_ids (osid.id.IdList): the list of ``Ids``
                to retrieve
        return: (osid.assessment.authoring.SequenceRuleList) - the
                returned ``SequenceRule`` list
        raise:  NotFound - a ``Id was`` not found
        raise:  NullArgument - ``sequence_rule_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_sequence_rules_by_genus_type(self, sequence_rule_genus_type):
        """Gets a ``SequenceRuleList`` corresponding to the given sequence rule genus ``Type`` which does not include sequence rule of genus types derived from the specified ``Type``.

        arg:    sequence_rule_genus_type (osid.type.Type): a sequence
                rule genus type
        return: (osid.assessment.authoring.SequenceRuleList) - the
                returned ``SequenceRule`` list
        raise:  NullArgument - ``sequence_rule_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_sequence_rules_by_parent_genus_type(self, sequence_rule_genus_type):
        """Gets a ``SequenceRuleList`` corresponding to the given sequence rule genus ``Type`` and include any additional sequence rule with genus types derived from the specified ``Type``.

        arg:    sequence_rule_genus_type (osid.type.Type): a sequence
                rule genus type
        return: (osid.assessment.authoring.SequenceRuleList) - the
                returned ``SequenceRule`` list
        raise:  NullArgument - ``sequence_rule_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_sequence_rules_by_record_type(self, sequence_rule_record_type):
        """Gets a ``SequenceRuleList`` containing the given sequence rule record ``Type``.

        arg:    sequence_rule_record_type (osid.type.Type): a sequence
                rule record type
        return: (osid.assessment.authoring.SequenceRuleList) - the
                returned ``SequenceRule`` list
        raise:  NullArgument - ``sequence_rule_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_sequence_rules_for_assessment_part(self, assessment_part_id):
        """Gets a ``SequenceRuleList`` for the given source assessment part.

        arg:    assessment_part_id (osid.id.Id): an assessment part
                ``Id``
        return: (osid.assessment.authoring.SequenceRuleList) - the
                returned ``SequenceRule`` list
        raise:  NullArgument - ``assessment_part_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_sequence_rules_for_next_assessment_part(self, next_assessment_part_id):
        """Gets a ``SequenceRuleList`` for the given target assessment part.

        arg:    next_assessment_part_id (osid.id.Id): an assessment part
                ``Id``
        return: (osid.assessment.authoring.SequenceRuleList) - the
                returned ``SequenceRule`` list
        raise:  NullArgument - ``next_assessment_part_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_sequence_rules_for_assessment_parts(self, assessment_part_id, next_assessment_part_id):
        """Gets a ``SequenceRuleList`` for the given source and target assessment parts.

        arg:    assessment_part_id (osid.id.Id): source assessment part
                ``Id``
        arg:    next_assessment_part_id (osid.id.Id): target assessment
                part ``Id``
        return: (osid.assessment.authoring.SequenceRuleList) - the
                returned ``SequenceRule`` list
        raise:  NullArgument - ``assessment_part_id`` or
                ``next_assessment_part_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_sequence_rules_for_assessment(self, assessment_id):
        """Gets a ``SequenceRuleList`` for an entire assessment.

        arg:    assessment_id (osid.id.Id): an assessment ``Id``
        return: (osid.assessment.authoring.SequenceRuleList) - the
                returned ``SequenceRule`` list
        raise:  NullArgument - ``assessment_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_sequence_rules(self):
        """Gets all ``SequenceRules``.

        return: (osid.assessment.authoring.SequenceRuleList) - the
                returned ``SequenceRule`` list
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    sequence_rules = property(fget=get_sequence_rules)


class SequenceRuleAdminSession(abc_assessment_authoring_sessions.SequenceRuleAdminSession, osid_sessions.OsidSession):
    """This session creates and removes sequence rules.

    The data for create and update is provided via the
    ``SequenceRuleForm``.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_bank_id(self):
        """Gets the ``Bank``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Bank Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank_id = property(fget=get_bank_id)

    def get_bank(self):
        """Gets the ``Bank`` associated with this session.

        return: (osid.assessment.Bank) - the bank
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    bank = property(fget=get_bank)

    def can_create_sequence_rule(self):
        """Tests if this user can create sequence rules.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known creating a
        ``SequenceRule`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        create operations to an unauthorized user.

        return: (boolean) - ``false`` if ``SequenceRule`` creation is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_create_sequence_rule_with_record_types(self, sequence_rule_record_types):
        """Tests if this user can create a single ``SequenceRule`` using the desired record types.

        While
        ``AssessmentAuthoringManager.getSequenceRuleRecordTypes()`` can
        be used to examine which records are supported, this method
        tests which record(s) are required for creating a specific
        ``SequenceRule``. Providing an empty array tests if a
        ``SequenceRule`` can be created with no records.

        arg:    sequence_rule_record_types (osid.type.Type[]): array of
                sequence rule record types
        return: (boolean) - ``true`` if ``SequenceRule`` creation using
                the specified record ``Types`` is supported, ``false``
                otherwise
        raise:  NullArgument - ``sequence_rule_record_types`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_sequence_rule_form_for_create(self, assessment_part_id, next_assessment_part_id, sequence_rule_record_types):
        """Gets the sequence rule form for creating new sequence rules between two assessment parts.

        A new form should be requested for each create transaction.

        arg:    assessment_part_id (osid.id.Id): the source assessment
                part ``Id``
        arg:    next_assessment_part_id (osid.id.Id): the target
                assessment part ``Id``
        arg:    sequence_rule_record_types (osid.type.Type[]): array of
                sequence rule record types
        return: (osid.assessment.authoring.SequenceRuleForm) - the
                sequence rule form
        raise:  InvalidArgument - ``assessment_part_id`` and
                ``next_assessment_part_id`` not on the same assessment
        raise:  NotFound - ``assessment_part_id`` or
                ``next_assessment_part_id`` is not found
        raise:  NullArgument - ``assessment_part_id,
                next_assessment_part_id`` , or
                ``sequence_rule_record_types`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - unable to get form for requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def create_sequence_rule(self, sequence_rule_form):
        """Creates a new ``SequenceRule``.

        arg:    sequence_rule_form
                (osid.assessment.authoring.SequenceRuleForm): the form
                for this ``SequenceRule``
        return: (osid.assessment.authoring.SequenceRule) - the new
                ``SequenceRule``
        raise:  IllegalState - ``sequence_rule_form`` already used in a
                create transaction
        raise:  InvalidArgument - one or more of the form elements is
                invalid
        raise:  NullArgument - ``sequence_rule_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``sequence_rule_form`` did not originate
                from ``get_sequence_rule_form_for_create()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_update_sequence_rules(self):
        """Tests if this user can update sequence rules.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known updating a
        ``SequenceRule`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        update operations to an unauthorized user.

        return: (boolean) - ``false`` if ``SequenceRule`` modification
                is not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_sequence_rule_form_for_update(self, sequence_rule_id):
        """Gets the sequence rule form for updating an existing sequence rule.

        A new sequence rule form should be requested for each update
        transaction.

        arg:    sequence_rule_id (osid.id.Id): the ``Id`` of the
                ``SequenceRule``
        return: (osid.assessment.authoring.SequenceRuleForm) - the
                sequence rule form
        raise:  NotFound - ``sequence_rule_id`` is not found
        raise:  NullArgument - ``sequence_rule_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def update_sequence_rule(self, sequence_rule_form):
        """Updates an existing sequence rule.

        arg:    sequence_rule_form
                (osid.assessment.authoring.SequenceRuleForm): the form
                containing the elements to be updated
        raise:  IllegalState - ``sequence_rule_form`` already used in an
                update transaction
        raise:  InvalidArgument - the form contains an invalid value
        raise:  NullArgument - ``sequence_rule_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``sequence_rule_form`` did not originate
                from ``get_sequence_rule_form_for_update()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_delete_sequence_rules(self):
        """Tests if this user can delete sequence rules.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known deleting a
        ``SequenceRule`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may opt not to offer
        delete operations to an unauthorized user.

        return: (boolean) - ``false`` if ``SequenceRule`` deletion is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def delete_sequence_rule(self, sequence_rule_id):
        """Deletes a ``SequenceRule``.

        arg:    sequence_rule_id (osid.id.Id): the ``Id`` of the
                ``SequenceRule`` to remove
        raise:  NotFound - ``sequence_rule_id`` not found
        raise:  NullArgument - ``sequence_rule_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_manage_sequence_rule_aliases(self):
        """Tests if this user can manage ``Id`` aliases for sequence rules.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known changing an alias
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer alias
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``SequenceRule`` aliasing is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def alias_sequence_rule(self, sequence_rule_id, alias_id):
        """Adds a ``Id`` to a ``SequenceRule`` for the purpose of creating compatibility.

        The primary ``Id`` of the ``SequenceRule`` is determined by the
        provider. The new ``Id`` performs as an alias to the primary
        ``Id`` . If the alias is a pointer to another sequence rule. it
        is reassigned to the given sequence rule ``Id``.

        arg:    sequence_rule_id (osid.id.Id): the ``Id`` of a
                ``SequenceRule``
        arg:    alias_id (osid.id.Id): the alias ``Id``
        raise:  AlreadyExists - ``alias_id`` is already assigned
        raise:  NotFound - ``sequence_rule_id`` not found
        raise:  NullArgument - ``sequence_rule_id`` or ``alias_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_sequence_sequence_rules(self):
        """Tests if this user can order ``SequenceRules``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known sequencing operations
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer sequencing
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``SequenceRule`` ordering is
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def move_sequence_rule_ahead(self, sequence_rule_id, assessment_part_id, reference_id):
        """Reorders sequence rule for a source assessment part by moving the specified sequence rule in front of a reference sequence rule.

        arg:    sequence_rule_id (osid.id.Id): the ``Id`` of a
                ``SequenceRule``
        arg:    assessment_part_id (osid.id.Id): the ``Id`` of an
                ``AssessmentPart``
        arg:    reference_id (osid.id.Id): the reference sequence rule
                ``Id``
        raise:  NotFound - ``sequence_rule_id, assessment_part_id,`` or
                ``reference_id`` not found or, ``sequence_rule_id`` or
                ``reference_id`` not related to ``assessment_part_id``
        raise:  NullArgument - ``sequence_rule_id, assessment_part_id,``
                or ``reference_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def move_sequence_rule_behind(self, sequence_rule_id, assessment_part_id, reference_id):
        """Reorders sequence rule for a source assessment part by moving the specified sequence rule behind a reference sequence rule.

        arg:    sequence_rule_id (osid.id.Id): the ``Id`` of a
                ``SequenceRule``
        arg:    assessment_part_id (osid.id.Id): the ``Id`` of an
                ``AssessmentPart``
        arg:    reference_id (osid.id.Id): the reference sequence rule
                ``Id``
        raise:  NotFound - ``sequence_rule_id, assessment_part_id,`` or
                ``reference_id`` not found or, ``sequence_rule_id`` or
                ``reference_id`` not related to ``assessment_part_id``
        raise:  NullArgument - ``sequence_rule_id, assessment_part_id,``
                or ``reference_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def order_sequence_rules(self, sequence_rule_ids, assessment_part_id):
        """Reorders a set of sequence rules for an assessment part.

        arg:    sequence_rule_ids (osid.id.Id[]): the ``Ids`` for a set
                of ``SequenceRules``
        arg:    assessment_part_id (osid.id.Id): the ``Id`` of an
                ``AssessmentPart``
        raise:  NotFound - ``assessment_part_id`` not found or, a
                ``sequence_rule_id`` not related to
                ``assessment_part_id``
        raise:  NullArgument - ``sequence_rule_ids`` or
                ``assessment_part_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



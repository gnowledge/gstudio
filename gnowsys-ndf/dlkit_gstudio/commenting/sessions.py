"""GStudio implementations of commenting sessions."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.commenting import sessions as abc_commenting_sessions
from ..osid import sessions as osid_sessions
from ..osid.sessions import OsidSession
from dlkit.abstract_osid.osid import errors




class CommentLookupSession(abc_commenting_sessions.CommentLookupSession, osid_sessions.OsidSession):
    """This session defines methods for retrieving comments."""

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_book_id(self):
        """Gets the ``Book``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Book Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    book_id = property(fget=get_book_id)

    def get_book(self):
        """Gets the ``Book`` associated with this session.

        return: (osid.commenting.Book) - the book
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    book = property(fget=get_book)

    def can_lookup_comments(self):
        """Tests if this user can examine this book.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer these
        operations.

        return: (boolean) - ``false`` if book reading methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_comparative_comment_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_comment_view(self):
        """A complete view of the ``Comment`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_federated_book_view(self):
        """Federates the view for methods in this session.

        A federated view will include comments in books which are
        children of this book in the book hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_isolated_book_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts retrievals to this book only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_effective_comment_view(self):
        """Only comments whose effective dates are current are returned by methods in this session.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_any_effective_comment_view(self):
        """All comments of any effective dates are returned by all methods in this session.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comment(self, comment_id):
        """Gets the ``Comment`` specified by its ``Id``.

        arg:    comment_id (osid.id.Id): the ``Id`` of the ``Comment``
                to retrieve
        return: (osid.commenting.Comment) - the returned ``Comment``
        raise:  NotFound - no ``Comment`` found with the given ``Id``
        raise:  NullArgument - ``comment_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_by_ids(self, comment_ids):
        """Gets a ``CommentList`` corresponding to the given ``IdList``.

        arg:    comment_ids (osid.id.IdList): the list of ``Ids`` to
                retrieve
        return: (osid.commenting.CommentList) - the returned ``Comment
                list``
        raise:  NotFound - an ``Id was`` not found
        raise:  NullArgument - ``comment_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_by_genus_type(self, comment_genus_type):
        """Gets a ``CommentList`` corresponding to the given comment genus ``Type`` which does not include comments of genus types derived from the specified ``Type``.

        arg:    comment_genus_type (osid.type.Type): a comment genus
                type
        return: (osid.commenting.CommentList) - the returned ``Comment``
                list
        raise:  NullArgument - ``comment_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_by_parent_genus_type(self, comment_genus_type):
        """Gets a ``CommentList`` corresponding to the given comment genus ``Type`` and include any additional comments with genus types derived from the specified ``Type``.

        arg:    comment_genus_type (osid.type.Type): a comment genus
                type
        return: (osid.commenting.CommentList) - the returned ``Comment``
                list
        raise:  NullArgument - ``comment_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_by_record_type(self, comment_record_type):
        """Gets a ``CommentList`` containing the given comment record ``Type``.

        arg:    comment_record_type (osid.type.Type): a comment record
                type
        return: (osid.commenting.CommentList) - the returned ``Comment``
                list
        raise:  NullArgument - ``comment_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_on_date(self, from_, to):
        """Gets a ``CommentList`` effective during the entire given date range inclusive but not confined to the date range.

        arg:    from (osid.calendaring.DateTime): starting date
        arg:    to (osid.calendaring.DateTime): ending date
        return: (osid.commenting.CommentList) - the returned ``Comment``
                list
        raise:  InvalidArgument - ``from`` is greater than ``to``
        raise:  NullArgument - ``from`` or ``to`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_by_genus_type_on_date(self, comment_genus_type, from_, to):
        """Gets a ``CommentList`` of a given genus type and effective during the entire given date range inclusive but not confined to the date range.

        arg:    comment_genus_type (osid.type.Type): a comment genus
                type
        arg:    from (osid.calendaring.DateTime): starting date
        arg:    to (osid.calendaring.DateTime): ending date
        return: (osid.commenting.CommentList) - the returned ``Comment``
                list
        raise:  InvalidArgument - ``from`` is greater than ``to``
        raise:  NullArgument - ``comment_genus_type, from,`` or ``to``
                is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_for_commentor(self, resource_id):
        """Gets a list of comments corresponding to a resource ``Id``.

        arg:    resource_id (osid.id.Id): the ``Id`` of the resource
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  NullArgument - ``resource_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_for_commentor_on_date(self, resource_id, from_, to):
        """Gets a list of all comments corresponding to a resource ``Id`` and effective during the entire given date range inclusive but not confined to the date range.

        arg:    resource_id (osid.id.Id): the ``Id`` of the resource
        arg:    from (osid.calendaring.DateTime): from date
        arg:    to (osid.calendaring.DateTime): to date
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  InvalidArgument - ``to`` is less than ``from``
        raise:  NullArgument - ``resource_id, from,`` or ``to`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_by_genus_type_for_commentor(self, resource_id, comment_genus_type):
        """Gets a list of comments of the given genus type corresponding to a resource ``Id``.

        arg:    resource_id (osid.id.Id): the ``Id`` of the resource
        arg:    comment_genus_type (osid.type.Type): the comment genus
                type
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  NullArgument - ``resource_id`` or ``comment_genus_type``
                is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_by_genus_type_for_commentor_on_date(self, resource_id, comment_genus_type, from_, to):
        """Gets a list of all comments of the given genus type corresponding to a resource ``Id`` and effective during the entire given date range inclusive but not confined to the date range.

        arg:    resource_id (osid.id.Id): the ``Id`` of the resource
        arg:    comment_genus_type (osid.type.Type): the comment genus
                type
        arg:    from (osid.calendaring.DateTime): from date
        arg:    to (osid.calendaring.DateTime): to date
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  InvalidArgument - ``to`` is less than ``from``
        raise:  NullArgument - ``resource_id, comment_genus_type,
                from,`` or ``to`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_for_reference(self, reference_id):
        """Gets a list of comments corresponding to a reference ``Id``.

        arg:    reference_id (osid.id.Id): the ``Id`` of the reference
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  NullArgument - ``reference_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_for_reference_on_date(self, reference_id, from_, to):
        """Gets a list of all comments corresponding to a reference ``Id`` and effective during the entire given date range inclusive but not confined to the date range.

        arg:    reference_id (osid.id.Id): a reference ``Id``
        arg:    from (osid.calendaring.DateTime): from date
        arg:    to (osid.calendaring.DateTime): to date
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  InvalidArgument - ``to`` is less than ``from``
        raise:  NullArgument - ``reference_id, from,`` or ``to`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_by_genus_type_for_reference(self, reference_id, comment_genus_type):
        """Gets a list of comments of the given genus type corresponding to a reference ``Id``.

        arg:    reference_id (osid.id.Id): the ``Id`` of the reference
        arg:    comment_genus_type (osid.type.Type): the comment genus
                type
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  NullArgument - ``reference_id`` or
                ``comment_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_by_genus_type_for_reference_on_date(self, reference_id, comment_genus_type, from_, to):
        """Gets a list of all comments of the given genus type corresponding to a reference ``Id`` and effective during the entire given date range inclusive but not confined to the date range.

        arg:    reference_id (osid.id.Id): a reference ``Id``
        arg:    comment_genus_type (osid.type.Type): the comment genus
                type
        arg:    from (osid.calendaring.DateTime): from date
        arg:    to (osid.calendaring.DateTime): to date
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  InvalidArgument - ``to`` is less than ``from``
        raise:  NullArgument - ``reference_id, comment_genus_type,
                from,`` or ``to`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_for_commentor_and_reference(self, resource_id, reference_id):
        """Gets a list of comments corresponding to a resource and reference ``Id``.

        arg:    resource_id (osid.id.Id): the ``Id`` of the resource
        arg:    reference_id (osid.id.Id): the ``Id`` of the reference
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  NullArgument - ``resource_id`` or ``reference_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_for_commentor_and_reference_on_date(self, resource_id, reference_id, from_, to):
        """Gets a list of all comments corresponding to a resource and reference ``Id`` and effective during the entire given date range inclusive but not confined to the date range.

        arg:    resource_id (osid.id.Id): the ``Id`` of the resource
        arg:    reference_id (osid.id.Id): a reference ``Id``
        arg:    from (osid.calendaring.DateTime): from date
        arg:    to (osid.calendaring.DateTime): to date
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  InvalidArgument - ``to`` is less than ``from``
        raise:  NullArgument - ``resource_id, reference_id, from,`` or
                ``to`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_by_genus_type_for_commentor_and_reference(self, resource_id, reference_id, comment_genus_type):
        """Gets a list of comments of the given genus type corresponding to a resource and reference ``Id``.

        arg:    resource_id (osid.id.Id): the ``Id`` of the resource
        arg:    reference_id (osid.id.Id): the ``Id`` of the reference
        arg:    comment_genus_type (osid.type.Type): the comment genus
                type
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  NullArgument - ``resource_id, reference_id`` or
                ``comment_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_comments_by_genus_type_for_commentor_and_reference_on_date(self, resource_id, reference_id, comment_genus_type, from_, to):
        """Gets a list of all comments corresponding to a resource and reference ``Id`` and effective during the entire given date range inclusive but not confined to the date range.

        arg:    resource_id (osid.id.Id): the ``Id`` of the resource
        arg:    reference_id (osid.id.Id): a reference ``Id``
        arg:    comment_genus_type (osid.type.Type): the comment genus
                type
        arg:    from (osid.calendaring.DateTime): from date
        arg:    to (osid.calendaring.DateTime): to date
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  InvalidArgument - ``to`` is less than ``from``
        raise:  NullArgument - ``resource_id, reference_id,
                comment_genus_type, from,`` or ``to`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_comments(self):
        """Gets all comments.

        return: (osid.commenting.CommentList) - a list of comments
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    comments = property(fget=get_comments)


class CommentQuerySession(abc_commenting_sessions.CommentQuerySession, osid_sessions.OsidSession):
    """This session provides methods for searching ``Comment`` objects.

    The search query is constructed using the ``CommentQuery``. The book
    record ``Type`` also specifies the record for the book query.

    Comments may have a query record indicated by their respective
    record types. The query record is accessed via the ``CommentQuery``.
    The returns in this session may not be cast directly to these
    interfaces.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_book_id(self):
        """Gets the ``Book``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Book Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    book_id = property(fget=get_book_id)

    def get_book(self):
        """Gets the ``Book`` associated with this session.

        return: (osid.commenting.Book) - the book
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    book = property(fget=get_book)

    def can_search_comments(self):
        """Tests if this user can perform comment searches.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may not wish to offer search
        operations to unauthorized users.

        return: (boolean) - ``false`` if search methods are not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_federated_book_view(self):
        """Federates the view for methods in this session.

        A federated view will include comments in books which are
        children of this book in the book hierarchy.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_isolated_book_view(self):
        """Isolates the view for methods in this session.

        An isolated view restricts searches to this book only.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def get_comment_query(self):
        """Gets a comment query.

        return: (osid.commenting.CommentQuery) - the comment query
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    comment_query = property(fget=get_comment_query)

    @utilities.arguments_not_none
    def get_comments_by_query(self, comment_query):
        """Gets a list of comments matching the given search.

        arg:    comment_query (osid.commenting.CommentQuery): the search
                query array
        return: (osid.commenting.CommentList) - the returned
                ``CommentList``
        raise:  NullArgument - ``comment_query`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``comment_query`` is not of this service
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class CommentAdminSession(abc_commenting_sessions.CommentAdminSession, osid_sessions.OsidSession):
    """This session creates, updates, and deletes ``Comments``.

    The data for create and update is provided by the consumer via the
    form object. ``OsidForms`` are requested for each create or update
    and may not be reused.

    Create and update operations differ in their usage. To create a
    ``Comment,`` a ``CommentForm`` is requested using
    ``get_comment_form_for_create()`` specifying the desired
    relationship peers and record ``Types`` or none if no record
    ``Types`` are needed. The returned ``CommentForm`` will indicate
    that it is to be used with a create operation and can be used to
    examine metdata or validate data prior to creation. Once the
    ``CommentForm`` is submiited to a create operation, it cannot be
    reused with another create operation unless the first operation was
    unsuccessful. Each ``CommentForm`` corresponds to an attempted
    transaction.

    For updates, ``CommentForms`` are requested to the ``Comment``
    ``Id`` that is to be updated using ``getCommentFormForUpdate()``.
    Similarly, the ``CommentForm`` has metadata about the data that can
    be updated and it can perform validation before submitting the
    update. The ``CommentForm`` can only be used once for a successful
    update and cannot be reused.

    The delete operations delete ``Comments``. To unmap a ``Comment``
    from the current ``Book,`` the ``CommentBookAssignmentSession``
    should be used. These delete operations attempt to remove the
    ``Comment`` itself thus removing it from all known ``Book``
    catalogs.

    This session includes an ``Id`` aliasing mechanism to assign an
    external ``Id`` to an internally assigned Id.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_book_id(self):
        """Gets the ``Book``  ``Id`` associated with this session.

        return: (osid.id.Id) - the ``Book Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    book_id = property(fget=get_book_id)

    def get_book(self):
        """Gets the ``Book`` associated with this session.

        return: (osid.commenting.Book) - the book
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    book = property(fget=get_book)

    def can_create_comments(self):
        """Tests if this user can create comments.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known creating a
        ``Comment`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may not wish to offer
        create operations to unauthorized users.

        return: (boolean) - ``false`` if ``Comment`` creation is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_create_comment_with_record_types(self, comment_record_types):
        """Tests if this user can create a single ``Comment`` using the desired record types.

        While ``CommentingManager.getCommentRecordTypes()`` can be used
        to examine which records are supported, this method tests which
        record(s) are required for creating a specific ``Comment``.
        Providing an empty array tests if a ``Comment`` can be created
        with no records.

        arg:    comment_record_types (osid.type.Type[]): array of
                comment record types
        return: (boolean) - ``true`` if ``Comment`` creation using the
                specified record ``Types`` is supported, ``false``
                otherwise
        raise:  NullArgument - ``comment_record_types`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_comment_form_for_create(self, reference_id, comment_record_types):
        """Gets the comment form for creating new comments.

        A new form should be requested for each create transaction.

        arg:    reference_id (osid.id.Id): the ``Id`` for the reference
                object
        arg:    comment_record_types (osid.type.Type[]): array of
                comment record types
        return: (osid.commenting.CommentForm) - the comment form
        raise:  NullArgument - ``reference_id or comment_record_types``
                is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - unable to get form for requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def create_comment(self, comment_form):
        """Creates a new ``Comment``.

        arg:    comment_form (osid.commenting.CommentForm): the form for
                this ``Comment``
        return: (osid.commenting.Comment) - the new ``Comment``
        raise:  IllegalState - ``comment_form`` already used in a create
                transaction
        raise:  InvalidArgument - one or more of the form elements is
                invalid
        raise:  NullArgument - ``comment_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``comment_form`` did not originate from
                ``get_comment_form_for_create()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_update_comments(self):
        """Tests if this user can update comments.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known updating a
        ``Comment`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may not wish to offer
        update operations to unauthorized users.

        return: (boolean) - ``false`` if ``Comment`` modification is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_comment_form_for_update(self, comment_id):
        """Gets the comment form for updating an existing comment.

        A new comment form should be requested for each update
        transaction.

        arg:    comment_id (osid.id.Id): the ``Id`` of the ``Comment``
        return: (osid.commenting.CommentForm) - the comment form
        raise:  NotFound - ``comment_id`` is not found
        raise:  NullArgument - ``comment_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def update_comment(self, comment_form):
        """Updates an existing comment.

        arg:    comment_form (osid.commenting.CommentForm): the form
                containing the elements to be updated
        raise:  IllegalState - ``comment_form`` already used in an
                update transaction
        raise:  InvalidArgument - the form contains an invalid value
        raise:  NullArgument - ``comment_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``comment_form`` did not originate from
                ``get_comment_form_for_update()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_delete_comments(self):
        """Tests if this user can delete comments.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known deleting an
        ``Comment`` will result in a ``PermissionDenied``. This is
        intended as a hint to an application that may not wish to offer
        delete operations to unauthorized users.

        return: (boolean) - ``false`` if ``Comment`` deletion is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def delete_comment(self, comment_id):
        """Deletes a ``Comment``.

        arg:    comment_id (osid.id.Id): the ``Id`` of the ``Comment``
                to remove
        raise:  NotFound - ``comment_id`` not found
        raise:  NullArgument - ``comment_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_manage_comment_aliases(self):
        """Tests if this user can manage ``Id`` aliases for ``Comnents``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known changing an alias
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer alias
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Comment`` aliasing is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def alias_comment(self, comment_id, alias_id):
        """Adds an ``Id`` to a ``Comment`` for the purpose of creating compatibility.

        The primary ``Id`` of the ``Comment`` is determined by the
        provider. The new ``Id`` performs as an alias to the primary
        ``Id``. If the alias is a pointer to another comment, it is
        reassigned to the given comment ``Id``.

        arg:    comment_id (osid.id.Id): the ``Id`` of a ``Comment``
        arg:    alias_id (osid.id.Id): the alias ``Id``
        raise:  AlreadyExists - ``alias_id`` is already assigned
        raise:  NotFound - ``comment_id`` not found
        raise:  NullArgument - ``comment_id`` or ``alias_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class BookLookupSession(abc_commenting_sessions.BookLookupSession, osid_sessions.OsidSession):
    """This session provides methods for retrieving ``Book`` objects.

    The ``Book`` represents a collection of comments.

    This session defines views that offer differing behaviors when
    retrieving multiple objects.

      * comparative view: elements may be silently omitted or re-ordered
      * plenary view: provides a complete set or is an error condition


    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def can_lookup_books(self):
        """Tests if this user can perform ``Book`` lookups.

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

    def use_comparative_book_view(self):
        """The returns from the lookup methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_book_view(self):
        """A complete view of the ``Book`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_book(self, book_id):
        """Gets the ``Book`` specified by its ``Id``.

        In plenary mode, the exact ``Id`` is found or a ``NotFound``
        results. Otherwise, the returned ``Book`` may have a different
        ``Id`` than requested, such as the case where a duplicate ``Id``
        was assigned to a ``Book`` and retained for compatibility.

        arg:    book_id (osid.id.Id): ``Id`` of the ``Book``
        return: (osid.commenting.Book) - the book
        raise:  NotFound - ``book_id`` not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_books_by_ids(self, book_ids):
        """Gets a ``BookList`` corresponding to the given ``IdList``.

        In plenary mode, the returned list contains all of the books
        specified in the ``Id`` list, in the order of the list,
        including duplicates, or an error results if an ``Id`` in the
        supplied list is not found or inaccessible. Otherwise,
        inaccessible ``Books`` may be omitted from the list and may
        present the elements in any order including returning a unique
        set.

        arg:    book_ids (osid.id.IdList): the list of ``Ids`` to
                retrieve
        return: (osid.commenting.BookList) - the returned ``Book`` list
        raise:  NotFound - an ``Id was`` not found
        raise:  NullArgument - ``book_ids`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_books_by_genus_type(self, book_genus_type):
        """Gets a ``BookList`` corresponding to the given book genus ``Type`` which does not include books of genus types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known books or
        an error results. Otherwise, the returned list may contain only
        those books that are accessible through this session.

        arg:    book_genus_type (osid.type.Type): a book genus type
        return: (osid.commenting.BookList) - the returned ``Book`` list
        raise:  NullArgument - ``book_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_books_by_parent_genus_type(self, book_genus_type):
        """Gets a ``BookList`` corresponding to the given book genus ``Type`` and include any additional books with genus types derived from the specified ``Type``.

        In plenary mode, the returned list contains all known books or
        an error results. Otherwise, the returned list may contain only
        those books that are accessible through this session.

        arg:    book_genus_type (osid.type.Type): a book genus type
        return: (osid.commenting.BookList) - the returned ``Book`` list
        raise:  NullArgument - ``book_genus_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_books_by_record_type(self, book_record_type):
        """Gets a ``BookList`` containing the given book record ``Type``.

        In plenary mode, the returned list contains all known books or
        an error results. Otherwise, the returned list may contain only
        those books that are accessible through this session.

        arg:    book_record_type (osid.type.Type): a book record type
        return: (osid.commenting.BookList) - the returned ``Book`` list
        raise:  NullArgument - ``book_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def get_books_by_provider(self, resource_id):
        """Gets a ``BookList`` from the given provider ````.

        In plenary mode, the returned list contains all known books or
        an error results. Otherwise, the returned list may contain only
        those books that are accessible through this session.

        arg:    resource_id (osid.id.Id): a resource ``Id``
        return: (osid.commenting.BookList) - the returned ``Book`` list
        raise:  NullArgument - ``resource_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def get_books(self):
        """Gets all ``Books``.

        In plenary mode, the returned list contains all known books or
        an error results. Otherwise, the returned list may contain only
        those books that are accessible through this session.

        return: (osid.commenting.BookList) - a list of ``Books``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    books = property(fget=get_books)


class BookAdminSession(abc_commenting_sessions.BookAdminSession, osid_sessions.OsidSession):
    """This session creates, updates, and deletes ``Books``.

    The data for create and update is provided by the consumer via the
    form object. ``OsidForms`` are requested for each create or update
    and may not be reused.

    Create and update operations differ in their usage. To create a
    ``Book,`` a ``BookForm`` is requested using
    ``get_book_form_for_create()`` specifying the desired record
    ``Types`` or none if no record ``Types`` are needed. The returned
    ``BookForm`` will indicate that it is to be used with a create
    operation and can be used to examine metdata or validate data prior
    to creation. Once the ``BookForm`` is submiited to a create
    operation, it cannot be reused with another create operation unless
    the first operation was unsuccessful. Each ``BookForm`` corresponds
    to an attempted transaction.

    For updates, ``BookForms`` are requested to the ``Book``  ``Id``
    that is to be updated using ``getBookFormForUpdate()``. Similarly,
    the ``BookForm`` has metadata about the data that can be updated and
    it can perform validation before submitting the update. The
    ``BookForm`` can only be used once for a successful update and
    cannot be reused.

    The delete operations delete ``Books``.

    This session includes an ``Id`` aliasing mechanism to assign an
    external ``Id`` to an internally assigned Id.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def can_create_books(self):
        """Tests if this user can create ``Books``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known creating a ``Book``
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may not wish to offer create
        operations to unauthorized users.

        return: (boolean) - ``false`` if ``Book`` creation is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def can_create_book_with_record_types(self, book_record_types):
        """Tests if this user can create a single ``Book`` using the desired record types.

        While ``CommentingManager.getBookRecordTypes()`` can be used to
        examine which records are supported, this method tests which
        record(s) are required for creating a specific ``Book``.
        Providing an empty array tests if a ``Book`` can be created with
        no records.

        arg:    book_record_types (osid.type.Type[]): array of book
                record types
        return: (boolean) - ``true`` if ``Book`` creation using the
                specified record ``Types`` is supported, ``false``
                otherwise
        raise:  NullArgument - ``book_record_types`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_book_form_for_create(self, book_record_types):
        """Gets the book form for creating new books.

        A new form should be requested for each create transaction.

        arg:    book_record_types (osid.type.Type[]): array of book
                record types
        return: (osid.commenting.BookForm) - the book form
        raise:  NullArgument - ``book_record_types`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - unable to get form for requested record
                types
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def create_book(self, book_form):
        """Creates a new ``Book``.

        arg:    book_form (osid.commenting.BookForm): the form for this
                ``Book``
        return: (osid.commenting.Book) - the new ``Book``
        raise:  IllegalState - ``book_form`` already used in a create
                transaction
        raise:  InvalidArgument - one or more of the form elements is
                invalid
        raise:  NullArgument - ``book_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``book_form`` did not originte from
                ``get_book_form_for_create()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_update_books(self):
        """Tests if this user can update ``Books``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known updating a ``Book``
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may not wish to offer update
        operations to unauthorized users.

        return: (boolean) - ``false`` if ``Book`` modification is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def get_book_form_for_update(self, book_id):
        """Gets the book form for updating an existing book.

        A new book form should be requested for each update transaction.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        return: (osid.commenting.BookForm) - the book form
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def update_book(self, book_form):
        """Updates an existing book.

        arg:    book_form (osid.commenting.BookForm): the form
                containing the elements to be updated
        raise:  IllegalState - ``book_form`` already used in an update
                transaction
        raise:  InvalidArgument - the form contains an invalid value
        raise:  NullArgument - ``book_form`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``book_form`` did not originte from
                ``get_book_form_for_update()``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_delete_books(self):
        """Tests if this user can delete ``Books`` A return of true does not guarantee successful authorization.

        A return of false indicates that it is known deleting a ``Book``
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may not wish to offer delete
        operations to unauthorized users.

        return: (boolean) - ``false`` if ``Book`` deletion is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def delete_book(self, book_id):
        """Deletes a ``Book``.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book`` to
                remove
        raise:  NotFound - ``book_id`` not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def can_manage_book_aliases(self):
        """Tests if this user can manage ``Id`` aliases for ``Books``.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known changing an alias
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer alias
        operations to an unauthorized user.

        return: (boolean) - ``false`` if ``Book`` aliasing is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def alias_book(self, book_id, alias_id):
        """Adds an ``Id`` to a ``Book`` for the purpose of creating compatibility.

        The primary ``Id`` of the ``Book`` is determined by the
        provider. The new ``Id`` performs as an alias to the primary
        ``Id``. If the alias is a pointer to another book, it is
        reassigned to the given book ``Id``.

        arg:    book_id (osid.id.Id): the ``Id`` of a ``Book``
        arg:    alias_id (osid.id.Id): the alias ``Id``
        raise:  AlreadyExists - ``alias_id`` is already assigned
        raise:  NotFound - ``book_id`` not found
        raise:  NullArgument - ``book_id`` or ``alias_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class BookHierarchySession(abc_commenting_sessions.BookHierarchySession, osid_sessions.OsidSession):
    """This session defines methods for traversing a hierarchy of ``Book`` objects.

    Each node in the hierarchy is a unique ``Book``. The hierarchy may
    be traversed recursively to establish the tree structure through
    ``get_parent_books()`` and ``getChildBooks()``. To relate these
    ``Ids`` to another OSID, ``get_book_nodes()`` can be used for
    retrievals that can be used for bulk lookups in other OSIDs. Any
    ``Book`` available in the Commenting OSID is known to this hierarchy
    but does not appear in the hierarchy traversal until added as a root
    node or a child of another node.

    A user may not be authorized to traverse the entire hierarchy. Parts
    of the hierarchy may be made invisible through omission from the
    returns of ``get_parent_books()`` or ``get_child_books()`` in lieu
    of a ``PermissionDenied`` error that may disrupt the traversal
    through authorized pathways.

    This session defines views that offer differing behaviors when
    retrieving multiple objects.

      * comparative view: book elements may be silently omitted or re-
        ordered
      * plenary view: provides a complete set or is an error condition


    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_book_hierarchy_id(self):
        """Gets the hierarchy ``Id`` associated with this session.

        return: (osid.id.Id) - the hierarchy ``Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_hierarchy_id
        return self._hierarchy_session.get_hierarchy_id()

    book_hierarchy_id = property(fget=get_book_hierarchy_id)

    def get_book_hierarchy(self):
        """Gets the hierarchy associated with this session.

        return: (osid.hierarchy.Hierarchy) - the hierarchy associated
                with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_hierarchy
        return self._hierarchy_session.get_hierarchy()

    book_hierarchy = property(fget=get_book_hierarchy)

    def can_access_book_hierarchy(self):
        """Tests if this user can perform hierarchy queries.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known all methods in this
        session will result in a ``PermissionDenied``. This is intended
        as a hint to an application that may opt not to offer lookup
        operations.

        return: (boolean) - ``false`` if hierarchy traversal methods are
                not authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.can_access_bin_hierarchy
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    def use_comparative_book_view(self):
        """The returns from the book methods may omit or translate elements based on this session, such as authorization, and not result in an error.

        This view is used when greater interoperability is desired at
        the expense of precision.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def use_plenary_book_view(self):
        """A complete view of the ``Book`` returns is desired.

        Methods will return what is requested or result in an error.
        This view is used when greater precision is desired at the
        expense of interoperability.

        *compliance: mandatory -- This method is must be implemented.*

        """
        raise errors.Unimplemented()

    def get_root_book_ids(self):
        """Gets the root book ``Ids`` in this hierarchy.

        return: (osid.id.IdList) - the root book ``Ids``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_root_bin_ids
        return self._hierarchy_session.get_roots()

    root_book_ids = property(fget=get_root_book_ids)

    def get_root_books(self):
        """Gets the root books in the book hierarchy.

        A node with no parents is an orphan. While all book ``Ids`` are
        known to the hierarchy, an orphan does not appear in the
        hierarchy unless explicitly added as a root node or child of
        another node.

        return: (osid.commenting.BookList) - the root books
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method is must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_root_bins
        return BookLookupSession(
            self._proxy,
            self._runtime).get_books_by_ids(list(self.get_root_book_ids()))

    root_books = property(fget=get_root_books)

    @utilities.arguments_not_none
    def has_parent_books(self, book_id):
        """Tests if the ``Book`` has any parents.

        arg:    book_id (osid.id.Id): a book ``Id``
        return: (boolean) - ``true`` if the book has parents, f ``alse``
                otherwise
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.has_parent_bins
        return self._hierarchy_session.has_parents(id_=book_id)

    @utilities.arguments_not_none
    def is_parent_of_book(self, id_, book_id):
        """Tests if an ``Id`` is a direct parent of book.

        arg:    id (osid.id.Id): an ``Id``
        arg:    book_id (osid.id.Id): the ``Id`` of a book
        return: (boolean) - ``true`` if this ``id`` is a parent of
                ``book_id,`` f ``alse`` otherwise
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``id`` or ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: If ``id`` not found return ``false``.

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.is_parent_of_bin
        return self._hierarchy_session.is_parent(id_=book_id, parent_id=id_)

    @utilities.arguments_not_none
    def get_parent_book_ids(self, book_id):
        """Gets the parent ``Ids`` of the given book.

        arg:    book_id (osid.id.Id): a book ``Id``
        return: (osid.id.IdList) - the parent ``Ids`` of the book
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_parent_bin_ids
        return self._hierarchy_session.get_parents(id_=book_id)

    @utilities.arguments_not_none
    def get_parent_books(self, book_id):
        """Gets the parent books of the given ``id``.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book`` to
                query
        return: (osid.commenting.BookList) - the parent books of the
                ``id``
        raise:  NotFound - a ``Book`` identified by ``Id is`` not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_parent_bins
        return BookLookupSession(
            self._proxy,
            self._runtime).get_books_by_ids(
                list(self.get_parent_book_ids(book_id)))

    @utilities.arguments_not_none
    def is_ancestor_of_book(self, id_, book_id):
        """Tests if an ``Id`` is an ancestor of a book.

        arg:    id (osid.id.Id): an ``Id``
        arg:    book_id (osid.id.Id): the ``Id`` of a book
        return: (boolean) - ``tru`` e if this ``id`` is an ancestor of
                ``book_id,``  ``false`` otherwise
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``id`` or ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: If ``id`` not found return ``false``.

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.is_ancestor_of_bin
        return self._hierarchy_session.is_ancestor(id_=id_, ancestor_id=book_id)

    @utilities.arguments_not_none
    def has_child_books(self, book_id):
        """Tests if a book has any children.

        arg:    book_id (osid.id.Id): a book ``Id``
        return: (boolean) - ``true`` if the ``book_id`` has children,
                ``false`` otherwise
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.has_child_bins
        return self._hierarchy_session.has_children(id_=book_id)

    @utilities.arguments_not_none
    def is_child_of_book(self, id_, book_id):
        """Tests if a book is a direct child of another.

        arg:    id (osid.id.Id): an ``Id``
        arg:    book_id (osid.id.Id): the ``Id`` of a book
        return: (boolean) - ``true`` if the ``id`` is a child of
                ``book_id,``  ``false`` otherwise
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``id`` or ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: If ``id`` not found return ``false``.

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.is_child_of_bin
        return self._hierarchy_session.is_child(id_=book_id, child_id=id_)

    @utilities.arguments_not_none
    def get_child_book_ids(self, book_id):
        """Gets the child ``Ids`` of the given book.

        arg:    book_id (osid.id.Id): the ``Id`` to query
        return: (osid.id.IdList) - the children of the book
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_child_bin_ids
        return self._hierarchy_session.get_children(id_=book_id)

    @utilities.arguments_not_none
    def get_child_books(self, book_id):
        """Gets the child books of the given ``id``.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book`` to
                query
        return: (osid.commenting.BookList) - the child books of the
                ``id``
        raise:  NotFound - a ``Book`` identified by ``Id is`` not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_child_bins
        return BookLookupSession(
            self._proxy,
            self._runtime).get_books_by_ids(
                list(self.get_child_book_ids(book_id)))

    @utilities.arguments_not_none
    def is_descendant_of_book(self, id_, book_id):
        """Tests if an ``Id`` is a descendant of a book.

        arg:    id (osid.id.Id): an ``Id``
        arg:    book_id (osid.id.Id): the ``Id`` of a book
        return: (boolean) - ``true`` if the ``id`` is a descendant of
                the ``book_id,``  ``false`` otherwise
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``id`` or ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*
        *implementation notes*: If ``id`` is not found return ``false``.

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.is_descendant_of_bin
        return self._hierarchy_session.is_descendant(id_=id_, descendant_id=book_id)

    @utilities.arguments_not_none
    def get_book_node_ids(self, book_id, ancestor_levels, descendant_levels, include_siblings):
        """Gets a portion of the hierarchy for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` to query
        arg:    ancestor_levels (cardinal): the maximum number of
                ancestor levels to include. A value of 0 returns no
                parents in the node.
        arg:    descendant_levels (cardinal): the maximum number of
                descendant levels to include. A value of 0 returns no
                children in the node.
        arg:    include_siblings (boolean): ``true`` to include the
                siblings of the given node, ``false`` to omit the
                siblings
        return: (osid.hierarchy.Node) - a book node
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_node_ids
        return self._hierarchy_session.get_nodes(
            id_=book_id,
            ancestor_levels=ancestor_levels,
            descendant_levels=descendant_levels,
            include_siblings=include_siblings)

    @utilities.arguments_not_none
    def get_book_nodes(self, book_id, ancestor_levels, descendant_levels, include_siblings):
        """Gets a portion of the hierarchy for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` to query
        arg:    ancestor_levels (cardinal): the maximum number of
                ancestor levels to include. A value of 0 returns no
                parents in the node.
        arg:    descendant_levels (cardinal): the maximum number of
                descendant levels to include. A value of 0 returns no
                children in the node.
        arg:    include_siblings (boolean): ``true`` to include the
                siblings of the given node, ``false`` to omit the
                siblings
        return: (osid.commenting.BookNode) - a book node
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_nodes
        return objects.BookNode(self.get_book_node_ids(
            book_id=book_id,
            ancestor_levels=ancestor_levels,
            descendant_levels=descendant_levels,
            include_siblings=include_siblings)._my_map, runtime=self._runtime, proxy=self._proxy)


class BookHierarchyDesignSession(abc_commenting_sessions.BookHierarchyDesignSession, osid_sessions.OsidSession):
    """This session manages a hierarchy of books.

    Books may be organized into a hierarchy for organizing or
    federating. A parent ``Book`` includes all of the comments of its
    children such that a single root node contains all of the comments
    of the federation.

    """

    def __init__(self, proxy=None, runtime=None, **kwargs):
        OsidSession.__init__(self)
        OsidSession._init_proxy_and_runtime(proxy=proxy, runtime=runtime)
        self._kwargs = kwargs

    def get_book_hierarchy_id(self):
        """Gets the hierarchy ``Id`` associated with this session.

        return: (osid.id.Id) - the hierarchy ``Id`` associated with this
                session
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_hierarchy_id
        return self._hierarchy_session.get_hierarchy_id()

    book_hierarchy_id = property(fget=get_book_hierarchy_id)

    def get_book_hierarchy(self):
        """Gets the hierarchy associated with this session.

        return: (osid.hierarchy.Hierarchy) - the hierarchy associated
                with this session
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchySession.get_bin_hierarchy
        return self._hierarchy_session.get_hierarchy()

    book_hierarchy = property(fget=get_book_hierarchy)

    def can_modify_book_hierarchy(self):
        """Tests if this user can change the hierarchy.

        A return of true does not guarantee successful authorization. A
        return of false indicates that it is known performing any update
        will result in a ``PermissionDenied``. This is intended as a
        hint to an application that may opt not to offer these
        operations to an unauthorized user.

        return: (boolean) - ``false`` if changing this hierarchy is not
                authorized, ``true`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        # NOTE: It is expected that real authentication hints will be
        # handled in a service adapter above the pay grade of this impl.
        return True

    @utilities.arguments_not_none
    def add_root_book(self, book_id):
        """Adds a root book.

        arg:    book_id (osid.id.Id): the ``Id`` of a book
        raise:  AlreadyExists - ``book_id`` is already in hierarchy
        raise:  NotFound - ``book_id`` is not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchyDesignSession.add_root_bin_template
        return self._hierarchy_session.add_root(id_=book_id)

    @utilities.arguments_not_none
    def remove_root_book(self, book_id):
        """Removes a root book.

        arg:    book_id (osid.id.Id): the ``Id`` of a book
        raise:  NotFound - ``book_id`` is not a root
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchyDesignSession.remove_root_bin_template
        return self._hierarchy_session.remove_root(id_=book_id)

    @utilities.arguments_not_none
    def add_child_book(self, book_id, child_id):
        """Adds a child to a book.

        arg:    book_id (osid.id.Id): the ``Id`` of a book
        arg:    child_id (osid.id.Id): the ``Id`` of the new child
        raise:  AlreadyExists - ``book_id`` is already a parent of
                ``child_id``
        raise:  NotFound - ``book_id`` or ``child_id`` not found
        raise:  NullArgument - ``book_id`` or ``child_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchyDesignSession.add_child_bin_template
        return self._hierarchy_session.add_child(id_=book_id, child_id=child_id)

    @utilities.arguments_not_none
    def remove_child_book(self, book_id, child_id):
        """Removes a child from a book.

        arg:    book_id (osid.id.Id): the ``Id`` of a book
        arg:    child_id (osid.id.Id): the ``Id`` of the new child
        raise:  NotFound - ``book_id`` not a parent of ``child_id``
        raise:  NullArgument - ``book_id`` or ``child_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchyDesignSession.remove_child_bin_template
        return self._hierarchy_session.remove_child(id_=book_id, child_id=child_id)

    @utilities.arguments_not_none
    def remove_child_books(self, book_id):
        """Removes all children from a book.

        arg:    book_id (osid.id.Id): the ``Id`` of a book
        raise:  NotFound - ``book_id`` not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceHierarchyDesignSession.remove_child_bin_template
        return self._hierarchy_session.remove_children(id_=book_id)



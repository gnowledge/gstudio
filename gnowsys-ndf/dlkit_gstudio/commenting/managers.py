"""GStudio implementations of commenting managers."""

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
from dlkit.manager_impls.commenting import managers as commenting_managers




class CommentingProfile(osid_managers.OsidProfile, commenting_managers.CommentingProfile):
    """The commenting profile describes the interoperability among commenting services."""

    def supports_visible_federation(self):
        """Tests if any book federation is exposed.

        Federation is exposed when a specific book may be identified,
        selected and used to create a lookup or admin session.
        Federation is not exposed when a set of books appears as a
        single book.

        return: (boolean) - ``true`` if visible federation is supported,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_comment_lookup(self):
        """Tests for the availability of a comment lookup service.

        return: (boolean) - ``true`` if comment lookup is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_rating_lookup(self):
        """Tests for the availability of a rating lookup service.

        return: (boolean) - ``true`` if rating lookup is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_comment_query(self):
        """Tests if querying comments is available.

        return: (boolean) - ``true`` if comment query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_comment_search(self):
        """Tests if searching for comments is available.

        return: (boolean) - ``true`` if comment search is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_comment_admin(self):
        """Tests if managing comments is available.

        return: (boolean) - ``true`` if comment admin is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_comment_notification(self):
        """Tests if comment notification is available.

        return: (boolean) - ``true`` if comment notification is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_comment_book(self):
        """Tests if a comment to book lookup session is available.

        return: (boolean) - ``true`` if comment book lookup session is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_comment_book_assignment(self):
        """Tests if a comment to book assignment session is available.

        return: (boolean) - ``true`` if comment book assignment is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_comment_smart_book(self):
        """Tests if a comment smart booking session is available.

        return: (boolean) - ``true`` if comment smart booking is
                supported, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_book_lookup(self):
        """Tests for the availability of an book lookup service.

        return: (boolean) - ``true`` if book lookup is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_book_query(self):
        """Tests if querying books is available.

        return: (boolean) - ``true`` if book query is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_book_search(self):
        """Tests if searching for books is available.

        return: (boolean) - ``true`` if book search is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_book_admin(self):
        """Tests for the availability of a book administrative service for creating and deleting books.

        return: (boolean) - ``true`` if book administration is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_book_notification(self):
        """Tests for the availability of a book notification service.

        return: (boolean) - ``true`` if book notification is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented in all
        providers.*

        """
        return False # Change to True when implemented.

    def supports_book_hierarchy(self):
        """Tests for the availability of a book hierarchy traversal service.

        return: (boolean) - ``true`` if book hierarchy traversal is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return False # Change to True when implemented.

    def supports_book_hierarchy_design(self):
        """Tests for the availability of a book hierarchy design service.

        return: (boolean) - ``true`` if book hierarchy design is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented in all
        providers.*

        """
        return False # Change to True when implemented.

    def supports_commenting_batch(self):
        """Tests for the availability of a commenting batch service.

        return: (boolean) - ``true`` if commenting batch service is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented in all
        providers.*

        """
        return False # Change to True when implemented.

    def get_comment_record_types(self):
        """Gets the supported ``Comment`` record types.

        return: (osid.type.TypeList) - a list containing the supported
                comment record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('COMMENT_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    comment_record_types = property(fget=get_comment_record_types)

    @utilities.arguments_not_none
    def supports_comment_record_type(self, comment_record_type):
        """Tests if the given ``Comment`` record type is supported.

        arg:    comment_record_type (osid.type.Type): a ``Type``
                indicating a ``Comment`` record type
        return: (boolean) - ``true`` if the given ``Type`` is supported,
                ``false`` otherwise
        raise:  NullArgument - ``comment_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('COMMENT_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (comment_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    comment_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    comment_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_comment_search_record_types(self):
        """Gets the supported comment search record types.

        return: (osid.type.TypeList) - a list containing the supported
                comment search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('COMMENT_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    comment_search_record_types = property(fget=get_comment_search_record_types)

    @utilities.arguments_not_none
    def supports_comment_search_record_type(self, comment_search_record_type):
        """Tests if the given comment search record type is supported.

        arg:    comment_search_record_type (osid.type.Type): a ``Type``
                indicating a comment record type
        return: (boolean) - ``true`` if the given ``Type`` is supported,
                ``false`` otherwise
        raise:  NullArgument - ``comment_search_record_type`` is
                ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('COMMENT_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (comment_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    comment_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    comment_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_book_record_types(self):
        """Gets the supported ``Book`` record types.

        return: (osid.type.TypeList) - a list containing the supported
                book record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('BOOK_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    book_record_types = property(fget=get_book_record_types)

    @utilities.arguments_not_none
    def supports_book_record_type(self, book_record_type):
        """Tests if the given ``Book`` record type is supported.

        arg:    book_record_type (osid.type.Type): a ``Type`` indicating
                a ``Book`` record type
        return: (boolean) - ``true`` if the given ``Type`` is supported,
                ``false`` otherwise
        raise:  NullArgument - ``book_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('BOOK_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (book_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    book_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    book_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports

    def get_book_search_record_types(self):
        """Gets the supported book search record types.

        return: (osid.type.TypeList) - a list containing the supported
                book search record types
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.get_resource_record_types_template
        record_type_maps = get_registry('BOOK_SEARCH_RECORD_TYPES', self._runtime)
        record_types = []
        for record_type_map in record_type_maps:
            record_types.append(Type(**record_type_maps[record_type_map]))
        return TypeList(record_types)

    book_search_record_types = property(fget=get_book_search_record_types)

    @utilities.arguments_not_none
    def supports_book_search_record_type(self, book_search_record_type):
        """Tests if the given book search record type is supported.

        arg:    book_search_record_type (osid.type.Type): a ``Type``
                indicating a book record type
        return: (boolean) - ``true`` if the given ``Type`` is supported,
                ``false`` otherwise
        raise:  NullArgument - ``book_search_record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for
        # osid.resource.ResourceProfile.supports_resource_record_type_template
        record_type_maps = get_registry('BOOK_SEARCH_RECORD_TYPES', self._runtime)
        supports = False
        for record_type_map in record_type_maps:
            if (book_search_record_type.get_authority() == record_type_maps[record_type_map]['authority'] and
                    book_search_record_type.get_identifier_namespace() == record_type_maps[record_type_map]['namespace'] and
                    book_search_record_type.get_identifier() == record_type_maps[record_type_map]['identifier']):
                supports = True
        return supports


class CommentingManager(osid_managers.OsidManager, CommentingProfile, commenting_managers.CommentingManager):
    """The commenting manager provides access to commenting sessions and provides interoperability tests for various aspects of this service.

    The sessions included in this manager are:

      * ``CommentLookupSession:`` a session to lookup comments
      * ``RatingLookupSession:`` a session to lookup comments
      * ``CommentQuerySession:`` a session to query comments
      * ``CommentSearchSession:`` a session to search comments
      * ``CommentAdminSession:`` a session to manage comments
      * ``CommentNotificationSession:`` a session to subscribe to
        notifications of comment changes
      * ``CommentBookSession:`` a session for looking up comment and
        book mappings
      * ``CommentBookAssignmentSession:`` a session for managing comment
        and book mappings
      * ``CommentSmartBookSession:`` a session to manage dynamic comment
        books
      * ``BookLookupSession:`` a session to retrieve books
      * ``BookQuerySession:`` a session to query books
      * ``BookSearchSession:`` a session to search for books
      * ``BookAdminSession:`` a session to create, update and delete
        books
      * ``BookNotificationSession:`` a session to receive notifications
        for changes in books
      * ``BookHierarchyTraversalSession:`` a session to traverse
        hierarchies of books
      * ``BookHierarchyDesignSession:`` a session to manage hierarchies
        of books


    The commenting manager also provides a profile for determing the
    supported search types supported by this service.

    """

    def __init__(self):
        osid_managers.OsidManager.__init__(self)

    def get_comment_lookup_session(self):
        """Gets the ``OsidSession`` associated with the comment lookup service.

        return: (osid.commenting.CommentLookupSession) - a
                ``CommentLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_lookup()`` is ``true``.*

        """
        if not self.supports_comment_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentLookupSession(runtime=self._runtime)

    comment_lookup_session = property(fget=get_comment_lookup_session)

    @utilities.arguments_not_none
    def get_comment_lookup_session_for_book(self, book_id):
        """Gets the ``OsidSession`` associated with the comment lookup service for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        return: (osid.commenting.CommentLookupSession) - a
                ``CommentLookupSession``
        raise:  NotFound - no ``Book`` found by the given ``Id``
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_lookup()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_comment_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CommentLookupSession(book_id, self._runtime)

    def get_rating_lookup_session(self):
        """Gets the ``OsidSession`` associated with the rating lookup service.

        return: (osid.commenting.RatingLookupSession) - a
                ``RatingLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_rating_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_rating_lookup()`` is ``true``.*

        """
        if not self.supports_rating_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RatingLookupSession(runtime=self._runtime)

    rating_lookup_session = property(fget=get_rating_lookup_session)

    @utilities.arguments_not_none
    def get_rating_lookup_session_for_book(self, book_id):
        """Gets the ``OsidSession`` associated with the rating lookup service for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        return: (osid.commenting.RatingLookupSession) - a
                ``RatingLookupSession``
        raise:  NotFound - no ``Book`` found by the given ``Id``
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_rating_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_rating_lookup()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_rating_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.RatingLookupSession(book_id, self._runtime)

    def get_comment_query_session(self):
        """Gets the ``OsidSession`` associated with the comment query service.

        return: (osid.commenting.CommentQuerySession) - a
                ``CommentQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_query()`` is ``true``.*

        """
        if not self.supports_comment_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentQuerySession(runtime=self._runtime)

    comment_query_session = property(fget=get_comment_query_session)

    @utilities.arguments_not_none
    def get_comment_query_session_for_book(self, book_id):
        """Gets the ``OsidSession`` associated with the comment query service for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        return: (osid.commenting.CommentQuerySession) - a
                ``CommentQuerySession``
        raise:  NotFound - no ``Book`` found by the given ``Id``
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_query()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_comment_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CommentQuerySession(book_id, self._runtime)

    def get_comment_search_session(self):
        """Gets the ``OsidSession`` associated with the comment search service.

        return: (osid.commenting.CommentSearchSession) - a
                ``CommentSearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_search()`` is ``true``.*

        """
        if not self.supports_comment_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentSearchSession(runtime=self._runtime)

    comment_search_session = property(fget=get_comment_search_session)

    @utilities.arguments_not_none
    def get_comment_search_session_for_book(self, book_id):
        """Gets the ``OsidSession`` associated with the comment search service for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        return: (osid.commenting.CommentSearchSession) - a
                ``CommentSearchSession``
        raise:  NotFound - no ``Book`` found by the given ``Id``
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_search()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_comment_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CommentSearchSession(book_id, self._runtime)

    def get_comment_admin_session(self):
        """Gets the ``OsidSession`` associated with the comment administration service.

        return: (osid.commenting.CommentAdminSession) - a
                ``CommentAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_admin()`` is ``true``.*

        """
        if not self.supports_comment_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentAdminSession(runtime=self._runtime)

    comment_admin_session = property(fget=get_comment_admin_session)

    @utilities.arguments_not_none
    def get_comment_admin_session_for_book(self, book_id):
        """Gets the ``OsidSession`` associated with the comment administration service for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        return: (osid.commenting.CommentAdminSession) - a
                ``CommentAdminSession``
        raise:  NotFound - no ``Book`` found by the given ``Id``
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_admin()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_comment_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CommentAdminSession(book_id, self._runtime)

    @utilities.arguments_not_none
    def get_comment_notification_session(self, comment_receiver):
        """Gets the ``OsidSession`` associated with the comment notification service.

        arg:    comment_receiver (osid.commenting.CommentReceiver): the
                receiver
        return: (osid.commenting.CommentNotificationSession) - a
                ``CommentNotificationSession``
        raise:  NullArgument - ``comment_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_notification()`` is ``true``.*

        """
        if not self.supports_comment_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentNotificationSession(runtime=self._runtime, receiver=comment_receiver)

    @utilities.arguments_not_none
    def get_comment_notification_session_for_book(self, comment_receiver, book_id):
        """Gets the ``OsidSession`` associated with the comment notification service for the given book.

        arg:    comment_receiver (osid.commenting.CommentReceiver): the
                receiver
        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        return: (osid.commenting.CommentNotificationSession) - a
                ``CommentNotificationSession``
        raise:  NotFound - no ``Book`` found by the given ``Id``
        raise:  NullArgument - ``comment_receiver`` or ``book_id`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_notification()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_comment_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CommentNotificationSession(book_id, runtime=self._runtime, receiver=comment_receiver)

    def get_comment_book_session(self):
        """Gets the session for retrieving comment to book mappings.

        return: (osid.commenting.CommentBookSession) - a
                ``CommentBookSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_book()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_book()`` is ``true``.*

        """
        if not self.supports_comment_book():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentBookSession(runtime=self._runtime)

    comment_book_session = property(fget=get_comment_book_session)

    def get_comment_book_assignment_session(self):
        """Gets the session for assigning comment to book mappings.

        return: (osid.commenting.CommentBookAssignmentSession) - a
                ``CommentBookAssignmentSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_book_assignment()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_book_assignment()`` is ``true``.*

        """
        if not self.supports_comment_book_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentBookAssignmentSession(runtime=self._runtime)

    comment_book_assignment_session = property(fget=get_comment_book_assignment_session)

    @utilities.arguments_not_none
    def get_comment_smart_book_session(self, book_id):
        """Gets the session associated with the comment smart book for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of the book
        return: (osid.commenting.CommentSmartBookSession) - a
                ``CommentSmartBookSession``
        raise:  NotFound - ``book_id`` not found
        raise:  NullArgument - ``book_id`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_smart_book()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_smart_book()`` is ``true``.*

        """
        raise errors.Unimplemented()

    def get_book_lookup_session(self):
        """Gets the ``OsidSession`` associated with the book lookup service.

        return: (osid.commenting.BookLookupSession) - a
                ``BookLookupSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_lookup()`` is ``true``.*

        """
        if not self.supports_book_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookLookupSession(runtime=self._runtime)

    book_lookup_session = property(fget=get_book_lookup_session)

    def get_book_query_session(self):
        """Gets the ``OsidSession`` associated with the book query service.

        return: (osid.commenting.BookQuerySession) - a
                ``BookQuerySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_query()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_query()`` is ``true``.*

        """
        if not self.supports_book_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookQuerySession(runtime=self._runtime)

    book_query_session = property(fget=get_book_query_session)

    def get_book_search_session(self):
        """Gets the ``OsidSession`` associated with the book search service.

        return: (osid.commenting.BookSearchSession) - a
                ``BookSearchSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_search()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_search()`` is ``true``.*

        """
        if not self.supports_book_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookSearchSession(runtime=self._runtime)

    book_search_session = property(fget=get_book_search_session)

    def get_book_admin_session(self):
        """Gets the ``OsidSession`` associated with the book administrative service.

        return: (osid.commenting.BookAdminSession) - a
                ``BookAdminSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_admin()`` is ``true``.*

        """
        if not self.supports_book_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookAdminSession(runtime=self._runtime)

    book_admin_session = property(fget=get_book_admin_session)

    @utilities.arguments_not_none
    def get_book_notification_session(self, book_receiver):
        """Gets the ``OsidSession`` associated with the book notification service.

        arg:    book_receiver (osid.commenting.BookReceiver): the
                receiver
        return: (osid.commenting.BookNotificationSession) - a
                ``BookNotificationSession``
        raise:  NullArgument - ``book_receiver`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_notification()`` is ``true``.*

        """
        if not self.supports_book_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookNotificationSession(runtime=self._runtime, receiver=book_receiver)

    def get_book_hierarchy_session(self):
        """Gets the ``OsidSession`` associated with the book hierarchy service.

        return: (osid.commenting.BookHierarchySession) - a
                ``BookHierarchySession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_hierarchy()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_hierarchy()`` is ``true``.*

        """
        if not self.supports_book_hierarchy():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookHierarchySession(runtime=self._runtime)

    book_hierarchy_session = property(fget=get_book_hierarchy_session)

    def get_book_hierarchy_design_session(self):
        """Gets the ``OsidSession`` associated with the book hierarchy design service.

        return: (osid.commenting.BookHierarchyDesignSession) - a
                ``BookHierarchyDesignSession``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_hierarchy_design()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_hierarchy_design()`` is ``true``.*

        """
        if not self.supports_book_hierarchy_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookHierarchyDesignSession(runtime=self._runtime)

    book_hierarchy_design_session = property(fget=get_book_hierarchy_design_session)

    def get_commenting_batch_manager(self):
        """Gets a ``CommentingBatchManager``.

        return: (osid.commenting.batch.CommentingBatchManager) - a
                ``CommentingBatchManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_commenting_batch()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_commenting_batch()`` is ``true``.*

        """
        raise errors.Unimplemented()

    commenting_batch_manager = property(fget=get_commenting_batch_manager)


class CommentingProxyManager(osid_managers.OsidProxyManager, CommentingProfile, commenting_managers.CommentingProxyManager):
    """The commenting manager provides access to commenting sessions and provides interoperability tests for various aspects of this service.

    Methods in this manager accept a ``Proxy`` for passing information
    from a server environment. The sessions included in this manager
    are:

      * ``CommentLookupSession:`` a session to lookup comments
      * ``RatingLookupSession:`` a session to lookup comments
      * ``CommentQuerySession:`` a session to query comments
      * ``CommentSearchSession:`` a session to search comments
      * ``CommentAdminSession:`` a session to manage comments
      * ``CommentNotificationSession:`` a session to subscribe to
        notifications of comment changes
      * ``CommentBookSession:`` a session for looking up comment and
        book mappings
      * ``CommentBookAssignmentSession:`` a session for managing comment
        and book mappings
      * ``CommentSmartBookSession:`` a session to manage dynamic comment
        books
      * ``BookLookupSession:`` a session to retrieve books
      * ``BookQuerySession:`` a session to query books
      * ``BookSearchSession:`` a session to search for books
      * ``BookAdminSession:`` a session to create, update and delete
        books
      * ``BookNotificationSession:`` a session to receive notifications
        for changes in books
      * ``BookHierarchyTraversalSession:`` a session to traverse
        hierarchies of books
      * ``BookHierarchyDesignSession:`` a session to manage hierarchies
        of books


    The commenting manager also provides a profile for determing the
    supported search types supported by this service.

    """

    def __init__(self):
        osid_managers.OsidProxyManager.__init__(self)

    @utilities.arguments_not_none
    def get_comment_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the comment lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentLookupSession) - a
                ``CommentLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_lookup()`` is ``true``.*

        """
        if not self.supports_comment_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_comment_lookup_session_for_book(self, book_id, proxy):
        """Gets the ``OsidSession`` associated with the comment lookup service for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentLookupSession) - a
                ``CommentLookupSession``
        raise:  NotFound - no ``Book`` found by the given ``Id``
        raise:  NullArgument - ``book_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_lookup()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_comment_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CommentLookupSession(book_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_rating_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the rating lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.RatingLookupSession) - a
                ``RatingLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_rating_lookup()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_rating_lookup()`` is ``true``.*

        """
        if not self.supports_rating_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.RatingLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_rating_lookup_session_for_book(self, book_id, proxy):
        """Gets the ``OsidSession`` associated with the rating lookup service for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.RatingLookupSession) - a
                ``RatingLookupSession``
        raise:  NotFound - no ``Book`` found by the given ``Id``
        raise:  NullArgument - ``book_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_rating_lookup()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_rating_lookup()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_rating_lookup():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.RatingLookupSession(book_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_comment_query_session(self, proxy):
        """Gets the ``OsidSession`` associated with the comment query service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentQuerySession) - a
                ``CommentQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_query()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_query()`` is ``true``.*

        """
        if not self.supports_comment_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_comment_query_session_for_book(self, book_id, proxy):
        """Gets the ``OsidSession`` associated with the comment query service for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentQuerySession) - a
                ``CommentQuerySession``
        raise:  NotFound - no ``Comment`` found by the given ``Id``
        raise:  NullArgument - ``book_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_query()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_query()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_comment_query():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CommentQuerySession(book_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_comment_search_session(self, proxy):
        """Gets the ``OsidSession`` associated with the comment search service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentSearchSession) - a
                ``CommentSearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_search()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_search()`` is ``true``.*

        """
        if not self.supports_comment_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentSearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_comment_search_session_for_book(self, book_id, proxy):
        """Gets the ``OsidSession`` associated with the comment search service for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentSearchSession) - a
                ``CommentSearchSession``
        raise:  NotFound - no ``Comment`` found by the given ``Id``
        raise:  NullArgument - ``book_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_search()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_search()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_comment_search():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CommentSearchSession(book_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_comment_admin_session(self, proxy):
        """Gets the ``OsidSession`` associated with the comment administration service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentAdminSession) - a
                ``CommentAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_admin()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_admin()`` is ``true``.*

        """
        if not self.supports_comment_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_comment_admin_session_for_book(self, book_id, proxy):
        """Gets the ``OsidSession`` associated with the comment administration service for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentAdminSession) - a
                ``CommentAdminSession``
        raise:  NotFound - no ``Comment`` found by the given ``Id``
        raise:  NullArgument - ``book_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_admin()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_admin()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_comment_admin():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CommentAdminSession(book_id, proxy, self._runtime)

    @utilities.arguments_not_none
    def get_comment_notification_session(self, comment_receiver, proxy):
        """Gets the ``OsidSession`` associated with the comment notification service.

        arg:    comment_receiver (osid.commenting.CommentReceiver): the
                receiver
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentNotificationSession) - a
                ``CommentNotificationSession``
        raise:  NullArgument - ``comment_receiver`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_notification()`` is ``true``.*

        """
        if not self.supports_comment_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentNotificationSession(proxy=proxy, runtime=self._runtime, receiver=comment_receiver)

    @utilities.arguments_not_none
    def get_comment_notification_session_for_book(self, comment_receiver, book_id, proxy):
        """Gets the ``OsidSession`` associated with the comment notification service for the given book.

        arg:    comment_receiver (osid.commenting.CommentReceiver): the
                receiver
        arg:    book_id (osid.id.Id): the ``Id`` of the ``Book``
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentNotificationSession) - a
                ``CommentNotificationSession``
        raise:  NotFound - no ``Comment`` found by the given ``Id``
        raise:  NullArgument - ``comment_receiver, book_id`` or
                ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_notification()`` or
                ``supports_visible_federation()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_notification()`` and
        ``supports_visible_federation()`` are ``true``*

        """
        if not self.supports_comment_notification():
            raise errors.Unimplemented()
        ##
        # Also include check to see if the catalog Id is found otherwise raise errors.NotFound
        ##
        # pylint: disable=no-member
        return sessions.CommentNotificationSession(catalog_id=book_id, proxy=proxy, runtime=self._runtime, receiver=comment_receiver)

    @utilities.arguments_not_none
    def get_comment_book_session(self, proxy):
        """Gets the session for retrieving comment to book mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentBookSession) - a
                ``CommentBookSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_book()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_book()`` is ``true``.*

        """
        if not self.supports_comment_book():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentBookSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_comment_book_assignment_session(self, proxy):
        """Gets the session for assigning comment to book mappings.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentBookAssignmentSession) - a
                ``CommentBookAssignmentSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_book_assignment()``
                is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_book_assignment()`` is ``true``.*

        """
        if not self.supports_comment_book_assignment():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentBookAssignmentSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_comment_smart_book_session(self, book_id, proxy):
        """Gets the session for managing dynamic comment books for the given book.

        arg:    book_id (osid.id.Id): the ``Id`` of a book
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.CommentSmartBookSession) - ``book_id``
                not found
        raise:  NotFound - ``book_id`` or ``proxy`` is ``null``
        raise:  NullArgument - ``book_id`` or ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_comment_smart_book()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_comment_smart_book()`` is ``true``.*

        """
        if not self.supports_comment_smart_book():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.CommentSmartBookSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_book_lookup_session(self, proxy):
        """Gets the ``OsidSession`` associated with the book lookup service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.BookLookupSession) - a
                ``BookLookupSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_lookup()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_lookup()`` is ``true``.*

        """
        if not self.supports_book_lookup():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookLookupSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_book_query_session(self, proxy):
        """Gets the ``OsidSession`` associated with the book query service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.BookQuerySession) - a
                ``BookQuerySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_queryh()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_query()`` is ``true``.*

        """
        if not self.supports_book_query():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookQuerySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_book_search_session(self, proxy):
        """Gets the ``OsidSession`` associated with the book search service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.BookSearchSession) - a
                ``BookSearchSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_search()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_search()`` is ``true``.*

        """
        if not self.supports_book_search():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookSearchSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_book_admin_session(self, proxy):
        """Gets the ``OsidSession`` associated with the book administrative service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.BookAdminSession) - a
                ``BookAdminSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_admin()`` is ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_admin()`` is ``true``.*

        """
        if not self.supports_book_admin():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookAdminSession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_book_notification_session(self, book_receiver, proxy):
        """Gets the ``OsidSession`` associated with the book notification service.

        arg:    book_receiver (osid.commenting.BookReceiver): the
                receiver
        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.BookNotificationSession) - a
                ``BookNotificationSession``
        raise:  NullArgument - ``book_receiver`` or ``proxy`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_notification()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_notification()`` is ``true``.*

        """
        if not self.supports_book_notification():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookNotificationSession(proxy=proxy, runtime=self._runtime, receiver=book_receiver)

    @utilities.arguments_not_none
    def get_book_hierarchy_session(self, proxy):
        """Gets the ``OsidSession`` associated with the book hierarchy service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.BookHierarchySession) - a
                ``BookHierarchySession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_hierarchy()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_hierarchy()`` is ``true``.*

        """
        if not self.supports_book_hierarchy():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookHierarchySession(proxy=proxy, runtime=self._runtime)

    @utilities.arguments_not_none
    def get_book_hierarchy_design_session(self, proxy):
        """Gets the ``OsidSession`` associated with the book hierarchy design service.

        arg:    proxy (osid.proxy.Proxy): a proxy
        return: (osid.commenting.BookHierarchyDesignSession) - a
                ``BookHierarchyDesignSession``
        raise:  NullArgument - ``proxy`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_book_hierarchy_design()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_book_hierarchy_design()`` is ``true``.*

        """
        if not self.supports_book_hierarchy_design():
            raise errors.Unimplemented()
        # pylint: disable=no-member
        return sessions.BookHierarchyDesignSession(proxy=proxy, runtime=self._runtime)

    def get_commenting_batch_proxy_manager(self):
        """Gets a ``CommentingBatchProxyManager``.

        return: (osid.commenting.batch.CommentingBatchProxyManager) - a
                ``CommentingBatchProxyManager``
        raise:  OperationFailed - unable to complete request
        raise:  Unimplemented - ``supports_commenting_batch()`` is
                ``false``
        *compliance: optional -- This method must be implemented if
        ``supports_commenting_batch()`` is ``true``.*

        """
        raise errors.Unimplemented()

    commenting_batch_proxy_manager = property(fget=get_commenting_batch_proxy_manager)



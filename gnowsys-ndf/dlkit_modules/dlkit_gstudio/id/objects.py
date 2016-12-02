"""GStudio implementations of id objects."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.id import objects as abc_id_objects
from ..osid import objects as osid_objects
from ..primitives import Id
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.id.primitives import Id




class IdForm(abc_id_objects.IdForm, osid_objects.OsidForm):
    """This form provides a means of creating an ``Id``."""

    def get_authority_metadata(self):
        """Gets the metadata for the authority.

        return: (osid.Metadata) - metadata for the authority
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    authority_metadata = property(fget=get_authority_metadata)

    @utilities.arguments_not_none
    def set_authority(self, authority):
        """Sets the authority.

        arg:    authority (string): the authority
        raise:  InvalidArgument - ``authority`` is invalid
        raise:  NoAccess - ``authority`` cannot be modified
        raise:  NullArgument - ``authority`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_authority(self):
        """Clears the authority.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    authority = property(fset=set_authority, fdel=clear_authority)

    def get_identifier_namespace_metadata(self):
        """Gets the metadata for the identifier namespace.

        return: (osid.Metadata) - metadata for the namespace
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    identifier_namespace_metadata = property(fget=get_identifier_namespace_metadata)

    @utilities.arguments_not_none
    def set_identifier_namespace(self, namespace):
        """Seta the identifier namespace.

        arg:    namespace (string): the namespace
        raise:  InvalidArgument - ``namespace`` is invalid
        raise:  NoAccess - ``namespace`` cannot be modified
        raise:  NullArgument - ``namespace`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_identifier_namespace(self):
        """Clears the identifier namespace.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    identifier_namespace = property(fset=set_identifier_namespace, fdel=clear_identifier_namespace)

    def get_identifier_prefix_metadata(self):
        """Gets the metadata for the identifier prefix.

        return: (osid.Metadata) - metadata for the prefix
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    identifier_prefix_metadata = property(fget=get_identifier_prefix_metadata)

    @utilities.arguments_not_none
    def set_identifier_prefix(self, prefix):
        """Seta the identifier prefix.

        An identifier will be generated with this prefix.

        arg:    prefix (string): the prefix
        raise:  InvalidArgument - ``prefix`` is invalid
        raise:  NoAccess - ``prefix`` cannot be modified
        raise:  NullArgument - ``prefix`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_identifier_prefix(self):
        """Clears the identifier prefix.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    identifier_prefix = property(fset=set_identifier_prefix, fdel=clear_identifier_prefix)

    def get_identifier_suffix_metadata(self):
        """Gets the metadata for the identifier suffix.

        return: (osid.Metadata) - metadata for the suffix
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    identifier_suffix_metadata = property(fget=get_identifier_suffix_metadata)

    @utilities.arguments_not_none
    def set_identifier_suffix(self, suffix):
        """Seta the identifier prefix.

        An identifier will be generated with this suffix.

        arg:    suffix (string): the suffix
        raise:  InvalidArgument - ``suffix`` is invalid
        raise:  NoAccess - ``suffix`` cannot be modified
        raise:  NullArgument - ``suffix`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_identifier_suffix(self):
        """Clears the identifier suffix.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    identifier_suffix = property(fset=set_identifier_suffix, fdel=clear_identifier_suffix)

    def get_identifier_metadata(self):
        """Gets the metadata for the identifier.

        return: (osid.Metadata) - metadata for the identifier
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    identifier_metadata = property(fget=get_identifier_metadata)

    @utilities.arguments_not_none
    def set_identifier(self, identifier):
        """Seta the identifier.

        arg:    identifier (string): the identifier
        raise:  InvalidArgument - ``identifier`` is invalid
        raise:  NoAccess - ``identifier`` cannot be modified
        raise:  NullArgument - ``identifier`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    def clear_identifier(self):
        """Clears the identifier.

        raise:  NoAccess - ``Metadata.isRequired()`` is ``true`` or
                ``Metadata.isReadOnly()`` is ``true``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    identifier = property(fset=set_identifier, fdel=clear_identifier)


class IdList(abc_id_objects.IdList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``IdList`` provides a means for accessing ``Id`` elements sequentially either one at a time or many at a time.

    Examples: while (il.hasNext()) { Id id = il.getNextId(); }

    or
      while (il.hasNext()) {
           Id[] ids = il.getNextIds(il.available());
      }



    """

    def get_next_id(self):
        """Gets the next ``Id`` in this list.

        return: (osid.id.Id) - the next ``Id`` in this list. The
                ``has_next()`` method should be used to test that a next
                ``Id`` is available before calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        try:
            next_item = self.next()
        except StopIteration:
            raise errors.IllegalState('no more elements available in this list')
        except: #Need to specify exceptions here
            raise errors.OperationFailed()
        else:
            return next_item

    def next(self):
        return self._get_next_object(Id)

    next_id = property(fget=get_next_id)

    @utilities.arguments_not_none
    def get_next_ids(self, n):
        """Gets the next set of ``Ids`` in this list.

        The specified amount must be less than or equal to the return
        from ``available()``.

        arg:    n (cardinal): the number of ``Id`` elements requested
                which must be less than or equal to ``available()``
        return: (osid.id.Id) - an array of ``Id`` elements.The length of
                the array is less than or equal to the number specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        # Implemented from template for osid.resource.ResourceList.get_next_resources
        return self._get_next_n(n)



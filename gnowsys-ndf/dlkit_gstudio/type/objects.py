"""GStudio implementations of type objects."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from dlkit.abstract_osid.type import objects as abc_type_objects
from ..osid import objects as osid_objects
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.id.primitives import Id




class TypeForm(abc_type_objects.TypeForm, osid_objects.OsidForm):
    """This form provides a means of updating various fields in the ``Type``.

    Note that the domain, authority and identifier are part of the
    ``Type`` identification, and as such not modifiable.

    """

    def __init__(self, type_=None, update=False):
        from ..osid.objects import OsidForm
        OsidForm.__init__(self)
        self._init_metadata()
        self._my_map = {}
        self._init_map()
        self._my_map['authority'] = type_.get_authority()
        self._my_map['namespace'] = type_.get_identifier_namespace()
        self._my_map['identifier'] = type_.get_identifier()
        self._my_map['displayName']['text'] = type_.get_display_name().get_text()
        self._my_map['displayLabel']['text'] = type_.get_display_label().get_text()
        self._my_map['description']['text'] = type_.get_description().get_text()
        self._my_map['domain']['text'] = type_.get_domain().get_text()
        self._for_update = update

    def _init_metadata(self):
        from . import mdata_conf
        from ..primitives import Id
        from ..osid.objects import OsidForm
        OsidForm._init_metadata(self)
        self._display_name_metadata = {
            'element_id': Id(authority = self._authority,
                             namespace = self._namespace,
                             identifier = 'display_name')}
        self._display_name_metadata.update(mdata_conf.display_name)
        self._display_label_metadata = {
            'element_id': Id(authority = self._authority,
                             namespace = self._namespace, 
                             identifier = 'description')}
        self._display_label_metadata.update(mdata_conf.display_label)
        self._description_metadata = {
            'element_id': Id(authority = self._authority,
                             namespace = self._namespace, 
                             identifier = 'description')}
        self._description_metadata.update(mdata_conf.description)
        self._domain_metadata = {
            'element_id': Id(authority = self._authority,
                             namespace = self._namespace, 
                             identifier = 'description')}
        self._domain_metadata.update(mdata_conf.domain)

    def _init_map(self):
        from . import profile
        self._my_map['displayName'] = self._display_name_metadata['default_string_values'][0]
        self._my_map['displayLabel'] = self._display_label_metadata['default_string_values'][0]
        self._my_map['description'] = self._description_metadata['default_string_values'][0]
        self._my_map['domain'] = self._domain_metadata['default_string_values'][0]

    def get_display_name_metadata(self):
        """Gets the metadata for the display name.

        return: (osid.Metadata) - metadata for the display name
        *compliance: mandatory -- This method must be implemented.*

        """
        from ..osid.metadata import Metadata
        return Metadata(**self._display_name_metadata)

    display_name_metadata = property(fget=get_display_name_metadata)

    @utilities.arguments_not_none
    def set_display_name(self, display_name):
        """Sets a display name.

        arg:    display_name (string): the new display name
        raise:  InvalidArgument - ``display_name`` is invalid
        raise:  NoAccess - ``display_name`` cannot be modified
        raise:  NullArgument - ``display_name`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.get_display_name_metadata().is_read_only():
            raise errors.NoAccess()
        if not self._is_valid_string(display_name, 
                                     self.get_display_name_metadata()):
            raise errors.InvalidArgument()
        self._my_map['displayName']['text'] = display_name

    def clear_display_name(self):
        """Clears the display name.

        raise:  NoAccess - ``display_name`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        if (self.get_display_name_metadata().is_read_only() or
            self.get_display_name_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['displayName'] = self._display_name_metadata['default_string_values'][0]

    display_name = property(fset=set_display_name, fdel=clear_display_name)

    def get_display_label_metadata(self):
        """Gets the metadata for the display label.

        return: (osid.Metadata) - metadata for the display label
        *compliance: mandatory -- This method must be implemented.*

        """
        from ..osid.metadata import Metadata
        return Metadata(**self._display_label_metadata)

    display_label_metadata = property(fget=get_display_label_metadata)

    @utilities.arguments_not_none
    def set_display_label(self, display_label):
        """Seta a display label.

        arg:    display_label (string): the new display label
        raise:  InvalidArgument - ``display_label`` is invalid
        raise:  NoAccess - ``display_label`` cannot be modified
        raise:  NullArgument - ``display_label`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.get_display_label_metadata().is_read_only():
            raise errors.NoAccess()
        if not self._is_valid_string(display_label, 
                                     self.get_display_label_metadata()):
            raise errors.InvalidArgument()
        self._my_map['displayLabel']['text'] = display_label

    def clear_display_label(self):
        """Clears the display label.

        raise:  NoAccess - ``display_label`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        if (self.get_display_label_metadata().is_read_only() or
            self.get_display_label_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['displayLabel'] = self._display_label_metadata['default_string_values'][0]

    display_label = property(fset=set_display_label, fdel=clear_display_label)

    def get_description_metadata(self):
        """Gets the metadata for the description.

        return: (osid.Metadata) - metadata for the description
        *compliance: mandatory -- This method must be implemented.*

        """
        from ..osid.metadata import Metadata
        return Metadata(**self._description_metadata)

    description_metadata = property(fget=get_description_metadata)

    @utilities.arguments_not_none
    def set_description(self, description):
        """Sets a description.

        arg:    description (string): the new description
        raise:  InvalidArgument - ``description`` is invalid
        raise:  NoAccess - ``description`` cannot be modified
        raise:  NullArgument - ``description`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.get_description_metadata().is_read_only():
            raise errors.NoAccess()
        if not self._is_valid_string(description, 
                                     self.get_description_metadata()):
            raise errors.InvalidArgument()
        self._my_map['description']['text'] = description

    def clear_description(self):
        """Clears the description.

        raise:  NoAccess - ``description`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        if (self.get_domain_metadata().is_read_only() or
            self.get_domain_metadata().is_required()):
            raise errors.NoAccess()
        self._my_map['domain'] = self._domain_metadata['default_string_values'][0]

    description = property(fset=set_description, fdel=clear_description)

    def get_domain_metadata(self):
        """Gets the metadata for the domain.

        return: (osid.Metadata) - metadata for the domain
        *compliance: mandatory -- This method must be implemented.*

        """
        from ..osid.metadata import Metadata
        return Metadata(**self._domain_metadata)

    domain_metadata = property(fget=get_domain_metadata)

    @utilities.arguments_not_none
    def set_domain(self, domain):
        """Sets a domain.

        arg:    domain (string): the new domain
        raise:  InvalidArgument - ``domain`` is invalid
        raise:  NoAccess - ``domain`` cannot be modified
        raise:  NullArgument - ``domain`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.get_domain_metadata().is_read_only():
            raise errors.NoAccess()
        if not self._is_valid_string(domain, 
                                     self.get_domain_metadata()):
            raise errors.InvalidArgument()
        self._my_map['domain']['text'] = domain

    def clear_domain(self):
        """Clears the domain.

        raise:  NoAccess - ``domain`` cannot be modified
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    domain = property(fset=set_domain, fdel=clear_domain)


class TypeList(abc_type_objects.TypeList, osid_objects.OsidList):
    """Like all ``OsidLists,``  ``TypeList`` provides a means for accessing ``Type`` elements sequentially either one at a time or many at a time.

    Examples: while (tl.hasNext()) { Type type = tl.getNextType(); }

    or
      while (tl.hasNext()) {
           Type[] types = tl.getNextTypes(tl.available());
      }



    """

    def get_next_type(self):
        """Gets the next ``Type`` in this list.

        return: (osid.type.Type) - the next ``Type`` in this list. The
                ``has_next()`` method should be used to test that a next
                ``Type`` is available before calling this method.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        return self.next()
            
    def next(self):
        from .primitives import Type
        return self._get_next_object(Type)

    next_type = property(fget=get_next_type)

    @utilities.arguments_not_none
    def get_next_types(self, n):
        """Gets the next set of ``Types`` in this list.

        The specified amount must be less than or equal to the return
        from ``available()``.

        arg:    n (cardinal): the number of ``Type`` elements requested
                which must be less than or equal to ``available()``
        return: (osid.type.Type) - an array of ``Type`` elements.The
                length of the array is less than or equal to the number
                specified.
        raise:  IllegalState - no more elements available in this list
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._get_next_n(n)



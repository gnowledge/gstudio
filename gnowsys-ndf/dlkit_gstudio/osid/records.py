"""GStudio implementations of osid records."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from dlkit.abstract_osid.osid import records as abc_osid_records




class OsidRecord(abc_osid_records.OsidRecord):
    """``OsidRecord`` is a top-level interface for all record objects.

    A record is an auxiliary interface that can be retrieved from an
    OSID object, query, form or search order that contains method
    definitions outside the core OSID specification. An OSID record
    interface specification is identified with a ``Type``.

    """

    @utilities.arguments_not_none
    def implements_record_type(self, record_type):
        """Tests if the given type is implemented by this record.

        Other types than that directly indicated by ``get_type()`` may
        be supported through an inheritance scheme where the given type
        specifies a record that is a parent interface of the interface
        specified by ``getType()``.

        arg:    record_type (osid.type.Type): a type
        return: (boolean) - ``true`` if the given record ``Type`` is
                implemented by this record, ``false`` otherwise
        raise:  NullArgument - ``record_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



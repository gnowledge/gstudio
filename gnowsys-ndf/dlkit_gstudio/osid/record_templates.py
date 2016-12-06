"""Not sure why this is here. Seems duplicated with osid.records. use that instead?"""

from dlkit.abstract_osid.osid import records as abc_osid_records


class OsidRecord(abc_osid_records.OsidRecord):
    """``OsidRecord`` is a top-level interface for all record objects.

    A record is an auxiliary interface that can be retrieved from an
    OSID object, query, form or search order that contains method
    definitions outside the core OSID specification. An OSID record
    interface specification is identified with a ``Type``.

    """

    def __init__(self):
        # This is set in implemented Records.  Should super __init__
        #self._implemented_record_type_identifiers = None
        pass

    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith('__'):
                yield attr

    def __getitem__(self, item):
        return getattr(self, item)

    def implements_record_type(self, record_type=None):
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
        return record_type.get_identifier() in self._implemented_record_type_identifiers



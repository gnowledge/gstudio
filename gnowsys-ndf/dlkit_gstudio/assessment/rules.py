"""GStudio implementations of assessment rules."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.assessment import rules as abc_assessment_rules
from ..osid import rules as osid_rules




class Response(abc_assessment_rules.Response, osid_rules.OsidCondition):
    """A response to an assessment item.

    This interface contains methods to set values in response to an
    assessmet item and mirrors the item record structure with the
    corresponding setters.

    """

    def get_item_id(self):
        """Gets the ``Id`` of the ``Item``.

        return: (osid.id.Id) - the assessment item ``Id``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    item_id = property(fget=get_item_id)

    def get_item(self):
        """Gets the ``Item``.

        return: (osid.assessment.Item) - the assessment item
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    item = property(fget=get_item)

    @utilities.arguments_not_none
    def get_response_record(self, item_record_type):
        """Gets the response record corresponding to the given ``Item`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``item_record_type`` may be the ``Type``
        returned in ``get_record_types()`` or any of its parents in a
        ``Type`` hierarchy where ``has_record_type(item_record_type)``
        is ``true`` .

        arg:    item_record_type (osid.type.Type): an item record type
        return: (osid.assessment.records.ResponseRecord) - the response
                record
        raise:  NullArgument - ``item_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(item_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()



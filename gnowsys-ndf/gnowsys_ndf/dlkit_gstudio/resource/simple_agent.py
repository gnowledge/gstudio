"""Simple Agent implementation for use by resource service"""

from dlkit.abstract_osid.osid import markers as abc_markers
from dlkit.abstract_osid.osid.objects import OsidObject as abcOsidObject
from dlkit.abstract_osid.authentication.objects import Agent as abcAgent
from dlkit.abstract_osid.osid import errors
from dlkit.primordium.locale.primitives import DisplayText
from dlkit.primordium.type.primitives import Type
from ..type.objects import TypeList
from .. import types
DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data('DEFAULT'))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data('DEFAULT'))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data('DEFAULT'))
DEFAULT_GENUS_TYPE = Type(**types.Genus().get_type_data('DEFAULT'))


class Identifiable(abc_markers.Identifiable):
    """Simple Identifiable"""

    def __init__(self, id_):
        self.id_ = id_

    def get_id():
        """Returns an Id"""
        return self.id_

    def is_current():
        """Immutable and always current"""
        return True


class Extensible(abc_markers.Extensible):
    """Simple Extensible"""

    def get_record_types():
        """None here"""
        return TypeList([])

    def has_record_type(record_type):
        """I said, none here!"""
        return False


class Browsable(abc_markers.Browsable):
    """Simple Browseable"""

    def get_properties(self):
        """Not required by customer"""
        raise errors.OperationFailed('oops, forgot to implement')

    def get_properties_by_record_type(record_type):
        """Not required by customer"""
        raise errors.OperationFailed('oops, forgot to implement')


class OsidObject(abcOsidObject, Identifiable, Extensible, Browsable):
    """Simple Identifiable"""

    def get_display_name():
        """Creates a display name"""
        return DisplayText(text = self.id_.get_identifier(),
                           language_type = DEFAULT_LANGUAGE_TYPE,
                           script_type = DEFAULT_SCRIPT_TYPE,
                           format_type = DEFAULT_FORMAT_TYPE,)

    def get_description():
        """Creates a description"""
        return DisplayText(text = 'Agent representing ' + str(self.id_),
                           language_type = DEFAULT_LANGUAGE_TYPE,
                           script_type = DEFAULT_SCRIPT_TYPE,
                           format_type = DEFAULT_FORMAT_TYPE,)

    def get_genus_type():
        """Returns the genus type"""
        return DEFAULT_GENUS_TYPE


class Agent(abcAgent, OsidObject):
    """An ``Agent`` represents an authenticatable identity.

    Like all OSID objects, an ``Agent`` is identified by its ``Id`` and
    any persisted references should use the ``Id``.

    """

    def __init__(self, agent_id):
        Identifiable.__init__(self, agent_id)

    def get_agent_record(self, agent_record_type):
        """Gets the agent record corresponding to the given ``Agent`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``agent_record_type`` may be the ``Type``
        returned in ``get_record_types()`` or any of its parents in a
        ``Type`` hierarchy where ``has_record_type(agent_record_type)``
        is ``true`` .

        :param agent_record_type: the type of the record to retrieve
        :type agent_record_type: ``osid.type.Type``
        :return: the agent record
        :rtype: ``osid.authentication.records.AgentRecord``
        :raise: ``NullArgument`` -- ``agent_record_type`` is ``null``
        :raise: ``OperationFailed`` -- unable to complete request
        :raise: ``Unsupported`` -- ``has_record_type(agent_record_type)`` is ``false``

        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unsupported()


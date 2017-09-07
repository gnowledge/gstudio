"""GStudio implementations of proxy rules."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from ...abstract_osid.proxy import rules as abc_proxy_rules
from ..osid import rules as osid_rules
from ..primitives import Id
from dlkit.abstract_osid.osid import errors




class Proxy(abc_proxy_rules.Proxy, osid_rules.OsidResult):
    """A ``Proxy`` is used to transfer external information from an application server into an OSID Provider."""

    def __init__(self,
                 authentication=None,
                 effective_agent_id=None,
                 effective_date=None,
                 effective_clock_rate=None,
                 locale=None,
                 format_type=None):
        self._authentication = authentication
        self._effective_agent_id = effective_agent_id
        self._effective_date = effective_date
        self._effective_clock_rate = effective_clock_rate
        self._locale = locale
        self._format_type = format_type

    def has_authentication(self):
        """Tests if an authentication is available.

        return: (boolean) - ``true`` if an ``Authentication`` is
                available, ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return bool(self._authentication)

    def get_authentication(self):
        """Gets the ``Authentication`` for this proxy.

        return: (osid.authentication.process.Authentication) - the
                authentication
        raise:  IllegalState - ``has_authentication()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.has_authentication():
            return self._authentication
        else:
            raise errors.IllegalState()

    authentication = property(fget=get_authentication)

    def has_effective_agent(self):
        """Tests if an effective agent is available.

        return: (boolean) - ``true`` if an effective agent is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return bool(self._effective_agent_id)

    def get_effective_agent_id(self):
        """Gets the effective ``Agent Id`` for this proxy.

        return: (osid.id.Id) - the effective agent ``Id``
        raise:  IllegalState - ``has_effective_agent()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.has_effective_agent():
            return self._effective_agent_id
        else:
            raise errors.IllegalState()

    effective_agent_id = property(fget=get_effective_agent_id)

    def get_effective_agent(self):
        """Gets the effective ``Agent`` for this proxy.

        return: (osid.authentication.Agent) - the effective agent
        raise:  IllegalState - ``has_effective_agent()`` is ``false``
        raise:  OperationFailed - unable to complete request
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented

    effective_agent = property(fget=get_effective_agent)

    def has_effective_date(self):
        """Tests if an effective date is available.

        return: (boolean) - ``true`` if an effective date is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return bool(self._authentication)

    def get_effective_date(self):
        """Gets the effective date.

        return: (timestamp) - the effective date
        raise:  IllegalState - ``has_effective_date()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.has_effective_date():
            return self._effective_date
        else:
            raise errors.IllegalState()

    effective_date = property(fget=get_effective_date)

    def get_effective_clock_rate(self):
        """Gets the rate of the clock.

        return: (decimal) - the rate
        raise:  IllegalState - ``has_effective_date()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.has_effective_date():
            return self._effective_clock_rate
        else:
            raise errors.IllegalState()

    effective_clock_rate = property(fget=get_effective_clock_rate)

    def get_locale(self):
        """Gets the locale.

        return: (osid.locale.Locale) - a locale
        *compliance: mandatory -- This method must be implemented.*

        """
        return self._locale

    locale = property(fget=get_locale)

    def has_format_type(self):
        """Tests if a ``DisplayText`` format ``Type`` is available.

        return: (boolean) - ``true`` if a format type is available,
                ``false`` otherwise
        *compliance: mandatory -- This method must be implemented.*

        """
        return bool(self._format_type)

    def get_format_type(self):
        """Gets the ``DisplayText`` format ``Type``.

        return: (osid.type.Type) - the format ``Type``
        raise:  IllegalState - ``has_format_type()`` is ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.has_format_type():
            return self._format_type
        else:
            raise errors.IllegalState()

    format_type = property(fget=get_format_type)

    @utilities.arguments_not_none
    def get_proxy_record(self, proxy_record_type):
        """Gets the proxy record corresponding to the given ``Proxy`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``proxy_record_type`` may be the ``Type``
        returned in ``get_record_types()`` or any of its parents in a
        ``Type`` hierarchy where ``has_record_type(proxy_record_type)``
        is ``true`` .

        arg:    proxy_record_type (osid.type.Type): the type of proxy
                record to retrieve
        return: (osid.proxy.records.ProxyRecord) - the proxy record
        raise:  NullArgument - ``proxy_record_type`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported - ``has_record_type(proxy_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class ProxyCondition(abc_proxy_rules.ProxyCondition, osid_rules.OsidCondition):
    """A ``ProxyCondition`` is used to transfer external information into a proxy."""

    def __init__(self):
        self._effective_agent_id = None
        self._language_type = None
        self._script_type = None
        self._calendar_type = None
        self._time_type = None
        self._currency_type = None
        self._unit_system_type = None
        self._format_type = None
        self._http_request = None

    @utilities.arguments_not_none
    def set_effective_agent_id(self, agent_id):
        """Sets the effective agent ``Id`` to indicate acting on behalf of.

        arg:    agent_id (osid.id.Id): an agent ``Id``
        raise:  NullArgument - ``agent_id`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._effective_agent_id = agent_id

    effective_agent_id = property(fset=set_effective_agent_id)

    @utilities.arguments_not_none
    def set_effective_date(self, date, rate):
        """Sets the effective date.

        arg:    date (timestamp): a date
        arg:    rate (decimal): the rate at which the clock should tick
                from the given effective date. 0 is a clock that is
                fixed
        raise:  NullArgument - ``date`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    @utilities.arguments_not_none
    def set_language_type(self, language_type):
        """Sets the language type.

        arg:    language_type (osid.type.Type): the language type
        raise:  NullArgument - ``language_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._language_type = language_type

    language_type = property(fset=set_language_type)

    @utilities.arguments_not_none
    def set_script_type(self, script_type):
        """Sets the script type.

        arg:    script_type (osid.type.Type): the script type
        raise:  NullArgument - ``script_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._script_type = script_type

    script_type = property(fset=set_script_type)

    @utilities.arguments_not_none
    def set_calendar_type(self, calendar_type):
        """Sets the calendar type.

        arg:    calendar_type (osid.type.Type): the calendar type
        raise:  NullArgument - ``calendar_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._calendar_type = calendar_type

    calendar_type = property(fset=set_calendar_type)

    @utilities.arguments_not_none
    def set_time_type(self, time_type):
        """Sets the time type.

        arg:    time_type (osid.type.Type): the time type
        raise:  NullArgument - ``time_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._time_type = time_type

    time_type = property(fset=set_time_type)

    @utilities.arguments_not_none
    def set_currency_type(self, currency_type):
        """Sets the currency type.

        arg:    currency_type (osid.type.Type): the currency type
        raise:  NullArgument - ``currency_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._currency_type = currency_type

    currency_type = property(fset=set_currency_type)

    @utilities.arguments_not_none
    def set_unit_system_type(self, unit_system_type):
        """Sets the unit system type.

        arg:    unit_system_type (osid.type.Type): the unit system type
        raise:  NullArgument - ``unit_system_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._unit_system_type = unit_system_type

    unit_system_type = property(fset=set_unit_system_type)

    @utilities.arguments_not_none
    def set_format_type(self, format_type):
        """Sets the ``DisplayText`` format type.

        arg:    format_type (osid.type.Type): the format type
        raise:  NullArgument - ``format_type`` is ``null``
        *compliance: mandatory -- This method must be implemented.*

        """
        self._format_type = format_type

    format_type = property(fset=set_format_type)

    @utilities.arguments_not_none
    def get_proxy_condition_record(self, proxy_condition_type):
        """Gets the proxy condition record corresponding to the given ``Proxy`` record ``Type``.

        This method is used to retrieve an object implementing the
        requested record. The ``proxy_record_type`` may be the ``Type``
        returned in ``get_record_types()`` or any of its parents in a
        ``Type`` hierarchy where ``has_record_type(proxy_record_type)``
        is ``true`` .

        arg:    proxy_condition_type (osid.type.Type): the type of proxy
                condition record to retrieve
        return: (osid.proxy.records.ProxyConditionRecord) - the proxy
                condition record
        raise:  NullArgument - ``proxy_condition_record_type`` is
                ``null``
        raise:  OperationFailed - unable to complete request
        raise:  Unsupported -
                ``has_record_type(proxy_condition_record_type)`` is
                ``false``
        *compliance: mandatory -- This method must be implemented.*

        """
        if self.has_record_type(proxy_condition_type):
            return self
        else:
            raise errors.Unsupported()

    def set_http_request(self, http_request):
        """Support the HTTPRequest ProxyConditionRecordType and checks for special effective agent ids"""
        self._http_request = http_request
        if 'HTTP_LTI_USER_ID' in http_request.META:
            try:
                authority = http_request.META['HTTP_LTI_TOOL_CONSUMER_INSTANCE_GUID']
            except (AttributeError, KeyError):
                authority = 'unknown_lti_consumer_instance'
            self.set_effective_agent_id(Id(
                authority=authority,
                namespace='agent.Agent',
                identifier=http_request.META['HTTP_LTI_USER_ID']))

    http_request = property(fset=set_http_request)



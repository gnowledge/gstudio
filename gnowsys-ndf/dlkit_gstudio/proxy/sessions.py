"""GStudio implementations of proxy sessions."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from . import rules
from .. import utilities
from ...abstract_osid.proxy import sessions as abc_proxy_sessions
from ..authentication_process.objects import Authentication
from ..osid import sessions as osid_sessions
from dlkit.abstract_osid.osid import errors




class ProxySession(abc_proxy_sessions.ProxySession, osid_sessions.OsidSession):
    """This session converts external data into a proxy for use in OSID proxy managers.

    The external data is specified in the form of a ``ProxyCondition``.

    """

    def __init__(self, proxy=None, runtime=None):
        self._proxy = proxy
        self._runtime = runtime

    def get_proxy_condition(self):
        """Gets a proxy condition for acquiring a proxy.

        A new proxy condition should be acquired for each proxy request.

        return: (osid.proxy.ProxyCondition) - a proxy condiiton
        *compliance: mandatory -- This method is must be implemented.*

        """
        return rules.ProxyCondition()

    proxy_condition = property(fget=get_proxy_condition)

    @utilities.arguments_not_none
    def get_proxy(self, input_):
        """Gets a proxy.

        arg:    input (osid.proxy.ProxyCondition): a proxy condition
        return: (osid.proxy.Proxy) - a proxy
        raise:  NullArgument - ``input`` is ``null``
        raise:  OperationFailed - unable to complete request
        raise:  PermissionDenied - authorization failure
        raise:  Unsupported - ``input`` is not of this service
        *compliance: mandatory -- This method is must be implemented.*

        """
        if input_._http_request is not None:
            authentication = Authentication()
            authentication.set_django_user(input_._http_request.user)
        else:
            authentication = None
        effective_agent_id = input_._effective_agent_id
        # Also need to deal with effective dates and Local
        return rules.Proxy(authentication=authentication,
                           effective_agent_id=effective_agent_id)


